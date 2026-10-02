"""Authored surface wrapping against actual pinned source triangles, no new anatomy."""
import numpy as np
from source_surface_constraints import inside

def bounded_inside(points,vertices,triangles):
    result=np.zeros(len(points),dtype=bool)
    ids=np.flatnonzero(((points>=vertices.min(0)-1e-8)&(points<=vertices.max(0)+1e-8)).all(1))
    if len(ids):result[ids]=inside(points[ids],vertices,triangles)
    return result

def nearest_surface(points,vertices,triangles):
    tri=vertices[triangles];a,b,c=tri[:,0],tri[:,1],tri[:,2];ab=b-a;ac=c-a
    normal=np.cross(ab,ac);nn=(normal*normal).sum(1)
    out=[]
    for p in points:
        projection=p-normal*((normal*(p-a)).sum(1)/np.maximum(nn,1e-30))[:,None]
        ap=projection-a;d00=(ab*ab).sum(1);d01=(ab*ac).sum(1);d11=(ac*ac).sum(1)
        d20=(ap*ab).sum(1);d21=(ap*ac).sum(1);den=d00*d11-d01*d01
        v=(d11*d20-d01*d21)/np.maximum(den,1e-30);w=(d00*d21-d01*d20)/np.maximum(den,1e-30)
        candidates=[projection];valid=(v>=0)&(w>=0)&(v+w<=1)&(nn>1e-25)
        distances=[np.where(valid,((projection-p)**2).sum(1),np.inf)]
        for start,end in [(a,b),(b,c),(c,a)]:
            edge=end-start;t=np.clip(((p-start)*edge).sum(1)/np.maximum((edge*edge).sum(1),1e-30),0,1)
            q=start+t[:,None]*edge;candidates.append(q);distances.append(((q-p)**2).sum(1))
        distances=np.stack(distances);ci,ti=np.unravel_index(np.argmin(distances),distances.shape);out.append(candidates[ci][ti])
    return np.array(out)

def wrap(frame,rest,idx,contacts,locked):
    original=frame.copy();correction=np.zeros_like(frame);pins={};records=[]
    edges=np.unique(np.sort(np.r_[idx[:,[0,1]],idx[:,[1,2]],idx[:,[2,0]]],axis=1),axis=0)
    weights=1/np.maximum(np.linalg.norm(rest[edges[:,0]]-rest[edges[:,1]],axis=1),1e-8)
    degree=np.bincount(edges.ravel(),weights=np.repeat(weights,2),minlength=len(frame))
    for iteration in range(12):
        added=False
        for key,bone,tri,baseline in contacts:
            fresh=np.flatnonzero(bounded_inside(frame,bone,tri)&~baseline)
            free=np.array([v for v in fresh if int(v) not in locked],dtype=int)
            if not len(free):continue
            q=nearest_surface(frame[free],bone,tri);direction=q-frame[free];length=np.linalg.norm(direction,axis=1)
            q+=direction/np.maximum(length,1e-15)[:,None]*.00015
            for v,target in zip(free,q):pins[int(v)]=target-original[v]
            records.append({'sourceKey':key,'iteration':iteration,'vertexIndices':free.tolist(),'maximumPushMetres':float(length.max())});added=True
        if not added:break
        for v,value in pins.items():correction[v]=value
        for relax in range(400):
            sums=np.zeros_like(correction)
            np.add.at(sums,edges[:,0],weights[:,None]*correction[edges[:,1]]);np.add.at(sums,edges[:,1],weights[:,None]*correction[edges[:,0]])
            correction=.5*correction+.5*sums/np.maximum(degree,1)[:,None]
            for v,value in pins.items():correction[v]=value
            correction[list(locked)]=0
        frame=original+correction
    return frame,{'contactPushes':records,'maximumCorrectiveMetres':float(np.linalg.norm(correction,axis=1).max()),'correctiveVectors':correction.tolist()}

def arap_wrap(frame,rest,idx,contacts,locked,force_shape=False):
    """Local rest-edge-preserving corrective with exact authored endpoint constraints.

    Contact targets derive only from actual source triangles. The independent
    orientation/area and source-containment verifier still decides acceptance.
    """
    edges=np.unique(np.sort(np.r_[idx[:,[0,1]],idx[:,[1,2]],idx[:,[2,0]]],axis=1),axis=0)
    i,j=edges.T;d=rest[i]-rest[j];w=1/np.maximum(np.linalg.norm(d,axis=1),1e-8)
    degree=np.bincount(edges.ravel(),weights=np.repeat(w,2),minlength=len(rest))
    original=frame.copy();x=frame.copy();pins={int(v):frame[v].copy() for v in locked};records=[]
    for contactPass in range(8):
        for key,bone,tri,baseline in contacts:
            fresh=np.flatnonzero(bounded_inside(x,bone,tri)&~baseline)
            free=np.array([v for v in fresh if int(v) not in locked],dtype=int)
            if not len(free):continue
            q=nearest_surface(x[free],bone,tri);direction=q-x[free];length=np.linalg.norm(direction,axis=1)
            q+=direction/np.maximum(length,1e-15)[:,None]*.00015
            for v,target in zip(free,q):pins[int(v)]=target
            records.append({'sourceKey':key,'pass':contactPass,'vertexIndices':free.tolist(),'maximumPushMetres':float(length.max())})
        if not records and not force_shape:break
        for iteration in range(300 if force_shape else 100):
            current=x[i]-x[j];cov=np.zeros((len(x),3,3));outer=w[:,None,None]*current[:,:,None]*d[:,None,:]
            np.add.at(cov,i,outer);np.add.at(cov,j,outer)
            u,_,vt=np.linalg.svd(cov);rot=u@vt;bad=np.linalg.det(rot)<0;u[bad,:,-1]*=-1;rot=u@vt
            desired=np.einsum('nij,nj->ni',(rot[i]+rot[j])*.5,d)
            sums=np.zeros_like(x);np.add.at(sums,i,w[:,None]*(x[j]+desired));np.add.at(sums,j,w[:,None]*(x[i]-desired))
            target=sums/np.maximum(degree,1)[:,None]
            x=.5*x+.5*(.98*target+.02*original)
            for v,value in pins.items():x[v]=value
        if force_shape and not contacts:break
    return x,{'contactPushes':records,'correctiveVectors':(x-original).tolist(),'maximumCorrectiveMetres':float(np.linalg.norm(x-original,axis=1).max()),'method':'authored_rest_edge_arap_not_measured_physiology'}
