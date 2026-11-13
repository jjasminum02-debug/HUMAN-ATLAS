"""One-time migration input for D2: snapshot the pre-v2 composed runtime (Z-Anatomy rows only).

The old dev-server composition (BodyParts3D supplement + overlays + nerve scene) produced the learner
rows and geometry the app shows today. This copies exactly what it served, so v2 can keep names,
content keys, chunk bytes, resource keys and matrices identical (motion playback checks all of them).

  python3 atlas-data/pipeline/freeze_legacy_runtime.py --server http://127.0.0.1:5173
Requires the pre-v2 dev server. Writes atlas-data/runtime/legacy/runtime-2026-11-03.json and chunk files
into atlas-data/source-cache/datasets/za-v2/chunks/.
"""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / 'atlas-data/runtime/legacy/runtime-2026-11-03.json'
CHUNKS = ROOT / 'atlas-data/source-cache/datasets/za-v2/chunks'


def get(server, path):
    with urllib.request.urlopen(server + path) as response:
        return response.read()


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--server', default='http://127.0.0.1:5173')
    server = parser.parse_args().server
    integration = json.loads(get(server, '/__atlas/integration.json'))
    manifest = json.loads(get(server, '/__atlas/datasets/human-atlas-local/manifest.json'))
    keep = lambda ns: ns != 'bp3d-r4'  # BodyParts3D rows were inspection-only; v2 drops them
    instances = [i for i in manifest['instances'] if keep(i.get('sourceNamespace'))]
    keys = {i['sourceKey'] for i in instances}
    rows = [r for r in integration['objects'] if r['sourceKey'] in keys]
    chunks = [c for c in manifest['chunks'] if keep(c.get('sourceNamespace'))]
    resources = {i['lods'][level]['resource'] for i in instances for level in ('overview', 'detail')}
    CHUNKS.mkdir(parents=True, exist_ok=True)
    for chunk in chunks:
        data = get(server, chunk['url'])
        assert hashlib.sha256(data).hexdigest() == chunk['sha256'] and len(data) == chunk['bytes'], chunk['id']
        (CHUNKS / f"{chunk['sha256']}.glb").write_bytes(data)
    snapshot = {'schemaVersion': 1, 'frozenFrom': 'pre-v2 composed dev runtime (git tag pre-reset-2026-11-03 + D1)',
                'datasetRevision': manifest['sourceRevisions']['za-c7010a9'], 'policy': integration['policy'],
                # Identity values that motion, acupoint and skin bindings were made against.
                'compat': {'datasetRevision': manifest['revision'], 'frameContract': manifest['frameContract'],
                           'sourceRevisions': {'za-c7010a9': manifest['sourceRevisions']['za-c7010a9']},
                           'integrationRevision': integration['revision'], 'sourceComponents': integration['sourceComponents'],
                           'sourceOverlaySha256': integration['sourceOverlaySha256'], 'rightsEvidenceSha256': integration['rightsEvidenceSha256'],
                           'rightsDecisionId': integration['policy']['rightsDecisionId']},
                'rows': rows, 'instances': instances, 'chunks': chunks,
                'resources': {k: v for k, v in manifest['resources'].items() if k in resources}}
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(snapshot, ensure_ascii=False, separators=(',', ':')) + '\n')
    print(json.dumps({'rows': len(rows), 'instances': len(instances), 'chunks': len(chunks),
                      'chunkBytes': sum(c['bytes'] for c in chunks), 'out': str(OUT_JSON.relative_to(ROOT))}))


if __name__ == '__main__':
    main()
