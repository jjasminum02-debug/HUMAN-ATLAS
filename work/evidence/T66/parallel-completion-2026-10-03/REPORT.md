# T66 internal parallel preparation — 2026-10-03

## Result

Wave 1 is frozen and worker-ready for manual execution. This is an internal T66 preparation result, not a new task, T66 acceptance, learner registration, anatomical approval, or public redistribution approval. No worker, agent, thread, app runtime, learner UI, or source geometry was started or changed.

The frozen run is `T66-W1-20261003-5dadff8d782b`, based on HEAD `ae993a8a455632d738b2141f50ad09789bf5ee7c`. Canonical manifest SHA256: `a495d9421e38aadf4990dcfa5758661ab4a852d8690b483c328b34bccce2b511`. The manifest and input snapshots are at `work/evidence/T66/parallel-completion-2026-10-03/wave-1/`.

## Frozen responsibility and denominators

The run preserves 542 targets, 563 memberships, 12 regions, 429 muscle targets/447 memberships, 232 source concepts/462 source surfaces, 210 whole-bone source rows, 98 nerve label rows, 130 HA bindings, and historical 163 (6/20/135/2). Bone and nerve row counts are not treated as independent anatomical concept counts. Source-only remains true; public redistribution is held; human review is `not_performed`; no canonical binding was added.

| Manual wave-1 owner | Targets | Memberships | Muscle source keys | Bone context rows | Nerve rows | Work keys |
|---|---:|---:|---:|---:|---:|---:|
| A — hand/digits | 26 | 26 | 42 | 54 | 0 | 42 |
| B — hip/knee/ankle/foot | 82 | 85 | 112 | 64 | 0 | 112 |
| C — spine/ribs/respiration | 158 | 162 | 166 | 54 | 0 | 166 |
| F — nerve text/course | 0 | 0 | 0 | 0 | 98 | 98 |

Across assignments, 418 of 560 exact work keys are assigned once; 142 remain deferred with the frozen integration routing. No assigned work-key collision was found. D/E are wave 2 and were not launched. Shoulder/scapular and other residual integration work remains with the common writer. Source keys can recur in distinct family/action responsibilities; they are not counted as duplicate assets.

The 924 immutable source-resource references cover the frozen source surface records; there are 627 unique resource hashes. Full source archives were not copied or rehashed. Source GLBs are resolved from their immutable local paths and checked against their pinned hashes when the candidate harness reads them.

## Common processing path and bounded smoke

Added the candidate package schema, manifest validator/builder, exact work-key protocol tests, and a worker harness with explicit repository, frozen-input, and output roots. Geometry output is confined to the selected owner directory; workers cannot write the frozen common files or register into the learner runtime. Frozen code is imported from the snapshot. Cache identity includes source bytes/frame/side/geometry, instance transform, candidate input, pose, weights/mask, validator revision, rights policy, and family scope.

The existing U02 left hip-flexion input was run through the common writer dry-run with source cache disabled and enabled. Both runs checked 72 existing source GLBs against their SHA references and made 110 source-cache requests. The no-cache run recorded 110 misses; cached run recorded 72 misses/38 hits. Source read/hash/decode/transform was 0.0572 s vs 0.0247 s. Total authoring geometry/solver/GLB assembly was 1.5307 s vs 1.5077 s in this single pair; this is not a speedup claim. Reference GLB, emitted motion GLB, authoring record, and pose-QC bytes were identical, as were semantic handoff and replay fields. Existing pose/contact/interpolation QC was reused only because source input and emitted GLB hashes matched. 56 rigid rows replayed and 16 deforming rows remain subject to geometry QC. Reflection rows were preserved. The sample remained a candidate dry-run and was not registered.

The saved T66 B1 r6 failure was inspected without rerunning its failed contact trial. Existing evidence records three newly contained femur vertices (248, 257, 262) for source `ZA-c7010a9-fd0168c8488ff1aa5ec47694` against hip-bone source `ZA-c7010a9-ecb65ff4cc3da710e5a2d157`; the artifact-only profile records generation-stage timing as unavailable. No new hypothesis justified repeating that trial.

## Validation and preservation

- Final read-only manifest validation passed for the run hash and all target, membership, source, bone, nerve, assignment, and snapshot consistency checks.
- Eight protocol cases passed: valid package acceptance; rejection of extra/missing/duplicate fields and invalid/timezone-free timestamps; rejection of an exact repeated action key; acceptance of the same source in distinct families.
- Python compilation passed for the builder, protocol, harness, validator, and protocol tests.
- The candidate smoke compared four emitted file byte hashes plus semantic handoff; no learner/browser integration was attempted because this unit changes no learner runtime.
- The start baseline records 2,389 pre-existing dirty paths (628,289,617 regular-file bytes). Existing U03 shared-code hashes matched its checkpoint at start. `OpenSim_Models/` had no dirty paths. Source cache, T13 drafts, other unit evidence, and user WIP were not edited.
- Final preservation comparison rehashed all 1,195 pre-existing dirty files in the T66 serial-unit evidence subtree against the start baseline: 0 changed and 0 missing. `OpenSim_Models/`, source-cache, and T13 path status remained clean. See `preservation-final.json`.

## Handoff boundary

T66 remains `in_progress / partial`; parent `nextUnit=author-and-integrate-normal-motion-bone-and-nerve`; unresolved product blocker T66-B3 remains. This result only makes wave-1 inputs and the candidate path ready. It does not finish the outstanding U03/U01 content and UI gaps, T66 motion production, or any worker assignment.

Manual worker prompts are ready, but none has started:

- A: `work/plans/t66-parallel-completion-2026-10-03/02-worker-A-hand.txt`
- B: `work/plans/t66-parallel-completion-2026-10-03/03-worker-B-leg-foot.txt`
- C: `work/plans/t66-parallel-completion-2026-10-03/04-worker-C-spine-ribs.txt`
- F: `work/plans/t66-parallel-completion-2026-10-03/05-worker-F-nerve-text.txt`

Validation artifacts: `wave-1/validation/manifest-validation-final.json`, `assignment-summary-final.json`, `writer-checkpoint-final.json`, `protocol-contract-tests-final.json`, `cache-equivalence-final-v2.json`, `historical-r6-failure-profile.json`, and `preservation-final.json`.
