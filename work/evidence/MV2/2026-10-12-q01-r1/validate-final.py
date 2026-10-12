import json,hashlib,subprocess
from pathlib import Path
R=Path.cwd();E=R/'work/evidence/MV2/2026-10-12-q01-r1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text())
start=load(E/'start.json');assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==start['head'];wip={p:sha(R/p)==h for p,h in start['trackedWipHashes'].items()};assert all(wip.values())
inputs=load(E/'input-hashes.json');assert all(sha(R/r['path'])==r['sha256'] for r in inputs)
protected=load(E/'protected-current-hashes.json');owned={'work/EXECUTION.json','atlas-web/src/data/motionLearningData.ts','atlas-web/plugins/motionAssets.ts'};assert all(sha(R/p)==h for p,h in protected.items() if p not in owned)
old=load(E/'execution-before-update.json');now=load(R/'work/EXECUTION.json');check=json.loads(json.dumps(now));check['featureWorkUnits']['MV2']=old['featureWorkUnits']['MV2'];assert check==old and now['featurePlans']['acupoint-at-361']['nextUnit']=='AT22'
assert now['featureWorkUnits']['MV2']['lastRun']['acceptancePassed'] and not now['featureWorkUnits']['MV2']['acceptancePassed'];q=load(E/'repair-queue.json');assert q['candidateGroups'][0]['status']=='resolved_engineering' and all(r['status']=='observed_ambiguous' for r in q['candidateGroups'][1:]);assert sum(r['mappingCount'] for r in q['candidateGroups'][1:])==32
for row in load(R/'atlas-data/motion/source-motion-repairs-r1.json')['rows']:
 assert sha(R/row['baseUri'])==row['baseSha256'] and sha(R/row['uri'])==row['sha256'];assert (R/row['uri']).stat().st_size==row['bytes'] and row['bytes']<8*1024*1024
assert load(E/'emitted-validation.json')['passed'] and load(E/'real-loader-validation.json')['passed'];assert all(r['exitCode']==0 for r in load(E/'build-final-r1.json'));assert 'tests 20' in (E/'tests-final.log').read_text() and 'fail 0' in (E/'tests-final.log').read_text();assert 'no writes' in (E/'sync-check-final.log').read_text();assert load(E/'console-final.json')==[]
shots=[]
for p in sorted(E.glob('*.png')):
 j=p.with_suffix('.json')
 if not j.exists():continue
 d=load(j);ds=d.get('canvas',[{}])[0].get('dataset',{});scene=json.loads(ds.get('scene','{}'));shots.append({'path':str(p.relative_to(R)),'sha256':sha(p),'progress':d.get('progress'),'phase':d.get('phase'),'root':scene.get('root'),'owner':scene.get('cameraOwner'),'data':str(j.relative_to(R))})
(E/'screenshot-index.json').write_text(json.dumps(shots,ensure_ascii=False,indent=2)+'\n')
rest=load(E/'after-left-return-restored.json');acu=load(E/'acupoint-after-motion-LU9-settled.json');final=load(E/'final-native-restored.json')
scene=lambda d:json.loads(d['canvas'][0]['dataset']['scene']);dataset=lambda d:json.loads(d['canvas'][0]['dataset']['dataset']);assert len(final['canvas'])==1;assert scene(rest)['root']==scene(acu)['root']==scene(final)['root'];assert scene(final)['cameraOwner'] is None and scene(final)['registeredUpdates']==0 and dataset(final)['motion'] is None
current=subprocess.check_output(['git','status','--porcelain=v1','-z','--untracked-files=all']);own_paths=['work/evidence/MV2/2026-10-12-q01-r1/','work/reports/MV2.md','work/EXECUTION.json','atlas-data/assets/motion/mv2-q01-r1-','atlas-data/motion/source-motion-repairs-r1.json','atlas-web/src/domain/sourceMotionRepairs','atlas-web/src/data/motionLearningData.ts','atlas-web/plugins/motionAssets.ts','atlas-web/plugins/motionAssets.test.ts']
def external(raw):
 return sorted(x.decode() for x in raw.split(b'\0') if x and not any(x[3:].decode().startswith(p) for p in own_paths))
assert external(current)==external((E/'start-status.z').read_bytes())
result={'passed':True,'startHead':start['head'],'inheritedTrackedWipFilesUnchanged':len(wip),'specifiedOriginalHashesUnchanged':len(inputs),'protectedHashesUnchanged':len(protected)-len(owned),'outOfScopeStatusUnchanged':True,'outOfScopeStatusEntries':len(external(current)),'onlyMV2ExecutionRecordChanged':True,'scheduledNextTask':'AT22','thisBundleAccepted':True,'wholeMV2Accepted':False,'remainingGroups':4,'remainingObservedAmbiguousMappings':32,'capturedUIScreenshots':len(shots),'actualSameSceneMotionToAcupointAndBack':True,'tests':20,'buildChecks':13,'syncCheck':True,'newUnresolvedApproval':False};(E/'validation-final.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
