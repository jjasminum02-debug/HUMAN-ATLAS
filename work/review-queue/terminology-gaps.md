# T11 용어 검토 큐

확인일: 2026-09-25. 용어를 웹에서 찾은 상태와 사람의 해부학 검토 상태를 분리한다. 이 큐는 교과서/공식용어집의 원문 확보, 사람 검토, 전신 분모 확정을 대신하지 않는다.

## 전신 용어 coverage

- 현재 catalog에 있는 85개(개별근육 48, 근군 16, 부분/근두 21)는 부분 TA2 검색 색인 목록이다. 전신 분모가 아니며 동결되지 않았다.
- 첫 배치 T11-B01은 기존 canonical ID 8개와 기존 lookup 2개(판상근 후보)를 기록했다. 8 canonical 항목은 모두 출처가 불완전하거나 표기 검토가 남아 있어 web_checked_with_gaps다.
- T11-B02는 HA-G-000001–HA-G-000010의 근군 용어를 확인했고 `complete_with_gaps`다. 10개 전부 영어/라틴어 TA2 색인 관찰과 필드별 증거가 있다. 한글 표시 7개, 실제 출처 한자 4개만 채택했고 사람 검토는 하지 않았다.
- T11-B03은 `HA-G-000011`–`HA-G-000016`, `HA-M-000007`–`HA-M-000010` 10개를 `complete_with_gaps`로 기록했다. 영어/라틴어 20필드, 학습 overlay 7개, 출처 한자 4개가 있다. 상세 근거는 `work/reports/T11-B03.md` 및 `work/evidence/T11/B03/`에 있다.
- T11-B05–B08은 기존 ID를 `complete_with_gaps`로 조사했다. B08은 `HA-P-000004`–`HA-P-000013`이며 필수 50개와 별칭 6개의 field evidence를 기록했다. 마지막 배치 B09도 마쳤다. 배치 순서와 ID 목록은 `atlas-data/terminology/term-review-batches.json`에 있다.
- T11 전체 및 T14 언어 게이트는 미완이다.

## B07의 구체적 미확인/충돌

- T11-B07의 기존 ID 10개는 `complete_with_gaps`로 기록했다. 기본 필드 50행과 TA2/KMLE에서 관찰한 추가 동의어 17행을 남겼다. 총 누적 field evidence는 385개, 부분 목록 85개 중 68개가 web-checked-with-gaps, learner overlay는 64개다.
- Dalhousie 호스팅 TA2 Part II PDF의 직접 텍스트에서 Chapter 4 헤더 및 지정 행을 대조했다. HA-M-000043 `Obturator internus`/`Musculus obturatorius internus`, HA-M-000047 `Flexor brevis hallucis`/`Musculus flexor hallucis brevis`, HA-M-000048 `Adductor hallucis`/`Musculus adductor hallucis`의 기본 term과 synonym 열 차이를 확인했다. 기존 T04 crosswalk는 보존하고 B07 row locator에 열린 텍스트 셀 전체와 이전 색인 관찰을 함께 기록했다. 페이지 시각 검토는 하지 않았다.
- HA-M-000043의 한자는 exact source row에서 보이지 않아 null이다. HA-M-000046의 `大槌方形筋`은 문자 손상 가능성이 있어 미채택이다. HA-M-000047의 `短母指屈筋`/`短足拇趾屈筋`은 KMLE 결과에 함께 있어 한자 선택을 보류했다. HA-M-000048의 `母趾內轉筋`은 같은 legacy 결과의 다른 Korean spelling `모지내전근`에 연결되어 primary Hanja와 합치지 않았다.
- HA-P-000001/000002의 기존 overlay label은 보존했다. 이전 Korean field 문구 `장딴지근 · 가쪽갈래`, `장딴지근 · 안쪽갈래`는 head-specific 우리말 표기로 직접 확인하지 못해 검색 필드에서 빼고, 기존 overlay snapshot 및 미채택 후보로 남겼다. 2012 논문의 `비복근의 외측두/내측 두` 관찰은 label phrase만 뒷받침하며 사람 해부학 검토가 아니다.
- HA-P-000003의 KMLE 색인 표기 `교근의 천부`는 label로 기록했다. part-specific 순우리말 및 Hanja는 확인하지 못했으며 부모 `깨물근`/`咬筋`을 전용하지 않았다.
- KMLE 기반 원 사전의 정확한 판본·개정은 대부분 미노출이다. 모든 B07 값은 `humanReviewed=false`; 웹 색인·열린 HTML·논문 표현 검토를 해부학자 review와 분리했다. URL, 판본, locator, 접근 방식은 `work/evidence/T11/B07/web-source-log.md`와 `term-review-batches.json`에 있다.
- 통합 검색 32/32, B07 coverage/provenance, learning reference, preservation, `git diff --check`를 통과했다. 결과는 `work/evidence/T11/B07/validation.json`과 `validation.log`에 있다.
- T11 batch sequence는 B01–B09 총 9개이며, B09까지 웹 용어 배치 실행을 마쳤다. T12는 미시작, T14는 미완이다.

