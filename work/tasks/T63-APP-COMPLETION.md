# T63 — 같은 장면의 신경 주행·지배근 선택

2026-10-01 · 현재 계획 · 담당 Sol High.
현재 기준은 27-APP-COMPLETION-AND-CONTENT-ROADMAP.md와 EXECUTION의 acceptanceContract/promptFile이다.
이전 명세 `work/tasks/T63.md`와 흡수 task의 자료/보고는 역사로 보존한다. 계획 수정은 실행·합격이 아니다.

## 범위

검증된 T62 신경을 기존 scene/renderer/camera에서 표시하고 typed 선택/카드/근거 있는 지배근 강조/복원을 연결한다. T89의 같은 방식 확장은 데이터 기반 내부 unit으로 흡수한다. 신경 주행·좌표·pose가 확인된 실제 surface/curve만 사용하고 미확보 신경은 미지원으로 유지한다. source 후보나 이름을 실제 주행으로 조작하지 않는다.

## 수행

하나의 신경 3D 경로로 검증된 자료 전체를 처리하고 선택/branch/side/region/card 및 지배근 강조/복원을 연결한다. loader 취소·cache·layer-off·pose 지원을 기존 controller와 통합한다. 지원되지 않은 운동 pose에서 정적 신경을 잘못 고정하지 않는다. 데이터 계약 전수 검사와 지역/주행 유형·변경 사례의 실제 UI를 확인한다. T89를 따로 실행하지 않는다.

## 합격과 보존

실제 지정된 기능/자료/계획의 근거·검증과 해당 계약을 충족하면 scoped passed로 종료한다. 지원한다고 표시한 자료·기능의 오류는 해결하며 전체 콘텐츠 completeness는 독립이다. 본문에 남은 과거 전수 0-gap/10개 종료/후속 순서 문구는 현재 계약과 충돌하면 적용하지 않는다.

report/evidence, progress.productAcceptance와 EXECUTION의 해당 record를 갱신하고 sync_execution.py 및 --check를 수행한다. 기존 원본/OpenSim_Models/T13/사용자 WIP/HA130/역사163/source-only/rights/humanReview를 보존한다. 소유 변경만 로컬 커밋하며 다른 task/자동 위임/push/배포/임상 기능은 실행하지 않는다.
