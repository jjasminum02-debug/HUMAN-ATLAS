# T59 — 앞정강근 실제 변형·공통 재생 연결

2026-10-01 · 현재 계획 · 담당 Sol High.
현재 기준은 27-APP-COMPLETION-AND-CONTENT-ROADMAP.md와 EXECUTION의 acceptanceContract/promptFile이다.
이전 명세 `work/tasks/T59.md`와 흡수 task의 자료/보고는 역사로 보존한다. 계획 수정은 실행·합격이 아니다.

## 범위

T35의 현재 base에 실제 앞정강근 변형과 발 움직임을 제작하고 같은 viewport의 공통 재생기로 연결한다. T60의 player/CTA 통합을 같은 task에 흡수한다. source/frame/rest pose/endpoint 근거, 실제 skinning 또는 morph 변형, 주변 구조의 수동 대응/관통을 검증한다. scale-only/뼈나 선 길이만/별도 모형 전환은 제품 수축 시범으로 세지 않는다.

## 수행

현재 product-scope의 실제 근육/뼈와 T35 제작 입력을 사용하여 derived rig/clip을 별도 소유 경로에 만든다. 원본을 수정하지 않는다. 실제 표면 변형과 관절 움직임, 주변 맥락을 같은 scene에 결속한다. CTA의 명시 재생/pause/속도/진행/처음 자세, reduced-motion, 전환·실패·unmount 정리를 공통 player로 구현한다. 데이터/pose/주변 관통과 실제 전신 탐색→선택→재생→복원을 확인한다. T60 별도 실행을 하지 않는다.

## 합격과 보존

실제 지정된 기능/자료/계획의 근거·검증과 해당 계약을 충족하면 scoped passed로 종료한다. 지원한다고 표시한 자료·기능의 오류는 해결하며 전체 콘텐츠 completeness는 독립이다. 본문에 남은 과거 전수 0-gap/10개 종료/후속 순서 문구는 현재 계약과 충돌하면 적용하지 않는다.

report/evidence, progress.productAcceptance와 EXECUTION의 해당 record를 갱신하고 sync_execution.py 및 --check를 수행한다. 기존 원본/OpenSim_Models/T13/사용자 WIP/HA130/역사163/source-only/rights/humanReview를 보존한다. 소유 변경만 로컬 커밋하며 다른 task/자동 위임/push/배포/임상 기능은 실행하지 않는다.
