"""Source-ring/native-facet local registration with ARAP and determinant guard.

Offline only. Does not approve landmark semantics or mutate native/QA inputs.
Positive one-ring affine gradients are diagnosed independently of global collisions.
"""
from pathlib import Path
import argparse,sys,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--revision',default='r23');p.add_argument('--parts',default='hand,foot');p.add_argument('--steps',type=int,default=12);p.add_argument('--guard',choices=['one-ring','skin-prism','active-prism'],default='active-prism');p.add_argument('--extended-reference',action='store_true');args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);E=R/args.evidence;B=R/'work/evidence/AT10/2026-10-13-skin-fit-r1';B2=R/'work/evidence/AT10/2026-10-13-skin-fit-r2'
d=json.loads((B2/'candidates/fit-r22.json').read_text());source=np.array(d['sourceVertices']);v=np.array(d['positions']);before=v.copy();ctrl={c['id']:c for c in json.loads((B/'native-controls-r2.json').read_text())['controls']};native=json.loads((B/'native-surfaces-r1.json').read_text());faces=[f['derivedVertices'] for f in d['faces']];edges=np.array(sorted({tuple(sorted((a,b))) for f in faces for a,b in zip(f,f[1:]+f[:1])}));records=[];logs=[]
def frame(axis,width):
 axis=axis/np.linalg.norm(axis);width=width-axis*np.dot(axis,width);width/=np.linalg.norm(width);return np.column_stack([axis,width,np.cross(axis,width)])
def cap(side,name,end):
 key=next(k for k,s in native.items() if s['side']==side and s['name']==name);nv=np.array(native[key]['v']);low=nv[:,1].min();high=nv[:,1].max();ids=np.flatnonzero(nv[:,1]<low+(high-low)*.04) if end=='distal' else np.flatnonzero(nv[:,1]>high-(high-low)*.04);nt=np.array(native[key]['t']);ti=int(np.flatnonzero(np.isin(nt,ids).any(1))[0]);return nv[ids].mean(0),{'sourceKey':key,'nativeVertexIds':ids.tolist(),'nativeTriangle':ti,'nativeWorldM':nv[nt[ti]].tolist(),'operator':'observed distal cap mean; dimensional axis, not a skin crease'}
def smoothstep(x):x=np.clip(x,0,1);return x*x*(3-2*x)
def context(side,terms,a,b,radius):
 vertices=[];triangles=[];addresses=[];axis=b-a;length=np.linalg.norm(axis);axis/=length
 for key,s in native.items():
  if s['side']!=side or not any(t in s['name'].lower() for t in terms):continue
  nv=np.array(s['v']);nt=np.array(s['t']);q=nv[nt].mean(1)-a;f=q@axis;rad=np.linalg.norm(q-np.outer(f,axis),axis=1);selected=np.flatnonzero((f>-.022)&(f<length+.023)&(rad<radius));off=len(vertices);vertices.extend(nv);triangles.extend((nt[selected]+off).tolist());addresses.extend([(key,int(i)) for i in selected])
 return BVHTree.FromPolygons(vertices,triangles,all_triangles=True),addresses,a,b,radius
