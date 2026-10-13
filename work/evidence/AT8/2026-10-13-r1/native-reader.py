"""Read-only AC1 world reader reused; no external coordinate or source write."""
from pathlib import Path
import json,hashlib,ast,struct
import numpy as np
R=Path(__file__).resolve().parents[4];E=Path(__file__).parent;A=R/'work/evidence/acupoint-AC1';cache=R/'atlas-data/source-cache/datasets/za'
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest();inputs={};meshes={}
rows={r['sourceKey']:r for r in read(A/'runtime-integration.json')['objects'] if r['sourceKey'].startswith('ZA-c7010a9-')}
fn=next(n for n in ast.parse((A/'build_carrier.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='world');exec(compile(ast.Module(body=[fn],type_ignores=[]),'AC1-reader','exec'),globals())
def find(name,side):
 ks=[k for k,r in rows.items() if r['side']==side and r['names']['en']==name];assert len(ks)==1,(name,side);return ks[0]
def inspect():
 names=['Humerus','Radius','Ulna','Scapula','Second metacarpal bone','Fourth metacarpal bone','Fifth metacarpal bone','Proximal phalanx of second finger of hand','Sternocleidomastoid muscle','Nasalis muscle','Orbicularis oris muscle','Orbital part of orbicularis oculi','Temporal bone','Cricoid cartilage','Thyroid cartilage','Mandible']
 out=[]
 for name in names:
  for side in ['right','left',None]:
   try:k=find(name,side)
   except AssertionError:continue
   v,t=world(k);centres=v[t].mean(axis=1)
   out.append({'sourceKey':k,'name':name,'side':side,'fileHash':inputs,'topologyHash':sha(v.astype('<f4').tobytes()+t.astype('<u4').tobytes()),'bounds':[v.min(0).tolist(),v.max(0).tolist()],'extremeFacets':{f'{axis}-{end}':{'triangle':int(getattr(np,'arg'+end)(centres[:,axis])),'world':centres[getattr(np,'arg'+end)(centres[:,axis])].tolist()} for axis in range(3) for end in ['min','max']}})
 (E/'native-inspection-r1.json').write_text(json.dumps({'observations':out,'inputHashes':inputs,'earSources':[r['names']['en'] for r in rows.values() if any(s in r['names']['en'].lower() for s in ['auricle','auricular','pinna','tragus','ear lobe'])]},ensure_ascii=False,indent=2)+'\n')
 print([(o['name'],o['side'],o['bounds']) for o in out if o['side'] in ['right',None]])
if __name__=='__main__':inspect()
