"""Read-only independent replay, seams and native triangle intersection audit."""
from pathlib import Path
from collections import defaultdict,Counter
import argparse,ast,hashlib,json,struct
import numpy as np

R=Path(__file__).resolve().parents[2];A=R/'work/evidence/acupoint-AC1'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--evidence-dir',required=True,help='Workspace-relative evidence directory to audit')
args=parser.parse_args();E=(R/args.evidence_dir).resolve()
assert E.is_relative_to(R/'work/evidence'),'Evidence must remain in work/evidence'
OUT=R/'atlas-data/acupoints/carriers/education-r1'
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
generation=read(E/'generation.json');manifest=read(OUT/'manifest.json');hits=read(E/'native-hits.json')
dataset=read(A/'runtime-dataset.json');rows={r['sourceKey']:r for r in read(A/'runtime-integration.json')['objects']}
cache=R/'atlas-data/source-cache/datasets/za';inputs,meshes={},{}
reader_path=A/'build_carrier.py';tree=ast.parse(reader_path.read_text());reader=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='world')
exec(compile(ast.Module(body=[reader],type_ignores=[]),str(reader_path),'exec'),globals())
# Replay probe inputs independently from the recorded original world geometry.
for item in generation.get('probeGeometryInputs',[]):
    path=R/item['path'];assert sha(path.read_bytes())==item['sha256']
    probe=read(path);assert probe['frame']==dataset['frameContract']['targetFrameId'] and probe['unit']=='m'
    obj=next(o for o in probe['objects'] if o['name']==item['object'])
    v=np.array(obj['positions']);t=np.array(obj['indices'],dtype='<u4')
    if 'triangleIds' in item:t=t[item['triangleIds']]
    meshes[item['key']]=(v,t);rows[item['key']]={'side':item['side'],'names':{'en':item['object']},'bounds':[v.min(axis=0).tolist(),v.max(axis=0).tolist()]}
for path,h in generation['sourceInputs'].items():assert sha((R/path).read_bytes())==h,path
assert sha(reader_path.read_bytes())==generation['readerSha256']
assert sha((R/'work/evidence/AT2/validation.json').read_bytes())==generation['AT2ValidationSha256']
assert sha((OUT/'manifest.json').read_bytes())==generation['manifestSha256']
assert manifest['frameId']==dataset['frameContract']['targetFrameId'] and manifest['unit']==dataset['unit']=='m'
assert manifest['poseId']==dataset['frameContract']['staticReferencePose']['id'] and manifest['datasetRevision']==dataset['revision']
for p,h in generation['unitInputs'].items():assert sha((R/p).read_bytes())==h,p
bounds_checks=[]
for k,g in generation['geometry'].items():
    v,t=world(k)
    if k.startswith('ZA-c7010a9-'):
        u=read(cache/'units'/f'{k}.json');assert u['geometrySpace']=='source_local' and not u['transformAppliedToGeometry']
    actual=np.array([v.min(axis=0),v.max(axis=0)]);catalog=np.array(rows[k]['bounds'])
    assert np.max(np.abs(actual-np.array(g['bounds'])))<1e-9,k
    # Catalog bounds are conservative, not necessarily tight detail-vertex bounds.
    # Check containment and record the difference; replay uses actual detail vertices.
    assert np.all(actual[0]>=catalog[0]-.0001) and np.all(actual[1]<=catalog[1]+.0001),k
    bounds_checks.append({'sourceKey':k,'actualWorldBounds':actual.tolist(),'catalogConservativeBounds':catalog.tolist(),
      'maximumBoundsDifferenceMetres':float(np.abs(actual-catalog).max()),'contained':True})
assert all(generation['sourceInputs'][p]==h for p,h in inputs.items())

