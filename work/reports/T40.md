# T40 로컬 전달 결과 — 2026-10-06

**T40 completed/passed, nextUnit=null.** 현재 지원 앱을 개발 서버 없이 로컬에서 실행·검사·재시작할 수 있다. `productReadiness=local_app_ready`, `contentCompleteness=partial`이며 전 해부학·전신 정상 모형 완성이나 공개 배포 승인은 아니다. 이번 실행은 T40만 수행했다.

## 전달 대상과 수정

실제 T85 completed/passed와 최신 optimization 및 motion-context 검증을 확인했다. 지원 앱의 unresolved product blocker는 0이다. 기존 dist에는 motion GLB가 있었지만 전신/신경 dataset·integration·compiled chunk URL은 dev middleware에서만 제공됐다. 따라서 기존 dist만으로 독립 실행 가능하다고 안내하지 않고, 기존 검증된 wholeBodyPlugin의 projection과 chunk 검사를 재사용하여 완전한 고정 패키지를 만들었다. 새로운 viewer나 원장 브라우저 파서는 추가하지 않았다.

최종 패키지는 `atlas-web/dist-local/local-20261006032053779-deedfed2/`, CURRENT manifest SHA-256은 `e51b978ec763cf8a718489424f4fb2af6d1d277bbcf3c743e6532d77763c6f1b`다. 공개 URL 허용 파일 99개(앱5·projection2·모형18·motion74), public payload 253,769,494 bytes와 private 원장/색인 105,085,638 bytes다. launcher와 manifest를 포함한 정확한 폴더 바이트 수는 final-validation.json에 기록했다. 고유 GLB 파일 수를 독립 근육·작용·전체 extent 완료 수로 세지 않았다.

패키지는 Node.js 24 이상만 있으면 저장소·dev middleware·원본·인터넷 없이 실행한다. 127.0.0.1에만 bind하며 정확한 URL allowlist를 쓴다. 내부 원장·provenance·source는 URL로 열리지 않는다. 시작 시 파일/원장/index/launcher를 검사하고, 현재 파일 바이트와 private dependency를 확인한 뒤에만 ETag 304를 응답한다. 누락·변조·stale index에서는 실패하고 다른 모형으로 대체하지 않는다. 새 snapshot은 검증 후 atomic CURRENT 교체로 등록하며 이전 정상 snapshot은 보존한다.

## HEAD와 WIP 의존성

기준 HEAD는 `eefd8f161689b55ad130e48c64599c4b663e842c`, 전달 기준은 **preserved_working_tree_snapshot_not_commit_only**다. standalone package는 고정 바이트로 실행하므로 저장소의 WIP를 이후에 수정해도 해당 패키지는 바뀌지 않는다. 그러나 HEAD만 checkout하여 최신 콘텐츠를 재생성할 수 있다고 주장하지 않는다.

실제 전달 자산 92개 중 HEAD 밖의 로컬 자산은 33개다. 자산별 원본 경로·실제 SHA/bytes·HEAD SHA·등록 URL·T59/T66 작성 또는 T77/T100/T66 compiler 소유 범위는 asset-provenance.json에 기록했다. 임의로 다른 작성자의 자산을 stage하지 않았다. 런타임 입력의 HEAD 차이는 snapshot-manifest.json sourceDependencies에 기록했으며 T40 package scripts 변경과 기존 WIP 소유 미확정 상태를 구분했다.

특히 motion-learning.json(103,283,078 bytes)·t66-wave1-registration.json(1,787,960 bytes)과 같은 작성자가 만든 작은 local-motion-delivery-index를 함께 고정했다. 생성된 단일 learnerMotionRuntime freshness를 확인했다. source attachment/card field WIP와 player/presentation/adapter WIP도 실제 bundle 입력 해시로 고정했지만 커밋하지 않았다. 기존 registry/compiled cache와 source 자산은 읽어서 확인하고 별도 패키지로 복사했다. 원본/source-cache/OpenSim_Models/T13 및 기존 자산은 수정하지 않았다.

## 실제 지원 집계

전체 target/membership/region 542/563/12, 근육429/447·기존232 source concepts/462 surfaces, HA130와 역사163(6/20/135/2)을 보존했다. BP3D supplement를 포함한 현재 learner-eligible 표시 단위는 근육472·뼈213·신경195 source 표면이다. 원본 검색 이름 묶음은 근육237·뼈126·신경98이며 이를 독립 해부 개념 수나 TA2 target 수로 바꾸지 않았다. 뼈 target 분모는113, 독립 신경 개념 분모는 미확정이다.

