import json
from pathlib import Path
from PIL import Image,ImageDraw
E=Path(__file__).parent
for side in ['left','right']:
 names=['paired-before-'+side+'-max','after-left-max-settled' if side=='left' else 'paired-after-right-max'];im=Image.new('RGB',(1280,600),'white');draw=ImageDraw.Draw(im)
 for i,n in enumerate(names):
  v=Image.open(E/(n+'.png')).crop((266,116,940,556)).resize((640,418));im.paste(v,(i*640,60));draw.text((i*640+20,15),'ORIGINAL' if i==0 else 'REPAIRED (same camera)',fill='black');d=json.loads((E/(n+'.json')).read_text());s=json.loads(d['canvas'][0]['dataset']['scene']);draw.text((i*640+15,495),side+' / max prepared / 19.5 deg unchanged',fill='black');draw.text((i*640+15,525),'camera '+str([round(x,6) for x in s['camera']]),fill='black')
 im.save(E/('comparison-'+side+'.png'))
 pairs=[]
 for i in [3,11,18,23,31,40]:
  p=E/f'after-{side}-cycle-{i}.png';d=json.loads(p.with_suffix('.json').read_text());pairs.append((p,d['phase'],d['progress']))
 im=Image.new('RGB',(1348,1500),'white');dr=ImageDraw.Draw(im)
 for i,(p,phase,progress) in enumerate(pairs):
  x=(i%2)*674;y=(i//2)*500;im.paste(Image.open(p).crop((266,116,940,556)),(x,y+35));dr.text((x+10,y+10),side+' progress '+str(progress)+' / frame '+p.stem.split('-')[-1],fill='black')
 im.save(E/('cycle-review-'+side+'.png'))
