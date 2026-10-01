# T62 — 신경 자료 검증·공통 등록

2026-10-01 · 현재 계획 · 담당 Luna Max.
현재 기준은 27-APP-COMPLETION-AND-CONTENT-ROADMAP.md와 EXECUTION의 acceptanceContract/promptFile이다.
이전 명세 `work/tasks/T62.md`와 흡수 task의 자료/보고는 역사로 보존한다. 계획 수정은 실행·합격이 아니다.

## 범위

T61의 실제 지원 신경을 우선순위에 따라 조사·검증·등록한다. T87의 확장 조사와 T88의 등록은 같은 task의 공통 pipeline으로 흡수한다. trunk/branch/지역/좌우/pose/지배 관계와 source 근거를 구분한다. 이미 확보한 자료부터 완성하며 새 source가 필요한 신경은 명시한 확장 backlog로 남긴다. 모든 신경 연구가 끝날 때까지 첫 검증 자료를 제품에서 사용할 수 없게 만드는 조건은 폐기한다.

## 수행

T61의 지원 후보와 실제 source를 검증하고 같은 schema/registry로 bulk 등록한다. 공식/학술 원문에서 필요한 관계를 확인하고 원문·AI 해석·채택·사람검토를 분리한다. source geometry/좌표/branch와 지배 관계를 각각 검증한다. 실제 통합 가능 자료와 미확보를 보고하며 한 파일럿 또는 자료 수만으로 전 신경 완료라고 하지 않는다. T87/T88 별도 실행·반복 전수 builder를 만들지 않는다.

## 합격과 보존

실제 지정된 기능/자료/계획의 근거·검증과 해당 계약을 충족하면 scoped passed로 종료한다. 지원한다고 표시한 자료·기능의 오류는 해결하며 전체 콘텐츠 completeness는 독립이다. 본문에 남은 과거 전수 0-gap/10개 종료/후속 순서 문구는 현재 계약과 충돌하면 적용하지 않는다.

report/evidence, progress.productAcceptance와 EXECUTION의 해당 record를 갱신하고 sync_execution.py 및 --check를 수행한다. 기존 원본/OpenSim_Models/T13/사용자 WIP/HA130/역사163/source-only/rights/humanReview를 보존한다. 소유 변경만 로컬 커밋하며 다른 task/자동 위임/push/배포/임상 기능은 실행하지 않는다.
