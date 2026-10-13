"""Regional measured adult shape recipe after articulated native cage; no pointwise shrinkwrap."""
from pathlib import Path
import os,json,numpy as np
R=Path(__file__).resolve().parents[2];E=Path(os.environ.get('AT10_SKIN_EVIDENCE',str(R/'work/evidence/AT10/2026-10-13-skin-fit-r1')))
d=json.loads((E/'candidates/cage-r2.json').read_text());src=np.array(d['sourceVertices']);v=np.array(d['positions']);original=v.copy()
native=json.loads((E/'native-surfaces-r1.json').read_text());controls=json.loads((E/'native-controls-r2.json').read_text())['controls'];ctrl={c['id']:c for c in controls}
regions=[]
for p in src:
    side='left' if p[0]>0 else 'right';letter='l' if p[0]>0 else 'r'
    wrist=np.array(ctrl[f'joint-{letter}-hand']['source']);mc=np.mean([ctrl[f'joint-{letter}-finger-{digit}-1']['source'] for digit in range(2,6)],axis=0);handAxis=(mc-wrist)/np.linalg.norm(mc-wrist)
    if p[1]>.58:region='head'
    elif abs(p[0])>.35 and np.dot(p-wrist,handAxis)>-.02:region='hand-'+side
    elif abs(p[0])>.17 and p[1]>-.08:region='arm-'+side
    elif p[1]<-.745:region='foot-'+side
    elif p[1]<.03 and abs(p[0])>.045:region='leg-'+side
    else:region='groin' if p[1]<.06 else 'trunk'
    regions.append(region)
regions=np.array(regions);recipes=[]
# Native profile extrema are dimensional fit evidence, not acupuncture landmarks.
def smooth(values):
    a=np.array(values)
    for _ in range(3):a[1:-1]=.25*a[:-2]+.5*a[1:-1]+.25*a[2:]
    return a
# Convex cross-section support envelopes preserve the articulated source angular
# correspondence; unlike a nearest projection they do not copy individual muscle triangles.
angles=np.linspace(0,2*np.pi,48,endpoint=False);directions=np.c_[np.cos(angles),np.sin(angles)]
def fit_section(ids,cloud,a0,b0,allowance,label):
    axis=(b0-a0)/np.linalg.norm(b0-a0);uaxis=np.array([1.,0,0]);uaxis-=axis*np.dot(axis,uaxis);uaxis/=np.linalg.norm(uaxis);vaxis=np.cross(axis,uaxis)
    if vaxis[2]<0:vaxis=-vaxis
    length=np.linalg.norm(b0-a0);q=cloud-a0;pc=q@axis/length;px=q@uaxis;pz=q@vaxis
    base=original[ids]-a0;sc=base@axis/length;sx=base@uaxis;sz=base@vaxis
    knots=np.linspace(min(-.05,sc.min()),max(1.05,sc.max()),35);supports=[]
    for f in knots:
        ns=np.abs(pc-f)<.035
        if ns.sum()<10:ns=np.argsort(np.abs(pc-f))[:30]
        xy=np.c_[px[ns],pz[ns]];supports.append(np.max(xy@directions.T,axis=0)+allowance)
    h=np.array(supports)
    # upper neighbouring envelope rather than smoothing across a bulge inward
    h[1:-1]=np.maximum(np.maximum(h[:-2],h[1:-1]),h[2:])
    for j,i in enumerate(ids):
        xy=np.array([sx[j],sz[j]]);radius=np.linalg.norm(xy)
        if radius<1e-5:continue
        dr=xy/radius;cos=directions@dr;hs=np.array([np.interp(sc[j],knots,h[:,k]) for k in range(len(angles))]);required=np.min(hs[cos>.01]/cos[cos>.01])
        # Skin source relief is preserved outside the conservative hull.
        target=max(required,radius);v[i]=original[i]+(uaxis*dr[0]+vaxis*dr[1])*(target-radius)
    recipes.append({'region':label,'axisStart':a0.tolist(),'axisEnd':b0.tolist(),'knots':knots.tolist(),'supportPlanes':h.tolist(),'allowanceM':allowance,'method':'bone-local sampled convex support cage; source angular/topology correspondence retained'})
