# T82 — 지원 구조 설명·카드 감사와 보완

2026-10-01 · 현재 계획 · 담당 Luna Max.

이 명세는 [27-APP-COMPLETION-AND-CONTENT-ROADMAP.md](../../design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md)와 EXECUTION의 계약을 따른다. 계획 수정은 구현 합격이 아니다. 이전 명세 `work/tasks/T82.md`와 보고서는 역사로 보존된다.

## 범위

T81이 연결한 현재 지원 근육 전체의 기시정지/카드/명칭/갈래와 운동·감각 신경 구분을 감사하고 실질적인 오류를 보완한다. 257행과 전체 target disposition을 확인하되 미검증 세부 연구를 완료로 만들지 않는다. 주요 구조 학습 흐름과 private 원문 비노출을 검증한다. 기존 콘텐츠 backlog나 모든 신경 세부 가지의 미확정만으로 앱 기능 합격을 취소하지 않는다.

## 합격 기준

- 현재 지원 카드 전체의 데이터 계약과 주요 구조 설명 흐름을 감사한다.
- 확인된 기시정지/갈래/손발/신경 구분 오류와 private 원문 노출을 수정한다.
- 범위가 명시된 구조 설명 기능 acceptance와 콘텐츠 completeness를 별도 보고한다.

해당 제품 계약을 실제로 검증한 경우 completed/passed, nextUnit=null로 종료한다. 전체 콘텐츠 completeness는 별도 partial이어도 된다. 지원한다고 표시한 구조의 잘못된 이름/좌우/범위/위치는 허용하지 않는다. 문서 수정만으로 합격하지 않는다.

## 실행과 산출물

AGENTS, EXECUTION, 27 설계, 이 명세, 지정 promptFile, 실제 선행 보고·evidence를 읽는다. 기존 25·26의 보존·공통 처리 원칙은 유지하되 충돌하는 전체 콘텐츠 gate/10개 종료 규칙은 적용하지 않는다.

task 소유 코드/자료 수정, 관련 검사와 필요한 실제 UI 검증, 보고서 및 작은 evidence를 남긴다. 원본/OpenSim_Models/T13/기존 WIP/source-only/public held/humanReview를 보존한다. 기존 542/563/12와 HA 130/역사163을 유지한다. source/hash와 제품 route 실제 숫자를 보고하며 전체 해부학 완료라고 쓰지 않는다.

해당 task record 갱신 후 sync_execution.py와 --check로 문서를 동기화한다. 소유 변경만 로컬 커밋한다. 다음 task 자동 실행·push·배포·자동 위임·임상 기능 구현은 하지 않는다.
