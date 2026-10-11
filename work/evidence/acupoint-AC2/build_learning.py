"""AC2 review-only teaching carrier from each side's own cached ZA meshes.
No mirror, external point coordinates, source writes, or anatomical acceptance.
"""
from pathlib import Path
import json,hashlib,struct
import numpy as np
R=Path(__file__).resolve().parents[3]; O=Path(__file__).resolve().parent; A=O.parent/'acupoint-AC1'
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
dataset=read(A/'runtime-dataset.json');rows={r['sourceKey']:r for r in read(A/'runtime-integration.json')['objects']};cache=R/'atlas-data/source-cache/datasets/za'
inputs={};unit_inputs={};meshes={}
def world(k):
 if k in meshes:return meshes[k]
 unitpath=cache/'units'/f'{k}.json';unit_inputs[str(unitpath.relative_to(R))]=sha(unitpath.read_bytes());u=read(unitpath);l=u['lods']['detail'];p=cache/l['path'];b=p.read_bytes();assert sha(b)==l['sha256'];inputs[str(p.relative_to(R))]=sha(b)
 size=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+size]);start=28+size
 def arr(ai):
  a=d['accessors'][ai];v=d['bufferViews'][a['bufferView']];dtype={5126:'<f4',5123:'<u2',5125:'<u4'}[a['componentType']];n={'VEC3':3,'SCALAR':1}[a['type']]
  return np.frombuffer(b,dtype=dtype,count=a['count']*n,offset=start+v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,n)
 prim=d['meshes'][0]['primitives'][0];v=arr(prim['attributes']['POSITION']).astype('f8');t=arr(prim['indices']).reshape(-1,3);m=np.array(u['matrix']).reshape(4,4,order='F');v=(np.c_[v,np.ones(len(v))]@m.T)[:,:3];assert np.max(np.abs(np.array([v.min(axis=0),v.max(axis=0)])-np.array(rows[k]['bounds'])))<.0001,k;meshes[k]=(v,t);return v,t
names=['중부','운문','천부','협백','척택','공최','열결','경거','태연','어제','소상'];romans=['Zhongfu','Yunmen','Tianfu','Xiabai','Chize','Kongzui','Lieque','Jingqu','Taiyuan','Yuji','Shaoshang']
# Short independent summaries, no textbook or full classical route claims.
locations=['첫째늑간 높이, 쇄골 아래 가쪽 6 비례촌.','쇄골 아래 오목, 부리돌기 안쪽 6 비례촌.','위팔 앞가쪽, 위팔두갈래근 가쪽·겨드랑 주름 아래 3 비례촌.','같은 위팔 기준, 겨드랑 주름 아래 4 비례촌.','팔꿈치 주름, 위팔두갈래근 힘줄 가쪽 오목.','척택–태연 선, 손목 주름 위 7 비례촌.','노쪽 아래팔의 엄지 건 사이, 손목 위 1.5 비례촌.','노뼈 붓돌기와 노동맥 사이, 손목 위 1 비례촌.','손목 노쪽, 붓돌기–주상골 사이·긴엄지벌림근 건의 자쪽.','첫째중수골 중간 노쪽의 손바닥 피부 경계.','엄지 요측 조갑각의 몸쪽·가쪽 0.1 손가락촌.']
landmarks=['쇄골 · 첫째/둘째갈비뼈','쇄골 · 어깨뼈 부리돌기','위팔두갈래근 · 겨드랑 앞주름','위팔두갈래근 · 겨드랑 앞주름','위팔두갈래근 건 · 팔꿈치 주름','팔꿈치–손목 주름 구간','긴엄지벌림근 · 짧은엄지폄근 건','노뼈 붓돌기 · 노동맥','노뼈 · 주상골 · 긴엄지벌림근 건','첫째중수골 · 피부 경계','엄지 말절골 · 손톱 요측 모서리']
concepts=[]
for i,(name,roman,text) in enumerate(zip(names,romans,locations)):
 ref={'id':'who-location-2008-2009','title':'WHO Standard Acupuncture Point Locations in the Western Pacific Region','edition':'2008; updated and reprinted 2009','locator':f'printed p. {26+i//2}','url':'https://www.medbox.org/index.php/dl/627a4de115110145a1723f64'}
 concepts.append({'code':f'LU{i+1}','nameKo':name,'romanization':roman,'aliases':[],'channel':'LU','revision':'AC2-text-r1','standard':ref,'nameSources':[{'id':'kmcric-lung-names','title':'KMCRIC 표준경혈 DB 수태음폐경','edition':None,'locator':f'LU{i+1}','url':'https://www.kmcric.com/database/acupoint/LU'}],'textbook':None,'location':{'text':text,'sources':[ref],'interpretation':'source_summary'},'posture':None,'explanation':None,'measurements':[{'kind':'F-cun' if i==10 else 'B-cun' if i in [0,1,2,3,5,6,7] else 'landmark','value':{0:6,1:6,2:3,3:4,5:7,6:1.5,7:1,10:.1}.get(i),'reference':('앞정중선에서 가쪽' if i<2 else '겨드랑 앞주름 아래' if i in [2,3] else '손목 주름 위' if i in [5,6,7] else '엄지 요측 조갑각 몸쪽·가쪽' if i==10 else landmarks[i])}],'landmarkLabel':landmarks[i]})
