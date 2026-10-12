from pathlib import Path
import json
from PIL import Image,ImageDraw
E=Path(__file__).parent
selected=[]
for side in ['left','right']:
 frames=json.loads((E/f'final-{side}-loop-index.json').read_text()); ids=sorted(set([0,len(frames)-1]+list(range(0,len(frames),5))+[min(range(len(frames)),key=lambda i:abs(int(frames[i]['progress'])-p)) for p in [0,25,50,75,100]]))
 for i in ids:selected.append({'side':side,**frames[i]})
(E/'visually-reviewed-frame-selection.json').write_text(json.dumps(selected,indent=2)+'\n')
for page in range((len(selected)+11)//12):
 group=selected[page*12:(page+1)*12];out=Image.new('RGB',(1440,840),'#eef2ef');draw=ImageDraw.Draw(out)
 for n,row in enumerate(group):
  src=Image.open(E/(row['name']+'.png')).crop((266,112,940,558)).resize((360,238))
  x=(n%4)*360;y=(n//4)*280;out.paste(src,(x,y+25));draw.text((x+6,y+5),f"{row['side']} {row['name'].split('-')[-1]} {row['progress']}% {'return' if '복귀' in row['phase'] else 'action'}",fill='black')
 out.save(E/f'contact-sheet-{page+1:02}.png')
print('selected',len(selected),'pages',(len(selected)+11)//12)
