# AT10/skin-fit 실패 원인과 종료 경로 검토

2026-10-14, 확인 HEAD `0e8c055191aa49980d31b4774e6469a61828b6ef`.

이 문서는 실제 코드·자산·교차 evidence를 읽은 **분석과 권고안**이다. 구현 실행, task 추가, EXECUTION 변경 또는 acceptance 승인이 아니다. 현재 skin-fit은 partial/geometry=false이며 skin-runtime을 시작하지 않는다.

## 판단

MakeHuman 피부 입력과 권리/단위/원본 대응/GLB export 경로는 확보돼 있다. 현재 병목은 **ZA에 맞는 부위별 피부 표면 대응과 접합을 작성하지 못했고, 수정 과정에서 실제 관통을 막는 제약이 충분하지 않은 것**이다. 교수 승인이나 피부 파일 전체의 부재가 원인이 아니다. MakeHuman 원본이 전신 입력으로 부적합하다고 입증한 결과도 없다.

기존 도구·보존·export·검사 경로는 재사용할 수 있다. 피부 외형 자체는 아직 완성되지 않았다. 제가 수치상 안정된 후보를 만들면서도 실제 표면 대응과 전신 인수 검사를 닫지 못한 구현 실패다.

| 실제 상태 | native와 교차한 피부 triangle | non-adjacent 자기 교차 쌍 | 판정 |
|---|---:|---:|---|
| r22 기준 checkpoint | 3,874 | 1,604 | 미달, 현재 재개 입력 |
| r34 귀·양측 골반 시도 | 3,978 | 1,130 | 미채택 |
| r35 손·발 시도 | 4,775 | 1,063 | 미채택 |

source/native pair 제안 6,922개는 실제 주소가 기록됐다는 뜻이다. 대응의 해부 의미·정합 품질이 승인됐다는 뜻이 아니다. 실제 learner skin import는 0이며 offline 화면을 learner 합격으로 세지 않았다.

## 확인된 구현 문제

1. **관절 중심 정합을 피부 윤곽 정합으로 연결하는 조건이 부족하다.** r35의 관절 중심 이동은 손 2.25µm/발 3.75µm 이내지만 실제 fascia/tendon이 피부 밖에 남는다. 중심과 축을 맞춰도 손바닥 두께, 엄지 web, 발등/발바닥/heel, 귀 부착 형태는 결정되지 않는다.
2. **표면 구역 배정에 연결성과 해부 역할의 보장이 없다.** `at10_skin_surface_bands.py`의 `contact_bands`는 각 source vertex를 가까운 bone beam으로 독립 배정하고, 넓은 이름 필터와 축/반경 안의 ray hit를 사용한다. 인접한 source 면이 다른 손가락·힘줄·앞뒤 표면으로 넘어가는 것을 구조적으로 막지 못한다. global source-Y의 양/음 표시도 그 자체로 해부학적 palmar/dorsal 분류가 아니다. 코드의 3/5mm allowance는 정합 여유값이며 표준 피하 두께가 아니다.
3. **교차 검사가 주로 사후 검사다.** 현재 line search는 sampled Jacobian과 target 오차를 검사하지만, 실제 native/self triangle 교차를 이동 허용 조건으로 직접 사용하지 않는다. 양의 국소 미분·작은 제약 오차와 관통이 함께 존재할 수 있다.
4. **경계 위치를 고정하는 것만으로 전신 접합이 끝나지 않는다.** source boundary와 인접 ring을 유지해도 기울기·접선, 피부 간 접촉과 주변 구역의 남은 변형까지 해결되지 않는다. 손·발의 local solver가 겨드랑이나 얼굴의 기존 결함을 고칠 수도 없다.
5. **미완 목록이 실제 전신 결함을 충분히 세분화하지 못했다.** 손발·귀·샅 중심으로 재시도하면서 겨드랑/팔–몸통, 얼굴 return과 외피를 별도 완료 단위로 명확히 닫지 못했다. r22의 다른 부위 역시 이미 승인된 전신으로 간주하면 안 된다.

방향 비교 경고 731개와 큰 target edge 도약 271건은 위 대응 규칙을 재검토할 주소 목록이다. 면 법선 비교와 길이 비율은 진단값으로, 잘못된 해부 대응이나 정합 불가능의 수학적 증명이 아니다. 실제 미달은 emitted 교차와 화면으로 확인됐다.

## 이번 재검토에서 분해한 자기 교차

기존 `fit-r35-contact-addresses.npz`의 실제 self triangle pair를 candidate의 기존 vertex-region으로 분류했다. 새 모델을 생성하지 않았다.

