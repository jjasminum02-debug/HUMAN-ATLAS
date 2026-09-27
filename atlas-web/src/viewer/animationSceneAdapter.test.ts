import assert from "node:assert/strict";
import test from "node:test";
import { AnimationMixer, Mesh, MeshBasicMaterial, Texture } from "three";
import type { MotionAsset } from "../domain/motionLearning.ts";
import { disposeAnimationScenes, loadAnimationScene, SUPPORTED_MOTION_FRAME } from "./animationSceneAdapter.ts";

const encoder = new TextEncoder();

function floats(values: number[]): Uint8Array {
  const bytes = new Uint8Array(values.length * 4);
  const view = new DataView(bytes.buffer);
  values.forEach((value, index) => view.setFloat32(index * 4, value, true));
  return bytes;
}

function uints(values: number[], bytesPerValue: 1 | 2): Uint8Array {
  const bytes = new Uint8Array(values.length * bytesPerValue);
  const view = new DataView(bytes.buffer);
  values.forEach((value, index) => bytesPerValue === 1
    ? view.setUint8(index, value)
    : view.setUint16(index * 2, value, true));
  return bytes;
}

type FixtureRepresentation = MotionAsset["representationType"];

/** In-memory synthetic GLB only. It is never written under atlas-data/assets or consumed by the learner. */
function syntheticGlb(representation: FixtureRepresentation = "rigged_mesh"): ArrayBuffer {
  const rigged = representation === "rigged_mesh";
  const hasPath = representation !== "rigged_mesh";
  const chunks: Uint8Array[] = [];
  let byteLength = 0;
  const bufferViews: Array<Record<string, number>> = [];
  const accessors: Array<Record<string, unknown>> = [];
  const add = (bytes: Uint8Array, target?: number): number => {
    while (byteLength % 4) { chunks.push(new Uint8Array([0])); byteLength += 1; }
    const offset = byteLength;
    chunks.push(bytes);
    byteLength += bytes.byteLength;
    const view: Record<string, number> = { buffer: 0, byteOffset: offset, byteLength: bytes.byteLength };
    if (target) view.target = target;
    bufferViews.push(view);
    return bufferViews.length - 1;
  };
  const accessor = (view: number, componentType: number, count: number, type: string, extra: Record<string, unknown> = {}) => {
    accessors.push({ bufferView: view, componentType, count, type, ...extra });
    return accessors.length - 1;
  };

  const position = accessor(add(floats([0, 0, 0, 0.1, 0, 0, 0, 0.1, 0]), 34962), 5126, 3, "VEC3", { min: [0, 0, 0], max: [0.1, 0.1, 0] });
  let joints: number | null = null;
  let weights: number | null = null;
  if (rigged) {
    joints = accessor(add(uints(Array(12).fill(0), 1), 34962), 5121, 3, "VEC4");
    weights = accessor(add(floats([1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]), 34962), 5126, 3, "VEC4");
  }
  const indices = accessor(add(uints([0, 1, 2], 2), 34963), 5123, 3, "SCALAR");
  let inverseBind: number | null = null;
  if (rigged) {
    inverseBind = accessor(add(floats([
      1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1,
      1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1,
    ])), 5126, 2, "MAT4");
  }
  const input = accessor(add(floats([0, 1])), 5126, 2, "SCALAR", { min: [0], max: [1] });
  const output = accessor(add(floats([0, 0, 0, 0, 0.25, 0])), 5126, 2, "VEC3");
  const pathOutput = hasPath ? accessor(add(floats([0, 0, 0, 0.125, 0, 0])), 5126, 2, "VEC3") : null;
  const json = {
    asset: { version: "2.0", generator: "HUMAN ATLAS T22 synthetic loader test" },
    scene: 0,
    scenes: [{ nodes: [0] }],
    nodes: [
      { name: "SyntheticRoot", children: hasPath ? [1, 3, 4] : [1, 3] },
      { name: "SyntheticSkeletonRoot", children: [2] },
      { name: "SyntheticBoneNode" },
      { name: "SyntheticSurface", mesh: 0, ...(rigged ? { skin: 0 } : {}) },
      ...(hasPath ? [{ name: "SyntheticPathNode" }] : []),
    ],
    meshes: [{ name: "SyntheticSurface", primitives: [{ attributes: {
      POSITION: position,
      ...(rigged ? { JOINTS_0: joints, WEIGHTS_0: weights } : {}),
    }, indices }] }],
    ...(rigged ? { skins: [{ name: "SyntheticRig", skeleton: 1, joints: [1, 2], inverseBindMatrices: inverseBind }] } : {}),
    animations: [{
      name: "SyntheticClip",
      samplers: [
        { input, output, interpolation: "LINEAR" },
        ...(hasPath ? [{ input, output: pathOutput, interpolation: "LINEAR" }] : []),
      ],
      channels: [
        { sampler: 0, target: { node: 2, path: "translation" } },
        ...(hasPath ? [{ sampler: 1, target: { node: 4, path: "translation" } }] : []),
      ],
    }],
    buffers: [{ byteLength }],
    bufferViews,
    accessors,
  };
  const jsonBytes = encoder.encode(JSON.stringify(json));
  const paddedJsonLength = Math.ceil(jsonBytes.length / 4) * 4;
  const jsonChunk = new Uint8Array(paddedJsonLength).fill(0x20);
  jsonChunk.set(jsonBytes);
  const binary = new Uint8Array(byteLength);
  let cursor = 0;
  for (const chunk of chunks) { binary.set(chunk, cursor); cursor += chunk.byteLength; }
  const paddedBinaryLength = Math.ceil(binary.length / 4) * 4;
  const binaryChunk = new Uint8Array(paddedBinaryLength);
  binaryChunk.set(binary);
  const totalLength = 12 + 8 + jsonChunk.byteLength + 8 + binaryChunk.byteLength;
  const glb = new Uint8Array(totalLength);
  const view = new DataView(glb.buffer);
  view.setUint32(0, 0x46546c67, true);
  view.setUint32(4, 2, true);
  view.setUint32(8, totalLength, true);
  view.setUint32(12, jsonChunk.byteLength, true);
  view.setUint32(16, 0x4e4f534a, true);
  glb.set(jsonChunk, 20);
  const binaryHeader = 20 + jsonChunk.byteLength;
  view.setUint32(binaryHeader, binaryChunk.byteLength, true);
  view.setUint32(binaryHeader + 4, 0x004e4942, true);
  glb.set(binaryChunk, binaryHeader + 8);
  return glb.buffer;
}

