import sys
from pathlib import Path
sys.path=[p for p in sys.path if Path(p or '.').resolve()!=Path(__file__).parent.resolve()]
exec((__import__('pathlib').Path(__file__).parent/'author-lung.py').read_text().split('# First milestone:')[0])
import sys
sys.path.insert(0,str(R/'atlas-web/scripts'))
from nativeSurfaceIntersections import SurfaceIndex
out=R/'atlas-data/acupoints/carriers/lung-fossa-r1';assert not out.exists()
# Actual anatomy surfaces, excluding held inputs, exactly as the common native-envelope generator.
keys=[k for k,r in rows.items() if not r.get('hardHoldReasons') and (r['kind'] in ['muscle','bone'] or 'fascia' in r['names']['en'].lower()) and k.startswith('ZA-c7010a9-')]
index=SurfaceIndex({k:world(k) for k in keys});chunks=[];records=[];failure=[]
for side in ['right','left']:
 refs=[('Clavicular head of pectoralis major muscle',375),('Clavicular part of deltoid muscle',1897),('Clavicular part of deltoid muscle',2462)]
 coords=[];addresses=[]
 for name,i in refs:
  k=find(name,side);g=geometry(k,side);a={'triangle':i,'barycentric':[1/3]*3};coords.append(at(g,a));addresses.append({'sourceKey':k,'name':name,'native':anchor(g,a,side),'world':at(g,a).tolist()})
 ref=np.array(coords,dtype='<f4');attempts=[];chosen=None
 for clearance in [.003,.004,.005,.006,.007,.008,.009,.010]:
  v=(ref+np.array([0,0,clearance])).astype('<f4');hits=index.intersections(v);attempts.append({'clearanceMetres':clearance,'properIntersections':hits})
  if not hits:chosen=(v,clearance);break
 record={'side':side,'sourceAddresses':addresses,'attempts':attempts,'construction':'Small local educational membrane between actual pectoral upper border and deltoid medial border, not a skin scan; +Z declared visual separation only','landmarkMeaning':'Depression/triangle medial to source-addressed coracoid and below clavicle; skin crease and actual nipple remain unobserved.'}
 if chosen is None:failure.append(record);continue
 v,clearance=chosen;ids=np.array([0,1,2] if side=='right' else [0,2,1],dtype='<u2');assert max(np.linalg.norm(v[a]-v[b]) for a,b in [(0,1),(1,2),(2,0)])<.030
 buf=v.tobytes()+ref.tobytes()+ids.tobytes();topo=sha(v.tobytes()+ids.astype('<u4').tobytes());rh=sha(ref.tobytes()+ids.astype('<u4').tobytes());cid='fossa-'+side+'-0';file=cid+'.bin'
 chunks.append({'id':cid,'family':'trunk','side':side,'label':'쇄골 아래 삼각 국소 교육 지표 면','revision':'AT6-fossa-r1','topologySha256':topo,'referenceHash':rh,'file':file,'sha256':sha(buf),'bytes':len(buf),'vertices':3,'triangles':1,'geometryBufferBytes':len(buf),'bounds':[v.min(0).tolist(),v.max(0).tolist()],'clearanceMetres':clearance});record.update({'chunk':cid,'clearanceMetres':clearance,'properIntersections':[]});records.append(record)
 if not out.exists():out.mkdir()
 (out/file).write_bytes(buf)
manifest={k:v for k,v in m.items() if k not in ['chunks','totalBytes','totalTriangles','totalGeometryBufferBytes']};manifest.update({'revision':'AT6-fossa-r1','chunks':chunks,'totalBytes':sum(c['bytes'] for c in chunks),'totalTriangles':len(chunks),'totalGeometryBufferBytes':sum(c['bytes'] for c in chunks),'method':'Explicit source-addressed local teaching membrane; whole-body native proper triangle collision check; not skin.'})
if chunks:(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
(E/'fossa-patch-build-r1.json').write_text(json.dumps({'records':records,'failed':failure,'sourceReadHashes':inputs,'collisionSurfaceCount':len(keys)},ensure_ascii=False,indent=2)+'\n');print('patches',len(chunks),'failed',len(failure))