| 자기 교차 영역 | 쌍 수 | 해석·할 일 |
|---|---:|---|
| head–head | 522 | provisional return cohort에 닿는 188쌍과 그렇지 않은 334쌍을 구분해 실제 면을 검사해야 함 |
| head–trunk | 5 | 목/인접 구역의 연결 검사 |
| arm–trunk | 260 | 양측 130쌍. 겨드랑·팔과 몸통의 접합/접촉을 독립 수정해야 함 |
| arm 내부 | 12 | 양측 6쌍. 잔여 arm 구역 검사 |
| groin/leg 관련 | 264 | groin–leg 54, groin 내부63, 좌우 leg117, 각 leg 내부30 |
| 합계 | **1,063** | 이 중 일부를 제외해서 원시 총수를 줄이지 않음 |

이 분류는 현행 region metadata에 따른 영역 분류이며 각각의 생리적 접촉/실제 결함 판정을 대신하지 않는다. 손·발 native 관통과 전신 자기 교차는 서로 다른 문제다. 손발만 고쳐도 나머지 1,063쌍이 자동으로 없어지지 않는다.

## 권고 종료 경로

모든 작업은 기존 **AT10/skin-fit 안의 내부 unit**이다. 새 task 번호나 다음 단계 실행을 만들지 않는다. 같은 자동 대응 규칙의 전신 후보 생성은 잠시 멈추고 아래 순서로 진행한다.

### 1. 전신 결함 지도를 고정

r22와 고정 ZA를 계속 입력으로 사용한다. native 교차, 자기 교차, 과도한 간격, 접합/접선, 실제 없는 점막, 미완 교육 지표를 각각 별도 목록으로 만든다. 얼굴 외피/눈·입의 안쪽 return, 의도된 개구부/접촉은 source face ID로 먼저 판별한다. 외피의 실제 관통을 return으로 바꿔 제외하면 안 된다. 원시 교차 총수와 분류 후 미해결 수를 함께 남긴다.

### 2. 한쪽 손목–손바닥–엄지 연결 구역을 먼저 끝냄

Blender의 기존 원본/고정 native 비교에서 담당 AI가 source 면 묶음과 경계 loop를 직접 작성한다. 손등/손바닥, radial/ulnar wrist, thumb base/web, 각 digit를 실제 original vertex/face와 native facet으로 구분한다. 이 단계의 직접 authoring은 사용자에게 수동 좌표 작업이나 교수 승인을 요구한다는 뜻이 아니다.

source 경계 loop와 native 기준 구조의 순서, 앞뒤/좌우, 공유 vertex, 접선·모양을 확인한 뒤 변형한다. nearest/ray는 확인한 구역 안의 정합 보조로 제한한다. 우선 한 연속 구역의 실제 native/self 교차와 주변 seam까지 해결하고 성공 산출물을 별도 보존한다. 그 전에 같은 잘못된 대응을 양측/전신으로 확대하지 않는다.

### 3. 실제 충돌을 고려하는 국소 변형으로 교체·보완

현재 RBF/ARAP는 초기 자세 이동과 매끄러운 변형 보조로 재사용할 수 있다. source-to-native 대응이 맞는지부터 확인하고, 이동 과정에는 새 관통 방지·기존 관통 깊이 감소/해소·자기 접힘·국소 변형·경계 접합을 함께 제약한다. 이미 관통한 초기값에 단순히 '처음부터 교차0'을 요구해 영구 정지시키는 방식도 피한다.

원본/native는 읽기 전용으로 유지한다. 작성기와 독립 검사기를 분리한다. 전체 mesh scale, 균일 offset, 정상 방향 밀기, source 면 숨김으로 겉모습만 통과시키지 않는다. 현 topology를 우선 사용하고, 부족한 부위의 실제 국소 제작이 필요하면 원본 ID/face-corner UV 계보와 새 derived mapping을 명시하는 별도 recipe revision으로 남긴다.

### 4. 같은 완료 방식으로 다른 구역을 닫음

| 구역 | 필수 산출물·검사 |
|---|---|
| 반대 손·모든 손가락 | 반대쪽 실제 native 주소와 좌우 확인; mirror는 시작 제안에만 사용 |
| 발목·발등·발바닥·heel·MTP·발가락 | 앞뒤 표면과 각 toe 소유 구역, ankle 공통 경계, 주변 tendon/fascia와 간격·교차 |
| 얼굴·귀·목 | helix/concha/lobule/root의 순서 있는 표면 묶음; 눈/입 return과 외피 분리; neck seam |
| 겨드랑·팔–몸통 | 두 구역을 함께 보는 source 경계와 접촉 조건; 현재 arm–trunk260쌍/arm 내부12쌍 재검사 |
| 골반·샅·상부 넙다리 | 양측의 공유 구역으로 정합; inner-thigh/perineal/gluteal 표면과 seam 동시 확인 |
| 잔여 전신 | 머리/목/몸통/어깨/팔꿈치/손발/무릎/천골의 최종 조립 회귀. 큰 부위를 자동 승인하지 않음 |

