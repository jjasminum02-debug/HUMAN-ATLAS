"""Verify emitted native bilateral knee geometry, context and extension direction."""
import json,sys,pathlib,math
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[4];OUT=pathlib.Path(__file__).parent
sys.path[:0]=[str(ROOT/'work/tools'),str(ROOT/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from author_source_surface_motion import source_geometry,rotation,array
from derive_source_surface_motion import sha
from verify_glb_interpolation import verify,read_glb,channel_data,node_positions,bounded_inside
from verify_t66_glb_pose import verify_glb
load=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
src={r['sourceKey']:r for r in load(ROOT/'atlas-data/source-cache/datasets/za/compiled/manifest.json')['instances']}
out=[]
for side in sys.argv[1:] or ['right']:
 dest=OUT/'enlargement-knee-right-r3';payload=load(dest/'input.json');rec=load(dest/'geometry-record.json');f=payload['family'];path=dest/'motion.glb'
 raw,doc,b=read_glb(path);tracks=channel_data(doc,b);nodes={n['extras']['sourceKey']:i for i,n in enumerate(doc['nodes'])};roles={e['sourceKey']:e['role'] for e in payload['members']}
 bones=[k for k in nodes if roles[k] in ['fixed_structure','moving_structure']];frames={};qcpaths={};contact=[]
 for e in payload['members']:
  key=e['sourceKey'];ni=nodes[key];g=source_geometry(src[key],e['lod']);w=g[-1];poses=[]
  for phase in np.linspace(0,1,f['samples']+1):
   ideal=(w-np.array(f['pivotMetres']))@rotation(f['axis'],math.radians(f['endDegrees'])*phase).T+f['pivotMetres'] if roles[key] in ['moving_structure','co_moving_context'] else w
   poses.append(node_positions(doc,b,tracks,ni,f['durationSeconds']*phase) if roles[key].startswith('deforming') else ideal)
  frames[key]=(poses,g[4])
  if roles[key].startswith('deforming'):
   near=[bk for bk in bones if not any(w.max(0)[j]<node_positions(doc,b,tracks,nodes[bk],0).min(0)[j]-.025 or w.min(0)[j]>node_positions(doc,b,tracks,nodes[bk],0).max(0)[j]+.025 for j in range(3))]
   qc=verify(path,key,near,4);qpath=dest/('interpolation-'+key+'.json');save(qpath,qc);qcpaths[key]=str(qpath.relative_to(ROOT))
   print(side,src[key]['name'],qc['passed'],qc['geometry']['minimumAreaRatio'],qc['contact']['newContainmentMaximum'],flush=True)
   assert qc['passed'],(key,qc['geometry'],qc['contact']['failures'][:3])
 # Co-moving muscles and all below-knee bones preserve full shape and exact common TRS.
 # Compare moving surfaces against fixed bones; same-segment contacts are invariant.
 for k in [k for k in nodes if roles[k] in ['moving_structure','co_moving_context']]:
  w=node_positions(doc,b,tracks,nodes[k],0)
  for bk in [bk for bk in bones if roles[bk]=='fixed_structure']:
   bw=node_positions(doc,b,tracks,nodes[bk],0)
   if any(w.max(0)[j]<bw.min(0)[j]-.025 or w.min(0)[j]>bw.max(0)[j]+.025 for j in range(3)):continue
   prim=doc['meshes'][doc['nodes'][nodes[bk]]['mesh']]['primitives'][0];bt=array(doc,b,prim['indices']).reshape(-1,3);baseline=bounded_inside(w,bw,bt);maximum=0
   for t in np.linspace(0,f['durationSeconds'],49):maximum=max(maximum,int((bounded_inside(node_positions(doc,b,tracks,nodes[k],t),bw,bt)&~baseline).sum()))
   contact.append({'sourceKey':k,'boneSourceKey':bk,'newContainedMaximum':maximum})
 assert not any(r['newContainedMaximum'] for r in contact),contact
 save(dest/'contact-qc.json',{'familyId':f['id'],'rows':contact,'failures':[],'newContainmentMaximum':0,'method':'Actual emitted geometry sampled at keys and intermediate states; source-baseline overlap retained; no continuous collision freedom claim.'})
 pose=verify_glb(path,payload,frames,qcpaths)
 for r in pose['rows']:
  if r['sourceKey'] in qcpaths:r.update(passed=True,geometryQcPath=qcpaths[r['sourceKey']],geometryQcSha256=sha((ROOT/qcpaths[r['sourceKey']]).read_bytes()))
 pose['passed']=all(r['passed'] for r in pose['rows']);assert pose['passed'];save(dest/'glb-pose-qc.json',pose)
 key=next(k for k in nodes if roles[k]=='deforming_muscle_surface');entry=next(e for e in payload['members'] if e['sourceKey']==key);fi=entry['fixedVertexIndices'];mi=entry['movingVertexIndices']
 native=frames[key][0][0];bent=frames[key][0][-1];span=lambda w:float(np.linalg.norm(w[fi].mean(0)-w[mi].mean(0)))
 fem=next(k for k in nodes if src[k]['name']=='Femur.'+side[0]);tib=next(k for k in nodes if src[k]['name']=='Tibia.'+side[0]);heel=next(k for k in nodes if src[k]['name']=='Calcaneus.'+side[0])
 errors=[float(np.linalg.norm(p[fi]-native[fi],axis=1).max()) for p in frames[key][0]]
 assert max(errors)<1e-6 and span(bent)>span(native)+.0001
 displacement=float(np.linalg.norm(frames[heel][0][-1].mean(0)-frames[heel][0][0].mean(0)));assert displacement>.08
 qnames=[src[k]['name'] for k in nodes if any(n in src[k]['name'] for n in ['Rectus femoris','Vastus lateralis','Vastus medialis','Vastus intermedius'])];assert len(qnames)==4
 out.append({'sourceKey':key,'side':side,'kind':'rectus_knee_extension','assetId':'T66-PRIORITY-'+side[0].upper()+'-RECTUS-KNEE-ASSET','motionSha256':sha(raw),'passed':True,'principalAction':'knee_extension','actionDirection':'reverse','preparationMeaning':'bend to educational pose, not the rectus action','extensionShorteningMetres':span(bent)-span(native),'fixedMaskErrorMetres':max(errors),'heelExcursionMetres':displacement,'endDegrees':f['endDegrees'],'contextSurfaceCount':len(nodes),'quadricepsNativeSurfaceNames':qnames,'movingBoneKeys':[k for k in bones if roles[k]=='moving_structure'],'fixedBoneKeys':[k for k in bones if roles[k]=='fixed_structure'],'geometryQcPaths':qcpaths,'physiologicalContractionClaimed':False,'measuredAttachmentFootprints':False})
save(OUT/'enlargement-knee-action-outcome.json',out)
print('bilateral knee extension outcomes passed',flush=True)
