"""Source-local segmented teaching spine; immutable native meshes, no measured axes/ROM.

Emit native bilateral anatomy and independently replay the emitted morph/TRS data.
Only three requested teaching families are authored; old C candidates are untouched.
"""
import pathlib,sys,json,copy,math,hashlib
import numpy as np
R=pathlib.Path(__file__).resolve().parents[4];O=pathlib.Path(__file__).parent/'enlargement-trunk';O.mkdir(exist_ok=True)
sys.path[:0]=[str(R/'work/tools'),str(R/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from author_source_surface_motion import source_geometry,array,normals,container,rotation,RIGHTS
from author_t66_family_motion import signed_quat
from derive_source_surface_motion import accessor_bytes,append_bytes,geometry_hash,sha
from verify_glb_interpolation import read_glb,channel_data,node_positions,bounded_inside,verify
from verify_t66_glb_pose import verify_glb
from t66_contact_correctives import source_bone_projection_corrective,source_topology_contact_patch_corrective
load=lambda p:json.loads((R/p).read_text())
def save(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n');return str(p.relative_to(R))
man=load('atlas-data/source-cache/datasets/za/compiled/manifest.json');src={r['sourceKey']:r for r in man['instances']};typed={r['sourceKey']:r for r in load('atlas-data/overlays/za-local-integration.json')['objects']};byname={r['name']:k for k,r in src.items()};cache={}
def geom(k):
 if k not in cache:cache[k]=source_geometry(src[k],'overview')
 return cache[k]
def center(k):return geom(k)[-1].mean(0)
def smooth(x):x=np.clip(x,0,1);return x*x*(3-2*x)
levels=[byname['Vertebra L'+str(i)] for i in range(5,0,-1)]+[byname['Vertebra T'+str(i)] for i in range(12,0,-1)]
centers=np.array([center(k) for k in levels]);pelvis=[byname[n] for n in ['Hip bone.l','Hip bone.r','Sacrum']]
hipaxis=center(pelvis[0])-center(pelvis[1]);hipaxis/=np.linalg.norm(hipaxis)
vertical=centers[-1]-centers[0];vertical/=np.linalg.norm(vertical)
# Thoracic attachment context includes the original sternum, ribs and native cartilages.
# Complete shoulder/arm context is reused as source identities, not old motion tracks.
base=load('atlas-data/motion/motion-learning.json');keys=set(pelvis+levels)
for a in base['motionAssets']:
 if a.get('sourceBinding',{}).get('sourceFamilyId') in ['priority-lev-left','priority-lev-right']:
  keys.update(m['sourceKey'] for m in a['sourceBinding']['members'])
for k,t in typed.items():
 if t['kind'] not in ['bone','muscle'] or not t['localDisplayEligible'] or t['hardHoldReasons']:continue
 if set(t['regionIds'])&{'thorax','abdomen-lumbar','back','neck'}:keys.add(k)
keys=sorted(keys);targets=[byname[n+s] for n in ['Rectus abdominis muscle','External abdominal oblique muscle'] for s in ['.l','.r']]
save(O/'qualitative-action-evidence.json',{'accessedOn':'2026-10-05','sources':[{'url':'https://medicine.uams.edu/neuroscience/education/medical-school-courses/human-structure-module/anatomy-tables/muscle-tables/muscles-of-the-abdominal-region/','locators':['rectus abdominis origin/insertion/action row','external abdominal oblique origin/insertion/action row']},{'url':'https://www.unm.edu/~lkravitz/Article%20folder/abdominal.html','locators':['Anatomical and Kinesiological Review paragraphs rectus attachments and flexion','external oblique opposite-side rotator and internal oblique same-side rotator paragraphs']},{'url':'https://pubmed.ncbi.nlm.nih.gov/11703044/','locator':'Abstract Results: contralateral external oblique in seated thorax-relative-to-pelvis rotation'}],'paraphraseKo':{'rectus':'복직근은 치골 부근에서 다섯째–일곱째 갈비연골·검상돌기 부근으로 이어집니다. 골반을 유지하고 흉곽을 골반 쪽으로 가까이 하는 몸통 굽힘을 보여줍니다.','oblique':'외복사근은 아래 여덟 갈비뼈에서 백선·치골·앞쪽 장골능 부근으로 이어집니다. 골반이 고정된 시범에서 왼쪽은 오른쪽 몸통 회전, 오른쪽은 왼쪽 몸통 회전에 관여합니다. 양측은 몸통 굽힘에도 관여합니다. 반대쪽 내복사근의 협응과 단독근 수축이 아님을 안내합니다.'},'limits':'qualitative attachment/action only; no measured footprint, native rig, physiological ROM, force, activation or individual normal-axis claim'})
inspection=[]
for k in targets+levels+pelvis:
 *_,w=geom(k);inspection.append({'sourceKey':k,'name':src[k]['name'],'side':src[k]['sourceLabelSide'],'bounds':[w.min(0).tolist(),w.max(0).tolist()],'centroid':w.mean(0).tolist(),'vertices':len(w)})
save(O/'source-inspection.json',inspection)
def transforms(kind,phase):
 axis=hipaxis if kind=='flex' else vertical;sign=-1 if kind=='rot-right' else 1
 # Bounded authored increments, not measured regional rotation distribution.
 increments=[0]+([4.55]*4+[0]*12 if kind=='flex' else [2.5]*4+[0]*12)
 out=[];T=np.eye(4)
 for i,k in enumerate(levels):
  if i:
   pivot=(centers[i]+centers[i-1])/2;rr=rotation(axis,math.radians(sign*increments[i]*phase));A=np.eye(4);A[:3,:3]=rr;A[:3,3]=pivot-rr@pivot;T=T@A
  out.append(T.copy())
 return out
def transform(k,ts):
 name=src[k]['name'];w=geom(k)[-1]
 if k in levels:return ts[levels.index(k)]
 if k in pelvis or 'Femur' in name or 'Coccyx' in name:return np.eye(4)
 # Ribs follow their actual numbered thoracic source level; cartilages remain
 # native continuous passive surfaces below rather than independent fake joints.
 ords=['First','Second','Third','Fourth','Fifth','Sixth','Seventh','Eighth','Ninth','Tenth','Eleventh','Twelfth']
 if any(name.startswith(n+' rib.') for n in ords):
  return ts[-1]
 if typed[k]['kind']=='bone' and any(n in name.lower() for n in ['sternum','xiphoid']):return ts[levels.index(byname['Vertebra T7'])]
 if w[:,1].min()>=centers[4,1] or set(typed[k]['regionIds'])&{'upper-limb','shoulder-scapular'} or any(n in name.lower() for n in ['intercostal','diaphragm','sternum','xiphoid','costal cartilage']):return ts[-1]
 if typed[k]['kind']=='bone':return ts[int(np.argmin(abs(centers[:,1]-w[:,1].mean())))]
 return None
def field(w,ts):
 # Piecewise smooth partition of unity across adjacent observed source levels.
 # Every vertex remains; lower pelvic masks are unchanged and upper context follows.
 y=w[:,1];posed=np.zeros_like(w);a=np.clip(np.searchsorted(centers[:,1],y)-1,0,len(levels)-2);v=smooth((y-centers[a,1])/(centers[a+1,1]-centers[a,1]));below=y<=centers[0,1];above=y>=centers[-1,1]
 for i in range(len(levels)):
  weight=np.where(a==i,1-v,0)+np.where(a+1==i,v,0);weight[below]=1 if i==0 else 0;weight[above]=1 if i==len(levels)-1 else 0;T=ts[i];posed+=weight[:,None]*(w@T[:3,:3].T+T[:3,3])
 return posed
for kind in ['flex']:
 dest=O/kind;dest.mkdir(exist_ok=True)
 if (dest/'complete.json').exists():
  c=load(str((dest/'complete.json').relative_to(R)));assert c['motionSha256']==sha((dest/'motion.glb').read_bytes()) and c['restSha256']==sha((dest/'reference.glb').read_bytes());print('reuse completed unchanged family',kind,flush=True);continue
 if (dest/'glb-pose-qc.json').exists():
  g=load(str((dest/'geometry-record.json').relative_to(R)));assert g['motionSha256']==sha((dest/'motion.glb').read_bytes());print('retain emitted candidate for targeted repair only',kind,flush=True);continue
 print('author',kind,'native surfaces',len(keys),flush=True)
 doc={'asset':{'version':'2.0','generator':'HUMAN ATLAS segmented source-local trunk teaching r1'},'scene':0,'scenes':[{'nodes':[]}],'nodes':[],'meshes':[],'accessors':[],'bufferViews':[],'buffers':[{'byteLength':0}]};buf=bytearray();tracks=[];members=[];metrics=[];frames={};authored=[];deformers=[];bonekeys=[k for k in keys if typed[k]['kind']=='bone'];tsframes=[transforms(kind,p) for p in np.linspace(0,1,17)]
 def put(raw,typ,count,component=5126):
  off,ln=append_bytes(buf,raw);doc['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':ln});ai=len(doc['accessors']);doc['accessors'].append({'bufferView':len(doc['bufferViews'])-1,'componentType':component,'count':int(count),'type':typ});return ai
 def applyT(w,T):return w@T[:3,:3].T+T[:3,3]
 # Cache bones at exact keys before authoring surface contact correctives.
 bones={k:[applyT(geom(k)[-1],transform(k,ts)) for ts in tsframes] for k in bonekeys}
 for k in keys:
  sd,sb,sp,pos,tri,M,w=geom(k);n=len(pos);ni=len(doc['nodes']);attrs={};print('surface',kind,ni,src[k]['name'],flush=True)
  for semantic,ai in sp['attributes'].items():
   _,_,count,normalized,raw=accessor_bytes(sd,sb,ai);a=sd['accessors'][ai];out=put(raw,a['type'],count,a['componentType']);attrs[semantic]=out
   if normalized:doc['accessors'][out]['normalized']=True
   if semantic=='POSITION':doc['accessors'][out].update(min=pos.min(0).tolist(),max=pos.max(0).tolist())
  _,_,count,_,raw=accessor_bytes(sd,sb,sp['indices']);prim={'attributes':attrs,'indices':put(raw,'SCALAR',count,sd['accessors'][sp['indices']]['componentType']),'mode':4};mesh={'name':src[k]['lods']['overview']['resource'],'primitives':[prim]};node={'name':'surface_'+str(ni),'mesh':ni,'matrix':src[k]['matrix'],'extras':{'sourceKey':k}};T=transform(k,tsframes[-1]);fixed=[];moving=[];corrections=[]
  if T is None:
   role='deforming_muscle_surface' if k in targets else 'deforming_passive_surface';deformers.append(k);poses=[field(w,ts) for ts in tsframes];fixed=np.flatnonzero(w[:,1]<=centers[0,1]).tolist();moving=np.flatnonzero(w[:,1]>=np.quantile(w[:,1],.94)).tolist()
   # Near-degenerate native taper triangles cannot tolerate independently sampled
   # displacement fields. Couple only failing source topology to a shared local
   # displacement; preserve the original vectors rather than flattening the mesh.
   bt=w[tri];bn=np.cross(bt[:,1]-bt[:,0],bt[:,2]-bt[:,0]);ba=np.linalg.norm(bn,axis=1);good=ba>=1e-12;groups=[];repair=[]
   for iteration in range(64):
    bad=set()
    for frame in poses[1:]:
     ft=frame[tri];fn=np.cross(ft[:,1]-ft[:,0],ft[:,2]-ft[:,0]);bad.update(np.flatnonzero(good&(((fn*bn).sum(1)<0)|(np.linalg.norm(fn,axis=1)<ba*.15))).tolist())
    if not bad:break
    ids=set(int(v) for v in tri[sorted(bad)].ravel());merged=[]
    for group in groups:
     if ids&set(group):ids.update(group)
     else:merged.append(group)
    groups=merged+[sorted(ids)];repair.append({'iteration':iteration,'sourceTriangleIds':sorted(bad),'sourceVertexIndices':sorted(ids)})
    for frame in poses[1:]:
     for group in groups:
      delta=np.zeros(3) if set(group)&set(fixed) else (frame[group]-w[group]).mean(0);frame[group]=w[group]+delta
   nearby=[]
   for bk in bonekeys:
    bw=geom(bk)[-1]
    if any(w.max(0)[j]<bw.min(0)[j]-.012 or w.min(0)[j]>bw.max(0)[j]+.012 for j in range(3)):continue
    nearby.append((bk,geom(bk)[4],bounded_inside(w,bw,geom(bk)[4])))
   # Correct only detected fresh containment. Immutable baseline overlap is retained.
   for step in range(1,17):
    contacts=[(bk,bones[bk][step],bt,baseline) for bk,bt,baseline in nearby]
    try:poses[step],c=source_bone_projection_corrective(poses[step],w,tri,contacts,set(fixed),[g for g in groups if not set(g)&set(fixed)],margin_metres=.00015)
    except ValueError as e:
     print('targeted shape/contact patch',src[k]['name'],kind,step,str(e),flush=True)
     poses[step],c=source_topology_contact_patch_corrective(poses[step],w,tri,contacts,set(fixed),[],margin_metres=.00015,shape_floor=.3,patch_rings=3,topology_groups=[g for g in groups if not set(g)&set(fixed)])
    corrections.append(c)
   primitiveTargets=[];normal=array(sd,sb,sp['attributes']['NORMAL'])
   for frame in poses[1:]:
    local=(frame-M[:3,3])@np.linalg.inv(M[:3,:3]).T;local[fixed]=pos[fixed];delta=(local-pos).astype('<f4');pa=put(delta.tobytes(),'VEC3',n);doc['accessors'][pa].update(min=delta.min(0).tolist(),max=delta.max(0).tolist());primitiveTargets.append({'POSITION':pa,'NORMAL':put((normals(local,tri)-normal).astype('<f4').tobytes(),'VEC3',n)})
   prim['targets']=primitiveTargets;mesh['weights']=[0]*16;node['weights']=[0]*16;values=np.zeros((17,16),dtype='<f4');values[1:]=np.eye(16);tracks.append((ni,'weights',values.ravel(),'SCALAR'))
   authored.append({'sourceKey':k,'fixedVertexIndices':fixed,'movingVertexIndices':moving,'weightField':'source y adjacent-level smooth partition, plus detected contact-only correctives','lowerFixedReferenceY':float(centers[0,1]),'upperMasksAreContextNotMeasuredAttachment':True,'sourceTopologyRepairs':repair,'sourceTopologyCoupledVertexGroups':groups,'correctives':corrections,'contactBoneKeys':[b[0] for b in nearby]})
  else:
   role='moving_structure' if typed[k]['kind']=='bone' and not np.allclose(T,np.eye(4)) else 'fixed_structure' if typed[k]['kind']=='bone' else 'co_moving_context' if not np.allclose(T,np.eye(4)) else 'passive_context';poses=[applyT(w,transform(k,ts)) for ts in tsframes]
   if not np.allclose(T,np.eye(4)):
    q,sc=signed_quat(M);node.pop('matrix');node.update(translation=M[:3,3].tolist(),rotation=q,scale=sc);tv=[];qv=[]
    for ts in tsframes:
     mm=transform(k,ts)@M;tv.extend(mm[:3,3]);qv.extend(signed_quat(mm)[0])
    tracks.extend([(ni,'translation',tv,'VEC3'),(ni,'rotation',qv,'VEC4')])
  frames[k]=(poses,tri);bm=w[tri];bn=np.cross(bm[:,1]-bm[:,0],bm[:,2]-bm[:,0]);ba=np.linalg.norm(bn,axis=1);good=ba>=1e-12;flips=0;amin=1
  if T is None:
   for f in poses:
    ft=f[tri];fn=np.cross(ft[:,1]-ft[:,0],ft[:,2]-ft[:,0]);flips+=int(((fn*bn).sum(1)[good]<0).sum());amin=min(amin,float((np.linalg.norm(fn,axis=1)[good]/ba[good]).min()))
  if flips or amin<.1:raise ValueError(('geometry',src[k]['name'],kind,flips,amin))
  metrics.append({'sourceKey':k,'role':role,'flips':flips,'minimumAreaRatio':amin,'maximumDisplacementMetres':float(np.linalg.norm(poses[-1]-w,axis=1).max())});members.append({'sourceKey':k,'nodeId':node['name'],'sourceNamespace':man['namespace'],'role':role,'side':src[k]['sourceLabelSide'],'resourceKey':src[k]['lods']['overview']['resource'],'lod':'overview','sourceChunkSha256':src[k]['lods']['overview']['chunk'],'geometrySha256':geometry_hash(sd,sb,0)[0],'instanceMatrix':src[k]['matrix']});doc['nodes'].append(node);doc['meshes'].append(mesh);doc['scenes'][0]['nodes'].append(ni)
 save(dest/'authored-input.json',{'sourceManifestSha256':sha((R/'atlas-data/source-cache/datasets/za/compiled/manifest.json').read_bytes()),'kind':kind,'sourceKeys':keys,'segmentSourceKeys':levels,'segmentCentroids':centers.tolist(),'axis':(hipaxis if kind=='flex' else vertical).tolist(),'segmentTransformsAtKeys':[[T.tolist() for T in ts] for ts in tsframes],'measuredAnatomicalAxis':False,'measuredAttachmentFootprints':False,'surfaceFields':authored})
 rest=container(doc,buf);(dest/'reference.glb').write_bytes(rest);times=np.linspace(0,2.5,17).astype('<f4');ta=put(times.tobytes(),'SCALAR',17);doc['accessors'][ta].update(min=[0],max=[2.5]);samplers=[];channels=[]
 for ni,path,values,typ in tracks:
  values=np.array(values,dtype='<f4');ai=put(values.tobytes(),typ,len(values)//{'SCALAR':1,'VEC3':3,'VEC4':4}[typ]);samplers.append({'input':ta,'output':ai,'interpolation':'LINEAR'});channels.append({'sampler':len(samplers)-1,'target':{'node':ni,'path':path}})
 clip='T66-PRIORITY-S04-'+kind.upper();doc['animations']=[{'name':clip,'samplers':samplers,'channels':channels}];motion=container(doc,buf);(dest/'motion.glb').write_bytes(motion)
 family={'id':'priority-trunk-'+kind,'axis':(hipaxis if kind=='flex' else vertical).tolist(),'pivotMetres':((centers[0]+centers[1])/2).tolist(),'endDegrees':18.2 if kind=='flex' else -10 if kind=='rot-right' else 10,'referencePoseId':'ZA-pinned-source-frame0-autoexec-off','endPoseId':clip+'-END','samples':16,'durationSeconds':2.5,'segmentedTrajectory':True,'thoraxPolicy':'native cage co-moves intact; authored lumbar increments are not measured regional ROM; no thoracic independent DOF claimed'}
 record={'family':family,'members':members,'surfaceMetrics':metrics,'restSha256':sha(rest),'motionSha256':sha(motion),'sourceGeometryModified':False,'measuredAnatomicalAxis':False,'measuredAttachmentFootprints':False};save(dest/'geometry-record.json',record)
 qcpose=verify_glb(dest/'motion.glb',{'family':family},frames,deformers);qpaths={};failures=[]
 for k in deformers:
  contact=next(e['contactBoneKeys'] for e in authored if e['sourceKey']==k);qc=verify(dest/'motion.glb',k,contact,4);qpaths[k]=save(dest/('interpolation-'+k+'.json'),qc);print(kind,src[k]['name'],qc['passed'],'minarea',round(qc['geometry']['minimumAreaRatio'],4),'contain',qc['contact']['newContainmentMaximum'],flush=True)
  row=next(r for r in qcpose['rows'] if r['sourceKey']==k);row.update(passed=qc['passed'],geometryQcPath=qpaths[k],geometryQcSha256=sha((R/qpaths[k]).read_bytes()));failures+=qc['contact']['failures'];next(r for r in metrics if r['sourceKey']==k).update(flips=qc['geometry']['flippedFaceSamples'],minimumAreaRatio=qc['geometry']['minimumAreaRatio'])
 qcpose['passed']=all(r['passed'] for r in qcpose['rows']);save(dest/'glb-pose-qc.json',qcpose);save(dest/'geometry-record.json',record);save(dest/'contact-qc.json',{'failures':failures,'newContainmentMaximum':max((r['newContainedVertexCount'] for r in failures),default=0),'passed':not failures,'baselineOverlapPreserved':True,'continuousCollisionFreedomClaimed':False})
 if not qcpose['passed']:raise RuntimeError('emitted geometry/contact failed '+kind)
 save(dest/'complete.json',{'kind':kind,'clipId':clip,'family':family,'members':members,'motionSha256':sha(motion),'restSha256':sha(rest),'glbInterpolationQcPaths':qpaths,'contextSurfaces':len(keys),'deformingSurfaces':len(deformers)})
