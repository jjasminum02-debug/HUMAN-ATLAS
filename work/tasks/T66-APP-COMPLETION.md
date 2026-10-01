# T66 — 움직임 family 재사용 확장·학습 연결

2026-10-01 · 현재 계획 · 담당 Luna Max.
현재 기준은 27-APP-COMPLETION-AND-CONTENT-ROADMAP.md와 EXECUTION의 acceptanceContract/promptFile이다.
이전 명세 `work/tasks/T66.md`와 흡수 task의 자료/보고는 역사로 보존한다. 계획 수정은 실행·합격이 아니다.

## 범위

T27/T28/T45/T46/T29/T31의 소흉근·견갑대 준비/시범/설명/감사를 이 task의 내부 unit으로 흡수한다. T35가 실제 지원 가능으로 정한 family를 공통 rig/player/설명 계약으로 확장한다. 현재 base에서 실제 해부학적 이동과 표면 변형이 성립하는 사례만 지원한다. 사용자 제외 표정근 clip은 만들지 않는다. 전 근육 animation 수집을 무제한 종료 조건으로 두지 않고 지원 집합과 나머지 backlog를 명시한다.

## 수행

T59 공통 rig/player와 T25 학습 흐름을 재사용하여 T35의 후속 family를 제작한다. 소흉근·견갑대의 실제 source/부착/pose/움직이는 뼈·수동 변형 근거를 검증한다. 검증된 clip과 같은 scene의 설명/카드/재생을 함께 연결한다. 모든 이동을 단순 scale로 표현하지 않는다. 실제 family별 의미 검토와 전환/복원/관통/소스 보존 검사를 한다. 흡수된 작은 task를 별도로 실행하거나 batch 전용 runtime 분기를 만들지 않는다. 새 근거 없이는 지원 clip 수를 채우기 위한 모션을 만들지 않는다.

## 합격과 보존

실제 지정된 기능/자료/계획의 근거·검증과 해당 계약을 충족하면 scoped passed로 종료한다. 지원한다고 표시한 자료·기능의 오류는 해결하며 전체 콘텐츠 completeness는 독립이다. 본문에 남은 과거 전수 0-gap/10개 종료/후속 순서 문구는 현재 계약과 충돌하면 적용하지 않는다.

report/evidence, progress.productAcceptance와 EXECUTION의 해당 record를 갱신하고 sync_execution.py 및 --check를 수행한다. 기존 원본/OpenSim_Models/T13/사용자 WIP/HA130/역사163/source-only/rights/humanReview를 보존한다. 소유 변경만 로컬 커밋하며 다른 task/자동 위임/push/배포/임상 기능은 실행하지 않는다.
