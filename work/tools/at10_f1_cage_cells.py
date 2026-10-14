"""Build and inspect ordered source-section tetrahedral cage cells for AT10 F1.

This is an offline investigation aid. A positive cell Jacobian is local evidence
only; it does not prove global injectivity, fit acceptance, or learner readiness.
"""
from pathlib import Path
import argparse, json, math, sys
import numpy as np

R=Path(__file__).resolve().parents[2]
P=argparse.ArgumentParser()
P.add_argument('--evidence',required=True)
P.add_argument('--audit',required=True)
P.add_argument('--candidate',default='work/evidence/AT10/2026-10-14-f1-right-foot-r1/frozen-recipes/candidates/fit-r56.json')
A=P.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
E=R/A.evidence

def read(p):return json.loads((R/p).read_text())
def tet_matrix(t):
    return np.column_stack((t[1]-t[0],t[2]-t[0],t[3]-t[0]))
def tetra_barycentric(p,t):
    m=tet_matrix(t)
    det=float(np.linalg.det(m))
    if abs(det)<1e-15:return None
    q=np.linalg.solve(m,np.asarray(p)-t[0])
    return np.r_[1-q.sum(),q]
def mapped_by_frame(p,source_center,target_center,source_frame,target_frame):
    local=(np.asarray(p)-source_center)@source_frame
    return target_center+local@target_frame.T
def signed2d_area(points,axis,up):
    n=np.asarray(axis,dtype=float);u=np.asarray(up,dtype=float);u=u-n*np.dot(u,n);u/=np.linalg.norm(u);r=np.cross(u,n)
    q=np.column_stack((np.asarray(points)@r,np.asarray(points)@u))
    return float(.5*np.sum(q[:,0]*np.roll(q[:,1],-1)-q[:,1]*np.roll(q[:,0],-1)))
def point_in_polygon_2d(p,points,axis,up):
    n=np.asarray(axis,dtype=float);u=np.asarray(up,dtype=float);u=u-n*np.dot(u,n);u/=np.linalg.norm(u);r=np.cross(u,n)
    q=np.column_stack((np.asarray(points)@r,np.asarray(points)@u));x,y=np.asarray(p)@r,np.asarray(p)@u
    inside=False
    for i in range(len(q)):
        x0,y0=q[i];x1,y1=q[(i+1)%len(q)]
        if (y0>y)!=(y1>y) and x<(x1-x0)*(y-y0)/(y1-y0)+x0:inside=not inside
    return inside

