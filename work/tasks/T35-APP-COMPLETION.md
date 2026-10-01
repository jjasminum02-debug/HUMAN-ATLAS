# T35 — 전체 근육 움직임 범위·공통 제작 계약

2026-10-02 · 전수 motion 계획 개정 · 담당 Sol High.
27 앱 완료 계약과 [28 전체 근육 움직임 계획](../../design/2026-09-25-muscle-atlas/28-ALL-MUSCLE-MOTION-PIPELINE.md) 및 EXECUTION의 현재 promptFile이 기준이다. 과거 파일/보고는 보존한다. 계획 수정은 실행·합격이 아니다.

## 범위

전체 근육 관련 429 target/447 membership과 현재 232 source 개념/462 표면을 빠짐없이 움직임 제작 대상으로 계획한다. 별도 초기 근육 목록을 두지 않는다. 실제 source/side/part/frame/rest pose/부착·작용/rig 가능성을 전수 disposition으로 연결한다. 관절·다관절·넓은 부착·반복/분절·비관절 연조직 family를 공통 같은-scene 계약으로 정리한다. 과거 표정근 제외는 최신 전 근육 지시로 대체하되 자료 없는 형상을 만들지 않는다. 계획 task이며 새 clip 제작은 T59/T66에서 한다.

## 수행

1. 실제 T65 passed/report/evidence, 현재 App/정적 dataset loader/animation adapter/공통 controller를 읽어 현재 실제 motion 지원 0과 역사 T24 기술 candidate를 구분한다. 과거 blocked T24를 재실행하지 않는다.
2. 준비된 run-manifest 및 snapshots를 읽고 python3 work/tools/validate_motion_parallel_plan.py로 해시·429/232/462 전수 배정·중복 0을 검증한다. 입력이 같으면 배정을 다시 만들지 않는다. A/B/C는 사람이 별도 프롬프트로 실행할 수 있는 같은 T35 자료 준비 작업이다. 자동 위임/새 thread를 만들지 않는다.
3. 전체 target/source/part/group/side/action/pose의 움직임 원장을 만든다. 기시·정지31개 설명/201개 gap을 재사용하고 원문 locator와 source geometry/rig 입력의 부족을 구체적으로 연결한다. 전체 원장에서 임의로 쉬운 근육만 제외/선정하거나 몇 개 예시를 목표로 고정하지 않는다. 그룹/반복 family의 일부 구현을 전체로 세지 않는다.
4. 원문·좌표·pose·부착 근거와 source-derived authoring 선택을 구분한다. OpenSim은 해당 frame/관절/path를 검증할 수 있을 때 보조로 쓰며 전 근육 solver 설치를 일괄 선행 조건으로 만들지 않는다. 기존 source-only와 null canonical binding을 지원 제작의 일괄 차단으로 쓰지 않는다.
5. work/evidence/T35/motion-contract.json에 native source identity/hash/rest pose, sourceKey 기반 결속, derived skin/morph/corrective 변형, 움직이는 뼈·고정 구조·주변 수동 변형·관통 위험, 부분/좌우/동작 조건과 비관절 변형 유형의 계약을 정한다. 수치·pivot·정합을 근거 없이 채우지 않는다. 부족한 입력은 정확한 재개 조건으로 둔다. pipeline 표본은 전체 원장에서 검증 가능성에 따라 정하며 초기 확장 리스트가 아니다.
6. A/B/C 결과가 실제 있으면 --results 검사로 검증한 전수 결과만 통합한다. worker 실행은 선택 사항이며 없으면 같은 manifest 전수 규칙으로 현재 입력/제작 가능성 계획을 직접 처리한다. 아직 조사중인 필드는 unknown·필요 입력으로 남기고 없는 근거를 만들지 않는다. 전체 원장의 현재 상태/필요 작업과 검증된 공통 제작 계약을 완성하면 계획 task를 종료할 수 있으며, 모든 근육의 원문/clip 확보를 T59 시작의 일괄 조건으로 만들지 않는다. 실제 계획/공통 계약 자체가 미완이면 그 unit만 같은 T35에서 해결한다. 공통 작성자는 이 담당자 하나다.
7. T59가 공통 제작/player를 만들고 authoring-run-manifest를 실제 생성한 후 전체 자산을 병렬 제작하는 순서를 구체화한다. T35 합격은 전수 제작 계획/계약 완료이지 새 motion 구현 합격이 아니다. 전체 근육 목표를 소수의 clip 지원으로 축소하지 않는다.

## 합격과 보존

542/563/12, 근육 관련429 target/447 membership, 현재232 source 개념/462 표면과 원장 전체를 보존한다. 기존 HA130·역사163(6/20/135/2), source-only·권리 held·humanReview=not_performed·원본/OpenSim_Models/T13/WIP를 유지한다. 자동 위임·새 task/thread·push/배포·임상 기능은 금지한다. 전체 움직임 완료와 해당 task의 실제 책임 완료를 구분하며 일부 clip 성공으로 전체를 완료 처리하지 않는다. report/evidence/EXECUTION의 현재 acceptance 필드를 실제 검증으로 기록하고 sync/check 및 소유 로컬 커밋 후 멈춘다.
