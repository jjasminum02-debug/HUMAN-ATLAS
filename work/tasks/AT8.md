# AT8 — 대장경·삼초경 43혈 위치·경로 연결

## 2026-10-12 구현 정정 — 공통 package 연결 먼저

담당 **Sol xhigh**. [통합 계획](../plans/mv2-at-integrated-2026-10-12/START-HERE.md)과 [최신 프롬프트](../plans/mv2-at-integrated-2026-10-12/PROMPTS-IN-ORDER.md)의 AT8을 사용한다. 기존 AT 순서와 43혈 범위는 유지한다.

현재 `learningPackage.ts`는 LU/11개/22 instance와 `lung-r7.json`에 고정돼 있고 `AcupointReview.tsx`도 LU만 실제 로딩한다. 이번 task에서 이를 공통 registry·채널 package·code+side·구간 경로로 일반화한 뒤 LI/TE를 연결한다. 부분 ST/BL/GB package 합성, 정중선 1 instance 및 중복/누락 검증을 공통 계약에 포함한다. 정중 기술 fixture는 실제 CV/GV 위치로 내보내지 않는다. LU의 기존 내용·22점·좌우·취소·복귀 회귀를 보존한다.

완료에는 실제 LI/TE 양측 입력·표시 판정, 다경맥 전환/전체점, 필요한 carrier만 로딩·공유·해제하는 경로 검증이 필요하다. 공통화만 하고 43혈 범위를 완료 처리하지 않는다. 카메라에 전달할 기존 형식의 실제 국소 구조 context는 데이터로 추가하되 카메라 정책·패널 디자인을 바꾸지 않는다. 아래 과거 UI 문구보다 사용자 최신 UI 보류 지시가 우선한다.

2026-10-11 작업 단위 정정. 상태는 EXECUTION의 해당 record에서 읽는다. 이 명세 자체는 구현 완료의 증거가 아니다.
선행: AT5, AT6, AT7, AT22. 실행 순서는 번호순이 아니라 [현재 계획](../plans/acupoint-at-2026-10-11/START-HERE.md)과 EXECUTION.featurePlans.acupoint-at-361.order를 따른다.

## 읽을 자료

AGENTS.md, work/EXECUTION.json, work/NEXT.md, design/2026-09-25-muscle-atlas/30-AT-361-POINTS-AND-TERRITORIES.md, design/2026-09-25-muscle-atlas/31-AT-EXPERIENCE-AND-DELIVERY-CONTRACT.md, 선행 AT report/evidence.
AC1·AC2 보고서와 schema/overlay/CameraSessions/tour는 최초 또는 관련 변경 때 재사용 근거를 확인한다. 같은 자료를 매번 재조사하지 않는다.

## 수행 범위

공통 compiler/자료 대조/renderer만 사용해 지정 코드의 양측 또는 정중 위치와 체표 학습 경로를 연결한다. 집중 점검: 손끝·팔꿈치·어깨·얼굴 경계. 공통 카메라·UI를 경맥별로 복제하지 않는다.

대상 코드: LI1, LI2, LI3, LI4, LI5, LI6, LI7, LI8, LI9, LI10, LI11, LI12, LI13, LI14, LI15, LI16, LI17, LI18, LI19, LI20, TE1, TE2, TE3, TE4, TE5, TE6, TE7, TE8, TE9, TE10, TE11, TE12, TE13, TE14, TE15, TE16, TE17, TE18, TE19, TE20, TE21, TE22, TE23.

## 완료 기준

43개 개념의 모든 instance에 위치 규칙·carrier hash·판정이 있다. 실제 점 선택/가림/순서와 구간 화면을 확인하고 분지 jump는 직선으로 관통시키지 않는다. 전체 입력 처리와 예외 수를 함께 보고한다.

## 작업 경계와 인수 검사

- 산출물: 배정 코드의 위치 규칙·side instance·경로 data package 하나. 공통 compiler로 일괄 생성 후 해부 지표 예외만 보정한다.
- 검사: 각 코드의 입력/표시/미해결을 전수 대조한다. 양측 또는 정중, 시작·끝·모든 예외의 실제 화면을 검사하고 전체 경맥 framing을 확인한다.
- 경계: 전용 loader/UI/renderer 추가 금지. 각 점을 독립 mesh나 컴포넌트로 수작업 복제하지 않는다. 코드 순서를 신체를 관통하는 자동 직선으로 연결하지 않는다.

