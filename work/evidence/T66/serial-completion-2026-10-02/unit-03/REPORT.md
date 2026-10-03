# T66 내부 unit 03 — 어깨띠·어깨·팔꿈치·전완·손목

- 담당: Luna Max · 실행: 2026-10-03
- 판정: **unit 범위 구현·검증 완료, content gap 2개**
- 부모 T66: `in_progress / partial`; `nextUnit=author-and-integrate-normal-motion-bone-and-nerve` 유지
- 다음 수동 입력: `work/plans/t66-serial-completion-2026-10-02/04-T66-hand-digits.txt` (시작하지 않음)

## 범위와 결과

어깨띠·어깨·팔꿈치·전완·손목의 source/action 책임 큐 66개를 전수 대조했다. 64개는 실제 same-scene 변형·선택 관계로 구현하고 자동/실제 화면 검증을 통과했다. 좌우 척측수근굴근 자갈래의 방향 2개는 열린 근거가 신체 기준의 측방향 표현을 제공하지만 radial/ulnar action으로 안전하게 정규화하지 못해 `processed_with_content_gaps`로 남겼다. Supinator 원문 내부의 방향 충돌은 방향 action으로 등록하지 않았다. 승모근은 전체군 action 범위만 유지하고 상·중·하부에 상속하지 않았다. 674개 비작용 문맥 행은 action 성공 수로 세지 않았다.

18개 family-side 패키지와 682개 selector 관계를 기존 scene/runtime에 등록했다. 이 가운데 이번 revision에서 새로 만든 표면 변형 GLB는 6개다: 전완 엎침 좌우, 어깨띠 올림 좌우, 어깨띠 앞쪽 이동 좌우. 각 패키지는 정확한 source side와 source key에 결속되고 9 authored poses 및 실제 GLB 보간 검사를 거쳤다. 전체 근육/그룹 범위 승인이나 근육 주작용·수축 시범을 의미하지 않는다.

## 변형과 표현 경계

R5 산출에서 변형 대상 source surface는 전완 패키지당 3개, 어깨띠 패키지당 10개다. sampled minimum area ratio는 0.19887 이상, face flip 0, 새 containment 0, contact failure 0이었다. GLB authored keys와 dense interpolation 검증 및 validator adapter 검증이 모두 통과했다. 검사한 결과는 해당 source 자세의 교육용 표면 관찰이며, 원본에 없는 조직을 만들거나 실제 부착점·정상축·정상 ROM을 추정하지 않았다.

관절 자세에 따른 수동 변형과 근육의 주작용 시범을 분리했다. Supinator의 원문 방향 충돌과 척측수근굴근 자갈래 2개는 구체적인 content gap이며, 미작성 exporter/mask/trajectory 문제가 자료 gap으로 분류된 것은 아니다. 사람 검토는 `not_performed`, 공개 재배포 권리는 `held`, source-only/local technical selection 상태는 유지했고 신규 HA canonical binding은 0개다.

## 실제 브라우저와 자동 검증

Chrome/Playwright로 로컬 앱을 열어 좌우 전거근 카드와 어깨띠 앞쪽 이동, 네모엎침근·노뼈 선택과 전완 엎침, 재생 후 rest 복귀, scrub/각도 유지, 숨김 상태의 재생 차단을 확인했다. 390×900, 1024×900, 1440×900 화면에서 canvas/플레이어 배치와 가로 overflow를 확인했고, 학생 화면에서 제작 내부 메타데이터가 나타나지 않았다. console/page error는 0건이었다. 최초 angle probe에서 오른쪽 knob가 잡히지 않은 결과는 합격에 포함하지 않았다. 수정된 별도 pointer probe에서 양쪽 knob를 실제 hit하고 autoplay 종료 후 각도 유지가 확인됐다.

- motion schema: 1,145 actions / 1,139 definitions / 1,139 assets, 통과
- source policy/hash: 통과, source bytes 변경 없음
- U03 coverage: 66개 중 64 implemented, 2 content gaps, 674 out-of-action-scope 유지
- runtime projection: 262 selectors / 1,145 actions / 1,138 playable source-bound candidates, 통과
- 관련 회귀: 38/38 통과; TypeScript typecheck 및 production build 통과
- build는 500 kB 초과 chunk 안내를 냈으나 실패하지 않았다. GLTF fixture accessor 경고는 테스트 픽스처 경고다.
- `sync_execution.py`와 `--check` 통과

세부 지표·응답/자산 해시·명령은 [`final-validation.json`](final-validation.json), 등록 증거는 [`registration.json`](registration.json), 브라우저 산출물은 [`browser/`](browser/) 아래에 있다. 캡처는 대표 동작과 화면 크기를 보여주며 18패키지 전수 시각 확인이나 전체 target/group extent 확인으로 확대하지 않는다.

## 보존과 커밋 경계

시작 HEAD는 `a71e3246fedd2bdd9c4b52a4ea6042649b7c39a4`, 시작 dirty path는 1,448개였다. 시작 입력 21개 중 18개 hash는 종료 시에도 같았다. 나머지 세 개(`work/EXECUTION.json`, `work/tasks/T66-APP-COMPLETION.md`, `work/reports/T66.md`)는 이번 U03 상태/보고 기록으로 의도적으로 갱신했다. 시작 dirty 목록의 1,448 regular files 중 1,445개 hash는 불변이다.

