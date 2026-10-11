import sys
from pathlib import Path
sys.path=[p for p in sys.path if Path(p or '.').resolve()!=Path(__file__).parent.resolve()]
exec((Path(__file__).parent/'author-lung.py').read_text().split('# First milestone:')[0])
sys.path.insert(0,str(R/'atlas-web/scripts'))
from nativeSurfaceIntersections import SurfaceIndex
keys=[k for k,r in rows.items() if not r.get('hardHoldReasons') and (r['kind'] in ['muscle','bone'] or 'fascia' in r['names']['en'].lower()) and k.startswith('ZA-c7010a9-')];surfaces={k:world(k) for k in keys}
for spec in read(E/'thenar-nail-config.json')['probeInputs']:
 b=(R/spec['path']).read_bytes();assert sha(b)==spec['sha256'];o=next(o for o in json.loads(b)['objects'] if o['name']==spec['object']);surfaces[spec['key']]=(np.array(o['positions']),np.array(o['indices'])[spec['triangleIds']])
index=SurfaceIndex(surfaces);p=R/'atlas-data/acupoints/carriers/lung-AT6-r1/manifest.json';mf=read(p);checks=[]
for c in mf['chunks']:
 b=(p.parent/c['file']).read_bytes();assert sha(b)==c['sha256'];v=np.frombuffer(b,dtype='<f4',count=c['vertices']*3).reshape(-1,3);ref=np.frombuffer(b,dtype='<f4',offset=c['vertices']*12,count=c['vertices']*3).reshape(-1,3);t=np.frombuffer(b,dtype='<u2',offset=c['vertices']*24).reshape(-1,3)
 assert sha(v.tobytes()+t.astype('<u4').tobytes())==c['topologySha256'];assert sha(ref.tobytes()+t.astype('<u4').tobytes())==c['referenceHash'];assert np.isfinite(v).all();assert len(t)==c['triangles'];assert t.max()<len(v)
 assert (v[:,0]<0).all() if c['side']=='right' else (v[:,0]>0).all()
 gap=np.linalg.norm(v-ref,axis=1);assert np.max(abs(gap-c['clearanceMetres']))<1e-6
 collisions=[{'triangle':i,'sources':hit} for i,tri in enumerate(v[t]) if (hit:=index.intersections(tri))];assert not collisions,(c['id'],collisions[:3])
 checks.append({'id':c['id'],'side':c['side'],'bytes':len(b),'triangles':len(t),'topologyHashVerified':True,'referenceHashVerified':True,'properNativeIntersections':0,'clearanceMetres':c['clearanceMetres'],'clearanceErrorMetres':float(np.max(abs(gap-c['clearanceMetres']))),'frame':mf['frameId'],'unit':mf['unit'],'poseId':mf['poseId']})
# Confirm independently generated wrist-to-AT3 seam, including original float32 edges, on both sides.
seams=[]
for side in ['right','left']:
 p1=R/'atlas-data/acupoints/carriers/education-r1';old=read(p1/'manifest.json');a=next(c for c in old['chunks'] if c['id']=='arm-'+side+'-0');bc=next(c for c in mf['chunks'] if c['id']=='wrist-link-'+side+'-0');av=np.frombuffer((p1/a['file']).read_bytes(),dtype='<f4',count=a['vertices']*3).reshape(-1,3);bv=np.frombuffer((p.parent/bc['file']).read_bytes(),dtype='<f4',count=bc['vertices']*3).reshape(-1,3);shared=set(map(tuple,av))&set(map(tuple,bv));assert len(shared)==40;seams.append({'side':side,'sharedExactFloat32Vertices':len(shared),'y':float(next(iter(shared))[1]),'noBridge':True})
(E/'geometry-validation-r1.json').write_text(json.dumps({'passed':True,'localActiveChecks':checks,'seams':seams,'wholeNativeSourceCount':len(surfaces),'sourceReadHashes':inputs,'skinAccuracy':'unresolved','professorReview':'not_performed'},indent=2)+'\n');print('passed',len(checks),'local chunks',sum(c['triangles'] for c in checks),'triangles; native intersections zero')
