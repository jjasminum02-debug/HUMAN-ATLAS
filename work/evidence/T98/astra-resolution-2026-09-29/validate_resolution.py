"""Independent checks for T98 feasibility, preserved holds, and source integrity."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
checks=[]
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,condition):
    if not condition: raise AssertionError(name)
    checks.append(name)

def validate_catalog(catalog):
    rows=catalog['objects']
    assert len({r['sourceKey'] for r in rows})==len(rows)
    assert len({r['name'] for r in rows})==len(rows)
    for row in rows:
        assert row['sourceLocator']['sourceFileSha256']==catalog['sourceHash']
        assert row['sourceOnly'] and row['canonicalConceptId'] is None
        assert row['upstreamFjId'] is None and row['learnerBinding']=='source_only_unbound'
        assert row['appDisplayRights']=='held_not_approved_by_this_task'
        assert row['publicRedistribution']=='held' and row['humanReview']=='not_performed'
        assert row['defaultLearnerVisible'] is False
    assert catalog['canonicalTargetCount']==542 and catalog['regionMembershipCount']==563
    assert catalog['muscleUniqueDenominator'] is None
    assert len(catalog['targetOverlay'])==542
    assert all(not t['canonicalIdentityVerified'] and not t['learnerBindingAdded'] for t in catalog['targetOverlay'])

catalog=read(OUT/'source-catalog.json'); probe=read(OUT/'evaluated-base-probe.json')
decision=read(OUT/'base-selection.json'); frame=read(OUT/'frame-contract.json')
rights=read(OUT/'rights-scope.json'); integrity=read(OUT/'runtime-integrity.json')
frozen=read(ROOT/'work/evidence/T98/representative-sample-freeze.json')
original=read(ROOT/'work/evidence/T98/resume-2026-09-28/evaluated-export-manifest.json')
validate_catalog(catalog); checks.append('source-only identity and independent held states')
check('960 exact object keys',len(catalog['objects'])==len(probe['objects'])==960)
check('542 target IDs preserved',{r['targetId'] for r in catalog['targetOverlay']}==
      {r['targetId'] for r in read(ROOT/'work/evidence/T98/target-reconciliation-t98.json')['targets']})
check('563 region memberships preserved',sum(len(r['regionIds']) for r in catalog['targetOverlay'])==563)
check('all decision inputs match actual bytes',all(sha(OUT/name)==h for name,h in decision['inputHashes'].items()))
check('source blend preserved',sha(ROOT/'atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend')==frozen['source']['memberSha256']==probe['sourceHashAfter'])
check('archive preserved',sha(ROOT/frozen['source']['archivePath'])==frozen['source']['archiveSha256'])
check('official DMG checksum matches local bytes',integrity['officialDmgSha256']==sha(Path('/private/tmp/t97-blender-3.5.0-arm64.dmg'))==integrity['localDmgSha256'])
check('actual executable matches receipt',sha(Path('/Volumes/Blender/Blender.app/Contents/MacOS/Blender'))==integrity['binarySha256']==probe['runtimeBinarySha256'])
check('signature verified in approved execution',integrity['codeSignature']['exitCode']==0 and integrity['codeSignature']['permissionMode']=='require_escalated')
check('no geometry evaluation failures',not probe['failures'])
before={r['objectName']:r['evaluatedGeometrySha256'] for r in original['sample']['objects']}
check('all 12 frozen hashes independently reproduced',len(probe['sampleReproducibility'])==12 and
      {r['name']:r['hash'] for r in probe['sampleReproducibility']}==before)
check('all original frozen locators represented',set(before)=={r['sourceObjectLocator']['objectIdName'] for r in frozen['objects']})
check('positive source metric scale confirmed',probe['unit']['system']=='METRIC' and
      probe['unit']['scaleLength']==frame['metersPerSourceUnit']==1.0 and probe['unit']['oneSourceUnitFormatted']=='1 m')
matrix=frame['sourceToProjectConvention']
check('axis conversion preserves handedness and metres',matrix==[[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]])
check('no invented BP3D registration or rig pose',frame['registeredToBP3DGeometry'] is False and
      frame['staticReferencePose']['sourceProvidedRestPoseId'] is None and not frame['staticReferencePose']['rigBindingVerified'])
check('456 source-labeled bilateral pairs checked',len(frame['evidence']['pairs'])==456 and
      all(r['sourceLabelAndPositionConsistent'] and r['leftCenterX']>0>r['rightCenterX'] for r in frame['evidence']['pairs']))
check('finite geometry and totals are source measured',sum(r['triangles'] for r in probe['objects'])==probe['totals']['triangles']==3025614)
check('indexed layout estimate calculated not file size',all(r['indexedPositionNormalIndexBytes']==r['vertices']*24+r['triangles']*12 for r in probe['objects']))
check('separate core and accessory representations',decision['corePreviewObjects']==786 and decision['coreKindCounts']==
      {'skeletal_surface':277,'muscle_surface_or_part':509,'musculoskeletal_accessory':174})
check('rights declaration preserved with exception groups',rights['publicRedistribution']=='held' and
      rights['appDisplayRights']=='held' and not rights['commercialOrPublicReleaseAuthorized'] and len(rights['exceptionGroups'])==4)
check('source README hash matches',sha(OUT/'source-readme.md')==rights['pinnedReadmeSha256'])
check('base decision limited to local source engineering',decision['decision']=='select_Z_Anatomy_as_primary_local_offline_compilation_base' and
      not decision['wholeBodyCoverageComplete'] and not decision['productionReleaseApproved'] and not decision['T99Started'])
for preview in probe['preview']:
    p=OUT/preview['path'];check('preview '+p.name,sha(p)==preview['sha256'] and p.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n' and p.stat().st_size>10000)
check('six actual preview views',len(probe['preview'])==6)
for name,mutate in [
    ('duplicate source identity rejected',lambda c:c['objects'][1].update(sourceKey=c['objects'][0]['sourceKey'])),
    ('invented canonical binding rejected',lambda c:c['objects'][0].update(canonicalConceptId='TA2:2231')),
    ('public-rights promotion rejected',lambda c:c['objects'][0].update(publicRedistribution='allowed')),
    ('hidden promotion rejected',lambda c:c['objects'][0].update(defaultLearnerVisible=True)),
    ('source hash drift rejected',lambda c:c['objects'][0]['sourceLocator'].update(sourceFileSha256='0'*64))]:
    bad=copy.deepcopy(catalog);mutate(bad)
    try:validate_catalog(bad)
    except AssertionError:checks.append(name)
    else:raise AssertionError(name)
baseline=read(OUT/'baseline.json')
owned={'design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md','work/tasks/T98.md',
       'work/reports/T98.md','work/EXECUTION.json','work/evidence/T98/progress.json',
       'work/STATUS.md','work/task-registry-r15.json','work/NEXT.md',
       'design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md'}
unexpected=[p for p,h in baseline['hashes'].items() if p not in owned and (not (ROOT/p).is_file() or sha(ROOT/p)!=h)]
check('all unrelated baseline files preserved',not unexpected)
execution=read(ROOT/'work/EXECUTION.json')
prior_execution=json.loads(subprocess.check_output(['git','show',baseline['head']+':work/EXECUTION.json'],cwd=ROOT,text=True))
check('other task records unchanged',all(v==execution['tasks'][k] for k,v in prior_execution['tasks'].items() if k!='T98'))
check('current queue accepts T98 and stops before T99',execution['tasks']['T98']['acceptance']=='passed' and
      execution['tasks']['T99']['acceptance']=='pending' and execution['activeOrder']==prior_execution['activeOrder'])
check('OpenSim source HEAD unchanged',subprocess.check_output(['git','-C',str(ROOT/'OpenSim_Models'),'rev-parse','HEAD'],text=True).strip()==baseline['openSimHead'])
check('OpenSim remains clean',subprocess.check_output(['git','-C',str(ROOT/'OpenSim_Models'),'status','--porcelain=v1'],text=True)==baseline['openSimStatus']=='')
result={'task':'T98','status':'passed','checks':checks,'passed':len(checks),'failed':0,
        'scope':'source feasibility; does not approve product completeness, public rights or clinical use',
        'validationScriptSha256':sha(Path(__file__)),'protectedBaselineFiles':len(baseline['hashes']),
        'applicationCodeChanged':False,'sourceOnlyRetained':True,'nextTaskNotStarted':True}
(OUT/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('T98 resolution checks',len(checks),'passed')
