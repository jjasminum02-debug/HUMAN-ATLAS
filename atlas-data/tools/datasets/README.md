# Local dataset compiler (T99)

This is a local technical pipeline, not learner-display or redistribution approval.

1. Run the already verified Blender 3.5 executable through the approved execution path:

   `/Volumes/Blender/Blender.app/Contents/MacOS/Blender --background --factory-startup --disable-autoexec --python atlas-data/tools/datasets/compile_za.py`

2. `python3 atlas-data/tools/datasets/build_za.py`
3. From `atlas-web`: `node --experimental-strip-types scripts/prepareDatasets.ts`
4. `python3 atlas-data/tools/datasets/validate.py`
5. From `atlas-web`: `node --experimental-strip-types --test src/viewer/datasets/*.test.ts scripts/delivery.test.ts`

Use the installed Node runtime if node is not on PATH. Do not acquire another Blender or rescan source identity/rights. An unavailable mounted executable requires restoring the verified runtime, not bypassing publisher checks.

## Boundaries

- `compile_za.py` is the source-specific Blender adapter. Exact object name/data/parent/collections and evaluated geometry hashes are checked against T98. It never saves the source. Local indexed geometry retains smoothing seams; a column-major instance matrix applies source world transform followed by `[x,z,-y]` exactly once. Units remain metres. This is not BP3D registration or rigging.
- `pack.py` is the common normalized resource/chunk compiler, with actual binary sizes, shared resources and content-addressed outputs. An oversized group is split; a single oversized resource is a failed unit. No surface is dropped.
- `build_za.py` preserves full source catalog, target overlays and exclusions offline. `prepareDatasets.ts` projects compact runtime records. Its BP3D adapter is an explicit **historical byte-preserving compatibility boundary**, preserving existing manifests/GLB bytes and the existing viewer. New data must not add a task-specific extension or branch. BP3D is not silently simplified or registered to ZA.
- The common local delivery registry supports namespaces from `index.json`. It validates frozen dependencies once per loaded snapshot and invalidates on source changes. Every delivered chunk is hash-checked. It has no production emission or preview hook.
- `DatasetResources` attaches to an existing root, with no renderer/camera. Source keys remain separate from shared geometry. Overview remains while detail is fetched; active triangle budget may retain overview when requested detail would exceed the limit. There is no promise that every muscle simultaneously renders at maximum detail.
- `ResourceQueue` uses byte-based LRU, wanted/pinned protection, bounded concurrent loads, aborts, late-result release and idempotent disposal. The default new dataset geometry limit is 96MiB. Encoded data is not retained in the queue; two concurrent requests each have an 8MiB chunk limit. This measures CPU arrays, not GPU memory or browser total memory.
- The learner app still uses BP3D. `/qa/t99.html` explicitly opts into local technical inspection only. Source-only, original hide flags, canonical nulls, rights and human-review state remain intact. T100 must decide eligible display/selection without treating this QA view as approval.

## Resume and reproducibility

Every object checkpoint records adapter/catalog fingerprint, exact name/key, per-LOD resource hash, transform and quality measurement. Valid units are reused; damaged/missing checkpoint/resources are re-evaluated; object failures are quarantined in `progress.json`, and whole compile is refused while failures remain. Partial output does not publish a complete manifest. Manifest replacement is atomic.

Blender normals/decimation re-evaluation was not bit-identical across fresh processes in this run (including a one-triangle overview difference). Never claim byte reproducibility of a fresh Blender evaluation. Original evaluated position/triangle hashes still match T98 exactly; each resulting LOD is measured against that source. Repacking the same frozen indexed checkpoints is byte-identical. Dataset revision includes actual resources/instances and compiler code so changed output cannot inherit an old revision. Historical cache files are not cleaned by this task.

LOD distance is a deterministic **sampled symmetric surface distance**, up to 192 vertices each direction, tolerance 0.15–2mm according to object size. It is not a guaranteed Hausdorff bound or anatomical/human approval. Detail retains all original evaluated triangles. The 960 surface instances are not 960 unique muscles: 509 muscle/part, 277 skeletal, 174 accessory. The 542 targets/563 memberships remain unresolved where T98 left them.
