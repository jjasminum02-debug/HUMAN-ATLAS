"""Read-only check against original GLBs, frozen hashes and per-item display decisions."""
import json, hashlib, struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'atlas-data/source-cache/bodyparts3d-r4/converted/t77'
M=ROOT/'atlas-data/manifests/bodyparts3d-r4-t77'
def read_glb(p):
 raw=p.read_bytes(); n=struct.unpack_from('<I',raw,12)[0];return json.loads(raw[20:20+n]),raw[28+n:]
def payload(g,b,n):
 p=g['meshes'][n['mesh']]['primitives'][0];parts=[]
 for key in list(p['attributes'].values())+[p['indices']]:
  a=g['accessors'][key];v=g['bufferViews'][a['bufferView']];parts.append(b[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']])
 return hashlib.sha256(b''.join(parts)).hexdigest()
def verify():
 lock=json.loads((M/'input-lock.json').read_text());manifest=json.loads((D/'manifest.json').read_text());policy=json.loads((M/'display-policy.json').read_text())['items'];original={}
 for p,h in lock.items():
  raw=(ROOT/p).read_bytes();assert hashlib.sha256(raw).hexdigest()==h,p
  if p.endswith('.glb'):
   g,b=read_glb(ROOT/p)
   for n in g['nodes']:
    if 'mesh' not in n:continue
    id=n['extras']['sourceFileId'];value=payload(g,b,n)
    if id in original:assert original[id]==value
    original[id]=value
 seen=set();triangle_count=0;active=0;bound=[];held=[]
 for c in manifest['chunks']:
  path=D/(c['id']+'.glb');assert hashlib.sha256(path.read_bytes()).hexdigest()==c['sha256'];g,b=read_glb(path)
  assert len(g['nodes'])==len(c['assets']);assert len(g['scenes'])==1
  for n,a in zip(g['nodes'],c['assets']):
   id=a['id'];assert id not in seen;seen.add(id)
   assert n['name']==a['nodeId']=='HA-MESH-BP3D4-'+id
   assert n['extras']['sourceSha256']==a['sourceSha256']
   assert payload(g,b,n)==original[id],id
   assert a['localDisplay']==policy[id] and a['humanReviewed'] is False and a['publicRedistribution']=='held'
   assert a['holdReasons']==policy[id]['retainedHoldReasons']
   if a['defaultVisible']:active+=1;assert not policy[id]['integrityHolds']
   else:held.append(id)
   if a['stableIds']:bound.append(id);assert a['pickState']=='existing_binding_unreviewed'
   else:assert a['pickState']!='existing_binding_unreviewed'
   triangle_count+=g['accessors'][g['meshes'][n['mesh']]['primitives'][0]['indices']]['count']//3
 old=json.loads((ROOT/'atlas-data/source-cache/bodyparts3d-r4/converted/t56/manifest.json').read_text());oa={a['id']:a for c in old['chunks'] for a in c['assets']}
 current={a['id']:a for c in manifest['chunks'] for a in c['assets']}
 for id,a in oa.items():
  for field in ['nodeId','sourceSha256','side','stableIds','pickState','holdReasons','humanReviewed','regions','bounds']:assert a[field]==current[id][field],(id,field)
 assert len(seen)==543 and active==531 and len(bound)==10 and len(held)==12
 assert set(held)=={id for id,a in oa.items() if a['pickState']=='held'}
 for id in ['FJ3157','FJ3159','FJ3162','FJ3165','FJ3168','FJ3393']:assert current[id]['defaultVisible'] and current[id]['pickState']=='source_only_unbound'
 assert manifest['wholeBodyDenominator'] is None and manifest['visualCoverage']=='partial'
 assert manifest['missingTargets']==[{'name':'latissimus dorsi','state':'missing','decision':'T94:no_exact_source_found','geometry':None,'binding':None}]
 return {'status':'passed','lockedInputs':len(lock),'uniqueNodes':len(seen),'defaultVisible':active,'heldHidden':held,'unchangedBindings':bound,'newSourceNodes':30,'explicitDisplayChanges':sum(not a['beforeDefaultVisible'] and a['afterDefaultVisible'] for a in policy.values()),'trianglesIncludingHeld':triangle_count,'geometryBytesUnchanged':True,'historicalFieldsUnchanged':True,'visualCoverage':'partial','wholeBodyDenominator':None}
if __name__=='__main__': print(json.dumps(verify(),indent=2))
