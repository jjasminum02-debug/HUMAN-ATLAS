"""Pure source-triangle contact diagnostics for local derived educational surfaces."""
import math
import numpy as np

def inside(points,vertices,triangles):
    # Generalized winding number; exact triangle solid angles, not bounding-box collision claims.
    tri=vertices[triangles];result=[]
    for start in range(0,len(points),64):
        p=points[start:start+64,None,:];a=tri[None,:,0]-p;b=tri[None,:,1]-p;c=tri[None,:,2]-p
        la=np.linalg.norm(a,axis=2);lb=np.linalg.norm(b,axis=2);lc=np.linalg.norm(c,axis=2)
        top=np.einsum('ijk,ijk->ij',a,np.cross(b,c))
        bottom=la*lb*lc+np.einsum('ijk,ijk->ij',a,b)*lc+np.einsum('ijk,ijk->ij',b,c)*la+np.einsum('ijk,ijk->ij',c,a)*lb
        winding=np.sum(2*np.arctan2(top,bottom),axis=1)/(4*math.pi)
        result.extend(np.abs(winding)>.75)
    return np.array(result)
