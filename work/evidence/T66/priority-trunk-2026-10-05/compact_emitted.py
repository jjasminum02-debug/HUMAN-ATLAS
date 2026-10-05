"""Remove unreferenced generated buffers, retaining every used accessor byte exactly."""
import pathlib,sys,json,copy,numpy as np
R=pathlib.Path(__file__).resolve().parents[4];O=pathlib.Path(__file__).parent
sys.path[:0]=[str(R/'work/tools'),str(R/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from verify_glb_interpolation import read_glb
from author_source_surface_motion import container
from derive_source_surface_motion import append_bytes,accessor_bytes,sha
save=lambda p,j:p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
for kind in sys.argv[1:]:
 d=O/kind;raw,old,binary=read_glb(d/'motion.glb');doc=copy.deepcopy(old);refs=[]
 for mesh in doc['meshes']:
  for p in mesh['primitives']:
   refs.extend((p['attributes'],s) for s in p['attributes'])
   if 'indices' in p:refs.append((p,'indices'))
   for target in p.get('targets',[]):refs.extend((target,s) for s in target)
 for skin in doc.get('skins',[]):
  if 'inverseBindMatrices' in skin:refs.append((skin,'inverseBindMatrices'))
 for anim in doc.get('animations',[]):
  used=sorted(set(c['sampler'] for c in anim['channels']));mapping={v:i for i,v in enumerate(used)};anim['samplers']=[anim['samplers'][i] for i in used]
  for c in anim['channels']:c['sampler']=mapping[c['sampler']]
  for s in anim['samplers']:refs.extend([(s,'input'),(s,'output')])
 used=sorted(set(obj[field] for obj,field in refs));mapping={v:i for i,v in enumerate(used)};doc['accessors']=[doc['accessors'][i] for i in used]
 for obj,field in refs:obj[field]=mapping[obj[field]]
 usedviews=sorted(set(a['bufferView'] for a in doc['accessors']));vmap={v:i for i,v in enumerate(usedviews)};buf=bytearray();views=[]
 for i in usedviews:
  v=copy.deepcopy(old['bufferViews'][i]);start=v.get('byteOffset',0);off,ln=append_bytes(buf,binary[start:start+v['byteLength']]);v.update(buffer=0,byteOffset=off,byteLength=ln);views.append(v)
 for a in doc['accessors']:a['bufferView']=vmap[a['bufferView']]
 doc['bufferViews']=views;doc['buffers']=[{'byteLength':len(buf)}];packed=container(doc,buf)
 for oldi,newi in mapping.items():assert accessor_bytes(old,binary,oldi)==accessor_bytes(doc,buf,newi),oldi
 # No quality/DOF/key reduction; all used typed arrays are byte-identical.
 (d/'motion.glb').write_bytes(packed);pose=json.loads((d/'glb-pose-qc.json').read_text());geo=json.loads((d/'geometry-record.json').read_text());inp=json.loads((d/'authored-input.json').read_text())
 for e in inp['surfaceFields']:
  p=d/('interpolation-'+e['sourceKey']+'.json');j=json.loads(p.read_text());j['motionGlbSha256']=sha(packed);j['unreferencedBufferCompactionReceipt']='compaction-receipt.json';save(p,j);next(r for r in pose['rows'] if r['sourceKey']==e['sourceKey'])['geometryQcSha256']=sha(p.read_bytes())
 pose['motionSha256']=sha(packed);geo['motionSha256']=sha(packed);save(d/'glb-pose-qc.json',pose);save(d/'geometry-record.json',geo)
 if (d/'complete.json').exists():
  c=json.loads((d/'complete.json').read_text());c['motionSha256']=sha(packed);save(d/'complete.json',c)
 receipt={'oldMotionSha256':sha(raw),'newMotionSha256':sha(packed),'beforeBytes':len(raw),'afterBytes':len(packed),'usedAccessorCount':len(mapping),'everyUsedAccessorByteIdentical':True,'geometryQualityAndKeysReduced':False};save(d/'compaction-receipt.json',receipt);print(kind,receipt,flush=True)
