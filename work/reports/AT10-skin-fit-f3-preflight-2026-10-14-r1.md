# AT10 skin-fit F3 head/ear/neck preflight — 2026-10-14

**Disposition: F3 not started because F1 and F2 prerequisites do not pass.** No head, ear, neck, eyelid, oral-return geometry, recipe, GLB, or learner QA was performed.

## Start and ownership

- Starting HEAD: `e2a5526d060cba259d9d6a608498ed6973bea291`.
- Starting worktree status: 7477 entries, 845287 bytes, SHA-256 `07d3267670f88f6a569c10949f716ff822938704f6d5a5e2cb828d87397f252e`.
- Starting `work/EXECUTION.json` SHA-256: `4cef3d5ab9965dd77b43e53d2b2af45d2361b2a1ef8117f5d014fc8557432f74`.
- Owned changes are limited to this preflight folder, this report, and `featureWorkUnits.AT10.skinFit.f3Preflight`. The existing user WIP, F1/F2 outputs, source/native/UV/helpers, original IDs, OpenSim/T13, historical evidence, and AT10 acceptance fields remain untouched.
- The visible Codex task snapshot contained no matching active AT10/F3 worker.

## Actual predecessor gate

The latest EXECUTION records AT10 `resumeUnit=skin-fit`, AT10 `acceptancePassed=false`, and `featurePlans.acupoint-at-361.nextUnit=AT10`. F1 evidence in [f1-assessment-r2.json](../evidence/AT10/2026-10-14-f1-right-foot-r1/f1-assessment-r2.json) remains partial, with `candidateEmitted=false` and no final candidate manifest/GLB. Its exact remaining unit is **`F1-conforming-branch-cage-and-source-surface-embedding`**. F2 evidence in [f2-preflight.json](../evidence/AT10/2026-10-14-f2-preflight-r1/f2-preflight.json) says F2 was not started and left-foot raw/policy QA and learner screens were not run. The existing r41 hand checkpoint still records local native/self crossings of zero for both hands, but it does not pass whole-skin geometry. Therefore F1/F2 actual bilateral finals and QA are not complete, so F3 cannot begin.

## Existing F3 evidence retained for later reuse

I read the existing head/ear attempt ledger and remaining queue without repeating its source survey. The r56 `reference-assessment` contains 12,412 actionable head native-address pairs over 461 unique skin triangles; the stored remaining queue records 461 head native-crossing facets and 527 head self pairs. The prior source baseline separately reports 0 self pairs for core source and 30 for the pinned young target; these counts describe different inputs and are not merged. The current actual head screen is [actual-r58p1-head.png](../evidence/AT10/2026-10-14-completion-r1/screens/actual-r58p1-head.png), a young-target preview with visible eyelid/oral/ear/neck mismatch, not an accepted adult recipe. Earlier r48/r49 head attempts remain rejected: r48 reduced local self intersections while worsening native contacts, and r49 retained 1,156 local native crossings and failed its positive-Jacobian guard. Ear cartilage exposure and lower-face/neck/return mismatch remain documented in the existing visual review.

The historical r41 bilateral hand asset is preserved with its exact manifest/GLB and local-only QA. The r56/r58 GLBs are rejected baselines, and r22 is only a review checkpoint. These files are not F1/F2 pass assets.

## Result and next unit

F3's adult deterministic recipe, outer cranial/face bands, pinna attachment/helix/concha/lobule mapping, neck collar, eyelid/oral-return contract, emitted GLB, and actual front/bilateral/back/close-up learner QA are **not started**. No mucosa, return exception, or geometry was fabricated.

Exact next unit remains **AT10/skin-fit/F1-conforming-branch-cage-and-source-surface-embedding**. Resume with [NEXT-F1-RESUME-R2.txt](../evidence/AT10/2026-10-14-f1-right-foot-r1/NEXT-F1-RESUME-R2.txt); only after accepted F1 and F2 bilateral outputs may F3 start. F4 was not started.

## Validation

`work/EXECUTION.json` records only this F3 preflight. AT10 parent status/acceptance, `resumeUnit`, feature-plan next ID, F1/F2 results, and unrelated records are unchanged. `sync_execution.py` and `--check` are run after the scoped update.
