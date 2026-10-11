# MV1 — 근육 움직임 전수 조사

계획 상태이며 이번 검토에서 실행하지 않았다. 담당 Luna Max.

설계: [32-AT6-PLACEMENT-CONTEXT-CAMERA-AND-MOTION-QA.md](../../design/2026-09-25-muscle-atlas/32-AT6-PLACEMENT-CONTEXT-CAMERA-AND-MOTION-QA.md)

```text
HUMAN ATLAS에서 MV1만 수행해라. 담당 Luna Max. 근육 움직임 전수 조사이며 수정 task가 아니다.
AGENTS.md, 최신 EXECUTION, design/2026-09-25-muscle-atlas/32-AT6-PLACEMENT-CONTEXT-CAMERA-AND-MOTION-QA.md 4절, work/tasks/MV1.md,
work/evidence/at6-motion-camera-review-2026-10-11/motion-inventory.json과 실제 learner runtime/등록/loader/authoring 입력을 읽어라.
1,160 asset record가 46개 고유 파일을 참조한다는 값은 시작 스냅샷이다. 최신 actual learner reachability/clip/side/subject/playback mapping 분모를 동결해라.
중복은 hash+clip+transform+playback으로 제거하되 역할·강조·side 차이는 별도 검사해라. 전달 index 74건을 모두 현행이라고 가정하지 마라.
대퇴직근 무릎 시범 준비 자세와 대흉근을 먼저 재현하고 고유 재생 자산 전체를 검사해라.
rest/준비/중간/최대/복귀와 키프레임 사이에서 부착부 drift, 관통, 접힘/면 뒤집힘, 과도 돌출, 주변 분리, temporal pop, 복귀를 확인해라.
실제 emitted GLB와 runtime을 검사하고 자동 지표+정면/측면/사선 contact sheet+전체 재생 시각 판정을 남겨라.
정상 형태 변화와 결함을 구분하고 '수치 통과'를 자연스러운 수축 승인으로 쓰지 마라.
모든 대상에 pass/fail/not_checked/error를 기록하고 미검사 포함 시 전수 완료라고 하지 마라.
work/evidence/MV1/ 아래 inventory/defects/repair-queue/시각 evidence 및 재사용 공통 조사 도구, work/reports/MV1.md를 남겨라.
원인 후보별로 묶고 sourceKey·asset/clip/hash·phase·재현 조작·기대 형태·실제 관찰·심각도·영향 대상을 적어 Sol이 바로 수정할 수 있게 해라.
runtime/기존 motion data/GLB/authoring 입력은 수정하지 마라. 조사 도구와 evidence만 소유한다.
시작 HEAD/status/hash와 소유 경계를 남겨라. 원본/OpenSim_Models/T13 drafts/기존 사용자 WIP를 보존해라.
기존 증거/원본을 덮지 말고 versioned 결과를 남겨라. 관련 검사와 실제 화면, 보고서/evidence를 작성해라.
최신 EXECUTION을 다시 읽고 해당 record만 갱신하며 sync_execution.py 및 --check를 수행해라.
소유 변경만 선별 로컬 커밋하고 hash·포함/제외·잔여 변경·다음 프롬프트를 남겨라.
시간 경과를 종료 조건으로 쓰지 말고 합격 기준과 실제 남은 unit으로 판단해라.
다음 작업 자동 실행·위임·push·배포·진단·치료·침 시뮬레이션 금지.
다음은 MV2(Sol High, 고정 queue의 공통 원인 묶음 하나 수정)이며 자동 실행하지 마라.
```
