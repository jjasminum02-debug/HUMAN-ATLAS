"""Lossless offline triangle-subset packing for registered local carrier sessions.
Keeps original world Float32 values, barycentrics, normal triangles and adjacency. Never edits source carriers.
"""
from pathlib import Path
import json,hashlib,argparse
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--out',required=True);p.add_argument('--carrier-directories',nargs='+',required=True);p.add_argument('--evidence-dir',required=True);p.add_argument('--observation-files',nargs='+',required=True);p.add_argument('--revision',default='AT8-source-subset-r12');p.add_argument('--result-stem',default='r12');args=p.parse_args();R=Path(__file__).resolve().parents[2];E=R/args.evidence_dir;d=json.loads((R/args.input).read_text());sha=lambda b:hashlib.sha256(b).hexdigest();read=lambda p:json.loads(p.read_text());used={};old={};maps={}
for directory in args.carrier_directories:
 m=read(R/'atlas-data/acupoints/carriers'/directory/'manifest.json')
 for c in m['chunks']:old[c['id']]=(directory,m,c);used[c['id']]=set()
for u in d['units']:
 for l in u['landmarks']:
  cid=l['surface'].get('carrierId',u['carrierId'])
  if cid in used:used[cid].add(l['surface']['triangle'])
 if u['rule']['kind'] in ['B-cun','F-cun','surface_fraction']:
  for s in u['rule']['path']:
   cid=s.get('carrierId',u['carrierId'])
   if cid in used:used[cid].add(s['triangle'])
for f in args.observation_files:
 for s in read(R/f)['teachingPaths']:
  if s.get('carrierId') in used:used[s['carrierId']].add(s['triangle'])
OUT=R/args.out;OUT.mkdir(exist_ok=False);base=read(R/'atlas-data/acupoints/carriers'/args.carrier_directories[0]/'manifest.json');base['revision']=args.revision;base['chunks']=[];audit=[]
for cid,faces in used.items():
 if not faces:continue
 directory,m,c=old[cid];source=R/'atlas-data/acupoints/carriers'/directory/c['file'];b=source.read_bytes();assert sha(b)==c['sha256'];v=np.frombuffer(b,dtype='<f4',count=c['vertices']*3).reshape(-1,3);ref=np.frombuffer(b,dtype='<f4',count=c['vertices']*3,offset=c['vertices']*12).reshape(-1,3);t=np.frombuffer(b,dtype='<u2',offset=c['vertices']*24).reshape(-1,3)
 # Two actual edge-neighbour rings preserve the local surface around accepted anchors and supported paths; no fill triangles.
 edges={}
 for i,tri in enumerate(t):
  for a,bb in [(tri[0],tri[1]),(tri[1],tri[2]),(tri[2],tri[0])]:edges.setdefault(tuple(sorted([int(a),int(bb)])),[]).append(i)
 for _ in range(2):
  added=set(faces)
  for i in faces:
   tri=t[i]
   for a,bb in [(tri[0],tri[1]),(tri[1],tri[2]),(tri[2],tri[0])]:added.update(edges[tuple(sorted([int(a),int(bb)]))])
  faces=added
 fi=np.array(sorted(faces));vi=np.unique(t[fi]);vinv={int(k):i for i,k in enumerate(vi)};tt=np.array([[vinv[int(k)] for k in tri] for tri in t[fi]],dtype='<u4');vv=v[vi];rr=ref[vi];content=vv.tobytes()+rr.tobytes()+tt.astype('<u2').tobytes();file=cid+'.bin';(OUT/file).write_bytes(content);mapping={int(old):i for i,old in enumerate(fi)};maps[cid]=mapping
 new=dict(c,id=cid,revision=args.revision,file=file,vertices=len(vv),triangles=len(tt),bytes=len(content),geometryBufferBytes=len(content),sha256=sha(content),topologySha256=sha(vv.tobytes()+tt.tobytes()),referenceHash=sha(rr.tobytes()+tt.tobytes()),bounds=[vv.min(0).tolist(),vv.max(0).tolist()]);base['chunks'].append(new)
 d['inputs']['carriers'][cid]={**d['inputs']['carriers'][cid],'revision':new['revision'],'topologySha256':new['topologySha256'],'positions':vv.ravel().tolist(),'indices':tt.ravel().tolist()};audit.append({'carrierId':cid,'sourceFile':str(source.relative_to(R)),'originalFileHash':c['sha256'],'originalTopologyHash':c['topologySha256'],'packedTopologyHash':new['topologySha256'],'originalVertexIds':vi.tolist(),'originalTriangleIds':fi.tolist(),'oldBytes':c['bytes'],'packedBytes':len(content),'oldTriangles':c['triangles'],'packedTriangles':len(tt),'worldFloat32AndReferenceBitsUnchanged':bool(vv.tobytes()==v[vi].tobytes() and rr.tobytes()==ref[vi].tobytes()),'fillTriangles':0})
for u in d['units']:
 for l in u['landmarks']:
  cid=l['surface'].get('carrierId',u['carrierId'])
  if cid in maps:l['surface']['triangle']=maps[cid][l['surface']['triangle']]
 if u['rule']['kind'] in ['B-cun','F-cun','surface_fraction']:
  for s in u['rule']['path']:
   cid=s.get('carrierId',u['carrierId'])
   if cid in maps:s['triangle']=maps[cid][s['triangle']]
 if u['carrierId'] in maps:
  refs=[u['relationEvidenceId'],u['surfaceEvidenceId']]+[l['evidenceId'] for l in u['landmarks']]+[r['evidenceId'] for r in u.get('observedReferences',[])]
  if u['rule']['kind'] in ['B-cun','F-cun','surface_fraction']:refs.append(u['rule']['evidenceId'])
  for ev in d['inputs']['evidence']:
   if ev['id'] in refs:ev['carrierHash']=d['inputs']['carriers'][u['carrierId']]['topologySha256'];ev['originalText']+=' [Lossless carrier packing: original anatomical text/addresses preserved; surface triangle index remapped with immutable original-face map; world positions unchanged.]'
for k,n in [('totalBytes','bytes'),('totalTriangles','triangles'),('totalGeometryBufferBytes','geometryBufferBytes')]:base[k]=sum(c[n] for c in base['chunks'])
base['derivation']='Lossless original triangle subset with2 shared-edge neighbour rings; actual source/address maps retained in development evidence. No smoothing, scale, skin claim or hole fill.';(OUT/'manifest.json').write_text(json.dumps(base,ensure_ascii=False,indent=2)+'\n');(E/('carrier-compaction-'+args.result_stem+'.json')).write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n');(E/('rules-'+args.result_stem+'.json')).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n');print({'oldBytes':sum(a['oldBytes'] for a in audit),'packedBytes':base['totalBytes'],'packedTriangles':base['totalTriangles'],'carriers':len(audit)})
