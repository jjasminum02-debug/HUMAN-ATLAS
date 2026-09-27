# T43 전신 자료 확보 가능성 조사

- 조사일: 2026-09-27
- 상태: metadata 조사 완료, 권위 분모·지역 scene·human review는 미완
- 범위: source/asset metadata; no bulk download, canonical catalog generation, scene implementation, claim authoring, or motion clip creation.

## 요약

- 제품 기본 메뉴: 12개, 하위 메뉴 추가: 0.
- 기존 T15g 분모 상태 유지: 85 partial unique IDs (48 individual, 16 groups, 21 parts), whole-body individual denominator `null`, `denominatorFrozen=false`.
- 현 제품 데이터는 종아리만 partial static scene 2개와 근육 membership 6개. 뼈 membership은 0이며 9개 우측 뼈는 장면 컨텍스트/선택 binding이다.
- 20 source OBJ/2 derived GLB는 종아리 subset. 이번 조사에서 다운로드한 자산은 없다.
- 부위 분류상 11개는 `additional_build_needed`, 종아리는 `static_only`; 전체 동작 clip은 0.

## 12개 부위 취득 표

| 부위 | T15g source candidate IDs¹ | 기존 제품 scene / 근육 membership | 취득 상태 | 주요 geometry / rig 경로 |
|---|---:|---|---|---|
| 머리 (`head`) | 22 | 없음 / 0 | additional_build_needed | Oculomotor Model: 3 DOF, 6 muscles, CC BY 4.0; covers eye movement only, not full head/face/jaw |
| 목 (`neck`) | 0 | 없음 / 0 | additional_build_needed | OpenSim 2.4 Human Neck Model page: 19 individual muscles; flexion, extension, axial rotation and lateral bending; model download link listed, not fetched; license not resolved in this documentation page |
| 등 (`back`) | 9 | 없음 / 0 | additional_build_needed | Thoracolumbar spine and rib cage: T1-L5/rib cage and adjacent modeled segments; 93 DOF / 552 muscle-tendon actuators; MIT, July 2017; model files not fetched |
| 어깨·어깨뼈 (`shoulder-scapular`) | 10 | 없음 / 0 | additional_build_needed | Upper Extremity Dynamic Model: right upper extremity, 50th-percentile male, shoulder/arm movement, MIT, July 2014; model file/geometry/coordinate mapping not verified |
| 가슴우리 (`thorax`) | 7 | 없음 / 0 | additional_build_needed | Thoracolumbar spine and rib cage model: ribs and articulated T1-L5; MIT, July 2017; documented model files include example motion but no respiratory-action clip was inspected |
| 배·허리 (`abdomen-lumbar`) | 2 | 없음 / 0 | additional_build_needed | Thoracolumbar spine/rib cage model (MIT, July 2017); separate Lumbar Spine Model lists 3 DOF/238 muscle fascicles but documentation warns it lacks inertial body properties and is inappropriate for dynamics; CC BY 3.0 as listed |
| 골반·샅 (`pelvis-perineum`) | 0 | 없음 / 0 | additional_build_needed | No perineal/pelvic-floor muscle-actuated model located in the opened OpenSim model matrix; Thoracolumbar model includes pelvis context but that is not perineum coverage |
| 볼기·깊은엉덩이 (`gluteal-hip`) | 10 | 없음 / 0 | additional_build_needed | OpenSim Custom Hip Model (based on Gait2392; CC BY 3.0 as listed); Full Body Running Model has lower-body muscles but torque-actuated arms; downloads not inspected |
| 넙다리 (`thigh`) | 0 | 없음 / 0 | additional_build_needed | gait2392_simbody: bilateral lower limbs + lumped torso, 23 DOF/92 muscle-tendon actuators, CC BY 3.0 as listed; model files not freshly acquired |
| 종아리 (`leg`) | 6 current leg IDs; lower-ext 4 groups + 2 parts held | HA-SCENE-LEG-RIGHT-PILOT-T12B, HA-SCENE-LEG-RIGHT-BONES-T13 / 6 | static_only | gait2392/gait2354 and leg6dof9musc models are bilateral or unilateral lower-limb simulation candidates; specific included rights/contents/licenses vary by model as listed; no T43 motion package imported |
| 발 (`foot`) | 3 | 없음 / 0 | additional_build_needed | lower-limb OpenSim candidates contain a foot segment, but the opened model matrix did not provide a complete intrinsic-foot muscle/clip package; local mesh pilot includes only right-foot bone context, no foot membership rows |
| 팔·손 (`upper-limb`) | 10 | 없음 / 0 | additional_build_needed | Arm26: right upper extremity, 2 DOF/6 muscles, CC BY 3.0 as listed; Upper Extremity Dynamic Model: right shoulder/arm, MIT; Kinematic Arm with Articulated Hand: 20 hand DOF, no muscles and license listed as None. These are distinct models; no one is a full bilateral viewer rig. |

