"""Address source-skin samples to the boundary of the positive-volume cage.

The map uses the closest exact source cage face, then extends that owning
tetrahedron's full 3D affine map by the measured off-face vector. It does not
alter the source model or authorize the resulting skin.
"""
from pathlib import Path
import argparse, collections, hashlib, json, math, sys
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

R=Path(__file__).resolve().parents[2]
P=argparse.ArgumentParser()
P.add_argument('--evidence',required=True);P.add_argument('--audit',required=True);P.add_argument('--cells',required=True)
P.add_argument('--candidate',default='work/evidence/AT10/2026-10-14-f1-right-foot-r1/frozen-recipes/candidates/fit-r56.json')
P.add_argument('--max-distance-m',type=float,default=.002)
A=P.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
E=R/A.evidence

def read(p):return json.loads((R/p).read_text())
def barycentric(p,t):
    a,b,c=np.asarray(t,dtype=float);v0=b-a;v1=c-a;v2=np.asarray(p,dtype=float)-a
    d00=float(v0@v0);d01=float(v0@v1);d11=float(v1@v1);d20=float(v2@v0);d21=float(v2@v1)
    den=d00*d11-d01*d01
    if abs(den)<1e-18:return None
    v=(d11*d20-d01*d21)/den;w=(d00*d21-d01*d20)/den
    return np.asarray([1-v-w,v,w],dtype=float)
