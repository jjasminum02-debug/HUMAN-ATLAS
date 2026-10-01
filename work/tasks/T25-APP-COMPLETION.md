# T25 — 전체 근육 공통 움직임 학습 흐름

2026-10-02 · 전수 motion 계획 개정 · 담당 Luna Max.
27 앱 완료 계약과 [28 전체 근육 움직임 계획](../../design/2026-09-25-muscle-atlas/28-ALL-MUSCLE-MOTION-PIPELINE.md) 및 EXECUTION의 현재 promptFile이 기준이다. 과거 파일/보고는 보존한다. 계획 수정은 실행·합격이 아니다.

## 범위

T59 공통 변형/player를 source별 구조/기능 카드와 연결하고 전체 원장의 motion 가용성을 정확히 표시한다. 현재 실제 자산의 탐색→선택→작용→재생→pause/scrub/처음 자세→복원을 검증한다. 자료/clip 미확보와 실제 지원을 분리한다. 한 파일럿의 성공을 전체 범위 완료로 세지 않는다.

## 수행

1. T35/T59 실제 계약·자산·report/evidence 및 전수 motion 원장을 읽고 source/side/part/action 지원과 learner CTA의 상태를 데이터로 연결한다. HA ID가 없는 검증된 source muscle도 공통 sourceKey 경로를 사용하며 canonical binding을 만들지 않는다.
2. 같은 동작 family에서 선택 근육과 정확한 source 표면/설명이 바뀌는 흐름을 만들고, 작용 조건/여러 작용을 일반화하지 않는다. 내부 source/task/evidence 메타데이터를 학생 UI에 넣지 않는다.
3. 같은 scene의 근육 선택→기시/정지·작용→명시 CTA→몸 움직임과 실제 표면 변형→재생/정지/scrub/속도→rest 복원, 검색·양측·카드·키보드·뒤/앞·숨김을 확인한다. 지원되지 않은 신경 pose는 정확히 가리고 복원은 user layer 상태를 따른다.
4. 390/1024/1440 실제 UI와 관련 공통 계약을 검사하고 발견된 문제를 고친다. T66 자산 workers가 frozen contract 아래 candidate 폴더에서 작업할 수 있게 UI 입력 계약을 유지한다. common code는 이 writer만 변경한다.
5. 전체 target/source 원장과 잔여 제작 작업을 유지하고 실제 현재 공통 UI responsibility acceptance를 보고한다. 전체 근육 움직임 구현 완료를 선언하지 않는다. 다음 T66을 자동 실행하지 않는다.

## 합격과 보존

542/563/12, 근육 관련429 target/447 membership, 현재232 source 개념/462 표면과 원장 전체를 보존한다. 기존 HA130·역사163(6/20/135/2), source-only·권리 held·humanReview=not_performed·원본/OpenSim_Models/T13/WIP를 유지한다. 자동 위임·새 task/thread·push/배포·임상 기능은 금지한다. 전체 움직임 완료와 해당 task의 실제 책임 완료를 구분하며 일부 clip 성공으로 전체를 완료 처리하지 않는다. report/evidence/EXECUTION의 현재 acceptance 필드를 실제 검증으로 기록하고 sync/check 및 소유 로컬 커밋 후 멈춘다.
