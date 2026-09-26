# T11-B04 필드별 웹 출처 기록

조회일: 2026-09-25. 문자열 출처 확인과 해부학적 동일성 검토는 분리한다. 모든 KMLE 값은 용어 문자열만 뒷받침하며 기시·정지/기능 claim은 가져오지 않았다. 사람이 해부학 검토자는 없었다.

## FIPAT TA2 영어·라틴어 관찰

- URL: [FIPAT TA2 Part 2 공식 호스팅 PDF](https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf)
- 판본: *Terminologia Anatomica*, 2nd edition, Part 2; online edition published 2019; PDF 경로는 2020-09.
- 접근: 공식 PDF 검색 색인 텍스트를 확인했다. 2026-09-25 웹 open은 HTTP 502로 실패했다. 로컬 파일·페이지 이미지·열 역할/열 머리글·정오표는 확인하지 못했다. 따라서 아래 English/Latin은 정확한 TA2 행의 검색 색인 관찰값이며 표준 열 역할은 미확인이다.
- 각 필드는 `term-review-batches.json`에 개별 row/page/value locator, URL, edition, `2026-09-25`, `official_hosted_PDF_search_index_text_only` 접근방식으로 연결돼 있다.

| 기존 ID | TA2 위치 | Latin observation | English observation |
|---|---|---|---|
| HA-M-000011 | Part 2 p.74 row 2048 | Musculus obliquus superior bulbi oculi | Superior oblique muscle |
| HA-M-000012 | p.77 row 2105 | Masseter | Masseter muscle |
| HA-M-000013 | p.77 row 2108 | Musculus temporalis | Temporalis muscle |
| HA-M-000014 | p.77 row 2109 | Musculus pterygoideus lateralis | Lateral pterygoid muscle |
| HA-M-000015 | p.77 row 2113 | Musculus pterygoideus medialis | Medial pterygoid muscle |
| HA-M-000016 | p.77 row 2117 | Musculus genioglossus | Genioglossus muscle |
| HA-M-000017 | p.77 row 2118 | Musculus hyoglossus | Hyoglossus muscle |
| HA-M-000018 | p.77 row 2121 | Musculus styloglossus | Styloglossus muscle |
| HA-M-000020 | p.81 row 2231 | Musculus latissimus dorsi | Latissimus dorsi muscle |
| HA-M-000021 | p.81 row 2232 | Musculus rhomboideus major | Rhomboid major muscle |

검색 결과가 직접 보여 준 범위: [TA2 Part 2 p.74 검색 색인](https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf), [TA2 Part 2 p.77 rows 2105–2121 검색 색인](https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf), [TA2 Part 2 p.81 rows 2231–2232 검색 색인](https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf).

## 한국어·한자 필드 출처와 접근

KMLE 웹 검색의 대다수는 하위 사전의 판본·발행연도·개정 정보를 노출하지 않았다. `검색 색인 발췌`와 `열린 HTML`을 소스별로 구분했다. 링크의 쿼리와 각 entry/section locator를 함께 기록했다.