U03 통합으로 `atlas-data/motion/motion-asset-sources.json`, `atlas-data/motion/motion-scenes.json`, `atlas-data/schemas/validate_motion_learning.py`가 시작 hash에서 달라졌다. 이 파일은 선행 U01/U02 및 다른 T66 WIP와 섞인 공유 파일이므로 전체 파일을 U03 단독 소유로 커밋하지 않았다. 생산 runtime projection, R5 자산과 다른 기존 dirty/WIP도 이 checkout에 보존한다. `OpenSim_Models`는 clean이며 원본 source bytes와 이전 evidence는 덮어쓰지 않았다. 자세한 path/hash 비교는 [`preservation-final.json`](preservation-final.json)에 있다.

이번 unit의 pass는 T66 전체 pass가 아니다. 남은 family engineering과 T66 통합이 필요하다. 다음 파일은 사람이 별도로 실행할 U04 hand/digits 입력이다.

## 2026-10-03 continuation — U01 브라우저 보완과 U03 집계 교정

원래 U01 기록의 `blocked_by_environment`는 네 개 source/action 조합의 실제 UI 표본이 없다는 뜻이었다. 같은 checkout의 현재 앱을 기존 Chrome/Playwright 절차로 열어 양측 짧은갈래 위팔두갈래근의 어깨 앞쪽 굽힘·팔꿈치 굽힘 4개 조합을 보완 확인했다. 각 카드의 source/좌우와 선택 action, 중간 재생, canvas 변화, 재클릭 rest 복귀와 카드 유지가 일치했고 내부 ID/evidence 노출·console/page 오류는 없었다. 이 보완은 해당 4개 표면 조합의 UI 차단을 해소하며, 근육 전체/그룹 extent나 사람 해부학 승인을 뜻하지 않는다. 실제 페이지/장면 캡처와 SHA-256은 [`browser-u01`](continuation-2026-10-03/browser-u01/)에 있다.

U03의 최종 후보/등록 reconciliation은 revision별 실패 이력을 보존한 채 각 family-side의 최신 production 결과를 비교했다. 18개 최신 후보가 `candidate_pass`이고 18개가 실제 r4 등록 receipt에 있으며 각 GLB hash가 일치한다. 이 수치는 등록/후보 QC이지 18개 모두의 개별 UI 시각 합격은 아니다. 요청에 나온 `registration-r2.json`은 저장소에 없으며, 확인한 실제 최신 파일은 `registration.json`의 `t66-u03-registration-r4`다. revision별 rejection/error와 최신 family-side 대조는 [`candidate-registration-reconciliation.json`](continuation-2026-10-03/candidate-registration-reconciliation.json)에 기록했다.

등록된 U03 family는 source 자세 관찰과 수동 표면 변형 범위이며, U03에서 새 prime-mover/근육 활성 클립을 추가하지 않았다. 견갑골 위쪽돌림 R2는 위팔뼈와 먼쪽 팔의 움직임을 명시적으로 제외하므로 완전한 어깨위팔 리듬이 아니다. 현재 양측 손목 노쪽 편위 R3는 중간 R2의 4도 범위 대신 authored 7도 관찰을 복원했으며, 어느 쪽도 생리적 정상 ROM이 아니다. source 측/member 선택과 전체 target/group extent는 분리했다. 상세 입력 hash는 [`scope-interpretation.json`](continuation-2026-10-03/scope-interpretation.json)에 있다.

기존 U03 전 집계에서 129는 고유 근육 표면이 아니라 근육 action 행이었다. 고정 전 기준 81개 고유 근육 source surface / 129 action 행, 122개 고유 뼈 source instance / 327 bone-family 행, source-derived motion URI 15개를 U03 receipt의 144개 muscle·538개 bone selector 행과 대조했다. U03은 그중 baseline에 없던 26개 근육 source ID와 28개 뼈 source ID, 18개 source-derived URI를 추가했다. 현재 runtime 결과는 107개 고유 근육 source surface / 273 action 행, 150개 고유 뼈 source instance / 865 bone-family 행, 33개 source-derived motion URI 및 33개 고유 GLB SHA-256 hash다. T24의 비-ZA 자산까지 합한 전체 runtime은 URI 34개 / hash 34개다. 두 분모는 별도로 계산했고 이 snapshot에서는 1:1이다. 행 수와 물리 source identity 수를 분리한 재현 계산은 [`runtime-count-reconciliation.json`](continuation-2026-10-03/runtime-count-reconciliation.json)에 있다.

공통 runtime/exporter 및 scene 파일은 이 continuation에서 수정하지 않았다. 다음 writer가 그 시점의 파일을 정확히 고정하도록 현재 shared interface/hash checkpoint를 [`common-writer-checkpoint.json`](continuation-2026-10-03/common-writer-checkpoint.json)에 남겼다. T66은 계속 `in_progress / partial`, 부모 `nextUnit=author-and-integrate-normal-motion-bone-and-nerve`다. U03의 기존 두 FCU 방향 content rows, Supinator 원문 방향 충돌, 승모근 부분 범위 미확정은 그대로 남는다. 다음 수동 입력은 `work/plans/t66-parallel-completion-2026-10-03/01-writer-freeze-and-optimize.txt`이며 이번 continuation에서는 시작하지 않았다.
