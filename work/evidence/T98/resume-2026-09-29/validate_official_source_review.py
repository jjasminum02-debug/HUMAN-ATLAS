#!/usr/bin/env python3
"""Validate the bounded T98 official-source review and preservation boundary."""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent

def sha_bytes(value: bytes) -> str: return hashlib.sha256(value).hexdigest()
def sha_file(path: Path) -> str: return sha_bytes(path.read_bytes())
def add(checks, name, condition, evidence): checks.append({'name':name,'passed':bool(condition),'evidence':evidence})
def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
checks=[]
ledger=json.loads((HERE/'official-source-review.json').read_text(encoding='utf-8'))
execution=json.loads((ROOT/'work/EXECUTION.json').read_text(encoding='utf-8'))
progress=json.loads((ROOT/'work/evidence/T98/progress.json').read_text(encoding='utf-8'))
report=(ROOT/'work/reports/T98.md').read_text(encoding='utf-8')
reentry=json.loads((HERE/'reentry-no-new-official-materials.json').read_text(encoding='utf-8'))
row=execution['tasks']['T98']; unit='resolve-frame-unit-pose-side-rights-lineage-and-base-comparison'
add(checks,'official source review records the primary Blender listing and exact Z-Anatomy commit',ledger['checks'][0]['primarySourceUrl']=='https://download.blender.org/release/Blender3.5/' and ledger['checks'][1]['pinnedRevision']=='c7010a903b75a2fd24a13b1c2c4c3546a9223780',{'checks':len(ledger['checks'])})
add(checks,'checksum sidecar remained unreadable and runtime gate is not promoted','not obtained' in ledger['checks'][0]['sidecarRetrieval'] and ledger['checks'][0]['result'].startswith('unresolved') and row['progress']['gate']['runtimePublisherProvenanceVerified'] is False,ledger['checks'][0])
add(checks,'object identity/rights and frame/pose remain unresolved',ledger['checks'][1]['result'].startswith('unresolved') and row['progress']['gate']['sourceIdentityAndRightsResolved'] is False and row['progress']['gate']['sourceFrameUnitPoseResolved'] is False,ledger['checks'][1])
add(checks,'whole-body comparable coverage/cost remains unresolved',ledger['checks'][2]['result'].startswith('unresolved') and row['progress']['gate']['wholeBodyComparableCostAvailable'] is False,ledger['checks'][2])
add(checks,'production and learner/review holds were preserved',ledger['preservation']['productionBase'] is None and ledger['preservation']['sourceOnly'] is True and ledger['preservation']['localUseRights'].startswith('held') and ledger['preservation']['publicRedistribution']=='held' and ledger['preservation']['humanReview']=='not_performed' and not ledger['preservation']['canonicalMappingOrLearnerUIChanged'],ledger['preservation'])
add(checks,'T98 stays partial at the same unit and T99 is not started',row['acceptance']=='partial' and row['executionStatus']=='in_progress' and row['progress']['nextUnit']==unit and row['progress']['nextId']=='T98' and not row['progress']['gate']['nextTaskExecutionStarted'] and ledger['preservation']['T99Started'] is False,{'acceptance':row['acceptance'],'executionStatus':row['executionStatus'],'nextUnit':row['progress']['nextUnit']})
add(checks,'progress mirror and report point to the new evidence',progress['acceptance']=='partial' and progress['nextUnit']==unit and any(x.get('evidence','').endswith('official-source-review.json') for x in progress['resumeHistory']) and 'official-source-review.json' in report,{'historyCount':len(progress.get('resumeHistory',[]))})
add(checks,'no new official or hash-bound source material appeared since the previous review',reentry['checkedExistingEvidence']['newOfficialSourceFilesOrReceiptsFound'] is False and not reentry['checkedExistingEvidence']['shaMismatches'] and reentry['checkedExistingEvidence']['assessmentInputCount']==15, reentry['checkedExistingEvidence'])
add(checks,'concrete missing source material is recorded without resolving any gate by inference',len(reentry['unresolvedMaterialsRequiredToAdvance'])==4 and reentry['result'].startswith('no_new_official_materials') and reentry['preservation']['productionBase'] is None and reentry['preservation']['sourceOnly'] is True and reentry['preservation']['humanReview']=='not_performed',{'missingMaterials':reentry['unresolvedMaterialsRequiredToAdvance'],'preservation':reentry['preservation']})
add(checks,'latest T98 resume history retains the same nextUnit and does not start T99',any(x.get('evidence','').endswith('reentry-no-new-official-materials.json') and x.get('nextUnit')==unit and x.get('nextId')=='T98' for x in row['progress']['resumeHistory']) and reentry['preservation']['T99Started'] is False,{'nextUnit':row['progress']['nextUnit'],'nextId':row['progress']['nextId']})
head=ledger['startBaseline']['head']
old_exec=json.loads(subprocess.check_output(['git','show',f'{head}:work/EXECUTION.json'],cwd=ROOT,text=True))
others_old={k:v for k,v in old_exec['tasks'].items() if k!='T98'}
others_now={k:v for k,v in execution['tasks'].items() if k!='T98'}
add(checks,'only the T98 execution task row differs from starting HEAD',others_old==others_now,{'startHead':head,'nonT98RowsEqual':others_old==others_now})
base=json.loads((HERE/'baseline.json').read_text(encoding='utf-8'))
current_status=subprocess.check_output(['git','status','--porcelain=v1'],cwd=ROOT,text=True).splitlines()
missing=[line for line in base['workingTree']['statusLines'] if line not in current_status]
add(checks,'all pre-existing user WIP status paths remain present',not missing,{'baselineCount':base['workingTree']['pathCount'],'missing':missing})
old_validation='work/evidence/T98/resume-2026-09-29/runtime-chain-validation.json'
old_bytes=subprocess.check_output(['git','show',f'{head}:{old_validation}'],cwd=ROOT)
old_hash=sha_bytes(old_bytes)
add(checks,'prior T98 runtime-chain validation artifact is unchanged',sha_file(ROOT/old_validation)==old_hash,{'path':old_validation,'sha256':sha_file(ROOT/old_validation)})
expected_archive=base['inputFiles']['atlas-data/source-cache/z-anatomy/t97/Z-Anatomy.zip']['sha256']
expected_blend=base['inputFiles']['atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend']['sha256']
add(checks,'source archive and Startup.blend bytes remain unchanged',sha_file(ROOT/'atlas-data/source-cache/z-anatomy/t97/Z-Anatomy.zip')==expected_archive and sha_file(ROOT/'atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend')==expected_blend,{'archiveSha256':sha_file(ROOT/'atlas-data/source-cache/z-anatomy/t97/Z-Anatomy.zip'),'startupBlendSha256':sha_file(ROOT/'atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend')})
os_head=git('-C','OpenSim_Models','rev-parse','HEAD'); os_status=git('-C','OpenSim_Models','status','--porcelain')
add(checks,'OpenSim_Models remains clean at recorded HEAD',os_head==base['openSimModels']['head'] and os_status==base['openSimModels']['status'],{'head':os_head,'status':os_status})
sync=subprocess.run([sys.executable,str(ROOT/'work/tools/sync_execution.py'),'--check'],cwd=ROOT,text=True,capture_output=True)
add(checks,'generated execution projections pass sync check',sync.returncode==0,{'exit':sync.returncode,'stdout':sync.stdout.strip(),'stderr':sync.stderr.strip()})
result={'schemaVersion':'1.0.0','task':'T98','checkedAt':reentry['checkedAt'],'result':'passed_partial_gates_remain' if all(x['passed'] for x in checks) else 'validation_failed','taskStatus':'in_progress/partial','checks':checks,'summary':{'checkCount':len(checks),'passedCount':sum(x['passed'] for x in checks),'failedCount':sum(not x['passed'] for x in checks),'nextUnit':row['progress']['nextUnit'],'nextId':'T98','nextTaskStarted':False}}
out=HERE/'official-source-review-validation.json'
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result['summary'],ensure_ascii=False,indent=2))
if result['summary']['failedCount']: sys.exit(1)
