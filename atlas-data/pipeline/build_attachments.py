"""Attachment areas per muscle for the viewer (ROADMAP C4).

  python3 atlas-data/pipeline/build_attachments.py
Z-Anatomy draws each muscle's origin (.ol/.or) and insertion (.el/.er) as patch meshes on the bone; D1 extracted them
(705) and relations.json links each patch to its owner muscles and bone. This writes, per visible muscle, the patch
structure keys the app draws on the bone when the muscle is selected: atlas-data/runtime/attachments.json.
Muscles without patches are listed in the file's `missing` (filled by contact later, see `contact` rows).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / 'atlas-data/runtime'


def main():
    structures = json.loads((RUNTIME / 'structures.json').read_text())['structures']
    relations = json.loads((RUNTIME / 'relations.json').read_text())['relations']
    by_id = {s['id']: s for s in structures}
    visible = {s['id'] for s in structures if s['learner']['visible'] and s['layer'] == 'muscle'}
    muscles = {}
    for r in relations:
        if r['type'] not in ('origin', 'insertion'): continue
        patch = by_id.get(r['from'])
        if not patch or not patch.get('geometry'): continue
        bone = by_id.get(r.get('bone') or '')
        for owner in r['owners']:
            if owner not in visible: continue
            muscles.setdefault(by_id[owner]['key'], []).append({'key': patch['key'], 'role': r['type'], 'bone': bone['key'] if bone else None, 'source': 'za'})
    for rows in muscles.values(): rows.sort(key=lambda x: (x['role'] != 'origin', x['key']))
    missing = sorted(by_id[i]['key'] for i in visible if by_id[i]['key'] not in muscles)
    doc = {'schemaVersion': 1, 'note': 'Z-Anatomy origin/insertion patches per muscle (build_attachments.py)', 'muscles': muscles, 'missing': missing}
    (RUNTIME / 'attachments.json').write_text(json.dumps(doc, ensure_ascii=False, separators=(',', ':')) + '\n')
    print('ATTACHMENTS', json.dumps({'muscles': len(muscles), 'patches': sum(len(v) for v in muscles.values()), 'missing': len(missing),
                                     'originOnly': sum(1 for v in muscles.values() if {x['role'] for x in v} == {'origin'}),
                                     'insertionOnly': sum(1 for v in muscles.values() if {x['role'] for x in v} == {'insertion'})}))


if __name__ == '__main__':
    main()
