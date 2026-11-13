"""Offline, source-addressed local fit; exact contacts drive bounded corrections.

The validator is separate and read-only. Never writes the baseline or native inputs.
Run in verified Blender with --factory-startup --disable-autoexec.
"""
from pathlib import Path
import argparse, sys, json, hashlib, importlib.util
import numpy as np
from mathutils.bvhtree import BVHTree

R = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--evidence', required=True)
parser.add_argument('--revision', default='r12')
parser.add_argument('--iterations', type=int, default=40)
parser.add_argument('--orientation', choices=['surface','anatomical'], default='anatomical')
parser.add_argument('--input')
parser.add_argument('--contact-mode',choices=['support','plane'],default='plane')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
E = R / args.evidence
B = R / 'work/evidence/AT10/2026-10-13-skin-fit-r1'
d = json.loads((R/args.input if args.input else B / 'candidates/fit-r9.json').read_text())
v = np.array(d['positions']); initial = v.copy(); src = np.array(d['sourceVertices'])
base = np.array(json.loads((B / 'candidates/fit-r9-base.json').read_text())['positions'])
ctrl = {c['id']: c for c in json.loads((B / 'native-controls-r2.json').read_text())['controls']}
regions = np.array(d['vertexRegions'])
faces = [f['derivedVertices'] for f in d['faces']]
t = np.array([[f[0], f[j], f[j+1]] for f in faces for j in range(1, len(f)-1)])
edges = np.array(sorted({tuple(sorted((a,b))) for f in faces for a,b in zip(f,f[1:]+f[:1])}))
degree = np.bincount(edges.ravel(), minlength=len(v))
def mean_neighbours(a):
    result = np.zeros_like(a)
    np.add.at(result, edges[:,0], a[edges[:,1]])
    np.add.at(result, edges[:,1], a[edges[:,0]])
    return result / np.maximum(degree, 1)[:,None]
def smoothstep(x):
    x = np.clip(x,0,1); return x*x*(3-2*x)

# Remove the thin *skeletal cage* handoff at the wrist. The existing measured
# forearm envelope and the proper palm bind share a 50 mm source-axis interval.
cohorts = []
for side, letter in [('left','l'),('right','r')]:
    fr = d['articulatedFrames'][side]
    aS = np.array(fr['sourceWrist']); aT = np.array(fr['targetWrist'])
    pS = np.array(fr['sourcePalmFrame']); pT = np.array(fr['targetPalmFrame'])
    scales = np.array(fr['palmScale'])
    progress = (src-aS) @ pS[:,0]
    mask = (regions == 'hand-'+side) & (progress < .03)
    # Reconstruct the original proper palm transform, not the cage blend.
    palm = aT + ((src-aS) @ pS * scales) @ pT.T
    weight = smoothstep((progress+.025)/.05)
    if not args.input:v[mask] = base[mask]*(1-weight[mask,None]) + palm[mask]*weight[mask,None]
    cohorts.append({'id':'wrist-palm-'+side,'sourceVertices':np.array(d['originalVertexIds'])[mask].tolist(),
                    'sourceJoint':ctrl[f'joint-{letter}-hand'], 'sourceAxis':pS[:,0].tolist(),
                    'sourceIntervalM':[-.025,.025], 'method':'measured forearm envelope to proper palm frame C1 blend'})

# Source ear relief has a clear original cohort (ear pinna beyond lateral scalp).
# Match both actual original native ears independently; no mirror-as-validation.
native = json.loads((B/'native-surfaces-r1.json').read_text())
for side, sign in [('left',1),('right',-1)]:
    ear = (src[:,0]*sign > .070) & (src[:,1] > .658) & (src[:,1] < .726) & (src[:,2] < .065)
    # Observed source extrema used for pinna registration; falloff continues into scalp.
    near = (src[:,0]*sign > .061) & (src[:,1] > .64) & (src[:,1] < .745) & (src[:,2] < .075)
    surfaces = {k:s for k,s in native.items() if (s['side']==side or s['name'].endswith('.'+('l' if side=='left' else 'r')))
                and any(w in s['name'].lower() for w in ['helix','lobule','tragus'])}
    cloud = np.concatenate([np.array(s['v']) for s in surfaces.values()])
    # Axis-local pinna scale/translation from actual surface bounds, blended at attachment.
    old = v[ear]; lo=old.min(0); hi=old.max(0); targetlo=cloud.min(0); targethi=cloud.max(0)
    scale = np.clip((targethi-targetlo+np.array([.005,.005,.005]))/(hi-lo), .65, 1.7)
    mapped = (v-(lo+hi)/2)*scale+(targetlo+targethi)/2
    w = smoothstep((src[:,0]*sign-.061)/.010)*smoothstep((src[:,1]-.64)/.018)*smoothstep((.745-src[:,1])/.019)*smoothstep((.075-src[:,2])/.01)
    v[near] = v[near]*(1-w[near,None])+mapped[near]*w[near,None]
    cohorts.append({'id':'pinna-'+side,'sourceVertices':np.array(d['originalVertexIds'])[ear].tolist(),
                    'nativeSources':list(surfaces),'nativeBoundsM':[targetlo.tolist(),targethi.tolist()],
                    'sourceDerivedBoundsBeforeM':[lo.tolist(),hi.tolist()], 'scale':scale.tolist(),
                    'method':'independent pinna observed bounds and continuous scalp attachment; contact QA still required'})

