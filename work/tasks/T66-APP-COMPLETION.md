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

## 2026-10-05 — wave-2 writer 계약 정정 및 후보 대조

- 실행 산출물: `work/evidence/T66/final-writer-2026-10-05/`.
- wave-2 원 manifest의 D 16행/E 66행은 exact six-field work key와 ID/hash는 frozen `sourceActionScopeQueue`와 일치했지만, 복제된 `disposition/assignedTo/deferredTo`만 `deferred/null/E`였다. writer correction r1은 원 manifest SHA 및 각 scope/source/assignment row hash에 묶인 정정 receipt다. frozen queue와 `sourceDisposition`에서 실제 D/E 배정을 확인해 이 세 필드만 effective in-memory copy에서 교정한다. 원 manifest, assignment snapshot, worker handoff는 수정하지 않았다.
- D/E 실제 runner preflight는 각각 16/66 work key로 통과했다. bone 자료는 muscle source 목록과 분리한 read-only context(D 1, E 16)이며 muscle member나 독립 DOF로 처리되지 않는다. non-empty output root는 소유 기록·symlink·경계·다른 소유자 검사 후 허용하고 신규 출력 경로 충돌은 거부한다.
- 후보 형태가 서로 다르다. D는 여러 family payload와 candidate inventory를 handoff에 포함하지만 별도 aggregate `candidate-package.json`이 없다. E는 56개 후보 GLB와 입력/QC를 가리키는 aggregate index를 제공한다. E용 aggregate validator를 분리했고 여러 candidate input을 단일 payload runner에 넘기지 않았다.
- D의 worker handoff에는 아직 교정 전 manifest-conflict 표시가 남아 있어 이를 덮지 않았다. D 22개 후보 GLB의 action 책임 중 jaw 10개는 실제 edge/area 변형 결함, 2개는 source/relation gap, 2개는 적용 불가다. 2개 `candidate_validated` 행은 family/action이 없는 scope disposition으로 실제 작용·앱 연결 승인을 뜻하지 않는다.
- E 집계 index는 206 artifact 중 205개의 hash/크기가 일치한다. `proposals.json`의 index hash/크기가 현재 worker 파일과 다르다(기대 `d9ccc51c…af52eb`, 949336 bytes; 실제 `92115698…cf09`, 980461 bytes). worker 파일/원장을 수정하거나 현재 bytes로 재기준화하지 않았다. E 56개 GLB 중 local geometry QC는 38 pass/18 fail, action-outcome QC 0 pass, candidate-validated work key 0이다. D/E 앱 등록은 0이다.
- action 학습 지표는 13 label / 35 exact source-action links / 19 source surfaces다. 311 source-action rows는 원장 행 수이지 서로 다른 작용 311개가 아니다. 주변 자세를 선택 근육의 작용으로 승격하지 않았다.
- runner/payload 계약 positive/negative fixture 14건과 기존 protocol regression 8건 통과, D/E 실제 preflight 통과, E aggregate index preflight는 위 hash 불일치로 예상된 실패다. 이 변경은 writer 도구/evidence만 건드렸으므로 학습 runtime/브라우저를 다시 실행하지 않았다. 기존 action UI 증거의 실측 viewport는 825×807이고, 390/1024/1440은 이 실행에서 통과로 주장하지 않는다.
- T66은 `in_progress / partial`, 부모 `nextUnit=author-and-integrate-normal-motion-bone-and-nerve` 유지다. W1-A/B/C, unit03 및 D/E 실제 제작/연결 차단이 남으므로 T85 인계를 하지 않는다. source-only, local selection, public rights `held`, humanReview `not_performed`, HA130, 542/563/12, 역사 163 분류 및 기존 source/WIP를 유지한다.


## 2026-10-05 최신 사용자 개정 — 우선7근육 완성 후 점진 확장

2026-10-05 사용자 개정: 우선7근육군(앞정강근·대흉근·견갑거근·대퇴직근·복직근·외복사근·능형근)의 대표 작용을 양측 available source/part에서 실제 제작·등록·검증하고 현재 지원 신경 주행/지배·관련근육 학습 흐름을 보완한다. 전체 원장·기존 지원 기능과 확장 backlog는 보존한다.

현재 T66 record의 priority-muscle-atlas-2026-10-05 acceptanceContract가 과거 전수 제작 가능 package 일괄완료 gate보다 우선한다. 범위 밖 failed engineering은 별도 deferred backlog로 원래 실패 상태를 보존한다. 실제 지원된 기존 기능의 회귀와 우선 근육의 engineering 미완은 해결해야 한다. 신규 pass는 마지막 통합 실제 검증 후만 기록한다. 현재 partial/같은nextUnit을 유지한다. 이번 신경 표시 수정과 실측 검증은 work/evidence/T66/nerve-and-priority-review-2026-10-05/REPORT.md를 참조한다. 새 수동 프롬프트 순서는 work/plans/t66-priority-atlas-2026-10-05/README.md다.


## 2026-10-05 우선 범위 최종 통합 계약·결과

우선7군의 available20 native source/side/part와22 exact muscle_action binding/13 unique GLB에 대해 현재 지원 앱의 통합 계약을 검사했다. 현재 completed/passed,nextUnit=null이며 whole-content는 partial이다. 최신 실제 근거는 work/evidence/T66/priority-integration-2026-10-05/REPORT.md 및 product-scope.json이다. 이전 full-queue engineering gate는 최신 사용자 우선 범위의 pass 조건이 아니다.

동작 가시성 증대는 무릎/대흉근/견갑거근/능형근의 실제 각도×1.3, 기존+30% T59 보존, 검증된14° 몸통 morph의 projection zoom1.3으로 구현한다. 몸통18.2° 실패 후보는 등록하지 않고 blocked_engineering/deferred로 보존한다. 화면 확대를 정상 ROM 또는 실제 각도 증가로 주장하지 않는다. 원본 morph/주변 구조/정적 신경 pose 제한을 유지한다.

T85는 현재 지원 우선 범위의 UI/성능 품질 검사로 수동 인계하며 턱/얼굴/호흡/E 후보 제작을 추가하지 않는다. T85 record/status는 수정하지 않았다.
