"""Validate display overlays without promoting their anatomical review status."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
catalog = json.loads((root / 'atlas-data/catalog/canonical-catalog.json').read_text())['entities']
names = json.loads((root / 'atlas-data/terminology/learning-names.json').read_text())
summaries = json.loads((root / 'atlas-data/terminology/learning-structure-summaries.json').read_text())
concept_ids = {c['id'] for c in catalog['muscleConcepts']}
claims = {c['id']: c for c in catalog['claims']}
assert len({n['id'] for n in names['entries']}) == len(names['entries'])
for n in names['entries']:
    assert n['id'] in concept_ids or n['lookupOnly'], n['id']
    assert n['label'] and n['english'] and n['sourceIds'], n['id']
    assert all(s in names['sources'] for s in n['sourceIds']), n['id']
    assert n['humanReviewed'] is False, 'T10 cannot grant human approval'
    if n['parentId']:
        assert n['parentId'] in concept_ids
assert len({(s['conceptId'], s['role']) for s in summaries}) == len(summaries)
for s in summaries:
    assert s['conceptId'] in concept_ids and s['role'] in ('origin', 'insertion')
    assert s['humanReviewed'] is False and s['sourceClaimIds']
    originals = [claims[c] for c in s['sourceClaimIds']]
    digest = hashlib.sha256(json.dumps(originals, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    assert digest == s['sourceClaimHash'], f"Stale summary: {s['conceptId']} {s['role']}"
print(json.dumps({'pass': True, 'nameEntries': len(names['entries']), 'summaries': len(summaries), 'scope': 'references and stale hashes, not anatomy approval'}))
