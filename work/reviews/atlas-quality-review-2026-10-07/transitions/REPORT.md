# 설명창·부위 메뉴 전환 개선

2026-10-07 사용자 요청의 두 UI 개선을 직접 구현하고 새 로컬 전달본에 반영했다. 기존 task 판정과 해부학 데이터는 수정하지 않았다.

## 변경

- 설명창 첫 등장: 420ms 동안 투명도와 짧은 이동을 함께 적용한다. 데스크톱은 오른쪽에서 16px, 좁은 화면은 아래에서 14px 이동한다. 텍스트를 흐리게 하거나 크게 확대하지 않는다.
- 다른 구조/좌우 선택: 같은 카드와 player를 유지하고 내용만 280ms 동안 가볍게 전환한다. 빠른 재선택은 이전 효과를 취소한다. 별도 scene/frame clock이나 상시 render를 추가하지 않았다.
- 부위 메뉴: DOM을 열 때마다 생성/제거하던 방식과 220ms scale 효과를 대신해, 같은 메뉴의 실제 높이를 440ms 동안 펼치고 접는다. 투명도는 320ms, 이동은 6px이다. 목록이 한 번에 밀려나는 동작도 함께 완화했다.
- 마우스가 잠깐 경계를 벗어나면 140ms 동안 닫힘을 유예하며 재진입 시 취소한다. hover 열기와 기존 클릭/키보드/포커스 복원은 보존한다.
- 닫힌 메뉴는 즉시 inert/aria-hidden으로 전환하여 fade-out 중에 버튼을 누르거나 Tab으로 진입하지 못하게 한다. 높이와 투명도만 서서히 사라진다.
- 기존 reduced-motion CSS는 등장/높이 전환을 비활성화한다. 내용 전환도 해당 설정에서는 실행하지 않고, 실행 중 설정이 바뀌면 취소한다.

## 검증

TypeScript 검사, learner card/motion 생성 결과 freshness 검사, production build, 고정 snapshot 검증과 서버 시작이 통과했다. 기존 큰 JavaScript chunk 안내는 남으며 예산을 변경하지 않았다.

새 전달본을 실제 브라우저의 1440×900, 1024×768, 390×844 CSS viewport에서 확인했다. 설명창 등장, 양측 내용 교체, 메뉴 열기/닫기와 높이 변화, Space/Escape와 포커스 복귀, 닫힌 메뉴 Tab 제외, 목 부위 선택, 근육의 기능 탭과 실제 loop/reclick-rest를 확인했다. canvas/player는 각각 하나이고 scene root가 유지됐다. console error는 0건이다.

메뉴를 여는 즉시 포인터 자동화로 선택한 첫 시도는 메뉴가 아직 펼쳐지는 중이라 선택되지 않았다. 완전히 펼쳐진 현재 위치를 확인한 다음 목을 선택했고 route/제목/검색 초기화/포커스 복귀가 일치했다. 이 도구 시도와 성공 확인을 browser-validation.json에 구분해 남겼다.

390은 실기기 시험이 아니다. 이번 도구에서는 실제 hover-only 포인터 이동과 브라우저 reduced-motion 선호를 변경하는 검증을 하지 못했다. 해당 handler와 CSS/animation 취소 조건은 코드로 확인했으며, 실제 브라우저 메뉴 검증은 클릭/Space/Escape로 수행했다. PNG는 정지 화면 근거이며 동영상 검증으로 표현하지 않는다.

## 로컬 반영·보존

새 snapshot: `local-20261007060553869-bf4218bb`

Manifest SHA256: `4934cedcc7f053eebc68616f46e5797f9d57209978df16bb45791c3136842dc4`

확인 주소: <http://127.0.0.1:5184/>

현재 CURRENT 포인터는 새 snapshot을 가리킨다. 실행 중인 이전 5181/5182/5183 서버와 과거 snapshot은 보존했다. 일반 로컬 시작 절차도 새 포인터를 사용한다. 전달 기준은 기존 WIP를 보존한 작업 트리 snapshot이다.

이전 snapshot과 비교하여 motion/anatomy/projection 94개 파일과 private 입력 3개의 hash가 모두 같다. 이름·신경·기시정지·geometry·권리·사람 검토·전체 분모는 바뀌지 않았다. 원본/OpenSim_Models/T13과 다른 사람의 WIP를 수정하지 않았다. 변경 소스는 App.tsx와 atlasShell.css 두 파일뿐이다. 새 번호/agent/다음 task/push/배포를 실행하지 않았다.

재현: 기존 `work/delivery/T40/start.command` 또는 atlas-web의 `local:start`가 CURRENT를 읽는다. 기존 포트가 사용 중이면 이번처럼 `--port 5184`를 지정한다. 소스 수정 확인을 위해 이번에 시작한 개발 서버는 검증 후 정리하고, 새 고정 전달 서버는 결과 확인용으로 유지한다.
