"""Muscle cards: innervation, segments, blood supply and action for every visible muscle (ROADMAP C2).

  python3 atlas-data/pipeline/build_muscle_cards.py           # first run fetches ~200 Wikipedia pages (cached)
Writes atlas-data/runtime/muscle-cards.json (what the app shows) and atlas-data/anatomy/muscle-card-checks.json
(field-by-field comparison and the exception list).

Two independent sources per field: the AI-drafted table in muscle_content.py and the English Wikipedia muscle
infobox (nerve / artery / action fields, wikitext via the MediaWiki API, cached under source-cache). The runtime keeps
only values both sources state: nerves and arteries that appear in both (a trunk counts as agreeing with its branch),
spinal segments in both, and the drafted action sentence when the infobox action names the same movement.
Everything else is listed in the checks file with its reason. Wikipedia text itself is not copied into the runtime.
"""
import html
import json
from pathlib import Path
import re
import sys
import time
import urllib.parse
import urllib.error
import urllib.request

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from muscle_content import ARTERIES, CONCEPTS, NERVES, PARTS, TENDONS  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / 'atlas-data/source-cache/wikipedia-2026-11-04'
API = 'https://en.wikipedia.org/w/api.php'
OUT = ROOT / 'atlas-data/runtime/muscle-cards.json'
CHECKS = ROOT / 'atlas-data/anatomy/muscle-card-checks.json'
def fetch(titles):
    """title -> {'title', 'revid', 'wikitext'} (or None when the page does not exist); cached per title."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = lambda t: CACHE / (re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-') + '.json')
    todo = [t for t in titles if not path(t).exists()]
    for i in range(0, len(todo), 40):
        batch = todo[i:i + 40]
        query = urllib.parse.urlencode({'action': 'query', 'prop': 'revisions', 'rvprop': 'ids|content', 'rvslots': 'main',
                                        'titles': '|'.join(batch), 'redirects': 1, 'format': 'json', 'formatversion': 2})
        request = urllib.request.Request(f'{API}?{query}', headers={'User-Agent': 'HUMAN-ATLAS-anatomy-check/1.0 (local educational build)'})
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read())['query']
        alias = {t: t for t in batch}
        for step in ('normalized', 'redirects'):
            for row in data.get(step, []):
                for t, cur in list(alias.items()):
                    if cur == row['from']: alias[t] = row['to']
        pages = {p['title']: p for p in data['pages']}
        for t in batch:
            page = pages.get(alias[t])
            rec = None
            if page and 'revisions' in page:
                rev = page['revisions'][0]
                rec = {'title': page['title'], 'revid': rev['revid'], 'wikitext': rev['slots']['main']['content']}
            path(t).write_text(json.dumps(rec, ensure_ascii=False))
        time.sleep(1)
    return {t: json.loads(path(t).read_text()) for t in titles}


def template(text, start):
    """Body of the template opening at `start` ('{{'), by brace depth."""
    depth, i = 0, start
    while i < len(text):
        if text.startswith('{{', i): depth += 1; i += 2; continue
        if text.startswith('}}', i):
            depth -= 1; i += 2
            if depth == 0: return text[start + 2:i - 2]
            continue
        i += 1
    return text[start + 2:]


def split_top(body):
    out, depth, cur, i = [], 0, '', 0
    while i < len(body):
        two = body[i:i + 2]
        if two in ('{{', '[['): depth += 1; cur += two; i += 2; continue
        if two in ('}}', ']]'): depth -= 1; cur += two; i += 2; continue
        if body[i] == '|' and depth == 0: out.append(cur); cur = ''; i += 1; continue
        cur += body[i]; i += 1
    return out + [cur]


def clean(value):
    value = re.sub(r'<!--.*?-->', '', value, flags=re.S)
    value = re.sub(r'<ref[^>/]*/>', '', value)
    value = re.sub(r'<ref[^>]*>.*?</ref>', '', value, flags=re.S)
    for _ in range(4):  # innermost templates -> their arguments
        value = re.sub(r'\{\{([^{}]*)\}\}', lambda m: ', '.join(a.split('=', 1)[-1] for a in m.group(1).split('|')[1:]), value)
    # Links keep target and label: '[[posterior humeral circumflex artery|posterior]]' names the artery in the target.
    value = re.sub(r'\[\[([^|\]]*)\|([^\]]*)\]\]', lambda m: m.group(2) if m.group(2).lower() in m.group(1).lower() or re.fullmatch(r'[CTLS]\d{1,2}', m.group(2)) else f'{m.group(2)} ({m.group(1)})', value)
    value = re.sub(r'\[\[([^\]]*)\]\]', r'\1', value)
    value = html.unescape(re.sub(r'<[^>]+>', ' ', value))
    return re.sub(r'\s+', ' ', value.replace("'''", '').replace("''", '')).strip()


def infobox(wikitext):
    m = re.search(r'\{\{\s*Infobox (muscle|anatomy)', wikitext or '', re.I)
    if not m: return None
    fields = {}
    for part in split_top(template(wikitext, m.start()))[1:]:
        if '=' in part:
            k, v = part.split('=', 1)
            fields[k.strip().lower()] = clean(v)
    return {'nerve': fields.get('nerve') or fields.get('innervation') or '', 'artery': fields.get('artery') or fields.get('blood') or fields.get('supply') or '',
            'action': fields.get('action') or fields.get('actions') or ''}


from second_sources import kenhub_facts, uams_row, uams_rows  # noqa: E402


def vocab_keys(text, vocab):
    """Vocabulary keys named in an infobox field, specific names first; matched text is consumed."""
    text, found = f' {text.lower()} ', []
    for key, entry in vocab.items():
        pattern = re.compile(rf'(?<![a-z])(?:{entry[4]})')  # whole words only: 'segmental' must not read as 'mental'
        if pattern.search(text):
            found.append(key); text = pattern.sub(' ', text)
    rest = re.sub(r'\b(nerves?|arter(y|ies)|branch(es)?|of|the|and|via|from|to|or|its|muscular|supplied|by|division|part|portion|fibers?|fibres?|motor|sensory)\b|[^a-z]', ' ', text)
    return found, ' '.join(rest.split())


def ancestors(key, vocab):
    parents = vocab[key][3]
    parents = [] if parents is None else [parents] if isinstance(parents, str) else list(parents)
    return [a for p in parents for a in [p, *ancestors(p, vocab)]]


def compare(draft, source, vocab):
    """Keys both sources state (a trunk agrees with its branch), plus what each source adds."""
    related = lambda a, b: a == b or b in ancestors(a, vocab) or a in ancestors(b, vocab)
    agreed = [d for d in draft if any(related(d, s) for s in source)]
    return agreed, [d for d in draft if d not in agreed], [s for s in source if not any(related(d, s) for d in draft)]


SEG = re.compile(r'\b([CTLS])\s?(\d{1,2})(?:\s*(?:[-–—]|to|through)\s*([CTLS])?\s?(\d{1,2}))?\b')
ORDER = [f'C{i}' for i in range(1, 9)] + [f'T{i}' for i in range(1, 13)] + [f'L{i}' for i in range(1, 6)] + [f'S{i}' for i in range(1, 6)]


def segments(text):
    out = set()
    for a, i, b, j in SEG.findall(text.replace('‑', '-')):
        lo = f'{a}{i}'; hi = f'{b or a}{j}' if j else lo
        if lo in ORDER and hi in ORDER and ORDER.index(lo) <= ORDER.index(hi):
            out.update(ORDER[ORDER.index(lo):ORDER.index(hi) + 1])
    return out


def segment_text(segs):
    """Sorted segment set -> 'C5–C6' style text, contiguous runs joined."""
    idx = sorted(ORDER.index(s) for s in segs); runs, out = [], []
    for i in idx:
        if runs and i == runs[-1][-1] + 1: runs[-1].append(i)
        else: runs.append([i])
    for r in runs: out.append(ORDER[r[0]] if len(r) == 1 else f'{ORDER[r[0]]}–{ORDER[r[-1]]}')
    return ', '.join(out)


# Q2-1: artery terms -> Z-Anatomy vessel names where the spelling differs or one term covers several vessels.
VESSEL_ALIASES = {'intercostal': ['Posterior intercostal arteries'],
                  'deep_temporal': ['Anterior deep temporal artery', 'Posterior deep temporal artery'],
                  'genicular': ['Superior lateral genicular artery', 'Superior medial genicular artery', 'Inferior lateral genicular artery',
                                'Inferior medial genicular artery', 'Middle genicular artery']}


def vessel_structures(key, vessel_names):
    norm = lambda t: re.sub(r'[^a-z]', '', t.lower().replace('arteries', 'artery'))
    by_norm = {norm(n): n for n in vessel_names}
    found = VESSEL_ALIASES.get(key) or [by_norm.get(norm(ARTERIES[key][2]))]
    return [n for n in found if n in vessel_names]


def entry(key, vocab, structures=()):
    ko, trad, en = vocab[key][:3]
    return {'ko': ko, 'koTraditional': trad, 'en': en, **({'structure': en} if en in structures else {})}


def main():
    structures = json.loads((ROOT / 'atlas-data/runtime/structures.json').read_text())['structures']
    muscles = sorted({s['names']['en'] for s in structures if s['learner']['visible'] and s['layer'] == 'muscle'})
    nerve_names = {s['names']['en'] for s in structures if s['learner']['visible'] and s['layer'] == 'nerve'}
    vessel_names = {s['names']['en'] for s in structures if s['learner']['visible'] and s['layer'] == 'vessel'}
    unmapped = [n for n in muscles if n not in TENDONS and PARTS.get(n, n) not in CONCEPTS]
    if unmapped: raise SystemExit(f'no concept for {unmapped}')
    pages = fetch(sorted({c['wiki'] for c in CONCEPTS.values()}))
    second = uams_rows()

    cards, checks, exceptions, used = {}, {}, [], {'nerve': set(), 'artery': set()}
    tally = {f: {'agree': 0, 'partial': 0, 'conflict': 0, 'noSource': 0, 'noDraft': 0} for f in ('nerve', 'roots', 'artery', 'action')}
    for name in muscles:
        if name in TENDONS:
            cards[name] = {'tendonOf': TENDONS[name]}; continue
        concept_name = PARTS.get(name, name); concept = CONCEPTS[concept_name]
        draft = {**concept, **concept['parts'].get(name, {})}
        page = pages[concept['wiki']]; box = infobox(page['wikitext']) if page else None
        source = {'page': page['title'] if page else None, 'revid': page['revid'] if page else None, 'infobox': box is not None}
        card = {'concept': concept_name}; check = {'source': source}
        uams = uams_row(second, name, concept_name, concept['wiki'])
        if uams: source['uams'] = uams['page'] + ':' + uams['muscle']
        third = {}
        def kenhub():
            if 'facts' not in third:
                third['facts'] = kenhub_facts(concept['wiki'], concept_name)
                if third['facts']: source['kenhub'] = third['facts']['page']
            return third['facts']

        def record(field, status, **detail):
            tally[field][status] += 1; check[field] = {'status': status, **detail}
            if status != 'agree': exceptions.append({'muscle': name, 'field': field, 'status': status, **detail})

        for field, vocab in (('nerve', NERVES), ('artery', ARTERIES)):
            mine = draft[field]
            wiki, rest = vocab_keys(box[field], vocab) if box else ([], '')
            if not mine: record(field, 'noDraft', wikipedia=wiki); continue
            agreed = compare(mine, wiki, vocab)[0] if wiki else []
            if not agreed and uams:
                # Wikipedia is empty or contradicts the draft: the draft is shown only where UAMS states the same value.
                theirs = vocab_keys(uams['innervation' if field == 'nerve' else 'artery'], vocab)[0]
                ok, only_draft, only_uams = compare(mine, theirs, vocab)
                if ok:
                    card[field] = ok; used[field].update(ok)
                    record(field, 'agree' if not only_draft and not only_uams else 'partial', by='uams', draft=mine, uams=theirs,
                           wikipedia=wiki or None, **({'onlyDraft': only_draft} if only_draft else {}), **({'onlyUams': only_uams} if only_uams else {}))
                    continue
            if not agreed and (facts := kenhub()) and facts.get(field):
                theirs = vocab_keys(facts[field], vocab)[0]
                ok, only_draft, only_kenhub = compare(mine, theirs, vocab)
                if ok:
                    card[field] = ok; used[field].update(ok)
                    record(field, 'agree' if not only_draft and not only_kenhub else 'partial', by='kenhub', draft=mine, kenhub=theirs,
                           wikipedia=wiki or None, **({'onlyDraft': only_draft} if only_draft else {}), **({'onlyKenhub': only_kenhub} if only_kenhub else {}))
                    continue
            if not wiki: record(field, 'noSource', draft=mine, unparsed=rest[:160] or None,
                                **({'uams': uams['innervation' if field == 'nerve' else 'artery'][:160]} if uams else {})); continue
            agreed, only_draft, only_wiki = compare(mine, wiki, vocab)
            if agreed: card[field] = agreed; used[field].update(agreed)
            status = 'agree' if agreed and not only_draft and not only_wiki else 'partial' if agreed else 'conflict'
            record(field, status, draft=mine, wikipedia=wiki, **({'onlyDraft': only_draft} if only_draft else {}),
                   **({'onlyWikipedia': only_wiki} if only_wiki else {}), **({'unparsed': rest[:160]} if rest and status != 'agree' else {}))

        mine = segments(draft['roots']); wiki = segments(box['nerve']) if box else set()
        if not mine: record('roots', 'noDraft', wikipedia=segment_text(wiki) or None)
        elif not wiki:
            # Wikipedia gives no segments: the draft is shown where UAMS or Kenhub names the same segments.
            for by, text in (('uams', uams['innervation'] if uams else ''), ('kenhub', (kenhub() or {}).get('nerve', ''))):
                theirs = segments(text); both = mine & theirs
                if both:
                    card['roots'] = segment_text(both)
                    record('roots', 'agree' if both == mine == theirs else 'partial', by=by, draft=segment_text(mine), **{by: segment_text(theirs)}); break
            else: record('roots', 'noSource', draft=draft['roots'])
        else:
            both = mine & wiki
            if both: card['roots'] = segment_text(both)
            record('roots', 'agree' if both == mine == wiki else 'partial' if both else 'conflict',
                   draft=segment_text(mine), wikipedia=segment_text(wiki))

        action = box['action'] if box else ''
        if action and re.search(draft['check'], action.lower()):
            card['action'] = draft['action']; record('action', 'agree')
        elif uams and re.search(draft['check'], uams['action'].lower()):
            card['action'] = draft['action']; record('action', 'agree', by='uams', wikipedia=action[:200] or None, uams=uams['action'][:200])
        elif (facts := kenhub()) and re.search(draft['check'], facts.get('action', '').lower()):
            card['action'] = draft['action']; record('action', 'agree', by='kenhub', wikipedia=action[:200] or None, kenhub=facts['action'][:200])
        elif not action: record('action', 'noSource', **({'uams': uams['action'][:200]} if uams else {}))
        else: record('action', 'conflict', expected=draft['check'], wikipedia=action[:200], **({'uams': uams['action'][:200]} if uams else {}))
        cards[name] = card; checks[name] = check

    OUT.write_text(json.dumps({
        'schemaVersion': 1,
        'note': 'Muscle innervation, spinal segments, blood supply and action (ROADMAP C2). Values stated by both an AI-drafted table '
                '(atlas-data/pipeline/muscle_content.py) and the English Wikipedia muscle infobox, or the UAMS muscle tables where Wikipedia is '
                'empty or disagrees, or Kenhub where neither settles it; human review not performed. '
                'Keyed by Z-Anatomy English name; tendon structures point at their muscle.',
        # Vocabulary for the keys used below; `structure` = English name of the visible Z-Anatomy nerve to link to.
        'nerves': {k: entry(k, NERVES, nerve_names) for k in sorted(used['nerve'])},
        # `structures` = English names of the Z-Anatomy vessels drawn for this term (vessel layer, Q2-1).
        'arteries': {k: {**entry(k, ARTERIES), **({'structures': v} if (v := vessel_structures(k, vessel_names)) else {})} for k in sorted(used['artery'])},
        'cards': cards,
    }, ensure_ascii=False, separators=(',', ':')) + '\n')
    CHECKS.write_text(json.dumps({
        'schemaVersion': 1,
        'sources': {'draft': 'atlas-data/pipeline/muscle_content.py (AI-drafted, not human-reviewed)',
                    'wikipedia': {'site': 'en.wikipedia.org', 'accessedOn': '2026-11-04', 'license': 'CC BY-SA 4.0',
                                  'use': 'infobox nerve/artery/action fields parsed to vocabulary keys; no text copied to the runtime'},
                    'uams': {'site': 'medicine.uams.edu (Department of Neuroscience muscle tables)', 'accessedOn': '2026-11-10',
                             'use': 'second source where Wikipedia is empty or contradicts the draft (`by: uams`); no text copied to the runtime'},
                    'kenhub': {'site': 'www.kenhub.com (library "Key facts")', 'accessedOn': '2026-11-10',
                               'use': 'asked only when Wikipedia and UAMS settle nothing (`by: kenhub`); values parsed to vocabulary keys, no text copied'}},
        'statuses': {'agree': 'both sources state the same values (Wikipedia, or UAMS where marked by: uams)', 'partial': 'shown values are those both state; one source adds others',
                     'conflict': 'no common value; not shown', 'noSource': 'infobox missing or the field is empty / unrecognised; not shown',
                     'noDraft': 'the draft table has no value; not shown'},
        'summary': tally, 'exceptions': exceptions, 'muscles': checks,
    }, ensure_ascii=False, indent=1) + '\n')
    print('CARDS', len(cards), json.dumps(tally))


main()
