# MV2 — 대퇴직근 좌우 무릎 돌출 수정

2026-10-12 / 담당 Sol High / 실행 묶음 `MV1-Q01-rectus-femoris-knee-contour`.

이번 Q01 묶음은 **engineering acceptance 통과**다. **MV2 전체는 partial**이며 4묶음·32개 observed_ambiguous 매핑이 남는다. MV1의 미관찰 수는 0이고, 그 34건을 사람 승인 대기나 미조사로 해석하지 않았다. 역사 MV1 판정과 220장/74조합/332 learner-flow 원장은 변경하지 않았다. 이번 결과는 생리적 자연 수축, 실제 부착 footprint 또는 정상 ROM 승인과 구분한다.

시작 HEAD는 `6651c2049e0bb2e1e5215723e166cf6d5fc5ee51`. [시작 상태·소유 경계](../evidence/MV2/2026-10-12-q01-r1/start.json)와 NUL 구분 원본 status를 보존했다. 지정 authoring·원본 GLB·geometry/QC 의존 입력 50개 hash가 등록값과 일치했다. 동결 MV1의 17 입력/73 GLB hash도 비교했고 이번에 소유한 learner resolver 한 파일을 제외하면 일치한다. 전수 조사를 재실행하지 않았다.

원인은 **부착 역할과 가중치 영역의 잘못된 배정**이다. 기존 입력은 움직이는 무릎뼈를 대퇴직근의 fixedBoneKeys에 포함했고, 이동 mask에 y=0.6486m 부근의 근복 정점까지 포함했다. 근복의 fractional rotation이 먼 무릎 pivot을 중심으로 회전하면서 양측 최대 82.868mm, 앞쪽 약 71.1mm의 돌출을 만들었다. 실제 emitted 결과가 최종 가중치 공식과 일치한다. 근위 고정 mask 오류나 frame 변환 중복이 이 돌출을 만든 것은 아니다. 대퇴직근에 vector contact corrective는 없고, contact pin/weight relaxation이 잘못 배정된 mask를 유지한 채 작동했다. LINEAR의 인접 one-hot morph 보간은 spline overshoot를 만들지 않았으며, clip 끝은 굽힌 준비 자세이고 역재생이 무릎 폄이라는 매핑도 맞았다. [수치 진단](../evidence/MV2/2026-10-12-q01-r1/diagnosis-numeric.json).

