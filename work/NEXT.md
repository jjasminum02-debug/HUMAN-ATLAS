# 현재 다음 실행

자동 생성. 편집 원본은 [EXECUTION.json](EXECUTION.json). 역사 handoff/자료 개수로 다음 작업을 결정하지 않는다.

- 확인된 최근 진행: T104 / passed_with_gaps_report_and_commit_verified
- 다음 ID: **T98**
- 먼저 전신 구조 G1을 완성한다. 새 task 번호 없이 T98→T99→T100→T80→T58.

```text
HUMAN ATLAS에서 T98만 수행해라. 담당 Luna Max.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: T97 pinned archive/BP3D metadata/cache/T96 전체 target 및 T104까지 최신 WIP·evidence를 읽는다. 25 설계 3절의 전체 Object/Mesh/Collection/curve/helper/instance와 source 권리 상속·예외를 대조한다. canonical concept·geometry·instance·file 분모를 구분하고12부위 필수 전체 목록을 freeze한다. Z-Anatomy는 우선 후보이며 actual evaluated geometry 변환/좌우·pose/권리/포괄성/비용으로 주 베이스를 선택한다. 정확히 동결한8–12개 대표 object의 실제 exporter spike와 preview/hash를 남긴다. T97 Metal 실패를 같은 방식으로 반복하지 않고 검증된 headless/export 경로를 확인한다. raw 배열을 modifier/instance 결과로 오인하지 않는다. 모든 source를 다시 다운로드하거나 광배근만 검사하고 완료하지 않는다. source inventory만 있고 exporter가 미검증이면 partial. 웹 runtime/다음 task를 구현하지 않는다. Resume boundary (2026-09-28): the initial raw datablock inventory, T96 542-target/563-membership freeze, rights-family comparison, and exact 12-object locator freeze are completed and must not be repeated. The frozen 12-object set has now been evaluated and exported with a local three-axis preview. Continue only at nextUnit: reconcile source unit/frame/rest pose/laterality and runtime provenance against T50/T69, resolve exact object-to-rights-family ancestry, compare whole-body coverage and measured costs, then select a base only if all gates are supported; otherwise keep it undecided. Do not redownload or repeat inventory/export. Resume boundary (2026-09-29): existing local mount metadata links the current Blender 3.5.0 executable through /private/tmp/t97-blender-3.5.0-arm64.dmg to the matching T97 download record; this is artifact lineage, not publisher/integrity verification because the saved 3.5.0 receipt lacks an official checksum and the saved codesign result is invalid. Existing exact-object records add no upstream ID or license-family mapping. Z-Anatomy units/frame/pose/side remain unregistered to the BodyParts3D-only T50/T69 contract; compare target candidate and sample-cost evidence without promoting lexical matches or sample metrics to whole-body coverage. Do not repeat inventory, archive acquisition, evaluated export, or preview. Continue only in this same nextUnit when new evidence exists; otherwise keep all holds and T98 partial.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T99. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```
