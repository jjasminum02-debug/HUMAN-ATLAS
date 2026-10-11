from pathlib import Path
import ast,json,hashlib,struct
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[4];E=Path(__file__).parent;A=R/'work/evidence/acupoint-AC1';cache=R/'atlas-data/source-cache/datasets/za'
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest();inputs={};meshes={}
rows={r['sourceKey']:r for r in read(A/'runtime-integration.json')['objects']}
fn=next(n for n in ast.parse((A/'build_carrier.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='world');exec(compile(ast.Module(body=[fn],type_ignores=[]),'AC1-reader','exec'),globals())
def find(name,side):
 ks=[k for k,r in rows.items() if r['side']==side and r['names']['en']==name];assert len(ks)==1,(name,side);return ks[0]
def native(name,side):return world(find(name,side))
def plot(names,side,region,box):
 specs=[(name,find(name,side),native(name,side)) for name in names];img=Image.new('RGB',(1500,850),'white');d=ImageDraw.Draw(img)
 colors=['#cd8848','#786baa','#68a8a0','#cb5959','#5475ad','#aa9850','#78905f','#8f4f75']
 for panel,dims in enumerate([(0,1),(2,1),(0,2)]):
  pts=np.concatenate([v for _,_,(v,t) in specs]);lo,hi=pts[:,dims].min(axis=0),pts[:,dims].max(axis=0)
  if box and panel==0:lo,hi=np.array(box[0]),np.array(box[1])
  scale=min(440/(hi[0]-lo[0]),690/(hi[1]-lo[1]));shift=np.array([panel*500+25,770]);
  def screen(v):return ((v[list(dims)]-lo)*[scale,-scale]+shift).tolist()
  draw=[]
  for j,(name,k,(v,t)) in enumerate(specs):
   for i,tri in enumerate(v[t]):
    if box and panel==0 and (tri[:,dims].max(axis=0)<lo).any() or box and panel==0 and (tri[:,dims].min(axis=0)>hi).any():continue
    draw.append((float(tri[:,3-sum(dims)].mean()),[screen(p) for p in tri],colors[j%len(colors)]))
  for _,p,color in sorted(draw):d.polygon([tuple(x) for x in p],fill=color,outline=color)
  d.text((panel*500+20,10),f'{side} {region}: axes {dims}',fill='black')
  for j,(name,k,(v,t)) in enumerate(specs):d.text((panel*500+20,30+j*15),f'{j} {name}',fill=colors[j%len(colors)])
  # Sparse face numbers make the observed geometry addressable, not bounds-point proposals.
  for j,(name,k,(v,t)) in enumerate(specs):
   stride=max(1,len(t)//60)
   for i in range(0,len(t),stride):
    p=screen(v[t[i]].mean(axis=0))
    if panel*500<p[0]<(panel+1)*500 and 170<p[1]<800:d.text(tuple(p),f'{j}:{i}',fill='black')
 img.save(E/f'inspect-{region}-{side}.png')
for side in ['right','left']:
 plot(['First metacarpal bone','Abductor pollicis brevis','Scaphoid bone','Abductor pollicis longus','Extensor pollicis brevis'],side,'hand',None)
 plot(['Radius','Ulna','Long head of biceps brachii','Brachioradialis muscle'],side,'arm',None)
 plot(['Clavicle','First rib','Second rib','Scapula','Clavicular head of pectoralis major muscle','Clavicular part of deltoid muscle'],side,'chest',None)
(E/'inspection-input-hashes.json').write_text(json.dumps(inputs,indent=2)+'\n')
