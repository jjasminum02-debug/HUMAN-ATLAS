"""Adult core head/neck recipe and source-addressed, corrected cage roles.

The young preview target is not silently treated as a production head recipe.
Base OBJ/helper/UV are immutable. The derived recipe drops that target on the
head, tapers at the collar, and preserves the successful extremity positions.
"""
from pathlib import Path
import json, hashlib, sys, argparse
import numpy as np
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'work/tools'))
from at10_skin_field_math import cubic_operator
E=R/'work/evidence/AT10/2026-10-14-skin-fit-r5'
p=argparse.ArgumentParser();p.add_argument('--revision',required=True);p.add_argument('--omit-handles',nargs='*',default=[])
p.add_argument('--collar-source-y',type=float,default=.50);a=p.parse_args()
load=lambda p:json.loads(p.read_text())
d=load(E/'candidates/fit-r41.json');s=np.array(d['sourceVertices']);v=np.array(d['positions'])
original_source=s.copy()
raw=np.array([list(map(float,line.split()[1:4])) for line in (R/'atlas-data/source-cache/datasets/skin-source-review-2026-10-13/base.obj').read_text().splitlines() if line.startswith('v ')])*.1
body_core=raw[np.array(d['originalVertexIds'])]
weight=np.clip((s[:,1]-a.collar_source_y)/.08,0,1);weight=weight*weight*(3-2*weight)
s+=weight[:,None]*(body_core-s)
ids=np.flatnonzero(original_source[:,1]>a.collar_source_y)
mask=np.zeros(len(s),bool);mask[ids]=True
edges=np.array(sorted({tuple(sorted((int(a),int(b)))) for f in d['faces'] for a,b in zip(f['derivedVertices'],f['derivedVertices'][1:]+f['derivedVertices'][:1])}))
cut=edges[mask[edges[:,0]]!=mask[edges[:,1]]];roots=np.array(sorted(set(cut.ravel())&set(ids)))
controls=load(R/'work/evidence/AT10/2026-10-13-skin-fit-r1/native-controls-r2.json')['controls']
native=load(R/'work/evidence/AT10/2026-10-13-skin-fit-r1/native-surfaces-r1.json')
native.update(load(E/'native-supplement-r1.json'))
selected=[x for x in controls if x['id'] in ['joint-neck','joint-head','joint-head-2','joint-jaw','joint-l-eye','joint-r-eye','crown','occiput','forehead','chin','nose-tip'] and x['id'] not in a.omit_handles]
new_controls=[]
for c in selected:
    c=json.loads(json.dumps(c));raw_source=raw[c['sourceVertexIds']].mean(0)
    w=np.clip((np.array(c['source'])[1]-a.collar_source_y)/.08,0,1);w=w*w*(3-2*w)
    c['source']=(np.array(c['source'])*(1-w)+raw_source*w).tolist()
    if c['id'] in ['joint-head','joint-neck']:
        name='Atlas (C1)' if c['id']=='joint-head' else 'Vertebra C6'
        key=next(k for k,x in native.items() if x['name']==name)
        c['previousTarget']=c['target'];c['target']=np.array(native[key]['v']).mean(0).tolist()
        c['nativeReferences']=[{'sourceKey':key,'sourceVertexIds':list(range(len(native[key]['v']))),'operator':'observed-vertex-mean','nativeTriangleIds':list(range(len(native[key]['t'])))}]
        c['role']='AI-authored static head/neck rig handle from source helper position and native cervical geometry; not an exact anatomical joint/landmark claim'
        c['semanticChange']='Replace whole occipital/C4 centre handles whose relative heights compressed the lower head/neck; numerical fit must be verified independently.'
    if c['id']=='joint-jaw':c['role']='source jaw/chin handle; not a temporomandibular hinge'
    new_controls.append(c)
centers=np.vstack([s[roots],np.array([x['source'] for x in new_controls])]);targets=np.vstack([v[roots],np.array([x['target'] for x in new_controls])])
reg=np.r_[np.full(len(roots),1e-10),np.full(len(new_controls),1e-8)]
operator=cubic_operator(centers,targets,reg)
mapped,jac=operator(s[ids]);v[ids]=mapped;v[roots]=np.array(d['positions'])[roots]
assert np.isfinite(v).all()
record={'patch':'head-bilateral','sourceVertices':ids.tolist(),'sharedBoundary':[{'sourceVertex':int(i),'sourceM':s[i].tolist(),'worldM':v[i].tolist()} for i in roots],
    'nativeJointControls':new_controls,'sourceFieldCentersM':centers.tolist(),'nativeFieldTargetsM':targets.tolist(),'regularization':reg.tolist(),
    'sourceMorphRecipe':{'headYoungTargetWeight':0,'restYoungTargetWeight':1,'collarTransitionSourceYoungYM':[a.collar_source_y,a.collar_source_y+.08],'transition':'cubic smoothstep in source recipe coordinates; numerical domain collar, not an anatomical landmark assertion','sourceIdsUnchanged':True},
    'minimumInitialSampledJacobian':float(np.linalg.det(jac).min()),'nonPositiveJacobianCount':int((np.linalg.det(jac)<=0).sum()),
    'omittedRigHandles':a.omit_handles,'omissionReason':'Source rig handles can lie outside skin and are not physical bone points. Original groups are retained, not equated to anatomical pivots.',
    'wholeSkinAcceptance':False,'requiresIndependentSourceAndEmittedQa':True}
d['sourceVertices']=s.tolist();d['positions']=v.tolist();d['candidateRevision']=a.revision;d['fitAcceptancePassed']=False;d['learnerEligible']=False
d['sourceCoordinateRecipe']={'originalSourceCoordinatesIn':'base.obj+target pinned immutable inputs','headCoreBlend':record['sourceMorphRecipe'],
    'logicalVertexCoreWeights':weight.tolist(),'priorSourceCoordinatesSha256':hashlib.sha256(original_source.astype('<f8').tobytes()).hexdigest()}
for path,payload in [(E/f'candidates/fit-{a.revision}.json',d),(E/f'surface-bands-{a.revision}.json',{'patches':[record]})]:
    assert not path.exists();path.write_text(json.dumps(payload,separators=(',',':')))
print({'sourceUnitVertices':len(ids),'boundaryVertices':len(roots),'minimumJacobian':record['minimumInitialSampledJacobian'],'nonPositive':record['nonPositiveJacobianCount']})
