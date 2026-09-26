# T11-B06 필드 출처와 웹 접근 로그

조회일: 2026-09-25. ID별 상세 provenance는 `atlas-data/terminology/term-review-batches.json`에 필드별로 연결한다. 검색 결과, 실제 열린 웹페이지/PDF, 사람 해부학 검토를 구분한다.

## TA2 Part 2 — 공식 PDF 텍스트 계층

- URL: <https://cdn.dal.ca/content/dam/dalhousie/pdf/library/FIPAT/TA2/FIPAT-TA2-Part-2.pdf> (Dalhousie 공식 호스팅).
- 판본 표기: PDF 앞부분에 *Terminologia Anatomica*, Second Edition (2.07); 서지 인용은 2nd ed., 2019; IFAA General Assembly approved/adopted, 2020이라고 표시되어 있다.
- Chapter 4 표 제목은 PDF 텍스트 페이지 P52, 인쇄면 73이며 열 제목은 `Latin term`, `Latin synonym`, `UK English`, `US English`, `English synonym`, `Other`다. PDF 텍스트 행을 직접 열어 다음 B06 행의 실제 문자열과 열을 확인했다.

| 기존 ID | 인쇄면 / PDF 텍스트 페이지 | TA2 row | Latin term | UK/US English | `Other` 확인 |
|---|---:|---:|---|---|---|
| HA-M-000032 | p.89 / P68 | 2458 | Musculus infraspinatus | Infraspinatus muscle | `Muculus infra spinam` (텍스트 계층 표기 그대로; alias로 채택하지 않음) |
| HA-M-000033 | p.89 / P68 | 2459 | Musculus teres minor | Teres minor muscle | 추가 문자열 없음 |
| HA-M-000034 | p.89 / P68 | 2460 | Musculus subscapularis | Subscapularis muscle | 추가 문자열 없음 |
| HA-M-000035 | p.89 / P68 | 2464 | Musculus biceps brachii | Biceps brachii muscle | 추가 문자열 없음 |
| HA-M-000036 | p.89 / P68 | 2468 | Musculus coracobrachialis | Coracobrachialis muscle | `Casserio's muscle` (같은 ID의 검색 alias로 보존) |
| HA-M-000037 | p.89 / P68 | 2469 | Musculus brachialis | Brachialis muscle | 추가 문자열 없음 |
| HA-M-000038 | p.89 / P68 | 2471 | Musculus triceps brachii | Triceps brachii muscle | 추가 문자열 없음 |
| HA-M-000039 | p.94 / P73 | 2598 | Musculus gluteus maximus | Gluteus maximus muscle | `Musculus glutaeus maximus` (같은 ID의 라틴 동의형으로 보존) |
| HA-M-000040 | p.94 / P73 | 2599 | Musculus gluteus medius | Gluteus medius muscle | `Musculus glutaeus medius` (같은 ID의 라틴 동의형으로 보존) |
| HA-M-000041 | p.94 / P73 | 2600 | Musculus gluteus minimus | Gluteus minimus muscle | `Musculus glutaeus minimus` (같은 ID의 라틴 동의형으로 보존) |

영어 필드는 표의 UK/US English 두 열에 같은 문자열로 나온 항목을 사용했다. Latin alias[0]는 `Latin term`이다. `Other`의 근거 행은 별도 alias 필드 evidence에 기록했다. 앞부분/행/열 제목의 직접 확인은 텍스트 계층 기준이며, PDF 페이지 이미지 및 시각 표 레이아웃은 검사하지 않았다. 이 확인은 표 문자열만 지지하며 개념 동일성, 구조, 기능 또는 부착의 사람 검토가 아니다.

## KMLE — 한국어와 한자

KMLE는 여러 사전의 검색·표시 통합 페이지다. 특정 용어집의 판본/개정일이 페이지에 나오지 않는 경우 각 evidence에 `KMLE web aggregation; exact underlying dictionary edition/revision is not exposed`로 기록했다. HTML을 연 경우도 그 페이지가 인용/집계하는 원 사전 전체를 직접 열었다는 뜻은 아니다.

