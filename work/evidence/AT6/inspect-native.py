from pathlib import Path
import ast,json,hashlib,struct
import numpy as np
R=Path(__file__).resolve().parents[3];E=Path(__file__).parent; A=R/'work/evidence/acupoint-AC1'
read=lambda p:json.loads(p.read_text()); sha=lambda b:hashlib.sha256(b).hexdigest()
cache=R/'atlas-data/source-cache/datasets/za';inputs={};meshes={}
fn=next(n for n in ast.parse((A/'build_carrier.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='world');exec(compile(ast.Module(body=[fn],type_ignores=[]),'AC1-world','exec'),globals())
rows={r['sourceKey']:r for r in read(A/'runtime-integration.json')['objects']}
names=['Clavicle','First rib','Second rib','Scapula','Long head of biceps brachii','Short head of biceps brachii','Radius','Scaphoid bone','Abductor pollicis longus','Extensor pollicis brevis','First metacarpal bone']
manifest=read(R/'atlas-data/acupoints/carriers/education-r1/manifest.json')
audit={'sourceInputs':inputs,'objects':[],'carrierChunks':[],'sideIndependent':True,'pointsAccepted':0}
for side in ['right','left']:
 for name in names:
  match=[(k,r) for k,r in rows.items() if r['side']==side and r['names']['en']==name];assert len(match)==1,(name,side)
  k,r=match[0];v,t=world(k);audit['objects'].append({'sourceKey':k,'name':name,'side':side,'vertices':len(v),'triangles':len(t),'bounds':[v.min(axis=0).tolist(),v.max(axis=0).tolist()],'sourceHold':r['hardHoldReasons']})
 for c in manifest['chunks']:
  if c['id'] not in [f'arm-{side}-0',f'arm-{side}-1',f'hand-{side}-0',f'finger-{side}-1-0',f'nail-fold-{side}-3-0']:continue
  b=(R/'atlas-data/acupoints/carriers/education-r1'/c['file']).read_bytes();assert sha(b)==c['sha256'];v=np.frombuffer(b,dtype='<f4',count=c['vertices']*3).reshape(-1,3);t=np.frombuffer(b,dtype='<u2',offset=c['vertices']*24).reshape(-1,3)
  audit['carrierChunks'].append({'id':c['id'],'side':side,'hash':c['topologySha256'],'actualYRange':[float(v[:,1].min()),float(v[:,1].max())],'vertices':len(v),'triangles':len(t)})
# Actual native triangles, not extrema or point coordinate transfer. Persist a bounded wrist cross-section inspection.
for side in ['right','left']:
 selected={k:world(k) for k,r in rows.items() if r['side']==side and r['names']['en'] in ['Radius','Scaphoid bone','Abductor pollicis longus','Extensor pollicis brevis']}
 out=[]
 for k,(v,t) in selected.items():
  tri=v[t];ids=np.flatnonzero((tri[:,:,1].min(axis=1)<=.874)&(tri[:,:,1].max(axis=1)>=.850))
  out.append({'sourceKey':k,'name':rows[k]['names']['en'],'triangles':[{'triangle':int(i),'vertices':tri[i].tolist()} for i in ids]})
 (E/f'wrist-{side}-native-section.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
(E/'native-inspection.json').write_text(json.dumps(audit,indent=2)+'\n');print('native objects',len(audit['objects']),'surface chunks',len(audit['carrierChunks']),'input files',len(inputs))