async function hash(buffer: ArrayBuffer): Promise<string> {
  const digest = await globalThis.crypto.subtle.digest("SHA-256", buffer);
  return [...new Uint8Array(digest)].map((value) => value.toString(16).padStart(2, "0")).join("");
}

async function assetFor(bytes: ArrayBuffer, representation: FixtureRepresentation = "rigged_mesh"): Promise<MotionAsset> {
  const rigged = representation === "rigged_mesh";
  const hasPath = representation !== "rigged_mesh";
  const combined = representation === "bone_motion_with_illustrative_path";
  return {
    id: `T22-SYNTHETIC-${representation.toUpperCase()}-ASSET`,
    motionDefinitionId: "T22-SYNTHETIC-DEFINITION",
    uri: "test-only://synthetic.glb",
    revision: "test-fixture-v1",
    sha256: await hash(bytes),
    sourceId: "TEST-ONLY-SOURCE",
    licenseId: "TEST-ONLY-LICENSE",
    representationType: representation,
    staticBinding: {
      sceneId: "TEST-ONLY-SCENE", sceneRevision: "test-scene-v1", modelId: "TEST-ONLY-MODEL",
      sourceAssetSha256: "a".repeat(64), frameId: SUPPORTED_MOTION_FRAME, units: "m", side: "right", referencePoseId: "TEST-REST-POSE",
    },
    rig: rigged || combined ? { id: "SyntheticRig", nodeBindings: [{ structureId: "SYNTHETIC-BONE", nodeId: "SyntheticBoneNode" }] } : null,
    illustration: hasPath ? { id: "SyntheticPath", trajectoryBindings: [{ structureId: combined ? "SYNTHETIC-MUSCLE-PATH" : "SYNTHETIC-PATH", trajectoryId: "SyntheticPathNode" }] } : null,
    clip: { id: "SyntheticClip", durationSeconds: 1, startPoseId: "TEST-REST-POSE", endPoseId: "TEST-END-POSE" },
    technicalStatus: "candidate",
  };
}