## B08의 구체적 미확인/충돌

- T11-B08 `HA-P-000004`–`HA-P-000013` 10개는 `complete_with_gaps`다. 필수 필드 근거 50개와 TA2 `Other` 셀에서 채택한 추가 alias 6개를 기록했다. 누적 field evidence는 441개, partial catalog coverage는 78/85, learner overlay는 74개다.
- FIPAT TA2 Second Edition (2.07) Part II의 공식 Dalhousie 호스팅 원본 PDF를 직접 열어 Chapter 4 머리글과 배정된 Latin/UK/US English/synonym 텍스트 셀을 확인했다. PDF text layer만 확인했으며 페이지 이미지를 렌더해 표 열 배치를 시각적으로 검사하지 않았다. T04 `source-crosswalk.json`은 수정하지 않았다.
- `심부 교근`은 KMLE 검색결과 설명문에서 관찰한 표현이며 전용 한글 표제어가 아니다. `외익돌근 상두/하두`는 KMLE 색인의 치과 용어 사전 머리 항목 표현이다. 두 출처 계열의 정확한 판본/개정은 노출되지 않았다. 현재 우리말 head 용어를 별도로 확인하지 못했다.
- 안쪽날개근의 깊은/얕은 근두는 정확한 한글·한자 근거를 찾지 못해 English display fallback을 유지했다. P4–P8 현재 우리말 필드는 null이다.
- P9–P11 `승모근 상부/중부/하부`와 `등세모근 위부분/중간부분/아래부분`, P12–P13 `대흉근 쇄골부/흉늑부`와 `큰가슴근 빗장부분/복장갈비부분`은 YES24 상품 페이지에 직접 표시된 목차에서 각각 영어 표현과 함께 읽었다. 책 본문은 접근하지 않았고 catalog 밖 상세 판본은 노출되지 않는다.
- 한자 10개 모두 part-specific 원문 근거가 없어 null이다. KMLE의 `僧帽筋`은 부모 등세모근 항목이므로 P9–P11에 이어 붙이지 않았다. 모든 B08 용어/필드의 사람 해부학 검토 상태는 `not_performed`다.
- B08 통합검색 회귀 35/35, coverage/provenance, learning reference, 파일 보존, `git diff --check`가 통과했다. 검증 결과는 `work/evidence/T11/B08/validation.json` 및 `validation.log`에 있다.
- T11은 B01–B09 총 9개 배치다. B09까지 배치 실행을 마쳤고 T12는 미시작, T14는 미완이다.

## B09의 구체적 미확인/충돌

