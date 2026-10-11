from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[4];E=Path(__file__).parent;root=R/'atlas-data/acupoints/carriers';out=root/'lung-AT6-r2';assert not out.exists();out.mkdir();doc=json.loads((E/'bilateral-rules-r6.json').read_text());ids={u['carrierId'] for u in doc['units']};chunks=[];components=[]
for edition in ['lung-AT6-r1','nail-indicator-r1']:
 p=root/edition/'manifest.json';m=json.loads(p.read_text())
 for c in m['chunks']:
  if c['id'] not in ids:continue
  data=(p.parent/c['file']).read_bytes();assert hashlib.sha256(data).hexdigest()==c['sha256'];(out/c['file']).write_bytes(data);chunks.append(c);components.append({'id':c['id'],'sourceEdition':edition,'sourceManifestSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'binarySha256':c['sha256']})
base=json.loads((root/'education-r1/manifest.json').read_text());manifest={k:v for k,v in base.items() if k not in ['chunks','totalBytes','totalTriangles','totalGeometryBufferBytes']};manifest.update(revision='AT6-active-local-carriers-r2',chunks=chunks,totalBytes=sum(c['bytes'] for c in chunks),totalTriangles=sum(c['triangles'] for c in chunks),totalGeometryBufferBytes=sum(c['geometryBufferBytes'] for c in chunks),components=components,method='Shared AT2 native-envelope path for local wrist/thenar/chest plus tiny source-addressed fossa and nail teaching membranes. Not a skin scan. Native thumb IP geometry is compiler-only calibration; no coarse thumb target is registered.')
assert len(chunks)==10
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');(E/'carrier-registration-r2.json').write_text(json.dumps({'output':str(out.relative_to(R)),'activeChunks':len(chunks),'totalBytes':manifest['totalBytes'],'totalTriangles':manifest['totalTriangles'],'components':components},indent=2)+'\n')
for edition in ['lung-AT6-r1','nail-indicator-r1']:shutil.move(str(root/edition),str(E/'carrier-candidates'/edition))
shutil.move(str(R/'atlas-data/acupoints/learner/lung-r4.json'),str(E/'learner-candidate-r4.json'))
print(len(chunks),manifest['totalBytes'],manifest['totalTriangles'])
