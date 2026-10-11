"""AC1 bounded, source-bound teaching patches. No source writes or external coordinates."""
from pathlib import Path
import json,hashlib,struct
import numpy as np
R=Path(__file__).resolve().parents[3]; O=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text()); sha=lambda b:hashlib.sha256(b).hexdigest()
dataset=read(O/'runtime-dataset.json'); overlay=read(O/'runtime-integration.json')
rows={r['sourceKey']:r for r in overlay['objects']}; instances={r['sourceKey']:r for r in dataset['instances']}
cache=R/'atlas-data/source-cache/datasets/za'
def key(name):
 matches=[r for r in rows.values() if r['side']=='right' and r['names']['en']==name];assert len(matches)==1;return matches[0]['sourceKey']
inputs={}; meshes={}
def world(k):
 if k in meshes:return meshes[k]
 u=read(cache/'units'/f'{k}.json');l=u['lods']['detail'];p=cache/l['path'];b=p.read_bytes();assert sha(b)==l['sha256'];inputs[str(p.relative_to(R))]=sha(b)
 size=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+size]);start=28+size
 def arr(ai):
  a=d['accessors'][ai];v=d['bufferViews'][a['bufferView']];dtype={5126:'<f4',5123:'<u2',5125:'<u4'}[a['componentType']];n={'VEC3':3,'SCALAR':1}[a['type']]
  return np.frombuffer(b,dtype=dtype,count=a['count']*n,offset=start+v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,n)
 prim=d['meshes'][0]['primitives'][0];v=arr(prim['attributes']['POSITION']).astype('f8');t=arr(prim['indices']).reshape(-1,3)
 m=np.array(u['matrix']).reshape(4,4,order='F');v=(np.c_[v,np.ones(len(v))]@m.T)[:,:3];meshes[k]=(v,t);return v,t
probe=read(O/'source-probe.json');nail=probe['objects'][0];peri=probe['objects'][1]
# Thumb identified by overlap with independently mapped right first distal hand phalanx.
thumb=key('Distal phalanx of first finger of hand');tb=rows[thumb]['bounds']
comp=[c for c in nail['components'] if c['bounds'][0][1]>.75 and c['bounds'][0][0]<-.33];assert len(comp)==1
nb=comp[0]['bounds']
clav=rows[key('Clavicle')]['bounds']; first=rows[key('Costal cartilage of first rib')]['bounds']; second=rows[key('Costal cartilage of second rib')]['bounds']
rad=rows[key('Radius')]['bounds']; scaph=rows[key('Scaphoid bone')]['bounds']
# These normalized landmark-envelope proposals do not implement B-cun/F-cun.
chestXY=[clav[0][0]+.1*(clav[1][0]-clav[0][0]),(first[0][1]+second[1][1])/2]
wristXY=[(rad[0][0]+scaph[0][0])/2,(rad[0][1]+scaph[1][1])/2]
thumbXY=[nb[0][0]+.25*(nb[1][0]-nb[0][0]),nb[1][1]-.07*(nb[1][1]-nb[0][1])]
plans=[('LU1','중부','Zhongfu',chestXY,.025,[key('Clavicular head of pectoralis major muscle'),key('Sternocostal head of pectoralis major muscle'),key('Pectoral fascia')],['Clavicle','First rib','Second rib'],['first-intercostal lateral surface and individual 6 B-cun not validated']),
 ('LU9','태연','Taiyuan',wristXY,.013,[key('Radius'),key('Scaphoid bone'),key('Abductor pollicis longus'),key('Abductor pollicis brevis')],['Radius','Scaphoid bone','Abductor pollicis longus'],['wrist crease, radial artery and tendon depression not resolved']),
 ('LU11','소상','Shaoshang',thumbXY,.006,[thumb],['Distal phalanx of first finger of hand'],['radial nail corner direction and individual 0.1 F-cun not validated'])]
