# 현재 다음 실행

자동 생성. 편집 원본은 [EXECUTION.json](EXECUTION.json). 역사 handoff/자료 개수로 다음 작업을 결정하지 않는다.

- 확인된 최근 진행: T65 / accepted
- 다음 ID: **T35**
- 현재 지원 앱 완성: T100 통합 마무리 → T80 사용 감사/보완 → T58 UI·성능 최적화. 전체 콘텐츠 확보는 별도 상태로 유지한다.

```text
HUMAN ATLAS에서 T35만 수행해라. 담당 Sol High.

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
이번 범위: 전체 근육 관련 429 target/447 membership과 현재 232 source 개념/462 표면을 빠짐없이 움직임 제작 대상으로 계획한다. 별도 초기 근육 목록을 두지 않는다. 실제 source/side/part/frame/rest pose/부착·작용/rig 가능성을 전수 disposition으로 연결한다. 관절·다관절·넓은 부착·반복/분절·비관절 연조직 family를 공통 같은-scene 계약으로 정리한다. 과거 표정근 제외는 최신 전 근육 지시로 대체하되 자료 없는 형상을 만들지 않는다. 계획 task이며 새 clip 제작은 T59/T66에서 한다.

1. 실제 T65 passed/report/evidence, 현재 App/정적 dataset loader/animation adapter/공통 controller를 읽어 현재 실제 motion 지원 0과 역사 T24 기술 candidate를 구분한다. 과거 blocked T24를 재실행하지 않는다.
2. 준비된 run-manifest 및 snapshots를 읽고 python3 work/tools/validate_motion_parallel_plan.py로 해시·429/232/462 전수 배정·중복 0을 검증한다. 입력이 같으면 배정을 다시 만들지 않는다. A/B/C는 사람이 별도 프롬프트로 실행할 수 있는 같은 T35 자료 준비 작업이다. 자동 위임/새 thread를 만들지 않는다.
3. 전체 target/source/part/group/side/action/pose의 움직임 원장을 만든다. 기시·정지31개 설명/201개 gap을 재사용하고 원문 locator와 source geometry/rig 입력의 부족을 구체적으로 연결한다. 전체 원장에서 임의로 쉬운 근육만 제외/선정하거나 몇 개 예시를 목표로 고정하지 않는다. 그룹/반복 family의 일부 구현을 전체로 세지 않는다.
4. 원문·좌표·pose·부착 근거와 source-derived authoring 선택을 구분한다. OpenSim은 해당 frame/관절/path를 검증할 수 있을 때 보조로 쓰며 전 근육 solver 설치를 일괄 선행 조건으로 만들지 않는다. 기존 source-only와 null canonical binding을 지원 제작의 일괄 차단으로 쓰지 않는다.
5. work/evidence/T35/motion-contract.json에 native source identity/hash/rest pose, sourceKey 기반 결속, derived skin/morph/corrective 변형, 움직이는 뼈·고정 구조·주변 수동 변형·관통 위험, 부분/좌우/동작 조건과 비관절 변형 유형의 계약을 정한다. 수치·pivot·정합을 근거 없이 채우지 않는다. 부족한 입력은 정확한 재개 조건으로 둔다. pipeline 표본은 전체 원장에서 검증 가능성에 따라 정하며 초기 확장 리스트가 아니다.
6. A/B/C 결과가 실제 있으면 --results 검사로 검증한 전수 결과만 통합한다. worker 실행은 선택 사항이며 없으면 같은 manifest 전수 규칙으로 현재 입력/제작 가능성 계획을 직접 처리한다. 아직 조사중인 필드는 unknown·필요 입력으로 남기고 없는 근거를 만들지 않는다. 전체 원장의 현재 상태/필요 작업과 검증된 공통 제작 계약을 완성하면 계획 task를 종료할 수 있으며, 모든 근육의 원문/clip 확보를 T59 시작의 일괄 조건으로 만들지 않는다. 실제 계획/공통 계약 자체가 미완이면 그 unit만 같은 T35에서 해결한다. 공통 작성자는 이 담당자 하나다.
7. T59가 공통 제작/player를 만들고 authoring-run-manifest를 실제 생성한 후 전체 자산을 병렬 제작하는 순서를 구체화한다. T35 합격은 전수 제작 계획/계약 완료이지 새 motion 구현 합격이 아니다. 전체 근육 목표를 소수의 clip 지원으로 축소하지 않는다.

종료 후 다음 ID는 T59다. 현재 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```
