from pathlib import Path
E=Path(__file__).parent
exec((E/'prepare-local-carriers.py').read_text().split('regions=[]')[0])
valid=lambda r:not r['hardHoldReasons'] and (r['kind'] in ['muscle','bone'] or 'fascia' in r['names']['en'].lower())
regions=[]
for side in ['right','left']:
 src=[k for k,r in rows.items() if valid(r) and r['side']==side and 'upper-limb' in r['regionIds'] and r['bounds'][1][1]>.757 and r['bounds'][0][1]<.796]
 regions.append({'id':f'mcp-link-{side}','family':'hand','side':side,'sources':src,'axis':[find(n,side) for n in ['Second metacarpal bone','Third metacarpal bone','Fourth metacarpal bone','Proximal phalanx of second finger of hand','Proximal phalanx of fourth finger of hand']],'range':[.757,.796],'angles':96,'steps':32,'limit':.08,'cuts':[],'labels':['손허리손가락 관절의 국소 체표'],'clearanceMetres':.003,'maxEdgeMetres':.009})
neck=[k for k,r in rows.items() if valid(r) and set(r['regionIds'])&{'neck','head','thorax','back'} and r['bounds'][1][1]>1.515 and r['bounds'][0][1]<1.546 and r['bounds'][0][0]>-.16 and r['bounds'][1][0]<.16]
regions.append({'id':'neck-upper-link','family':'head','side':'midline','sources':neck,'axis':[find(n,None) for n in ['Axis (C2)','Vertebra C3']],'range':[1.515,1.546],'angles':96,'steps':26,'limit':.13,'cuts':[],'labels':['턱각 높이 목빗근 국소 경계'],'clearanceMetres':.004,'maxEdgeMetres':.012})
girdle=[k for k,r in rows.items() if valid(r) and set(r['regionIds'])&{'upper-limb','thorax','back','neck'} and r['bounds'][1][1]>1.38 and r['bounds'][0][1]<1.44]
regions.append({'id':'girdle-link','family':'trunk','side':'midline','sources':girdle,'axis':[find(n,None) for n in ['Vertebra C7','Vertebra T1','Vertebra T2','Vertebra T3','Vertebra T4']],'range':[1.38,1.44],'angles':128,'steps':40,'limit':.3,'cuts':[],'labels':['견갑대 위 경계 국소 체표'],'clearanceMetres':.004,'maxEdgeMetres':.015})
(E/'boundary-links-inputs-r1.json').write_text(json.dumps({'regions':regions,'unsupportedRegions':['auricle-native-landmarks','finger-web-margin'],'regionMethod':'AT2 existing source-bound surface intersections; static non-scan educational patches'},ensure_ascii=False,indent=2)+'\n')
