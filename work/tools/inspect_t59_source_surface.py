#!/usr/bin/env python3
"""Wireframe review of the pinned T59 authoring validation case; no anatomy promotion."""
import sys,json,struct
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'work/tools'))
from derive_source_surface_motion import load_glb,accessor_bytes
m=json.loads((ROOT/'atlas-data/source-cache/datasets/za/compiled/manifest.json').read_text())
names=['Tibialis anterior muscle.r','Tibia.r','Fibula.r','Talus.r','Calcaneus.r','Medial cuneiform bone.r','First metatarsal bone.r','Soleus muscle.r','Extensor digitorum longus.r']
meshes=[]
for name in names:
 row=next(x for x in m['instances'] if x['sourceName']==name);res=row['lods']['detail']['resource'];doc,buf=load_glb(ROOT/f'atlas-data/source-cache/datasets/za/resources/{res}.glb');p=doc['meshes'][0]['primitives'][0];a=accessor_bytes(doc,buf,p['attributes']['POSITION']);v=np.frombuffer(a[-1],dtype='<f4').reshape(-1,3);M=np.array(row['matrix']).reshape(4,4).T;v=(np.c_[v,np.ones(len(v))]@M.T)[:,:3];a=accessor_bytes(doc,buf,p['indices']);idx=np.frombuffer(a[-1],dtype='<u2' if a[0]=='Uint16Array' else '<u4').reshape(-1,3);meshes.append((name,v,idx))
for zoom in [False,True]:
 im=Image.new('RGB',(1440,900),'#faf8f1');d=ImageDraw.Draw(im)
 for panel,axes in enumerate([(0,1),(2,1),(0,2)]):
  for i,(name,v,idx) in enumerate(meshes):
   scale=3000 if zoom else 1750
   # Foot views, anterior/sagittal/axial. actual source vertices; no landmarks asserted.
   offs=[.08,.07,.0] if zoom else [.08,.23,.0]
   xy=np.c_[(v[:,axes[0]]+offs[axes[0]])*scale+panel*480+240, -(v[:,axes[1]]-offs[axes[1]])*scale+450]
   col=['#2c9386','#b9aa85','#b9aa85','#d78937','#b9aa85','#aa64a2','#666ab3','#ca8e8a','#c78b79'][i]
   for tri in idx: d.polygon([tuple(xy[j]) for j in tri],outline=col)
   if name=='Talus.r' and zoom:
    # Indexed upper dome surface inspected against actual shape, annotate sparsely.
    candidates=np.where((v[:,1]>.079)&(v[:,2]>-.050)&(v[:,2]<-.023))[0]
    for j in candidates[::max(1,len(candidates)//9)]:
     x,y=xy[j];d.ellipse((x-3,y-3,x+3,y+3),fill='black');d.text((x+4,y),str(j),fill='black')
  d.text((panel*480+15,10),str(axes),fill='black')
 for i,(name,v,idx) in enumerate(meshes):d.text((10,30+i*17),name,fill='black')
 path=ROOT/'work/evidence/T59/resume-2026-10-02'/('source-foot.png' if zoom else 'source-leg.png');im.save(path);print(path)
for name,v,idx in meshes:
 if name=='Talus.r':
  sel=np.where((v[:,1]>.079)&(v[:,2]>-.050)&(v[:,2]<-.023))[0];print('talus dome candidates',[(int(i),v[i].round(5).tolist()) for i in sel]);
 if name=='Tibialis anterior muscle.r':print('TA lowest',[(int(i),v[i].round(5).tolist()) for i in np.argsort(v[:,1])[:12]])
