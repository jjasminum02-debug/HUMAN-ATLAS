"""Pure numerical cubic field used by offline AT10 authoring and inspection."""
import numpy as np

def landmark_flow_operator(recipe):
    """Replay a source-bound 3D field; no candidate or source is modified."""
    affine=np.asarray(recipe['affine']);translation=np.asarray(recipe['translation'])
    stages=[(np.asarray(x['centres']),np.asarray(x['sigmaM']),np.asarray(x['coefficients'])) for x in recipe['stages']]
    assert np.linalg.det(affine)>0
    for _,sigma,coefficient in stages:
        assert np.isfinite(sigma).all() and (sigma>0).all() and np.isfinite(coefficient).all()
        assert (np.linalg.norm(coefficient,axis=1)/(np.sqrt(np.e)*sigma)).sum()<1
    def evaluate(points):
        values=np.asarray(points)@affine.T+translation;jac=np.tile(affine,(len(values),1,1))
        for centres,sigma,coefficient in stages:
            delta=values[:,None,:]-centres[None,:,:]
            phi=np.exp(-np.einsum('qci,qci->qc',delta,delta)/(2*sigma**2))
            derivative=-phi[:,:,None]*delta/sigma[None,:,None]**2
            gradient=np.eye(3)+np.einsum('ci,qcj->qij',coefficient,derivative)
            jac=gradient@jac;values+=phi@coefficient
        return values,jac
    return evaluate

def cubic_operator(centers, targets, regularization, scale=.1):
    centers=np.asarray(centers);targets=np.asarray(targets)
    center=centers.mean(0);x=(centers-center)/scale
    r=np.linalg.norm(x[:,None]-x[None],axis=2);poly=np.column_stack([np.ones(len(x)),x])
    coefficient=np.linalg.solve(np.block([[r**3+np.diag(regularization),poly],[poly.T,np.zeros((4,4))]]),np.vstack([targets,np.zeros((4,3))]))
    def evaluate(points):
        values=[];derivatives=[]
        for start in range(0,len(points),256):
            q=(np.asarray(points)[start:start+256]-center)/scale
            delta=q[:,None]-x[None];radius=np.linalg.norm(delta,axis=2)
            values.append(np.einsum('qn,no->qo',radius**3,coefficient[:-4])+np.column_stack([np.ones(len(q)),q])@coefficient[-4:])
            derivatives.append((np.einsum('qnk,no->qok',3*radius[:,:,None]*delta,coefficient[:-4])+coefficient[-3:].T)/scale)
        return np.concatenate(values),np.concatenate(derivatives)
    return evaluate
