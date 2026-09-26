# T11-B05 필드 출처와 접근 로그

조회일: 2026-09-25. 각 provenance 행은 `atlas-data/terminology/term-review-batches.json`에 field별로 연결했다. 문자열 확인과 사람 해부학 검토를 혼동하지 않는다.

## FIPAT TA2 — 공식 PDF 원문 텍스트

- 판본: *Terminologia Anatomica*, second edition (TA2), Part 2, online edition published 2019.
- 사용 URL: <https://cdn.dal.ca/content/dam/dalhousie/pdf/library/FIPAT/TA2/FIPAT-TA2-Part-2.pdf> — Dalhousie 공식 호스팅 PDF. 원문 PDF를 직접 열었고 PDF 파서가 104쪽을 읽었다.
- 표 머리글: Chapter 4, PDF 텍스트 페이지 P52에 `Latin term`, `Latin synonym`, `UK English`, `US English`, `English synonym`, `Other`가 명시되어 있다.
- 원래 FIPAT library URL <https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf>는 직접 open 시 HTTP 502였다. 검색 색인 결과를 단독 원문으로 취급하지 않고 접근 가능한 공식 Dalhousie-hosted TA2 PDF의 텍스트 행으로 대조했다.
- 텍스트 행을 직접 읽어 열 머리글/열 역할을 확인했다. 페이지 PNG 캡처나 시각 레이아웃 검토는 하지 않았다. 따라서 `cellRoleStatus`는 열 역할은 원문 텍스트 머리글로 확인, 시각 레이아웃은 미검토로 구분한다.

| 기존 ID | Part 2 인쇄면 / PDF 텍스트 페이지 | Latin alias로 저장한 값 | English로 저장한 값 | 관찰 열 |
|---|---|---|---|---|
| HA-M-000022 | p.81 row 2233 / P60 | Musculus rhomboideus minor | Rhomboid minor muscle | Latin term; UK/US English |
| HA-M-000023 | p.81 row 2234 / P60 | Musculus levator scapulae | Levator scapulae muscle | Latin synonym; English synonym. 표의 Latin term은 `Levator scapulae` |
| HA-M-000024 | p.83 row 2301 / P62 | Musculus pectoralis major | Pectoralis major muscle | Latin term; UK/US English |
| HA-M-000025 | p.83 row 2305 / P62 | Musculus pectoralis minor | Pectoralis minor muscle | Latin term; UK/US English |
| HA-M-000026 | p.83 row 2306 / P62 | Musculus subclavius | Subclavius muscle | Latin term; UK/US English |
| HA-M-000027 | p.83 row 2307 / P62 | Musculus serratus anterior | Serratus anterior muscle | Latin term; UK/US English |
| HA-M-000028 | p.86 row 2373 / P65 | Musculus obliquus internus abdominis | Internal abdominal oblique muscle | Latin term; UK/US English |
| HA-M-000029 | p.86 row 2375 / P65 | Musculus transversus abdominis | Transversus abdominis muscle | Latin term; UK/US English |
| HA-M-000030 | p.89 row 2452 / P68 | Musculus deltoideus | Deltoid muscle | Latin term; UK/US English |
| HA-M-000031 | p.89 row 2457 / P68 | Musculus supraspinatus | Supraspinatus muscle | Latin term; UK/US English |

직접 열린 원문은 PDF 내 텍스트의 TA2 번호/영문/라틴어 문자열을 지지한다. 원문 시각 레이아웃을 보거나 배정 개념의 해부학적 동일성/기능/부착을 검토한 것으로 기록하지 않는다.

## KMLE 한글 및 한자 출처

KMLE의 각 field source record에는 사용 URL, result locator, 2026-09-25 조회일, 웹 결과 발췌 또는 열린 HTML 접근방식이 있다. 판본이 안 보인 경우 `exact underlying dictionary edition/revision is not exposed`로 기록했다.

