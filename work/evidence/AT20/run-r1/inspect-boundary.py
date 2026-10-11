"""Replay actual native landmarks, binary carrier and contour; scientific SVG evidence only."""
from pathlib import Path
import ast, struct, hashlib, json, sys
sys.dont_write_bytecode = True
import numpy as np

R=Path(__file__).resolve().parents[4]; E=Path(__file__).parent
read=lambda p:json.loads(p.read_text()); sha=lambda b:hashlib.sha256(b).hexdigest()
cache=R/'atlas-data/source-cache/datasets/za'; inputs={};meshes={}
# Reuse only the AC1 GLB/world reader, never execute its historical authoring main.
fn=next(n for n in ast.parse((R/'work/evidence/acupoint-AC1/build_carrier.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='world')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'AC1-world-reader','exec'),globals())
rules=read(R/'work/evidence/AT6/resume-r1/bilateral-rules-r9.json'); d=read(R/'atlas-data/acupoints/territories/AT20-r1/lung-forearm-right-boundary-r1.json')
m=read(R/d['carrierBinding']['manifest']); chunk=next(c for c in m['chunks'] if c['id']==d['carrierBinding']['id']);binary=(R/d['carrierBinding']['manifest']).parent/chunk['file'];b=binary.read_bytes()
assert sha((R/d['carrierBinding']['manifest']).read_bytes())==d['carrierBinding']['manifestSha256']
assert sha((R/d['construction']['generationReference']).read_bytes())==d['construction']['generationSha256']
assert all(sha((R/l['inputFile']).read_bytes())==l['inputSha256'] for l in d['landmarks'])
assert sha(b)==chunk['sha256']
v=np.frombuffer(b,dtype='<f4',count=chunk['vertices']*3).reshape(-1,3)
basis=np.frombuffer(b,dtype='<f4',offset=chunk['vertices']*12,count=chunk['vertices']*3).reshape(-1,3)
t=np.frombuffer(b,dtype='<u2',offset=chunk['vertices']*24).reshape(-1,3).astype('<u4')
assert sha(v.tobytes()+t.tobytes())==d['carrierBinding']['topologySha256']
assert np.array_equal(v.ravel(),rules['inputs']['carriers'][chunk['id']]['positions'])
assert np.array_equal(t.ravel(),rules['inputs']['carriers'][chunk['id']]['indices'])
native_replay=[]
for l in d['landmarks']:
 g=rules['inputs']['native'][l['sourceKey']];nv,nt=world(l['sourceKey']);assert sha(nv.astype('<f4').tobytes()+nt.astype('<u4').tobytes())==g['topologySha256']
 a=l['native'];point=np.array(a['barycentric'])@nv[nt[a['triangle']]]
 nv2=np.array(g['positions']).reshape(-1,3);nt2=np.array(g['indices']).reshape(-1,3);expected=np.array(a['barycentric'])@nv2[nt2[a['triangle']]]
 error=float(np.linalg.norm(point-expected));assert error<1e-7
 native_replay.append({'id':l['id'],'sourceKey':l['sourceKey'],'triangle':a['triangle'],'worldPosition':point.tolist(),'errorMetres':error,'originalSkinObserved':False,'modelIndicator':l.get('modelIndicator')})
gen=read(R/'work/evidence/AT3/generation.json');mp=np.array(gen['chunkSourceGridMappings'][chunk['id']]);angle=mp%40;level=mp//40
selected=np.all((angle[t]<=12)&(level[t]>=1)&(level[t]<=16),axis=1);faceIds=np.flatnonzero(selected);tri=v[t[selected]]
assert len(faceIds)==d['handoff']['expectedFaceCountForReplay'] and sha(faceIds.astype('<u4').tobytes())==d['handoff']['candidateFaceSetSha256']
lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1))
contexts=read(R/'atlas-data/acupoints/observation/lung-context-r1.json')['contexts']
points=[c for c in contexts if c['side']=='right' and c['code'] in ['LU6','LU7','LU8']]
ledger=read(R/'work/evidence/AT6/resume-r1/bilateral-compiler-r8/ledger.json')
for c in points:
 i=ledger['units'][c['code']+'-right']['instance'];assert i['triangle'] in faceIds
 assert c['placementBinding']['carrierHash']==chunk['topologySha256']

# AT3's actual ZA collision universe whose catalog boxes overlap the examined patch.
rows={r['sourceKey']:r for r in read(R/'work/evidence/acupoint-AC1/runtime-integration.json')['objects']}
local=[]
for key,row in rows.items():
 if key not in gen['collisionSourceKeys'] or row['side']!='right' or row['hardHoldReasons']:continue
 a,z=np.array(row['bounds'])
 if np.all(z>=lo-.005) and np.all(a<=hi+.005):
  nv,nt=world(key);local.append((key,row['names']['en'],nv,nt))
sys.path.insert(0,str(R/'atlas-web/scripts'))
from nativeSurfaceIntersections import SurfaceIndex
index=SurfaceIndex({key:(nv,nt) for key,_,nv,nt in local})
collisions=[{'triangle':int(fi),'sourceKeys':index.intersections(v[t[fi]])} for fi in faceIds]
collisions=[c for c in collisions if c['sourceKeys']];assert not collisions

# Source-derived native support addresses per boundary vertex, including visual clearance.
hits=read(R/'work/evidence/AT3/native-hits.json')['arm-right'];controls=[]
for loop in d['components'][0]['loops']:
 for c in loop['controls']:
  h=hits[int(mp[c['vertex']])];assert h is not None
  nv,nt=world(h['sourceKey']);reference=np.array(h['barycentric'])@nv[nt[h['triangle']]]
  error=float(np.linalg.norm(reference-basis[c['vertex']]));assert error<1e-7
  controls.append({'id':c['id'],'role':loop['role'],'sourceKey':h['sourceKey'],'nativeTriangle':h['triangle'],'nativeBarycentric':h['barycentric'],'surfacePosition':v[c['vertex']].tolist(),'nativeReferencePosition':reference.tolist(),'basisReplayErrorMetres':error,'clearanceMetres':float(np.linalg.norm(v[c['vertex']]-reference)),'clearanceIsSkinThickness':False})
audit={'carrierBinary':str(binary.relative_to(R)),'binarySha256':sha(b),'topologySha256':chunk['topologySha256'],'frame':m['frameId'],'unit':m['unit'],'pose':m['poseId'],'side':'right','nativeLandmarkReplay':native_replay,'boundaryNativeSupport':controls,'sourceReadHashes':inputs,'localNativeObjects':len(local),'properNativeTriangleIntersections':len(collisions),'examinedFaces':len(faceIds),'loops':[len(l['controls']) for l in d['components'][0]['loops']],'bounds':[lo.tolist(),hi.tolist()],'linkedPointsCovered':[p['code'] for p in points],'masksExported':0,'leftReflected':False,'graphicsCost':{'newRuntimeBytes':0,'newRuntimeTriangles':0,'newRuntimeGPUBufferBytes':0,'newDrawCalls':0,'sharedCarrierEncodedBytes':len(b),'sharedCarrierTriangles':len(t),'prospectiveMaskUint32Float32Bytes':len(faceIds)*8,'driverVRAMMeasured':False},'limitations':['scientific contour figure, not learner mask renderer QA','native support and clearance do not establish cutaneous or classical sinew boundary','two exclusion loops preserved; proximal native-envelope pinch excluded']}
(E/'surface-inspection-r1.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')

# Code-native vector figure: actual coordinates, three views, no generated anatomy or image edit.
from PIL import Image, ImageDraw, ImageFont
im=Image.new('RGB',(1100,740),'#f5f7f6');draw=ImageDraw.Draw(im);font=ImageFont.load_default(size=15)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="740" viewBox="0 0 1100 740"><rect width="1100" height="740" fill="#f5f7f6"/>']
def text(x,y,s,size=15):
 draw.text((x,y),s,fill='#263c38',font=ImageFont.load_default(size=size));svg.append(f'<text x="{x}" y="{y+size}" fill="#263c38" font-family="sans-serif" font-size="{size}">{s}</text>')
def line(ps,colour,width):
 ps=[tuple(p) for p in ps];draw.line(ps,fill=colour,width=max(1,round(width)));svg.append('<polyline points="'+ ' '.join(f'{x:.2f},{y:.2f}' for x,y in ps)+f'" stroke="{colour}" stroke-width="{width}" fill="none"/>')
text(35,20,'LU right forearm: AI learning contour input (not skin / not final mask)',21)
scale=500/(hi[1]-lo[1]+.025)
for panel,(dim,label) in enumerate(zip([0,2,0],['Anterior (+Z)','Right lateral (-X)','Posterior (-Z)'])):
 center=190+360*panel;text(center-135,65,label,18)
 def project(ps):
  a=np.asarray(ps);x=(a[:,dim]-(lo[dim]+hi[dim])/2)*scale*(-1 if panel==2 else 1)+center;y=(hi[1]+.0125-a[:,1])*scale+120
  return np.column_stack([x,y])
 for key,name,nv,nt in local:
  good=np.all((nv[nt]>=lo-.01)&(nv[nt]<=hi+.01),axis=(1,2));ts=nv[nt[good]][::3]
  for tr in ts:line(project(tr[[0,1,2,0]]),'#c1cac5',.35)
 for tr in tri:line(project(tr[[0,1,2,0]]),'#c2d3d5',.35)
 for loop in d['components'][0]['loops']:
  ps=v[[c['vertex'] for c in loop['controls']]+[loop['controls'][0]['vertex']]]
  line(project(ps),'#bc6b34' if loop['role']=='outer' else '#954564',2.2)
 for p in points:
  x,y=project([p['point']])[0];draw.ellipse((x-3,y-3,x+3,y+3),fill='#183f44');svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3" fill="#183f44"/>');text(x+6,y-18,p['code'])
 text(center-130,643,'Y .87451 to 1.00213 m | '+('Z' if dim==2 else 'X')+' horizontal',13)
text(35,680,'Orange: outer boundary | Purple: two excluded holes | Gray: actual native surface wire samples',14)
text(35,707,'Includes occluded structures. Runtime depth, alpha and colour-mask QA belong to AT21.',14)
svg.append('</svg>');(E/'boundary-native-three-views-r1.svg').write_text('\n'.join(svg)+'\n');im.save(E/'boundary-native-three-views-r1.png')
print('PASS: actual carrier binary, native annotations',len(native_replay),'source support65, covered LU6/7/8, proper intersections0; no mask export')
