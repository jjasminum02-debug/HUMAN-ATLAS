"""Focused actual-buffer validation; unchanged hip/T59 QC reused only with matching hashes."""
import json,sys,pathlib,numpy as np,math
ROOT=pathlib.Path(__file__).resolve().parents[4];OUT=pathlib.Path(__file__).parent
sys.path[:0]=[str(ROOT/'work/tools'),str(ROOT/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from author_source_surface_motion import array,source_geometry,rotation
from derive_source_surface_motion import sha
from verify_glb_interpolation import read_glb,channel_data,node_positions,verify,bounded_inside
from verify_t66_glb_pose import verify_glb
from PIL import Image,ImageDraw
load=lambda p:json.loads((ROOT/p).read_text())
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
man=load('atlas-data/source-cache/datasets/za/compiled/manifest.json');source={x['sourceKey']:x for x in man['instances']};bundle=load('atlas-data/motion/motion-learning.json')
# Native source wireframes are inspection evidence, with authoring masks and context bones, not inferred footprints.
im=Image.new('RGB',(1500,950),'white');draw=ImageDraw.Draw(im)
for panel,(key,title) in enumerate([('ZA-c7010a9-74ced50ada635db761f807e4','Left tibialis anterior'),('ZA-c7010a9-afb0624c66f652ea012c7534','Left rectus femoris'),('ZA-c7010a9-eb0a993e09d73159468116ce','Right rectus femoris')]):
 g=source_geometry(source[key],'detail' if panel==0 else 'overview');world=g[-1];yz=world[:,[2,1]];lo=yz.min(0);extent=yz.max(0)-lo;scale=min(430/max(extent[0],.001),800/extent[1]);xy=(yz-lo)*scale;xy[:,0]+=panel*500+35;xy[:,1]=900-xy[:,1]
 draw.text((panel*500+20,20),title+' native sagittal source',fill='black')
 for tri in g[4]:draw.line([tuple(xy[v]) for v in [*tri,tri[0]]],fill=(143,72,59),width=1)
im.save(OUT/'source-inspection.png')
# Evaluate every changed left surface at emitted key/intermediate states, with native context.
p=load(str((OUT/'left-tibialis/input.json').relative_to(ROOT))); rec=load(str((OUT/'left-tibialis/authoring-record.json').relative_to(ROOT)));path=OUT/'left-tibialis/motion.glb';raw,d,b=read_glb(path);tracks=channel_data(d,b);nodes={x['extras']['sourceKey']:i for i,x in enumerate(d['nodes'])}
family={'id':'priority-left-tibialis-dorsiflexion','type':'ankle','label':'발목 등쪽굽힘','frameId':man['frameContract']['frameId'] if 'frameId' in man['frameContract'] else 'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR','referencePoseId':rec['poseRange']['referencePoseId'],'axis':rec['poseRange']['axis'],'pivotMetres':rec['poseRange']['pivotMetres'],'endDegrees':6.5,'validatedAuthoringLimitDegrees':6.5,'samples':p['morphSamples'],'durationSeconds':2}
frames={};deform=[];bones=[e['sourceKey'] for e in p['members'] if e['role'] in ['fixed_structure','moving_structure']];contactrows=[];qcpaths={}
for e in p['members']:
 key=e['sourceKey'];ni=nodes[key];g=source_geometry(source[key],e['lod']);w=g[-1];role=e['role'];poses=[]
 for phase in np.linspace(0,1,p['morphSamples']+1):
  expected=(w-np.array(family['pivotMetres']))@rotation(family['axis'],math.radians(6.5)*phase).T+family['pivotMetres']+np.array(rec['poseRange']['coupledClearanceMetres'])*phase if role in ['moving_structure','co_moving_context'] else w
  poses.append(node_positions(d,b,tracks,ni,2*phase) if role.startswith('deforming') else expected)
 frames[key]=(poses,g[4])
 if role.startswith('deforming'):
  deform.append(key);near=[bk for bk in bones if not any(w.max(0)[j]<frames.get(bk,([source_geometry(source[bk],'overview')[-1]],))[0][0].min(0)[j]-.025 or w.min(0)[j]>source_geometry(source[bk],'overview')[-1].max(0)[j]+.025 for j in range(3))]
  qc=verify(path,key,near,8);qp=OUT/'left-tibialis'/('interpolation-'+key+'.json');write(qp,qc);qcpaths[key]=str(qp.relative_to(ROOT));print(key,qc['passed'],qc['geometry']['flippedFaceSamples'],qc['contact']['newContainmentMaximum'],flush=True)
  assert qc['passed'],'changed emitted surface failed'
# New moving-bone containment against fixed mortise at actual interpolated poses.
for key in [k for k in bones if next(e['role'] for e in p['members'] if e['sourceKey']==k)=='moving_structure']:
 for bk in [k for k in bones if next(e['role'] for e in p['members'] if e['sourceKey']==k)=='fixed_structure']:
  ni=nodes[key];bn=nodes[bk];w=node_positions(d,b,tracks,ni,0);bw=node_positions(d,b,tracks,bn,0);bt=array(d,b,d['meshes'][d['nodes'][bn]['mesh']]['primitives'][0]['indices']).reshape(-1,3);base=bounded_inside(w,bw,bt);maximum=0
  for t in np.linspace(0,2,33): maximum=max(maximum,int((bounded_inside(node_positions(d,b,tracks,ni,t),node_positions(d,b,tracks,bn,t),bt)&~base).sum()))
  contactrows.append({'sourceKey':key,'boneSourceKey':bk,'newContainedMaximum':maximum})
assert not any(x['newContainedMaximum'] for x in contactrows)
contact={'familyId':family['id'],'rows':contactrows,'failures':[],'newContainmentMaximum':0,'method':'Actual GLB dense interpolation, source-baseline containment retained separately; not continuous collision proof.'};write(OUT/'left-tibialis/contact-qc.json',contact)
pose=verify_glb(path,{'family':family},frames,deform)
for row in pose['rows']:
 if row['sourceKey'] in qcpaths:
  qp=ROOT/qcpaths[row['sourceKey']];row.update(passed=True,geometryQcPath=qcpaths[row['sourceKey']],geometryQcSha256=sha(qp.read_bytes()))
pose['passed']=all(x['passed'] for x in pose['rows']);assert pose['passed'];write(OUT/'left-tibialis/glb-pose-qc.json',pose)
georec={'schemaVersion':'t66-authored-family-record-v1','id':rec['id'],'family':family,'members':rec['members'],'surfaceMetrics':[{**x,'flips':x['flippedTriangles'],'minimumAreaRatio':json.loads((ROOT/qcpaths[x['sourceKey']]).read_text())['geometry']['minimumAreaRatio'] if x['sourceKey'] in qcpaths else 1} for x in rec['surfaceMetrics']],'motionSha256':rec['motionSha256'],'restSha256':rec['restSha256']};write(OUT/'left-tibialis/family-geometry-record.json',georec)
# Action evidence is independent of general deformation QC and never changes the passive actions.
out=[]
for side,kind,key in [('right','tibialis','ZA-c7010a9-54ae5266082b61f48ed8e83e'),('left','tibialis','ZA-c7010a9-74ced50ada635db761f807e4'),('left','rectus','ZA-c7010a9-afb0624c66f652ea012c7534'),('right','rectus','ZA-c7010a9-eb0a993e09d73159468116ce')]:
 if kind=='tibialis':
  ip=OUT/'left-tibialis/input.json' if side=='left' else ROOT/'work/evidence/T59/resume-2026-10-02/authoring-input.json';payload=json.loads(ip.read_text());glb=path if side=='left' else ROOT/'atlas-data/assets/motion/t59-za-right-ankle/motion.glb';assetid='T66-PRIORITY-L-TIBANT-ASSET' if side=='left' else 'T59-ASSET-ZA-R-TIBANT-DF';tcount=33
 else:
  ip=ROOT/f'work/evidence/T66/serial-completion-2026-10-02/unit-02/trials-r1/hip-flexion-{side}/input.json';payload=json.loads(ip.read_text());asset=next(x for x in bundle['motionAssets'] if x.get('sourceBinding',{}).get('subjectSourceKey')==key and x.get('sourceBinding',{}).get('sourceFamilyId')==f'hip-flexion-{side}');glb=ROOT/asset['uri'];assetid='T66-PRIORITY-'+('L' if side=='left' else 'R')+'-RECTUS-ASSET';assert sha(glb.read_bytes())==asset['sha256'];tcount=65
 raw,doc,binary=read_glb(glb);tr=channel_data(doc,binary);nd={x['extras']['sourceKey']:i for i,x in enumerate(doc['nodes'])};entry=next(x for x in payload['members'] if x['sourceKey']==key);ni=nd[key];w=node_positions(doc,binary,tr,ni,0);f=entry['fixedVertexIndices'];v=entry['movingVertexIndices'];o=w[f].mean(0);ins=w[v].mean(0);rows=[]
 for t in np.linspace(0,2,tcount):
  q=node_positions(doc,binary,tr,ni,t);rows.append({'phase':float(t/2),'fixedMaskErrorMetres':float(np.linalg.norm(q[f]-w[f],axis=1).max()),'endpointSeparationMetres':float(np.linalg.norm(q[f].mean(0)-q[v].mean(0)))})
 end=node_positions(doc,binary,tr,ni,2);motion=end-w;nonRigid=float(np.linalg.norm(motion-motion.mean(0),axis=1).max());assert nonRigid>.001 and max(x['fixedMaskErrorMetres'] for x in rows)<1e-6
 # Actual functional direction, independent of label/intent.
 if kind=='rectus':
  assert end[v,2].mean()>w[v,2].mean()+.01 and rows[-1]['endpointSeparationMetres']<rows[0]['endpointSeparationMetres']
  # Patella/tibia and femur share rigid hip motion: knee is held, not flexed/claimed as extensor action.
  names=[(k,source[k]['name']) for k in nd];fem=next(k for k,n in names if n=='Femur.'+side[0]);tib=next(k for k,n in names if n=='Tibia.'+side[0]);pat=next(k for k,n in names if n=='Patella.'+side[0]);cent=lambda k,t:node_positions(doc,binary,tr,nd[k],t).mean(0)
  knee=[]
  for t in np.linspace(0,2,9):
   aa=cent(fem,t)-cent(pat,t);bb=cent(tib,t)-cent(pat,t);knee.append(float(np.arccos(np.clip(aa@bb/np.linalg.norm(aa)/np.linalg.norm(bb),-1,1))))
  assert max(knee)-min(knee)<1e-6;extra={'heldKneeAngleDriftRadians':max(knee)-min(knee),'patellaSourceKey':pat,'femurSourceKey':fem,'tibiaSourceKey':tib,'principalAction':'hip_flexion_knee_held','kneeExtensionAnimated':False}
 else:
  met=next(k for k in nd if source[k]['name']=='First metatarsal bone.'+side[0]);start=node_positions(doc,binary,tr,nd[met],0).mean(0);endbone=node_positions(doc,binary,tr,nd[met],2).mean(0);assert endbone[1]>start[1]+.001;extra={'firstMetatarsalHeadwardDeltaMetres':float(endbone[1]-start[1]),'principalAction':'ankle_dorsiflexion'}
 out.append({'sourceKey':key,'side':side,'kind':kind,'assetId':assetid,'motionUri':str(glb.relative_to(ROOT)),'motionSha256':sha(raw),'nativeSourceResourceSha256':source[key]['lods'][entry['lod']]['resource'],'samples':rows,'nonRigidDisplacementSpreadMetres':nonRigid,'shorteningMetres':rows[0]['endpointSeparationMetres']-rows[-1]['endpointSeparationMetres'],'passed':True,'measuredAttachmentFootprints':False,'physiologicalContractionClaimed':False,**extra})
write(OUT/'action-outcome.json',out);print('four exact source-action outcomes passed',flush=True)