# Body profiles exclude other arms; major fixed torso/pelvis envelope only.
body=(regions=='trunk')|(regions=='groin');cloud=np.concatenate([np.array(s['v']) for s in native.values() if not any(x in s['name'].lower() for x in ['auricular','helix','lobule','tragus'])]);cloud=cloud[(np.abs(cloud[:,0])<.18)&(cloud[:,1]>.70)&(cloud[:,1]<1.50)]
fit_section(np.flatnonzero(body),cloud,np.array([0.,.7,-.012]),np.array([0.,1.50,-.012]),.009,'body')
for side,letter in [('left','l'),('right','r')]:
    for kind,chain in [('arm',['shoulder','elbow','hand']),('leg',['upper-leg','knee','ankle'])]:
        candidates=[(f'joint-{letter}-{a}',f'joint-{letter}-{b}') for a,b in zip(chain,chain[1:])]
        ids=np.flatnonzero(regions==kind+'-'+side);labels=[]
        for i in ids:
            opts=[]
            for k,(a,b) in enumerate(candidates):
                aa=np.array(ctrl[a]['source']);bb=np.array(ctrl[b]['source']);u=np.clip(np.dot(src[i]-aa,bb-aa)/np.dot(bb-aa,bb-aa),0,1);opts.append((np.linalg.norm(src[i]-(aa+u*(bb-aa))),k))
            labels.append(min(opts)[1])
        labels=np.array(labels)
        for k,(a,b) in enumerate(candidates):
            if kind=='arm':terms=['humerus','deltoid','triceps','biceps brachii','brachialis','coracobrachialis','brachial fascia'] if k==0 else ['radius','ulna','extensor','flexor','pronator','supinator','brachioradialis','antebrachial fascia']
            else:terms=['femur','vastus','rectus femoris','biceps femoris','semitendinosus','semimembranosus','adductor','sartorius','gracilis','iliotibial','fascia lata'] if k==0 else ['tibia','fibula','soleus','gastrocnemius','tibialis','fibularis','extensor digitorum longus','flexor digitorum longus','hallucis','crural fascia']
            picked={key:s for key,s in native.items() if s['side']==side and any(term in s['name'].lower() for term in terms)}
            cloud=np.concatenate([np.array(s['v']) for s in picked.values()]);a0=np.array(ctrl[a]['target']);b0=np.array(ctrl[b]['target']);axis=(b0-a0)/np.linalg.norm(b0-a0);q=cloud-a0;f=q@axis/np.linalg.norm(b0-a0);rad=np.linalg.norm(q-np.outer(q@axis,axis),axis=1)
            cloud=cloud[(f>-.08)&(f<1.08)&(rad<(.12 if kind=='leg' else .10))]
            these=ids[labels==k]
            if len(these):fit_section(these,cloud,a0,b0,.007,kind+'-'+side+'-'+str(k));recipes[-1]['nativeSurfaceIds']=list(picked)
    # Hand and foot require their own short chains, not a forearm or calf cylinder.
    for kind in ['hand','foot']:
        these=np.flatnonzero(regions==kind+'-'+side);segments=[]
        for digit in range(1,6):
            prefix=f'joint-{letter}-'+('finger' if kind=='hand' else 'toe')+f'-{digit}-'
            for part in range(1,4 if kind=='hand' else 3):
                if prefix+str(part) in ctrl and prefix+str(part+1) in ctrl:segments.append((prefix+str(part),prefix+str(part+1),digit,part))
        groups={}
        for i in these:
            opts=[]
            for a,b,digit,part in segments:
                aa=np.array(ctrl[a]['source']);bb=np.array(ctrl[b]['source']);u=np.dot(src[i]-aa,bb-aa)/np.dot(bb-aa,bb-aa);dist=np.linalg.norm(src[i]-(aa+np.clip(u,0,1)*(bb-aa)));opts.append((dist,a,b,digit,part,u))
            x=min(opts);_,a,b,digit,part,f=x
            palm=(kind=='hand' and f<.10 and part==1 and digit!=1) or (kind=='foot' and src[i,2]<.13)
            label='base' if palm else (a,b,digit,part)
            groups.setdefault(label,[]).append(i)
        for label,inds in groups.items():
            if label=='base':
                if kind=='hand':
                    a0=np.array(ctrl[f'joint-{letter}-hand']['target']);b0=np.mean([ctrl[f'joint-{letter}-finger-{x}-1']['target'] for x in range(2,6)],axis=0)
                    picked={key:s for key,s in native.items() if s['side']==side and any(z in s['name'].lower() for z in ['metacarpal','palmar','dorsal fascia of hand','lumbrical muscles of hand','tendon sheath'])};cloud=np.concatenate([np.array(s['v']) for s in picked.values()]);cloud=cloud[(cloud[:,1]>.775)&(cloud[:,1]<.869)]
                else:
                    a0=np.array([.085 if side=='left' else -.085,.035,-.083]);b0=np.array([a0[0],.025,.075]);picked={key:s for key,s in native.items() if s['side']==side and any(z in s['name'].lower() for z in ['calcaneus','talus','metatarsal','cuneiform','cuboid','navicular','plantar','dorsal fascia of foot','calcaneal tendon'])};cloud=np.concatenate([np.array(s['v']) for s in picked.values()]);cloud=cloud[(cloud[:,1]<.095)&(cloud[:,2]<.09)]
            else:
                a,b,digit,part=label;a0=np.array(ctrl[a]['target']);b0=np.array(ctrl[b]['target']);word=['first','second','third','fourth','fifth'][digit-1]
                picked={key:s for key,s in native.items() if s['side']==side and (f'phalanx of {word} finger of '+('hand' if kind=='hand' else 'foot') in s['name'].lower() or (digit==1 and kind=='hand' and s['name'].lower()=='first metacarpal bone'))};cloud=np.concatenate([np.array(s['v']) for s in picked.values()])
            fit_section(np.array(inds),cloud,a0,b0,.0035,kind+'-'+side+'-'+str(label));recipes[-1]['nativeSurfaceIds']=list(picked)
# Head source relief remains; the cranial envelope fit is applied to outer surfaces
# and leaves the mouth/eyelid return surfaces available for the separate mucosa contract.
head=np.flatnonzero(regions=='head');cloud=np.concatenate([np.array(s['v']) for s in native.values()]);cloud=cloud[cloud[:,1]>1.465]
fit_section(head,cloud,np.array([0.,1.48,-.012]),np.array([0.,1.72,-.012]),.0045,'head')
# Smooth local changes over original topology; this is a cage displacement, not
# a smoothing of source skin details. Limbs/trunk transitions retain correspondence.
adj=[set() for _ in v]
for f in d['faces']:
    vs=f['derivedVertices']
    for a,b in zip(vs,vs[1:]+vs[:1]):adj[a].add(b);adj[b].add(a)
delta=v-original
for _ in range(4):delta=.65*delta+.35*np.array([delta[list(ns)].mean(0) if ns else delta[i] for i,ns in enumerate(adj)])
v=original+delta
out=dict(d,positions=v.tolist(),vertexRegions=regions.tolist(),regionalShapeRecipe=recipes)
(E/'candidates/fit-r9-base.json').write_text(json.dumps(out,separators=(',',':')))
print('profile fit',v.min(0),v.max(0),np.linalg.norm(delta,axis=1).max())
