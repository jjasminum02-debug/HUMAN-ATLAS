# T58 — 앱 화면·관찰 UX·실측 성능 완성

2026-10-01 · 현재 계획 · 담당 Astra · 현재 대화 직접 구현.

이 명세는 [27-APP-COMPLETION-AND-CONTENT-ROADMAP.md](../../design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md)와 EXECUTION의 계약을 따른다. 계획 수정은 구현 합격이 아니다. 이전 명세 `work/tasks/T58.md`와 보고서는 역사로 보존된다.

## 범위

T80이 감사한 현재 지원 앱을 화면과 성능 측면에서 완성한다. 단일 scene/camera, 밝은 배경·뼈/근육·선택 대비·카메라 프레이밍·패널·깊은 구조 접근을 실제 UI에서 다듬는다. 1440/1024/390px, 키보드·검색·뒤/앞 흐름과 cold/warm loading, 실제 render/frame/caches를 측정하고 큰 비용부터 최적화한다. 기존 콘텐츠 backlog 전체 해결은 선행 조건이 아니다. 잘못된 구조를 노출하거나 품질을 숨김으로 줄여 성능을 통과시키지 않는다. 로컬 앱 준비와 전체 콘텐츠·공개 권리는 별도로 보고한다.

## 합격 기준

- 1440/1024/390 폭에서 주요 조작/카드/화면이 가려지지 않고 scene/camera 연속성을 유지한다.
- cold/warm, 실제 renderer/frame 및 반복 지역 전환 cache를 측정하고 확인된 큰 성능 문제를 수정한다.
- 대표 전신/지역/선택 장면의 실제 캡처와 변경 전후 성능·오류 상태를 남긴다.
- 현재 지원 범위의 local_app_ready를 실제 검증으로 판정하고 전체 콘텐츠/모바일 실기기/공개 권리 한계를 분리한다.

해당 제품 계약을 실제로 검증한 경우 completed/passed, nextUnit=null로 종료한다. 전체 콘텐츠 completeness는 별도 partial이어도 된다. 지원한다고 표시한 구조의 잘못된 이름/좌우/범위/위치는 허용하지 않는다. 문서 수정만으로 합격하지 않는다.

## 실행과 산출물

AGENTS, EXECUTION, 27 설계, 이 명세, 지정 promptFile, 실제 선행 보고·evidence를 읽는다. 기존 25·26의 보존·공통 처리 원칙은 유지하되 충돌하는 전체 콘텐츠 gate/10개 종료 규칙은 적용하지 않는다.

task 소유 코드/자료 수정, 관련 검사와 필요한 실제 UI 검증, 보고서 및 작은 evidence를 남긴다. 원본/OpenSim_Models/T13/기존 WIP/source-only/public held/humanReview를 보존한다. 기존 542/563/12와 HA 130/역사163을 유지한다. source/hash와 제품 route 실제 숫자를 보고하며 전체 해부학 완료라고 쓰지 않는다.

해당 task record 갱신 후 sync_execution.py와 --check로 문서를 동기화한다. 소유 변경만 로컬 커밋한다. 다음 task 자동 실행·push·배포·자동 위임·임상 기능 구현은 하지 않는다.
