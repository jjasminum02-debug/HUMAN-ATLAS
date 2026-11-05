"""Cross-check structure-names-ko.json against the 대한해부학회 dictionary block on KMLE (ROADMAP C1).

  python3 atlas-data/pipeline/verify_names_kmle.py            # resumes; cached pages are reused
Writes atlas-data/terminology/structure-names-kmle.json: per English term the KAA entry found
(modern / 옛 용어), the URL, and whether the drafted pair matched. KMLE pages are CP949.
"""
import html
import json
from pathlib import Path
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from names_ko import NAMES, series  # noqa: E402
from vessel_names_ko import vessel_name  # noqa: E402

CACHE = ROOT / 'atlas-data/source-cache/kmle-2026-11-04'
OUT = ROOT / 'atlas-data/terminology/structure-names-kmle.json'
BASE = ('https://www.kmle.co.kr/search.php?DictAbbreviationAll=YES&DictAll=YES&DictDefAll=YES'
        '&DictNownuri=YES&DictWordNet=YES&EbookTerminology=YES&Search=')
UNNAMED = ['Frenula capsulae', 'Iliopectineal arch', 'Intercornual ligament', 'Investing abdominal fascia', 'Triradiate cartilage']


def fetch(term):
    path = CACHE / (re.sub(r'[^a-z0-9]+', '-', term.lower()).strip('-') + '.html')
    if path.exists():
        return path.read_text()
    url = BASE + urllib.parse.quote_plus(term)
    for attempt in range(4):
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (HUMAN ATLAS terminology check)'})
            with urllib.request.urlopen(request, timeout=20) as response:
                text = response.read().decode('cp949', errors='replace')
            CACHE.mkdir(parents=True, exist_ok=True); path.write_text(text); time.sleep(1.2)
            return text
        except Exception:
            time.sleep(5 * (attempt + 1))
    return None


def kaa_entries(page):
    """(english, modern, old) rows from the 대한해부학회 panels (exact block first, then similar)."""
    rows = []
    for panel in re.split(r'<div class="panel panel-default">', page):
        if '대한해부학회 의학용어 사전' not in panel[:400]:
            continue
        for eng, kor in re.findall(r'icon-lang-eng"></span>(.*?)</div>\s*<div class="col-xs-6">\s*<span class="icon-lang-kor"></span>(.*?)</div>', panel, re.S):
            eng = html.unescape(re.sub(r'<[^>]+>', '', eng)).strip()
            parts = [html.unescape(re.sub(r'<[^>]+>', '', p)).strip() for p in re.split(r'<br\s*/?>', kor)]
            modern = parts[0] if parts else ''
            old = next((p.replace('[옛 용어]', '').strip() for p in parts[1:] if '[옛 용어]' in p), None)
            if eng and modern and eng not in ('영문',):
                rows.append((eng, modern, old))
    return rows


def norm(text):
    t = text.lower().replace('-', ' ').replace(' muscle', '').replace(' m.', '')
    t = re.sub(r'[^a-z ]', ' ', t)
    words = [w[:-1] if w.endswith('s') and len(w) > 4 else w for w in t.split()]
    return ' '.join(words)


def compact(text):
    return re.sub(r'[\s·()]', '', text or '')


def main():
    structures = json.loads((ROOT / 'atlas-data/runtime/structures.json').read_text())['structures']
    vessels = {s['names']['en'].rstrip('.') for s in structures if s['layer'] == 'vessel' and vessel_name(s['names']['en'])}
    terms = sorted({k for k in NAMES if not series(k)} | set(UNNAMED) | vessels)
    previous = json.loads(OUT.read_text())['terms'] if OUT.exists() else {}
    results = {}
    for i, term in enumerate(terms, 1):
        if term in previous and previous[term].get('status') != 'fetch_failed':
            results[term] = previous[term]; continue
        page = fetch(term)
        if page is None:
            results[term] = {'status': 'fetch_failed'}; continue
        rows = kaa_entries(page)
        hit = next((r for r in rows if r[0].lower() == term.lower()), None) or next((r for r in rows if norm(r[0]) == norm(term)), None)
        draft = NAMES.get(term) or vessel_name(term)
        if not hit:
            results[term] = {'status': 'not_in_kaa_dictionary', 'url': BASE + urllib.parse.quote_plus(term)}
        else:
            results[term] = {'status': 'kaa_found', 'kaaEnglish': hit[0], 'koModern': hit[1], 'koTraditional': hit[2],
                             'url': BASE + urllib.parse.quote_plus(term),
                             'draftModernMatch': bool(draft) and compact(draft[0]) == compact(hit[1]),
                             'draftTraditionalMatch': bool(draft) and bool(hit[2]) and compact(draft[1]) == compact(hit[2])}
        if i % 25 == 0:
            print(f'KMLE {i}/{len(terms)}', flush=True)
            OUT.write_text(json.dumps({'schemaVersion': 1, 'checkedOn': '2026-11-04', 'terms': {**previous, **results}}, ensure_ascii=False, indent=1) + '\n')
    OUT.write_text(json.dumps({'schemaVersion': 1, 'checkedOn': '2026-11-04', 'source': 'KMLE 대한해부학회 의학용어 사전 block',
                               'terms': results}, ensure_ascii=False, indent=1) + '\n')
    status = {}
    for r in results.values(): status[r['status']] = status.get(r['status'], 0) + 1
    found = [r for r in results.values() if r['status'] == 'kaa_found']
    print(json.dumps({'terms': len(terms), 'status': status,
                      'modernMatch': sum(r['draftModernMatch'] for r in found), 'traditionalMatch': sum(r['draftTraditionalMatch'] for r in found)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
