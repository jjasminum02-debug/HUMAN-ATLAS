"""Native nail-to-distal-phalanx component correspondence, not acupoint approval."""
from pathlib import Path
import ast,struct,json,hashlib
import numpy as np
R=Path(__file__).resolve().parents[3];E=Path(__file__).parent;A=R/'work/evidence/acupoint-AC1'
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
rows={r['sourceKey']:r for r in read(A/'runtime-integration.json')['objects']};cache=R/'atlas-data/source-cache/datasets/za';inputs={};meshes={}
tree=ast.parse((A/'build_carrier.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='world');exec(compile(ast.Module(body=[fn],type_ignores=[]),'AC1-world','exec'),globals())
config=read(R/'atlas-data/acupoints/carriers/education-special-inputs.json');out=[]
for item in config['probeInputs']:
 if 'nail-' not in item['key'].lower() and 'toenail-' not in item['key'].lower():continue
 obj=next(o for o in read(R/item['path'])['objects'] if o['name']==item['object']);v=np.array(obj['positions']);t=np.array(obj['indices'])[item['triangleIds']];pts=v[np.unique(t)];centroid=pts.mean(axis=0)
 family='foot' if '(foot)' in item['object'] else 'hand'
 bones=[k for k,r in rows.items() if r['side']==item['side'] and r['names']['en'].startswith('Distal phalanx') and r['names']['en'].endswith('of '+family) and k.startswith('ZA-c7010a9-')]
 distances=[]
 for k in bones:
  p,_=world(k);d=np.linalg.norm(p-centroid,axis=1);i=int(d.argmin());distances.append((float(d[i]),k,i))
 distance,key,index=min(distances);assert distance<.014,(item['key'],distance)
 assert np.all(pts[:,0]<0) if item['side']=='right' else np.all(pts[:,0]>0)
 out.append({'probeComponent':item['key'],'nativeObject':item['object'],'side':item['side'],'componentVertices':len(pts),'componentTriangles':len(t),'actualBounds':[pts.min(axis=0).tolist(),pts.max(axis=0).tolist()], 'nearestDistalPhalanx':key,'phalanxName':rows[key]['names']['en'],'nativeVertex':index,'distanceMetres':distance,'grade':'independent native component spatial correspondence; nail corners and pads not palpation validated','mirror':False})
for family in ['Nail plate','Perionyx','Nail plate (foot)','Perionyx (foot)']:
 for side,suffix in [('right','.r'),('left','.l')]:
  match=[o for o in out if o['nativeObject']==family+suffix];assert len(match)==5 and len({o['nearestDistalPhalanx'] for o in match})==5,(family,side)
(E/'nail-landmark-validation.json').write_text(json.dumps({'status':'passed','matchedComponents':len(out),'oneToOneFiveDigitsPerObject':True,'frame':'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR','unit':'m','sourceInputs':inputs,'components':out,'acupointsApproved':0,'leftMirror':False},ensure_ascii=False,indent=2)+'\n')
print('matched',len(out),'max distance',max(o['distanceMetres'] for o in out))
