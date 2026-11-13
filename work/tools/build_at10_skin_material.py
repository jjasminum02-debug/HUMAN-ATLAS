"""Build V1 appearance only; immutable F2 GLB and source UVs remain untouched."""
import hashlib,json,struct,shutil
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'atlas-data/anatomy/skin/at10-appearance-v1'
SRC=ROOT/'atlas-data/source-cache/datasets/skin-material-v1'
F2=ROOT/'atlas-data/anatomy/skin/at10-f2-left-foot-r1'
def sha(b):return hashlib.sha256(b).hexdigest()
def build():
 OUT.mkdir(parents=True,exist_ok=True)
 raw=(F2/'skin-candidate-f2c3.glb').read_bytes();assert sha(raw)=='07ab569e3a3a3453ed825e9bc583869394e5e94babdee7edec6b6c437836586f';n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);binary=raw[28+n:]
 def attr(i):
  a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']];return binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]
 uv=np.frombuffer(attr(2),dtype='<f4').reshape(-1,2);pos=np.frombuffer(attr(0),dtype='<f4').reshape(-1,3)
 mapping=json.loads((F2/'source-to-derived-f2c3.json').read_text());source=ROOT/'atlas-data/source-cache/datasets/skin-source-review-2026-10-13/base.obj'
 sourceuv=np.array([[float(v) for v in l.split()[1:3]] for l in source.read_text().splitlines() if l.startswith('vt ')],dtype='<f4')
 expected=sourceuv[[v['sourceUv'] for v in mapping['emittedVertices']]]
 assert np.array_equal(uv,expected),'UV source correspondence changed'
 source_img=SRC/'skins/young_asian_male/young_lightskinned_male_diffuse3.png'
 assert sha(source_img.read_bytes())=='f50016a5507fc687dc8df06599c8ea48de950cd185de33a71cafc1319ddab4d5'
 im=Image.open(source_img).convert('RGB');assert im.size==(2048,2048)
 im.save(OUT/'color.webp',quality=79,method=6)
 # Subtle high-pass relief from the real source image. This is an illustrative
 # shading cue, NOT measured displacement or a new anatomical landmark map.
 small=im.resize((1024,1024),Image.Resampling.LANCZOS)
 lum=np.asarray(small.convert('L'),dtype=float)/255
 blur=np.asarray(small.convert('L').filter(ImageFilter.GaussianBlur(2)),dtype=float)/255
 high=np.clip(lum-blur,-.08,.08)
 dy,dx=np.gradient(high);normal=np.stack([-dx*.8,dy*.8,np.ones_like(dx)],axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
 Image.fromarray(np.uint8(np.clip((normal*.5+.5)*255,0,255))).resize((512,512),Image.Resampling.LANCZOS).save(OUT/'normal.webp',lossless=True,method=6)
 # Region weights use source UV vertices and original neutral-space anatomy,
 # not guessed rectangular islands or a new skin geometry. Rasterize the
 # existing triangles to encode broad hand/foot/face roughness. Nails retain
 # source color detail; no artificial nail outline is drawn.
 from PIL import ImageDraw
 rough=Image.new('L',(1024,1024),int(.77*255));draw=ImageDraw.Draw(rough)
 indices=np.frombuffer(attr(3),dtype='<u2').reshape(-1,3)
 for tri in indices:
  c=pos[tri].mean(axis=0);r=.77
  if c[1]<.12:r=.68
  elif abs(c[0])>.20 and c[1]<1.0:r=.69
  elif c[1]>1.50:r=.72
  draw.polygon([(float(uv[i,0]*1023),float((1-uv[i,1])*1023)) for i in tri],fill=round(r*255))
 rough=rough.filter(ImageFilter.GaussianBlur(1.2));rough.convert('RGB').save(OUT/'roughness.webp',lossless=True,method=6)
 maps={}
 for kind in ['color','normal','roughness']:
  p=OUT/(kind+'.webp');img=Image.open(p);w,h=img.size
  # RGBA8 upload + exact mip chain, conservative for all maps.
  tw,th=w,h;gpu=0
  while True:
   gpu+=tw*th*4
   if tw==th==1:break
   tw=max(1,tw//2);th=max(1,th//2)
  maps[kind]={'file':p.name,'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size,'width':w,'height':h,'gpuBytes':gpu,'colorSpace':'srgb' if kind=='color' else 'linear','flipY':True}
 manifest={'schemaVersion':1,'id':'at10-skin-appearance-v1','geometrySha256':sha(raw),'uvSha256':sha(attr(2)),'uvLayout':'MakeHuman base.obj original vt; OBJ V up; flip image on bitmap decode','maps':maps,'encodedBytes':sum(v['bytes'] for v in maps.values()),'textureBytes':sum(v['gpuBytes'] for v in maps.values()),'normalScale':.35,'source':{'url':json.loads((SRC/'acquisition.json').read_text())['url'],'member':str(source_img.relative_to(SRC)),'sha256':sha(source_img.read_bytes()),'license':'CC0-1.0 per selected mhmat explicit September 2020 release','derivative':'color WebP; source high-pass illustrative normal; geometry-region roughness; no displacement'},'rights':{'localMaterialUse':'supported','wholeSkinPublicRedistribution':'held'},'geometryChanged':False,'sourceUvExactVertices':len(uv),'learnerEligible':False}
 (OUT/'material.json').write_text(json.dumps(manifest,indent=2)+'\n')
 shutil.copyfile(SRC/'skins/young_asian_male/young_asian_male.mhmat',OUT/'SOURCE-LICENSE.mhmat')
 print(json.dumps(manifest,indent=2))
if __name__=='__main__':build()
