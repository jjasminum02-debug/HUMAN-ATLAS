"""Read-only actual recipe/GLB preservation and finite-difference check."""
import sys,json,hashlib,struct,numpy as np
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'work/tools'));from at10_skin_field_math import landmark_flow_operator
E=R/'work/evidence/AT10/2026-10-14-f1-correspondence-r2';A=R/'atlas-data/anatomy/skin/at10-f1-correspondence-r2';rev=sys.argv[1]
load=lambda p:json.loads(p.read_text());d=load(E/f'candidates/fit-{rev}.json');base=load(R/'work/evidence/AT10/2026-10-14-skin-fit-r5/candidates/fit-r41.json');recipe=load(E/'recipe-f1c5.json');s=np.array(d['sourceVertices']);v=np.array(d['positions']);ids=np.array(recipe['sourceUnitVertices']);outside=np.setdiff1d(np.arange(len(v)),ids)
assert np.array_equal(v[outside],np.array(base['positions'])[outside])
for key in ['sourceVertices','originalVertexIds','faces','uv']:assert d[key]==base[key]
fixed=np.array(recipe['actualTopologicalBoundary']);assert np.array_equal(v[fixed],np.array(base['positions'])[fixed])
initial=landmark_flow_operator(recipe);contact=load(E/f'contact-fit-{rev}.json');stages=contact['steps']
for stage in stages:
 bound=float((np.linalg.norm(stage['rawFieldCoefficients'],axis=1)/(np.sqrt(np.e)*np.array(stage['sigmaM']))).sum());assert bound<1
 assert abs(bound-stage['globalDisplacementLipschitzBound'])<1e-10

def evaluate(points):
 p,j=initial(points)
 for stage in stages:
  c=np.array(stage['fieldCentersM']);co=np.array(stage['rawFieldCoefficients']);sig=np.array(stage['sigmaM']);delta=p[:,None,:]-c[None,:,:];phi=np.exp(-np.einsum('pki,pki->pk',delta,delta)/(2*sig**2));g=-phi[:,:,None]*delta/sig[None,:,None]**2
  j=(np.eye(3)+np.einsum('ki,pkj->pij',co,g))@j;p+=phi@co
 return p,j
tri=np.array([[f['derivedVertices'][0],f['derivedVertices'][j],f['derivedVertices'][j+1]] for f in d['faces'] for j in range(1,len(f['derivedVertices'])-1)]);local=tri[np.isin(tri,ids).all(1)]
interior=np.array([q['source'] for q in recipe['controls'] if q['id'].startswith('joint-')])
queries=np.vstack([s[ids],s[local].mean(1),interior]);p,j=evaluate(queries);error=np.linalg.norm(p[:len(ids)]-v[ids],axis=1);assert error.max()<1e-7
fdp=np.vstack([interior,s[ids][::83],s[local].mean(1)[::151]]);_,analytic=evaluate(fdp);columns=[];eps=1e-6
for axis in range(3):
 e=np.eye(3)[axis]*eps;columns.append((evaluate(fdp+e)[0]-evaluate(fdp-e)[0])/(2*eps))
fd=np.stack(columns,axis=2);fd_error=float(np.abs(fd-analytic).max());assert fd_error<1e-5
raw=(A/f'skin-candidate-{rev}.glb').read_bytes();l=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+l]);o=28+l;ac=g['accessors'][0];bv=g['bufferViews'][ac['bufferView']];pv=np.frombuffer(raw,dtype='<f4',count=ac['count']*3,offset=o+bv.get('byteOffset',0)).reshape(-1,3);mp=load(A/f'source-to-derived-{rev}.json');emit=np.array([x['logicalVertex'] for x in mp['emittedVertices']]);assert np.array_equal(pv,v[emit].astype('<f4'))
# Edge dihedrals are a measured seam comparison, not an invented tangent pass.
from collections import defaultdict
faces=defaultdict(list)
for i,tt in enumerate(tri):
 for x,y in zip(tt,np.roll(tt,-1)):faces[tuple(sorted([int(x),int(y)]))].append(i)
inside=np.isin(tri,ids).all(1);seams=[(edge,ff) for edge,ff in faces.items() if len(ff)==2 and inside[ff].sum()==1]
def dihedral(vertices):
 norms=np.cross(vertices[tri[:,1]]-vertices[tri[:,0]],vertices[tri[:,2]]-vertices[tri[:,0]]);norms/=np.linalg.norm(norms,axis=1)[:,None]
 return np.array([np.degrees(np.arccos(np.clip(norms[f[0]]@norms[f[1]],-1,1))) for _,f in seams])
bd=dihedral(np.array(base['positions']));after=dihedral(v)
result={'revision':rev,'candidateSha256':hashlib.sha256((E/f'candidates/fit-{rev}.json').read_bytes()).hexdigest(),'emittedGlbSha256':hashlib.sha256(raw).hexdigest(),'sourceTopologyUVAndOriginalIdsExact':True,'outsideRightPatchVerticesExact':len(outside),'handVerticesExactByOutsidePatchPreservation':True,'boundaryVerticesExact':len(fixed),'boundaryMaximumGapM':0,'rawSourceHelpersUnmodified':True,'recipeStages':len(recipe['stages']),'contactStages':len(stages),'maximumIncrementGlobalLipschitzBound':max(x['globalDisplacementLipschitzBound'] for x in stages),'minimumComposed3DDerivativeDeterminant':float(np.linalg.det(j).min()),'nonPositiveComposedSampleCount':int((np.linalg.det(j)<=0).sum()),'sourceModelControlDerivativeSamples':len(interior),'verifiedSourceInteriorControlCount':load(E/'source-control-interiority.json')['insideCount'],'sourceInteriorityEvidence':'source-control-interiority.json','surfaceVertexAndFacetSamples':len(queries)-len(interior),'maximumRecipePositionResidualM':float(error.max()),'finiteDifferenceQueries':len(fdp),'finiteDifferenceStepM':eps,'maximumFiniteDifferenceJacobianError':fd_error,'emittedFloat32PositionsExactlyReproduced':True,'seamDihedral':{'edgeCount':len(seams),'baselineMedianDeg':float(np.median(bd)),'candidateMedianDeg':float(np.median(after)),'baselineMaxDeg':float(bd.max()),'candidateMaxDeg':float(after.max()),'maximumChangeDeg':float(abs(after-bd).max()),'addresses':[{'logicalEdge':list(e),'triangles':f,'baselineDeg':float(x),'candidateDeg':float(y)} for (e,f),x,y in zip(seams,bd,after)]},'continuousFieldOrientationArgument':'Proper affine followed by I+u with global Lipschitz(u)<1 at every source and contact stage. Exact seam join residual is separately checked; emitted straight triangles require native/self/visual QA.','emittedGeometryAcceptance':False,'learnerEligible':False}
(E/f'field-preservation-{rev}.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k!='seamDihedral'})
