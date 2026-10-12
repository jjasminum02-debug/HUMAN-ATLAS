exec(open('work/evidence/MV2/2026-10-12-q01-r1/diagnose.py').read().split('out=[]')[0])
from author_source_surface_motion import array
from PIL import Image,ImageDraw
names={r['sourceKey']:r['name'] for r in json.loads((R/'atlas-data/source-cache/datasets/za/compiled/manifest.json').read_text())['instances']}
for side in ['left','right']:
 p=json.loads((R/f'work/evidence/T66/priority-integration-2026-10-05/adopted-knee-{side}/input.json').read_text());e=next(e for e in p['members'] if e['role']=='deforming_muscle_surface');raw,d,b=read_glb(R/f'atlas-data/assets/motion/t66-priority-s05-{side}-knee/motion.glb');tr=channel_data(d,b);nodes={n['extras']['sourceKey']:i for i,n in enumerate(d['nodes'])};n=nodes[e['sourceKey']];w=node_positions(d,b,tr,n,0);f=node_positions(d,b,tr,n,3)
 print(side, 'old fixed y',w[e['fixedVertexIndices'],1].min(),w[e['fixedVertexIndices'],1].max(),'old moving y',w[e['movingVertexIndices'],1].min(),w[e['movingVertexIndices'],1].max())
 print('highest',[(int(i),w[i].round(6).tolist()) for i in np.argsort(w[:,1])[-8:]],'lowest',[(int(i),w[i].round(6).tolist()) for i in np.argsort(w[:,1])[:8]])
 im=Image.new('RGB',(1400,1200),'white');draw=ImageDraw.Draw(im);draw.text((20,10),side+' native z/y side view. red=old moving mask; blue=old fixed. Right: emitted bent.',fill='black')
 for panel,time in enumerate([0,3]):
  def xy(v):return [(panel*700+100+float(q[2]) *2200,1100-(float(q[1])-.33)*1700) for q in v]
  for key,ni in nodes.items():
   if key!=e['sourceKey'] and not any(z in names[key] for z in ['Patella','Femur','Hip bone','Vastus']):continue
   v=node_positions(d,b,tr,ni,time);prim=d['meshes'][d['nodes'][ni]['mesh']]['primitives'][0];idx=array(d,b,prim['indices']).reshape(-1,3);pts=xy(v)
   for face in idx:draw.line([pts[i] for i in [*face,face[0]]],fill=(120,130,135) if key!=e['sourceKey'] else (30,150,125),width=1)
  for ids,col in [(e['fixedVertexIndices'],'blue'),(e['movingVertexIndices'],'red')]:
   pts=xy(w if time==0 else f)
   for i in ids:x,y=pts[i];draw.ellipse((x-2,y-2,x+2,y+2),fill=col)
 im.save(E/f'native-mask-{side}.png')