positions=[];indices=[];patches=[];points=[];audit=[]
for code,name,roman,xy,size,ks,lms,missing in plans:
 vs=[];ts=[]
 for k in ks:
  v,t=world(k);ts.append(v[t]);vs.append(v)
 if code=='LU11':
  for obj in [nail,peri]:
   v=np.array(obj['positions']);t=np.array(obj['indices']);ts.append(v[t]);vs.append(v)
 triangles=np.concatenate(ts);allv=np.concatenate(vs);tri=triangles.copy()
 den=(tri[:,1,1]-tri[:,2,1])*(tri[:,0,0]-tri[:,2,0])+(tri[:,2,0]-tri[:,1,0])*(tri[:,0,1]-tri[:,2,1]);valid=abs(den)>1e-12;tri=tri[valid];den=den[valid]
 start=len(positions)//3;first=len(indices)//3;grid=17;fallback=0;clearance=.004 if code!='LU11' else .001
 for j in range(grid):
  for i in range(grid):
   x=xy[0]+size*(i/(grid-1)*2-1);y=xy[1]+size*(j/(grid-1)*2-1)
   a=((tri[:,1,1]-tri[:,2,1])*(x-tri[:,2,0])+(tri[:,2,0]-tri[:,1,0])*(y-tri[:,2,1]))/den
   b=((tri[:,2,1]-tri[:,0,1])*(x-tri[:,2,0])+(tri[:,0,0]-tri[:,2,0])*(y-tri[:,2,1]))/den;c=1-a-b;hit=(a>=0)&(b>=0)&(c>=0)
   if hit.any():z=float(np.max((a*tri[:,0,2]+b*tri[:,1,2]+c*tri[:,2,2])[hit]))
   else:
    near=np.argmin(np.sum((allv[:,:2]-[x,y])**2,axis=1));z=float(allv[near,2]);fallback+=1
   positions.extend([x,y,z+clearance])
 for j in range(grid-1):
  for i in range(grid-1):
   a=start+j*grid+i;indices.extend([a,a+1,a+grid,a+1,a+grid+1,a+grid])
 # A stable triangle at center; binding is an AI placement proposal, not accepted point.
 triangle=first+((grid//2)*(grid-1)+grid//2)*2
 patches.append({'code':code,'firstTriangle':first,'triangleCount':512,'clearanceMetres':clearance,'nearestFallbackVertices':fallback})
 lkeys=[key(n) for n in lms]
 points.append({'code':code,'side':'right','triangle':triangle,'barycentric':[1,0,0],'landmarkSourceKeys':lkeys,'locationValidation':'unresolved','aiProposal':True,'professorReview':'not_performed','missing':missing})
 audit.append({'code':code,'inputSourceKeys':ks,'landmarks':[{'sourceKey':k,'name':rows[k]['names']['en'],'side':rows[k]['side'],'bounds':rows[k]['bounds']} for k in lkeys],'xyProposal':xy,'clearanceMetres':clearance,'fallbackVertices':fallback})
p=np.array(positions,dtype='<f4');idx=np.array(indices,dtype='<u4');h=sha(p.tobytes()+idx.tobytes())
carrier={'id':'za-right-learning-patches','revision':'AC1-r1','topologySha256':h,'datasetRevision':dataset['revision'],'frameId':dataset['frameContract']['targetFrameId'],'unit':'m','poseId':dataset['frameContract']['staticReferencePose']['id'],'side':'right','kind':'authored_teaching_surface','precision':'coarse_not_skin','positions':p.tolist(),'indices':idx.tolist(),'patches':patches,'rights':{'source':'ZA pinned package declaration CC BY-SA 4.0; upstream attribution retained','localObservation':'supported','publicRedistribution':'held','professorReview':'not_performed'}}
for point in points:point.update({'carrierId':carrier['id'],'carrierRevision':carrier['revision'],'carrierHash':h,'frameId':carrier['frameId'],'unit':'m','poseId':carrier['poseId'],'revision':'AC1-proposal-r1'})
(O/'prototype.json').write_text(json.dumps({'schemaVersion':1,'usage':'development_review_only','carrier':carrier,'instances':points},ensure_ascii=False,separators=(',',':'))+'\n')
(O/'carrier-validation.json').write_text(json.dumps({'decision':'author bounded teaching patches on current ZA; no second body, no external coordinates','sourceInputs':inputs,'sourceProbeSha256':sha((O/'source-probe.json').read_bytes()),'patchAudit':audit,'carrierHash':h,'vertices':len(p)//3,'triangles':len(idx)//3,'positionIndexBytes':p.nbytes+idx.nbytes,'normalsBytes':p.nbytes,'geometryGPUBufferEstimateBytes':p.nbytes*2+idx.nbytes,'datasetRevision':dataset['revision'],'prototypeOnly':True,'anatomicallyAcceptedPoints':0},indent=2))
print('carrier',len(p)//3,len(idx)//3,h)
