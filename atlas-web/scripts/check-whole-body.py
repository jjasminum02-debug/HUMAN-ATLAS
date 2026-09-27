"""Independent output accessor-byte/identity check against the input repack evidence."""
import hashlib
import json
import struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'atlas-data/source-cache/bodyparts3d-r4/converted/t56'
manifest=json.loads((D/'manifest.json').read_text())
evidence=json.loads((ROOT/'work/evidence/T56/repack.json').read_text())
seen=set(); checks=0; triangles=0
for c in manifest['chunks']:
    raw=(D/(c['id']+'.glb')).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==c['sha256'];checks+=1
    length=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+length]);b=raw[28+length:]
    assert len(g['nodes'])==len(g['scenes'][g['scene']]['nodes'])==len(c['assets']);checks+=1
    for n in g['nodes']:
        id=n['extras']['sourceFileId'];assert id not in seen;seen.add(id)
        p=g['meshes'][n['mesh']]['primitives'][0];payload=bytearray()
        for index in list(p['attributes'].values())+[p['indices']]:
            a=g['accessors'][index];v=g['bufferViews'][a['bufferView']];payload.extend(b[v['byteOffset']:v['byteOffset']+v['byteLength']])
        assert hashlib.sha256(payload).hexdigest()==evidence['geometryPayloadSha256'][id], id
        assert n['name']=='HA-MESH-BP3D4-'+id
        assert n['extras'].get('humanAnatomyReviewed', False) is False
        triangles+=g['accessors'][p['indices']]['count']//3;checks+=4
assert len(seen)==513
assets=[a for c in manifest['chunks'] for a in c['assets']]
assert sum(a['defaultVisible'] for a in assets)==481
assert sum(a['supplement'] for a in assets)==20
assert sum(a['pickState']=='existing_binding_unreviewed' for a in assets)==10
assert manifest['wholeBodyDenominator'] is None and manifest['boneRootGaps']==26
result={'status':'passed','checks':checks+5,'uniqueSourceIds':len(seen),'trianglesIncludingHeld':triangles,'defaultVisible':481,'supplementOptIn':20,'heldHidden':12,'existingBindings':10,'geometryBytesUnchanged':True}
(ROOT/'work/evidence/T56/asset-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
