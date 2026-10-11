# AT6 — 폐경 위치 보완·learner 연결 체크포인트

2026-10-11. **AT6는 partial이다. 필수인 ‘양측 22개 실제 위치 표시’는 미달이다.** LU1–11의 11개 개념과 양측 22개 카드 선택·이름·기본 위치 문장은 실제 learner 화면에 연결했다. 정밀 위치 **0**, 교육용 개략 위치 **0**, 미확정 **22**이며, 카드 선택이나 삼각형 주소 재현을 위치 완료 수로 계산하지 않는다.

AGENTS, 최신 EXECUTION/NEXT, AT6 명세, 30/31 설계, AC1/AC2·AT3/4/5 보고서와 실제 carrier/native/nail/compiler/runtime evidence를 확인했다. 선행 화면도 읽었다. 원본 probe와 공통 reader·compiler를 재사용했고 재다운로드·원본 변경·새 renderer/인체 제작은 0회다. 과거 deferred/교수 미검토/공개 held 때문에 구현을 중단한 결과가 아니다.

## 실제 입력 검사와 위치 실패

`inspect-native.py`는 AC1의 world reader만 AST로 읽어 22개 좌우 구조의 detail vertex/triangle와 matrix를 재현했다. 18개 실제 GLB 및 22개 unit metadata를 읽었고 좌우에 각자의 source key/matrix를 사용했다. Wrist의 Radius/Scaphoid/APL/EPB 실제 triangle section도 양측 별도로 남겼다. AT4 손톱 대조에서 엄지 판은 component 0, 엄지 손톱주름은 **component 3**이다. component 번호를 손가락 번호로 추정하지 않았다.

AT3/4 carrier의 실제 binary와 hash를 읽고 기존 AC2 proposal 22개를 해당 부위 topology에 대조했다. 14개 proposal XY에는 정확한 전방 ray face 주소가 있었고 8개에는 없었다(LU2/9/10/11 양측). nearest fallback·mirror·다른 외피로의 이동을 쓰지 않았다. **이는 기존 proposal의 기술 표면 probe이며, 실제 혈위의 의미 있는 landmark annotation이 아니다.** 기존 좌표의 bounds 작성 provenance를 `surface-probes.json`에 명시했다. ray 성공 14개를 승인하지 않았다.

아래팔 carrier 최하단 y=0.866m, 손 core 최상단 y≈0.847446m 사이에는 열린 구간이 있다. 원본 구조는 있어도 손목 체표·주름을 채운 면은 아니다. LU9를 위쪽 팔로 옮겨 빈 구간을 숨기지 않았다. 나머지 ray 실패도 해당 혈 전체가 영구 불가능하다는 뜻은 아니다. 현재 proposal/등록 표면 연결의 실패와 실제 위치 입력 부재를 구분한다.

| 양측 대상 | 실제 확인한 구조 | 남은 입력 |
|---|---|---|
| LU1 중부 | 빗장뼈·첫째/둘째갈비뼈, 몸통 carrier | 첫째늑간 체표 annotation·앞정중선/6 B-cun 기준 |
| LU2 운문 | 빗장뼈·어깨뼈, 몸통/어깨의 열린 면 | 쇄골아래 함요·부리돌기 안쪽 대응·6 B-cun |
| LU3 천부 | 각 쪽 이두근·위팔 carrier | 실제 겨드랑/팔꿈치 주름 endpoint·3 B-cun path |
| LU4 협백 | 각 쪽 이두근·위팔 carrier | 같은 endpoint·4 B-cun path |
| LU5 척택 | 이두근·몸쪽 노뼈·팔꿈치 주변 면 | 건 가쪽 함요·팔꿈치 주름·굴곡 자세와 현재 정지 자세의 대응 |
| LU6 공최 | 노뼈·아래팔 carrier | 주름 endpoint·7 B-cun 경로 |
| LU7 열결 | APL/EPB·노뼈 | 실제 힘줄 사이 함요·손목주름·1.5 B-cun |
| LU8 경거 | 노뼈 주변 | 노동맥/손목주름 annotation·1 B-cun |
| LU9 태연 | 노뼈·주상골·APL, 실제 wrist section | 손목 체표 구간·주름/동맥/건 자쪽 함요의 대응 |
| LU10 어제 | 첫째손허리뼈·손 core | 적백육제/손바닥·손등 피부 경계 annotation |
| LU11 소상 | 독립 양측 엄지 판/주름·말절골 | 노쪽 몸쪽 조갑각·인접 피부·해당 모델 0.1 F-cun calibration/path |