정성적인 기시/정지와 무릎 폄 관계는 [UAMS lower limb table](https://medicine.uams.edu/neuroscience/education/medical-school-courses/human-structure-module/anatomy-tables/muscle-tables/muscles-of-the-lower-limb/)의 rectus femoris/quadriceps 항목을 대조했다. 문헌 관계와 이 모델의 source-region annotation을 분리했다. 실제 좌우 원본 overview의 정점 521(무릎뼈 위쪽 sleeve 부근)과 275(원위 taper/근복 전환 부근), sourceKey·matrix·geometry hash를 기록했다. 이 두 지표와 경계는 AI가 작성한 교육용 모델 지표이며 측정된 부착 면이 아니다. 좌우의 실제 source 행렬·정점을 각각 읽었으며 mirror를 검증으로 대신하지 않았다.

고정 hip/femur 쪽과 이동 patella/tibia 쪽의 영역을 바로잡고, 원위 sleeve/taper에서만 무릎 회전 가중치를 전환했다. 첫 후보는 97시점 검사에서 20건의 면 방향 실패 표본이 나와 폐기했다. 최종 후보는 기존 authorer의 free-weight 국소 shape relaxation을 한 번 적용했다. 검증 임계값을 바꾸지 않았다. **각 GLB의 node 47 POSITION/NORMAL morph 12개만 교체**했고, 다른 70개 node·원본 POSITION/index·pivot·axis·19.5°·3초·LINEAR track·역재생은 유지했다. 대퇴직근 고관절 시범과 대흉근은 수정하지 않았다. 대흉근은 별도 shoulder/linear-blend 경로이며 이번 knee mask 원인을 공유한다는 근거가 없다. [비교 기록](../evidence/MV2/2026-10-12-q01-r1/pectoral-cause-comparison.json).

기존 registry와 사용자 WIP를 덮지 않도록 [source-pinned 교체 manifest](../../atlas-data/motion/source-motion-repairs-r1.json)를 기존 learner resolver/asset delivery에 연결했다. 두 실제 learner 참조만 바뀐다. 원본 hash와 전체 frame/pose/side/topology/camera/playback binding이 달라지면 교체 candidate는 null로 격리된다. 실제 GLB loader와 현재 장면의 원본 geometry/LOD/hash 검사는 그대로 수행된다. 데이터와 검증이 없는 이름 변경이나 fixture 승격은 없다.

| 관련 검사 | 결과 |
|---|---|
| 최종 양측 emitted 보간 | 각각 97시점, 뒤집힘 0, 새 hip/femur/patella/tibia contained vertex 0 |
| 면적·edge | 최소 source 면적비 약 0.622, 최대 edge 상대 변화 약 0.522; 기존 .1 기준 유지 |
| 실제 loader vs 독립 replay | 194시점 일치, 최대 약 1.14e-16m |
| 근위부/원위부 | 고정 오차 0; 이동 mask 보간 경로 오차 <1e-9m |
| 원상복귀 | 실제 loader/controller 원본 좌표 일치; learner 양측 종료 후 progress 0, motion=null, update 0 |
| 실제 화면 | 양측 준비·50%·최대·역재생·복귀와 측면 주변 구조, 동일 camera/target 전후 비교 |
| UI 캡처와 판독 구분 | 최종 cycle 42+43장 캡처; 대표 6장씩을 contact sheet로 직접 판독, 최대 전후·측면 별도 확인 |
| 테스트 / 빌드 | 관련 20 tests, package build 13 checks 통과; 기존 dist를 덮지 않은 격리 출력 |
| 기존 경혈 흐름 | 같은 root에서 motion 종료→LU9 태연 카드/점/경로/AT21 부분 색 면→OFF/닫기; console error/warn 0 |

[왼쪽 전후](../evidence/MV2/2026-10-12-q01-r1/comparison-left.png), [오른쪽 전후](../evidence/MV2/2026-10-12-q01-r1/comparison-right.png), [실제 learner/복귀](../evidence/MV2/2026-10-12-q01-r1/README.md), [실제 loader 검사](../evidence/MV2/2026-10-12-q01-r1/real-loader-validation.json), [보간 검증](../evidence/MV2/2026-10-12-q01-r1/emitted-validation.json).

왼쪽 GLB는 3,077,372→3,297,068 bytes, 오른쪽은 3,078,676→3,298,376 bytes다. 원본을 보존하며 새 morph stream을 추가한 source payload 증가이고, geometry/animation 배열 비용은 각각 2,711,754/28,808 bytes로 유지된다. 실제 loader의 보수적 active-memory 추정은 6,037,630/6,038,938 bytes다. 같은 71개 표면과 1,488-face 대퇴직근 topology를 사용하며, renderer geometry 배열도 기존과 같은 7,493,256 bytes를 관찰했다. driver VRAM 실측이라고 주장하지 않는다. 각 자산의 8MiB 제한과 기존 장면 예산을 올리지 않았다. 격리 빌드는 기존 원본과 새 두 자산을 함께 보존하므로 전체 배포 파일에는 새 두 GLB 비용이 추가되며, learner 재생은 선택한 새 자산만 지연 로드한다.

source local-use 결정은 상속하되 public redistribution=held, humanReview=not_performed를 유지한다. AI 작성 provenance는 위의 source-addressed annotation/repair 기록에 남는다. 생체역학 solver나 환자 진단·치료·침 시뮬레이션은 수행하지 않았다.

소유 변경은 두 새 GLB, source-pinned repair manifest, 공통 교체 resolver와 delivery 연결/관련 테스트, 이 report/versioned evidence, EXECUTION의 MV2 record다. 원본/OpenSim_Models/T13/AT7/AT21와 기존 사용자 WIP 45개 tracked 파일 및 소유 외 untracked 경로는 제외한다. 커밋 전 보존·소유 검사와 로컬 commit receipt는 이 evidence 디렉터리에 남기며, 실제 commit hash와 포함/제외·잔여 변경은 최종 응답에서도 보고한다. push/배포는 없다.

[최신 수정 큐](../evidence/MV2/2026-10-12-q01-r1/repair-queue.json)에서 Q01 두 건만 resolved_engineering이며 다른 상태는 그대로다. [잔여 unit](../evidence/MV2/2026-10-12-q01-r1/remaining-units.json): Q02 외복사근 1, Q03 위팔두갈래근 3, Q04 손 말단 26, Q05 깊은 몸통 2. 별도 MV2 재개 시 우선 Q02의 실제 layering 원인만 조사한다. 현재 입력이 없어서 막힌 것이 아니며 새 사용자 요청 없이 실행하지 않는다.

예정된 다음 앱 task는 **AT22**다. 최신 `featurePlans.acupoint-at-361.order/nextUnit` 및 AT21 완료와 대조했다. AT record/feature plan은 변경하지 않는다. 다음 프롬프트:

```text
HUMAN ATLAS에서 AT22만 수행해라. 최신 AGENTS.md, EXECUTION/NEXT, work/tasks/AT22.md와 30/31 설계, AT21 실제 mask/evidence 및 MV2 Q01 결과를 읽어라. 개발 review의 canonical-carrier triangle brush/지우기/undo·redo/동일 카메라 전후 비교와 revision 저장 한 경로만 구현·검증해라. point/route/carrier hash와 이번 motion repair 및 AT7 카메라를 보존해라. AT22 명세의 경계/인수 검사·versioned evidence·sync/check·소유 로컬 commit을 완료하되 다른 MV2 잔여 묶음/다음 task/push/배포를 자동 실행하지 마라.
```

별도 수정 재개 프롬프트:

```text
HUMAN ATLAS에서 MV2의 MV1-Q02-left-external-oblique-lateral-layering만 재개해라. 최신 MV2 repair-queue/remaining-units와 변경된 input hash를 읽고 기존 MV1 전수 조사를 반복하지 마라. 실제 learner·원본/authoring에서 이웃 mesh, source topology, 가중치, 접촉/보간을 분리해 원인을 진단하고 근거가 있는 최소 수정만 해라. 해결된 Q01 좌우 무릎 자산과 AT7/AT21·사용자 WIP를 보존하고 다른 묶음/AT22/push/배포를 자동 실행하지 마라.
```

구현·검증 로컬 commit: `3ee4587b12a7c8482d699f48fda71a0c430f0ae5` (361 files). 커밋 직후 기존 status 5,966건이 시작 원본과 byte 단위로 일치하고 index가 비어 있음을 확인했다. [로컬 영수증](../evidence/MV2/2026-10-12-q01-r1/local-commit-receipt.json)을 후속 문서 checkpoint로 함께 보존한다.
