# T78 개정 — 전신 모형 확보 우선, 부위 복수 선택, 실제 광배근 구현 경로

2026-09-28 · 사용자 요청 반영 · Astra 설계 / 후속 구현 Luna Max. 이 문서는 계획이며 모형·UI 구현 완료를 뜻하지 않는다. 이번 변경 범위에서 19/20 및 이전 프롬프트보다 우선한다. T73–77/T92–94 결과는 수정하지 않는다.

## 지금 확인된 문제

- **팔의 왼쪽 견갑골은 이미 있다.** FJ3279는 shoulder-scapular/thorax, 오른쪽 FJ3384는 shoulder-scapular/upper-limb에 속한다. 팔 필터가 왼쪽을 제외한다. 원자료 분류를 덮어쓰지 않고 별도의 제품 맥락 소속으로 양측을 포함한다. 쇄골 FJ3237/FJ3362도 함께 대조한다.
- **부위 선택은 현재 단일값이다.** 목과 머리를 함께 켜는 사용자 요구는 아직 구현되지 않았다. T95로 변경한다.
- **이두근·삼두근의 양측 갈래 10개는 공식 source 후보가 있지만 현재 장면에 없다.** T79에서 실제 취득·같은 장면 통합부터 한다. 데이터 카드 입력을 먼저 끝낼 필요는 없다.
- **광배근은 여전히 missing.** T94의 `no_exact_source_found`는 유효한 역사 결과다. 이름 검색 반복을 중단하고 T97에서 실제 공식 archive 내부 객체를 검사한다. TA2 2231은 해부학 용어 ID이지 mesh ID가 아니다.
- 근육 기관 root만 보면 323/323 표면이 확보되어 있으나 갈래/부분 root를 포함하면 53개 근육 표면이 미통합이다. 뼈는 17개 추가 표면이 있다. 대표 예는 대퇴이두근 갈래, 광근들, 왼쪽 비복근 갈래, 짧은엄지굽힘근·엄지모음근 갈래, 원회내근·척측수근굴근 갈래, 경장근·후두 근육 부분이다. 정확한 목록은 `work/evidence/T78/source-elements.json`과 `inventory-summary.json`이다. 이미 있는 whole-muscle과 겹치는 part는 추가 표시 전에 실제 중복 여부를 확인해야 한다.

## 전체 목록과 분모의 한계

공식 TA2 Viewer v2.07 명칭 데이터에서 근육계/골격계와 이소골 관련 **2422행**을 읽기 전용 텍스트 추출했다. source URL·원본 SHA256·선택 snapshot을 보존했다. 그중 자동 분류한 구조 후보 **556개**는 named muscle 245, serial muscle family 47, muscle group 45, muscle part 96, bone/series 123이다. 이는 **556개 근육이라는 뜻이 아니며 확정된 개별근 분모도 아니다.** supporting 용어도 ledger에 남겨 제외 누락을 재검사할 수 있다.

TA2 명칭과 BodyParts3D 명칭의 정규화 일치는 대응 **후보**일 뿐이다. 골격근군/부분/반복근/변이와 뼈·뼈군·표지의 의미 검증, 양측 인스턴스 확정이 남아 T96을 배정했다. T78 상태는 `partial_target_semantics_pending`으로 기록한다. 목록·queue 검증은 통과해도 전신 개별근 분모는 계속 null이다. T96에서 정확한 포함 규칙/대응표를 동결하고 변경된 후보를 후속 batch에 재배정한다. 누락 항목을 지워서 분모를 줄이는 것은 금지한다.

한편 **source-element 분모는 판본 한정 613개로 동결**했다. 근육기관+갈래/부분 root와 기존 승인된 source extension을 합친 근육 표면407개, 뼈 root+기존 context extension206개다. 543개는 현재 장면, 70개는 미통합이다. 이 분모는 BodyParts3D R4와 기존 source extension의 기술적 표면 집합이며 전체 인간 해부학의 분모가 아니다. 광배근처럼 해당 집합 밖인 해부학 target은 별도 누락으로 남는다.

각 target의 geometry/side/frame/region/binding/세 이름/기시정지/function/animation을 독립 필드로 둔다. 아직 교차 대조하지 못한 내용은 not_reconciled이며 absent나 complete로 단정하지 않는다. 기존 10 binding node와 content를 새 556개 target에 자동 승격하지 않는다. source states는 실제 manifest 값을 그대로 보존한다.

## 사용자 경험 계약 — T95

1. 12개 부위 버튼은 복수 선택 toggle이다. 활성 부위의 합집합만 보인다. 같은 부위를 다시 누르면 해제한다. 0개면 전신이다. `전체`는 선택 집합을 비운다.
2. 부위 소속은 many-to-many이고 node는 한 번만 존재한다. 근육/뼈 레이어를 사용자가 끈 상태, 개별 held/hidden 정책은 지역 선택보다 우선한다. `전체`를 누르는 것만으로 보류 구조나 꺼 둔 레이어를 되살리지 않는다.
3. URL은 기존 `region=leg` 호환, 다중 선택은 반복 `region` 값으로 저장한다. 새로고침/뒤로가기/모바일/키보드 모두 같은 상태가 된다.
4. 필터로 선택 근육이 숨겨지면 카드 선택을 해제한다. 검색에서 범위 밖 구조를 선택하면 해당 부위를 합집합에 추가하되 이전 부위는 유지한다. 직접 URL의 구조 선택과 부위 필터를 검증한다.
5. 팔 보기의 양측 견갑골·쇄골은 제품 맥락 뼈다. source taxonomy와 분리해 같은 장면에서 표시한다. 요추/엉치뼈도 기존 local display 허용 상태를 보존한다. 사용자에게 보완자산 버튼을 다시 만들지 않는다.
6. 한 AnatomySceneRoot/renderer/camera, 카메라 연속성, 미니멀 UI 유지. 로딩 로고·인체 그림·슬로건 복구 금지.