(O/'point-concepts.json').write_text(json.dumps(concepts,ensure_ascii=False,indent=2)+'\n')
for side in ['right','left']:
 inputs={};unit_inputs={}
 def key(name):
  m=[r for r in rows.values() if r['side']==side and r['names']['en']==name];assert len(m)==1,(side,name);return m[0]['sourceKey']
 def bounds(name):return np.array(rows[key(name)]['bounds'])
 def radial(b):return b[0,0] if side=='right' else b[1,0]
 def lateral_at(name,y):
  v,_=world(key(name));slice=v[abs(v[:,1]-y)<.008];assert len(slice)>0
  return float(np.min(slice[:,0]) if side=='right' else np.max(slice[:,0]))
 clav=bounds('Clavicle');first=bounds('Costal cartilage of first rib');second=bounds('Costal cartilage of second rib');rad=bounds('Radius');scaph=bounds('Scaphoid bone');meta=bounds('First metacarpal bone');thumb=bounds('Distal phalanx of first finger of hand')
 probe=read(A/'source-probe.json' if side=='right' else O/'left-source-probe.json');nail,peri=probe['objects'];candidates=[c for c in nail['components'] if c['vertices']>10];comp=min(candidates,key=lambda c:np.linalg.norm(np.mean(c['bounds'],axis=0)-np.mean(thumb,axis=0)));nb=np.array(comp['bounds']);assert np.linalg.norm(nb.mean(axis=0)-thumb.mean(axis=0))<.025
 # Source-bound envelopes; axillary/elbow/wrist creases and B/F-cun remain missing.
 chest=[radial(clav)+(.1*(clav[1,0]-clav[0,0]) if side=='right' else -.1*(clav[1,0]-clav[0,0])),float((first[0,1]+second[1,1])/2)]
 wrist=np.array([(radial(rad)+radial(scaph))/2,(rad[0,1]+scaph[1,1])/2]);elbow=np.array([lateral_at('Long head of biceps brachii',float(rad[1,1])),rad[1,1]])
 ax=bounds('Brachial fascia')[1,1];upper=[]
 for fraction in [3/9,4/9]:
  y=ax+(elbow[1]-ax)*fraction;upper.append([lateral_at('Long head of biceps brachii',y),y])
 xy=[chest,[chest[0],float(clav[0,1]-.005)],*upper,elbow.tolist(),(wrist+(elbow-wrist)*7/12).tolist(),(wrist+(elbow-wrist)*1.5/12).tolist(),(wrist+(elbow-wrist)*1/12).tolist(),wrist.tolist(),[radial(meta),float(meta[:,1].mean())],[float(radial(nb)+(.25*(nb[1,0]-nb[0,0]) if side=='right' else -.25*(nb[1,0]-nb[0,0]))),float(nb[1,1]-.07*(nb[1,1]-nb[0,1]))]]
 groups=[['Clavicular head of pectoralis major muscle','Sternocostal head of pectoralis major muscle','Pectoral fascia','Clavicular part of deltoid muscle']]*2+[['Long head of biceps brachii','Short head of biceps brachii','Brachial fascia','Brachialis muscle','Acromial part of deltoid muscle','Clavicular part of deltoid muscle','Brachioradialis muscle']]*3+[['Antebrachial fascia','Radius','Abductor pollicis longus','Extensor pollicis brevis','Brachioradialis muscle']]*4+[['First metacarpal bone','Abductor pollicis brevis']]+[['Distal phalanx of first finger of hand']]
 lmnames=[['Clavicle','First rib','Second rib'],['Clavicle','Scapula'],['Long head of biceps brachii','Brachial fascia'],['Long head of biceps brachii','Brachial fascia'],['Long head of biceps brachii','Radius'],['Radius','Antebrachial fascia'],['Abductor pollicis longus','Extensor pollicis brevis'],['Radius'],['Radius','Scaphoid bone','Abductor pollicis longus'],['First metacarpal bone'],['Distal phalanx of first finger of hand']]
 positions=[];indices=[];instances=[];audit=[];samplers=[]
 def sampler(ks,extra=[]):
  triangles=np.concatenate([world(k)[0][world(k)[1]] for k in ks]+[np.array(o['positions'])[np.array(o['indices'])] for o in extra]);allv=triangles.reshape(-1,3);den=(triangles[:,1,1]-triangles[:,2,1])*(triangles[:,0,0]-triangles[:,2,0])+(triangles[:,2,0]-triangles[:,1,0])*(triangles[:,0,1]-triangles[:,2,1]);valid=abs(den)>1e-12;tri=triangles[valid];den=den[valid]
  def sample(x,y):
   a=((tri[:,1,1]-tri[:,2,1])*(x-tri[:,2,0])+(tri[:,2,0]-tri[:,1,0])*(y-tri[:,2,1]))/den;b=((tri[:,2,1]-tri[:,0,1])*(x-tri[:,2,0])+(tri[:,0,0]-tri[:,2,0])*(y-tri[:,2,1]))/den;c=1-a-b;hit=(a>=0)&(b>=0)&(c>=0)
   return (float(np.max((a*tri[:,0,2]+b*tri[:,1,2]+c*tri[:,2,2])[hit])),False) if hit.any() else (float(allv[np.argmin(np.sum((allv[:,:2]-[x,y])**2,axis=1)),2]),True)
  return sample
 for n,(center,gn,lms) in enumerate(zip(xy,groups,lmnames)):
  ks=[key(k) for k in gn];sample=sampler(ks,[nail,peri] if n==10 else []);samplers.append(sample);start=len(positions)//3;firsttri=len(indices)//3;grid=9;size=.006 if n==10 else .009 if n>=6 else .018;fallback=0;clearance=.001 if n==10 else .004
  for j in range(grid):
   for i in range(grid):
    x=center[0]+size*(i/8*2-1);y=center[1]+size*(j/8*2-1);z,miss=sample(x,y);fallback+=miss;positions.extend([x,y,z+clearance])
  for j in range(8):
   for i in range(8):a=start+j*grid+i;indices.extend([a,a+1,a+grid,a+1,a+grid+1,a+grid])
  missing=['skin surface and point-specific proportional measure/crease/depression not validated']
  if n in [2,3]:missing+=['anterior axillary fold absent; fascia envelope used only for proposal']
  if n==10:missing+=['radial nail corner and 0.1 F-cun not anatomically accepted']
  instances.append({'code':f'LU{n+1}','side':side,'triangle':firsttri+72,'barycentric':[1,0,0],'landmarkSourceKeys':[key(k) for k in lms],'locationValidation':'unresolved','aiProposal':True,'professorReview':'not_performed','missing':missing})
  audit.append({'code':f'LU{n+1}','xyProposal':list(center),'inputKeys':ks,'landmarks':[{'key':key(k),'side':side,'name':k,'bounds':rows[key(k)]['bounds']} for k in lms],'fallbackVertices':fallback,'gridVertices':81})
 # Authored narrow teaching ribbon. Not a classical meridian course; no internal/branch data.
 routePositions=[];routeFallback=0
 for n in range(10):
  sample=sampler(list(dict.fromkeys([key(k) for k in groups[n]+groups[n+1]])),[nail,peri] if n>=9 else [])
  for j in range(17):
   t=j/16;x,y=np.array(xy[n])*(1-t)+np.array(xy[n+1])*t;z,miss=sample(x,y);routeFallback+=miss;routePositions.extend([float(x),float(y),z+.005])
 # Freeze the narrow route surface in the same anchor carrier topology.
 start=len(positions)//3
 for j in range(len(routePositions)//3):
  x,y,z=routePositions[j*3:j*3+3];positions.extend([x-.001,y,z-.0004,x+.001,y,z-.0004])
  if j%17:
   a=start+(j-1)*2;indices.extend([a,a+1,a+2,a+1,a+3,a+2])
 p=np.array(positions,dtype='<f4');idx=np.array(indices,dtype='<u4');h=sha(p.tobytes()+idx.tobytes())
 carrier={'id':f'za-{side}-lung-teaching-patches','revision':'AC2-r1','topologySha256':h,'datasetRevision':dataset['revision'],'frameId':dataset['frameContract']['targetFrameId'],'unit':'m','poseId':dataset['frameContract']['staticReferencePose']['id'],'side':side,'kind':'authored_teaching_surface','precision':'coarse_not_skin','positions':p.tolist(),'indices':idx.tolist(),'rights':read(A/'prototype.json')['carrier']['rights']}
 for point in instances:point.update({'carrierId':carrier['id'],'carrierRevision':carrier['revision'],'carrierHash':h,'frameId':carrier['frameId'],'unit':'m','poseId':carrier['poseId'],'revision':'AC2-proposal-r1'})
 route={'id':f'LU-{side}-surface-teaching','channel':'LU','side':side,'revision':'AC2-teaching-r1','kind':'surface_teaching','sources':[],'segments':[{'id':'teaching-order','branchOf':None,'direction':'forward','anchors':instances}],'teachingPointOrder':[f'LU{i+1}' for i in range(11)],'positions':routePositions,'interpretation':'ai_proposal','carrierHash':h}
 (O/f'{side}-learning.json').write_text(json.dumps({'schemaVersion':1,'usage':'development_review_only','carrier':carrier,'instances':instances,'route':route,'concepts':concepts},ensure_ascii=False,separators=(',',':'))+'\n')
 (O/f'{side}-carrier-validation.json').write_text(json.dumps({'side':side,'independentNativeGeometry':True,'mirrored':False,'thumbNailComponent':comp,'probeHash':sha((A/'source-probe.json' if side=='right' else O/'left-source-probe.json').read_bytes()),'sourceInputs':inputs.copy(),'unitMetadataInputs':unit_inputs.copy(),'worldBoundsToleranceMetres':.0001,'carrierHash':h,'vertices':len(p)//3,'triangles':len(idx)//3,'routeVertices':len(routePositions)//3,'routeNearestFallback':routeFallback,'points':audit,'anatomicallyAcceptedPoints':0,'precision':'coarse_not_skin','frame':carrier['frameId'],'unit':'m','pose':carrier['poseId']},ensure_ascii=False,indent=2)+'\n')
 print(side,h,len(p)//3,len(idx)//3,'route',len(routePositions)//3)
