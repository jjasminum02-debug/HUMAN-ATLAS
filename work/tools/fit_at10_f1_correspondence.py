"""Offline right-foot source correspondence repair; never approves a skin.

Reuses r41 topology/hands, actual r52 toe cap addresses, and the shared exporter
and independent contact checker. Each Gaussian displacement has a conservative
GLOBAL Lipschitz bound <1, so its continuous 3D map is injective and orientation
preserving. This does not certify the straight emitted triangles or the seam.
No grid/cage, no native edits, and no nearest-surface anatomical approval.
"""
from pathlib import Path
import argparse, json, hashlib, sys
import numpy as np

R=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--revision',required=True)
p.add_argument('--recipe',help='Exact saved field replay, without solving again')
p.add_argument('--refine',action='store_true',help='Coarse-to-fine velocity support; same addressed targets, not a quality waiver')
p.add_argument('--surface-pairs',action='store_true',help='Actual closed source sections paired with addressed native containment supports')
p.add_argument('--continue-recipe',help='Continue a saved finite solve, preserving completed field stages')
p.add_argument('--centre-indicators',action='store_true',help='Separate source rig handles from authored inner model axes using own-digit closed skin sections')
a=p.parse_args();E=R/a.evidence;E.mkdir(exist_ok=True);(E/'candidates').mkdir(exist_ok=True)
load=lambda x:json.loads(x.read_text())
B=R/'work/evidence/AT10/2026-10-14-skin-fit-r5'
d=load(B/'candidates/fit-r41.json');s=np.array(d['sourceVertices']);old=np.array(d['positions']);v=old.copy()
f=load(B/'surface-bands-r52.json')['patches'][0];ids=np.array(f['sourceVertices']);n=len(s)
faces=[x['derivedVertices'] for x in d['faces']]
t=np.array([[z[0],z[j],z[j+1]] for z in faces for j in range(1,len(z)-1)])
edges=np.array(sorted({tuple(sorted((int(x),int(y)))) for z in t for x,y in zip(z,np.roll(z,-1))}))
mask=np.zeros(n,bool);mask[ids]=True
roots=np.unique(edges[mask[edges].any(1)&~mask[edges].all(1)][mask[edges[mask[edges].any(1)&~mask[edges].all(1)]]])
assert len(roots)==22
declared=np.array([x['sourceVertex'] for x in f['sharedBoundary']]);interior=np.setdiff1d(declared,roots)
native=load(R/'work/evidence/AT10/2026-10-13-skin-fit-r1/native-surfaces-r1.json')
native.update(load(B/'native-supplement-r1.json'))
controls=[]
def address(vi):
 return {'logicalVertex':int(vi),'originalVertex':d['originalVertexIds'][vi],
         'sourceObjFaces':[x['sourceFace'] for x in d['faces'] if vi in x['derivedVertices']], 'sourceM':s[vi].tolist()}
for vi in roots:
 controls.append(dict(id='actual-calf-seam-'+str(vi),source=s[vi].tolist(),target=old[vi].tolist(),
                      sourceAddress=address(vi),role='actual topological calf boundary; NOT ankle',sigmaM=.065))
for c in f['nativeJointControls']:
 row=dict(c);row['source']=c.get('sourceOriginalHelperM',c['source']);row['target']=list(c['target']);row['sigmaM']=.022 if 'toe' in c['id'] else .045
 row['role']='preserved source rig joint to observed native bone cap/joint model estimate'
 if 'toe' in c['id']:
  digit=int(c['id'].split('-')[-2]);part=int(c['id'].split('-')[-1]);last=3 if digit==1 else 4
  if part==last:
   prior=next(x for x in f['nativeJointControls'] if x['id']==c['id'][:-1]+str(part-1))
   axis=np.array(c['target'])-prior['target'];axis/=np.linalg.norm(axis)
   row['target']=(np.array(c['target'])+axis*.005).tolist()
   row['role']='authored outer toe-tip model control, not bone endpoint; original rig tip retained'
   row['authoredSkinPadM']=.005
 controls.append(row)

