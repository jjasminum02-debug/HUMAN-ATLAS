"""Pure numerical cubic field used by offline AT10 authoring and inspection."""
import numpy as np

def flow_line_search_floor(certified_step, unscaled_surface_update_m):
    """A coefficient scale must not invalidate an otherwise useful safe motion.

    Retain twelve relative halvings and a 10nm numerical movement floor. Neither
    value is a source/native clearance, geometry, or anatomical acceptance gate.
    """
    assert np.isfinite(certified_step) and certified_step>0
    assert np.isfinite(unscaled_surface_update_m) and unscaled_surface_update_m>=0
    if certified_step*unscaled_surface_update_m<1e-8:return None
    return max(certified_step/2048,1e-8/unscaled_surface_update_m)

def owned_field_basis(values, active_vertices, fixed_vertices):
    """Make the solve predict the same per-vertex ownership as emitted updates."""
    result=np.asarray(values).copy()
    result[~np.asarray(active_vertices,dtype=bool)]=0
    result[np.asarray(fixed_vertices,dtype=int)]=0
    return result

def boundary_nullspace(values, derivatives=None, directions=None):
    """Null displacement and optional surface directional derivatives at anchors.

    This is a numerical boundary condition, not anatomical correspondence.
    Derivative rows use a metre scale to keep the SVD units comparable.
    """
    rows=np.asarray(values)
    if derivatives is not None:
        gradients=np.asarray(derivatives);vectors=np.asarray(directions)
        assert gradients.shape[0]==vectors.shape[0] and vectors.shape[-1]==3
        rows=np.vstack([rows,np.einsum('ank,adk->adn',gradients,vectors).reshape(-1,rows.shape[1])*.01])
    _,singular,vh=np.linalg.svd(rows,full_matrices=True)
    rank=int((singular>singular[0]*1e-9).sum())
    null=vh[rank:].T
    assert null.shape[1]>0,'Boundary constraints leave no free field coefficients'
    return null,rank

def landmark_flow_operator(recipe):
    """Replay a source-bound 3D field; no candidate or source is modified."""
    affine=np.asarray(recipe['affine']);translation=np.asarray(recipe['translation'])
    stages=[(np.asarray(x['centres']),np.asarray(x['sigmaM']),np.asarray(x['coefficients'])) for x in recipe['stages']]
    assert np.linalg.det(affine)>0
    for _,sigma,coefficient in stages:
        assert np.isfinite(sigma).all() and (sigma>0).all() and np.isfinite(coefficient).all()
        assert (np.linalg.norm(coefficient,axis=1)/(np.sqrt(np.e)*sigma)).sum()<1
    def evaluate(points):
        values,jac=landmark_flow_operator(recipe['initialField'])(points) if 'initialField' in recipe else (np.asarray(points)@affine.T+translation,np.tile(affine,(len(points),1,1)))
        for centres,sigma,coefficient in stages:
            delta=values[:,None,:]-centres[None,:,:]
            phi=np.exp(-np.einsum('qci,qci->qc',delta,delta)/(2*sigma**2))
            derivative=-phi[:,:,None]*delta/sigma[None,:,None]**2
            gradient=np.eye(3)+np.einsum('ci,qcj->qij',coefficient,derivative)
            jac=gradient@jac;values+=phi@coefficient
        for field in recipe.get('postFields',[]):
            values,g=regional_shape_operator(field)(values);jac=g@jac
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

def solve_landmark_flow(controls, *, initial_affine=None, initial_translation=None, max_stages=1800, tolerance=1e-8):
    """Shared offline source-bound solve; every accepted 3D increment has ||Du||<1.

    Targets are explicitly authored before this numerical tool. It makes no
    anatomical, topology, surface containment or visual acceptance decision.
    """
    x=np.asarray([c['source'] for c in controls]);target=np.asarray([c['target'] for c in controls]);base_sigma=np.asarray([c['sigmaM'] for c in controls])
    if initial_affine is None:
        affine=np.linalg.lstsq(np.c_[x,np.ones(len(x))],target,rcond=None)[0];a=affine[:3].T;b=affine[3]
    else:a=np.asarray(initial_affine);b=np.asarray(initial_translation)
    assert np.linalg.det(a)>0 and np.isfinite(a).all() and (base_sigma>0).all()
    current=x@a.T+b;stages=[]
    for step in range(max_stages):
        residual=target-current;error=float(np.linalg.norm(residual,axis=1).max())
        if error<tolerance:break
        delta=current[:,None,:]-current[None,:,:]
        nearest=np.sqrt((delta**2).sum(2)+np.eye(len(x))*100).min(1)
        sigma=np.minimum(base_sigma,np.maximum(nearest*.85,base_sigma/(2**(step//250))))
        kernel=np.exp(-(delta**2).sum(2)/(2*sigma[None,:]**2));coefficient=np.linalg.solve(kernel+np.eye(len(kernel))*.001,residual)
        bound=float((np.linalg.norm(coefficient,axis=1)/(np.sqrt(np.e)*sigma)).sum());alpha=min(1.,.30/max(bound,1e-20));coefficient*=alpha
        stages.append({'centres':current.tolist(),'sigmaM':sigma.tolist(),'coefficients':coefficient.tolist(),'globalDisplacementLipschitzBound':alpha*bound});current+=kernel@coefficient
        if step%100==0:print('FLOW',step,'residual',error,flush=True)
    return {'method':'proper initial 3D map + Lipschitz-bounded Gaussian landmark flow','controls':controls,'affine':a.tolist(),'translation':b.tolist(),'stages':stages,'maximumControlResidualM':float(np.linalg.norm(target-current,axis=1).max()),'sourceMeaningNotApprovedBySolver':True}

def regional_shape_operator(field):
    """Analytic bounded local correction; containment aid, not a landmark claim."""
    centre=np.asarray(field['centreM']);sigma=float(field['sigmaM']);assert sigma>0
    if field['kind']=='gaussian_translation':
        shift=np.asarray(field['translationM']);bound=np.linalg.norm(shift)/(np.sqrt(np.e)*sigma)
    else:
        assert field['kind']=='regional_affine';scale=np.asarray(field['linearDisplacement']);lo,hi=field['axialWindowY'];assert hi>lo
        bound=np.max(abs(scale))*(1+2/np.e+1.5/(hi-lo)*sigma/np.sqrt(np.e))
    assert bound<1 and abs(bound-field['globalDisplacementLipschitzBound'])<1e-10
    def evaluate(points):
        p=np.asarray(points);d=p-centre;phi=np.exp(-np.einsum('ij,ij->i',d,d)/(2*sigma*sigma));gradient=-phi[:,None]*d/(sigma*sigma)
        if field['kind']=='gaussian_translation':u=phi[:,None]*shift;du=np.einsum('i,pj->pij',shift,gradient)
        else:
            t=np.clip((p[:,1]-lo)/(hi-lo),0,1);w=t*t*(3-2*t);dw=6*t*(1-t)/(hi-lo);radial=d*scale;factor=w*phi;gf=w[:,None]*gradient;gf[:,1]+=dw*phi
            u=factor[:,None]*radial;du=np.einsum('pi,pj->pij',radial,gf)+factor[:,None,None]*np.diag(scale)[None]
        return p+u,np.eye(3)[None]+du
    return evaluate