- **근육:** origin/insertion 텍스트가 연결된 source 표면은 각각461/472. 작용/자세 설명 옵션이 있는 표면142, 도달 가능한 재생 표면134·source-option 연결332·고유GLB71. 이 중 실제 muscle_action은38표면·56연결이며 나머지276연결은 자세 관찰이다. 근육429 target의 전체 기능·extent 완료가 아니다. 우선 제품 합격7근육군은20표면·22실제 작용 연결·13GLB로 별도 유지한다.
- **뼈:** 직접 선택 재생 표면166/213·source-option 역할 연결1,581·고유GLB57. moving role이 있는 source133, fixed role97이며 서로 배타적 분류가 아니다. pose control 연결1,567은 반복된 단일 방향 교육용 slider 연결 수다. 독립 정상 DOF 수는 확정하지 않았다. 47표면은 직접 재생 연결이 없다. 기시/정지는 근육의 필드이며 뼈 카드에 그 필드가 없다는 이유로 실패 처리하지 않았다. 일부 뼈의 관련 근육/표지 설명은 미완이다.
- **신경:** 실제 정적3D195표면·원본 이름 묶음98. 현재 근거/재사용 주행 설명10묶음, 정적 모형 맥락 안내만 있는88묶음. 옛 구현 원장의8개에 후대퇴피·가슴사이신경의 현재 field/hash 검증2개를 더해 계산했다. 기존 원장이 지원한 포착 설명5묶음/미지원93, 운동 관계18행(exact geometry2·문헌 개념16). 동적 pose0·포착 좌표 결속0. field 존재나 “근거 미연결” 문구를 문헌 지원 수로 세지 않았다.

전체 source/side/options와 재생이 없는 source는 feature-coverage.json에 남겼다. 실패 후보·턱/얼굴/호흡 및 E 무결성 복구는 기존 deferred engineering backlog로 보존했고, 진짜 source/관계 미확보와 합치지 않았다. 일부 전체-bone attachment mapping의 미확정61표면/141연결도 T85 원장으로 유지한다. 새 자료/의미/변형 입력이 필요한 항목은 후속 사용자 요청에서 근육·측·작용별로 결정한다. 이번 전달을 이유로 전수 콘텐츠 연구를 반복하지 않았다.

## 검증과 재사용

전달 전용 회귀 **9/9**: 정상 GET/HEAD/ETag, 저장소 없는 재시작, private/unknown/path escape 차단, 누락·변조·private dependency 변경·stale index·symlink·launcher 검사. 모두 임시 fixture에서 검사했고 원본을 훼손해 시험하지 않았다. 실제 고정 파일99개의 HTTP 바이트/SHA 및 ETag 응답은99/99 통과했다. 최종 snapshot의 동일99개 바이트/hash를 대조해 재사용 receipt를 남겼다. 최종 launcher --verify-only도 통과했다.

현재 WIP 입력에서 generator freshness와 production build를 한 번 수행했다. 큰 JS chunk의 기존 권고 경고는 남으며 예산을 올리지 않았다. 최종 패키지는 변경 없는 bundle/input hash를 확인해 재사용했고 geometry/typecheck/전체 suite는 반복하지 않았다. T85의184 unique/455 source-side 최적화 대조·103관련 회귀·331 core context 검사와 T59 별도 오른쪽 앞정강근 근거를 영향 분석하여 재사용했다. 331은 최신 context audit의 행 수이며 별도 T59 원본 clip을 포함한 이번 도달 가능332와 다른 집계다.

실제 production/local 전달 URL에서 홈→왼쪽 앞정강근 선택→반복/재클릭 smooth rest→scrub100%→교육용 각도6.5/0→숨김 guard, 목말뼈 직접 선택→무릎 자세 시범, 정중신경 주행/포착 설명·3D, 깊은종아리신경→왼쪽 앞정강근 작용, 동작 중 정적 신경0/복원 시195표면을 확인했다. 목말뼈의 무릎 시범은 하지 공동 이동 관찰이며 독립 발목 DOF 확보로 세지 않았다. 실제 서버를 종료/재시작하고 페이지를 reload하여 선택/모형/카드 복구·asset failure0을 확인했다. console error0·canvas1이다.

새 실제 viewport는1280×720 CSS/DPR2다. 390×844/1024×900/1440×900은 동일 learner source/CSS/검증된 bundle 자산의 T85 실제 근거를 영향 분석하여 재사용했다. 새3width 또는 실기기 검증이라고 쓰지 않는다. PNG·해시·관찰 결과는 browser-validation.json과 impact-analysis.json에 기록했다.

## 계약과 경계

acceptanceScope: 현재 지원 정상 구조·7우선 근육군 및 기존 지원 motion/bone/nerve 학습을 그대로 실행하는 해시 고정 로컬 전달, private index/asset 검증·복구·실제 learner 흐름.

contractRevision=`app-completion-2026-10-01`, productReadiness=`local_app_ready`, contentCompleteness=`partial`, unresolvedProductBlockers=`[]`. wholeMuscleMotionGoal/wholeBoneMotionGoal/nerveCourseCoverage는 위 실제 지원 수로 별도 기록한다.

Source-only, 기술적으로 검증된 로컬 선택, humanReview=`not_performed`, public redistribution=`held`는 독립 상태다. 교육용 authored weights/trajectory와 source 실측 attachment/normal ROM/힘/활성도를 혼동하지 않는다. 후속 병리 모형은 정상 source geometry/frame/pose/hash를 고정한 별도 파생 데이터 계약에서 시작해야 한다. partial 정상 모형을 병리 구현 준비 완료로 취급하지 않았으며 병리 editor/진단·치료·자침은 구현하지 않았다. 다음 task 자동 실행, 새 task/thread/위임, push/배포는 없다.

실행·설치·복구 안내: `work/delivery/T40/README.md`, `work/delivery/T40/start.command`. 현재 report와 검증 evidence는 T40 소유 변경이며 원조사·다른 task WIP·held 패키지는 커밋에서 제외한다.
