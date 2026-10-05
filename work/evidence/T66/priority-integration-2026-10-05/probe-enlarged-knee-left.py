import pathlib,sys,json,traceback
R=pathlib.Path(__file__).resolve().parents[4];O=pathlib.Path(__file__).parent/'enlargement-knee-left-r4';O.mkdir(exist_ok=True)
sys.path.insert(0,str(R/'work/tools'))
from author_t66_family_motion import author
from derive_source_surface_motion import sha
p=json.loads((R/'work/evidence/T66/priority-ankle-knee-2026-10-05/knee-extension-left/input.json').read_text())
p['id']='T66-PRIORITY-INTEGRATION-KNEE-L-ENLARGEMENT-PROBE';p['family']['endDegrees']=19.5;p['family']['validatedAuthoringLimitDegrees']=19.5
p['family']['rangeMeaning']='candidate authored teaching range, not accepted until emitted QC; requested 1.3x previous 15-degree trajectory'
src=json.loads((R/'atlas-data/source-cache/datasets/za/compiled/manifest.json').read_text())['instances'];names={x['sourceKey']:x['name'] for x in src}
for e in p['members']:
 if names[e['sourceKey']] in ['Semimembranosus muscle.l','Medial head of gastrocnemius.l']:e['contactWeightPolicy']='source-phase-contact-and-shape-feasible-weight-fields'
(O/'input.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')
try:
 rest,motion,record,frames=author(p)
 (O/'reference.glb').write_bytes(rest);(O/'motion.glb').write_bytes(motion);(O/'geometry-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');result={'generated':True,'accepted':False,'bytes':len(motion),'sha256':sha(motion),'pending':'actual emitted intermediate/context/action QC'}
except Exception as e:
 result={'generated':False,'accepted':False,'status':'blocked_engineering','failureType':type(e).__name__,'failure':str(e)};traceback.print_exc()
(O/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result),flush=True)
