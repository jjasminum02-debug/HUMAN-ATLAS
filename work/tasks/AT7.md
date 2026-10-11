# AT7 — 기존 따라보기 일반화·화면 맞춤·전체 점 표시

상태: planned / 구현 미착수. 실행 상태 원본은 work/EXECUTION.json의 featureWorkUnits.AT7.
예상: **40–60분**. 선행: AT6. 기본 실행 순서: AT1→AT29.

## 읽을 자료

AGENTS.md, work/EXECUTION.json, work/NEXT.md, design/2026-09-25-muscle-atlas/30-AT-361-POINTS-AND-TERRITORIES.md, work/reports/acupoint-AC1.md, work/reports/acupoint-AC2.md와 선행 AT report/evidence. AC 역사 자료는 최초 또는 관련 변경 때만 읽고 반복 다운로드하지 않는다.

## 수행 범위

AC2 Tour/CameraSessions를 데이터 기반 14경맥용으로 일반화하고 경맥 전체/선택 점 framing을 화면 맞춤·선택 맞춤에 연결한다. 전체 경혈 점 표시와 선택 경맥 필터, LOD label을 구현한다. 관찰 시점 메뉴는 복구하지 않는다.

대상 코드: 별도 point 배정 없음.

## 완료 기준

실제 LU tour·수동 orbit 우선권·기존 해부 선택 회귀를 검사한다. 모든 점 표시에서는 점을 임의 생략하지 않고 겹치는 이름만 축약한다. off/on·cancel은 기존 구현을 재사용한다.

## 공통 실행 규칙

- 기존 AC1·AC2 코드와 실제 evidence를 재사용한다. 교수 검토 미수행/과거 미승인만으로 독립 기술 작업을 막지 않는다. 근거 없는 좌표·권리·검토는 만들지 않는다.
- 한 번에 이 task만 실행한다. 20–80분 규모의 계획이며 이 task의 예상 시간은 위 표기다. 60분에 진행률을 점검하고 80분에는 안전한 checkpoint를 남긴다. 시간만 채우지 말고 일찍 끝나면 종료한다. 미달을 pass로 바꾸지 않는다.
- 처음부터 정밀 수작업을 전부 하는 추정이 아니다. 선행 공통 도구와 확인된 입력 재사용을 전제로 한다. 같은 실패가 재현되면 같은 접근을 반복하지 말고 한 가지 구체적 대안/필요 입력을 남긴다. 새 번호를 자동 발급하지 않는다.
- 같은 AnatomySceneRoot/renderer/camera, 기존 frame/metre/static pose, 사용자 layer-off/선택을 보존한다. 관찰 시점 메뉴는 되살리지 않으며 화면 맞춤과 선택 맞춤을 사용한다.
- 읽기 전용 원본/OpenSim_Models/T13 drafts/사용자 WIP와 역사 freeze를 보존한다. private 교재·source cache·실패 이력은 learner bundle에 넣지 않는다.
- 관련 unit/data 검사와 변경한 실제 화면만 우선 검증한다. 모든 단계마다 전체 역사 suite를 반복하지 않는다. 코드/필수 data/작은 evidence·보고서의 소유 변경만 로컬 commit한다.
- 상태는 EXECUTION.featureWorkUnits의 해당 AT record만 갱신한다. featurePlans의 nextUnit은 순서/선행을 확인해 갱신하고, 숫자 T queue와 역사 AC 기록은 바꾸지 않는다. sync_execution.py와 --check를 실행한다.
- 보고서에 elapsed time, 완료/미완, 실제 표시 수/근거/검증 범위, commit hash/포함·제외·잔여 변경, 다음 ID/프롬프트를 남긴다. 다음 task 자동 실행·push·배포·진단·치료·침 시뮬레이션 금지.

## 산출물

이 범위의 코드/자료 + work/reports/AT7.md + work/evidence/AT7/. 계획 파일을 실제 artifact로 세지 않는다.

## 붙여 넣을 프롬프트

```text
HUMAN ATLAS에서 AT7만 수행해라.
AGENTS.md, 최신 work/EXECUTION.json, work/tasks/AT7.md,
design/2026-09-25-muscle-atlas/30-AT-361-POINTS-AND-TERRITORIES.md와 지정된 선행 실제 evidence를 읽어라.
범위: AC2 Tour/CameraSessions를 데이터 기반 14경맥용으로 일반화하고 경맥 전체/선택 점 framing을 화면 맞춤·선택 맞춤에 연결한다. 전체 경혈 점 표시와 선택 경맥 필터, LOD label을 구현한다. 관찰 시점 메뉴는 복구하지 않는다.
필수 결과: 실제 LU tour·수동 orbit 우선권·기존 해부 선택 회귀를 검사한다. 모든 점 표시에서는 점을 임의 생략하지 않고 겹치는 이름만 축약한다. off/on·cancel은 기존 구현을 재사용한다.
40–60분 규모로 수행하되 최대 80분에는 안전한 checkpoint를 남겨라.
기존 AC1/AC2를 다시 만들지 말고 미확정 혈위를 자동 승인하지 마라.
단일 장면, 원본/OpenSim_Models/T13/사용자 WIP를 보존해라.
관찰 시점 메뉴를 복구하거나 보기옵션을 다시 디자인하지 마라.
관련 검증·실제 화면·report/evidence를 남기고 EXECUTION의 이 AT 상태와 feature plan 다음 ID만 갱신해라.
sync_execution.py 및 --check를 실행하고 소유 변경만 선별 로컬 커밋해라.
미달이면 정확한 남은 unit을 기록하고 완료를 가장하지 마라.
다음은 AT8이며 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```