모든 remaining unit과 시도·필요 입력은 `remaining-units.json`에 있다. 대안은 하나다: **현재 정지 모델에 맞춘 양측 체표 지표 annotation package**를 확보/작성하여 실제 주름·함요·자세와 B-cun/F-cun endpoint/path/calibration을 명시하고 공통 compiler로 재현한다. 단순 bounds 길이, 근막 envelope, nearest 결과를 그 입력으로 대신할 수 없다. 이 입력이 아직 없다는 것을 ‘교수 승인 대기’나 AI 영구 차단으로 바꾸지 않는다.

`lung-rules.json`은 실제 등록 carrier 11개를 사용하며 22 unit을 공통 AT5 CLI에 전달한다. 기술 topology/frame/side 검사는 22개 통과했으나 위치 관계 evidence는 unresolved로 유지하여 22개 모두 거절됐다. 원문 입력 edition과 실패 이력은 compiler/에 보존했다. 재개는 실패 22개를 다시 계산하고 성공 재사용은 0개다. runtime-projection은 빈 배열이며 fixture export 0이다. 원래 AC1/AC2 JSON을 덮어쓰지 않았다.

## 공통 구현과 learner 연결

몸통 carrier는 인체 정중선을 걸치는 공유 면인데, 기존 adapter/compiler는 carrier의 `side=midline`을 모든 point의 side로 강제했다. 이를 고쳐 같은 몸통 면에서 양측 anchor를 재현할 수 있다. 실제 triangle의 해부학적 X 부호로 반대쪽 주소를 거절한다. 실제 trunk-2 양측 face로 자동 검증했고, 위치 evidence/pose/hash guard는 유지했다. 정중 point의 off-midline 검사는 기존 compiler/projection에서 계속 수행한다.

공통 overlay는 여러 등록 carrier를 하나의 root/group에서 참조하고 점의 carrierId에 맞는 adapter를 사용한다. 공유 marker geometry, 기존 tour/CameraSessions/update clock/기존 선택 흐름을 유지한다. task별 renderer/controller/카메라 관리자는 없다. 실제 현재 learner projection이 비어 있으므로 이 다중 carrier 표시를 실제 승인 점 렌더 완료라고 주장하지 않는다.

기존 `AcupointEntry`/`AcupointReview`의 카드와 수명을 함께 재사용한다. 기본 진입 `경혈`은 learner이며, DEV proposal 검토는 `?acupointReview=1`에서만 열린다. Production의 review 데이터 import는 제거된다. 실제 learner는 compact `atlas-data/acupoints/learner/lung.json`만 읽고, compiler projection의 registered carrier/hash/frame/static pose/side를 검사한 위치만 기존 overlay에 전달한다. 일부 승인 위치만 있는 package에도 전체 11혈 tour를 켜지 않는다.

확인된 이름/기본 위치 문장과 표시 불가 이유·교과서 설명 대기를 구분했다. 이번 learner의 22개 이름 선택은 원래 해부 source 선택을 바꾸지 않는다. unresolved 점·경로·선택 label·교재/fixture/source cache/실패 이력은 learner에 내보내지 않는다. 빈 projection은 geometry/카메라 session을 할당하거나 카메라를 이동하지 않는다. learner 진입이 기존 motion을 강제로 복원하지 않으며, 고정 위치는 복원된 정지 pose에서만 허용한다. AI provenance는 compiler 입력/실패 ledger와 향후 compact projection에 유지한다.

loader는 마지막 요청 token/AbortController, hash 후 취소 재검사와 정확한 carrier ID 선택 로딩을 사용한다. 빈 projection에는 carrier manifest/binary 요청이 없다. unload와 source/motion 변경 시 진입 요청·label·overlay·listener/update를 해제한다. source local rights supported, 위치 unresolved, AI author, professor not_performed, public redistribution held는 별개 상태다. 공개 빌드는 로컬 검증 산출물이며 공개 배포 승인이 아니다.

## 실제 화면과 한계

Learner root `e81840e3-accd-4d34-9f17-fa761c969681`에서 양측 LU1–11 **22개 카드**를 실제 선택했다. 코드·이름·side가 맞고 점 label 0/geometry 증가 0이었다. 같은 root/renderer/camera/target/원래 넙다리곧은근 선택/레이어/pose를 유지했다. 오른쪽/왼쪽 LU1·LU9·LU11 PNG/JSON과 390×844, 1024×768, 1440×900 카드 화면을 남겼다. 390 카드의 긴 안내는 기존 카드 스크롤을 사용한다. 44px touch/패널 접힘/선택 점 framing 등 AT7 전체 인수까지 완료했다고 부르지 않는다.

