# 실행 공통 계약 — 2026-10-15

이 문서와 START-HERE.md는 사용자의 피부 품질 개선·진행 순서 재설계 요청을 반영한다. 구현 완료나 품질 통과 기록이 아니다. 요청당 AT10 내부 한 unit만 실행한다. 기본 담당 Sol xhigh, C1 데이터 연결·검증 Luna Max. 모델 성능의 보증이 아니라 기존 사용자 역할 분담이다.

## 실행 기준

- AGENTS.md, EXECUTION.featureWorkUnits.AT10.completionExecution, 해당 prompt, 최신 실제 manifest/report를 읽는다. work/NEXT.md 기본 앱 큐가 끝났어도 featurePlans의 AT10은 별도 진행 중이다.
- 최신 F1 f1c7과 F2 f2c3 결과가 옛 preflight 실패를 대체한다. f2Preflight/f3Preflight, r22, 과거 NEXT-F1은 역사다. 입력 hash가 같은 최신 통과 결과를 다시 미승인으로 취급하지 않는다.
- local geometry, appearance, runtime delivery, acupoint location, optional professor review, public redistribution은 별도 판정이다. 부모 AT10 partial, 교수 검토 없음, 공개 배포 held는 독립적인 개발 미리보기·재질 작업의 차단 조건이 아니다.
- 실제 실패는 숨기지 않는다. unit마다 필수 입력과 완료 조건만 선행으로 검사한다. F3/F4는 V1/V2 미통과만으로 차단하지 않는다. V1은 F5/F6 전신 통과를 요구하지 않는다. 최종 제품 연결은 geometry와 appearance 모두 필요하다.
- 어떤 unit을 요청했는데 이미 통과했다면 재실행하지 않고 해당 증거와 다음 프롬프트를 보고한다. 다음 unit은 자동 실행하지 않는다.

## 구현과 품질

- 한 AnatomySceneRoot/renderer/camera를 유지한다. UI 배치·카메라 정책·홈·로딩 개편은 하지 않는다. 피부 표면의 재질/노멀 변경은 이번 허용 범위이며 UI 보류로 차단하지 않는다.
- 원본/OpenSim_Models/T13/사용자 WIP, native, UV/original ID, 역사 evidence를 보존한다. MakeHuman/ZA 원본 조사를 처음부터 반복하지 않는다. 필요한 재질 자산만 실제 파일·UV·권리를 확인한다.
- 완성 기준은 알고리즘명이 아니다. 기존 flow/contact/ARAP/export/checker를 먼저 재사용한다. 실패한 sparse push나 cage의 가중치 변경만 반복하지 않는다. 같은 원인의 두 번째 실패가 확인되면 대응/제약/형상/구현 중 원인을 분류하여 방법을 수정하고 실행한다. 재시도 횟수나 시간만으로 합격시키지 않는다.
- 유한하고 표시 가능한 중간 후보는 DEV 같은 장면에서 검사한다. 그 미리보기가 제품 승인이라는 뜻은 아니다. 최종 품질/비용/정합 검사는 별도다. non-finite/잘못된 index는 미리보기에서도 거부한다.
- 색상·roughness 변경만으로 질감 완료를 선언하지 않는다. UV 경계 음영, 실제 실루엣, 피부색/손발톱, 거칠기, 미세 노멀, 경혈 가독성을 함께 본다. 피부 투명화나 카메라를 멀리 옮겨 결함을 숨기지 않는다.
- 노멀·재질만 바꾸면 canonical position/index/anchor 주소를 유지한다. UV 경계를 지우는 무조건 weld 금지. 실루엣/정점을 바꾸면 versioned derived mapping과 해당 영향 범위 geometry/anchor 재검증이 필요하다. 기존 국소 합격은 옛 자산에 보존하되 새 자산에 자동 상속하지 않는다.
- 정확한 fascia 예외만 보존한다: 오른쪽991, 별도 실제 왼쪽994. raw와 유효 참조 검사를 구분하며 다른 뼈·힘줄을 숨기거나 삭제해 맞추지 않는다.
- 텍스처는 GLB에 무조건 허용하거나 로더의 검증을 삭제하지 말고, 별도 명시적 hash/UV/layout/색공간/bytes/dimensions manifest 또는 검증된 embedded 경로를 설계한다. 단일 공통 재질 경로를 사용한다. browser에 Blender/생성기를 넣지 않는다.
- encoded bytes와 decoded GPU texture/mipmap 비용을 구분한다. 초기 2K 색/1K 보조 맵은 출발 후보이지 고정 합격 수치가 아니다. 실제 detail 화면과 메모리로 결정한다. 기존 예산은 기록 없이 올리지 않는다. 예산 부족 시 공유·지연 로딩·압축/해상도를 먼저 조정하고 필수 구조 삭제 금지.

## 반복을 줄이는 판정과 인계

결과에는 (1) 이번에 눈으로 달라진 것 (2) 실제 통과/실패 (3) 실패 주소/재현/영향 범위 (4) 다음 수정 행동 (5) 독립적으로 진행 가능한 unit을 남긴다. 단순 no_new_evidence/approval_pending 재보고로 끝내지 않는다. 해결 불가능한 외부 입력은 정확히 명시하고 가능한 작업은 마친다. 어려운 geometry 성공이나 추가 수정이 전혀 없을 것을 보장할 수는 없다.

기본 직렬 실행. 같은 checkout에서 asset/runtime/EXECUTION을 두 대화가 함께 수정하지 않는다. 별도 병렬 조사는 사용자 요청이 있을 때만 소유 폴더로 분리하고 단일 통합자가 반영한다. 오래된 미커밋 파일 존재만으로 활성 중복 작업이라고 단정하지 말고 실제 실행 상태와 소유 기록을 확인한다. 이번 계획은 다른 대화에 메시지를 보내거나 task를 자동 실행하지 않는다.

## 결과·Git

시작 HEAD/status/hash와 소유 파일을 기록한다. 변경 영향에 맞는 자동 검사와 실제 앱 전후 캡처, console·선택/레이어 회귀를 남긴다. 같은 시점/배율/조명 비교와 무채색 형상 보기로 질감이 형상 결함을 숨기지 않는지 확인한다. 최종 R2는 390/1024/1440px 실앱이다.

work/evidence/AT10/<날짜>-<unit>/과 report에 실제 자산 hash, 전후 화면, bytes/triangles/GPU/프레임 측정 조건, remaining을 남긴다. 실패 후보 원본 보존, runtime 배포 목록에는 최종 선택 파일만 포함한다.

종료 시 최신 EXECUTION을 다시 읽고 해당 unit 결과와 completionExecution의 nextUnit/nextPrompt만 병합한다. result/역사 acceptance·다른 task 기록을 덮지 않는다. 다음 actionable unit은 의존성 기준으로 지정하되 자동 실행하지 않는다. 해당 단계 미완을 pass로 바꾸지 않는다. completionExecution의 status는 계획 작성만으로 complete가 되지 않는다.

sync_execution.py 및 --check 후 소유 변경만 선별 로컬 커밋한다. 혼합 파일은 소유 hunk만 포함하거나 제외 이유/인계 patch를 남긴다. 커밋 hash·포함/제외·잔여 변경과 다음 prompt를 보고하고 멈춘다. push/배포/진단/치료/침 시뮬레이션은 하지 않는다. 취혈자세는 361혈과 영역·내용 이후 AT30/31이다.
