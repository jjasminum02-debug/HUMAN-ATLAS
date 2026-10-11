# AT4 — 머리·손발·가려진 부위 체표 보완

2026-10-11 작업 단위 정정. 상태는 EXECUTION의 해당 record에서 읽는다. 이 명세 자체는 구현 완료의 증거가 아니다.
선행: AT3. 실행 순서는 번호순이 아니라 [현재 계획](../plans/acupoint-at-2026-10-11/START-HERE.md)과 EXECUTION.featurePlans.acupoint-at-361.order를 따른다.

## 읽을 자료

AGENTS.md, work/EXECUTION.json, work/NEXT.md, design/2026-09-25-muscle-atlas/30-AT-361-POINTS-AND-TERRITORIES.md, design/2026-09-25-muscle-atlas/31-AT-EXPERIENCE-AND-DELIVERY-CONTRACT.md, 선행 AT report/evidence.
AC1·AC2 보고서와 schema/overlay/CameraSessions/tour는 최초 또는 관련 변경 때 재사용 근거를 확인한다. 같은 자료를 매번 재조사하지 않는다.

## 수행 범위

같은 제작 경로로 머리/손발과 구강·회음 접근에 필요한 carrier 부분을 처리한다. 기존 손톱 probe를 재사용한다. 세밀 조형 전체 제작은 범위 밖이며 부위별 취혈 지표가 유지되는 표면을 확보한다.

대상 코드: 별도 point 배정 없음.

## 완료 기준

손발 끝·손톱·입 안·회음의 실제 표현 가능/불가능 목록과 접근 시점을 남긴다. 표면이 없는 구역의 점을 얼굴이나 허벅지 등 다른 외피로 옮기지 않는다.

## 작업 경계와 인수 검사

- 산출물: AT3 adapter의 세부 부위 입력과 접근/가림 manifest. 새 조형 엔진을 만들지 않는다.
- 검사: 머리·손발 및 구강/회음의 지원 표면을 실제 확인한다. 미지원은 부위/원인/영향 코드/필요 입력을 명시한다.
- 경계: 표면 부재를 외피 좌표로 덮지 않는다. 지원 불가 목록만으로 전신 체표 완료라고 하지 않는다.

## 실행·검증·기록

- 종료는 산출물과 완료 기준으로 판단한다. 경과 시간을 이유로 중단하거나 검증을 생략하지 않는다. 정정 전 시간 checkpoint 지시는 폐기한다.
- 범위의 완료까지 진행한다. 실제 입력 부재/재현 결함으로 진행이 불가능한 경우에만 남은 unit·시도한 해결·필요 입력을 구체적으로 남긴다. 무한 재검색이나 자동 task 증식은 하지 않는다.
- 31 설계의 공통 구현/화면 계약 중 이 task에 해당하는 항목만 구현·검증한다. AT2에 후속 UI/전신 제작을 추가하지 않는다.
- source/권리/교수 검토/교육용 위치 등급을 분리한다. 과거 미승인만으로 독립 작업을 막지 않으며 unresolved 위치를 자동 승인하지 않는다.
- 단일 scene/root/renderer/camera와 사용자 layer-off/선택을 보존한다. 관찰 시점 메뉴, 로딩 로고·인체 그림·슬로건을 되살리지 않는다. 기존 보기옵션을 재배치하지 않는다.
- 원본/OpenSim_Models/T13 drafts/사용자 WIP와 역사 evidence를 보존한다. 개발 evidence·private 교재·source cache는 learner bundle에 넣지 않는다.
- 변경에 관련된 자동 검사와 실제 화면을 확인한다. 데이터 처리 성공과 실제 표시/시각 검증 수를 구분한다. 전체 역사 suite를 매 task 반복하지 않는다.
- 최신 EXECUTION을 다시 읽고 이 AT record와 feature plan의 nextUnit만 갱신한다. 다음 ID는 order/선행에서 구하며 번호에 1을 더하지 않는다. 다른 실행자의 변경이나 숫자 T/AC 기록을 덮지 않는다. sync_execution.py 및 --check를 실행한다.
- work/reports/AT4.md, work/evidence/AT4/에 실제 산출물·검증·미완·다음 ID/프롬프트를 남긴다. 소유 변경만 선별 로컬 commit하고 hash/포함·제외·잔여 변경을 보고한다. 경과 시간 보고는 완료 조건이 아니다.
- 다음 task 자동 실행·push·배포·진단·치료·침 시뮬레이션 금지.

## 붙여 넣을 프롬프트

```text
HUMAN ATLAS에서 AT4만 수행해라.
AGENTS.md, 최신 work/EXECUTION.json, work/tasks/AT4.md,
design/2026-09-25-muscle-atlas/30-AT-361-POINTS-AND-TERRITORIES.md,
design/2026-09-25-muscle-atlas/31-AT-EXPERIENCE-AND-DELIVERY-CONTRACT.md 및 지정 선행 실제 evidence를 읽어라.
범위: 같은 제작 경로로 머리/손발과 구강·회음 접근에 필요한 carrier 부분을 처리한다. 기존 손톱 probe를 재사용한다. 세밀 조형 전체 제작은 범위 밖이며 부위별 취혈 지표가 유지되는 표면을 확보한다.
필수 결과: 손발 끝·손톱·입 안·회음의 실제 표현 가능/불가능 목록과 접근 시점을 남긴다. 표면이 없는 구역의 점을 얼굴이나 허벅지 등 다른 외피로 옮기지 않는다.
명세의 작업 경계와 인수 검사를 완료해라. 경과 시간에 따른 중단 지시는 폐기됐으며 산출물과 합격 기준으로 종료해라.
기존 AC1/AC2와 공통 compiler/overlay/CameraSessions를 재사용하고 task별 구현을 복제하지 마라.
같은 장면·사용자 조작·원본/OpenSim_Models/T13/기존 WIP를 보존해라.
31 설계 중 이번 범위의 자연스러운 그래픽·카메라·학습 UI 기준을 실제 화면에서 확인해라.
관찰 시점 메뉴를 복구하거나 기존 보기옵션을 다시 디자인하지 마라.
관련 검증·report/evidence를 남기고 최신 EXECUTION의 이 AT record와 feature plan 다음 ID만 갱신해라.
sync_execution.py 및 --check 후 소유 변경만 로컬 커밋해라. 실제 미달은 정확히 보고해라.
계획상 다음은 AT5. 최신 order/선행과 대조하고 자동 실행하지 마라.
push·배포·진단·치료·침 시뮬레이션 금지.
```
