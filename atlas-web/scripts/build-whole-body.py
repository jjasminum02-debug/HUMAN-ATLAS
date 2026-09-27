"""T56 local-only, byte-preserving regional/layer repack. Never publishes sources."""
import copy
import hashlib
import json
import struct
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'atlas-data/source-cache/bodyparts3d-r4/converted/t56'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(rel):
    raw = (ROOT / rel).read_bytes()
    return json.loads(raw), sha(raw)


def merge():
    paths = [f'atlas-data/manifests/bodyparts3d-r4-t{n}/{f}' for n, f in [(70, 'integration-manifest.json'), (71, 'integration-manifest.json'), (72, 'integration-extension.json')]]
    pairs = [load(p) for p in paths]
    parent, parent_hash = pairs[0]
    assets = {a['sourceElementFileId']: a for a in parent['assets']}
    chunks = {c['chunkId']: c for c in parent['localQaChunks']}
    for doc, _ in pairs[1:]:
        assert doc['parentIntegrationManifest']['sha256'] == parent_hash, 'parent hash mismatch'
        for key in ['projectFrame', 'projectUnit', 'sourceId', 'pose']:
            assert doc['sceneContract'][key] == parent['sceneContract'][key], f'frame contract {key}'
        for a in doc['assets']:
            key = a['sourceElementFileId']
            if key in assets:
                assert assets[key] == a, f'historical asset drift: {key}'
            else:
                assert a['learnerPickState'] == 'source_only_unbound' and not a['existingLearnerStableIds']
                assert not a['learnerDefaultVisible'] and not a['humanAnatomyReviewed']
                assets[key] = a
        for c in doc['localQaChunks']:
            key = c['chunkId']
            if key in chunks:
                assert chunks[key] == c, f'historical chunk drift: {key}'
            chunks[key] = c
    sibling = pairs[2][0]['siblingPackageReferences'][0]
    assert pairs[1][1] in json.dumps(sibling), 'sibling hash mismatch'
    assert len(assets) == 513 and len(chunks) == 14
    return assets, chunks, dict(zip(paths, [p[1] for p in pairs]))


