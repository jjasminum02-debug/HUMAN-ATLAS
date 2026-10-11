exec((__import__('pathlib').Path(__file__).parent/'author-lung.py').read_text().split('# First milestone:')[0])
# Extend only versioned local registrations; no historical manifest/binary writes.
manifests['lung-local-r3']=read(manifest_path('lung-local-r3'))
import heapq
failures=[];prepared={}
def side_direction(side,x=-1,z=0):return [x if side=='right' else -x,0,z]
def face(name,side,i,b=None):
 g=geometry(find(name,side),side);a={'triangle':i,'barycentric':b or [1/3]*3};return g,a,at(g,a)
def mapped(code,side,c,name,i,surface,label,construction,limits,b=None):
 g,a,p=face(name,side,i,b);return landmark(code,side,c,name,a,surface,label,construction,limits)
def path(carrierIds,start,end):
 """Dual triangle path; only actual shared edges (including byte-identical registered seams)."""
 gs=[carrier(k) for k in carrierIds];faces={};edges={};centers={}
 for g in gs:
  v,t=arrays(g)
  for i,idx in enumerate(t):
   if (v[idx][:,0]<0).all()!= (start['side']=='right'):continue
   key=(g['id'],i);faces[key]=idx;centers[key]=v[idx].mean(axis=0)
   for a,b in [(idx[0],idx[1]),(idx[1],idx[2]),(idx[2],idx[0])]:
    edge=tuple(sorted([tuple(np.round(v[a],7)),tuple(np.round(v[b],7))]));edges.setdefault(edge,[]).append(key)
 graph={k:[] for k in faces};shared={}
 for e,fs in edges.items():
  if len(fs)==2:
   a,b=fs;graph[a].append(b);graph[b].append(a);shared[a,b]=shared[b,a]=np.mean(e,axis=0)
 a=(start['carrierId'],start['triangle']);b=(end['carrierId'],end['triangle']);assert a in graph and b in graph
 # Anterior/lateral strip, with no source-independent rescaling; endpoints are the observed structural indicators.
 pa=at(carriers[a[0]],start);pb=at(carriers[b[0]],end);low,high=sorted([pa[1],pb[1]]);sign=-1 if start['side']=='right' else 1
 distance={a:0};previous={};queue=[(0,a)]
 while queue:
  cost,k=heapq.heappop(queue)
  if cost!=distance[k]:continue
  if k==b:break
  for n in graph[k]:
   p=centers[n]
   if p[1]<low-.015 or p[1]>high+.015:continue
   f=(p[1]-pb[1])/(pa[1]-pb[1]);x=pb[0]+f*(pa[0]-pb[0]);z=pb[2]+f*(pa[2]-pb[2])
   if abs(p[0]-x)>.035 or p[2]<z-.014:continue
   nc=cost+np.linalg.norm(centers[k]-p)
   if nc<distance.get(n,1e9):distance[n]=nc;previous[n]=k;heapq.heappush(queue,(nc,n))
 if b not in distance:raise ValueError('No connected anterior source-bound carrier path')
 chain=[b]
 while chain[-1]!=a:chain.append(previous[chain[-1]])
 chain.reverse();segments=[];p=pa
 def bary(g,i,p):
  v,t=arrays(g);tri=v[t[i]];uv=np.linalg.lstsq((tri[1:]-tri[0]).T,p-tri[0],rcond=None)[0];b=np.maximum([1-uv.sum(),*uv],0);return (b/b.sum()).tolist()
 for j,k in enumerate(chain):
  q=shared[k,chain[j+1]] if j+1<len(chain) else pb
  if np.linalg.norm(p-q)>1e-9:segments.append({'carrierId':k[0],'triangle':k[1],'from':bary(carriers[k[0]],k[1],p),'to':bary(carriers[k[0]],k[1],q)})
  p=q
 return segments
