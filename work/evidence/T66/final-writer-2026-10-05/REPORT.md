# T66 final writer continuation — 2026-10-05

## Scope and baseline

This execution fixes the shared wave-2 writer contract and reviews the actual D/E candidate layouts and evidence. It does not change the learner runtime or promote a candidate to app registration. Baseline HEAD was `67840b1e51ad8956ac8a52f3214feb9288d25c21`. The initial status snapshot contained 5,464 dirty/untracked entries with SHA256 `9a4da85caeca9db6d2cca120cbab24627e92de5cc7dee5abe43a74a325d1fdfb`; prior WIP is preserved.

## Writer contract changes

The frozen wave-2 manifest has raw SHA256 `d6ad4413da2beb44508715f1e48b8389c29071d2cad28fb28c2254a3f0c1a600`. Its D 16 and E 66 assigned work-key IDs and six-field keys match the frozen scope queue, but copied ownership fields disagree: the embedded assignment rows say `deferred/null/E` while the queue and source disposition say `assigned/D` or `assigned/E`. Receipt `writer-correction-revision-r1.json` pins the raw file and hashes each affected row. It changes only `disposition`, `assignedTo`, and `deferredTo` in an in-memory effective copy: D 16, E 66. The original manifest, assignment snapshots, and worker handoffs remain unchanged. The effective manifest validates at 542 targets, 563 memberships, 462 muscle surfaces, 210 bone source rows, 98 nerve rows, 560 exact work keys, 500 assigned keys, and 924 resource refs.

Runner preflight succeeds for D (16 keys) and E (66 keys), including E's existing non-empty output root with `start.json` and `source-audit.json`. The ownership scan found no symlink or other-assignment file. Typed bone context is kept separate from assigned muscle keys and read-only: D has 1 context key and E has 16. Neither becomes a muscle member or independent DOF. The preflight-only command creates and removes its unique probe and authors no geometry.

The post-run preservation check confirms the frozen wave-2 manifest, D handoff, E aggregate package index and E handoff still match their start-of-run SHA256 values. No preflight probe remains. `OpenSim_Models/` and `work/evidence/T13/` have no Git status changes.

The worker output formats differ. D has per-family jaw/jointless packages nested in its handoff and no aggregate `candidate-package.json`. Its candidate batches are not forced through the runner's single-payload interface. E has a separate aggregate candidate index referring to 56 GLBs and multiple candidate input records, so a separate aggregate-index validator checks the index and artifact hashes.

## Actual candidate result

- **D:** The frozen D handoff still contains its historical pre-correction assignment conflict and remains unregistered. Its 16 rows comprise 10 jaw engineering failures, 2 source/relation gaps, 2 not-applicable rows, and 2 `candidate_validated` rows with null family/action. The latter are scope dispositions, not muscle-action acceptance. D has 22 candidate GLBs, none registered.
- **E:** Its index contains 206 artifact rows. 205 current files match the indexed SHA256 and size. `proposals.json` does not: indexed SHA `d9ccc51c8e263b936d7d7b97043b3b2a5c598c9c195a0251ed562a0689af52eb` / 949,336 bytes; observed SHA `921156988bb276547c4284626798c6fb05af6fbaa0675edee57bbf564fa9cf09` / 980,461 bytes. The validator records this as a failure. The file and index were not rewritten or rebased. Its 56 candidate GLBs have 38 local geometry-QC passes and 18 failures, but action-outcome QC is 0/56 and validated work keys are 0. No E candidate is registered.
- Both runners' preflight pass only confirms frozen assignment/module/output readiness; it is not candidate authoring or learner acceptance. E's aggregate index failure remains a distinct artifact-integrity blocker.
- Exact D/E remaining action work keys and their family/side/part/pose keys are enumerated in `wave2-unresolved-workkeys.json` (D 12 blocked/missing rows; E 66 blocked/missing rows). The evidence gives the next engineering or source-resolution action per row and preserves the original worker handoffs.

## Learner action and content scope

The current action explorer is 13 labels, 35 exact source-action links, and 19 source surfaces. The 311 source-action ledger rows are rows, not 311 distinct actions. Contextual posture is not counted as a muscle action. The preserved action experience has one CTA, actual-clock toggle/rest behavior and scrub-held behavior. No learner/runtime code changed in this writer-only correction; existing browser evidence is reused. That evidence records actual viewport 825×807; this execution does not claim that 390/1024/1440 were verified.

Denominators remain 542 targets / 563 memberships / 12 regions; muscle 429 / 447; 232 source concepts / 462 surfaces; HA canonical bindings 130; historical classification 163 (6/20/135/2). Source-only, technical local selection, public redistribution `held`, human review `not_performed`, no new full-target extent approvals, and existing source bytes/OpenSim_Models/T13/user WIP are preserved.

## Verification

- `test_t66_writer_contract.py`: 14 positive/negative contract cases passed, including correction receipt/hash pinning, immutable assignment snapshots, typed bone-context validation, non-empty owned output root, wrong-owner and symlink rejection, output-collision rejection, multi-input aggregate-index distinction, and expected rejection of the actual E index mismatch.
- Existing `test_t66_parallel_protocol.py`: 8 cases passed against wave-2 schema.
- Actual D and E runner preflight: passed without authoring; the E aggregate package preflight: failed on the recorded `proposals.json` hash/size mismatch and wrote `e-aggregate-preflight.json`.
- No app bundle/geometry changed, so app tests/build/browser suite were not repeated. Existing action UI evidence is retained with its 825×807 viewport limitation.

## Acceptance

T66 remains `in_progress / partial`, with `nextUnit=author-and-integrate-normal-motion-bone-and-nerve`. W1-A/B/C, unit03, D and E still contain production-capable engineering work and unregistered candidates. This execution resolves writer contract defects but does not satisfy T66's authoring/registration responsibility. Product readiness and whole-body motion/content completeness remain partial. T85 is not handed off.