def build():
    assets, chunks, inputs = merge()
    groups = defaultdict(list)
    seen = set()
    payload_hashes = {}
    for chunk in chunks.values():
        raw = (ROOT / chunk['localQaGlbPath']).read_bytes()
        assert sha(raw) == chunk['glbSha256'], 'GLB hash mismatch'
        length = struct.unpack_from('<I', raw, 12)[0]
        doc = json.loads(raw[20:20+length])
        binary = raw[28+length:]
        assert doc['scene'] == 0 and len(doc['scenes']) == 1
        for node_index in doc['scenes'][0]['nodes']:
            node = doc['nodes'][node_index]
            source_id = node['extras']['sourceFileId']
            if source_id in chunk['suppressDuplicateSourceElementFileIds']:
                continue
            assert source_id not in seen, f'duplicate {source_id}'
            seen.add(source_id)
            a = assets[source_id]
            assert node['name'] == a['renderNodeId'] and node['extras']['sourceSha256'] == a['sourceSha256']
            assert not any(k in node for k in ['children', 'matrix', 'translation', 'rotation', 'scale', 'skin']), 'unsupported transform'
            layer = 'bone' if any('bone' in s for s in a['sourceClassCandidates']) else 'muscle'
            regions = a['productRegionIdsFromHistoricalPackages'] or a.get('candidateProductRegionIds', [])
            assert regions, f'no region: {source_id}'
            # No inferred depth or canonical identity: group only existing regional observations and layer.
            key = (regions[0], layer, a['primaryPackage'] in ['T71', 'T72'])
            mesh = doc['meshes'][node['mesh']]
            assert len(mesh['primitives']) == 1
            primitive = mesh['primitives'][0]
            assert set(primitive) <= {'attributes', 'indices', 'mode'}
            bounds = doc['accessors'][primitive['attributes']['POSITION']]
            entry = {'id': source_id, 'nodeId': a['renderNodeId'], 'sourceSha256': a['sourceSha256'], 'regions': regions,
                     'side': node['extras'].get('lateralityFromExactSourceHeader', node['extras'].get('laterality')), 'layer': layer, 'defaultVisible': a['learnerDefaultVisible'], 'supplement': key[2],
                     'pickState': a['learnerPickState'], 'stableIds': a['existingLearnerStableIds'],
                     'holdReasons': a['holdReasons'], 'humanReviewed': a['humanAnatomyReviewed'],
                     'bounds': [bounds['min'], bounds['max']]}
            if entry['stableIds']:
                assert entry['side'] in ['left', 'right', 'midline'], 'bound source side required'
            groups[key].append((node, mesh, doc, binary, entry))
    assert seen == set(assets)
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {'version': 1, 'frame': 'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR', 'unit': 'm',
                'localOnly': True, 'publicRedistribution': 'held', 'lodLevels': 1, 'wholeBodyDenominator': None,
                'boneRootGaps': 26, 'firstPassResidual': 0, 'inputs': inputs, 'chunks': []}
    for index, (key, entries) in enumerate(sorted(groups.items())):
        result = {'asset': {'version': '2.0', 'generator': 'T56 byte-preserving local repack'}, 'scene': 0,
                  'scenes': [{'nodes': []}], 'nodes': [], 'meshes': [], 'accessors': [], 'bufferViews': [], 'buffers': []}
        data = bytearray()
        for node, mesh, doc, binary, entry in entries:
            new_node = copy.deepcopy(node)
            new_node['mesh'] = len(result['meshes'])
            result['scenes'][0]['nodes'].append(len(result['nodes']))
            result['nodes'].append(new_node)
            new_mesh = copy.deepcopy(mesh)
            p = new_mesh['primitives'][0]
            original = mesh['primitives'][0]
            original_bytes = bytearray()
            for target, old in [(k, v) for k, v in original['attributes'].items()] + [('indices', original['indices'])]:
                accessor = copy.deepcopy(doc['accessors'][old])
                assert 'sparse' not in accessor
                view = copy.deepcopy(doc['bufferViews'][accessor['bufferView']])
                part = binary[view.get('byteOffset', 0):view.get('byteOffset', 0)+view['byteLength']]
                original_bytes.extend(part)
                view['byteOffset'] = len(data)
                view['buffer'] = 0
                data.extend(part)
                data.extend(b'\0' * (-len(data) % 4))
                accessor['bufferView'] = len(result['bufferViews'])
                result['bufferViews'].append(view)
                new_index = len(result['accessors'])
                result['accessors'].append(accessor)
                if target == 'indices': p['indices'] = new_index
                else: p['attributes'][target] = new_index
            payload_hashes[entry['id']] = sha(original_bytes)
            result['meshes'].append(new_mesh)
        result['buffers'] = [{'byteLength': len(data)}]
        header = json.dumps(result, separators=(',', ':')).encode()
        header += b' ' * (-len(header) % 4)
        glb = struct.pack('<4sII', b'glTF', 2, 28+len(header)+len(data)) + struct.pack('<I4s', len(header), b'JSON') + header + struct.pack('<I4s', len(data), b'BIN\0') + data
        name = f'{index:02d}-{key[0]}-{key[1]}-{int(key[2])}'
        (OUT / f'{name}.glb').write_bytes(glb)
        manifest['chunks'].append({'id': name, 'url': f'/__atlas/body/{name}.glb', 'sha256': sha(glb),
                                   'bytes': len(glb), 'assets': [e[4] for e in entries]})
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    evidence = {'inputs': inputs, 'sourceChunks': len(chunks), 'uniqueSourceIds': len(assets),
                'chunks': len(groups), 'bytes': sum(c['bytes'] for c in manifest['chunks']),
                'geometryPayloadSha256': payload_hashes, 'outputManifestSha256': sha((OUT/'manifest.json').read_bytes()),
                'outputSha256': {c['id']: c['sha256'] for c in manifest['chunks']}}
    (ROOT/'work/evidence/T56/repack.json').write_text(json.dumps(evidence, indent=2)+'\n')
    print(json.dumps({k:v for k,v in evidence.items() if k not in ['geometryPayloadSha256','outputSha256','inputs']}))

if __name__ == '__main__':
    build()
