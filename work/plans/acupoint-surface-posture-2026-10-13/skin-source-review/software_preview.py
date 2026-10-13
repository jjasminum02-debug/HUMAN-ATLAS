import json, numpy as np
from PIL import Image, ImageDraw
from pathlib import Path
p=Path(__import__('sys').argv[1]);d=json.loads((p/'mesh-0.json').read_text());v=np.array(d['vertices']);f=np.array(d['faces'])
v[:,2]-=v[:,2].min();v*=1.75/(v[:,2].max());v[:,:2]-=(v[:,:2].max(0)+v[:,:2].min(0))/2
verts=v[f];ns=np.cross(verts[:,1]-verts[:,0],verts[:,2]-verts[:,0]);ns/=np.maximum(np.linalg.norm(ns,axis=1)[:,None],1e-10)
W,H=400,720;scale=305;canvas=Image.new('RGB',(W*3,H),(237,241,239))
for k,(title,angle) in enumerate([('FRONT',0),('SIDE',-np.pi/2),('BACK',np.pi)]):
 rot=np.array([[np.cos(angle),-np.sin(angle),0],[np.sin(angle),np.cos(angle),0],[0,0,1]])
 rv=v@rot.T;rn=ns@rot.T;polys=rv[f]; order=np.argsort(-polys[:,:,1].mean(1))
 im=Image.new('RGB',(W*2,H*2),(237,241,239));dr=ImageDraw.Draw(im)
 light=np.array([-.3,-.7,.65]);light/=np.linalg.norm(light)
 for i in order:
  # Keep front-facing faces and use a consistent virtual light.
  if rn[i,1]>=0:continue
  intensity=.57+.40*max(0,float(np.dot(rn[i],light)))
  c=tuple(int(t*intensity) for t in (229,194,167))
  pts=[((x*scale+W/2)*2,(H-38-z*scale)*2) for x,_,z in polys[i]]
  dr.polygon(pts,fill=c)
 im=im.resize((W,H),Image.Resampling.LANCZOS);dr=ImageDraw.Draw(im);dr.text((14,16),title,fill=(43,66,62));canvas.paste(im,(k*W,0))
ImageDraw.Draw(canvas).text((15,H-17),'MakeHuman source-shape preview / not fitted to ZA / no production material',fill=(60,75,70))
canvas.save(p/'makehuman-shape-preview.png')
print(p/'makehuman-shape-preview.png')
