# ADR T20 — Muscle action and motion learning contract

- Status: accepted for the T20 technical contract; no anatomical content is approved.
- Date: 2026-09-27
- Scope: data contract, strict validation, typed runtime model, and a non-persistable legacy migration preview.

## Context

The existing canonical `JointAction` schema includes action wording, posture conditions, contraction role, optional task context/role, evidence IDs, and a review state. Its collection is empty in the current canonical catalog, and the catalog has no canonical `joint` structure kind. The six right-calf instances and static T12/T13 scenes exist, but no validated rig or motion clip exists. The existing AI evidence overlay has source-bound origin/insertion fields only; it contains no action or motion claims.

Changing the old record in place would risk reinterpreting its `reviewState`, breaking `Assessment.targetFunctionIds`, or turning an AI comparison into a human approval. Creating pilot actions or moving-bone claims without source-backed IDs would invent anatomy.

## Decision

1. Keep the T03 `JointAction` shape and assessment references unchanged. Store future actions and motion links in a separate `atlas-data/motion/motion-learning.json` bundle with its own JSON Schema.
2. A `MuscleAction` binds existing muscle/part IDs to field-level source claim/value hashes, evidence IDs, posture and stabilization conditions, and role assignments scoped to a named action context. Both functional role and contraction mode are stored per context so one muscle is not assigned one mode across unlike tasks. If a source-backed explanation exists before a canonical joint ID does, `jointBindingState=unmapped` plus an explicit reason permits text-only content without inventing an ID. Such a row cannot be used by a `MotionDefinition`. An empty stabilization list also needs a gap note. It has no `reviewState` or human approval field.
3. A `MotionDefinition` binds an action to an existing side-specific anatomical instance, moving bone IDs, fixed structure IDs, canonical joint IDs, a retained static scene revision/hash/frame/unit/reference pose, a distinct end pose, and evidence references for the pose range. It requires the action's canonical joint binding. Its initial pose must exactly match the static reference pose; this contract does not accept implicit retargeting or coordinate transforms.
4. A `MotionAsset` binds a registered source and license, local asset revision and SHA-256, representation type (`rigged_mesh` or `illustrative_path`), exact static frame/side/revision/pose, rig nodes or trajectory paths, and clip start/end pose IDs. `binding_verified` means the validator can establish technical compatibility only; it is not human review or educational release.
5. `MotionSession` is a TypeScript runtime state only. It is never part of persisted learning content. Text projection and technical clip compatibility are separate values; an action explanation without an asset remains text-only.
6. The existing `JointAction` migration is a deterministic preview only. It preserves source ID, source snapshot hash, exact original review state, and legacy evidence IDs separately; it is explicitly non-persistable and cannot create approval. The production JointAction collection has zero rows, so there is no real row to migrate.
7. All synthetic positive/negative records and the sentinel asset live under `work/evidence/T20/fixtures/`. Production motion content remains empty until sources, canonical joint IDs, compatible assets, and applicable review gates exist.

## Consequences

- A future task must add stable canonical joint records and source-backed action/pose claims before a production `MuscleAction` or `MotionDefinition` can pass.
- A real asset must be local, licensed, content-hash verified, and exactly bound to its definition. Missing asset, rig/trajectory binding, pose, side, model revision, or frame rejects the record.
- The current static reference frames and poses are not promoted to movement observations. No actual clip, learner playback UI, Pro extension, or anatomical content is supplied by T20.
- Legacy assessment IDs continue to reference the unchanged `JointAction` collection.

## Verification

See `work/evidence/T20/validation-results.json`, `motion-learning-tests.log`, `legacy-migration-tests.log`, `typecheck.log`, and `build.log`. The test-only fixture notice is in `work/evidence/T20/fixtures/README.md`.
