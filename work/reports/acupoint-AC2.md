# AC2 — 폐경 점·체표 학습선·따라보기

2026-10-11. **학습 흐름과 장면 연결은 검증됨. 실제 혈위의 acceptance는 partial이다.** 오른쪽 LU1–LU11 및 독립 원본으로 작성한 왼쪽 11점은 모두 `unresolved` 제안이며, 제품으로 내보낸 확정 좌표는 **0개**다. AC1의 기술 검증을 재사용했지만 AC1의 LU1·LU9·LU11 미확정을 위치 승인으로 바꾸지 않았다.

이번 명시적 AC2 요청을 구현 근거로 사용했다. 과거 deferred/다른 task 미승인으로 전역 구현을 차단하지 않았다. AC3는 프롬프트만 남겼으며 실행하지 않았다.

## 사용할 수 있는 흐름

현재 개발 서버 `http://127.0.0.1:5183/`의 기존 학습 화면에서 **경혈 학습 검토**를 누른다. 최소 진입점은 DEV에서만 보이며, heavy module과 좌우 데이터는 진입/전환 후 불러온다. URL의 별도 flag가 없어도 개발 검토를 열 수 있다. production 빌드에는 검토 UI·overlay·좌표 fixture가 포함되지 않는다.

첫 진입은 기존 카메라에서 가슴과 오른팔을 보여주는 짧은 이동이다. 이후 **경혈 따라보기**는 LU1→LU11을 선택하며 가슴(LU1–2) → 위팔(LU3–4) → 팔꿈치·아래팔(LU5–8) → 손목·엄지(LU9–11) 구간에서만 카메라를 이동한다. 각 점의 기본 dwell은 3.2초, 카메라 이동은 기존 scene의 0.56초 보간을 쓴다. 별도 timer/RAF/renderer/인체를 만들지 않았다.

선택 점만 자세한 화면 label과 카드가 있고 다른 점은 코드 버튼으로 선택한다. 이전/다음/정지/복귀/전체 경로를 제공한다. 수동 orbit·wheel·방향 키·기존 카메라 명령은 tour와 자동 복귀를 중단한다. 명시적으로 다시 누른 따라보기/복귀는 사용자 명령으로 처리한다. OS reduced-motion 초기값/변경 구독을 유지하고, 검토 패널의 ‘이동 줄이기’도 즉시 이동을 사용한다.

기존 보기옵션·홈·로딩 디자인은 수정하지 않았다. active 검토 카드가 기존 상세 카드 공간을 사용하며, canvas가 남은 공간에 맞춰 줄어든다. 기존 카드의 선택 state는 유지된다. 390 화면에서는 기존 보기 도구 위쪽 canvas와 아래쪽 286px 검토 카드 공간을 분리하고, 선택점이 실제 남은 canvas 안에 들어오는지 검사했다. ‘체표 학습선 · 위치 미확정 · 교과서 설명 준비 중’은 좁은 카드에서도 계속 보인다.

## 이름·기본 위치와 설명 준비 상태

