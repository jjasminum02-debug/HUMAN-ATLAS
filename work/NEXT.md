# 현재 다음 실행

자동 생성. 편집 원본은 [EXECUTION.json](EXECUTION.json). 역사 handoff/자료 개수로 다음 작업을 결정하지 않는다.

- 확인된 최근 진행: T25 / accepted
- 다음 ID: **T66**
- 현재 지원 앱 완성: T100 통합 마무리 → T80 사용 감사/보완 → T58 UI·성능 최적화. 전체 콘텐츠 확보는 별도 상태로 유지한다.

```text
HUMAN ATLAS에서 T66 내부 unit 02만 수행해라. 담당 Luna Max · 현재 대화 직접 구현.

이번 입력 파일: work/plans/t66-serial-completion-2026-10-02/02-T66-hip-knee.txt
계획: work/plans/t66-serial-completion-2026-10-02/README.md
직전 파일 work/plans/t66-serial-completion-2026-10-02/01-T66-deformation-repair.txt의 실제 결과를 읽는다. 선행 산출이 없으면 완료로 추정하지 말고 누락된 구현을 먼저 이어받는다. 실패가 이번 입력/공통 계약을 막으면 해당 수정부터 수행하고, 의존하지 않는 콘텐츠 gap은 종료를 막지 않는다.

AGENTS.md, work/EXECUTION.json, work/product-acceptance.json, 해당 task 현재 spec/promptFile, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md와28-ALL-MUSCLE-MOTION-PIPELINE.md를 읽어라. 이번 직렬 계획 README와 실제 선행 unit REPORT/validation, work/reports/T66.md 및 work/evidence/T66/implementation-2026-10-02/{final-validation.json,final-blockers.json,family-queue.json}를 확인한다. T25/T59/A/B/C는 필요한 정확한 근거만 재사용한다. 자산 A/B/C의 JSON661개를 GLB661개로 세지 않는다.

최신 사용자 지정은 Luna Max·현재 대화 직접 구현·직렬이다. 과거 Astra/병렬 지시보다 우선한다. 계획/내부 unit은 새 task ID가 아니다. 새 agent/thread/자동 위임/다음 unit 자동 실행/push/배포/임상 기능/병리 editor를 금지한다. 작업 시작 시 dirty 파일/hash를 기록하고 다른 소유 WIP·과거 evidence를 덮지 않는다. 입력이 달라졌으면 영향 dependency만 재검증한다. r13 evidence/원본은 보존하고 새 명시 revision에 출력한다.

전체 근육/뼈/신경 목표와 현재 지원 범위의 제품 acceptance를 분리한다. 542target/563membership/12부위, 근육429/447/232source concepts/462surfaces, HA130·역사163(6/20/135/2), 원본/source-cache/OpenSim_Models/T13/기존 WIP를 보존한다. source-only/local selection/humanReview=not_performed/public rights held는 독립 상태다. source 행/label group을 독립 해부 개념으로 세지 않는다. 없는 mesh/좌우/관계/정확한 footprint/실측 정상축을 만들지 않는다. 실제 원본 관찰+검토된 정성 근거에 따른 재현 가능한 authored 교육용 masks/weights/pivots/trajectory/correctives는 직접 작성한다. native rig 부재만으로 engineering 책임을 자료 gap으로 돌리지 않는다.

기존 단일 viewport/scene/renderer/camera/controller/frame clock 및 common pose state를 유지한다. '움직임으로 이해하기' 하나: 클릭 반복 왕복, 재클릭 부드러운 rest 복원. 느리게/별도 pause/reset 버튼은 넣지 않는다. slider는 autoplay 중단/자세 유지, reduced-motion을 보존한다. 숨김/투명/layer/selection/history/카메라/취소를 재생이 덮지 않는다. T59 기존+30%를 다시 확대하지 않는다. 학생 화면에 task/source/evidence/내부 ID를 넣지 않는다. 필요한 권리 attribution은 기존 정책대로 유지한다.

자동 계약은 이번 지원/변경 집합 전체에 검사한다. 실제 UI는 가족 유형·좌우·변경/충돌·중간 pose를 확인하고 동일 입력 근거는 재사용한다. 전체 suite/12부위 전수 PNG/문헌 검색을 매 unit 반복하지 않는다. 관측하지 않은 GPU/VRAM/메모리는 추정치와 구분한다.

이번 실행은 T66 내부 unit 02만이다. 고관절 굽힘 양측 2후보와 무릎 굽힘 양측 2후보를 실제 구현한다. unit 01이 만든 공통 exporter/변형 계약을 재사용한다.

1. T66-B1의 femur–hipbone 새 containment와 head-pivot-r10 결과를 읽는다. 현재 관통 3정점/원본 overlap/운동 후 새 관통을 구분하고 실제 관절 표면의 위치 및 접촉 trajectory를 작성한다. 구면 fitting residual이 작다는 사실을 정상 관절축 승인으로 쓰지 않는다. 그대로 실패한 pivot 재실행은 하지 않는다.
2. T66-B4와 knee fractional_rotation의 sampled geometry/contact pass를 재사용한다. 실제 Patella source와 검토된 quadriceps 부착 문맥을 연결해 슬개골·넙다리뼈·정강뼈 및 주변 근육의 cooperative trajectory를 구현한다. 슬개골 없이 무릎 정상 시범이라고 등록하지 않는다. 단일 공통 pivot이 부족하면 per-member/coupled trajectory 데이터를 공통 pose 경로에 추가한다.
3. 두 관절에서 fixed/moving/passive/불명확 구조를 근거로 구별한다. 힘줄/관절낭 등 없는 조직을 생성하지 않는다. 근육은 surface deformation, 뼈는 rigid motion의 각각의 계약을 검사한다. sourced 위치와 authored 교육용 trajectory를 구별한다.
4. rest/mid/end 및 보간·복합 pose의 접촉/형상, signed-frame 실제 GLB replay를 검사하고 양측 근육/뼈 직접 선택·slider·smooth rest·hidden 유지까지 실제 UI에서 확인해 등록한다.

이번 성공 조건: 4후보의 실제 접촉/협응/등록 차단 해소. geometry 시험 통과만으로 슬개골 협응 완료나 주작용 완료를 계산하지 않는다. 실패는 engineering blocker이며 자료 gap으로 바꾸지 않는다.

작업 기록: work/evidence/T66/serial-completion-2026-10-02/unit-02/에 REPORT.md, 실제 validation 결과·자산/QC/화면 경로·입력 영향/hash를 남긴다. serial-queue.json의 해당 unit 책임 키에 implemented_verified / processed_with_content_gaps / blocked_by_product_defect를 실제 증거로 기록한다. 자료 gap은 missing source/identity/qualitative relation 등 구체적 자료 부족 근거가 있어야 한다. 단순 exporter/mask/trajectory/연결 미구현이나 기하 실패는 engineering blocker다. 원장만 작성하고 unit 성공으로 끝내지 않는다.

T66 내부 unit 01~10의 성공은 T66 전체 passed가 아니다. EXECUTION T66의 progress에 내부 진척과 제품 차단/콘텐츠 gap을 갱신하고 부모 nextUnit=author-and-integrate-normal-motion-bone-and-nerve 및 partial을 유지한다. spec에는 이번 책임을 내부 unit으로 명시하고 promptFile을 이번 파일로 기록하되 다른 task 상태는 바꾸지 않는다. T66 report는 짧은 진척/현재 차단 링크로 갱신하고 전면 재작성/전체 보고 반복은 unit11까지 하지 않는다. unit11은 본문의 최종 판정 규칙을 따른다. python3 work/tools/sync_execution.py와 --check를 수행하고 소유 변경만 선별 로컬 커밋한다.

종료 시 이번 실제 구현/지원 수와 unresolved engineering/content gap을 구분해 보고하고 멈춘다. 다음 수동 실행 파일은 work/plans/t66-serial-completion-2026-10-02/03-T66-shoulder-forearm-wrist.txt이다. 실제 남은 선행 구현 차단이 있으면 재개할 파일도 명시한다. 다음 파일을 자동 실행하지 않는다.
```
