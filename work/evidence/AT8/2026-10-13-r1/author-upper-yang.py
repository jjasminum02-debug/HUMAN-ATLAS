"""AT8 source-addressed AI structural proposals. Landmarks precede ray registration.
Preserves every failed input. No mirror, bounds-ratio location or external coordinates.
"""
from pathlib import Path
import runpy,json,hashlib,heapq
import numpy as np
E=Path(__file__).parent;g=runpy.run_path(str(E/'native-reader.py'));globals().update({k:g[k] for k in ['R','rows','world','find','inputs','sha','read']})
context={k:read(R/'atlas-data/acupoints/learner/lung-r7.json')[k] for k in ['datasetRevision','frameId','unit','poseId']};facts=read(E/'basic-locations-r1.json');rights=read(R/'atlas-data/acupoints/carriers/education-r1/manifest.json')['rights']
carriers={};native={};units=[];annotations=[];evidence=[];failures=[];prepared={};graphs={}
manifest_dirs=['education-r1','lung-AT6-r2','upper-yang-AT8-r3']
manifests={v:read(R/f'atlas-data/acupoints/carriers/{v}/manifest.json') for v in manifest_dirs}
def carrier(ident):
 if ident not in carriers:
  ver,c=next((v,c) for v,m in manifests.items() for c in m['chunks'] if c['id']==ident);m=manifests[ver];b=(R/f'atlas-data/acupoints/carriers/{ver}'/c['file']).read_bytes();assert sha(b)==c['sha256'];v=np.frombuffer(b,dtype='<f4',count=c['vertices']*3).reshape(-1,3);t=np.frombuffer(b,dtype='<u2',offset=c['vertices']*24).reshape(-1,3).astype('<u4')
  carriers[ident]={'id':ident,'revision':c['revision'],'topologySha256':c['topologySha256'],**context,'side':c['side'],'kind':m['kind'],'precision':m['precision'],'rights':rights,'positions':v.ravel().tolist(),'indices':t.ravel().tolist()}
 return carriers[ident]
def geometry(name,side):
 k=find(name,side)
 if k not in native:
  v,t=world(k);native[k]={'id':k,'revision':'native-world-frozen-r1','topologySha256':sha(v.astype('<f4').tobytes()+t.astype('<u4').tobytes()),**context,'side':side or 'midline','rights':rights,'positions':v.ravel().tolist(),'indices':t.ravel().tolist()}
 return native[k]
def arrays(c):return np.array(c['positions']).reshape(-1,3),np.array(c['indices']).reshape(-1,3)
def at(c,a):v,t=arrays(c);return np.array(a['barycentric'])@v[t[a['triangle']]]
def facet(name,side,axis=None,end=None,near=None,mask=None):
 c=geometry(name,side);v,t=arrays(c);cent=v[t].mean(1);ids=np.arange(len(t));
 if mask is not None:ids=ids[mask(cent)];assert len(ids),name
 j=int(ids[np.argmin(np.linalg.norm(cent[ids]-near,axis=1))] if near is not None else ids[(np.argmin if end=='min' else np.argmax)(cent[ids,axis])]);a={'triangle':j,'barycentric':[1/3]*3};return c,a,cent[j]
def slice_point(name,side,y,axis=0,end='min'):
 c=geometry(name,side);v,t=arrays(c);tr=v[t];candidates=[]
 for i,tri in enumerate(tr):
  for a,b in [(0,1),(1,2),(2,0)]:
   if (tri[a,1]<=y)!=(tri[b,1]<=y):
    f=(y-tri[a,1])/(tri[b,1]-tri[a,1]);w=np.zeros(3);w[a]=1-f;w[b]=f;candidates.append((w@tri,i,w))
 if not candidates:raise ValueError(f'No native {name} section at anatomy-defined plane {y}')
 p,j,w=(min if end=='min' else max)(candidates,key=lambda c:c[0][axis]);return c,{'triangle':j,'barycentric':w.tolist()},p
