# T100 parallel A/B/C integration — 2026-09-30

## Scope and decision

Reviewed the frozen run `T100-parallel-resolution-2026-09-30-r1` and worker A/B/C outputs against the recorded run manifest and the shared T96/TA2/source inputs. Applied only the independently supported subset through `apply_supported_integration.py`; did not run the prior bulk resolver's apply path. The production overlay is validated by the common TypeScript dataset/integration builder and strict whole-body tests.

| Item | Decision | Applied effect | Boundary retained |
|---|---|---|---|
| TA2:1512, distal phalanx of foot | Accept bounded class-member relations | Ten source surfaces have explicit distal level, toe ordinal and `.l`/`.r`; added ten `verified_class_member` relations with distinct `distal:{ordinal}:{side}` codes. | Existing generic TA2:1505 relations remain. TA2:1512 source cardinality and full group extent are not asserted; these are ten member routes, not evidence of complete coverage. |
| TA2:2196, posterior cricoarytenoid | Accept exact frozen-source crosswalk | Added two side-specific relations for the source objects named “Posterior crico-arytenoid muscle.l/r”. T96's English string has a spelling discrepancy; frozen TA2 2.07 entry `#/id=2196` has exact `en_GB` “posterior crico-arytenoid muscle”, the same Latin target, and parent 2192. Source parent and collections place both objects in laryngeal muscles. | Similar arytenoid/laryngeal objects were excluded. Existing ancestor links were not rewritten. No canonical HA binding, completeness, or human approval was added. |
| TA2:2261, iliocostalis colli | Keep unresolved | No overlay change. The exact-name unsided object and the right-side object remain `side_conflicted`, `conceptKey=null`. | Target remains outside the 135-member A/B unresolved assignment and contributes to the whole-scope unrouted count. No side or binding inferred. |
| TA2:1255, trapezium bone | Accept direct modern field only | Added `큰마름뼈` to the internal term evidence from opened NIKL record 565982 (English translation “trapezium bone”; collection period 1998–2008). | Existing traditional `대능형골` evidence retained; no learner-facing alias, canonical binding or Hanja added. |
| TA2:2481, flexor carpi radialis | Accept two direct Korean fields | Added modern `노쪽손목굽힘근` and traditional `요 수근 굴근` from the opened KSES page 60 exact row. | The displayed edition columns are named but publication years are not exposed. Internal terminology evidence only. |
| TA2:2056, TA2:2532 | Do not promote AI-only modern suggestions | Existing traditional evidence retained; AI suggestions `이마근` and `손 벌레근` remain unpromoted. | Modern target fields remain missing; suggestions are not source citations or human review. |
| TA2:1253, triquetrum | Keep unresolved | No Korean field applied. | KMLE portal's “Triquetral bone” synonym headword and old-term results are not an exact match to the pinned “triquetrum bone” row; historical candidates conflict (`삼각골`/`삼각근`). Underlying records were not opened. |

## Current counts and preserved state

The final overlay contains 542 targets, 563 target-region memberships and 12 regions; 960 source objects; 130 pre-existing HA bindings; 830 source-only rows; all 960 rows remain public-redistribution `held` and human-review `not_performed`. The historical 163 classification remains 6 exact-label observations, 20 descendant surfaces, 135 ancestor/group surfaces and 2 frozen-hierarchy non-observations. No geometry or new canonical HA bindings were added.

The common runtime projection and final overlay yield selectable paths for **408/542 target IDs** (134 without any path) and **426/563 memberships** (137 without a path). Relation-kind target counts overlap: normalized exact 279, class member 18, taxonomy member 102, source crosswalk 10; their distinct-target union is 408. These are route counts, not visual acceptance. They correct the prior current-scope 407 target figure; the old 406 observation and 407 statement remain preserved in historical reconciliation evidence.

The 135-target A/B continuation subset falls to 133 unresolved after accepting TA2:1512 and TA2:2196. This differs from the whole-scope 134 target IDs without a selectable route because TA2:2261 is a separately held conflict. The earlier broader 166-target remainder and the 31 partial-member additions remain historical scope evidence; no historical file was rewritten.

Within C's 75 assigned term rows, 73 still have at least one Korean field gap (73 modern, 71 traditional); no Hanja was collected. This only updates the internal evidence ledger. Exact-term work, 12-region route cycles and performance measurements were not repeated.

## Validation

- `pnpm run test:whole-body`: passed, 51/51.
- `pnpm run test:delivery`: passed, 3/3.
- `pnpm run typecheck`: passed.
- `pnpm run build`: passed; existing production chunk-size warning (>500 kB) remains.
- Runtime QA baseline: produced through the same `buildRuntimeIntegration` and dataset validator used by the Vite endpoint; overlay SHA-256 `4a11f7235a1956a31958a5dc647dac243e44e2c52f79afb33e7102f70329da71`; projected JSON SHA-256 `ce5dfa8d63798e2bfa5d8710a2f6ffb5d9fb048327e7b002d69cdb8e151b13db`, 889,304 bytes.
- Browser visual selection remains pending. The local dev-server listen attempt returned sandbox `EPERM`; no screenshot, console-clean state or exhaustive visual pass is claimed. Existing localized browser samples are not promoted to this integration's visual acceptance.
- Active-scene performance was not remeasured; prior readings remain tied to their recorded overlay revision.

## Files

- `integration-decisions.json`: accepted/held decisions and policy invariants.
- `integration-validation.json`: shared validator, route count and verification results.
- `qa-baseline.json`: final overlay/runtime/relevant input hashes and all 563 target-region route rows.
- `browser-validation.json`: explicit pending visual QA boundary.
- `apply_supported_integration.py`, `build_qa_baseline.mjs`: reproducible bounded integration and QA-baseline builders.

T100 remains `in_progress / partial`; `nextUnit=resolve-target-representation-and-final-scene-qa`. Remaining work includes 133 unresolved A/B target scopes plus separate TA2:2261 conflict, 73 Korean term-evidence gap rows, 134 target IDs and 137 memberships without an exact selectable route, and exhaustive localized visual selection QA. No next task was started.