if a.centre_indicators:
 sys.path.insert(0,str(R/'work/tools'))
 from at10_surface_sections import section_loops
 localfaces=np.flatnonzero(mask[t].all(1));indicatorAudit=[]
 for digit in range(1,6):
  chain=[c for c in f['nativeJointControls'] if c['id'].startswith('joint-r-toe-'+str(digit)+'-')];observed=[]
  for part,(ca,cb) in enumerate(zip(chain[:-1],chain[1:])):
   sa=np.array(ca['sourceOriginalHelperM']);sb=np.array(cb['sourceOriginalHelperM']);axis=sb-sa;axis/=np.linalg.norm(axis)
   up=np.array([0.,1.,0.]);up-=axis*(up@axis);up/=np.linalg.norm(up);right=np.cross(up,axis)
   for fraction in [.35,.5,.72]:
    so=sa*(1-fraction)+sb*fraction;loops,opened=section_loops(s,t,so,axis,localfaces)
    selected=[];rejected=[]
    for loop in loops:
     pp=np.array([x['pointM'] for x in loop['nodes']]);q=pp-so;xx=q@right;yy=q@up;cross=xx*np.roll(yy,-1)-np.roll(xx,-1)*yy;area=cross.sum()/2
     if abs(area)<1e-12:continue
     centre=so+right*((xx+np.roll(xx,-1))*cross).sum()/(6*area)+up*((yy+np.roll(yy,-1))*cross).sum()/(6*area)
     length=np.linalg.norm(pp-np.roll(pp,1,axis=0),axis=1).sum();lateral=abs((centre-so)@right)
     rec={'part':part,'fraction':fraction,'sourceOriginM':so.tolist(),'areaCentroidM':centre.tolist(),'ringLengthM':float(length),'lateralCentreDistanceM':float(lateral),'nodes':loop['nodes'],'segmentTriangles':loop['segmentTriangles']}
     if length<(.105 if digit==1 else .082) and lateral<(.010 if digit==1 else .0055):selected.append(rec)
     else:rejected.append(rec)
    if selected:observed.append(min(selected,key=lambda q:np.linalg.norm(np.array(q['areaCentroidM'])-so)))
    indicatorAudit.append({'digit':digit,'part':part,'fraction':fraction,'acceptedForAuthoredModelAxis':bool(selected),'rejectedLoops':rejected,'anatomicalSourceBoneApproval':False})
  assert observed,('no own-digit source section',digit)
  for part,c in enumerate(chain[:-1]):
   row=next(x for x in controls if x['id']==c['id']);q=np.array(c['sourceOriginalHelperM']);nearest=min(observed,key=lambda x:np.linalg.norm(np.array(x['sourceOriginM'])-q));offset=np.array(nearest['areaCentroidM'])-nearest['sourceOriginM'];row['source']=(q+offset).tolist()
   row['sourceOriginalHelperM']=q.tolist();row['sourceInnerModelIndicator']={'method':'own-digit closed source skin section area centroid; transverse offset carried to rig station','observedSection':nearest,'offsetM':offset.tolist(),'authoredNotProviderBone':True,'notClinicalLandmark':True}
   row['role']='AI-authored inner toe model axis to actual native bone cap; original rig helper preserved separately'
 (E/f'inner-indicator-audit-{a.revision}.json').write_text(json.dumps({'checks':indicatorAudit,'controls':[x for x in controls if 'sourceInnerModelIndicator' in x],'automaticAnatomicalApproval':False},indent=2)+'\n')

