# T43 누락·보류 목록

- T43 상태: `open_gaps_for_T32_and_future_region_packages`
- 아래 gap은 메타데이터 조사 완료와 전신 구현을 구분한다.

## T43-G-DENOMINATOR
- 상태: open
- 근거: T15g denominatorFrozen=false; count=null; coverage=null; 85 current rows are partial extraction.
- 담당: T32 / Luna Max after T31 prerequisite
- 해결 조건: Complete authoritative section enumeration, inclusion/exclusion decision ledger, and per-concept table/page locators; freeze only after unresolved exceptions have explicit held states.

## T43-G-TA2-ACCESS
- 상태: blocked_by_access_and_locator_audit
- 근거: TA2 Part 2 direct official PDF open returned 502; existing source-crosswalk term cell role is unverified. Search index is not an opened source.
- 담당: T32 and region data batches
- 해결 조건: Open official Part 2 source or legitimate local copy; inspect table columns and validate each exact row/page locator. Keep existing rows provisional.

## T43-G-MESH-ACQUISITION
- 상태: candidate_inventory_only
- 근거: BodyParts3D table candidates are open; full polygon bundles are 136MB/62MB and were not downloaded. Existing local OBJ/GLB are right-calf subset only.
- 담당: T32 package planner; later bounded structure package owner
- 해결 조건: For selected IDs resolve representation→ELEMENT file ID, request only permitted needed OBJ files, record hash/license/side/unit/frame/topology, inspect, and map only after evidence.

## T43-G-BILATERAL-COVERAGE
- 상태: partial
- 근거: Index contains explicit right/left examples but no complete side audit; product scene is right-sided only.
- 담당: T32
- 해결 조건: List authority and model entries by side for every included concept; never mirror a unilateral source mesh without transformation evidence.

## T43-G-LOWER-EXTREMITY-BOUNDARY
- 상태: open
- 근거: T15g crosswalk forbids auto-copying lower_extremity into thigh/leg/foot; six current leg individuals have existing product decisions; four groups and two muscle parts remain unassigned.
- 담당: T32 / anatomy crosswalk reviewer
- 해결 조건: Decide each stable ID's evidence-backed memberships; permit multi-membership without duplicating stable ID.

## T43-G-LEARNER-CONTENT
- 상태: not_created
- 근거: This survey lists terms and source-candidate rows only. No origin/insertion/function learner text was authored.
- 담당: Future source-backed structure/function packages
- 해결 조건: Extract only exact supported field text with per-field source references and keep AI evidence/human review states independent.

## T43-G-RIG-CLIP
- 상태: candidate_models_only
- 근거: OpenSim docs list disparate research/example models with different frames, sides, licenses and limitations; no compatible learner rig/production MotionDefinition/clip was validated.
- 담당: T44 and later motion package owners
- 해결 조건: Choose one coherent source per demonstration; verify source archive, license, topology, frames, units, pose and motion data before any import.

## T43-G-MODEL-RIGHTS
- 상태: partial
- 근거: BodyParts3D database CC BY 4.0 attribution identified. OpenSim doc rows have per-model rights (including CC BY, MIT, Custom, None); local files are not fully itemized for redistribution.
- 담당: Selected regional package owner
- 해결 조건: Audit each specific source asset and derivative obligations; no blanket project license inference.

## T43-G-HUMAN-ANATOMY
- 상태: not_reviewed
- 근거: No anatomical reviewer participated in T43.
- 담당: Human reviewer when package review is scheduled
- 해결 조건: Review source terms/mapping/content and any geometry/motion as separate review targets; do not promote automatically.

## 부위별 취득상태

| 부위 | 상태 | 현재 후보 IDs | 현재 근육 memberships | 미완 |
|---|---|---:|---:|---|
| 머리 (`head`) | additional_build_needed | 22 | 0 | BodyParts3D index lookup for literal “masseter” and “temporalis” returned no match (L0, no matching text); this is a bounded index-search gap, not proof of model absence.; T15g head pool merges source head/face/mastication/eye/tongue only as routing candidates. |
| 목 (`neck`) | additional_build_needed | 0 | 0 | No neck source rows in the current T15g crosswalk; official index entries do not create project canonical IDs or memberships.; Resolve source terminology rows and name triplets without guessing; preserve original English/Latin evidence. |
| 등 (`back`) | additional_build_needed | 9 | 0 | T15g has 9 source-index rows but not exhaustive enumeration.; Resolve source terminology rows and name triplets without guessing; preserve original English/Latin evidence. |
| 어깨·어깨뼈 (`shoulder-scapular`) | additional_build_needed | 10 | 0 | Recommended first non-calf expansion input: T15g has 10 partial source IDs here; official index provides explicit right/left scapula/clavicle rows and deltoid-part entries; no local shoulder mesh or scene is currently inventoried.; Concrete acquisition route: query FMA/BP IDs in the opened IS-A metadata list; resolve compound concepts to ELEMENT file IDs using the documented isa_element_parts.txt table; select only required OBJ members from the official 99%-reduced IS-A archive after recording hashes and CC BY attribution. Do not use representation ID as an OBJ filename without the element mapping. |
| 가슴우리 (`thorax`) | additional_build_needed | 7 | 0 | T15g has 7 source-index rows, not an exhaustive thorax or respiratory-muscle list.; Resolve source terminology rows and name triplets without guessing; preserve original English/Latin evidence. |
| 배·허리 (`abdomen-lumbar`) | additional_build_needed | 2 | 0 | T15g has 2 abdominal-wall rows only; no full abdominal or lumbar muscle list is available. “rectus abdominis” no-hit in this exact table lookup is not an absence claim.; Resolve source terminology rows and name triplets without guessing; preserve original English/Latin evidence. |
| 골반·샅 (`pelvis-perineum`) | additional_build_needed | 0 | 0 | T15g source crosswalk has zero rows here; official BodyParts3D candidate rows are an acquisition lead, not membership decisions.; Resolve source terminology rows and name triplets without guessing; preserve original English/Latin evidence. |
| 볼기·깊은엉덩이 (`gluteal-hip`) | additional_build_needed | 10 | 0 | T15g has 10 gluteal source rows, not a complete hip or gluteal list.; Resolve source terminology rows and name triplets without guessing; preserve original English/Latin evidence. |
| 넙다리 (`thigh`) | additional_build_needed | 0 | 0 | No separate thigh sourceRegion in T15g; lower_extremity records are not auto-routed to thigh. B3D rows are external acquisition candidates only.; Resolve source terminology rows and name triplets without guessing; preserve original English/Latin evidence. |
| 종아리 (`leg`) | static_only | 6 | 6 | Current right calf pilot only: 6 muscle product membership rows, 2 static scenes; 9 right scene-bound bone IDs are context/selection bindings, not bone RegionMembership rows. Static partial scene is not a full leg catalog.; Resolve source terminology rows and name triplets without guessing; preserve original English/Latin evidence. |
| 발 (`foot`) | additional_build_needed | 3 | 0 | T15g includes only 3 foot source rows (one group, two individual muscles); not exhaustive. 3 other T13 right metatarsal mesh contexts are unbound, and are not foot membership.; Resolve source terminology rows and name triplets without guessing; preserve original English/Latin evidence. |
| 팔·손 (`upper-limb`) | additional_build_needed | 10 | 0 | T15g has 10 upper_extremity source rows and zero hand rows. The BodyParts3D hand group entry does not imply hand member enumeration.; Resolve source terminology rows and name triplets without guessing; preserve original English/Latin evidence. |
