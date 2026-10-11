"""Offline native-surface intersection index for carrier generation tools."""
from collections import defaultdict
import numpy as np

class SurfaceIndex:
    def __init__(self, surfaces, cell=.025):
        self.keys=list(surfaces);self.cell=cell
        self.triangles=np.concatenate([v[t] for v,t in surfaces.values()])
        self.source_ids=np.concatenate([np.full(len(t),i,dtype=np.int32) for i,(v,t) in enumerate(surfaces.values())])
        self.low=self.triangles.min(axis=1);self.high=self.triangles.max(axis=1)
        bins=defaultdict(list)
        for i,(lo,hi) in enumerate(zip(np.floor(self.low[:,:2]/cell).astype(int),np.floor(self.high[:,:2]/cell).astype(int))):
            for x in range(lo[0],hi[0]+1):
                for y in range(lo[1],hi[1]+1):bins[x,y].append(i)
        self.bins={k:np.array(v,dtype=np.int32) for k,v in bins.items()}

    @staticmethod
    def crosses(origins,directions,triangles):
        e1=triangles[:,1]-triangles[:,0];e2=triangles[:,2]-triangles[:,0]
        pv=np.cross(directions,e2);det=np.einsum('ij,ij->i',e1,pv)
        inv=np.divide(1,det,out=np.zeros_like(det),where=np.abs(det)>1e-12)
        tv=origins-triangles[:,0];u=np.einsum('ij,ij->i',tv,pv)*inv;q=np.cross(tv,e1)
        v=np.einsum('ij,ij->i',directions,q)*inv;distance=np.einsum('ij,ij->i',e2,q)*inv
        return (np.abs(det)>1e-12)&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(distance>1e-7)&(distance<1-1e-7)

    def intersections(self, triangle):
        lo=triangle.min(axis=0);hi=triangle.max(axis=0)
        a=np.floor(lo[:2]/self.cell).astype(int);b=np.floor(hi[:2]/self.cell).astype(int)
        bins=[self.bins[x,y] for x in range(a[0],b[0]+1) for y in range(a[1],b[1]+1) if (x,y) in self.bins]
        if not bins:return []
        ids=np.unique(np.concatenate(bins));ids=ids[(self.low[ids]<=hi+1e-8).all(axis=1)&(self.high[ids]>=lo-1e-8).all(axis=1)]
        if not len(ids):return []
        native=self.triangles[ids];mask=np.zeros(len(ids),dtype=bool)
        for a,b in [(0,1),(1,2),(2,0)]:
            mask|=self.crosses(np.broadcast_to(triangle[a],(len(ids),3)),np.broadcast_to(triangle[b]-triangle[a],(len(ids),3)),native)
            mask|=self.crosses(native[:,a],native[:,b]-native[:,a],np.broadcast_to(triangle,(len(ids),3,3)))
        return sorted({self.keys[self.source_ids[i]] for i in ids[mask]})