¹ `source candidate IDs`는 T15g partial crosswalk를 product category route로 검토하기 위한 후보 수다. 승인된 membership 수가 아니다. Lower-extremity source region은 thigh/leg/foot으로 자동 복제하지 않았다. 각 부위별 근육·뼈 candidate와 BodyParts3D line locator, T04 crosswalk rows는 JSON에 보존했다.

## 부위별 gaps와 다음 행동

### 1. 머리 (`head`)
- T15g source region: `head, face, mastication, eye, tongue`; current partial rows: 22; candidate stable IDs: 22.
- BodyParts3D muscle candidates: FMA46751 BP4926 muscle of face, FMA49033 BP4927 extra-ocular muscle; locator `isa_parts_list_e.txt L1764-L1774; head bone candidate FMA52748 BP8107 mandible at L2055; right/left maxilla L2068-L2069`.
- Bone candidates: FMA52748 BP8107 mandible, FMA53649 BP8309 right maxilla, FMA53650 BP9046 left maxilla; locator `isa_parts_list_e.txt L2055-L2069`.
- OpenSim candidate: Oculomotor Model: 3 DOF, 6 muscles, CC BY 4.0; covers eye movement only, not full head/face/jaw.
- Shared movement group candidate: ocular rotations / saccade-fixation candidate; no head/face product clip. No production clip validated.
- Gap/next: BodyParts3D index lookup for literal “masseter” and “temporalis” returned no match (L0, no matching text); this is a bounded index-search gap, not proof of model absence.
- Gap/next: T15g head pool merges source head/face/mastication/eye/tongue only as routing candidates.

### 2. 목 (`neck`)
- T15g source region: `neck`; current partial rows: 0; candidate stable IDs: 0.
- BodyParts3D muscle candidates: FMA13385 BP4879 scalenus anterior, FMA13386 BP4877 scalenus medius, FMA13407 BP4908 sternocleidomastoid; locator `isa_parts_list_e.txt L431-L439 and L453-L455`.
- Bone candidates: FMA9915 BP7846 cervical vertebra, FMA12519 BP8831 atlas, FMA12520 BP8459 axis; locator `isa_parts_list_e.txt L320-L321 and L365-L372`.
- OpenSim candidate: OpenSim 2.4 Human Neck Model page: 19 individual muscles; flexion, extension, axial rotation and lateral bending; model download link listed, not fetched; license not resolved in this documentation page.
- Shared movement group candidate: cervical flexion-extension / axial rotation / lateral bending candidate. No production clip validated.
- Gap/next: No neck source rows in the current T15g crosswalk; official index entries do not create project canonical IDs or memberships.