# Exact ray address, registration only (AC1/AT6 method), no nearest fallback.
fn=next(n for n in __import__('ast').parse((R/'work/evidence/AT6/resume-r1/author-lung.py').read_text()).body if isinstance(n,__import__('ast').FunctionDef) and n.name=='address');exec(compile(__import__('ast').Module(body=[fn],type_ignores=[]),'AT6-ray','exec'),globals())
def note(code,side,c,purpose,text,**extra):
 id=f'{code}-{side}-{purpose}-{len(evidence)}';src={**facts['source'],'locator':f'printed pp. {34+(int(code[2:])-1)//2 if code.startswith("LI") else 158+(int(code[2:])-1)//2}'}
 evidence.append({'id':id,'purpose':purpose,'source':src,'originalText':text,'author':'ai','status':'confirmed','method':'anatomical_correspondence','side':side,'frameId':context['frameId'],'poseId':context['poseId'],'carrierHash':c['topologySha256'],'pointCode':code,'rights':{'localObservation':'supported','publicRedistribution':'held'},**extra});return id
limits=['Source has no observed skin fold/colour or palpated depression. AI indicator is a static structural teaching approximation.','Ray/closest facet only registers independently named anatomical relations; it is not their semantic evidence.']
def lm(code,side,c,source,a,surface,label,construction):
 assert source['side']==side
 obs={'code':code,'side':side,'sourceKey':source['id'],'native':{'carrierId':source['id'],'carrierRevision':source['revision'],'carrierHash':source['topologySha256'],'frameId':context['frameId'],'unit':'m','poseId':context['poseId'],'side':side,**a},'nativeWorld':at(source,a).tolist(),'surface':{**surface,'carrierId':c['id']},'surfaceWorld':at(c,surface).tolist(),'anatomy':label,'construction':construction,'limitations':limits};annotations.append(obs)
 return {'id':f'{code}-{side}-lm{len(annotations)}','anatomy':label,'acquisition':'anatomical_annotation','side':side,'sourceKey':source['id'],'native':obs['native'],'surface':obs['surface'],'evidenceId':note(code,side,c,'landmark_annotation',json.dumps(obs,ensure_ascii=False)),'role':'anatomical_landmark','modelIndicator':{'kind':'educational_model_indicator','observedSkinLandmark':False,'construction':construction,'limitations':limits}}
def make(code,side,c,ls,rule,extra=''):
 relation=facts['locations'][code]+' '+extra;rid=note(code,side,c,'location_relation',relation);sid=note(code,side,c,'surface_registration','Frozen native anatomical indicator to registered surface; no observed skin assertion.',maxRegistrationGapMetres=.02)
 units.append({'id':f'{code}-{side}','scope':'real_input','code':code,'side':side,'revision':'AT8-native-r1','context':context,'carrierId':c['id'],'originalText':facts['locations'][code],'originalSources':[{**facts['source'],'locator':evidence[-2]['source']['locator']}],'author':'ai','professorReview':'not_performed','landmarks':ls,'rule':rule,'relationEvidenceId':rid,'surfaceEvidenceId':sid})
def direct(code,side,carrier_id,p,direction,refs,label):
 c=carrier(carrier_id);surface=address(c,p,direction);ls=[]
 for name,a,anatomy in refs:
  ng=geometry(name,side);ls.append(lm(code,side,c,ng,a,surface,anatomy,label))
 # Superficial correspondence facet is selected near the already defined structural interval.
 # Its identity is never substituted for the deeper joint/tendon relation.
 if any(np.linalg.norm(at(native[l['sourceKey']],l['native'])-at(c,surface))>.02 for l in ls):raise ValueError('Anatomical reference exceeds 20mm surface correspondence tolerance; local indicator required')
 make(code,side,c,ls,{'kind':'landmark','landmark':ls[0]['id']},label);prepared[side,code]=(c,surface,ls)
