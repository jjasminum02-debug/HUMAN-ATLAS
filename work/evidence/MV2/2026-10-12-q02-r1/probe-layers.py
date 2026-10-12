"""Expand only Q02's native adjacent abdominal-layer probe to every welded vertex."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
R=Path(__file__).resolve().parents[4];E=Path(__file__).parent
sys.path[:0]=[str(R/'work/tools'),str(R/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from verify_glb_interpolation import read_glb,channel_data,node_positions,bounded_inside
from author_source_surface_motion import array
from t66_contact_correctives import nearest_surface_details
raw,d,b=read_glb(R/'atlas-data/assets/motion/t66-priority-s04-flex/motion.glb');tracks=channel_data(d,b)
assert hashlib.sha256(raw).hexdigest()=='fd09265a937bebff65f0d1b095bc2d0350f13b7222e53a90c32bb40b80c43adf'
nodes={n.get('extras',{}).get('sourceKey'):i for i,n in enumerate(d['nodes'])}
keys=['ZA-c7010a9-d75abb958e1463ceecb5430b','ZA-c7010a9-eb0bd1853a90acada85e9177']
neighbors=[['ZA-c7010a9-62a4fba42674f5d453c6e277','ZA-c7010a9-98148d5380ab1abd5154e41c','ZA-c7010a9-33941d62db2cd36b20fe5945'],['ZA-c7010a9-bef3937bee85a8c7bcc77d9c','ZA-c7010a9-6d200091f5d75fd817af12ad','ZA-c7010a9-9184adfd521c527f3b352e71']]
def points(k,t):return node_positions(d,b,tracks,nodes[k],t)
def tri(k):
 p=d['meshes'][d['nodes'][nodes[k]]['mesh']]['primitives'][0];return np.asarray(array(d,b,p['indices']),dtype=int).reshape(-1,3)
rows=[]
for side,k,ns in zip(['left','right'],keys,neighbors):
 rest=points(k,0);_,ids=np.unique(np.round(rest,7),axis=0,return_index=True)
 for neighbor in ns:
  triangles=tri(neighbor);baseline=bounded_inside(rest[ids],points(neighbor,0),triangles);samples=[]
  for t in [0,.625,1.25,1.875,2.5]:
   p=points(k,t)[ids];v=points(neighbor,t);current=bounded_inside(p,v,triangles);fresh=current&~baseline
   depth=0
   if fresh.any():
    q,_=nearest_surface_details(p[fresh],v,triangles);depth=float(np.linalg.norm(p[fresh]-q,axis=1).max()*1000)
   samples.append({'seconds':t,'contained':int(current.sum()),'newContained':int(fresh.sum()),'newSourceVertexIds':ids[fresh].tolist(),'newNearestDepthMaxMm':depth})
  rows.append({'side':side,'sourceKey':k,'neighborSourceKey':neighbor,'sampleVertices':len(ids),'baselineContained':int(baseline.sum()),'samples':samples})
  (E/'adjacent-layers-full-vertex-probe.json').write_text(json.dumps({'sha256':hashlib.sha256(raw).hexdigest(),'rows':rows,'allSurfaceIntersectionsExcluded':False,'windingThreshold':.75,'sourceSurfacesNotGuaranteedWatertight':True},indent=2)+'\n')
  print(side,neighbor,'maxNew',max(x['newContained'] for x in samples),'maxDepthMm',max(x['newNearestDepthMaxMm'] for x in samples),flush=True)
