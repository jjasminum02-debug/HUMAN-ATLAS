"""Second and third independent sources for muscle facts (ROADMAP C2, 4-1 steps 3-4): the UAMS Department of Neuroscience
muscle tables and Kenhub "Key facts". Pages are cached under atlas-data/source-cache (git-ignored); nothing is copied
to the runtime, values are only compared with the AI-drafted tables. Used by build_muscle_cards.py and build_actions.py.
"""
import html
from pathlib import Path
import re
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
# Second independent source for what Wikipedia leaves empty or contradicts: UAMS Department of Neuroscience muscle tables
# (Muscle / Origin / Insertion / Action / Innervation / Artery). Cached HTML, git-ignored; refetch with fetch_uams().
UAMS = ROOT / 'atlas-data/source-cache/uams-2026-11-10'
UAMS_URL = 'https://medicine.uams.edu/neuroscience/education/medical-school-courses/human-structure-module/anatomy-tables/muscle-tables/{}/'
UAMS_PAGES = ['muscles-of-the-head-and-neck', 'muscles-of-the-upper-limb', 'muscles-of-the-back-region', 'muscles-of-the-thorax',
              'muscles-of-the-pelvis-and-perineum', 'muscles-of-the-abdominal-region', 'muscles-of-the-lower-limb']


def fetch_uams():
    UAMS.mkdir(parents=True, exist_ok=True)
    for page in UAMS_PAGES:
        path = UAMS / f'{page}.html'
        if not path.exists():
            request = urllib.request.Request(UAMS_URL.format(page), headers={'User-Agent': 'HUMAN-ATLAS-anatomy-check/1.0 (local educational build)'})
            with urllib.request.urlopen(request, timeout=40) as response: path.write_bytes(response.read())


ABBREVIATIONS = [(r'\baa\.', 'arteries'), (r'\ba\.', 'artery'), (r'\bnn\.', 'nerves'), (r'\bn\.', 'nerve'), (r'\bbrs?\.', 'branch'), (r'\bmm?\.', 'muscle'),
                 (r'\bant\.', 'anterior'), (r'\bpost\.', 'posterior'), (r'\bsup\.', 'superior'), (r'\binf\.', 'inferior'), (r'\blat\.', 'lateral'),
                 (r'\bmed\.', 'medial'), (r'\bint\.', 'internal'), (r'\bext\.', 'external'), (r'\bdesc\.', 'descending'), (r'\basc\.', 'ascending')]


# Third source, asked only for what the draft and neither Wikipedia nor UAMS settle: Kenhub "Key facts" (cached, git-ignored).
KENHUB = ROOT / 'atlas-data/source-cache/kenhub-2026-11-10'
KENHUB_URL = 'https://www.kenhub.com/en/library/anatomy/{}'
KENHUB_FIELDS = {'innervation': 'nerve', 'blood supply': 'artery', 'action': 'action', 'actions': 'action', 'function': 'action', 'functions': 'action'}


def kenhub_facts(*names):
    """{'nerve', 'artery', 'action'} text from the first Kenhub page found for these names, or None."""
    KENHUB.mkdir(parents=True, exist_ok=True)
    slugs = []
    for name in names:
        base = re.sub(r'[^a-z0-9]+', '-', name.lower().strip('() ')).strip('-')
        slugs += [base] if base.endswith(('-muscle', '-muscles')) else [f'{base}-muscle', f'{base}-muscles', base]
    for slug in dict.fromkeys(slugs):
        path, missing = KENHUB / f'{slug}.html', KENHUB / f'{slug}.missing'
        if missing.exists(): continue
        if not path.exists():
            request = urllib.request.Request(KENHUB_URL.format(slug), headers={'User-Agent': 'HUMAN-ATLAS-anatomy-check/1.0 (local educational build)'})
            time.sleep(1)
            try:
                with urllib.request.urlopen(request, timeout=30) as response: path.write_bytes(response.read())
            except urllib.error.HTTPError as error:
                if error.code == 404: missing.write_text(''); continue
                raise
        text = path.read_text(errors='ignore'); start = text.find('Key facts')
        if start < 0: continue
        parts = [' '.join(html.unescape(p).split()) for p in re.split(r'<[^>]+>', text[start:start + 6000])]
        parts = [p for p in parts if p]
        facts, field = {}, None
        stop = {'origin', 'origins', 'insertion', 'insertions', 'contents', 'show all'}
        for part in parts[1:]:
            low = part.lower()
            if low.startswith(('in this article', 'clinical notes', 'sources', '+ show all')) or '<' in part: break
            if low in KENHUB_FIELDS: field = KENHUB_FIELDS[low] if KENHUB_FIELDS[low] not in facts else None; continue
            if low in stop: field = None; continue
            # A field can span several lines ("Descending (upper) fibers: ..."): keep everything up to the next label.
            if field: facts[field] = f"{facts.get(field, '')} {part}".strip()
        if facts: return {**facts, 'page': slug}
    return None


