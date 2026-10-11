# AT7-CAMERA 실행 프롬프트

```text
HUMAN ATLAS에서 AT7만 수행해라. 담당 Sol High.
AGENTS.md, 최신 EXECUTION, work/tasks/AT7.md, 30/31 설계와 design/2026-09-25-muscle-atlas/32-AT6-PLACEMENT-CONTEXT-CAMERA-AND-MOTION-QA.md 3절,
최신 AT6 실제 표시 data/report/evidence, AcupunctureOverlay/AcupointReview/tour/CameraSessions를 읽어라.
핵심은 경혈 선택 시 해당 혈과 주변 근육·힘줄·기준 뼈/관절이 함께 보이는 중간 거리 관찰이다.
점들만 묶는 focusSection과 LU별 고정 거리 대신 공통 ObservationContext 입력을 사용해라.
긴 뼈/근육 전체가 아니라 해당 혈 인근 구간의 실제 bounds를 사용하고 실제 카드/하단 조작부 가림을 제외한 영역에 맞춰라.
카드·검색·점 클릭 모두 같은 함수로 연결해라. 이미 충분한 문맥 구도면 유지하고 아니면 target/distance/orientation을 부드럽게 이동해라.
전신샷 유지나 점 하나만 극단적으로 확대하면 실패다. 수동 입력 우선·reduced-motion·빠른 선택 취소·같은 scene/camera를 보존해라.
실제 위치가 미확정이면 점을 만들지 말고 확인된 기준 구조만 관찰하는 모드로 구분해라. 이를 AT6 위치 완료로 세지 마라.
LU1/LU5/LU9/LU11 양측, 390/1024/1440에서 점과 주변 구조 가시성·패널 가림·전환을 실제 검사해라.
명세의 기존 tour 일반화/표시 제어도 유지하되 보기옵션 재배치나 경혈 패널 전면 디자인은 하지 마라.
시작 HEAD/status/hash와 소유 경계를 남겨라. 원본/OpenSim_Models/T13 drafts/기존 사용자 WIP를 보존해라.
기존 증거/원본을 덮지 말고 versioned 결과를 남겨라. 관련 검사와 실제 화면, 보고서/evidence를 작성해라.
최신 EXECUTION을 다시 읽고 해당 record만 갱신하며 sync_execution.py 및 --check를 수행해라.
소유 변경만 선별 로컬 커밋하고 hash·포함/제외·잔여 변경·다음 프롬프트를 남겨라.
시간 경과를 종료 조건으로 쓰지 말고 합격 기준과 실제 남은 unit으로 판단해라.
다음 작업 자동 실행·위임·push·배포·진단·치료·침 시뮬레이션 금지.
다음 계획은 AT20이며 자동 실행하지 마라.
```
