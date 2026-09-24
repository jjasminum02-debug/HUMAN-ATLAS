# Atlas data schema and validator

`atlas.schema.json` defines HUMAN ATLAS data using JSON Schema Draft 2020-12. `validate.py` is a dependency-free validator for the keyword subset used by this schema. Before validating data it rejects unknown schema keywords, then applies structural checks and HUMAN ATLAS domain rules. This is a project validator, not a general-purpose implementation of every Draft 2020-12 feature.

Run from the project root:

```sh
python3 atlas-data/schemas/validate.py --check-schemas
python3 atlas-data/schemas/validate.py --fixtures
python3 atlas-data/schemas/validate.py --dataset path/to/atlas-dataset.json
```

`--fixtures` validates the schema and runs the indexed positive and negative examples. Each negative case passes only when the dataset is invalid and its expected diagnostic is present. The fixture index also asserts that only `individual_muscle` concepts count toward the individual-concept denominator; side instances, groups, parts, and model elements do not increase it.

The spatial contract records asset-native units/frame and annotation units/frame. A transform chain is required when they differ. For the T02 BodyParts3D source frame, conversion to the Atlas frame must encode `atlas[x,y,z]m = source[x,z,-y]mm / 1000`, the corresponding orientation-preserving rotation matrix, determinant `+1`, and a known-marker error within its recorded tolerance. Atlas world v1 is right-handed, +X patient-left, +Y head/superior, +Z anterior, in meters.

Fixture records are synthetic-only and live under `work/evidence/T03/fixtures/`; they are not anatomy data and must not be ingested into the learning catalog. Fixture review approvals deliberately exercise the data gate and do not represent real reviewers or anatomy approval. The validator checks that a record says it has current human approval, evidence, and a matching content hash. It cannot authenticate a person's identity or signature; production review access control remains a separate requirement. A missing Hani term stays null until it has evidence and current human review; this validator does not translate it.
