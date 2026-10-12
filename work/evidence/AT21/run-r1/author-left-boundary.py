"""Independent left contour on actual frozen topology. No reflection or source writes."""
from pathlib import Path
from collections import Counter,defaultdict
import json,hashlib,copy
import numpy as np
R=Path(__file__).resolve().parents[4];E=Path(__file__).parent
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rulesPath=R/'work/evidence/AT6/resume-r1/bilateral-rules-r9.json';rules=read(rulesPath)
generation=read(R/'work/evidence/AT3/generation.json')
right=read(R/'atlas-data/acupoints/territories/AT20-r1/lung-forearm-right-boundary-r1.json')
c=rules['inputs']['carriers']['arm-left-0'];v=np.array(c['positions']).reshape(-1,3);t=np.array(c['indices']).reshape(-1,3)
mp=np.array(generation['chunkSourceGridMappings'][c['id']]);a=mp%40;level=mp//40
# Actual left radial side is +X, grid angles28..39 plus0 (different faces/holes from right).
sel=np.all(((a[t]>=28)|(a[t]==0))&(level[t]>=1)&(level[t]<=16),axis=1)
fs=t[sel];counts=Counter(tuple(sorted(e)) for tri in fs for e in [(tri[0],tri[1]),(tri[1],tri[2]),(tri[2],tri[0])]);graph=defaultdict(list)
for (x,y),n in counts.items():
 if n==1:graph[int(x)].append(int(y));graph[int(y)].append(int(x))
assert all(len(ns)==2 for ns in graph.values()),'pinched boundary; needs separate contour'
loops=[]
while graph:
 start=min(graph);prev=None;p=start;loop=[]
 while True:
  loop.append(p);q=next(n for n in graph[p] if n!=prev);prev,p=p,q
  if p==start:break
 for x in loop:del graph[x]
 loops.append(loop)
loops.sort(key=len,reverse=True)
def anchor(vertex):
 f=int(np.flatnonzero((t==vertex).any(axis=1))[0]);b=[0,0,0];b[list(t[f]).index(vertex)]=1
 return {'carrierId':c['id'],'carrierRevision':c['revision'],'carrierHash':c['topologySha256'],'frameId':c['frameId'],'unit':'m','poseId':c['poseId'],'side':'left','triangle':f,'barycentric':b}
landmarks=[]
ledger=read(R/'work/evidence/AT6/resume-r1/bilateral-compiler-r8/ledger.json')
pointRecords=[]
for code in ['LU6','LU7','LU8']:
 u=next(x for x in rules['units'] if x['id']==code+'-left');i=ledger['units'][u['id']]['instance'];assert i['triangle'] in np.flatnonzero(sel)
 pointRecords.append({'code':code,'triangle':i['triangle'],'carrierHash':i['carrierHash'],'worldPosition':(np.array(i['barycentric'])@v[t[i['triangle']]]).tolist()})
 for l in u['landmarks']:
  if l['id'] not in [z['id'] for z in landmarks]:landmarks.append({'id':l['id'],'anatomy':l['anatomy'],'native':l['native'],'surface':l['surface'],'sourceKey':l['sourceKey'],'modelIndicator':l.get('modelIndicator'),'inputFile':str(rulesPath.relative_to(R)),'inputSha256':sha(rulesPath),'locator':f'units[{u["id"]}].landmarks[{l["id"]}]'})
d=copy.deepcopy(right);d.update({'id':'LU-forearm-left','side':'left','revision':'AT21-left-r1','boundaryRevision':'LU-forearm-left-r1','landmarks':landmarks,'linkedEducationalPoints':['LU6-left','LU7-left','LU8-left']})
d['carrierBinding'].update({'id':c['id'],'topologySha256':c['topologySha256'],'component':'arm-left'})
d['construction'].update({'anatomicalRelation':'Actual left source-addressed radiocarpal/cubital endpoints and APL/EPB groove, checked by AT6 independent native keys. No literal radial artery or skin crease observed.','proximalStop':'ring16, Y1.002126932m includes left LU6; matched partial forearm learning interval, not an anatomical transverse boundary. Left topology examined independently; no copied right pinch claim.','distalStop':'ring1 before wrist-link seam; includes actual left LU8.','widthRule':'AI anterior-to-left-radial learning window, actual left grid angles28..39 plus0. Visual108-degree width is not source-defined skin/jingjin boundary.','holes':'actual left rejected-face holes, independently extracted','gridSelection':{'ringInclusive':[1,16],'angleSet':list(range(28,40))+[0]},'reflectionUsed':False})
d['components']=[{'id':'left-forearm','carrierId':c['id'],'seedTriangle':pointRecords[0]['triangle'],'loops':[{'role':'outer' if n==0 else 'hole','controls':[{'id':f'left-loop{n}-v{x}','vertex':x,'anchor':anchor(x)} for x in loop]} for n,loop in enumerate(loops)]}]
d['handoff'].update({'expectedFaceCountForReplay':int(sel.sum()),'candidateFaceSetSha256':hashlib.sha256(np.flatnonzero(sel).astype('<u4').tobytes()).hexdigest(),'operation':'Common barrier/seed replay on actual left topology; preserve all holes.','finalMaskCreated':False})
d['limitations']=['partial left forearm only; no complete LU territory','native-derived educational envelope, not skin scan or canonical cutaneous/jingjin boundary','width and transverse stops are AI visual learning choices','LU1–5/LU9–11 outside this sample; no point coordinates changed','independent original left addresses and holes; reflection never used']
(E/'left-boundary-r1.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
(E/'left-authoring-r1.json').write_text(json.dumps({'side':'left','carrierHash':c['topologySha256'],'actualPoints':pointRecords,'actualNativeSourceKeys':[l['sourceKey'] for l in landmarks],'loopLengths':[len(l) for l in loops],'faces':int(sel.sum()),'bounds':[v[fs].min(axis=(0,1)).tolist(),v[fs].max(axis=(0,1)).tolist()],'reflectionUsed':False,'landmarkInputSha256':sha(rulesPath)},ensure_ascii=False,indent=2)+'\n')
print('Left actual contour:',int(sel.sum()),'faces; loop lengths',list(map(len,loops)),'native annotations',len(landmarks),'no reflection')
