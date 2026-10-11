import sys
from pathlib import Path
sys.path=[p for p in sys.path if Path(p or '.').resolve()!=Path(__file__).parent.resolve()]
exec((Path(__file__).parent/'author-lung.py').read_text().split('# First milestone:')[0])
sys.path.insert(0,str(R/'atlas-web/scripts'))
from nativeSurfaceIntersections import SurfaceIndex
previous=read(E/'bilateral-rules-r5.json');native=previous['inputs']['native'];keys=[k for k,r in rows.items() if not r.get('hardHoldReasons') and (r['kind'] in ['muscle','bone'] or 'fascia' in r['names']['en'].lower()) and k.startswith('ZA-c7010a9-')];surfaces={k:world(k) for k in keys}
for spec in read(E/'thenar-nail-config.json')['probeInputs']:
 raw=(R/spec['path']).read_bytes();assert sha(raw)==spec['sha256'];o=next(x for x in json.loads(raw)['objects'] if x['name']==spec['object']);surfaces[spec['key']]=(np.array(o['positions']),np.array(o['indices'])[spec['triangleIds']])
index=SurfaceIndex(surfaces);out=R/'atlas-data/acupoints/carriers/nail-indicator-r1';assert not out.exists();out.mkdir();chunks=[];records=[]
for side in ['right','left']:
 u=next(u for u in previous['units'] if u['code']=='LU11' and u['side']==side);g=native[u['landmarks'][0]['sourceKey']];a=u['landmarks'][0]['native'];corner=at(g,a)
 ph=native[find('Distal phalanx of first finger of hand',side)];prox=at(ph,{'triangle':92,'barycentric':[1/3]*3})-at(ph,{'triangle':49,'barycentric':[1/3]*3});prox/=np.linalg.norm(prox)
 pp=native[find('Proximal phalanx of first finger of hand',side)];radial=at(pp,{'triangle':10,'barycentric':[1/3]*3})-at(pp,{'triangle':140,'barycentric':[1/3]*3});radial-=prox*np.dot(radial,prox);radial/=np.linalg.norm(radial);direction=prox+radial;direction/=np.linalg.norm(direction)
 assert (direction[0]<0 if side=='right' else direction[0]>0) and direction[1]>0
 z=np.array([0,0,.0005]);ref=np.array([corner-z,corner+direction*.004-z,corner+z,corner+direction*.004+z],dtype='<f4');v=(ref+radial*.0007).astype('<f4');t=np.array([[0,1,2],[1,3,2]],dtype='<u2')
 collisions=[index.intersections(v[f]) for f in t];assert not any(collisions),collisions
 buf=v.tobytes()+ref.tobytes()+t.tobytes();cid='nail-indicator-'+side+'-0';file=cid+'.bin';(out/file).write_bytes(buf)
 chunks.append({'id':cid,'family':'nail','label':'엄지 조갑각 근위·요측 국소 교육 지표 면','side':side,'revision':'AT6-nail-native-directions-r1','topologySha256':sha(v.tobytes()+t.astype('<u4').tobytes()),'referenceHash':sha(ref.tobytes()+t.astype('<u4').tobytes()),'file':file,'sha256':sha(buf),'bytes':len(buf),'vertices':4,'triangles':2,'geometryBufferBytes':len(buf),'bounds':[v.min(0).tolist(),v.max(0).tolist()],'clearanceMetres':.0007})
 records.append({'side':side,'sourceCorner':a,'cornerWorld':corner.tolist(),'proximalSourceFaces':[49,92],'radialSourceFaces':[10,140],'proximal':prox.tolist(),'radial':radial.tolist(),'pathDirection':direction.tolist(),'properNativeIntersections':collisions,'method':'Explicit source-addressed small teaching membrane at radial nail-base corner; native phalangeal axis and IP radial/ulnar references determine directions. Reference interior is AI authored, not observed skin.','lengthMetres':.004,'widthMetres':.001,'visualClearanceMetres':.0007})
mf={k:v for k,v in m.items() if k not in ['chunks','totalBytes','totalTriangles','totalGeometryBufferBytes']};mf.update(revision='AT6-nail-indicator-r1',chunks=chunks,totalBytes=sum(c['bytes'] for c in chunks),totalTriangles=4,totalGeometryBufferBytes=sum(c['bytes'] for c in chunks));(out/'manifest.json').write_text(json.dumps(mf,ensure_ascii=False,indent=2)+'\n');(E/'nail-membrane-build-r1.json').write_text(json.dumps({'records':records,'collisionSurfaceCount':len(surfaces),'sourceReadHashes':inputs},indent=2)+'\n');print('native nail membranes',len(chunks))
