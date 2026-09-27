# T44 ADR 001 — Coherent OpenSim right ankle input scene

Date: 2026-09-27. Decision: use a **separate Gait2392 rest-pose scene** for the first right tibialis anterior dorsiflexion input. This is a static production input candidate, not a motion clip or reviewed anatomy.

## Source and rights

- Exact source: `OpenSim_Models/Models/Gait2392_Simbody/gait2392_thelen2003muscle.osim`, `CustomJoint ankle_r`, `subtalar_r`, `mtp_r`, `Thelen2003Muscle tib_ant_r`, and its attached five ASCII VTP meshes. File hashes and body correspondence are in `joint-binding-t44.json`. Original files remain untouched.
- The `.osim` credits explicitly identify the contributors and CC BY 3.0. The [official Gait2392 model page](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53086215) describes the model's foot joints and skeletal representation. The [OpenSim model catalog](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53090607) lists Gait2392's model-level rights. The five VTP files contain no individual license notice; model-level CC BY 3.0 is recorded, with attribution retained. Verify individual geometry redistribution rights before public release.
- Existing T21 source link `T21-E-HA-M-000003-action-2` points to [Lim et al. 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10624435/), “Foot dorsiflexion and inversion” section. It supports the muscle/action context, not model geometry or an exact movement contribution. The action record remains `needs_review`.

## Coordinate and hierarchy decision

- The [OpenSim coordinate convention](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53090629) is +X anterior, +Y superior, +Z patient right. The **new scene frame** is +X patient left, +Y superior/head, +Z anterior, in metres. Source→scene is `(-z, y, x)`, the manifest's 4×4 column-major matrix (proper rotation, determinant +1, scale 1, translation 0). The origin is `tibia_r` body-local at q=0, **not** the existing BodyParts3D origin. All five meshes have `socket_frame=..`, scale `(1,1,1)` in the `.osim`; no model-specific mesh transform was omitted.
- No shared fiducials or compatible pose registration between BodyParts3D and Gait2392 were established. A zero residual here means only that OpenSim joint/path points are consistently transformed into their own scene. It is **not** a cross-model fit result. The source/scene frame IDs are intentionally distinct. The learner-facing switch copy for later UI integration is: “움직임 시범은 별도 OpenSim 모형으로 전환됩니다.” T44 preview displays the model change; learner UI wiring belongs to T25.
- In source `ankle_r`, parent `tibia_r_offset=(0,-0.43,0)` m, child `talus_r_offset=(0,0,0)`, default `ankle_angle_r=0` rad. The rotation1 axis is `(-0.10501355,-0.17402245,0.97912632)` in the joint frame; scene-axis transform is `(-0.97912632,-0.17402245,-0.10501355)`. `tibia_r` is fixed, and `talus_r` with `calcn_r` and `toes_r` is the moving subtree. The positive source rotation lifts an anterior lever by the axis cross-product; this direction interpretation is a model calculation, not a patient range claim.
- Rest positions in the source tibia frame: tibia `(0,0,0)`, talus `(0,-0.43,0)`, calcn `(-0.04877,-0.47195,0.00792)`, toes `(0.13003,-0.47395,0.009)` m. `subtalar_r` and `mtp_r` defaults also equal zero. Zero here is the model default, not a measured clinical neutral position.

## Model path and canonical boundary

- The OpenSim `tib_ant_r` GeometryPath has two `tibia_r`-local points and one `calcn_r`-local point. Their exact numbers and source/scene rest positions are in the manifest. The red GLB line is **an explanatory model path**. P1 and P3 are bone-local endpoints for later motion binding; they do not assert anatomical origin/insertion surfaces. No muscle deformation, force, clip, or exact attachment region was created.
- Migration `migrate_t44_ankle_joint.py` adds one right ankle joint ID, one right dorsiflexion joint-action relation to `HA-M-000003`, two source records, two evidence records, and one term. It preserves all prior catalog rows and review states; new action/term are `needs_review`. Existing bilateral T21 action is left untouched because it also includes inversion. No BodyParts3D FJ3385 talus identity is inferred.
- The GLB contains one embedded binary buffer, no external URI and no animation. It is a preparation input for T24; current production motion definitions/assets remain zero. T24 must test rotation/path behavior and three poses with the real model before any motion-ready status.

## Reproduction and quantitative checks

Run `python3 atlas-data/tools/build_t44_ankle_scene.py`, then `python3 atlas-data/tools/build_t44_ankle_scene.py --check` and `python3 atlas-data/tools/verify_t44_ankle_scene.py`. Only Python 3 standard library and checked-in sources are required. The manifest records generator version/script hash, six input hashes, output hash, source/scene frames, pivot/axis, body hierarchy, q=0 pose, and six landmark correspondences.

Six same-source landmark residuals are 0 m in double precision. Encoded GLB path float32 maximum deviation from manifest positions is `9.47e-9` m, below the `1e-6` m encoding tolerance. That tolerance is for deterministic coordinate serialization, **not** anatomical registration. `scene-validation.json` checks source-side names, expected geometry per body, hierarchy, self-contained GLB, and preservation of prior catalog entities. The browser preview showed the q=0 tibia/talus/foot/toes scene; console errors and warnings were absent.

For the same browser view, run `python3 atlas-data/tools/prepare_t44_preview.py`, then use the printed `python3 -m http.server ... --bind 127.0.0.1 --directory /private/tmp/t44-rest-preview-...` command and open `http://127.0.0.1:8764/`. The staging script copies only the HTML, existing Three.js modules and T44 GLB into a fresh temporary folder; it does not serve the repository or install software.
