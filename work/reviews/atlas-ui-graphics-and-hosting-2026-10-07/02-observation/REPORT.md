# 02 — 관찰 조작·카메라 완료

현재 지원 모형의 관찰 기능은 **passed / local_supported_observation_ready**입니다. 기존 task 상태는 수정하지 않았습니다. 전체 콘텐츠는 계속 partial이며 새 모형·clip·부착점·신경 관계·검토 승인을 추가하지 않았습니다.

## 구현한 동작

- ‘관찰 시점’ 메뉴의 앞·뒤·왼쪽·오른쪽은 실제 변환 계약의 `HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR`를 사용합니다. 해당 frame이 없는 자료에는 방향 버튼을 활성화하지 않습니다. target·높이·거리·zoom을 유지하고 560ms easing으로 같은 camera를 회전합니다. 반대편 전환도 모형을 통과하지 않습니다.
- 맞춤은 공통 API에서 현재 카메라 방향으로 bounds의 8개 모서리를 계산합니다. 연속 시점 클릭은 진행 중 맞춤의 최종 목적지를 이어받습니다. 드래그·방향키는 전환을 취소합니다. reduced-motion은 즉시 전환하며 첫 등장 12도/1.4초 정책을 보존합니다.
- 집중 관찰은 선택 구조와 현재 자료의 같은쪽/중앙 주변 구조 및 기존 부착 뼈·신경 관련 근육을 포함합니다. 주변 근육을 옅게 처리하지만 뼈와 검증된 신경 강조는 유지합니다. 동작 중에는 기존 package의 동반 구조와 실제 움직이는 geometry bounds를 사용합니다.
- 집중 관찰은 사용자 hidden/translucent/layer와 별개입니다. 종료 또는 구조·부위·홈 변경 시 이전 camera를 복원합니다. 사용자 설정은 그대로 유지합니다. layer-off 상태에서도 관찰을 끝낼 수 있습니다. ‘선택 구조 숨기기 / 선택 다시 표시’는 작은 관찰 메뉴 안에 있으며 상시 전체보기·복원 버튼은 추가하지 않았습니다.
- 노트북의 기존 왼쪽 탐색을 유지했습니다. 600–1100px에는 왼쪽 ‘부위 탐색’ rail을 항상 표시하고 250px 서랍을 펼칩니다. 950px 이하에서는 서랍이 주변 영역 위에 열려 camera 영역이 0으로 줄지 않습니다. 검색/선택/설명 접기를 기존 흐름으로 유지하며 휴대폰은 기존 상단 탐색 진입점을 사용합니다.

## 실제 검증

[검증 JSON](validation.json), [개발 UI 원장](browser-validation.json), [고정 production UI](production-browser-validation.json), [PNG 치수·hash](screenshots.json).

- 외복사근 숨김 → 내복사근 선택 → 집중 관찰: 숨긴 외복사근이 다시 나타나지 않음.
- 앞/뒤/좌/우 실제 시점과 camera 좌표 확인; 드래그 취소; 집중 중 반투명 설정 → 다른 근육 선택: 이전 camera와 사용자 반투명이 복원됨.
- 대퇴직근의 기존 무릎 폄 시범: 동반 **71개 표면**을 유지하며 집중/맞춤/방향 전환, scrub, 재클릭 복원, 근육 layer-off를 확인함. 이 수는 새 작용/새 자산 수가 아님.
- 긴노쪽손목폄근의 기존 **손목 굽힘 자세 관찰**: 동반 **37개 표면**, 손·손목·부착 뼈 문맥과 정적 신경의 비지원 운동 pose 숨김 정책을 유지함. 이를 선택 근육의 실제 작용으로 승격하지 않음.
- 집중 관찰 → 부착 뼈 → 뒤로: 임시 집중 상태를 자동으로 다시 켜지 않음. 마지막 수리 근거는 [개발 history 검증](history-fix-validation.json)과 [최종 고정 production 검증](production-history-fix-validation.json)에 있음. 이전 3폭 레이아웃/그래픽 근거는 CSS/geometry가 같은 입력이므로 재사용하고, 영향받은 history 흐름만 추가 확인함.
- 정중신경 → 관련 근육 → 뒤/앞; 신경 집중 관찰에서 기존 파란 관련 근육 강조 유지.
- 왼쪽 탐색 열기/닫기, 어깨·어깨뼈 + 종아리 복수 선택, 768px 서랍의 유효 canvas 확인.
- 실제 **1440×900 / 1024×768 / 390×844**, 추가 **768×1024** 검사. 단일 canvas, 버튼/document overflow 0, console error/warning 0. 고정 production 빌드에서 세 필수 폭을 별도 확인함. 마지막 history 상태 수리 뒤에는 CSS/geometry 영향이 없는 세 폭 근거를 재사용하고, 최종 snapshot의 해당 흐름을 실제 1280×720에서 추가 확인함. 실제 아이폰/아이패드 검증은 아님.
- 최종 resize는 같은 root를 유지함. 개발 HMR로 코드가 바뀐 시점은 별도 root로 기록했으며 지속성 합격으로 사용하지 않음.
- 정지 관찰 구간 renderedFrames는 **1461 → 1461**: 새로운 render loop나 idle render를 추가하지 않음.

