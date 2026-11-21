"""Learner text ends in 합니다체 (ROADMAP 4-3 U1): "돌린다." → "돌립니다.", "관절이다." → "관절입니다.".

Only the sentence-final word changes. The card builders call `polite_tree` before writing; run this file to
convert the current runtime files in place (idempotent):
    python3 atlas-data/pipeline/polite.py
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# Nouns that end in a vowel and take 다 directly as the copula ("인대다" = 인대 + 이다).
NOUN_DA = {'인대다', '섬유다', '부위다', '근육다', '뼈다', '자리다', '고리다', '머리다'}
BASE, JONG = 0xAC00, 28
J_N, J_B, J_L = 4, 17, 8  # ㄴ, ㅂ, ㄹ final consonants


def _jong(ch):
    code = ord(ch) - BASE
    return code % JONG if 0 <= code < 11172 else None


def _with_jong(ch, j):
    code = ord(ch) - BASE
    return chr(BASE + code - code % JONG + j)


def polite_word(w):
    """The 합니다 form of one sentence-final word ending in 다 (unchanged if it is not plain style)."""
    if not w.endswith('다') or w.endswith('니다') or len(w) < 2:
        return w
    if w in NOUN_DA:
        return w[:-1] + '입니다'
    if w.endswith('이다'):
        return w[:-2] + '입니다'
    if w.endswith('는다'):          # consonant-stem verb: 막는다 → 막습니다
        return w[:-2] + '습니다'
    if w.endswith('하다'):          # 강하다 → 강합니다
        return w[:-2] + '합니다'
    p = w[-2]; j = _jong(p)
    if j is None:
        return w
    if j == 0:                       # vowel stem: 띠다 → 띱니다
        return w[:-2] + _with_jong(p, J_B) + '니다'
    if j in (J_N, J_L):              # 돌린다 → 돌립니다, 만든다 → 만듭니다
        return w[:-2] + _with_jong(p, J_B) + '니다'
    return w[:-1] + '습니다'         # adjective with a final consonant: 작다 → 작습니다


_FINAL = re.compile(r'([가-힣]+다)(?=\.(?:\s|$)|$)')


def polite(text):
    if not isinstance(text, str) or not re.search('[가-힣]', text):
        return text
    return _FINAL.sub(lambda m: polite_word(m.group(1)), text)


def polite_tree(o):
    if isinstance(o, str):
        return polite(o)
    if isinstance(o, list):
        return [polite_tree(v) for v in o]
    if isinstance(o, dict):
        return {k: polite_tree(v) for k, v in o.items()}
    return o


def main():
    rt = ROOT / 'atlas-data/runtime'
    cards = json.loads((rt / 'structure-cards.json').read_text())
    body = polite_tree({'joints': cards['joints'], 'cards': cards['cards']})
    revision = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    (rt / 'structure-cards.json').write_text(json.dumps({'schemaVersion': cards['schemaVersion'], 'revision': revision,
                                                         'provenance': cards['provenance'], **body}, ensure_ascii=False, separators=(',', ':')) + '\n')
    muscles = json.loads((rt / 'muscle-cards.json').read_text())
    for card in muscles['cards'].values():
        if card.get('action'):
            card['action'] = polite(card['action'])
    (rt / 'muscle-cards.json').write_text(json.dumps(muscles, ensure_ascii=False, separators=(',', ':')) + '\n')
    print('converted structure-cards.json and muscle-cards.json')


if __name__ == '__main__':
    main()
