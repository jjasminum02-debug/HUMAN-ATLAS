# T59 — 전체 근육용 공통 변형·제작·재생 경로

2026-10-02 · 전수 motion 계획 개정 · 담당 Sol High.
27 앱 완료 계약과 [28 전체 근육 움직임 계획](../../design/2026-09-25-muscle-atlas/28-ALL-MUSCLE-MOTION-PIPELINE.md) 및 EXECUTION의 현재 promptFile이 기준이다. 과거 파일/보고는 보존한다. 계획 수정은 실행·합격이 아니다.

## 범위

T35의 전체 근육 계약에 따라 같은 전신 scene에서 원본 source 표면의 derived 변형/관절 움직임을 제작하고 공통 player/CTA/취소/복원을 구현한다. 근육별 runtime 코드나 별도 viewer를 만들지 않는다. T60를 흡수한다. 실제 검증 표본은 공통 경로 검증 수단이며 전체 429 target/232 source 제작 범위를 축소하지 않는다. T66용 전수 authoring manifest와 hash/validator를 실제 남긴다.

## 수행

1. T35 실제 report/전수 원장/motion-contract, 준비된 research manifest와 실제 A/B/C 근거를 읽는다. 전체 근육 목표와 현재 실제 제작 가능한 입력을 구분한다. 원본/OpenSim_Models을 수정하지 않는다.
2. 기존 static loader가 animation graph를 거부하고 geometry만 캐시하는 지점을 실제로 해결한다. 전체 glTF skeleton/skin/morph/clip graph를 유지하는 공통 motion adapter를 기존 scene 아래에 결속하고 sourceKey/frame/rest-pose/hash를 검증한다. AnimationSceneAdapter/player 정책과 controller.addUpdate를 재사용해 한 renderer/camera/frame clock을 유지한다.
3. reproducible exporter/derivation 경로와 source별 weights/morph/corrective 입력·관절/pose/family 패키지 계약을 구현한다. source geometry 공유 cache는 불변이며 instance별 deformation state를 분리한다. 관절 동작 재사용과 source별 부착/변형을 분리해 전체에 같은 scale 효과를 복사하지 않는다.
4. 전체 원장에서 선택한 실제 계약 검증 사례로 rest/중간/끝 pose·표면 변형·동반 뼈/수동 주변 근육·관통·좌우/part·원본 복귀를 확인한다. 희소/부채꼴/다관절/비관절 유형은 계약이 실제 지원하는 것과 미지원인 것을 명시한다. 이 표본 선택으로 제품 scope를 제한하지 않는다.
5. 명시 CTA 재생/pause/scrub/속도/reduced-motion, 선택/부위 변경·취소/late response/실패/unmount/context loss, user hidden/layer/selection/camera 복원을 구현한다. 움직이는 pose에서 정적 신경을 잘못 고정하지 않는다. 필요한 family만 lazy load하고 motion buffers/skin/morph를 cache 예산에 포함한다.
6. T66의 전체 source/target 제작을 위해 work/evidence/T59/authoring-run-manifest.json과 실제 manifest validator를 생성한다. 실제 계약·exporter·입력 hash, 모든 패키지의 owner/assigned IDs/dependency/출력 경로·미확보 작업을 기록한다. common rig/관절/sourceKey 정의는 단일 writer가 고정하고 A/B/C는 candidate package만 쓰게 한다. 이 파일과 전수 배정/입력 검사가 없으면 T59 인계를 완료로 쓰지 않는다.
7. 관련 자동 회귀·type/build·실제 현재 앱 재생→복원을 한 번 검증하고 측정/한계를 남긴다. 공통 경로 pass를 전체 근육 제작 완료로 쓰지 않는다. 다음은 T25, 전체 자산 제작/등록은 T66이다.

## 합격과 보존

542/563/12, 근육 관련429 target/447 membership, 현재232 source 개념/462 표면과 원장 전체를 보존한다. 기존 HA130·역사163(6/20/135/2), source-only·권리 held·humanReview=not_performed·원본/OpenSim_Models/T13/WIP를 유지한다. 자동 위임·새 task/thread·push/배포·임상 기능은 금지한다. 전체 움직임 완료와 해당 task의 실제 책임 완료를 구분하며 일부 clip 성공으로 전체를 완료 처리하지 않는다. report/evidence/EXECUTION의 현재 acceptance 필드를 실제 검증으로 기록하고 sync/check 및 소유 로컬 커밋 후 멈춘다.
