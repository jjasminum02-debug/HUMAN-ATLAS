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


## 2026-10-12 재개 — q01-learning-quality

이번 unit은 **교육용 작용 표현 통과**다. 기존 Q01 돌출 수정의 engineering pass는 보존했다. 최신 후보라는 이유로 r8을 승인하지 않았으며, 실제 비교 후 **r9**를 양측 learner 교체 자산으로 채택했다. 전체 MV2는 **partial / acceptancePassed=false**다. Q02–Q05 4묶음·32매핑은 기존 observed_ambiguous 상태를 유지하며 이번에 조사하거나 승인하지 않았다. MV1 미관찰 0과 기존 220/74/332 검사는 재사용했다.

[최종 판정](../evidence/MV2/2026-10-12-q01-learning-quality-r1/validation-final-r1.json), [새 큐](../evidence/MV2/2026-10-12-q01-learning-quality-r1/repair-queue.json), [잔여 unit](../evidence/MV2/2026-10-12-q01-learning-quality-r1/remaining-units.json).

### 복원한 중단 지점과 소유 범위

시작/재개 HEAD는 AT22 완료 커밋 `b9b041fa579ac463fd6158e8a5d37b7d71cb9853`다. 재개 시 실제 manifest는 r5를 가리켰고, r8은 후보 폴더에만 있었다. 기존 45 WIP와 보호 입력 1,771개 hash가 시작 기록과 일치했다. 원본 Q01 교체본 `a82d6459…` / `2c09324f…`, original base `04b6461e…` / `5d8fb2a5…`도 보존했다. 기존 생성/검사를 반복하지 않고 남은 loader/앱 검사와 실제로 발견한 r8 접촉 잔여의 국소 보완만 이어갔다.

소유 구현은 새 GLB 2개와 `source-motion-repairs-r1.json`의 두 row URI/hash/bytes/revision뿐이다. original base URI/hash와 전체 binding signature는 불변이다. 원본에 직접 대응하는 교체이며 runtime patch chain이 없다. 새 renderer/rig/근육별 runtime 분기, 카메라 정책·거리·연출·UI·보기옵션 변경은 없다. 기존 resolver, actual loader/controller와 offline source reader/contact corrective를 재사용했다. 공통 authoring 및 viewer 파일의 기존 WIP는 수정하지 않았다.

### 관찰·작성·채택 근거

기존 수정본은 source 근복 영역을 고정하고 원위 전환 구간만 움직여, 주요 근복의 길이 변화를 보여주는 데 부족했다. 원본 upper 12 vertex의 실제 좌표와 centroid, distal sleeve vertex 521 및 taper 275를 양측 source matrix로 각각 읽었다. source origin→sleeve 축에 근거한 material coordinate와 9개 native section centroid를 작성했다. 이는 AI의 교육용 모형 지표다. 측정된 기시 footprint나 근섬유가 아니다. 잘못된 원래 hip-fixed 52개를 그대로 복사하지 않았고, 실제 근위 neck 61개를 고정했다.

r9는 source sleeve 이동의 **축 방향 성분**을 기존 distal weight와 부드러운 분포에 연결한다. patella의 횡방향 이동은 기존 원위 sleeve에 남기며, 근복 전체를 knee pivot으로 돌리지 않는다. distal 153개는 기존 통과본의 LINEAR 경로를 정확히 유지한다. 기존 접촉 보정은 표면 정합 도구로 사용했다. 통째 scale/rigid 이동, 임의 부풀림, 색 변화, 숨김, 각도 축소로 수축을 대신하지 않았다.

| 구분 | 왼쪽 | 오른쪽 |
|---|---:|---:|
| 근복 section-centroid 경로: 처음→준비 | 291.710→303.523mm | 291.709→303.523mm |
| 작용 구간 3→0초의 경로 단축 | 11.814mm | 11.814mm |
| 주요 근복 최대 이동 | 12.909mm | 12.909mm |
| 고정 근위부 오차 | 0 | 0 |
| 원위 기존 경로 오차 | <2nm | <2nm |
| 최소 면적 비 / 최대 edge 변화 | 0.578 /0.248 | 0.578 /0.248 |
| 면 뒤집힘 / 네 기준 뼈의 새 contained vertex | 0 /0 | 0 /0 |

