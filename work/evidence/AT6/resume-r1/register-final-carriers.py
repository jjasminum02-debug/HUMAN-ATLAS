from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[4];E=Path(__file__).parent;root=R/'atlas-data/acupoints/carriers';out=root/'lung-AT6-r1';assert not out.exists();out.mkdir();doc=json.loads((E/'bilateral-rules-r5.json').read_text());ids={u['carrierId'] for u in doc['units']};chunks=[];components=[]
for v in ['lung-local-r2','lung-local-r3','lung-local-r6','lung-local-r7','lung-fossa-r1']:
 p=root/v/'manifest.json';m=json.loads(p.read_text())
 for c in m['chunks']:
  if c['id'] not in ids:continue
  data=(p.parent/c['file']).read_bytes();assert hashlib.sha256(data).hexdigest()==c['sha256'];(out/c['file']).write_bytes(data);chunks.append(c);components.append({'id':c['id'],'sourceEdition':v,'sourceManifestSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'binarySha256':c['sha256']})
base=json.loads((root/'education-r1/manifest.json').read_text());manifest={k:v for k,v in base.items() if k not in ['chunks','totalBytes','totalTriangles','totalGeometryBufferBytes']};manifest.update(revision='AT6-active-local-carriers-r1',chunks=chunks,totalBytes=sum(c['bytes'] for c in chunks),totalTriangles=sum(c['triangles'] for c in chunks),totalGeometryBufferBytes=sum(c['geometryBufferBytes'] for c in chunks),components=components,method='AT2 native-envelope path for wrist/thenar/thumb/chest plus a source-addressed local fossa teaching membrane. All are authored coarse geometry, not skin. No body source copy.')
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
(E/'carrier-registration-r1.json').write_text(json.dumps({'output':str(out.relative_to(R)),'activeChunks':len(chunks),'totalBytes':manifest['totalBytes'],'totalTriangles':manifest['totalTriangles'],'components':components,'archivedCandidateDirectory':'work/evidence/AT6/resume-r1/carrier-candidates'},indent=2)+'\n')
archive=E/'carrier-candidates';archive.mkdir()
for p in root.glob('lung-local-r*'):
 if p.is_dir():shutil.move(str(p),str(archive/p.name))
shutil.move(str(root/'lung-fossa-r1'),str(archive/'lung-fossa-r1'))
for edition in ['r2','r3']:
 p=R/f'atlas-data/acupoints/learner/lung-{edition}.json';shutil.move(str(p),str(E/f'learner-candidate-{edition}.json'))
print('registered',len(chunks),manifest['totalBytes'],manifest['totalTriangles'])
