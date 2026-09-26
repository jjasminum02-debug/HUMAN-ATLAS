# Atlas data schema and validator

`atlas.schema.json` defines HUMAN ATLAS data using JSON Schema Draft 2020-12. `validate.py` is a dependency-free validator for the keyword subset used by this schema. Before validating data it rejects unknown schema keywords, then applies structural checks and HUMAN ATLAS domain rules. This is a project validator, not a general-purpose implementation of every Draft 2020-12 feature.

Run from the project root:

```sh
python3 atlas-data/schemas/validate.py --check-schemas
python3 atlas-data/schemas/validate.py --fixtures
python3 atlas-data/schemas/validate.py --dataset path/to/atlas-dataset.json
python3 atlas-data/schemas/validate_ai_evidence.py --check
python3 atlas-data/schemas/validate_ai_evidence.py --fixtures
python3 atlas-data/schemas/build_ai_evidence_overlay.py --check
```

`--fixtures` validates the schema and runs the indexed positive and negative examples. Each negative case passes only when the dataset is invalid and its expected diagnostic is present. The fixture index also asserts that only `individual_muscle` concepts count toward the individual-concept denominator; side instances, groups, parts, and model elements do not increase it.

The spatial contract records asset-native units/frame and annotation units/frame. A transform chain is required when they differ. For the T02 BodyParts3D source frame, conversion to the Atlas frame must encode `atlas[x,y,z]m = source[x,z,-y]mm / 1000`, the corresponding orientation-preserving rotation matrix, determinant `+1`, and a known-marker error within its recorded tolerance. Atlas world v1 is right-handed, +X patient-left, +Y head/superior, +Z anterior, in meters.

Fixture records are synthetic-only and live under `work/evidence/T03/fixtures/`; they are not anatomy data and must not be ingested into the learning catalog. Fixture review approvals deliberately exercise the data gate and do not represent real reviewers or anatomy approval. The validator checks that a record says it has current human approval, evidence, and a matching content hash. It cannot authenticate a person's identity or signature; production review access control remains a separate requirement. A missing Hani term stays null until it has evidence and current human review; this validator does not translate it.

## T16 field-level AI evidence overlay

`ai-evidence-overlay.schema.json` and `atlas-data/terminology/ai-evidence-overlay.json` are a separate learning evidence layer; they do not edit or replace T03 `Claim`, `Review`, or `reviewState` records. Each field row records its source work identity, edition/access state, locator, supported-value hash, and independent geometry/motion states. Cross-checking requires opened field evidence from at least two distinct `underlyingWorkId` values; two URLs that cite one book remain one underlying work.

The overlay schema intentionally has no writable `humanReviewed`, `reviewState`, reviewer, clinical-eligibility, or publication-approval field. Legacy migration carries an exact read-only snapshot of the prior summary/claim hashes and review references. New `single_source` claims require opened field text; index/abstract/metadata/fixture records do not qualify. The only un-opened exception is an exact `legacy_summary_migration` preview bound to its existing source and review hashes. Learner components consume `LearnerFieldProjection`, which contains text, plain-language caveats/comparisons, source links, and quiz eligibility but not internal status codes or authoring JSON.

The production `ai-evidence-overlay.json` is deliberately empty for T16. `build_ai_evidence_overlay.py --check` validates an in-memory migration preview against the same schema, canonical claim/evidence/source references, and exact legacy review/hash bindings without copying it into learner data. `--preview PATH` writes that preview only outside `atlas-data/terminology/`; it refuses a production-data destination. Synthetic contract fixtures are kept under `work/evidence/T16/fixtures/` and never enter the learning catalog.