관련 계약 **32/32**, typecheck, production/local build 및 generated freshness, execution projection check 통과. 실제 UI에서 발견한 맞춤 중간 종료, 선택 변경 복원 경합, 신경 강조 우선순위, 메뉴의 왼쪽 이탈을 수리한 뒤 영향 부분을 재검증했습니다. 마지막 빌드에는 이 수리가 포함됩니다. 큰 JS chunk 경고는 남아 있으며 예산은 변경하지 않았습니다.

## 치수와 표시 비용

| 실제 화면 | canvas / 상태 |
|---|---|
| 1440×900 | 834×619.5, 설명 열림·관찰 메뉴 닫힘 |
| 1440×900 | 834×603.5, 관찰 메뉴 열림 |
| 1024×768 | 624×471.5, 왼쪽 rail·설명 열림 |
| 1024×768 | 366×471.5, 왼쪽 서랍·설명 열림 |
| 768×1024 | 368×727.5, 서랍·설명 열림; canvas가 사라지지 않음 |
| 390×844 | 390×300.8, 설명 열림·관찰 메뉴 닫힘 |

Stage 01의 1024px 설명 열림 canvas는 684px 폭이었습니다. 이번에는 탐색 진입점을 왼쪽에 계속 노출하기 위해 60px를 예약합니다. 선택된 내복사근의 집중 관찰은 기존 전신 672개 표시에서 주변 문맥 **17개**로 좁혀 관찰했고, 해제 시 기존 표시 집합으로 돌아옵니다. 구조를 삭제하거나 원본 geometry를 줄인 것이 아닙니다. GPU/VRAM/전체 프로세스 메모리는 측정하지 않았습니다.

## 보존·근거 재사용

입력/출력 SHA는 validation과 baseline에 있습니다. 이전 고정 패키지와 새 패키지의 **94개 non-app URI/bytes/SHA가 동일**합니다. 원본/source-cache/OpenSim_Models/T13에 쓰지 않았습니다. 542/563/12와 기존 HA130·역사163 및 source-only/local selection/권리 held/humanReview not_performed를 유지합니다. EXECUTION/product-acceptance 파일 hash는 시작과 같습니다.

동일 source/geometry/action QC 및 stage01의 관련 기존 레이아웃 근거는 영향 분석 후 재사용했습니다. 변경한 관찰/정책/탐색 흐름만 추가 검사했습니다. 소스·원장 전체 검색, 전수 PNG, 전체 suite를 반복하지 않았습니다.

고정 로컬 패키지: `local-20261007143727068-bf4218bb`, manifest SHA `883c66d07ed18e11ed8c1025b76e7bf7e72db86d9dde375cc05defd0026633bd`. 실제 보존 WIP를 포함한 snapshot이며 commit만으로 전 모형 자산을 재현한다고 주장하지 않습니다. 99 public file은 로컬 패키지 내 파일 수이며 외부 배포하지 않았습니다.

## 남은 범위·인계

현재 관찰 범위의 제품 blocker는 없습니다. 기존 미확보 anatomy/동작/신경 pose/정확한 부착점과 범위 밖 engineering backlog는 별도 유지합니다. 새로운 material/lighting이나 clip 제작은 하지 않았습니다.

다음은 `work/plans/atlas-ui-graphics-and-hosting-2026-10-07/03-materials-and-lighting.txt`입니다. 자동 실행하지 않습니다. 카메라 프리셋/집중 관찰과 신경 관련 근육의 기존 강조 우선순위를 보존하고, 동일 source 자산 QA를 다시 만들지 않아도 됩니다.