| ID | KMLE 조회 URL | 검색결과 / 직접 열린 페이지에서 확인한 용어 locator |
|---|---|---|
| HA-M-000032 | <https://m.kmle.co.kr/search.php?Search=musculus+infraspinatus> | 검색 결과. 대한해부학회 `Infraspinatus m.` → 가시아래근, 옛 용어 극하근; 옛 대한의협 3의 정확한 `infraspinatus` 행에 극하근(棘下筋)이 표시됨. 같은 검색결과의 별도 `musculus infraspinatus` 행에는 極下筋 변형도 보이며 충돌 후보로 보존했다. 직접 HTML 열기는 cache miss. |
| HA-M-000033 | <https://m.kmle.co.kr/search.php?Search=teres+minor+muscle> / <https://m.kmle.co.kr/search.php?Search=teres+minor+m> | 검색 결과. 대한해부학회 `Teres minor m.` → 작은원근, 옛 용어 소원근; 별도 대한신경외과학회 `teres minor m.` 행에 소원근(小圓筋). 다른 legacy 결과의 小園筋 및 小圓形筋은 미채택 충돌 후보. 직접 HTML 열기는 URL 접근/문자 디코딩 문제. |
| HA-M-000034 | <https://m.kmle.co.kr/search.php?Search=musculus+subscapularis> | 검색 결과. `subscapularis muscle` → 어깨밑근, 견갑하근; `musculus subscapularis` legacy 행에 견갑하근(肩甲下筋). CancerWEB 검색결과는 `subscapular muscle`을 synonym으로 표기한다. 직접 HTML 열기는 Unicode decoding error. |
| HA-M-000035 | <https://m.kmle.co.kr/search.php?Search=biceps+brachii+muscle> | 검색 결과. 대한해부학회 `Biceps brachii m.` → 위팔두갈래근, 옛 용어 상완이두근; 옛 대한의협 3 legacy 행에 상완이두근(上腕二頭筋). 직접 HTML 원문은 열지 못했다. |
| HA-M-000036 | <https://m.kmle.co.kr/search.php?Search=coracobrachialis> | 직접 열린 KMLE HTML, lines 18–20의 대한의협, 67–70의 대한해부학회에서 부리위팔근 / 옛 용어 오훼완근 확인. CancerWEB lines 84–88의 synonym `Casser's perforated muscle`, `coracobrachial muscle`을 확인했다. KMLE에서 해당 항목의 완전한 한자명은 확인하지 못함. |
| HA-M-000037 | <https://m.kmle.co.kr/search.php?Search=brachialis> | 직접 열린 KMLE HTML, lines 14–16 및 108–111에서 위팔근 / 옛 용어 상완근; 대한신경외과학회 lines 121–125의 한자 上腕筋; CancerWEB lines 151–153의 `brachial muscle` synonym 확인. |
| HA-M-000038 | <https://m.kmle.co.kr/search.php?Search=triceps+brachii> | 검색결과 발췌. 대한해부학회 `Triceps brachii m.` → 위팔세갈래근, 옛 용어 상완삼두근; 옛 대한의협 3 행에 上腕三頭筋. CancerWEB synonym `triceps muscle of arm`도 결과에 표시. 직접 HTML 열기는 실패. |
| HA-M-000039–000041 | <https://m.kmle.co.kr/search.php?Search=gluteus> | 직접 열린 KMLE HTML. 옛 대한의협 3 근육 항목 lines 124–145에서 대둔근(大臀筋), 중둔근(中臀筋), 소둔근(小臀筋); 대한해부학회 lines 170–183에서 큰/중간/작은볼기근 및 옛 용어 확인. CancerWEB lines 261–283의 명칭/synonym 결과도 확인. |

### 충돌, 미채택 및 결측

- HA-M-000032: `棘下筋`은 legacy `infraspinatus` 항목에 직접 연결된 검색 결과라 실제 source Hanja로 기록했다. 같은 결과의 다른 행 `極下筋`은 변형 후보로 기록하고 학습 alias에는 넣지 않았다. TA2 `Other`의 텍스트 계층 표기 `Muculus infra spinam`도 다른 원자료의 대조가 없어 alias로 채택하지 않았다.
- HA-M-000033: 작은원근/소원근에 대해 KMLE에 `小圓筋`, `小園筋`, `小圓形筋`이 서로 다른 legacy 항목/사전으로 나타난다. `小圓筋`은 정확한 `teres minor m.`을 표기한 대한신경외과학회 결과에서 확인되어 기록하고, 다른 두 형식은 같은 ID에 검색어로 억지 병합하지 않고 미채택으로 보존했다.
- HA-M-000036: KMLE의 정확한 coracobrachialis 항목/열린 HTML은 완전한 한자 값을 제공하지 않았다. 검색 결과에서 인용되는 2차 위키 페이지에 `烏喙腕筋` 및 `烏口腕筋` 후보가 보였으나 해당 표기의 원 판본/locator를 확인하지 못해 `hanja=null`로 둔다.
- 사람 해부학 검토는 수행하지 않았다. 표준명, 한국어 용어, 검색 alias의 학습 사용 승인은 모두 미완이다.
