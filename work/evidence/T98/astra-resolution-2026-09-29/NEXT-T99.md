# 다음 작업: T99 · Sol High

T98은 소스 타당성/로컬 일괄 변환용 베이스 선택 범위에서 passed다. T99는 아직 시작하지 않았다. 오래된 T98 `no_new_evidence` 재개 프롬프트를 실행하지 않는다.

```text
HUMAN ATLAS에서 T99만 수행해라. 담당 Sol High.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, STATUS의 현재 generated 블록,
work/tasks/T99.md, 25-WHOLE-BODY-BASE-RESET.md(2026-09-29 정정 포함),
work/reports/T98.md의 최신 Astra 결과와
work/evidence/T98/astra-resolution-2026-09-29/의
base-selection.json, source-catalog.json, frame-contract.json,
rights-scope.json, runtime-integrity.json, validation.json을 읽어라.

T98은 실제 평가한 Z-Anatomy snapshot을 로컬 compiler의 주 입력으로 선택했다.
960개는 고유 근육 수가 아니라 근골격/부속 표면 객체 수다.
source Muscles collection의 509개 근육/부분 표면과 277개 골격 표면을
구분하고, 나머지 174개 근막/점액낭 등 부속 표면은 버리지 말고 별도 분류해라.
542 targets/563 memberships/12부위 및 unresolved canonical 후보를 그대로 보존해라.
모든 근육/뼈 학습 연결, 앱 표시 승인, 공개 재배포가 완료됐다고 해석하지 마라.

이번에는 T99 범위의 공통 source adapter/schema/compiler와
overview/detail chunk·LOD·cache/eviction·취소 처리 경로를 구현해라.
역사 task마다 전용 loader/manifest 합성 코드를 더 복제하지 마라.
검증된 기존 BP3D subset 회귀를 보존하며 Z-Anatomy source namespace를 분리해라.
고정 입력을 일괄 처리하되 실패한 object/unit을 격리·재개할 수 있어야 한다.
Blender 실행에는 확인된 승인 경로와 --factory-startup --disable-autoexec를 사용한다.
매번 새 Blender를 받거나 T98 inventory/권리/정합 조사를 처음부터 반복하지 마라.

ZA는 원본 1 unit=1 metre다. [x,z,-y]는 축 규약 변환이며
BP3D의 mm→m 스케일을 재사용하거나 두 모델이 정합됐다고 가정하지 마라.
이미 world transform을 적용한 geometry에 다시 같은 transform을 적용하지 마라.
source key/객체 이름은 Blender 복사본 이름 잘림과 분리해 보존해라.
T98의 flat-normal QA GLB를 제품 exporter로 복사하지 말고,
indexed geometry·smoothing·공유 resource·LOD 대응과 실제 bytes를 검증해라.
기존 20MiB overview/1M active triangles/96MiB geometry 등 예산을
기록 없이 높이거나 필수 구조를 삭제해서 맞추지 마라.

로컬 기술 변환과 app-display/public redistribution 권리는 독립이다.
기존 source-only/held/hidden/사용자 layer-off/human-review 상태를 유지해라.
held source를 변환했다고 learner binding이나 기본 표시를 승격하지 마라.
T100의 학습 연결·기본 전신 통합, T80 전수 제품 점검, T58 최종 UI는 실행하지 마라.

시작 HEAD/status/hash와 작업 기준선을 남기고 원본/OpenSim_Models/T13 drafts/사용자 WIP를 보존해라.
관련 자동 검사와 실제 필요한 검증·report/evidence를 남겨라.
EXECUTION의 T99 record만 갱신하고 sync_execution.py 및 --check를 실행해라.
소유 변경만 선별 로컬 커밋하고 hash·포함/제외·잔여 변경과 다음 ID/프롬프트를 남겨라.
필수 기준 미달이면 정확한 실패 unit을 같은 T99로 재개하며
관성적으로 no_new_evidence 보고만 반복하거나 새로운 번호를 발급하지 마라.
T100 이상, push, 배포, 진단·치료·침 시뮬레이션은 시작하지 마라.
```
