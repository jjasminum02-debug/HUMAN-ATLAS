#!/usr/bin/env python3
"""Validate computed T59 handoff/candidates, without mutating historical or current inputs."""
import argparse,copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH='work/evidence/T59/authoring-run-manifest-r2.json'
def read(path):return json.loads((ROOT/path).read_text())
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def require(value,message):
    if not value:raise ValueError(message)
def filecheck(ref):
    path=(ROOT/ref['path']).resolve();require(path.is_relative_to(ROOT),'path containment')
    require(path.is_file() and sha(ref['path'])==ref['sha256'],f"hash drift: {ref['path']}")
def validate(m):
    require(m['schemaVersion']=='t59-authoring-manifest-v2','schema')
    old=read(m['predecessor']['path']);filecheck(m['predecessor'])
    require(m['denominators']==old['denominators'],'frozen denominators')
    packages=m['targetPackages']+m['sourceConceptPackages'];ids=[p['packageId'] for p in packages]
    require(len(ids)==661 and len(set(ids))==len(ids),'429 target + 232 concept packages')
    require({p['packageId'] for p in m['targetPackages']}=={p['packageId'] for p in old['targetPackages']},'target completeness')
    require({p['packageId'] for p in m['sourceConceptPackages']}=={p['packageId'] for p in old['sourceConceptPackages']},'concept completeness')
    previous={p['packageId']:p for p in old['targetPackages']+old['sourceConceptPackages']}
    for package in packages:
        for field in ['owner','assignedTargetIds','assignedMembershipKeys','assignedSourceConceptKeys','assignedSourceKeys']:
            require(package.get(field)==previous[package['packageId']].get(field),'immutable exact assignment scope')
        if package in m['targetPackages']:
            require(package['authoringStatus']==('needs_authoring' if package.get('candidateSourceRelations') else 'unavailable'),'target readiness needs scope-specific production proof')
    assigned=[]
    for owner,w in m['workers'].items():
        expected={p['packageId'] for p in packages if p['owner']==owner}
        require(set(w['assignedPackageIds'])==expected and len(w['assignedPackageIds'])==len(expected),'worker ownership')
        assigned+=w['assignedPackageIds']
    require(sorted(assigned)==sorted(ids),'no missing or duplicated assignments')
    source=read('atlas-data/source-cache/datasets/za/compiled/manifest.json');instances={r['sourceKey']:r for r in source['instances']}
    units=m['sourceSurfaceUnits'];keys=[u['sourceKey'] for u in units]
    require(len(keys)==462 and len(set(keys))==462,'all 462 source units')
    require(set(keys)=={key for p in m['sourceConceptPackages'] for key in p['assignedSourceKeys']},'surface assignment completeness')
    for unit in units:
        dep=unit['geometryDependency'];filecheck(dep);src=instances[unit['sourceKey']]
        require(dep['instanceMatrix']==src['matrix'] and dep['datasetRevision']==source['revision'] and dep['sourceNamespace']==source['namespace'],'source frame/revision drift')
        package=next(p for p in m['sourceConceptPackages'] if p['packageId']==unit['packageId'])
        require(unit['owner']==package['owner'],'surface owner')
        require(unit['status'] in ['ready','needs_authoring','unavailable'],'surface status')
        require(unit['status']!='unavailable' or bool(unit['unavailableReason']),'honest unavailable reason')
    for dep in m['immutableSharedProductionDependencies'].values():filecheck(dep)
    require(not any('learner-card-runtime' in key or key.startswith('atlas-web/') for key in m['immutableSharedProductionDependencies']),'UI must not freeze production')
    filecheck(m['researchAdoption']);adoption=read(m['researchAdoption']['path'])
    for original in adoption['originalHeaders'].values():filecheck(original)
    bundle=read('atlas-data/motion/motion-learning.json');readyKeys=set();authored=0;verified=0
    for path in m['candidatePackages']:
        c=read(path);asset=next(a for a in bundle['motionAssets'] if a['id']==c['assetId']);authored+=1
        filecheck({'path':c['assetPath'],'sha256':c['assetSha256']});filecheck(c['authoringRecord']);filecheck(c['authoringInput'])
        record=read(c['authoringRecord']['path']);inp=read(c['authoringInput']['path'])
        require(record['motionSha256']==asset['sha256']==c['assetSha256'],'candidate asset registry')
        require(record['inputSha256']==hashlib.sha256(json.dumps(inp,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'authoring input hash')
        require(asset['sourceBinding']['members']==record['members'] and c['sourceKey']==asset['sourceBinding']['subjectSourceKey'],'candidate members')
        require(record['rights']['sourceOnly'] is True and record['rights']['humanReview']=='not_performed' and record['rights']['publicRedistribution']=='held','no approval promotion')
        require(all(v['flippedTriangles']==0 for v in record['surfaceMetrics']),'surface orientation')
        definition=next(d for d in bundle['motionDefinitions'] if d['id']==asset['motionDefinitionId'])
        require(record['poseRange']['endPoseId']==definition['endPoseId'] and record['poseRange']['referencePoseId']==definition['startPoseId'],'pose provenance')
        for dep in c['productionDependencies'].values():filecheck(dep)
        filecheck(c['geometryQA']);geometry=read(c['geometryQA']['path'])
        require(geometry['assetSha256']==asset['sha256'],'current asset geometric QA')
        require(all(geometry['summary'][k]==0 for k in ['newSubjectContainmentMaximum','newPassiveContainmentMaximum','newTalusContainmentMaximum']),'source-relative penetration at tested poses')
        ready=False
        if c['browserQA']:
            filecheck(c['browserQA']);qa=read(c['browserQA']['path'])
            ready=qa['status']=='passed' and qa['assetSha256']==asset['sha256'] and all(x['passed'] for x in qa['checks'])
        require((c['status']=='ready')==ready,'ready requires current actual browser QA')
        if ready:readyKeys.add(c['sourceKey']);verified+=1
    require({u['sourceKey'] for u in units if u['status']=='ready'}==readyKeys,'candidate readiness matches surfaces')
    for unit in units:
        sourceSide=instances[unit['sourceKey']]['sourceLabelSide']
        expected='ready' if unit['sourceKey'] in readyKeys else 'needs_authoring' if sourceSide in ['left','right','midline','not_applicable'] else 'unavailable'
        require(unit['status']==expected,'computed surface readiness from actual pinned inputs')
    for p in m['sourceConceptPackages']:

        owned=[u for u in units if u['packageId']==p['packageId']]
        expected='ready' if all(u['status']=='ready' for u in owned) else 'needs_authoring' if any(u['status']!='unavailable' for u in owned) else 'unavailable'
        require(p['authoringStatus']==expected,'aggregate side/extent readiness')
    expected={'sourceSurfaceUnits':{s:sum(u['status']==s for u in units) for s in ['ready','needs_authoring','unavailable']},
      'aggregatePackages':{s:sum(p['authoringStatus']==s for p in packages) for s in ['ready','needs_authoring','unavailable']},'actualAuthoredSourceAssets':authored,'actualBrowserVerifiedSourceAssets':verified}
    require(m['currentReadiness']==expected,'computed readiness, never hardcoded zero')
    require(m['commonWriterContract']['owner']=='T59-common-writer' and all(f['owner']=='T59-common-writer' for f in m['commonWriterContract']['sharedFamilies']),'shared rig/clip ownership')
    return expected
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--fixtures',action='store_true');parser.add_argument('--output');a=parser.parse_args();m=read(PATH);counts=validate(m);negative=[]
    if a.fixtures:
        for kind in ['assignment','readiness','source_matrix','approval']:
            changed=copy.deepcopy(m)
            if kind=='assignment':changed['workers']['A']['assignedPackageIds'].pop()
            elif kind=='readiness':changed['currentReadiness']['actualBrowserVerifiedSourceAssets']+=1
            elif kind=='source_matrix':changed['sourceSurfaceUnits'][0]['geometryDependency']['instanceMatrix'][0]+=1
            else:changed['commonWriterContract']['sharedFamilies'][0]['owner']='A'
            try:validate(changed)
            except ValueError:negative.append({'case':kind,'passed':True})
            else:raise ValueError(f'negative fixture accepted: {kind}')
    result={'status':'passed','manifest':PATH,'sha256':sha(PATH),'readiness':counts,'negativeFixtures':negative}
    if a.output:(ROOT/a.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result))
if __name__=='__main__':main()
