#!/usr/bin/env python3
"""Compare T43's protected workspace and OpenSim tree with its start baseline."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / 'work/evidence/T43'
baseline = json.loads((EVIDENCE / 'start-baseline.json').read_text())


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


preexisting = []
for item in baseline['preexistingChangedAndUntrackedFiles']:
    path = ROOT / item['path']
    current_hash = sha256(path) if path.is_file() else None
    preexisting.append({
        'path': item['path'],
        'exists': path.is_file(),
        'expectedSha256': item['sha256'],
        'actualSha256': current_hash,
        'unchangedFromStart': path.is_file() and current_hash == item['sha256'],
    })

protected = []
for rel, expected in baseline['protectedInputHashes'].items():
    path = ROOT / rel
    actual = sha256(path) if path.is_file() else None
    protected.append({
        'path': rel,
        'expectedSha256': expected,
        'actualSha256': actual,
        'unchanged': actual == expected,
        'intentionalT43StatusUpdate': rel == 'work/STATUS.md',
    })

models = ROOT / baseline['openSimModels']['path']
model_head = subprocess.run(
    ['git', '-C', str(models), 'rev-parse', 'HEAD'], check=True, text=True,
    capture_output=True,
).stdout.strip()
model_status = subprocess.run(
    ['git', '-C', str(models), 'status', '--short'], check=True, text=True,
    capture_output=True,
).stdout.splitlines()
tracked = subprocess.run(
    ['git', '-C', str(models), 'ls-files', '-z'], check=True, capture_output=True,
).stdout.decode().split('\0')
tracked = sorted(path for path in tracked if path)
model_hashes = [(rel, sha256(models / rel)) for rel in tracked if (models / rel).is_file()]
model_tree = hashlib.sha256()
for rel, digest in model_hashes:
    model_tree.update(rel.encode())
    model_tree.update(b'\0')
    model_tree.update(digest.encode())
    model_tree.update(b'\n')

failed_preexisting = [item for item in preexisting if not item['unchangedFromStart']]
failed_protected = [
    item for item in protected
    if not item['unchanged'] and not item['intentionalT43StatusUpdate']
]
same_opensim = model_head == baseline['openSimModels']['head'] and not model_status
result = {
    'task': 'T43',
    'checkedOn': '2026-09-27',
    'startingHead': baseline['startingHead'],
    'preexistingChangedAndUntracked': {
        'count': len(preexisting),
        'unchangedCount': sum(item['unchangedFromStart'] for item in preexisting),
        'changedOrMissing': failed_preexisting,
        'paths': preexisting,
    },
    'protectedInputs': {
        'count': len(protected),
        'unchangedCount': sum(item['unchanged'] for item in protected),
        'intentionalTaskUpdate': ['work/STATUS.md'],
        'changed': [item for item in protected if not item['unchanged']],
    },
    'openSimModels': {
        'head': model_head,
        'expectedHead': baseline['openSimModels']['head'],
        'clean': not model_status,
        'status': model_status,
        'trackedModelFileCount': len(model_hashes),
        'trackedFilesSha256': model_tree.hexdigest(),
        'sameHeadAndClean': same_opensim,
    },
    'pass': not failed_preexisting and not failed_protected and same_opensim,
}
(EVIDENCE / 'preservation-after.json').write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + '\n'
)
print(json.dumps({
    'pass': result['pass'],
    'preexistingUnchanged': len(preexisting) - len(failed_preexisting),
    'preexistingCount': len(preexisting),
    'protectedUnchanged': result['protectedInputs']['unchangedCount'],
    'protectedCount': len(protected),
    'protectedChanged': result['protectedInputs']['changed'],
    'openSimSameHeadAndClean': same_opensim,
    'modelFileCount': len(model_hashes),
}, ensure_ascii=False, indent=2))
if not result['pass']:
    raise SystemExit(1)