HMR 이후 별도 root `071b9da3-b1f6-4432-acdf-7512e9caadb7`에서 빠른 좌우 전환의 마지막 요청, 즉시 닫기와 잔여 projection/label/update 0을 확인했다. 실제 가슴 클릭은 오른쪽 대흉근 흉늑부의 기존 anatomy source/card 흐름을 열고 learner 표시를 끝냈다. 그 뒤 목록 선택은 기본 왼쪽 넙다리곧은근이었다(`native-restored`); 이를 원래 오른쪽 선택 복원이라고 주장하지 않는다. 최종 전달 화면은 원래 오른쪽 source의 정상 anatomy URL로 열었다.

기존 DEV overlay도 별도 root `5ec984d4-c19b-4d98-99a0-8a15d90e0892`에서 오른쪽 LU1/LU9/LU11과 왼쪽 LU11을 확인했다. 이것은 **기존 미확정 proposal 4개 선택의 회귀**이며 learner 위치 승인 수는 0이다. DEV-off 즉시 snapshot은 scene buffer 진단의 이전 frame 값이 남아 있으므로 이를 최종 GPU 반환 측정으로 사용하지 않는다. 실제 learner OFF의 geometry/update는 baseline과 같다. 최종 console warn/error 0이다.

G1/G2의 같은 모델·카드/side 기준은 확인했다. **실제 점과 카드의 위치 일치 및 자연스러운 경혈 framing은 승인 위치가 없어 미달**이다. 새 관찰 시점 메뉴·보기옵션 재배치·홈·로딩 변경은 없다. 미확정 좌표를 보여 성공 화면처럼 만들지 않았다.

## 비용·검증·보존

- 관련 자동 검사 **47/47**, TypeScript typecheck, Vite production build, 실제 evidence validator와 sync/check 통과. 큰 chunk warning을 유지했고 임계값/예산을 올리지 않았다.
- 공통 carrier **83 chunks / 813,096 bytes / 40,520 triangles** 그대로. 새 geometry/triangles/textures 0.
- Learner data **6,422 bytes**. Initial JS **1,325,559 bytes**, AT5 대비 **+1,547**; heavy Review 약 25.9kB와 carrier loader는 lazy. 2MiB initial JS 및 20MiB/96MiB/1M/8MiB 기존 예산 유지.
- 실제 빈 learner overlay 추가 buffer **0**, baseline scene mesh buffer 진단 **6,947,334 bytes**, shared update **0**, carrier request 0. Driver heap/GPU 시간/FPS는 측정하지 않았다.
- 기존 DEV 검토의 carrier 포함 논리 buffer **46,704 bytes**, triangles **3,576**, route bytes **2,040**, textures 0을 그대로 대조했다. 전체 scene mesh buffer 진단은 Line을 제외하므로 둘을 같은 계측으로 혼합하지 않는다.
- 원본 Blender와 역사/등록 carrier/source 입력 **148개 hash**, 기존 tracked WIP **45개 hash**가 동일하다. 원본/OpenSim_Models/T13/사용자 WIP에 쓰지 않았다. 기존 5,966개 WIP는 로컬 커밋에서 제외한다. untracked WIP의 byte 전수 검사를 했다고 주장하지 않는다.

EXECUTION은 AT6 record만 갱신했고 **partial이므로 nextUnit=AT6을 유지**했다. AT7이 order상 다음이며 dependsOn=AT6임을 확인했다. 계획상 프롬프트는 `next-AT7-prompt.txt`에 남겼으며 현재 미달을 건너뛰는 실행 승인이 아니다. 숫자 T/AC·다른 AT·NEXT/STATUS 상태를 덮어쓰지 않았다.

소유 변경: learner compact data, 공통 adapter/compiler의 shared trunk side 보완, 기존 overlay/entry/card/loader integration, 관련 테스트, AT6 report/evidence 및 AT6 실행 기록. 제외: DatasetSceneAdapter를 포함한 기존 WIP, 원본/OpenSim_Models/T13, 역사 AC1/AC2·AT3/4/5 및 carrier binary, 다른 task와 보기옵션/홈/로딩. 정확한 파일 목록과 커밋 hash는 commit-scope/receipt에 기록한다. AT7 자동 실행·push·배포·진단·치료·침 시뮬레이션은 하지 않았다.
