"""Measured source/native patch correspondence and continuous radial cage.

Scoped anatomical clouds, not a whole-body nearest shrinkwrap. Exact validation
remains separate. All dimensional controls retain source/native triangle addresses.
"""
from pathlib import Path
import argparse,json,numpy as np
R=Path(__file__).resolve().parents[2];p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--revision',default='r16');p.add_argument('--smoothing',type=int,default=20);p.add_argument('--clearance-multiplier',type=float,default=1.0);a=p.parse_args();E=R/a.evidence;B=R/'work/evidence/AT10/2026-10-13-skin-fit-r1'
d=json.loads((E/'candidates/fit-r14-base.json').read_text());v=np.array(d['positions']);src=np.array(d['sourceVertices']);original=v.copy();regs=np.array(d['vertexRegions']);ctrl={x['id']:x for x in json.loads((B/'native-controls-r2.json').read_text())['controls']};native=json.loads((B/'native-surfaces-r1.json').read_text());recipes=[]
angles=np.linspace(0,2*np.pi,80,endpoint=False);drs=np.c_[np.cos(angles),np.sin(angles)]
def smoothstep(x):x=np.clip(x,0,1);return x*x*(3-2*x)
def cloudpick(side,terms):
 return {k:s for k,s in native.items() if (side is None or s['side']==side) and any(term in s['name'].lower() for term in terms)}
def cage(ids,picked,a0,b0,gap,label,filter_radius=None,source_axis=None,source_width=None,target_width=None):
 gap*=a.clearance_multiplier
 axis=(b0-a0)/np.linalg.norm(b0-a0);x=np.array([1.,0,0]) if target_width is None else target_width.copy();x-=axis*np.dot(axis,x);x/=np.linalg.norm(x);z=np.cross(axis,x);length=np.linalg.norm(b0-a0)
 vs=[];addresses=[];facets=[];facet_addresses=[]
 for key,s in picked.items():
  vertices=np.array(s['v']);vs.extend(vertices);addresses.extend([(key,i) for i in range(len(vertices))]);facets.extend(vertices[np.array(s['t'])]);facet_addresses.extend([(key,i) for i in range(len(s['t']))])
 q=np.array(vs)-a0;pc=q@axis;px=q@x;pz=q@z;rad=np.hypot(px,pz)
 allowed=(pc>-.020)&(pc<length+.025)
 if filter_radius is not None:allowed&=rad<filter_radius
 pc=pc[allowed];xy=np.c_[px[allowed],pz[allowed]];ad=[addresses[i] for i in np.flatnonzero(allowed)]
 facets=np.array(facets)-a0;fp=facets@axis;fxy=np.stack([facets@x,facets@z],axis=2);fl=fp.min(1);fh=fp.max(1)
 q=v[ids]-a0;sp=q@axis;sxy=np.c_[q@x,q@z]
 if source_axis is not None:
  sa,sb=source_axis;saxis=(sb-sa)/np.linalg.norm(sb-sa);sx=np.array([1.,0,0]) if source_width is None else source_width.copy();sx-=saxis*np.dot(saxis,sx);sx/=np.linalg.norm(sx);sz=np.cross(saxis,sx);sq=src[ids]-sa;sp=sq@saxis*length/np.linalg.norm(sb-sa);sxy=np.c_[sq@sx,sq@sz]
 knots=np.linspace(min(-.01,sp.min()),max(length+.01,sp.max()),60);h=[];samples=[]
 for k in knots:
  # Exact native facet/section intersections; vertex-only slices miss long
  # fascia strips between their endpoints and cannot establish an envelope.
  fids=np.flatnonzero((fl<k+.007)&(fh>k-.007));points=[];refs=[]
  for plane in [k-.007,k,k+.007]:
   for aa,bb in [(0,1),(1,2),(2,0)]:
    p0=fp[fids,aa];p1=fp[fids,bb];u=np.divide(plane-p0,p1-p0,out=np.full_like(p0,-1),where=np.abs(p1-p0)>1e-10);valid=(u>=0)&(u<=1);inter=fxy[fids[valid],aa]+u[valid,None]*(fxy[fids[valid],bb]-fxy[fids[valid],aa]);rad=np.linalg.norm(inter,axis=1);accept=np.ones(len(inter),bool) if filter_radius is None else rad<filter_radius
    points.extend(inter[accept]);refs.extend([facet_addresses[int(fi)] for fi in fids[valid][accept]])
  if len(points)<4:
   near=np.argsort(np.abs(pc-k))[:30];points=xy[near].tolist();refs=[(key,int(np.flatnonzero((np.array(native[key]['t'])==vi).any(1))[0])) for key,vi in [ad[i] for i in near]]
  points=np.array(points);values=points@drs.T;extreme=values.argmax(0);support=values.max(0)+gap
  h.append(support);samples.append([refs[int(j)] for j in extreme])
 h=np.array(h);h[1:-1]=np.maximum(h[1:-1],np.maximum(h[:-2],h[2:]))
 result=v[ids].copy()
 for j,i in enumerate(ids):
  r=np.linalg.norm(sxy[j]);direction=sxy[j]/max(r,1e-9);cos=drs@direction
  hs=np.array([np.interp(sp[j],knots,h[:,k]) for k in range(len(angles))]);need=np.min(hs[cos>.02]/cos[cos>.02])
  if source_axis is not None:result[j]=a0+axis*sp[j]+(x*direction[0]+z*direction[1])*max(need,r*(.45 if label.startswith(('ankle-foot','toe-')) else 1.12))
  elif need>r:result[j]+=(x*direction[0]+z*direction[1])*(need-r)
 # Native vertex extrema map to incident triangles, hence inspectable actual facets.
 extrema=[]
 for ids80 in samples[::8]:
  for key,ti in ids80[::10]:
   tri=np.array(native[key]['t']);extrema.append({'sourceKey':key,'nativeTriangle':ti,'nativeWorldM':np.array(native[key]['v'])[tri[ti]].tolist()})
 recipes.append({'id':label,'sourceVertexIds':np.array(d['originalVertexIds'])[ids].tolist(),'axisM':[a0.tolist(),b0.tolist()],'sourceAxisM':[x.tolist() for x in source_axis] if source_axis is not None else None,'nativeSources':list(picked),'clearanceM':gap,'knotsM':knots.tolist(),'supportPlanes':h.tolist(),'nativeFacetExtrema':extrema})
 return result

