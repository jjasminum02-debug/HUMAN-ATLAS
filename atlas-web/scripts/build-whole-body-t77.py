"""T77 locked-input local repack. Historical source packages remain immutable."""
import copy
import hashlib
import json
import struct
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'atlas-data/source-cache/bodyparts3d-r4/converted/t77'


def sha(data):
    return hashlib.sha256(data).hexdigest()


NON_VISIBILITY_HOLDS = {'not_canonical_learner_binding', 'no_canonical_learner_binding', 'human_anatomy_review_not_performed', 'public_redistribution_held'}
POLICY = ROOT / 'atlas-data/manifests/bodyparts3d-r4-t77'

def merge():
    import importlib.util
    spec = importlib.util.spec_from_file_location('t56_repack', ROOT/'atlas-web/scripts/build-whole-body.py')
    old = importlib.util.module_from_spec(spec); spec.loader.exec_module(old)
    inputs = json.loads((POLICY/'input-lock.json').read_text())
    for path, expected in inputs.items():
        assert sha((ROOT/path).read_bytes()) == expected, f'Locked input drift: {path}'
    assets, chunks, _ = old.merge()
    parent = json.loads((ROOT/'atlas-data/manifests/bodyparts3d-r4-t70/integration-manifest.json').read_text())
    parent_hash = inputs['atlas-data/manifests/bodyparts3d-r4-t70/integration-manifest.json']
    for task in [74, 75, 76, 92]:
        doc = json.loads((ROOT/f'atlas-data/manifests/bodyparts3d-r4-t{task}/integration-extension.json').read_text())
        assert doc['parentIntegrationManifest']['sha256'] == parent_hash
        for key in ['projectFrame', 'projectUnit', 'sourceId', 'pose']:
            assert doc['sceneContract'][key] == parent['sceneContract'][key], key
        for a in doc['assets']:
            id = a['sourceElementFileId']
            if id in assets: assert assets[id] == a, f'history drift {id}'
            else:
                assert a['primaryPackage'] == f'T{task}'
                assert not a['learnerDefaultVisible'] and a['learnerPickState'] == 'source_only_unbound'
                assert not a['existingLearnerStableIds'] and not a['humanAnatomyReviewed']
                assets[id] = a
        for c in doc['localQaChunks']:
            id = c['chunkId']
            if id in chunks: assert chunks[id] == c, f'chunk drift {id}'
            chunks[id] = c
    assert len(assets) == 543 and len(chunks) == 18
    # Individual source rows and raw hashes are required, even for previous opt-in assets.
    source_rows = {}
    for task in [71, 72, 74, 75, 76, 92]:
        path = f'atlas-data/manifests/bodyparts3d-r4-t{task}/source-manifest.json'
        doc = json.loads((ROOT/path).read_text())
        for row in doc['sourceAssets']:
            id = row['sourceElementFileId']
            if assets[id]['primaryPackage'] != f'T{task}': continue
            row = dict(row); row['_manifest'] = path
            source_rows[id] = row
    baseline = json.loads((ROOT/'atlas-data/source-cache/bodyparts3d-r4/converted/t56/manifest.json').read_text())
    historical = {a['id']: a for c in baseline['chunks'] for a in c['assets']}
    decisions = {}
    for id, a in sorted(assets.items()):
        before = a['learnerDefaultVisible']
        integrity = sorted(set(a['holdReasons']) - NON_VISIBILITY_HOLDS)
        evidence = []
        side = historical.get(id, {}).get('side')
        eligible = before
        if id in source_rows:
            row = source_rows[id]
            assert row['sourceSha256'] == a['sourceSha256']
            assert row['projectFrame'] == parent['sceneContract']['projectFrame']
            assert row.get('sourcePose', row.get('pose')) in [parent['sceneContract']['pose'], 'bodyparts3d-r4-static-reference; no standardized articulated pose asserted']
            assert row['sourceVertexCount'] > 0 and row['sourceTriangleCount'] > 0
            raw_paths = list((ROOT / f"atlas-data/source-cache/bodyparts3d-r4/mesh/{a['primaryPackage'].lower()}").rglob(f"{id}.obj"))
            assert len(raw_paths) == 1, f"exact raw path {id}"
            raw_path = raw_paths[0]
            assert sha(raw_path.read_bytes()) == a['sourceSha256'], f'raw hash {id}'
            side = next((row.get(k) for k in ['explicitSourceSide','exactSourceSideFromHeader','sideFromExactOfficialConceptRelation','lateralityFromExplicitOfficialRelation','lateralityFromExactSourceName'] if row.get(k)), None)
            assert side in ['left','right',None,'not_stated','unspecified','not_lateralized_by_exact_source_name','not_lateralized_by_official_relations']
            if side in ['not_stated','unspecified','not_lateralized_by_exact_source_name','not_lateralized_by_official_relations']: side = None
            evidence = [row['_manifest'], f"work/evidence/{a['primaryPackage']}/validation.json"]
            # Existing local technical surface use only: does not resolve redistribution or review.
            eligible = not integrity and a['localQaRender'] == 'available_source_surface'
        if integrity or a['learnerPickState'] == 'held': eligible = False
        decisions[id] = {'beforeDefaultVisible': before, 'afterDefaultVisible': eligible,
            'state': 'allowed' if eligible else 'held', 'sourceSide': side,
            'runtimeSide': historical[id]['side'] if id in historical else side,
            'sourceSha256': a['sourceSha256'], 'integrityHolds': integrity,
            'evidenceIds': evidence, 'retainedHoldReasons': a['holdReasons'],
            'bindingState': a['learnerPickState'], 'publicRedistribution': 'held', 'humanReviewed': False,
            'basis': 'verified_local_source_context_only' if not before and eligible else 'preserved_historical_policy'}
    assert sum(x['afterDefaultVisible'] for x in decisions.values()) == 531
    (POLICY/'display-policy.json').write_text(json.dumps({'revision':'T77-local-display-v1','notPublicReleaseApproval':True,'items':decisions},indent=2)+'\n')
    return assets, chunks, inputs, decisions