- T11-B09의 기존 ID `HA-P-000014`, `HA-P-000016`–`HA-P-000021` 7개를 `complete_with_gaps`로 기록했다. 필수 field evidence 35개와 개별 alias evidence 13개, 합계 48개를 추가했다. 누적 field evidence는 489개, partial catalog coverage는 85/85 `web_checked_with_gaps`, learner overlay는 81개다. 85는 현재 부분 목록 분모이며 전신 분모가 아니다.
- FIPAT TA2 Second Edition (2.07) Part II의 공식 Dalhousie 호스팅 PDF를 열어 Chapter 4 표 머리글과 지정 행 2453, 2455, 2465–2466, 2472–2474의 텍스트 셀을 확인했다. 텍스트 계층 대조이며 페이지 이미지의 표 열 배치와 정오표는 시각 검토하지 않았다. T04 `source-crosswalk.json`은 byte-identical하게 유지했다.
- KMLE는 직접 연 집계 HTML과 검색 색인 발췌를 구분했다. underlying dictionary 판본/개정은 노출되지 않는다. P14의 `빗장부분`은 generic Clavicular part 표기여서 기존 TA2 deltoid part와 연결했지만 부모 말을 붙여 full phrase를 조합하지 않았다. P16은 full Korean term을 확인하지 못했다. 일반 `Spinal part → 척수부분`은 맥락이 달라 채택하지 않았다.
- P17/P19의 generic `긴갈래`는 각각 이두근 장두와 삼두근 장두의 공통 검색어라 검색에서 두 기존 ID를 함께 반환한다. P20의 KMLE legacy result가 lateral head를 caput longum/장두에 연결하는 충돌은 TA2 row 2473의 caput laterale와 상충하므로 학습 alias로 제외했다.
- 7개 모두 part/head-specific 한자 근거가 없어 null이다. 부모 근육 한자를 상속하지 않았다. 웹 용어 증거, PDF/HTML 직접 열람, 검색 색인을 사람 해부학 검토와 구분했으며 사람 검토는 미수행이다.
- 전체 통합검색은 38/38, B09 coverage/provenance, learning-content reference, preservation, `git diff --check`가 통과했다. ID별 source URL·판본 상태·locator·조회일·접근 방식은 `work/evidence/T11/B09/web-source-log.md` 및 terminology ledger에 있다. 검사 결과는 `work/evidence/T11/B09/validation.json`과 `validation.log`다.
- T11의 B01–B09 용어 배치 실행은 모두 끝났으나 전체 상태는 partial이다. 현재 85개 목록 밖의 전신 분모, 판상근 lookup canonicalization, 사람 해부학 검토, T14 언어 gate가 남았다. 다음 task T12는 미시작이다.

## B02의 구체적 미확인/충돌

- HA-G-000004 혀근육: KMLE의 옛 표기 설근은 발견했으나 한자 원문이 보이지 않고 혀뿌리/설근과 혼동될 수 있어 alias에서 보류했다.
- HA-G-000005 hypaxial muscles of back: 일반 muscles of back / 등근육·배부근은 검색되었지만 TA2의 narrower hypaxial group과 동일하다는 근거가 없다. 한국어/한자 label을 만들지 않았다.
- HA-G-000006 muscles of thorax: 옛 항목 흉부근(胸部筋)은 확인했다. 가슴근육은 KMLE 대한해부학회 용어 색인에서 Pectoralis muscles에도 쓰여 unique alias로 연결하지 않았다.
- HA-G-000008 scapulohumeral muscles: 형용사 scapulohumeral의 어깨위팔-/견갑상완(골)-만 검색되었다. 근군명은 조합해 만들지 않았다.
- HA-G-000009 rotator cuff muscles: 회전근개/돌림근띠/回旋腱板는 cuff term으로 확인했으며 TA2 muscle-group ID 전체와의 용어 동치를 확인하지 못했다.
- 한글 표시 label은 7/10에만 추가했다. 미확인 세 그룹은 기존 English/Latin canonical terms를 유지하고 learner overlay Korean 값은 비웠다.

## B03의 구체적 미확인/충돌

