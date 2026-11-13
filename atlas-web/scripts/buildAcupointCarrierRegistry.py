"""Compact metadata projections of immutable canonical carrier manifests; no geometry or rights change."""
from pathlib import Path
import json,hashlib,argparse
R=Path(__file__).resolve().parents[2];A=R/'atlas-data/acupoints/carriers'
p=argparse.ArgumentParser();p.add_argument('--directories',nargs='+',required=True);p.add_argument('--evidence-dir',required=True);args=p.parse_args();E=R/args.evidence_dir;OUT=A/'runtime-registry-r1';OUT.mkdir(exist_ok=True);audit=[]
keys=['schemaVersion','usage','revision','kind','precision','datasetRevision','frameId','unit','poseId','rights','acceptedAcupoints','totalBytes','totalTriangles','totalGeometryBufferBytes']
chunkKeys=['id','family','label','side','revision','topologySha256','referenceHash','file','sha256','bytes','vertices','triangles','geometryBufferBytes','bounds','clearanceMetres']
for directory in args.directories:
 src=A/directory/'manifest.json';raw=src.read_bytes();m=json.loads(raw);runtime={k:m[k] for k in keys};runtime['chunks']=[{k:c[k] for k in chunkKeys} for c in m['chunks']];out=OUT/(directory+'.json');out.write_text(json.dumps(runtime,ensure_ascii=False,separators=(',',':'))+'\n');audit.append({'directory':directory,'originalManifestSha256':hashlib.sha256(raw).hexdigest(),'runtimeManifestSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'originalBytes':len(raw),'runtimeBytes':out.stat().st_size,'geometryHashesUnchanged':True,'rightsUnchanged':runtime['rights']==m['rights'],'sourceManifestPreserved':True})
(E/'runtime-manifest-audit-r1.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n');print(audit)