for side,letter,sign in [('left','l',1),('right','r',-1)]:
 # Distal forearm and wrist share one measured cylinder: no thin skeletal cage.
 ids=np.flatnonzero((src[:,0]*sign>.37)&(src[:,0]*sign<.48)&(src[:,1]>.12))
 picked=cloudpick(side,['radius','ulna','carpal','flexor','extensor','antebrachial fascia','brachioradialis','pronator','supinator'])
 aa=np.array(ctrl[f'joint-{letter}-elbow']['target']);bb=np.array(ctrl[f'joint-{letter}-hand']['target']);out=cage(ids,picked,aa,bb,.006,'forearm-wrist-'+side,.075)
 # Stop at a source wrist plane; palm field takes over continuously.
 fr=d['articulatedFrames'][side];sp=np.array(fr['sourcePalmFrame']);sw=np.array(fr['sourceWrist']);pr=(src[ids]-sw)@sp[:,0];w=1-smoothstep((pr+.020)/.04);v[ids]=v[ids]*(1-w[:,None])+out*w[:,None]
 ids=np.flatnonzero(regs=='hand-'+side)
 joints=[(f'joint-{letter}-finger-{di}-{pa}',f'joint-{letter}-finger-{di}-{pa+1}',di,pa) for di in range(1,6) for pa in range(1,4)]
 groups={}
 for i in ids:
  options=[]
  for aa,bb,di,pa in joints:
   s0=np.array(ctrl[aa]['source']);s1=np.array(ctrl[bb]['source']);u=np.dot(src[i]-s0,s1-s0)/np.dot(s1-s0,s1-s0);distance=np.linalg.norm(src[i]-(s0+np.clip(u,0,1)*(s1-s0)));options.append((distance,aa,bb,di,pa,u))
  dist,aa,bb,di,pa,u=min(options)
  palm=(pa==1 and u<.18 and di!=1) or (np.dot(src[i]-sw,sp[:,0])<.015)
  groups.setdefault('palm' if palm else (aa,bb,di,pa),[]).append(i)
 for label,values in groups.items():
  values=np.array(values)
  if label=='palm':
   aa=np.array(fr['targetWrist']);bb=np.mean([ctrl[f'joint-{letter}-finger-{di}-1']['target'] for di in range(2,6)],axis=0)
   picked=cloudpick(side,['metacarpal','palmar','dorsal fascia of hand','lumbrical muscles of hand','tendon sheath'])
   sa=np.array(fr['sourceWrist']);sb=np.mean([ctrl[f'joint-{letter}-finger-{di}-1']['source'] for di in range(2,6)],axis=0)
   out=cage(values,picked,aa,bb,.004,'palm-'+side,.08,(sa,sb),sp[:,1],np.array(fr['targetPalmFrame'])[:,1])
  else:
   akey,bkey,di,pa=label;aa=np.array(ctrl[akey]['target']);bb=np.array(ctrl[bkey]['target']);word=['first','second','third','fourth','fifth'][di-1]
   picked=cloudpick(side,[f'phalanx of {word} finger of hand','dorsal fascia of hand','lumbrical muscles of hand','tendon sheath'])
   out=cage(values,picked,aa,bb,.003,'finger-'+side+'-'+str(di)+'-'+str(pa),.015,(np.array(ctrl[akey]['source']),np.array(ctrl[bkey]['source'])),sp[:,1],np.array(fr['targetPalmFrame'])[:,1])
  v[values]=out
 # Foot body uses its long axis; toes use independent native phalanx controls.
 ids=np.flatnonzero((src[:,0]*sign>.08)&(src[:,1]<-.705));groups={}
 for i in ids:
  if src[i,2]<.129:label='foot-body'
  else:
   options=[]
   for di in range(1,6):
    for pa in range(1,3):
     aa=f'joint-{letter}-toe-{di}-{pa}';bb=f'joint-{letter}-toe-{di}-{pa+1}';s0=np.array(ctrl[aa]['source']);s1=np.array(ctrl[bb]['source']);u=np.clip(np.dot(src[i]-s0,s1-s0)/np.dot(s1-s0,s1-s0),0,1);options.append((np.linalg.norm(src[i]-(s0+u*(s1-s0))),aa,bb,di,pa))
   _,aa,bb,di,pa=min(options);label=(aa,bb,di,pa)
  groups.setdefault(label,[]).append(i)
 for label,values in groups.items():
  values=np.array(values)
  if label=='foot-body':
   aa=np.array([sign*.0795,.037,-.060]);bb=np.array([sign*.085,.035,.09]);picked=cloudpick(side,['tibia','fibula','talus','calcaneus','metatarsal','cuneiform','cuboid','navicular','plantar','foot','calcaneal','tendon sheath','retinaculum','tibialis','fibularis'])
   out=cage(values,picked,aa,bb,.004,'ankle-foot-'+side,.10,(np.array([sign*.18,-.785,-.030]),np.array([sign*.17,-.790,.136])))
  else:
   akey,bkey,di,pa=label;aa=np.array(ctrl[akey]['target']);bb=np.array(ctrl[bkey]['target']);word=['first','second','third','fourth','fifth'][di-1];picked=cloudpick(side,[f'phalanx of {word} finger of foot','tendon of extensor digitorum longus','tendon sheath of extensor hallucis','lumbrical muscles of foot'])
   out=cage(values,picked,aa,bb,.003,'toe-'+side+'-'+str(di)+'-'+str(pa),.017,(np.array(ctrl[akey]['source']),np.array(ctrl[bkey]['source'])))
  v[values]=out

