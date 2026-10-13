from pathlib import Path
import runpy,json
E=Path(__file__).parent;g=runpy.run_path(str(E/'native-reader.py'));R=g['R'];rows=g['rows'];find=g['find']
def valid(r):return not r['hardHoldReasons'] and (r['kind'] in ['muscle','bone'] or 'fascia' in r['names']['en'].lower())
regions=[]
for side in ['right','left']:
 sources=[k for k,r in rows.items() if valid(r) and r['side']==side and 'upper-limb' in r['regionIds'] and r['bounds'][1][1]>.762 and r['bounds'][0][1]<.866]
 regions.append({'id':f'hand-link-{side}','side':side,'sources':sources,'axis':[find(n,side) for n in ['Second metacarpal bone','Third metacarpal bone','Fourth metacarpal bone','Fifth metacarpal bone','Radius','Scaphoid bone']],'range':[.772,.852],'angles':56,'steps':42,'limit':.08,'cuts':[],'labels':['손등·손허리 관절 경계'],'clearanceMetres':.003,'maxEdgeMetres':.012})
neck=[k for k,r in rows.items() if valid(r) and set(r['regionIds'])&{'neck','head','thorax','back'} and r['bounds'][1][1]>1.423 and r['bounds'][0][1]<1.54 and r['bounds'][0][0]>-.16 and r['bounds'][1][0]<.16]
regions.append({'id':'neck-link','side':'midline','sources':neck,'axis':[find(f'Vertebra C{i}',None) for i in range(3,8)]+[find('Vertebra T1',None)],'range':[1.426,1.518],'angles':64,'steps':42,'limit':.13,'cuts':[],'labels':['목 근육·후두 구조 모형 경계'],'clearanceMetres':.004,'maxEdgeMetres':.018})
(E/'local-carrier-inputs-r1.json').write_text(json.dumps({'regions':regions,'unsupportedRegions':['auricle-lobule-tragus','precise-skin-fold','deforming-pose'],'regionMethod':'AT2/3/4 native section and outer surface intersections; no synthetic full body'},ensure_ascii=False,indent=2)+'\n');print([(c['id'],len(c['sources'])) for c in regions])
