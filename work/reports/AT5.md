# AT5 — 공통 landmark compiler·판정·schema migration

2026-10-11. **AT5의 공통 도구 인수 검사는 완료했다. 실제 혈위 신규 승인은 0개다.** 별도 point 배정이 없는 AT5와 양측 LU 위치를 보완하는 AT6를 구분한다. 기존 LU 22개는 모두 미확정이며 이를 완료 위치로 세지 않았다. AT6는 실행하지 않았다.

## 변경과 입력

AGENTS, 최신 EXECUTION/NEXT, AT5 명세, 30/31 설계, AT4 report와 실제 source/geometry/nail/access/runtime evidence를 읽었다. AC1/AC2 보고서·원본 probe·실제 양측 learning JSON을 재사용했다. 읽은 입력 hash는 `work/evidence/AT5/input-hashes.json`, 원본·권리·frame 계약은 `source-contract.json`에 있다. 재다운로드와 Blender 원본 재작성은 0회다.

기존 schema/anchorAdapter를 확장하고 `anchorCompiler.ts` 하나를 만들었다. 등록 carrier와 native geometry의 SHA, frame, metre, dataset revision, 정지 pose, 인체 좌우 및 triangle/barycentric 주소를 재현한다. 지표는 명시적으로 작성한 해부 annotation이며 자동 탐지기가 아니다. 표면 대응의 허용차는 replay 조건으로 기록하며 피부 두께나 정밀 혈위의 증거로 해석하지 않는다.

- landmark: 의미가 명시되고 실제 source 주소와 체표 대응을 확인한 지표를 사용한다.
- B-cun: 문헌 denominator와 확인된 두 지표 사이의 연결된 체표 path 비율을 사용한다.
- F-cun: 해당 모델의 손가락촌 지표와 문헌 calibration을 사용한다. 고정 mm로 바꾸거나 지원 path 밖으로 외삽하지 않는다.

path의 각 segment는 동일 triangle 안에서 계산한다. 연결 triangle과 endpoint의 topology를 검사하여, 좌표가 우연히 겹치는 다른 component/손가락으로도 건너가지 않는다. bounds·nearest·mirror·unresolved 및 단순 상태 이름 변경은 위치 승인 경로가 아니다. 원문과 source locator를 보존하며, 실제 입력 작성자는 `confirmed/anatomical_correspondence`를 문헌과 native 지표 대조 없이 부여해서는 안 된다. 이 compiler는 명시한 입력을 검증하는 도구이며 범용 해부학 자동 판독기가 아니다.

## 독립 판정과 migration

V2 assessment는 technical replay, educational approximation, AI/human 작성 provenance, 위치 근거/check, 교수 검토, 로컬 권리, 공개 재배포를 분리한다. 기존 `aiProposal`와 모든 V1 field를 그대로 유지한다. 실제 위치는 교육용 개략으로만 판정할 수 있으며 정확한 피부 취혈/임상 위치 등급을 추가하지 않았다.

`productInstances`의 영구 `!aiProposal` 제외를 없앴다. 실제 의미 있는 지표·문헌 관계·surface 대응·side/pose/frame/hash가 확인되고 로컬 source 권리가 지원되는 위치만 통과한다. AI 작성과 교수 미검토/공개 held는 독립 상태다. 로컬 source 권리가 held이거나 위치가 미확정인 대상은 계속 제외한다. scope와 input domain 및 검증 binding을 함께 확인하여 fixture의 이름/scope만 바꿔 제품으로 내보낼 수 없다.

`migratePlacementDocument`는 add-only/idempotent V1→V2 변환이다. 역사 원문 JSON을 덮어쓰지 않는다. 실제 오른쪽/왼쪽 LU 입력 각각 11개에서 원래 code/side/anchor/source key/AI/missing/review field가 모두 동일함을 검사했다. 근거가 없는 기존 위치는 migration으로 승격하지 않는다.

`projectLearnerInstances`와 `resolveLearnerProjection`은 실제 geometry bytes, frame/pose/context 및 motion/cancellation을 확인하고 공통 adapter로 고정 주소를 재현한다. 작은 runtime projection은 author/input SHA/교육용 등급/독립 review·public 상태를 유지한다. 원문·실패 이력·geometry·fixture는 learner projection에 복사하지 않는다.

