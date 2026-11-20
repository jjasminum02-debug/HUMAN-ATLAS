"""Correct the origin/insertion role of Z-Anatomy attachment patches against the card text (2026-11-20).

Z-Anatomy names each patch .o (origin) or .e (insertion), but for some muscles the names are the other way round
(pectoralis minor: its rib patches are .e and the coracoid patch .o). The card text (learner-attachment-context.json,
built from the two-source muscle cards) says which bones the origin and the insertion are on. A patch whose bone the
card puts only under the other role takes that role; a bone the card does not name, or names under both, is left alone.
Contact-estimated rows (build_attachment_contacts.py) took the complementary role of the Z-Anatomy patch, so they are
checked the same way, and an unlabelled contact 'attachment' gets the card's role when the card names its bone once.
Run after build_attachment_contacts.py as well (the contact step reads and rewrites attachments.json).

  python3 atlas-data/pipeline/attachment_roles.py    # fixes runtime/attachments.json in place (also run by build_attachments.py)
Writes the list of flipped patches to atlas-data/anatomy/attachment-role-checks.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / 'atlas-data/runtime'
CONTEXT = ROOT / 'atlas-data/terminology/learner-attachment-context.json'
CHECKS = ROOT / 'atlas-data/anatomy/attachment-role-checks.json'


def fix_roles(muscles: dict) -> list:
    context = json.loads(CONTEXT.read_text())
    flipped = []
    for muscle, rows in muscles.items():
        card = context.get(muscle)
        if not card: continue
        origin, insertion = set(card.get('origin', [])), set(card.get('insertion', []))
        for row in rows:
            if row.get('source') not in ('za', 'contact') or not row.get('bone'): continue
            bone, role = row['bone'], row['role']
            if role != 'insertion' and bone in insertion and bone not in origin: new = 'insertion'
            elif role != 'origin' and bone in origin and bone not in insertion: new = 'origin'
            else: continue
            flipped.append({'muscle': muscle, 'patch': row.get('key'), 'source': row['source'], 'bone': bone, 'was': role, 'card': new})
            row['role'] = new  # rows keep their order: contact rows index their triangle files by position
    return flipped


def names():
    structures = json.loads((RUNTIME / 'structures.json').read_text())['structures']
    return {s['key']: s.get('names', {}).get('en') or s['id'] for s in structures}


def write_checks(flipped: list):
    label = names()
    CHECKS.write_text(json.dumps({
        'schemaVersion': 1,
        'note': 'Patch or contact role contradicted (or was missing from) the card text (two-source cards); the card role is used.',
        'flipped': [{**f, 'muscleName': label.get(f['muscle']), 'boneName': label.get(f['bone'])} for f in flipped],
    }, ensure_ascii=False, indent=1) + '\n')


def main():
    path = RUNTIME / 'attachments.json'
    doc = json.loads(path.read_text())
    flipped = fix_roles(doc['muscles'])
    path.write_text(json.dumps(doc, ensure_ascii=False, separators=(',', ':')) + '\n')
    if flipped or not CHECKS.exists(): write_checks(flipped)
    print('ROLES flipped', len(flipped), 'patches in', len({f['muscle'] for f in flipped}), 'muscles')


if __name__ == '__main__':
    main()
