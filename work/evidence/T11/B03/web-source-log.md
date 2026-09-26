# T11-B03 웹 출처 기록

조회일은 모두 `2026-09-25`다. 용어 문자열의 웹 근거, 표준 판본의 검색 색인, 열린 원문, 사람 해부학 검토는 서로 다른 상태다. 필드별 정규 기록은 `atlas-data/terminology/term-review-batches.json`에 있으며 각 `sourceId`가 아래 URL·판본·locator·접근방식에 연결된다.

## 출처 레지스트리

| sourceId | URL | 판본/버전 | locator와 접근방식 |
|---|---|---|---|
| `fipat-ta2-b03-index` | [FIPAT TA2 Part 2 PDF](https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf) | *Terminologia Anatomica*, 2판 Part 2, 온라인 2019; PDF 호스팅 경로 2020-09 | 인쇄면 74, 94–96; 표 행 2042–2045, 2597, 2603, 2643, 2651, 2654, 2669. 공식 PDF 검색결과 텍스트를 확인했다. PDF 직접 open은 이전 확인에서 HTTP 502, 이번 도구에서는 Internal Error로 실패했다. 로컬 PDF·페이지 이미지·열 역할·정오표를 대조하지 않았다. 정확한 행과 영어/라틴어는 T04 crosswalk와 함께 사용하며 열 의미는 미확인으로 둔다. |
| `kmle-b03-gluteus-near-match` | [KMLE gluteus 검색](https://m.kmle.co.kr/search.php?Search=gluteus) | KMLE 웹 통합; 해당 사전 항목의 판본/개정일 미노출 | 열린 HTML의 일반 `gluteus muscle` → 볼기근, 둔근; 구 대한의협 3 `gluteus = glutaeus` → 둔근(臀筋), 신경외과 사전 `gluteus m.` → 볼기근/둔근·臀筋. 일반어뿐이므로 표층·심층 볼기근군에 연결하지 않았다. |
| `kmle-b03-intrinsic-foot-near-match` | [KMLE intrinsic muscles of foot 검색](https://m.kmle.co.kr/search.php?Search=intrinsic+muscles+of+foot) | KMLE 웹 통합; 인용된 CancerWEB 항목은 결과에 2000-03-05로 표시되나 정확한 판본/개정은 미노출 | 검색결과 발췌에서 `intrinsic muscles of foot`를 발 안에 완전히 놓인 근육으로 한정한 정의와 일반 `foot` → 발/족을 확인했다. 검색 페이지 직접 open은 실패했다. 전체 발 근육군과 범위가 달라 채택하지 않았다. |
| `ko-wiki-b03-anterior-leg-compartment` | [종아리앞칸 고정판](https://ko.wikipedia.org/w/index.php?title=종아리앞칸&oldid=39701799) | 편집판이 고정되지 않는 공동 편집 문서; 캡처 revision `oldid=39701799`, 최종 편집일 2025-05-07 | 열린 HTML, 문서 제목 및 식별정보 영역: 종아리앞칸, Latin/English 용어, TA2 행 2643. 표제어 문자열만 사용했다. |
| `ko-wiki-b03-lateral-leg-compartment` | [종아리가쪽칸 고정판](https://ko.wikipedia.org/w/index.php?title=종아리가쪽칸&oldid=39701801) | 편집판이 고정되지 않는 공동 편집 문서; 캡처 revision `oldid=39701801`, 최종 편집일 2025-05-07 | 열린 HTML, 문서 제목 및 식별정보 영역: 종아리가쪽칸, Latin/English 용어, TA2 행 2651. 표제어 문자열만 사용했다. |
| `ko-wiki-b03-posterior-leg-compartment` | [종아리뒤칸 고정판](https://ko.wikipedia.org/w/index.php?title=종아리뒤칸&oldid=39701625) | 편집판이 고정되지 않는 공동 편집 문서; 캡처 revision `oldid=39701625`, 최종 편집일 2025-05-07 | 열린 HTML, 문서 제목 및 식별정보 영역: 종아리뒤칸, Latin/English 용어, TA2 행 2654. 문서가 얕은층·깊은층 구분을 함께 적어 전체 뒤칸 명칭으로만 사용했다. |
| `nikl-b03-superior-rectus` | [국립국어원 온용어 상직근](https://kli.korean.go.kr/term/trgtWord/indexTrgtWord.do?trgtWordNo=2251777) | 온용어 페이지가 밝힌 우리말샘 전문용어 자료 기준 2023-06; 온용어 페이지 개정일 미노출 | 열린 국립국어원 용어 항목: 상직근, 원어 上直筋, 영어 superior rectus/superior rectus muscle, 동의어 위^곧은근. 용어 표기만 사용했다. |
| `kmle-b03-inferior-rectus` | [KMLE inferior rectus 검색](https://m.kmle.co.kr/search.php?Search=rectus+muscle+of+thigh) | KMLE 웹 통합; 하위 사전 판본/개정 미노출 | 열린 HTML의 하직근(下直筋), 아래곧은근 항목과 대한해부학회 섹션의 아래곧은근/옛 용어 하직근. 넓은 검색어지만 해당 용어 결과를 locator로 구분했다. |
| `kmle-b03-medial-rectus` | [KMLE medial rectus 검색](https://m.kmle.co.kr/search.php?Search=medial+rectus) | KMLE 웹 통합; 하위 사전 판본/개정 미노출 | 열린 HTML, 대한신경외과학회 항목: 안쪽곧은근·내직근·內直筋; 대한해부학회 항목: 안쪽곧은근/옛 용어 내측직근. |
| `kmle-b03-lateral-rectus` | [KMLE lateral rectus 검색](https://m.kmle.co.kr/search.php?Search=lateral+rectus+muscle) | KMLE 웹 통합; 하위 사전 판본/개정 미노출 | 열린 HTML, 구 대한의협 3 항목: 외직근(外直筋), 가쪽곧은근; 대한해부학회 항목: 가쪽곧은근/옛 용어 외측직근. |

## 배정 ID별 사용 필드

영어 값과 라틴어 `aliases[0]`는 각 ID의 T04 TA2 crosswalk 행과 공식 호스팅 PDF 검색결과에서 가져왔다. 필드 evidence에는 행 번호, 인쇄면, 정확한 표준 판본, URL을 가진 source ID가 연결되어 있다.

| 기존 ID | label / korean / hanja 필드 | english / aliases[0] | 결정 |
|---|---|---|---|
| `HA-G-000011` | 세 값 모두 결측; KMLE generic gluteus 근접항목만 근거 | TA2 row 2597 | `볼기근`, `둔근`, `臀筋`을 표층 근군에 연결하지 않음 |
| `HA-G-000012` | 세 값 모두 결측; KMLE generic gluteus 근접항목만 근거 | TA2 row 2603 | `볼기근`, `둔근`, `臀筋`을 심층 근군에 연결하지 않음 |
| `HA-G-000013` | `종아리앞칸` / `종아리앞칸` / 결측; 고정된 Wikipedia 문서 제목 | TA2 row 2643 | source label은 웹 대조이며 사람 검토 아님 |
| `HA-G-000014` | `종아리가쪽칸` / `종아리가쪽칸` / 결측; 고정된 Wikipedia 문서 제목 | TA2 row 2651 | source label은 웹 대조이며 사람 검토 아님 |
| `HA-G-000015` | `종아리뒤칸` / `종아리뒤칸` / 결측; 고정된 Wikipedia 문서 제목 | TA2 row 2654 | 뒤칸 전체로 기록; 얕은층/깊은층으로 좁히지 않음 |
| `HA-G-000016` | 세 값 모두 결측; KMLE 발 고유근·일반 발 근접항목만 근거 | TA2 row 2669 | intrinsic-only 그룹을 전체 발 근육군에 연결하지 않음 |
| `HA-M-000007` | `상직근` / `위곧은근` / `上直筋`; 국립국어원 온용어 | TA2 row 2042 | label·우리말·실제 한자 모두 같은 기존 ID |
| `HA-M-000008` | `하직근` / `아래곧은근` / `下直筋`; KMLE | TA2 row 2043 | label·우리말·실제 한자 모두 같은 기존 ID |
| `HA-M-000009` | `내직근` / `안쪽곧은근` / `內直筋`; KMLE | TA2 row 2044 | label·우리말·실제 한자 모두 같은 기존 ID |
| `HA-M-000010` | `외직근` / `가쪽곧은근` / `外直筋`; KMLE | TA2 row 2045 | label·우리말·실제 한자 모두 같은 기존 ID |

## 검토 경계

- TA2의 영어/라틴어는 공식 검색결과 텍스트와 T04 crosswalk 관찰값이다. 원본 PDF를 열어 행 배치·열 역할·정오표를 확인한 것은 아니다.
- KMLE 페이지에서 하위 사전 이름 일부는 보이지만 해당 용어집의 판본·발행연도·개정 이력을 대부분 노출하지 않는다.
- 한국어 Wikipedia 판본은 문서상 TA2 ID를 가리키므로 표제어 cross-reference에만 썼다. 이 사이트를 자격 있는 사람의 해부학 검토로 보지 않았다.
- 사람 해부학 검토자는 없었다. 모든 B03 필드 및 overlay는 `humanAnatomyReviewStatus=not_performed`, `humanReviewed=false`다.
