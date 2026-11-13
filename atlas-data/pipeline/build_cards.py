"""Joint / ligament / fascia card data (ROADMAP C3).

  python3 atlas-data/pipeline/build_cards.py      (after build_runtime_v2.py and contacts_za.py)
Joint membership and joint type come from the Z-Anatomy Arthrology hierarchy; bones/muscles a structure
touches come from contacts.json; learner text comes from joint_content.py (AI-written, no human review).
Writes atlas-data/runtime/structure-cards.json keyed by runtime structure key.
"""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from joint_content import DISC_TEXT, JOINTS, KIND_TEXT, NUCLEUS_TEXT, STRUCTURES  # noqa: E402
from za_classify import slug  # noqa: E402

D1 = ROOT / 'atlas-data/source-cache/datasets/za-full'
OUT = ROOT / 'atlas-data/runtime/structure-cards.json'
GROUP = re.compile(r'^(Joints of|Synovial joints|Fibrous joints|Cartilaginous joints|Cranial (fibrous|synovial) joints|Joints$)')
JOINT_WORD = re.compile(r'joint|syndesmos|symphysis', re.I)
MAX_BONES, MAX_MUSCLES = 4, 8


def joint_of(paths):
    """(joint name, type) from the deepest Arthrology path element that names a joint."""
    for path in paths:
        if 'Arthrology' not in path: continue
        tail = path[path.index('Arthrology') + 1:]
        names = [x for x in tail if JOINT_WORD.search(x) and not GROUP.match(x)]
        if not names: continue
        text = ' '.join(tail).lower()
        kind = 'synovial' if 'synovial' in text else 'fibrous' if 'fibrous' in text or 'syndesmos' in text \
            else 'cartilaginous' if 'cartilaginous' in text or 'symphysis' in text else None
        return names[-1], kind
    return None, None


def text_for(s):
    name = s['name']
    if name in STRUCTURES: return STRUCTURES[name]
    if name.startswith('Nucleus pulposus'): return NUCLEUS_TEXT
    if name.startswith('Intervertebral disc'): return DISC_TEXT
    return KIND_TEXT.get(s['kind'])


def main():
    d1 = json.loads((D1 / 'structures.json').read_text())['structures']
    contacts = json.loads((D1 / 'contacts.json').read_text())['contacts']
    runtime = {s['id']: s for s in json.loads((ROOT / 'atlas-data/runtime/structures.json').read_text())['structures']}
    kmle_path = ROOT / 'atlas-data/terminology/joint-names-kmle.json'
    kmle = json.loads(kmle_path.read_text())['terms'] if kmle_path.exists() else {}
    visible = lambda i: i in runtime and runtime[i]['learner']['visible']
    key = lambda i: runtime[i]['key']

    joints, cards = {}, {}
    for s in d1:
        if not visible(s['id']) or runtime[s['id']]['layer'] not in ('joint', 'fascia', 'muscle'):
            continue
        if runtime[s['id']]['layer'] == 'muscle' and s['kind'] != 'tendon':
            continue
        joint, joint_type = joint_of(s['bonusPaths'])
        touch = contacts.get(s['id'], {})
        layer = runtime[s['id']]['layer']
        card = {'text': text_for(s),
                'bones': [key(b['id']) for b in touch.get('bones', []) if visible(b['id'])][:MAX_BONES] if layer == 'joint' else [],
                'muscles': [key(m['id']) for m in touch.get('muscles', []) if visible(m['id'])][:MAX_MUSCLES],
                'joint': None}
        if joint and joint in JOINTS:
            joint_key = f"joint:{slug(joint)}:{s['side']}"
            entry = joints.setdefault(joint_key, {'name': joint, 'type': joint_type, 'side': s['side'], 'members': [], 'boneVotes': {}})
            entry['members'].append(key(s['id']))
            for b in touch.get('bones', []):
                if visible(b['id']): entry['boneVotes'][key(b['id'])] = entry['boneVotes'].get(key(b['id']), 0) + b['vertices']
            card['joint'] = joint_key
        cards[key(s['id'])] = card

    for joint_key, entry in joints.items():
        modern, traditional, form, movements, summary = JOINTS[entry['name']]
        found = kmle.get(entry['name'], {})
        if found.get('status') == 'kaa_found':
            modern, traditional = found['koModern'], found['koTraditional'] or traditional
        votes = entry.pop('boneVotes')
        total = sum(votes.values()) or 1
        entry.update({'names': {'koModern': modern, 'koTraditional': traditional, 'en': entry['name']},
                      'form': form or None, 'movements': movements or None, 'summary': summary or None,
                      'bones': [k for k, n in sorted(votes.items(), key=lambda kv: -kv[1]) if n >= .05 * total][:6]})
    body = {'joints': dict(sorted(joints.items())), 'cards': dict(sorted(cards.items()))}
    revision = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    OUT.write_text(json.dumps({'schemaVersion': 1, 'revision': revision,
                               'provenance': 'membership: Z-Anatomy Arthrology; links: surface contacts; text: AI-written, human review not performed',
                               **body}, ensure_ascii=False, separators=(',', ':')) + '\n')
    print(json.dumps({'joints': len(joints), 'cards': len(cards), 'withText': sum(bool(c['text']) for c in cards.values()),
                      'withJoint': sum(bool(c['joint']) for c in cards.values()), 'withBones': sum(bool(c['bones']) for c in cards.values()),
                      'withMuscles': sum(bool(c['muscles']) for c in cards.values()), 'bytes': OUT.stat().st_size}))


if __name__ == '__main__':
    main()