function editGlb(bytes: ArrayBuffer, edit: (document: any) => void): ArrayBuffer {
  const original = new DataView(bytes);
  const jsonLength = original.getUint32(12, true);
  const document = JSON.parse(new TextDecoder().decode(new Uint8Array(bytes, 20, jsonLength)));
  edit(document);
  const jsonBytes = encoder.encode(JSON.stringify(document));
  const paddedLength = Math.ceil(jsonBytes.length / 4) * 4;
  const binaryTail = new Uint8Array(bytes, 20 + jsonLength);
  const result = new Uint8Array(20 + paddedLength + binaryTail.byteLength);
  result.set(new Uint8Array(bytes, 0, 20));
  result.fill(0x20, 20, 20 + paddedLength);
  result.set(jsonBytes, 20);
  result.set(binaryTail, 20 + paddedLength);
  const view = new DataView(result.buffer);
  view.setUint32(8, result.byteLength, true);
  view.setUint32(12, paddedLength, true);
  return result.buffer;
}

test("GLTFLoader import keeps hierarchy, skin attributes, named node bindings and original clip tracks", async () => {
  const bytes = syntheticGlb("rigged_mesh");
  const asset = await assetFor(bytes);
  const loaded = await loadAnimationScene(bytes, asset);
  try {
    assert.equal(loaded.frameId, SUPPORTED_MOTION_FRAME);
    assert.equal(loaded.units, "m");
    assert.equal(loaded.representationType, "rigged_mesh");
    assert.equal(loaded.skinnedMeshCount, 1);
    assert.deepEqual(loaded.scene.scale.toArray(), [1, 1, 1]);
    const mesh = loaded.scene.getObjectByName("SyntheticSurface");
    assert.ok(mesh && (mesh as import("three").SkinnedMesh).isSkinnedMesh);
    const skinned = mesh as import("three").SkinnedMesh;
    assert.deepEqual(skinned.skeleton.bones.map((bone) => bone.name), ["SyntheticSkeletonRoot", "SyntheticBoneNode"]);
    assert.equal(skinned.geometry.getAttribute("skinIndex")?.count, skinned.geometry.getAttribute("position")?.count);
    assert.equal(loaded.rigNodes.get("SYNTHETIC-BONE")?.name, "SyntheticBoneNode");
    assert.equal(loaded.animations.length, 1);
    assert.equal(loaded.animations[0].name, "SyntheticClip");
    assert.equal(loaded.animations[0].tracks[0].name, "SyntheticBoneNode.position");
    assert.equal(loaded.animations[0].tracks[0].values[4], 0.25);

    const mixer = new AnimationMixer(loaded.scene);
    mixer.clipAction(loaded.animations[0]).play();
    mixer.setTime(0.5);
    assert.ok(Math.abs(loaded.rigNodes.get("SYNTHETIC-BONE")!.position.y - 0.125) < 1e-6);
    mixer.stopAllAction();
    mixer.uncacheRoot(loaded.scene);
  } finally {
    loaded.dispose();
  }
});

