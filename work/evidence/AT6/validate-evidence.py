from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parents[3];E=Path(__file__).parent
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
baseline=read(E/'baseline.json');inputs=read(E/'input-hashes.json')
assert all(sha(R/p)==h for p,h in inputs.items())
assert all(sha(R/p)==h for p,h in baseline['trackedWipHashes'].items())
package=read(R/'atlas-data/acupoints/learner/lung.json');receipt=read(E/'compiler/receipt.json');ledger=read(E/'compiler/ledger.json');probes=read(E/'surface-probes.json')
assert len(receipt['failed'])==22 and receipt['localLearnerEligible']==0 and receipt['fixtureExports']==0 and receipt['originalPreserved']
assert package['projections']==[] and package['precisionCounts']=={'precise':0,'educationalApproximation':0,'unresolved':22}
assert len(probes)==22 and all(u['assessment']['author']=='ai' and u['assessment']['precision']=='unresolved' for u in ledger['units'].values())
assert all(u['assessment']['technical']=='passed' and u['assessment']['checks']['side'] for u in ledger['units'].values())
def capture(name):
 d=read(E/(name+'.json'));a=d['canvas'][0]['attrs'];return d,readstr(a['data-scene']),readstr(a['data-dataset']),readstr(a.get('data-acupoint-projection','{}'))
readstr=json.loads
base,bs,bd,bp=capture('learner-baseline'); roots=set();counts=0
names=[c['nameKo'] for c in package['concepts']]
for side in ['right','left']:
 for k in range(1,12):
  d,s,ds,p=capture(f'learner-{side}-LU{k}');roots.add(s['root']);assert d['canvasCount']==1
  assert p['mode']=='learner' and p['side']==side and p['selection']=={'kind':'acupoint','code':f'LU{k}','side':side}
  assert p['rendered']==[] and p['localLearnerEligible']==0 and p['fixtureExports']==0 and d['labels']==0
  assert names[k-1]+f' · LU{k}' in d['card'] and ('오른쪽' if side=='right' else '왼쪽') in d['card']
  for key in ['camera','target','geometryBuffersBytes','registeredUpdates','cameraOwner','renderer']:assert s[key]==bs[key],key
  for key in ['selected','hidden','translucent','motion','nerveLayer']:assert ds[key]==bd[key],key
  counts+=1
assert roots=={bs['root']}
_,fb,fd,_=capture('final-baseline')
for name in ['learner-rapid-off','learner-immediate-close']:
 d,s,ds,p=capture(name);assert s['root']==fb['root'] and d['labels']==0 and p=={}
 for k in ['camera','target','geometryBuffersBytes','registeredUpdates','cameraOwner']:assert s[k]==fb[k],k
 assert ds['selected']==fd['selected']
assert capture('native-pick-ready')[2]['selected']=='ZA-c7010a9-2ea5931bed7570848730b3f4'
assert capture('native-pick-ready')[3]=={}
for width in [390,1024,1440]:
 d,s,ds,p=capture(f'learner-{width}-LU9');assert p['selection']['code']=='LU9' and d['labels']==0
assets=R/'atlas-web/dist/assets';j={p.name:p.stat().st_size for p in assets.glob('*.js')};initial=sum(v for k,v in j.items() if k.startswith(('App-','index-')))
js='\n'.join(p.read_text() for p in assets.glob('*.js'))
assert not any(marker in js for marker in ['FIXTURE-','right-learning.json','left-learning.json','WHO Standard Acupuncture Point Locations','work/evidence','technical_fixture'])
assert not list(assets.glob('*learning*.json'))
assert initial<=2*1024*1024
m=read(R/'atlas-data/acupoints/carriers/education-r1/manifest.json'); assert len(m['chunks'])==83 and m['totalBytes']==813096 and m['totalTriangles']==40520
result={'acceptancePassed':False,'engineeringValidationPassed':True,'realInputUnits':22,'concepts':11,'actualCardSelections':counts,'preciseLocations':0,'educationalApproximationLocations':0,'unresolvedLocations':22,'fixtureExports':0,'actualTopologyRayAddresses':sum(p['surfaceProbe'] is not None for p in probes),'sourceGeometryObjectsRead':22,'learnerRoot':bs['root'],'transitionAndNativePickRoot':fb['root'],'newLearnerGeometryBytes':0,'newLearnerTriangles':0,'learnerDataBytes':(R/'atlas-data/acupoints/learner/lung.json').stat().st_size,'initialJsBytes':initial,'initialJsDeltaVsAT5':initial-1324012,'registeredCarrierBytes':m['totalBytes'],'registeredCarrierTriangles':m['totalTriangles'],'newSceneOrBody':False,'WipTrackedHashesPreserved':len(baseline['trackedWipHashes']),'historicalAndSourceHashesPreserved':len(inputs),'plannedSuccessor':'AT7','nextEligibleUnit':'AT6','budgetIncrease':False}
(E/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
