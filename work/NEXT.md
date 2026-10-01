# 현재 다음 실행

자동 생성. 편집 원본은 [EXECUTION.json](EXECUTION.json). 역사 handoff/자료 개수로 다음 작업을 결정하지 않는다.

- 확인된 최근 진행: T80 / accepted
- 다음 ID: **T58**
- 현재 지원 앱 완성: T100 통합 마무리 → T80 사용 감사/보완 → T58 UI·성능 최적화. 전체 콘텐츠 확보는 별도 상태로 유지한다.

```text
HUMAN ATLAS에서 T58만 수행해라. 담당 Astra · 현재 대화 직접 구현.

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
1. T100/T80 새 계약의 passed, 실제 product-scope.json, T80 결함·개선 원장과 최신 UI를 확인한다. 오래된 전체 콘텐츠 gate나 역사 T57→T59 순서를 재실행하지 않는다. 담당 Astra, 현재 대화 직접 구현이며 자동 위임하지 않는다.
2. 현재 UI를 먼저 보고 화면의 큰 문제부터 수정한다. 단일 viewport/scene/camera, 밝은 배경, 뼈·근육 식별, 선택 대비, 카메라 프레이밍, 패널 가림, 깊은 구조 접근, 복원 예측 가능성에 집중한다. 제거한 로딩 로고/인체 그림/슬로건을 복구하지 않는다. 학생 화면에 source/task/evidence 메타데이터를 넣지 않는다.
3. 변경 전 한 번의 실제 프로파일을 잡는다. cold와 warm bytes/loading, render 호출 비용과 frame interval을 구분하고 active triangles/draws/CPU geometry, 20회 지역 전환 후 cache/취소/late-response 상태를 확인한다. GPU/VRAM/total-process 메모리 관측 불가는 한계로 기록한다.
4. 확인된 병목부터 lazy loading·경량 projection·캐시/LRU·중복 render·불필요한 state churn·패널 layout·LOD를 공통 경로에서 최적화한다. 실제 필요 없이 기술을 갈아엎거나 별도 viewer를 만들지 않는다. 구조 삭제/잘못된 좌우/무조건 품질 저하로 빠르게 만들지 않는다. 예산 변경은 근거와 품질 영향으로 명시하고 몰래 상향하지 않는다.
5. 1440/1024/390 실제 브라우저에서 전신·머리·손·하지/등 대표 시점, 검색·양측 선택·카드·키보드·뒤/앞·숨김/복원을 검증한다. 검은 프레임·로딩 실패·카메라 reset·overlap·console error와 성능 회귀를 수정한다. desktop 390px를 모바일 실기기 검증으로 부르지 않는다.
6. 최종 관련 회귀/typecheck/build와 영향받는 실제 흐름을 한 번 검증하고 변경 전후 수치·PNG·한계를 남긴다. 제품 차단 결함 없이 지원 앱이 안정적으로 사용 가능하면 T58 completed/passed 및 local_app_ready를 기록한다. 전체 해부학 완료나 공개 배포 승인을 뜻하지 않는다. 다음 T81은 자동 실행하지 않는다.

종료 후 다음 ID는 T81다. 다음 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```
