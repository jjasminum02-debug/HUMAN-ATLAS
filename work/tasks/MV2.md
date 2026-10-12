# MV2 — 기존 근육 동작의 결함 수정과 학습 표현 검증

## 현재 실행 계약 — 2026-10-12 Q03 재검토

현재 상태는 `work/EXECUTION.json.featureWorkUnits.MV2` 및 최종 evidence를 따른다.
**유일한 현재 실행 프롬프트:** [PROMPTS-IN-ORDER.md](../plans/mv2-at-integrated-2026-10-12/PROMPTS-IN-ORDER.md).
바로 시작할 프롬프트는 [NEXT-MV2-Q03.md](../plans/mv2-at-integrated-2026-10-12/NEXT-MV2-Q03.md)다.
이 명세는 같은 날 앞선 q01/Q02 대기·매번 한 원인만 수정·검토 후 기록만 종료 지시를 대체한다.
역사 검증 및 보고서는 바꾸지 않는다. 재계획 자체는 새 검증/통과가 아니다.

- 완료: Q01 engineering, q01-learning-quality (`2d182a6`), Q02 (`5b51ff6`).
- 최신 Q03 실행 기록: `88cfb15`, `work/evidence/MV2/2026-10-12-q03-r2/`.
- Q03은 3매핑의 실제 전체 주기를 이번 실행에서 확인하지 못해 partial이다. source/GLB QC와 시각 판정을 분리한다.
- 이번 코드 진단에서 297/298/299는 `posture_observation`이며, 근육 작용 검색에서 제외되는 대신 기존 기능 탭의 **자세에서 관찰하기**에 존재함을 확인했다. 검색 0건은 자료 부재/권리 차단의 증거가 아니다. 현재 진단은 브라우저 재생 합격이 아니다.
- 남은 범위는 Q03 3 / Q04 26 / Q05 2매핑, 합계 31개다. 원래 Q01–Q05의 34매핑과 q01 표현 기준을 동결하고 신규 전신 동작을 이 task에 끼워 넣지 않는다.

## 실행 묶음

1. **Sol xhigh / Q03:** 기존 정확한 UI 경로로 3개를 재생·관찰하고 필요한 선택/연결/재생/기하 결함까지 해결한다. UI 개편 보류는 기능 수리 금지가 아니다. 기존 정상 GLB를 다시 만들 필요는 없다.
2. **Luna Max / Q04+Q05:** 28매핑의 정확한 연결과 실제 국소 형태를 판정한다. 공통 lifecycle 회귀는 같은 runtime 결과를 공유한다. 다 통과하면 전체 큐 대조까지 이번 실행에서 끝낼 수 있다.
3. **Sol xhigh / 확인된 잔여만:** 필요할 때만 공통 원인별 최소 수정과 영향 회귀로 전체 종료한다. 같은 MV2의 고정 잔여 목록까지 이번 요청에서 처리하며 원인마다 사용자 재승인을 요구하지 않는다.

정확한 판정, 변경 범위, browser/asset 재사용, 보존/커밋 계약은 현재 프롬프트의 공통 계약을 따른다.
[기존 WIP 인수 규칙](../plans/mv2-at-integrated-2026-10-12/RESUME-OWNERSHIP.md)은 유지한다.
교수/사람 검토·공개 재배포는 로컬 기술/교육용 표현 수락과 독립이다. 통과하지 않은 실제 동작을 완료로 바꾸지 않는다.
전체 MV2 완료는 모든 근육의 신규 수축 애니메이션 완성이 아니다. 자세 관찰을 근육 작용으로 일괄 바꾸지 않는다.

카메라·보기옵션·패널 배치 개편은 후속 UI 요청까지 보류한다. 원본/OpenSim_Models/T13/사용자 WIP 보존, 소유 로컬 커밋, 자동 다음 작업·push·배포 금지는 유지한다.

상위 범위 참고: [32-AT6-PLACEMENT-CONTEXT-CAMERA-AND-MOTION-QA.md](../../design/2026-09-25-muscle-atlas/32-AT6-PLACEMENT-CONTEXT-CAMERA-AND-MOTION-QA.md) 4절.
계획 진단: [closure-review.json](../plans/mv2-at-integrated-2026-10-12/closure-review.json).
