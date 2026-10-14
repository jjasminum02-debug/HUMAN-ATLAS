# AT10 / skin-fit — 2026-10-13 r1, partial

**전신 입력과 실행 가능한 후보는 확보했지만 전신 정합 인수는 미달이다.** r9 emitted GLB는 실제 loader/Blender import와 독립 재생성을 통과한다. 고정 ZA와의 proper segment–triangle 교차가 남아 있는 피부 triangle은 **5,197 / 26,756**이다. 이것을 완성 피부·local learner eligible·정밀 혈위로 등록하지 않았다. 지금 재개할 단위는 **AT10/skin-fit**이며, 통과 후 예정 단위는 **AT10/skin-runtime**이다. 시간이나 사람 승인 대기로 종료 판정을 내리지 않았다.

## 기준선과 소유 범위

시작 HEAD `cdeda6018f40e1e32b8144e28a6c12ef4441b2bb`. [start.json](../evidence/AT10/2026-10-13-skin-fit-r1/start.json)과 `start-status.z`에 tracked WIP 45개의 파일 hash/상태를 기록했다. AGENTS, 최신 EXECUTION/AT10/r2 순서, REVIEW-AND-DESIGN/PROMPTS, AT3/4 carrier/geometry/access, AT5 compiler 및 현재 package를 재사용했다. Luna `738316ab5941ca1bb1a3148cba22bd0278f1dffb`의 portfolio-content, 기존 AT10 result/acceptance, AT30/31 planned, 기존 LU/LI/TE 및 HT/PC/SI/ST package 상태를 보존한다.

소유 변경은 offline 생성·검사 도구, candidate asset/mapping/landmark/recipe, 이번 versioned evidence/report, AT10의 `skinFit` record뿐이다. web runtime/renderer/camera/UI/보기옵션/홈/로딩은 변경하지 않았다. 원본 Startup.blend SHA `9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd`, pinned 피부 원본, native detail GLB, 기존 package hash와 45개 WIP hash를 다시 검사했다. OpenSim_Models/T13 drafts/역사 evidence는 변경하지 않았다.

## 소스와 재현 경로

MakeHuman core revision `a8bc2d54ff0ac92e78ff71431b1023eda42bf482`, base.obj SHA `8e761e6624b8f54536409135d1636da63b32486a90d4897f84e121d144f6fb4c`, target SHA `ed2e8c191cb6b87b4a2d97c80486acb2604fa549316c7aa2a738a5d5a14334dc`. 두 license 파일도 selection.json의 SHA와 일치한다. base/target assets CC0와 MakeHuman program AGPL을 분리했다. program/Blender는 web bundle에 넣지 않았다. native ZA/BP3D 권리와 정합 derivative 공개 판단은 별개다. 교수 검토 미수행은 이번 실패 원인이 아니다.

