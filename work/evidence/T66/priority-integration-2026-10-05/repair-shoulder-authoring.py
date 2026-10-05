"""Targeted changed-range passive context repair, not a motor claim for context muscles."""
import pathlib,sys,json,traceback,copy
R=pathlib.Path(__file__).resolve().parents[4];O=pathlib.Path(__file__).parent
sys.path.insert(0,str(R/'work/tools'))
from author_t66_family_motion import author
lat={x['side']:x for x in json.loads((O/'latissimus-passive-source-fields.json').read_text())};results=[]
for kind,side in [(k,s) for k in ['lev','rhom'] for s in ['left','right']]:
 before=O/('enlargement-'+kind+'-'+side);dest=O/('enlargement-'+kind+'-'+side+'-r2');dest.mkdir(exist_ok=True);p=json.loads((before/'input.json').read_text());p['revision']='priority-amplitude-passive-context-r2';field=lat[side];index=next(i for i,e in enumerate(p['members']) if e['sourceKey']==field['sourceKey']);p['members'][index]=copy.deepcopy(field)
 failures=[]
 for qpath in before.glob('interpolation-*.json'):
  q=json.loads(qpath.read_text())
  if not q['passed']:
   e=next(e for e in p['members'] if e['sourceKey']==q['targetSourceKey']);e['contactWeightPolicy']='source-phase-contact-and-shape-feasible-weight-fields';failures.append(q['targetSourceKey'])
 p['authoringNotes'].append('Native latissimus is passively deformed with explicit held broad axial/lower mask and native humeral end; original rigid carriage is not treated as a correct attachment model.')
 (dest/'input.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n');print(kind,side,'targeted passive fields',field['sourceKey'],failures,flush=True)
 try:
  rest,motion,record,frames=author(p);(dest/'reference.glb').write_bytes(rest);(dest/'motion.glb').write_bytes(motion);(dest/'geometry-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');result={'kind':kind,'side':side,'generated':True,'accepted':False,'range':p['family']['endDegrees'],'newPassiveLatissimusField':field['sourceKey'],'targetedContactFields':failures,'pending':'actual emitted interpolation/contact/frame/attachment/action validation'}
 except Exception as e:result={'kind':kind,'side':side,'generated':False,'accepted':False,'failure':str(e)};traceback.print_exc()
 results.append(result);(dest/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');(O/'shoulder-targeted-repair-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print(result,flush=True)
