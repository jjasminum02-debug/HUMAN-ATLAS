"""Korean names for structures that had none (ROADMAP C1).

  python3 atlas-data/pipeline/names_ko.py   -> atlas-data/terminology/structure-names-ko.json

Each entry: English source name -> (우리말 koModern, 한자어 in Hangul koTraditional, basis).
basis S: established 대한해부학회 (KAA) term. C: composed from KAA component terms (e.g. 노 + 손목 + 인대),
not individually attested. Series rules (discs, nuclei, costal cartilages, teeth) are R.
Names not confidently known are deliberately absent and land in the exception list instead.
AI-written; sample cross-check results are recorded in the output, human review is separate.
"""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'atlas-data/terminology/structure-names-ko.json'

NAMES = {
    # ── Shoulder girdle / shoulder
    'Acromioclavicular ligament': ('봉우리빗장인대', '견봉쇄골인대', 'S'),
    'Coraco-acromial ligament': ('부리봉우리인대', '오훼견봉인대', 'S'),
    'Coracohumeral ligament': ('부리위팔인대', '오훼상완인대', 'S'),
    'Conoid ligament': ('원뿔인대', '원추인대', 'S'),
    'Trapezoid ligament': ('마름인대', '능형인대', 'S'),
    'Costoclavicular ligament': ('갈비빗장인대', '늑쇄인대', 'S'),
    'Interclavicular ligament': ('빗장사이인대', '쇄골간인대', 'S'),
    'Anterior sternoclavicular ligament': ('앞복장빗장인대', '전흉쇄인대', 'S'),
    'Posterior sternoclavicular ligament': ('뒤복장빗장인대', '후흉쇄인대', 'S'),
    'Superior glenohumeral ligament': ('위오목위팔인대', '상관절상완인대', 'S'),
    'Middle glenohumeral ligament': ('중간오목위팔인대', '중관절상완인대', 'S'),
    'Inferior glenohumeral ligament': ('아래오목위팔인대', '하관절상완인대', 'S'),
    'Transverse humeral ligament': ('위팔가로인대', '상완횡인대', 'S'),
    'Superior transverse scapular ligament': ('위어깨가로인대', '상견갑횡인대', 'S'),
    'Inferior transverse scapular ligament': ('아래어깨가로인대', '하견갑횡인대', 'S'),
    'Glenoid labrum': ('관절오목테두리', '관절와순', 'S'),
    # ── Elbow / forearm
    'Ulnar collateral ligament': ('자쪽곁인대', '척측측부인대', 'S'),
    'Radial collateral ligament': ('노쪽곁인대', '요측측부인대', 'S'),
    'Annular ligament of radius': ('노뼈둘레인대', '요골윤상인대', 'S'),
    'Quadrate ligament': ('네모인대', '방형인대', 'S'),
    'Oblique cord': ('빗끈', '사삭', 'S'),
    'Interosseous membrane of forearm': ('아래팔뼈사이막', '전완골간막', 'S'),
    'Dorsal radio-ulnar ligament': ('등쪽노자인대', '배측요척인대', 'S'),
    'Palmar radio-ulnar ligament': ('손바닥쪽노자인대', '장측요척인대', 'S'),
    # ── Wrist / hand
    'Radial collateral ligament of wrist joint': ('손목노쪽곁인대', '요측수근측부인대', 'S'),
    'Ulnar collateral ligament of wrist joint': ('손목자쪽곁인대', '척측수근측부인대', 'S'),
    'Dorsal radiocarpal ligament': ('등쪽노손목인대', '배측요골수근인대', 'S'),
    'Radiate carpal ligament': ('부챗살손목인대', '방사상수근인대', 'S'),
    'Pisohamate ligament': ('콩알갈고리인대', '두상유구인대', 'S'),
    'Pisometacarpal ligament': ('콩알손허리인대', '두상중수인대', 'S'),
    'Pisotriquetral ligament': ('콩알세모인대', '두상삼각인대', 'C'),
    'Dorsal intercarpal ligaments': ('등쪽손목뼈사이인대', '배측수근간인대', 'S'),
    'Dorsal carpometacarpal ligaments': ('등쪽손목손허리인대', '배측수근중수인대', 'S'),
    'Palmar carpometacarpal ligaments': ('손바닥쪽손목손허리인대', '장측수근중수인대', 'S'),
    'Dorsal metacarpal ligaments': ('등쪽손허리인대', '배측중수인대', 'S'),
    'Palmar metacarpal ligaments': ('손바닥쪽손허리인대', '장측중수인대', 'S'),
    'Interosseous metacarpal ligaments': ('뼈사이손허리인대', '골간중수인대', 'S'),
    'Deep transverse metacarpal ligament': ('깊은가로손허리인대', '심횡중수인대', 'S'),
    'Superficial transverse metacarpal ligament': ('얕은가로손허리인대', '천횡중수인대', 'S'),
    'Collateral metacarpophalangeal ligaments': ('손허리손가락관절 곁인대', '중수지절관절 측부인대', 'C'),
    'Collateral interphalangeal ligaments of hand': ('손가락뼈사이관절 곁인대', '수지절간관절 측부인대', 'C'),
    'Palmar interphalangeal ligaments': ('손가락뼈사이관절 손바닥쪽인대', '수지절간관절 장측인대', 'C'),
    'Dorsal ulnocarpal ligament': ('등쪽자손목인대', '배측척골수근인대', 'C'),
    'Ulnolunate ligament': ('자반달인대', '척골월상인대', 'C'),
    'Ulnotriquetral ligament': ('자세모인대', '척골삼각인대', 'C'),
    'Ulnocapitate ligament': ('자알머리인대', '척골유두인대', 'C'),
    'Ulnopisiform ligament': ('자콩알인대', '척골두상인대', 'C'),
    'Radiocapitate ligament': ('노알머리인대', '요골유두인대', 'C'),
    'Radioscaphocapitate ligament': ('노손배알머리인대', '요골주상유두인대', 'C'),
    'Scapholunate interosseous ligament': ('손배반달뼈사이인대', '주상월상골간인대', 'C'),
    'Lunotriquetral interosseous ligament': ('반달세모뼈사이인대', '월상삼각골간인대', 'C'),
    'Palmar lunotriquetral ligament': ('손바닥쪽반달세모인대', '장측월상삼각인대', 'C'),
    'Dorsal scaphotriquetral ligament': ('등쪽손배세모인대', '배측주상삼각인대', 'C'),
    'Palmar scaphotriquetral ligament': ('손바닥쪽손배세모인대', '장측주상삼각인대', 'C'),
    'Scaphocapitate ligament': ('손배알머리인대', '주상유두인대', 'C'),
    'Scaphotrapeziotrapezoidal ligament': ('손배큰마름작은마름인대', '주상대능형소능형인대', 'C'),
    'Trapeziotrapezoidal interosseous ligament': ('큰마름작은마름뼈사이인대', '대능형소능형골간인대', 'C'),
    'Trapezoideocapitate interosseous ligament': ('작은마름알머리뼈사이인대', '소능형유두골간인대', 'C'),
    'Palmar trapezoideocapitate ligament': ('손바닥쪽작은마름알머리인대', '장측소능형유두인대', 'C'),
    'Capitohamate interosseous ligament': ('알머리갈고리뼈사이인대', '유두유구골간인대', 'C'),
    'Palmar capitohamate ligament': ('손바닥쪽알머리갈고리인대', '장측유두유구인대', 'C'),
    'Triquetrocapitate ligament': ('세모알머리인대', '삼각유두인대', 'C'),
    'Triquetrohamate ligament': ('세모갈고리인대', '삼각유구인대', 'C'),
    # ── Hip / pelvis
    'Descending part of iliofemoral ligament': ('엉덩넙다리인대 내림부분', '장골대퇴인대 하행부', 'C'),
    'Transverse part of iliofemoral ligament': ('엉덩넙다리인대 가로부분', '장골대퇴인대 횡부', 'C'),
    'Ischiofemoral ligament': ('궁둥넙다리인대', '좌골대퇴인대', 'S'),
    'Pubofemoral ligament': ('두덩넙다리인대', '치골대퇴인대', 'S'),
    'Ligament of head of femur': ('넙다리뼈머리인대', '대퇴골두인대', 'S'),
    'Transverse acetabular ligament': ('절구가로인대', '관골구횡인대', 'S'),
    'Zona orbicularis': ('둘레띠', '윤대', 'S'),
    'Acetabular labrum': ('절구테두리', '관골구순', 'S'),
    'Sacrospinous ligament': ('엉치가시인대', '천극인대', 'S'),
    'Sacrotuberous ligament': ('엉치결절인대', '천결절인대', 'S'),
    'Anterior sacro-iliac ligament': ('앞엉치엉덩인대', '전천장인대', 'S'),
    'Posterior sacro-iliac ligament': ('뒤엉치엉덩인대', '후천장인대', 'S'),
    'Interosseous sacro-iliac ligament': ('뼈사이엉치엉덩인대', '골간천장인대', 'S'),
    'Iliolumbar ligament': ('엉덩허리인대', '장요인대', 'S'),
    'Superior pubic ligament': ('위두덩인대', '상치골인대', 'S'),
    'Inferior pubic ligament': ('아래두덩인대', '하치골인대', 'S'),
    'Inguinal ligament': ('샅고랑인대', '서혜인대', 'S'),
    'Interpubic disc': ('두덩사이원판', '치골간원판', 'S'),
    'Pubic symphysis': ('두덩결합', '치골결합', 'S'),
    'Sacrococcygeal symphysis': ('엉치꼬리결합', '천미결합', 'S'),
    'Obturator membrane': ('폐쇄막', '폐쇄막', 'S'),
    # ── Knee
    'Anterior cruciate ligament': ('앞십자인대', '전십자인대', 'S'),
    'Posterior cruciate ligament': ('뒤십자인대', '후십자인대', 'S'),
    'Fibular collateral ligament': ('종아리쪽곁인대', '비측측부인대', 'S'),
    'Superficial part of tibial collateral ligament': ('정강쪽곁인대 얕은부분', '경측측부인대 천부', 'C'),
    'Deep part of tibial collateral ligament': ('정강쪽곁인대 깊은부분', '경측측부인대 심부', 'C'),
    'Transverse ligament of knee': ('무릎가로인대', '슬횡인대', 'S'),
    'Oblique popliteal ligament': ('빗오금인대', '사슬와인대', 'S'),
    'Arcuate popliteal ligament': ('활꼴오금인대', '궁상슬와인대', 'S'),
    'Popliteofibular ligament': ('오금종아리인대', '슬와비골인대', 'C'),
    'Meniscopatellar ligament': ('반달무릎뼈인대', '반월슬개인대', 'C'),
    'Anterior meniscotibial ligament (Lateral meniscus)': ('앞반달정강인대 (가쪽반달)', '전반월경골인대 (외측반월)', 'C'),
    'Anterior meniscotibial ligament (Medial meniscus)': ('앞반달정강인대 (안쪽반달)', '전반월경골인대 (내측반월)', 'C'),
    'Posterior meniscotibial ligament (Lateral meniscus)': ('뒤반달정강인대 (가쪽반달)', '후반월경골인대 (외측반월)', 'C'),
    'Posterior meniscotibial ligament (Medial meniscus)': ('뒤반달정강인대 (안쪽반달)', '후반월경골인대 (내측반월)', 'C'),
    'Anterior ligament of fibular head': ('앞종아리뼈머리인대', '전비골두인대', 'S'),
    'Posterior ligament of fibular head': ('뒤종아리뼈머리인대', '후비골두인대', 'S'),
    'Medial meniscus': ('안쪽반달', '내측반월', 'S'),
    'Lateral meniscus': ('가쪽반달', '외측반월', 'S'),
    'Infrapatellar fat pad': ('무릎뼈아래지방체', '슬개하지방체', 'S'),
    'Medial patellar retinaculum': ('안쪽무릎뼈지지띠', '내측슬개지대', 'S'),
    'Lateral patellar retinaculum': ('가쪽무릎뼈지지띠', '외측슬개지대', 'S'),
    'Interosseous membrane of leg': ('종아리뼈사이막', '하퇴골간막', 'S'),
    # ── Ankle / foot
    'Anterior talofibular ligament': ('앞목말종아리인대', '전거비인대', 'S'),
    'Posterior talofibular ligament': ('뒤목말종아리인대', '후거비인대', 'S'),
    'Calcaneofibular ligament': ('발꿈치종아리인대', '종비인대', 'S'),
    'Anterior tibiofibular ligament': ('앞정강종아리인대', '전경비인대', 'S'),
    'Posterior tibiofibular ligament': ('뒤정강종아리인대', '후경비인대', 'S'),
    'Transverse tibiofibular ligament': ('가로정강종아리인대', '횡경비인대', 'C'),
    'Posterior tibiotalar ligament': ('뒤정강목말인대', '후경거인대', 'C'),
    'Tibiocalcaneal ligament': ('정강발꿈치인대', '경종인대', 'C'),
    'Tibionavicular ligament': ('정강발배인대', '경주인대', 'C'),
    'Talocalcaneal interosseous ligament': ('뼈사이목말발꿈치인대', '골간거종인대', 'S'),
    'Anterior talocalcaneal ligament': ('앞목말발꿈치인대', '전거종인대', 'S'),
    'Posterior talocalcaneal ligament': ('뒤목말발꿈치인대', '후거종인대', 'S'),
    'Lateral talocalcaneal ligament': ('가쪽목말발꿈치인대', '외측거종인대', 'S'),
    'Medial talocalcaneal ligament': ('안쪽목말발꿈치인대', '내측거종인대', 'S'),
    'Talonavicular ligament': ('목말발배인대', '거주인대', 'S'),
    'Calcaneonavicular ligament': ('발꿈치발배인대', '종주인대', 'S'),
    'Calcaneocuboid ligament': ('발꿈치입방인대', '종입방인대', 'S'),
    'Dorsal calcaneocuboid ligament': ('등쪽발꿈치입방인대', '배측종입방인대', 'S'),
    'Plantar calcaneonavicular ligament': ('발바닥발꿈치발배인대', '족저종주인대', 'S'),
    'Plantar calcaneocuboid ligament': ('발바닥발꿈치입방인대', '족저종입방인대', 'S'),
    'Long plantar ligament': ('긴발바닥인대', '장족저인대', 'S'),
    'Dorsal cuboideonavicular ligament': ('등쪽입방발배인대', '배측입방주상인대', 'S'),
    'Plantar cuboideonavicular ligament': ('발바닥입방발배인대', '족저입방주상인대', 'S'),
    'Dorsal cuneonavicular ligaments': ('등쪽쐐기발배인대', '배측설주인대', 'S'),
    'Plantar cuneonavicular ligaments': ('발바닥쐐기발배인대', '족저설주인대', 'S'),
    'Dorsal intercuneiform ligaments': ('등쪽쐐기뼈사이인대', '배측설상간인대', 'S'),
    'Plantar intercuneiform ligaments': ('발바닥쐐기뼈사이인대', '족저설상간인대', 'S'),
    'Intercuneiform interosseous ligaments': ('뼈사이쐐기뼈사이인대', '골간설상간인대', 'S'),
    'Dorsal cuneocuboid ligament': ('등쪽쐐기입방인대', '배측설입방인대', 'S'),
    'Plantar cuneocuboid ligament': ('발바닥쐐기입방인대', '족저설입방인대', 'S'),
    'Cuneocuboid interosseous ligament': ('뼈사이쐐기입방인대', '골간설입방인대', 'S'),
    'Dorsal tarsometatarsal ligaments': ('등쪽발목발허리인대', '배측족근중족인대', 'S'),
    'Plantar tarsometatarsal ligaments': ('발바닥발목발허리인대', '족저족근중족인대', 'S'),
    'Cuneometatarsal interosseous ligaments': ('뼈사이쐐기발허리인대', '골간설중족인대', 'S'),
    'Dorsal metatarsal ligaments': ('등쪽발허리인대', '배측중족인대', 'S'),
    'Plantar metatarsal ligaments': ('발바닥발허리인대', '족저중족인대', 'S'),
    'Metatarsal interosseous ligaments': ('뼈사이발허리인대', '골간중족인대', 'S'),
    'Deep transverse metatarsal ligament': ('깊은가로발허리인대', '심횡중족인대', 'S'),
    'Superficial transverse metatarsal ligament': ('얕은가로발허리인대', '천횡중족인대', 'S'),
    'Plantar metatarsophalangeal ligaments': ('발허리발가락관절 발바닥쪽인대', '중족지절관절 족저인대', 'C'),
    'Collateral metatarsophalangeal ligaments': ('발허리발가락관절 곁인대', '중족지절관절 측부인대', 'C'),
    'Collateral interphalangeal ligaments of foot': ('발가락뼈사이관절 곁인대', '족지절간관절 측부인대', 'C'),
    'Plantar interphalangeal ligaments': ('발가락뼈사이관절 발바닥쪽인대', '족지절간관절 족저인대', 'C'),
    'Intersesamoid ligament': ('종자뼈사이인대', '종자골간인대', 'C'),
    # ── Vertebral column / ribs
    'Anterior longitudinal ligament': ('앞세로인대', '전종인대', 'S'),
    'Posterior longitudinal ligament': ('뒤세로인대', '후종인대', 'S'),
    'Ligamenta flava': ('황색인대', '황색인대', 'S'),
    'Interspinous ligaments': ('가시사이인대', '극간인대', 'S'),
    'Supraspinous ligament': ('가시끝인대', '극상인대', 'S'),
    'Intertransverse ligaments': ('가로돌기사이인대', '횡돌기간인대', 'S'),
    'Nuchal ligament': ('목덜미인대', '항인대', 'S'),
    'Radiate ligament of head of rib': ('부챗살갈비뼈머리인대', '방사상늑골두인대', 'S'),
    'Intra-articular ligament of head of rib': ('관절속갈비뼈머리인대', '관절내늑골두인대', 'S'),
    'Costotransverse ligament': ('갈비가로돌기인대', '늑횡돌기인대', 'S'),
    'External intercostal membrane': ('바깥갈비사이막', '외늑간막', 'S'),
    'Internal intercostal membrane': ('속갈비사이막', '내늑간막', 'S'),
    # ── Head / neck
    'Lateral temporomandibular ligament': ('가쪽관자아래턱인대', '외측측두하악인대', 'S'),
    'Sphenomandibular ligament': ('나비아래턱인대', '접형하악인대', 'S'),
    'Stylomandibular ligament': ('붓아래턱인대', '경돌하악인대', 'S'),
    'Stylohyoid ligament': ('붓목뿔인대', '경돌설골인대', 'S'),
    'Pterygospinous ligament': ('날개가시인대', '익극인대', 'S'),
    'Median cricothyroid ligament': ('정중반지방패인대', '정중윤상갑상인대', 'S'),
    'Median thyrohyoid ligament': ('정중방패목뿔인대', '정중갑상설골인대', 'S'),
    'Lateral thyrohyoid ligament': ('가쪽방패목뿔인대', '외측갑상설골인대', 'S'),
    'Cricopharyngeal ligament': ('반지인두인대', '윤상인두인대', 'S'),
    'Quadrangular membrane': ('네모막', '방형막', 'S'),
    'Thyroid cartilage': ('방패연골', '갑상연골', 'S'),
    'Cricoid cartilage': ('반지연골', '윤상연골', 'S'),
    'Arytenoid cartilage': ('모뿔연골', '피열연골', 'S'),
    'Corniculate cartilage': ('잔뿔연골', '소각연골', 'S'),
    'Nasal septal cartilage': ('코중격연골', '비중격연골', 'S'),
    'Lateral process of nasal septal cartilage': ('코중격연골 가쪽돌기', '비중격연골 외측돌기', 'C'),
    'Major alar cartilage': ('큰콧방울연골', '대비익연골', 'S'),
    'Superior tarsus': ('위눈꺼풀판', '상검판', 'S'),
    'Inferior tarsus': ('아래눈꺼풀판', '하검판', 'S'),
    'Trochlea of superior oblique muscle': ('위빗근도르래', '상사근활차', 'S'),
    'Common tendinous ring': ('온힘줄고리', '총건륜', 'S'),
    'Epicranial aponeurosis': ('머리덮개널힘줄', '모상건막', 'S'),
    # ── Joint capsules and discs
    'Articular capsule of acromioclavicular joint': ('봉우리빗장관절 관절주머니', '견쇄관절 관절낭', 'C'),
    'Articular capsule of elbow joint': ('팔꿉관절 관절주머니', '주관절 관절낭', 'C'),
    'Articular capsule of glenohumeral joint': ('어깨관절 관절주머니', '견관절 관절낭', 'C'),
    'Articular capsule of hip joint': ('엉덩관절 관절주머니', '고관절 관절낭', 'C'),
    'Articular capsule of knee joint': ('무릎관절 관절주머니', '슬관절 관절낭', 'C'),
    'Articular capsule of radiocarpal joint': ('노손목관절 관절주머니', '요골수근관절 관절낭', 'C'),
    'Articular capsule of sternoclavicular joint': ('복장빗장관절 관절주머니', '흉쇄관절 관절낭', 'C'),
    'Articular capsule of superior tibiofibular joint': ('정강종아리관절 관절주머니', '경비관절 관절낭', 'C'),
    'Articular capsule of temporomandibular joint': ('턱관절 관절주머니', '측두하악관절 관절낭', 'C'),
    'Articular capsule of interphalangeal joint of great toe': ('엄지발가락뼈사이관절 관절주머니', '무지지절간관절 관절낭', 'C'),
    'Articular capsules of distal interphalangeal joints': ('먼쪽손가락뼈사이관절 관절주머니', '원위수지절간관절 관절낭', 'C'),
    'Articular capsules of distal interphalangeal joints of foot': ('먼쪽발가락뼈사이관절 관절주머니', '원위족지절간관절 관절낭', 'C'),
    'Articular capsules of proximal interphalangeal joints': ('몸쪽손가락뼈사이관절 관절주머니', '근위수지절간관절 관절낭', 'C'),
    'Articular capsules of proximal interphalangeal joints of foot': ('몸쪽발가락뼈사이관절 관절주머니', '근위족지절간관절 관절낭', 'C'),
    'Articular capsules of metacarpophalangeal joints': ('손허리손가락관절 관절주머니', '중수지절관절 관절낭', 'C'),
    'Articular capsules of metatarsophalangeal joints': ('발허리발가락관절 관절주머니', '중족지절관절 관절낭', 'C'),
    'Articular disc of acromioclavicular joint': ('봉우리빗장관절원판', '견쇄관절원판', 'C'),
    'Articular disc of distal radio-ulnar joint': ('먼쪽노자관절원판', '원위요척관절원판', 'C'),
    'Articular disc of sternoclavicular joint': ('복장빗장관절원판', '흉쇄관절원판', 'C'),
    'Articular disc of temporomandibular joint': ('턱관절원판', '측두하악관절원판', 'C'),
    # ── Bursae (윤활주머니 / 점액낭)
    'Subacromial bursa': ('봉우리밑윤활주머니', '견봉하점액낭', 'S'),
    'Subdeltoid bursa': ('어깨세모근밑윤활주머니', '삼각근하점액낭', 'S'),
    'Subcutaneous acromial bursa': ('봉우리피부밑윤활주머니', '피하견봉점액낭', 'C'),
    'Coracobrachial bursa': ('부리위팔근윤활주머니', '오훼완근점액낭', 'C'),
    'Subtendinous bursa of infraspinatus muscle': ('가시아래근힘줄밑윤활주머니', '극하근건하점액낭', 'C'),
    'Subtendinous bursa of teres major muscle': ('큰원근힘줄밑윤활주머니', '대원근건하점액낭', 'C'),
    'Subtendinous bursa of trapezius muscle': ('등세모근힘줄밑윤활주머니', '승모근건하점액낭', 'C'),
    'Subtendinous bursa of triceps brachii muscle': ('위팔세갈래근힘줄밑윤활주머니', '상완삼두근건하점액낭', 'C'),
    'Bicipitoradial bursa': ('두갈래노윤활주머니', '이두요골점액낭', 'C'),
    'Suprapatellar bursa': ('무릎위윤활주머니', '슬개상점액낭', 'S'),
    'Subcutaneous prepatellar bursa': ('무릎앞피부밑윤활주머니', '피하슬개전점액낭', 'S'),
    'Subfacial prepatellar bursa': ('무릎앞근막밑윤활주머니', '근막하슬개전점액낭', 'C'),
    'Subtendinous prepatellar bursa': ('무릎앞힘줄밑윤활주머니', '건하슬개전점액낭', 'C'),
    'Subcutaneous infrapatellar bursa': ('무릎아래피부밑윤활주머니', '피하슬개하점액낭', 'S'),
    'Deep infrapatellar bursa': ('깊은무릎아래윤활주머니', '심슬개하점액낭', 'S'),
    'Subcutaneous bursa of tuberosity of tibia': ('정강뼈거친면피부밑윤활주머니', '경골조면피하점액낭', 'C'),
    'Anserine bursa': ('거위발윤활주머니', '아족점액낭', 'S'),
    'Semimembranosus bursa': ('반막모양근윤활주머니', '반막양근점액낭', 'S'),
    'Medial subtendinous bursa of gastrocnemius muscle': ('장딴지근안쪽힘줄밑윤활주머니', '비복근내측건하점액낭', 'C'),
    'Lateral subtendinous bursa of gastrocnemius muscle': ('장딴지근가쪽힘줄밑윤활주머니', '비복근외측건하점액낭', 'C'),
    'Superior bursa of biceps femoris muscle': ('넙다리두갈래근위윤활주머니', '대퇴이두근상점액낭', 'C'),
    'Inferior subtendinous bursa of biceps femoris muscle': ('넙다리두갈래근아래힘줄밑윤활주머니', '대퇴이두근하건하점액낭', 'C'),
    'Subtendinous bursa of sartorius muscle': ('넙다리빗근힘줄밑윤활주머니', '봉공근건하점액낭', 'C'),
    'Subtendinous bursa of tibialis anterior': ('앞정강근힘줄밑윤활주머니', '전경골근건하점액낭', 'C'),
    'Subcutaneous calcaneal bursa': ('발꿈치피부밑윤활주머니', '피하종골점액낭', 'S'),
    'Subtendinous calcaneal bursa': ('발꿈치힘줄밑윤활주머니', '종골건하점액낭', 'S'),
    'Subcutaneous bursa of lateral malleolus': ('가쪽복사피부밑윤활주머니', '외과피하점액낭', 'C'),
    'Subcutaneous bursa of medial malleolus': ('안쪽복사피부밑윤활주머니', '내과피하점액낭', 'C'),
    'Trochanteric bursa of gluteus maximus muscle': ('큰볼기근돌기윤활주머니', '대둔근전자점액낭', 'C'),
    'Trochanteric bursa of gluteus medius muscle': ('중간볼기근돌기윤활주머니', '중둔근전자점액낭', 'C'),
    'Trochanteric bursa of gluteus minimus muscle': ('작은볼기근돌기윤활주머니', '소둔근전자점액낭', 'C'),
    'Subcutaneous trochanteric bursa': ('돌기피부밑윤활주머니', '피하전자점액낭', 'C'),
    'Intermuscular gluteal bursae': ('볼기근사이윤활주머니', '둔근간점액낭', 'C'),
    'Sciatic bursa of gluteus maximus muscle': ('큰볼기근궁둥윤활주머니', '대둔근좌골점액낭', 'C'),
    'Sciatic bursa of obturator internus': ('속폐쇄근궁둥윤활주머니', '내폐쇄근좌골점액낭', 'C'),
    'Subtendinous bursa of obturator internus': ('속폐쇄근힘줄밑윤활주머니', '내폐쇄근건하점액낭', 'C'),
    'Bursa of piriformis muscle': ('궁둥구멍근윤활주머니', '이상근점액낭', 'C'),
    'Iliopectineal bursa': ('엉덩두덩윤활주머니', '장치점액낭', 'C'),
    'Subtendinous bursa of iliacus muscle': ('엉덩근힘줄밑윤활주머니', '장골근건하점액낭', 'C'),
    # ── Fascia, septa, retinacula, aponeuroses, raphe, tendons
    'Antebrachial fascia': ('아래팔근막', '전완근막', 'S'),
    'Brachial fascia': ('위팔근막', '상완근막', 'S'),
    'Crural fascia': ('종아리근막', '하퇴근막', 'S'),
    'Fascia lata': ('넙다리근막', '대퇴근막', 'S'),
    'Deltoid fascia': ('어깨세모근근막', '삼각근근막', 'S'),
    'Pectoral fascia': ('가슴근막', '흉근근막', 'S'),
    'Clavipectoral fascia': ('빗장가슴근막', '쇄흉근막', 'S'),
    'Diaphragmatic fascia': ('가로막근막', '횡격막근막', 'S'),
    'Dorsal fascia of hand': ('손등근막', '수배근막', 'S'),
    'Iliopsoas fascia': ('엉덩허리근근막', '장요근근막', 'S'),
    'Masseteric fascia': ('깨물근근막', '교근근막', 'S'),
    'Transversalis fascia': ('가로근막', '횡근막', 'S'),
    'Popliteal fascia': ('오금근막', '슬와근막', 'S'),
    'Piriformis fascia': ('궁둥구멍근근막', '이상근근막', 'C'),
    'Anterior layer of thoracolumbar fascia': ('등허리근막 앞층', '흉요근막 전엽', 'S'),
    'Middle layer of thoracolumbar fascia': ('등허리근막 중간층', '흉요근막 중엽', 'S'),
    'Posterior layer of thoracolumbar fascia': ('등허리근막 뒤층', '흉요근막 후엽', 'S'),
    'Superficial layer of temporal fascia': ('관자근막 얕은층', '측두근막 천엽', 'S'),
    'Superficial investing cervical fascia': ('목근막 얕은층', '경근막 천엽', 'S'),
    'Iliotibial tract': ('엉덩정강띠', '장경인대', 'S'),
    'Anterior intermuscular septum of leg': ('종아리앞근육사이막', '하퇴전근간중격', 'S'),
    'Posterior intermuscular septum of leg': ('종아리뒤근육사이막', '하퇴후근간중격', 'S'),
    'Transverse intermuscular septum of leg': ('종아리가로근육사이막', '하퇴횡근간중격', 'S'),
    'Lateral femoral intermuscular septum': ('가쪽넙다리근육사이막', '외측대퇴근간중격', 'S'),
    'Medial femoral intermuscular septum': ('안쪽넙다리근육사이막', '내측대퇴근간중격', 'S'),
    'Lateral intermuscular septum of arm': ('가쪽위팔근육사이막', '외측상완근간중격', 'S'),
    'Medial intermuscular septum of arm': ('안쪽위팔근육사이막', '내측상완근간중격', 'S'),
    'Extensor retinaculum of wrist': ('손목폄근지지띠', '수근신근지대', 'S'),
    'Flexor retinaculum of wrist': ('손목굽힘근지지띠', '수근굴근지대', 'S'),
    'Flexor retinaculum of ankle': ('발목굽힘근지지띠', '족근굴근지대', 'S'),
    'Superior extensor retinaculum of ankle': ('위폄근지지띠', '상신근지대', 'S'),
    'Inferior extensor retinaculum of ankle': ('아래폄근지지띠', '하신근지대', 'S'),
    'Superior fibular retinaculum': ('위종아리근지지띠', '상비골근지대', 'S'),
    'Inferior fibular retinaculum': ('아래종아리근지지띠', '하비골근지대', 'S'),
    'Palmar aponeurosis': ('손바닥널힘줄', '수장건막', 'S'),
    'Plantar aponeurosis': ('발바닥널힘줄', '족저건막', 'S'),
    'Linea alba': ('백색선', '백선', 'S'),
    'Calcaneal tendon': ('발꿈치힘줄', '종골건', 'S'),
    'Intermediate tendon of digastric muscle': ('두힘살근중간힘줄', '이복근중간건', 'S'),
    'Tendinous arch of levator ani': ('항문올림근힘줄활', '항문거근건궁', 'S'),
    'Tendon of extensor digitorum longus': ('긴발가락폄근힘줄', '장지신근건', 'C'),
    # ── Tendon sheaths (힘줄집 / 건초)
    'Common flexor tendon sheath': ('온굽힘근힘줄집', '총굴근건초', 'S'),
    'Common tendon sheath of fibularis muscles': ('종아리근온힘줄집', '비골근총건초', 'S'),
    'Plantar tendon sheath of fibularis longus muscle': ('긴종아리근발바닥힘줄집', '장비골근족저건초', 'C'),
    'Intertubercular tendon sheath': ('결절사이힘줄집', '결절간건초', 'S'),
    'Synovial sheaths of digits of hand': ('손가락윤활집', '수지활액초', 'S'),
    'Cruciform part of fibrous sheath of digit of hand': ('손가락섬유집 십자부분', '수지섬유초 십자부', 'C'),
    'Tendon sheath - abd. pollicis longus - ext. pollicis brevis': ('긴엄지벌림근·짧은엄지폄근 힘줄집', '장무지외전근·단무지신근 건초', 'C'),
    'Tendon sheath of extensor carpi ulnaris': ('자쪽손목폄근힘줄집', '척측수근신근건초', 'C'),
    'Tendon sheath of extensor digiti minimi manus': ('새끼폄근힘줄집', '소지신근건초', 'C'),
    'Tendon sheath of extensor digitorum and extensor indicis': ('손가락폄근·집게폄근 힘줄집', '지신근·시지신근 건초', 'C'),
    'Tendon sheath of extensor digitorum longus': ('긴발가락폄근힘줄집', '장지신근건초', 'C'),
    'Tendon sheath of extensor hallucis longus': ('긴엄지폄근힘줄집', '장무지신근건초', 'C'),
    'Tendon sheath of extensor pollicis longus': ('긴엄지폄근힘줄집', '장무지신근건초', 'C'),
    'Tendon sheath of extensors carpi radialis': ('노쪽손목폄근힘줄집', '요측수근신근건초', 'C'),
    'Tendon sheath of flexor carpi radialis': ('노쪽손목굽힘근힘줄집', '요측수근굴근건초', 'C'),
    'Tendon sheath of flexor digitorum longus': ('긴발가락굽힘근힘줄집', '장지굴근건초', 'C'),
    'Tendon sheath of flexor hallucis longus': ('긴엄지굽힘근힘줄집', '장무지굴근건초', 'C'),
    'Tendon sheath of flexor pollicis longus': ('긴엄지굽힘근힘줄집', '장무지굴근건초', 'C'),
    'Tendon sheath of tibialis anterior': ('앞정강근힘줄집', '전경골근건초', 'C'),
    'Tendon sheath of tibialis posterior muscle': ('뒤정강근힘줄집', '후경골근건초', 'C'),
    # ── Nerves not in the pre-v2 nerve overlay
    'Olfactory nerve (I)': ('후각신경 (I)', '후신경 (I)', 'S'),
    'Optic nerve (II)': ('시각신경 (II)', '시신경 (II)', 'S'),
    'Oculomotor nerve (III)': ('눈돌림신경 (III)', '동안신경 (III)', 'S'),
    'Trochlear nerve (IV)': ('도르래신경 (IV)', '활차신경 (IV)', 'S'),
    'Trigeminal nerve (V)': ('삼차신경 (V)', '삼차신경 (V)', 'S'),
    'Abducens nerve (VI)': ('갓돌림신경 (VI)', '외전신경 (VI)', 'S'),
    'Facial nerve (VII)': ('얼굴신경 (VII)', '안면신경 (VII)', 'S'),
    'Vestibulocochlear nerve (VIII)': ('속귀신경 (VIII)', '내이신경 (VIII)', 'S'),
    'Glossopharyngeal nerve (IX)': ('혀인두신경 (IX)', '설인신경 (IX)', 'S'),
    'Vagus nerve (X)': ('미주신경 (X)', '미주신경 (X)', 'S'),
    'Accessory nerve (XI)': ('더부신경 (XI)', '부신경 (XI)', 'S'),
    'Hypoglossal nerve (XII)': ('혀밑신경 (XII)', '설하신경 (XII)', 'S'),
    'Ophthalmic nerve': ('눈신경', '안신경', 'S'),
    'Maxillary nerve': ('위턱신경', '상악신경', 'S'),
    'Anterior division of mandibular nerve': ('아래턱신경 앞갈래', '하악신경 전지', 'C'),
    'Posterior division of mandibular nerve': ('아래턱신경 뒤갈래', '하악신경 후지', 'C'),
    'Meningeal branch of maxillary nerve': ('위턱신경 수막가지', '상악신경 경막지', 'C'),
    'Motor root of trigeminal nerve': ('삼차신경 운동뿌리', '삼차신경 운동근', 'S'),
    'Sensory root of trigeminal nerve': ('삼차신경 감각뿌리', '삼차신경 감각근', 'S'),
    'Buccal nerve': ('볼신경', '협신경', 'S'),
    'Lingual nerve': ('혀신경', '설신경', 'S'),
    'Inferior alveolar nerve': ('아래이틀신경', '하치조신경', 'S'),
    'Mental nerve': ('턱끝신경', '이신경', 'S'),
    'Nerve to mylohyoid muscle': ('턱목뿔근신경', '악설골근신경', 'S'),
    'Chorda tympani': ('고실끈신경', '고삭신경', 'S'),
    'Cochlear nerve': ('달팽이신경', '와우신경', 'S'),
    'Vestibular nerve': ('안뜰신경', '전정신경', 'S'),
    'Nucleus of hypoglossal nerve': ('혀밑신경핵', '설하신경핵', 'S'),
    'Nucleus of trochlear nerve': ('도르래신경핵', '활차신경핵', 'S'),
    'Posterior nucleus of vagus nerve': ('미주신경뒤핵', '미주신경배측핵', 'S'),
    'Axillary nerve': ('겨드랑신경', '액와신경', 'S'),
    'Musculocutaneous nerve': ('근육피부신경', '근피신경', 'S'),
    'Median nerve': ('정중신경', '정중신경', 'S'),
    'Ulnar nerve': ('자신경', '척골신경', 'S'),
    'Radial nerve': ('노신경', '요골신경', 'S'),
    'Deep branch of radial nerve': ('노신경 깊은가지', '요골신경 심지', 'S'),
    'Superficial branch of radial nerve': ('노신경 얕은가지', '요골신경 천지', 'S'),
    'Dorsal scapular nerve': ('등쪽어깨신경', '견갑배신경', 'S'),
    'Long thoracic nerve': ('긴가슴신경', '장흉신경', 'S'),
    'Suprascapular nerve': ('어깨위신경', '견갑상신경', 'S'),
    'Femoral nerve': ('넙다리신경', '대퇴신경', 'S'),
    'Obturator nerve': ('폐쇄신경', '폐쇄신경', 'S'),
    'Lateral femoral cutaneous nerve': ('가쪽넙다리피부신경', '외측대퇴피신경', 'S'),
    'Posterior femoral cutaneous nerve': ('뒤넙다리피부신경', '후대퇴피신경', 'S'),
    'Saphenous nerve': ('두렁신경', '복재신경', 'S'),
    'Sciatic nerve': ('궁둥신경', '좌골신경', 'S'),
    'Tibial nerve': ('정강신경', '경골신경', 'S'),
    'Common fibular nerve': ('온종아리신경', '총비골신경', 'S'),
    'Deep fibular nerve': ('깊은종아리신경', '심비골신경', 'S'),
    'Superficial fibular nerve': ('얕은종아리신경', '천비골신경', 'S'),
    'Sural nerve': ('장딴지신경', '비복신경', 'S'),
    'Medial plantar nerve': ('안쪽발바닥신경', '내측족저신경', 'S'),
    'Lateral plantar nerve': ('가쪽발바닥신경', '외측족저신경', 'S'),
    'Cauda equina': ('말총', '마미', 'S'),
    'Spinal ganglion': ('척수신경절', '척수신경절', 'S'),
    'Ganglia of sympathetic trunk': ('교감신경줄기신경절', '교감신경간신경절', 'S'),
}
# Deliberately unnamed until a source is found (kept in English, listed as exceptions):
# Iliopectineal arch, Investing abdominal fascia, Intercornual ligament, Triradiate cartilage, Frenula capsulae.

