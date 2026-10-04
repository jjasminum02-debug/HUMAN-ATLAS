#!/usr/bin/env python3
"""Replay actual GLB TRS/morph keys against the authored source-frame poses.

This catches exporter placement mistakes which ideal Python trajectories alone
cannot detect. It does not approve anatomical axes, footprints or normal ROM.
"""
import numpy as np
import json, struct
from author_source_surface_motion import array
from derive_source_surface_motion import sha

def qmatrix(q):
 x,y,z,w=q
 return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
  [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
  [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])

def verify_glb(path,payload,frames,deformation_source_keys=()):
 deforming=set(deformation_source_keys)
 raw=path.read_bytes();magic,version,length=struct.unpack_from('<III',raw)
 if magic!=0x46546c67 or version!=2 or length!=len(raw):raise ValueError('invalid actual GLB header')
 jl,jt=struct.unpack_from('<II',raw,12);bl,bt=struct.unpack_from('<II',raw,20+jl)
 if jt!=0x4e4f534a or bt!=0x004e4942 or 28+jl+bl!=length:raise ValueError('invalid actual GLB chunks')
 doc=json.loads(raw[20:20+jl]);buf=raw[28+jl:];tracks={}
 for channel in doc['animations'][0]['channels']:
  sample=doc['animations'][0]['samplers'][channel['sampler']]
  times=np.asarray(array(doc,buf,sample['input']),dtype=float).reshape(-1)
  values=np.asarray(array(doc,buf,sample['output']),dtype=float).reshape(len(times),-1)
  tracks[(channel['target']['node'],channel['target']['path'])]=(times,values)
 def track_at(node,path,time):
  track=tracks.get((node,path))
  if track is None:return None
  times,values=track;index=int(np.argmin(np.abs(times-time)))
  if abs(float(times[index])-time)>1e-6:raise ValueError(f'authored frame time missing in emitted GLB {node}/{path}: {time}')
  return values[index]
 rows=[]
 for ni,node in enumerate(doc['nodes']):
  key=node['extras']['sourceKey'];primitive=doc['meshes'][node['mesh']]['primitives'][0]
  pos=array(doc,buf,primitive['attributes']['POSITION']);poses=frames[key][0]; maximum=0
  if key in deforming:
   rows.append({'sourceKey':key,'sourceFrameComparison':'authored_surface_deformation',
    'rigidCounterfactualDifferenceMetres':None,'passed':False,'requiresGeometryQc':True,
    'reflectionPreserved':bool('scale' in node and node['scale'][0]<0)})
   continue
  for step,expected in enumerate(poses):
   time=float(payload['family']['durationSeconds'])*step/(len(poses)-1)
   local=pos.astype(float).copy()
   weight_values=track_at(ni,'weights',time)
   if 'targets' in primitive and weight_values is not None:
    weights=weight_values.reshape(len(primitive['targets']))
    for target,weight in zip(primitive['targets'],weights):
     if weight:local+=array(doc,buf,target['POSITION'])*weight
   if 'matrix' in node:
    M=np.array(node['matrix']).reshape(4,4).T; actual=local@M[:3,:3].T+M[:3,3]
   else:
    q=track_at(ni,'rotation',time)
    t=track_at(ni,'translation',time)
    if q is None:q=node.get('rotation',[0,0,0,1])
    if t is None:t=node.get('translation',[0,0,0])
    actual=(local*np.array(node['scale']))@qmatrix(q).T+t
   maximum=max(maximum,float(np.max(np.linalg.norm(actual-expected,axis=1))))
  rows.append({'sourceKey':key,'maximumWorldErrorMetres':maximum,
   'sourceFrameComparison':'exact_rigid_source_frame','passed':maximum<=1e-6,
   'requiresGeometryQc':False,
   'reflectionPreserved':bool('scale' in node and node['scale'][0]<0)})
 return {'familyId':payload['family']['id'],'method':'Actual emitted GLB quaternion/translation/signed scale and morph buffers replay at authored keys; rigid structures compare to immutable source-frame trajectories while authored deforming surfaces require linked interpolation geometry/contact QC',
  'motionSha256':sha(path.read_bytes()),'testedKeys':payload['family']['samples']+1,
  'rows':rows,'maximumWorldErrorMetres':max((r['maximumWorldErrorMetres'] for r in rows if 'maximumWorldErrorMetres' in r),default=0),
  'passed':all(r['passed'] for r in rows),'anatomicalApproval':False}
