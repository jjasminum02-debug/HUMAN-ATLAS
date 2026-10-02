#!/usr/bin/env python3
"""T59 immutable production handoff. R1 research/manifests are historical read-only inputs."""
import argparse,copy,hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT='work/evidence/T59/authoring-run-manifest-r2.json'
BASE='work/evidence/T59/authoring-run-manifest.json'
DIR='work/evidence/T59/authoring-r2'
CHECK=False
def digest(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def read(p):return json.loads((ROOT/p).read_text())
def dump(p,v):
    f=ROOT/p
    if CHECK:
        if not f.is_file() or read(p)!=v:raise ValueError(f'r2 output drift: {p}')
        return
    f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def snapshot(p):
    dest=f'{DIR}/input-snapshot/{digest(p)}/{p}';f=ROOT/dest;f.parent.mkdir(parents=True,exist_ok=True)
    if f.exists() and digest(dest)!=digest(p):raise ValueError(f'immutable r2 snapshot drift: {p}; create a new revision')
    if not f.exists():
        if CHECK:raise ValueError(f'missing frozen snapshot: {dest}')
        shutil.copyfile(ROOT/p,f)
    return {'path':dest,'sha256':digest(dest),'provenancePath':p}
def reconcile():
    adopted=[];headers={}
    for worker in 'ABC':
        path=f'work/evidence/motion-all-muscles-plan-2026-10-02/research-{worker.lower()}/proposals.json';p=read(path)
        hashes=p.get('header',{}).get('inputHashes',p.get('inputHashes',{}));changed={k for k,v in hashes.items() if not (ROOT/k).is_file() or digest(k)!=v}
        hashPaths={v:k for k,v in hashes.items()}
        headers[worker]={'path':path,'sha256':digest(path),'originalRunId':p.get('header',{}).get('runId',p.get('runId')),'currentDrift':sorted(changed),'originalHeaderUntouched':True}
        def inspect(value):
            paths=set();locators=[];noteChecks=[]
            if isinstance(value,dict):
                for k,v in value.items():
                    if k in ['sourceByteSha256','sourcePageBytesSha256'] and v in hashPaths:paths.add(hashPaths[v])
                    if k.endswith('Path') and isinstance(v,str) and (ROOT/v).is_file():paths.add(v)
                    if k=='reviewNotePath' and isinstance(v,str) and value.get('reviewNoteSha256'):
                        noteChecks.append({'path':v,'expected':value['reviewNoteSha256'],'matched':(ROOT/v).is_file() and digest(v)==value['reviewNoteSha256']})
                    if k in ['url','locator','evidenceRefs','sourceId','evidenceId'] and v:locators.append({k:v})
                    pp,ll,nn=inspect(v);paths.update(pp);locators+=ll;noteChecks+=nn
            elif isinstance(value,list):
                for v in value:
                    pp,ll,nn=inspect(v);paths.update(pp);locators+=ll;noteChecks+=nn
            elif isinstance(value,str) and value in hashes:paths.add(value)
            return paths,locators,noteChecks
        for kind in ['targetRows','sourceRows']:
            for row in p.get(kind,[]):
                for field,value in row.items():
                    if not isinstance(value,(dict,list)):continue
                    deps,locators,notes=inspect(value);impacted=sorted(deps&changed)
                    disposition='recheck_changed_dependencies' if impacted or any(not n['matched'] for n in notes) else 'reuse_unchanged_evidence_with_original_scope' if locators else 'retain_observation_without_promoting_claim'
                    adopted.append({'worker':worker,'rowId':row.get('targetId',row.get('sourceConceptKey')),'field':field,
                        'fieldSha256':hashlib.sha256(canonical(value)).hexdigest(),'dependencyPaths':sorted(deps),'impactedPaths':impacted,
                        'locators':locators,'reviewNoteHashChecks':notes,'disposition':disposition,
                        'productionMeaning':'research observation only; no inherited anatomy, source rig, clinical range or approval'})
    result={'schemaVersion':'t59-field-adoption-v2','originalHeaders':headers,'fields':adopted,
            'policy':'Learner projection drift impacts only dependent fields. Independent quoted/source-scoped claims retain their original locator and limits. Native rig absence does not prohibit authored derivation.'}
    dump(f'{DIR}/research-adoption.json',result);return {'path':f'{DIR}/research-adoption.json','sha256':digest(f'{DIR}/research-adoption.json')}
def build():
    old=read(BASE);source=read('atlas-data/source-cache/datasets/za/compiled/manifest.json');bySource={r['sourceKey']:r for r in source['instances']}
    paths=['atlas-data/catalog/target-scope-t96.json','atlas-data/source-cache/datasets/za/compiled/manifest.json',
      'atlas-data/overlays/za-local-integration.json','work/evidence/T35/motion-contract.json',
      'work/evidence/T59/resume-2026-10-02/authoring-input.json','atlas-data/motion/authoring/t59-za-right-ankle.json',
      'work/tools/author_source_surface_motion.py','work/tools/source_surface_constraints.py','work/tools/derive_source_surface_motion.py','atlas-data/schemas/motion-learning.schema.json']
    paths=[p for p in paths if (ROOT/p).is_file()]
    immutable={p:snapshot(p) for p in paths}
    # Action condition copied per value; UI/learner-card files are audit-only and never dependencies.
    bundle=read('atlas-data/motion/motion-learning.json');action=next(a for a in bundle['muscleActions'] if a['id']=='T59-ACTION-ZA-R-TIBANT-DF')
    conditionDigest=hashlib.sha256(canonical(action)).hexdigest();conditionPath=f'{DIR}/input-snapshot/{conditionDigest}/action-condition.json';dump(conditionPath,action)
    immutable['action-condition']={'path':conditionPath,'sha256':digest(conditionPath)}
    candidatePath=f'{DIR}/candidate-package.json';qaPath='work/evidence/T59/resume-2026-10-02/browser-qa.json';qa=read(qaPath) if (ROOT/qaPath).is_file() else {}
    asset=next(a for a in bundle['motionAssets'] if a['id']=='T59-ASSET-ZA-R-TIBANT-DF');record=read('atlas-data/motion/authoring/t59-za-right-ankle.json')
    geometryPath='work/evidence/T59/resume-2026-10-02/geometry-qc.json';geometry=read(geometryPath)
    ready=qa.get('status')=='passed' and qa.get('assetSha256')==asset['sha256'] and geometry['assetSha256']==asset['sha256'] and all(geometry['summary'][k]==0 for k in ['newSubjectContainmentMaximum','newPassiveContainmentMaximum','newTalusContainmentMaximum'])
    candidate={'schemaVersion':'t59-authoring-candidate-v2','packageId':'T59-ENGINE-VALIDATION-ZA-R-ANKLE','owner':'T59-common-writer',
       'sourceKey':asset['sourceBinding']['subjectSourceKey'],'assetId':asset['id'],'assetPath':asset['uri'],'assetSha256':asset['sha256'],
       'authoringRecord':immutable['atlas-data/motion/authoring/t59-za-right-ankle.json'],
       'authoringInput':immutable['work/evidence/T59/resume-2026-10-02/authoring-input.json'],
       'status':'ready' if ready else 'needs_authoring','browserQA':{'path':qaPath,'sha256':digest(qaPath)} if (ROOT/qaPath).is_file() else None,
       'geometryQA':{'path':geometryPath,'sha256':digest(geometryPath)},'productionDependencies':immutable,'rights':record['rights'],'coverage':'one exact right source instance; no left/full target-group coverage inferred'}
    dump(candidatePath,candidate)
    targets=[];concepts=[];units=[]
    for group,out in [('targetPackages',targets),('sourceConceptPackages',concepts)]:
        for original in old[group]:
            row={k:copy.deepcopy(original[k]) for k in ['packageId','packageType','owner','assignedTargetIds','assignedMembershipKeys','assignedSourceConceptKeys','assignedSourceKeys','semanticKind','regionIds','sourceConceptKey','sourceDataName','candidateSourceRelations','targetIdentityDisposition','outputPath'] if k in original}
            keys=row.get('assignedSourceKeys',[])
            if group=='sourceConceptPackages':
                for key in keys:
                    src=bySource[key];geom=src['lods']['detail'];path=f"atlas-data/source-cache/datasets/za/resources/{geom['resource']}.glb"
                    available=(ROOT/path).is_file() and digest(path)==geom['resource']
                    status='ready' if key==candidate['sourceKey'] and ready else 'needs_authoring' if available and src['sourceLabelSide'] in ['left','right','midline','not_applicable'] else 'unavailable'
                    unit={'sourceKey':key,'packageId':row['packageId'],'owner':row['owner'],'status':status,
                        'unavailableReason':None if status!='unavailable' else 'source side unresolved' if available else 'pinned source resource unavailable or hash mismatch',
                        'geometryDependency':{'path':path,'sha256':geom['resource'],'instanceMatrix':src['matrix'],'sourceNamespace':source['namespace'],'datasetRevision':source['revision']},
                        'candidate':candidatePath if key==candidate['sourceKey'] else None,
                        'missingInputs':[] if status=='ready' else ['authored source vertex/landmark regions with scoped anatomical context','specific qualitative action and authored pose conditions','same-scene passive context, collision/attachment and restore QA']}
                    units.append(unit)
                owned=[u for u in units if u['packageId']==row['packageId']]
                row['authoringStatus']='ready' if all(u['status']=='ready' for u in owned) else 'needs_authoring' if any(u['status']!='unavailable' for u in owned) else 'unavailable'
                row['surfaceUnitKeys']=keys
            else:
                row['authoringStatus']='needs_authoring' if row.get('candidateSourceRelations') else 'unavailable'
            row['missingInputs']=[] if row['authoringStatus']=='ready' else ['resolve exact target/part/group/side scope','author deformation against pinned static source; native rig is optional','verify actual selected source clip and required context']
            row['unavailableReason']='no exact target-to-source association in this pinned local scope; not a claim of geometry absence' if row['authoringStatus']=='unavailable' else None
            row['dependencyPolicy']='Immutable per-source geometry/frame/authoring inputs; shared pose family owned by common writer. Learner UI audit hashes do not freeze assets.'
            out.append(row)
    workers=copy.deepcopy(old['workers'])
    for owner,w in workers.items():w['assignedPackageIds']=[p['packageId'] for p in targets+concepts if p['owner']==owner]
    return {'schemaVersion':'t59-authoring-manifest-v2','task':'T59','runId':'T59-authoring-handoff-2026-10-02-r2','contractRevision':old['contractRevision'],
       'acceptanceScope':old['acceptanceScope'],'predecessor':{'path':BASE,'sha256':digest(BASE),'immutableHistoricalState':True},'denominators':old['denominators'],
       'workers':workers,'commonWriterContract':{'owner':'T59-common-writer','sharedFamilies':[{'id':'ZA-static-reference-sagittal-ankle-hinge','owner':'T59-common-writer','sourceNamespace':'za-c7010a9','candidatePath':candidatePath,
           'crossRegionContext':['leg','foot'],'members':record['members'],'reusePolicy':'Reuse family tooling; every new pose/member mask/action retains individual evidence and QA.'}],
           'workerWritePolicy':'candidate folders only; no common data/UI/manifest writes; T25 and T66 not started'},
       'targetPackages':targets,'sourceConceptPackages':concepts,'sourceSurfaceUnits':units,'immutableSharedProductionDependencies':immutable,
       'provenanceAudit':{'r1FrozenInputHashes':old['frozenInputHashes'],'currentHashes':{p:digest(p) for p in old['frozenInputHashes'] if (ROOT/p).is_file()},'notProductionDependencies':'App/UI/learner projections and whole-report hashes'},
       'researchAdoption':reconcile(),'candidatePackages':[candidatePath],
       'currentReadiness':{'sourceSurfaceUnits':{status:sum(u['status']==status for u in units) for status in ['ready','needs_authoring','unavailable']},
       'aggregatePackages':{status:sum(p['authoringStatus']==status for p in targets+concepts) for status in ['ready','needs_authoring','unavailable']},
       'actualAuthoredSourceAssets':len([asset]) if (ROOT/asset['uri']).is_file() else 0,'actualBrowserVerifiedSourceAssets':int(ready)},
       'preservation':old['preservation']}
def main():
    global CHECK
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args();CHECK=args.check;manifest=build()
    if args.check:
        if read(OUT)!=manifest:raise ValueError('r2 manifest is stale')
    else:dump(OUT,manifest)
    print(json.dumps({'status':'passed' if args.check else 'built','manifest':OUT,'readiness':manifest['currentReadiness']}))
if __name__=='__main__':main()