| ID | 표시 label / 우리말 / 한자 | 사용 URL 및 정확한 locator |
|---|---|---|
| HA-M-000022 | 소능형근 / 작은마름근 / 小菱形筋 | [KMLE rhomboid minor](https://m.kmle.co.kr/search.php?Search=rhomboid+minor), `rhomboid minor muscle` 및 대한해부학회 Rhomboid minor m. 항목. 한자와 관용어 쌍은 [KMLE rhomboideus](https://m.kmle.co.kr/search.php?Search=rhomboideus), old 대한의협 3 `musculus rhomboideus minor` 항목. 검색결과만 확인, 직접 페이지 열기는 cache miss. |
| HA-M-000023 | 견갑거근 / 어깨올림근 / 肩甲擧筋 | [KMLE scapulae query](https://m.kmle.co.kr/search.php?FuzzyTrack=scapula&IsFuzzy=YES&Search=scapulae), `levator scapulae m.`, `musculus levator scapulae`, 대한해부학회 Levator scapulae m. 결과. 검색결과만 확인, 직접 페이지 열기는 cache miss. |
| HA-M-000024–000025 | 대흉근 / 큰가슴근 / 大胸筋; 소흉근 / 작은가슴근 / 小胸筋 | [KMLE pectoralis](https://www.kmle.co.kr/search.php?Search=pectoralis), 대한해부학회 major/minor 항목과 old 대한의협 3 `musculus pectoralis major/minor` 한자 포함 행. 검색결과만 확인, 직접 페이지 열기는 Unicode decoding error. |
| HA-M-000026 | 쇄골하근 / 빗장밑근 / 鎖骨下筋 | [KMLE subclavius muscle](https://www.kmle.co.kr/search.php?Search=subclavius+muscle), current subclavius muscle Korean result and old `쇄골아래근, 쇄골하근(鎖骨下筋)` row. 검색결과만 확인, 직접 페이지 열기는 cache miss. |
| HA-M-000027 | 전거근 / 앞톱니근 / 前鋸筋 | [KMLE serratus](https://www.kmle.co.kr/search.php?Search=serratus), `musculus serratus anterior` old 대한의협 3 and 대한해부학회 rows. Same results show another form `前方鋸筋`; it is not adopted because it is a distinct displayed string and its equivalence was not independently reviewed. Search result only; direct page open had Unicode decoding error. |
| HA-M-000028 | 내복사근 / 배속빗근 / 內腹斜筋 | [KMLE obliquus internus abdominis](https://m.kmle.co.kr/search.php?Search=obliquus+internus+abdominis), 대한해부학회 current `배속빗근` / old `내복사근`; [KMLE internal oblique muscle of abdomen](https://m.kmle.co.kr/search.php?Search=internal+oblique+muscle+of+abdomen), old 대한의협 3 exact `내복사근(內腹斜筋)` row. Search results only; exact underlying revisions unexposed. |
| HA-M-000029 | 복횡근 / 배가로근 / 腹橫筋 | [KMLE transversus abdominis](https://m.kmle.co.kr/search.php?Search=transversus+abdominis), 대한해부학회 current/old pair and old 대한의협 3 `musculus transversus abdominis` exact Hanja row. Search result only. |
| HA-M-000030 | 삼각근 / 어깨세모근 / 三角筋; retained English alias `Deltoid` | [KMLE deltoid](https://m.kmle.co.kr/search.php?Search=deltoid), actual HTML opened. 대한의협 `deltoid muscle` → 어깨세모근, 삼각근 (lines 30–32); old 대한의협 3 삼각근(三角筋) (101–103); CancerWEB `deltoid` entry and synonym (232–234; dated 05 Mar 2000). The prior `Deltoid` overlay value is retained as alias. |
| HA-M-000031 | 극상근 / 가시위근 / 棘上筋 | [KMLE musculus supraspinatus](https://m.kmle.co.kr/search.php?Search=musculus+supraspinatus), result `supraspinatus muscle` and old 대한의협 3 exact `가시윗근, 극상근(棘上筋)` row; 대한해부학회 current `가시위근`. Search results only; direct page open had Unicode decoding error. |

KMLE에서 `소능형근`과 Hanja `小菱形筋`을 직접 묶은 검색결과의 다른 old transcription `소릉형근`은 Hanja/발음 대응으로 혼합하지 않았다. `鎖骨下筋`은 검색 인덱스에 뒤쪽 공백이 붙어 보이는 곳이 있어 구조 값에는 문자만 기록했다. 모든 한자값은 검색결과 안에 완전한 문자열로 나타난다.

## 검토 상태

- `search-index excerpt`: 대부분의 KMLE 이름/한자 값.
- `opened source`: TA2 PDF 직접 text-layer open; KMLE deltoid HTML open.
- `visual page rendering`: 수행하지 않음.
- `human anatomy review`: 수행하지 않음 (`humanReviewed=false`, `not_performed`).
- 한국어 용어집의 판본/개정 이력을 모든 이름에 대해 확정하지 못했다. M30 기존 English 값은 정확한 HTML source를 통해 기존 `Deltoid` alias로 보존했으며, TA2 exact English 값은 `Deltoid muscle`로 기록했다.