decoded={};replay_errors=[];chunk_rows=[]
for c in manifest['chunks']:
    if c['id'] not in generation.get('newChunkIds',[c['id']]):
        assert sha((OUT/c['file']).read_bytes())==c['sha256'];continue
    b=(OUT/c['file']).read_bytes();assert len(b)==c['bytes'] and sha(b)==c['sha256']
    n=c['vertices'];p=np.frombuffer(b,dtype='<f4',count=n*3).reshape(-1,3).copy();ref=np.frombuffer(b,dtype='<f4',count=n*3,offset=n*12).reshape(-1,3).copy()
    idx=np.frombuffer(b,dtype='<u2',offset=n*24).reshape(-1,3).astype('<u4')
    assert sha(p.tobytes()+idx.tobytes())==c['topologySha256']
    assert sha(ref.tobytes()+idx.tobytes())==c['referenceHash']
    assert np.isfinite(p).all() and idx.max()<n and len(idx)==c['triangles'] and len(np.unique(idx))==n
    if c['side']=='right':assert np.all(p[:,0]<0)
    if c['side']=='left':assert np.all(p[:,0]>0)
    assert np.max(np.abs(np.linalg.norm(p-ref,axis=1)-c['clearanceMetres']))<1e-6
    group=c['id'].rsplit('-',1)[0];mapping=generation['chunkSourceGridMappings'][c['id']]
    assert len(mapping)==n
    for i,sample in enumerate(mapping):
        h=hits[group][sample];assert h is not None
        assert c['side']=='midline' or rows[h['sourceKey']]['side']==c['side']
        v,t=world(h['sourceKey']);weights=np.array(h['barycentric']);assert weights.min()>=-1e-9 and abs(weights.sum()-1)<1e-8
        replay_errors.append(float(np.linalg.norm(weights@v[t[h['triangle']]]-ref[i])))
    f=p[idx];norm=np.cross(f[:,1]-f[:,0],f[:,2]-f[:,0]);assert np.linalg.norm(norm,axis=1).min()>1e-8
    edges=Counter(tuple(sorted(e)) for t in idx.tolist() for e in [(t[0],t[1]),(t[1],t[2]),(t[2],t[0])]);assert max(edges.values())==2
    lengths=np.linalg.norm(np.concatenate([f[:,1]-f[:,0],f[:,2]-f[:,1],f[:,0]-f[:,2]]),axis=1);assert lengths.max()<=c.get('maxEdgeMetres',.03)+1e-6
    graph=[set() for _ in p]
    for a,b in edges:graph[a].add(b);graph[b].add(a)
    remaining=set(range(n));components=[]
    while remaining:
        todo=[next(iter(remaining))];seen=set()
        while todo:
            i=todo.pop()
            if i not in seen:seen.add(i);todo.extend(graph[i]-seen)
        remaining-=seen;components.append(len(seen))
    chunk_rows.append({'id':c['id'],'side':c['side'],'vertices':n,'triangles':len(idx),'connectedComponents':len(components),'componentVertices':components,
      'boundaryEdges':sum(n==1 for n in edges.values()),'largestEdgeMetres':float(lengths.max()),'allVerticesReplayed':True})
    decoded[c['id']]=(p,ref,idx)
assert max(replay_errors)<1e-6

seams=[]
for s in generation['seams']:
    a,b=decoded[s['a']][0],decoded[s['b']][0]
    pa=a[np.abs(a[:,1]-s['y'])<1e-6];pb=b[np.abs(b[:,1]-s['y'])<1e-6]
    ka={tuple(p) for p in pa};kb={tuple(p) for p in pb};shared=ka&kb
    assert shared,s
    seams.append({'a':s['a'],'b':s['b'],'sharedPositions':len(shared),'exactPositionAgreement':True,
      'unsharedBoundaryVertices':len(ka^kb),'gapPolicy':'unshared rays remain open, never bridge a rejected face'})

# Stronger check than the compiler's seven radial samples: carrier edges against native
# triangles AND native edges against carrier triangles, across all replayed objects.
keys=list(meshes);native=np.concatenate([meshes[k][0][meshes[k][1]] for k in keys])
source_ids=np.concatenate([np.full(len(meshes[k][1]),i,dtype=np.int32) for i,k in enumerate(keys)])
low=native.min(axis=1);high=native.max(axis=1);cell=.025
bins=defaultdict(list);lo=np.floor(low[:,:2]/cell).astype(int);hi=np.floor(high[:,:2]/cell).astype(int)
for i,(l,h) in enumerate(zip(lo,hi)):
    for x in range(l[0],h[0]+1):
        for y in range(l[1],h[1]+1):bins[(x,y)].append(i)
