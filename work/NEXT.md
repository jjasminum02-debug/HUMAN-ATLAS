# 현재 다음 실행

자동 생성. 편집 원본은 [EXECUTION.json](EXECUTION.json). 역사 handoff/자료 개수로 다음 작업을 결정하지 않는다.

- 확인된 최근 진행: T98 / accepted
- 다음 ID: **T99**
- 먼저 전신 구조 G1을 완성한다. 새 task 번호 없이 T98→T99→T100→T80→T58.

```text
HUMAN ATLAS에서 T99만 수행해라. 담당 Sol High.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: T98 실제 exporter와 선택된 source snapshot이 선행이다. 25 설계4절대로 source adapter→공통 schema/검증→overview/detail chunk와compact catalog를 생성한다. 기존 BP3D subset 재현과 전체 frozen dataset 변환을 같은 파이프라인으로 검증한다. task별 TypeScript extension/parent-chain/plugin 분기를 추가하지 말고 revision당 검증한 generic manifest로 바꾼다. source namespace/object instance/shared geometry/개념 binding/frame/rest pose와hold를 독립 보존한다. 전신overview와 상세LOD, byte-budget LRU/pin/해제/취소를 구현하고 geometry추가당 runtime 코드0을 검증한다. 원본/역사 cache·freeze는 변경하지 않는다. T98 대표12개만 변환하고 전체compile 완료라 하지 않는다. 새 기준은 manifest·resource·정합·품질·성능 회귀로 검증하며 learner의 전체 이름/선택 연결은 T100에 맡긴다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T100. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```
