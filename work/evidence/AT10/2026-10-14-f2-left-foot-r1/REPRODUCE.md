# F2 재현·검사

Working directory: `/Users/daniel/Downloads/SIM /HUMAN ATLAS`.
Python with numpy: `/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`.
Blender: `/Volumes/Blender/Blender.app/Contents/MacOS/Blender --background --factory-startup --disable-autoexec`.
Node: `/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node`.
No executable generator or Blender runtime is added to the web bundle.

The original OBJ/young target and dm→m conversion are already preserved in candidate.sourceVertices. Do not scale or transform them again. Current source identity, frame0 reference pose and hashes are in start.json and the final manifest. All source/native data is read-only. Use a fresh evidence/artifact directory for any future run, never overwrite the accepted files or historical evidence.

## Existing result replay

`work/tools/verify_at10_foot_fields.py` independently reads the source flow and every saved contact field, evaluates derivatives and finite differences, and compares actual float32 GLB positions. Inputs:

- `--evidence work/evidence/AT10/2026-10-14-f2-left-foot-r1`
- `--artifacts atlas-data/anatomy/skin/at10-f2-left-foot-r1`
- `--revision f2c3`
- `--initial-recipe work/evidence/AT10/2026-10-14-f2-left-foot-r1/recipe-f2c1.json`
- `--base-candidate work/evidence/AT10/2026-10-14-f1-correspondence-r2/candidates/fit-f1c7.json`

The tool writes only a QA result in evidence. For future independent replay copy the necessary candidate/recipe/contact JSON and GLB/mapping to fresh output directories, retaining the original source/base paths. Full body acquisition, Luna content work, r22 reproduction and F1 authoring must not be rerun.

## Authoring path used

1. `prepare_at10_foot_chain.py --evidence E --revision f2controls1 --side left --base-candidate [F1 final candidate JSON] --source-field-manifest work/evidence/AT10/2026-10-14-skin-fit-r5/initial-foot-fields-r31.json --native-supplement work/evidence/AT10/2026-10-14-skin-fit-r5/native-supplement-r1.json --controls-only` in Blender. Actual left native caps; nineteen toe helpers. No legacy cubic candidate is emitted.
2. `fit_at10_f1_correspondence.py --evidence E --revision f2c1 --side left --base-candidate [F1 final candidate JSON] --field-manifest E/surface-bands-f2controls1.json --body-controls E/left-body-controls.json --refine --centre-indicators`. Source/left native identity and unique section checks are explicit. `recipe-f2c1.json` is the authoritative solved flow; archived unused cubic metadata is not a positive-volume result.
3. `fit_at10_skin_contact.py` in Blender with `AT10_NATIVE_SUPPLEMENT=work/evidence/AT10/2026-10-14-skin-fit-r5/native-supplement-r1.json` and:
   - `--side left --unit foot --field-manifest E/contact-field-f2c1.json`
   - `--initial-candidate E/candidates/fit-f2c1.json --base-candidate [F1 final candidate JSON]`
   - `--reference-exceptions E/reference-exceptions-left-f2r1.json`
   - `--helper-mode bounded-soft --maximum-helper-drift .005 --floor-m .0005`
   - `--shape-target E/candidates/fit-f2c1.json --shape-weight 3 --jacobian-barriers --centers 240`
   - first `--revision f2c2 --steps 40`, then `--revision f2c3 --steps 220 --resume f2c2`. The latter stopped on geometry+margin acceptance at iteration167; 206 accepted stages total, not a time limit. Recipe data includes the complete resumed field sequence. Do not resample a deformed mesh or merely push its normals.
4. `export_at10_skin.py --revision f2c3` with `AT10_SKIN_EVIDENCE=E`, `AT10_SKIN_ARTIFACTS=A`. The emitter retains original face-corner UV/IDs/helpers and original topology, splitting only original UV seams.
5. `validate_at10_skin_blender.py -- f2c3` in Blender with E/A and the native supplement. This reads actual emitted float32 positions and all834 native references, saves exact raw addresses and all non-adjacent self pairs, and does not modify the candidate.
6. `scope-emitted-checks.py f2c3`, `check-emitted-margin.py`, source section identity, source-control interiority and field replay are read-only checks. Reference classification has its own addressed left evidence; raw counts are never replaced by policy counts.
7. `validate_at10_skin_loader.mjs f2c3` with E/A uses the same installed Three GLTFLoader. Existing DEV `?skinReview=1&skinCandidate=f2c3` uses SkinLayer in the same scene; click 피부 before changing region because the existing region route can remove DEV query flags. Confirm the actual loaded SHA, never the URL name alone. Actual app screenshots are required in addition to Blender checks.

## App/engineering checks

- `node --experimental-transform-types --test src/viewer/skin/skinRuntime.test.ts` in atlas-web (7 passed).
- `node node_modules/typescript/bin/tsc --noEmit` (passed).
- `node node_modules/vite/bin/vite.js build --outDir /private/tmp/at10-f2-dist --emptyOutDir` (passed; existing chunk-size warning retained). No broad learner data generator run; no DEV skin assets in production output.
- Exact local cost: GLB626576B, GPU625080B,26756tri; texture0,1material. Whole-delivery20MiB excess520699B is still the future R1 unit.
- Existing input/WIP hashes and non-owned EXECUTION records are checked separately at closure; sync_execution.py and --check run after the scoped merge.

F2 local acceptance does not register a product skin, move any acupoint, authorize a pose, approve public redistribution, or replace professor review.
