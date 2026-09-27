# T50 shared learner scene contract

**Status:** architecture decision only; no learner-scene implementation in T50.\
**Preferred static basis:** BodyParts3D Release 4.0, provisional shared reference geometry.\
**Motion readiness:** not ready. T24/T44 OpenSim artifacts remain separate regression/reference assets until a future, evidence-backed registration or a single-source motion package exists.

## One renderer and one anatomical root

- The learner owns exactly one `WebGLRenderer`, one `Scene`, and one persistent `AnatomySceneRoot` for the selected body model. Region navigation, muscle/bone selection, layer visibility, and motion are commands against this scene. They must not mount a second viewport or replace the body with a demonstration model.
- `AnatomySceneRoot` contains the body model's immutable source/reference geometry and typed scene nodes. A model revision change replaces the root contents through one scene controller while retaining the renderer, canvas, camera, lights, and controls.
- `SceneController` owns the renderer, canvas sizing, camera/OrbitControls, lights, shared material policy, one root, source/model revision, `canonicalId → instanceId → stable node path` bindings, base pose snapshot, layer visibility, pickability, selection, current motion session, resource cache, abort state, and GPU disposal.
- UI components own neither a renderer nor a scene. They dispatch typed selection/layer/pose/motion commands and render learner cards from the same selected canonical ID.

## Binding and source integrity

- Every selectable ID resolves through an explicit versioned binding row: canonical ID, source ID and version, source file/entry ID, source hash, scene revision/hash, laterality, coordinate frame, unit, reference pose ID, instance ID, and stable node path. Names or fuzzy substring matching never create bindings.
- A node can host one or more representation meshes only where the manifest says so; canonical concepts, source file IDs, scene nodes, and mesh IDs remain distinct.
- The source/reference pose is immutable baseline geometry. Runtime state is a separate transform/morph layer with reversible deltas and an exact reset to the baseline. A pose change must not silently reset camera, selection, or layer state.
- Attachments and motion channels require source-backed anatomy claims and human review as required by their own gates. Missing identity, side, pose, frame, pivot, or topology is a held state, not an inferred value.

## Single ownership of pose, layers, selection, and session

- `PoseController` owns base/current pose revision and its reversible node transforms/vertex deltas. It must never scale an entire muscle uniformly as the motion representation.
- `LayerController` owns per-node visibility, opacity/material treatment, and pickability. Hiding a layer changes presentation only; it does not substitute for a contraction or joint movement.
- `SelectionController` owns the active typed canonical selection and node set. Route state, outline/highlight, and learner card derive from this state, not separate component-local flags.
- `MotionSessionController` owns one active session, one clock/RAF loop, one clip binding, and cancellation/disposal. It updates mapped muscle surface deformation and/or mapped skeletal transforms within the same `AnatomySceneRoot`. It cannot load a second demo scene.
- `LearnerSessionState` is the serializable owner of route, selected ID, camera intent, visible layers, current pose/clip/time and pause state. No authoring draft is promoted by playback.

## Camera, lighting, and materials

- Camera and controls live outside the model root and persist across region/selection changes; a deliberate “frame selection” command is distinct from “reset pose.”
- One shared hemisphere/key/fill lighting rig and a small semantic material palette are applied at the renderer/scene layer. Selected-object emphasis is an overlay/material state, never a duplicate viewport.
- Scene background, exposure, tone mapping, color space, and clipping planes are set once by the scene controller. Region packages cannot create a black canvas or their own renderer.

## T50 evidence limits and next work

T50's private browser spike proves only that the current BodyParts3D GLB can be displayed under one root and that localized vertex-buffer edits plus a reversible matrix/pivot transform can execute in one renderer. The displacement weights and the talus pivot are deliberately synthetic. They do not establish muscle anatomy, attachments, joint centers, an animation, a product demo, or a reviewed model. Production deformation requires surface segmentation/identity, source-backed attachment/joint constraints, topology-safe per-vertex weights or reviewed deformation bases, validated pose/frame/pivot data, and same-root browser QA. T51 must inventory and selectively acquire a coherent whole-body Release 4.0 package, verify IDs/sides/rights/hashes and frame/pose, quantify unsupported anatomy, and determine whether the archive meshes can support the needed product fidelity before any learner scene is integrated.
