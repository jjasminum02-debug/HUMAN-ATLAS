"""Actual GLB contact checks for the 16 added native distal muscles per side."""
import json,pathlib,sys,numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[4];OUT=pathlib.Path(__file__).parent
sys.path[:0]=[str(ROOT/'work/tools'),str(ROOT/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from verify_glb_interpolation import read_glb,channel_data,node_positions,bounded_inside
from author_source_surface_motion import array
from derive_source_surface_motion import sha
load=lambda p:json.loads((ROOT/p).read_text())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
b=load('atlas-data/motion/motion-learning.json');reg=load('atlas-data/motion/authoring/registry.json');accept=load('atlas-data/motion/t66-priority-action-acceptance.json')
for side in ['left','right']:
 asset=next(a for a in b['motionAssets'] if a['id']=='T66-PRIORITY-'+side[0].upper()+'-RECTUS-ASSET');raw,doc,bin=read_glb(ROOT/asset['uri']);tr=channel_data(doc,bin);nodes={n['extras']['sourceKey']:i for i,n in enumerate(doc['nodes'])};dest=OUT/('hip-complete-'+side);receipt=json.loads((dest/'context-reuse-receipt.json').read_text());rows=[]
 bones=[m['sourceKey'] for m in asset['sourceBinding']['members'] if m['role'] in ['fixed_structure','moving_structure']]
 for key in receipt['appendedNativeCoMovingSurfaces']:
  rest=node_positions(doc,bin,tr,nodes[key],0)
  for bone in bones:
   bw=node_positions(doc,bin,tr,nodes[bone],0)
   if any(rest.max(0)[j]<bw.min(0)[j]-.025 or rest.min(0)[j]>bw.max(0)[j]+.025 for j in range(3)):continue
   prim=doc['meshes'][doc['nodes'][nodes[bone]]['mesh']]['primitives'][0];tri=array(doc,bin,prim['indices']).reshape(-1,3);baseline=bounded_inside(rest,bw,tri);maximum=0
   for t in np.linspace(0,asset['clip']['durationSeconds'],65):
    maximum=max(maximum,int((bounded_inside(node_positions(doc,bin,tr,nodes[key],t),node_positions(doc,bin,tr,nodes[bone],t),tri)&~baseline).sum()))
   rows.append({'sourceKey':key,'boneSourceKey':bone,'newContainedMaximum':maximum})
 failures=[r for r in rows if r['newContainedMaximum']];print(side,len(rows),'pairs',len(failures),'failures',flush=True)
 save(dest/'appended-contact-qc.json',{'rows':rows,'failures':failures,'passed':not failures,'samples':65,'newContainmentMaximum':max([r['newContainedMaximum'] for r in rows],default=0),'motionSha256':sha(raw),'continuousCollisionFreedomClaimed':False})
 assert not failures,failures
 authorpath=next(r['path'] for r in reg['records'] if r['id']=='T66-PRIORITY-'+side[0].upper()+'-RECTUS-AUTHORING');author=load(authorpath);cp=ROOT/author['contactQcPath'];contact=json.loads(cp.read_text());contact['appendedDistalContactQcPath']=str((dest/'appended-contact-qc.json').relative_to(ROOT));contact['appendedDistalContactPairs']=len(rows);save(cp,contact)
 deps={d['path']:d for d in author['verificationDependencies']}
 for path in [author['contactQcPath'],contact['appendedDistalContactQcPath']]:deps[path]={'path':path,'sha256':sha((ROOT/path).read_bytes())}
 author['verificationDependencies']=list(deps.values());save(ROOT/authorpath,author);next(r for r in reg['records'] if r['path']==authorpath)['sha256']=sha((ROOT/authorpath).read_bytes());next(r for r in accept['rows'] if r['authoringPath']==authorpath)['authoringSha256']=sha((ROOT/authorpath).read_bytes())
save(ROOT/'atlas-data/motion/authoring/registry.json',reg);save(ROOT/'atlas-data/motion/t66-priority-action-acceptance.json',accept)
