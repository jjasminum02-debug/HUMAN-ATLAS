# T100 재개 프롬프트

HUMAN ATLAS에서 T100만 재개해라. 담당 Luna Max.
AGENTS.md, 최신 work/EXECUTION.json 및 generated STATUS/NEXT, work/tasks/T100.md,
work/reports/T100.md, work/evidence/T100/progress.json, region-coverage-matrix.json,
coverage-validation.json, browser-cycles.json과 지정된 T96/T98/T99 원본 evidence를 읽어라.

현재 nextUnit은 `resolve-z-anatomy-source-to-canonical-concept-and-12-region-crosswalk`다.
T96 542 targets / 563 memberships / 12 historical packages, T98/T99 input hash,
manifest와 10개 chunk 검증은 다시 하지 말고 기존 산출물을 재사용해라.
현재 542개 중 ZA exact target identity 0, learner binding 0, ZA 12-region map 0이다.
이름 유사·bounds·side suffix만으로 ID, side, region, 세 이름 또는 selection을 만들지 마라.

공식 source/crosswalk 근거가 추가되었는지 먼저 확인하고, 확인되는 범위만 exact hash/locator와
primary/secondary region으로 기록해라. 각 object의 identity, side/part/group, region,
geometry/frame, local display eligibility, redistribution rights, human review를 독립 상태로 유지해라.
source-only 관찰과 canonical learner selection을 분리한다. T99의 검증된 chunk/LOD,
공통 DatasetResources/ResourceQueue 및 기존 단일 AnatomySceneRoot/renderer/camera만 재사용한다.
미해결 표면을 기본 표시하지 말고 BP3D와 ZA를 겹치지 마라.

542 target와 563 membership, 12개 부위 전부에서 실제 surface/세 이름/typed selection/hold를
coverage matrix로 대조한다. 통합이 허용되는 정확한 입력만 하나의 learner scene으로 연결하고,
실제 브라우저에서 전신/부위/검색/선택/기본 보기/핵심 관찰/화면 비용을 확인해라.
T99 offline budget 수치를 T100 draw/FPS로 재사용하지 마라.
표정근 motion disabled, source-only, app-display/right holds, humanReview=not_performed,
T13 drafts, 원본/사용자 WIP/OpenSim_Models를 보존해라.

필수 단위가 남으면 T100을 `in_progress/partial`로 두고 정확한 같은 nextUnit과
필요 evidence를 기록해라. work/EXECUTION.json의 T100 record만 갱신하고
`python3 work/tools/sync_execution.py` 및 `--check`를 실행해라.
소유 변경만 선별 스테이징/검토/로컬 커밋하고 hash·잔여 WIP를 기록해라.
T80/T58 자동 실행, push, 배포, 임상 진단·치료·침 시뮬레이션은 금지한다.
