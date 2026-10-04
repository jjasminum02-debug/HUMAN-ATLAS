# T66 — 전체 근육 변형 자산 제작·통합

2026-10-02 · 전수 motion 계획 개정 · 담당 Luna Max.
27 앱 완료 계약과 [28 전체 근육 움직임 계획](../../design/2026-09-25-muscle-atlas/28-ALL-MUSCLE-MOTION-PIPELINE.md) 및 EXECUTION의 현재 promptFile이 기준이다. 과거 파일/보고는 보존한다. 계획 수정은 실행·합격이 아니다.

## 범위

T35/T59 전체 근육 원장과 공통 rig/player/설명 계약으로 429 target/232 source 개념 전체를 처리한다. T27/T28/T45/T46/T29/T31 내부 작업을 흡수한다. 별도 초기 확장 근육 목록을 두지 않으며 제작 가능으로 확정한 모든 source/family 패키지를 구현·검증·등록한다. 미확보/충돌도 전수 원장과 구체적 다음 작업으로 남긴다. 같은 task 내 병렬 candidate 제작과 단일 writer 통합을 사용한다.

## 수행

1. T35/T59/T25의 실제 산출물, work/evidence/T59/authoring-run-manifest.json과 validator를 읽고 frozen 계약·전수 배정·출력 ownership/hash를 검사한다. manifest 없이 과거 임의 배정/근육 shortlist를 추정하지 않는다. 소흉근/견갑대만 처리하는 과거 범위를 반복하지 않는다.
2. 전체 429 target/447 membership과 232 source/462 표면의 action/side/part/geometry/rig/clip 상태를 유지한다. 전체를 작업 큐로 처리하며 batch는 내부 복구 단위다. 몇 개 예시나 10개 후 의무 종료로 범위를 줄이지 않는다. group/repeated family가 일부 member로 완료되지 않도록 정확한 지원 범위를 계산한다.
3. 사람이 자산 A/B/C 프롬프트를 실행했으면 owned candidate package와 생성/검증 근거를 통합한다. 자동 agent/thread는 만들지 않는다. worker 미실행이면 같은 공통 exporter로 직접 처리한다. 공통 rig/axis/frame/key를 worker가 제각각 재정의하지 않게 한다.
4. 가능한 입력은 실제 derived skin/morph/corrective 자산으로 만들고 정확한 현재 source/side/pose에 결속한다. shared 관절 동작을 재사용하되 해당 muscle의 부착·분절·수동 주변 변형·관통/중간 pose를 검증한다. 원본 변형/가짜 geometry·선/scale-only/별도 모델 뷰로 완료를 만들지 않는다.
5. 부족한 실제 입력은 새 단서에 따라 조사/보완하고 source 없는 항목은 null·구체적 확보 작업을 유지한다. 제작 가능으로 확정한 패키지가 미구현이면 실제 미완 unit으로 남기고 같은 task에서 계속 해결한다. 전수 row 작성만으로 clip 구현을 합격 처리하지 않는다.
6. 전수 자동 source/side/rest/weights/topology/track/pose/cleanup/정책 검사와 유형·변경/충돌 실제 화면을 검사한다. whole suite/12지역 PNG는 각 worker가 반복하지 않고 통합 writer가 영향 분석 후 한 번 검사한다. 지원된 실제 자산의 bugs를 해결하고 범위를 정직하게 보고한다.
7. 모든 현재 제작 가능 패키지의 구현/통합 책임을 마쳤을 때 해당 task acceptance를 기록한다. 전체 움직임 목표는 각 target/side/action의 실제 구현에서 별도로 계산하며 remaining이 있으면 wholeMuscleMotionGoal=partial이다. 몇 개 근육 성공으로 전체 구현 완료라고 쓰거나 나머지 근육을 삭제하지 않는다. 다음은 T85다.

## 합격과 보존