def main():
    audit=read(A.audit);candidate=read(A.candidate);v=np.asarray(candidate['positions'],dtype=float)
    assert len(v)==13380 and np.isfinite(v).all()
    cell_rows=[];all_tets=[];groups=[]
    for digit in audit['crossSectionPolicy']['digits']:
        for segment in digit['segments']:
            sections=sorted(segment['orderedSections'],key=lambda x:x['stationFraction'])
            if not all(s['status']=='closed_ordered_source_loop' for s in sections):
                raise RuntimeError(f"missing source section digit={digit['digit']} segment={segment['segment']}")
            source_frame=np.asarray(segment['sourceFrame'],dtype=float);target_frame=np.asarray(segment['nativeFrame'],dtype=float)
            source_axis=(np.asarray(segment['sourceEnd'])-np.asarray(segment['sourceStart']))
            for low,high in zip(sections[:-1],sections[1:]):
                s0=np.asarray([q['sourcePointM'] for q in low['samples']],dtype=float)
                s1=np.asarray([q['sourcePointM'] for q in high['samples']],dtype=float)
                if len(s0)!=len(s1) or len(s0)<8:raise RuntimeError('section correspondence count mismatch')
                # Reconstruct the existing r56 surface mapping at each exact
                # source triangle/barycentric address.
                d0=np.asarray([np.asarray(q['sourceBarycentric'])@v[np.asarray(q['sourceTriangleLogicalVertices'],dtype=int)] for q in low['samples']])
                d1=np.asarray([np.asarray(q['sourceBarycentric'])@v[np.asarray(q['sourceTriangleLogicalVertices'],dtype=int)] for q in high['samples']])
                # Alternative source-section cage: transfer each ordered ring
                # through its proper source/native joint frames, preserving its
                # measured radial profile rather than pushing skin normals.
                source_centers=[s0.mean(0),s1.mean(0)]
                frac=[low['stationFraction'],high['stationFraction']]
                target_centers=[np.asarray(segment['nativeStart'])+frac[i]*(np.asarray(segment['nativeEnd'])-np.asarray(segment['nativeStart'])) for i in range(2)]
                # The section plane origins share the source joint axis, while
                # cage center nodes use the actual polygon centroid so each
                # triangular fan is checked for containment.
                a0=np.asarray(low['sourcePlaneOriginM']);a1=np.asarray(high['sourcePlaneOriginM'])
                cageTarget=[]
                for pts,origin,tc in [(s0,a0,target_centers[0]),(s1,a1,target_centers[1])]:
                    cageTarget.append(np.asarray([mapped_by_frame(p,origin,tc,source_frame,target_frame) for p in pts]))
                c2=np.asarray(cageTarget)
                cageTargetSource=np.asarray([d0,d1])
                centers={'source':[s0.mean(0),s1.mean(0)],'r56':[d0.mean(0),d1.mean(0)],'frameCage':[c2[0].mean(0),c2[1].mean(0)]}
                centerContainment=[]
                for pts,section,center in [(s0,low,s0.mean(0)),(s1,high,s1.mean(0))]:
                    centerContainment.append(point_in_polygon_2d(center,pts,source_axis,[0,0,1]))
                for method,targetRings in [('r56',cageTargetSource),('frameCage',c2)]:
                    cA,cB=[np.asarray(x) for x in centers[method]]
                    for j in range(len(s0)):
                        jn=(j+1)%len(s0)
                        srcTets=[np.asarray([centers['source'][0],s0[j],s0[jn],centers['source'][1]]),
                                 np.asarray([s0[j],s0[jn],centers['source'][1],s1[j]]),
                                 np.asarray([s0[jn],centers['source'][1],s1[j],s1[jn]])]
                        dstTets=[np.asarray([cA,targetRings[0][j],targetRings[0][jn],cB]),
                                 np.asarray([targetRings[0][j],targetRings[0][jn],cB,targetRings[1][j]]),
                                 np.asarray([targetRings[0][jn],cB,targetRings[1][j],targetRings[1][jn]])]
                        for k,(st,dt) in enumerate(zip(srcTets,dstTets)):
                            sm=tet_matrix(st);dm=tet_matrix(dt);sd=float(np.linalg.det(sm));dd=float(np.linalg.det(dm))
                            if abs(sd)<1e-15:
                                jdet=None;fd='degenerate_source_cell'
                            else:
                                if sd<0:st[[2,3]]=st[[3,2]];dt[[2,3]]=dt[[3,2]];sm=tet_matrix(st);dm=tet_matrix(dt);sd=-sd;dd=float(np.linalg.det(dm))
                                J=dm@np.linalg.inv(sm);jdet=float(np.linalg.det(J));fd='finite'
                            row={'digit':digit['digit'],'segment':segment['segment'],'stations':[low['stationFraction'],high['stationFraction']],
                                 'ringInterval':j,'subtet':k,'mapping':method,'sourceCellSigned6VolumeM3':sd,
                                 'targetCellSigned6VolumeM3':dd,'jacobianDeterminant':jdet,'status':fd,
                                 'sourceCellVerticesM':st.tolist(),'targetCellVerticesM':dt.tolist()}
                            if jdet is not None:
                                # Finite differences of this exact piecewise
                                # affine tetra map at interior barycentric probes.
                                inv=np.linalg.inv(sm);base=st[0];ybase=dt[0];errs=[]
                                for vec in [sm[:,0],sm[:,1],sm[:,2]]:
                                    delta=vec*1e-3;point=base+delta;bar=np.r_[1-np.linalg.solve(sm,point-base).sum(),np.linalg.solve(sm,point-base)]
                                    direct=bar@dt;linear=ybase+J@delta;errs.append(float(np.linalg.norm(direct-linear)))
                                row['finiteDifferenceMaxErrorM']=max(errs)
                            cell_rows.append(row);all_tets.append((digit['digit'],segment['segment'],low['stationFraction'],high['stationFraction'],j,k,st,dt,method))
                groups.append({'digit':digit['digit'],'segment':segment['segment'],'stations':[low['stationFraction'],high['stationFraction']],
                    'sourcePolygonCentroidInsideBothSections':centerContainment,'sourceSectionPerimetersM':[low['ringLengthM'],high['ringLengthM']],
                    'existingR56MappedPerimetersM':[float(np.linalg.norm(np.diff(np.vstack([d0,d0[0]]),axis=0),axis=1).sum()),float(np.linalg.norm(np.diff(np.vstack([d1,d1[0]]),axis=0),axis=1).sum())],
                    'frameCageMappedPerimetersM':[float(np.linalg.norm(np.diff(np.vstack([c2[0],c2[0][0]]),axis=0),axis=1).sum()),float(np.linalg.norm(np.diff(np.vstack([c2[1],c2[1][0]]),axis=0),axis=1).sum())]})
    body=audit['crossSectionPolicy']['wholeFootBodyAxis'];bodySections=sorted([x for x in body['sections'] if x['status'] in ('closed_ordered_main_foot_axis_loop','closed_ordered_nearest_main_foot_loop')],key=lambda x:x['stationFraction'])
    bodySourceFrame=np.asarray(body['sourceFrame'],dtype=float);bodyTargetFrame=np.asarray(body['nativeFrame'],dtype=float)
    for low,high in zip(bodySections[:-1],bodySections[1:]):
        s0=np.asarray([q['sourcePointM'] for q in low['samples']],dtype=float);s1=np.asarray([q['sourcePointM'] for q in high['samples']],dtype=float)
        d0=np.asarray([np.asarray(q['sourceBarycentric'])@v[np.asarray(q['sourceTriangleLogicalVertices'],dtype=int)] for q in low['samples']])
        d1=np.asarray([np.asarray(q['sourceBarycentric'])@v[np.asarray(q['sourceTriangleLogicalVertices'],dtype=int)] for q in high['samples']])
        c0=np.asarray([low['sourcePlaneOriginM'],high['sourcePlaneOriginM']],dtype=float)
        t0=np.asarray([low['nativePlaneOriginM'],high['nativePlaneOriginM']],dtype=float)
        fr0=np.asarray([[mapped_by_frame(p,c0[i],t0[i],bodySourceFrame,bodyTargetFrame) for p in pts] for i,pts in enumerate([s0,s1])])
        # The topological patch boundary is a hard source-bound cage ring. Its
        # target points are the exact preserved r41/r56 positions, not the
        # frame-fit estimate; the frame only interpolates the next layers.
        for i,section in enumerate([low,high]):
            if section.get('status')=='closed_ordered_preserved_topological_boundary':
                fr0[i]=np.asarray([q['preservedTargetPointM'] for q in section['samples']],dtype=float)
        targetCenters={'r56':[d0.mean(0),d1.mean(0)],'frameCage':[fr0[0].mean(0),fr0[1].mean(0)]}
        targets={'r56':[d0,d1],'frameCage':fr0}
        for method in ['r56','frameCage']:
            ca,cb=[np.asarray(x) for x in targetCenters[method]];rr=targets[method]
            for j in range(len(s0)):
                jn=(j+1)%len(s0)
                srcTets=[np.asarray([s0.mean(0),s0[j],s0[jn],s1.mean(0)]),
                         np.asarray([s0[j],s0[jn],s1.mean(0),s1[j]]),
                         np.asarray([s0[jn],s1.mean(0),s1[j],s1[jn]])]
                dstTets=[np.asarray([ca,rr[0][j],rr[0][jn],cb]),
                         np.asarray([rr[0][j],rr[0][jn],cb,rr[1][j]]),
                         np.asarray([rr[0][jn],cb,rr[1][j],rr[1][jn]])]
                for k,(st,dt) in enumerate(zip(srcTets,dstTets)):
                    sm=tet_matrix(st);dm=tet_matrix(dt);sd=float(np.linalg.det(sm));dd=float(np.linalg.det(dm))
                    if abs(sd)<1e-15:jdet=None;fd='degenerate_source_cell'
                    else:
                        if sd<0:st[[2,3]]=st[[3,2]];dt[[2,3]]=dt[[3,2]];sm=tet_matrix(st);dm=tet_matrix(dt);sd=-sd;dd=float(np.linalg.det(dm))
                        J=dm@np.linalg.inv(sm);jdet=float(np.linalg.det(J));fd='finite'
                    row={'digit':0,'segment':'whole-foot-body','stations':[low['stationFraction'],high['stationFraction']],
                        'ringInterval':j,'subtet':k,'mapping':method,'sourceCellSigned6VolumeM3':sd,
                        'targetCellSigned6VolumeM3':dd,'jacobianDeterminant':jdet,'status':fd,
                        'sourceCellVerticesM':st.tolist(),'targetCellVerticesM':dt.tolist()}
                    if jdet is not None:
                        errs=[];base=st[0];ybase=dt[0]
                        for vec in [sm[:,0],sm[:,1],sm[:,2]]:
                            delta=vec*1e-3;q=np.linalg.solve(sm,delta);bar=np.r_[1-q.sum(),q]
                            errs.append(float(np.linalg.norm(bar@dt-(ybase+J@delta))))
                        row['finiteDifferenceMaxErrorM']=max(errs)
                    cell_rows.append(row)
        groups.append({'digit':0,'segment':'whole-foot-body','stations':[low['stationFraction'],high['stationFraction']],
            'sourcePolygonCentroidInsideBothSections':[point_in_polygon_2d(s0.mean(0),s0,bodySourceFrame[:,0],[0,0,1]),point_in_polygon_2d(s1.mean(0),s1,bodySourceFrame[:,0],[0,0,1])],
            'sourceSectionPerimetersM':[low['ringLengthM'],high['ringLengthM']],
            'existingR56MappedPerimetersM':[float(np.linalg.norm(np.diff(np.vstack([d0,d0[0]]),axis=0),axis=1).sum()),float(np.linalg.norm(np.diff(np.vstack([d1,d1[0]]),axis=0),axis=1).sum())],
            'frameCageMappedPerimetersM':[float(np.linalg.norm(np.diff(np.vstack([fr0[0],fr0[0][0]]),axis=0),axis=1).sum()),float(np.linalg.norm(np.diff(np.vstack([fr0[1],fr0[1][0]]),axis=0),axis=1).sum())]})
    by_method={}
    for method in ['r56','frameCage']:
        rows=[x for x in cell_rows if x['mapping']==method]
        vals=[x['jacobianDeterminant'] for x in rows if x['jacobianDeterminant'] is not None]
        by_method[method]={'cellCount':len(rows),'finiteCellCount':len(vals),'degenerateSourceCells':sum(x['status']!='finite' for x in rows),
            'nonPositiveJacobianCells':sum(x['jacobianDeterminant'] is not None and x['jacobianDeterminant']<=0 for x in rows),
            'minimumSampledCellJacobian':min(vals) if vals else None,'maximumSampledCellJacobian':max(vals) if vals else None,
            'maxFiniteDifferenceErrorM':max((x.get('finiteDifferenceMaxErrorM',0) for x in rows),default=None),
            'globalInjectivityProven':False,'naturalShapeApproved':False}
    out={'schemaVersion':1,'task':'AT10 skin-fit F1 right foot','status':'volume-cell-comparison-not-accepted',
        'inputs':{'orderedSectionAudit':A.audit,'candidateRecipe':A.candidate,'candidateSha256':__import__('hashlib').sha256((R/A.candidate).read_bytes()).hexdigest()},
        'cageDefinition':{'surfaceRingSamples':32,'sourceOriginalFaceBarycentricPreserved':True,'tubeCell':'two ordered source sections plus closed ring fan; each triangular prism split into three tetrahedra','nativeFrames':'per digit segment proper frame; section radii retained from source','sourceTopologyModified':False},
        'summaryByMapping':by_method,'sectionGroups':groups,'tetrahedralCells':cell_rows,
        'limitations':['The whole-foot axial section family and per-digit section tube cells do not yet prove the branched MTP/web volume is globally covered.','Positive sampled cell Jacobians do not prove global injectivity.','No candidate GLB or learner acceptance is produced by this inspection tool.']}
    path=E/'volume-cage-cell-audit-r6.json';assert not path.exists(),path
    path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'output':str(path),'summaryByMapping':by_method,'cellCount':len(cell_rows)},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
