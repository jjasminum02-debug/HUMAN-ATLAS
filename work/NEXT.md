# 현재 다음 실행

자동 생성. 편집 원본은 [EXECUTION.json](EXECUTION.json). 역사 handoff/자료 개수로 다음 작업을 결정하지 않는다.

- 확인된 최근 진행: T99 / accepted
- 다음 ID: **T100**
- 먼저 전신 구조 G1을 완성한다. 새 task 번호 없이 T98→T99→T100→T80→T58.

```text
HUMAN ATLAS에서 T100만 수행해라. 담당 Luna Max.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
26-T100-BULK-DELIVERY-PLAN.md의 공통 처리·예외 검토·앱 데이터 분리·변경별 검증 원칙을 적용한다. 고정 10개 처리 후 의무 종료하지 않는다. 역사 evidence는 보존한다.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: T98 전체 target와 T99 실제 전체dataset 산출물을 사용한다. 25 설계5절에 따라 하나의 scene에 전신bones/muscles를 넣고12부위/복수region/좌우/세 이름/검색/typed card를 전체coverage matrix로 연결한다. T105–121의 exact 대상/보류/지역자료를 내부workUnits로 흡수하고 historical source나 ID를 삭제하지 않는다. 얼굴표정근/광배근/양측상완/견갑골/요추·엉치뼈/손발·골반바닥을 빠뜨리지 않는다. source-only 관찰과 canonical 학습 선택은 별도이며 이름만으로binding을 만들지 않는다. 기존controller를 재사용해 주변흐림·선택반투명·숨김·격리·맞춤·undo/복원 핵심을 함께 구현한다. held/layer-off를 복원으로 노출하지 않는다. 전체overview에서 시작하고 camera연속성/미니멀UI를 지킨다. 표정근motion은disabled, 새애니메이션·신경3D·검증전엑셀본문은 넣지 않는다. 고정 10개 종료 대신 26 설계의 공통 전수처리와 예외 의미검증을 사용하고 같은 T100을 재개하며 첫부위를 전신완료로 부르지 않는다. 실제12부위·선택·성능evidence가필수다. 2026-09-29 사용자 정정: 과거 not_approved_by_this_task/공개 재배포 held/사람검토 미수행은 일괄 차단 조건이 아니다. 25 설계 마지막 상태 교정과 T100 resolution-2026-09-29 현재 decision overlay를 적용하고, 남은 의미/이름/형상 누락만 처리한다. 2026-09-29 효율화: design/2026-09-25-muscle-atlas/26-T100-BULK-DELIVERY-PLAN.md를 읽고 A 공통 builder/validator 및 경량 runtime projection → B 전체 명칭/반복 구조 일괄 연결 → C 실제 예외/누락 해결 → D 최종 통합 검증 순서로 수행한다. B01–B04와 승모근 교정을 보존한다. 10개마다 종료·전체 빌드·브라우저 검증·전용 코드를 반복하지 않는다. 상세 evidence는 개발 원장에 두고 앱에는 필수 필드만 전달하되 policy 검사를 보존한다. 필수 gap이 남으면 완료로 세지 않는다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
25 설계의 T100 상태 교정에 따라 과거 not_approved_by_this_task·공개 재배포 held·humanReview 미수행을 로컬 개발의 일괄 차단으로 사용하지 마라. 담당 AI가 source-family 근거/예외와 객체·의미 대응을 검토하여 현재 overlay 결정을 기록하고 진짜 충돌 항목만 보류한다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T80. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```
