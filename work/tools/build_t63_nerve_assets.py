"""Compile evaluated native surfaces through the common bounded chunk compiler."""
import hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(b):return hashlib.sha256(b).hexdigest()
def save(p,v):(ROOT/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
spec=importlib.util.spec_from_file_location('pack',ROOT/'atlas-data/tools/datasets/pack.py'); pack=importlib.util.module_from_spec(spec);spec.loader.exec_module(pack)
evaluated=json.loads((ROOT/'work/evidence/T63/evaluated-surfaces.json').read_text()); registry=json.loads((ROOT/'atlas-data/overlays/nerve-support-t62.json').read_text())
identity=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]
pose='za-c7010a9-9f08a17ea011-frame0-static'
rows=evaluated['rows']; resources={}; instances=[]
for row in rows:
 p=ROOT/row['path'];assert sha(p.read_bytes())==row['sha256']; key=row['sourceKey']; c=row['sourceToAtlas']
 resources[key]={**{k:row[k] for k in ['sha256','vertices','triangles','geometryBytes']},'path':str(p)}
 lod={k:row[k] for k in ['vertices','triangles','geometryBytes']};lod['resource']=key
 instances.append({'sourceKey':key,'sourceName':row['name'],'kind':'nerve_surface','matrix':[c[col+rr*4] for col in range(4) for rr in range(4)],'lods':{'overview':lod,'detail':lod},'sourceNamespace':'za-c7010a9','geometrySpace':'source_local','canonicalConceptId':None,'learnerBinding':'source_only_unbound','defaultLearnerVisible':False,'appDisplayRights':'held_not_approved_by_this_task','publicRedistribution':'held','humanReview':'not_performed','sourceHiddenStatePreserved':{'hideRender':row['hideRender'],'hideViewport':row['hideViewport']}})
dataset=pack.compile_dataset({'namespace':'za-c7010a9','revision':'za-verified-nerve-surfaces-v1','unit':'m','geometrySpace':'source_local','localOnly':True,'publicRedistribution':'held','instances':instances,'resources':resources}, ROOT/'atlas-data/assets/derived-glb/za-nerve-t63/chunks')
proofpath='work/evidence/T63/evaluated-surfaces.json'; proofhash=sha((ROOT/proofpath).read_bytes())
for row in rows:
 n=next(n for n in registry['instances'] if n['id']==row['instanceId'])
 g={'kind':'curve','assetPath':row['path'],'assetSha256':row['sha256'],'topologySha256':row['topologySha256'],'sourceNamespace':n['sourceNamespace'],'sourceFrameId':'ZA_RH_M_XLEFT_YPOSTERIOR_ZSUPERIOR','sourcePoseId':pose,'sourceUnit':'m','targetFrameId':'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR','geometrySpace':'source_world','sourceObjectToWorld':identity,'sourceToAtlas':row['sourceToAtlas'],'transformKind':'same_source_axis_conversion','evidenceIds':[],'registrationEvidenceIds':[],'validatedPoseIds':[pose]}
 signature=json.dumps([g[k] for k in ['assetSha256','topologySha256','sourceNamespace','sourceFrameId','sourcePoseId','sourceUnit','targetFrameId','geometrySpace','sourceObjectToWorld','sourceToAtlas','transformKind']],separators=(',',':'))
 # Python floats serialize with .0 while JS JSON.stringify uses integer spelling.
 signature=json.dumps([g[k] for k in ['assetSha256','topologySha256','sourceNamespace','sourceFrameId','sourcePoseId','sourceUnit','targetFrameId','geometrySpace','sourceObjectToWorld','sourceToAtlas','transformKind']],separators=(',',':')).replace('.0,',',').replace('.0]',']')
 for predicate in ['frame','placement','pose']:
  ev={'id':n['id']+':t63-'+predicate,'sourcePath':proofpath,'sourceSha256':proofhash,'locator':'rows[instanceId='+n['id']+']; original Curve evaluation at frame 0, source-world bake, axis conversion once; scope is this source course only','subjectId':n['id'],'predicate':predicate,'objectId':pose if predicate=='pose' else g['assetSha256'],'status':'verified_local'}
  if predicate=='frame':ev['value']=signature
  registry['evidence'].append(ev); g['evidenceIds'].append(ev['id'])
 n['geometry']=g;n['localSelection']='verified_geometry'
registry['contractRevision']='T63-source-native-static-geometry-2026-10-01'
save('atlas-data/overlays/nerve-support-t63.json',registry)
readme='work/evidence/T98/astra-resolution-2026-09-29/source-readme.md'
rights={'id':'ZA-fibular-local-prototype-2026-10-01','sourceSha256':evaluated['sourceSha256'],'sourceRevision':'c7010a903b75a2fd24a13b1c2c4c3546a9223780','readme':{'path':readme,'sha256':sha((ROOT/readme).read_bytes())},'allowedSourceKeys':[r['sourceKey'] for r in rows], 'exceptionReview':'Exact peripheral Common/Deep/Superficial fibular Curve objects and Nerves/Peripheral nervous system/lower-limb collections. No cranial-nerve, white-matter, inner-ear or kidney exception collection occurs. Pinned source family derivative permission used for local educational observation only. Original render-hidden flag is retained independently. No public license grant added.','localUseRights':'supported_local_prototype','sourceOnly':True,'humanReview':'not_performed','publicRedistribution':'held'}
save('work/evidence/T63/local-use-rights.json',rights)
inputs=['atlas-data/overlays/nerve-support-t62.json',proofpath,'atlas-data/overlays/nerve-support-t63.json','work/evidence/T63/local-use-rights.json','atlas-data/assets/derived-glb/za-nerve-t63/chunks/manifest.json']
inputs += [readme]
inputs+=sorted({e['sourcePath'] for e in registry['evidence']})
inputs+= [r['path'] for r in rows]
for chunk in dataset['chunks']:inputs.append('atlas-data/assets/derived-glb/za-nerve-t63/chunks/'+chunk['id']+'.glb')
save('atlas-data/manifests/nerve-scene-t63.json',{'schemaVersion':1,'revision':'nerve-scene-v1','registryPath':'atlas-data/overlays/nerve-support-t63.json','datasetPath':'atlas-data/assets/derived-glb/za-nerve-t63/chunks/manifest.json','rightsPath':'work/evidence/T63/local-use-rights.json','inputSha256':{p:sha((ROOT/p).read_bytes()) for p in sorted(set(inputs))},'objects':[{k:r[k] for k in ['instanceId','sourceKey','bounds','name','path','sha256','topologySha256']} for r in rows]})
print(json.dumps(dataset['metrics']))
