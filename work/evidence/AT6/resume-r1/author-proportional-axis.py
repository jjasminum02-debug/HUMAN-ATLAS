from pathlib import Path
import json
E=Path(__file__).parent;d=json.loads((E/'bilateral-rules-r7.json').read_text());e={i['id']:i for i in d['inputs']['evidence']};changes=[]
for u in d['units']:
 r=u['rule']
 if r['kind']!='B-cun':continue
 r['measurementAxis']={'from':r['from'],'to':r['to']};ev=e[r['evidenceId']];ev['measurementAxis']='anatomical_native_axis';ev['originalText']+=' The source-addressed native endpoint axis defines anatomical longitudinal proportional measurement. The connected surface path is registration only: select its unique intersection with the measured plane. Its circumferential detour length is not a body-proportional ruler. The reference endpoints are authored static skin-fold correspondences; precise skin measurement remains unresolved.'
 changes.append(u['id'])
with (E/'bilateral-rules-r8.json').open('x') as f:json.dump(d,f,ensure_ascii=False,separators=(',',':'));f.write('\n')
with (E/'proportional-axis-authoring-r1.json').open('x') as f:json.dump({'changedUnits':changes,'basis':'WHO p12 anatomical interval units9 axillary-to-cubital,12 cubital-to-wrist; source-addressed native endpoints, not whole-body bounds','surfaceRole':'connected unique plane crossing registration only','noGateRelaxation':True},f,indent=2);f.write('\n')