test("illustrative path remains a distinct unskinned representation", async () => {
  const bytes = syntheticGlb("illustrative_path");
  const loaded = await loadAnimationScene(bytes, await assetFor(bytes, "illustrative_path"));
  try {
    assert.equal(loaded.representationType, "illustrative_path");
    assert.equal(loaded.skinnedMeshCount, 0);
    assert.equal(loaded.pathNodes.get("SYNTHETIC-PATH")?.name, "SyntheticPathNode");
  } finally {
    loaded.dispose();
  }
});

test("bone motion plus illustrative path uses separate node and path bindings", async () => {
  const bytes = syntheticGlb("bone_motion_with_illustrative_path");
  const loaded = await loadAnimationScene(bytes, await assetFor(bytes, "bone_motion_with_illustrative_path"));
  try {
    assert.equal(loaded.representationType, "bone_motion_with_illustrative_path");
    assert.equal(loaded.skinnedMeshCount, 0);
    assert.equal(loaded.rigNodes.get("SYNTHETIC-BONE")?.name, "SyntheticBoneNode");
    assert.equal(loaded.pathNodes.get("SYNTHETIC-MUSCLE-PATH")?.name, "SyntheticPathNode");
    assert.deepEqual(loaded.animations[0].tracks.map((track) => track.name), ["SyntheticBoneNode.position", "SyntheticPathNode.position"]);
    const mixer = new AnimationMixer(loaded.scene);
    mixer.clipAction(loaded.animations[0]).play();
    mixer.setTime(0.5);
    assert.ok(Math.abs(loaded.rigNodes.get("SYNTHETIC-BONE")!.position.y - 0.125) < 1e-6);
    assert.ok(Math.abs(loaded.pathNodes.get("SYNTHETIC-MUSCLE-PATH")!.position.x - 0.0625) < 1e-6);
    mixer.stopAllAction();
    mixer.uncacheRoot(loaded.scene);
  } finally {
    loaded.dispose();
  }
});

test("frame, unit and source hash mismatch fail closed without rescaling", async () => {
  const bytes = syntheticGlb("rigged_mesh");
  const asset = await assetFor(bytes);
  await assert.rejects(loadAnimationScene(bytes, { ...asset, sha256: "0".repeat(64) }), /SHA-256/);
  await assert.rejects(loadAnimationScene(bytes, {
    ...asset,
    staticBinding: { ...asset.staticBinding, frameId: "UNSUPPORTED-FRAME" },
  }), /frame/);
  await assert.rejects(loadAnimationScene(bytes, {
    ...asset,
    staticBinding: { ...asset.staticBinding, units: "mm" as "m" },
  }), /단위는 m/);
});

test("missing node binding and clip mismatch are rejected", async () => {
  const bytes = syntheticGlb("rigged_mesh");
  const asset = await assetFor(bytes);
  await assert.rejects(loadAnimationScene(bytes, {
    ...asset,
    rig: { id: "SyntheticRig", nodeBindings: [{ structureId: "SYNTHETIC-BONE", nodeId: "MissingNode" }] },
  }), /node binding/);
  await assert.rejects(loadAnimationScene(bytes, {
    ...asset,
    clip: { ...asset.clip, id: "MissingClip" },
  }), /clip을 찾을 수/);
});

test("import bundle disposes shared geometry, material and texture once and is idempotent", async () => {
  const bytes = syntheticGlb("rigged_mesh");
  const loaded = await loadAnimationScene(bytes, await assetFor(bytes));
  const source = loaded.scene.getObjectByName("SyntheticSurface") as import("three").SkinnedMesh;
  const extra = new Mesh(source.geometry, source.material);
  loaded.scene.add(extra);
  const material = Array.isArray(source.material) ? source.material[0] : source.material;
  const texture = new Texture({ close() { closedBitmaps += 1; } } as unknown as HTMLImageElement);
  (material as MeshBasicMaterial).map = texture;
  let geometryDisposeCount = 0;
  let materialDisposeCount = 0;
  let textureDisposeCount = 0;
  let closedBitmaps = 0;
  source.geometry.addEventListener("dispose", () => geometryDisposeCount++);
  material.addEventListener("dispose", () => materialDisposeCount++);
  texture.addEventListener("dispose", () => textureDisposeCount++);
  loaded.dispose();
  loaded.dispose();
  assert.equal(geometryDisposeCount, 1);
  assert.equal(materialDisposeCount, 1);
  assert.equal(textureDisposeCount, 1);
  assert.equal(closedBitmaps, 1);
});

