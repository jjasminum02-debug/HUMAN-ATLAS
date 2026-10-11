# AT6 — 폐경 11혈 양측 위치 보완·학습 화면 연결

2026-10-11 작업 단위 정정. 상태는 EXECUTION의 해당 record에서 읽는다. 이 명세 자체는 구현 완료의 증거가 아니다.
선행: AT5. 실행 순서는 번호순이 아니라 [현재 계획](../plans/acupoint-at-2026-10-11/START-HERE.md)과 EXECUTION.featurePlans.acupoint-at-361.order를 따른다.

## 2026-10-11 AT1–6 검토 반영

실제 모델 landmark annotation과 필요한 국소 carrier 보완을 작성해 기존 compiler에서 learner 점까지 연결한다. 자료 부재 목록만 반복하지 않는다. 교육용 모형 지표와 실제 피부/취혈 정확성을 구분하며 첫 실제 위치 연결 후 양측 22개로 확장한다.
상세 구현·검증 기준: [32 설계](../../design/2026-09-25-muscle-atlas/32-AT6-PLACEMENT-CONTEXT-CAMERA-AND-MOTION-QA.md). 역사 완료 기록과 AT6 partial 판정을 이번 명세 수정으로 승격하지 않는다.

## 읽을 자료

AGENTS.md, work/EXECUTION.json, work/NEXT.md, design/2026-09-25-muscle-atlas/30-AT-361-POINTS-AND-TERRITORIES.md, design/2026-09-25-muscle-atlas/31-AT-EXPERIENCE-AND-DELIVERY-CONTRACT.md, 선행 AT report/evidence.
AC1·AC2 보고서와 schema/overlay/CameraSessions/tour는 최초 또는 관련 변경 때 재사용 근거를 확인한다. 같은 자료를 매번 재조사하지 않는다.

## 수행 범위

기존 AC2의 양측 22점 제안을 AT3/4/5 carrier·규칙에 연결해 고친다. DEV review만 있는 진입과 실제 learner projection을 분리하여 확인된 위치를 기존 카드/overlay로 연결한다.

대상 코드: LU1, LU2, LU3, LU4, LU5, LU6, LU7, LU8, LU9, LU10, LU11.

## 완료 기준

LU1–11 11개 개념의 양측 선택·이름·기본 위치가 실제 모델 위에서 동작한다. 정밀 위치와 교육용 개략 표현 수를 따로 남기고 미확정 점은 완료로 세지 않는다.

## 작업 경계와 인수 검사

- 산출물: 기존 LU 22개 proposal을 실제 carrier와 연결하고 기존 카드에 learner 진입을 추가한다.
- 검사: 경혈 진입→폐경→오른쪽/왼쪽→LU1·LU9·LU11 선택을 같은 모델에서 확인. 선택 점·카드·현재 side가 일치한다.
- 경계: 여기서는 폐경 위치/카드 연결만 완성한다. 공통 탐색·카메라 조율은 AT7, 색 영역은 AT21에서 한다.

## 실행·검증·기록

