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

def verify_glb(path,payload,frames):
 raw=path.read_bytes();magic,version,length=struct.unpack_from('<III',raw)
 if magic!=0x46546c67 or version!=2 or length!=len(raw):raise ValueError('invalid actual GLB header')
 jl,jt=struct.unpack_from('<II',raw,12);bl,bt=struct.unpack_from('<II',raw,20+jl)
 if jt!=0x4e4f534a or bt!=0x004e4942 or 28+jl+bl!=length:raise ValueError('invalid actual GLB chunks')
 doc=json.loads(raw[20:20+jl]);buf=raw[28+jl:];tracks={}
 for channel in doc['animations'][0]['channels']:
  sample=doc['animations'][0]['samplers'][channel['sampler']]
  tracks[(channel['target']['node'],channel['target']['path'])]=array(doc,buf,sample['output'])
 rows=[]
 for ni,node in enumerate(doc['nodes']):
  key=node['extras']['sourceKey'];primitive=doc['meshes'][node['mesh']]['primitives'][0]
  pos=array(doc,buf,primitive['attributes']['POSITION']);poses=frames[key][0]; maximum=0
  for step,expected in enumerate(poses):
   local=pos.astype(float).copy()
   if 'targets' in primitive:
    weights=tracks[(ni,'weights')].reshape(len(poses),len(primitive['targets']))[step]
    for target,weight in zip(primitive['targets'],weights):
     if weight:local+=array(doc,buf,target['POSITION'])*weight
   if 'matrix' in node:
    M=np.array(node['matrix']).reshape(4,4).T; actual=local@M[:3,:3].T+M[:3,3]
   else:
    q=tracks[(ni,'rotation')][step];t=tracks[(ni,'translation')][step]
    actual=(local*np.array(node['scale']))@qmatrix(q).T+t
   maximum=max(maximum,float(np.max(np.linalg.norm(actual-expected,axis=1))))
  rows.append({'sourceKey':key,'maximumWorldErrorMetres':maximum,'passed':maximum<=1e-6,
   'reflectionPreserved':bool('scale' in node and node['scale'][0]<0)})
 return {'familyId':payload['family']['id'],'method':'Actual emitted GLB quaternion/translation/signed scale and morph buffers replay at all 9 authored keys, compared to immutable source-frame engineering trajectories',
  'motionSha256':sha(path.read_bytes()),'testedKeys':payload['family']['samples']+1,
  'rows':rows,'maximumWorldErrorMetres':max(r['maximumWorldErrorMetres'] for r in rows),'passed':all(r['passed'] for r in rows),'anatomicalApproval':False}
