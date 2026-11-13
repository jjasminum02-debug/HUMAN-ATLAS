"""Map source-bound right-foot patch vertices through the ordered tetra cage.

This is a gated offline proposal tool. It keeps all declared shared controls
fixed and emits an unaccepted recipe only if patch coverage, interior control
compatibility, and exact contact-address compatibility are all demonstrated.
"""
from pathlib import Path
import argparse,hashlib,json,sys
import numpy as np

R=Path(__file__).resolve().parents[2]
P=argparse.ArgumentParser()
P.add_argument('--evidence',required=True)
P.add_argument('--audit',required=True)
P.add_argument('--cells',required=True)
P.add_argument('--candidate',default='work/evidence/AT10/2026-10-14-f1-right-foot-r1/frozen-recipes/candidates/fit-r56.json')
A=P.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
E=R/A.evidence

def read(p):return json.loads((R/p).read_text())
def closest_triangle_point(p,a,b,c):
    ab=b-a;ac=c-a;ap=p-a;d1=float(ab@ap);d2=float(ac@ap)
    if d1<=0 and d2<=0:return a
    bp=p-b;d3=float(ab@bp);d4=float(ac@bp)
    if d3>=0 and d4<=d3:return b
    vc=d1*d4-d3*d2
    if vc<=0 and d1>=0 and d3<=0:return a+(d1/(d1-d3))*ab
    cp=p-c;d5=float(ab@cp);d6=float(ac@cp)
    if d6>=0 and d5<=d6:return c
    vb=d5*d2-d1*d6
    if vb<=0 and d2>=0 and d6<=0:return a+(d2/(d2-d6))*ac
    va=d3*d6-d5*d4
    if va<=0 and (d4-d3)>=0 and (d5-d6)>=0:return b+((d4-d3)/((d4-d3)+(d5-d6)))*(c-b)
    den=1.0/(va+vb+vc);v=vb*den;w=vc*den
    return a+ab*v+ac*w
def point_tet_distance(p,t):
    q=np.column_stack((t[1]-t[0],t[2]-t[0],t[3]-t[0]))
    b=np.r_[1-np.linalg.solve(q,p-t[0]).sum(),np.linalg.solve(q,p-t[0])]
    if np.all(b>=-1e-10) and np.all(b<=1+1e-10):return 0.0
    dist=min(float(np.linalg.norm(p-closest_triangle_point(p,t[ids[0]],t[ids[1]],t[ids[2]])))
             for ids in ((0,1,2),(0,1,3),(0,2,3),(1,2,3)))
    return dist
def map_point(point,rows,src_tets,dst_tets,invs,lows,highs,eps=1e-7):
    p=np.asarray(point,dtype=float)
    cand=np.flatnonzero(np.all(p>=lows-eps,axis=1)&np.all(p<=highs+eps,axis=1))
    if not len(cand):
        delta=np.maximum(np.maximum(lows-p,0),p-highs);ds=np.linalg.norm(delta,axis=1);idx=int(np.argmin(ds))
        return {'status':'outside_cage_aabb','candidateCells':0,'nearestCellByAabb':idx,
            'nearestCellAabbDistanceM':float(ds[idx]),'mappings':[]}
    q=np.einsum('nij,nj->ni',invs[cand],p-src_tets[cand,0])
    b=np.column_stack((1-q.sum(1),q));ok=np.all(b>=-eps,axis=1)&np.all(b<=1+eps,axis=1)
    ids=cand[ok]
    if not len(ids):
        margins=b.min(axis=1);best=int(np.argmax(margins));cell=int(cand[best])
        d=point_tet_distance(p,src_tets[cell])
        return {'status':'inside_aabb_outside_tets','candidateCells':len(cand),'nearestCellByBarycentricMargin':cell,
            'maximumMinimumBarycentric':float(margins[best]),'nearestTetSurfaceDistanceM':d,'mappings':[]}
    bary=b[ok];mapped=np.einsum('ni,nij->nj',bary,dst_tets[ids]);best=int(np.argmax(bary.min(1)))
    discrepancy=float(np.max(np.linalg.norm(mapped-mapped[best],axis=1))) if len(ids)>1 else 0.
    return {'status':'mapped','candidateCells':len(cand),'containingCells':len(ids),'cellIndices':ids.tolist(),
            'barycentrics':bary.tolist(),'mappedPointsM':mapped.tolist(),'bestCell':int(ids[best]),
            'bestBarycentric':bary[best].tolist(),'bestMappedPointM':mapped[best].tolist(),
            'cellBoundaryDisagreementM':discrepancy,'consistent':discrepancy<=2e-5}