해당 local unit의 성공과 전체 skin-fit acceptance를 별도 보존한다. 독립 성공 구역을 다음 실패 후보로 덮지 않는다. 모든 실패 구역을 합쳐 새 전신 최종본으로 부르지 않는다.

### 5. skin-fit 산출물을 닫고 skin-runtime으로 전달

아래를 모두 만족한 한 자산을 최종본으로 동결한다.

- 의도하지 않은 외피–native 관통/자기 관통이 해결되고, 의도된 개구부·접촉·미지원 점막은 실제 source 주소와 이유로 별도 기록된다. 원시 교차 총수도 보존한다.
- 부위별 경계/접선/형태와 간격이 실제 화면에서 적합하다. 모든 부위에 같은 3/5mm 간격이나 nearest-distance 임계값을 강요하지 않는다. mm tolerance가 필요하면 모델 QA 기준과 해부학적 의미를 구분해 사전에 고정한다.
- 정면/뒤/좌우 및 얼굴·귀·겨드랑·손발·샅의 actual emitted GLB와 fixed native를 검사하고, 실제 product GLTFLoader 경로의 좌표/노드 transform/normal/UV를 확인한다.
- source/derived vertex·face·UV/helper 계보, frame/unit/pose/hash, 정합 recipe가 일치한다. 통과한 새 최종 recipe만 새 디렉터리에서 한 번 독립 재현한다. 원본 확보/r22의 옛 형식 검사를 다시 조사하지 않는다.
- 배꼽·유두·주름·손톱 등 필요한 교육 지표를 source 관찰/AI 작성으로 구분해 등록한다. 361점 작성은 포함하지 않는다.
- 피부 GLB/manifest/mapping/landmarks/recipe/부위별 QA·지원/미지원 목록/비용/최종 hash가 한 묶음으로 전달된다.

**skin-fit 종료에 피부 버튼이나 경혈 접촉 UI 구현을 끼워 넣을 필요는 없다.** 파일의 geometry·정합·export가 통과하면 skin-fit을 끝낼 수 있다. 같은 제품 장면의 실제 ON/OFF·선택·가림·점 접촉·G1–G8은 다음 skin-runtime에서 별도 통과해야 한다. 현재 진행을 막는 이유는 앱 import0이 아니라 실제 피부 geometry의 미달이다. offline QA로 다음 제품 gate를 대신하지 않는다.

## 비용 전달 조건

현재 한 피부는 626,572 encoded bytes / 26,756 triangles / 625,080 decoded geometry bytes다. overview+기존 교육용 carrier+피부를 모두 더하면 21,482,184bytes로 기존20MiB보다510,664bytes 초과한다.

권고안은 새 피부 모드에서 기존 교육용 carrier mesh와 새 피부의 **중복 상주를 피하는 전달 계약**이다. 기존 carrier 데이터/원본/역사 증거는 보존하고, 새 canonical 피부로 전환되는 때의 점/영역 주소 호환을 다음 runtime 범위에서 검증한다. 주변 native 구조 삭제나 예산 증액으로 해결하지 않는다.

파일 합산만 보면 overview+피부는20,669,088bytes로20MiB보다302,432bytes 작다. 이는 실제 runtime 전송/상주/GPU/FPS 합격의 증거가 아니다. 공존이 필요한 경우 해당 이유와 실제 lazy-load/LOD 비용을 skin-runtime에서 검증해야 한다.

## 실행 경계와 근거

이번 검토에서는 피부 자산·실행 상태·코드를 바꾸지 않았다. 이 문서만 추가했다. 자동 위임/다음 실행/push/배포는 하지 않는다. 다음 구현 요청은 위의 '한쪽 손목–손바닥–엄지 표면 authoring과 충돌 해결'부터 같은 skin-fit 안에서 시작하는 것이 권고다. 손목 성공 전 전신 자동 후보 재생성을 반복하지 않는다.

- [현재 결과](../../evidence/AT10/2026-10-14-skin-fit-r4/summary.json), [실패 ledger](../../evidence/AT10/2026-10-14-skin-fit-r4/attempt-ledger.json)
- [실제 화면 판독](../../evidence/AT10/2026-10-14-skin-fit-r4/visual-review-r35.json), [나머지 실제 주소](../../evidence/AT10/2026-10-14-skin-fit-r4/remaining-probes-r35.json)
- [field 검사](../../evidence/AT10/2026-10-14-skin-fit-r4/field-inspection-r35.json), [self pair 전체](../../evidence/AT10/2026-10-14-skin-fit-r4/candidates/fit-r35-contact-addresses.npz)
- [현재 작성기](../../tools/at10_skin_surface_bands.py), [독립 field 검사기](../../tools/inspect_at10_skin_fields.py)
- [보고서](../../reports/AT10-skin-fit.md), [기존 skin-fit/runtime 계약](PROMPTS-IN-ORDER.md)
