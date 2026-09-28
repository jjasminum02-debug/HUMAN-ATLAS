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
