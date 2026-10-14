"""Addressed ordered mesh/plane contours, shared by offline authoring and checking.

Contours retain edge weights and triangle IDs. A geometric section is not an
anatomical landmark; the caller records its body-part/axis evidence separately.
"""
import collections
import numpy as np

def section_loops(vertices, triangles, origin, normal, face_ids=None):
    v=np.asarray(vertices);t=np.asarray(triangles);o=np.asarray(origin);n=np.asarray(normal);n=n/np.linalg.norm(n)
    distances=(v-o)@n;face_ids=np.arange(len(t)) if face_ids is None else np.asarray(face_ids)
    graph=collections.defaultdict(set);nodes={};segments={}
    for fi in face_ids:
        face=t[fi];dd=distances[face]
        if dd.min()>=0 or dd.max()<=0:continue
        cut=[]
        for i,j in [(0,1),(1,2),(2,0)]:
            a,b=int(face[i]),int(face[j])
            if distances[a]*distances[b]>=0:continue
            a,b=sorted((a,b));key=(a,b);u=distances[a]/(distances[a]-distances[b])
            nodes[key]={'edgeVertices':[a,b],'weights':[float(1-u),float(u)],'pointM':(v[a]*(1-u)+v[b]*u).tolist(),'triangle':int(fi)};cut.append(key)
        if len(cut)==2:
            a,b=cut;graph[a].add(b);graph[b].add(a);segments[frozenset([a,b])]=int(fi)
    seen=set();loops=[];open_components=[]
    for seed in sorted(graph):
        if seed in seen:continue
        comp={seed};stack=[seed]
        while stack:
            for k in graph[stack.pop()]:
                if k not in comp:comp.add(k);stack.append(k)
        seen|=comp
        if not all(len(graph[k])==2 for k in comp):
            open_components.append({'nodes':len(comp),'degrees':dict(collections.Counter(len(graph[k]) for k in comp))});continue
        ordered=[];previous=None;current=min(comp)
        while current not in ordered:
            ordered.append(current);nexts=sorted(k for k in graph[current] if k!=previous);previous,current=current,nexts[0]
        if current!=ordered[0] or len(ordered)!=len(comp):continue
        loops.append({'nodes':[nodes[k] for k in ordered],'segmentTriangles':[segments[frozenset([ordered[i],ordered[(i+1)%len(ordered)]])] for i in range(len(ordered))]})
    return loops,open_components

def ordered_samples(loop,vertices,triangles,origin,normal,up,count=20):
    points=np.array([x['pointM'] for x in loop['nodes']]);n=np.asarray(normal,dtype=float);n/=np.linalg.norm(n);u=np.asarray(up,dtype=float);u=u-n*(u@n);u/=np.linalg.norm(u);right=np.cross(u,n)
    # Positive polar winding in the section, beginning at its actual dorsal rim.
    xy=np.column_stack([(points-origin)@right,(points-origin)@u]);area=np.sum(xy[:,0]*np.roll(xy[:,1],-1)-xy[:,1]*np.roll(xy[:,0],-1))
    if area<0:
        loop={'nodes':loop['nodes'][::-1],'segmentTriangles':np.roll(loop['segmentTriangles'][::-1],-1).tolist()};points=points[::-1];xy=xy[::-1]
    start=int(xy[:,1].argmax());nodes=loop['nodes'][start:]+loop['nodes'][:start];faces=loop['segmentTriangles'][start:]+loop['segmentTriangles'][:start];points=np.array([x['pointM'] for x in nodes]);points=np.vstack([points,points[0]])
    lengths=np.linalg.norm(np.diff(points,axis=0),axis=1);distance=np.r_[0,np.cumsum(lengths)];result=[]
    for phase in np.arange(count)/count:
        at=phase*distance[-1];i=min(np.searchsorted(distance,at,side='right')-1,len(nodes)-1);a=nodes[i];b=nodes[(i+1)%len(nodes)];q=(at-distance[i])/max(lengths[i],1e-15);weights={}
        for node,factor in [(a,1-q),(b,q)]:
            for vi,w in zip(node['edgeVertices'],node['weights']):weights[vi]=weights.get(vi,0)+w*factor
        fi=faces[i];tt=triangles[fi];bw=[weights.get(int(k),0) for k in tt]
        assert abs(sum(bw)-1)<1e-6,(fi,weights,tt)
        p=np.array(bw)@vertices[tt]
        result.append({'triangle':int(fi),'barycentric':bw,'pointM':p.tolist(),'arcFraction':float(phase),'ringLengthM':float(distance[-1])})
    return result