- HA-G-000011 superficial gluteal muscles, HA-G-000012 deep gluteal muscles: KMLE가 일반 `gluteus muscle`에 `볼기근`, `둔근`, `臀筋`을 보이지만 층별 근군과 동일하다고 말하지 않는다. 세 용어를 B03 ID에 연결하지 않았고 label/korean/hanja를 미확인으로 유지했다.
- HA-G-000013 anterior, HA-G-000014 lateral, HA-G-000015 posterior compartment of leg: 고정 revision의 한국어 Wikipedia 표제/식별정보에서 `종아리앞칸`, `종아리가쪽칸`, `종아리뒤칸` 표기를 확인해 웹-용어 overlay에 기록했다. 세 문서는 공동 편집 페이지여서 사람 해부학 검토로 세지 않는다. 한자 자료는 확인하지 않았다.
- HA-G-000015 posterior compartment: 원문에서 얕은층과 깊은층으로 나뉜다는 설명이 있어 전체 뒤칸 명칭만 적용했다. 깊은 뒤칸 이름으로 제한하지 않았다.
- HA-G-000016 muscles of foot: KMLE에서 확인된 것은 `intrinsic muscles of foot` 정의 및 일반 발 항목이다. TA2 전체 발 근육군과 범위가 달라 한국어/한자 label 및 overlay를 보류했다.
- HA-M-000007–000010 superior/inferior/medial/lateral rectus: `상직근/하직근/내직근/외직근`, 우리말 `위곧은근/아래곧은근/안쪽곧은근/가쪽곧은근`, 실제로 표기된 `上直筋/下直筋/內直筋/外直筋`을 동일한 기존 ID에 연결했다. M07은 국립국어원 온용어(우리말샘 2023-06 기준)에서 확인했다. M08–10의 KMLE 하위 사전 판본/개정일은 노출되지 않는다.
- B03 영어/라틴어 값은 FIPAT TA2 공식 검색결과 및 T04 crosswalk 관찰이다. TA2 PDF 직접 open 실패로 열 역할·원문 행 시각 대조·정오표 확인은 미완이다. B03 사람 해부학 검토는 수행하지 않았다.

## B01의 구체적 미확인/충돌

- Gastrocnemius (HA-M-000001): KMLE에 비腹筋/排腹筋 등 혼합·손상 문자 표기가 있어 한자를 null로 유지한다.
- Soleus (HA-M-000002): 가자미근과 연결되는 신뢰 가능한 한자 항목/판본 locator를 찾지 못했다.
- Tibialis anterior (HA-M-000003): 前脛骨筋은 용어집의 exact item이 아니라 한의표준임상진료지침 PDF의 문자열 사용 사례다. 용어 쌍 관찰만 기록했고 임상·침 콘텐츠는 가져오지 않았다.
- Tibialis posterior (HA-M-000004): 後脛骨筋은 KMLE legacy dictionary section에서 확인했다. 정확한 원 사전 판본/연도는 화면에 노출되지 않는다.
- Fibularis longus/brevis (HA-M-000005/000006): 長鼻骨筋/長排骨筋/長批骨筋, 短鼻骨筋 등 legacy spelling이 서로 달라 한자를 채택하지 않았다.
- Deltoid acromial part (HA-P-000015): TA2 row와 영어 lateral (acromial) 표기는 있으나 한국어 견봉부분은 조합형 표시어이며 별도의 한국어 항목 출처가 없다. 한자도 part-specific 근거가 없다. 측면삼각근은 사용자 검색어였고 사람 검토 전까지 source-approved Korean synonym이 아니다.
- 기존 middle deltoid 별칭은 이번 출처 확인에서 acromial part와 직접 동치로 연결하는 정확한 문구를 찾지 못해 overlay에서 제거했다. 필요하면 이후 사람이 확인된 출처로 다시 연결한다.
- Splenius capitis/cervicis lookup (LOOKUP-SPLENIUS-CAPITIS/CERVICIS): TA2 Part 2 search index rows 2273–2274와 KMLE legacy Hanja rows를 확인했다. 현재 85개 catalog에는 같은 개념의 canonical ID가 없다. canonical denominator/ID 동결 전 임의 ID나 조인을 만들지 않았다. generic splenius/널판근/판상근 검색은 두 후보를 모두 보인다.

## 출처 접근 및 검토 상태

