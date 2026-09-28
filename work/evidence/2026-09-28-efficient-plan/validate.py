import json,hashlib,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[3];E=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=load(E/'baseline.json');q=load(E/'execution-queue.json');old=load(R/'work/evidence/T78/execution-queue.json');reg=load(R/'work/task-registry-r15.json');checks=[]
def check(name,yes):checks.append({'name':name,'passed':bool(yes)})
check('28 active tasks, unique IDs',len(q['order'])==len(set(q['order']))==len(q['jobs'])==28)
check('44 retired tasks excluded from active queue',len(q['supersededTaskIds'])==44 and not set(q['supersededTaskIds'])&set(reg['activeQueue']))
check('no new numeric task ID',set(q['order'])|set(q['supersededTaskIds'])==set(old['order']) and q['nextUnallocatedNumericId']==166)
check('12 regional packages, awaiting real T96 freeze',len([j for j in q['jobs'] if j['kind']=='regional_structure_package'])==12 and all(j['targetIds'] is None and j['targetFreezeState']=='pending_T96' for j in q['jobs'] if j['kind']=='regional_structure_package'))
check('exact 70 source gaps preserved',sorted((j['id'],j['targetIds']) for j in q['jobs'] if j['kind']=='source_acquisition')==sorted((j['id'],j['targetIds']) for j in old['jobs'] if j['kind']=='source_acquisition'))
check('latissimus four independent gates preserved',all(any(j['id']==i for j in q['jobs']) for i in ['T97','T98','T99','T100']))
check('dependencies occur before consumers',all(d=='T78' or q['order'].index(d)<q['order'].index(j['id']) for j in q['jobs'] for d in j['prerequisiteIds']))
check('next links and registry aligned',all(j['defaultNext']==(q['order'][i+1] if i+1<len(q['order']) else 'T80') and next(t for t in reg['tasks'] if t['id']==j['id'])['defaultNext']==j['defaultNext'] for i,j in enumerate(q['jobs'])))
check('T80 requires current active structure scope',next(t for t in reg['tasks'] if t['id']=='T80')['prerequisiteIds']==q['order'])
check('no retirement marked completed',all(reg['taskStatuses'][id]=='superseded_not_executed' for id in q['supersededTaskIds']))
check('current prompts reference latest contract',all('22-EFFICIENT' in j['prompt'] and (R/j['spec']).exists() for j in q['jobs']))
changed=[p for p,h in b['files'].items() if not (R/p).is_file() or sha(R/p)!=h]
allowed={f'work/tasks/{i}.md' for i in old['order']}|{f'work/tasks/{i}.md' for i in ['T80','T81','T83','T87','T89','T91']}|{'work/STATUS.md','work/task-registry-r15.json'}|{f'design/2026-09-25-muscle-atlas/{n}' for n in ['19-ALL-MUSCLES-BEFORE-NERVES.md','20-SERIAL-PROMPTS-FULL-SCOPE.md','21-WHOLE-BODY-ACQUISITION-T78.md']}
check('only authorized planning paths changed',set(changed)<=allowed)
check('original T78 report and evidence preserved',all(sha(R/p)==h for p,h in b['files'].items() if p.startswith('work/evidence/T78/') or p=='work/reports/T78.md'))
check('app code and runtime data unchanged',not any(p.startswith(('atlas-web/','atlas-data/')) for p in changed))
check('all 650 source files unchanged',all((R/p).is_file() and sha(R/p)==h for p,h in b['source'].items()))
check('OpenSim immutable HEAD and status',subprocess.check_output(['git','-C',str(R/'OpenSim_Models'),'rev-parse','HEAD'],text=True).strip()==b['opensimHead'] and subprocess.check_output(['git','-C',str(R/'OpenSim_Models'),'status','--porcelain'],text=True)==b['opensimStatus'])
check('T78 partial and future work unexecuted',reg['taskStatuses']['T78']=='partial_target_semantics_pending' and all(reg['taskStatuses'][j['id']].startswith('planned') for j in q['jobs']))
result={'passed':sum(c['passed'] for c in checks),'total':len(checks),'checks':checks,'changedExistingPaths':changed,'runtimeChecks':'not rerun; no app/asset changes, historic measurements explicitly labeled','actualImplementationStarted':False}
(E/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':result['passed'],'total':len(checks),'failures':[c for c in checks if not c['passed']]},ensure_ascii=False))
assert all(c['passed'] for c in checks)
