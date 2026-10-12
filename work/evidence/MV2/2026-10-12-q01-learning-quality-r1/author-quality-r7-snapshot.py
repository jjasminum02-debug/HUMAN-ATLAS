"""Q01-only source-addressed longitudinal transport, based on immutable original clips.

Retains Q01's corrected distal attachment motion. This is an AI-authored teaching
deformation, not a fibre model, physiological volume law or measured footprint.
"""
from pathlib import Path
import sys,json,copy
import numpy as np
R=Path.cwd();E=Path(__file__).resolve().parent
sys.path[:0]=[str(R/'work/tools'),str(R/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from verify_glb_interpolation import read_glb,channel_data,node_positions,verify
from author_source_surface_motion import array,normals,container,rotation
from author_t66_family_motion import deform
from derive_source_surface_motion import append_bytes,sha
from t66_contact_correctives import bounded_inside,source_topology_contact_patch_corrective
from contact_depth import depth_wrap

def compact(doc,binary):
    """Keep referenced accessors/views byte-for-byte; do not append a repair chain."""
    d=copy.deepcopy(doc);references=[];views=set()
    assert len(d['buffers'])==1 and not d.get('extensionsUsed')
    for mesh in d['meshes']:
        for p in mesh['primitives']:
            references.extend((p['attributes'],k) for k in p['attributes'])
            if 'indices' in p:references.append((p,'indices'))
            for t in p.get('targets',[]):references.extend((t,k) for k in t)
    for a in d.get('animations',[]):
        for s in a['samplers']:references.extend([(s,'input'),(s,'output')])
    for skin in d.get('skins',[]):
        if 'inverseBindMatrices' in skin:references.append((skin,'inverseBindMatrices'))
    used=sorted({o[k] for o,k in references});accessors=[copy.deepcopy(d['accessors'][i]) for i in used];amap={old:new for new,old in enumerate(used)}
    for a in accessors:
        if 'bufferView' in a:views.add(a['bufferView'])
        if 'sparse' in a:
            for k in ['indices','values']:views.add(a['sparse'][k]['bufferView'])
    views.update(image['bufferView'] for image in d.get('images',[]) if 'bufferView' in image)
    output=bytearray();newviews=[];vmap={}
    for old in sorted(views):
        view=copy.deepcopy(d['bufferViews'][old]);assert view['buffer']==0
        offset=view.get('byteOffset',0);data=binary[offset:offset+view['byteLength']];assert len(data)==view['byteLength']
        off,ln=append_bytes(output,data);view.update(buffer=0,byteOffset=off,byteLength=ln);vmap[old]=len(newviews);newviews.append(view)
    for o,k in references:o[k]=amap[o[k]]
    for a in accessors:
        if 'bufferView' in a:a['bufferView']=vmap[a['bufferView']]
        if 'sparse' in a:
            for k in ['indices','values']:a['sparse'][k]['bufferView']=vmap[a['sparse'][k]['bufferView']]
    for image in d.get('images',[]):
        if 'bufferView' in image:image['bufferView']=vmap[image['bufferView']]
    d['accessors']=accessors;d['bufferViews']=newviews;d['buffers']=[{'byteLength':len(output)}]
    return d,output,{'accessorsBefore':len(doc['accessors']),'accessorsAfter':len(accessors),'viewsBefore':len(doc['bufferViews']),'viewsAfter':len(newviews),'binaryBefore':len(binary),'binaryAfter':len(output)}

names={r['sourceKey']:r['name'] for r in json.loads((R/'atlas-data/source-cache/datasets/za/compiled/manifest.json').read_text())['instances']}
inspected={r['side']:r for r in json.loads((E/'native-path-inspection-r1.json').read_text())};results=[]
for side in ['left','right']:
    original=R/f'atlas-data/assets/motion/t66-priority-s05-{side}-knee/motion.glb';raw,old,ob=read_glb(original);tr=channel_data(old,ob)
    prior=json.loads((R/f'work/evidence/MV2/2026-10-12-q01-r1/{side}-candidate-r2/repair-record.json').read_text());assert sha(raw)==prior['originalSha256']
    d=copy.deepcopy(old);buf=bytearray(ob);ni=prior['changedNode'];key=prior['key'];assert d['nodes'][ni]['extras']['sourceKey']==key
    prim=d['meshes'][d['nodes'][ni]['mesh']]['primitives'][0];pos=array(old,ob,prim['attributes']['POSITION']);tri=array(old,ob,prim['indices']).reshape(-1,3);normal=array(old,ob,prim['attributes']['NORMAL']);M=np.array(d['nodes'][ni]['matrix']).reshape(4,4).T;world=node_positions(old,ob,tr,ni,0)
    p=json.loads((R/f'work/evidence/T66/priority-integration-2026-10-05/adopted-knee-{side}/input.json').read_text());fam=p['family'];pivot=np.array(fam['pivotMetres']);axis=np.array(fam['axis']);weights=np.array(prior['weights']);moving=np.array(prior['movingVertexIndices'])
    annotation=inspected[side];origin_ids=annotation['proximalSourceIndices'];origin=world[origin_ids].mean(0);sleeve=annotation['sleeveVertex'];direction=world[sleeve]-origin;length=np.linalg.norm(direction);longitudinal=(world-origin)@direction/length**2
    assert np.allclose(origin,annotation['proximalSourceCentroid'],atol=1e-10)
    # Hold the inspected proximal neck/hip region, not the previous whole-belly mask.
    # .06 of the actual source origin-to-sleeve axis bounds this AI-authored region.
    proximal_limit=.06;fixed=np.flatnonzero(longitudinal<=proximal_limit);assert set(origin_ids)<=set(fixed) and not set(fixed)&set(moving)
    u=np.clip((longitudinal-proximal_limit)/(1-proximal_limit),0,1);distribution=u*u*(3-2*u);distribution[fixed]=0
    stations=[]
    for fraction in np.arange(.12,.8001,.08):
        ids=np.flatnonzero(abs(longitudinal-fraction)<.025);assert len(ids)>=3
        stations.append({'axisFraction':float(fraction),'sourceVertexIndices':ids.tolist(),'restCentroidMetres':world[ids].mean(0).tolist(),'meaning':'native section vertex-centroid, not an anatomical fibre or measured attachment'})
    def put(a,kind='VEC3'):
        off,ln=append_bytes(buf,a.astype('<f4').tobytes());d['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':ln});ai=len(d['accessors']);d['accessors'].append({'bufferView':len(d['bufferViews'])-1,'componentType':5126,'count':len(a),'type':kind,'min':a.min(0).tolist(),'max':a.max(0).tolist()});return ai
    _,accepted,ab=read_glb(R/f'atlas-data/assets/motion/mv2-q01-r1-{side}/motion.glb');assert sha((R/f'atlas-data/assets/motion/mv2-q01-r1-{side}/motion.glb').read_bytes())==prior['candidateSha256'];at=channel_data(accepted,ab)
    samples=24;frames=[world];corrections=[np.zeros_like(world)]
    for step in range(1,samples+1):
        phase=step/samples;previous=node_positions(accepted,ab,at,ni,phase*3);sleeve_delta=previous[sleeve]-world[sleeve]
        # Bounded distal excursion distributed along native material coordinates.
        # Distal fully-moving pins follow their exact prior path; the proximal neck stays fixed.
        frames.append(node_positions(accepted,ab,at,ni,phase*3));corrections.append((1-weights)[:,None]*distribution[:,None]*sleeve_delta)
    alpha=np.ones(len(world));contact_limit={'method':'existing source-surface nearest projection plus weighted graph corrective smoothing','numericalMarginMetres':.00015,'keyframes':[]};neighbors=[]
    for n,node in enumerate(accepted['nodes']):
        name=names.get(node.get('extras',{}).get('sourceKey'),'')
        if name.startswith('Vastus') or node.get('extras',{}).get('sourceKey') in prior['fixedBoneKeys']+prior['movingBoneKeys']:
            primitive=accepted['meshes'][node['mesh']]['primitives'][0];neighbors.append((n,node['extras']['sourceKey'],array(accepted,ab,primitive['indices']).reshape(-1,3),name.startswith('Vastus')))
    prim['targets']=[]
    for step in range(1,samples+1):
        previous=frames[step];frame=previous+corrections[step]
        contacts=[];patch_contacts=[]
        for n,ck,ct,same_pose in neighbors:
            context=node_positions(accepted,ab,at,n,3*step/samples);reference=previous if same_pose else world
            reference_context=context if same_pose else node_positions(accepted,ab,at,n,0)
            contacts.append((ck,context,ct,reference,reference_context))
            patch_contacts.append((ck,context,ct,bounded_inside(reference,reference_context,ct)))
        frame,corrective=depth_wrap(frame,world,tri,contacts,set(fixed)|set(moving));contact_limit['keyframes'].append({'seconds':3*step/samples,**corrective})
        source_tri=world[tri];sn=np.cross(source_tri[:,1]-source_tri[:,0],source_tri[:,2]-source_tri[:,0]);sa=np.linalg.norm(sn,axis=1);posed=frame[tri];pn=np.cross(posed[:,1]-posed[:,0],posed[:,2]-posed[:,0]);bad=np.flatnonzero((sa>1e-12)&(((sn*pn).sum(1)<0)|(np.linalg.norm(pn,axis=1)<sa*.3)))
        if len(bad):
            frame,shape=source_topology_contact_patch_corrective(frame,world,tri,patch_contacts,set(fixed)|set(moving),[],shape_seed_vertices=np.unique(tri[bad]).tolist(),shape_floor=.3,margin_metres=.00015)
            contact_limit['keyframes'][-1]['sourceTopologyShapePatch']=shape
        frame[fixed]=world[fixed];frame[moving]=previous[moving]
        local=(frame-M[:3,3])@np.linalg.inv(M[:3,:3]).T;local[fixed]=pos[fixed]
        # A fully limited vertex retains the exact accepted local morph stream.
        accepted_prim=accepted['meshes'][accepted['nodes'][ni]['mesh']]['primitives'][0]
        delta=local-pos
        prim['targets'].append({'POSITION':put(delta),'NORMAL':put(normals(pos+delta,tri)-normal)})
    d['meshes'][d['nodes'][ni]['mesh']]['weights']=[0]*samples;d['nodes'][ni]['weights']=[0]*samples
    time_values=np.linspace(0,3,samples+1,dtype='<f4');weight_values=np.zeros((samples+1,samples),dtype='<f4')
    for step in range(1,samples+1):weight_values[step,step-1]=1
    for animation in d['animations']:
        for channel in animation['channels']:
            if channel['target']=={'node':ni,'path':'weights'}:
                sampler=animation['samplers'][channel['sampler']];sampler.update(input=put(time_values[:,None],'SCALAR'),output=put(weight_values.reshape(-1,1),'SCALAR'))
    destination=E/(side+'-candidate-r7');assert not destination.exists();destination.mkdir();uncompact=container(d,buf);(destination/'uncompact.glb').write_bytes(uncompact)
    packed,pb,cost=compact(d,buf);final=container(packed,pb);(destination/'motion.glb').write_bytes(final);_,nd,nb=read_glb(destination/'motion.glb');nt=channel_data(nd,nb)
    # Every surface and intermediate pose must remain equivalent after stream compaction.
    err=0;other_error=0;fixed_error=0;moving_error=0;metrics=[]
    unpacked_tracks=channel_data(d,buf)
    for time in np.linspace(0,3,samples*8+1):
        for n in range(len(nd['nodes'])):
            if 'mesh' not in nd['nodes'][n]:continue
            before=node_positions(d,buf,unpacked_tracks,n,time);after=node_positions(nd,nb,nt,n,time);err=max(err,float(np.linalg.norm(before-after,axis=1).max()))
            if n!=ni:other_error=max(other_error,float(np.linalg.norm(node_positions(old,ob,tr,n,time)-after,axis=1).max()))
        v=node_positions(nd,nb,nt,ni,time);oldrepair=deform(world,pivot,axis,fam['endDegrees'],time/3,weights,'fractional_rotation')
        fixed_error=max(fixed_error,float(np.linalg.norm(v[fixed]-world[fixed],axis=1).max()))
        # Compare moving pins to the actual original LINEAR one-hot interpolation.
        k=min(11,int(time/.25));alpha=(time-k*.25)/.25
        expected=(1-alpha)*deform(world,pivot,axis,fam['endDegrees'],k/12,weights,'fractional_rotation')+alpha*deform(world,pivot,axis,fam['endDegrees'],(k+1)/12,weights,'fractional_rotation')
        moving_error=max(moving_error,float(np.linalg.norm(v[moving]-expected[moving],axis=1).max()))
        centers=np.array([v[s['sourceVertexIndices']].mean(0) for s in stations]);path_length=float(np.linalg.norm(np.diff(centers,axis=0),axis=1).sum())
        body=np.flatnonzero((longitudinal>=.12)&(longitudinal<=.8));metrics.append({'seconds':float(time),'mainBellySectionCentroidPathMm':path_length*1000,'bodyMaxDisplacementMm':float(np.linalg.norm(v[body]-world[body],axis=1).max()*1000),'maxAnteriorMm':float((v[:,2]-world[:,2]).max()*1000)})
    assert err==0 and other_error==0 and fixed_error<1e-8 and moving_error<1e-7
    checks={}
    for ck in prior['fixedBoneKeys']+prior['movingBoneKeys']:
        qc=verify(destination/'motion.glb',key,[ck],subdivisions=8);checks[names[ck]]=qc;(destination/('qc-'+names[ck].replace(' ','-')+'.json')).write_text(json.dumps(qc,indent=2)+'\n')
    record={'side':side,'sourceKey':key,'originalUri':str(original.relative_to(R)),'originalSha256':sha(raw),'priorAcceptedSha256':prior['candidateSha256'],'sha256':sha(final),'bytes':len(final),'uncompactBytes':len(uncompact),'compaction':cost,'changedNode':ni,'sourceMatrix':d['nodes'][ni]['matrix'],'frameId':fam['frameId'],'poseId':fam['referencePoseId'],'unit':'m','angleDegrees':fam['endDegrees'],'durationSeconds':3,'interpolation':'LINEAR one-hot adjacent morphs','actionDirection':'reverse','sourceOriginIndices':origin_ids,'sourceSleeveVertex':sleeve,'sourceTaperVertex':annotation['taperVertex'],'proximalRegionAxisFraction':proximal_limit,'fixedVertexIndices':fixed.tolist(),'movingVertexIndices':moving.tolist(),'sourceSections':stations,'method':'prior corrected distal fractional rotation plus smooth material-axis distribution of source sleeve excursion; no radial inflation/scale/color/rigid substitute','compactReplayMaxMetres':err,'other70NodesMaxChangeMetres':other_error,'proximalFixedErrorMetres':fixed_error,'distalMovingPathErrorMetres':moving_error,'metrics':metrics,'checks':{k:{'passed':v['passed'],'flips':v['geometry']['flippedFaceSamples'],'minArea':v['geometry']['minimumAreaRatio'],'maxEdgeDelta':v['geometry']['maximumAbsoluteEdgeRatioDelta'],'newContactMax':v['contact']['newContainmentMaximum']} for k,v in checks.items()},'rights':p['rights'],'author':'ai','measuredAttachmentFootprints':False,'physiologicalCertification':False,'volumeClaim':False}
    record['contactLimitedTransport']=contact_limit;record['morphSamples']=samples;record['denseTimes']=samples*8+1;record['method']+='; added free transport wrapped against accepted same-pose vastus vertex containment, numerical clearance only'
    (destination/'record.json').write_text(json.dumps(record,indent=2)+'\n');results.append({k:v for k,v in record.items() if k not in ['fixedVertexIndices','movingVertexIndices','sourceSections','metrics','transportFactors']});print(side,record['checks'],metrics[-1],cost,contact_limit,flush=True)
(E/'candidate-summary-r7.json').write_text(json.dumps(results,indent=2)+'\n')
