# T04 canonical-catalog gaps and review queue

확인일: 2026-09-25. `atlas-data/catalog/`의 catalog은 공식 TA2 검색 색인에서 발견한 일부 행만 구조화한 partial extract다. 아래 항목은 미확인 또는 보류 상태이며 빈 영역을 추측으로 채우지 않는다.

## 전신 목록 및 분모

- 현재 catalog: individual muscle 48, group 16, part/head 21. 확인된 이 부분 집계는 T01 whole-body denominator가 아니다.
- 전체 목록의 source binary가 없어 모든 범위 부위의 행을 일관된 기준으로 추출할 수 없다. `catalog-status.json`의 전체 근육 수와 `denominatorFrozen`은 null/false이며 `wholeBodyGate=blocked`다.
- `variants=0`은 captured excerpts에서 variant로 확정한 행이 0이라는 뜻이다. 해부 변이가 없다는 뜻이 아니다. 괄호가 들어간 TA2 행은 괄호만으로 variant라고 추정하지 않고 미분류로 남긴다.

## 영역별 확인 범위

| T01 region ID | T04 상태 | 비고 |
|---|---|---|
| head | partial | TA2 head heading과 눈 항목 일부 |
| face | not enumerated | 근육별 locator 미확인 |
| mastication | partial | group과 선택 항목 |
| eye | partial | extraocular group과 선택 근육 |
| tongue | partial | group과 선택 항목 |
| pharynx | not enumerated | 근육별 locator 미확인 |
| larynx | not enumerated | 근육별 locator 미확인 |
| neck | not enumerated | 근육별 locator 미확인 |
| back | partial | 일부 hypaxial group, muscle, part |
| thorax_respiratory | partial | thorax heading, 일부 pectoral/thoracic 항목 |
| abdominal_wall | partial | 일부 abdominal row만 노출; 전체 section tree 미확인 |
| pelvic_floor_perineum | not enumerated | 인접한 broad `Muscles of pelvis` heading은 보였지만 T01 scope와 일치하는 구성 근육을 확인하지 못해 catalog에 넣지 않음 |
| shoulder | partial | scapulohumeral, cuff, deltoid 일부 |
| upper_extremity | partial | upper limb heading과 선택 arm 항목; hand section 미확인 |
| hand | not enumerated | 근육별 locator 미확인 |
| gluteal | partial | shallow/deep group과 일부 개별 항목 |
| lower_extremity | partial | hip/thigh/leg/fascia table excerpt; 전체 목록 아님 |
| foot | partial | foot heading과 일부 intrinsic muscle/part |

## 판본과 term-cell 역할

- TA2 2판(2019)은 공식 IFAA 안내에서 기준판으로 식별되었다. Part 2 PDF 원본은 로컬 미확보이고 row text는 FIPAT-hosted search index로만 봤다. 날짜 고정 파일/hash 및 표 셀 시각 검토는 없다.
- FIPAT 안내의 term category/7열 설명은 확인했지만, PDF 원본의 개별 표 셀 배치를 확인하지 못했다. 모든 source term records는 `needs_review`; source crosswalk에서 official/equivalent/synonym 열 역할이 미확정이다.
- FIPAT Errata PDF 링크를 기록했으나 catalog의 모든 행을 errata와 대조하지 않았다.
- 별도 괄호 행 중 분류 보류 예시: row 2230 `(Musculus transversus nuchae)`, row 2300 `(Musculus sternalis)`, row 2304 `(Pars abdominalis musculi pectoralis majoris)`, row 2617 `(Caput tertium musculi recti femoris)`, row 2632 `(Adductor minimus)`. 이는 미등록/보류 예시이며 해당 분류 의미를 확인한 것이 아니다.

## 언어와 사람 검토

- 대한해부학회 해부학용어집 원본/최신판, 정확한 근육 항목 및 라이선스를 확보하기 전까지 한국어 Hangul/Hanja term은 null이다.
- 현재 concept/term은 사람 해부학 검토를 받지 않았다. T02의 FMA/representation/file 연결은 T04 provisional name crosswalk일 뿐이다.
- TA2 CC BY-ND 4.0에 대한 특정 파일 attribution, 내부 구조화 인덱스가 adaptation인지 여부, 외부 재사용 범위의 법률 검토가 끝나지 않았다. 공개/재배포는 승인되지 않았다.

## 해소 작업

1. 사용 가능한 공식 TA2 Part 2 원본을 확보하고 파일명, 판본, retrieved date, SHA-256을 기록한다. 원본이 계속 inaccessible이면 사용자가 제공한 합법적 source copy 또는 FIPAT 승인 접근 경로를 활용한다.
2. 페이지/행 및 7-column role을 시각 대조하고 Errata를 전수 확인한다.
3. 18개 T01 영역 전체의 row inventory를 체계적으로 추출하되 group/individual/part/variant를 나누고 예외/중복/다영역 tag를 사람 검토한다.
4. KAA/대한해부학회가 지정하는 현행 용어집의 정확한 근육 항목/판본/재사용 조건을 확보한 뒤 한국어와 Hanja를 별도로 입력한다.
5. 실제 FMA↔TA2 crosswalk 및 T02 mesh relationship을 해부 전문가가 확인한다.
