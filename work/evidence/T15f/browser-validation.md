# T15f 실제 브라우저 검증

날짜: 2026-09-26
환경: HUMAN ATLAS production preview, Codex In-app Browser, 127.0.0.1:4174. 사용자 /review 및 localStorage 자료는 열거나 변경하지 않았다.

## 요청된 상태 전이 재검증

1440 × 900 화면에서 실제 learner UI를 조작했다. 시작은 단비골근 선택 상태였다.

| 순서 | 조작 | 주소·카드·선택 상태 관찰 |
|---|---|---|
| 1 | 선택만 보기 켬 | 격리 체크가 켜지고 선택된 단비골근만 강조 |
| 2 | 선택 해제 | 주소가 region=leg&side=right로 정규화, 카드에 “구조를 선택해 주세요”, 목록 강조 없음, 선택만 보기 꺼짐, 선택 해제 비활성 |
| 3 | 전경골근 선택 | URL에 kind=muscle&id=HA-M-000003, 전경골근 목록 선택, 카드 제목/영어명/기시·정지 요약이 전경골근과 일치 |
| 4 | 브라우저 뒤로가기 | 선택 없는 종아리 URL로 돌아오고 카드·목록 선택이 모두 비어 있음 |
| 5 | 보기 초기화 | 앞면 선택, 뒷면/측면 미선택, 선택만 보기·주변 투명하게 꺼짐, 카드 비어 있음, 목록 강조 없음, 선택 해제 비활성 |

브라우저 접근성 트리에서 각 단계의 실제 URL, 체크 상태, 목록 선택 값, 카드 제목과 버튼 활성 상태를 확인했다. 선택 해제 직후에도 isolate=false로 돌아왔고, history 뒤로가기 후와 보기 초기화 후 상태가 일치했다.

## T15f 장면·카드 흐름

- 종아리 파일럿 오른쪽 근육 6개를 실제 목록에서 차례로 선택했다. 각각 주소 ID, 선택 표시, 카드 제목, 한국어 3종 이름, 기시/정지 요약이 같은 구조를 가리켰다.
- source-linked 오른쪽 뼈 9개(Tibia, Fibula, Calcaneus, Cuboid, Femur, Medial Cuneiform, Metatarsal 1, Metatarsal 5, Navicular)는 각 typed deep link에서 뼈 카드·영어 이름·오른쪽 side·사람 검토 전 상태를 확인했다. Tibia는 canvas에서 직접 선택했고, Tibia 카드의 가자미근 연결 동작으로 근육→뼈→근육 선택도 확인했다.
- canvas 앞/뒤, 선택만 보기, 주변 투명하게, 격리/선택 초기화 제어를 확인했다. 학습 본문과 선택 가능한 구조 목록에서 개발 ID/JSON/메시 제작 입력을 표시하지 않았다.
- 현대 연구 대조 disclosure는 각 기시/정지 요약 가까이에 접혀 있었다. 단비골근을 다른 근육으로 바꾸면 이전 항목의 열림 상태가 이어지지 않았다. source locator 및 접근 제한이 열린 disclosure에서 보였다.
- 1440×900, 1024×768, 390×844에서 확인했다. 모바일 390px에서 body/document 가로 넘침은 없었고, category selector/list, 선택 카드, viewer controls가 사용 가능했다. 키보드 Enter로 근육 선택을 확인했고, 모바일 category selector로 장면 없는 머리를 선택하면 “준비 중” 상태가 나타나 종아리 장면을 대신 표시하지 않았다.
- 브라우저의 마지막 확인에서 warning/error console 항목은 0이었다. build는 별도로 기존 대형 chunk 경고를 보고했다.

## 경계

이 확인은 UI·route 일치의 기술 검증이며 해부학 검토가 아니다. 4개 미매핑 mesh, T05 표면 후보 0/41, 9개 bone mapping의 needs_review/not_reviewed와 T14b 사람 검토 대기를 유지했다. screenshot 파일은 저장하지 않았으며 접근성 상태와 관찰 결과를 이 문서에 기록했다.