### 3. 등 (`back`)
- T15g source region: `back`; current partial rows: 9; candidate stable IDs: 9.
- BodyParts3D muscle candidates: FMA33581 BP5638 ascending part of right trapezius, FMA33583 BP8225 ascending part of left trapezius, FMA13379 BP9246 rhomboid major, FMA13380 BP8586 rhomboid minor; locator `isa_parts_list_e.txt L425-L430 and L1262-L1320`.
- Bone candidates: FMA9139 BP8044 thoracic vertebra, FMA9921 BP8134 lumbar vertebra; locator `isa_parts_list_e.txt L262-L265 and L320-L322`.
- OpenSim candidate: Thoracolumbar spine and rib cage: T1-L5/rib cage and adjacent modeled segments; 93 DOF / 552 muscle-tendon actuators; MIT, July 2017; model files not fetched.
- Shared movement group candidate: thoracolumbar segment motion candidate; exact shared clip not identified. No production clip validated.
- Gap/next: T15g has 9 source-index rows but not exhaustive enumeration.

### 4. 어깨·어깨뼈 (`shoulder-scapular`)
- T15g source region: `shoulder`; current partial rows: 10; candidate stable IDs: 10.
- BodyParts3D muscle candidates: FMA34680 BP7573 clavicular part of right deltoid, FMA34682 BP7571 acromial part of right deltoid, FMA34684 BP5607 spinal part of right deltoid, FMA13109 BP9039 pectoralis minor, FMA13413 BP8215 subscapularis; locator `isa_parts_list_e.txt L383-L384, L440-L442, and L1321-L1330`.
- Bone candidates: FMA13395 BP9101 right scapula, FMA13396 BP9121 left scapula, FMA13322 BP9271 right clavicle, FMA13323 BP8841 left clavicle; locator `isa_parts_list_e.txt L396-L398 and L440-L442`.
- OpenSim candidate: Upper Extremity Dynamic Model: right upper extremity, 50th-percentile male, shoulder/arm movement, MIT, July 2014; model file/geometry/coordinate mapping not verified.
- Shared movement group candidate: shoulder/arm movement candidate; a clip may be shared with upper-limb only after scene/frame/pose compatibility is demonstrated. No production clip validated.
- Gap/next: Recommended first non-calf expansion input: T15g has 10 partial source IDs here; official index provides explicit right/left scapula/clavicle rows and deltoid-part entries; no local shoulder mesh or scene is currently inventoried.
- Gap/next: Concrete acquisition route: query FMA/BP IDs in the opened IS-A metadata list; resolve compound concepts to ELEMENT file IDs using the documented isa_element_parts.txt table; select only required OBJ members from the official 99%-reduced IS-A archive after recording hashes and CC BY attribution. Do not use representation ID as an OBJ filename without the element mapping.

### 5. 가슴우리 (`thorax`)
- T15g source region: `thorax_respiratory`; current partial rows: 7; candidate stable IDs: 7.
- BodyParts3D muscle candidates: FMA9756 BP8306 external intercostal muscle, FMA9757 BP8018 internal intercostal muscle, FMA9758 BP9146 innermost intercostal muscle, FMA13354 BP8019 intercostal muscle; locator `isa_parts_list_e.txt L314-L321 and L421`.
- Bone candidates: FMA7486 BP8562 manubrium, FMA7487 BP8989 body of sternum, FMA7574 BP8085 rib; locator `isa_parts_list_e.txt L159-L175`.
- OpenSim candidate: Thoracolumbar spine and rib cage model: ribs and articulated T1-L5; MIT, July 2017; documented model files include example motion but no respiratory-action clip was inspected.
- Shared movement group candidate: thoracic/rib-cage articulated motion candidate; not evidence of a respiratory muscle demonstration. No production clip validated.
- Gap/next: T15g has 7 source-index rows, not an exhaustive thorax or respiratory-muscle list.

