"""Clinical test names per structure (ROADMAP 4-2 step 9).

Learners see the test name and one line on what it looks at — no procedure text, no animation, no
diagnostic accuracy. A test is listed only when two independent publishers state the same target
(Wikipedia, Orthobullets, Physiotutors, MedBridge; pages read 2026-11-19). Tests or targets with one
publisher only are kept in HELD and are not written to the runtime.

Run: python3 atlas-data/pipeline/clinical_tests.py
Writes atlas-data/runtime/clinical-tests.json (learner fields) and
atlas-data/anatomy/clinical-test-checks.json (sources, held items).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACCESSED = '2026-11-19'

SOURCES = {
    'wp': 'en.wikipedia.org',
    'ob': 'www.orthobullets.com',
    'pt': 'www.physiotutors.com',
    'mb': 'www.medbridge.com',
}

# id: (name, English name, what it looks at (one line), target English names, [(source, url, what that page states)])
TESTS = {
    'jobe': ('엠티캔·풀캔 검사', 'Empty can / full can (Jobe) test',
             '어깨 높이로 든 팔을 내리누를 때의 약함·통증 — 극상근. 다른 근육도 함께 버티므로 극상근만 따로 보지는 못합니다.',
             ['Supraspinatus muscle'],
             [('ob', 'https://www.orthobullets.com/shoulder-and-elbow/3037/shoulder-exam', 'Jobe test: supraspinatus weakness / impingement'),
              ('pt', 'https://www.physiotutors.com/wiki/full-can-test', 'full can: supraspinatus tears; does not selectively activate supraspinatus')]),
    'erResist': ('외회전 저항 검사', 'Resisted external rotation (infraspinatus test)',
                 '팔을 옆구리에 붙이고 바깥으로 돌리는 힘의 약함 — 극하근.',
                 ['Infraspinatus muscle'],
                 [('pt', 'https://www.physiotutors.com/wiki/infraspinatus-test', 'weakness in external rotation, arms at side: infraspinatus'),
                  ('ob', 'https://www.orthobullets.com/shoulder-and-elbow/3043/rotator-cuff-tears', 'infraspinatus: ER weakness at 0° abduction')]),
    'erLag': ('외회전 지연 징후', 'External rotation lag sign',
              '끝까지 바깥돌림해 둔 팔을 놓으면 버티지 못하고 돌아옴 — 극하근 힘줄 파열.',
              ['Infraspinatus muscle'],
              [('wp', 'https://en.wikipedia.org/wiki/Rotator_cuff_tear', 'external rotation lag sign: infraspinatus tears'),
               ('ob', 'https://www.orthobullets.com/shoulder-and-elbow/3037/shoulder-exam', 'external rotation lag: infraspinatus'),
               ('pt', 'https://www.physiotutors.com/wiki/lateral-rotation-lag-sign', 'lag sign: supraspinatus, infraspinatus, teres minor')]),
    'bellyPress': ('벨리프레스 검사', 'Belly press test',
                   '손바닥으로 배를 누르며 팔꿈치를 앞으로 유지하지 못함 — 견갑하근.',
                   ['Subscapularis muscle'],
                   [('wp', 'https://en.wikipedia.org/wiki/Subscapularis_muscle', 'belly press: significant subscapularis tearing'),
                    ('ob', 'https://www.orthobullets.com/shoulder-and-elbow/3037/shoulder-exam', 'belly press: subscapularis')]),
    'liftOff': ('리프트오프 검사', 'Lift-off test (Gerber)',
                '허리 뒤에 댄 손을 등에서 떼어 내지 못함 — 견갑하근.',
                ['Subscapularis muscle'],
                [('wp', 'https://en.wikipedia.org/wiki/Subscapularis_muscle', 'Gerber lift-off: established test for subscapularis'),
                 ('ob', 'https://www.orthobullets.com/shoulder-and-elbow/3037/shoulder-exam', 'lift-off: subscapularis')]),
    'finkelstein': ('핀켈스타인 검사', 'Finkelstein test',
                    '엄지를 쥐고 손목을 자쪽으로 굽힐 때 노뼈 붓돌기 통증 — 장무지외전근·단무지신근 힘줄집 (드퀘르벵).',
                    ['Abductor pollicis longus', 'Extensor pollicis brevis', 'Tendon sheath - abd. pollicis longus - ext. pollicis brevis'],
                    [('wp', 'https://en.wikipedia.org/wiki/Finkelstein%27s_test', 'APL and EPB tenosynovitis'),
                     ('pt', 'https://www.physiotutors.com/wiki/finkelstein-test', 'synovial sheath of EPB and APL')]),
    'thomas': ('토마스 검사', 'Thomas test',
               '반대쪽 무릎을 끌어안을 때 편 다리의 넙다리가 침대에서 뜸 — 장요근 단축.',
               ['Psoas major', 'Iliacus muscle'],
               [('wp', 'https://en.wikipedia.org/wiki/Thomas_test', 'hip flexion contracture; tight iliopsoas'),
                ('pt', 'https://www.physiotutors.com/wiki/thomas-test/', 'iliopsoas shortening')]),
    'slr': ('하지직거상 검사 (SLR)', 'Straight leg raise',
            '편 다리를 들 때 다리로 뻗치는 익숙한 통증 — 좌골신경(허리 신경뿌리) 긴장.',
            ['Sciatic nerve'],
            [('wp', 'https://en.wikipedia.org/wiki/Straight_leg_raise', 'lumbar nerve root tension; radiating leg pain'),
             ('pt', 'https://www.physiotutors.com/wiki/straight-leg-raise-test', 'tensions the sciatic nerve; familiar leg pain')]),
    'aslr': ('능동 하지직거상 검사 (ASLR)', 'Active straight leg raise',
             '누워 편 다리를 스스로 들기 어려움(골반을 조여 주면 쉬워짐) — 골반띠의 하중 전달.',
             ['Anterior sacro-iliac ligament', 'Interosseous sacro-iliac ligament', 'Posterior sacro-iliac ligament', 'Pubic symphysis'],
             [('pt', 'https://www.physiotutors.com/wiki/active-straight-leg-raise-test', 'load transfer between leg and trunk in pelvic girdle pain'),
              ('mb', 'https://www.medbridge.com/educate/exam-tests/42', 'stability of lumbar spine and pelvic girdle (SIJ, pubic symphysis)')]),
    'mcmurray': ('맥머레이 검사', 'McMurray test',
                 '무릎을 굽혔다 펴며 정강이를 돌릴 때 딸깍·걸림·통증 — 바깥돌림은 내측 반월, 안쪽돌림은 외측 반월.',
                 ['Medial meniscus', 'Lateral meniscus'],
                 [('wp', 'https://en.wikipedia.org/wiki/McMurray_test', 'meniscus; ER → posterior medial, IR → posterior lateral'),
                  ('pt', 'https://www.physiotutors.com/wiki/mcmurray-test', 'tibia lateral rotation → medial meniscus, medial rotation → lateral meniscus')]),
    'valgus': ('외반 스트레스 검사', 'Valgus stress test',
               '무릎 안쪽이 벌어짐·통증 — 30° 굽힘에서는 내측측부인대, 편 자세에서도 벌어지면 십자인대까지.',
               ['Superficial part of tibial collateral ligament', 'Deep part of tibial collateral ligament'],
               [('wp', 'https://en.wikipedia.org/wiki/Valgus_stress_test', 'MCL; 30° MCL primary, 0° adds capsule and cruciates'),
                ('ob', 'https://www.orthobullets.com/knee-and-sports/3003/history-and-physical-exam-of-the-knee', '30° only = isolated MCL; 0° and 30° = with ACL/PCL'),
                ('pt', 'https://www.physiotutors.com/wiki/valgus-stress-test', 'medial gapping / pain')]),
    'varus': ('내반 스트레스 검사', 'Varus stress test',
              '무릎 가쪽이 벌어짐·통증 — 외측측부인대.',
              ['Fibular collateral ligament'],
              [('pt', 'https://www.physiotutors.com/wiki/varus-stress-test', 'LCL; gapping / pain'),
               ('ob', 'https://www.orthobullets.com/knee-and-sports/3003/history-and-physical-exam-of-the-knee', 'lateral opening at 30° = LCL')]),
}

# Not shown: one publisher only, or no readable page (Physiopedia and NCBI/StatPearls refused automated reading).
HELD = [
    {'item': 'FABER (Patrick) — hip joint vs sacroiliac joint by pain location', 'why': 'Wikipedia only (Patrick\'s test, SIJ dysfunction, FAI pages); SIJ sentence marked citation needed'},
    {'item': 'FADIR — femoroacetabular impingement / labrum', 'why': 'Wikipedia only (FAI page)'},
    {'item': 'Hip scour / quadrant test', 'why': 'no readable page'},
    {'item': 'Lumbar quadrant (Kemp) test — facet joints', 'why': 'not checked; the model has no zygapophysial joint structure to attach it to'},
    {'item': 'Thomas test → rectus femoris (knee extends) and tensor fasciae latae (thigh abducts)', 'why': 'Wikipedia only; Physiotutors names iliopsoas only'},
    {'item': 'SLR → hamstrings, and the 30–70° range', 'why': 'no page names hamstring tightness; angle range on Wikipedia only'},
    {'item': 'Resisted external rotation at 90° abduction → teres minor', 'why': 'Orthobullets only'},
    {'item': 'Varus stress at 0° → cruciate ligaments too', 'why': 'Orthobullets only'},
]


def main():
    names = {r['names']['en'] for r in json.loads((ROOT / 'atlas-data/runtime/structures.json').read_text())['structures']}
    for tid, (_, _, _, targets, sources) in TESTS.items():
        missing = [t for t in targets if t not in names]
        assert not missing, f'{tid}: no structure {missing}'
        assert len({s for s, _, _ in sources}) >= 2, f'{tid}: needs two publishers'
    runtime = {
        'schemaVersion': 1,
        'note': 'Test names and one line on what each looks at; targets are structure English names. Sources: atlas-data/anatomy/clinical-test-checks.json',
        'tests': [{'id': tid, 'name': n, 'en': en, 'what': what, 'targets': targets} for tid, (n, en, what, targets, _) in TESTS.items()],
    }
    checks = {
        'schemaVersion': 1,
        'method': 'Shown only when two independent publishers state the same target. Facts were read from each page; no text copied. Accessed ' + ACCESSED + '.',
        'publishers': SOURCES,
        'tests': {tid: [{'by': s, 'url': u, 'states': st} for s, u, st in sources] for tid, (*_, sources) in TESTS.items()},
        'held': HELD,
    }
    (ROOT / 'atlas-data/runtime/clinical-tests.json').write_text(json.dumps(runtime, ensure_ascii=False, indent=1) + '\n')
    (ROOT / 'atlas-data/anatomy/clinical-test-checks.json').write_text(json.dumps(checks, ensure_ascii=False, indent=1) + '\n')
    print(len(TESTS), 'tests,', len(HELD), 'held')


if __name__ == '__main__':
    main()
