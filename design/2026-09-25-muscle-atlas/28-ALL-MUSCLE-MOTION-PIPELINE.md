# 전체 근육의 같은 모형 움직임 제작과 병렬 처리

2026-10-02 · 사용자 지시: 초기 확장 근육 목록을 두지 않고 전체 근육을 대상으로 진행한다.
**계획 개정이며 T35 또는 motion 구현의 실행·합격 기록이 아니다.** 27 설계의 앱 acceptance/content completeness 분리는 유지한다. 미래 G4 움직임 범위의 파일럿·소흉근 중심 제한과 과거 표정근 제외 문구는 이번 전체 근육 지시로 대체한다. 과거 task/spec/evidence/사용자 피드백은 수정하지 않는다.

## 목표와 전체 분모

근육을 몇 개 골라 끝내는 방식에서 전체 근육을 동일한 제작·검증 경로로 처리하는 방식으로 바꾼다. 사용자 예시, 제작하기 쉬운 근육 또는 최초 regression 표본을 제품 확장 범위로 고정하지 않는다.

- 기존 제품 분모 **542 targets / 563 memberships / 12부위**는 유지한다.
- 이 원장의 근육 관련 target은 **429개**, 근육 membership은 **447개**다. named muscle 245, part 94, group 58, repeated family 26, complex 6을 포함한다. 이는 서로 다른 실제 근육 429개라는 뜻이 아니다. 전체 개인 근육 수는 기존처럼 null이다.
- 현재 실제 지원 source 근육 **232개 개념 / 462개 표면**도 전수 제작 대상으로 유지한다. 현재 없는 target 형상·정확 대응은 429개 원장에서 빼지 않고 확보/대응/rig/pose/변형 과제를 남긴다. source에만 있는 개념도 삭제하지 않는다.
- 표정·안구·혀·목·몸통·손발·골반/샅까지 대상에 포함한다. 일반 관절 회전과 다른 움직임은 별도 **같은 엔진의 변형 유형**으로 처리한다. 표정근을 제외한다는 과거 제한은 미래 움직임 작업에 적용하지 않는다. source에 없는 피부·혀·눈·신경 형상을 만든다는 허가는 아니다.
- 그룹/갈래/반복 family는 별도 scope다. 일부 member의 움직임으로 전체 그룹 완료를 표시하지 않는다. 좌우와 posture 조건, 여러 작용도 각각 지원 상태를 가진다.
- 첫 실제 표본은 구현 검증을 위한 regression 사례일 뿐이다. 첫 표본이 통과해도 **전체 근육 움직임 목표 완료**로 쓰지 않는다. 소수 표본을 골라 전체 제작 범위를 축소하려면 별도 사용자 변경 지시가 필요하다.

전체 구조·움직임 목표, 실행 task의 책임 완료, 현재 로컬 앱 사용 가능 여부는 서로 다른 상태다. 전체 움직임 완료는 실제 모든 해당 범위가 충족된 경우만 선언한다. 자료 부족으로 아직 만들지 못한 항목은 전체 목표의 잔여 과제로 계속 남는다.

## 현재 실제 구조에서 확인한 문제

T65는 완료했고 다음 task는 T35다. 현행 학습 CTA는 App.tsx에서 disabled이며 실제 같은 모델 근육 움직임의 지원 수는 0이다. 역사 T24의 OpenSim 발 움직임/설명 경로 자산 1건은 원래 근육 표면 수축에 미달한 candidate다. registry의 asset 개수를 실제 learner clip 개수로 바꾸어 읽지 않는다.

현재 DatasetResources는 정적 mesh geometry만 캐시하고 skins/animations를 거부한다. 기존 AnimationSceneAdapter/AnimationPlayback/도메인 상태기는 자산 파싱·clock·취소 정책에 재사용할 수 있지만, 기존 정적 loader에 animation 허용 한 줄을 추가해서 live skeleton/weights를 보존할 수 있는 구조는 아니다. 같은 scene 아래에서 전체 glTF deformation graph를 보존하는 명시적 motion adapter와 sourceKey 결속이 필요하다.

OpenSim의 muscle geometry path는 작용선이며 실제 근육 체적 표면과 다르다. local Arm26에는 팔꿈치 관련 6개 muscle actuator만 있다. Gait 모델의 `pect` 같은 축약명은 대흉근 대응을 뜻하지 않는다. 다운로드한 모델 이름/근육 path/어깨 model 문서의 존재를 현재 ZA 표면의 rig나 정합으로 승격하지 않는다. OpenSim은 적합한 관절/경로 근거가 있을 때 보조 자료로 쓰며 전체 근육 구현의 무조건 선행 조건으로 두지 않는다.

