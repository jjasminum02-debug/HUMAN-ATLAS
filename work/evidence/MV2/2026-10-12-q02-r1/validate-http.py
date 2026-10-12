from pathlib import Path
import json,hashlib,urllib.request,urllib.error,sys
E=Path(__file__).parent;uri=json.loads((E/'original-glb-structure.json').read_text())['uri'];url='http://127.0.0.1:5183/'+uri
with urllib.request.urlopen(url) as response:
 data=response.read();result={'url':url,'status':response.status,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'headers':dict(response.headers)}
assert result['bytes']==31306820 and result['sha256']=='fd09265a937bebff65f0d1b095bc2d0350f13b7222e53a90c32bb40b80c43adf'
etag=next(v for k,v in result['headers'].items() if k.lower()=='etag')
try:urllib.request.urlopen(urllib.request.Request(url,headers={'If-None-Match':etag}))
except urllib.error.HTTPError as error:result['cachedStatus']=error.code
assert result['cachedStatus']==304
(E/(sys.argv[1] if len(sys.argv)>1 else 'actual-http-delivery.json')).write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k!='headers'})
