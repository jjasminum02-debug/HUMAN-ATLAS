"""Author 30-percent candidate ranges from fixed native shoulder family inputs.

Prior accepted weights and attachment masks are retained as starting engineering
inputs; these candidates are never registered by this script.
"""
import pathlib,sys,json,copy,traceback
R=pathlib.Path(__file__).resolve().parents[4];O=pathlib.Path(__file__).parent
sys.path.insert(0,str(R/'work/tools'))
from author_t66_family_motion import author
load=lambda p:json.loads((R/p).read_text())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
results=[]
for kind,side in [(k,s) for k in ['lev','rhom'] for s in ['left','right']]:
 ar=load('atlas-data/motion/authoring/t66-priority-s03-'+side[0]+'-'+kind+'-authoring.json');geo=load(ar['geometryRecordPath']);dep=next(d for d in ar['verificationDependencies'] if d['path'].endswith('/input.json'));p=copy.deepcopy(load(dep['path']));d=O/('enlargement-'+kind+'-'+side);d.mkdir(exist_ok=True);before=p['family']['endDegrees'];p['family']['endDegrees']=before*1.3;p['family']['validatedAuthoringLimitDegrees']=abs(before*1.3);p['family']['rangeMeaning']='30-percent larger candidate authored teaching range, not measured normal ROM or accepted until emitted QC';p['id']='T66-S05-'+kind.upper()+'-'+side.upper()+'-AMPLITUDE-CANDIDATE';p['revision']='priority-amplitude-candidate-r1'
 # Retain actual accepted free-vertex fields instead of resolving the same old
 # masks from scratch. Contact at the changed range still requires fresh QC.
 fields={r['sourceKey']:r for r in geo['surfaceMetrics'] if 'authoredFinalWeights' in r}
 for e in p['members']:
  if e['sourceKey'] in fields:
   e['weights']=fields[e['sourceKey']]['authoredFinalWeights'];e['contactWeightPolicy']='preserve-authored-mask-transition'
 save(d/'input.json',p);print(kind,side,'authoring candidate',before,'->',p['family']['endDegrees'],flush=True)
 try:
  rest,motion,record,frames=author(p);(d/'reference.glb').write_bytes(rest);(d/'motion.glb').write_bytes(motion);save(d/'geometry-record.json',record);result={'kind':kind,'side':side,'generated':True,'accepted':False,'bytes':len(motion),'previousEndDegrees':before,'endDegrees':p['family']['endDegrees'],'required':'actual emitted interpolation/context/attachment/action QC'}
 except Exception as e:
  result={'kind':kind,'side':side,'generated':False,'accepted':False,'status':'blocked_engineering','failure':str(e)};traceback.print_exc()
 save(d/'result.json',result);results.append(result);save(O/'shoulder-enlargement-probes.json',results);print(result,flush=True)
