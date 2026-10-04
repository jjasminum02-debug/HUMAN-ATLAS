# T66 — Atlas식 근육 작용 학습으로 방향 수정 (2026-10-05)

T66 전체 판정은 **in_progress / partial**, nextUnit은 **author-and-integrate-normal-motion-bone-and-nerve**로 유지한다. 이번 변경은 실제 지원 애니메이션의 의미·탐색·재생 흐름을 수정했다. 새 동작 GLB 제작이나 전체 근육 작용 완료로 세지 않는다.

## 왜 끝나지 않았는가

1. **학습 목적과 실행 결과의 차이.** 129개 근육 표면/311개 source-action 행은 작용 애니메이션 129개/311개를 뜻하지 않는다. 실제 등록에는 주변 관절 자세에서 따라 변하는 수동 표면이 많이 포함된다. 실제 UI에서 상완이두근 단두의 기본 옵션이 어깨 가쪽돌림 자세 관찰인데도 기능 탭 제목이 ‘이 근육이 하는 일’이었다. 이 의미 혼동을 이번에 수정했다.
2. **배정 문서 결함.** W2 D의 상위 assignments.D에는 16개 key가 있지만 각 key에 assignedTo=null/deferredTo=E가 남아 있다. 이는 별도의 writer 배정 메타데이터 오류다. 실제 턱 변형 실패와 합쳐 해부학 자료 부재라고 해석하지 않는다. 이번 실행은 동결 manifest/worker 결과를 수정하지 않았다.
3. **runner 계약 충돌.** E의 runner-contract.md와 현재 runner를 대조했다. start.json/source-audit.json을 먼저 작성하도록 하면서 runner는 비어 있지 않은 outputRoot를 거부한다. 지정된 뼈 문맥에 대한 typed index도 근육 sourceKeys와 구분되어 있지 않다. 원장 작성자의 입력 누락으로만 돌릴 문제가 아니다. 이 수정은 아직 적용하지 않았다.
4. **모형이 움직임을 설명하지 않는 문제.** E의 38개 기하 통과 후보는 geometry-derived teaching field이며 실제 해부학 작용 축/endpoint trajectory가 아니다. 안구·눈꺼풀·입술·혀 등 동작 결과를 보여 줄 의존 구조도 미확보다. 따라서 기하 통과를 작용 합격으로 바꿀 수 없다. 전체 action-outcome 0건에는 이 사유와 실행 도구 결함이 함께 있다.
5. **실제 제작 결함도 남아 있다.** 손 92행, 하지 29 후보, 호흡 2 후보, 턱 edge/area 실패 및 E 18개 새 bone containment는 각각의 구체적 제작/기하 문제다. 좌우·scope·관통·뒤집힘을 검사에서 빼면 올바른 정상 움직임이 생기는 것은 아니다. 반대로 전체 target extent·사람 승인·모든 신경 pose를 학습용 앱 완료의 전제조건으로 복구할 필요도 없다.

근거: 기존 integration-final/REPORT.md 및 final-blocker-list.json, W2 run-manifest.json, workers/E/summary.md, workers/E/patch-proposals/runner-contract.md. 과거 원장과 실패 자산은 그대로 보존했다.

## 원래 Atlas에서 확인한 방식

사용자가 지칭한 앱은 Visible Body의 Human Anatomy Atlas로 해석했다. App Store 제품 설명, 공식 iPad 사용 문서와 Visible Body Support의 ‘Muscle Action Features | Human Anatomy Atlas’ 영상을 확인했다. 설치된 최신 iPad 앱을 직접 실행한 것은 아니다.

- 공식 문서는 70개 이상 distinct muscle actions, 부위별 목록 및 근육 관련 내용/검색을 통한 접근을 설명한다.
- 동작 구간에서는 근육을 선명하게 표시하고 복귀 구간은 흐리게 표시하며 더 빠르게 되돌린다. 복귀는 반대 근육 작용의 시범과 구분된다.
- 이를 기반으로 **동작·관절 family를 중심으로 하나의 장면을 작성하고 관련 근육을 연결**하는 구성을 권고한다. 전체 근육 원장은 유지하며 개별 근육마다 별도의 엔진/정밀 생리 시뮬레이션을 만들 필요가 없다. 해당 앱의 자산을 가져오거나 모든 근육이 개별 생리 시뮬레이션된다고 주장하지 않는다.

공식 자료:
- https://apps.apple.com/us/app/human-anatomy-atlas-2027/id1117998129?platform=ipad
- https://help.cengage.com/visible-body/student/visible-body/atlas-muscle-actions-ipad.html
- https://www.youtube.com/watch?v=NjXTSFc5uaY

## 실제 구현