### 6. 배·허리 (`abdomen-lumbar`)
- T15g source region: `abdominal_wall`; current partial rows: 2; candidate stable IDs: 2.
- BodyParts3D muscle candidates: FMA13335 BP8155 external oblique, FMA13336 BP4967 right external oblique; locator `isa_parts_list_e.txt L405-L407; literal “rectus abdominis” lookup had no matching text`.
- Bone candidates: FMA9921 BP8134 lumbar vertebra, FMA13072 BP8948 first lumbar vertebra, FMA13076 BP8280 fifth lumbar vertebra; locator `isa_parts_list_e.txt L322 and L377-L381`.
- OpenSim candidate: Thoracolumbar spine/rib cage model (MIT, July 2017); separate Lumbar Spine Model lists 3 DOF/238 muscle fascicles but documentation warns it lacks inertial body properties and is inappropriate for dynamics; CC BY 3.0 as listed.
- Shared movement group candidate: lumbar/trunk motion candidate; exact shared clip and abdominal muscle actuation not verified. No production clip validated.
- Gap/next: T15g has 2 abdominal-wall rows only; no full abdominal or lumbar muscle list is available. “rectus abdominis” no-hit in this exact table lookup is not an absence claim.

### 7. 골반·샅 (`pelvis-perineum`)
- T15g source region: `pelvic_floor_perineum`; current partial rows: 0; candidate stable IDs: 0.
- BodyParts3D muscle candidates: FMA19090 BP7792 pubococcygeus, FMA19091 BP8203 puborectalis, FMA19092 BP8008 iliococcygeus, FMA9623 BP8936 perineal muscle; locator `isa_parts_list_e.txt L300, L700-L707, and L1627-L1632`.
- Bone candidates: FMA16202 BP9174 sacrum, FMA16585 BP8769 hip bone, FMA16586 BP8768 right hip bone, FMA16587 BP8950 left hip bone; locator `isa_parts_list_e.txt L654-L658`.
- OpenSim candidate: No perineal/pelvic-floor muscle-actuated model located in the opened OpenSim model matrix; Thoracolumbar model includes pelvis context but that is not perineum coverage.
- Shared movement group candidate: pelvic-floor/perineum motion group: no source-backed clip candidate located in this metadata pass. No production clip validated.
- Gap/next: T15g source crosswalk has zero rows here; official BodyParts3D candidate rows are an acquisition lead, not membership decisions.

### 8. 볼기·깊은엉덩이 (`gluteal-hip`)
- T15g source region: `gluteal`; current partial rows: 10; candidate stable IDs: 10.
- BodyParts3D muscle candidates: FMA22314 BP8402 gluteus maximus, FMA22315 BP9214 gluteus medius, FMA22317 BP8624 gluteus minimus, FMA22340 BP5076 right piriformis; locator `isa_parts_list_e.txt L768-L789`.
- Bone candidates: FMA16585 BP8769 hip bone, FMA16586 BP8768 right hip bone, FMA24474 BP8920 right femur; locator `isa_parts_list_e.txt L656-L658 and L1172-L1173`.
- OpenSim candidate: OpenSim Custom Hip Model (based on Gait2392; CC BY 3.0 as listed); Full Body Running Model has lower-body muscles but torque-actuated arms; downloads not inspected.
- Shared movement group candidate: hip/gait movement candidate; link with thigh/leg/foot clip only after compatible source frames and pose are proven. No production clip validated.
- Gap/next: T15g has 10 gluteal source rows, not a complete hip or gluteal list.

### 9. 넙다리 (`thigh`)
- T15g source region: `none directly routed; lower_extremity remains held`; current partial rows: 0; candidate stable IDs: 0.
- BodyParts3D muscle candidates: FMA22430 BP8095 rectus femoris, FMA22431 BP8755 vastus lateralis, FMA22432 BP9129 vastus medialis, FMA22433 BP9208 vastus intermedius; locator `isa_parts_list_e.txt L807-L815 and L1506-L1513`.
- Bone candidates: FMA24474 BP8920 right femur, FMA24475 BP9042 left femur, FMA24485 BP8379 patella; locator `isa_parts_list_e.txt L1172-L1184`.
- OpenSim candidate: gait2392_simbody: bilateral lower limbs + lumped torso, 23 DOF/92 muscle-tendon actuators, CC BY 3.0 as listed; model files not freshly acquired.
- Shared movement group candidate: hip/knee gait-cycle candidate shared with adjacent leg only if compatible clip/body pose is proven. No production clip validated.
- Gap/next: No separate thigh sourceRegion in T15g; lower_extremity records are not auto-routed to thigh. B3D rows are external acquisition candidates only.

