"""Source-addressed ordered toe-section cage authoring and read-only QA for AT10 F1.

Runs only inside the pinned Blender Python with --factory-startup --disable-autoexec.
The cage is derived from source skin section loops and native joint-axis roles. The
section map is geometric registration only; it does not approve skin or landmarks.
"""
from pathlib import Path
import argparse, collections, hashlib, json, math, sys
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

R = Path(__file__).resolve().parents[2]
P = argparse.ArgumentParser()
P.add_argument('--evidence', required=True)
P.add_argument('--mode', choices=['audit'], default='audit')
A = P.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
E = R / A.evidence
BASE = R / 'work/evidence/AT10/2026-10-14-completion-r1'
FIT = R / 'work/evidence/AT10/2026-10-14-skin-fit-r5'
NATIVE_PATH = R / 'work/evidence/AT10/2026-10-13-skin-fit-r1/native-surfaces-r1.json'

def read(path): return json.loads(path.read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def unit(x):
    x=np.asarray(x,dtype=float); n=float(np.linalg.norm(x))
    if not np.isfinite(n) or n<1e-12: raise ValueError('invalid zero/nonfinite frame vector')
    return x/n
def barycentric(p, tri):
    p=np.asarray(p,dtype=float); a,b,c=np.asarray(tri,dtype=float)
    v0=b-a;v1=c-a;v2=p-a
    d00=v0@v0;d01=v0@v1;d11=v1@v1;d20=v2@v0;d21=v2@v1
    den=d00*d11-d01*d01
    if abs(den)<1e-18: return [None,None,None]
    v=(d11*d20-d01*d21)/den;w=(d00*d21-d01*d20)/den
    return [float(1-v-w),float(v),float(w)]
def source_edge_address(tri,bary,original_ids):
    near_zero=[i for i,x in enumerate(bary) if abs(float(x))<1e-7]
    near_one=[i for i,x in enumerate(bary) if abs(float(x)-1)<1e-7]
    if len(near_zero)==1:
        ids=[i for i in range(3) if i not in near_zero];weights=np.asarray([bary[i] for i in ids],dtype=float);weights/=weights.sum()
        return {'kind':'mesh-edge-interpolation','logicalVertices':[int(tri[i]) for i in ids],
                'originalVertexIds':[int(original_ids[int(tri[i])]) for i in ids],
                'edgeWeights':weights.tolist(),'excludedTriangleCorner':near_zero[0]}
    if len(near_one)==1:return {'kind':'original-vertex','logicalVertex':int(tri[near_one[0]]),'originalVertexId':int(original_ids[int(tri[near_one[0]])])}
    return {'kind':'triangle-interior','triangleLogicalVertices':list(map(int,tri)),
            'originalVertexIds':[int(original_ids[int(i)]) for i in tri],
            'triangleBarycentric':list(map(float,bary))}
def segment_triangle_hit(p0,p1,tri,eps=1e-9):
    """Return an inclusive Moller-Trumbore hit for one 3D segment/triangle."""
    p0=np.asarray(p0,dtype=float);d=np.asarray(p1,dtype=float)-p0
    a,b,c=np.asarray(tri,dtype=float);e1=b-a;e2=c-a
    h=np.cross(d,e2);det=float(e1@h)
    if abs(det)<eps:return None
    inv=1.0/det;s=p0-a;u=float((s@h)*inv)
    if u < -eps or u > 1+eps:return None
    q=np.cross(s,e1);v=float((d@q)*inv)
    if v < -eps or u+v > 1+eps:return None
    t=float((e2@q)*inv)
    if t < -eps or t > 1+eps:return None
    return {'pointM':(p0+np.clip(t,0,1)*d).tolist(),'segmentFraction':t,
            'triangleBarycentric':[float(1-u-v),u,v]}
def triangle_triangle_addresses(a,b):
    """Find and deduplicate the exact boundary intersections of two triangles."""
    a=np.asarray(a,dtype=float);b=np.asarray(b,dtype=float);hits=[]
    for tri_from,tri_to,from_label,to_label in [(a,b,'skin','native'),(b,a,'native','skin')]:
        for i,j in [(0,1),(1,2),(2,0)]:
            h=segment_triangle_hit(tri_from[i],tri_from[j],tri_to)
            if h is None:continue
            h[from_label+'Edge']=[i,j];h[from_label+'EdgeFraction']=h.pop('segmentFraction')
            h[to_label+'Barycentric']=h.pop('triangleBarycentric')
            h['pointM']=np.asarray(h['pointM']).tolist();hits.append(h)
    result=[]
    for h in hits:
        if any(np.linalg.norm(np.asarray(h['pointM'])-np.asarray(z['pointM']))<1e-8 for z in result):continue
        # Every crossing point lies on both input triangles. Recompute both
        # addresses at the common point rather than trusting edge arithmetic.
        p=np.asarray(h['pointM'],dtype=float)
        h['skinBarycentric']=barycentric(p,a);h['nativeBarycentric']=barycentric(p,b)
        result.append(h)
    return result
def frame(axis, width):
    longitudinal=unit(axis); transverse=np.asarray(width,dtype=float)-longitudinal*np.dot(width,longitudinal)
    if np.linalg.norm(transverse)<1e-8: transverse=np.array([1.,0.,0.])-longitudinal*longitudinal[0]
    transverse=unit(transverse); dorsal=unit(np.cross(longitudinal,transverse))
    if dorsal[2]<0: transverse=-transverse; dorsal=-dorsal
    F=np.column_stack((longitudinal,transverse,dorsal))
    if np.linalg.det(F)<0.999999: raise ValueError('non-proper local frame')
    return F
def triangulate(faces):
    tris=[]; meta=[]
    for fi,f in enumerate(faces):
        q=f['derivedVertices']
        for j in range(1,len(q)-1):
            tris.append([q[0],q[j],q[j+1]])
            meta.append({'faceIndex':fi,'sourceObjFace':f['sourceFace'],'sourceCorners':[0,j,j+1]})
    return np.asarray(tris,dtype=np.int32),meta
def section_contains_origin(loop,origin,normal,up):
    pts=np.asarray([x['pointM'] for x in loop['nodes']],dtype=float);n=unit(normal);u=np.asarray(up,dtype=float);u=unit(u-n*np.dot(u,n));r=np.cross(u,n)
    q=np.column_stack(((pts-origin)@r,(pts-origin)@u));x=y=0.;inside=False
    for i in range(len(q)):
        x0,y0=q[i];x1,y1=q[(i+1)%len(q)]
        if (y0>y)!=(y1>y) and x<(x1-x0)*(y-y0)/(y1-y0)+x0:inside=not inside
    return inside

def main():
    sys.path.insert(0,str(R/'work/tools'))
    from at10_surface_sections import section_loops, ordered_samples
    candidate=read(E/'frozen-recipes/candidates/fit-r56.json')
    fields=read(FIT/'surface-bands-r52.json')['patches'][0]
    native=read(NATIVE_PATH)
    residual=read(BASE/'right-foot-remaining-r56.json')
    controls={x['id']:x for x in fields['nativeJointControls']}
    source=np.asarray(candidate['sourceVertices'],dtype=float)
    if source.shape!=(13380,3) or not np.isfinite(source).all():
        raise RuntimeError(f'invalid frozen source array shape/finite: {source.shape}; finite={bool(np.isfinite(source).all())}')
    tris,triMeta=triangulate(candidate['faces'])
    mapping=read(R/'atlas-data/anatomy/skin/at10-completion-r1/source-to-derived-r56.json')
    if not np.array_equal(tris,np.asarray(mapping['logicalTriangles'],dtype=np.int32)):
        raise RuntimeError('candidate triangle order does not match emitted r56 GLB mapping')
    patch=set(map(int,fields['sourceVertices']))
    patchTri=np.asarray([i for i,t in enumerate(tris) if all(int(v) in patch for v in t)],dtype=np.int32)
    patchEdgeFaces=collections.defaultdict(list)
    for ti in patchTri:
        t=tris[int(ti)]
        for a,b in [(t[0],t[1]),(t[1],t[2]),(t[2],t[0])]:patchEdgeFaces[tuple(sorted((int(a),int(b))))].append(int(ti))
    outerEdges=[edge for edge,owners in patchEdgeFaces.items() if len(owners)==1]
    outerAdj=collections.defaultdict(list)
    for a,b in outerEdges:outerAdj[a].append(b);outerAdj[b].append(a)
    if not outerAdj or any(len(v)!=2 for v in outerAdj.values()):raise RuntimeError('patch boundary is not a simple degree-two loop')
    boundaryLoop=[];prev=None;cur=min(outerAdj);start=cur
    while cur not in boundaryLoop:
        boundaryLoop.append(cur);nxt=sorted(x for x in outerAdj[cur] if x!=prev)
        if not nxt:raise RuntimeError('open patch boundary loop')
        prev,cur=cur,nxt[0]
    if cur!=start or len(boundaryLoop)!=len(outerAdj):raise RuntimeError('patch has multiple boundary loops or a nonclosing boundary')
    declaredBoundary={int(x['sourceVertex']):np.asarray(x['targetM'],dtype=float) for x in fields['sharedBoundary']}
    if set(boundaryLoop)-set(declaredBoundary):raise RuntimeError('outer source patch boundary escapes declared preserved boundary set')
    boundaryPolicyResidual=max(float(np.linalg.norm(np.asarray(candidate['positions'][i])-declaredBoundary[i])) for i in boundaryLoop)
    if boundaryPolicyResidual>1e-9:raise RuntimeError(f'frozen r56 does not preserve shared source boundary: {boundaryPolicyResidual}')
    toes=[];issues=[];ringCount=32
    lateral=np.asarray(controls['joint-r-toe-5-1']['source'])-np.asarray(controls['joint-r-toe-1-1']['source'])
    lateralTarget=np.asarray(controls['joint-r-toe-5-1']['target'])-np.asarray(controls['joint-r-toe-1-1']['target'])
    for digit in range(1,6):
        chain=[];part=1
        while f'joint-r-toe-{digit}-{part}' in controls:
            chain.append(controls[f'joint-r-toe-{digit}-{part}']);part+=1
        digitRecord={'digit':digit,'handleRole':'AI-authored static-model joint/cap correspondence; not a locating landmark','segments':[]}
        for si,(ca,cb) in enumerate(zip(chain[:-1],chain[1:]),start=1):
            sa=np.asarray(ca.get('sourceOriginalHelperM',ca['source']),dtype=float)
            sb=np.asarray(cb.get('sourceOriginalHelperM',cb['source']),dtype=float)
            ta=np.asarray(ca['target'],dtype=float);tb=np.asarray(cb['target'],dtype=float)
            sf=frame(sb-sa,lateral);tf=frame(tb-ta,lateralTarget)
            segment={'segment':si,'sourceStart':sa.tolist(),'sourceEnd':sb.tolist(),'nativeStart':ta.tolist(),'nativeEnd':tb.tolist(),
                     'sourceFrame':sf.tolist(),'nativeFrame':tf.tolist(),'frameDeterminant':float(np.linalg.det(tf@sf.T)),
                     'sourceLengthM':float(np.linalg.norm(sb-sa)),'nativeLengthM':float(np.linalg.norm(tb-ta)),
                     'nativeAxisRole':{'start':ca['id'],'end':cb['id'],'sourceKeyNames':[x.get('name') for x in ca.get('nativeReferences',[]) + cb.get('nativeReferences',[])],
                                       'sourceKeyCandidates':[k for k,v in native.items() if v.get('side')=='right' and any(x.get('name')==v.get('name') for x in ca.get('nativeReferences',[])+cb.get('nativeReferences',[]))]},
                     'orderedSections':[]}
            axisRaw=sb-sa;axis=unit(axisRaw)
            for station in (.1,.2,.3,.4,.5,.6,.7,.8,.9):
                origin=sa+axisRaw*station
                # The closed source section is recovered from the original
                # topology; the current fit patch boundary is not itself a
                # valid substitute surface and can truncate the contour.
                if not (np.isfinite(origin).all() and np.isfinite(axis).all()):raise RuntimeError(f'nonfinite source section input digit={digit} segment={si} station={station}')
                try:
                    with np.errstate(over='raise',invalid='raise',divide='raise'):
                        loops,open_components=section_loops(source,tris,origin.copy(),axis.copy())
                except FloatingPointError as exc:
                    raise RuntimeError(f'nonfinite/degenerate section operation digit={digit} segment={si} station={station} axis={axis.tolist()} origin={origin.tolist()}') from exc
                chosen=None;chosenDist=None
                options=[]
                for loop in loops:
                    pts=np.asarray([n['pointM'] for n in loop['nodes']]);centroid=pts.mean(0);dist=float(np.linalg.norm(centroid-origin))
                    local=pts-origin;axial=local@axis;radial=np.linalg.norm(local-np.outer(axial,axis),axis=1)
                    perimeter=float(np.linalg.norm(np.diff(np.vstack([pts,pts[0]]),axis=0),axis=1).sum())
                    options.append({'nodeCount':len(loop['nodes']),'centroidM':centroid.tolist(),'centroidDistanceFromNativeAxisM':dist,
                        'perimeterM':perimeter,'radialRangeFromSourceAxisM':[float(radial.min()),float(radial.max())],
                        'sourceOriginalFaceCount':len(set(triMeta[int(x)]['sourceObjFace'] for x in loop['segmentTriangles']))})
                    if chosen is None or dist<chosenDist:chosen=loop;chosenDist=dist
                if chosen is None:
                    segment['orderedSections'].append({'stationFraction':station,'status':'no_closed_source_loop','sourcePlaneOriginM':origin.tolist(),'openComponents':open_components})
                    continue
                samples=ordered_samples(chosen,source,tris,origin.copy(),axis.copy(),[0,0,1],ringCount)
                ordered=[]
                for j,s in enumerate(samples):
                    triIndex=int(s['triangle']);tri=tris[triIndex];meta=triMeta[triIndex]
                    ordered.append({'order':j,'sourceObjFace':meta['sourceObjFace'],'sourceTriangleLogicalVertices':tri.tolist(),
                                    'originalVertexIds':[int(candidate['originalVertexIds'][int(v)]) for v in tri],
                                    'sourceBarycentric':list(map(float,s['barycentric'])),'sourcePointM':s['pointM'],
                                    'insideFitPatchTriangle':bool(all(int(k) in patch for k in tri)),
                                    'overlapsFitPatchTriangle':bool(any(int(k) in patch for k in tri)),
                                    'sourceSurfaceAddress':source_edge_address(tri,s['barycentric'],candidate['originalVertexIds']),
                                    'arcFraction':s['arcFraction']})
                loopPoints=np.asarray([x['sourcePointM'] for x in ordered])
                ringLength=float(np.linalg.norm(np.diff(np.vstack([loopPoints,loopPoints[0]]),axis=0),axis=1).sum())
                segment['orderedSections'].append({'stationFraction':station,'status':'closed_ordered_source_loop','sourcePlaneOriginM':origin.tolist(),
                    'sourceOriginalFaceCount':len(set(x['sourceObjFace'] for x in ordered)),'ringSampleCount':ringCount,'ringLengthM':ringLength,
                    'allClosedLoopOptions':options,
                    'dorsalAnchor':'first sample is source +Z projection maximum; polar winding follows section helper',
                    'surfaceRole':'source geometry section only; dorsal/plantar sides are geometric orientation tags, not new tissue identity',
                    'samples':ordered})
            digitRecord['segments'].append(segment)
        toes.append(digitRecord)

    # A shared whole-foot section family carries heel, arch, metatarsal and web
    # material that has not separated into individual digit contours. Its
    # stations are source geometry sections, not clinical landmarks.
    ankle=controls['joint-r-ankle'];mcp=[controls[f'joint-r-toe-{i}-1'] for i in range(1,6)]
    bodySourceStart=np.mean(source[boundaryLoop],axis=0);bodySourceEnd=np.mean([np.asarray(x['source'],dtype=float) for x in mcp],axis=0)
    bodyTargetStart=np.mean(np.asarray(candidate['positions'],dtype=float)[boundaryLoop],axis=0);bodyTargetEnd=np.mean([np.asarray(x['target'],dtype=float) for x in mcp],axis=0)
    bodyWidth=np.asarray(controls['joint-r-toe-5-1']['source'])-np.asarray(controls['joint-r-toe-1-1']['source'])
    bodyTargetWidth=np.asarray(controls['joint-r-toe-5-1']['target'])-np.asarray(controls['joint-r-toe-1-1']['target'])
    bodyAxisRaw=bodySourceEnd-bodySourceStart;bodyAxis=unit(bodyAxisRaw);bodyTargetAxisRaw=bodyTargetEnd-bodyTargetStart
    bodySourceFrame=frame(bodyAxisRaw,bodyWidth);bodyTargetFrame=frame(bodyTargetAxisRaw,bodyTargetWidth)
    # Resample the actual source-patch topological boundary with an edge
    # barycentric address; its target ring is the preserved r41/r56 ring.
    bpoints=source[boundaryLoop];bu=np.asarray([0,0,1.],dtype=float);bn=bodyAxis;bu=unit(bu-bn*np.dot(bu,bn));br=np.cross(bu,bn)
    bxy=np.column_stack(((bpoints-bodySourceStart)@br,(bpoints-bodySourceStart)@bu));area=float(np.sum(bxy[:,0]*np.roll(bxy[:,1],-1)-bxy[:,1]*np.roll(bxy[:,0],-1)))
    if area<0:boundaryLoop=[boundaryLoop[0]]+boundaryLoop[:0:-1];bpoints=source[boundaryLoop]
    bu=unit(np.asarray([0,0,1.])-bn*np.dot([0,0,1.],bn));br=np.cross(bu,bn)
    upProjection=(bpoints-bodySourceStart)@bu;rot=int(np.argmax(upProjection));boundaryLoop=boundaryLoop[rot:]+boundaryLoop[:rot];bpoints=source[boundaryLoop]
    bedges=[float(np.linalg.norm(bpoints[(i+1)%len(boundaryLoop)]-bpoints[i])) for i in range(len(boundaryLoop))]
    bdist=np.r_[0,np.cumsum(bedges)];bper=float(bdist[-1]);boundarySamples=[]
    for j in range(ringCount):
        at=(j/ringCount)*bper;i=min(int(np.searchsorted(bdist,at,side='right')-1),len(boundaryLoop)-1);q=(at-bdist[i])/max(bedges[i],1e-15)
        va=boundaryLoop[i];vb=boundaryLoop[(i+1)%len(boundaryLoop)];edge=tuple(sorted((va,vb)));faceIndex=patchEdgeFaces[edge][0];tri=tris[faceIndex];wa=1-q;wb=q
        bary=[wa if int(k)==va else wb if int(k)==vb else 0.0 for k in tri]
        meta=triMeta[faceIndex];srcpt=source[va]*wa+source[vb]*wb;targetpt=np.asarray(candidate['positions'])[va]*wa+np.asarray(candidate['positions'])[vb]*wb
        boundarySamples.append({'order':j,'sourceObjFace':meta['sourceObjFace'],'sourceTriangleLogicalVertices':tri.tolist(),
            'originalVertexIds':[int(candidate['originalVertexIds'][int(k)]) for k in tri],'sourceBarycentric':bary,'sourcePointM':srcpt.tolist(),
            'insideFitPatchTriangle':True,'overlapsFitPatchTriangle':True,
            'sourceSurfaceAddress':{'kind':'shared-boundary-original-edge-interpolation','logicalVertices':[va,vb],
                'originalVertexIds':[int(candidate['originalVertexIds'][va]),int(candidate['originalVertexIds'][vb])],
                'edgeWeights':[wa,wb],'sourceObjFace':meta['sourceObjFace']},
            'preservedTargetPointM':targetpt.tolist(),'arcFraction':float(j/ringCount)})
    bodySections=[{'stationFraction':0.0,'status':'closed_ordered_preserved_topological_boundary','sourcePlaneOriginM':bodySourceStart.tolist(),
        'nativePlaneOriginM':bodyTargetStart.tolist(),'ringSampleCount':ringCount,'ringLengthM':bper,
        'sourceBoundaryVertexCount':len(boundaryLoop),'sourceBoundaryOriginalVertexIds':[int(candidate['originalVertexIds'][i]) for i in boundaryLoop],
        'samples':boundarySamples,'role':'exact existing patch boundary; preserved r41/r56 target ring, not inferred as ankle'},]
    bodyOptions=[]
    for station in (.05,.15,.25,.35,.45,.55,.65,.75,.85,.95):
        origin=bodySourceStart+station*bodyAxisRaw
        loops,open_components=section_loops(source,tris,origin.copy(),bodyAxis.copy())
        choices=[]
        for li,loop in enumerate(loops):
            pts=np.asarray([n['pointM'] for n in loop['nodes']],dtype=float);cent=pts.mean(0);per=float(np.linalg.norm(np.diff(np.vstack([pts,pts[0]]),axis=0),axis=1).sum())
            choices.append({'loopIndex':li,'containsSourceBodyAxis':section_contains_origin(loop,origin,bodyAxis,[0,0,1]),
                'centroidM':cent.tolist(),'centroidDistanceM':float(np.linalg.norm(cent-origin)),'perimeterM':per,
                'sourceOriginalFaceCount':len(set(triMeta[int(x)]['sourceObjFace'] for x in loop['segmentTriangles']))})
        # Keep the source contour attached to the intended foot axis even if
        # the authored axis misses the closed contour. The nearest centroid
        # is selected only when the first-vs-second distance margin makes the
        # choice unambiguous; the miss distance remains explicit QA data.
        eligible=sorted([(x,loops[x['loopIndex']]) for x in choices],key=lambda z:(z[0]['centroidDistanceM'],-z[0]['perimeterM']))
        if eligible:
            chosenRecord,chosen=eligible[0]
            secondDistance=eligible[1][0]['centroidDistanceM'] if len(eligible)>1 else None
            margin=(secondDistance-chosenRecord['centroidDistanceM']) if secondDistance is not None else None
            if margin is not None and margin<0.05:
                bodySections.append({'stationFraction':station,'status':'ambiguous_nearest_closed_loop','sourcePlaneOriginM':origin.tolist(),
                    'allClosedLoopOptions':choices,'nearestLoopDistanceMarginM':margin})
                bodyOptions.append({'stationFraction':station,'status':'ambiguous_nearest_closed_loop','allClosedLoopOptions':choices,'openComponents':open_components})
                continue
            samples=ordered_samples(chosen,source,tris,origin.copy(),bodyAxis.copy(),[0,0,1],ringCount)
            ordered=[]
            for j,s in enumerate(samples):
                tri=tris[int(s['triangle'])];meta=triMeta[int(s['triangle'])]
                ordered.append({'order':j,'sourceObjFace':meta['sourceObjFace'],'sourceTriangleLogicalVertices':tri.tolist(),
                    'originalVertexIds':[int(candidate['originalVertexIds'][int(k)]) for k in tri],
                    'sourceBarycentric':list(map(float,s['barycentric'])),'sourcePointM':s['pointM'],
                    'insideFitPatchTriangle':bool(all(int(k) in patch for k in tri)),
                    'overlapsFitPatchTriangle':bool(any(int(k) in patch for k in tri)),
                    'sourceSurfaceAddress':source_edge_address(tri,s['barycentric'],candidate['originalVertexIds']),
                    'arcFraction':s['arcFraction']})
            bodySections.append({'stationFraction':station,'status':'closed_ordered_nearest_main_foot_loop',
                'sourcePlaneOriginM':origin.tolist(),'nativePlaneOriginM':(bodyTargetStart+station*bodyTargetAxisRaw).tolist(),
                'ringSampleCount':ringCount,'ringLengthM':float(np.linalg.norm(np.diff(np.vstack([np.asarray([x['sourcePointM'] for x in ordered]),ordered[0]['sourcePointM']]),axis=0),axis=1).sum()),
                'selectedLoop':chosenRecord,'nearestLoopDistanceMarginM':margin,
                'axisInsideSelectedLoop':chosenRecord['containsSourceBodyAxis'],'samples':ordered,
                'role':'whole-foot source contour across heel/midfoot/metatarsal/MTP-web material; section geometry only, no landmark semantics'})
            bodyOptions.append({'stationFraction':station,'status':'selected_nearest_unambiguous_closed_loop','allClosedLoopOptions':choices,'openComponents':open_components})
        else:
            bodySections.append({'stationFraction':station,'status':'no_closed_loop_contains_source_body_axis','sourcePlaneOriginM':origin.tolist(),
                'openComponents':open_components})
            bodyOptions.append({'stationFraction':station,'status':'no_axis_containing_loop','allClosedLoopOptions':choices,'openComponents':open_components})

    # Restore all r56 residual contacts to exact logical/source/native addresses.
    contactAudit=[];bySourceFace=collections.defaultdict(list)
    for idx,f in enumerate(candidate['faces']): bySourceFace[int(f['sourceFace'])].append(idx)
    for addr in residual['addresses']:
        sourceFace=int(addr['sourceObjFace']);faceIndices=bySourceFace.get(sourceFace,[])
        sourceFaceIdx=faceIndices[0] if faceIndices else None
        skinTriangle=int(addr['skinTriangle']);nativeTriangleIndex=int(addr['nativeTriangle'])
        if skinTriangle<0 or skinTriangle>=len(tris):raise RuntimeError(f'invalid emitted skin triangle {skinTriangle}')
        logicalTri=tris[skinTriangle].astype(int);sourceTri=logicalTri.tolist()
        sourceFaceForTriangle=triMeta[skinTriangle]['sourceObjFace']
        if sourceFaceForTriangle!=sourceFace:raise RuntimeError(f'source face mismatch for emitted triangle {skinTriangle}')
        derivedTri=np.asarray(candidate['positions'],dtype=float)[logicalTri]
        nativeTri=np.asarray(native[addr['sourceKey']]['v'],dtype=float)[np.asarray(native[addr['sourceKey']]['t'],dtype=int)[nativeTriangleIndex]]
        exact=triangle_triangle_addresses(derivedTri,nativeTri)
        for hit in exact:
            sb=np.asarray(hit['skinBarycentric'],dtype=float);nb=np.asarray(hit['nativeBarycentric'],dtype=float)
            sourcePoint=sb@source[logicalTri]
            hit['sourcePointM']=sourcePoint.tolist();hit['sourceBarycentricOnLogicalTriangle']=barycentric(sourcePoint,source[logicalTri])
            hit['sourceOriginalVertexIds']=[int(candidate['originalVertexIds'][int(i)]) for i in logicalTri]
            hit['nativeTriangleVertexIndices']=np.asarray(native[addr['sourceKey']]['t'],dtype=int)[nativeTriangleIndex].tolist()
            hit['interiorOnBothTriangles']=bool(np.min(sb)>1e-7 and np.min(nb)>1e-7)
        key=addr['sourceKey']; nativeTri=np.asarray(native[key]['v'])[np.asarray(native[key]['t'])[int(addr['nativeTriangle'])]]
        contactAudit.append({'skinTriangle':int(addr['skinTriangle']),'sourceObjFace':sourceFace,'sourceFaceIndex':sourceFaceIdx,
            'sourceOriginalVertexIds':[int(candidate['originalVertexIds'][int(i)]) for i in logicalTri],
            'sourceTriangleLogicalVertices':sourceTri,'emittedTriangleOrderVerified':True,
            'nativeSourceKey':key,'nativeName':addr['nativeName'],'nativeSide':addr['nativeSide'],'nativeTriangle':nativeTriangleIndex,
            'exactIntersectionAddressCount':len(exact),'exactIntersectionAddresses':exact,
            'sourceVerticesM':addr['sourceVerticesM'],'r56DerivedVerticesM':addr['derivedVerticesM'],'nativeVerticesM':addr['nativeVerticesM'],
            'sourceQueryMeaning':'r56 collision address, not an acupoint or clinical landmark'})

    # Bind r60/r61 nonpositive samples back to the nearest source triangle.
    r61=read(BASE/'dense-field-r61.json');queryAudit=[]
    bvh=BVHTree.FromPolygons(source.tolist(),[list(map(int,x)) for x in tris.tolist()],all_triangles=True)
    for q in r61['nonPositiveSourceQueries']:
        p=np.asarray(q['sourceM'],dtype=float);hit=bvh.find_nearest(Vector(p.tolist()))
        if hit is None or hit[2] is None: raise RuntimeError('source query could not be addressed')
        ti=int(hit[2]);tri=tris[ti];meta=triMeta[ti]
        queryAudit.append({'queryIndex':q['query'],'sourceQueryM':q['sourceM'],'diagnosticJacobian':q['jacobianDeterminant'],
            'nearestSourceTriangleIndex':ti,'sourceObjFace':meta['sourceObjFace'],'sourceTriangleLogicalVertices':tri.tolist(),
            'sourceOriginalVertexIds':[int(candidate['originalVertexIds'][int(v)]) for v in tri],
            'sourceBarycentric':barycentric(np.asarray(hit[0]),source[tri]),'nearestPointM':list(hit[0]),'distanceM':float(hit[3]),
            'meaning':'source-field failure diagnostic only; not proof of the full r56 cause and not a landmark'})

    exception=read(BASE/'reference-exceptions-right-r1.json')
    fx=exception['facets'][0]
    sourceInput={p:sha(R/p) for p in [
        'atlas-data/source-cache/datasets/skin-source-review-2026-10-13/base.obj',
        'atlas-data/source-cache/datasets/skin-source-review-2026-10-13/makehuman-asian-male-young.target',
        'atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend']}
    out={'schemaVersion':1,'task':'AT10 skin-fit F1 right foot','status':'source_address_audit','source':{'makeHumanRevision':candidate['inputHashes'].get('atlas-data/source-cache/datasets/skin-source-review-2026-10-13/base.obj'),
        'inputHashes':sourceInput,'unit':'m','frame':'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR','sourceObjectFaceAddress':'candidate.faces[].sourceFace; triangulation and original vertex ids retained'},
        'inputs':{'r56CandidateJsonSha256':sha(E/'frozen-recipes/candidates/fit-r56.json'),'r56GlbSha256':sha(R/'atlas-data/anatomy/skin/at10-completion-r1/skin-candidate-r56.glb'),
                  'surfaceBandsR52Sha256':sha(FIT/'surface-bands-r52.json'),'nativeSurfacesSha256':sha(NATIVE_PATH),'authorizationSha256':sha(BASE/'authorization-r1.json'),
                  'referencePolicySha256':sha(BASE/'reference-exceptions-right-r1.json')},
        'nativeReferencePolicy':{'wholeObjects':834,'rawQaRequired':True,'exceptionSourceKey':fx['sourceKey'],'exceptionName':fx['sourceName'],'exceptionSide':fx['side'],
            'exceptionSourceGeometrySha256':fx['geometrySha256'],'exceptionTriangleCount':len(fx['triangleIds']),'retainedTriangles':10875-len(fx['triangleIds']),
            'leftPolicyInferred':False,'sourceChanged':False},
        'rightFootSourcePatch':{'logicalVertices':len(fields['sourceVertices']),'sharedAnkleBoundaryVertices':len(fields['sharedBoundary']),
            'triangles':int(len(patchTri)),'acceptedGeometry':False,'sourceHelpersChanged':False,'topologyPreserved':True,
            'sourceBoundaryLogicalVertices':list(map(int,boundaryLoop)),
            'sourceBoundaryEdges':[{'logicalVertices':[int(boundaryLoop[i]),int(boundaryLoop[(i+1)%len(boundaryLoop)])],
                'originalVertexIds':[int(candidate['originalVertexIds'][boundaryLoop[i]]),int(candidate['originalVertexIds'][boundaryLoop[(i+1)%len(boundaryLoop)]])],
                'sourcePointsM':[source[boundaryLoop[i]].tolist(),source[boundaryLoop[(i+1)%len(boundaryLoop)]].tolist()],
                'preservedTargetPointsM':[np.asarray(candidate['positions'])[boundaryLoop[i]].tolist(),np.asarray(candidate['positions'])[boundaryLoop[(i+1)%len(boundaryLoop)]].tolist()]}
                for i in range(len(boundaryLoop))],
            'declaredSharedControls':[{'logicalVertex':int(i),'originalVertexId':int(candidate['originalVertexIds'][i]),
                'isTopologicalBoundaryVertex':bool(i in set(boundaryLoop)),'sourceM':source[i].tolist(),
                'preservedTargetM':np.asarray(candidate['positions'])[i].tolist()} for i in sorted(declaredBoundary)],
            'ringSamplesInsideFitPatch':sum(1 for d in toes for s in d['segments'] for x in s['orderedSections'] for q in x.get('samples',[]) if q['insideFitPatchTriangle']),
            'ringSamplesOverlappingFitPatch':sum(1 for d in toes for s in d['segments'] for x in s['orderedSections'] for q in x.get('samples',[]) if q['overlapsFitPatchTriangle'])},
        'crossSectionPolicy':{'bodyAxisOrder':['shared-patch-boundary','heel','midfoot/arch','metatarsal/MTP-web','toe-pad/tip'],'wholeFootBodyAxis':{
            'sourceStart':bodySourceStart.tolist(),'sourceEnd':bodySourceEnd.tolist(),'nativeStart':bodyTargetStart.tolist(),'nativeEnd':bodyTargetEnd.tolist(),
            'sourceFrame':bodySourceFrame.tolist(),'nativeFrame':bodyTargetFrame.tolist(),'sectionPolicy':'nearest closed whole-source loop to source body axis, only when first-vs-second centroid-distance margin is at least 50 mm; axis containment and miss distance retained; section geometry only',
            'boundaryInput':{'sourceVertices':len(declaredBoundary),'topologicalBoundaryVertices':len(boundaryLoop),
                'r56ToApprovedBoundaryPositionMaxResidualM':boundaryPolicyResidual,
                'sourceDistanceFromAnkleJointControlRangeM':[min(float(np.linalg.norm(source[i]-ankle['source'])) for i in boundaryLoop),max(float(np.linalg.norm(source[i]-ankle['source'])) for i in boundaryLoop)],
                'identity':'source set labels this shared boundary; its distance from the explicit joint-r-ankle control is retained as a discrepancy, not silently relabeled'},
            'sections':bodySections,'loopOptions':bodyOptions},'digits':toes,'notClinicalLandmarks':True},
        'r56ResidualContactAddressCount':len(contactAudit),'r56ResidualContactTriangleCount':len(set(x['skinTriangle'] for x in contactAudit)),
        'r56ResidualAddresses':contactAudit,'denseFieldDiagnosticAddresses':queryAudit,
        'counts':{'sourceSectionClosed':sum(1 for d in toes for s in d['segments'] for x in s['orderedSections'] if x['status']=='closed_ordered_source_loop'),
                  'sourceSectionMissing':sum(1 for d in toes for s in d['segments'] for x in s['orderedSections'] if x['status']!='closed_ordered_source_loop'),
                  'sourceTopologyTriangles':len(tris),'sourcePatchTriangles':int(len(patchTri)),
                  'wholeFootBodySectionsClosed':sum(1 for x in bodySections if x['status'] in ('closed_ordered_main_foot_axis_loop','closed_ordered_nearest_main_foot_loop')),
                  'wholeFootBodySectionsMissing':sum(1 for x in bodySections if x['status'] not in ('closed_ordered_main_foot_axis_loop','closed_ordered_nearest_main_foot_loop','closed_ordered_preserved_topological_boundary')),
                  'diagnosticQueryCount':len(queryAudit),'r56RawFootSkinTriangles':513,'r56ValidReferenceFootSkinTriangles':21,'r58RawFootSkinTriangles':730,'r58ValidReferenceFootSkinTriangles':228},
        'disclaimer':'Finite ordered sections and mapped cap references are local geometric evidence only; no global injectivity, clinical landmark, learner skin, point placement or whole-skin acceptance.'}
    p=E/'ordered-source-native-cage-audit-r10.json';assert not p.exists(),p
    p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'output':str(p),'sourceSectionClosed':out['counts']['sourceSectionClosed'],'sourceSectionMissing':out['counts']['sourceSectionMissing'],
        'r56ResidualTriangles':out['r56ResidualContactTriangleCount'],'nativeReferences':len(native),'sourceQueryAddresses':len(queryAudit)},ensure_ascii=False),flush=True)

if __name__=='__main__': main()