| ID | 필드 값 | URL / 판본 | locator / 접근 |
|---|---|---|---|
| HA-M-000011 | label 상사근; korean 위빗근; hanja 上斜筋 | [KMLE superior oblique](https://m.kmle.co.kr/search.php?Page=1&Search=superior+oblique); KMLE 하위 판본 미노출 | 열린 HTML old 대한의협 3 entry와 대한해부학회·대한신경외과학회 섹션. Superior oblique muscle → 상사근(上斜筋), 위빗근; 해부학회는 위빗근 [옛 용어] 상사근, 신경외과학회는 上斜筋을 표시. 현재/옛 용어를 별도 필드로 보존. |
| HA-M-000012 | label 교근; korean 깨물근; hanja 咬筋 | [KMLE masseter](https://m.kmle.co.kr/search.php?Search=masseter); 하위 판본 미노출 | 검색결과 발췌. 대한해부학회 Masseter m. → 깨물근 [옛 용어] 교근; old 대한의협 3 `musculus masseter` → 교근(咬筋); 신경외과학회는 咬筋. direct HTML open은 Unicode decoding error. |
| HA-M-000013 | label 측두근; korean 관자근; hanja 側頭筋 | [KMLE temporalis](https://m.kmle.co.kr/search.php?Search=temporalis); 하위 판본 미노출 | 검색결과 발췌. 대한해부학회 Temporalis m. → 관자근 [옛 용어] 측두근; 신경외과학회 `temporalis m.` → 측두근 / 側頭筋. direct HTML open은 Unicode decoding error. |
| HA-M-000014 | label 외측익돌근; korean 가쪽날개근; hanja 外側翼突筋 | [KMLE pterygoid entries](https://www.kmle.co.kr/search.php?Search=nervus+pterygoideus); 하위 판본 미노출 | 검색결과 발췌의 old 대한의협 3 `musculus pterygoideus lateralis` → 외측날개근·외측익돌근(外側翼突筋); 대한해부학회 Lateral pterygoid m. → 가쪽날개근 [옛 용어] 외측익돌근. direct open 실패. |
| HA-M-000015 | label 내측익돌근; korean 안쪽날개근; hanja 內側翼突筋 | [KMLE pterygoid entries](https://www.kmle.co.kr/search.php?Search=nervus+pterygoideus); 하위 판본 미노출 | 검색결과 발췌의 old 대한의협 3 `musculus pterygoideus medialis` → 내측날개근·내측익돌근(內側翼突筋); 대한해부학회 Medial pterygoid m. → 안쪽날개근 [옛 용어] 내측익돌근. direct open 실패. |
| HA-M-000016 | label 이설근; korean 턱끝혀근; hanja 결측 | [KMLE genioglossus terms](https://kmle.co.kr/search.php?Search=geni); [legacy Hanja check](https://m.kmle.co.kr/search.php?Page=5&Search=posterior+papillary+muscle); 판본 미노출 | 첫 검색결과 발췌는 `genioglossus muscle` → 턱끝혀근·이설근. 별도 old 대한의협 2 발췌는 이설근/턱끝혀근 옆에 불완전 조각 `舌筋`만 표시한다. 조각은 완전 한자명으로 승격하지 않았다. Hanja 필드가 두 번째 URL의 fragment evidence를 직접 가리킨다. 두 direct open은 실패(Cache miss/HTML decode). |
| HA-M-000017 | label 설골설근; korean 목뿔혀근; hanja 舌骨舌筋 | [KMLE hyoglossus muscle](https://m.kmle.co.kr/search.php?Search=hyoglossus+muscle); 판본 미노출 | 검색결과 발췌. 대한해부학회 Hyoglossus m. → 목뿔혀근 [옛 용어] 설골설근; old `hyoglossus 나 musculus h.` → 설골혀근·설골설근(舌骨舌筋). direct HTML open은 Unicode decoding error. |
| HA-M-000018 | label 경돌설근; korean 붓혀근; hanja 莖突舌筋 | [KMLE styloglossus terms](https://m.kmle.co.kr/search.php?Page=1&Search=sty); 판본 미노출 | 검색결과 발췌. 대한해부학회 Styloglossus m. → 붓혀근 [옛 용어] 경돌설근; legacy `stylglossus` 표기에서 경돌설근(莖突舌筋). 원문 검색 색인에 보이는 `stylglossus` 오기는 alias로 복사하지 않았다. direct open은 cache miss. |
| HA-M-000020 | label 광배근; korean 넓은등근; hanja 廣背筋 | [KMLE latissimus dorsi](https://m.kmle.co.kr/search.php?Search=latissimus+dorsi); 판본 미노출 | 열린 HTML. 현재 대한의협 entry 넓은등근·광배근; old 대한의협 3 광배근(廣背筋); 대한해부학회 넓은등근 [옛 용어] 광배근; 신경외과학회 廣背筋. |
| HA-M-000021 | label 대능형근; korean 큰마름근; hanja 大菱形筋 | [KMLE rhomboid major](https://m.kmle.co.kr/search.php?Search=rhomboid+muscle%2C+greater); 판본 미노출 | 검색결과 발췌. 대한해부학회 Rhomboid major m. → 큰마름근 [옛 용어] 대능형근; old 대한의협 2 greater rhomboid muscle → 큰마름모근·대릉형근(大菱形筋). Hangul/hanja 원표기를 각각 보존. direct HTML open 실패. |

## 검토 경계

- FIPAT TA2의 20 English/Latin 필드는 공식 검색 색인과 T04 crosswalk row 관찰에 한정된다. 원 PDF 원문 visual review와 열 역할 확인은 실패/미수행이다.
- KMLE의 한글·한자 표기 관찰 중 실제 열린 HTML은 M11, M20이다. 나머지는 검색결과 발췌만 확인했고 접근 오류도 각 row에 남겼다.
- 모든 KMLE 하위 사전의 정확한 판본/개정일은 미노출이다.
- 웹 출처 확인을 사람 해부학 검토로 승격하지 않았다. 모든 신규 overlay와 field evidence에서 `humanReviewed=false`, 상태는 `not_performed`다.