## 재개와 실제 위치의 남은 입력

공통 offline CLI는 `atlas-web/scripts/compileAcupointAnchors.ts`이다. 사용법과 입력 계약은 `atlas-data/acupoints/anchor-rules/README.md`에 있다. 원문 byte edition은 `inputs/<sha256>.json`, 과거 시도는 `attempts/<sha256>.json`으로 보존한다. rule·관련 evidence·실제 geometry bytes·compiler version fingerprint가 같은 성공 unit만 재사용한다. 실패 unit은 재개하고, 관련 입력이 바뀐 unit은 다시 계산한다.

실제 LU 입력 22개에서 bounds 규칙을 명시적으로 거절했다. carrier/anchor의 기술적 재현이 실제 혈위 승인이라는 뜻은 아니다. migration 원문 hash와 보존 검사는 통과했으며 local learner eligible **0/22**다. landmark/B-cun/F-cun/정중 양성 기술 fixture **4개**는 기술 검사만 통과했고 product export **0개**다. positive AI 정책 계약 시험도 synthetic 테스트 환경 안에서만 수행했으며 실제 해부 위치로 기록하지 않았다.

`compiler-validation.json`과 `remaining-location-units.json`에 각 LU code/side의 원래 missing 및 기본 위치 source를 그대로 연결했다. AT6에 필요한 입력은 point별 native 해부 annotation, 문헌 관계, 지원 carrier 대응이다. B-cun은 실제 지표 endpoint/denominator/path, F-cun은 실제 손가락촌 calibration/조갑각 방향과 지원 표면이 필요하다. AT4의 입 안/회음 reference를 다른 피부로 옮겨 미지원 위치를 채우지 않는다. 이 목록은 미완의 실제 위치 자료이며 AT5 compiler 인수 실패를 숨긴 목록이 아니다.

## 화면·카메라·수명

기존 DEV `경혈 학습 검토`에 migration과 projection 검사를 연결했다. 기존 카드 문장·점/선의 미확정 안내와 typed acupoint 선택을 유지했다. 보기옵션·홈·로딩·관찰 시점 메뉴·CSS를 변경하지 않았다. 새 renderer, body, 전역 camera manager, task별 overlay는 없다. production learner 진입/실제 LU 위치 데이터는 AT6 범위로 남겼다.

실제 화면 검사에서 AC2의 좌우 전환 복귀 race를 발견했다. 새 side overlay가 이전 복귀 animation 중간 시점을 저장하여 종료 후 원래 시점으로 돌아가지 못했다. 검토 진입별 복귀 snapshot 하나를 공통 overlay에 전달하도록 고쳤다. dispose는 현재 acupoint camera owner일 때만 취소/복귀하며 foreign owner의 카메라를 빼앗지 않는다. 기존 CameraSessions와 update clock을 재사용한다. 실패 화면과 원인을 `pre-camera-fix-*`, `camera-regression.txt`로 남겼다.

최종 실행본의 **동일 root `25637efd-2753-4493-9cb7-59d96c6165fc`**, 한 canvas/renderer에서 오른쪽 LU1·LU9 태연·LU11 소상 및 왼쪽 LU11의 실제 카드/side/label을 확인했다. 4개 선택점은 패널을 제외한 safe viewport 안이다. 위치는 모두 unresolved이며 화면에서 확인한 수를 승인 수로 바꾸지 않았다. 양측 전환 후 닫으면 position/target이 진입 전과 1e-9 이내로 일치한다. 선택은 원래 오른쪽 넙다리곧은근이며 레이어·hidden/translucent/motion 상태를 보존했다.

앞선 별도 HMR 검증 세션에서는 수동 ArrowRight가 tour를 paused, autoReturn=false로 만들고 종료 후 수동 camera가 그대로 유지됨을 확인했다. 뼈 OFF 유지, 빠른 좌우 전환 마지막 요청, 즉시 닫기, 실제 대흉근 클릭과 원래 선택 복원을 기록했다. HMR 전후 root들을 최종 한 root 검사와 구분했다. 움직임 중/owner 해제 후 변형 override가 남은 경우에는 공통 overlay/runtime guard를 자동 검사했다. 새 motion animation 화면 검사를 수행했다고 주장하지 않는다.

