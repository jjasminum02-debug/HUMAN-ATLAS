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
- Default muscle label is Sino-Korean written in Hangul; keep pure-Korean, actual Hanja, English, and aliases in distinct sourced fields. Known web-attested names may be used as display/search overlays without granting human anatomy approval.
- Design documents may be revised for this expressly authorized T10 replan; subsequent tasks preserve them unless their scope warrants a documented amendment.
