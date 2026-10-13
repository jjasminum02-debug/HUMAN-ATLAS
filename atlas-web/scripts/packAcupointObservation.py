"""Lossless deterministic gzip delivery; native coordinates and original JSON survive unchanged."""
from pathlib import Path
import argparse,json,gzip,hashlib,shutil,re
p=argparse.ArgumentParser();p.add_argument('--channels',nargs='+',required=True);p.add_argument('--evidence-dir',required=True);a=p.parse_args()
R=Path(__file__).resolve().parents[2];A=R/'atlas-data/acupoints';E=R/a.evidence_dir;E.mkdir(exist_ok=True);registry=A/'learner/registry-r1.json';d=json.loads(registry.read_text());audit=[];prepared=[]
# Preflight every package before any output is replaced or the registry switches revisions.
for r in d['packages']:
 if r['channel'] not in a.channels:continue
 assert re.fullmatch(r'[a-z0-9-]+\.json',r['observationFile']),'Already packed or invalid source file'
 sourceName=r['observationFile'];source=A/'observation'/sourceName;raw=source.read_bytes();packed=gzip.compress(raw,compresslevel=9,mtime=0);name=sourceName[:-5]+'.bin';out=A/'observation'/name
 assert not out.exists() and not (E/sourceName).exists(),'Output/evidence exists; use a new revision'
 assert gzip.decompress(packed)==raw
 prepared.append((r,source,sourceName,out,packed,raw))
assert prepared,'No matching unpacked package'
for r,source,sourceName,out,packed,raw in prepared:
 out.write_bytes(packed);shutil.copyfile(source,E/sourceName);source.unlink();r.update(observationFile=out.name,observationEncoding='gzip',observationSha256=hashlib.sha256(packed).hexdigest())
 audit.append({'channel':r['channel'],'file':out.name,'encodedBytes':len(packed),'decodedBytes':len(raw),'decodedSha256':hashlib.sha256(raw).hexdigest(),'encodedSha256':r['observationSha256'],'decodedBytesBitIdentical':True,'sourceEvidenceFile':sourceName})
registry.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');(E/'delivery-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n');print(audit)
