# ADR-001 — 독립 animation-capable GLB loader

- 날짜: 2026-09-27
- 상태: 채택 (T22; 런타임 재생·학습 공개 승인은 아님)

## 결정

기존 `decodeT07Glb`는 단순 정적 메시용으로 유지한다. 움직임 자료는 별도 `loadAnimationScene` 어댑터에서 설치된 Three.js 0.186.1의 `GLTFLoader.parseAsync()`로 읽어 `scene(s)`, 노드 계층, `SkinnedMesh` skeleton/skin attributes와 원래 `AnimationClip`/tracks를 그대로 보존한다. 정적 decoder 결과로 변환하거나 node hierarchy를 평탄화하지 않는다. adapter는 playback mixer를 만들지 않으며 재생 상태·UI는 T23 범위다.

## 표현 선택

첫 후보는 **발목 발바닥굽힘 교육용 bone motion + 단순 설명 경로**다. 이는 bone/joint 장면의 움직임과 근육 형상의 단순화된 경로를 서로 다른 표현으로 보이며, 근육 mesh를 임의 축소하거나 정량 수축을 시뮬레이션하지 않는다. rigged mesh는 별도 표현으로 계약에 남기며 실제로 skin indices/weights, skeleton/node map, clip binding이 확인된 자산에만 사용한다. 합성 테스트의 rigged mesh는 loader 시험에만 쓰고 이 첫 교육용 시범의 자산으로 보지 않는다.

T20 계약의 `illustrative_path`는 경로만 바인딩해 bone motion을 별도로 나타낼 수 없었다. T22는 이를 `bone_motion_with_illustrative_path`라는 명시적 표현으로 확장했다. 이 표현은 `rig.nodeBindings`가 MotionDefinition의 moving bone ID만 정확히 덮고, `illustration.trajectoryBindings`가 MuscleAction의 subject muscle/part ID만 정확히 덮도록 한다. bone과 muscle 경로 ID를 한 배열에 섞지 않는다. 기존 `illustrative_path` 값은 이전 fixture/데이터와의 호환을 위해 유지한다. rigged mesh는 rig만 사용한다.

다만 T21의 `targetJointIds`는 비어 있고 `MotionDefinition`은 0건이다. 근거 있는 joint frame/pivot, 움직임 범위, 고정 구조 및 정적 장면 pose 연결이 아직 없다. 그러므로 T22는 동작 자산을 제작하지 않고 후보 방식을 기록한다. 해당 근거가 확보되기 전엔 어떤 뼈도 움직이지 않는다.

## frame/단위와 입력 게이트

glTF 2.0은 우수 좌표계, +Y up, +Z front, +X left, 길이 m, 각도 rad를 규정한다. 프로젝트 pilot frame과 맞는 `frameId`를 입력 계약에 요구하고 GLTF 파일 자체는 `units=m`만 허용한다. 로더가 mm를 조용히 0.001배 하거나 축을 회전하지 않는다. 변환이 필요한 원본은 파생 파이프라인에서 출처/툴/설정/입력·출력 hash를 남겨 GLB로 정규화한다. 현재 `HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR` 이외의 frame은 거부한다.

## source → derived → learner

1. exact source/file revision, license와 required attribution, source SHA-256을 검토한다.
2. 비파괴 복사/변환으로 source와 derived output을 분리한다. generator/tool version와 재현 설정, axes/units/pose, side, rig node map, clip name/duration, output SHA-256을 기록한다.
3. GLB source hash, declared frame/units, animation target nodes, representation에 맞는 rig/path bindings, skin attributes, clip duration을 자동검사한다.
4. 사람 해부학 검토와 learner-release 판단을 별도 유지한다. 기술 통과나 AI 대조는 사람 승인 상태를 바꾸지 않는다.

T22 조사 당시 BodyParts3D-derived calf GLB는 정적 11-node/11-mesh이며 skin/animation/morph가 없었다. OpenSim Gait2392 model file은 운동 모델이지 clip asset은 아니며, 현재 checkout에 `.mot`/`.sto`/`.trc` 또는 GLB export가 없고 authoring CLI도 확인되지 않았다. T20 `motionAssets` 및 T21 `motionDefinitions`는 계속 빈 배열이다. 후보와 hash는 `atlas-data/motion/motion-asset-sources.json`에 기록한다.

## 비용/소유권

Three.js manual에 따라 공유 geometry/material/texture/skeleton은 imported bundle 범위 안에서 객체 identity별 한 번만 정리한다. ImageBitmap은 texture dispose만으로 닫히지 않을 수 있어 동일 bitmap을 한 번 닫는다. adapter 결과를 복제해 별도 lifetime으로 쓰는 동작은 지원하지 않는다. 향후 공유 clone이 필요하면 T23에서 소유권/ref-count 규칙을 먼저 설계한다.

## 근거 자료

- [Three.js GLTFLoader docs](https://threejs.org/docs/pages/GLTFLoader.html) — `parseAsync()` 결과에 scenes/animations 포함.
- [Three.js SkinnedMesh docs](https://threejs.org/docs/pages/SkinnedMesh.html) — skeleton 및 skin index/weight 요구.
- [Three.js cleanup guide](https://threejs.org/manual/pages/how-to-dispose-of-objects.html) — geometry/material/texture/skeleton 자원별 dispose와 공유 자원 주의.
- [Khronos glTF 2.0 specification](https://github.com/KhronosGroup/glTF/blob/main/specification/2.0/Specification.adoc) — RH/+Y/+Z/+X, meters/radians.
- [BodyParts3D archive license](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html) — 2025-02-27 갱신 CC BY 4.0, 요구 attribution.
- [OpenSim Gait2392 model page](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53086215) — model file/result files 범위, Gait2392 joint/frame 배경.
- [OpenSim model table](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53090607) — Gait2392 모델 행의 CC BY 3.0 표시.

## T41 후속 결정 (2026-09-27)

T22 당시 첫 후보였던 발바닥굽힘은 역사적 결정으로 위에 보존한다. 현행 첫 시범 대상은 `HA-M-000003` 전경골근/앞정강근/Tibialis anterior의 **오른쪽 발목 배측굴곡**이다. 현행 source manifest의 후보만 이에 맞춰 갱신했으며 joint 좌표나 clip은 생성하지 않았다.

첫 운영 입력은 self-contained GLB로 한정한다. GLB JSON의 buffer/image URI는 parse 전에 거부한다. 재생 root는 `gltf.scene`이며 rig/path binding, 모든 clip track target, active skin skeleton의 bone은 이 root 아래에 있어야 한다. `gltf.scenes`의 다른 root는 소유 자원 해제를 위해 보관할 뿐 재생 binding으로 인정하지 않는다. 외부 의존 자산을 지원하려면 별도 출처/hash/license 및 취소·정리 계약을 후속 설계에서 먼저 정의한다.