def uams_name(name):
    """'oblique, external abdominal' / 'Abductor digiti minimi muscle of foot' -> 'external abdominal oblique' / 'abductor digiti minimi foot'."""
    n = name.lower().strip('() ')
    if ',' in n and '(' not in n: head, _, tail = n.partition(','); n = f'{tail} {head}'
    n = re.sub(r'\b(muscles?|musculus|of|the|in|m)\b|[^a-z ]', ' ', n.replace('-', ''))
    return ' '.join(n.split())


def uams_rows():
    """Normalized muscle name -> row; names whose rows disagree between tables are dropped as ambiguous."""
    fetch_uams(); rows, clash = {}, set()
    for page in UAMS_PAGES:
        text = (UAMS / f'{page}.html').read_text(errors='ignore')
        for table in re.findall(r'<table.*?</table>', text, re.S):
            trs = re.findall(r'<tr.*?</tr>', table, re.S)
            cell = lambda c: ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', c)).split())
            head = [cell(c).lower() for c in re.findall(r'<t[hd].*?</t[hd]>', trs[0], re.S)]
            for tr in trs[1:]:
                cells = [cell(c) for c in re.findall(r'<t[hd].*?</t[hd]>', tr, re.S)]
                if len(cells) != len(head) or not cells[0]: continue
                row = dict(zip(head, cells)); key = uams_name(row['muscle'])
                for pattern, word in ABBREVIATIONS:
                    for field in ('action', 'innervation', 'artery'): row[field] = re.sub(pattern, word, row.get(field, ''), flags=re.I)
                if key in rows and (rows[key]['innervation'], rows[key]['artery']) != (row['innervation'], row['artery']):
                    # Listed in two tables with different wording: nerve and artery are ambiguous, the actions are kept together.
                    clash.add(key); rows[key]['action'] = f"{rows[key]['action']}; {row['action']}"
                rows.setdefault(key, {**row, 'page': page})
    for key in clash: rows[key] = {**rows[key], 'innervation': '', 'artery': ''}
    return rows


# Same muscle, different spelling in the UAMS tables (name equivalence only; values still have to agree with the draft).
UAMS_ALIASES = {'Dorsal interossei muscles of foot': 'dorsal interosseous (foot)', 'Dorsal interossei muscles of hand': 'dorsal interosseous (hand)',
                'Plantar interossei muscles': 'plantar interosseous', 'Palmar interossei muscles': 'palmar interosseous',
                'Depressor septi nasi': 'depressor septi', 'Corrugator supercilii': 'corrugator', 'Rhomboid major muscle': 'rhomboideus major',
                'Rhomboid minor muscle': 'rhomboideus minor', 'Scalenus medius muscle': 'middle scalene', 'Opponens digiti minimi muscle of hand': 'opponens digiti minimi',
                'Fibularis brevis muscle': 'fibularis (peroneus) brevis', 'Fibularis longus muscle': 'fibularis (peroneus) longus',
                'Fibularis tertius muscle': 'fibularis (peroneus) tertius', 'Levator nasolabialis': 'levator labii superioris alaque nasi'}


def uams_row(rows, *names):
    names = [UAMS_ALIASES.get(n, n) for n in names]
    for name in names:
        key = uams_name(name)
        if key in rows: return rows[key]
        if key.endswith(('foot', 'hand')) and f'{key[:-5]} {key[-4:]}' in rows: return rows[f'{key[:-5]} {key[-4:]}']
    return None
