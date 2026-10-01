# T100 — 현재 지원 범위 앱 통합 마무리

2026-10-01 · 현재 계획 · 담당 Luna Max.

이 명세는 [27-APP-COMPLETION-AND-CONTENT-ROADMAP.md](../../design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md)와 EXECUTION의 계약을 따른다. 계획 수정은 구현 합격이 아니다. 이전 명세 `work/tasks/T100.md`와 보고서는 역사로 보존된다.

## 범위

현재 단일 scene의 ZA 기반 전신 앱 통합을 마무리한다. 현재 runtime에서 product-scope.json을 생성하여 지원 구조/실제 표현 범위/학습 경로/개발 관찰을 구분한다. BP3D 미정합 13개는 일반 학습 노출에서 격리하고 source-only 근거를 보존한다. 지원 구조의 검색·세 이름 카드·좌우·12부위·선택·핵심 관찰 controller와 정책을 검증한다. 127개 세부 target 확보·73개 직접 인용·전체 extent pass는 콘텐츠 backlog이며 이 task의 일괄 종료 조건이 아니다. 실제 지원한다고 표시한 구조의 오류는 고친다. 최종 UI polish와 정밀 성능 최적화는 T58 책임이다.

## 합격 기준

- 현재 실제 runtime에서 지원 범위와 정확한 표현 수준을 생성하고 542/563 전체 disposition을 기존 원장과 연결한다.
- 지원 경로의 카드/side/region/name/정책 자동 계약 검사와 기본 전신·12부위·선택 controller의 실제 동작을 확인한다.
- 미정합 BP3D의 잘못된 일반 학습 노출을 격리하고 held/user-layer-off 복원 우회를 막는다.
- 발견된 통합 차단 결함을 수정하고 콘텐츠 completeness와 제품 acceptance를 별도 기록한다.

해당 제품 계약을 실제로 검증한 경우 completed/passed, nextUnit=null로 종료한다. 전체 콘텐츠 completeness는 별도 partial이어도 된다. 지원한다고 표시한 구조의 잘못된 이름/좌우/범위/위치는 허용하지 않는다. 문서 수정만으로 합격하지 않는다.

## 실행과 산출물

AGENTS, EXECUTION, 27 설계, 이 명세, 지정 promptFile, 실제 선행 보고·evidence를 읽는다. 기존 25·26의 보존·공통 처리 원칙은 유지하되 충돌하는 전체 콘텐츠 gate/10개 종료 규칙은 적용하지 않는다.

task 소유 코드/자료 수정, 관련 검사와 필요한 실제 UI 검증, 보고서 및 작은 evidence를 남긴다. 원본/OpenSim_Models/T13/기존 WIP/source-only/public held/humanReview를 보존한다. 기존 542/563/12와 HA 130/역사163을 유지한다. source/hash와 제품 route 실제 숫자를 보고하며 전체 해부학 완료라고 쓰지 않는다.

해당 task record 갱신 후 sync_execution.py와 --check로 문서를 동기화한다. 소유 변경만 로컬 커밋한다. 다음 task 자동 실행·push·배포·자동 위임·임상 기능 구현은 하지 않는다.