[공식 단위 설명](https://static.makehumancommunity.org/makehuman/docs/exports_and_file_formats.html)의 내부 dm을 `0.1`로 한 번만 m로 바꾼다. normalized preview mesh-0.json은 사용하지 않는다. 실제 joint-l/r 및 head/ground 그룹에서 +X left / +Y head / +Z anterior를 확인했다. 기존 native reader의 unit world matrix는 한 번만 적용한다. GLB world matrix는 identity다. Blender QA의 `[x,-z,y]`는 z-up 표시 변환이며 GLB y-up 변환과 구분한다.

body 13,380 source vertices / 13,378 quads를 사용하고 나머지 5,778 helper/joint vertices는 외피 export에서 제외한다. 원본 face/vertex/corner-UV ID와 emitted UV seam split 대응을 남겼다. source bone helper 99개와 관찰한 표면 extrema 5개를 native의 좌우 독립 cap/centre 주소에 대응시켰다. 이후 부위별 bone-local section cage, 손바닥 frame과 개별 손가락의 proper rotation/bind, 국소 craniofacial cage를 적용했다. 단일 macro target는 한 입력 성분이고 이 추가 정합 recipe 전체도 **생산 승인 전의 결정적 후보 recipe**다.

[manifest](../../atlas-data/anatomy/skin/at10-fit-r1/manifest-r9.json), [GLB](../../atlas-data/anatomy/skin/at10-fit-r1/skin-candidate-r9.glb), [source mapping](../../atlas-data/anatomy/skin/at10-fit-r1/source-to-derived-r9.json), [recipe](../../atlas-data/anatomy/skin/at10-fit-r1/recipe-r9.json), [landmark registry](../../atlas-data/anatomy/skin/at10-fit-r1/landmarks-r9.json)를 남겼다. 새 writable output directory에 `AT10_SKIN_EVIDENCE`와 `AT10_SKIN_ARTIFACTS`를 지정하고 `fit_at10_skin.py --revision r2 → profile_at10_skin.py → bind_at10_extremities.py → export_at10_skin.py` 순으로 재현한다. pinned 원본과 기존 native 캐시/AT8 원본 probe가 필요하다. 별도 `/private/tmp/at10-skin-fit-repro-r9`에서 emitted SHA가 **`1ff4f35229f1b598796f2fb55a9ee9d1813c9831c5a40624213e6ed54de659f7`**로 일치했다.

## 실제 수정과 실패를 구분

r1 skeletal cage는 전신 rest pose를 옮겼지만 몸통/머리 뒤와 팔다리 깊이가 부족했다. r2의 global radial contact는 다른 손가락/다리/몸통을 잡아 형태를 깨뜨려 폐기했다. native 좌측 winding 차이를 확인한 r3 nearest-normal 보정도 울퉁불퉁한 면과 접힘을 만들었다. 이를 생산 경로로 채택하지 않았다.

부위별 section cage와 손 분류를 수정했다. 단순 source XYZ 범위가 엄지·손끝을 아래팔/몸통에 잘못 포함하므로 실제 source wrist-to-MCP 기준면을 사용했다. 손바닥 전체 frame과 같은 손가락 안의 bind를 분리해 roll과 손가락 순서를 보존했다. r9를 현재 재개 기준 후보로 선택했다. r10의 unsmoothed 제약은 샅/상부 넙다리 접힘을 악화시켰다. r8/r11 enclosure 시도도 수렴/형태 기준을 만족한 최종본으로 간주하지 않는다.

검사 도구가 부위 분류를 다시 계산해 후보 metadata를 덮는 결함을 발견해 고쳤다. geometry는 불변으로 유지하고 r9-base의 원래 cohort를 복원했다. 검사 도구는 candidate에 쓰지 않는다. 영향을 받은 부위 통계/보정만 다시 검사했고 legacy-region 시도는 별도 보존했다. 전신 source 부재로 바꾸거나 기존 조사/다운로드를 다시 수행하지 않았다.

## 비용과 검증

| 항목 | 실제 emitted 결과 |
|---|---:|
| GLB | 626,572 bytes |
| logical / emitted vertices | 13,380 / 14,517 |
| triangles | 26,756 |
| decoded geometry buffers | 625,080 bytes |
| material / texture | 1 / 0 |
| degenerate triangle < 1e-12 m² | 0 |
| actual learner import / approved fitted skin | 0 / 0 |
| precise acupoint added / posture implementation | 0 / 0 |

기존 education-r1 83 chunks도 함께 계산했다: 813,096 bytes / 40,520 triangles / 813,096 geometry bytes. skin+그 carrier는 1,439,668 encoded bytes / 67,276 triangles / 1,438,176 geometry bytes다. 기존 overview 20,042,516에 둘을 모두 더하면 20MiB보다 **510,664 bytes 초과**한다. 기존 897,212 triangles와 합산하면 964,488, geometry 17,437,548과 합산하면 18,875,724 bytes다. 예산을 올리거나 주변 구조를 삭제하지 않았다. 다음 runtime에서는 old carrier와 skin의 실제 공존/전송 정책을 조정해야 한다. 여기의 buffer bytes는 정확한 저장량이고 실제 learner driver VRAM/FPS 측정으로 주장하지 않는다.

`validate_at10_skin_loader.mjs`가 실제 설치된 Three GLTFLoader로 GLB를 연다. `check_at10_skin.py`는 원본 hash, body/helper 분리, 원본 face/vertex/UV 대응, native side, proper rotation determinant, 독립 GLB 재현, 기존 package/WIP 보존과 **실패 gate 유지**를 검사했다. syntax/format checks는 pass이며 anatomy fit는 fail이다. runtime 코드 변경이 없어 web 전체 역사 suite/build는 반복하지 않았다.

검증된 `/Volumes/Blender/Blender.app/Contents/MacOS/Blender` 3.5에 `--background --factory-startup --disable-autoexec`를 사용했다. 최종 emitted r9 GLB를 다시 import해 21개 고유 시점의 피부/고정 native 중첩 42장으로 전신 정면·뒤·양측과 얼굴/귀·목/어깨/겨드랑·양측 팔꿈치/손목/손가락/손바닥·흉복부/배꼽·등/천골·샅·무릎·발등/발목·양측 발바닥/발가락을 검사했다. [전신 뒤 중첩](../evidence/AT10/2026-10-13-skin-fit-r1/screens/emitted-r9-whole-back-overlay.png)과 4개 review sheet는 통과만 추린 화면이 아니다. 붉은 native 관통과 손/샅 접합 형태 문제를 그대로 남겼다. 실제 learner 화면의 skin 검증은 0이며 이 Blender QA를 G1–G8 learner 합격으로 세지 않는다. 기존 AT7/21/22와 UI는 그대로 유지했다.

교차는 공통 nativeSurfaceIntersections의 양방향 segment–triangle 검사를 사용한다. [교차 통계](../evidence/AT10/2026-10-13-skin-fit-r1/candidates/fit-r9-intersections.json), [실제 source/native triangle 주소 표본](../evidence/AT10/2026-10-13-skin-fit-r1/candidates/fit-r9-remaining-probes.json), 부위별 unsigned 최단 표면 거리도 기록했다. unsigned 거리나 winding 부호를 피부 바깥 간격/정밀 혈위 승인으로 바꾸지 않았다. head 교차에는 eyelid/oral return 면도 포함하므로 모두 같은 외피 결함으로 일괄 판정하지 않는다. 동시에 원형 귀/두개 측면/후경부의 실제 중첩은 해결되지 않았다.

## 남은 unit과 다음 프롬프트

[remaining-units.json](../evidence/AT10/2026-10-13-skin-fit-r1/remaining-units.json)의 다섯 unit은 양측 손목/손 정합, 양측 발목/발 정합, 골반/샅/상부 넙다리 접합, 두개/귀/목과 내측 return 분류, 최종 지역 QA/landmark annotation이다. 필요한 입력은 기존 source body/native facet에 대한 **올바른 국소 표면 대응과 연속 cage/bind 규칙**이다. MakeHuman 파일 전체가 없거나 전신 입력을 다시 구해야 하는 문제가 아니다. 제안한 cap/section 규칙만으로 해당 부위를 충분히 정합하지 못했다.

navel/nipple/crease/nail의 정확한 source annotation과 derived 적합성은 아직 완료하지 않았다. 원본 관찰 형상과 AI가 만든 joint plane/cap correspondence를 구분했다. 구강은 기존 AT4의 tongue 138-triangle 부분과 access 계약에 연결할 준비만 남겼다. 실제 없는 gingiva/frenulum/sublingual mucosa를 외피로 대체하지 않았다.

[재개 프롬프트](../evidence/AT10/2026-10-13-skin-fit-r1/next-skin-fit-prompt.txt)는 같은 AT10/skin-fit의 구체적 재개다. 통과 후에만 [문서의 skin-runtime 프롬프트](../plans/acupoint-surface-posture-2026-10-13/PROMPTS-IN-ORDER.md)를 사용한다. skin-runtime, reconciliation, AT30/31, 361점 authoring, 취혈자세, push/배포는 실행하지 않았다.

로컬 commit에는 report/evidence와 offline tools/candidate/mapping/manifest 및 AT10 record만 포함한다. native-surfaces-r1.json(재구성 가능한 106MiB reference cache), 나머지 실패 후보/중간 render, 전체 source cache/private 교재, 기존 사용자 WIP는 stage하지 않는다. 실제 commit hash/포함·제외/잔여 변경은 같은 evidence의 commit-receipt.json 및 최종 응답에 기록한다.


## 2026-10-13 r2 — 실제 남은 국소 정합 재개, 인수 미달

시작 HEAD `0179ab8df828e90858ece4aa8fd64ab2d335cad2`. [r2 start](../evidence/AT10/2026-10-13-skin-fit-r2/start.json)의 45 tracked WIP/원본/native snapshot hash를 대조했다. 기존 r9 GLB `1ff4f35229f1b598796f2fb55a9ee9d1813c9831c5a40624213e6ed54de659f7`, MakeHuman pinned SHA/4 source files, 고정 native detail 입력/각 unit world matrix, Startup.blend와 기존 package가 모두 그대로다. Luna portfolio/source 확보/전신 변환은 재실행하지 않았다. 재개는 이미 생성한 r9의 source topology와 실제 native/probe를 사용했다.

**완성 피부가 아니다. 선택한 r22는 독립 국소 개선을 보존한 review checkpoint이며 acceptancePassed/geometryValidationPassed/learnerEligible는 모두 false다.** 실제 emitted native 교차는 **3,874 / 26,756 skin triangles**, non-adjacent 자기 교차는 **1,604쌍**이다. 동일 검사기로 원본 r9 emitted GLB를 영향 범위만 재대조한 값은 5,197개/1,358쌍이다. native 교차 감소를 승인으로 바꾸지 않았고 자기 교차 증가를 숨기지 않았다. 정합 승인 피부/learner import/경혈 추가/자세 구현은 전부 0이다.

### 구현과 원인

- 손목의 얇은 skeleton-cage handoff 대신 실제 source wrist/MCP와 양측 native cap 주소를 사용하는 연속 Gaussian 변형장을 작성했다. 손바닥의 proper frame 회전은 양측에서 determinant >0.999이다. source 관절 입력만으로 표면 정합이 끝났다고 하지 않는다. 손목·손바닥·엄지/fascia와 손가락은 여전히 관통한다.
- 발목/뒤꿈치/발등·발바닥/발가락의 독립 source helper와 실제 Calcaneus/native facet 주소로 cage와 표면 station 입력을 작성했다. 변형된 후보의 각도 대신 원본 dorsal/plantar 방향을 사용했다. native vertex만 단면으로 잘라 긴 fascia facet 사이를 놓치는 문제도 실제 triangle–section 교차로 고쳤다. 그러나 toe/ankle seam과 음수 ground clearance, 표면 대응 충돌이 남았다. r21 발 surface control residual 최대 11.55 mm와 실제 화면을 보존하고 실패한 발 후보는 r22에 적용하지 않았다. r22 발은 r9를 유지한다.
- source `abs(X)<45 mm`로 안쪽 넙다리를 몸통에 넣던 분류가 샅의 큰 틈을 만들었다. 실제 source femur axis/양측 native bone와 adductor/fascia facet에 연결해 안쪽 넙다리를 다시 정합했다. 샅 틈은 줄었지만 seam/후면 볼기·상부 넙다리 교차와 접힘은 남았다.
- outer scalp/neck에 실제 native facet 단면을 적용하고 pinna는 양측 original Helix/Lobule/Tragus source를 독립 사용했다. 두개/후경부 노출은 줄었으나 귀 rim/attachment가 미달이다. source inward-normal eyelid/oral return cohort는 원본 vertex/face 주소로 별도 기록했다. provisional cohort에 닿은 86 crossing triangle도 총수 3,874에서 제외하지 않는다. 이 분류는 임상적 mucosa 확인이 아니며, 기존 AT4의 tongue 부분과 실제 없는 gingiva/frenulum/sublingual 입력을 구분했다.

[attempt ledger](../evidence/AT10/2026-10-13-skin-fit-r2/attempt-ledger.json), source/native 표면 지표를 직접 작성한 [r21 correspondence](../evidence/AT10/2026-10-13-skin-fit-r2/surface-correspondence-r21.json), [588개 실제 미달 표본](../evidence/AT10/2026-10-13-skin-fit-r2/remaining-probes-r22.json)과 압축된 전체 crossing native-source/local-triangle 주소가 있다. nearest/raycast를 혈위 의미로 쓰지 않았다.

r12–15 normal/support contact push는 교차 일부를 줄였지만 65 mm 이상 변위와 접힘을 만들어 폐기했다. r20 unsmoothed envelope도 손/샅/발 seam을 악화시켰다. r21의 surface-extrema 대응은 thumb distortion/발 입력 충돌을 재현했다. 이를 상동 해부 지표나 최종본으로 승인하지 않았다. r22는 r19의 head/hip field와 r14의 continuous-hand field만 보존하고 원래 발을 유지한 구성이다. 새로운 번호라는 이유로 통과한 것이 아니다. 현재 실제 재현 결함은 **native 접촉 제약과 국소 bind의 접힘/자기 교차를 동시에 해결하지 못하는 것**이며, 전신 파일 부재나 교수 승인 대기가 아니다.

### 실제 자산과 검증

[manifest](../../atlas-data/anatomy/skin/at10-fit-r2/manifest-r22.json), [emitted GLB](../../atlas-data/anatomy/skin/at10-fit-r2/skin-candidate-r22.glb), [source mapping](../../atlas-data/anatomy/skin/at10-fit-r2/source-to-derived-r22.json), [recipe](../../atlas-data/anatomy/skin/at10-fit-r2/recipe-r22.json), [지표/return registry](../../atlas-data/anatomy/skin/at10-fit-r2/landmarks-r22.json). GLB SHA **`53b3a057ff9df98162cfa3deb47844103886d5ced28121b30a24534c41834b93`**.

body 13,380 logical vertices/13,378 original quads/26,756 triangles, 14,517 emitted UV seam vertices를 유지했다. helper 5,778 vertices는 원본에서 보존하고 export하지 않는다. original vertex/face ID, 모든 face-corner UV, source dm→m 0.1와 이미 적용한 native world frame이 불변이다. 추가 전신 scale/복제 인체/원본 변경은 없다. 새 recipe는 `author_at10_skin_patches.py → envelope_at10_skin_patches.py(r19) → compose_at10_skin_checkpoint.py(r22) → export_at10_skin.py(r22)`이며 별도 `/private/tmp/at10-local-fit-r2-reproduction`에서 GLB 전체 bytes가 일치했다.

- 같은 설치된 Three GLTFLoader parse와 Blender glTF import 통과. 후보가 learner eligible=false인 것과 실제 learner import 0을 검사했다.
- `check_at10_skin_local.py`는 pinned source/native/unit-matrix hash, 원본 source/face/UV 대응, 좌우/rotation, package와 WIP 45개 보존, 독립 재현, 검사기 read-only를 통과했다. `validatorReadOnlyPassed=true`; 검사기는 입력 후보를 수정하지 않는다.
- native 교차는 emitted float32 POSITION을 실제 mapping으로 읽은 뒤 BVH와 공통 양방향 segment–triangle 검사로 계산했다. 자기 교차는 source 인접 vertex를 공유하지 않는 삼각형 쌍을 따로 검사했다. unsigned 최단 거리/부위별 median/p95는 간격 진단이며 signed containment/정밀 취혈 승인이 아니다.
- 고정 native와 최종 GLB의 정면/후면/양측, 얼굴/양측 귀/후경부, 어깨/양측 팔꿈치/손목/손바닥·손가락, 몸통/천골/샅/무릎, 발목·발등/양측 발바닥·발가락 **23시점 × 피부/중첩 = 46장**을 실제 렌더하고 판독했다. [review 1](../evidence/AT10/2026-10-13-skin-fit-r2/screens/review-r22-1.jpg), [review 2](../evidence/AT10/2026-10-13-skin-fit-r2/screens/review-r22-2.jpg), [review 3](../evidence/AT10/2026-10-13-skin-fit-r2/screens/review-r22-3.jpg), [review 4](../evidence/AT10/2026-10-13-skin-fit-r2/screens/review-r22-4.jpg). 관통과 접힘을 그대로 남겼다. 이 offline 검증을 실제 learner G1–G8 합격으로 세지 않았다.

GLB **626,572 bytes**, decoded geometry **625,080 bytes**, **26,756 triangles**, material 1/texture 0, degenerate <1e-12 m² 0. 기존 carrier 포함한 합산 비용과 overview budget 초과 **510,664 bytes**는 r1과 동일하다. 예산은 올리지 않았고 주변 native 구조를 삭제하지 않았다. Blender/program은 web bundle에 넣지 않았으며 learner VRAM/FPS로 주장하지 않는다. runtime 코드가 변하지 않아 typecheck/build/역사 전수 suite를 반복하지 않고 관련 offline/loader/format 검사를 실행했다.

### 정확한 남은 작업과 경계

[remaining-units](../evidence/AT10/2026-10-13-skin-fit-r2/remaining-units.json)은 손목·손바닥·엄지 양측, 발목·발등·발바닥·MTP/toe 양측, pinna/neck/return, pelvis/perineal/thigh와 잔여 arm/trunk seam, 전신 최종 QA/landmark다. source/native 주소는 충분히 존재하지만 제안한 bind/표면 대응이 통과하지 못했다. 다음 정합은 상동 표면 쌍과 fold-aware 변형/양의 국소 Jacobian을 작성하고 native/self 교차를 함께 해결해야 한다. navel/nipple/crease/nail의 최종 교육 지표 판정도 아직 미완이다.

source CC0, native ZA/BP3D 권리/derivative 공개 보류, AI 작성 provenance, 교수 검토 미수행, 위치·geometry 승인 상태는 독립 유지했다. source/cached 자료가 없는 것으로 바꾸지 않았고 실제 없는 구강 점막을 외피로 옮기지 않았다. AT10 parent result/acceptance와 Luna portfolio, AT30/31 planned, 다른 AT/MV 기록, 원본/OpenSim_Models/T13 drafts/WIP/역사 evidence는 보존한다. 웹 camera/UI/보기옵션/홈/로딩/361점/자세는 변경하지 않았다.

실제 재개 단위는 계속 **AT10/skin-fit**이다. [구체적 다음 프롬프트](../evidence/AT10/2026-10-13-skin-fit-r2/next-skin-fit-prompt.txt)를 남겼다. 통과 후 계획만 AT10/skin-runtime이며 자동 실행하지 않는다. 로컬 commit은 offline 소유 도구·선택된 checkpoint/recipe/mapping·versioned evidence·보고서·AT10.skinFit만 포함하며 실패 중간 GLB/전체 native cache/private source/사용자 WIP는 제외한다. hash/실제 포함·제외/잔여 변경은 r2 commit receipt와 최종 응답에 기록한다.

## 2026-10-14 r3 — 국소 surface-pair/ARAP 시도 종료, 정합 미달

시작 HEAD는 `bb3840b4ed9d416c9c83064705190f735c5c8ddb`다. [start.json](../evidence/AT10/2026-10-13-skin-fit-r3/start.json)에 45개 tracked WIP hash와 소유 경계를 고정했다. 기존 r22 GLB hash 및 r2의 source/native/권리·독립 형식 재현 검사를 재사용했다. source 확보, Luna portfolio/package 조사, 전신 변환을 다시 수행하지 않았다. 10월 13일 시작한 r3 디렉터리에 10월 14일 종료 결과를 추가했으며 기존 r1/r2 evidence는 덮지 않았다.

**이번 시도에서도 완성 피부를 얻지 못했다. r23–r30은 모두 미채택이며 r22 review checkpoint를 그대로 유지한다.** r22의 native 교차 3,874개/자기 교차 1,604쌍과 geometry acceptance=false도 변하지 않는다. 최신 r30은 native 교차 **4,339개**, non-adjacent 자기 교차 **1,211쌍**으로 native 교차가 465개 증가했다. 자기 교차 감소를 전신 정합 통과로 바꾸지 않았다. approved fitted skin/실제 learner import/새 교육 지표 승인/경혈 추가/자세 구현은 모두 0이다.

### 실제 구현·실패 원인

[at10_skin_arap.py](../tools/at10_skin_arap.py)는 원본 source 관절·같은 손가락/마디 소유 구역과 native의 이름 있는 fascia/bone facet을 연결하는 국소 ring 제약을 작성한다. source 원래 vertex/OBJ face와 native source key/local triangle/world 좌표를 남겼다. 긴 fascia facet의 중심만 국소 범위에 있어 다른 구역을 잡는 문제는 실제 hit의 축/반경 검사로 제한했다. 동일 source vertex에 서로 다른 손가락 제약을 평균하지 않고 구체적인 digit 역할을 우선하며 충돌을 기록한다. source helper 관절은 원본에서 읽은 제작 지표이고, source radial/ulnar·tibial/fibular 방향과 ring 역할은 AI 작성 모형 지표다. 이를 관찰된 피부 주름이나 검증된 상동 취혈 지표로 주장하지 않는다.

양의 source edge weight를 쓰는 ARAP와 단계적 target, proper local rotation, 국소 line search를 구현했다. 손목은 실제 Radius/Ulna distal cap과 source 아래팔 관절/면을 사용하고, 발은 ankle–MTP frame 및 실제 Tibia/Fibula cap으로 종아리 연속 구역을 확장했다. 전신 scale/shrinkwrap/normal push로 결과를 감추지 않았다. 다만 **현재 source/native 표면 제약과 접합 경계 조건이 맞물려 수렴하지 않는 실제 결함**이 남았다. 원본 입력 부재나 교수 승인 대기가 아니다.

엄격한 one-ring determinant guard는 target residual 약 51–56mm에서 멈췄다. transported tangent/normal skin-prism guard는 더 움직이지만 양의 prism만으로 3차원 변형/전역 비관통이 증명되지 않는다. r28의 최종 회전 갱신 누락으로 남은 음수 prism은 r29에서 수정했다. r30은 prism 음수 0이지만 regularized one-ring 음수 진단은 손 양측 각각 109, 발 각각 68개이며 control residual은 손 최대 27.35mm/발 19.62mm다. 이를 양의 3D 국소 변형 합격으로 세지 않았다. 관통과 실제 손목/엄지·발 형태도 여전히 실패한다.

r27은 별도로 양측 original Helix/Lobule/Tragus와 source pinna에 6개씩 실제 주소 제약을 작성했다. control residual 0.081mm에도 귀 전체 rim/attachment가 native를 감싸지 못했다. 여섯 extrema 제안을 상동 지표로 자동 승인하지 않고 폐기했다. pelvis/thigh와 실제 Gluteus maximus facet 제약도 residual 최대 28.46mm 및 접합/접힘이 남아 적용하지 않았다. [attempt-ledger](../evidence/AT10/2026-10-13-skin-fit-r3/attempt-ledger.json)에 각 시도와 실제 판정을 구분했다. r30 초기 syntax 실패 로그도 보존하며 성공 실행은 `arap-r30-run2.log`다. 현재 도구는 최종 r30 알고리즘이고 과거 모든 중간 알고리즘의 재현을 주장하지 않는다.

### 실제 emitted 자산·화면·검사

**미채택 진단 자산** [manifest](../../atlas-data/anatomy/skin/at10-fit-r3/manifest-r30.json), [GLB](../../atlas-data/anatomy/skin/at10-fit-r3/skin-candidate-r30.glb), [mapping](../../atlas-data/anatomy/skin/at10-fit-r3/source-to-derived-r30.json), [recipe](../../atlas-data/anatomy/skin/at10-fit-r3/recipe-r30.json)를 남겼다. r30 GLB SHA는 `218b6bba246bc8f306e2d8d6fe50e6c4da9a58468fbc89a46e4e0733860db5af`다. learner package에는 등록하지 않았다. source CC0, target/native 권리와 공개 재배포 보류, AI 작성 provenance, 선택적 교수 검토 미수행, geometry 판정을 각각 유지한다.

- 같은 설치된 Three GLTFLoader와 Blender glTF import 통과. 실제 emitted POSITION과 original IDs, 모든 face-corner UV의 대응을 전수 확인했다. helper는 보존하되 GLB에 내보내지 않았다. dm→m와 native world matrix를 다시 적용하지 않았다.
- [scoped checks](../evidence/AT10/2026-10-13-skin-fit-r3/scoped-checks-r30.json)는 1,236개 source/native 실제 facet·좌우 주소, proper reference frame, 원본 topology/UV/ID/return cohort, 검사기 read-only, r22 불변, WIP 45개 보존을 통과했다. **검사 도구의 정상 수행과 geometry acceptance=false는 별개**다. r30 새 전체 생성의 독립 재현은 수행하지 않았고 이미 통과한 r22 형식 재현만 재사용했다.
- actual emitted float32 기반 공통 양방향 segment–triangle 검사와 자기 교차 쌍을 보존했다. shared validator의 유일한 변경은 full self-pair 주소를 기존 NPZ에 함께 저장하는 것이다. [remaining probes](../evidence/AT10/2026-10-13-skin-fit-r3/remaining-probes-r30.json)에는 source/native 실제 주소와 self-pair 표본, NPZ에는 전체 45,092 native crossing pair와 1,211 self pair가 있다. return cohort 관련 86개도 총수에서 빼지 않았다.
- 고정 native와 GLB의 정면/뒤/양측·머리/귀/목·어깨/팔꿈치·손목/손바닥/손가락·흉복부/천골/샅·무릎/발등/양측 발바닥·발가락을 23시점 × 피부/중첩 **46장**으로 렌더·판독했다. [sheet 1](../evidence/AT10/2026-10-13-skin-fit-r3/screens/review-r30-1.jpg), [sheet 2](../evidence/AT10/2026-10-13-skin-fit-r3/screens/review-r30-2.jpg), [sheet 3](../evidence/AT10/2026-10-13-skin-fit-r3/screens/review-r30-3.jpg), [sheet 4](../evidence/AT10/2026-10-13-skin-fit-r3/screens/review-r30-4.jpg)에 관통/접합 결함이 보인다. **실제 learner 화면 0, G1–G8 합격 아님**을 명시했다. 제품 camera/UI는 건드리지 않았다.

GLB **626,576 bytes**, logical/emitted vertices 13,380/14,517, triangles 26,756, decoded geometry 625,080 bytes, material 1/texture 0, degenerate 0이다. GLB metadata가 r22보다 4bytes 늘었고 geometry 비용은 같다. ymin −7.70mm로 ground clearance도 실패한다. 기존 carrier와 overview를 함께 더하면 encoded 21,482,188bytes/964,488triangles/decoded geometry 18,875,724bytes이며 기존 20MiB보다 **510,668bytes 초과**한다. 예산을 올리거나 native를 삭제하지 않았다. 실제 learner VRAM/FPS 측정으로 주장하지 않는다. 런타임 코드 변경이 없으므로 전체 web build/역사 suite를 반복하지 않고 관련 Python syntax·loader·source mapping·주소·read-only·WIP 검사를 수행했다.

### 종료 상태와 남은 unit

[remaining-units](../evidence/AT10/2026-10-13-skin-fit-r3/remaining-units.json)의 다섯 unit은 양측 손목/손바닥/엄지, 양측 발목/발바닥/발등/MTP/toe, 귀 attachment/목/return, 골반/샅/넙다리와 잔여 seam, 최종 전신/교육 지표 QA다. 필요한 것은 현재 모델에 존재하는 source/native **연속 표면 band와 공유 경계·접촉 조건의 올바른 대응**이다. 여섯 점 residual, 단면 extrema 또는 교차 수 감소만으로 해결됐다고 할 수 없다. 실제 없는 gingiva/frenulum/sublingual mucosa만 별도 미지원으로 유지한다.

EXECUTION은 기존 r22 candidate/count/format result를 보존하고 AT10.skinFit의 이번 미채택 시도·재개 evidence만 추가한다. AT10 parent result/acceptance와 Luna 산출물, AT30/31 planned, 다른 AT/MV/feature plan의 순서를 보존한다. 재개는 계속 **AT10/skin-fit**, [다음 정확한 프롬프트](../evidence/AT10/2026-10-13-skin-fit-r3/next-skin-fit-prompt.txt)에 남겼다. 통과 후 예정만 skin-runtime이며 실행하지 않았다.

소유 offline 도구/진단 r30 자산·versioned evidence/보고서/AT10.skinFit만 로컬 commit한다. 실패 중간 GLB/전체 native cache/source 원본/private 자료/45개 사용자 WIP/역사 evidence는 제외하며 그대로 남긴다. 실제 hash/포함·제외·잔여 변경은 종료 후 이 evidence의 `commit-receipt.json`과 최종 응답에 기록한다. 다음 task·위임·push·배포는 수행하지 않는다.

## 2026-10-14 r4 — 연속 surface field와 실제 대응 충돌 검사, 미달

시작 HEAD `c22da3a7776c26c4590c0f955ac49d8d87dffb25`. [start](../evidence/AT10/2026-10-14-skin-fit-r4/start.json)에 45개 tracked WIP hash와 소유 경계를 남겼다. r22의 실제 GLB SHA가 그대로임을 대조하고, 이미 끝난 source/권리/hash·독립 형식 재현을 재사용했다. source 확보/Luna portfolio/package/전신 제작 조사는 반복하지 않았다.

**이번에도 전신 정합은 해결하지 못했다. r31–35는 모두 미채택이고 r22 baseline(native 3,874개/self 1,604쌍, geometry=false)를 유지한다.** 최신 손·발 시도 r35는 native 교차 **4,775개**, non-adjacent self 교차 **1,063쌍**이다. 독립 귀·양측 골반 시도 r34는 **3,978개/1,130쌍**이다. 자기 교차 감소, 양의 국소 수치, 앞쪽 샅 모양 개선을 전체 피부 합격으로 바꾸지 않았다. approved fitted skin/새 교육 지표 승인/실제 learner import는 0이다.

### 이번 구현과 실제 판정

[at10_skin_surface_bands.py](../tools/at10_skin_surface_bands.py)는 원본 helper 관절/native joint 주소와 같은 source boundary vertex를 사용하는 **연속 3D cubic radial-basis field**를 작성한다. 원본 손가락·마디, 손바닥/아래팔과 발가락·heel/MTP/종아리 구역의 실제 source face/vertex, native source key/local triangle/world 좌표를 기록했다. 고정 native는 움직이지 않는다. shared seam을 맞춘 source field에서 등쪽/바닥쪽을 구분하는 표면 제약을 추가하고, 관절 중심과 경계를 보존하며 오차가 증가하는 이동을 막았다. native ray/nearest는 여기서도 정합 도구일 뿐 상동 지표/혈위 의미의 근거가 아니다. 모든 pair는 `placementVerified=false`다.

귀는 r27의 여섯 점만으로 끝내지 않고 source pinna face cohort와 actual Helix/Lobule/Tragus/Auricular-region facet을 사용했다. 골반은 좌우를 따로 움직이는 대신 하나의 양측 field와 공유 경계로 source pelvis/upper-leg/native 주소를 연결했다. [r34 numeric bands](../evidence/AT10/2026-10-14-skin-fit-r4/surface-bands-r34.json)와 [r35 numeric bands](../evidence/AT10/2026-10-14-skin-fit-r4/surface-bands-r35.json)에 **6,922개** 실제 surface-pair 제안이 있다. source helper는 관찰된 피부 주름이 아니며, AI가 작성한 source band/축/face-normal cohort와 원본 구조를 분리했다.

r31 관절·경계 field는 source 형태를 연속 이동했지만 native fascia를 감싸지 못했다. r32에서 r30의 표면 제안을 그대로 넣자 analytic Jacobian이 음수가 되어 export하지 않았다. r33은 표면 오차를 줄이면서 관절 중심을 움직이고 다른 target 오차를 키워 실제 화면에서 손·발 접합이 악화됐다. r35는 관절 중심 이동을 손 최대 2.25µm/발 3.75µm로 제한하고 source field를 보존했지만, 실제 palmar/dorsal wrist/thumb와 발등·발바닥·heel/MTP/toe 대응은 실패했다. r34도 앞쪽 groin native 교차 30→23과 self 감소가 있었으나 posterior gluteal/상부 넙다리/귀 lobule/rim 관통은 남았다. 어느 patch도 r22에 합치지 않았다. [attempt-ledger](../evidence/AT10/2026-10-14-skin-fit-r4/attempt-ledger.json)에 실제 결과와 초기 Blender 인자/BVH 인덱스 실패 로그를 보존했다.

### 단순 prism 수치와 구분한 3D 검사

[inspect_at10_skin_fields.py](../tools/inspect_at10_skin_fields.py)는 후보를 수정하지 않는다. 저장된 초기 field와 모든 보정 field를 다시 계산하여 actual candidate 위치와 비교하고, analytic 3D Jacobian을 central finite difference로 대조했다. vertex뿐 아니라 source face centroid와 source-axis 내부 표본까지 **16,882개 query**를 검사했다. 최대 위치 재생 오차 약 2.14e-12m, finite-difference Jacobian 오차 최대 3.89e-7이며 표본의 음수 Jacobian은 0이다. 이는 **유한 표본 검사**로 전역 injectivity/전체 피부 acceptance를 증명하지 않는다. 실제 emitted 교차/자기 교차가 별도 실패하는 것을 그대로 유지했다.

보다 구체적인 미달은 target band 제안에 있다. [r34 field inspection](../evidence/AT10/2026-10-14-skin-fit-r4/field-inspection-r34.json), [r35 field inspection](../evidence/AT10/2026-10-14-skin-fit-r4/field-inspection-r35.json)에 **source 면 방향 비교 경고 731개**와 **인접 target edge 도약 경고 271건**의 전체 source face/vertex ID, 실제 native facet 표본을 남겼다. 손 방향 경고 140/137·도약 76/76, 발 111/117·57/57, 귀 108/110·0/0, 양측 골반 8·5다. 도약은 같은 source edge 길이의 4배 초과이면서 20mm 초과인 incidence이며 중복 edge를 포함한다. 초기 proper field로 옮긴 면 법선과 target 면 법선의 방향 비교는 대응 충돌 **진단**이며 해부학적 불가능이나 잘못된 상동 관계의 수학적 증명은 아니다. 실제 피부 미달 판정은 교차와 화면에 근거한다. 진행 중 831개라고 알린 것은 합산 오류였으며 저장된 올바른 총수는 731개다.

따라서 이번 구현은 r30의 수치 양성만 반복하지 않고 실제 3D field와 source/native 대응 충돌을 검사했지만, **표면 band의 일관된 chart 소유·공유 경계와 contact를 동시에 해결하는 데 실패**했다. 같은 미검증 pair를 더 강하게 적용하거나 경고 pair를 제외해 통과시키지 않는다. 이것은 전신 파일/권리 입력 부재 또는 교수 승인 대기가 아니다.

### 자산·화면·관련 검사

미채택 [r35 manifest](../../atlas-data/anatomy/skin/at10-fit-r4/manifest-r35.json) / [GLB](../../atlas-data/anatomy/skin/at10-fit-r4/skin-candidate-r35.glb) / [mapping](../../atlas-data/anatomy/skin/at10-fit-r4/source-to-derived-r35.json) / [recipe](../../atlas-data/anatomy/skin/at10-fit-r4/recipe-r35.json)의 SHA는 **`f1ba78ba12973e4201c5ae87b21b869e55b9d12331ae83f5e8fe78e7d4444bf2`**다. 귀·골반 [r34 manifest](../../atlas-data/anatomy/skin/at10-fit-r4/manifest-r34.json)의 GLB SHA는 `7858687ed49d1134afcb2f5f6fb673a50b34d65fc9dc458b7c686a02859ac8e3`이다. 둘 다 learner 미등록/eligible=false, 정지 native pose이며 skin scan이 아니다. CC0 source asset/AGPL program 분리, native 권리/derivative 공개 보류, AI 작성 provenance와 선택적 교수 검토 상태를 보존했다.

- 같은 설치된 Three GLTFLoader와 Blender glTF import로 actual emitted 자산을 읽었다. [scoped-checks](../evidence/AT10/2026-10-14-skin-fit-r4/scoped-checks-r35.json)는 모든 face-corner UV/original IDs/source geometry/helper 분리, 6,922개 source/native facet/side 주소, helper controls, 검사기 read-only, r22/WIP 45개 불변을 검사한다. source dm→m/ZA world transform을 중복 적용하지 않았다.
- 공통 native/self validator를 재사용했다. [remaining probes](../evidence/AT10/2026-10-14-skin-fit-r4/remaining-probes-r35.json)와 두 NPZ에는 actual emitted source/native crossing 및 self-pair 전체 주소가 있다. 거리값은 간격 진단이며 nearest normal 부호를 containment 승인으로 세지 않는다. return cohort도 교차 총수에서 빼지 않았다.
- r35 final GLB의 정면/후면/좌우·머리/귀/목·어깨/양측 팔꿈치·손목/손바닥/손가락·흉복부/천골/샅/무릎·발등/발목/양측 발바닥/발가락 **23시점 × 피부/중첩 = 46장**을 실제 렌더하고 네 sheet 모두 판독했다. [sheet 1](../evidence/AT10/2026-10-14-skin-fit-r4/screens/review-r35-1.jpg), [sheet 2](../evidence/AT10/2026-10-14-skin-fit-r4/screens/review-r35-2.jpg), [sheet 3](../evidence/AT10/2026-10-14-skin-fit-r4/screens/review-r35-3.jpg), [sheet 4](../evidence/AT10/2026-10-14-skin-fit-r4/screens/review-r35-4.jpg). r34 귀·groin·perineum·sacrum 10장도 생성하고 다섯 overlay를 판독했다. **실제 learner skin import 0, G1–G8 합격 아님**이다. skin-runtime이나 camera/UI/보기옵션/홈/로딩은 구현하지 않았다.

각 GLB **626,572bytes**, logical/emitted vertices 13,380/14,517, source quads 13,378, triangles **26,756**, decoded geometry **625,080bytes**, material1/texture0, degenerate0다. r35 ymin +3.70mm로 ground-clearance 형식 검사는 통과하나 피부 geometry는 실패다. overview+기존 carrier+피부 한 개 비용은 기존과 같은 21,482,184 encoded bytes/964,488triangles/18,875,724 decoded geometry bytes이며 20MiB보다 **510,664bytes 초과**한다. 예산을 바꾸거나 native를 삭제하지 않았다. 실제 learner VRAM/FPS 측정으로 주장하지 않는다. 새 전체 생성의 독립 재현은 수행하지 않았고 field 수치 replay/미분 대조와 기존 r22 형식 재현 재사용을 분리했다. Python syntax/관련 loader/자동 검사만 수행하며 runtime 변경이 없어 전체 web build/역사 suite를 반복하지 않았다.

### 남은 입력과 종료 경계

[remaining-units](../evidence/AT10/2026-10-14-skin-fit-r4/remaining-units.json)는 손목·손바닥·엄지, 발 dorsal/plantar/heel/MTP/toe, 귀 attachment/목/return, 골반·샅·넙다리 seam, 최종 전신/교육 지표다. 다음에는 기록된 충돌 source face와 native triangle을 직접 대조해 **먼저 한 연속 band의 실제 대응·native/self 교차를 해결**해야 한다. source 축/ray/nearest만으로 상동 지표를 자동 승인하거나 미달 pair를 제외해 완료 수를 만들지 않는다. 구강은 기존 AT4 partial tongue와 실제 없는 gingiva/frenulum/sublingual 입력을 분리하며 외피로 옮기지 않았다.

최신 EXECUTION의 AT10.skinFit에만 이번 시도와 구체적 재개 evidence를 추가하고 기존 r3 시도/primary r22/parent result·acceptance/Luna 결과/AT30·31 planned/다른 task와 plan nextUnit=AT10을 보존한다. [다음 정확한 프롬프트](../evidence/AT10/2026-10-14-skin-fit-r4/next-skin-fit-prompt.txt)는 같은 skin-fit의 대응 충돌 unit이다. 전체 정합 통과 후 예정만 skin-runtime이며 자동 실행하지 않는다. 로컬 commit에는 소유 offline 도구와 r34/r35 진단 자산·versioned evidence/report/AT10.skinFit만 포함한다. 실패 중간 자산·전체 source/native cache·원본/OpenSim_Models/T13/private/45개 WIP와 역사 evidence는 제외·보존한다. commit hash와 실제 포함/제외/잔여 변경은 종료 receipt와 최종 응답에 기록한다. 위임/push/배포는 하지 않는다.

## 2026-10-14 r5 — 양손 접촉 정합 보존, 검사 누락·발가락 역할 수정, 전신은 미달

시작 HEAD `0e8c055191aa49980d31b4774e6469a61828b6ef`. [start](../evidence/AT10/2026-10-14-skin-fit-r5/start.json)에 소유 경계와 기존 tracked WIP 45개 hash를 남겼다. [종료 경로 검토](../plans/acupoint-surface-posture-2026-10-13/SKIN-FIT-CLOSEOUT-REVIEW-2026-10-14.md)를 구현에 적용했다. 고정 MakeHuman/ZA 입력과 완료한 source·권리·r22 형식 재현/Luna 결과는 재조사하지 않았다.

**전신 skin-fit은 이번에도 완료하지 못했다.** 다만 양손목–손바닥–엄지/손가락–아래팔의 **국소 native/self 관통 0**을 실제 emitted GLB로 처음 분리 보존했다. 이 결과는 손톱/피부 주름의 정밀 표현, 새 교육 지표 승인 또는 전신 완료가 아니다. skin-runtime/learner eligible로 승격하지 않았다.

| 자산/범위 | native와 교차한 skin triangle | non-adjacent self pair | 판정 |
|---|---:|---:|---|
| r22 역사 checkpoint, 기존 648표면 | 3,874 | 1,604 | 원본 상태/미달 유지 |
| r41 양손 접촉 수정, 같은 648표면 | 2,478 | 1,604 | 양손 국소 접촉만 성공 |
| r41, 누락 보완 834표면 | 2,773 | 1,604 | 전신 미달, 보존용 국소 checkpoint |
| r54 오른발 시도, 834표면 | 2,288 | 1,334 | 미채택 진단 후보 |
| r41 양손 구역 각각, 834표면 | **0 / 0** | **0 / 0** | 국소 접촉 성공만 독립 보존 |
| r54 오른발 구역, 834표면 | **410** | **0** | native/형태 미달 |

서로 다른 reference 범위의 총수를 직접 비교해 개선이나 완료를 주장하지 않는다. [summary](../evidence/AT10/2026-10-14-skin-fit-r5/summary.json), [attempt ledger](../evidence/AT10/2026-10-14-skin-fit-r5/attempt-ledger.json), [remaining units](../evidence/AT10/2026-10-14-skin-fit-r5/remaining-units.json)에 전체/국소/작성기 수치/독립 emitted 검사와 미완을 구분했다. primary r22의 geometry=false와 native3874/self1604를 덮지 않는다.

### 실제 수정과 확인한 원인

`fit_at10_skin_contact.py`는 기존 원본/공통 교차 검사와 r31의 numeric 초기 field를 재사용한다. native→주소가 있는 skin facet의 barycentric containment 제약, 세 방향 ray parity, 실제 native/self 교차를 포함한 line search를 넣었다. shared source boundary와 원본 rig helper/작성 모형 control을 구분한다. Gaussian field의 boundary-null 조건, shape/Laplacian 항과 sampled 3D Jacobian을 검사한다. 새 self 접촉은 단순 거부만 하지 않고 분리 부등식으로 같은 QP에 넣었다. 이후 다수 제약에서 잔여 위반을 남기던 고정 반복 active-set을 Hildreth 방식으로 고쳐 실제 위반량을 기록했다. nearest/ray는 정합·포함 도구이며 혈위 의미의 근거가 아니다.

오른손 r40과 왼손 r41은 각각 실제 right/left native cap/source helper 주소로 작성했다. mirror를 검증으로 쓰지 않았다. 각 1,787 source vertices의 국소 구역에 대해 독립 emitted native/self 교차가 0이며, shared boundary 위치는 그대로다. 별도 source 체적 grid 133개씩과 source vertices/face centroids의 field replay를 확인했다. 최소 sampled 3D Jacobian은 오른손 약0.0621/왼손0.0592, 체적 표본 최소는 약0.0845다. 위치 replay 최대오차 약2.12e-10m, finite-difference 미분 대조 최대 약2.57e-7이다. 이것은 유한 표본 검사이며 전역 injectivity 증명이 아니다. 실제 외피 교차와 화면이 별도 기준이다.

**검사 대상 누락도 발견해 고쳤다.** 과거 도구가 영문 이름에 `muscle/bone/...`이 있는지로 native를 골라, 기본 표시 ZA 근육149/뼈37개를 놓쳤다. 같은 AC1 hash-checked detail GLB/world reader로 그 186개만 보충했다. 기존 648표면은 수정하지 않았고, 기본 표시 ZA bone/muscle **672개 전부 + 상속된 accessory**를 포함한 **834표면/2,729,450 native triangles**로 양손을 다시 검사해 0/0을 확인했다. 다른 hidden accessory 전체를 조사했다고 주장하지 않는다. [inventory](../evidence/AT10/2026-10-14-skin-fit-r5/native-inventory-completion-r1.json)에 누락 원인·실제 source key/hash/side/frame/world bounds가 있다. 원본 재다운로드나 전체 소스 수집을 반복하지 않았다.

**발의 실제 source/native 역할 오류를 수정했다.** 원본 OBJ에 엄지발가락 helper는3개, 둘째–다섯째는4개가 있는데 과거 recipe가 모두3개만 읽었다. 뒤 네 발가락의 DIP 쪽 handle을 native distal bone 끝에 연결하고 네 번째 TIP를 누락했다. `prepare_at10_foot_chain.py`는 실제 원본19개 toe helper와 양측 독립 native bone cap 주소를 읽는 경로를 만들었다. 이번 실행은 right만 검증·시도했으며 left는 자동 승인/실행하지 않았다. MTP/PIP/DIP/끝과 native joint-gap 추정/뼈 끝을 구분하고 source rig handle을 임상적 관절 지표로 부르지 않는다.

source 포함 검사에서 오른 엄지 TIP/둘째 TIP 원본 helper가 피부 밖 각각 약1.093/0.941mm에 있는 것도 확인했다. 이 원본을 수정하지 않고, 실제 source triangle/face/original vertex ID와 안쪽 방향이 기록된 별도 **내부 모형 control**을 작성했다. native 뼈/원본 helper/AI 모형 control을 분리한 r52 recipe는 format·역할 검사 대상이지 위치 승인 자료가 아니다. 실제 static 피부 정합에서는 native bone을 항상 고정하고 model handle만 최대5mm의 bounded-soft 조건으로 조정해 보았다. r54의 독립 replay상 최대 handle 이동은 약0.200mm다.

이 수정만으로 발이 완성되지는 않았다. r54 오른발은 실제 emitted 교차410개가 남았고, 그 중 **bone:기본표시18개 / accessory:기본OFF406개**가 있다(집합14개 중복). first/fifth metatarsal, proximal phalanx와 Crural fascia/발가락 extensor tendon 주소를 [분류](../evidence/AT10/2026-10-14-skin-fit-r5/right-foot-remaining-role-classification-r54.json)에 남겼다. accessory를 제외해 pass하지 않았고 숨김/투명화/전체 scale/각도 축소/원본 변경으로 해결하지 않았다. 발끝이 각지고 접힌 형태도 실제 화면에서 미달이다.

연속 surface-pair를 만들기 위해 source/native 인접 digit chart curve를 추적해 original edge/triangle/weights로 draft를 만들었다. 네 번째 helper를 포함한 뒤 graph는 모두 연결됐지만, 실제 화면에서 일부가 진짜 web valley 대신 distal toe side를 따랐다. `foot-webs-r1~r3`/`foot-surface-guides-r1`은 **미검증 draft로 유지하고 fitting/landmark에 적용하지 않았다.** 단순 bounds/nearest/bisector가 의미 있는 혈위·모형 지표라는 주장을 하지 않는다. r39 국소 분할도 교차를 해결하지 못해 원본 canonical topology로 채택하지 않았다.

머리는 원본 core의 self0과 young-preview 전체 적용 소스의 head self30을 실제 source geometry로 구분했다. 성인 core 기반 머리/목 recipe와 rig handle 역할·collar domain을 고친 r48은 해당 구역 self를 없앴지만 native 교차가 늘었다. r49는 작성기 국소 native1156개가 남고 positive-Jacobian guard에 걸렸다. **r46~49는 모두 미채택**이다. 이 새 시도를 전신 source 부재, 교수 승인 대기 또는 귀 전체 성공으로 바꾸지 않는다.

### 보존 자산과 실제 검증

보존용 [r41 manifest](../../atlas-data/anatomy/skin/at10-fit-r5/manifest-r41.json) / [GLB](../../atlas-data/anatomy/skin/at10-fit-r5/skin-candidate-r41.glb) / [mapping](../../atlas-data/anatomy/skin/at10-fit-r5/source-to-derived-r41.json) / [frozen recipe](../../atlas-data/anatomy/skin/at10-fit-r5/recipe-r41.json)의 GLB SHA는 **`52b23499e52d1b3b0d64448ebe5d1973508e24b419bf1c1e068ad10b00a54e4d`**다. 오른손 독립 r40 SHA는 `1e9e2f4ea22d1ce0ff964d1657c53c7dbb4455ff6612f8f1b4f7e436873c9205`다. [양손 보존 record](../evidence/AT10/2026-10-14-skin-fit-r5/preserved-units-r41-full-native-r1.json)는 후속 실패와 독립이다.

r41은 `/private/tmp/at10-contact-r5-replay-01`에서 원본 대응 numeric 초기 field와 저장된 increment만으로 다시 생성했다. 최종 target 좌표를 읽지 않았고 GLB **전체 bytes/hash가 일치**했다. 이것은 frozen numeric recipe의 독립 재현이며 optimizer 전체 재실행이라고 부르지 않는다. [재현](../evidence/AT10/2026-10-14-skin-fit-r5/reproduction-r41.json), [scoped checks](../evidence/AT10/2026-10-14-skin-fit-r5/scoped-checks-r41-r54.json)에 근거가 있다.

마지막 미채택 발 [r54 manifest](../../atlas-data/anatomy/skin/at10-fit-r5/manifest-r54.json) / [GLB](../../atlas-data/anatomy/skin/at10-fit-r5/skin-candidate-r54.glb)의 SHA는 **`60a92ef8ceeb5e42a174be822fe28b12e9e926280f1b337f8b777aa7116d1861`**이다. 독립 field replay는 vertices1249/face centroids2474/체적 grid497개에서 양의 sampled Jacobian과 미분 대조를 통과했지만 native/형태가 실패했다. 수치 양성을 geometry 합격으로 바꾸지 않았다. 양손과 나머지 source unit 밖 위치는 r41과 byte-exact하게 보존됐다.

- 실제 설치된 Three GLTFLoader와 Blender glTF importer로 emitted 자산을 읽었다. identity node/world transform, metres/static pose, 원본 IDs와 모든 face-corner UV/13,380 logical vertices/13,378 quads/26,756 triangles, helper5,778개 원본 보존/미export, source hashes를 검사했다.
- 독립 BVH/공통 양방향 segment–triangle 검사는 **actual float32 GLB POSITION**을 읽는다. checker는 candidate를 수정하지 않았다. source/native 전체 주소는 `fit-r41-full-native-r1-contact-addresses.npz`, `fit-r54-full-native-r1-contact-addresses.npz`와 respective remaining-probes에 있다.
- r41 actual GLB를 834 고정 native 위에서 정면/뒤/양측과 요구 근접부 **23시점×skin/overlay=46장** 렌더하고 [sheet1](../evidence/AT10/2026-10-14-skin-fit-r5/screens/review-r41-full-native-r1-1.jpg), [sheet2](../evidence/AT10/2026-10-14-skin-fit-r5/screens/review-r41-full-native-r1-2.jpg), [sheet3](../evidence/AT10/2026-10-14-skin-fit-r5/screens/review-r41-full-native-r1-3.jpg), [sheet4](../evidence/AT10/2026-10-14-skin-fit-r5/screens/review-r41-full-native-r1-4.jpg)를 판독했다. 양손/아래팔 추가 근접과 r54 actual 발등/발바닥, source/native guide 화면도 확인했다. 거리 진단은 unsigned nearest 검사이며 피부 두께나 취혈 정밀도의 승인이 아니다.
- **실제 learner import0, learner G1–G8 합격 아님**이다. offline 검사를 learner 검사로 대신하지 않았다. 현재 요청은 버튼 전 skin-fit이므로 제품 scene/camera/UI/보기옵션/홈/로딩/점 접촉/361점/취혈자세를 구현하지 않았다. application renderer를 추가하지 않았다.
- Python 관련 syntax15개, source/native cap 주소 재구성·좌우·read-only·45개 WIP 보존·실제 loader·재현 검사를 통과했다. runtime 코드 변경이 없어 web build/역사 전체 suite를 반복하지 않았다.

한 GLB는 **626,572bytes / 26,756triangles / decoded geometry625,080bytes**, material1/texture0/degenerate0이다. 기존 overview+교육용 carrier+피부 동시 합계는21,482,184bytes/964,488triangles/18,875,724 decoded bytes로 기존20MiB보다 **510,664bytes 초과**한다. 예산은 올리지 않았고 native/주변 구조를 삭제하지 않았다. 실제 driver VRAM/FPS/상주 합격은 주장하지 않는다. [비용](../evidence/AT10/2026-10-14-skin-fit-r5/cost-with-carriers-r41-r54.json)에 기록했다. 생성기/Blender는 web bundle에 넣지 않았다.

### 정확한 미완과 재개

필수 전신 정합/자연스러운 세부 형태/교육 지표는 아직 미달이다. 남은 것은 오른발의 실제 MTP/발등/발바닥/toe-pad/web source↔native band와 18개 bone 교차 및 406개 accessory 접촉의 개별 해결, 실제 left chain/표면 검증, 외피/귀/목/return, 겨드랑·몸통/팔, 골반·샅/넙다리 seam과 최종 전신/landmark QA다. 이미 있는 입력을 더 강하게 nearest/push하거나 미확정 지표의 이름만 바꾸는 것으로 닫을 수 없었다. 이것은 자료 전체의 부재나 사람 승인 대기가 아니라 **남아 있는 실제 대응·변형·형태 구현 결함**이다.

원본/UV/helpers/IDs/native/OpenSim_Models/T13 drafts/역사 evidence와 기존 WIP45개를 보존했다. MakeHuman asset CC0/program AGPL, native 권리/public held, AI 작성, 선택적 human review와 기술/위치 승인은 분리했다. 새 학습 지표/정밀 혈위/learner eligible는0이다. 성공한 두 손 contact를 다음 실패로 덮지 않는다.

최신 EXECUTION은 AT10.skinFit의 이번 부분 결과/보존 구역/정확한 재개만 병합한다. parent result·acceptance/Luna/AT30·31 planned/다른 task와 plan nextUnit=AT10을 보존한다. [다음 프롬프트](../evidence/AT10/2026-10-14-skin-fit-r5/next-skin-fit-prompt.txt)는 계속 **AT10/skin-fit**이다. 전신이 실제 통과한 뒤 예정만 skin-runtime이며 자동 실행하지 않는다. 시간 경과를 합격/종료 조건으로 쓰지 않았다. 소유 도구·선택 자산과 versioned evidence/report/해당 EXECUTION hunk만 로컬 commit하며 raw native supplement/source cache/실패 중간 자산·사용자 WIP는 제외·보존한다. 실제 commit hash/포함·제외·잔여 변경은 종료 receipt와 최종 응답에 남긴다. 위임/push/배포는 하지 않았다.
