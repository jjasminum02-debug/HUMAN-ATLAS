"""Additional emitted rigid skeleton/passive context contact, separate from muscle QC."""
import pathlib,sys,json,numpy as np
R=pathlib.Path(__file__).resolve().parents[4];O=pathlib.Path(__file__).parent
sys.path[:0]=[str(R/'work/tools'),str(R/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from verify_glb_interpolation import read_glb,channel_data,node_positions,bounded_inside,sample,qmatrix
from author_source_surface_motion import array
src={r['sourceKey']:r for r in json.loads((R/'atlas-data/source-cache/datasets/za/compiled/manifest.json').read_text())['instances']};results=[]
for kind in sys.argv[1:] or ['flex','rot-right','rot-left']:
 d=O/kind;complete=json.loads((d/'complete.json').read_text());raw,doc,buf=read_glb(d/'motion.glb');tr=channel_data(doc,buf);nd={n['extras']['sourceKey']:i for i,n in enumerate(doc['nodes'])};bones=[m['sourceKey'] for m in complete['members'] if m['role'] in ['fixed_structure','moving_structure']];rigids=[m['sourceKey'] for m in complete['members'] if m['role'] in ['moving_structure','co_moving_context']];rest={k:node_positions(doc,buf,tr,i,0) for k,i in nd.items()};posed={k:[node_positions(doc,buf,tr,nd[k],float(t)) for t in np.linspace(0,2.5,65)] for k in bones+rigids};rows=[]
 def net(k,t):
  node=doc['nodes'][nd[k]]
  if 'matrix' in node:actual=np.array(node['matrix']).reshape(4,4).T
  else:
   actual=np.eye(4);actual[:3,:3]=qmatrix(sample(tr[(nd[k],'rotation')],t,'rotation'))@np.diag(node['scale']);actual[:3,3]=sample(tr[(nd[k],'translation')],t,'translation')
  return actual@np.linalg.inv(np.array(src[k]['matrix']).reshape(4,4).T)
 nets={k:[net(k,float(t)) for t in np.linspace(0,2.5,65)] for k in set(bones+rigids)}
 for k in rigids:
  for b in bones:
   if k==b or any(rest[k].max(0)[j]<rest[b].min(0)[j] or rest[k].min(0)[j]>rest[b].max(0)[j] for j in range(3)):continue
   residual=max(float(np.abs(a-bb).max()) for a,bb in zip(nets[k],nets[b]));worldbound=max(float(np.linalg.norm(posed[k][i]-(rest[k]@nets[b][i][:3,:3].T+nets[b][i][:3,3]),axis=1).max()) for i in range(65))
   # Native key replay retains the existing 1 um requirement. Independent
   # glTF translation/quaternion interpolation adds a tiny chord approximation
   # between keys. For co-moving rigid pairs, explicitly bound that artifact
   # at 10 um; do not apply this allowance to deforming muscle/contact QC.
   if residual<=1e-5 and worldbound<=1e-5:
    rows.append({'sourceKey':k,'boneSourceKey':b,'newContainmentMaximum':0,'failures':[],'method':'common_rigid_frame_with_bounded_gltf_interpolation_precision','actualTransformSamples':65,'maximumRelativeTransformResidual':residual,'maximumVertexWorldBoundMetres':worldbound,'rigidInterpolationPrecisionMetres':1e-5,'nativeKeyFrameToleranceMetres':1e-6,'strictNumericalRayRepeatsClaimed':False});continue
   tri=array(doc,buf,doc['meshes'][doc['nodes'][nd[b]]['mesh']]['primitives'][0]['indices']).reshape(-1,3);baseline=bounded_inside(rest[k],rest[b],tri);maxn=0;hits=[]
   for i in range(65):
    fresh=bounded_inside(posed[k][i],posed[b][i],tri)&~baseline;n=int(fresh.sum());maxn=max(maxn,n)
    if n:hits.append({'sample':i,'sourceVertexIndices':np.flatnonzero(fresh).tolist()})
   rows.append({'sourceKey':k,'boneSourceKey':b,'newContainmentMaximum':maxn,'failures':hits})
   if maxn:print(kind,src[k]['name'],src[b]['name'],maxn,flush=True)
 report={'kind':kind,'rows':rows,'inspectedPoseSamples':65,'newContainmentMaximum':max((r['newContainmentMaximum'] for r in rows),default=0),'passed':all(not r['newContainmentMaximum'] for r in rows),'baselineOverlapPreserved':True,'continuousCollisionFreedomClaimed':False};(d/'rigid-context-qc.json').write_text(json.dumps(report,indent=2)+'\n');results.append(report);print(kind,'rigid contact pairs',len(rows),'passed',report['passed'],flush=True)
(O/'context-contact-summary.json').write_text(json.dumps([{'kind':r['kind'],'pairs':len(r['rows']),'newContainmentMaximum':r['newContainmentMaximum'],'passed':r['passed']} for r in results],indent=2)+'\n');assert all(r['passed'] for r in results)
