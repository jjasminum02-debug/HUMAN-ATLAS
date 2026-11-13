"""Select core skin members using byte ranges; never download/execute the whole pack."""
import io,json,zipfile,urllib.request,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
URL='https://files.makehumancommunity.org/asset_packs/makehuman_system_assets/makehuman_system_assets_cc0.zip'
SIZE=280737770
OUT=ROOT/'atlas-data/source-cache/datasets/skin-material-v1'
class Remote(io.RawIOBase):
 def __init__(self): self.pos=0;self.ranges=[]
 def seekable(self):return True
 def seek(self,n,w=0):self.pos=n if w==0 else self.pos+n if w==1 else SIZE+n;return self.pos
 def tell(self):return self.pos
 def read(self,n=-1):
  if n<0:n=SIZE-self.pos
  if not n:return b''
  end=min(SIZE,self.pos+n)-1
  req=urllib.request.Request(URL,headers={'Range':f'bytes={self.pos}-{end}'})
  with urllib.request.urlopen(req,timeout=45) as r:
   if r.status!=206 or r.headers.get('Content-Range')!=f'bytes {self.pos}-{end}/{SIZE}':raise ValueError('Unexpected range/source revision')
   b=r.read();self.ranges.append([self.pos,end,hashlib.sha256(b).hexdigest()]);self.pos+=len(b);return b
if __name__=='__main__':
 OUT.mkdir(parents=True,exist_ok=True);f=Remote();records=[]
 with zipfile.ZipFile(f) as z:
  names=z.namelist()
  selected=[n for n in names if n=='packs/makehuman_system_assets.json' or (any(n.startswith('skins/'+c+'/') for c in ['young_asian_male','young_caucasian_male2']) and n.endswith(('.png','.mhmat')))]
  for name in selected:
   p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
   if not p.exists():p.write_bytes(z.read(name))
   b=p.read_bytes();records.append({'member':name,'crc32':z.getinfo(name).CRC,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()});print(name,len(b),flush=True)
 (OUT/'acquisition.json').write_text(json.dumps({'url':URL,'archiveBytes':SIZE,'selected':records,'readRanges':f.ranges,'wholeArchiveDownloaded':False},indent=2)+'\n')
