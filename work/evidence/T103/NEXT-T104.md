# 다음 작업 프롬프트 — T104

```text
HUMAN ATLAS에서 T104만 수행해라. 담당 Luna Max.
AGENTS.md, 최신 work/STATUS.md와 work/task-registry-r15.json, design/2026-09-25-muscle-atlas/의 22-EFFICIENT-DELIVERY-AND-PERFORMANCE.md, 23-PROMPTS-AFTER-T95.md, 24-WORKBOOK-FACE-AND-OBSERVATION.md 및 R15 13/14/15/16 설계, work/tasks/T104.md, work/reports/T103.md, work/evidence/T103/와 선행 실제 manifest/evidence를 읽어라. T103의 실제 완료 상태와 최신 queue를 먼저 확인하고, 이미 구현된 부분은 재작업하지 마라.

T104에 동결된 정확한 BodyParts3D R4 source IDs FJ1516, FJ1516M, FJ1518, FJ1518M, FJ1557, FJ1600, FJ1601, FJ2774, FJ2781, FJ2783만 기존 R4 취득·검증·변환 도구로 취득해라. 새 전체 archive/model 다운로드는 하지 마라. 각 ID에 대해 공식 row, OBJ header, hash/CRC, side/part, mm 단위, bounds, T50/T69 frame·pose·변환을 개별 검증하고 기존 root/renderer/camera와 정적 기준 자세를 유지한 새 sibling manifest extension에 실제 GLB surface를 append해라. 원본 bytes와 T77/T79/T101/T102/T103 freeze를 보존해라.

parent whole-muscle mesh가 있으면 실제 triangle geometry를 비교하고 표본 거리와 한계를 기록해라. AABB만으로 중첩/충돌을 단정하지 말고, 연속 교차를 증명했다고 주장하지 마라. ancestor 이름만으로 canonical binding을 만들지 마라. 같은 FJ는 한 source node로만 둬라. local technical display eligibility, learner identity, human anatomy review, public redistribution rights를 분리하고 source-only 기본값·개별 held 상태를 유지해라.

T104 정확한 subset의 실제 브라우저 근접/전신 표시, 양측, layer off/on, 중복 node 부재, 단일 장면/root/renderer를 검증해라. 관련 전체 회귀, typecheck, build와 보존 대조를 실행하고 결과·미완·work/STATUS·R15 taskStatuses를 갱신해라. 소유 변경만 선별 stage하고 staged diff를 검토해 로컬 커밋해라. 기존 사용자 WIP, OpenSim_Models, T13 drafts, 권리/사람 검토 hold를 보존해라.

필수 기준 미달이면 T104 상태를 partial/blocked로 유지하고 T105를 자동 실행하지 마라. commit hash, 포함/제외, 남은 변경과 다음 ID/프롬프트를 보고한 뒤 멈춰라. push/deploy 금지.
```

## Frozen T104 target list

`FJ1516, FJ1516M, FJ1518, FJ1518M, FJ1557, FJ1600, FJ1601, FJ2774, FJ2781, FJ2783`

Source: `work/tasks/T104.md`; T104 has not been started by this task.
