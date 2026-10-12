"""Continuous same-pose penetration-depth bound using existing source readers.

Boolean 'already inside' cannot permit an arbitrarily deeper new overlap. The
accepted source pose defines the depth bound; actual source nearest triangles
define the corrective. Neither is an anatomical footprint or physical tissue.
"""
import numpy as np
from t66_contact_correctives import bounded_inside,nearest_surface_details,outward_surface_direction

def depth_wrap(frame,rest,tri,contacts,locked,margin=.00015):
    original=frame.copy();current=frame.copy();correction=np.zeros_like(frame);pins={};records=[]
    edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0)
    ew=1/np.maximum(np.linalg.norm(rest[edges[:,0]]-rest[edges[:,1]],axis=1),1e-8);degree=np.bincount(edges.ravel(),weights=np.repeat(ew,2),minlength=len(frame))
    # Exact baseline depths, including previously illustrated overlaps.
    prepared=[]
    for key,neighbor,idx,reference,reference_neighbor in contacts:
        inside=bounded_inside(reference,reference_neighbor,idx);allow=np.zeros(len(frame));ids=np.flatnonzero(inside)
        if len(ids):q,_=nearest_surface_details(reference[ids],reference_neighbor,idx);allow[ids]=np.linalg.norm(reference[ids]-q,axis=1)
        prepared.append((key,neighbor,idx,allow))
    for iteration in range(16):
        added=False
        for key,neighbor,idx,allow in prepared:
            ids=np.array([v for v in np.flatnonzero(bounded_inside(current,neighbor,idx)) if int(v) not in locked],dtype=int)
            if not len(ids):continue
            q,faces=nearest_surface_details(current[ids],neighbor,idx);depth=np.linalg.norm(q-current[ids],axis=1);bad=depth>allow[ids]+1e-8
            if not bad.any():continue
            ids=ids[bad];q=q[bad];faces=faces[bad];depth=depth[bad]
            for v,nearest,face in zip(ids,q,faces):
                outward,_=outward_surface_direction(current[v],nearest,neighbor,idx,face)
                target=nearest+outward*(margin if allow[v]==0 else -max(0,allow[v]-margin))
                pins[int(v)]=target-original[v]
            records.append({'sourceKey':key,'iteration':iteration,'sourceVertexIndices':ids.tolist(),'maximumExcessDepthMetres':float(np.max(depth-allow[ids]))});added=True
        if not added:break
        for _ in range(400):
            sums=np.zeros_like(correction);np.add.at(sums,edges[:,0],ew[:,None]*correction[edges[:,1]]);np.add.at(sums,edges[:,1],ew[:,None]*correction[edges[:,0]])
            correction=.5*correction+.5*sums/np.maximum(degree,1)[:,None]
            for v,value in pins.items():correction[v]=value
            correction[list(locked)]=0
        current=original+correction
    return current,{'method':'source same-pose depth bound and weighted graph smoothing','numericalMarginMetres':margin,'contactPushes':records,'maximumCorrectiveMetres':float(np.linalg.norm(correction,axis=1).max()),'correctiveVectors':correction.tolist()}
