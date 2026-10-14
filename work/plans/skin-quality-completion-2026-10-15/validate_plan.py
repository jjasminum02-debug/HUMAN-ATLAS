"""Validate this planning amendment without promoting implementation acceptance."""
from pathlib import Path
import copy, hashlib, importlib.util, json, re, subprocess, types
ROOT=Path(__file__).resolve().parents[3]
P=Path(__file__).resolve().parent
checks=[]
def check(name, condition):
    if not condition: raise AssertionError(name)
    checks.append(name)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
current=json.loads((ROOT/'work/EXECUTION.json').read_text())
baseline=json.loads((P/'baseline.json').read_text())
before=json.loads(subprocess.check_output(['git','show',baseline['head']+':work/EXECUTION.json'],cwd=ROOT))
unit=current['featureWorkUnits']['AT10']; original=before['featureWorkUnits']['AT10']
allowed={'nextPrompt','resumeUnit','completionExecution','skinFit','skinRuntime'}
check('AT10 original nonplanning fields preserved', all(unit[k]==v for k,v in original.items() if k not in allowed))
for key in ['skinFit','skinRuntime']:
    a=copy.deepcopy(unit[key]);b=copy.deepcopy(original[key]);a.pop('completionPlan',None);b.pop('completionPlan',None)
    check(key+' actual results preserved',a==b)
check('all other feature units preserved',{k:v for k,v in current['featureWorkUnits'].items() if k!='AT10'}=={k:v for k,v in before['featureWorkUnits'].items() if k!='AT10'})
check('all base tasks preserved',current['tasks']==before['tasks'])
check('other feature plan preserved',current['featurePlans']['motion-quality-review']==before['featurePlans']['motion-quality-review'])
check('AT order preserved',current['featurePlans']['acupoint-at-361']['order']==before['featurePlans']['acupoint-at-361']['order'])
check('AT10 acceptance still false',unit['acceptancePassed'] is False)
c=unit['completionExecution'];q=json.loads((P/'queue.json').read_text())
check('eight remaining units',len(c['order'])==8 and len(set(c['order']))==8)
check('next V1 is planned not executed',c['nextUnit']=='V1' and all(v['status']=='planned' for v in c['units'].values()))
check('queue order aligned',c['order']==[s['unit'] for s in q['stages']])
for i,s in enumerate(q['stages']):
    check(s['unit']+' prompt exists',(ROOT/s['prompt']).is_file())
    check(s['unit']+' dependencies earlier',all(d in c['order'][:i] for d in s['requires']))
    text=(ROOT/s['prompt']).read_text()
    check(s['unit']+' common contract linked','COMMON.md' in text)
for file in P.glob('*.md'):
    if file.name.startswith('historical-'): continue # Exact archive; relative links use original directory.
    for url in re.findall(r'\]\(([^)]+)\)',file.read_text()):
        if not url.startswith(('https:','http:','#')):
            check('link '+file.name+' '+url,(file.parent/url.split('#')[0]).exists())
for manifest_path in ['atlas-data/anatomy/skin/at10-f1-correspondence-r2/manifest-f1c7.json','atlas-data/anatomy/skin/at10-f2-left-foot-r1/manifest-f2c3.json']:
    m=json.loads((ROOT/manifest_path).read_text());check('actual asset '+m['id'],sha(ROOT/m['url'])==m['sha256'])
# Source generator regression checks: explicit feature pointer, legacy prose untouched, missing file rejected.
script=ROOT/'work/tools/sync_execution.py'
spec=importlib.util.spec_from_file_location('skin_plan_sync',script);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
rendered=module.render(current)
check('NEXT has AT10/V1','**AT10/V1**' in rendered[ROOT/'work/NEXT.md'])
check('STATUS has feature pointer','FEATURE_NEXT: acupoint-at-361 / AT10/V1' in rendered[ROOT/'work/STATUS.md'])
without=copy.deepcopy(current);without['featureWorkUnits']['AT10'].pop('completionExecution')
check('legacy prose feature pointers do not block base renderer','## 기능 확장' not in module.render(without)[ROOT/'work/NEXT.md'])
bad=copy.deepcopy(current);bad['featureWorkUnits']['AT10']['completionExecution']['nextPrompt']='missing-skin-plan-prompt.txt'
try: module.render(bad)
except ValueError: checks.append('missing structured prompt rejected')
else: raise AssertionError('missing prompt not rejected')
# Re-render old source/data to prove mixed WIP outside generated blocks is intact.
old_source=subprocess.check_output(['git','show',baseline['head']+':work/tools/sync_execution.py'],cwd=ROOT).decode()
old=types.ModuleType('old_sync');old.__file__=str(script);exec(compile(old_source,str(script),'exec'),old.__dict__)
old_views=old.render(before)
for path,digest in baseline['trackedWipHashes'].items():
    file=ROOT/path
    if file in old_views:
        check('prior generated-view WIP preserved '+path,hashlib.sha256(old_views[file].encode()).hexdigest()==digest)
    else: check('prior WIP preserved '+path,sha(file)==digest)
subprocess.run(['python3',str(script),'--check'],cwd=ROOT,check=True)
result={'scope':'plan/link/input preservation and feature projection tests only; no geometry/material implementation','checksPassed':len(checks),'checks':checks,'implementationExecuted':False,'acceptanceChanged':False}
(P/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(f'{len(checks)} checks passed')
