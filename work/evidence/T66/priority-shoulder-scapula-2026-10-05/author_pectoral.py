"""Repair source-specific broad pectoral deformation, preserving unrelated verified tracks.

The reverse leg demonstrates adduction from a bounded abducted preparation.
All values are authored educational engineering, not measured physiology.
"""
import pathlib,sys,json,copy,numpy as np
R=pathlib.Path(__file__).resolve().parents[4];O=pathlib.Path(__file__).parent
sys.path[:0]=[str(R/'work/tools'),str(R/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from author_source_surface_motion import source_geometry,array,normals,container
from derive_source_surface_motion import accessor_bytes,append_bytes,geometry_hash,sha
from verify_glb_interpolation import read_glb,channel_data,node_positions,bounded_inside,verify,qmatrix,sample
from t66_contact_correctives import source_bone_projection_corrective,source_topology_contact_patch_corrective
load=lambda p:json.loads((R/p).read_text())
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');return str(p.relative_to(R))
b=load('atlas-data/motion/motion-learning.json');reg=load('atlas-data/motion/authoring/registry.json');scenes=load('atlas-data/motion/motion-scenes.json');man=load('atlas-data/source-cache/datasets/za/compiled/manifest.json');src={r['sourceKey']:r for r in man['instances']}
for side in ['left','right']:
 family='shoulder-abduction-'+side;dest=O/('pectoral-'+side);dest.mkdir(exist_ok=True)
 a=copy.deepcopy(next(a for a in b['motionAssets'] if a.get('sourceBinding',{}).get('sourceFamilyId')==family));arp=next(r['path'] for r in reversed(reg['records']) if load(r['path']).get('sourceFamilyId')==family);ar=load(arp);gp=ar['geometryRecordPath'];geo=load(gp);pose=load(ar['glbPoseQcPath']);ip=next(d['path'] for d in ar['verificationDependencies'] if d['path'].endswith('/input.json'));payload=load(ip)
 ep=next(r['path'] for r in reversed(reg['records']) if load(r['path']).get('sourceFamilyId')=='shoulder-girdle-elevation-'+side);ea=load(ep);eip=next(d['path'] for d in ea['verificationDependencies'] if d['path'].endswith('/input.json'));elevation=load(eip)
 oldraw,old,oldbin=read_glb(R/a['uri']);oldtracks=channel_data(old,oldbin);doc=copy.deepcopy(old);buf=bytearray(oldbin);oldcount=len(doc['nodes']);members=copy.deepcopy(a['sourceBinding']['members']);keyset={m['sourceKey'] for m in members};newentries=[]
 scene=next(s for s in scenes['sceneManifests'] if s['id']==a['staticBinding']['sceneId']);refr,ref,refbin=read_glb(R/scene['assetUri']);ref=copy.deepcopy(ref);refbuf=bytearray(refbin)
 def put(document,buffer,raw,typ,count,component=5126):
  off,length=append_bytes(buffer,raw);vi=len(document['bufferViews']);document['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':length});ai=len(document['accessors']);document['accessors'].append({'bufferView':vi,'componentType':component,'count':int(count),'type':typ});return ai
 def append_fixed(document,buffer,key):
  row=src[key];sd,sb,sp,pos,tri,M,w=source_geometry(row,'overview');attrs={}
  for semantic,ai in sp['attributes'].items():
   _,_,count,normalized,raw=accessor_bytes(sd,sb,ai);sa=sd['accessors'][ai];new=put(document,buffer,raw,sa['type'],count,sa['componentType']);attrs[semantic]=new
   if normalized:document['accessors'][new]['normalized']=True
   if semantic=='POSITION':document['accessors'][new].update(min=pos.min(0).tolist(),max=pos.max(0).tolist())
  _,_,count,_,raw=accessor_bytes(sd,sb,sp['indices']);ni=len(document['nodes']);node={'name':'surface_'+str(ni),'mesh':len(document['meshes']),'matrix':row['matrix'],'extras':{'sourceKey':key}};mesh={'name':row['lods']['overview']['resource'],'primitives':[{'attributes':attrs,'indices':put(document,buffer,raw,'SCALAR',count,sd['accessors'][sp['indices']]['componentType']),'mode':4}]}
  document['nodes'].append(node);document['meshes'].append(mesh);document['scenes'][0]['nodes'].append(ni)
  return {'sourceKey':key,'nodeId':node['name'],'sourceNamespace':man['namespace'],'role':'passive_context','side':row['sourceLabelSide'],'resourceKey':row['lods']['overview']['resource'],'lod':'overview','sourceChunkSha256':row['lods']['overview']['chunk'],'geometrySha256':geometry_hash(sd,sb,0)[0],'instanceMatrix':row['matrix']}
 # Use already typed roles rather than inferring a structure kind from its name.
 typed={r['sourceKey']:r for r in load('atlas-data/overlays/za-local-integration.json')['objects']}
 for e in elevation['members']:
  key=e['sourceKey']
  if key in keyset:continue
  m=append_fixed(doc,buf,key);append_fixed(ref,refbuf,key);m['role']='fixed_structure' if typed[key]['kind']=='bone' else 'passive_context';members.append(m);newentries.append({'sourceKey':key,'lod':'overview','role':m['role']});keyset.add(key)
 nodes={n['extras']['sourceKey']:i for i,n in enumerate(doc['nodes'])};entries={e['sourceKey']:copy.deepcopy(e) for e in payload['members']};bones=[m['sourceKey'] for m in members if m['role'] in ['fixed_structure','moving_structure']];newtargets=[m['sourceKey'] for m in members if any(x in src[m['sourceKey']]['name'] for x in ['Abdominal part of pectoralis major','Sternocostal head of pectoralis major'])]
 stationary=[key for key in nodes if any(n in src[key]['name'] for n in ['Longissimus capitis','Splenius capitis'])]
 for key in stationary:
  ni=nodes[key];node=doc['nodes'][ni];mi=node['mesh'];name=node['name'];node.clear();node.update(name=name,mesh=mi,matrix=src[key]['matrix'],extras={'sourceKey':key});doc['animations'][0]['channels']=[c for c in doc['animations'][0]['channels'] if c['target']['node']!=ni];next(m for m in members if m['sourceKey']==key)['role']='passive_context';entries[key]['role']='passive_context'
 changed=[]; authored=[];times=np.linspace(0,a['clip']['durationSeconds'],17);timea=put(doc,buf,times.astype('<f4').tobytes(),'SCALAR',len(times));doc['accessors'][timea].update(min=[0],max=[float(times[-1])])
 for key in newtargets:
  e=copy.deepcopy(next(e for e in elevation['members'] if e['sourceKey']==key));e['role']='deforming_passive_surface';entries[key]=e;ni=nodes[key];node=doc['nodes'][ni];meshindex=node['mesh'];assert meshindex==ni;node.clear();node.update(name=members[ni]['nodeId'],mesh=meshindex,matrix=src[key]['matrix'],extras={'sourceKey':key});prim=doc['meshes'][ni]['primitives'][0];prim['targets']=[];sd,sb,sp,pos,tri,M,world=source_geometry(src[key],'overview');baseN=normals(pos,tri);weights=np.array(next(r['authoredFinalWeights'] for r in load(ea['geometryRecordPath'])['surfaceMetrics'] if r['sourceKey']==key));f=e['fixedVertexIndices'];v=e['movingVertexIndices'];humerus=e['movingBoneKeys'][0];hn=nodes[humerus];restH=node_positions(doc,bytes(buf),channel_data(doc,bytes(buf)),hn,0);hM=np.array(src[humerus]['matrix']).reshape(4,4).T
  # Relax source-specific taper weights while preserving authored attachment masks.
  base=world[tri];bn=np.cross(base[:,1]-base[:,0],base[:,2]-base[:,0]);locked=set(f)|set(v);repairs=[]
  for iteration in range(128):
   bad=set()
   for t in times[1:]:
    tr=channel_data(doc,bytes(buf));hnod=doc['nodes'][hn];T=np.eye(4);T[:3,:3]=qmatrix(sample(tr[(hn,'rotation')],float(t),'rotation'))@np.diag(hnod['scale']);T[:3,3]=sample(tr[(hn,'translation')],float(t),'translation');T=T@np.linalg.inv(hM);rigid=world@T[:3,:3].T+T[:3,3];trial=world+weights[:,None]*(rigid-world);trial[f]=world[f];trial[v]=rigid[v];ft=trial[tri];fn=np.cross(ft[:,1]-ft[:,0],ft[:,2]-ft[:,0]);bad.update(np.flatnonzero((bn*fn).sum(1)<0).tolist())
   if not bad:break
   for ti in sorted(bad):
    vertices=tri[ti];pins=[int(vv) for vv in vertices if int(vv) in locked];value=float(np.mean(weights[pins if pins else vertices]));print('weight repair',key,ti,vertices.tolist(),pins,value,flush=True)
    for vv in vertices:
     if int(vv) not in locked:weights[vv]=value
   repairs.append({'iteration':iteration,'triangleIds':sorted(bad)})
  e['weights']=weights.tolist();e['shapeWeightRepairs']=repairs
  contacts=[]
  for bone in bones:
   if bone==key:continue
   bw=node_positions(doc,bytes(buf),channel_data(doc,bytes(buf)),nodes[bone],0)
   if any(world.max(0)[j]<bw.min(0)[j]-.025 or world.min(0)[j]>bw.max(0)[j]+.025 for j in range(3)):continue
   bp=doc['meshes'][doc['nodes'][nodes[bone]]['mesh']]['primitives'][0];bt=array(doc,bytes(buf),bp['indices']).reshape(-1,3);contacts.append((bone,bt,bounded_inside(world,bw,bt)))
  corrections=[]
  for t in times[1:]:
   tr=channel_data(doc,bytes(buf));hnode=doc['nodes'][hn];T=np.eye(4);T[:3,:3]=qmatrix(sample(tr[(hn,'rotation')],float(t),'rotation'))@np.diag(hnode['scale']);T[:3,3]=sample(tr[(hn,'translation')],float(t),'translation');T=T@np.linalg.inv(hM);rigid=world@T[:3,:3].T+T[:3,3];frame=world+weights[:,None]*(rigid-world);frame[f]=world[f];frame[v]=rigid[v]
   pc=[(bone,node_positions(doc,bytes(buf),tr,nodes[bone],float(t)),bt,baseline) for bone,bt,baseline in contacts]

   print('author',side,key,float(t),flush=True)
   try:frame,corrective=source_bone_projection_corrective(frame,world,tri,pc,set(f)|set(v),margin_metres=.000005)
   except ValueError as err:
    base=world[tri];bn=np.cross(base[:,1]-base[:,0],base[:,2]-base[:,0]);ft=frame[tri];fn=np.cross(ft[:,1]-ft[:,0],ft[:,2]-ft[:,0]);bad=np.flatnonzero((bn*fn).sum(1)<0);print('repair',str(err),bad.tolist(),flush=True)
    frame,corrective=source_topology_contact_patch_corrective(frame,world,tri,pc,set(f)|set(v),[],margin_metres=.000005,shape_seed_vertices=np.unique(tri[bad]).tolist(),shape_floor=.15,patch_rings=3)
   corrections.append(corrective);local=(frame-M[:3,3])@np.linalg.inv(M[:3,:3]).T;local[f]=pos[f];delta=(local-pos).astype('<f4');nd=(normals(local,tri)-baseN).astype('<f4');pa=put(doc,buf,delta.tobytes(),'VEC3',len(pos));doc['accessors'][pa].update(min=delta.min(0).tolist(),max=delta.max(0).tolist());prim['targets'].append({'POSITION':pa,'NORMAL':put(doc,buf,nd.tobytes(),'VEC3',len(pos))})
  doc['meshes'][ni]['weights']=[0]*16;node['weights']=[0]*16;weightsOut=np.zeros((17,16),dtype='<f4');weightsOut[1:]=np.eye(16);wa=put(doc,buf,weightsOut.tobytes(),'SCALAR',weightsOut.size);anim=doc['animations'][0];anim['channels']=[c for c in anim['channels'] if c['target']['node']!=ni];si=len(anim['samplers']);anim['samplers'].append({'input':timea,'output':wa,'interpolation':'LINEAR'});anim['channels'].append({'sampler':si,'target':{'node':ni,'path':'weights'}});next(m for m in members if m['sourceKey']==key)['role']='deforming_passive_surface';changed.append(key);authored.append({'sourceKey':key,'inputMask':e,'contacts':len(contacts),'correctives':corrections})
 motion=container(doc,buf);reference=container(ref,refbuf);(dest/'motion.glb').write_bytes(motion);(dest/'reference.glb').write_bytes(reference);_,nd,nb=read_glb(dest/'motion.glb');nt=channel_data(nd,nb);errors=[]
 for ni in range(oldcount):
  if old['nodes'][ni]['extras']['sourceKey'] in changed+stationary:continue
  for t in np.linspace(0,float(times[-1]),65):errors.append(float(np.linalg.norm(node_positions(old,oldbin,oldtracks,ni,t)-node_positions(nd,nb,nt,ni,t),axis=1).max()))
 assert max(errors)<1e-12
 qp={}
 for key in changed:
  w=source_geometry(src[key],'overview')[-1];near=[bone for bone in bones if not any(w.max(0)[j]<node_positions(nd,nb,nt,nodes[bone],0).min(0)[j]-.025 or w.min(0)[j]>node_positions(nd,nb,nt,nodes[bone],0).max(0)[j]+.025 for j in range(3))];qc=verify(dest/'motion.glb',key,near,4);qp[key]=save(dest/('interpolation-'+key+'.json'),qc);print(side,key,qc['passed'],qc['geometry']['flippedFaceSamples'],qc['geometry']['minimumAreaRatio'],qc['contact']['newContainmentMaximum'],flush=True)
  assert qc['passed']
 receipt={'originalMotionUri':a['uri'],'originalMotionSha256':sha(oldraw),'originalReferenceUri':scene['assetUri'],'originalReferenceSha256':sha(refr),'oldMembers':oldcount,'correctedStationaryNativeNeckContext':stationary,'oldUnchangedMembers':oldcount-len(changed)-len(stationary),'oldUnchangedReplaySamples':65,'oldUnchangedReplayMaximumErrorMetres':max(errors),'appendedStaticNativeMembers':[e['sourceKey'] for e in newentries],'newSourceSpecificDeformers':changed,'newMotionSha256':sha(motion),'newReferenceSha256':sha(reference),'sourceMeshesModified':False,'measuredAxisOrFootprintClaimed':False}
 save(dest/'reuse-receipt.json',receipt);save(dest/'authored-contact-input.json',authored);save(dest/'registration-input.json',{'baseAsset':a,'baseAuthoringPath':arp,'baseInputPath':ip,'baseGeometryPath':gp,'baseElevationAuthoringPath':ep,'members':members,'newEntries':newentries,'newDeformers':changed,'correctedStationaryContext':stationary,'interpolationPaths':qp,'sourceSpecificEntries':list(entries.values())+newentries,'motionSha256':sha(motion),'restSha256':sha(reference),'surfaceCount':len(members)})
