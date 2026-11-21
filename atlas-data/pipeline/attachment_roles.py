"""Correct the origin/insertion role of Z-Anatomy attachment patches against the card text (2026-11-20).

Z-Anatomy names each patch .o (origin) or .e (insertion), but for some muscles the names are the other way round
(pectoralis minor: its rib patches are .e and the coracoid patch .o). The card text (learner-attachment-context.json,
built from the two-source muscle cards) says which bones the origin and the insertion are on. A patch whose bone the
card puts only under the other role takes that role; a bone the card does not name, or names under both, is left alone.
Contact-estimated rows (build_attachment_contacts.py) took the complementary role of the Z-Anatomy patch, so they are
checked the same way, and an unlabelled contact 'attachment' gets the card's role when the card names its bone once.
Run after build_attachment_contacts.py as well (the contact step reads and rewrites attachments.json).

  python3 atlas-data/pipeline/attachment_roles.py    # fixes runtime/attachments.json in place (also run by build_attachments.py)
Before the roles, fix_sides corrects patches owned by or linked to the other side's muscle or bone.
Writes the flipped and moved patches to atlas-data/anatomy/attachment-role-checks.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / 'atlas-data/runtime'
CONTEXT = ROOT / 'atlas-data/terminology/learner-attachment-context.json'
CHECKS = ROOT / 'atlas-data/anatomy/attachment-role-checks.json'
TRIANGLES = ROOT / 'atlas-data/source-cache/datasets/za-v2/attachments'  # contact triangle files (derived, git-ignored)


def _structures():
    return {s['key']: s for s in json.loads((RUNTIME / 'structures.json').read_text())['structures']}


def _mirror(structures: dict, key: str, side: str):
    """The same structure on the other side ('Femur.r' -> 'Femur.l')."""
    s = structures[key]; base = s['sourceName'].rsplit('.', 1)[0]
    for k, t in structures.items():
        if t['side'] == side and t['sourceName'].rsplit('.', 1)[0] == base and t['layer'] == s['layer']: return k
    return None


# 2026-11-21: rows whose role is certain from anatomy alone but that the card text cannot settle (it names no such bone).
# (muscle without side, bone without side, source) -> new role, or None to drop an estimated area that is not an attachment.
CERTAIN = {
    ('Serratus anterior muscle', 'Ninth rib', 'za'): ('origin', 'serratus anterior arises from the ribs; it inserts on the scapula only'),
    ('Serratus posterior superior muscle', 'Second rib', 'contact'): ('insertion', 'arises from spinous processes C7–T3, inserts on ribs 2–5'),
    ('Serratus posterior superior muscle', 'Third rib', 'contact'): ('insertion', 'arises from spinous processes C7–T3, inserts on ribs 2–5'),
    ('Serratus posterior superior muscle', 'Fourth rib', 'contact'): ('insertion', 'arises from spinous processes C7–T3, inserts on ribs 2–5'),
    ('Serratus posterior superior muscle', 'Fifth rib', 'contact'): ('insertion', 'arises from spinous processes C7–T3, inserts on ribs 2–5'),
    ('Serratus posterior inferior muscle', 'Ninth rib', 'contact'): ('insertion', 'arises from spinous processes T11–L2, inserts on ribs 9–12'),
    ('Serratus posterior inferior muscle', 'Tenth rib', 'contact'): ('insertion', 'arises from spinous processes T11–L2, inserts on ribs 9–12'),
    ('Serratus posterior inferior muscle', 'Eleventh rib', 'contact'): ('insertion', 'arises from spinous processes T11–L2, inserts on ribs 9–12'),
    ('Serratus posterior inferior muscle', 'Twelfth rib', 'contact'): ('insertion', 'arises from spinous processes T11–L2, inserts on ribs 9–12'),
    ('Short head of biceps brachii', 'Humerus', 'contact'): (None, 'the short head arises from the coracoid process; contact with the humerus is not an attachment'),
}


def fix_certain(muscles: dict) -> list:
    structures = _structures()
    base = lambda k: structures[k]['sourceName'].rsplit('.', 1)[0] if structures[k]['side'] in ('left', 'right') else structures[k]['sourceName']
    changes = []
    for muscle, rows in muscles.items():
        for row in list(rows):
            if not row.get('bone'): continue
            rule = CERTAIN.get((base(muscle), base(row['bone']), row.get('source')))
            if not rule: continue
            role, why = rule
            if role is None:
                # Contact rows index their triangle file by position: drop the row and the same entry of the file.
                contact = [r for r in rows if r.get('source') == 'contact']
                index = next(i for i, r in enumerate(contact) if r is row)
                tris_path = TRIANGLES / f'{muscle}.json'
                if tris_path.exists():
                    tris = json.loads(tris_path.read_text())
                    del tris['rows'][index]
                    if tris['rows']: tris_path.write_text(json.dumps(tris, separators=(',', ':')) + '\n')
                    else: tris_path.unlink()
                rows.remove(row); changes.append({'muscle': muscle, 'bone': row['bone'], 'source': row['source'], 'was': row['role'], 'now': 'removed', 'why': why})
            elif row['role'] != role:
                changes.append({'muscle': muscle, 'bone': row['bone'], 'source': row['source'], 'was': row['role'], 'now': role, 'why': why})
                row['role'] = role
    return changes


def fix_sides(muscles: dict) -> list:
    """2026-11-21: some Z-Anatomy patches of a left muscle are linked to a right bone (or the other way round).
    Where the patch mesh itself lies on the bone's side, the patch belongs to the same muscle of that side and moves there;
    where it lies on the muscle's side, only the bone link is wrong and points to the same bone of the muscle's side.
    A patch on the midline (nasal bones, |x| < 1 cm) keeps its bone. Contact rows are left alone: their triangle files
    are keyed by the bone they were measured on."""
    structures = _structures()
    centre_x = lambda k: sum(structures[k]['geometry']['bounds'][i][0] for i in (0, 1)) / 2
    changes, moves = [], []
    for muscle, rows in muscles.items():
        side = structures[muscle]['side']
        if side not in ('left', 'right'): continue
        for row in rows:
            bone = row.get('bone')
            if row.get('source') != 'za' or not bone or structures[bone]['side'] not in ('left', 'right') or structures[bone]['side'] == side: continue
            x = centre_x(row['key'])
            if abs(x) < .01: continue
            patch_side = 'left' if x > 0 else 'right'  # the model's left is +x
            if patch_side == structures[bone]['side']:
                other = _mirror(structures, muscle, patch_side)
                if other: moves.append((muscle, other, row))
                changes.append({'muscle': muscle, 'patch': row['key'], 'fix': 'moved to the other side\'s muscle', 'to': other})
            else:
                to = _mirror(structures, bone, side)
                changes.append({'muscle': muscle, 'patch': row['key'], 'fix': 'bone link to the same side', 'from': bone, 'to': to})
                if to: row['bone'] = to
    for muscle, other, row in moves:
        muscles[muscle].remove(row)
        if not any(r.get('key') == row['key'] for r in muscles.setdefault(other, [])): muscles[other].append(row)
    return changes


def fix_roles(muscles: dict) -> list:
    context = json.loads(CONTEXT.read_text())
    structures = _structures()
    flipped = []
    for muscle, rows in muscles.items():
        card = context.get(muscle)
        if not card: continue
        origin, insertion = set(card.get('origin', [])), set(card.get('insertion', []))
        for row in rows:
            if row.get('source') not in ('za', 'contact') or not row.get('bone'): continue
            bone, role = row['bone'], row['role']
            # A midline patch on the other side's bone (nasal bones, maxilla at the septum): compare by the same bone of the muscle's side.
            side = structures[muscle]['side']
            if side in ('left', 'right') and structures[bone]['side'] in ('left', 'right') and structures[bone]['side'] != side:
                bone = _mirror(structures, bone, side) or bone
            if role != 'insertion' and bone in insertion and bone not in origin: new = 'insertion'
            elif role != 'origin' and bone in origin and bone not in insertion: new = 'origin'
            else: continue
            flipped.append({'muscle': muscle, 'patch': row.get('key'), 'source': row['source'], 'bone': row['bone'], 'was': role, 'card': new})
            row['role'] = new  # rows keep their order: contact rows index their triangle files by position
    return flipped


def names():
    structures = json.loads((RUNTIME / 'structures.json').read_text())['structures']
    return {s['key']: s.get('names', {}).get('en') or s['id'] for s in structures}


def write_checks(flipped: list, sides: list, certain: list = ()):
    """Adds this run's changes to the list (a rerun finds only what is still wrong, so earlier entries are kept)."""
    label = names()
    previous = json.loads(CHECKS.read_text()) if CHECKS.exists() else {}
    def merge(old, new, key):
        seen = {key(x) for x in old}
        return old + [x for x in new if key(x) not in seen]
    doc = {
        'schemaVersion': 1,
        'note': 'Patch or contact role contradicted (or was missing from) the card text (two-source cards); the card role is used. '
                'sides: Z-Anatomy patches owned by or linked to the other side (fix_sides).',
        'flipped': merge(previous.get('flipped', []), [{**f, 'muscleName': label.get(f['muscle']), 'boneName': label.get(f['bone'])} for f in flipped],
                         lambda x: (x['muscle'], x.get('patch'), x.get('source'), x['bone'], x['card'])),
        'sides': merge(previous.get('sides', []), [{**c, 'muscleName': label.get(c['muscle']), 'toName': label.get(c.get('to'))} for c in sides],
                       lambda x: (x['muscle'], x['patch'])),
        'certain': merge(previous.get('certain', []), [{**c, 'muscleName': label.get(c['muscle']), 'boneName': label.get(c['bone'])} for c in certain],
                         lambda x: (x['muscle'], x['bone'], x['source'], x['now'])),
    }
    CHECKS.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n')


def main():
    path = RUNTIME / 'attachments.json'
    doc = json.loads(path.read_text())
    sides = fix_sides(doc['muscles'])
    flipped = fix_roles(doc['muscles'])
    certain = fix_certain(doc['muscles'])
    # A muscle left with no rows (its only patches belonged to the other side) is listed as missing, like build_attachments does.
    for muscle in [m for m, rows in doc['muscles'].items() if not rows]:
        del doc['muscles'][muscle]
        if muscle not in doc['missing']: doc['missing'].append(muscle)
    doc['missing'].sort()
    path.write_text(json.dumps(doc, ensure_ascii=False, separators=(',', ':')) + '\n')
    if flipped or sides or certain or not CHECKS.exists(): write_checks(flipped, sides, certain)
    print('SIDES fixed', len(sides), '· ROLES flipped', len(flipped), 'patches in', len({f['muscle'] for f in flipped}), 'muscles', '· CERTAIN', len(certain))


if __name__ == '__main__':
    main()
