# T66 unit 03 continuation - 2026-10-03

## Verdict

This continuation preserves the in-progress U03 verification, completes the actual-browser supplement for U01, and reconciles current U03 candidate/registration and runtime counts. Parent T66 remains `in_progress / partial`, with `nextUnit=author-and-integrate-normal-motion-bone-and-nerve`. No common runtime, exporter, source, or GLB file was modified by this continuation.

## Baseline and current counts

- Starting HEAD: `2aa20fc03757f4a890dbe8220eb316aa282863bc`; the dirty-path snapshot records 2,389 paths. It did not record per-file hashes for dirty paths, so byte equality for those paths is not claimed.
- Current motion bundle SHA-256: `39843e60f22bfa0e8380362f90c3415d2d992399f4b1640ef852e73e6256ca25`.
- Unique muscle source surfaces: 107; muscle-action rows: 273. Unique bone source instances: 150; bone-family rows: 865.
- Source-derived GLB URIs: 33 and unique GLB SHA-256 hashes: 33. Runtime including T24: 34 URIs and 34 hashes. URI and hash counts were calculated separately and are one-to-one in this runtime. These are asset references/hashes, not visual acceptance or independent anatomy concepts.
- All 18 latest U03 family-side candidates are `candidate_pass`; all 18 are in the r4 registration receipt, with zero candidate/receipt hash mismatches. This is candidate QC and registration, not individual learner-UI acceptance for 18 packages. The requested `registration-r2.json` does not exist; the current registration is `registration.json` (`t66-u03-registration-r4`).

## Pose and action scope

The registered U03 packages are bounded source-pose observations with passive surface deformation; they add no prime-mover or muscle-activation clip. Scapular superior rotation R2 is explicitly scapula/clavicle-only, with humerus and distal-arm movement excluded; it does not represent full scapulohumeral rhythm. Current wrist radial-deviation R3 restores an authored 7-degree observation on each side after the intermediate R2 4-degree trial; neither is physiological ROM. Exact source side/member scope is recorded separately from whole-target/group extent. Inputs and hashes are in [`scope-interpretation.json`](scope-interpretation.json).

## U01 browser supplement

Chrome/Playwright verified four combinations: bilateral short head of biceps brachii with shoulder flexion and elbow flexion. Source/side/action card match, canvas change during motion, re-click return to rest, no internal metadata exposure, and zero console/page errors were observed at 1440x960. This closes only the U01 UI environment gap for those exact combinations; it does not approve a whole-family extent or constitute human review. Captures and hashes are in [`browser-u01/`](browser-u01/).

## Remaining gaps and preservation

Existing U03 content gaps remain: bilateral FCU ulnar-head direction (2 rows), the Supinator source-direction conflict, and trapezius whole-group action not inherited to portions. Source-only/local technical selection, public rights `held`, human review `not_performed`, and zero new HA canonical bindings remain unchanged. No new family expansion or T66 pass was claimed. Historical trials remain preserved by revision.

The common-writer checkpoint is [`common-writer-checkpoint.json`](common-writer-checkpoint.json). The initial dirty-path manifest lacks hashes for files already dirty at start, so it does not claim prior byte equality; it records the current hash for the next writer to snapshot and compare. Execution projections were synchronized and checked with `python3 work/tools/sync_execution.py` and `--check`.

Next manual input: `work/plans/t66-parallel-completion-2026-10-03/01-writer-freeze-and-optimize.txt`. It was not started.