- 전 지원 집합에서 **근육 작용 찾기**를 생성했다. 부위 선택 → 동작 목록 → 관련 근육·좌우 선택 → 기존 모형에서 시범으로 연결된다. 새로운 초기 근육 shortlist는 만들지 않았다.
- 목록에는 기존 T59 1개 + 재사용 가능한 W1 A 34개의 exact source-action 연결만 들어간다. **13개 동작 라벨 / 35개 연결 / 19개 source 근육 표면**이다. 13은 목록 라벨 수이며 상용 앱의 70개와 직접적인 백분율 비교가 불가능하다. 현재 목록은 손·오른쪽 앞정강근 중심이며 전신 작용 완성이 아니다.
- W1 C 4행과 기존 주변 자세 관찰은 작용 목록에서 제외했다. 기하 변형 또는 citation이 있다는 이유만으로 작용으로 승격하지 않고 `t66-motion-learning-intents.json`의 명시적 검토를 사용한다. 새 target extent 승인은 0이다.
- 지원되는 작용을 기본으로 선택한다. 주변 자세에는 ‘관절 움직임과 주변 구조’ 제목과 구분 안내를 보여 준다. ‘자세에서 살펴보기/관찰’ 반복 문구를 화면 동작명에서 정리하되 시작 구간/일부 범위 제한을 지우지 않는다.
- 기존 CTA **움직임으로 이해하기** 하나를 유지한다. 동작 강조 → 1.7배 빠른 중립 복귀 및 부드러운 색 흐림 → 반복. 재클릭 시 0.7초 부드러운 rest 복원, scrub 시 선택 자세 유지. 별도 느리게/멈춤/처음 자세 버튼을 추가하지 않았다.
- 재클릭이 카드에 저장된 상태 대신 실제 재생기의 실행 상태를 따르게 수정했다. 중간 브라우저 검사에서 한 번 복원이 끝나지 않은 사례를 기록했고, 실제 clock/반복 endpoint 상태 동기화 및 회귀 검사 뒤 두 번째 왕복의 복원까지 확인했다. 초기 끝점 완료 신호 추정만으로 원인을 확정하지 않았다.
- scene/renderer/camera/frame clock을 추가하지 않았다. geometry 갱신은 기존 시계를 사용하고 카드 진행 표시는 최대 10Hz로 줄였다. 자산 각도/변형/기존 T59 +30% 변경을 다시 확대하지 않았다.

## 검증과 한계

- 관련 자동 회귀 **51/51**, typecheck, production build, learner 배포 누출 검사가 통과했다. 기존 content/schema/source-policy/decoder 검사는 변경 영향이 없는 동일 입력 결과를 재사용한다. checks.json과 개별 로그에 기록했다.
- 실제 브라우저에서 작용 목록의 exact source/좌우 연결, 두 번째 반복 후 재클릭 복원, 색 흐림, 끝점 scrub 유지/재생, 숨김 취소, 근육 layer-off 취소, 좌우 전환, 뒤로 이동, 주변 자세 의미 구분을 확인했다. 한 canvas와 같은 root/camera를 유지했다. 최종 reload 이후 console error 0이다.
- **실제 화면은 825×807**이었다. 크기 변경 API에 390/1024/1440을 요청했지만 DOM과 캡처 크기는 바뀌지 않았다. 이 요청을 세 크기의 실제 QA 합격으로 세지 않는다. 과거 변경 전의 세 크기 검증은 역사 근거로만 유지한다. 새 목록/카드의 그 크기 재검증은 남는다.
- 관찰 표본의 warm render CPU P95 약 1.9–2.2ms, frame interval P95 약 18–18.4ms. 장면 loading/LOD가 함께 변하므로 이전과 통제된 성능 비교나 전 앱 예산 합격으로 해석하지 않는다. GPU/VRAM/total-process memory는 관측하지 않았다.
- JS app chunk 약 6.24MB / gzip 649KB의 기존 크기 경고가 남는다. 예산을 올려 숨기지 않았다.

증거: browser-validation.json, checks.json, intent-review.json, final-action.jpg, final-return.jpg, biceps-context.jpg. 숫자 viewport 이름이 붙은 중간 캡처들도 실제 825px이므로 요청 크기의 근거가 아니다.

## 상태와 남은 작업

acceptanceScope: 현재 등록된 source 범위의 작용/주변 관찰을 구별하는 단일 장면 학습 UI 및 재생 흐름. 전체 T66 authoring 책임은 기존 계약으로 별도 유지.
contractRevision: app-completion-2026-10-01
productReadiness: partial_with_unresolved_motion_engineering
contentCompleteness: partial
knownContentGaps: 전신 근육 작용 연결/자산 제작, 뼈 독립 기능 대조, 신경의 추가 주행 근거 및 동적 pose/좌표 결속 등 기존 원장 유지. UI 목록의 현재 13개 동작을 전신 완료로 쓰지 않는다.
unresolvedProductBlockers: 기존 integration-final의 실제 제작/작용 검증 및 D/runner 계약 오류 보존. 변경 UI의 요청 크기 검증은 별도 remainingVerification에 둔다.

542/563/12, 근육429/447/232 source concepts/462 surfaces, HA130, 역사163(6/20/135/2), 원본/source-cache/OpenSim_Models/T13, 기존 WIP, source-only, public rights held, humanReview=not_performed를 보존했다. 새 GLB/HA binding/target extent 승인 0. 다음 task/agent/thread/push/배포를 시작하지 않았다.

다음 수동 재개는 이번 폴더의 NEXT-T66-ATLAS-ACTIONS.txt를 사용한다. 같은 T66이며 T85를 자동 시작하지 않는다.

## 소유 변경 보존

검증은 기존 WIP를 보존한 현재 working tree에서 수행했다. 선별 커밋은 이번 구현의 tracked diff 및 새 의도/공통 UI·회귀·근거만 포함한다. learnerMotionRuntime.generated.ts는 재생성 중 기존 raw/projection WIP까지 반영되어 이번 의도 필드만의 변경이 아니므로 전체 파일을 커밋에 넣지 않는다. 갱신 파일과 before/ 복구 사본은 로컬에 보존한다. 기존 미커밋 코드를 다른 소유 변경으로 묶어 커밋하거나 깨끗한 HEAD 단독 검증을 했다고 주장하지 않는다. sync_execution.py 및 --check는 통과했다.