- FIPAT TA2 Part 2의 공식 검색 색인은 B01 row 2272–2274, B02 rows 2040, 2041, 2104, 2116, 2225, 2299, 2450, 2451, 2456, 2592, B03 rows 2042–2045, 2597, 2603, 2643, 2651, 2654, 2669의 관찰을 포함한다. B02에서 직접 PDF open은 HTTP 502, B03에서는 fetch Internal Error로 실패했고 원본 페이지 이미지/열 역할/errata는 대조하지 못했다. TA2 term-cell 역할은 계속 needs review다.
- KMLE 페이지에서 현재 대한해부학회 표기 및 일부 구용어/한자 결과를 확인했으나 KMLE가 표시한 각 underlying dictionary의 정확한 판본/연도는 대부분 노출되지 않았다.
- 국립국어원 온용어 승모근 entry는 우리말샘 2023년 6월 snapshot이라고 자료 설명에 밝히며 僧帽筋 및 동의어 등세모근을 함께 보인다.
- NCBI Bookshelf StatPearls (2024 Jan-, last update 2024-01-30) 검색결과 excerpt는 deltoid lateral part를 acromial로 표시했다. 직접 페이지/전문 접근은 이번 확인에서 되지 않아 indexed excerpt 상태다.
- 웹·사전 근거는 철자/용어 관찰에만 사용한다. ID 사이의 해부학적 동일성, part classification, 영어/한글 preferred status 및 구조/기능 정확성에 대한 자격 있는 사람의 검토는 수행하지 않았다.

다음 조치: T12를 시작할 때 T12a 엔진 동등성 실험만 수행하고 T12b는 별도 단계로 둔다. T11의 웹 용어 배치 완료가 사람 해부학 검토, 전신 분모 동결, T14 언어 gate를 대신하지 않는다. Splenius canonical mapping, TA2 표 시각/errata 대조, B01의 Hanja/part Korean term 확정과 B02/B03 범위 충돌은 적절한 원자료 확보 또는 사람 검토가 선행되어야 한다.

## B04의 구체적 미확인/충돌

- T11-B04의 10개 기존 ID는 `complete_with_gaps`로 기록했다. 각 ID의 영어·라틴어 관찰은 TA2 공식 검색 색인에 있다. PDF 직접 open이 HTTP 502라 원문 행/열과 용어 열 역할·정오표는 아직 확인되지 않았다.
- HA-M-000011–000018, HA-M-000020–000021의 우리말 및 관용/구용어 표기는 KMLE 페이지/검색결과에서 확인했으나 KMLE 하위 사전 판본·개정일은 미노출이다. 실제 열린 HTML은 superior oblique와 latissimus dorsi 두 검색 페이지이고, 나머지는 검색결과 발췌만 확인했다.
- HA-M-000016 genioglossus: `이설근`, `턱끝혀근`은 검색결과에 있으나 `舌筋`만 불완전 조각으로 관찰된다. 완전한 한자 용어로 확장하지 않고 `hanja=null`로 유지했다. 조각은 learner search field에 넣지 않았다.
- 나머지 9개 B04 개별근육 한자는 KMLE 항목에 표시된 완전한 표기만 기록했다. 고어/현행 한글 차이를 같은 ID의 `label`과 `korean`에 나누어 유지했다. 이 표기 확인은 ID-개념 동일성에 대한 사람 해부학 검토가 아니다.
- 검색 회귀 첫 실행의 부정 assertion은 `舌骨舌筋`에 포함된 부분 문자열 `舌筋`이 유효한 HA-M-000017 검색 결과로 잡히는 점을 고려하지 않아 실패했다. assertion을 수정해 불완전 조각이 HA-M-000016에 연결되지 않는지만 검사했고 최종 25/25 회귀 통과했다. 데이터 값을 수정한 것은 아니다.
- 사람 해부학 검토는 미수행이며 overlay에서 전부 `humanReviewed=false`다. 용어 완성 및 T14 언어 gate는 미완이다.
- B04 검색 회귀의 부가 관찰: 부분검색 `舌筋`은 완전한 한자 검색어 `舌骨舌筋`(HA-M-000017), `莖突舌筋`(HA-M-000018)에 대한 일반 substring 결과로 이 둘을 반환하지만 HA-M-000016으로는 연결되지 않는다. 이는 명시적 alias/evidence가 아니며 결과 ID는 `work/evidence/T11/B04/search-fragment-observation.json`에 기록했다.