def ring_constraints(ids,sa,sb,ta,tb,sw,tw,ctx,label,stations,gap):
 sf=frame(sb-sa,sw);tf=frame(tb-ta,tw);sl=np.linalg.norm(sb-sa);tl=np.linalg.norm(tb-ta);q=(source[ids]-sa)@sf;rows=[]
 for station in stations:
  ring=np.flatnonzero((np.abs(q[:,0]-station*sl)<.0035)&(np.linalg.norm(q[:,1:],axis=1)>.001)&(np.linalg.norm(q[:,1:],axis=1)<.055))
  if len(ring)<5:continue
  theta=np.arctan2(q[ring,2],q[ring,1]);rad=np.linalg.norm(q[ring,1:],axis=1)
  for angle in np.linspace(-np.pi,np.pi,12,endpoint=False):
   # Original vertex and joint-local ring role, never anonymous bounds ratios.
   score=np.abs(np.angle(np.exp(1j*(theta-angle))))+np.abs(q[ring,0]-station*sl)/.01
   si=int(ids[ring[np.argmin(score)]]);local=(source[si]-sa)@sf;actualAngle=np.arctan2(local[2],local[1]);u=local[0]/sl;direction=tf[:,1]*np.cos(actualAngle)+tf[:,2]*np.sin(actualAngle);centre=ta+tf[:,0]*u*tl
   origin=centre+direction*.15;point=None;remaining=.18
   # A selected long fascia facet may extend beyond its centroid's context.
   # Reject out-of-context hits rather than turning a calf surface into foot skin.
   for _ in range(32):
    hit,n,fi,dist=ctx[0].ray_cast(Vector(origin),Vector(-direction),remaining)
    if hit is None:break
    h=np.array(hit);delta=h-ctx[2];axis=(ctx[3]-ctx[2]);length=np.linalg.norm(axis);axis/=length;axial=np.dot(delta,axis);radial=np.linalg.norm(delta-axis*axial)
    if radial<ctx[4] and axial>-.022 and axial<length+.023:point=hit;break
    remaining-=dist+.00001;origin=h-direction*.00001
    if remaining<=0:break
   if point is None:continue
   key,ti=ctx[1][fi];nt=np.array(native[key]['t'])[ti];nv=np.array(native[key]['v'])[nt];target=np.array(point)+direction*gap
   rows.append({'id':label+f'-{station}-{angle:.5f}','vertex':si,'sourceVertex':d['originalVertexIds'][si],'sourceObjFaces':[d['faces'][j]['sourceFace'] for j,f in enumerate(faces) if si in f], 'sourceM':source[si].tolist(),'targetM':target.tolist(),'role':label,'sourceJointFrame':sf.tolist(),'nativeJointFrame':tf.tolist(),'sourceAxialFraction':float(u),'sourceRingAngleRad':float(actualAngle),'sampleSlotAngleRad':float(angle),'nativeSourceKey':key,'nativeTriangle':ti,'nativeWorldM':nv.tolist(),'skinAllowanceM':gap,'operator':'joint-local homologous section ray; geometric registration, not acupoint meaning','placementVerified':False})
 return rows