def proportion(code,side,landmarks,start,end,pathlist,value,total,relation):
 lengths=[np.linalg.norm(at(carriers[s['carrierId']],{'triangle':s['triangle'],'barycentric':s['to']})-at(carriers[s['carrierId']],{'triangle':s['triangle'],'barycentric':s['from']})) for s in pathlist];remaining=sum(lengths)*value/total;j=0
 while j<len(lengths)-1 and remaining>lengths[j]:remaining-=lengths[j];j+=1
 c=carriers[pathlist[j]['carrierId']]
 # Evidence is code/target-hash specific, including reference annotations; no re-labelling legacy evidence.
 ls=[]
 for l in landmarks:
  a=annotations[l['annotationIndex']];g=native[a['sourceKey']];sf={**a['surface'],'carrierId':a['surfaceCarrierId']};e=note(code,side,c,'landmark_annotation',json.dumps(a,ensure_ascii=False));ls.append({**l,'evidenceId':e,'surface':sf});ls[-1].pop('annotationIndex',None)
 ev=note(code,side,c,'proportion',f'WHO p12/p27-29: {total} B-cun between addressed structural model endpoints. {relation}',basic[code]['standard'],measurement={'kind':'B-cun','value':total})
 unit(code,side,c,ls,{'kind':'B-cun','from':ls[start]['id'],'to':ls[end]['id'],'value':value,'totalCun':total,'path':pathlist,'evidenceId':ev},relation)