def main():
    audit=read(A.audit);cells=read(A.cells);candidate=read(A.candidate)
    source=np.asarray(candidate['sourceVertices'],dtype=float);baseline=np.asarray(candidate['positions'],dtype=float)
    bands=read('work/evidence/AT10/2026-10-14-skin-fit-r5/surface-bands-r52.json')['patches'][0]
    patch=sorted(set(map(int,bands['sourceVertices'])))
    shared={int(x['sourceVertex']):np.asarray(x['targetM'],dtype=float) for x in bands['sharedBoundary']}
    topological=set(map(int,audit['rightFootSourcePatch']['sourceBoundaryLogicalVertices']))
    rows=[x for x in cells['tetrahedralCells'] if x['mapping']=='frameCage']
    records={};faceOwners=collections.defaultdict(list)
    for ci,row in enumerate(rows):
        st=np.asarray(row['sourceCellVerticesM'],dtype=float);dt=np.asarray(row['targetCellVerticesM'],dtype=float)
        sm=np.column_stack((st[1]-st[0],st[2]-st[0],st[3]-st[0]));dm=np.column_stack((dt[1]-dt[0],dt[2]-dt[0],dt[3]-dt[0]))
        det=float(np.linalg.det(sm))
        if not np.isfinite(st).all() or not np.isfinite(dt).all() or not math.isfinite(det) or abs(det)<1e-15:raise RuntimeError(f'nonfinite or degenerate source cage cell {ci}')
        J=dm@np.linalg.inv(sm)
        if not np.isfinite(J).all() or float(np.linalg.det(J))<=0:raise RuntimeError(f'nonpositive actual 3D deformation cell {ci}')
        records[ci]={'sourceTet':st,'targetTet':dt,'deformationGradient':J,'jacobian':float(np.linalg.det(J))}
        for omit in range(4):
            ids=[j for j in range(4) if j!=omit];tri=st[ids];key=tuple(sorted(tuple(round(float(v),9) for v in q) for q in tri))
            faceOwners[key].append({'cell':ci,'ids':ids,'source':tri,'target':dt[ids],'deformationGradient':J})
    boundary=[z[0] for z in faceOwners.values() if len(z)==1]
    nonmanifold=sum(len(z)>2 for z in faceOwners.values())
    interiorDuplicate=sum(len(z)==2 for z in faceOwners.values())
    if nonmanifold:raise RuntimeError(f'cage tetra face incidence has {nonmanifold} nonmanifold face(s)')
    coordIndex={};verts=[];polys=[]
    for rec in boundary:
        poly=[]
        for p in rec['source']:
            k=tuple(round(float(v),9) for v in p)
            if k not in coordIndex:coordIndex[k]=len(verts);verts.append(np.asarray(p,dtype=float))
            poly.append(coordIndex[k])
        polys.append(poly)
    tree=BVHTree.FromPolygons([x.tolist() for x in verts],polys,all_triangles=True)
    if tree is None or not len(polys):raise RuntimeError('cage boundary BVH is empty')
    # Stable face-index-to-cell map follows the same insertion order.
    faceRecords=boundary
    def address(p):
        hit=tree.find_nearest(Vector(np.asarray(p,dtype=float).tolist()))
        if hit is None or hit[2] is None:return {'status':'no_nearest_cage_face'}
        q=np.asarray(hit[0],dtype=float);fi=int(hit[2]);rec=faceRecords[fi];bar=barycentric(q,rec['source'])
        if bar is None or not np.isfinite(bar).all():return {'status':'degenerate_nearest_cage_face','cageFace':fi,'distanceM':float(hit[3])}
        J=rec['deformationGradient'];mapped=bar@rec['target']+J@(np.asarray(p,dtype=float)-q)
        return {'status':'mapped' if float(hit[3])<=A.max_distance_m else 'surface_offset_exceeds_limit',
            'cageFace':fi,'ownerCell':rec['cell'],'sourceFaceBarycentric':bar.tolist(),'sourceClosestPointM':q.tolist(),
            'sourceOffsetVectorM':(np.asarray(p)-q).tolist(),'distanceM':float(hit[3]),
            'mappedPointM':mapped.tolist(),'deformationGradient':J.tolist(),'jacobianDeterminant':float(np.linalg.det(J)),
            'actual3DPositiveDerivative':bool(np.isfinite(J).all() and np.linalg.det(J)>0)}
    mappedPositions=baseline.copy();vertexRows=[]
    for vi in patch:
        if vi in shared:
            vertexRows.append({'sourceVertex':vi,'originalVertexId':int(candidate['originalVertexIds'][vi]),
                'status':'preserved_declared_shared_control','isTopologicalBoundaryVertex':vi in topological,
                'sourceM':source[vi].tolist(),'preservedTargetM':shared[vi].tolist(),'baselineM':baseline[vi].tolist()})
            continue
        x=address(source[vi]);x.update({'sourceVertex':vi,'originalVertexId':int(candidate['originalVertexIds'][vi]),'sourceM':source[vi].tolist()})
        if x['status']=='mapped':mappedPositions[vi]=x['mappedPointM'];x['baselineM']=baseline[vi].tolist();x['displacementFromR56M']=float(np.linalg.norm(mappedPositions[vi]-baseline[vi]))
        vertexRows.append(x)
    contactRows=[]
    for addr in audit['r56ResidualAddresses']:
        logical=np.asarray(addr['sourceTriangleLogicalVertices'],dtype=int)
        for hi,h in enumerate(addr['exactIntersectionAddresses']):
            x=address(h['sourcePointM']);bar=np.asarray(h['sourceBarycentricOnLogicalTriangle'],dtype=float)
            surface=bar@mappedPositions[logical]
            x.update({'skinTriangle':addr['skinTriangle'],'sourceObjFace':addr['sourceObjFace'],'nativeSourceKey':addr['nativeSourceKey'],
                'nativeName':addr['nativeName'],'nativeSide':addr['nativeSide'],'nativeTriangle':addr['nativeTriangle'],'intersectionIndex':hi,
                'sourcePointM':h['sourcePointM'],'sourceFaceBarycentric':h['sourceBarycentricOnLogicalTriangle'],
                'mappedSkinSurfacePointM':surface.tolist(),'directCageVsMappedSurfaceM':float(np.linalg.norm(np.asarray(x.get('mappedPointM',surface))-surface))})
            contactRows.append(x)
    counts=collections.Counter(x['status'] for x in vertexRows)
    distances=[x['distanceM'] for x in vertexRows if 'distanceM' in x]
    contactCounts=collections.Counter(x['status'] for x in contactRows)
    contactDistances=[x['distanceM'] for x in contactRows if 'distanceM' in x]
    fixedAddress=[]
    for vi,target in sorted(shared.items()):
        x=address(source[vi]);pred=x.get('mappedPointM')
        fixedAddress.append({'sourceVertex':vi,'originalVertexId':int(candidate['originalVertexIds'][vi]),
            'isTopologicalBoundaryVertex':vi in topological,'sourceM':source[vi].tolist(),'preservedTargetM':target.tolist(),
            'status':x['status'],'distanceM':x.get('distanceM'),'mappedPointM':pred,
            'cageVsPreservedTargetM':float(np.linalg.norm(np.asarray(pred)-target)) if pred is not None else None})
    fixedBad=[x for x in fixedAddress if (not x['isTopologicalBoundaryVertex']) and (x['cageVsPreservedTargetM'] is None or x['cageVsPreservedTargetM']>2e-5)]
    contactMismatch=[x for x in contactRows if x['status']!='mapped' or x['directCageVsMappedSurfaceM']>2e-5]
    unmapped=[x for x in vertexRows if x['status'] not in ('mapped','preserved_declared_shared_control')]
    outsideUnchanged=np.array_equal(mappedPositions[~np.isin(np.arange(len(baseline)),patch)],baseline[~np.isin(np.arange(len(baseline)),patch)])
    ready=not unmapped and not fixedBad and not contactMismatch and outsideUnchanged and np.isfinite(mappedPositions).all()
    output={'schemaVersion':1,'task':'AT10 skin-fit F1 right foot','status':'cage-shell-source-address-assessment',
        'inputs':{'sectionAudit':A.audit,'sectionAuditSha256':hashlib.sha256((R/A.audit).read_bytes()).hexdigest(),
            'volumeCells':A.cells,'volumeCellsSha256':hashlib.sha256((R/A.cells).read_bytes()).hexdigest(),
            'frozenCandidate':A.candidate,'frozenCandidateSha256':hashlib.sha256((R/A.candidate).read_bytes()).hexdigest(),
            'maxSourceSurfaceOffsetM':A.max_distance_m},
        'cageBoundary':{'tetraCellCount':len(rows),'boundaryTriangleCount':len(boundary),'interiorFaceCount':interiorDuplicate,
            'nonmanifoldFaceCount':nonmanifold,'cellJacobianMin':min(x['jacobian'] for x in records.values()),
            'allActual3DCellDerivativesFinitePositive':all(x['jacobian']>0 for x in records.values()),
            'globalInjectivityProven':False,'sourceTopologyModified':False,
            'method':'nearest exact cage boundary face with source-face barycentric address and full owning-tet 3D affine derivative applied to measured off-face vector'},
        'vertexCoverage':{'patchVertexCount':len(patch),'fixedControlCount':len(shared),'topologicalBoundaryCount':len(topological),
            'mappedWithinDistanceLimit':counts['mapped'],'unmappedOrTooFar':len(unmapped),'statusCounts':dict(counts),
            'distanceMinM':min(distances) if distances else None,'distanceMedianM':float(np.median(distances)) if distances else None,
            'distanceP90M':float(np.quantile(distances,.9)) if distances else None,'distanceMaxM':max(distances) if distances else None,
            'allPatchVerticesMappedOrPreserved':not unmapped,'vertices':vertexRows},
        'sharedControls':{'count':len(fixedAddress),'topologicalBoundaryCount':sum(x['isTopologicalBoundaryVertex'] for x in fixedAddress),
            'interiorControlCount':sum(not x['isTopologicalBoundaryVertex'] for x in fixedAddress),'badInteriorControlCount':len(fixedBad),
            'topologicalBoundaryPositionPreservationExact':all(np.array_equal(baseline[x['sourceVertex']],np.asarray(x['preservedTargetM'])) for x in fixedAddress if x['isTopologicalBoundaryVertex']),
            'addresses':fixedAddress},
        'contactAddresses':{'pointCount':len(contactRows),'mappedWithinDistanceLimit':contactCounts['mapped'],
            'statusCounts':dict(contactCounts),'mismatchOver20um':len(contactMismatch),
            'maxDirectCageVsMappedSurfaceM':max((x['directCageVsMappedSurfaceM'] for x in contactRows),default=0),'addresses':contactRows},
        'candidateProposal':{'readyForEmission':ready,'emitted':False,'accepted':False,'learnerEligible':False,
            'outsidePatchPositionsUnchanged':outsideUnchanged,'note':'If emitted by a later exact-source mapping proposal, this JSON is still not acceptance; local self/intersection, seam, natural-shape, GLB, installed-loader and learner-scene gates remain required.'}}
    out=E/'cage-shell-mapping-r1.json';assert not out.exists(),out;out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    if ready:
        d=dict(candidate);d['positions']=mappedPositions.tolist();d['candidateRevision']='r57';d['fitAcceptancePassed']=False;d['learnerEligible']=False
        d['localFitRecipe']={'revision':'r57','base':'frozen-r56','method':output['cageBoundary']['method'],
            'sectionAudit':A.audit,'volumeCellAudit':A.cells,'shellMapAudit':str(out.relative_to(R)),
            'sourceTopologyPreserved':True,'sourceHelpersChanged':False,'sharedControlsPreserved':True,
            'outsideFootPatchUnchanged':outsideUnchanged,'geometryAcceptance':False,'globalInjectivityProven':False,'learnerEligible':False}
        cp=E/'candidates/fit-r57.json';cp.parent.mkdir(parents=True,exist_ok=True);assert not cp.exists(),cp;cp.write_text(json.dumps(d,separators=(',',':'))+'\n')
        output['candidateProposal'].update({'emitted':True,'candidateJson':str(cp.relative_to(R)),'candidateSha256':hashlib.sha256(cp.read_bytes()).hexdigest()})
        out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'output':str(out),'cageBoundary':{k:v for k,v in output['cageBoundary'].items() if k not in ('method',)},
        'vertexCoverage':{k:v for k,v in output['vertexCoverage'].items() if k!='vertices'},
        'sharedControls':{k:v for k,v in output['sharedControls'].items() if k!='addresses'},
        'contactAddresses':{k:v for k,v in output['contactAddresses'].items() if k!='addresses'},
        'candidateProposal':output['candidateProposal']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
