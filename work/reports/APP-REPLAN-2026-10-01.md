# 앱 완성 중심 실행 재계획

2026-10-01 · 사용자 승인에 따른 기준·순서·task 명세·프롬프트 구현.

T100을 더 엄격한 자료 수집 기준으로 계속 재개하는 흐름을 현재 지원 앱의 통합 → 실제 사용자 흐름 감사 → UI/성능 완성으로 바꿨다. 이 실행은 계획과 실행 도구의 수정이며 실제 앱 task를 대신 구현하거나 합격 처리하지 않았다.

## 적용

- 현재 설계: `design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md`
- 실행 원본: `work/EXECUTION.json`, revision `app-completion-2026-10-01`
- 제품 계약: `work/product-acceptance.json`
- 콘텐츠 확장 색인: `work/content-backlog.json`; 기존 상세 blocker 원장을 그대로 참조
- 현재 명세: 향후 18개 task의 `work/tasks/*-APP-COMPLETION.md`
- 독립 프롬프트: `work/prompts/app-completion-2026-10-01/`의 18개 txt, 01-T100부터 18-T40까지
- 현재 NEXT/전체 프롬프트북/STATUS/registry의 generated projection을 동기화
- AGENTS 및 25·26 설계에 사용자 승인 개정의 우선순위를 명시

## 종료 의미

T100은 지원 구조의 통합과 안전한 노출을 끝낸다. T80은 주요 사용 흐름의 실제 결함을 찾아 보완한다. T58은 화면·카메라·패널·실측 성능을 완성한다. 이후 현재 지원 근육의 구조/기능 설명, 신경 계약→자료→주행→화면→설명, 움직임 계획→변형/재생→파일럿→family 확장→품질 순서로 진행한다.

후반의 첫 batch·자료 확장·등록·동일 흐름 감사 14개 task는 해당 기능 task의 내부 unit으로 흡수했다. 앞으로의 실행 수를 32개에서 18개로 줄였으며 새 ID를 만들지 않았다. 흡수는 실행 완료가 아니고 이전 record 및 원본 task 명세/근거를 보존한다.

task의 scoped acceptance, local product readiness, 전체 콘텐츠 completeness를 분리했다. 경로 없는 127/130, 직접 인용 73, 미정합 BP3D 13개는 정확한 미확정 상태와 재개 조건으로 보존하며 일괄 앱 개발 종료 차단으로 두지 않는다. 지원한다고 표시한 구조의 잘못된 이름/좌우/범위/위치와 실제 핵심 조작 결함은 계속 차단한다. 미정합 표면은 T100에서 일반 학습 경로에서 격리하고 개발 관찰 근거를 보존한다.

분모 542/563/12, 기존 HA 130, 역사163(6/20/135/2), source-only, public held, humanReview not_performed는 유지한다. 과거 source-wide geometry 부재를 새로 주장하지 않는다. 제품 지원 범위를 합격용 작은 subset으로 줄이지 않으며 실제 runtime의 유효한 지원 경로 전체를 원장으로 생성한다.

## 현재 상태

계획 시작 HEAD: `0c5f5d2c3c2297ec6b41b97b3e14b8dd1af1b179`.
T100의 상태는 아직 `in_progress / partial`이다. nextUnit만 `finalize-supported-app-integration`으로 바꿨고 이전 nextUnit·pending·gate·result·finalization은 EXECUTION의 scopeAmendmentHistory에 보존했다. T80/T58 및 다른 task는 실행하지 않았다. 어떤 task의 acceptance도 이번 수정으로 바꾸지 않았다.

`work/product-scope.json`은 T100이 실제 runtime으로 생성해야 한다. 이번 계획에서 target ID 지원 집합이나 구현 성공 증거를 추정해 만들지 않았다.

## 실행 도구와 검증

sync_execution.py는 task별 promptFile을 읽어 NEXT와 전체 프롬프트북을 생성한다. scoped pass에는 계약 revision, 빈 unresolvedProductBlockers, 실제 workspace evidence 파일 및 nextUnit=null을 확인한다. 기존 T98/T99 보고와 acceptance는 그대로 유지한다.

계획 검증은 JSON 참조/18개 실행 순서와 prompt 연결/현재 spec/이전 record와 acceptance 및 evidence 보존/기존 WIP 보존/동기화 검사로 수행한다. 앱 코드와 geometry를 수정하지 않았으므로 UI 테스트와 production build를 반복하지 않는다. 검증 결과는 `work/evidence/app-completion-replan-2026-10-01/verification.json`에 기록한다.

## 후속

사용자는 01-T100 → 02-T80 → 03-T58 순으로 별도 프롬프트를 실행한다. 실행마다 해당 task만 진행한다. 이후 04-T81부터 순서를 이어간다. 새 콘텐츠 확보는 새로운 실제 근거·특정 구조 요청·사용 감사에서 확인한 주요 공백이 있을 때 관련 항목을 재개한다. 다음 task 자동 실행, push, 배포는 하지 않았다.

## 로컬 체크포인트 범위

새 설계·현재 task 명세·18개 프롬프트·제품 계약/콘텐츠 색인·EXECUTION·NEXT·생성 프롬프트북·동기화 도구·이 보고와 계획 검증 근거를 포함한다. AGENTS는 이번 추가 개정만, STATUS는 현재 generated execution 및 기존 역사 필드 구분만 부분 스테이징한다.

기존 AGENTS/STATUS의 사용자 WIP, 미추적 R15 registry와 과거 task/설계/evidence 폴더는 체크포인트에 혼합하지 않고 작업 트리에 보존한다. 앱 코드·source mesh·OpenSim_Models·T13 변경은 없다. 커밋 해시는 최종 응답으로 보고한다.