for side in ['right','left']:
 # Read native side independently; same triangle numbers are checked on each actual side object, never reflected geometry.
 c=carrier('wrist-link-'+side+'-0');r,ra,pr=face('Radius',side,93);s,sa,ps=face('Scaphoid bone',side,120);apl,aa,pp=face('Abductor pollicis longus',side,260)
 p=(pr+ps)/2;surf=address(c,p,side_direction(side,.3,1));prepared[side,'LU9']=(c,surf)
 ls=[]
 for name,i,label,construction in [('Radius',93,'Distal radial styloid facet','Actual styloid facet observed with scaphoid interval.'),('Scaphoid bone',120,'Scaphoid facet distal/ulnar to styloid','AI structural interval between native styloid and scaphoid, ulnar to addressed APL.'),('Abductor pollicis longus',260,'APL distal tendon radial to model point','Actual APL facet radial to model point; no inferred artery claimed.')]:
  gg,aa,pp=face(name,side,i);own=address(c,pp,side_direction(side,-1,1))
  ls.append(mapped('LU9',side,c,name,i,own,label,construction,['No actual crease, pulsation or radial artery annotation; structural approximation only.','Palmar polarity verified by FCR/palmaris longus anterior to extensor digitorum, not old view names.']))
 ls.append(mapped('LU9',side,c,'Abductor pollicis brevis',488,surf,'Superficial registration of addressed radiocarpal interval','APB superficial facet488 supports transfer of styloid/scaphoid/APL structural relation to the current palmar envelope. APB itself is not the location definition.',['No observed skin crease, radial artery or pulsation; approximate structural model indicator.']))
 unit('LU9',side,c,ls,{'kind':'landmark','landmark':ls[3]['id']},'WHO p30: styloid/scaphoid interval ulnar to APL. Native addressed interval transferred to structural envelope; independent radial artery/skin crease absent.')
 c=carrier('thenar-'+side+'-0');g,a,p=face('First metacarpal bone',side,407);surf=address(c,p,side_direction(side,-1,0));prepared[side,'LU10']=(c,surf)
 l=mapped('LU10',side,c,'First metacarpal bone',407,surf,'Radial side of first metacarpal midshaft at thenar margin','Facet407 inspected at shaft midpoint; measured base518/head185 average is 1.44mm from shaft facet. Radial contour registered against actual thenar muscles; model red-white boundary authored at radial palmar/dorsal transition, not observed colour.',['No source skin colour boundary; radial contour is an AI educational correspondence, not palpation accuracy.'])
 unit('LU10',side,c,[l],{'kind':'landmark','landmark':l['id']},'WHO p30: radial to MC1 midpoint on palm at red-white border. Actual shaft/thenar radial contour supports a model border indicator; original skin colour is absent.')
 # Elbow correspondence in frozen extended pose: native distal biceps tendon + lateral adjacent contour at humeral joint plane.
 c=carrier('arm-'+side+'-0');g,a,p=face('Long head of biceps brachii',side,351);p=p+np.array(side_direction(side,-.004,0));surf=address(c,p,[0,0,1]);prepared[side,'LU5']=(c,surf)
 l=mapped('LU5',side,c,'Long head of biceps brachii',351,surf,'Lateral cubital interval adjacent to distal biceps tendon','Observed distal tendon facet351 near distal humeral articulation. Authored cubital indicator at joint plane and 4mm lateral correspondence; no source skin crease or 90-degree flexion produced.',['Elbow is extended; flexible crease/depression transferred as static structural indicator only.'])
 unit('LU5',side,c,[l],{'kind':'landmark','landmark':l['id']},'WHO p28: cubital level lateral to biceps tendon. AI static extended-pose teaching correspondence to native distal tendon/joint, no claim of an observed flexed crease.')
 # Native axillary insertion at pectoralis insertion marks upper measurement level, not a skin fold assertion.
 upper=carrier('arm-'+side+'-1');g,a,p=face('Clavicular part of deltoid muscle',side,199);sf=address(upper,p,[0,0,1]);la=mapped('LU3',side,upper,'Clavicular part of deltoid muscle',199,sf,'Superficial axillary model measurement level','Actual deltoid facet199 at Y1.33814 is a superficial registration of the native pectoralis insertion facet45 Y1.33836. Separate addressed pectoral observation defines axial level, not deltoid identity.',['No source axillary skin crease; static model correspondence to pectoral insertion plane, not a detected fold.'])
 annotations[-1]['surfaceCarrierId']=upper['id'];la['annotationIndex']=len(annotations)-1
 c5,a5=prepared[side,'LU5'];l5=units[-1]['landmarks'][0].copy();annotations[-2]['surfaceCarrierId']=c5['id'];l5['annotationIndex']=len(annotations)-2
 start={**sf,'carrierId':upper['id'],'side':side};end={**a5,'carrierId':c5['id'],'side':side}
 try:
  line=path([upper['id'],c5['id']],start,end)
  for code,n in [('LU3',3),('LU4',4)]:proportion(code,side,[la,l5],0,1,line,n,9,'Actual pectoral-insertion model fold to distal-biceps cubital indicator, 9 B-cun; 3/9 or 4/9 inferior, along connected anterior-lateral carrier. Native crease absence and static pose remain explicit.')
 except Exception as e:failures.extend({'code':code,'side':side,'error':str(e),'attempt':'Native endpoints and connected dual mesh path'} for code in ['LU3','LU4'])
 # Wrist->elbow teaching measurement uses the verified byte-identical .866 ring; no synthetic bridge.
 c9,a9=prepared[side,'LU9'];first=next(u for u in units if u['code']=='LU9' and u['side']==side)['landmarks'][3].copy();a9obs=next(i for i,a in enumerate(annotations) if a['side']==side and a['surface']==a9 and a['relation']=='Superficial registration of addressed radiocarpal interval');annotations[a9obs]['surfaceCarrierId']=c9['id'];first['annotationIndex']=a9obs
 # Locate the actual LU5 annotation by its explicit id, not positional order after proportions.
 l5=next(u for u in units if u['code']=='LU5' and u['side']==side)['landmarks'][0].copy();idx=next(i for i,a in enumerate(annotations) if a['surface']==a5 and a['relation'].startswith('Lateral cubital'));annotations[idx]['surfaceCarrierId']=c5['id'];l5['annotationIndex']=idx
 try:
  line=path([c9['id'],c5['id']],{**a9,'carrierId':c9['id'],'side':side},{**a5,'carrierId':c5['id'],'side':side})
  for code,n in [('LU6',7),('LU8',1)]:proportion(code,side,[first,l5],0,1,line,n,12,'12 B-cun model palmar wrist to cubital level. LU6 is on LU9-LU5 course; LU8 is 1 B-cun proximal. Radial artery absent and model crease not observed, so educational structural approximation only.')
 except Exception as e:failures.extend({'code':code,'side':side,'error':str(e),'attempt':'Shared-ring wrist link and connected anterior course'} for code in ['LU6','LU8'])
(E/'bilateral-rules-r2.json').write_text(json.dumps({'schemaVersion':2,'context':context,'units':units,'inputs':{'domain':'real_input','carriers':carriers,'native':native,'evidence':evidence}},ensure_ascii=False,separators=(',',':'))+'\n')
(E/'annotations-r2.json').write_text(json.dumps(annotations,ensure_ascii=False,indent=2)+'\n');(E/'author-failures-r2.json').write_text(json.dumps(failures,ensure_ascii=False,indent=2)+'\n');print('authored',len(units),'failed',failures)
