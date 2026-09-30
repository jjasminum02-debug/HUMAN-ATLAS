> **현재 실행 기준:** `work/EXECUTION.json`과 `design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md`가 현재 순서·범위의 유일한 기준이다. 실행 전에 `work/NEXT.md`를 읽고, absorbed/retired task나 역사 evidence의 nextTask를 실행하지 않는다. 종료 시 EXECUTION의 해당 record를 갱신하고 `python3 work/tools/sync_execution.py` 및 `--check`를 수행한다. 원본/기존 WIP와 역사 evidence를 보존한다.

# HUMAN ATLAS project instructions

- Run one task ID per request. Read the start guide, runbook, status, task specification, relevant design sections, and the prior report before continuing. Stop after the requested task.
- Treat every design document and template as a plan until the corresponding artifact and validation exist. Keep task specifications, reports, source material, AI interpretation, technical checks, and human review distinct.
- Treat `OpenSim_Models/` as an immutable, read-only source checkout. Do not edit, transform in place, reset, update, switch branches, or change its embedded Git metadata. Put any future derived files elsewhere and record the source revision and hashes.
- Preserve existing project files and user changes. Only edit paths allowed by the active task. Keep local Git checkpoints limited to task-owned changes; do not push or deploy.
- Do not invent anatomy names, claims, coordinates, examination content, or source permissions. Record missing or conflicting evidence as unresolved.
- This is an educational anatomy project. Automated deployment, patient diagnosis, treatment, acupuncture simulation, and patient data are outside scope.

## T10 user-requested revision

- Follow revised T11–T24 in the runbook and individual work/tasks specifications. Original T10 mapping moved to T13. T00–T09 history stays unchanged.
- Learner UI must not expose task numbers, internal IDs, JSON exchange, or annotation authoring. Keep authoring in the development-only /review surface. Validation/conversion remain separate tools.
- Default muscle/bone label is Sino-Korean written in Hangul; required names are modern Korean, traditional Korean written in Hangul, and English. Actual Hanja characters are not a product requirement; preserve legacy evidence without collecting more Hanja. Known web-attested names may be used as display/search overlays without granting human anatomy approval.
- Design documents may be revised for this expressly authorized T10 replan; subsequent tasks preserve them unless their scope warrants a documented amendment.

## R12 user revision — 2026-09-26

- Read design/2026-09-25-muscle-atlas/06-REGION12-MUSCLE-BONE-REVISION.md first for changed requirements. Exactly 12 learner categories, no visible subcategory taxonomy; many-to-many membership; muscle and bone selection need typed cards. Preserve source taxonomy independently.
- T14b remains needs_human_review, but does not block independent T15a–g engineering. Never fabricate approval or surface geometry.
- Default implementation: Luna Max. T15b contract/migration and T15e scene lifecycle: Sol High, as user requested. No automatic delegation or next-task execution.
- After validation, commit only task-owned changes locally; inspect and preserve existing user changes, use partial staging when needed. Report hash, included scope, exclusions and remaining changes. No push/deploy without explicit request.
- Acupoints, nerve-based MPS/pain-hunting workflows and Pro mode are deferred; do not implement their UI, data or clinical logic now.

## R13 user revision — AI evidence and movement learning

- Read design/2026-09-25-muscle-atlas/07-AI-EVIDENCE-AND-MOTION-DESIGN.md, 08-SERIAL-ROADMAP-AND-GIT.md and 09-ATLAS-REFERENCE-RESEARCH.md. They supersede conflicting global human-review blockers and old T16–T24 plans. Preserve the T15a–g flow.
- AI should research, cross-check and write basic anatomy tables. Human review is an independent optional review record, not a mandatory gate for every educational name/origin/insertion/action. Never fabricate human approval, exact attachment surfaces, or motion assets.
- The user's summary documents are optional source material, not required manual homework. Keep private sources separate and do not upload them without authorization.
- Use distinct whole-number task IDs after T15; registry is work/task-registry-r13.json. Additional tasks receive unused IDs T41 onward with explicit queue links. A task number or design is never a completion claim.
- Implement educational muscle/bone movements only in their assigned tasks. Keep action text, clip support and human review separate. Default selected muscle focus fades other muscles with a reversible toggle. Main action label: 움직임으로 이해하기.
- Preserve stable IDs, frames and source assets. Future muscles need an animation-capable rig/adapter; do not fake contraction by scaling a static mesh. Acupoints, Pro mode, patient diagnosis and treatment remain deferred.

## R14 user revision — structure/function delivery first