def path(ids,start,end,side):
 key=tuple(ids)+(side,)
 if key not in graphs:
  edges={};centres={};adj={};faces={}
  for id in ids:
   c=carrier(id);v,t=arrays(c)
   for i,idx in enumerate(t):
    if not (v[idx,0]<0).all() if side=='right' else not (v[idx,0]>0).all():continue
    f=(id,i);faces[f]=idx;centres[f]=v[idx].mean(0);adj[f]=[]
    for a,b in [(idx[0],idx[1]),(idx[1],idx[2]),(idx[2],idx[0])]:edges.setdefault(tuple(sorted([tuple(v[a]),tuple(v[b])])),[]).append(f)
  shared={}
  for e,fs in edges.items():
   if len(fs)==2:a,b=fs;adj[a].append(b);adj[b].append(a);shared[a,b]=shared[b,a]=np.mean(e,0)
  graphs[key]=(centres,adj,shared)
 centres,adj,shared=graphs[key];a=(start['carrierId'],start['triangle']);b=(end['carrierId'],end['triangle']);pa=at(carriers[a[0]],start);pb=at(carriers[b[0]],end);axis=pb-pa;length=np.linalg.norm(axis);assert length>1e-6
 dist={a:0};prev={};queue=[(0,a)]
 while queue:
  cost,k=heapq.heappop(queue)
  if cost!=dist[k]:continue
  if k==b:break
  for n in adj[k]:
   p=centres[n];f=np.clip(np.dot(p-pa,axis)/length**2,0,1);deviation=np.linalg.norm(p-(pa+axis*f))
   if deviation>.06:continue
   nc=cost+np.linalg.norm(centres[k]-p)*(1+30*deviation)
   if nc<dist.get(n,1e9):dist[n]=nc;prev[n]=k;heapq.heappush(queue,(nc,n))
 if b not in dist:raise ValueError('No supported connected anatomical corridor; no seam/air bridge')
 chain=[b]
 while chain[-1]!=a:chain.append(prev[chain[-1]])
 chain.reverse();out=[];p=pa
 def bary(id,i,p):
  v,t=arrays(carriers[id]);tri=v[t[i]];uv=np.linalg.lstsq((tri[1:]-tri[0]).T,p-tri[0],rcond=None)[0];w=np.maximum([1-uv.sum(),*uv],0);return (w/w.sum()).tolist()
 for j,k in enumerate(chain):
  q=shared[k,chain[j+1]] if j+1<len(chain) else pb
  if np.linalg.norm(p-q)>1e-9:out.append({'carrierId':k[0],'triangle':k[1],'from':bary(*k,p),'to':bary(*k,q)})
  p=q
 return out

def proportion(code,side,first,last,value,total,ids,extra):
 c0,a0,l0=prepared[side,first];c1,a1,l1=prepared[side,last];line=path(ids,{**a0,'carrierId':c0['id']},{**a1,'carrierId':c1['id']},side);origin=at(c0,a0);axis=at(c1,a1)-origin;axis/=np.linalg.norm(axis);extent=np.dot(at(c1,a1)-origin,axis);target=value/total*extent;c=None
 for seg in line:
  cc=carriers[seg['carrierId']];p=at(cc,{'triangle':seg['triangle'],'barycentric':seg['from']});q=at(cc,{'triangle':seg['triangle'],'barycentric':seg['to']});x=np.dot(p-origin,axis);y=np.dot(q-origin,axis)
  if min(x,y)<=target<=max(x,y):c=cc;break
 assert c is not None,'missing plane crossing'
 ls=[]
 for l in [l0[0],l1[0]]:
  l=json.loads(json.dumps(l));l['evidenceId']=note(code,side,c,'landmark_annotation',json.dumps(l,ensure_ascii=False));ls.append(l)
 ev=note(code,side,c,'proportion',f'WHO p12: {total} B-cun named joint/crease interval; '+extra,measurement={'kind':'B-cun','value':total},measurementAxis='anatomical_native_axis')
 make(code,side,c,ls,{'kind':'B-cun','from':ls[0]['id'],'to':ls[1]['id'],'value':value,'totalCun':total,'measurementAxis':{'from':ls[0]['id'],'to':ls[1]['id']},'path':line,'evidenceId':ev},extra)

