# AT10 skin-fit F2 left-foot preflight — 2026-10-14

**Disposition: F2 not started because F1 has not passed.** No left-foot geometry, reference checks, GLB, or learner-runtime work was performed. AT10 remains on the exact F1 unit.

## Start and scope

- Starting HEAD: `045227c5c08a7e9cb1299ce48d431f583b8e0b1c`.
- Starting status: 7,477 entries, 845,287 bytes, SHA-256 `07d3267670f88f6a569c10949f716ff822938704f6d5a5e2cb828d87397f252e`.
- Starting `work/EXECUTION.json` SHA-256: `5bd200717f51a14f2902c21e1748671e2683a86f0f445d8ca399fe6b1d4041c0`.
- Owned output is limited to this versioned preflight folder, this report, and `featureWorkUnits.AT10.skinFit.f2Preflight`. Existing user WIP, `OpenSim_Models/T13`, all F1/history evidence, source/native inputs, and GLBs/manifests were read-only.
- The visible Codex task snapshot had no matching active AT10 skin-fit task. OS process enumeration returned `operation not permitted`; no process-level claim is made.

## Predecessor gate

The latest EXECUTION still records AT10 `resumeUnit=skin-fit`, `skinFit.status=partial`, `acceptancePassed=false`, `geometryValidationPassed=false`, and `candidateRevision=r22` as a review checkpoint. The current F1 run evidence is [f1-assessment-r2.json](../evidence/AT10/2026-10-14-f1-right-foot-r1/f1-assessment-r2.json), [remaining-units-r2.json](../evidence/AT10/2026-10-14-f1-right-foot-r1/remaining-units-r2.json), and [run-manifest-r4.json](../evidence/AT10/2026-10-14-f1-right-foot-r1/run-manifest-r4.json). F1 has `acceptancePassed=false`, emitted no candidate, and leaves **`F1-conforming-branch-cage-and-source-surface-embedding`** incomplete. Its remaining record explicitly says `doNotAdvanceTo=F2`.

F1's source/native audit records 126/126 ordered toe sections, ten closed whole-foot sections, and 416 exact residual contact addresses. Its 40 shared controls include 22 actual topological boundary vertices and 18 interior controls; the source boundary is 0.298–0.335 m from the explicit ankle control, so it was not relabeled from geometry. The shell proposal leaves all 18 interior controls outside tolerance. Only 210/1,209 nonfixed patch vertices have consistent in-cell addresses; 999 are uncovered or ambiguous, and 412/416 source/native contact comparisons exceed 20 µm. Sampled positive cell derivatives are local diagnostics only. The frozen r55 toe-chain/harmonic-weight/C1-calf-collar recipe and rejected r56/r58 recipes were read by hash; the cage investigation did not emit an accepted replacement recipe. The source-role review remains incomplete. No F1 final candidate manifest/GLB/hash or installed-loader/learner QA exists. The existing r22 candidate is a review checkpoint, not an F1 pass.

The actual learner screens for historical r56p1 and r58p1 were viewed and their hashes are recorded in [f2-preflight.json](../evidence/AT10/2026-10-14-f2-preflight-r1/f2-preflight.json). They remain rejected historical baselines, not F1 outputs. r56 has 2,391 raw whole-surface crossings and 1,334 self-pairs; its right foot has 513 raw crossings and 21 retained valid-reference crossings. r58 remains a rejected alternative. The exact r41 hand checkpoint was reused read-only: prior evidence records both-hand native/self contacts at zero while whole geometry remains unaccepted. The 991-face right Crural fascia separation and remaining 9,884 faces are preserved; no exception was mirrored to the left.

## Result and next unit

F2 did not pass or fail its own geometry gates; it was **not started**. Left-side source/native role review, 834 raw/policy-separated reference QA, self/3D deformation/seam checks, emitted GLB, and actual learner screens are all `not_started`/`not_run`. No new screen was created because there is no accepted F1 method/output to extend.

Exact next unit remains **AT10/skin-fit/F1-conforming-branch-cage-and-source-surface-embedding**. Resume using [NEXT-F1-RESUME-R2.txt](../evidence/AT10/2026-10-14-f1-right-foot-r1/NEXT-F1-RESUME-R2.txt). Do not start F2 until F1 has an actual accepted source-bound candidate and learner QA.

## Validation and preservation

No geometry, authoring, manifest, candidate, runtime, camera, or UI files were changed. `work/EXECUTION.json` receives only the scoped F2 preflight note; AT10 parent acceptance, F1 result, resume unit, feature plan next ID, and unrelated records remain unchanged. `sync_execution.py` and `--check` are run after this record is added.