- Read design/2026-09-25-muscle-atlas/10-STRUCTURE-FUNCTION-DELIVERY-PLAN.md, 11-TASK-PROMPTS-R14.md and 12-ASSESSMENT-ANIMATION-FUTURE.md. These supersede conflicting R13 display/queue/task-size requirements. Use work/task-registry-r14.json for future execution; preserve R13 as history.
- T23 is blocked per the user's final stop report. Preserve its uncommitted WIP. Next: T41 loader correction, then resume T23, then T42. Do not execute implementations during the R14 planning request.
- Remove citations/source disclosures/review-process text from learner origin/insertion and function content. Preserve source/evidence/hash internally. Keep required asset attribution in a separate app-info/license surface compliant with its license.
- Muscle and bone cards both show modern Korean, Sino-Korean written in Hangul, and English. No actual Hanja collection.
- Place 움직임으로 이해하기 prominently below names and above structure/function tabs. A supported button shows real body movement and synchronized explanation; absent assets remain unavailable, not synthetic anatomy.
- Prioritize structure/function delivery. Hide the assessment tab until separately authorized later implementation. T36/T37/T48/T49/T38 are deferred two-person examination education, not diagnosis/treatment.
- R14 permits a pre-frozen one-region/one-scene package with internal 5–10-item batches; general new-content tasks retain the default 10-concept bound. New rig/clip work stays separately bounded.
- New numbered tasks T41–T49 are reserved. Allocate additional unused IDs from T50 using the R14 registry. Required acceptance failures are partial/blocked, not hidden as complete_with_gaps.

## R15 user revision — continuous whole-body graphics, then nerves

- Read design/2026-09-25-muscle-atlas/13-CONTINUOUS-WHOLE-BODY-EXPERIENCE-R15.md, 14-TASK-PROMPTS-R15.md, 15-NERVE-AND-ASSESSMENT-SCOPE-R15.md and work/task-registry-r15.json. These supersede conflicting R14 fallback, sequence and assessment scope.
- T24 has a technical candidate but is blocked at the product gate. Next T50. T41/T23/T42/T43/T44 are historical completed work; do not repeat them based on stale R14 current-task snapshots.
- First create coherent whole-body bone/muscle graphics and the branded loading/home experience. Motion must animate the same selected muscle surface in the same learner viewport/model with camera, lighting and surrounding structures preserved. No separate model/black viewer/bone-path-only fallback as product completion.
- Single learner WebGL scene ownership; UI sends playback commands rather than spawning a separate anatomy scene. Whole-body visual coverage is separate from complete content or all-muscle motion coverage.
- Nerve educational layers/innervation/possible entrapment and site-specific findings are now planned after the first same-model motion, ahead of assessment. Use only the designated bounded tasks; no implementation during this planning request.
- No mandatory Pro split: layers plus progressive information disclosure. Peripheral sensory territories, dermatomes and traditional meridian regions remain distinct. Entrapment location must not automatically become a needling location/depth recommendation.
- Assessments start with a major-muscle/function shortlist and one test animation, not every muscle. Acupoint/meridian/intervention design remains deferred in T68. Patient diagnosis/treatment and needling simulation remain out of current implementation scope.
- T34 is audit-only; T35 planning-only; first bounded action expansion is T66. New T50–T68 are reserved; allocate subsequent unused numeric IDs from T69 and record explicit queue insertion.

## R15 ownership amendment — user-requested Astra UI implementation

- T51–T55: Luna Max; keep T50 source/frame/identity contracts and concentrate on acquisition/conversion/region assets. QA previews are allowed; final learner home/layout/loading/material/camera design belongs to T56–T58.
- T56–T58: Astra directly in the current conversation, as requested by the user. Read design/2026-09-25-muscle-atlas/16-ASTRA-UI-HANDOFF.md. Do not delegate or create another task automatically.
- T55 must leave actual asset paths, ID/node mapping, bounds/frame/units/side, load/size data, gaps and reproducible commands for T56. Stop after the requested task; T55 completion does not automatically authorize T56.
- Preserve in-progress T51 source-cache and evidence. Owner changes do not imply implementation completion or revoke existing work.

## 2026-09-29 T100 — user-authorized approval-state correction

- Read the T100 correction at the end of design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md. Historical `held_not_approved_by_this_task` means that task did not decide; it does not prohibit a later evidence-backed local-use decision.
- Keep source identity, local rendering/observation, semantic binding, optional human review and public redistribution independent. Public-release holds and `humanReview=not_performed` are not global local-development blockers.
- The assigned AI must resolve source-family rights and exception evidence and exact term/system/region/side/part correspondence within its task. Upstream FJ/TA2 IDs are not mandatory when the source has none; never fabricate them. A documented AI project crosswalk is distinct from provider identity and human approval.
- Preserve historical freezes. Apply current decisions through a versioned overlay, retain real per-object hard holds and user layer-off, and report genuine missing geometry/names honestly. Do not repeat approval-wait reports instead of performing the investigation.

## 2026-09-29 user-requested bulk-delivery amendment

- Follow design/2026-09-25-muscle-atlas/26-T100-BULK-DELIVERY-PLAN.md for current T100 execution and subsequent data-processing cadence. It supersedes mandatory ten-item stopping/repeated full-suite rules, not evidence or completion requirements.
- Batch is an internal recovery/review unit. Use one data-driven pipeline, bulk verified regular cases, and bounded review of real exceptions. Preserve historical scripts but do not add a runtime/test branch per batch.
- Separate compact learner runtime data from full development evidence; retain policy enforcement, source hashes, originals, user WIP and actual unresolved gaps. This amendment is planning, not implementation acceptance.