bins={k:np.array(v,dtype=np.int32) for k,v in bins.items()}
print('native collision triangles',len(native),'bins',len(bins),flush=True)

def segment_hits(origins,directions,triangles):
    # Vectorized Moller-Trumbore for finite segments; endpoints/coplanar tangency excluded.
    e1=triangles[:,1]-triangles[:,0];e2=triangles[:,2]-triangles[:,0]
    pv=np.cross(directions,e2);det=np.einsum('ij,ij->i',e1,pv)
    inv=np.divide(1,det,out=np.zeros_like(det),where=np.abs(det)>1e-12)
    tv=origins-triangles[:,0];u=np.einsum('ij,ij->i',tv,pv)*inv;q=np.cross(tv,e1)
    v=np.einsum('ij,ij->i',directions,q)*inv;d=np.einsum('ij,ij->i',e2,q)*inv
    return (np.abs(det)>1e-12)&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(d>1e-7)&(d<1-1e-7)

collisions=[];pair_count=0
for ident,(p,ref,idx) in decoded.items():
    for face_id,t in enumerate(p[idx]):
        mn=t.min(axis=0);mx=t.max(axis=0);l=np.floor(mn[:2]/cell).astype(int);h=np.floor(mx[:2]/cell).astype(int)
        candidates=[bins[(x,y)] for x in range(l[0],h[0]+1) for y in range(l[1],h[1]+1) if (x,y) in bins]
        if not candidates:continue
        ids=np.unique(np.concatenate(candidates));ids=ids[(low[ids]<=mx+1e-8).all(axis=1)&(high[ids]>=mn-1e-8).all(axis=1)]
        if not len(ids):continue
        others=native[ids];pair_count+=len(ids);mask=np.zeros(len(ids),dtype=bool)
        for a,b in [(0,1),(1,2),(2,0)]:
            mask|=segment_hits(np.broadcast_to(t[a],(len(ids),3)),np.broadcast_to(t[b]-t[a],(len(ids),3)),others)
            mask|=segment_hits(others[:,a],others[:,b]-others[:,a],np.broadcast_to(t,(len(ids),3,3)))
        if mask.any():collisions.append({'chunk':ident,'face':face_id,'sourceKeys':sorted({keys[source_ids[i]] for i in ids[mask]})})
    print(ident,'collisions so far',len(collisions),flush=True)

overview=sum(c['bytes'] for c in dataset['chunks'] if c['level']=='overview' and not c.get('selectionScoped'))+max([0]+[c['bytes'] for c in dataset['chunks'] if c.get('selectionScoped')])
triangles=sum(i['lods']['overview']['triangles'] for i in dataset['instances'])
access=manifest.get('accessManifest');access_bytes=0
if access:
    access_path=OUT/access['file'];assert sha(access_path.read_bytes())==access['sha256'] and access_path.stat().st_size==access['bytes'];access_bytes=access['bytes']
assert overview+manifest['totalBytes']+(OUT/'manifest.json').stat().st_size+access_bytes<=20*1024*1024
assert triangles+manifest['totalTriangles']<=1_000_000
landmarks=[]
landmark_specs=[]
if generation.get('probeGeometryInputs'):
    landmark_specs=[('Frontal bone',None,'head',2,1),('Occipital bone',None,'head',2,-1),('Mandible',None,'head',1,-1)]
    for side in ['right','left']:
        for ord in ['first','second','third','fourth','fifth']:
            landmark_specs += [('Distal phalanx of '+ord+' finger of hand',side,'hand',1,-1),('Distal phalanx of '+ord+' finger of foot',side,'foot',2,1)]
        landmark_specs += [('First metacarpal bone',side,'hand',1,1),('Third metacarpal bone',side,'hand',1,-1),('Calcaneus',side,'foot',2,-1)]
