"""Recover the exact pre-guard candidate from preserved accessor/buffer data."""
import pathlib,sys,json,copy
R=pathlib.Path(__file__).resolve().parents[4];O=pathlib.Path(__file__).parent;d=O/'enlargement-trunk/flex';sys.path[:0]=[str(R/'work/tools'),str(R/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from verify_glb_interpolation import read_glb
from author_source_surface_motion import container
from derive_source_surface_motion import sha
raw,doc,b=read_glb(d/'motion.glb');receipt=json.loads((d/'native-exterior-guard-receipt.json').read_text());repair=json.loads((d/'repair-receipt.json').read_text());doc=copy.deepcopy(doc);nodes={n['extras']['sourceKey']:i for i,n in enumerate(doc['nodes'])};anim=doc['animations'][0]
samplers=[i for i,s in enumerate(anim['samplers']) if doc['accessors'][s['input']]['count']==65 and doc['accessors'][s['output']]['count']==65*64]
old_indices=samplers[:-len(receipt['changedSourceKeys'])];keys=[r['sourceKey'] for r in repair['targetedRepairs']];assert len(old_indices)==len(keys)==3
for key,si in zip(keys,old_indices):
 ni=nodes[key];ai=anim['samplers'][si]['input'];prim=doc['meshes'][doc['nodes'][ni]['mesh']]['primitives'][0];n=doc['accessors'][prim['attributes']['POSITION']]['count'];targets=[{'POSITION':ai-128+2*i,'NORMAL':ai-127+2*i} for i in range(64)];assert all(doc['accessors'][p['POSITION']]['count']==n for p in targets);prim['targets']=targets;channel=next(c for c in anim['channels'] if c['target']=={'node':ni,'path':'weights'});channel['sampler']=si
old_count=len(doc['accessors'])-130*len(receipt['changedSourceKeys']);first=doc['accessors'][old_count];first_view=first['bufferView'];end=doc['bufferViews'][first_view]['byteOffset'];doc['accessors']=doc['accessors'][:old_count];doc['bufferViews']=doc['bufferViews'][:first_view];anim['samplers']=anim['samplers'][:max(old_indices)+1];recovered=container(doc,bytearray(b[:end]));assert sha(recovered)==receipt['oldMotionSha256'],(sha(recovered),receipt['oldMotionSha256'])
(O/'failed-exterior-guard.glb').write_bytes(raw);(d/'motion.glb').write_bytes(recovered);(d/'pre-guard-recovery-receipt.json').write_text(json.dumps({'failedCandidateSha256':sha(raw),'restoredCandidateSha256':sha(recovered),'matchesExactPreGuardFileHash':True,'originalSourceAndRegisteredAssetsModified':False},indent=2)+'\n');print('exact pre-guard candidate recovered',sha(recovered))