- 종료는 산출물과 완료 기준으로 판단한다. 경과 시간을 이유로 중단하거나 검증을 생략하지 않는다. 정정 전 시간 checkpoint 지시는 폐기한다.
- 범위의 완료까지 진행한다. 실제 입력 부재/재현 결함으로 진행이 불가능한 경우에만 남은 unit·시도한 해결·필요 입력을 구체적으로 남긴다. 무한 재검색이나 자동 task 증식은 하지 않는다.
- 31 설계의 공통 구현/화면 계약 중 이 task에 해당하는 항목만 구현·검증한다. AT2에 후속 UI/전신 제작을 추가하지 않는다.
- source/권리/교수 검토/교육용 위치 등급을 분리한다. 과거 미승인만으로 독립 작업을 막지 않으며 unresolved 위치를 자동 승인하지 않는다.
- 단일 scene/root/renderer/camera와 사용자 layer-off/선택을 보존한다. 관찰 시점 메뉴, 로딩 로고·인체 그림·슬로건을 되살리지 않는다. 기존 보기옵션을 재배치하지 않는다.
- 원본/OpenSim_Models/T13 drafts/사용자 WIP와 역사 evidence를 보존한다. 개발 evidence·private 교재·source cache는 learner bundle에 넣지 않는다.
- 변경에 관련된 자동 검사와 실제 화면을 확인한다. 데이터 처리 성공과 실제 표시/시각 검증 수를 구분한다. 전체 역사 suite를 매 task 반복하지 않는다.
- 최신 EXECUTION을 다시 읽고 이 AT record와 feature plan의 nextUnit만 갱신한다. 다음 ID는 order/선행에서 구하며 번호에 1을 더하지 않는다. 다른 실행자의 변경이나 숫자 T/AC 기록을 덮지 않는다. sync_execution.py 및 --check를 실행한다.
- work/reports/AT6.md, work/evidence/AT6/에 실제 산출물·검증·미완·다음 ID/프롬프트를 남긴다. 소유 변경만 선별 로컬 commit하고 hash/포함·제외·잔여 변경을 보고한다. 경과 시간 보고는 완료 조건이 아니다.
- 다음 task 자동 실행·push·배포·진단·치료·침 시뮬레이션 금지.

## 붙여 넣을 프롬프트

```text
HUMAN ATLAS에서 AT6만 수행해라.
design/2026-09-25-muscle-atlas/32-AT6-PLACEMENT-CONTEXT-CAMERA-AND-MOTION-QA.md의 해당 절을 반드시 읽어라.
추가 필수 범위: 실제 모델 landmark annotation과 필요한 국소 carrier 보완을 작성해 기존 compiler에서 learner 점까지 연결한다. 자료 부재 목록만 반복하지 않는다. 교육용 모형 지표와 실제 피부/취혈 정확성을 구분하며 첫 실제 위치 연결 후 양측 22개로 확장한다.
AGENTS.md, 최신 work/EXECUTION.json, work/tasks/AT6.md,
design/2026-09-25-muscle-atlas/30-AT-361-POINTS-AND-TERRITORIES.md,
design/2026-09-25-muscle-atlas/31-AT-EXPERIENCE-AND-DELIVERY-CONTRACT.md 및 지정 선행 실제 evidence를 읽어라.
범위: 기존 AC2의 양측 22점 제안을 AT3/4/5 carrier·규칙에 연결해 고친다. DEV review만 있는 진입과 실제 learner projection을 분리하여 확인된 위치를 기존 카드/overlay로 연결한다.
필수 결과: LU1–11 11개 개념의 양측 선택·이름·기본 위치가 실제 모델 위에서 동작한다. 정밀 위치와 교육용 개략 표현 수를 따로 남기고 미확정 점은 완료로 세지 않는다.
명세의 작업 경계와 인수 검사를 완료해라. 경과 시간에 따른 중단 지시는 폐기됐으며 산출물과 합격 기준으로 종료해라.
기존 AC1/AC2와 공통 compiler/overlay/CameraSessions를 재사용하고 task별 구현을 복제하지 마라.
같은 장면·사용자 조작·원본/OpenSim_Models/T13/기존 WIP를 보존해라.
31 설계 중 이번 범위의 자연스러운 그래픽·카메라·학습 UI 기준을 실제 화면에서 확인해라.
관찰 시점 메뉴를 복구하거나 기존 보기옵션을 다시 디자인하지 마라.
관련 검증·report/evidence를 남기고 최신 EXECUTION의 이 AT record와 feature plan 다음 ID만 갱신해라.
sync_execution.py 및 --check 후 소유 변경만 로컬 커밋해라. 실제 미달은 정확히 보고해라.
계획상 다음은 AT7. 최신 order/선행과 대조하고 자동 실행하지 마라.
push·배포·진단·치료·침 시뮬레이션 금지.
```
