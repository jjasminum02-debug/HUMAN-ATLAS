"""Validate planning coverage, queue, reproducibility, and immutable inputs."""
from pathlib import Path
import json,hashlib,subprocess,sys
R=Path(__file__).resolve().parents[3];E=R/'work/evidence/T78'
def load(n):return json.loads((E/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(label,ok):
 checks.append({'name':label,'passed':bool(ok)})
 if not ok:print('FAIL',label)
s=load('inventory-summary.json');t=load('targets.json');a=load('source-elements.json');q=load('execution-queue.json');mapping=load('target-task-map.json');base=load('start-baseline.json')
check('unique target records',len({x['id'] for x in t})==len(t)==556)
check('unique source elements',len({x['id'] for x in a})==len(a)==613)
check('source denominator is not individual muscle denominator',s['wholeBodyIndividualMuscleDenominator'] is None and s['classificationStatus'].startswith('provisional'))
check('latissimus retained missing and allocated four real gates',next(x for x in t if x['id']=='TA2:2231')['states']['geometry']=='missing' and mapping['TA2:2231']['latissimusTasks']==['T97','T98','T99','T100'])
check('every target assigned exactly once to bounded reconciliation',set(mapping)=={x['id'] for x in t} and sorted(i for j in q['jobs'] if j['kind']=='target_reconciliation' for i in j['targetIds'])==sorted(mapping))
check('bounded data tasks <=10 target IDs',all(len(j['targetIds'])<=10 for j in q['jobs']))
acquired=[i for j in q['jobs'] if j['kind']=='source_acquisition' for i in j['targetIds']]
check('all 70 exact source gaps assigned once',len(acquired)==len(set(acquired))==70 and set(acquired)==set(s['missingMuscleSourceIds']+s['missingBoneSourceIds']))
check('all hidden nodes separately assigned',set(i for j in q['jobs'] if j['kind']=='held_review' for i in j['targetIds'])=={x['id'] for x in a if x['runtime'] and not x['runtime']['defaultVisible']})
check('unique queue IDs, no collision with prior IDs except authorized T79',len(q['order'])==len(set(q['order']))==len(q['jobs']) and all(j['id']=='T79' or int(j['id'][1:])>=95 for j in q['jobs']))
check('all task specs and full prompts present',all((R/j['spec']).is_file() and j['prompt'] in (R/j['spec']).read_text() for j in q['jobs']))
check('next links follow actual serial queue',all(j['defaultNext']==(q['order'][q['order'].index(j['id'])+1] if q['order'].index(j['id'])+1<len(q['order']) else 'T80') for j in q['jobs']))
check('dependencies precede jobs',all(d=='T78' or q['order'].index(d)<q['order'].index(j['id']) for j in q['jobs'] for d in j['prerequisiteIds']))
check('all later tasks remain planned',all(j['status']=='planned_not_started' for j in q['jobs']))
check('scapula diagnostic reflects exact asymmetry',load('region-diagnostic.json')['assets']['FJ3279']['regions']==['shoulder-scapular','thorax'] and load('region-diagnostic.json')['assets']['FJ3384']['regions']==['shoulder-scapular','upper-limb'])
owned={'design/2026-09-25-muscle-atlas/19-ALL-MUSCLES-BEFORE-NERVES.md','design/2026-09-25-muscle-atlas/20-SERIAL-PROMPTS-FULL-SCOPE.md','work/tasks/T79.md','work/STATUS.md','work/task-registry-r15.json'}
changed=[p for p,h in base['files'].items() if not (R/p).is_file() or sha(R/p)!=h]
check('all pre-existing file changes are authorized planning paths',set(changed)<=owned)
sourcechanged=[p for p,h in base['source'].items() if not (R/p).is_file() or sha(R/p)!=h]
check('all source-cache files unchanged',not sourcechanged)
check('no app code changed',not any(p.startswith('atlas-web/') for p in changed))
head=subprocess.check_output(['git','-C',str(R/'OpenSim_Models'),'rev-parse','HEAD'],text=True).strip();status=subprocess.check_output(['git','-C',str(R/'OpenSim_Models'),'status','--porcelain'],text=True)
check('OpenSim HEAD and clean state preserved',head==base['opensimHead'] and status==base['opensimStatus'])
models=load('opensim-readonly-inventory.json')['models']
check('OpenSim inspected source file bytes unchanged',all(sha(R/m['path'])==m['sha256'] for m in models))
# Deterministic evidence regeneration; exclude future plan and preservation snapshots.
names=['classification-ledger.json','targets.json','source-elements.json','inventory-summary.json','region-diagnostic.json']
before={n:sha(E/n) for n in names}
subprocess.run([sys.executable,str(E/'build_inventory.py')],cwd=R,stdout=subprocess.DEVNULL,check=True)
check('five inventory outputs deterministic',before=={n:sha(E/n) for n in names})
r=json.loads((R/'work/task-registry-r15.json').read_text())
check('working registry agrees with plan and honest T78 status',r['nextTask']=='T95' and r['taskStatuses']['T78']=='partial_target_semantics_pending' and all(r['taskStatuses'][j['id']]=='planned_not_started' for j in q['jobs']))
result={'result':'passed' if all(c['passed'] for c in checks) else 'failed','checks':checks,'passed':sum(c['passed'] for c in checks),'total':len(checks),'baselineFileCount':len(base['files']),'preservedSourceFileCount':len(base['source']),'allowedExistingChanges':changed,'sourceChanged':sourcechanged,'OpenSimHead':head,'OpenSimStatus':status,'browser':'not_run_no_runtime_changes; region issue verified against exact code and runtime manifest','typecheckBuild':'not_rerun_no_application_changes','wholeBodyCoverage':'partial','semanticClosure':'T96 pending; no canonical denominator assertion'}
(E/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
assert result['result']=='passed'