### 10. 종아리 (`leg`)
- T15g source region: `none directly routed; lower_extremity remains held`; current partial rows: 0; candidate stable IDs: 6.
- BodyParts3D muscle candidates: FMA22544 BP5018 right tibialis anterior, FMA22558 BP4999 right soleus, FMA22552 BP5013 right fibularis longus, FMA45957 BP5539 medial head of right gastrocnemius, FMA45960 BP5541 lateral head of right gastrocnemius; locator `isa_parts_list_e.txt L840-L865 and L1642-L1648`.
- Bone candidates: FMA24477 BP8031 right tibia, FMA24480 BP8009 right fibula, FMA24482 BP8033 right talus; locator `isa_parts_list_e.txt L1174-L1182`.
- OpenSim candidate: gait2392/gait2354 and leg6dof9musc models are bilateral or unilateral lower-limb simulation candidates; specific included rights/contents/licenses vary by model as listed; no T43 motion package imported.
- Shared movement group candidate: gait / ankle / knee lower-limb joint-group candidate; no production MotionDefinition or clip. No production clip validated.
- Gap/next: Current right calf pilot only: 6 muscle product membership rows, 2 static scenes; 9 right scene-bound bone IDs are context/selection bindings, not bone RegionMembership rows. Static partial scene is not a full leg catalog.

### 11. 발 (`foot`)
- T15g source region: `foot`; current partial rows: 3; candidate stable IDs: 3.
- BodyParts3D muscle candidates: FMA37450 BP9216 flexor digitorum brevis, FMA37461 BP5048 right flexor digitorum brevis, FMA37448 BP9194 abductor hallucis; locator `isa_parts_list_e.txt L1372-L1383`.
- Bone candidates: FMA24491 BP8035 tarsal bone, FMA24492 BP7914 metatarsal bone, FMA24496 BP8534 calcaneus; locator `isa_parts_list_e.txt L1185-L1189 and L1194-L1212`.
- OpenSim candidate: lower-limb OpenSim candidates contain a foot segment, but the opened model matrix did not provide a complete intrinsic-foot muscle/clip package; local mesh pilot includes only right-foot bone context, no foot membership rows.
- Shared movement group candidate: gait/ankle/foot segment candidate; intrinsic foot motion and muscle-specific clip not identified. No production clip validated.
- Gap/next: T15g includes only 3 foot source rows (one group, two individual muscles); not exhaustive. 3 other T13 right metatarsal mesh contexts are unbound, and are not foot membership.

### 12. 팔·손 (`upper-limb`)
- T15g source region: `upper_extremity, hand`; current partial rows: 10; candidate stable IDs: 10.
- BodyParts3D muscle candidates: FMA37683 BP8817 long head of biceps brachii, FMA37686 BP5566 long head of right biceps brachii, FMA37372 BP8208 muscle of hand; locator `isa_parts_list_e.txt L1351-L1353 and L1404-L1409`.
- Bone candidates: FMA23130 BP9206 right humerus, FMA23131 BP9191 left humerus, FMA23464 BP8464 right radius, FMA23467 BP8233 right ulna; locator `isa_parts_list_e.txt L1078-L1088`.
- OpenSim candidate: Arm26: right upper extremity, 2 DOF/6 muscles, CC BY 3.0 as listed; Upper Extremity Dynamic Model: right shoulder/arm, MIT; Kinematic Arm with Articulated Hand: 20 hand DOF, no muscles and license listed as None. These are distinct models; no one is a full bilateral viewer rig..
- Shared movement group candidate: shoulder/elbow/wrist/hand kinematics candidate groups; exact muscle actuation and license depend on chosen source model. No production clip validated.
- Gap/next: T15g has 10 upper_extremity source rows and zero hand rows. The BodyParts3D hand group entry does not imply hand member enumeration.

