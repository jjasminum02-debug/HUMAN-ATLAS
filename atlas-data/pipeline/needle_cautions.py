"""Light caution marks on acupoints over the pleura or the kidney (ROADMAP 4-4 V5).

Only the two cases the user asked for: points where deep needling can reach the pleura and lung (pneumothorax)
and points over the kidney. A point is marked only when two independent publishers name it; the rest are held.
The app shows a small chip and one line; no needling depth or angle is given (AGENTS.md scope).

Sources (read 2026-11-20; no text copied):
  csp      - ACPTR/CSP "Learning from Litigation: Pneumothorax" (2023), list of thoracic and supraclavicular regions.
  chestCT  - PMC4592721, safe depths of chest acupoints measured to the pleura on CT (pneumothorax framing).
  backCT   - PMC4769822 (Ma 2016), upper back acupoints measured to the pleura on CT in children.
  birch    - PMC3804079 (Birch 2013), table of points implicated in pneumothorax.
  gb21     - PMC5817322, GB21 safe depth by posture and breathing (pneumothorax risk).
  meandqi  - Me & Qi point pages (practitioner reference) with kidney warnings at BL23 and BL52.
  bmas     - BMAS blog (2023) on the kidney laceration case of Cheng et al., Asian J Surg 2023: the authors
             attribute it to a needle at BL23; the blogger thinks a more lateral point such as BL52 more likely.

Run: python3 atlas-data/pipeline/needle_cautions.py
Writes atlas-data/runtime/acupoint-cautions.json (learner fields) and atlas-data/anatomy/acupoint-caution-checks.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SOURCES = {
    'csp': 'https://acptr.csp.org.uk/system/files/publication_files/LearningFromLitigation_Pneumothorax_2023.pdf',
    'chestCT': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4592721/',
    'backCT': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4769822/',
    'birch': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC3804079/',
    'gb21': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC5817322/',
    'meandqi': 'https://www.meandqi.com/knowledge-base/acupuncture/bladder-meridian/',
    'bmas': 'https://bmas.blog/2023/04/25/kidney-laceration-after-acupuncture-2023/',
}


def span(prefix, a, b):
    return [f'{prefix}{n}' for n in range(a, b + 1)]


# Codes each publisher names (what the page lists, not inferred).
NAMED = {
    'chest': {
        'csp': ['GB21', 'LU1', *span('SI', 12, 15), *span('BL', 11, 22), *span('BL', 41, 52), *span('KI', 22, 27),
                *span('ST', 12, 18), *span('SP', 17, 21), 'LR13', 'LR14'],
        'chestCT': ['LU1', 'LU2', *span('ST', 13, 18), *span('KI', 22, 27), *span('SP', 17, 20), 'PC1', 'GB22', 'GB23'],
        'backCT': [*span('BL', 11, 17), *span('BL', 41, 46), 'SI14', 'SI15', 'GB21', 'SP21'],
        'birch': ['BL13', 'GB21'],
        'gb21': ['GB21'],
    },
    'kidney': {
        'meandqi': ['BL23', 'BL52'],
        'bmas': ['BL23', 'BL52'],
    },
}

KINDS = {
    'chest': {'label': '흉강 주의', 'hint': '아래에 가슴막과 폐가 가까워, 기흉이 보고된 부위입니다.'},
    'kidney': {'label': '신장 주의', 'hint': '아래에 콩팥이 가까워, 콩팥 손상이 보고된 부위입니다.'},
}

NOTES = {
    'csp': 'CSP는 "LU1과 주변", 경맥 구간(BL11–22, BL41–52 등)으로 적습니다. 구간 안의 혈은 다른 출처가 함께 꼽을 때만 표시했습니다.',
    'bmas': 'BL23은 증례 저자(Cheng 2023)의 판단, BL52는 해설자의 추정입니다. 신장 쪽 두 출처 모두 연구 논문이 아니어서 교과서 대조가 남아 있습니다.',
    'gb25': 'GB25(경문)는 meandqi가 복막만 경고하고 신장 손상은 적지 않아 보류했습니다.',
}


def main():
    acupoints = json.loads((ROOT / 'atlas-data/runtime/acupoints.json').read_text())
    known = {c['code'] for c in acupoints['concepts']}
    points, checks, held = {}, {}, []
    for kind, by in NAMED.items():
        codes = sorted({c for lst in by.values() for c in lst}, key=lambda c: (c.rstrip('0123456789'), int(c[len(c.rstrip('0123456789')):])))
        for code in codes:
            names = [s for s, lst in by.items() if code in lst]
            if code not in known:
                held.append({'code': code, 'kind': kind, 'by': names, 'why': 'not in this model'})
            elif len(names) >= 2:
                points[code] = kind
                checks[code] = {'kind': kind, 'sources': names}
            else:
                held.append({'code': code, 'kind': kind, 'by': names, 'why': 'one source'})
    held.append({'code': 'GB25', 'kind': 'kidney', 'by': ['meandqi'], 'why': 'peritoneum warning only'})
    runtime = {
        'schemaVersion': 1,
        'note': '두 출처가 함께 꼽은 혈만 가볍게 표시합니다. 자침 깊이·각도 기준이 아닙니다.',
        'kinds': KINDS,
        'points': points,
    }
    (ROOT / 'atlas-data/runtime/acupoint-cautions.json').write_text(json.dumps(runtime, ensure_ascii=False, indent=1) + '\n')
    (ROOT / 'atlas-data/anatomy/acupoint-caution-checks.json').write_text(json.dumps(
        {'schemaVersion': 1, 'read': '2026-11-20', 'sources': SOURCES, 'notes': NOTES, 'points': checks, 'held': held},
        ensure_ascii=False, indent=1) + '\n')
    print(f'{len(points)} marked ({sum(k == "chest" for k in points.values())} chest, {sum(k == "kidney" for k in points.values())} kidney), {len(held)} held')


if __name__ == '__main__':
    main()
