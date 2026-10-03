# 현재 다음 실행

자동 생성. 편집 원본은 [EXECUTION.json](EXECUTION.json). 역사 handoff/자료 개수로 다음 작업을 결정하지 않는다.

- 확인된 최근 진행: T25 / accepted
- 다음 ID: **T66**
- 현재 지원 앱 완성: T100 통합 마무리 → T80 사용 감사/보완 → T58 UI·성능 최적화. 전체 콘텐츠 확보는 별도 상태로 유지한다.

```text
HUMAN ATLAS에서 T66 병렬 준비와 공통 처리 경로만 직접 구현해라. 담당 Luna Max. 이것은 T66 내부 실행이며 새 task가 아니다.

AGENTS.md, work/NEXT.md, work/EXECUTION.json, work/product-acceptance.json, T66 현재 spec/promptFile, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md와28-ALL-MUSCLE-MOTION-PIPELINE.md, 이번 계획 README를 읽어라. unit01/02/03 실제 최신 report/evidence와 현재 runtime을 읽되 이번 책임과 무관한 과거 원장 전체를 반복 조사하지 않는다.

최신 사용자가 병렬 분업을 허용했다. 과거 모든 작업을 직렬로 하라는 계획은 이번 명시적 분업 범위에서 대체한다. 담당은 Luna Max·현재 입력받은 대화 직접 구현이다. 자동 새 task ID/thread/agent 발급, 다음 단계 자동 실행, push/배포/임상 진단·치료·자침·병리 editor는 금지한다. 다른 담당을 실행하려고 자동 위임하지 않는다.

542targets/563memberships/12부위, 근육429/447/232source concepts/462surfaces, HA130·역사163(6/20/135/2), 원본/source-cache/OpenSim_Models/T13/기존 WIP를 보존한다. 실제 뼈·신경 고유 개념과 source/label group 분모는 구별한다. source-only/local selection/humanReview=not_performed/public rights held는 독립 상태다. 없는 원본/측/해부 관계/정확 footprint/실측 정상축을 만들지 않는다. 실제 source 관찰과 정성적 부착/작용 근거에 따른 authored 교육용 masks/weights/trajectory/correctives는 구현 책임이다. native rig 부재나 exporter 미작성 자체는 자료 gap이 아니다.

기존 단일 scene/renderer/camera/controller/frame clock과 pose state를 유지한다. CTA는 '움직임으로 이해하기' 하나: 반복 왕복→재클릭 smooth rest. 별도 느리게/pause/reset을 복구하지 않는다. slider는 autoplay를 중단하고 자세를 유지한다. hidden/layer/history/선택/카메라/취소/late response·reduced-motion을 보존한다. T59 이미+30%를 다시 확대하지 않는다. 학생 UI에 source/task/evidence/내부 ID를 넣지 않는다. 필요 attribution은 정책대로 유지한다.

현재 학습 기능 acceptance는 정확한 source·측·부분·작용 관계, 해당 방향의 교육용 자세, 실제 선택 표면 변형, 같은 장면의 뼈 문맥 및 복원이다. 근육 활성도/힘/생리적 수축량/개인 정상 ROM·실측 축을 추정하는 기능은 요구하지 않는다. '정성적 작용 학습 시범'과 '수동 자세 관찰'은 별도 binding 상태다. 검토된 작용 근거 없이 수동 변형을 주작용 시범으로 바꾸지 않는다. 반대로 실측 활성도/정확 footprint가 없다는 이유만으로 근거 있는 교육용 작용 시범 전체를 금지하지 않는다. canonical/target extent 승인은 source-local 교육 기능과 구별한다.

검증은 실제 생성 GLB의 signed scale/reflection·frame·tracks·key 및 중간 보간, geometry/contact/끝점/부착 문맥/side/scope/정책을 포함한다. 원본 overlap과 새 관통을 구별하고 source/member별 검사 범위를 기록한다. 모든 실제 defect는 유지하고 기준을 몰래 완화하지 않는다. 모든 정상 package에 실패 사례의 r33/초고밀도 보간 설정을 기본 적용하지 않는다. 위험 지표와 재현 primitive가 있는 구간을 추가 세분하고 기존 통과 범위는 재사용한다.

전수 작업 키는 (family,side,action,sourceKey,part,poseContractRevision)다. 같은 source가 다관절 family에 여러 번 속할 수 있다. 고유 sourceKey 수, source-action rows, target-side-action extent, unique GLB hash/URI 수를 따로 집계한다. 동일 source/GLB를 여러 selector가 사용해도 자산 제작 수를 중복 계산하지 않는다. 전체 근육 범위를 유지하며 임의 상위N개/예시 shortlist로 줄이지 않는다.


선행00의 unit03 공통 작성 checkpoint를 확인한다. 공통 파일을 다른 실행이 아직 수정 중이면 그것과 겹치지 않는 읽기/계획 작업을 하고 snapshot 확정만 보류한다. unit03 미해결 가족을 삭제하거나 전체 pass라고 쓰지 않는다.

1. family/source/action 전수 큐를 최신 실제 입력에서 만든다. A=hand-digit(기존unit04), B=hip/knee/ankle/foot-digit 남은 action(기존unit05), C=cervical/thoracolumbar/rib-respiration(기존unit06), D=jaw/hyoid-larynx/pharynx(기존unit07), E=eye/facial/tongue/pelvic-floor(기존unit08), F=실제 전수 신경 course/entrapment 설명(기존unit10)로 책임을 명시한다. unit03 잔여 상지 예외와 미배정 분류는 integration writer 책임이다. source 중복은 다관절 연관이면 허용하되 동일 작업 키 이중 배정은 금지한다. 모든 원장 행은 assigned/deferred-with-exact-reason/unsupported-evidence 중 어디 있는지 보존한다.
2. 기존 source_geometry/containment/phase solver/GLB decode/export/검증을 대표 일반 package 하나와 과거 실제 실패 하나에서 profile한다. decode·solver·export·QC·JSON·UI 준비 시간을 구별한다. 재사용 가능한 decode/rest topology/원본 overlap/공간 검색/pose cache를 측정된 병목부터 구현한다. cache key에는 source bytes/frame/side/geometry/weights/pose/validator revision/정책이 들어가야 한다. geometry는 같고 UI hash만 바뀐 경우 재제작하지 않는다. swept bounds 없이 정적 rest bbox만으로 접촉 검사를 생략하는 우회는 하지 않는다.
3. exact winding vector화/후보쌍의 보수적 broad-phase·동일bytes 파싱 재사용 등 현재 코드에서 유효한 개선을 선택한다. 이미 cache가 있는 경로를 다시 만들지 않는다. 동등 입력에서 QC 결과가 보존되는지 검사한다. 소요 시간 감소가 측정되지 않으면 최적화 완료라고 쓰지 않는다. unrelated 전체suite/빌드가 병목이라고 가정하지 않는다.
4. candidate 입력/출력 공통 계약과 worker CLI/harness를 구현한다. family는 데이터로 정의하고 worker가 자기 output 아래 authoring 함수를 추가할 수 있게 한다. 공통 schema/renderer/runtime는 worker가 수정하지 않는다. 공통 axis/rig/pose를 덮는 대신 family-local namespaced authored 계약을 입력으로 작성한다. shared source frame/public geometry identity/serializer/QC 계약은 frozen 코드로 고정한다. tongue등 비관절 기능 확장은 worker-local 코드 또는 정확한 patch proposal로 제출할 수 있어야 한다. 전체 가족의 anatomy 입력을 writer가 미리 만들어야만 worker가 시작하는 gate를 만들지 않는다.
5. manifest는 외부에서 기다리지 말고 이번 writer가 work/evidence/T66/parallel-completion-2026-10-03/wave-1/run-manifest.json과input-snapshot/을 실제 생성한다. runId·계약 버전·assignment별 정확한 assignedWorkKeys/assignedSourceKeys/assignedNerveRowIds·worker output root·입력path/hash/bytes·필수snapshot·추가참조 허용 범위·common files no-write 목록을 넣는다. compiled source bytes는 immutable 실제 path/hash로 결속하고 필요한 metadata/claims/exporter/QC code는 frozen snapshot으로 복사한다. private module의 부모 경로 ROOT 오류가 없도록 명시적인 repo root/input root/output root를 받게 한다. worker가 live 공통 bundle을 쓰지 않도록 실제 dry run으로 확인한다.
6. wave1은 A/B/C geometry 최대3명+F text1명이다. geometry 담당은 처음엔각CPU process1/BLAS1thread로 시작하고 메모리·wall time을 관찰한 뒤 필요한 만큼만 조정한다. 전역 '모든코어' 사용을 금지한다. writer는 worker가 읽는 frozen 코드를 바꾸지 않는다. 새 공통 개선이 필요하면 새revision으로 영향 assignment만 재실행한다.
7. 준비 산출물로 끝내기 전에 실제 기존 package 하나를 worker harness의 owned temp 경로에서 처리해 입력→실제GLB→QC→handoff가 동작함을 검증한다. 후보 지위이며 새 앱등록을 중복하지 않는다. manifest hash/ownership/정확 작업 키 coverage 및 동등QC를 확인한 뒤 worker-ready를 기록한다. dry run은 제작 범위의 상한이 아니다.

공통 writer는 기존 변경 소유/hash를 먼저 확인하고 이번 실행에 필요한 공통 경로만 수정한다. 예산 변경은 이유와 품질 영향을 명시한다. 의미 검토 묶음은 복구 단위이며 10개 후 의무 종료나 단서 없는 같은 검색/실패 재시험은 하지 않는다. report/evidence/EXECUTION은 실제 결과에 따라 갱신하고 부모T66은 최종 통합 전까지partial 및 기존nextUnit을 유지한다. python3 work/tools/sync_execution.py와 --check를 수행하고 소유 변경만 선별 로컬 커밋한다. 다른 task 상태는 바꾸지 않는다.

종료 후 wave1 worker A/B/C/F의 네 파일02·03·04·05를 동시에 수동 실행하도록 안내하고 멈춰라. 자동 worker/thread는 만들지 않는다. run-manifest를 실제 만들지 못했으면 불가 원인/수정만 구체적으로 남기고 worker-ready라고 하지 않는다.
```
