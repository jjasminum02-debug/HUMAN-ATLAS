# 현재 다음 실행

자동 생성. 편집 원본은 [EXECUTION.json](EXECUTION.json). 역사 handoff/자료 개수로 다음 작업을 결정하지 않는다.

- 확인된 최근 진행: T100 / accepted
- 다음 ID: **T80**
- 현재 지원 앱 완성: T100 통합 마무리 → T80 사용 감사/보완 → T58 UI·성능 최적화. 전체 콘텐츠 확보는 별도 상태로 유지한다.

```text
HUMAN ATLAS에서 T80만 수행해라. 담당 Luna Max.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence를 읽어라.
목표는 현재 지원 범위에서 정확하고 안정적으로 사용할 수 있는 앱이다. task acceptance와 전체 콘텐츠 completeness를 분리한다.
27 설계/현재 acceptanceContract가 과거 전체 콘텐츠 0-gap·full extent 전수 PNG·10개마다 종료 문구보다 우선한다.
542 target/563 membership/12부위, 기존 HA 130, 역사163(6/20/135/2), 원본/OpenSim_Models/T13/기존 WIP를 보존한다.
source-only, 검증된 로컬 선택, humanReview=not_performed, 공개 권리 held를 독립적으로 유지한다.
지원한다고 표시한 구조의 wrong side/name/scope/placement와 실제 사용자 흐름 결함은 해결한다. 미지원 자료로 geometry/binding/승인을 만들지 않는다.
자동 계약 검사는 전수 수행하고 실제 시각 검증은 대표 유형·12부위·변경/충돌 사례에 집중한다. 동일 입력의 기존 근거는 영향 분석 후 재사용한다.
새 단서 없는 고정 catalog 검색·직접 용어 인용 검색·전체 suite/보고서 반복을 하지 않는다. 의미 검토 묶음은 내부 복구 단위다.
제품 계약을 충족하면 completed/passed, nextUnit=null로 종료하고 contentCompleteness=partial 및 남은 콘텐츠를 별도로 보고한다.
실제 제품 차단 결함이 남으면 실패 기능만 구체적으로 기록해 같은 task에서 고친다. 계획 문서만으로 pass하지 않는다.
해당 report/evidence와 EXECUTION record에 acceptanceScope/contractRevision/productReadiness/contentCompleteness/knownContentGaps/unresolvedProductBlockers를 기록한다.
합격 기록은 progress.productAcceptance에 contractRevision=app-completion-2026-10-01, acceptanceScope, productReadiness, contentCompleteness, knownContentGaps, unresolvedProductBlockers=[], evidence=[실제 보고서/검증 파일 경로]를 남긴다.
python3 work/tools/sync_execution.py 및 --check를 수행하고 소유 변경만 선별 로컬 커밋한다.
다음 task 자동 실행, 새 번호/스레드 발급, 자동 위임, push/배포, 임상 진단·치료·자침 기능은 금지한다.

이번 실행:
1. T100이 새 계약으로 passed이고 product-scope.json과 실제 evidence가 있는지 확인한다. 과거 partial 보고서가 존재한다는 이유만으로 중단하지 않는다. 현재 지원 범위와 콘텐츠 completeness를 구분한다.
2. 전체 542 target/563 membership은 기존 disposition과 실제 runtime을 자동 대조한다. 이미 기록한 127개에 새 후보가 없으면 같은 catalog 검색을 반복하지 않는다. 경로/표현 범위/일반 learner 노출이 정확한지 검사한다.
3. 실제 브라우저에서 전신과 12부위, 합집합/전체 복귀, 이름 검색, 양측 전환, typed card, 국소 강조·주변 흐림, 깊은 구조의 격리/맞춤, 숨김/undo/복원, 뒤/앞 탐색을 연속 사용자 흐름으로 검사한다. 얼굴/광배근/양측 어깨·상완/손발/척추·엉치/골반 맥락은 기존 실제 지원 데이터로 확인한다. 표본마다 새 원장을 만들지 않는다.
4. 클릭되지 않는 유효한 표면, wrong side/card, parent를 exact part로 오인시키는 표시, 지역 맥락 손실, 격리 자료 재노출 등 실제 결함을 수정한다. 주요 부위 자체가 비어 있거나 핵심 조작을 할 수 없다면 제품 차단으로 처리한다. 어려운 결함을 콘텐츠 backlog로 바꿔 통과하지 않는다.
5. 선택 가능한 member가 있는 그룹은 그 제공 범위만 검증한다. 변이/미세 분절/미확보 구조는 정직하게 미지원으로 유지한다. 모든 542개의 full extent pass를 새로 만들 필요는 없다. 기존 side conflict는 근거 없이 해소하지 않는다.
6. 변경에 맞는 관련 회귀·타입·빌드 및 대표/변경 browser 사례를 확인한다. 제품 차단 결함이 없으면 T80 completed/passed, contentCompleteness=partial 허용으로 종료한다. UI polish·프로파일 결과·대표 캡처를 T58에 넘기고 자동 실행하지 않는다.

종료 후 다음 ID는 T58다. 다음 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```
