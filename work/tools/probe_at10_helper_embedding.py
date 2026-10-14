"""Read-only rig-handle embedding diagnostic; no automatic homology verdict."""
from pathlib import Path
import json, sys
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];E=R/'work/evidence/AT10/2026-10-14-skin-fit-r5'
base=json.loads((R/'work/evidence/AT10/2026-10-13-skin-fit-r2/candidates/fit-r22.json').read_text())
t=[[f['derivedVertices'][0],f['derivedVertices'][j],f['derivedVertices'][j+1]] for f in base['faces'] for j in range(1,len(f['derivedVertices'])-1)]
def inspect(point,tree):
    votes=[]
    for dr in [(-1,.137,.231),(-1,-.217,.113),(-1,.219,-.117)]:
        direction=Vector(dr).normalized();origin=Vector(point);count=0
        for _ in range(40):
            hit,_,_,_=tree.ray_cast(origin,direction,4.)
            if hit is None:break
            count+=1;origin=hit+direction*.000002
        votes.append(count%2)
    q,_,face,d=tree.find_nearest(Vector(point))
    return {'insideVotes':votes,'insideMajority':sum(votes)>=2,'nearestTriangle':face,'distanceM':d,'nearestM':list(q)}
records=[]
for revision,manifest,patch in [('r44',R/'work/evidence/AT10/2026-10-14-skin-fit-r4/surface-bands-r31.json','foot-right'),('r48',E/'surface-bands-r48.json','head-bilateral')]:
    d=json.loads((E/f'candidates/fit-{revision}.json').read_text());f=next(x for x in json.loads(manifest.read_text())['patches'] if x['patch']==patch)
    source=BVHTree.FromPolygons(d['sourceVertices'],t,all_triangles=True);candidate=BVHTree.FromPolygons(d['positions'],t,all_triangles=True)
    for c in f['nativeJointControls']:
        si=inspect(c['source'],source);di=inspect(c['target'],candidate)
        records.append({'revision':revision,'patch':patch,'handleId':c['id'],'sourceHelperVertexIds':c['sourceVertexIds'],'source':c['source'],'target':c['target'],'sourceEmbedding':si,'targetEmbeddingInCandidate':di,
            'outsideSourceToInsideCandidateDiagnostic':not si['insideMajority'] and di['insideMajority'],'notAHomologyApproval':True})
(E/'helper-embedding-r1.json').write_text(json.dumps(records,indent=2)+'\n')
print([(x['revision'],x['handleId'],x['sourceEmbedding']['insideMajority'],x['targetEmbeddingInCandidate']['insideMajority'],x['sourceEmbedding']['distanceM']) for x in records],flush=True)