# Preserve and identify inward-return source faces. These are never eligible as
# exterior skin anchors; they stay in the emitted original topology and QA counts.
sn = np.zeros_like(src)
cross = np.cross(src[t[:,1]]-src[t[:,0]],src[t[:,2]]-src[t[:,0]])
for j in range(3): np.add.at(sn,t[:,j],cross)
sn /= np.maximum(np.linalg.norm(sn,axis=1)[:,None],1e-12)
returns = (src[:,1]>.59)&(src[:,1]<.735)&(src[:,2]>.08)&(sn[:,2]<-.15)
return_tri = returns[t].any(1)
cohorts.append({'id':'eyelid-oral-return','sourceVertices':np.array(d['originalVertexIds'])[returns].tolist(),
                'sourceFaces':sorted({d['faces'][int(si//2)]['sourceFace'] for si in np.flatnonzero(return_tri)}),
                'classification':'source inward-facing return candidate; no exterior anchor eligibility',
                'oralNativeContract':'AT4 tongue partial only; gingiva/frenulum/sublingual mucosa absent',
                'excludedFromTotalCrossingCount':False})

nv=[]; nt=[]; source_keys=[]; localids=[]
for k,s in native.items():
    off=len(nv); nv.extend(s['v']); nt.extend([[a+off,b+off,c+off] for a,b,c in s['t']]);source_keys.extend([k]*len(s['t']));localids.extend(range(len(s['t'])))
nv=np.array(nv);nt=np.array(nt);nb=BVHTree.FromPolygons(nv.tolist(),nt.tolist(),all_triangles=True)
spec=importlib.util.spec_from_file_location('intersections',R/'atlas-web/scripts/nativeSurfaceIntersections.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def contacts(p):
    sb=BVHTree.FromPolygons(p.tolist(),t.tolist(),all_triangles=True)
    pairs=np.array(sb.overlap(nb),dtype=np.int32)
    if not len(pairs):return pairs
    st=p[t[pairs[:,0]]];nat=nv[nt[pairs[:,1]]];hit=np.zeros(len(pairs),bool)
    for a,b in [(0,1),(1,2),(2,0)]:
        hit |= m.SurfaceIndex.crosses(st[:,a],st[:,b]-st[:,a],nat)
        hit |= m.SurfaceIndex.crosses(nat[:,a],nat[:,b]-nat[:,a],st)
    return pairs[hit]

# Fixed source-bound directions avoid current folded normals changing the role.
# Triangle normal is an orientation constraint, not anatomy/point semantic evidence.
normal = np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]])
normal /= np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-12)
if args.orientation=='anatomical':
    def centre(p, sourcep, pairs):
        options=[]
        for aa,bb in pairs:
            sa=np.array(ctrl[aa]['source']);sb=np.array(ctrl[bb]['source'])
            u=np.clip(np.dot(sourcep-sa,sb-sa)/np.dot(sb-sa,sb-sa),0,1)
            options.append((np.linalg.norm(sourcep-(sa+u*(sb-sa))),aa,bb))
        _,aa,bb=min(options);a=np.array(ctrl[aa]['target']);b=np.array(ctrl[bb]['target'])
        u=np.clip(np.dot(p-a,b-a)/np.dot(b-a,b-a),0,1)
        return a+u*(b-a)
    vd=[]
    for i,p in enumerate(v):
        side='left' if src[i,0]>0 else 'right';letter='l' if side=='left' else 'r';region=regions[i]
        if region.startswith('hand'):
            fr=d['articulatedFrames'][side];aS=np.array(fr['sourceWrist']);pS=np.array(fr['sourcePalmFrame'])
            progress=np.dot(src[i]-aS,pS[:,0])
            if progress<.045:
                a=np.array(fr['targetWrist']);b=np.mean([ctrl[f'joint-{letter}-finger-{di}-1']['target'] for di in range(2,6)],axis=0)
                axis=b-a;u=np.clip(np.dot(p-a,axis)/np.dot(axis,axis),0,1);c=a+u*axis
            else:
                pairs=[(f'joint-{letter}-finger-{di}-{pa}',f'joint-{letter}-finger-{di}-{pa+1}') for di in range(1,6) for pa in range(1,4)]
                c=centre(p,src[i],pairs)
        elif region.startswith('arm'):
            c=centre(p,src[i],[(f'joint-{letter}-shoulder',f'joint-{letter}-elbow'),(f'joint-{letter}-elbow',f'joint-{letter}-hand')])
        elif region.startswith('foot'):
            # Hind-/mid-foot axis and independent toe chains preserve sole separation.
            if src[i,2]>.13:
                c=centre(p,src[i],[(f'joint-{letter}-toe-{di}-{pa}',f'joint-{letter}-toe-{di}-{pa+1}') for di in range(1,6) for pa in range(1,3)])
            else:c=np.array([.0795 if side=='left' else -.0795,.035,p[2]])
        elif region.startswith('leg') or (src[i,1]<.10 and abs(src[i,0])>.035):
            c=centre(p,src[i],[(f'joint-{letter}-upper-leg',f'joint-{letter}-knee'),(f'joint-{letter}-knee',f'joint-{letter}-ankle')])
        else:c=np.array([0,p[1],-.012])
        direction=p-c;direction/=max(np.linalg.norm(direction),1e-8);vd.append(direction)
    vd=np.array(vd);normal=vd[t].mean(1);normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-12)
