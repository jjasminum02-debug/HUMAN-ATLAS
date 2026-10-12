"""Q02 only: actual emitted tracks, native topology and adjacent-layer samples.

Read-only probe. Winding containment is a sampled surface diagnostic; source
muscles are not guaranteed watertight and this is not collision certification.
"""
from pathlib import Path
import sys, json, hashlib
import numpy as np
R=Path(__file__).resolve().parents[4]; E=Path(__file__).parent
sys.path[:0]=[str(R/'work/tools'),str(R/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from verify_glb_interpolation import read_glb, channel_data, node_positions, bounded_inside
from author_source_surface_motion import array
from t66_contact_correctives import nearest_surface_details
uri='atlas-data/assets/motion/t66-priority-s04-flex/motion.glb'
raw,d,b=read_glb(R/uri); sha=hashlib.sha256(raw).hexdigest()
assert sha=='fd09265a937bebff65f0d1b095bc2d0350f13b7222e53a90c32bb40b80c43adf'
tracks=channel_data(d,b); nodes={n.get('extras',{}).get('sourceKey'):i for i,n in enumerate(d['nodes'])}
auth=json.loads((R/'work/evidence/T66/priority-trunk-2026-10-05/flex/authored-input.json').read_text())
keys={'left':'ZA-c7010a9-d75abb958e1463ceecb5430b','right':'ZA-c7010a9-eb0bd1853a90acada85e9177'}
neighbors={'left':['ZA-c7010a9-62a4fba42674f5d453c6e277','ZA-c7010a9-98148d5380ab1abd5154e41c','ZA-c7010a9-33941d62db2cd36b20fe5945'], 'right':['ZA-c7010a9-bef3937bee85a8c7bcc77d9c','ZA-c7010a9-6d200091f5d75fd817af12ad','ZA-c7010a9-9184adfd521c527f3b352e71']}
def primitive(k):return d['meshes'][d['nodes'][nodes[k]]['mesh']]['primitives'][0]
def triangles(k):return np.asarray(array(d,b,primitive(k)['indices']),dtype=int).reshape(-1,3)
def points(k,t):return node_positions(d,b,tracks,nodes[k],t)
rows=[]
for side,key in keys.items():
 p=primitive(key); tri=triangles(key); rest=points(key,0)
 field=next(v for v in auth['surfaceFields'] if v['sourceKey']==key)
 base=rest[tri]; normals=np.cross(base[:,1]-base[:,0],base[:,2]-base[:,0]); areas=np.linalg.norm(normals,axis=1); good=areas>1e-12
 edge=np.unique(np.sort(np.r_[tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]],axis=1),axis=0)
 lengths=np.linalg.norm(rest[edge[:,0]]-rest[edge[:,1]],axis=1)
 unique,inv=np.unique(np.round(rest,7),axis=0,return_inverse=True); reps=np.unique(inv,return_index=True)[1]
 # Deterministic sample of the actual source vertices, both surfaces retained.
 ids=reps[np.linspace(0,len(reps)-1,min(240,len(reps)),dtype=int)]
 fixed=np.array(field['fixedVertexIndices'],dtype=int); moving=np.array(field['movingVertexIndices'],dtype=int)
 measures=[]
 for t in np.linspace(0,2.5,129):
  v=points(key,t); ft=v[tri]; nn=np.cross(ft[:,1]-ft[:,0],ft[:,2]-ft[:,0]); aa=np.linalg.norm(nn,axis=1)
  measures.append({'seconds':float(t),'flippedFaces':int(((nn*normals).sum(1)[good]<0).sum()),'minimumAreaRatio':float((aa[good]/areas[good]).min()),'maximumEdgeDelta':float(np.abs(np.linalg.norm(v[edge[:,0]]-v[edge[:,1]],axis=1)/np.maximum(lengths,1e-12)-1).max()),'fixedMaximumMm':float(np.linalg.norm(v[fixed]-rest[fixed],axis=1).max()*1000),'upperDisplacementMaximumMm':float(np.linalg.norm(v[moving]-rest[moving],axis=1).max()*1000)})
 layer=[]
 for neighbor in neighbors[side]:
  nt=triangles(neighbor); baseline=bounded_inside(rest[ids],points(neighbor,0),nt)
  probes=[]
  for t in [0,.625,1.25,1.875,2.5]:
   v=points(key,t)[ids]; nv=points(neighbor,t); contained=bounded_inside(v,nv,nt); fresh=contained&~baseline
   newids=ids[fresh]; depth=0.
   if fresh.any():
    q,_=nearest_surface_details(v[fresh],nv,nt);depth=float(np.linalg.norm(v[fresh]-q,axis=1).max()*1000)
   probes.append({'seconds':t,'contained':int(contained.sum()),'newContained':int(fresh.sum()),'newSourceVertexIds':newids.tolist(),'newNearestDepthMaxMm':depth})
  layer.append({'sourceKey':neighbor,'sampledVertices':len(ids),'baselineContained':int(baseline.sum()),'samples':probes})
  print(side,neighbor,'new contained',max(x['newContained'] for x in probes),flush=True)
 # Compare source POSITION/index/instance with the historical emitted rest file.
 _,rd,rb=read_glb(R/'work/evidence/T66/priority-trunk-2026-10-05/flex/reference.glb')
 rn=next(n for n in rd['nodes'] if n.get('extras',{}).get('sourceKey')==key);rp=rd['meshes'][rn['mesh']]['primitives'][0]
 identical={s:np.array_equal(array(d,b,p['attributes'][s]),array(rd,rb,rp['attributes'][s])) for s in ['POSITION','NORMAL']}
 identical['indices']=np.array_equal(array(d,b,p['indices']),array(rd,rb,rp['indices']))
 identical['matrix']=d['nodes'][nodes[key]].get('matrix')==rn.get('matrix')
 rows.append({'side':side,'sourceKey':key,'node':nodes[key],'sourceGeometryUnchanged':identical,'vertices':len(rest),'uniquePositionVertices':len(unique),'triangles':len(tri),'morphTargets':len(p['targets']),'fixedVertices':len(fixed),'movingUpperVertices':len(moving),'attachmentRoles':'source-Y masks with actual pelvis/rib context; not measured footprints','perSample':measures,'layerSamples':layer})
result={'uri':uri,'sha256':sha,'bytes':len(raw),'contextNodes':len(d['nodes']),'rows':rows,'allGeometryPassed':all(all(m['flippedFaces']==0 and m['minimumAreaRatio']>=.1 and m['fixedMaximumMm']<1e-6 for m in r['perSample']) for r in rows),'allSurfaceIntersectionsExcluded':False,'measuredAttachmentFootprints':False,'newPhysiologicalClaim':False}
(E/'current-geometry-probe.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='rows'}))