3초 clip의 0→3은 무릎을 굽히는 준비, 3→0은 무릎 폄 작용이다. 경로는 준비 중 증가하고 작용 중 단조 감소한다. 이것은 약 4%의 **모형 경로 변화**이며 실제 fascicle 수축률·조직 물성·volume·정상 ROM 인증이 아니다. 기존 19.5° pivot/좌표계/pose/양측 topology와 다른 70 node의 모든 sampled pose는 그대로다.

이전 시도는 versioned evidence에 보존했다. r2/r6은 뒤집힘, r3/r7은 과도한 edge 변화로 제외했다. r4/r5의 전체 sleeve-vector 보정과 비교해 r9의 축 방향 변형은 면적/edge 품질이 낫다. r8은 새 광근 contained 표본 6/7/8, 새 표본의 nearest-depth 최대 2.664mm가 남았다. r9의 기존 wrap 적용 후 각각 **3/3/2**, 최대 **1.850mm**로 줄었다. r8 record에 r5의 wrap 설명이 남았던 오류는 원본을 덮지 않고 `r8-annotation-corrigendum.json`으로 정정했다.

**한계는 남는다.** 원래 source/accepted pose에도 광근 vertex overlap이 있으며, r9에도 위 추가 국소 겹침이 있다. 새 표본의 nearest-depth 측정은 기존 already-inside 깊이 증가나 모든 triangle 교차를 검증한 것이 아니다. 기존 네 뼈 접촉 기준은 유지하고 통과했지만, 모든 연부조직 충돌이 없는 정확한 생체 모형이라고 주장하지 않는다. 이 알려진 거친 표면 근사를 포함한 local teaching demo를 판정했고, 교수 검토/생체역학 인증/공개 재배포 승인과 분리했다.

### 실제 emitted 파일·앱 검증

- 좌우 각각 **193시점**을 actual `loadAnimationScene` / `AnimationPlaybackController` / Three `getVertexPosition`+matrixWorld로 읽었다. 독립 GLB replay와 최대 차이는 0 /1.15e-16m다. compaction 전후 71 node 재생 오차0, 원본 대비 다른70 node 변화0이다. 준비·역방향 작용·왕복 경계·빠른 재시작·0.7초 복귀 후 원상복귀를 확인했다.
- 실제 **1280×720** 앱에서 양측 0/50/100, 준비·작용·반복 1배속과 오른쪽 100→90%의 느린 보간, 측면의 무릎/근육/뼈 관계를 확인했다. 1배속 시리즈 **175장**을 기록했고, 대표16장을 모은 contact sheet와 별도 static/측면/부착 화면을 판독했다. 캡처 수를 전수 시각 승인 수로 세지 않았다. 왼쪽 근위부가 잘리던 초기 확대 증거를 보존하고 전체 부착 문맥 화면을 추가했다.
- 기존 통과본과 최종본의 실제 전후는 같은 viewport에서 수동 정합했다. target 오차0, camera 위치 잔차 **0.87mm**를 명시한다. bit-identical camera라고 주장하지 않는다. 각 learner session 내부의 root/renderer는 유지했으며, 의도적인 reload/DEV route의 다른 UUID를 합쳐 한 session으로 세지 않았다.
- 빠른 중단/재시작, 재생 중 다른 근육 선택, 원본 geometry/선택/레이어 복귀를 확인했다. 무관한 대흉근 100/50 및 종료를 비교했다. 해당 원본 URI/hash는 불변이며, Q01과 동일한 원인으로 판정하거나 대흉근 전체 자연스러움을 승인하지 않았다.
- 변형 자세에서 경혈 진입은 ‘정지 자세에서 다시 열어 주세요’로 차단되어 정지 좌표 overlay가 노출되지 않았다. 대퇴직근 종료→LU7 점/경로/AT21 부분 면→닫기 후 source motion=null, update0, camera owner=null, native 배열 **6,947,334 bytes**·선택·레이어·camera가 복원됐다. 대흉근 종료 후 같은 왕복도 확인했다.
- AT22의 DEV triangle fixture 882면을 열고 닫아 기존 root/camera/선택/레이어와 native 배열 복원을 확인했다. 편집하거나 새 revision을 저장하지 않았다. AT22의 원래 36검사/13단계/화면 evidence를 재사용하며 이를 새 ST 영역 검증으로 세지 않는다.

