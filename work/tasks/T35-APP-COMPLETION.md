# T35 — 같은 모형 움직임 지원 범위·제작 계획

2026-10-01 · 현재 계획 · 담당 Sol High.
현재 기준은 27-APP-COMPLETION-AND-CONTENT-ROADMAP.md와 EXECUTION의 acceptanceContract/promptFile이다.
이전 명세 `work/tasks/T35.md`와 흡수 task의 자료/보고는 역사로 보존한다. 계획 수정은 실행·합격이 아니다.

## 범위

현재 실제 전신 base와 구조/설명/신경 지원 범위를 확인하여 첫 앞정강근 시범과 재사용 가능한 다음 움직임 family를 계획한다. 실제 source/frame/pose/부착/rig 가능성과 OpenSim 보조 source 대응을 검증한다. 현재 제작 가능한 범위를 명시하고 나머지는 움직임 backlog로 보존한다. exact 표정근 clip 사용자 제외는 유지하며 전 근육 clip 확보를 첫 움직임 제공의 선행 조건으로 두지 않는다. 계획 task이며 clip 구현은 T59/T66에서 한다.

## 수행

기존 실제 source와 target/rig 상태를 읽고 제작 입력·좌표·부착 근거·family 재사용/예외·품질 판단을 정한다. 임의로 지원 가능을 선언하지 않는다. 앞정강근 pilot과 후속 소흉근/견갑대 사례의 실제 가능성과 필요 작업을 확인한다. 검증 가능한 계획 산출물로 종료하며 새 clip/원본 geometry 변형을 하지 않는다.

## 합격과 보존

실제 지정된 기능/자료/계획의 근거·검증과 해당 계약을 충족하면 scoped passed로 종료한다. 지원한다고 표시한 자료·기능의 오류는 해결하며 전체 콘텐츠 completeness는 독립이다. 본문에 남은 과거 전수 0-gap/10개 종료/후속 순서 문구는 현재 계약과 충돌하면 적용하지 않는다.

report/evidence, progress.productAcceptance와 EXECUTION의 해당 record를 갱신하고 sync_execution.py 및 --check를 수행한다. 기존 원본/OpenSim_Models/T13/사용자 WIP/HA130/역사163/source-only/rights/humanReview를 보존한다. 소유 변경만 로컬 커밋하며 다른 task/자동 위임/push/배포/임상 기능은 실행하지 않는다.