iterations=[]; constraints=[]; baseline=v.copy()
for iteration in range(args.iterations):
    actual=contacts(v); ids=np.unique(actual[:,0]) if len(actual) else []
    outer=actual[~return_tri[actual[:,0]]] if len(actual) else actual
    entry={'iteration':iteration,'totalCrossingSkinTriangles':len(ids),'outerCrossingSkinTriangles':len(np.unique(outer[:,0])) if len(outer) else 0,'crossingPairs':len(actual)}
    print(entry,flush=True);iterations.append(entry)
    if not len(outer):break
    # Separate each intersecting skin/native pair by an outward tangent support plane.
    # Full native triangle projection, not an arbitrary nearest-point snap.
    step=np.zeros((len(v),3)); count=np.zeros(len(v))
    si=outer[:,0]; ni=outer[:,1]; dirs=normal[si]
    sk=v[t[si]]; na=nv[nt[ni]]
    if args.contact_mode=='plane':
        # Native facets can be very long fascia strips. Projecting their *entire*
        # extent onto a skin tangent plane over-constrains a local contact. Use
        # the intersected facet's plane and its actual local skin vertices.
        n=np.cross(na[:,1]-na[:,0],na[:,2]-na[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-12)
        n*=np.where((n*dirs).sum(1)<0,-1,1)[:,None]
        signed=((sk-na[:,0,None,:])*n[:,None,:]).sum(2)
        needed=np.clip(-signed.min(1)+.0015,0,.004)
        delta=n*needed[:,None]
        for j in range(3):
            np.add.at(step,t[si,j],delta);np.add.at(count,t[si,j],1)
    else:
        needed=(na*dirs[:,None,:]).sum(2).max(1)-(sk*dirs[:,None,:]).sum(2).min(1)+.0015
        needed=np.clip(needed,0,.006)
        required=np.zeros(len(t));np.maximum.at(required,si,needed)
        active=np.flatnonzero(required>0)
        for j in range(3):
            np.add.at(step,t[active,j],normal[active]*required[active,None]);np.add.at(count,t[active,j],1)
    step /= np.maximum(count,1)[:,None]
    # Local field extension, rather than independent per-vertex spikes. Only the
    # displacement is smoothed; original skin detail and all original IDs remain.
    for _ in range(3):step=.75*step+.25*mean_neighbours(step)
    step[returns]=0
    v += step
    if args.orientation=='anatomical':v[:,1]=np.maximum(v[:,1],.001)
    if iteration==0:
        for skin_id,native_id in outer[::max(1,len(outer)//180)]:
            constraints.append({'sourceObjFace':d['faces'][int(skin_id//2)]['sourceFace'],
                                'sourceVertexIds':[d['originalVertexIds'][i] for i in t[skin_id]],
                                'nativeSourceKey':source_keys[native_id],'nativeTriangle':localids[native_id],
                                'nativeWorldM':nv[nt[native_id]].tolist(), 'direction':normal[skin_id].tolist()})
    if np.linalg.norm(v-baseline,axis=1).max()>.065:
        entry['stopReason']='local displacement exceeds 65 mm; candidate must be reviewed, not accepted';break
d['positions']=v.tolist();d['candidateRevision']=args.revision;d['fitAcceptancePassed']=False;d['learnerEligible']=False
d['localFitRecipe']={'baseline':args.input or 'r9','wristsAndPinna':cohorts,'contactClearanceM':.0015,'maxStepM':.006,
                     'method':'source-oriented exact triangle contact support constraints with displacement extension',
                     'orientation':args.orientation,'contactMode':args.contact_mode,'iterations':len(iterations),'sourceHelpersPreserved':True,'nativeModified':False}
d['sourceReturnVertices']=np.flatnonzero(returns).tolist()
(E/f'candidates/fit-{args.revision}.json').write_text(json.dumps(d,separators=(',',':')))
(E/f'local-correspondence-{args.revision}.json').write_text(json.dumps({'cohorts':cohorts,'actualContactAddresses':constraints,'semanticAcupointAuthoring':False},indent=2)+'\n')
(E/f'local-fit-log-{args.revision}.json').write_text(json.dumps({'iterations':iterations,'maximumChangeFromR9M':float(np.linalg.norm(v-initial,axis=1).max()),'candidateAcceptance':False},indent=2)+'\n')
print('LOCAL_FIT_WRITTEN',args.revision,flush=True)