def build():
    assets, chunks, inputs, decisions = merge()
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
            key = (regions[0], layer, a['primaryPackage'] in ['T71', 'T72', 'T74', 'T75', 'T76', 'T92'])
            mesh = doc['meshes'][node['mesh']]
            assert len(mesh['primitives']) == 1
            primitive = mesh['primitives'][0]
            assert set(primitive) <= {'attributes', 'indices', 'mode'}
            bounds = doc['accessors'][primitive['attributes']['POSITION']]
            entry = {'id': source_id, 'nodeId': a['renderNodeId'], 'sourceSha256': a['sourceSha256'], 'regions': regions,
                     'side': decisions[source_id]['runtimeSide'], 'layer': layer, 'defaultVisible': decisions[source_id]['afterDefaultVisible'], 'supplement': key[2],
                     'pickState': a['learnerPickState'], 'stableIds': a['existingLearnerStableIds'],
                     'holdReasons': a['holdReasons'], 'humanReviewed': a['humanAnatomyReviewed'],
                     'bounds': [bounds['min'], bounds['max']], 'localDisplay': decisions[source_id],
                     'publicRedistribution': 'held', 'sourcePackage': a['primaryPackage']}
            if entry['stableIds']:
                assert entry['side'] in ['left', 'right', 'midline'], 'bound source side required'
            groups[key].append((node, mesh, doc, binary, entry))
    assert seen == set(assets)
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {'version': 2, 'frame': 'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR', 'unit': 'm',
                'localOnly': True, 'publicRedistribution': 'held', 'lodLevels': 1, 'wholeBodyDenominator': None,
                'historicalT72BoneRootGaps': 26, 'firstPassResidual': 0, 'visualCoverage': 'partial',
                'missingTargets': [{'name': 'latissimus dorsi', 'state': 'missing', 'decision': 'T94:no_exact_source_found', 'geometry': None, 'binding': None}], 'inputs': inputs, 'chunks': []}
    for index, (key, entries) in enumerate(sorted(groups.items())):
        result = {'asset': {'version': '2.0', 'generator': 'T77 byte-preserving local repack'}, 'scene': 0,
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
    (ROOT/'work/evidence/T77/repack.json').write_text(json.dumps(evidence, indent=2)+'\n')
    print(json.dumps({k:v for k,v in evidence.items() if k not in ['geometryPayloadSha256','outputSha256','inputs']}))

if __name__ == '__main__':
    build()