이번 UI 검증은 기존 desktop **1280×720** 범위다. 새로운 responsive UI를 만들지 않았으며 390/1024 전체 흐름이나 14경맥 탐색 완료로 확대하지 않는다. 최종 console warn/error **0건**이다.

## 비용과 검사

- 관련 자동 검사 **40/40**: 고정 입력 재실행, bounds/nearest/mirror 거절, wrong side/frame/pose/unit/hash 격리, component 건너뛰기 거절, 실제 LU migration 보존, failed-only resume, static guard, foreign-owner dispose, 기존 carrier/tour/CameraSessions.
- `tsc -b --pretty false`, Vite production build, `verifyAnchorCompiler.ts`, `validate-evidence.py` 통과. 전체 역사 npm suite를 재실행했다고 주장하지 않는다. 기존 큰 chunk warning은 보존하고 임계값을 올리지 않았다.
- AT3/4 공유 carrier **83 chunks / 813,096 bytes / 40,520 triangles** 그대로다. AT5 신규 geometry/GPU/texture **0**.
- 실제 기존 AC2 검토 overlay: encoded JSON **133,325 bytes**, GPU geometry buffer **46,704 bytes**, carrier 포함 **3,576 triangles**, textures **0**, shared geometry **3**. 기존 예산 20MiB/96MiB/1M/8MiB를 유지한다. 전체 AT4 carrier와 별도 검토 overlay를 동시에 활성화하는 새 흐름은 만들지 않았다.
- 최종 OFF GPU buffer **6,947,334 bytes**로 baseline과 동일, update 구독 **0**, point projection/label 해제. initial production JS **1,324,012 bytes**, AT4 대비 증가 **0**. compiler·migration 검토 모듈·fixture·private evidence는 production bundle에서 제외됨을 실제 파일로 검사했다.

검사 재현 명령은 evidence의 로그/공통 CLI와 `validate-evidence.py`에 있다. Node는 설치된 Codex runtime을 사용했다. 외부 점 좌표·환자 체형·진단·치료·침 시뮬레이션을 추가하지 않았다.

## 상태·보존·로컬 커밋

EXECUTION은 `/featureWorkUnits/AT5`와 feature plan의 `nextUnit=AT6`만 변경했다. 최신 order와 AT6.dependsOn=AT5를 대조했다. numeric T/AC/AT1–4 기록과 NEXT 등 다른 실행 기록은 보존한다. sync/check 결과는 `sync-execution.log`, `sync-check.log`에 남긴다.

기존 사용자 WIP **5,966건**을 제외한다. 변경 상태였던 tracked WIP 45개는 byte hash를 대조했고, 지정 역사/design/source 입력 17개도 hash가 동일하다. Blender 원본은 동일 SHA이며 OpenSim_Models/T13에 쓰기 작업을 하지 않았다. untracked WIP는 baseline path/status와 최종 잔여 집합을 대조한다; 모든 untracked byte를 전수 hash 검사했다고 주장하지 않는다.

포함: 공통 acupoint schema/adapter/compiler/policy/migration, 기존 review/overlay의 integration·camera 보존 수정, 관련 tests/CLI/입력 안내, AT5 report/evidence 및 지정 EXECUTION 포인터. 제외: 사용자 WIP, DatasetSceneAdapter의 기존 변경, 원본/OpenSim_Models/T13, AC1/AC2·AT1–4 역사 evidence, 기존 carrier binary, 보기옵션·홈·로딩, 그 외 task.

로컬 commit hash/정확한 파일 목록은 `commit-scope.json`와 후속 `commit-receipt.json`에 기록한다. push/배포는 수행하지 않는다. **다음은 AT6이며 자동 실행하지 않았다.** 붙여 넣을 프롬프트는 `work/evidence/AT5/next-AT6-prompt.txt`이다.

실제 primary 로컬 commit: `8853633b19190614d1331efe89b34da37f4d5833` — 소유 172개 파일. 커밋 직후 남은 변경은 baseline WIP 5,966건과 path/status가 정확히 같고 tracked WIP 45개의 byte hash도 같다. 후속 영수증 commit은 이 report와 `commit-receipt.json` 두 파일만 포함한다.