def arap(ids,rest,initial,constraints,roots,label):
 lookup=np.full(len(v),-1);lookup[ids]=np.arange(len(ids));selected=(lookup[edges]>=0).all(1);ee=lookup[edges[selected]];aa=ee[:,0];bb=ee[:,1];pe=rest[aa]-rest[bb];w=1/np.maximum(np.linalg.norm(pe,axis=1),.001);n=len(ids)
 degree=np.bincount(np.r_[aa,bb],weights=np.r_[w,w],minlength=n);fixed=np.zeros(n);targetsum=np.zeros((n,3));targetcount=np.zeros(n);targets=[]
 for row in constraints:
  i=lookup[row['vertex']]
  if i<0:continue
  targetsum[i]+=row['targetM'];targetcount[i]+=1
 targets=np.divide(targetsum,np.maximum(targetcount,1)[:,None]);fixed[targetcount>0]=degree[targetcount>0]*40
 rootlocal=lookup[roots];fixed[rootlocal]=degree[rootlocal]*120;targets[rootlocal]=v[roots]
 qq=initial.copy();original=qq.copy();diag=degree+fixed
 def mat(x):
  out=diag[:,None]*x;np.add.at(out,aa,-w[:,None]*x[bb]);np.add.at(out,bb,-w[:,None]*x[aa]);return out
 def cg(rhs,x):
  r=rhs-mat(x);z=r/diag[:,None];dr=z.copy();rz=(r*z).sum(0)
  for _ in range(180):
   ad=mat(dr);alpha=rz/np.maximum((dr*ad).sum(0),1e-30);x=x+dr*alpha;r=r-ad*alpha
   if np.linalg.norm(r)<1e-6:break
   z=r/diag[:,None];rn=(r*z).sum(0);dr=z+dr*(rn/np.maximum(rz,1e-30));rz=rn
  return x
 # One-ring volume gradient has a small isotropic rest regularizer. This is
 # an explicit local diagnostic, not a tetrahedral/global injectivity proof.
 covariance=np.zeros((n,3,3));pp=w[:,None,None]*pe[:,:,None]*pe[:,None,:];np.add.at(covariance,aa,pp);np.add.at(covariance,bb,pp);epsilon=np.trace(covariance,axis1=1,axis2=2)*1e-4+1e-10;inv=np.linalg.inv(covariance+epsilon[:,None,None]*np.eye(3))
 def rotations(x):
  qe=x[aa]-x[bb];c=np.zeros((n,3,3));val=w[:,None,None]*qe[:,:,None]*pe[:,None,:];np.add.at(c,aa,val);np.add.at(c,bb,val);u,_,vt=np.linalg.svd(c);det=np.linalg.det(u@vt);u[:,:,2]*=np.where(det<0,-1,1)[:,None];rot=u@vt;gradient=(c+epsilon[:,None,None]*rot)@inv;return rot,np.linalg.det(gradient)
 localtri=np.array([[f[0],f[j],f[j+1]] for f in faces for j in range(1,len(f)-1)]);localtri=lookup[localtri];localtri=localtri[(localtri>=0).all(1)];pn=np.cross(rest[localtri[:,1]]-rest[localtri[:,0]],rest[localtri[:,2]]-rest[localtri[:,0]]);area=np.maximum(np.linalg.norm(pn,axis=1),1e-15)
 def prism(x,previousRotation):
  expected=((previousRotation[localtri[:,0]]+previousRotation[localtri[:,1]]+previousRotation[localtri[:,2]])/3)@pn[:,:,None];expected=expected[:,:,0];expected/=np.maximum(np.linalg.norm(expected,axis=1)[:,None],1e-15);qn=np.cross(x[localtri[:,1]]-x[localtri[:,0]],x[localtri[:,2]]-x[localtri[:,0]]);return np.einsum('ij,ij->i',qn,expected)/area
 entries=[];rot,det=rotations(qq)
 for stage in range(1,args.steps+1):
  stageTargets=original+(targets-original)*(stage/args.steps)
  for iteration in range(12):
   rot,det=rotations(qq);rhs=np.zeros_like(qq);e=.5*(rot[aa]+rot[bb])@pe[:,:,None];e=e[:,:,0]*w[:,None];np.add.at(rhs,aa,e);np.add.at(rhs,bb,-e);rhs+=fixed[:,None]*stageTargets
   proposed=cg(rhs,qq.copy());step=1.;oldmin=det.min();guard=max(.01,min(oldmin,.05))
   if args.guard=='active-prism':
    scales=np.ones(n);violating=np.array([],dtype=int)
    for _ in range(30):
     trial=qq+(proposed-qq)*scales[:,None];trialRotation,_=rotations(trial);signed=np.minimum(prism(trial,rot),prism(trial,trialRotation));violating=np.flatnonzero(signed<=.01)
     if not len(violating):break
     affected=np.unique(localtri[violating].ravel());scales[affected]*=.5
    if len(violating):
     # No unchecked last-minute freeze: changed neighbour rotations can invert
     # an adjacent face. Keep the last actually verified state instead.
     break
    step=float(scales.min())
   else:
    while step>1/1024:
     trial=qq+(proposed-qq)*step;_,td=rotations(trial)
     test=td.min()>guard if args.guard=='one-ring' else prism(trial,rot).min()>.03
     if test:break
     step*=.5
    if step<=1/1024:break
   qq=trial
  signed=prism(qq,rot);rot,det=rotations(qq);error=np.linalg.norm(qq[targetcount>0]-targets[targetcount>0],axis=1);entry={'patch':label,'stage':stage,'guard':args.guard,'minimumSignedSkinPrismJacobian':float(signed.min()),'nonPositiveSkinPrisms':int((signed<=0).sum()),'minimumRegularizedOneRingDeterminant':float(det.min()),'nonPositiveOneRingCount':int((det<=0).sum()),'maximumTargetResidualM':float(error.max()) if len(error) else None,'lineSearchStep':step};entries.append(entry);print(entry,flush=True)
 v[ids]=qq;logs.extend(entries)
 return {'patch':label,'vertices':len(ids),'constraints':len(constraints),'rootVertices':roots.tolist(),'determinantMeaning':'one-ring affine curvature diagnostic + explicit 1 mm source tangent/transported-normal skin prism signed volume ratio; no global injectivity claim','guard':args.guard,'minimumSignedSkinPrismJacobian':float(signed.min()),'nonPositiveSkinPrisms':int((signed<=0).sum()),'finalMinimumDeterminant':float(det.min()),'nonPositiveOneRingCount':int((det<=0).sum()),'maximumTargetResidualM':float(error.max()) if len(error) else None,'constraintsData':constraints}
