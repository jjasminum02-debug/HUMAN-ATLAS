# T80 — 앱 사용 흐름·주요 구조 감사와 결함 보완

2026-10-01 · 현재 계획 · 담당 Luna Max.

이 명세는 [27-APP-COMPLETION-AND-CONTENT-ROADMAP.md](../../design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md)와 EXECUTION의 계약을 따른다. 계획 수정은 구현 합격이 아니다. 이전 명세 `work/tasks/T80.md`와 보고서는 역사로 보존된다.

## 범위

T100의 실제 product-scope와 기존 전수 원장/시각 evidence를 재사용하여 지원 앱을 감사하고 고친다. 전신→12부위→검색→양측 선택→카드→심부 관찰→숨김/복원과 주요 뼈 맥락이 실제로 사용 가능한지 확인한다. 모든 542/563 disposition은 유지하되 모든 세부 target의 새 geometry/PNG/직접 인용을 요구하지 않는다. 알려진 콘텐츠 backlog만으로 T100을 다시 partial로 돌리지 않는다. 지원하는 구조의 잘못된 대응·좌우·누락 노출·주요 학습 흐름 공백은 이 task에서 수정한다. UI polish/정밀 성능은 T58로 인계한다.

## 합격 기준

- 12부위와 주요 전신 맥락에서 검색·선택·카드·관찰의 실제 사용 흐름을 확인한다.
- 지원 표면의 잘못된 명칭/side/범위 및 주요 흐름을 막는 누락·복원·정책 결함을 수정한다.
- 전체 542/563 disposition 및 기존 gap 원장을 보존하고 제품 결함과 콘텐츠 확장 항목을 구분한다.
- 재현 가능한 제품 차단 결함이 남지 않고 T58용 실제 UI/성능 개선 목록을 전달한다.

해당 제품 계약을 실제로 검증한 경우 completed/passed, nextUnit=null로 종료한다. 전체 콘텐츠 completeness는 별도 partial이어도 된다. 지원한다고 표시한 구조의 잘못된 이름/좌우/범위/위치는 허용하지 않는다. 문서 수정만으로 합격하지 않는다.

## 실행과 산출물

AGENTS, EXECUTION, 27 설계, 이 명세, 지정 promptFile, 실제 선행 보고·evidence를 읽는다. 기존 25·26의 보존·공통 처리 원칙은 유지하되 충돌하는 전체 콘텐츠 gate/10개 종료 규칙은 적용하지 않는다.

task 소유 코드/자료 수정, 관련 검사와 필요한 실제 UI 검증, 보고서 및 작은 evidence를 남긴다. 원본/OpenSim_Models/T13/기존 WIP/source-only/public held/humanReview를 보존한다. 기존 542/563/12와 HA 130/역사163을 유지한다. source/hash와 제품 route 실제 숫자를 보고하며 전체 해부학 완료라고 쓰지 않는다.

해당 task record 갱신 후 sync_execution.py와 --check로 문서를 동기화한다. 소유 변경만 로컬 커밋한다. 다음 task 자동 실행·push·배포·자동 위임·임상 기능 구현은 하지 않는다.