## First expansion recommendation for T32

**어깨·어깨뼈 (`shoulder-scapular`)를 우선 검토 후보로 권고한다.** 기존 T15g에는 partial source candidate 10 IDs가 있고, official index에서 우/좌 scapula·clavicle와 deltoid parts를 찾았으며, OpenSim 문서에는 우측 어깨·팔 동작 연구 모델과 MIT 표시가 있다. BodyParts3D route는 IS-A FMA/BP row → compound이면 `isa_element_parts.txt`에서 ELEMENT file ID 확인 → 공식 99%-reduced OBJ archive 중 필요한 파일만 취득 → hash/license/side/frame/pose 검토 순이다. T43에서는 archive를 다운로드하지 않았다. 프로젝트 local scene/membership은 아직 0이고, 후보 mapping·품질·사람 해부학 review는 미확정이다.

T32 입력 JSON은 `work/review-queue/t32-input-t43.json`; full source locators/edition/access/right history는 `work/evidence/T43/source-access.json`; gaps는 `work/review-queue/region-acquisition-gaps-t43.json`이다. T32 자체는 T31을 prerequisite로 하므로 여기서 시작하지 않았다.

## 분모 후보 및 해석

- 후보 authoritative list: FIPAT Terminologia Anatomica Second Edition (2019) Muscular System rows already provisionally stored in `source-crosswalk.json`; current T15g partial list contains 85 stable IDs. Do not substitute asset-index rows for an authority list.
- T32 must decide and document: individual named skeletal muscle as unique denominator; groups/heads/parts/variants separated; side instances do not create new stable concepts; cardiac/smooth/non-muscle excluded; boundary items individually decided; one stable ID may have multiple product memberships but counts once in unique denominator.
- Current `lower_extremity` 12 partial IDs include 6 existing leg individual-mucle product decisions; 4 groups + 2 parts remain unrouted. Never fan these out to thigh/leg/foot by default.
- T15g status not mutated: `denominatorFrozen=false`, `wholeBodyIndividualMuscleCount=null`, `coveragePercent=null`.

## 출처/접근 경계

- [BodyParts3D archive README](https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/README_e.html): opened. Page dated 2025-02-27; states adult male whole-body model; Release 4.0 mesh last updated 2013-06-19; atomic ELEMENT polygons only; compound expansion file documented.
- [BodyParts3D IS-A metadata table](https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_parts_list_e.txt): opened as 2,906-line text list with FMA concept / representation / English label; exact line locators included in JSON.
- [BodyParts3D license](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html): opened; CC BY 4.0, attribution required.
- [Official download inventory](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html): opened; OBJ bundles are 136MB/62MB. Not downloaded.
- [OpenSim official model matrix](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53090607): opened; model entries have different scopes, revisions, limitations and per-model licenses. A simulation model is not a viewer-ready rig.
- [FIPAT TA2 Part 2 official PDF](https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf): direct fetch returned 502; search result is index-only. Existing crosswalk page/table locators and edition labels remain provisional; term-cell roles are unverified.

## 검증/보존

- Exact 12 category ID/order check against `atlas-navigation.json`; no submenu or canonical data change.
- T15g data checks, T15g crosswalk, BodyParts3D line evidence, rights/access records and source locator validation saved to `work/evidence/T43/validation-results.json`.
- Start status/HEAD and pre-existing changed-file SHA256 snapshot: `work/evidence/T43/start-baseline.json`. Post-task compare: `work/evidence/T43/preservation-after.json`.
- No code/UI/clip data changed, so browser, typecheck and production build were not in scope; source data validation and the existing T15g inventory regression were run.

## Next

**T44 / Sol High** is the R14 registry’s next actual task after T43. This report prepares its background only; T44 was not started. Copy the detailed prompt from `work/tasks/T44.md`.
