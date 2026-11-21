"""Posture patterns (Janda's crossed syndromes) for colouring the model (ROADMAP 4-2 step 10).

A muscle is listed only when both publishers name it for the same side of the pattern:
Physiopedia (Upper-Crossed Syndrome, Lower crossed syndrome; read in a browser) and learnmuscles.com
(Muscolino, tables of facilitated / inhibited muscles). Read 2026-11-19; no text copied.
Both pages say the patterns are clinical observations, not validated diagnoses; the learner note says so too.

Run: python3 atlas-data/pipeline/posture_patterns.py
Writes atlas-data/runtime/posture-patterns.json (learner fields) and atlas-data/anatomy/posture-pattern-checks.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SOURCES = {
    'pp-upper': 'https://www.physio-pedia.com/Upper-Crossed_Syndrome',
    'pp-lower': 'https://www.physio-pedia.com/Lower_crossed_syndrome',
    'lm-upper': 'https://learnmuscles.com/?p=5520',
    'lm-lower': 'https://learnmuscles.com/?p=5491',
}

PATTERNS = {
    'upperCrossed': {
        'name': '상부 교차 증후군', 'en': 'Upper crossed syndrome (Janda)',
        'signs': '등 굽음(흉추 후만 증가), 어깨가 앞으로 말림(어깨띠 내밈)',
        'short': ['Descending part of trapezius muscle', 'Levator scapulae', 'Clavicular head of pectoralis major muscle',
                  'Sternocostal head of pectoralis major muscle', '(Abdominal part of pectoralis major muscle)', 'Pectoralis minor muscle',
                  'Sternocleidomastoid muscle'],
        'weak': ['Longus colli muscle', 'Longus capitis muscle', 'Serratus anterior muscle', 'Rhomboid major muscle', 'Rhomboid minor muscle',
                 'Transverse part of trapezius muscle', 'Ascending part of trapezius muscle'],
        'sources': ['pp-upper', 'lm-upper'],
    },
    'lowerCrossed': {
        'name': '하부 교차 증후군', 'en': 'Lower crossed syndrome (Janda)',
        'signs': '골반 앞기울임(전방경사), 허리 앞굽음(요추 전만) 증가',
        'short': ['Psoas major', 'Iliacus muscle', 'Rectus femoris muscle', 'Tensor fasciae latae',
                  'Iliocostalis lumborum muscle', 'Iliocostalis thoracis muscle', 'Longissimus thoracis muscle', 'Spinalis thoracis muscle',
                  'Quadratus lumborum muscle'],
        'weak': ['Gluteus maximus muscle', 'Gluteus medius muscle',
                 'Rectus abdominis muscle', 'External abdominal oblique muscle', 'Internal abdominal oblique muscle', 'Transversus abdominis muscle'],
        'note': '배근육은 두 출처 모두 약해지는 쪽으로 꼽지만, 어느 층인지는 다릅니다(복직근·외복사근·내복사근 / 복횡근). 그래서 배벽 전체를 칠했습니다.',
        'sources': ['pp-lower', 'lm-lower'],
    },
}

# Named by one publisher only: not coloured.
HELD = [
    {'pattern': 'upperCrossed', 'item': 'suboccipital muscles (tight)', 'by': 'pp-upper'},
    {'pattern': 'upperCrossed', 'item': 'subclavius (tight)', 'by': 'lm-upper'},
    {'pattern': 'upperCrossed', 'item': 'infraspinatus, teres minor, thoracic erector spinae (weak)', 'by': 'lm-upper'},
    {'pattern': 'upperCrossed', 'item': 'medially rotated arms (sign)', 'by': 'lm-upper'},
    {'pattern': 'upperCrossed', 'item': 'forward head posture (sign)', 'by': 'pp-upper'},
    {'pattern': 'lowerCrossed', 'item': 'thigh adductors (tight)', 'by': 'lm-lower'},
    {'pattern': 'lowerCrossed', 'item': 'gluteus minimus (weak)', 'by': 'lm-lower'},
    {'pattern': 'lowerCrossed', 'item': 'hamstrings: increased tone (pp) / likely tight (learnmuscles ?p=5503), described as compensation; not coloured either way', 'by': 'both, unclear side'},
]


def main():
    names = {r['names']['en'] for r in json.loads((ROOT / 'atlas-data/runtime/structures.json').read_text())['structures'] if r['kind'] == 'muscle'}
    for pid, p in PATTERNS.items():
        missing = [m for m in p['short'] + p['weak'] if m not in names]
        assert not missing, f'{pid}: {missing}'
        assert not set(p['short']) & set(p['weak']), pid
    runtime = {
        'schemaVersion': 1,
        'note': 'Muscles by structure English name. short = tight / overactive, weak = inhibited. Sources: atlas-data/anatomy/posture-pattern-checks.json',
        'patterns': [{'id': pid, **{k: v for k, v in p.items() if k != 'sources'}} for pid, p in PATTERNS.items()],
    }
    checks = {
        'schemaVersion': 1,
        'method': 'A muscle is coloured only when both pages name it on the same side. Read 2026-11-19; no text copied.',
        'sources': SOURCES,
        'patterns': {pid: p['sources'] for pid, p in PATTERNS.items()},
        'held': HELD,
        'evidence': 'Both pages: observational clinical pattern (Janda), not a validated diagnosis.',
    }
    (ROOT / 'atlas-data/runtime/posture-patterns.json').write_text(json.dumps(runtime, ensure_ascii=False, indent=1) + '\n')
    (ROOT / 'atlas-data/anatomy/posture-pattern-checks.json').write_text(json.dumps(checks, ensure_ascii=False, indent=1) + '\n')
    print({pid: (len(p['short']), len(p['weak'])) for pid, p in PATTERNS.items()})


if __name__ == '__main__':
    main()