542/563/12, 근육 관련429 target/447 membership, 현재232 source 개념/462 표면과 원장 전체를 보존한다. 기존 HA130·역사163(6/20/135/2), source-only·권리 held·humanReview=not_performed·원본/OpenSim_Models/T13/WIP를 유지한다. 자동 위임·새 task/thread·push/배포·임상 기능은 금지한다. 전체 움직임 완료와 해당 task의 실제 책임 완료를 구분하며 일부 clip 성공으로 전체를 완료 처리하지 않는다. report/evidence/EXECUTION의 현재 acceptance 필드를 실제 검증으로 기록하고 sync/check 및 소유 로컬 커밋 후 멈춘다.

## 최신 사용자 정상 모형 개정과 현재 검증 결과

현재 promptFile인 `06-T66-after-results-full.txt`가 과거 근육만의 범위보다 우선한다. 모든 뼈 typed 선택/공동 이동/실제 DOF, 관절 조절, native 신경 정적 주행 및 문헌 포착 맥락을 같은 scene에 연결한다. 병리 editor는 제외한다. 공통 writer가 family/weights/trajectory/corrective를 직접 작성하며 native rig 부재를 engineering 전체의 차단으로 쓰지 않는다. 자동 위임·새 thread는 금지한다.

현재 검증된 subset은 기존 오른쪽 앞정강근 clip과 새 source-family GLB 6개다. 손목 굽힘·어깨 가쪽돌림·엉덩관절 벌림을 좌우에 등록했다. 선택 가능한 source 근육 표면 관찰75개와 고유 source 뼈120개/뼈-family 연결199개는 각각 실제 표면의 관찰과 공동 이동 수다. 근육 주작용 clip은 기존1개이며, 모든 근육 작용/활성도/target extent나 독립 DOF 완료로 승격하지 않는다. native static nerve195 표면은 보존한다.

source-only family는 명시적인 `source_family_bound` 계약으로 정확한 sourceKey/측/frame/pose/생성 GLB/기하·접촉 근거를 결속한다. 기존 canonical joint 계약은 유지하며 HA ID가 없다는 이유로 검증된 source-local 관찰 전체를 금지하지 않는다. 실제 GLB의 signed scale/quaternion/translation/morph를 모든 authored key에서 재생해 원본 frame 좌표와 대조해야 한다. 왼쪽 반사 변환 결함을 발견해 r13에서 고쳤고, 이상적 Python trajectory만으로 export placement를 합격 처리하지 않는다. 교육용 작성값은 출처 실측 정상축/부착 footprint/정상 ROM이 아니다.

최신 T66 결과와 blocker는 `work/reports/T66.md`, `work/evidence/T66/implementation-2026-10-02/final-blockers.json`이 기준이다. 손목 context 차단은 해결했다. 어깨 굽힘·팔꿈치 굽힘·엉덩관절 굽힘의6 후보는 기하/접촉 실패이며 무릎2 후보는 fractional geometry/contact가 통과해도 슬개골·넙다리네갈래근 협응 작성이 남았다. 척추·전완·손발가락·비관절 가족과 full232 source 큐 책임도 남았다. 현재 `partial`을 유지한다. 전체 0-gap·전수 PNG·사람 승인 gate를 복구하지 않는다.


## 직렬 실행 기록 — 내부 unit 01

- 실행 promptFile: `work/plans/t66-serial-completion-2026-10-02/01-T66-deformation-repair.txt`
- 책임: 양측 어깨 굽힘·팔꿈치 굽힘 short-head rejected surface candidate 4개의 deformation repair 및 기존 단일 scene 등록.
- 구현 상태: GLB/loader/mixer/자동 계약 검증 완료. 실제 learner-browser 시각 확인은 Mac 잠금 오류로 미실행이며 pass로 세지 않는다.
- T66은 계속 `in_progress / partial`; 부모 `nextUnit=author-and-integrate-normal-motion-bone-and-nerve` 유지.
- 다음 수동 unit: `work/plans/t66-serial-completion-2026-10-02/02-T66-hip-knee.txt`. unit02 전에 unit01의 실제 learner-browser 확인이 필요하면 잠금 해제 후 그 확인만 재개한다.

## 2026-10-03 직렬 내부 unit 02 실행 기록

