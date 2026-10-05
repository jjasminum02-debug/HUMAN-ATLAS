"""Add required morph bounds metadata without changing binary geometry/animation.
Reuse interpolation/contact results only after exact binary equality verification.
"""
import pathlib,sys,json,numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[4]; OUT=pathlib.Path(__file__).parent
sys.path[:0]=[str(ROOT/'work/tools'),str(ROOT/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from verify_glb_interpolation import read_glb
from author_source_surface_motion import array,container
from derive_source_surface_motion import sha
load=lambda p:json.loads((ROOT/p).read_text())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
b=load('atlas-data/motion/motion-learning.json'); reg=load('atlas-data/motion/authoring/registry.json'); acc=load('atlas-data/motion/t66-priority-action-acceptance.json');outcomes=load(str((OUT/'hip-context-outcome.json').relative_to(ROOT))); receipts=[]
for side in ['left','right']:
 a=next(a for a in b['motionAssets'] if a['id']=='T66-PRIORITY-'+side[0].upper()+'-RECTUS-ASSET'); dest=OUT/('hip-complete-'+side);raw,doc,binary=read_glb(ROOT/a['uri']); oldsha=sha(raw); changes=0
 for mesh in doc['meshes']:
  for prim in mesh['primitives']:
   for target in prim.get('targets',[]):
    if 'POSITION' in target:
     accessor=doc['accessors'][target['POSITION']]; values=array(doc,binary,target['POSITION']); accessor['min']=values.min(0).tolist();accessor['max']=values.max(0).tolist();changes+=1
 new=container(doc,bytearray(binary))
 (ROOT/a['uri']).write_bytes(new);(dest/'motion.glb').write_bytes(new);_,newdoc,newbinary=read_glb(ROOT/a['uri']); assert binary==newbinary
 a['sha256']=sha(new)
 authorpath=next(r['path'] for r in reg['records'] if r['id']=='T66-PRIORITY-'+side[0].upper()+'-RECTUS-AUTHORING');author=load(authorpath);author['motionSha256']=sha(new)
 corrections=load(str((dest/'distal-contact-correctives.json').relative_to(ROOT)));bykey={r['sourceKey']:r for r in corrections}
 for m in a['sourceBinding']['members']:
  if m['sourceKey'] in bykey:m['passiveCorrectiveMaxMetres']=float(bykey[m['sourceKey']]['maximumLocalCorrectiveMetres'])*1.001
 for path in [author['geometryRecordPath'],author['glbPoseQcPath'],str((dest/'appended-contact-qc.json').relative_to(ROOT)),*author['glbInterpolationQcPaths'].values()]:
  q=load(path)
  for key in ['motionSha256','motionGlbSha256']:
   if key in q:q[key]=sha(new)
  q['binaryIdenticalMetadataReuse']=True; save(ROOT/path,q)
 pose=load(author['glbPoseQcPath'])
 for row in pose['rows']:
  if row.get('geometryQcPath'):row['geometryQcSha256']=sha((ROOT/row['geometryQcPath']).read_bytes())
 save(ROOT/author['glbPoseQcPath'],pose)
 for dep in author['verificationDependencies']:
  if dep['path'].startswith(str(OUT.relative_to(ROOT))) or dep['path']==a['uri']:dep['sha256']=sha((ROOT/dep['path']).read_bytes())
 save(ROOT/authorpath,author)
 next(o for o in outcomes if o['assetId']==a['id'])['motionSha256']=sha(new)
 receipts.append({'side':side,'beforeSha256':oldsha,'afterSha256':sha(new),'binarySha256':sha(binary),'binaryIdentical':True,'changedPositionAccessorMetadata':changes,'passiveCorrectiveSurfaces':len(bykey),'geometryAndAnimationUnchanged':True})
save(OUT/'hip-context-outcome.json',outcomes)
for side in ['left','right']:
 ap=next(r['path'] for r in reg['records'] if r['id']=='T66-PRIORITY-'+side[0].upper()+'-RECTUS-AUTHORING');author=load(ap)
 for dep in author['verificationDependencies']:
  if dep['path']==author['actionOutcomePath']:dep['sha256']=sha((ROOT/dep['path']).read_bytes())
 save(ROOT/ap,author);next(r for r in reg['records'] if r['path']==ap)['sha256']=sha((ROOT/ap).read_bytes());next(r for r in acc['rows'] if r['authoringPath']==ap).update(motionSha256=author['motionSha256'],authoringSha256=sha((ROOT/ap).read_bytes()),outcomeSha256=sha((ROOT/author['actionOutcomePath']).read_bytes()))
for path,v in [('atlas-data/motion/motion-learning.json',b),('atlas-data/motion/authoring/registry.json',reg),('atlas-data/motion/t66-priority-action-acceptance.json',acc)]:save(ROOT/path,v)
save(OUT/'hip-metadata-reuse-receipt.json',receipts)
print(json.dumps(receipts))
