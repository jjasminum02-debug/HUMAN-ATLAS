# 다음 실행: AT10/F3 — Sol xhigh

V1 기술 구현은 보존하되, 전신 외관은 사용자가 반려했으므로 합격으로 취급하지 않는다. V1 잔여를 이유로 동일 재질 조사만 반복하지 말고 F3 형상을 직접 수정한다.

```text
HUMAN ATLAS에서 AT10/F3만 수행해라. 담당 Sol xhigh.
work/plans/skin-quality-completion-2026-10-15/START-HERE.md, COMMON.md,
02-F3-HEAD-EAR-NECK.txt의 2026-10-15 사용자 시각 반려 개정까지 읽고,
최신 EXECUTION의 AT10.completionExecution과 V1 보고서,
work/evidence/AT10/2026-10-15-v1-appearance/VISUAL-DIRECTION.md를 읽어라.

F1/F2 완료 원본과 V1 재질 로더를 보존하고 F3 얼굴·귀·목 형상을 직접 교정해라.
공식 참고 화면을 기준으로, 원형/정합후 피부/내부 해부 구조를 대조해
머리-목-어깨 연결과 눈·입·귀가 자연스럽게 보이도록 구현해라.
교차0이나 텍스처 적용만으로 합격시키지 말고, 중립 재질과 최종 재질로
전신·상반신·얼굴 양측을 실제 앱에서 검증해라.
V1은 skinAppearance=v1 개발 옵션이며 geometry/UV hash binding을 유지한다.
새 geometry에 연결할 때 실제 UV 검증과 새 manifest를 남겨라.

V1 외관 미완이나 기존 부모 partial을 F3 실행의 승인 차단으로 재사용하지 마라.
원본·사용자 WIP·성공한 손발을 보존하고, 영향 구역을 검증해라.
보고서·evidence·completionExecution 갱신, sync/check, 소유 로컬 커밋 후 멈춰라.
F4 자동 실행, UI/카메라 개편, push/배포는 하지 마라.
```
