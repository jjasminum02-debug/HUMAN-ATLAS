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
