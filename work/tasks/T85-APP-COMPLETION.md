# T85 — 전체 지원 움직임·통합 앱 품질 감사

2026-10-02 · 전수 motion 계획 개정 · 담당 Astra · 현재 대화 직접 구현.
27 앱 완료 계약과 [28 전체 근육 움직임 계획](../../design/2026-09-25-muscle-atlas/28-ALL-MUSCLE-MOTION-PIPELINE.md) 및 EXECUTION의 현재 promptFile이 기준이다. 과거 파일/보고는 보존한다. 계획 수정은 실행·합격이 아니다.

## 범위

T47 감사를 흡수해 전체 motion 원장에서 실제 지원하는 모든 clip/side/part/action 계약을 자동 검사하고 같은 source surface/scene 변형·신경 pose·카메라/선택/설명/복원/성능을 다듬는다. 미제작 전체 대상과 실제 지원을 분리하며 소수 예시 성공을 전체 근육 완성으로 표시하지 않는다. 담당 Astra 현재 대화 직접 구현을 유지한다.

## 수행

1. T66의 전수 처리 결과와 지원 clip 목록을 실제 assets/runtime으로 대조한다. target429/source232를 보존하고 예시 clip/registry entry/부분 group을 전체 muscle support로 잘못 세는 오류를 수정한다.
2. 실제 같은 source graph/frame/rest pose, deformation/bones/passive context·중간 pose/관통·part·side·layer-off/held·취소/전환/복원·신경 pose를 전수 자동 계약 검사한다. 필요한 변경 사례의 실제 시각 검증에 집중하고 동일 입력 근거를 재사용한다.
3. 390/1024/1440에서 여러 deformation 유형과 전체 12지역 탐색→근육→작용→재생→설명→복원을 실제 검증한다. 전신 renderer/camera를 유지하고 선택 대비/깊이/가림/카메라 reset·검은 frame/console errors를 고친다.
4. cold/warm bytes/loading, render CPU/frame interval, active triangles/draws/geometry+animation bytes, 반복 clip/region 전환 후 cache/cancel/late response를 확인한다. 관측 불가 GPU/VRAM은 한계로 남기고 실제 budget을 몰래 상향하지 않는다.
5. 현재 지원 기능의 제품 blocker를 해결한다. 전체 근육 움직임 목표의 진짜 구현율·남은 anatomy/source/rig/clip 작업과 local_app_ready를 별도 기록한다. 전체가 실제 구현되지 않았다면 wholeMuscleMotionGoal=complete로 쓰지 않는다. 다음 T40은 실행하지 않는다.

## 합격과 보존

542/563/12, 근육 관련429 target/447 membership, 현재232 source 개념/462 표면과 원장 전체를 보존한다. 기존 HA130·역사163(6/20/135/2), source-only·권리 held·humanReview=not_performed·원본/OpenSim_Models/T13/WIP를 유지한다. 자동 위임·새 task/thread·push/배포·임상 기능은 금지한다. 전체 움직임 완료와 해당 task의 실제 책임 완료를 구분하며 일부 clip 성공으로 전체를 완료 처리하지 않는다. report/evidence/EXECUTION의 현재 acceptance 필드를 실제 검증으로 기록하고 sync/check 및 소유 로컬 커밋 후 멈춘다.