test("disposal helper deduplicates resources shared across independent roots", () => {
  const geometry = new Mesh().geometry;
  const material = new MeshBasicMaterial();
  const rootA = new Mesh(geometry, material);
  const rootB = new Mesh(geometry, material);
  let geometryDisposals = 0;
  let materialDisposals = 0;
  geometry.addEventListener("dispose", () => geometryDisposals++);
  material.addEventListener("dispose", () => materialDisposals++);
  disposeAnimationScenes([rootA, rootB]);
  assert.equal(geometryDisposals, 1);
  assert.equal(materialDisposals, 1);
});

test("off-scene rig and path bindings are rejected while the active single scene still loads", async () => {
  const representation = "bone_motion_with_illustrative_path";
  const original = syntheticGlb(representation);
  const bytes = editGlb(original, (document) => {
    document.nodes.push({ name: "OffSceneBone" }, { name: "OffScenePath" });
    document.scenes.push({ nodes: [document.nodes.length - 2, document.nodes.length - 1] });
  });
  const asset = await assetFor(bytes, representation);
  await assert.rejects(loadAnimationScene(bytes, {
    ...asset, rig: { ...asset.rig!, nodeBindings: [{ structureId: "SYNTHETIC-BONE", nodeId: "OffSceneBone" }] },
  }), /node binding/);
  await assert.rejects(loadAnimationScene(bytes, {
    ...asset, illustration: { ...asset.illustration!, trajectoryBindings: [{ structureId: "SYNTHETIC-MUSCLE-PATH", trajectoryId: "OffScenePath" }] },
  }), /path binding/);
  const loaded = await loadAnimationScene(bytes, asset);
  try { assert.equal(loaded.scene.getObjectByName("OffSceneBone"), undefined); }
  finally { loaded.dispose(); }
});

test("off-scene skin joints and clip targets cannot accompany the returned active scene", async () => {
  const skinBytes = editGlb(syntheticGlb("rigged_mesh"), (document) => {
    document.nodes[0].children = [3];
    document.scenes.push({ nodes: [1] });
    document.animations[0].channels[0].target.node = 3;
  });
  const skinAsset = await assetFor(skinBytes);
  await assert.rejects(loadAnimationScene(skinBytes, {
    ...skinAsset, rig: { ...skinAsset.rig!, nodeBindings: [{ structureId: "SYNTHETIC-BONE", nodeId: "SyntheticSurface" }] },
  }), /SkinnedMesh의 joint/);
  const trackBytes = editGlb(syntheticGlb("illustrative_path"), (document) => {
    document.nodes.push({ name: "OffSceneTrack" });
    document.scenes.push({ nodes: [document.nodes.length - 1] });
    document.animations[0].channels[0].target.node = document.nodes.length - 1;
  });
  await assert.rejects(loadAnimationScene(trackBytes, await assetFor(trackBytes, "illustrative_path")), /track target node가 active scene/);
});

test("external buffer and image URI are rejected before GLTFLoader can resolve them", async () => {
  for (const edit of [
    (document: any) => { document.buffers[0].uri = "https://example.invalid/external.bin"; },
    (document: any) => { document.images = [{ uri: "external.png" }]; },
    (document: any) => { document.images = [{ uri: "data:image/png;base64,AA==" }]; },
  ]) {
    const bytes = editGlb(syntheticGlb(), edit);
    await assert.rejects(loadAnimationScene(bytes, await assetFor(bytes), { basePath: "https://example.invalid/" }), /외부 buffer\/image URI/);
  }
});
