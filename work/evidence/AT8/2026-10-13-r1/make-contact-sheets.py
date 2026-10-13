from pathlib import Path
import json
from PIL import Image,ImageDraw
E=Path(__file__).parent;R=E.parents[3];accepted={(i['code'],i['side']) for ch in ['li','te'] for p in json.loads((R/f'atlas-data/acupoints/learner/{ch}-r1.json').read_text())['projections'] for i in p['instances']};fs=[]
for ch in ['LI','TE']:
 for s in ['right','left']:
  for i in range(1,21 if ch=='LI' else 24):
   code=ch+str(i);f=E/f'screens/1440-{s}-{code}.png'
   if (code,s) in accepted:assert f.exists();fs.append(f)
for j in range(0,len(fs),8):
 canvas=Image.new('RGB',(1440,1848),'white');draw=ImageDraw.Draw(canvas)
 for k,f in enumerate(fs[j:j+8]):
  im=Image.open(f).convert('RGB');im.thumbnail((720,450));x=(k%2)*720;y=(k//2)*462;canvas.paste(im,(x,y+12));draw.text((x+5,y),f.name,fill='black')
 canvas.save(E/f'contact-supported-{j//8+1}.jpg',quality=92)
print('supported sheets',len(fs));print('all saved screens',len(list((E/'screens').glob('1440-*.png'))))