def attempt(code,side,fn):
 try:fn()
 except Exception as ex:failures.append({'code':code,'side':side,'attempt':'Anatomical native address -> semantic interval -> registered carrier -> shared compiler (no projection fallback)','error':str(ex),'neededInput':'See per-code rule and actual support audit; an independently source-addressed valid surface/relationship is required.'})

for side in ['right','left']:
 sign=-1 if side=='right' else 1;radial=[sign,0,-.4];dorsal=[0,0,-1];posterior=[0,0,-1]
 # MC2 MCP head and base are actually addressed extremities. Midshaft is a bone-specific anatomical construction.
 mc,head,hp=facet('Second metacarpal bone',side,1,'min');_,base,bp=facet('Second metacarpal bone',side,1,'max');_,shaft,sp=facet('Second metacarpal bone',side,near=(hp+bp)/2)
 for code,p,a,label in [('LI3',hp+np.array([sign*.004,.006,0]),head,'Radial/proximal MC2 head contour, not a red-white colour assertion.'),('LI4',sp+np.array([sign*.004,0,0]),shaft,'Radial MC2 shaft midpoint defined by independently addressed head/base, not hand bounds.')]:
  attempt(code,side,lambda code=code,p=p,a=a,label=label:direct(code,side,'hand-link-'+side+'-0',p,radial,[('Second metacarpal bone',a,'MC2 head/base-midshaft radial contour')],label))
 # LI2 on distal side of MCP head is checked on finger surface, never shifted to palm.
 ph,phbase,php=facet('Proximal phalanx of second finger of hand',side,1,'max');attempt('LI2',side,lambda:direct('LI2',side,'finger-'+side+'-2-0',(hp+php)/2,radial,[('Proximal phalanx of second finger of hand',phbase,'MCP2 proximal phalangeal base radial contour')],'Native MC2-head to proximal-phalanx-base joint interval; model radial surface corresponds to absent red-white border.'))
 m4,h4,p4=facet('Fourth metacarpal bone',side,1,'min');m5,h5,p5=facet('Fifth metacarpal bone',side,near=p4)
 attempt('TE3',side,lambda:direct('TE3',side,'hand-link-'+side+'-0',(p4+p5)/2+np.array([0,.006,0]),dorsal,[('Fourth metacarpal bone',h4,'MCP4 proximal interval'),('Fifth metacarpal bone',h5,'MC4-MC5 interval')],'Actual MC4 and MC5 facets identify dorsal intermetacarpal interval proximal to MCP4.'))
 # Wrist shared seam reuses the AT6 carrier. EPL/EPB actual sections at radial styloid plane define LI5.
 radius,ra,rp=facet('Radius',side,1,'min');y=rp[1]
 try:epl,ea,ep=slice_point('Extensor pollicis longus',side,y,0,'min' if side=='right' else 'max');epb,ba,bp2=slice_point('Extensor pollicis brevis',side,y,0,'max' if side=='right' else 'min')
 except Exception as ex:failures.append({'code':'LI5','side':side,'error':str(ex),'neededInput':'Snuffbox EPL/EPB native sections at styloid plane'});epl=None
 if epl is not None:attempt('LI5',side,lambda:direct('LI5',side,'wrist-link-'+side+'-0',(ep+bp2)/2,radial,[('Extensor pollicis longus',ea,'EPL border of snuffbox'),('Extensor pollicis brevis',ba,'EPB border of snuffbox')],'Static model snuffbox between actual two extensor tendon sections distal to styloid; no abducted depression/crease claimed.'))
 u,ua,up=facet('Ulna',side,1,'max');h,ha,hp2=facet('Humerus',side,0,'min' if side=='right' else 'max',mask=lambda x:x[:,1]<1.14)
 lu5doc=read(R/'work/evidence/AT6/resume-r1/bilateral-rules-r9.json');lu5=next(u for u in lu5doc['units'] if u['code']=='LU5' and u['side']==side);l5=lu5['landmarks'][0];gg=geometry('Long head of biceps brachii',side);lp=at(gg,l5['native']);p11=(lp+hp2)/2
 attempt('LI11',side,lambda:direct('LI11',side,'arm-'+side+'-1',p11,radial,[('Humerus',ha,'Actual lateral humeral epicondyle'),('Long head of biceps brachii',l5['native'],'Verified LU5 distal biceps correspondence')],'WHO midpoint LU5-to-lateral-epicondyle; both actual native addresses retained. Extended elbow teaching correspondence, not observed flexed crease.'))
 _,ridge,ridgep=facet('Humerus',side,near=hp2+np.array([0,.012,.003]));attempt('LI12',side,lambda:direct('LI12',side,'arm-'+side+'-1',ridgep,radial,[('Humerus',ridge,'Lateral supraepicondylar ridge above lateral epicondyle')],'Actual lateral humeral distal ridge, anterior/lateral contour; no generic arm ratio.'))
 for code,v in [('LI6',3),('LI7',5),('LI8',8),('LI9',9),('LI10',10)]:attempt(code,side,lambda code=code,v=v:proportion(code,side,'LI5','LI11',v,12,['wrist-link-'+side+'-0','arm-'+side+'-0','arm-'+side+'-1'],'Named radial dorsal wrist-to-lateral cubital interval 12 B-cun; connected carrier path crosses anatomical longitudinal plane.'))
 # Dorsal wrist extensor digitorum and the MC4/5 proximal direction.
 try:ed,eda,edp=slice_point('Extensor digitorum',side,y,0,'max' if side=='right' else 'min');edp=edp+np.array([-sign*.003,0,0]);attempt('TE4',side,lambda:direct('TE4',side,'wrist-link-'+side+'-0',edp,dorsal,[('Extensor digitorum',eda,'Ulnar border of extensor digitorum at radiocarpal level')],'Actual extensor digitorum dorsal wrist tendon; ulnar teaching interval, not observed dorsal skin crease.'))
 except Exception as ex:failures.append({'code':'TE4','side':side,'error':str(ex),'neededInput':'Dorsal ED tendon and MC4/5 proximal interval'})
 # Endpoint of dorsal forearm measurement at olecranon, not a TE product point.
 try:
  c=carrier('arm-'+side+'-1');sf=address(c,up,posterior);l=lm('TE5',side,c,u,ua,sf,'Olecranon prominence anatomical endpoint','Native proximal ulnar olecranon address defines posterior elbow measurement level.');prepared[side,'OLECRANON']=(c,sf,[l])
 except Exception as ex:failures.append({'code':'TE5-TE9','side':side,'error':str(ex),'neededInput':'Connected source-bound olecranon surface endpoint'})
 for code,v in [('TE5',2),('TE6',3),('TE8',4),('TE9',7)]:attempt(code,side,lambda code=code,v=v:proportion(code,side,'TE4','OLECRANON',v,12,['wrist-link-'+side+'-0','arm-'+side+'-0','arm-'+side+'-1'],'Dorsal wrist-to-olecranon interval 12 B-cun. Actual radius/ulna are observation references; direction follows posterior interosseous corridor.'))
 # Neck directly supported by independently addressed SCM and actual cartilage-height planes.
 for code,cart,which in [('LI17','Cricoid cartilage','midpoint'),('LI18','Thyroid cartilage','superior')]:
  ng,aa,pp=facet(cart,None,1,'max')
  if which=='midpoint':ng,ab,pb=facet(cart,None,1,'min');pp=(pp+pb)/2
  try:sc,sa,ps=slice_point('Sternocleidomastoid muscle',side,float(pp[1]),2,'min' if code=='LI17' else 'max');attempt(code,side,lambda code=code,sa=sa,ps=ps:direct(code,side,'neck-link-0',ps,[sign,0,.5],[('Sternocleidomastoid muscle',sa,'SCM border at independently observed laryngeal cartilage plane')],'Cricoid midpoint or thyroid superior native plane transferred to actual SCM surface; source cartilage address preserved in native inspection, no invented skin fold.'))
  except Exception as ex:failures.append({'code':code,'side':side,'error':str(ex),'neededInput':'Actual SCM/native cartilage level and matching neck carrier'})
 # Orbital superolateral muscle contour supports only an explicit eyebrow model indicator.
 og,oa,op=facet('Orbital part of orbicularis oculi',side,0,'min' if side=='right' else 'max',mask=lambda c:c[:,1]>1.602)
 attempt('TE23',side,lambda:direct('TE23',side,'head-0',op,[sign*.35,0,1],[('Orbital part of orbicularis oculi',oa,'Superolateral orbital rim muscular contour')],'AI model eyebrow-tail indicator on the superolateral orbital contour; actual eyebrow hair/skin depression not observed.'))
 # No product positions for actual missing ear/mobile/web/nail calibration input. Listed native alternatives remain context, not fake points.
 blocked={ 'LI1':'Index radial proximal nail-base corner and thumb-IP F-cun transfer must be independently addressed; existing nail probe exists but no accepted index calibration/membrane yet.', 'TE1':'Ring ulnar proximal nail-base corner and native proximal direction/F-cun transfer need independent authoring; no relocation onto finger shaft.', 'TE2':'Actual ring/little web margin is absent in separated AT4 finger envelopes; a connected web carrier requires source-supported native web geometry.', 'LI13':'Native anterior axillary insertion to lateral cubital 9 B-cun calibration and lateral LI11-LI15 corridor not yet authorable from existing accepted endpoints.', 'LI14':'Requires independently addressed anterior deltoid edge at 7 B-cun elbow level; no whole-arm bounds ratio.', 'LI15':'Actual anterior acromion/greater-tubercle interval needs facet inspection and static-pose depression correspondence.', 'LI16':'Actual acromial clavicle end and scapular spine interval requires independent two-landmark facet annotation.', 'LI19':'Native philtrum and nostril lateral-border correspondence is not established; nose muscle is not a nostril.', 'LI20':'Lateral nasal-ala midpoint with nasolabial sulcus correspondence needs source cartilage and surface annotation; no automatic nose bounds point.', 'TE7':'Requires just-radial-to-ulna corridor at independently calibrated 3 B-cun plane, distinct from interosseous midpoint.', 'TE10':'Requires native olecranon-to-posterior axillary 9 B-cun calibration, then 1 B-cun proximal static fossa correspondence.', 'TE11':'Native posterior axillary calibration and acromial-angle line need actual endpoint annotations.', 'TE12':'Native posterior axillary calibration and acromial-angle line need actual endpoint annotations.', 'TE13':'Posteroinferior deltoid edge and 3 B-cun below actual acromial angle require source-specific calibration.', 'TE14':'Actual posterior acromial-angle/greater-tubercle depression not yet independently addressed.', 'TE15':'Actual scapular superior angle and superior depression need source facet correspondence.', 'TE16':'Mandibular angle level and posterior SCM contour need ipsilateral shared-midline native-reference contract.', 'TE17':'Source runtime contains no auricle/earlobule/tragus; mastoid alone cannot locate posterior-earlobule interval.', 'TE18':'TE17-TE20 endpoints require absent earlobule/auricular apex; mastoid surface alone is insufficient.', 'TE19':'TE17-TE20 curved path endpoints require absent ear native landmarks.', 'TE20':'Native auricular apex is absent; temporal bone is not an auricular apex.', 'TE21':'Actual supratragic notch is absent; mandibular condyle alone is insufficient.', 'TE22':'Native auricular root and temple hairline absent; no skin coordinate inferred from temporal bounds.' }
 for code,needed in blocked.items():
  failures.append({'code':code,'side':side,'attempt':'Compared WHO relation, actual independent native inventory, AT3/4/6 carrier topology and source probes; no coordinates promoted','error':'Required semantic/geometry/calibration input not established','neededInput':needed})

out={'schemaVersion':2,'context':context,'units':units,'inputs':{'domain':'real_input','carriers':carriers,'native':native,'evidence':evidence}}
for name,data in [('rules-r2',out),('annotations-r2',annotations),('author-failures-r2',failures),('source-input-hashes-r2',inputs)]:
 (E/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
print('authored',len(units),'failed/blocked',len(failures));print([(x['code'],x['side'],x['error']) for x in failures if 'Required semantic' not in x['error']])