def digit_ownership(ids,prefix,parts):
 distances=[];labels=[]
 for di in range(1,6):
  for part in parts:
   aa=np.array(ctrl[f'{prefix}{di}-{part}']['source']);bb=np.array(ctrl[f'{prefix}{di}-{part+1}']['source']);axis=bb-aa;uu=np.clip((source[ids]-aa)@axis/np.dot(axis,axis),0,1);distances.append(np.linalg.norm(source[ids]-(aa+uu[:,None]*axis),axis=1));labels.append((di,part))
 closest=np.argmin(np.array(distances),axis=0);return np.array(labels)[closest]
for side,letter,sign in [('left','l',1),('right','r',-1)]:
 for kind in args.parts.split(','):
  rows=[];extension=None
  if kind=='hand':
   fr=d['articulatedFrames'][side];sw=np.array(fr['sourceWrist']);tw=np.array(fr['targetWrist']);sf=np.array(fr['sourcePalmFrame']);tf=np.array(fr['targetPalmFrame']);progress=(source-sw)@sf[:,0];ids=np.flatnonzero((source[:,0]*sign>.36)&(progress>-.07));scale=np.array(fr['palmScale']);scale[2]=1.25;rest=tw+((source[ids]-sw)@sf*scale)@tf.T
   if args.extended_reference:
    se=np.array(ctrl[f'joint-{letter}-elbow']['source']);te=np.array(ctrl[f'joint-{letter}-elbow']['target']);axis=sw-se;u=(source-se)@axis/np.dot(axis,axis);rad=np.linalg.norm(source-(se+np.clip(u,0,1)[:,None]*axis),axis=1);ids=np.flatnonzero(((source[:,0]*sign>.22)&(u>.08)&(u<1.05)&(rad<.065))|((source[:,0]*sign>.36)&(progress>-.07)));radialSource=np.array(ctrl[f'joint-{letter}-finger-1-1']['source'])-ctrl[f'joint-{letter}-finger-5-1']['source'];radius,rr=cap(side,'Radius','distal');ulna,ur=cap(side,'Ulna','distal');afs=frame(sw-se,radialSource);aft=frame(tw-te,radius-ulna);fore=tw+((source[ids]-sw)@afs*np.array([np.linalg.norm(tw-te)/np.linalg.norm(sw-se),1.,1.]))@aft.T;hand=tw+((source[ids]-sw)@sf*scale)@tf.T;w=smoothstep((progress[ids]+.075)/.045);rest=fore*(1-w[:,None])+hand*w[:,None];extension={'id':'source-radial-ulnar-to-native-Radius-Ulna','sourceElbowJoint':ctrl[f'joint-{letter}-elbow'],'sourceWristJoint':ctrl[f'joint-{letter}-hand'],'sourceRadialModelIndicator':'thumb CMC helper toward little MCP helper, distinct from source bone/skin-crease observation','nativeCapReferences':[rr,ur],'sourceForearmFrame':afs.tolist(),'nativeForearmFrame':aft.tolist(),'properRotationDeterminant':float(np.linalg.det(aft@afs.T)),'sourceTransitionIntervalM':[-.075,-.03]};ctx=context(side,['radius','ulna','flexor','extensor','pronator','supinator','brachioradialis','antebrachial fascia'],te,tw,.075);rows+=ring_constraints(ids,se,sw,te,tw,afs[:,1],aft[:,1],ctx,'forearm-wrist-continuity-'+side,[.18,.4,.7,.9],.005)
   ownership=digit_ownership(ids,f'joint-{letter}-finger-',range(1,4));sm=np.mean([ctrl[f'joint-{letter}-finger-{i}-1']['source'] for i in range(2,6)],axis=0);tm=np.mean([ctrl[f'joint-{letter}-finger-{i}-1']['target'] for i in range(2,6)],axis=0);ctx=context(side,['radius','ulna','metacarpal','carpal','palmar','dorsal fascia of hand','lumbrical muscles of hand','tendon sheath'],tw,tm,.065);palmids=ids[progress[ids]<np.linalg.norm(sm-sw)*.9];rows+=ring_constraints(palmids,sw,sm,tw,tm,sf[:,1],tf[:,1],ctx,'wrist-palm-'+side,[-.1,.15,.4,.65],.004)
   for di in range(1,6):
    for part in range(1,4):
     ak=f'joint-{letter}-finger-{di}-{part}';bk=f'joint-{letter}-finger-{di}-{part+1}';sa=np.array(ctrl[ak]['source']);sb=np.array(ctrl[bk]['source']);ta=np.array(ctrl[ak]['target']);tb=np.array(ctrl[bk]['target']);word=['first','second','third','fourth','fifth'][di-1];terms=[f'phalanx of {word} finger of hand','dorsal fascia of hand','lumbrical muscles of hand','tendon sheath']
     if di==1 and part==1:terms.append('first metacarpal bone')
     ctx=context(side,terms,ta,tb,.014)
     # The homologous source digit uses its own bone-distance cohort.
     sframe=frame(sb-sa,sf[:,1]);q=(source[ids]-sa)@sframe;digitids=ids[(ownership[:,0]==di)&(ownership[:,1]==part)&(q[:,0]>-.004)&(q[:,0]<np.linalg.norm(sb-sa)+.005)&(np.linalg.norm(q[:,1:],axis=1)<.012)]
     rows+=ring_constraints(digitids,sa,sb,ta,tb,sf[:,1],tf[:,1],ctx,f'finger-{side}-{di}-{part}',[.25,.6,.92],.003)
  elif kind=='foot':
   sw=np.array(ctrl[f'joint-{letter}-ankle']['source']);tw=np.array(ctrl[f'joint-{letter}-ankle']['target']);ids=np.flatnonzero((source[:,0]*sign>.055)&(source[:,1]<-.685));ownership=digit_ownership(ids,f'joint-{letter}-toe-',range(1,3));sm=np.mean([ctrl[f'joint-{letter}-toe-{di}-1']['source'] for di in range(1,6)],axis=0);tm=np.mean([ctrl[f'joint-{letter}-toe-{di}-1']['target'] for di in range(1,6)],axis=0);sourcewidth=np.array(ctrl[f'joint-{letter}-toe-5-1']['source'])-ctrl[f'joint-{letter}-toe-1-1']['source'];targetwidth=np.array(ctrl[f'joint-{letter}-toe-5-1']['target'])-ctrl[f'joint-{letter}-toe-1-1']['target'];sf=frame(sm-sw,sourcewidth);tf=frame(tm-tw,targetwidth);scale=np.array([np.linalg.norm(tm-tw)/np.linalg.norm(sm-sw),np.linalg.norm(targetwidth)/np.linalg.norm(sourcewidth),1.05]);rest=tw+((source[ids]-sw)@sf*scale)@tf.T
   if args.extended_reference:
    sk=np.array(ctrl[f'joint-{letter}-knee']['source']);tk=np.array(ctrl[f'joint-{letter}-knee']['target']);ids=np.flatnonzero((source[:,0]*sign>.03)&(source[:,1]<sk[1]-.02));ownership=digit_ownership(ids,f'joint-{letter}-toe-',range(1,3));tibia,tr=cap(side,'Tibia','distal');fibula,frcap=cap(side,'Fibula','distal');cfs=frame(sw-sk,sourcewidth);cft=frame(tw-tk,fibula-tibia);calf=tw+((source[ids]-sw)@cfs*np.array([np.linalg.norm(tw-tk)/np.linalg.norm(sw-sk),1.,1.]))@cft.T;foot=tw+((source[ids]-sw)@sf*scale)@tf.T;w=smoothstep((sw[1]+.10-source[ids,1])/.09);rest=calf*(1-w[:,None])+foot*w[:,None];extension={'id':'source-lateral-foot-model-indicator-to-native-Tibia-Fibula','sourceKneeJoint':ctrl[f'joint-{letter}-knee'],'sourceAnkleJoint':ctrl[f'joint-{letter}-ankle'],'nativeCapReferences':[tr,frcap],'sourceCalfFrame':cfs.tolist(),'nativeCalfFrame':cft.tolist(),'properRotationDeterminant':float(np.linalg.det(cft@cfs.T)),'sourceTransitionAboveAnkleM':[.10,.01]};ctx=context(side,['tibia','fibula','soleus','gastrocnemius','tibialis','fibularis','calcaneal','crural fascia'],tk,tw,.105);rows+=ring_constraints(ids,sk,sw,tk,tw,cfs[:,1],cft[:,1],ctx,'calf-ankle-continuity-'+side,[.18,.4,.7,.92],.006)
   sa=np.array([sign*.18,-.785,-.035]);sb=np.array([sign*.17,-.790,.133]);ta=np.array([sign*.0795,.035,-.075]);tb=np.array([sign*.085,.032,.082]);ctx=context(side,['talus','calcaneus','metatarsal','cuneiform','cuboid','navicular','plantar','foot','calcaneal','retinaculum','tendon sheath','tibialis','fibularis'],ta,tb,.063);bodyids=ids[source[ids,2]<.125];rows+=ring_constraints(bodyids,sa,sb,ta,tb,np.array([1.,0,0]),np.array([1.,0,0]),ctx,'heel-dorsal-plantar-MTP-'+side,[.05,.25,.5,.72,.95],.005)
   for di in range(1,6):
    for part in range(1,3):
     ak=f'joint-{letter}-toe-{di}-{part}';bk=f'joint-{letter}-toe-{di}-{part+1}';sa=np.array(ctrl[ak]['source']);sb=np.array(ctrl[bk]['source']);ta=np.array(ctrl[ak]['target']);tb=np.array(ctrl[bk]['target']);word=['first','second','third','fourth','fifth'][di-1];ctx=context(side,[f'phalanx of {word} finger of foot','tendon of extensor digitorum longus','tendon sheath of extensor hallucis','lumbrical muscles of foot'],ta,tb,.013);ss=frame(sb-sa,np.array([1.,0,0]));q=(source[ids]-sa)@ss;digitids=ids[(ownership[:,0]==di)&(ownership[:,1]==part)&(q[:,0]>-.005)&(q[:,0]<np.linalg.norm(sb-sa)+.005)&(np.linalg.norm(q[:,1:],axis=1)<.014)];rows+=ring_constraints(digitids,sa,sb,ta,tb,np.array([1.,0,0]),np.array([1.,0,0]),ctx,f'toe-{side}-{di}-{part}',[.25,.6,.93],.004)
  elif kind=='ear':
   ids=np.flatnonzero((source[:,0]*sign>.058)&(source[:,1]>.638)&(source[:,1]<.75)&(source[:,2]<.078));sf=np.eye(3);tf=np.eye(3);scale=np.array([1.10,.82,1.04]);centre=np.array([0,.685,.040]);targetCentre=np.array([0,1.580,-.008]);rest=(source[ids]-centre)*scale+targetCentre
   sideletter='l' if side=='left' else 'r';helixkey=next(k for k,s in native.items() if s['name']=='Helix.'+sideletter);helix=np.array(native[helixkey]['v']);natives=[helixkey]
   for sy in [.674,.684,.696,.710]:
    candidates=ids[(source[ids,0]*sign>.073)&(np.abs(source[ids,1]-sy)<.004)]
    if not len(candidates):continue
    si=int(candidates[np.argmax(source[candidates,0]*sign)]);ny=targetCentre[1]+(source[si,1]-centre[1])*scale[1];nn=np.flatnonzero(np.abs(helix[:,1]-ny)<.004)
    if not len(nn):nn=np.argsort(np.abs(helix[:,1]-ny))[:12]
    vi=int(nn[np.argmax(helix[nn,0]*sign)]);nt=np.array(native[helixkey]['t']);ti=int(np.flatnonzero((nt==vi).any(1))[0]);target=helix[vi]+[sign*.002,0,0]
    rows.append({'id':'helix-ridge-'+side+'-'+str(sy),'vertex':si,'sourceVertex':d['originalVertexIds'][si],'sourceObjFaces':[d['faces'][j]['sourceFace'] for j,f in enumerate(faces) if si in f],'sourceM':source[si].tolist(),'targetM':target.tolist(),'role':'authored source pinna lateral helix ridge station; visual review required','nativeSourceKey':helixkey,'nativeTriangle':ti,'nativeVertex':vi,'nativeWorldM':helix[nt[ti]].tolist(),'skinAllowanceM':.002,'placementVerified':False})
   for name,sourceRole in [('Lobule of auricle.','inferior-lobule'),('Tragus.','anterior-tragus')]:
    matches=[k for k,s in native.items() if s['name']==name+sideletter]
    if not matches:continue
    key=matches[0];natives.append(key);cloud=np.array(native[key]['v']);nt=np.array(native[key]['t']);vi=int(np.argmax(cloud[:,0]*sign));ti=int(np.flatnonzero((nt==vi).any(1))[0])
    if sourceRole=='inferior-lobule':cand=ids[(source[ids,0]*sign>.068)&(source[ids,2]>.022)];si=int(cand[np.argmin(source[cand,1])])
    else:cand=ids[(source[ids,1]>.671)&(source[ids,1]<.701)&(source[ids,0]*sign<.075)];si=int(cand[np.argmax(source[cand,2])])
    rows.append({'id':sourceRole+'-'+side,'vertex':si,'sourceVertex':d['originalVertexIds'][si],'sourceObjFaces':[d['faces'][j]['sourceFace'] for j,f in enumerate(faces) if si in f],'sourceM':source[si].tolist(),'targetM':(cloud[vi]+[sign*.002,0,0]).tolist(),'role':'authored source pinna '+sourceRole+' proposal, not an approved locating landmark','nativeSourceKey':key,'nativeTriangle':ti,'nativeVertex':vi,'nativeWorldM':cloud[nt[ti]].tolist(),'skinAllowanceM':.002,'placementVerified':False})
  elif kind=='pelvis':
   ids=np.flatnonzero((source[:,0]*sign>=0)&(np.abs(source[:,0])<.235)&(source[:,1]>-.26)&(source[:,1]<.115));sf=np.eye(3);tf=np.eye(3);scale=np.array([.94,1.02,1.06]);sw=np.array(ctrl['joint-pelvis']['source']);tw=np.array(ctrl['joint-pelvis']['target']);rest=tw+(source[ids]-sw)*scale
   sa=np.array(ctrl[f'joint-{letter}-upper-leg']['source']);sb=np.array(ctrl[f'joint-{letter}-knee']['source']);ta=np.array(ctrl[f'joint-{letter}-upper-leg']['target']);tb=np.array(ctrl[f'joint-{letter}-knee']['target']);ctx=context(side,['femur','vastus','rectus femoris','adductor','pectineus','gracilis','sartorius','fascia lata','biceps femoris','semitendinosus','semimembranosus','gluteus'],ta,tb,.145);thighids=ids[source[ids,1]<.018];rows+=ring_constraints(thighids,sa,sb,ta,tb,np.array([1.,0,0]),np.array([1.,0,0]),ctx,'pubic-medial-posterior-thigh-'+side,[.05,.18,.30,.42],.006)
   glutealkey=next(k for k,s in native.items() if s['side']==side and s['name']=='Gluteus maximus muscle');nv=np.array(native[glutealkey]['v']);nt=np.array(native[glutealkey]['t']);bvh=BVHTree.FromPolygons(nv.tolist(),nt.tolist(),all_triangles=True)
   posterior=ids[(source[ids,2]<-.04)&(source[ids,1]>-.10)&(source[ids,1]<.045)&(source[ids,0]*sign>.025)]
   for si in posterior[::max(1,len(posterior)//32)]:
    centre=v[si];point,n,ti,dist=bvh.ray_cast(Vector([centre[0],centre[1],-.35]),Vector([0,0,1]),.4)
    if point is None:continue
    target=np.array(point)+[0,0,-.006];rows.append({'id':'posterior-gluteal-surface-'+side+'-'+str(si),'vertex':int(si),'sourceVertex':d['originalVertexIds'][si],'sourceObjFaces':[d['faces'][j]['sourceFace'] for j,f in enumerate(faces) if si in f],'sourceM':source[si].tolist(),'targetM':target.tolist(),'role':'source posterior upper-thigh/gluteal skin patch matched to fixed named underlying Gluteus maximus; source pose/bone axis correspondence retained','nativeSourceKey':glutealkey,'nativeTriangle':int(ti),'nativeWorldM':nv[nt[ti]].tolist(),'skinAllowanceM':.006,'placementVerified':False})
  else:raise ValueError(kind)
  inpatch=np.zeros(len(v),bool);inpatch[ids]=True;boundary=edges[inpatch[edges].any(1)&~inpatch[edges].all(1)].ravel();roots=np.unique(boundary[inpatch[boundary]])
  # Start from the intact proper source shape, not the folded Gaussian/envelope.
  unique={};duplicates=[]
  for row in rows:
   i=row['vertex']
   if i in unique:
    if np.linalg.norm(np.array(unique[i]['targetM'])-row['targetM'])>.002:duplicates.append({'sourceVertex':d['originalVertexIds'][i],'priorRole':unique[i]['role'],'newRole':row['role'],'targetSeparationM':float(np.linalg.norm(np.array(unique[i]['targetM'])-row['targetM']))})
   # Digit-local ownership is more specific than the parent palm/foot body ring.
   unique[i]=row
  rec=arap(ids,rest,rest.copy(),list(unique.values()),roots,kind+'-'+side);rec['sourceReferenceFrame']=sf.tolist();rec['nativeReferenceFrame']=tf.tolist();rec['referenceScale']=scale.tolist();rec['duplicateRoleConflicts']=duplicates;rec['adjacentContinuityExtension']=extension;records.append(rec)
d['positions']=v.tolist();d['candidateRevision']=args.revision;d['fitAcceptancePassed']=False;d['learnerEligible']=False;d['foldAwareRegistration']={'method':'positive-weight source-edge ARAP with staged surface constraints and determinant line search','patches':[{k:val for k,val in r.items() if k!='constraintsData'} for r in records],'noGlobalInjectivityClaim':True,'geometryQARequired':True}
(E/f'candidates/fit-{args.revision}.json').write_text(json.dumps(d,separators=(',',':')))
(E/f'fold-aware-correspondence-{args.revision}.json').write_text(json.dumps({'patches':records,'logs':logs,'sourceHelpersAndFaceCornerUVUnchanged':True,'nativeModified':False,'anatomicalPointMeaning':False},indent=2)+'\n')
print('ARAP_WRITTEN',args.revision,flush=True)
