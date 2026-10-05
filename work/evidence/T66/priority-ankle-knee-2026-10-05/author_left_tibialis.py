"""Author the native left source. Counterpart correspondence is verified, not assumed."""
import copy,json,sys,pathlib,numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'work/tools'))
import author_source_surface_motion as tool
from author_t66_family_motion import signed_quat
from derive_source_surface_motion import sha
OUT=pathlib.Path(__file__).parent
m=tool.read('atlas-data/source-cache/datasets/za/compiled/manifest.json');rows={r['sourceKey']:r for r in m['instances']};names={r['name']:r for r in m['instances']}
p=tool.read('work/evidence/T59/resume-2026-10-02/authoring-input.json');q=copy.deepcopy(p);mapping={};checks=[]
for e in p['members']:
 r=rows[e['sourceKey']];l=names[r['name'][:-2]+'.l'];mapping[r['sourceKey']]=l['sourceKey']
 gr=tool.source_geometry(r,e['lod']);gl=tool.source_geometry(l,e['lod'])
 if not np.array_equal(gr[4],gl[4]) or gr[-1].shape!=gl[-1].shape:raise ValueError('native paired topology differs; masks cannot transfer')
 error=float(np.max(np.linalg.norm(gl[-1]-gr[-1]*[-1,1,1],axis=1)))
 if error>1e-6:raise ValueError('native source counterpart correspondence failed')
 checks.append({'rightSourceKey':r['sourceKey'],'leftSourceKey':l['sourceKey'],'nativeResourceSha256':l['lods'][e['lod']]['resource'],'maximumNativeReflectionResidualMetres':error,'triangleIndexCorrespondence':True})
for e in q['members']:
 e['sourceKey']=mapping[e['sourceKey']]
 # Constraints remain the same inspected geometrical regions, but native buffers/matrix are left-specific.
 if 'transitionMetres' in e:
  w=tool.source_geometry(rows[e['sourceKey']],e['lod'])[-1];low,high=e['transitionMetres']
  # Preserve non-planar corrective masks only after the whole native vertex correspondence above.
  assert len(w)>max(e['fixedVertexIndices']+e['movingVertexIndices'])
q.update(id='T66-PRIORITY-L-TIBANT-AUTHORING',side='left',subjectSourceKey=mapping[p['subjectSourceKey']],endPoseId='T66-PRIORITY-L-ANKLE-DF6P5')
q['joint']['landmark']['sourceKey']=mapping[p['joint']['landmark']['sourceKey']]
q['joint']['clearanceFixedShaftSourceKey']=mapping[p['joint']['clearanceFixedShaftSourceKey']]
q['preserveContacts']=[mapping[k] for k in p['preserveContacts']]
q['clip']['id']='T66-PRIORITY-L-TIBANT-DF6P5'
q['geometryInspection']['nativeCounterpartChecks']='work/evidence/T66/priority-ankle-knee-2026-10-05/native-counterpart.json'
q['geometryInspection']['paths']=['work/evidence/T66/priority-ankle-knee-2026-10-05/source-inspection.png']
q['geometryInspection']['selectedRegions']+=' Native left resources and instance matrices used; all source vertex/triangle correspondences verified before reusing inspected regions.'
q['unresolved'][0]='Exact ankle axis and subtalar coupling are unmeasured; this is a 6.5 degree educational sagittal approximation.'
(OUT/'native-counterpart.json').write_text(json.dumps(checks,indent=2)+'\n');(OUT/'left-tibialis').mkdir(exist_ok=True)
(OUT/'left-tibialis/input.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
# Left native instances include reflection: preserve the signed decomposition used by the shared T66 exporter.
tool.quat=signed_quat
rest,motion,record=tool.author(q)
for filename,raw in [('reference.glb',rest),('motion.glb',motion)]: (OUT/'left-tibialis'/filename).write_bytes(raw)
(OUT/'left-tibialis/authoring-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'members':len(record['members']),'bytes':len(motion),'sha256':sha(motion)}),flush=True)