[KMCRIC 폐경 목록](https://www.kmcric.com/database/acupoint/LU)에서 코드를 이름과 대조했다: LU1 중부, LU2 운문, LU3 천부, LU4 협백, LU5 척택, LU6 공최, LU7 열결, LU8 경거, **LU9 태연**, LU10 어제, **LU11 소상**. 기본 위치 요약은 [WHO 표준 위치 원문 보관본](https://www.medbox.org/index.php/dl/627a4de115110145a1723f64)의 인쇄 p.26–31에 근거한다(WHO 2008, 2009 재인쇄). 기존 조사 자료를 반복 다운로드하지 않았고 외부 3D 점 좌표를 복사하지 않았다.

이름·기본 위치·비례촌/손가락촌/landmark 문장은 PointConcept에, 모델의 제안 anchor는 PointInstance에 분리했다. 사용자 교과서 판본·해설·자세 설명은 미입력/null이며 카드에서 ‘교과서 설명 준비 중’으로 표시한다. 표준 위치 문헌 요약은 교과서 해설이나 3D 혈위 승인과 별개다. 진단·치료·침 시뮬레이션 데이터는 추가하지 않았다.

## 실제 carrier와 좌우 검증 범위

AC1 report, 실제 runtime-dataset/runtime-integration, carrier hash·원본 probe를 읽고 현재 source cache와 대조했다. AC1에서 확인한 현재 skin mesh 부재를 그대로 보존하여 **원본 구조에 맞춘 국소 학습용 체표 작성**을 확장했다. 전신 skin을 확보한 결과는 아니다.

`build_learning.py`는 기존 ZA detail GLB/unit metadata SHA를 확인하고 각 source matrix를 한 번 적용한다. native world bounds와 integration bounds는 0.0001m 허용차로 대조한다. frame=`HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR`, unit=m, pose=`ZA-9f08a17ea0115fed-frame0-autoexec-off`; 인체 오른쪽은 X<0, 왼쪽은 X>0이다. 각 점의 작은 9×9 patch와 좁은 학습 ribbon을 고정 topology로 작성했다. 앞쪽 envelope를 못 찾은 vertex의 nearest-height fallback 수는 점별 carrier-validation에 기록했다. 근육·뼈 envelope와 clearance는 피부 두께/정확한 혈위의 증거가 아니다.

왼쪽은 오른쪽 좌표를 mirror하지 않았다. 각각 다른 `.l` native source key·matrix·bounds·GLB SHA를 사용한다. 원본 저장 없이 읽은 `Nail plate.l`/`Perionyx.l`의 연결 component와 왼쪽 엄지 끝마디뼈를 독립 대조했다. 이 검증은 source/frame/side/anchor의 기술 검증이며 아래의 실제 피부 혈위 승인으로 확대하지 않는다.

| 점 | 좌우 각각 확인한 native 기준 | 남은 위치 검증 |
|---|---|---|
| LU1 | 쇄골, 첫째/둘째갈비뼈·연골, 대흉근/근막 | 피부 첫째늑간·정중선 6 B-cun |
| LU2 | 쇄골 가쪽 아래/주변 구조 | 오훼돌기 함요·쇄골아래 삼각·피부 |
| LU3·LU4 | 이두근 가쪽·상완근막의 위쪽 bounds | 실제 겨드랑주름·3/4 B-cun·개인 비율 |
| LU5 | 노뼈 몸쪽·이두근 주변 | 팔꿈치주름·이두근건 요측 함요·굴곡 자세 |
| LU6 | 노뼈·건 주변 및 팔꿈치/손목 proxy 구간 | 실제 7 B-cun·팔 앞가쪽 피부 |
| LU7 | 노뼈·긴엄지벌림근/짧은엄지폄근 | 붓돌기 위 함요·건 사이·1.5 B-cun |
| LU8 | 노뼈·노쪽손목굽힘근 주변 | 노동맥·손목주름에서 1 B-cun |
| LU9 | 노뼈 말단·주상골·긴엄지벌림근 주변 | 손목주름·동맥·건 사이 실제 피부 함요 |
| LU10 | 첫째손허리뼈·손바닥 근막 주변 | 실제 적백육제·엄지두덩 피부 중점 |
| LU11 | 각 side의 엄지 끝마디뼈·원본 손톱 component | 손톱 요측 몸쪽 모서리·0.1 F-cun·피부 외피 |

**표의 오른쪽/왼쪽 22점 모두 실제 위치는 unresolved다.** 비례촌을 고정 mm로 환산하지 않았다. LU11 제안점은 현재 보이는 뼈보다 가쪽에 놓이며 손톱 자료와 뼈의 관계만으로 정확한 소상으로 채택하지 않는다. LU2–8/10 역시 source bounds로 만든 AI 제안을 교수 검토 없이 정확한 혈위로 주장하지 않는다.

오른쪽 carrier SHA=`82991216229e5332bdd53c5e092341373a8b9b7ad8482ebfe99fe4194487a69a`; 왼쪽=`23c60b5d92a4b4370d40150496470ddffcf7b4e4a132bb1fccf3969188f9a42c`. 좌우 각각 1,231 vertices / 1,728 triangles다. AC1의 hash를 덮어쓰지 않았다.

권리는 AC1의 원본 계보/CC BY-SA 4.0 로컬 기술 관찰 범위를 재사용했다. source 권리의 로컬 지원, 위치 검증 unresolved, AI proposal=true, 교수 검토 not_performed, 공개 재배포 held를 독립 상태로 유지했다. 기존 상류 예외나 공개 승인을 새로 만들지 않았다.

## 경로·선택·카메라 소유권

선은 `kind=surface_teaching`인 AI 작성 학습 순서선이다. 좌우 각각 carrier hash/side와 연결된다. 전통적 전체 유주·분지·내행을 표현하지 않으며 해당 source/reference를 빈 배열로 둔다. classical route=0, territory=0, SinewPath=0이다. 공통 schema/anchor adapter는 재사용하고 nameSources만 별도로 추가했다.

선택은 `{kind:'acupoint', code, side}`이며 dataset/source ID로 위장하지 않는다. 점 raycast 우선권은 실제 보이는 anatomy보다 앞에 있는 점에 한정한다. carrier 넓은 면은 click을 받지 않는다. 기존 근육·뼈 선택/pose 변화 시 review가 해제되고 원래 카드가 열린다.

기존 단일 observation 복귀값을 owner별 `CameraSessions`로 교체했다. anatomy/acupoint/motion의 return camera를 따로 저장하고 owner 이전 때 revoke를 호출한다. 비활성 owner의 늦은 종료가 현재 camera를 복원할 수 없다. motion 시작 시 motion owner를 확보하고 정지 체표를 먼저 종료한다. review 진입은 기존 motion 정상 복원 경로로 실제 pose/resource를 되돌린 후 static carrier를 연결한다. 변형 추적을 구현하지 않았으므로 움직임 위에 고정 좌표를 남기지 않는다.

module import/data fetch의 세대 token·AbortController와 side/unmount cancellation을 구현했다. hash 검증 후에도 취소를 다시 검사한다. 해제 때 geometry/material/label/listener/shared update를 회수하고 진행 중 camera 보간을 취소한다. shared sphere geometry를 한 번만 해제하며 source geometry는 손대지 않는다.

## 실제 검증과 비용

자동 검사 **18/18**, TypeScript typecheck, 전체 production build 및 fixture 제외 검사를 통과했다. `finalize_evidence.py` → `validation.json`에 좌우 anchor/hash/native source SHA, 실제 화면·카메라·클릭 evidence와 보존 검사 결과를 연결했다. 실제 console warn/error는 최종 새 탭에서 0건이었다. 기존 큰 production chunk 경고는 빌드 로그에 그대로 남겼고 임계값을 바꾸지 않았다.

- 1440×900 오른쪽 11점 전부, 1024×900/390×844에서 네 구간과 LU11, 왼쪽 1024에서 11점 전부를 실제 선택했다. 각 세트 안의 AnatomySceneRoot는 하나다. 선택점의 frustum/패널을 뺀 canvas 안전 영역을 검사했다. 최종 390 화면에서는 보기 도구·카드·canvas rect 겹침이 없었다.
- 실제 자동 tour는 LU11까지 끝난 뒤 원래 camera/target으로 정확히 복귀했다. 자동 trace는 처음 일부와 완료 상태만 저장했으며 11개 자동 중간 frame 전수 기록으로 부르지 않는다. 순서/네 구간 전환은 결정적 테스트와 11개 실제 수동 화면으로 추가 확인했다.
- 수동 orbit은 paused/autoReturn=false가 됐다. 닫은 뒤 camera/target도 완전히 같고 update=0이었다(`manual-no-return.json`).
- motion owner→정상 원자세→acupoint owner를 실제 화면에서 확인했다. anatomy origin observation→acupoint→닫기의 원래 camera/attachment observation을 보존했다. 선택 source ID도 바뀌지 않았다.
- 실제 LU11 점 클릭은 typed point만 바꿨다. 엄지 뼈와 이두근 click은 overlay를 종료하고 기존 해부 카드를 열었다. active side 재클릭 및 빠른 좌우 전환 세 쌍에도 canvas=1, 올바른 side 11점이었다.
- 30회 ON/OFF에서 geometry 397→399→397, shader 2→4→2, shared update 0→1→0이 반복되어 증가하지 않았다. carrier 표시 ON에서는 geometry=400이며 다시 해제된다.
- OFF에서 heavy module/data 실제 resource 요청은 0이었다. ON에서 Review/Overlay/side JSON이 요청됐다. ‘이동 줄이기’ 즉시 이동은 실제로 검증했다. OS 설정 자체를 바꾸지는 않았으며 OS media subscription/기존 controller 정책은 유지했다.

같은 camera/target에서 캐리어까지 표시한 비교는 `same-camera-cost.json`에 있다.

| 비용 | 측정 |
|---|---:|
| 오른쪽 / 왼쪽 data | 133,325 / 131,968 bytes |
| active carrier position/normal/index buffer | 39,912 bytes |
| marker·line 포함 추가 GPU buffer 추정 | 46,704 bytes |
| 추가 texture | 0 |
| draw calls: OFF / 점+선 / carrier ON / 해제 | 672 / 684 / 685 / 672 |
| 실제 render triangles: 동일 순서 | 486,184 / 488,032 / 489,760 / 486,184 |
| geometry 객체: 동일 순서 | 397 / 399 / 400 / 397 |
| 양쪽 data 포함 보수적 overview bytes | 20,307,809 / 20,971,520 |
| carrier 포함 보수적 overview triangles | 900,788 / 1,000,000 |
| 해당 active queue + overlay buffers | 9,098,368 / 100,663,296 bytes |
| production initial JS | 1,324,688 / 2,097,152 bytes |

기존 20MiB overview / 96MiB geometry / 1M triangles / 8MiB chunk 예산은 올리지 않았다. GPU driver 전체 heap/elapsed GPU time은 미측정이다. 표의 GPU bytes는 실제 typed-array attribute/index 할당·upload 추정으로, driver overhead/CPU JSON heap과 구별한다. 화면별 frustum culling 비용을 동일 카메라 비교 수치와 혼합하지 않았다.

## 보존·커밋·다음 경계

시작 HEAD=`6e7f84518aef547a76b6d0e120b64a789f862e52`. 기존 WIP 5,960개 file SHA가 `before/baseline.json`에 있다. 기존 WIP 중 byte 변화는 DatasetSceneAdapter 하나이고, AC2 소유 8줄을 제거하면 시작 파일과 정확히 같다. 원본 Startup.blend SHA=`9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd` 불변을 다시 확인했다. 원본/source-cache/OpenSim_Models/T13/다른 task WIP에 쓰지 않았다.

포함: AC2 검토 UI·tour·native 좌우 제안 데이터/evidence, owner별 camera sessions, viewer DEV 진입, DatasetSceneAdapter의 source-selection/pose 알림 및 motion owner 추가분 8줄, EXECUTION의 AC2 feature 기록, 이 보고서와 AC3 prompt. Adapter는 HEAD+8줄 별도 index snapshot으로 stage하여 기존 사용자 6 insertion/3 deletion을 제외한다.

제외: 모든 기존 WIP, 원본/외부 source/다른 task·설계, `before/`의 코드·EXECUTION 전체 복사본 4개, 커밋 뒤 작성하는 receipt. 정확한 포함/제외는 `commit-scope.json`; 커밋 hash/잔여 상태는 로컬 `commit-receipt.json` 및 최종 응답에 남긴다. 숫자 task/active queue/NEXT·STATUS는 바꾸지 않는다.

다음은 `work/reports/acupoint-AC3-prompt.md`의 **프롬프트만** 제공한다. 그 요청이 들어오기 전 AC3를 시작하지 않는다. 실제 피부·개인 비례촌·교수/교과서 검증은 여전히 남아 있다. push/배포/진단/치료/침 시뮬레이션 없음.