# Upper medial thigh was previously assigned to the central body solely because
# abs(source X)<45 mm. Its source leg axis is the correct semantic correspondence.
for side,letter,sign in [('left','l',1),('right','r',-1)]:
 ids=np.flatnonzero((src[:,0]*sign>0)&(np.abs(src[:,0])<.20)&(src[:,1]<.015)&(src[:,1]>-.35))
 aa=np.array(ctrl[f'joint-{letter}-upper-leg']['target']);bb=np.array(ctrl[f'joint-{letter}-knee']['target']);sa=np.array(ctrl[f'joint-{letter}-upper-leg']['source']);sb=np.array(ctrl[f'joint-{letter}-knee']['source'])
 picked=cloudpick(side,['femur','vastus','rectus femoris','biceps femoris','semitendinosus','semimembranosus','adductor','sartorius','gracilis','iliotibial','fascia lata','pectineus','gluteus'])
 out=cage(ids,picked,aa,bb,.006,'pelvis-medial-thigh-'+side,.14,(sa,sb))
 w=smoothstep((.015-src[ids,1])/.075)*smoothstep((src[ids,1]+.35)/.060)
 v[ids]=v[ids]*(1-w[:,None])+out*w[:,None]
 regs[ids[src[ids,1]<-.05]]='leg-'+side