## 실행·검증·기록

- 종료는 산출물과 완료 기준으로 판단한다. 경과 시간을 이유로 중단하거나 검증을 생략하지 않는다. 정정 전 시간 checkpoint 지시는 폐기한다.
- 범위의 완료까지 진행한다. 실제 입력 부재/재현 결함으로 진행이 불가능한 경우에만 남은 unit·시도한 해결·필요 입력을 구체적으로 남긴다. 무한 재검색이나 자동 task 증식은 하지 않는다.
- 31 설계의 공통 구현/화면 계약 중 이 task에 해당하는 항목만 구현·검증한다. AT2에 후속 UI/전신 제작을 추가하지 않는다.
- source/권리/교수 검토/교육용 위치 등급을 분리한다. 과거 미승인만으로 독립 작업을 막지 않으며 unresolved 위치를 자동 승인하지 않는다.
- 단일 scene/root/renderer/camera와 사용자 layer-off/선택을 보존한다. 관찰 시점 메뉴, 로딩 로고·인체 그림·슬로건을 되살리지 않는다. 기존 보기옵션을 재배치하지 않는다.
- 원본/OpenSim_Models/T13 drafts/사용자 WIP와 역사 evidence를 보존한다. 개발 evidence·private 교재·source cache는 learner bundle에 넣지 않는다.
- 변경에 관련된 자동 검사와 실제 화면을 확인한다. 데이터 처리 성공과 실제 표시/시각 검증 수를 구분한다. 전체 역사 suite를 매 task 반복하지 않는다.
- 최신 EXECUTION을 다시 읽고 이 AT record와 feature plan의 nextUnit만 갱신한다. 다음 ID는 order/선행에서 구하며 번호에 1을 더하지 않는다. 다른 실행자의 변경이나 숫자 T/AC 기록을 덮지 않는다. sync_execution.py 및 --check를 실행한다.
- work/reports/AT8.md, work/evidence/AT8/에 실제 산출물·검증·미완·다음 ID/프롬프트를 남긴다. 소유 변경만 선별 로컬 commit하고 hash/포함·제외·잔여 변경을 보고한다. 경과 시간 보고는 완료 조건이 아니다.
- 다음 task 자동 실행·push·배포·진단·치료·침 시뮬레이션 금지.

## 붙여 넣을 프롬프트

```text
HUMAN ATLAS에서 AT8만 수행해라.
AGENTS.md, 최신 work/EXECUTION.json, work/tasks/AT8.md,
design/2026-09-25-muscle-atlas/30-AT-361-POINTS-AND-TERRITORIES.md,
design/2026-09-25-muscle-atlas/31-AT-EXPERIENCE-AND-DELIVERY-CONTRACT.md 및 지정 선행 실제 evidence를 읽어라.
범위: 공통 compiler/자료 대조/renderer만 사용해 지정 코드의 양측 또는 정중 위치와 체표 학습 경로를 연결한다. 집중 점검: 손끝·팔꿈치·어깨·얼굴 경계. 공통 카메라·UI를 경맥별로 복제하지 않는다.
필수 결과: 43개 개념의 모든 instance에 위치 규칙·carrier hash·판정이 있다. 실제 점 선택/가림/순서와 구간 화면을 확인하고 분지 jump는 직선으로 관통시키지 않는다. 전체 입력 처리와 예외 수를 함께 보고한다.
명세의 작업 경계와 인수 검사를 완료해라. 경과 시간에 따른 중단 지시는 폐기됐으며 산출물과 합격 기준으로 종료해라.
기존 AC1/AC2와 공통 compiler/overlay/CameraSessions를 재사용하고 task별 구현을 복제하지 마라.
같은 장면·사용자 조작·원본/OpenSim_Models/T13/기존 WIP를 보존해라.
31 설계 중 이번 범위의 자연스러운 그래픽·카메라·학습 UI 기준을 실제 화면에서 확인해라.
관찰 시점 메뉴를 복구하거나 기존 보기옵션을 다시 디자인하지 마라.
관련 검증·report/evidence를 남기고 최신 EXECUTION의 이 AT record와 feature plan 다음 ID만 갱신해라.
sync_execution.py 및 --check 후 소유 변경만 로컬 커밋해라. 실제 미달은 정확히 보고해라.
계획상 다음은 AT9. 최신 order/선행과 대조하고 자동 실행하지 마라.
push·배포·진단·치료·침 시뮬레이션 금지.
```
