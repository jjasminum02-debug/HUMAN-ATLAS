"""Limit only added transport against the accepted same-pose neighbor baseline.

No pushing, hidden surfaces or increased threshold. Existing source overlaps are
retained; this sampled vertex constraint does not certify collision-free tissue.
"""
import numpy as np
from verify_glb_interpolation import node_positions,bounded_inside,channel_data
from author_source_surface_motion import array

def constrained_field(world,tri,frames,corrections,prior_doc,prior_binary,ni,names):
    tracks=channel_data(prior_doc,prior_binary);samples=[];neighbors=[]
    for n,node in enumerate(prior_doc['nodes']):
        if names.get(node.get('extras',{}).get('sourceKey'),'').startswith('Vastus'):
            p=prior_doc['meshes'][node['mesh']]['primitives'][0];neighbors.append((n,array(prior_doc,prior_binary,p['indices']).reshape(-1,3)))
    for t in np.linspace(0,3,97):
        k=min(11,int(t/.25));a=(t-k*.25)/.25
        before=node_positions(prior_doc,prior_binary,tracks,ni,t);extra=corrections[k]*(1-a)+corrections[k+1]*a
        for n,idx in neighbors:
            neighbor=node_positions(prior_doc,prior_binary,tracks,n,t)
            samples.append((before,extra,neighbor,idx,bounded_inside(before,neighbor,idx)))
    edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0);adj=[[] for _ in world]
    for a,b in edges:adj[a].append(b);adj[b].append(a)
    base=world[tri];base_normal=np.cross(base[:,1]-base[:,0],base[:,2]-base[:,0]);base_area=np.linalg.norm(base_normal,axis=1);good=base_area>=1e-12
    alpha=np.ones(len(world));pins=set();iterations=[]
    for iteration in range(128):
        bad=set()
        bad_faces=set()
        for before,extra,neighbor,idx,baseline in samples:
            posed=before+extra*alpha[:,None]
            bad.update(np.flatnonzero(bounded_inside(posed,neighbor,idx)&~baseline).tolist())
            t=posed[tri];normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);bad_faces.update(np.flatnonzero(good&(((normal*base_normal).sum(1)<0)|(np.linalg.norm(normal,axis=1)<base_area*.1))).tolist())
        if not bad and not bad_faces:return alpha,{'iterations':iterations,'limitedVertexIndices':sorted(pins),'minimumFactor':float(alpha.min()),'meanFactor':float(alpha.mean()),'sampledTimes':97,'newSamePoseNeighborContainment':0,'faceThresholdUnchanged':.1}
        for f in bad_faces:bad.update(tri[f].tolist())
        pins.update(bad);alpha[list(pins)]=0
        # Lower neighboring free contributions smoothly; never raise a constrained value.
        for _ in range(4):
            average=np.array([alpha[a].mean() if a else alpha[i] for i,a in enumerate(adj)])
            alpha=np.minimum(alpha,.5*alpha+.5*average);alpha[list(pins)]=0
        iterations.append({'iteration':iteration,'limitedSourceVertexIndices':sorted(bad),'badTriangleIds':sorted(bad_faces)})
    raise ValueError('Added source transport could not satisfy same-pose neighbor constraint')
