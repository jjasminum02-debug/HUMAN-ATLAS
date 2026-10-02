# 현재 다음 실행

자동 생성. 편집 원본은 [EXECUTION.json](EXECUTION.json). 역사 handoff/자료 개수로 다음 작업을 결정하지 않는다.

- 확인된 최근 진행: T25 / accepted
- 다음 ID: **T66**
- 현재 지원 앱 완성: T100 통합 마무리 → T80 사용 감사/보완 → T58 UI·성능 최적화. 전체 콘텐츠 확보는 별도 상태로 유지한다.

```text
HUMAN ATLAS에서 T66만 수행해라. 담당 Luna Max · 현재 대화 직접 구현.

최신 실제 결과 반영 — T25/A/B/C 종료 후 실행 순서

이번에는 work/plans/normal-motion-and-nerve-2026-10-02/RESULTS-REVIEW.md를 먼저 읽어라. T25는 04403fd1b5e73e1174da2332f12b36b7e7c3b7e0에서 completed/passed이지만 contentCompleteness=partial이다. A/B/C는 정확한 배정 210/215/236개, 합계661개 package JSON을 만들었으며 새 GLB/변형 입력/clip 생성은 모두0이다. 기존 T59 오른쪽 앞정강근 하나만 실제 재생된다. 원장 작성이 자산 제작 완료라는 전제로 시작하지 않는다.

내부 unit 0 — 실제 UI 회귀 수정:
현재 MotionLearningPanel.tsx는 일시정지/계속재생, 별도의 처음 자세로 돌아가기, 보통/느리게 버튼을 다시 넣었다. 이는 최신 사용자 요구와 다르다. T25의 신경 관계/설명 연결/근육 layer-off guard는 유지하고, '움직임으로 이해하기' 단일 버튼 클릭 반복 왕복→재클릭 반복 중단 및 부드러운 rest 복원으로 되돌린다. 느리게/별도 pause/reset 버튼을 제거한다. scrub 자세 유지와 reduced-motion 접근성은 보존한다. T59 기존 +30% 자산을 다시30% 확대하지 않는다. 실제 브라우저로 재생/재클릭/복원/hidden/layer/카메라를 확인한다. T25 상태나 역사 report를 덮지 않고 T66에서 발견/수정한 회귀로 기록한다.

내부 unit 1 — 부족한 입력을 생성하는 단일 작성자 역할:
A/B/C는 공통 rig/axis/pose를 수정할 수 없고 r2에는 발목 family만 있다. worker가 자신의 delta/mask 입력을 작성해야 했지만 실제로는 입력 누락 기록만 반환했다. 현재 author_source_surface_motion.py는 inspected sagittal arc와 보수적인10도 상한 등의 발목 검증 제약이 있으므로 모든 관절에 무조건 적용하지 않는다. T66 공통 writer가 다른 관절/비관절 가족에 필요한 공통 계약과 authoring 기능을 실제 구현한다. family별 관찰 가능한 source landmarks, 의미 있는 DOF/pose/주변 moving-fixed-passive 구조, 명시 범위를 먼저 작성하고 검증한다. 기존 발목의 품질/범위 제약은 보존하며 새 family의 검증된 범위는 별도 데이터로 정의한다. 현재 제작 책임을 '입력이 없으니 불가'로 다시 끝내지 않는다.

내부 unit 2 — authored engineering과 anatomy fabrication 구별:
원본 mesh를 직접 관찰하고 확인된 정성적 작용/부착 근거를 사용해 재현 가능한 vertex masks, weights, 교육용 pivot/trajectory/corrective를 작성하는 것은 이번 구현 업무다. 이를 source 실측 부착점/생리량/정확 정상축/neutral pose로 포장하지 않는다. 없는 mesh/좌우/해부 관계/정확 footprint는 만들지 않는다. native rig 또는 upstream measured coordinate가 없다는 이유만으로 근거 있는 교육용 작성 전체를 금지하지 않는다. 실제 관찰 근거가 부족한 영역은 미확정으로 유지한다.

내부 unit 3 — 행별 근거 재사용과 source 범위 구현:
C는 source concept90개 중49개 direct_source_text 및1개 qualified_secondary_evidence 작용 상태를 기록했다. 이것을 바로 verified scope로 올리지 말고 T59 research-adoption과 실제 field locator/조건을 대조해 재사용 가능한 근거를 골라 작성한다. A/B 역시 현행 source별 근거를 확인한다. 전체 TA2 target/group/좌우 extent 승인까지 기다려 이미 정확한 source identity/side/part에 묶을 수 있는 local source 시범을 일괄 금지하지 않는다. source 범위 시범은 sourceKey로 구현하고 target/group 완료 수는 별도로 유지한다. A/B/C 조사·원장/hash 검사를 처음부터 다시 돌리지 않는다.

내부 unit 4 — 실제 제작/등록과 나머지 제품 범위:
가족 계약→source별 authored 입력→derived 자산→rest/mid/end·부착/기하·주변 문맥 검증→같은 scene 등록 순서로 전수 큐를 처리한다. 전체 관절/근육을 대상으로 하고 임의 초기 shortlist를 만들지 않는다. 공통 가족의 품질 표본은 검증 수단이며 나머지 제작 가능 패키지의 생략 사유가 아니다. 사람에게 새 입력을 직접 만들어 달라고 넘기지 말고 현재 자료와 도구로 할 수 있는 작성/검증까지 직접 수행한다. 실제 자료 부족과 구현해야 하는 engineering 입력을 분리해서 보고한다. 이후 아래 본문의 모든 뼈 직접 움직임/관절 조절/신경 주행·포착/검증·인계 범위를 수행한다.

T25 또는 A/B/C 재실행을 선행 조건으로 두지 않는다. 새 agent/thread/자동 병렬 실행은 금지한다. 다른 task의 common 파일 작성이 끝난 현재 결과에서 T66 단일 writer로 진행한다. 기존r2/worker evidence와 WIP를 보존한다.


AGENTS.md, work/EXECUTION.json, work/product-acceptance.json, 해당 task의 현재 spec/promptFile, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, 28-ALL-MUSCLE-MOTION-PIPELINE.md, work/plans/normal-motion-and-nerve-2026-10-02/README.md 및 T35/T59/T25와 자산 A/B/C의 실제 최신 report/evidence를 읽어라. 아래 최신 사용자 범위는 과거 소수 근육/신경 목록 및 근육만 선택하는 UI 제한보다 우선한다. 현재 네 작업을 다시 실행하거나 기존 후보/manifest를 덮지 않는다.

이번 목표: 정상 모형에서 전체 근육과 모든 뼈의 움직임 기능을 같은 scene으로 제공하고 신경들의 주행 흐름·포착 맥락을 공통 카드에 연결한다. 병리적 파열/압박 변형/질환 editor는 정상 모형 이후 단계이며 이번에는 구현하지 않는다. 사진은 정상 구조 관찰과 관절 조절 UI의 참고다. 어깨/몇 개 근육/특정 신경을 초기 확장 범위의 상한으로 삼지 않는다.

542 target/563 membership/12부위, 근육429 target/447 membership/현재232 source concepts/462 surfaces, HA130, 역사163(6/20/135/2), 원본/source-cache/OpenSim_Models/T13/기존 WIP를 보존한다. 뼈·신경의 실제 고유 개념/표면/측/membership 분모는 원장과 identity를 대조해 별도로 계산한다. source 행 수를 독립된 해부 개념 수로 쓰지 않는다. source-only/local selection/humanReview=not_performed/public rights held는 독립 상태다. 자료 없는 geometry/좌표/부착점/binding/승인을 만들지 않는다.

1. T59 최신 report가 지정한 r2 authoring manifest와 문서화된 실제 verifier를 확인한다. T25 설명·신경 관계/선택 계약과 A/B/C candidate를 실제 hash/assignedPackageIds/소유 경로에 따라 인계받는다. 후보와 등록/브라우저 검증을 구별한다. UI/hash 변경만으로 geometry/pose가 같은 모든 자산을 stale 처리하지 않는다. 실제 dependency 변경은 영향 package만 기록하고 새 명시 revision을 사용한다. 현재 네 작업이 아직 공통 파일을 수정 중이면 해당 통합 쓰기는 완료 후 수행하고 독립 읽기/분석을 계속한다. 자동 worker/thread 생성은 금지한다.
2. 전체 근육/뼈 원장을 하나의 joint-motion family 계약에 연결한다. T59는 실제 발목 family 한 개만 검증했으므로 이를 모든 근육/뼈에 그대로 적용하지 않는다. 가족별 source frame/rest reference/DOF/회전순서/교육용 각도 범위·조합/협응/주변 구조를 실제 작성한다. 어깨-빗장뼈-어깨뼈, 팔꿈치/전완, 손목/손, 고관절, 무릎/발목, 척추 및 비관절 근육 유형의 필요를 전수 큐로 처리한다. shared family/axis/rig/pose는 단일 writer가 정의하고 source별 변형 입력·자산은 데이터로 생성한다. 부족한 공통 입력을 계속 미확보라고 반복하는 것으로 구현 책임을 끝내지 않는다.
3. 근육은 실제 원본 표면의 skin/morph/corrective를 제작하고 기시정지·갈래/분절·넓은 부착·다관절·주변 수동 조직·중간 자세·관통을 검증한다. authored 값과 출처 실측값을 구분한다. rigid/scale-only/색 변화/선 길이로 근육 표면 변형을 대체하지 않는다. 힘줄/관절낭/관절와순 등 추가 조직은 실제 source/identity/권리/placement가 있을 때 등록하며 사진만으로 생성하지 않는다. 이미 검증한 클립의 동일 입력 검사를 반복하지 않는다.
4. 모든 뼈의 직접 선택 학습 기능을 구현한다. 현재 뼈 카드의 관련 근육 링크와 근육 시범의 동반 TRS는 뼈 직접 움직임 기능의 완료가 아니다. bone→joint/family/action 관계와 typed subject binding을 추가하고 뼈 선택→관절/가능한 움직임 안내→움직임으로 이해하기→각도 관찰→복원으로 연결한다. 직접 운동/공동 이동/고정 지지/미확정은 실제 근거로 구분한다. 각 뼈에 독립 DOF를 강제로 만들지 않는다. rigid한 뼈 운동은 정상 표현이며, 기존 근육 변형 validator를 완화하는 우회 없이 subject kind별 계약을 검사한다. 근육과 뼈를 선택할 때 같은 가족 자산/player/pose를 재사용한다.
5. 기존 단일 viewport/scene/renderer/camera/controller/frame clock을 유지한다. 기본 버튼은 '움직임으로 이해하기' 하나: 클릭 반복 왕복, 재클릭 부드러운 rest 복원. 제거한 느리게/멈춤/처음 자세 버튼을 복구하지 않는다. 펼치는 관절 조절에는 실제 지원 DOF별 slider/각도/검증 범위를 제공한다. slider 조작 시 autoplay를 중단하고 해당 자세를 유지한다. clip 시간/관절 각도/변형이 하나의 pose state를 사용하며 unsupported 각도 조합을 차단한다. 카메라/hidden/layer/selection/뒤앞/취소·복원을 보존한다. 각도는 교육용 자세이며 개인 정상 ROM·힘/활성도 추정값으로 표시하지 않는다.
6. 정상 구조를 깊이 관찰할 수 있게 muscle/tendon 대비, 주변 투명도/숨김 유지, 필요할 때 clipping/단면 관찰을 기존 presentation 경로에 연결한다. 별도 viewer/모형으로 바꾸지 않는다. 관찰을 위한 분리 간격을 제공하면 정상 관절 간격·병리 변화와 혼동되지 않게 presentation state로만 처리한다. 학생 화면에 source/task/evidence/내부 IDs를 넣지 않는다.
7. 신경 학습은 특정 신경/질환 목록을 새로 선정하는 기능이 아니다. 실제 신경 전수 원장과 기존 T25 claims를 재사용하여 정상 주행 흐름과 문헌상 포착 가능 구간을 공통 카드에 정리한다. 혼합 raw nervous-system collection의 비신경 구조를 신경 분모에 넣지 않는다. 각 신경의 이름/분지/측/주행 구간/주변 조직/포착 맥락/변이/근거/화면 연결을 별도 필드로 유지한다. 사용자 예시의 대퇴피·견갑배·액와·요골·정중신경만으로 범위를 제한하지 않는다. 대퇴피신경의 외측/후방 개념과 대퇴신경을 합치지 않는다. 기존 검증된 지배근/감각 정보는 보존하되 새 운동 지배 전수 확보를 주행·포착 설명의 필수 조건으로 만들지 않는다.
8. 정상 신경 geometry는 T61 raw 후보/T63 평가·변환 경로를 재사용해 실제 원본 Curve/mesh에서 등록한다. source hash/frame/pose/측/분지/placement/권리 예외를 확인한다. 이름이나 단순 두 endpoint로 가짜 신경 주행을 만들지 않는다. 텍스트 주행/포착 support, 정적3D, 움직임 pose, 포착 좌표 결속을 각각 계산한다. 실제 좌표/주변 조직이 없으면 검증된 텍스트를 제공하고 가짜 점/깊이/압박은 만들지 않는다. 정적 신경은 미지원 운동 pose에서 가리고 rest에서 user layer 상태대로 복원한다. 동적 신경은 실제 deformation/slide/분지 연속성을 검증했을 때만 표시한다. 가까움/교차만으로 병변을 판정하지 않는다. 개인 진단·검사 추천·치료·자침 기능은 구현하지 않는다.
9. 전수 자동 검사는 지원한 subject/source/측/범위/pose/부착/트랙/기하/취소·복원/정책/역관계를 포함한다. 실제 시각 QA는 12부위와 변형·관절 유형/변경·충돌/중간·복합 pose에 집중한다. 390/1024/1440의 근육·뼈·신경 선택/검색/카드/재생·각도 조절/깊은 관찰/숨김·복원을 확인한다. worker마다 전체 suite/전수 PNG를 반복하지 않는다. 관련 typecheck/build와 영향받는 실제 흐름을 최종 한 번 검증한다.
10. 계획/행 작성만으로 pass하지 않는다. 현재 근거와 계약에서 제작 가능으로 확인한 패키지 및 검증된 설명의 미연결을 실제 해결한다. 실제 자료 부족은 target/측/action/뼈/신경별 구체적 gap으로 남기고 전체 0-gap·전 형상/신경 pose·사람 승인을 task gate로 재도입하지 않는다. 필수 지원 기능 결함은 같은 task에서 수정하며 남으면 partial/같은 nextUnit을 유지한다. 합격 시 completed/passed,nextUnit=null,contentCompleteness 및 wholeMuscleMotionGoal/wholeBoneMotionGoal/nerveCourseCoverage를 실제 지원 수로 별도 기록한다. 미완 콘텐츠가 있으면 전체 해부학/정상 모형 완성으로 쓰지 않는다.

report/evidence와 해당 EXECUTION record에 acceptanceScope/contractRevision/productReadiness/contentCompleteness/knownContentGaps/unresolvedProductBlockers를 남긴다. 합격 progress.productAcceptance는 contractRevision=app-completion-2026-10-01, 실제 acceptanceScope, productReadiness, contentCompleteness, knownContentGaps, unresolvedProductBlockers=[], evidence=[실제 경로]를 기록한다. 최신 사용자 범위의 계약 개정은 T66 소유 record/spec에만 명시하고 다른 task 상태를 바꾸지 않는다. python3 work/tools/sync_execution.py 및 --check, 소유 변경만 선별 로컬 커밋한다. 다음 task 자동 실행/새 번호·thread/자동 위임/push/배포는 금지한다.

종료 후 다음 ID는 T85다. work/plans/normal-motion-and-nerve-2026-10-02/04-T85-full.txt를 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```