# Head/neck external cohort keeps source relief. Source inward oral/eyelid
# returns are separately addressed, retained, and not silently counted as fitted.
tri=np.array([[f['derivedVertices'][0],f['derivedVertices'][j],f['derivedVertices'][j+1]] for f in d['faces'] for j in range(1,3)]);sn=np.zeros_like(src);nn=np.cross(src[tri[:,1]]-src[tri[:,0]],src[tri[:,2]]-src[tri[:,0]])
for j in range(3):np.add.at(sn,tri[:,j],nn)
sn/=np.maximum(np.linalg.norm(sn,axis=1)[:,None],1e-12)
returns=(src[:,1]>.59)&(src[:,1]<.735)&(src[:,2]>.08)&(sn[:,2]<-.15)
ears=(np.abs(src[:,0])>.072)&(src[:,1]>.653)&(src[:,1]<.733)&(src[:,2]<.066)
ids=np.flatnonzero((src[:,1]>.565)&(~returns)&(~ears))
picked={k:s for k,s in native.items() if np.array(s['v'])[:,1].max()>1.48 and not any(x in s['name'].lower() for x in ['helix','lobule','tragus','auricular region'])}
out=cage(ids,picked,np.array([0,1.475,-.012]),np.array([0,1.715,-.012]),.004,'outer-head-neck',.16)
w=smoothstep((src[ids,1]-.565)/.025);v[ids]=v[ids]*(1-w[:,None])+out*w[:,None]
for side,sign in [('left',1),('right',-1)]:
 mask=ears&(src[:,0]*sign>0);ids=np.flatnonzero(mask);picked={k:s for k,s in native.items() if s['name'].endswith('.'+('l' if side=='left' else 'r')) and any(x in s['name'].lower() for x in ['helix','lobule','tragus'])};cloud=np.concatenate([s['v'] for s in picked.values()]);lo=v[ids].min(0);hi=v[ids].max(0);nl=cloud.min(0);nh=cloud.max(0);scale=np.clip((nh-nl+[.004,.004,.004])/(hi-lo),.65,1.7)
 v[ids]=(v[ids]-(lo+hi)/2)*scale+(nl+nh)/2
 recipes.append({'id':'source-pinna-'+side,'sourceVertexIds':np.array(d['originalVertexIds'])[ids].tolist(),'nativeSources':list(picked),'sourceDerivedBoundsBeforeM':[lo.tolist(),hi.tolist()],'nativeBoundsM':[nl.tolist(),nh.tolist()],'localScale':scale.tolist(),'skinAllowanceM':.002})

# Continuous displacement field removes source-cohort boundary steps while
# keeping the original mesh/UV and the authored adult detail intact.
edges=np.array(sorted({tuple(sorted((aa,bb))) for f in d['faces'] for aa,bb in zip(f['derivedVertices'],f['derivedVertices'][1:]+f['derivedVertices'][:1])}));degree=np.bincount(edges.ravel(),minlength=len(v));delta=v-original
for _ in range(a.smoothing):
 neighbours=np.zeros_like(delta);np.add.at(neighbours,edges[:,0],delta[edges[:,1]]);np.add.at(neighbours,edges[:,1],delta[edges[:,0]]);delta=.7*delta+.3*neighbours/degree[:,None]
v=original+delta
d['positions']=v.tolist();d['vertexRegions']=regs.tolist();d['sourceReturnVertices']=np.flatnonzero(returns).tolist();d['candidateRevision']=a.revision;d['patchEnvelopeRecipe']=recipes;d['fitAcceptancePassed']=False;d['learnerEligible']=False
(E/f'candidates/fit-{a.revision}.json').write_text(json.dumps(d,separators=(',',':')))
(E/f'envelope-recipe-{a.revision}.json').write_text(json.dumps({'patches':recipes,'displacementSmoothingIterations':a.smoothing,'maxDisplacementM':float(np.linalg.norm(delta,axis=1).max()),'semanticPointEvidence':False},separators=(',',':')))
print('PATCH_ENVELOPE',a.revision,'max',np.linalg.norm(delta,axis=1).max())
