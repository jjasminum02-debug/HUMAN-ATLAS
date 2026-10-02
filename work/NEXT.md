# 현재 다음 실행

자동 생성. 편집 원본은 [EXECUTION.json](EXECUTION.json). 역사 handoff/자료 개수로 다음 작업을 결정하지 않는다.

- 확인된 최근 진행: T25 / accepted
- 다음 ID: **T66**
- 현재 지원 앱 완성: T100 통합 마무리 → T80 사용 감사/보완 → T58 UI·성능 최적화. 전체 콘텐츠 확보는 별도 상태로 유지한다.

```text
HUMAN ATLAS에서 T66만 수행해라. 담당 Luna Max.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence 및 design/2026-09-25-muscle-atlas/28-ALL-MUSCLE-MOTION-PIPELINE.md를 읽어라.
2026-10-02 최신 사용자 지시: 초기 확장 근육 목록 없이 전체 근육을 대상으로 한다. 28 설계가 미래 motion의 소수 파일럿/소흉근 중심 범위와 과거 표정근 제외 문구보다 우선한다. 27의 제품 acceptance/content completeness 분리는 유지한다.
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
이번 범위: T35/T59 전체 근육 원장과 공통 rig/player/설명 계약으로 429 target/232 source 개념 전체를 처리한다. T27/T28/T45/T46/T29/T31 내부 작업을 흡수한다. 별도 초기 확장 근육 목록을 두지 않으며 제작 가능으로 확정한 모든 source/family 패키지를 구현·검증·등록한다. 미확보/충돌도 전수 원장과 구체적 다음 작업으로 남긴다. 같은 task 내 병렬 candidate 제작과 단일 writer 통합을 사용한다.

1. T35/T59/T25의 실제 산출물, work/evidence/T59/authoring-run-manifest.json과 validator를 읽고 frozen 계약·전수 배정·출력 ownership/hash를 검사한다. manifest 없이 과거 임의 배정/근육 shortlist를 추정하지 않는다. 소흉근/견갑대만 처리하는 과거 범위를 반복하지 않는다.
2. 전체 429 target/447 membership과 232 source/462 표면의 action/side/part/geometry/rig/clip 상태를 유지한다. 전체를 작업 큐로 처리하며 batch는 내부 복구 단위다. 몇 개 예시나 10개 후 의무 종료로 범위를 줄이지 않는다. group/repeated family가 일부 member로 완료되지 않도록 정확한 지원 범위를 계산한다.
3. 사람이 자산 A/B/C 프롬프트를 실행했으면 owned candidate package와 생성/검증 근거를 통합한다. 자동 agent/thread는 만들지 않는다. worker 미실행이면 같은 공통 exporter로 직접 처리한다. 공통 rig/axis/frame/key를 worker가 제각각 재정의하지 않게 한다.
4. 가능한 입력은 실제 derived skin/morph/corrective 자산으로 만들고 정확한 현재 source/side/pose에 결속한다. shared 관절 동작을 재사용하되 해당 muscle의 부착·분절·수동 주변 변형·관통/중간 pose를 검증한다. 원본 변형/가짜 geometry·선/scale-only/별도 모델 뷰로 완료를 만들지 않는다.
5. 부족한 실제 입력은 새 단서에 따라 조사/보완하고 source 없는 항목은 null·구체적 확보 작업을 유지한다. 제작 가능으로 확정한 패키지가 미구현이면 실제 미완 unit으로 남기고 같은 task에서 계속 해결한다. 전수 row 작성만으로 clip 구현을 합격 처리하지 않는다.
6. 전수 자동 source/side/rest/weights/topology/track/pose/cleanup/정책 검사와 유형·변경/충돌 실제 화면을 검사한다. whole suite/12지역 PNG는 각 worker가 반복하지 않고 통합 writer가 영향 분석 후 한 번 검사한다. 지원된 실제 자산의 bugs를 해결하고 범위를 정직하게 보고한다.
7. 모든 현재 제작 가능 패키지의 구현/통합 책임을 마쳤을 때 해당 task acceptance를 기록한다. 전체 움직임 목표는 각 target/side/action의 실제 구현에서 별도로 계산하며 remaining이 있으면 wholeMuscleMotionGoal=partial이다. 몇 개 근육 성공으로 전체 구현 완료라고 쓰거나 나머지 근육을 삭제하지 않는다. 다음은 T85다.

종료 후 다음 ID는 T85다. 현재 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```