- 이번 책임: 좌우 고관절 굽힘 2개·무릎 굽힘 2개 candidate를 실제 변형/협응/같은 scene 선택으로 작성·등록.
- 상태: implemented_verified; 4개 GLB package, 178 source selector relations(50 muscle/128 bone)을 공통 source-family/runtime 계약으로 검증했다. 근육 relation은 passive surface context, 뼈 role은 source별 moving/fixed로 유지한다.
- 검증: 샘플링 geometry/contact, 실제 Chrome 9개 표본, 회귀 14/14, schema/source policy/runtime projection, typecheck, production build. 사람 검토·정상 관절축·정상 ROM·연속 충돌 자유·공개 재배포 권리는 승인되지 않았다.
- evidence: work/evidence/T66/serial-completion-2026-10-02/unit-02/.
- T66은 in_progress / partial이며 부모 nextUnit은 변경하지 않는다. 이번 실행 promptFile은 work/plans/t66-serial-completion-2026-10-02/02-T66-hip-knee.txt이다. unit 01의 실제 UI 환경 차단은 별도 미검증으로 유지한다.
- 다음 수동 내부 unit 입력: work/plans/t66-serial-completion-2026-10-02/03-T66-shoulder-forearm-wrist.txt; 자동 실행 금지.


## 직렬 내부 unit 03 — 어깨띠·어깨·팔꿈치·전완·손목

- promptFile: `work/plans/t66-serial-completion-2026-10-02/03-T66-shoulder-forearm-wrist.txt`
- 수행 범위: 이 다섯 해부학 가족에서 현재 source/action 책임을 같은 scene에 구현한다. intrinsic 손가락은 unit 04 소유다.
- 판정: 66개 action responsibility 중 64개 `implemented_verified`, 좌우 척측수근굴근 자갈래 2개는 방향 근거가 불충분해 `processed_with_content_gaps`; 674개 비작용 문맥 행은 보존했다.
- 양측 견갑대 올림·앞쪽 이동과 전완 엎침을 포함해 U03의 18 family-side package/682 selector relation을 등록했다. 여섯 R5 package의 GLB key pose, 보간 geometry/contact 검사는 통과했다.
- 작용 카드와 자세 관찰을 구분한다. Supinator의 원문 방향 충돌은 미해결, 승모근 작용은 전체군 범위로 유지하며 세부 머리에 상속하지 않는다.
- source-only, 공개 재배포 held, humanReview `not_performed`, 새 HA canonical binding 0을 유지한다. 전체 T66은 계속 `in_progress / partial`, 부모 `nextUnit=author-and-integrate-normal-motion-bone-and-nerve`다.
- 실제 browser, regression, schema, runtime projection, typecheck, build 및 입력/원본 보존 결과: `work/evidence/T66/serial-completion-2026-10-02/unit-03/`.


## 2026-10-05 — 사용자 목표: 한국어 Atlas식 정상 작용 학습

Visible Body 공식 muscle-action 흐름을 참고하여 현재 근육 작용 목록/단일 scene 재생을 수정했다. 전 근육 원장과 authoring 책임을 유지하며 동작·joint family를 관련 근육/측/part에 연결하는 구조로 확장한다. 주변 관절 자세 관찰을 선택 근육의 작용으로 표시하지 않는다. 원문 좌우/기하·동작 결과를 확인하지 않은 generic morph와 source 후보를 실제 작용으로 승격하지 않는다. 현재 목록13 라벨/35 연결/19 표면은 전신 작용 완료가 아니다.

단일 CTA, 실제 clock 기준 toggle, 동작 강조·복귀 fade/1.7배 reset, scrub 유지와 숨김/layer/카메라 복원을 보존한다. 전체0-gap/전수PNG/생리 실측·사람 승인 gate는 도입하지 않는다. D manifest 소유 충돌 및 E runner의 실제 preflight 모순은 anatomy 부족과 별도로 writer가 해결해야 한다. 새 UI의390/1024/1440은 요청값이 아닌 실제 DOM 크기로 검증한다. 이번 전체 판정partial 및 기존 nextUnit을 유지한다. 근거와 다음 수동 재개는 work/evidence/T66/atlas-action-experience-2026-10-04/REPORT.md 및 NEXT-T66-ATLAS-ACTIONS.txt다.