기술 근거: [OpenSim Muscle Editor](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53090145)의 path 정의와 [glTF 2.0 규격](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)의 skin/morph/animation 계약. 실제 repo 관찰은 `work/evidence/motion-all-muscles-plan-2026-10-02/current-capability.json` 참조.

## 공통 구조 — 동작 재사용과 근육별 정확성을 함께 유지

같은 관절 움직임을 여러 선택 근육에서 재사용하되 **그 근육의 실제 source 표면과 부착·갈래 조건에 맞는 변형**은 각각 만든다. 근육마다 별도 viewer/player/코드를 복사하거나 모든 근육에 동일한 scale 효과를 넣지 않는다.

1. **전체 범위 원장**: target, source concept, side/part, 기존 geometry, 기시·정지/작용, 필요한 자료/rig, 움직임 family, 상태를 연결한다. target-to-source 후보와 실제 scope acceptance를 분리한다.
2. **동작/pose 데이터**: 움직이는 뼈·고정 구조·관절 frame·교육용 pose trajectory와 주변 수동 변형을 family 단위로 정의한다. 고정된 하나의 shoulder/hip clip을 모든 자세에 맞는 정상 움직임으로 표현하지 않는다. 공통 동작은 같은 좌표/pose 계약이 성립할 때만 재사용한다.
3. **source별 변형 데이터**: 원본 표면에서 derived skinning weights 또는 morph/corrective deformation을 생성한다. 가느다란·넓은 부채꼴·다관절·분절/반복·비관절 연조직을 같은 계약의 다른 유형으로 지원한다. 같은 family라고 같은 weights/부착점을 복사하지 않는다.
4. **same-scene playback**: 기존 AnatomySceneController/scene/root/renderer/camera를 유지한다. motion은 addUpdate 기반 하나의 frame clock을 사용한다. sourceKey로 정적/derived 표면을 결속하고 rest pose에서 원본 identity/위치/좌우를 검증한다. animation parse resource를 별도의 검은 viewer로 전환하지 않는다.
5. **선택 학습 UI**: 근육 선택→근거 있는 작용 선택→현재 모형에서 실제 변형/몸 움직임→pause/scrub/속도/처음 자세→기시·정지·설명으로 복귀를 공통 구현한다. 여러 근육이 함께 관여하는 동작을 한 근육의 단독 실제 수축량으로 표현하지 않는다.

실측 contraction/힘/활성도/환자 정상 범위를 예측하는 시뮬레이터를 만드는 작업은 아니다. 출처에 있는 해부학적 작용과 제작한 교육용 형상 변형, 정량 생체역학/사람 검토는 분리한다. 물리 FEM이나 실시간 OpenSim solver를 전 근육 표시의 선행 조건으로 늘리지 않는다. 반대로 단순 색 변화/rigid muscle 회전/선 길이/scale만으로 실제 근육 표면 변형을 완료했다고 쓰지 않는다.

현재 HA가 없는 source muscle도 정확한 source/side/part 근거로 제작·로컬 학습 연결이 가능하다. HA130 전체를 바꾸거나 HA ID를 새로 발급하는 우회는 하지 않는다.

## 신경·주변 구조와 복원 계약

- 실제 동작 pose에서 영향을 받는 뼈와 보이는 주변 근육은 대응 변형 또는 검증된 수동 변형을 제공한다. 움직이는 관절을 가로지르는 근육을 정적 제자리에 두어 잘못된 기시정지/관통을 만들지 않는다.
- 부착 뼈 이름 요약만으로 정확한 3D 부착점을 생성하지 않는다. source의 직접 대응/관찰 가능한 표지/derivation 근거를 구분하고 좌표 선택·잔차·적용 범위를 기록한다. 제작자 선택값은 출처 실측값으로 표기하지 않는다.
- T63 신경은 source static pose만 지원한다. 움직임 동안 pose 미지원 신경/강조는 기존 gate로 가리고 rest pose에 복귀하면 사용자의 원래 layer 상태에 맞춰 복원한다. 정적 신경을 움직이는 팔·다리에 그대로 붙이지 않는다.
- 재생 종료/선택·부위 전환/취소/실패/unmount/context loss 뒤, 원본 pose/selection/camera/hidden/layer/presentation을 정해진 계약으로 복원한다. 재생을 이유로 사용자가 숨긴 외복사근이나 끈 layer를 다시 켜지 않는다.
- source mesh/cache를 in-place로 변형하지 않는다. 공유 geometry를 수정해서 반대쪽·다른 instance가 움직이는 버그를 막고 source별 deformation state를 분리한다.

