# T100 cached-source integration — 2026-10-01

## Result

The six cached BodyParts3D R4 candidates from the frozen closure action queue were integrated into the existing single scene through the common mixed-source adapter. The supplement contains 13 source instances in five already-cached chunks; the original ZA base remains 960 objects, so the composite local dataset has 973 objects. No raw source bytes or source-cache GLB were downloaded or changed. The original `HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR` frame is preserved through the T50/T69/T77 registration (`[x,y,z] mm -> [x,z,-y] m`, no mirror, no source-side rewrite).

Target scopes: TA2:1282 uses the BodyParts3D FMA16580 three-member source-declared set (right hip bone FJ3152, left hip bone FJ3288, unsided sacrum FJ3393); this is not claimed to cover every anatomical definition of the bony pelvis. TA2:2128 maps the exact source-parent relation to bilateral levator veli palatini surfaces FJ2741/FJ2753. TA2:2129 maps tensor veli palatini FJ2748/FJ2760. TA2:2191 maps salpingopharyngeus FJ2745/FJ2757. TA2:2202 maps vocalis FJ2788/FJ2806. TA2:2283 maps semispinalis capitis FJ1538/FJ1538M. Every source row has source FMA/FJ identity, original source hash, compiled geometry identity, explicit source-side or unsided status, frame/pose, region, rights and target association in the supplement manifest.

## Actual app verification

The real learner app loaded each of the 13 source objects by source-key route. In all 13 samples the single canvas selected the expected source object; after existing “select only” and “fit” controls, only that object was visible, with no pending or failed loads. The source-backed card, region, and explicit left/right state matched. All 13 selected surfaces were visibly rendered; this is a local surface observation only, not proof of whole target, group, bilateral, variant or anatomical extent. The two salpingopharyngeus objects intentionally have `koTraditional: null`; no synonym was promoted to fill it.

CUA screenshot byte SHA256 values are recorded in `browser-qa.json`, but the browser API did not expose a filesystem save path; no PNG/JPEG file is claimed or committed. Direct endpoint navigation was blocked and local urllib was denied, so a hash of the actual browser network response could not be captured. The same Vite plugin middleware's endpoint bodies were exercised by `test:delivery`; their exact bytes and SHA256 are in `verification.json`, clearly labeled as plugin-harness output rather than browser-network response hashes. Console warning/error list after the browser run was empty.

## Fixed counts and policy

The canonical overlay remains at 409/542 target IDs and 427/563 memberships with a canonical path, because these supplemental observations deliberately create no HA binding and do not edit the overlay. The fixed denominator remains 542 targets / 563 memberships / 12 regions; the existing 130 HA bindings and historical 163 classifications (6/20/135/2) remain unchanged. Base eligible display-name count remains 672; direct target Korean citation gaps remain 73. Supplement rows are source-only and default-hidden; local display is allowed only by the per-item T77 decision, public redistribution stays held, and human review remains `not_performed`.

The six cached-candidate rows are now adjudicated as local source observations. The other 127 queue rows still need exact source correspondence, variant/member/extent/part/side evidence or an actually supported source. Missing routes remain unresolved rather than “geometry absent.” No repeated fixed-name search, new download or made-up geometry was used.

## Verification

- Supplement builder: passed.
- Whole-body regression: 54/54, including 46 compiled chunk dependencies.
- Delivery route checks: 3/3.
- Typecheck and production build: passed. Vite retained a non-failing 955.03 kB App bundle-size advisory.
- `python3 work/tools/sync_execution.py` and `--check`: passed; zero generated views needed updating, so shared STATUS/NEXT WIP was preserved.
- Browser: 13/13 source selections/card/side/region/isolation checks; screenshots observed but not persisted.

**T100 remains `in_progress / partial`, `nextUnit=resolve-target-representation-and-final-scene-qa`.** Remaining work includes 133/542 targets and 136/563 memberships without canonical paths, 73 direct term-evidence gaps, full target/part/group/side extent adjudication, and exhaustive localized selection QA. GPU/VRAM/process-memory measurement is not repeated. See `candidate-resolution.json`, `browser-qa.json`, and `verification.json`.
