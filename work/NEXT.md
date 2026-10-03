# 현재 다음 실행

자동 생성. 편집 원본은 [EXECUTION.json](EXECUTION.json). 역사 handoff/자료 개수로 다음 작업을 결정하지 않는다.

- 확인된 최근 진행: T25 / accepted
- 다음 ID: **T66**
- 현재 지원 앱 완성: T100 통합 마무리 → T80 사용 감사/보완 → T58 UI·성능 최적화. 전체 콘텐츠 확보는 별도 상태로 유지한다.

```text
HUMAN ATLAS에서 T66 내부 unit 03만 수행해라. 담당 Luna Max · 현재 대화 직접 구현.

이번 입력 파일: work/plans/t66-serial-completion-2026-10-02/03-T66-shoulder-forearm-wrist.txt
계획: work/plans/t66-serial-completion-2026-10-02/README.md
직전 파일 work/plans/t66-serial-completion-2026-10-02/02-T66-hip-knee.txt의 실제 결과를 읽는다. 선행 산출이 없으면 완료로 추정하지 말고 누락된 구현을 먼저 이어받는다. 실패가 이번 입력/공통 계약을 막으면 해당 수정부터 수행하고, 의존하지 않는 콘텐츠 gap은 종료를 막지 않는다.

AGENTS.md, work/EXECUTION.json, work/product-acceptance.json, 해당 task 현재 spec/promptFile, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md와28-ALL-MUSCLE-MOTION-PIPELINE.md를 읽어라. 이번 직렬 계획 README와 실제 선행 unit REPORT/validation, work/reports/T66.md 및 work/evidence/T66/implementation-2026-10-02/{final-validation.json,final-blockers.json,family-queue.json}를 확인한다. T25/T59/A/B/C는 필요한 정확한 근거만 재사용한다. 자산 A/B/C의 JSON661개를 GLB661개로 세지 않는다.

최신 사용자 지정은 Luna Max·현재 대화 직접 구현·직렬이다. 과거 Astra/병렬 지시보다 우선한다. 계획/내부 unit은 새 task ID가 아니다. 새 agent/thread/자동 위임/다음 unit 자동 실행/push/배포/임상 기능/병리 editor를 금지한다. 작업 시작 시 dirty 파일/hash를 기록하고 다른 소유 WIP·과거 evidence를 덮지 않는다. 입력이 달라졌으면 영향 dependency만 재검증한다. r13 evidence/원본은 보존하고 새 명시 revision에 출력한다.

전체 근육/뼈/신경 목표와 현재 지원 범위의 제품 acceptance를 분리한다. 542target/563membership/12부위, 근육429/447/232source concepts/462surfaces, HA130·역사163(6/20/135/2), 원본/source-cache/OpenSim_Models/T13/기존 WIP를 보존한다. source-only/local selection/humanReview=not_performed/public rights held는 독립 상태다. source 행/label group을 독립 해부 개념으로 세지 않는다. 없는 mesh/좌우/관계/정확한 footprint/실측 정상축을 만들지 않는다. 실제 원본 관찰+검토된 정성 근거에 따른 재현 가능한 authored 교육용 masks/weights/pivots/trajectory/correctives는 직접 작성한다. native rig 부재만으로 engineering 책임을 자료 gap으로 돌리지 않는다.

기존 단일 viewport/scene/renderer/camera/controller/frame clock 및 common pose state를 유지한다. '움직임으로 이해하기' 하나: 클릭 반복 왕복, 재클릭 부드러운 rest 복원. 느리게/별도 pause/reset 버튼은 넣지 않는다. slider는 autoplay 중단/자세 유지, reduced-motion을 보존한다. 숨김/투명/layer/selection/history/카메라/취소를 재생이 덮지 않는다. T59 기존+30%를 다시 확대하지 않는다. 학생 화면에 task/source/evidence/내부 ID를 넣지 않는다. 필요한 권리 attribution은 기존 정책대로 유지한다.

자동 계약은 이번 지원/변경 집합 전체에 검사한다. 실제 UI는 가족 유형·좌우·변경/충돌·중간 pose를 확인하고 동일 입력 근거는 재사용한다. 전체 suite/12부위 전수 PNG/문헌 검색을 매 unit 반복하지 않는다. 관측하지 않은 GPU/VRAM/메모리는 추정치와 구분한다.

이번 실행은 T66 내부 unit 03만이다. shoulder-girdle/shoulder/elbow/forearm/wrist 가족의 현재 확보 source와 근거 있는 action 전체를 처리한다. 기존 굽힘·가쪽돌림·손목 굽힘 성공을 재사용하고 남은 action/좌우/갈래를 작성한다. 손가락 자체 가족은 unit 04가 맡는다.

1. fullSourceQueue와 검토된 기시·정지·작용 claims를 family/side/action에 연결한다. 예시 근육 몇 개로 범위를 제한하지 않는다. 관절 위상/견갑골·빗장뼈 협응, 전완 회내·회외에서 실제 source 맥락을 관찰하고 교육용 coupled trajectory/DOF/조합 범위를 작성한다. 모든 axis를 발목 r2에서 복사하지 않는다.
2. 가족 계약→source별 weights/masks/correctives→GLB→기하/부착/주변 조직 및 실제 export pose 검증→같은 scene 등록을 배정 큐 전체에 수행한다. 정확한 source identity/side/part에 결속 가능한 시범을 전체 target/group extent 승인까지 기다리게 하지 않는다.
3. 각 muscle action binding의 시범과 카드가 맞아야 한다. 관절 자세에 동반되는 수동 변형을 해당 근육의 주작용 시범으로 제공하지 않는다. 직접 근거 있는 작용을 보여줄 때 방향/부착/의미를 검사한다. 원문 근거 부족이면 작용 설명·자세 관찰·주작용 시범의 지원 상태를 나눈다.
4. 뼈 직접 선택→관절/역할/지원 action→재생/각도 관찰→복원을 같은 family로 연결한다. 한 뼈에 여러 family가 있으면 관련 action을 선택할 수 있게 한다. fixed support는 고정 역할을 안내하고 독립 DOF를 만들지 않는다.
5. 신규 협응/회내회외/변형 유형·좌우·변경 사례를 실제 브라우저에서 확인한다. 기존 동일 입력 화면과 전체 suite는 반복하지 않는다.

이번 성공 조건: 해당 5가족의 전수 책임 큐에서 engineering으로 제작 가능한 항목을 실제 생성·등록·연결하고 지원 결함을 해결한다. 실제 원본/관계 부족만 구체적 content gap으로 남긴다. 단순 미작성은 gap이 아니다.

작업 기록: work/evidence/T66/serial-completion-2026-10-02/unit-03/에 REPORT.md, 실제 validation 결과·자산/QC/화면 경로·입력 영향/hash를 남긴다. serial-queue.json의 해당 unit 책임 키에 implemented_verified / processed_with_content_gaps / blocked_by_product_defect를 실제 증거로 기록한다. 자료 gap은 missing source/identity/qualitative relation 등 구체적 자료 부족 근거가 있어야 한다. 단순 exporter/mask/trajectory/연결 미구현이나 기하 실패는 engineering blocker다. 원장만 작성하고 unit 성공으로 끝내지 않는다.

T66 내부 unit 01~10의 성공은 T66 전체 passed가 아니다. EXECUTION T66의 progress에 내부 진척과 제품 차단/콘텐츠 gap을 갱신하고 부모 nextUnit=author-and-integrate-normal-motion-bone-and-nerve 및 partial을 유지한다. spec에는 이번 책임을 내부 unit으로 명시하고 promptFile을 이번 파일로 기록하되 다른 task 상태는 바꾸지 않는다. T66 report는 짧은 진척/현재 차단 링크로 갱신하고 전면 재작성/전체 보고 반복은 unit11까지 하지 않는다. unit11은 본문의 최종 판정 규칙을 따른다. python3 work/tools/sync_execution.py와 --check를 수행하고 소유 변경만 선별 로컬 커밋한다.

종료 시 이번 실제 구현/지원 수와 unresolved engineering/content gap을 구분해 보고하고 멈춘다. 다음 수동 실행 파일은 work/plans/t66-serial-completion-2026-10-02/04-T66-hand-digits.txt이다. 실제 남은 선행 구현 차단이 있으면 재개할 파일도 명시한다. 다음 파일을 자동 실행하지 않는다.
```