관련 자동 검사 **17/17**, typecheck를 포함한 isolated package build **13/13** 통과. 최종은 `related-tests-r9.log`, `build-final-r2.json`이다. 역사 전체 suite를 재실행하지 않았다. 기존 large-chunk warning과 예산 threshold는 유지했다. 실제 browser warn/error0이며 임시 viewport/tab을 정리했다.

![최종 왼쪽 준비·부착 문맥](../evidence/MV2/2026-10-12-q01-learning-quality-r1/final-left-complete-attachment100-r1.png)
![양측 실제 시리즈 대표 프레임](../evidence/MV2/2026-10-12-q01-learning-quality-r1/final-motion-contact-sheet-r1.png)

### 비용·권리·기록·정지

| actual loader 비용 | 기존 Q01 왼쪽/오른쪽 | 최종 왼쪽/오른쪽 |
|---|---:|---:|
| 파일 bytes | 3,297,068 /3,298,376 | **3,128,960 /3,130,044** |
| geometry 배열, morph 포함 | 2,711,754 | **2,925,450** |
| animation 배열 | 28,808 | **30,684** |
| source+geometry+animation 추정 | 6,037,630 /6,038,938 | **6,085,094 /6,086,178** |
| 파일 triangles /source node | 37,087 /71 | **37,087 /71** |

RF target12→24로 geometry 배열은 213,696 bytes 증가했지만 미사용 accessor49개 정리로 파일은 약168KB씩 감소했다. 총 loader 추정은 약47KB씩 증가한다. 같은 왼쪽 비교 구도의 render calls59/triangles34,099는 그대로다. DOM native/base-array 통계는 morph target을 포함하지 않으므로 전체 GPU 비용으로 대신 쓰지 않았다. 위 수치는 실제 배열 용량/호출 계수이며 driver VRAM 실측은 아니다. 20MiB overview /96MiB geometry /1M triangles /8MiB repair 예산은 올리지 않았다. 실제 lazy fetch/parse/attachment latency는 각 PNG의 JSON player profile에 남겼다. 종료 시 motion bytes0과 update0, native geometry 복원을 확인했다.

최종 왼쪽 SHA-256 `ab259d772f166d8417959680e5b7a1e1fd7de34e3320ee25169b7e22c318cde4`, 오른쪽 `60fa091ca479ba6d237cfe25a4e7b91776542793137e3b2bff1ddebb02cb8b53`. 두 파일은 `atlas-data/assets/motion/mv2-q01-learning-r1-{left,right}/motion.glb`이며 actual manifest/hash/binding을 대조했다. source-only/local-use 상속, AI 작성, humanReview=not_performed, publicRedistribution=held를 보존한다. 실패 후보/전체 authoring/evidence/private source를 learner bundle에 넣지 않는다.

최신 EXECUTION을 다시 읽고 **MV2 record와 motion-quality-review.lastDisposition만** 갱신했다. MV2 전체 acceptance=false, 이번 lastRun acceptance=true를 구분한다. AT/AC/T record와 acupoint plan은 불변이다. sync_execution.py는 Updated 0, --check는 Execution projections match; no writes로 통과했다. 원문 결과는 evidence에 남겼다. 커밋 포함은 위 두 GLB/repair manifest/이 보고서/versioned evidence/EXECUTION이다. 원본/OpenSim/T13/AT21/22/기존45 WIP 및 기존 미추적 파일은 제외한다. 실패 후보 GLB·uncompact·loader world dump·isolated build 출력은 versioned 위치에 보존하되 Git/learner bundle에서 제외한다.

다음 수리 큐는 **MV2 Q02**이며 [붙여 넣을 프롬프트](../evidence/MV2/2026-10-12-q01-learning-quality-r1/next-prompt-MV2-Q02.txt)를 남겼다. 경혈 계획의 현재 다음 ID는 **AT8**이다. 이번에는 q01-learning-quality만 수행했고 다음 묶음/AT8/위임/push/배포를 실행하지 않았다. 소유 커밋 hash와 최종 잔여 status는 완료 답변 및 해당 Git 기록에서 확인한다.