def main():
    audit=read(A.audit);cells=read(A.cells);candidate=read(A.candidate)
    source=np.asarray(candidate['sourceVertices'],dtype=float);base=np.asarray(candidate['positions'],dtype=float)
    bands=read('work/evidence/AT10/2026-10-14-skin-fit-r5/surface-bands-r52.json')['patches'][0]
    patch=sorted(set(map(int,bands['sourceVertices'])))
    sharedTargets={int(x['sourceVertex']):np.asarray(x['targetM'],dtype=float) for x in bands['sharedBoundary']}
    fixedControls=set(sharedTargets)
    topologicalBoundary=set(map(int,audit['rightFootSourcePatch']['sourceBoundaryLogicalVertices']))
    if not fixedControls.issubset(set(patch)) or not topologicalBoundary.issubset(fixedControls):
        raise RuntimeError('shared controls/topological boundary do not match the frozen source patch')
    rows=[x for x in cells['tetrahedralCells'] if x['mapping']=='frameCage']
    st=np.asarray([x['sourceCellVerticesM'] for x in rows],dtype=float);dt=np.asarray([x['targetCellVerticesM'] for x in rows],dtype=float)
    mats=np.asarray([np.column_stack((t[1]-t[0],t[2]-t[0],t[3]-t[0])) for t in st])
    det=np.linalg.det(mats)
    if not np.isfinite(st).all() or not np.isfinite(dt).all() or not np.isfinite(det).all() or np.any(np.abs(det)<1e-15):
        raise RuntimeError('cage contains nonfinite or degenerate source volume cells')
    invs=np.linalg.inv(mats);lows=st.min(axis=1);highs=st.max(axis=1)
    candidatePositions=base.copy();vertexMap=[];fixedControlAddresses=[]
    for vi in sorted(fixedControls):
        result=map_point(source[vi],rows,st,dt,invs,lows,highs)
        predicted=result.get('bestMappedPointM')
        fixedControlAddresses.append({'sourceVertex':vi,'originalVertexId':int(candidate['originalVertexIds'][vi]),
            'isTopologicalBoundaryVertex':vi in topologicalBoundary,'sourceM':source[vi].tolist(),
            'preservedTargetM':sharedTargets[vi].tolist(),'cageAddressStatus':result['status'],
            'cageBestMappedPointM':predicted,'cageBoundaryDisagreementM':result.get('cellBoundaryDisagreementM'),
            'cageVsPreservedTargetM':float(np.linalg.norm(np.asarray(predicted)-sharedTargets[vi])) if predicted is not None else None,
            'addressConsistent':result.get('consistent',False)})
    for vi in patch:
        if vi in fixedControls:
            vertexMap.append({'sourceVertex':vi,'originalVertexId':int(candidate['originalVertexIds'][vi]),
                'status':'preserved_declared_shared_control','isTopologicalBoundaryVertex':vi in topologicalBoundary,
                'sourceM':source[vi].tolist(),'baselineM':base[vi].tolist()})
            continue
        result=map_point(source[vi],rows,st,dt,invs,lows,highs)
        record={'sourceVertex':vi,'originalVertexId':int(candidate['originalVertexIds'][vi]),'sourceM':source[vi].tolist(),**result}
        if result['status']=='mapped' and result['consistent']:
            candidatePositions[vi]=result['bestMappedPointM'];record['baselineR56M']=base[vi].tolist()
            record['displacementFromR56M']=float(np.linalg.norm(candidatePositions[vi]-base[vi]))
        vertexMap.append(record)
    mapped=[x for x in vertexMap if x['status']=='mapped' and x.get('consistent')]
    preserved=[x for x in vertexMap if x['status']=='preserved_declared_shared_control']
    uncovered=[x for x in vertexMap if x['status'] not in ('mapped','preserved_declared_shared_control') or (x['status']=='mapped' and not x.get('consistent'))]
    contactResults=[]
    for addr in audit['r56ResidualAddresses']:
        logical=np.asarray(addr['sourceTriangleLogicalVertices'],dtype=int)
        for hitIndex,h in enumerate(addr['exactIntersectionAddresses']):
            p=np.asarray(h['sourcePointM'],dtype=float);cage=map_point(p,rows,st,dt,invs,lows,highs)
            bary=np.asarray(h['sourceBarycentricOnLogicalTriangle'],dtype=float)
            surfacePoint=bary@candidatePositions[logical]
            cagePoint=np.asarray(cage.get('bestMappedPointM',surfacePoint),dtype=float)
            contactResults.append({'skinTriangle':addr['skinTriangle'],'sourceObjFace':addr['sourceObjFace'],
                'nativeSourceKey':addr['nativeSourceKey'],'nativeTriangle':addr['nativeTriangle'],'intersectionIndex':hitIndex,
                'sourcePointM':p.tolist(),'sourceFaceBarycentric':bary.tolist(),'cageAddressStatus':cage['status'],
                'cageBestCell':cage.get('bestCell'),'mappedSkinSurfacePointM':surfacePoint.tolist(),
                'mappedCagePointM':cagePoint.tolist(),'surfaceVsCageMismatchM':float(np.linalg.norm(surfacePoint-cagePoint)),
                'cageBoundaryDisagreementM':cage.get('cellBoundaryDisagreementM'),
                'nearestTetSurfaceDistanceM':cage.get('nearestTetSurfaceDistanceM'),
                'nearestCellAabbDistanceM':cage.get('nearestCellAabbDistanceM'),
                'maximumMinimumBarycentric':cage.get('maximumMinimumBarycentric'),
                'nearestCellByBarycentricMargin':cage.get('nearestCellByBarycentricMargin'),
                'nearestCellByAabb':cage.get('nearestCellByAabb'),'addressConsistent':cage.get('consistent',False)})
    fixedSummary={'count':len(fixedControlAddresses),
        'topologicalBoundaryCount':sum(x['isTopologicalBoundaryVertex'] for x in fixedControlAddresses),
        'interiorSharedControlCount':sum(not x['isTopologicalBoundaryVertex'] for x in fixedControlAddresses),
        'mappedCount':sum(x['cageAddressStatus']=='mapped' for x in fixedControlAddresses),
        'inconsistentAddressCount':sum(not x['addressConsistent'] for x in fixedControlAddresses),
        'maxCageVsPreservedTargetM':max((x['cageVsPreservedTargetM'] for x in fixedControlAddresses if x['cageVsPreservedTargetM'] is not None),default=None),
        'interiorControlOver20um':sum((not x['isTopologicalBoundaryVertex']) and x['cageVsPreservedTargetM'] is not None and x['cageVsPreservedTargetM']>2e-5 for x in fixedControlAddresses),
        'topologicalBoundaryPositionsPreservedExactly':all(np.array_equal(base[x['sourceVertex']],sharedTargets[x['sourceVertex']]) for x in fixedControlAddresses if x['isTopologicalBoundaryVertex']),
        'addresses':fixedControlAddresses}
    fixedControlGate=(fixedSummary['interiorControlOver20um']==0 and fixedSummary['inconsistentAddressCount']==0)
    contactGate=all(x['cageAddressStatus']=='mapped' and x['addressConsistent'] and x['surfaceVsCageMismatchM']<=2e-5 for x in contactResults)
    counts={}
    for x in vertexMap:counts[x['status']]=counts.get(x['status'],0)+1
    output={'schemaVersion':1,'task':'AT10 skin-fit F1 right foot','status':'cage-coverage-assessment',
        'inputs':{'sectionAudit':A.audit,'volumeCells':A.cells,'baseCandidate':A.candidate,
            'sectionAuditSha256':hashlib.sha256((R/A.audit).read_bytes()).hexdigest(),
            'cellAuditSha256':hashlib.sha256((R/A.cells).read_bytes()).hexdigest(),
            'baseCandidateSha256':hashlib.sha256((R/A.candidate).read_bytes()).hexdigest()},
        'cage':{'method':'piecewise affine tetrahedral section loft from source-face/barycentric ring correspondences to proper native joint frames',
            'sourceTopologyPreserved':True,'cageCellCount':len(rows),'declaredSharedControlCount':len(fixedControls),
            'topologicalPatchBoundaryCount':len(topologicalBoundary),'interiorSharedControlCount':len(fixedControls-topologicalBoundary),
            'sharedControlPolicy':'preserve existing r56 positions exactly; do not relabel interior fixed controls as topological boundary',
            'globalInjectivityProven':False},
        'coverage':{'patchVertices':len(patch),'byStatus':counts,'mappedConsistentVertices':len(mapped),
            'preservedSharedControls':len(preserved),'uncoveredOrAmbiguousCount':len(uncovered),
            'allNonFixedPatchVerticesMapped':not uncovered,
            'maxDisplacementFromR56M':max((x.get('displacementFromR56M',0) for x in mapped),default=0)},
        'sharedControlCageCompatibility':fixedSummary,'mappedVertices':mapped,'uncoveredOrAmbiguousVertices':uncovered,
        'sourcePointContactMapping':{'r56ExactIntersectionPoints':len(contactResults),
            'mappedConsistentlyWithin20um':sum(x['cageAddressStatus']=='mapped' and x['addressConsistent'] and x['surfaceVsCageMismatchM']<=2e-5 for x in contactResults),
            'outsideOrInconsistent':sum(not (x['cageAddressStatus']=='mapped' and x['addressConsistent'] and x['surfaceVsCageMismatchM']<=2e-5) for x in contactResults),
            'maxSurfaceVsCageMismatchM':max((x['surfaceVsCageMismatchM'] for x in contactResults),default=0),
            'addresses':contactResults},
        'candidateEmission':{'attempted':not uncovered and fixedControlGate and contactGate,'accepted':False,
            'learnerEligible':False,'geometryAccepted':False,
            'gateDetails':{'allNonFixedPatchVerticesMapped':not uncovered,'fixedControlsCompatible':fixedControlGate,
                'allExactContactPointsMappedConsistentlyWithin20um':contactGate,'exactContactPointCount':len(contactResults)},
            'note':'No GLB is emitted unless all nonfixed patch vertices, preserved interior shared controls and exact contact addresses are compatible; self, seam, visual and learner QA remain separate gates.'}}
    p=E/'cage-surface-mapping-r6.json';assert not p.exists(),p;p.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    if output['candidateEmission']['attempted']:
        d=dict(candidate);d['positions']=candidatePositions.tolist();d['candidateRevision']='r57';d['fitAcceptancePassed']=False;d['learnerEligible']=False
        d['localFitRecipe']={'revision':'r57','base':'frozen-r56','method':'piecewise-affine ordered-source-section tetrahedral cage mapped through corresponding proper native toe frames',
            'sectionAudit':A.audit,'volumeCellAudit':A.cells,'sourceTopologyPreserved':True,'sourceHelpersChanged':False,
            'sharedControlsPreserved':True,'outsideFootPatchUnchanged':bool(np.array_equal(candidatePositions[~np.isin(np.arange(len(base)),patch)],base[~np.isin(np.arange(len(base)),patch)])),
            'geometryAcceptance':False,'globalInjectivityProven':False,'learnerEligible':False}
        cp=E/'candidates/fit-r57.json';cp.parent.mkdir(parents=True,exist_ok=True);assert not cp.exists(),cp;cp.write_text(json.dumps(d,separators=(',',':'))+'\n')
        output['candidateEmission'].update({'candidateJson':str(cp.relative_to(R)),'sha256':hashlib.sha256(cp.read_bytes()).hexdigest()})
        p.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'output':str(p),'coverage':output['coverage'],
        'sharedControlCageCompatibility':{k:v for k,v in fixedSummary.items() if k!='addresses'},
        'contactMapping':{k:v for k,v in output['sourcePointContactMapping'].items() if k!='addresses'},
        'candidateEmission':output['candidateEmission']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