## 실행 순서와 경제적 분할

| 순서 | task | 실제 산출물 |
|---|---|---|
| 1 | T95 | 복수 선택 + 왼쪽 견갑골 맥락 수정 한 기능 묶음 |
| 2 | T79 | 이두근·삼두근 10개 exact surface 취득·같은 장면 통합 |
| 3 | T97 | 광배근 공식 archive 실제 객체 inventory/추출 |
| 4 | T101–T107 | 남은 근육43개+뼈17개를 최대10 source씩 취득·통합 |
| 5 | T98 → T99 → T100 | 광배근 객체 권리/frame → 정합 → 단일 장면 통합 |
| 6 | T96 | 전체 목표의 의미·반복근/부분/변이·뼈 분모 확정 |
| 7 | T108–T109 | 기존 hidden12개 항목별 실제 원인 재검증 |
| 8 | T110–T165 | 전체556후보를 최대10개씩 exact identity/세 이름/선택에 연결. 미확보 target 추가 취득은 제한 범위, 다른 모델 정합은 별도 번호로 분리 |
| 9 | T80 → T58 | 전체 구조 gate 및 Astra 그래픽 재검증 |
| 10 | T81 전체 batch → T82 → T83 전체 batch → T84 | 기시정지 전체 → 작용 전체. 기존 프롬프트 유지 |
| 11 | T35 및 기존 동일모형 motion 단계 → T85 | 같은 화면·같은 근육 표면에서 작용별 실제 움직임 |
| 12 | T61/T86 이후 | 신경 근거 → 신경3D/지배근 → 기능이상 설명. 기존 gate 유지 |

72개 계획 항목 중 56개는 새로운 앱 기능을 각각 만드는 작업이 아니라 **기존 공통 파이프라인으로 최대10 target 데이터 검증·연결을 반복하는 batch**다. 모형 확보는 앞부분에서 먼저 눈에 보이는 결과를 만든다. 정합/scene contract 재설계를 매 근육마다 반복하지 않고 검증된 모델 변환·캐시·도구를 재사용한다. 성격이 다른 권리/정합/수백 개 콘텐츠를 한 task에 합치지 않는다. 번호를 순서로 해석하지 말고 queue를 따른다.

T97의 객체 부재나 T98 권리 보류는 독립 R4 표면 취득/T96을 막지 않는다. 다만 광배근의 의존 단계와 T80의 전체 완성 gate는 막는다. 보고서에서 다음 실행 가능한 task를 명시하며 자동 다음 실행은 하지 않는다. 필요한 추가 대체 객체는 실제 파일 하나를 정해 새 bounded ID로 배정한다. 무기한 이름검색 task는 만들지 않는다.

## 광배근 구현의 네 gate

- **T97 실제 객체:** 고정 공식 commit의 한 archive, 전송/해제/파일 수 상한, 안전한 오프라인 검사, object/data-block/path/geometry hash, 실제 표면 preview. 이름은 탐색용이며 객체 확인을 대체하지 못한다.
- **T98 사용·frame:** ancestry와 개별 권리 적용, local/derivation/public 권리 분리, 단위·축·side/part·parent transform·rest pose. 불명확한 것은 held.
- **T99 정합:** T50 model landmark, fitting 전에 정의한 허용 오차, fitting과 별도의 평가 지점, 실제 잔차와 before/after. min-max 크기 맞추기나 임의 반사복제 금지. 동일 좌표계도 증명한다.
- **T100 통합:** 기존 같은 scene의 신규 revision, layer/filter/양측/후면/중복표면 확인. exact identity 증거가 있으면 canonical 연결, 없으면 source-only. 애니메이션은 여기서 만들지 않는다.

## OpenSim 사용 범위

읽기 전용 34개 `.osim` 중25개 XML을 분석했고9개 legacy XML은 현재 parser에서 실패해 unknown으로 남겼다. 분석된22개 모델에 muscle actuator/GeometryPath가 있으나 분석된 근육 요소 안의 Mesh 연결은0개였다. 이것은 모든 파일에 어떤 근육 surface도 없다는 증명이 아니다. 실제로 확인한 경로와 해부학적 부피 표면은 다른 자산이다. OpenSim은 이후 작용/운동계와 비교할 수 있으나 그것만 읽어서 전신 고품질 표면이 생긴다고 계획하지 않는다.

원자료 HEAD/hash와 parse 오류는 `opensim-readonly-inventory.json`에 기록했다. 원본을 수정하거나 in-place 변환하지 않았다. [OpenSim 모델 구성 설명](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53088700), [TA2 Viewer](https://ta2viewer.openanatomy.org/).

## 실행 문서와 공통 기준

- `work/evidence/T78/PROMPTS-IN-ORDER.md`: 순서대로 모든 작업 명세 링크.
- `work/evidence/T78/execution-queue.json`: exact IDs, scope, dependencies, 개별 전체 프롬프트.
- `work/tasks/T95.md`, `T79.md`, `T96–T165.md`: 한 ID씩 실행할 명세.
- `work/evidence/T78/NEXT-T95.md`: 바로 다음 붙여 넣기.
- 향후 모든 geometry/UI task는 해당 실제 화면, side/frame/rights/hold, 중복node 및 카메라 연속성 검증이 필요하다. 개발자 내부 상태를 학생 UI에 늘어놓지 않는다.
- 필수 미달은 partial/blocked. 계획/해부학적 명칭/테스트 통과를 전신 시각 완성으로 부르지 않는다. 로컬 소유 변경 커밋만, push/deploy/다음 자동실행 금지.