## 순서와 병렬 처리

기존 ID와 순서 **T35→T59→T25→T66→T85→T40**를 유지한다. 새 task ID/자동 스레드/자동 위임은 없다. 사람이 각각 별도 대화에 프롬프트를 넣을 때만 병렬 작업을 시작한다.

| 단계 | 공통 단일 작성자 | 병렬로 가능한 일 | 완료 산출물 |
|---|---|---|---|
| 준비 — 이번 계획 | 고정 전수 배정·실제 입력 hash 준비 | 아직 실행하지 않음 | 준비된 research run-manifest + 실제 snapshot + 검사 |
| T35 | 전수 제작 가능성 원장·family/rig/좌표/지원 계약 통합 | A/B/C 전체 범위 자료·identity/part/작용·rig 입력 조사 | 429 target/232 source 전수 disposition, motion-contract, 공통 제작/검증 규칙 |
| T59 | 공통 exporter/rig adapter/player/loader/cache/복원 및 실제 표본 결속 | T35 조사 완료분 또는 계속되는 자료 준비; 공통 코드 동시 수정 금지 | 작동하는 공통 경로·실제 rig/pose 검증 및 T66용 authoring-run-manifest |
| T25 | 공통 학습 UI/설명/가용성/복원 흐름 검증·수정 | frozen contract 아래 자산 후보 제작은 별도 폴더에서 가능 | 실제 사용자 흐름 합격; 표본으로 전체 범위를 축소하지 않음 |
| T66 | 공통 계약으로 전체 원장 처리·등록·통합·예외 해결 | authoring manifest에 배정된 A/B/C package를 각자 제작 | 제작 가능한 모든 배정 패키지의 실제 자산/검증·원장·미확보 작업; 예시 몇 개에서 종료 금지 |
| T85 | 같은 앱의 전체 지원 clip/pose/좌우/복원·성능 감사 | 서로 다른 패키지의 독립 QA 자료 생성 | 변경/유형 대표 UI와 전수 계약; 발견된 오류 수정 |
| T40 | 실제 로컬 실행·asset 확보·전체 범위 전달 | 해당 없음 | 실행 가능한 앱과 정확한 전체 움직임 잔여 목록 |

병렬 worker 실행은 선택 사항이다. T35 writer는 같은 전수 규칙으로 직접 현재 입력/가능성 계획을 작성할 수도 있다. 진행중인 원문/자산 조사는 필요한 작업으로 남기되, 전체 원장의 계획과 검증된 공통 계약을 만든 후에는 모든 조사 완료를 T59 공통 구현의 일괄 조건으로 두지 않는다. 없는 근거를 완료로 꾸미지 않는다. 자료 조사는 engine 완성을 기다릴 필요가 없다. **자산 제작은 공동 rig/pose/export 계약 고정 뒤** 병렬화한다. 동일 어깨/척추 skeleton을 여러 사람이 별도로 정의하면 합칠 때 다시 제작하므로 공통 skeleton/관절/동작 경로는 단일 작성자가 결정한다. 모든 worker는 자신 폴더에서만 출력하고 common runtime/EXECUTION을 수정하지 않는다. 통합자는 manifest hash/범위 검증을 통과한 출력만 반영한다.

## 준비된 실제 조사 manifest

`work/evidence/motion-all-muscles-plan-2026-10-02/run-manifest.json`은 이번 요청에서 실제 생성했다. source HEAD, source 입력 SHA-256, snapshot hash, 최종 assigned IDs와 소유 outputDirectory가 있다. 파일 경로만 적어 놓고 준비를 후속 작업에 떠넘기지 않는다.

| 조사 worker | 지역의 주 소유 배정 | target | source 개념 | source 표면 |
|---|---|---:|---:|---:|
| A | 머리·목 | 144 | 66 | 131 |
| B | 어깨·팔/손·가슴우리·배허리·골반샅 | 139 | 76 | 151 |
| C | 등·볼기·넙다리·종아리·발 | 146 | 90 | 180 |
| 합계 | 12부위 전체 | **429** | **232** | **462** |

배정은 행정적인 단일 소유 기준이다. 여러 지역에 속한 근육은 원래 membership을 유지하고 다른 worker가 읽어서 교차 참조할 수 있다. target/source 개념은 하나의 worker만 쓰며, 그룹/같은 family의 교차 참조는 통합자가 조정한다. 조사 출력은 production motion acceptance가 아니다.

