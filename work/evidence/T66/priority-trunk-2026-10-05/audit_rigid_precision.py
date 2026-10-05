"""Distinguish strict ray hits from sub-tolerance common rigid-transform replay.

Never mask real relative bone/muscle motion or penetration beyond the existing
1 micrometre source-frame verification tolerance. Raw ray failures are retained.
"""
import pathlib,sys,json,numpy as np
R=pathlib.Path(__file__).resolve().parents[4];O=pathlib.Path(__file__).parent
sys.path[:0]=[str(R/'work/tools'),str(R/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from verify_glb_interpolation import read_glb,channel_data,node_positions,sample,qmatrix
from author_source_surface_motion import array
from t66_contact_correctives import nearest_surface
from derive_source_surface_motion import sha
src={r['sourceKey']:r for r in json.loads((R/'atlas-data/source-cache/datasets/za/compiled/manifest.json').read_text())['instances']};summaries=[]
for kind in sys.argv[1:] or ['flex','rot-right','rot-left']:
 d=O/kind;report=json.loads((d/'rigid-context-qc.json').read_text());raw,doc,buf=read_glb(d/'motion.glb');tracks=channel_data(doc,buf);nodes={n['extras']['sourceKey']:i for i,n in enumerate(doc['nodes'])};proof=[]
 def net(k,t):
  n=nodes[k];node=doc['nodes'][n]
  if 'matrix' in node:actual=np.array(node['matrix']).reshape(4,4).T
  else:
   actual=np.eye(4);actual[:3,:3]=qmatrix(sample(tracks[(n,'rotation')],t,'rotation'))@np.diag(node['scale']);actual[:3,3]=sample(tracks[(n,'translation')],t,'translation')
  return actual@np.linalg.inv(np.array(src[k]['matrix']).reshape(4,4).T)
 for row in report['rows']:
  if not row['newContainmentMaximum']:continue
  k,b=row['sourceKey'],row['boneSourceKey'];tri=array(doc,buf,doc['meshes'][doc['nodes'][nodes[b]]['mesh']]['primitives'][0]['indices']).reshape(-1,3);depth=0;difference=0
  for fail in row['failures']:
   t=2.5*fail['sample']/64;points=node_positions(doc,buf,tracks,nodes[k],t)[fail['sourceVertexIndices']];bone=node_positions(doc,buf,tracks,nodes[b],t);surface=nearest_surface(points,bone,tri);depth=max(depth,float(np.linalg.norm(points-surface,axis=1).max()));difference=max(difference,float(np.abs(net(k,t)-net(b,t)).max()))
  p={'sourceKey':k,'boneSourceKey':b,'strictRayFreshVertexMaximum':row['newContainmentMaximum'],'maximumSurfaceDepthMetres':depth,'maximumCommonTransformResidual':difference,'existingSourceFrameToleranceMetres':1e-6,'classification':'common_rigid_replay_numerical_ambiguity' if depth<=1e-6 and difference<=1e-6 else 'actual_relative_context_contact_failure','passed':depth<=1e-6 and difference<=1e-6};proof.append(p);print(kind,src[k]['name'],src[b]['name'],p['classification'],depth,difference,flush=True)
 audited={'motionSha256':sha(raw),'kind':kind,'rawRayQcPath':str((d/'rigid-context-qc.json').relative_to(R)),'rawRayQcSha256':sha((d/'rigid-context-qc.json').read_bytes()),'pairs':len(report['rows']),'precisionProof':proof,'passed':all(p['passed'] for p in proof),'realRelativeContextContactFailures':sum(not p['passed'] for p in proof),'sourceFrameToleranceUnchanged':True};(d/'rigid-context-audit.json').write_text(json.dumps(audited,indent=2)+'\n');summaries.append(audited)
(O/'context-contact-audit-summary.json').write_text(json.dumps(summaries,indent=2)+'\n');assert all(s['passed'] for s in summaries)
