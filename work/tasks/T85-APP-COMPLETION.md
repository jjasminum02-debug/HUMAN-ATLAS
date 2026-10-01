# T85 — 지원 움직임·통합 앱 품질 완성

2026-10-01 · 현재 계획 · 담당 Astra · 현재 대화 직접 구현.
현재 기준은 27-APP-COMPLETION-AND-CONTENT-ROADMAP.md와 EXECUTION의 acceptanceContract/promptFile이다.
이전 명세 `work/tasks/T85.md`와 흡수 task의 자료/보고는 역사로 보존한다. 계획 수정은 실행·합격이 아니다.

## 범위

T47의 구조/기능/motion 감사를 흡수하여 현재 실제 지원 clip의 같은 surface/scene 변형과 사용자 흐름을 검증하고 화면 품질을 다듬는다. 표정근 exact clip 제외, 나머지 미지원 움직임, 실제 지원 clip을 구분한다. camera/layer/선택/설명·신경 pose의 동기를 확인한다. 전 근육 clip 확보와 지원 앱 품질 합격은 분리한다. 담당 Astra 현재 대화 직접 구현을 유지한다.

## 수행

지원 clip 전체의 데이터/pose/player 계약과 family별 대표·변경 실제 화면을 감사한다. 움직임 없이 텍스트나 별도 viewer만 보이는 사례를 지원으로 세지 않는다. 실제 주변 관통·camera reset·layer 손실·잘못 고정된 정적 신경·설명 불일치·재생/복원 오류를 수정한다. 현재 앱의 구조/설명/신경/움직임 지원 범위와 콘텐츠 gap을 종합하여 scoped product acceptance를 판정한다. T47 별도 실행 또는 전 근육 제작 재개를 하지 않는다.

## 합격과 보존

실제 지정된 기능/자료/계획의 근거·검증과 해당 계약을 충족하면 scoped passed로 종료한다. 지원한다고 표시한 자료·기능의 오류는 해결하며 전체 콘텐츠 completeness는 독립이다. 본문에 남은 과거 전수 0-gap/10개 종료/후속 순서 문구는 현재 계약과 충돌하면 적용하지 않는다.

report/evidence, progress.productAcceptance와 EXECUTION의 해당 record를 갱신하고 sync_execution.py 및 --check를 수행한다. 기존 원본/OpenSim_Models/T13/사용자 WIP/HA130/역사163/source-only/rights/humanReview를 보존한다. 소유 변경만 로컬 커밋하며 다른 task/자동 위임/push/배포/임상 기능은 실행하지 않는다.