# Source coordinates are directly inspected outer-skin roles, not extrema
# automatically promoted to homologous clinical landmarks. Native addresses are
# containment supports; the thickness allowances below are explicit AI priors.
body=[
 ('heel-posterior',[-.183,-.792,-.061],'Calcaneus',2,-1,.008),
 ('heel-plantar',[-.183,-.818,-.025],'Calcaneus',1,-1,.007),
 ('heel-lateral',[-.214,-.796,-.025],'Calcaneus',0,-1,.007),
 ('heel-medial',[-.155,-.796,-.025],'Calcaneus',0,1,.007),
 ('instep-navicular',[-.171,-.756,.039],'Navicular bone',1,1,.004),
 ('lateral-midfoot',[-.223,-.795,.040],'Cuboid bone',0,-1,.009),
 ('medial-midfoot',[-.150,-.785,.040],'Navicular bone',0,1,.007),
 ('forefoot-plantar',[-.190,-.817,.108],'Superficial transverse metatarsal ligament',1,-1,.003),
]
for name,point,term,axis,sign,pad in body:
 vi=int(ids[np.linalg.norm(s[ids]-point,axis=1).argmin()]);key=next(k for k,x in native.items() if x['side']=='right' and x['name']==term)
 item=native[key];nv=np.array(item['v']);nt=np.array(item['t']);value=nv[:,axis]*sign
 cohort=np.flatnonzero(value>value.max()-.003);centre=nv[cohort].mean(0);ni=int(cohort[np.linalg.norm(nv[cohort]-centre,axis=1).argmin()])
 ti=int(np.flatnonzero((nt==ni).any(1))[0]);corner=int(np.flatnonzero(nt[ti]==ni)[0]);bary=[0.,0.,0.];bary[corner]=1.
 target=nv[ni].copy();target[axis]+=sign*pad
 controls.append(dict(id=name,source=s[vi].tolist(),target=target.tolist(),sourceAddress=address(vi),
                      nativeSourceKey=key,nativeName=term,nativeTriangle=ti,nativeBarycentric=bary,nativeWorldM=nv[nt[ti]].tolist(),
                      role='AI-authored outer skin '+name+' paired to named underlying containment support',
                      skinAllowanceM=pad,clinicalLandmarkApproval=False,sigmaM=.045))

