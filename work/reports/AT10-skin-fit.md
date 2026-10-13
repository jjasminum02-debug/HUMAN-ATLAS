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
