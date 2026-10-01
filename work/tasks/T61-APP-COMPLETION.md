# T61 — 신경 지원 범위·자료 inventory·공통 계약

2026-10-01 · 현재 계획 · 담당 Sol High.
현재 기준은 27-APP-COMPLETION-AND-CONTENT-ROADMAP.md와 EXECUTION의 acceptanceContract/promptFile이다.
이전 명세 `work/tasks/T61.md`와 흡수 task의 자료/보고는 역사로 보존한다. 계획 수정은 실행·합격이 아니다.

## 범위

T58의 지원 앱과 T84 설명 기능 뒤에 신경 source inventory와 실제 지원 집합을 정리하고 source namespace/frame/pose/curve 또는 mesh/branch/검증된 지배 관계/typed card/layer 계약을 구현한다. T86의 범위 대조를 같은 task에 흡수한다. 전체 원장과 미확보는 유지하지만 전 신경의 source 확보를 계약 완료 조건으로 두지 않는다. 감각영역·피부분절·경락을 혼합하지 않고 source 이름만으로 지배 관계를 만들지 않는다.

## 수행

현재 확보 자료와 주요 사용 흐름으로 지원/미지원 신경 집합을 정하고 정확한 identity/좌표/pose/지배 관계 계약을 구현한다. 조사 원장은 전수 참조하고 필수 참조의 실제 자료/hash를 검증한다. T86을 별도로 시작하지 않는다. 계약 fixtures와 기존 앱 policy/selection 회귀를 검사하며 새 신경3D를 완성했다고 쓰지 않는다.

## 합격과 보존

실제 지정된 기능/자료/계획의 근거·검증과 해당 계약을 충족하면 scoped passed로 종료한다. 지원한다고 표시한 자료·기능의 오류는 해결하며 전체 콘텐츠 completeness는 독립이다. 본문에 남은 과거 전수 0-gap/10개 종료/후속 순서 문구는 현재 계약과 충돌하면 적용하지 않는다.

report/evidence, progress.productAcceptance와 EXECUTION의 해당 record를 갱신하고 sync_execution.py 및 --check를 수행한다. 기존 원본/OpenSim_Models/T13/사용자 WIP/HA130/역사163/source-only/rights/humanReview를 보존한다. 소유 변경만 로컬 커밋하며 다른 task/자동 위임/push/배포/임상 기능은 실행하지 않는다.
