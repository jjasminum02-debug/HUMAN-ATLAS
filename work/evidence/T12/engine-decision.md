# T12a engine decision — 2026-09-25

**결정:** T12b에서는 Three.js 0.186.1의 GLTFLoader/OrbitControls를 대상으로 렌더러 어댑터를 구현한다. 현재 raw WebGL viewer를 즉시 교체하거나 학습 화면에 실험을 연결하지 않는다. T12b 브라우저 회귀를 통과한 경우에만 실제 viewer 전환을 완료로 기록한다.

## 작은 동등성 실험

`compare-engines.mjs`는 현재 `glb.ts`를 임시 JS로 컴파일한 파서와 실제 GLTFLoader가 **동일한 T07 GLB bytes**를 읽게 했다. `equivalence.json`에 11개 stable mesh ID, 21,480 vertices, 30,032 triangles의 결과를 저장했다. 각 mesh의 positions, normals, index 순서, bounds와 topology hash가 정확히 일치했다. 원본 OBJ 11개와 GLB의 SHA-256도 manifest와 일치했다. mm→m, `[x,z,-y]/1000`, determinant +1, 우측 음수 X, frame, static pose ID를 검사했다. GLTFLoader의 scene node는 identity transform이었다.

OrbitControls로 정면(+Z), 후면(-Z), 우측 측면(-X) 카메라 방향을 구성했다. **키보드 동등성은 기본 설정에서 실패한다.** 현재 viewer는 일반 화살표로 회전하지만 OrbitControls는 일반 화살표를 pan에 쓰고, Shift+화살표로 회전한다. pan을 끈 실험에서 일반 왼쪽 화살표는 움직이지 않았고 Shift+왼쪽 화살표는 회전했다. T12b에서 일반 화살표 회전을 명시적으로 연결하고 실제 브라우저에서 확인해야 한다.

## 선택 근거와 한계

- 현재 raw WebGL은 11개 T07 triangle mesh, 선택·투명·격리·annotation picking을 이미 지원한다. 단일 buffer, 변환 없는 node, 단일 primitive 등 이 파일럿 계약에 맞춘 구현이어서 일반 glTF hierarchy/extension 지원이나 재사용 가능한 엔진 어댑터가 아니다.
- GLTFLoader는 이 자산에서 정확한 기하·triangle 순서를 유지했다. OrbitControls의 기본 카메라 방향도 adapter에서 정할 수 있다. 따라서 Three.js 전환을 **T12b 구현 대상으로 채택**한다.
- 이번 실험은 WebGLRenderer의 픽셀 출력, 투명 정렬, Raycaster의 가장 가까운 표면, 숨김·투명 선택 차단, annotation overlay projection, 브라우저 키 입력과 포커스, FPS/메모리를 검증하지 않았다. 이것들은 T12b 합격 조건이며 미검증 상태다.
- Three.js에서 mesh의 index 또는 world transform이 바뀌는 경우 기존 T09 triangle ID를 재사용하지 않는다. asset hash/topology hash/pose를 재대조하고 draft를 stale로 둔다. 동일 topology를 이 실험에서 확인한 사실은 새 adapter의 미래 동작에 대한 보증이 아니다.
- talus `FJ3385`는 현재 canonical structure ID가 없다. T12b에서 근거로 ID를 해결하거나 mapping에서 명시적으로 제외한다. 현재 source mesh와 provisional null target은 유지한다.
- 모든 crosswalk 관계는 `needs_review`; 엔진 전환만으로 해부학적 동일성이나 부착면을 승인하지 않는다.

## T12b 검증 계약

1. package와 lockfile에 정확한 버전을 고정하고, T07 manifest/GLB 해시 확인 후 11개 ID·기하·topology/pose/frame/units 검사를 adapter 경계에서 유지한다.
2. front/back/lateral, 선택↔카드, 빠른 선택 전환, 전체/주변/선택 확대, 숨김·투명·격리·복원, 일반 화살표/Home/휠/드래그를 실제 브라우저에서 회귀 검증한다.
3. 숨김·투명 표면은 mesh/annotation picking에서 제외하고 Raycaster faceIndex와 T09 triangle ID 일치를 검증한다. overlay는 카메라 변경 후 같은 m 좌표에 붙어야 한다.
4. annotation JSON 왕복을 보존한다. topology 또는 asset revision 변경 시 stale 처리하고 검토 상태를 승격하지 않는다.
5. side instance/meshAssets/meshMappings는 T03 validator의 ref/provenance/좌우 검사에 통과시킨다. talus 처리 결과를 별도 기록한다.

공식 API 근거: [Three.js GLTFLoader](https://threejs.org/docs/pages/GLTFLoader.html), [OrbitControls](https://threejs.org/docs/pages/OrbitControls.html), [설치 안내](https://threejs.org/manual/pages/installation.html).