ORDINAL = {'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5, 'sixth': 6, 'seventh': 7, 'eighth': 8, 'ninth': 9, 'tenth': 10}
TOOTH = {'medial incisor': ('안쪽앞니', '중절치'), 'lateral incisor': ('가쪽앞니', '측절치'), 'canine': ('송곳니', '견치'),
         'first premolar': ('첫째작은어금니', '제1소구치'), 'second premolar': ('둘째작은어금니', '제2소구치'),
         'first molar tooth': ('첫째큰어금니', '제1대구치'), 'second molar tooth': ('둘째큰어금니', '제2대구치')}


def series(name):
    """Pattern-named series: vertebral discs and nuclei by level, costal cartilages, teeth."""
    m = re.fullmatch(r'Intervertebral disc ([CTLS]\d+-[CTLS]\d+)', name)
    if m: return (f'척추사이원판 {m[1]}', f'추간원판 {m[1]}', 'R')
    m = re.fullmatch(r'Nucleus pulposus ([CTLS]\d+-[CTLS]\d+)', name)
    if m: return (f'속질핵 {m[1]}', f'수핵 {m[1]}', 'R')
    m = re.fullmatch(r'Costal cartilage of (\w+) rib', name)
    if m and m[1] in ORDINAL: n = ORDINAL[m[1]]; return (f'제{n}갈비연골', f'제{n}늑연골', 'R')
    m = re.fullmatch(r'(Upper|Lower) (.+)', name)
    if m and m[2] in TOOTH:
        jaw = ('위턱', '상악') if m[1] == 'Upper' else ('아래턱', '하악')
        return (f'{jaw[0]} {TOOTH[m[2]][0]}', f'{jaw[1]} {TOOTH[m[2]][1]}', 'R')
    return None


# KMLE values rejected after review (kept: the drafted pair). Each is an evident source-data error.
SOURCE_REJECTED = {
    'External intercostal membrane': '한자어 "뇌측간막" is a typo of 외늑간막',
    'Corniculate cartilage': '한자어 "설상연골" names the cuneiform cartilage, not the corniculate',
    'Subtendinous prepatellar bursa': 'row repeats the subcutaneous (피부밑/피하) prepatellar bursa',
    'Tendon sheath of flexor digitorum longus': '우리말 "힘줄밑주머니" names a bursa, not a tendon sheath',
    'Tendon sheath of tibialis anterior': '우리말 "힘줄주머니" breaks the 힘줄집 pattern used for every other tendon sheath',
    'Iliopectineal bursa': 'row is parenthesised and names an iliopsoas/gluteal bursa (엉덩허리근볼기주머니)',
}


def clean_kaa(value):
    """Drop KMLE glosses: '심횡중수(장골)인대' -> '심횡중수인대'; '발꿈치힘줄 [아킬레스힘줄]' -> main + alias."""
    if not value: return value, []
    aliases = [a.strip() for a in re.findall(r'\[([^\]]+)\]', value)]
    value = re.sub(r'\s*\[[^\]]+\]', '', value)
    if value.startswith('(') and value.endswith(')'): value = value[1:-1]
    value = re.sub(r'\([^)]*\)', '', value).strip()
    return value, aliases


def kaa_convention(en, modern, traditional):
    """Bring a draft that KMLE does not list in line with the KAA forms seen in the verified entries."""
    n = en.lower()
    if 'bursa' in n:
        modern, traditional = modern.replace('윤활주머니', '주머니'), traditional.replace('점액낭', '낭')
    if 'ligament' in n:
        modern = modern.replace('손바닥쪽', '바닥쪽').replace('발바닥쪽', '바닥쪽')
        if n.startswith('plantar'): modern = re.sub(r'^발바닥', '바닥쪽', modern)
        traditional = traditional.replace('족저', '척측')
    return modern, traditional


def lookup(name):
    """(koModern, koTraditional, basis) or None. Parenthesised ZA names are looked up without the brackets."""
    bare = name[1:-1] if name.startswith('(') and name.endswith(')') else name
    return NAMES.get(bare) or series(bare)


def main():
    nerve = json.loads((ROOT / 'atlas-data/terminology/learner-nerve-display-names.json').read_text())
    structures = json.loads((ROOT / 'atlas-data/runtime/structures.json').read_text())['structures']
    # Names this table already supplies stay in scope after build_runtime_v2.py has filled them in.
    previous = set(json.loads(OUT.read_text())['entries']) | set(json.loads(OUT.read_text())['unnamed']) if OUT.exists() else set()
    needed = sorted({s['names']['en'] for s in structures if s['learner']['visible'] and (not s['names']['koModern'] or s['names']['en'] in previous)})
    # KAA dictionary entries found on KMLE (verify_names_kmle.py) override the draft.
    kmle_path = ROOT / 'atlas-data/terminology/structure-names-kmle.json'
    kmle = json.loads(kmle_path.read_text())['terms'] if kmle_path.exists() else {}
    entries, missing = {}, []
    for en in needed:
        bare = en[1:-1] if en.startswith('(') and en.endswith(')') else en
        kaa = kmle.get(bare, {})
        draft = lookup(en)
        if en in nerve and nerve[en].get('koModern'):
            entries[en] = {'koModern': nerve[en]['koModern'], 'koTraditional': nerve[en].get('koTraditional'), 'basis': 'nerve_overlay'}
        elif kaa.get('status') == 'kaa_found' and bare not in SOURCE_REJECTED:
            modern, alt_m = clean_kaa(kaa['koModern'])
            traditional, alt_t = clean_kaa(kaa['koTraditional'])
            numeral = re.search(r' \([IVX]+\)$', bare)  # KAA omits cranial-nerve numerals; keep them for learners
            if numeral and not modern.endswith(numeral[0]): modern += numeral[0]; traditional = (traditional or '') + numeral[0]
            aliases = [a for a in alt_m + alt_t + ([draft[0], draft[1]] if draft else []) if a and a not in (modern, traditional)]
            entries[en] = {'koModern': modern, 'koTraditional': traditional or (draft[1] if draft else modern),
                           'basis': 'kaa_dictionary', 'source': kaa['url'], 'aliases': sorted(set(aliases))}
        elif draft:
            modern, traditional = kaa_convention(bare, draft[0], draft[1])
            entries[en] = {'koModern': modern, 'koTraditional': traditional, 'basis': draft[2],
                           **({'kmleRejected': SOURCE_REJECTED[bare], 'source': kaa.get('url')} if bare in SOURCE_REJECTED else {})}
        else:
            missing.append(en)
    counts = {}
    for e in entries.values(): counts[e['basis']] = counts.get(e['basis'], 0) + 1
    OUT.write_text(json.dumps({'schemaVersion': 1, 'scope': 'visible v2 structures without a Korean name before C1',
                               'basisLegend': {'kaa_dictionary': '대한해부학회 dictionary entry found on KMLE (source URL kept)',
                                               'S': 'drafted as an established KAA term; not found on KMLE', 'C': 'composed from KAA component terms; not found on KMLE',
                                               'R': 'series rule', 'nerve_overlay': 'pre-v2 learner nerve display names'},
                               'counts': counts, 'unnamed': missing, 'entries': entries}, ensure_ascii=False, indent=1) + '\n')
    print(json.dumps({'needed': len(needed), 'named': len(entries), 'counts': counts, 'unnamed': missing}, ensure_ascii=False))


if __name__ == '__main__':
    main()
