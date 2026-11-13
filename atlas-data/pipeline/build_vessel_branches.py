"""Vessel branch relations (ROADMAP 4-1 step 6): which vessel each artery branches off and each vein drains into.

  python3 atlas-data/pipeline/build_vessel_branches.py
Writes atlas-data/runtime/vessel-branches.json (runtime: child English name -> parent English name, `{S}` = the child's
side) and atlas-data/anatomy/vessel-branch-checks.json (sidecar). Z-Anatomy has no branch data, so:
  - names that state their parent ("Descending branch of lateral circumflex femoral artery") use the name itself;
  - every other parent comes from the AI-drafted table vessel_branches.py and is kept only where the English Wikipedia
    vessel infobox (artery `Source`, vein `Drains to`) names the same vessel. No text is copied to the runtime.
"""
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_muscle_cards import clean, fetch, split_top, template  # noqa: E402
from vessel_branches import PARENT  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'atlas-data/runtime/vessel-branches.json'
CHECKS = ROOT / 'atlas-data/anatomy/vessel-branch-checks.json'
NAMED = re.compile(r'^(.+?) (branch|branches) of (.+)$', re.I)


def norm(text):
    t = re.sub(r'\([^)]*\)', ' ', text.lower()).replace('coeliac', 'celiac').replace('-', ' ')
    for pattern, word in SYNONYMS: t = re.sub(pattern, word, t)
    t = re.sub(r'\b(left|right|the|of)\b', ' ', t)
    t = re.sub(r'\barteries\b', 'artery', t); t = re.sub(r'\bveins\b', 'vein', t)
    return ' '.join(t.split())


SYNONYMS = [(r'profunda brachii( artery)?', 'deep brachial artery'), (r'profunda femoris', 'deep femoral'),
            (r'brachiocephalic artery', 'brachiocephalic trunk'), (r'celiac (artery|trunk)', 'celiac trunk'), (r'arch of (the )?aorta|aortic arch', 'aortic arch'),
            (r'thoracoacromial', 'thoraco acromial'), (r'infraorbital', 'infra orbital'), (r'supraorbital', 'supra orbital'),
            (r'hemiazygos', 'hemi azygos'), (r'\bportal vein\b', 'hepatic portal vein'), (r'descending aorta', 'thoracic aorta')]


def infobox_parent(wikitext, kind):
    """The infobox field naming the parent: artery `BranchFrom` (or `Source`), vein `DrainsTo`. Link targets and their
    display text are both kept ([[Profunda femoris vein|profunda femoris]] -> both)."""
    m = re.search(r'\{\{\s*Infobox (artery|vein|anatomy)', wikitext or '', re.I)
    if not m: return ''
    fields = {}
    for part in split_top(template(wikitext, m.start()))[1:]:
        if '=' in part:
            k, v = part.split('=', 1)
            v = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'\1 \2', v)
            fields[k.strip().lower()] = clean(v)
    keys = ('branchfrom', 'source', 'from') if kind == 'artery' else ('drainsto', 'drains_to')
    return next((fields[k] for k in keys if fields.get(k, '').strip()), '')


def main():
    structures = json.loads((ROOT / 'atlas-data/runtime/structures.json').read_text())['structures']
    vessels = {s['names']['en']: s['kind'] for s in structures if s['layer'] == 'vessel' and s['learner']['visible'] and s['kind'] != 'heart'}
    lower = {n.lower(): n for n in vessels}
    unknown = sorted({c for c in PARENT if c not in vessels} | {p.replace('{S}', side) for p in PARENT.values() for side in ('Left', 'Right')
                                                                   if '{S}' in p} - set(vessels) | {p for p in PARENT.values() if '{S}' not in p and p not in vessels and p not in ('Ascending aorta', 'Pulmonary trunk', 'Coronary sinus', 'Hepatic portal vein', 'Cavernous sinus', 'Straight sinus', 'Retromandibular vein', 'Superior vena cava', 'Dorsal venous network of hand', 'Dorsal metacarpal arteries')})
    if unknown: print('NOT IN MODEL', unknown)
    parents, checks = {}, {}
    for child in sorted(vessels):
        m = NAMED.match(child)
        if m and m.group(3).lower() in lower:
            parents[child] = lower[m.group(3).lower()]; checks[child] = {'status': 'name'}
    titles = sorted({re.sub(r'\s*\([^)]*\)', '', c).strip() for c in PARENT if c in vessels})
    pages = fetch(titles)
    for child, parent in PARENT.items():
        if child not in vessels or child in parents: continue
        page = pages.get(re.sub(r'\s*\([^)]*\)', '', child).strip())
        text = infobox_parent(page['wikitext'], vessels[child]) if page else ''
        target = parent.replace('{S}', 'Left')
        if not text: checks[child] = {'status': 'noSource', 'draft': parent, 'page': page and page['title']}; continue
        # The source may name the trunk of the drafted parent (internal iliac for its anterior division): still the same origin.
        ancestors = [target]
        while ancestors[-1] in PARENT and len(ancestors) < 4: ancestors.append(PARENT[ancestors[-1]].replace('{S}', 'Left'))
        hit = next((a for a in ancestors if norm(a) in norm(text)), None)
        if hit:
            if parent.replace('{S}', 'Left') in vessels or parent.replace('{S}', 'Right') in vessels or parent in vessels:
                parents[child] = parent
                checks[child] = {'status': 'agree' if hit == target else 'agreeTrunk', 'draft': parent, 'page': page['title'], **({'wikipediaNames': hit} if hit != target else {})}
            else: checks[child] = {'status': 'agreeNotInModel', 'draft': parent, 'page': page['title']}
        else: checks[child] = {'status': 'conflict', 'draft': parent, 'wikipedia': text[:200], 'page': page['title']}
    tally = {}
    for c in checks.values(): tally[c['status']] = tally.get(c['status'], 0) + 1
    OUT.write_text(json.dumps({'schemaVersion': 1, 'note': 'Parent vessel per vessel name (artery: branches off; vein: drains into). '
                               'From the Z-Anatomy name, or the AI table where the Wikipedia infobox agrees; {S} = the vessel\'s own side.',
                               'parents': parents}, ensure_ascii=False, separators=(',', ':')) + '\n')
    CHECKS.write_text(json.dumps({'schemaVersion': 1, 'sources': {'draft': 'atlas-data/pipeline/vessel_branches.py (AI-drafted)',
        'wikipedia': {'site': 'en.wikipedia.org', 'use': 'artery Source / vein Drains to infobox fields, compared by name'}},
        'summary': tally, 'vessels': checks}, ensure_ascii=False, indent=1) + '\n')
    print('BRANCHES', json.dumps({'vessels': len(vessels), 'withParent': len(parents), **tally}))


if __name__ == '__main__':
    main()