## B05의 구체적 미확인/충돌

- T11-B05의 기존 ID 10개는 `complete_with_gaps`로 기록했다. 필수 50개 field evidence와 HA-M-000030의 기존 `Deltoid` alias 보존 근거 1개를 기록했다. English/Latin 필드는 TA2 공식 Dalhousie-hosted PDF를 직접 열어 텍스트 행과 Chapter 4 열 머리글을 대조했다. 원 FIPAT library URL은 HTTP 502였고 PDF 시각 페이지 렌더는 수행하지 않았다.
- KMLE는 HA-M-000030 외에는 검색결과 발췌이며 하위 사전 판본/개정일이 노출되지 않았다. HA-M-000030은 실제 HTML 페이지를 열었고 CancerWEB 항목에 2000-03-05가 표기되어 있다.
- HA-M-000027 검색결과에는 `前方鋸筋`과 `前鋸筋`이 모두 보인다. 여기서는 exact musculus serratus anterior의 대한해부학회 old term 및 `前鋸筋`만 기록하고, `前方鋸筋`은 미채택했다.
- HA-M-000030의 기존 overlay `Deltoid`를 없애지 않고 TA2 English `Deltoid muscle`, Latin `Musculus deltoideus`와 별도 alias로 보존했다.
- HA-M-000022, HA-M-000023, HA-M-000024–000031의 선택된 한자 각각은 KMLE 검색결과에 완전한 문자열로 표시된다. 사전 판본과 사람 해부학 검토는 여전히 미확인/미수행이다.
- 사람 해부학 검토는 미수행이다. 상세 URL, locator, 접근 방식은 `work/evidence/T11/B05/web-source-log.md` 및 terminology fieldEvidence에 있다.

## B06의 구체적 미확인/충돌

- T11-B06은 기존 `HA-M-000032`–`HA-M-000041` 10개를 `complete_with_gaps`로 기록했다. 필수 50개 provenance와 원문에서 확인한 추가 동의어 10개를 남겼다. 영어/라틴어는 Dalhousie-hosted TA2 PDF 텍스트 계층의 지정 행 및 표 머리글에서 확인했다. 앞부분은 *Terminologia Anatomica*, Second Edition (2.07), 2019 인용, 2020 IFAA 승인/채택으로 표시된다. 시각 PDF 표 레이아웃 및 errata 대조는 미수행이다.
- KMLE에서는 검색결과 발췌와 실제 열린 HTML 페이지를 구분했다. 기저 용어집의 정확한 판본/개정은 대부분 노출되지 않았다. `棘下筋`, `小圓筋`은 exact legacy term row에 연결된 완전한 표기로 채택했다. 다른 결과의 `極下筋`, `小園筋`, `小圓形筋`은 같은 기존 ID의 learner alias로 합치지 않았다.
- HA-M-000036 오훼완근/부리위팔근은 한자를 직접 뒷받침하는 확인 가능한 KMLE 항목이 없으므로 `hanja=null`이다. `烏喙腕筋`, `烏口腕筋`은 원 판본/locator 미확인인 2차 후보로만 남겼다.
- TA2 `Other`에 나타난 HA-M-000032의 `Muculus infra spinam` 텍스트 계층 표기는 철자 이상 가능성이 있어 미채택했다. B06 learner overlay 및 모든 field evidence는 `humanReviewed=false`, `not_performed`이며 사람 해부학 검토가 아니다.
- 통합검색 regression은 29/29, B06 coverage/provenance와 학습 reference validator, 보존 검사, `git diff --check`는 통과했다. 전체 결과와 명령은 `work/evidence/T11/B06/validation.json` 및 `validation.log`; ID별 URL, locator, 조회일, 접근 방법은 `work/evidence/T11/B06/web-source-log.md`와 terminology ledger에 있다.
