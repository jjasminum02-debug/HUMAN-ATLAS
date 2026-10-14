"""Pure numerical cubic field used by offline AT10 authoring and inspection."""
import numpy as np

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
