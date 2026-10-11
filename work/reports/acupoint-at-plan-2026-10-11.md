# AT 개발 계획과 관찰 시점 메뉴 제거

2026-10-11. **계획 작성 완료 / AT1–AT29 구현 미착수**.

## 사용자 결정

- 기존 관찰 시점 메뉴 제거. 화면 맞춤·선택 맞춤과 orbit/zoom 유지.
- AT1부터 task 단위로 계획하며 각각 20–80분 범위의 크기.
- 사용자가 추가 응답으로 범위를 **14경맥 361혈 전체**로 확정. 경외기혈 제외.
- 모든 경혈 표시와 경맥별 색 영역 표현을 함께 설계.

## 결과

[30 설계](../../design/2026-09-25-muscle-atlas/30-AT-361-POINTS-AND-TERRITORIES.md)와 [AT 시작 문서](../plans/acupoint-at-2026-10-11/START-HERE.md), work/tasks/AT1.md–AT29.md에 범위·선행·시간·검증·개별 실행 프롬프트를 작성했다. 모든 예상 범위는 40–80분 안에 있다. 60분 점검/80분 checkpoint를 명시했으며 시간상한은 완료 보장이 아니다.

현재 AC1·AC2 코드, 실제 report와 schema/anchor/tour를 확인했다. 양측 LU 22점은 미확정 제안이며 제품 확정 좌표 0개, 전신 carrier는 아직 없다는 상태를 보존했다. 기존 camera session/overlay/tour 재구현을 배정하지 않고 전신 체표 및 실제 위치 연결 중심으로 재편했다. AT6과 AT8–18에 361개 코드가 정확히 한 번씩 배정된다.

색 영역은 공통 체표의 삼각형 mask로 구현하도록 했다. 경혈 점·경맥 선과 별도 revision이며, 선택 경맥/전체 비교/overlap과 위경 경계 수정 절차를 명시했다. 361개 혈마다 근거 없는 치료 반경을 만들지 않는다. 임독맥 학습 영역을 임의의 고유 경근으로 부르지 않는다.

work/EXECUTION.json에는 featurePlans.acupoint-at-361과 featureWorkUnits.AT1–AT29의 planned record만 추가했다. 기존 숫자 T queue와 AC1·AC2 기록은 byte 해석상 동일하게 보존했다. 역사 AC 프롬프트와 29 설계에는 AT 계획 우선 안내만 추가했다. 보고서 본문이나 과거 완료 상태를 덮어쓰지 않았다.

## 실제 UI 수정

WholeBodyViewer의 관찰 시점 details/방향 버튼과 사용하지 않는 변수, atlasShell.css의 관련 style만 제거했다. 화면 맞춤/선택 맞춤/기존 카메라 API와 AC 검토 도구는 보존했다. 실제 개발 서버에서 메뉴가 없고 화면 맞춤이 동작하는 화면을 확인했다. [검증 화면](../evidence/acupoint-at-plan-2026-10-11/view-tools.png).

TypeScript typecheck 통과. 계획의 29개 ID/선행/시간 범위/361개 배정/링크/역사 실행 보존 검사 통과. sync_execution.py는 변경할 투영이 0개였고 --check도 통과했다. 이번 UI 삭제는 작은 범위여서 전체 역사 build/test를 반복하지 않았다. 실제 확인은 데스크톱 화면이며 전 해상도 검증으로 확대하지 않는다.

## 보존·Git·다음

시작 HEAD `f7a59c854a93594b6c183d1aca6147a77e143ca3`. 기존 tracked WIP 45개의 hash 불변을 확인했다. 원본/OpenSim_Models/T13와 기존 untracked 자료는 수정하지 않았다. 소유 계획·task 명세·UI 2개 파일·EXECUTION 추가분·작은 evidence만 로컬 커밋한다. 기존 WIP·source cache·private 자료는 포함하지 않는다. push/배포는 하지 않았다.

다음은 **AT1**이다. [AT1 명세와 프롬프트](../tasks/AT1.md)를 사용한다. 기존 AC3 프롬프트 대신 새 순서를 적용하며 이 턴에서 AT1을 시작하지 않는다. 계획 합격을 361혈 위치/영역 구현 완료로 해석하지 않는다.