if a.surface_pairs:
 sys.path.insert(0,str(R/'work/tools'))
 from at10_surface_sections import section_loops,ordered_samples
 policy=load(R/'work/evidence/AT10/2026-10-14-completion-r1/reference-exceptions-right-r1.json')
 excepted={x['sourceKey']:set(x['triangleIds']) for x in policy['facets']}
 localfaces=np.flatnonzero(mask[t].all(1));pairs=[];sections=[]
 def ray(origin,direction,vertices,triangles):
  q=vertices[triangles];e1=q[:,1]-q[:,0];e2=q[:,2]-q[:,0];h=np.cross(direction,e2);det=np.einsum('ij,ij->i',e1,h);valid=np.abs(det)>1e-12
  inv=np.divide(1.,det,out=np.zeros_like(det),where=valid);z=origin-q[:,0];u=np.einsum('ij,ij->i',z,h)*inv;cross=np.cross(z,e1);w=cross@direction*inv;distance=np.einsum('ij,ij->i',e2,cross)*inv
  hits=np.flatnonzero(valid&(u>=0)&(w>=0)&(u+w<=1)&(distance>0)&(distance<.16))
  if not len(hits):return None
  i=int(hits[np.argmin(distance[hits])]);return i,[float(1-u[i]-w[i]),float(u[i]),float(w[i])],origin+direction*distance[i]
 def section(label,so,to,saxis,taxis,terms,pad,body=False):
  saxis=np.array(saxis,dtype=float);saxis/=np.linalg.norm(saxis);taxis=np.array(taxis,dtype=float);taxis/=np.linalg.norm(taxis)
  loops,opened=section_loops(s,t,so,saxis,localfaces)
  if not loops:sections.append({'id':label,'status':'no_closed_source_section','open':opened});return
  loop=min(loops,key=lambda z:np.linalg.norm(np.array([q['pointM'] for q in z['nodes']]).mean(0)-so))
  samples=ordered_samples(loop,s,t,so,saxis,[0,1,0],count=8)
  centre=np.array([x['pointM'] for x in loop['nodes']]).mean(0)
  right=np.cross(np.array([0.,1.,0.]),saxis);right/=np.linalg.norm(right)
  if not body and abs((centre-so)@right)>.006:
   sections.append({'id':label,'status':'adjacent_digit_loop_rejected','centreM':centre.tolist(),'originM':np.array(so).tolist()});return
  if samples[0]['ringLengthM']>(.32 if body else .10):sections.append({'id':label,'status':'merged_or_wrong_source_loop','lengthM':samples[0]['ringLengthM']});return
  nv=[];nt=[];addresses=[]
  for key,item in native.items():
   if item['side']!='right' or not any(term in item['name'].lower() for term in terms):continue
   vv=np.array(item['v']);tt=np.array(item['t']);cohort=np.array([i for i in range(len(tt)) if i not in excepted.get(key,set())],int)
   if body:cohort=cohort[(vv[tt[cohort],1].max(1)<.125)]
   offset=len(nv);nv.extend(vv);nt.extend(tt[cohort]+offset);addresses.extend((key,int(i)) for i in cohort)
  nv=np.array(nv);nt=np.array(nt);sup=np.array([0.,1.,0.]);sup-=saxis*(sup@saxis);sup/=np.linalg.norm(sup);sx=np.cross(sup,saxis)
  tup=np.array([0.,1.,0.]);tup-=taxis*(tup@taxis);tup/=np.linalg.norm(tup);tx=np.cross(tup,taxis)
  count=0
  for j,sm in enumerate(samples):
   sp=np.array(sm['pointM']);rad=sp-so;direction=tx*(rad@sx)+tup*(rad@sup);direction/=np.linalg.norm(direction)
   hit=ray(np.array(to)+direction*.08,-direction,nv,nt)
   if hit is None:continue
   ni,bary,hp=hit;key,ti=addresses[ni];r=float((hp-to)@direction)
   if r<0 or r>(.075 if body else .024):continue
   row={'id':label+'-'+str(j),'source':sp.tolist(),'target':(hp+direction*pad).tolist(),'sourceAddress':{
    'logicalTriangle':sm['triangle'],'sourceObjFace':d['faces'][sm['triangle']//2]['sourceFace'],'originalVertices':[d['originalVertexIds'][int(i)] for i in t[sm['triangle']]],'barycentric':sm['barycentric']},
    'nativeSourceKey':key,'nativeTriangle':ti,'nativeBarycentric':bary,'nativePointM':hp.tolist(),'nativeWorldM':np.array(native[key]['v'])[native[key]['t'][ti]].tolist(),
    'role':label+' closed source surface section to named underlying support; authored allowance, not native skin landmark','skinAllowanceM':pad,'sigmaM':.025 if body else .012,'clinicalLandmarkApproval':False}
   pairs.append(row);count+=1
  sections.append({'id':label,'status':'addressed_pair_proposal','pairedSamples':count,'sourceSectionLengthM':samples[0]['ringLengthM'],'sourceOriginM':np.array(so).tolist(),'targetOriginM':np.array(to).tolist(),'dorsalUp':[0,1,0],'homologyApproval':False})
 for z,tz in [(.055,.010),(.085,.038),(.112,.064)]:
  section('midfoot-dorsal-plantar-'+str(z),np.array([-.185,-.79,z]),np.array([-.095,.035,tz]),[0,0,1],[0,0,1],['foot','metatarsal','cuneiform','cuboid','navicular','crural fascia','digitorum','hallucis','fibularis'],.003,True)
 words=['first','second','third','fourth','fifth']
 for digit,word in enumerate(words,1):
  chain=[c for c in f['nativeJointControls'] if c['id'].startswith('joint-r-toe-'+str(digit)+'-')]
  for k,(ca,cb) in enumerate(zip(chain[:-1],chain[1:])):
   sa=np.array(ca.get('sourceOriginalHelperM',ca['source']));sb=np.array(cb.get('sourceOriginalHelperM',cb['source']));ta=np.array(ca['target']);tb=np.array(cb['target'])
   for u in [.35,.72]:
    section('toe-'+str(digit)+'-segment-'+str(k)+'-'+str(u),sa*(1-u)+sb*u,ta*(1-u)+tb*u,sb-sa,tb-ta,[f'phalanx of {word} finger of foot'],.0025)
 controls.extend(pairs)
 (E/f'surface-pair-audit-{a.revision}.json').write_text(json.dumps({'sections':sections,'pairs':pairs,'approvedExceptionCount':991,'sourceSkinHomologyAutoApproved':False,'nativeModified':False},indent=2)+'\n')

if a.recipe:
 recipe=load(R/a.recipe);assert recipe['baseCandidateSha256']==hashlib.sha256((B/'candidates/fit-r41.json').read_bytes()).hexdigest()
 A=np.array(recipe['affine']);b=np.array(recipe['translation']);stages=recipe['stages'];controls=recipe['controls']
else:
 X=np.array([c['source'] for c in controls]);T=np.array([c['target'] for c in controls]);sig=np.array([c['sigmaM'] for c in controls])
 affine=np.linalg.lstsq(np.c_[X,np.ones(len(X))],T,rcond=None)[0];A=affine[:3].T;b=affine[3];assert np.linalg.det(A)>0
 current=X@A.T+b;stages=[]
 if a.continue_recipe:
  prior=load(R/a.continue_recipe);assert prior['controls']==controls
  A=np.array(prior['affine']);b=np.array(prior['translation']);stages=prior['stages'];current=X@A.T+b
  for q in stages:
   delta=current[:,None,:]-np.array(q['centres'])[None,:,:];phi=np.exp(-(delta**2).sum(2)/(2*np.array(q['sigmaM'])[None,:]**2));current+=phi@np.array(q['coefficients'])
 start=len(stages)
 (E/f'control-input-{a.revision}.json').write_text(json.dumps({'controls':controls,'releasedPseudoBoundaryControls':[address(int(i)) for i in interior]},indent=2)+'\n')
 for step in range(start,start+(1400 if a.refine else 500)):
  residual=T-current;error=np.linalg.norm(residual,axis=1).max()
  if error<1e-8:break
  delta=current[:,None,:]-current[None,:,:]
  if a.refine:
   nearest=np.sqrt((delta**2).sum(2)+np.eye(len(current))*100).min(1)
   sig=np.minimum(np.array([c['sigmaM'] for c in controls]),np.maximum(nearest*.85,np.array([c['sigmaM'] for c in controls])/(2**(step//250))))
  K=np.exp(-(delta**2).sum(2)/(2*sig[None,:]**2))
  # Regularize the closely spaced calf seam controls. The old interpolating
  # inverse required enormous cancelling velocities; it was never emitted.
  coeff=np.linalg.solve(K+np.eye(len(K))*.001,residual)
  # sup ||D(exp(-r^2/2sigma^2)*coefficient)|| <= ||coefficient||/(sqrt(e)*sigma)
  bound=float((np.linalg.norm(coeff,axis=1)/(np.sqrt(np.e)*sig)).sum());alpha=min(1.,.30/max(bound,1e-20));coef=coeff*alpha
  stages.append(dict(centres=current.tolist(),sigmaM=sig.tolist(),coefficients=coef.tolist(),globalDisplacementLipschitzBound=alpha*bound))
  current+=K@coef
  if step%50==0:print('FLOW',step,'max target residual',error,'step',alpha,flush=True)
 print('FINAL_CONTROL_RESIDUAL',error,flush=True)
 recipe={'method':'affine + Lipschitz-bounded Gaussian landmark flow','controls':controls,'affine':A.tolist(),'translation':b.tolist(),'stages':stages,
         'baseCandidateSha256':hashlib.sha256((B/'candidates/fit-r41.json').read_bytes()).hexdigest()}

# These are actual source vertices, face interiors, plus interior source-foot
# points. The global bound is independent of this finite diagnostic set.
localtri=t[mask[t].all(1)];query=np.vstack([s[ids],s[localtri].mean(1),np.array([c['source'] for c in controls])])
P=query@A.T+b;J=np.tile(A,(len(P),1,1));minimumStepDet=1.
for k,stage in enumerate(stages):
 C=np.array(stage['centres']);sigma=np.array(stage['sigmaM']);coef=np.array(stage['coefficients'])
 delta=P[:,None,:]-C[None,:,:];phi=np.exp(-(delta**2).sum(2)/(2*sigma[None,:]**2));grad=-phi[:,:,None]*delta/sigma[None,:,None]**2
 D=np.eye(3)+np.einsum('ci,pcj->pij',coef,grad);minimumStepDet=min(minimumStepDet,float(np.linalg.det(D).min()))
 J=D@J;P+=phi@coef
v[ids]=P[:len(ids)]
boundaryError=float(np.linalg.norm(v[roots]-old[roots],axis=1).max())
# Preview emission is independent of acceptance. The exact seam overwrite and
# its residual are exposed; a large residual fails rather than withholding QA.
v[roots]=old[roots]
outside=np.setdiff1d(np.arange(n),ids);assert np.array_equal(v[outside],old[outside])
recipe.update(revision=a.revision,sourceUnitVertices=ids.tolist(),actualTopologicalBoundary=roots.tolist(),releasedPseudoBoundaryControls=interior.tolist(),
              sourceBoundaryAnkleDistancesM=np.linalg.norm(s[roots]-f['nativeJointControls'][0]['source'],axis=1).tolist(),
              boundaryResidualBeforeExactJoinM=boundaryError,minimumAffineDeterminant=float(np.linalg.det(A)),
              minimumComposedSampled3DDeterminant=float(np.linalg.det(J).min()),minimumIncrementSampledDeterminant=minimumStepDet,
              maximumIncrementGlobalLipschitzBound=max(x['globalDisplacementLipschitzBound'] for x in stages),
              continuousFieldInjectivityArgument='proper affine followed by maps I+u, each global ||Du||<1; inverse exists by contraction. Emitted straight facets, source self intersections and joined seam need independent QA.',
              outsideUnitExact=True,helpersUVAndOriginalIdsPreserved=True,nativeModified=False,
              globalEmittedSkinInjectivityProven=False,geometryAcceptance=False,learnerEligible=False)
d.update(positions=v.tolist(),candidateRevision=a.revision,fitAcceptancePassed=False,learnerEligible=False)
dataset=load(R/'atlas-data/source-cache/datasets/za/compiled/manifest.json')
d['referencePoseBinding']={'sourceHash':dataset['sourceHash'],'sourceFrame':0,'canonicalPoseId':dataset['frameContract']['staticReferencePose']['id'],'frameId':dataset['frameContract']['targetFrameId'],'meaning':'same previously hash-verified static native input; no rig/posture or geometry approval'}
d['f1CorrespondenceRecipe']=str((E/f'recipe-{a.revision}.json').relative_to(R))
for path,payload in [(E/f'candidates/fit-{a.revision}.json',d),(E/f'recipe-{a.revision}.json',recipe)]:
 assert not path.exists(),path
 path.write_text(json.dumps(payload,separators=(',',':'))+'\n')
print(json.dumps({k:v for k,v in recipe.items() if k not in ['controls','stages','sourceUnitVertices','sourceBoundaryAnkleDistancesM']}),flush=True)
