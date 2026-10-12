# MV2 Q01 r1 — 2026-10-12

This run diagnoses and repairs only the bilateral rectus knee teaching assets. MV1's 220/74/332 completed observation inventory is reused. The other 32 mappings remain observed_ambiguous.

- Start: `start.json`, `start-status.z`; original authoring dependencies: `input-hashes.json` (50 matches).
- Diagnosis: `diagnosis-numeric.json`, `native-mask-left/right.png`, `pectoral-cause-comparison.json`.
- First candidate rejected: `left/right-candidate-r1` (20 dense face-orientation failure samples; not delivered).
- Final: `left/right-candidate-r2` (97 dense times per side; zero flipped faces/new bone-contained vertices; existing .1 area floor retained). Only node 47's 12 POSITION/NORMAL morph targets replaced. All original GLBs/authoring inputs retained.
- Final product: `atlas-data/assets/motion/mv2-q01-r1-{left,right}/motion.glb`; compact source-pinned repair manifest applies through the existing learner resolver and delivery plugin. No new renderer, camera policy or UI.
- Actual loader: `real-loader-validation.json`, `emitted-validation.json`; final Three.js world samples agree with independent Python replay. No physiological solver/natural contraction/measured attachment footprint claim.
- Actual UI: `paired-before-*`, `paired-after-right-*`, `after-left-max-settled`, `after-*-cycle-*`, `after-*-side-*`, restoration and LU9/area screenshots. `camera-comparison.json` verifies identical before/after camera and target. `cycle-review-*.png` contains six manually inspected representative frames per side; the 42+43 capture series is not a claim that every screenshot was manually inspected.
- `repair-queue.json` and `remaining-units.json` supersede only Q01's ambiguity. Historical MV1 data are unchanged.

Reproduce from repository root with the bundled Python runtime (NumPy/Pillow) and Node runtime. `diagnose.py` is read-only; `repair-r2.py` writes only this versioned directory. `register-repair.mjs` copies only the two new derived assets and repair manifest. `validate-loader.mjs` uses the real production loader/controller; `validate-emitted.py` compares its world samples. `build-owned.py r1` runs the package's 13 build checks with a separate ignored output root, leaving existing dist untouched.

The two source-addressed teaching landmarks (vertices 521 and 275 of each actual native overview surface) are AI-authored region controls. They are not anatomical point measurements. The wrong mid-belly moving mask and patella fixed-region assignment are corrected; native proximal source, topology, 19.5-degree pivot/range, LINEAR morph tracks and reverse action mapping stay intact. New free-region weights are relaxed once with the existing authorer's local shape rule. No contact vector corrective is added.

Next scheduled task: **AT22**, only after a new user request. Next separate repair unit if explicitly resumed: **MV1-Q02-left-external-oblique-lateral-layering**. Nothing auto-runs, pushes or deploys.