실행 전 `python3 work/tools/validate_motion_parallel_plan.py`로 실제 입력과 배정을 검사한다. 본문 snap은 필요한 필드만 담아 대형 7MB overlay를 복제하지 않았지만 원본 전체 SHA도 고정했다. coordination용 EXECUTION의 상태 변경만으로 조사 입력을 재배정하지 않는다. 실제 anatomy/geometry/설명 입력이 바뀌면 통합자가 영향받은 항목만 새 명시 revision으로 갱신한다. worker가 임의로 hash/배정을 갱신하면 안 된다.

조사 A/B/C의 `proposals.json`은 header에 runId/assignment/inputHashes/assignedTargetIds/assignedSourceConceptKeys를 그대로 기록하고 targetRows/sourceRows에 배정 전수를 담는다. 원문을 직접 열지 못한 필드, geometry 없는 target도 row를 빼지 않고 필요한 자료와 다음 행동을 남긴다. 미확보를 형상 부재로 확정하거나 기존 HA/rights/review를 승격하지 않는다. 직접 원문 파일 hash와 검토 노트 hash는 다른 필드다.

자산 worker 프롬프트는 **T59가 실제 `work/evidence/T59/authoring-run-manifest.json`을 만든 뒤** 사용한다. 이 미래 파일은 아직 없는 motion contract에 기대는 자료이므로 지금 존재한다고 쓰지 않는다. T59 완료 조건에 manifest 생성·전수 배정·hash 검증을 넣어 과거처럼 필수 manifest 누락 상태로 다음 담당자를 보내지 않는다.

## 완료 기준과 낭비 방지

- T35는 전체 계획을 만들어도 clip 지원이 0인 상태를 정확히 보고한다. T35 계획 pass를 motion 구현 pass로 세지 않는다.
- T59/T25는 공통 경로·학습 UI 책임의 pass다. 표본 성공은 전체 근육 motion 완료가 아니다.
- T66은 전체 manifest를 처리하고 **현재 계약에서 제작 가능으로 확정한 패키지를 모두 제작/통합**해야 한다. 근거가 있는 제작 가능 항목이 미구현인 채 몇 개 예시 성공만으로 pass하지 않는다. 더 필요한 실제 자료/변형 계약은 구체적 blocker/잔여 작업으로 남기고 같은 task 내부에서 해결한다. 실제 미확보 자료는 content gap이며 삭제하지 않는다.
- `wholeMuscleMotionGoal` 상태는 전수 원장의 실제 지원에 근거한다. task completed라도 전체 목표가 partial이면 그렇게 명시한다. ‘전체 근육 지원’은 구현 완료율·범위/side/action이 실제 충족될 때만 표시한다.
- 텍스트 claim, 관절 동작, geometry deformation, 학습 clip, 기술 QA, source rights, 사람 검토는 각각 독립이다.
- 기존 근거/공통 동작/source chapter를 재사용하며 같은 catalog/직접 인용 검색을 이유 없이 반복하지 않는다. 행마다 별도 app 코드를 만들지 않는다. 원문 한 절로 여러 정확한 근육을 처리할 수 있어도 part/variant 의미를 검증한다.
- 전수 자동 검사에는 identity/side/frame/rest pose/skin weights/morph topology/clip binding/영향 구조/취소·복원 정책을 넣는다. endpoint뿐 아니라 실제 중간 pose·최대 굽힘·돌림·관통 위험 사례를 검사한다. screenshot 수를 완료 목표로 삼지 않는다.
- 관련 변경에 대한 검사만 하고 final type/build/browser는 통합 writer가 한 번 수행한다. worker마다 전체 suite/build와 별도 12부위 screenshot을 반복하지 않는다.
- lazy loading은 선택한 family/clip/필요 context만 요청하고 animation buffers/skin/morph/cache의 실제 bytes를 합산한다. 모든 근육 rig를 첫 화면에 올리지 않는다. 시간·목표 수를 미리 약속하지 않고 실제 대표 변형 유형의 제작/QA 시간을 측정해 전수 작업량을 추정한다.

## 다음 프롬프트 파일

기존 canonical T35/T59/T25/T66/T85/T40 promptFile을 이번 전수 목표로 갱신했다. `work/prompts/motion-all-muscles-2026-10-02/README.md`에 순서와 병렬 실행 시점을 정리했다. A/B/C 조사·제작 프롬프트는 각각 별도 파일이다. 이번 요청에서는 조사 worker나 T35/T59 구현을 시작하지 않는다.