else:
    landmark_specs=[('Body of sternum',None,'trunk',2,1),('Vertebra T7',None,'trunk',2,-1),('Vertebra T12',None,'trunk',2,-1),('Sacrum',None,'trunk',2,-1)]
    for side in ['right','left']:
        landmark_specs += [('Clavicle',side,'arm',0,-1 if side=='right' else 1),('Humerus',side,'arm',1,1),('Humerus',side,'arm',1,-1),('Ulna',side,'arm',1,1),('Radius',side,'arm',1,-1),('Hip bone',side,'trunk',0,-1 if side=='right' else 1),('Femur',side,'leg',1,1),('Patella',side,'leg',2,1),('Tibia',side,'leg',1,1),('Tibia',side,'leg',1,-1)]
for name,side,family,axis,direction in landmark_specs:
    candidates=[k for k,r in rows.items() if r['names']['en']==name and r['side']==side and k in meshes]
    assert len(candidates)==1,(name,side,candidates)
    key=candidates[0];v,t=meshes[key];vertex=int(np.argmax(v[:,axis]*direction));position=v[vertex]
    cs=[c for c in manifest['chunks'] if c['id'] in decoded and c['family']==family and (side is None or c['side'] in [side,'midline'])]
    nearest=[]
    for c in cs:
        p,ref,idx=decoded[c['id']];i=int(np.argmin(np.linalg.norm(ref-position,axis=1)))
        nearest.append((float(np.linalg.norm(ref[i]-position)),c['id'],i,ref[i].tolist()))
    distance,chunk,i,ref=min(nearest)
    landmarks.append({'name':name,'side':side,'nativeSourceKey':key,'nativeVertex':vertex,'worldPosition':position.tolist(),
      'technicalExtremum':{'axis':axis,'direction':direction},'nearestChunk':chunk,'nearestReferenceVertex':i,
      'nearestReferencePosition':ref,'distanceMetres':distance,'extentCheck':'open_boundary_or_gap' if distance>.05 else 'coarse_region_correspondence',
      'grade':'Native structure extrema for region/laterality inspection; not palpation landmarks or acupoint coordinates'})
out={'status':'passed' if not collisions else 'failed_native_intersections','manifestRevision':manifest['revision'],'nativeInputObjects':len(meshes),
  'boundsChecks':bounds_checks,
  'nativeTriangleCount':len(native),'nativeReplayMaxErrorMetres':max(replay_errors),'replayedChunkVertices':len(replay_errors),
  'chunks':chunk_rows,'seams':seams,'landmarks':landmarks,'intersectionCandidatePairs':pair_count,'properTriangleIntersectionCount':len(collisions),'intersections':collisions,
  'collisionLimitations':'Native triangle surfaces only; finite segment tests omit coplanar tangency and closed-volume containment; seven interior radial samples are a separate compiler check',
  'rejectedFaceCount':sum(len(g['rejectedTriangles']) for g in generation['groups']),'missingNativeRayCount':sum(len(g['missingNativeRays']) for g in generation['groups']),
  'cost':{'dataBytes':manifest['totalBytes'],'manifestBytes':(OUT/'manifest.json').stat().st_size,'geometryBufferBytes':manifest['totalGeometryBufferBytes'],'triangles':manifest['totalTriangles'],'drawCalls':len(manifest['chunks']),
    'overviewBytesWithCarrier':overview+manifest['totalBytes']+(OUT/'manifest.json').stat().st_size,'overviewTrianglesWithCarrier':triangles+manifest['totalTriangles'],'thresholdsRaised':False,'accessManifestBytes':access_bytes,'worstCaseOverviewBytesIncludingAccess':overview+manifest['totalBytes']+(OUT/'manifest.json').stat().st_size+access_bytes},
  'skinAccuracy':'unresolved','pointsAuthored':0,'noLeftMirror':True}
(E/'geometry-validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('result',out['status'],'intersections',len(collisions),flush=True)
