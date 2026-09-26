import {
  AnimationClip,
  BufferGeometry,
  Material,
  Object3D,
  PropertyBinding,
  Skeleton,
  SkinnedMesh,
  Texture,
} from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import type { MotionAsset } from "../domain/motionLearning.ts";

/** The only glTF frame currently compatible with the static calf pilot. */
export const SUPPORTED_MOTION_FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR";

export interface AnimationSceneLoadOptions {
  /** External resources are resolved relative to this URL. Bundled self-contained GLB is preferred. */
  basePath?: string;
  signal?: AbortSignal;
}

export interface AnimationSceneResource {
  readonly assetId: string;
  readonly revision: string;
  readonly uri: string;
  readonly sha256: string;
  readonly frameId: string;
  readonly units: "m";
  readonly representationType: MotionAsset["representationType"];
  /** Full imported tree; joints, skinned meshes, transforms and object names remain intact. */
  readonly scene: Object3D;
  readonly scenes: readonly Object3D[];
  /** Original clip objects from GLTFLoader; no tracks or durations are rewritten. */
  readonly animations: readonly AnimationClip[];
  readonly rigNodes: ReadonlyMap<string, Object3D>;
  readonly pathNodes: ReadonlyMap<string, Object3D>;
  readonly skinnedMeshCount: number;
  dispose(): void;
}

function abortError(): DOMException {
  return new DOMException("Animation asset loading cancelled", "AbortError");
}

async function sha256(buffer: ArrayBuffer): Promise<string> {
  if (!globalThis.crypto?.subtle) throw new Error("Web Crypto API가 없어 motion GLB hash를 확인할 수 없습니다.");
  const digest = await globalThis.crypto.subtle.digest("SHA-256", buffer);
  return [...new Uint8Array(digest)].map((value) => value.toString(16).padStart(2, "0")).join("");
}

function assertAssetContract(asset: MotionAsset): void {
  if (!asset.id || !asset.uri || !asset.revision || !/^[a-f0-9]{64}$/.test(asset.sha256)) {
    throw new Error("motion asset 식별자, revision, URI 또는 SHA-256이 유효하지 않습니다.");
  }
  if (asset.staticBinding.frameId !== SUPPORTED_MOTION_FRAME) {
    throw new Error(`지원하지 않는 motion frame입니다: ${asset.staticBinding.frameId}`);
  }
  // glTF 2.0 linear values are meters. Do not silently scale millimeter assets here.
  if (asset.staticBinding.units !== "m") throw new Error(`glTF motion asset 단위는 m이어야 합니다: ${asset.staticBinding.units}`);
  if (!Number.isFinite(asset.clip.durationSeconds) || asset.clip.durationSeconds <= 0) {
    throw new Error("motion clip duration은 양수여야 합니다.");
  }
  if (asset.representationType === "rigged_mesh") {
    if (!asset.rig || asset.illustration || asset.rig.nodeBindings.length === 0) {
      throw new Error("rigged_mesh는 rig node binding만 가져야 합니다.");
    }
  } else if (asset.representationType === "illustrative_path") {
    if (!asset.illustration || asset.rig || asset.illustration.trajectoryBindings.length === 0) {
      throw new Error("illustrative_path는 illustration trajectory binding만 가져야 합니다.");
    }
  } else if (!asset.rig || !asset.illustration || asset.rig.nodeBindings.length === 0 || asset.illustration.trajectoryBindings.length === 0) {
    throw new Error("bone_motion_with_illustrative_path는 뼈 node와 단순 경로 binding을 각각 가져야 합니다.");
  }
}

function collectNodes(scenes: readonly Object3D[]): { names: Map<string, Object3D>; duplicates: Set<string> } {
  const names = new Map<string, Object3D>();
  const duplicates = new Set<string>();
  for (const scene of scenes) scene.traverse((object) => {
    if (!object.name) return;
    if (names.has(object.name)) duplicates.add(object.name);
    else names.set(object.name, object);
  });
  return { names, duplicates };
}

function validateSkinnedMeshes(scenes: readonly Object3D[]): SkinnedMesh[] {
  const skinned: SkinnedMesh[] = [];
  const sceneObjects = new Set<Object3D>();
  for (const root of scenes) root.traverse((object) => sceneObjects.add(object));
  for (const root of scenes) root.traverse((object) => {
    if (!(object as SkinnedMesh).isSkinnedMesh) return;
    const mesh = object as SkinnedMesh;
    const joints = mesh.geometry.getAttribute("skinIndex");
    const weights = mesh.geometry.getAttribute("skinWeight");
    const positions = mesh.geometry.getAttribute("position");
    if (!mesh.skeleton || !joints || !weights || !positions || joints.count !== positions.count || weights.count !== positions.count) {
      throw new Error(`SkinnedMesh skin attribute 또는 skeleton이 불완전합니다: ${mesh.name || mesh.uuid}`);
    }
    if (mesh.skeleton.bones.length === 0 || mesh.skeleton.bones.some((bone) => !sceneObjects.has(bone))) {
      throw new Error(`SkinnedMesh의 joint가 로드된 scene tree에 없습니다: ${mesh.name || mesh.uuid}`);
    }
    skinned.push(mesh);
  });
  return skinned;
}

function collectTextures(value: unknown, textures: Set<Texture>, visited: Set<object>): void {
  if (!value || typeof value !== "object") return;
  if ((value as Texture).isTexture === true) {
    textures.add(value as Texture);
    return;
  }
  if (visited.has(value)) return;
  visited.add(value);
  if (Array.isArray(value)) {
    value.forEach((entry) => collectTextures(entry, textures, visited));
    return;
  }
  // Only inspect material-owned plain containers (e.g. shader uniforms), avoiding traversal into
  // renderer internals or arbitrary scene graph ownership.
  const prototype = Object.getPrototypeOf(value);
  if (prototype === Object.prototype || prototype === null) {
    Object.values(value).forEach((entry) => collectTextures(entry, textures, visited));
  }
}

/** Disposes each resource owned by the imported glTF exactly once, even when meshes share it. */
export function disposeAnimationScenes(scenes: readonly Object3D[]): void {
  const geometries = new Set<BufferGeometry>();
  const materials = new Set<Material>();
  const textures = new Set<Texture>();
  const skeletons = new Set<Skeleton>();
  const visitedValues = new Set<object>();
  const bitmaps = new Set<object>();

  for (const root of scenes) root.traverse((object) => {
    const mesh = object as Object3D & { geometry?: BufferGeometry; material?: Material | Material[]; skeleton?: Skeleton };
    if (mesh.geometry?.isBufferGeometry) geometries.add(mesh.geometry);
    if (mesh.skeleton) skeletons.add(mesh.skeleton);
    const materialRows = Array.isArray(mesh.material) ? mesh.material : mesh.material ? [mesh.material] : [];
    for (const material of materialRows) {
      materials.add(material);
      Object.values(material).forEach((value) => collectTextures(value, textures, visitedValues));
    }
  });

  for (const texture of textures) {
    const image = texture.image as unknown;
    if (image && typeof image === "object" && "close" in image && typeof (image as { close?: unknown }).close === "function") {
      if (!bitmaps.has(image)) {
        bitmaps.add(image);
        (image as { close: () => void }).close();
      }
    }
    texture.dispose();
  }
  geometries.forEach((geometry) => geometry.dispose());
  materials.forEach((material) => material.dispose());
  skeletons.forEach((skeleton) => skeleton.dispose());
  scenes.forEach((scene) => scene.removeFromParent());
}

/**
 * Parses a source-hash-verified GLB through Three.js's animation-capable path.
 * It is intentionally independent from the static T07 decoder and does not create an AnimationMixer.
 */
export async function loadAnimationScene(
  bytes: ArrayBuffer,
  asset: MotionAsset,
  options: AnimationSceneLoadOptions = {},
): Promise<AnimationSceneResource> {
  assertAssetContract(asset);
  if (options.signal?.aborted) throw abortError();
  if (await sha256(bytes) !== asset.sha256) throw new Error(`motion GLB SHA-256이 manifest와 다릅니다: ${asset.id}`);
  if (options.signal?.aborted) throw abortError();

  const loader = new GLTFLoader();
  const gltf = await loader.parseAsync(bytes, options.basePath ?? "");
  const scenes = gltf.scenes.length ? gltf.scenes : [gltf.scene];
  try {
    if (options.signal?.aborted) throw abortError();
    if (gltf.animations.length === 0) throw new Error(`motion asset에 animation clip이 없습니다: ${asset.id}`);

    const clip = gltf.animations.find((candidate) => candidate.name === asset.clip.id);
    if (!clip) throw new Error(`manifest clip을 찾을 수 없습니다: ${asset.clip.id}`);
    if (Math.abs(clip.duration - asset.clip.durationSeconds) > 1e-4) {
      throw new Error(`manifest와 GLB clip duration이 다릅니다: ${asset.clip.durationSeconds} != ${clip.duration}`);
    }

    const { names, duplicates } = collectNodes(scenes);
    const rigBindings = asset.rig?.nodeBindings ?? [];
    const pathBindings = asset.illustration?.trajectoryBindings.map(({ structureId, trajectoryId }) => ({ structureId, nodeId: trajectoryId })) ?? [];
    const allStructureIds = [...rigBindings.map((row) => row.structureId), ...pathBindings.map((row) => row.structureId)];
    if (new Set(allStructureIds).size !== allStructureIds.length) throw new Error("rig와 path structure binding이 겹칩니다.");
    const allNodeIds = [...rigBindings.map((row) => row.nodeId), ...pathBindings.map((row) => row.nodeId)];
    if (new Set(allNodeIds).size !== allNodeIds.length) throw new Error("rig와 path node binding이 겹칩니다.");
    const rigNodes = new Map<string, Object3D>();
    const pathNodes = new Map<string, Object3D>();
    for (const binding of rigBindings) {
      if (duplicates.has(binding.nodeId)) throw new Error(`glTF node 이름이 중복되어 binding이 모호합니다: ${binding.nodeId}`);
      const node = names.get(binding.nodeId);
      if (!node) throw new Error(`manifest node binding을 찾을 수 없습니다: ${binding.nodeId}`);
      if (rigNodes.has(binding.structureId)) throw new Error(`structure binding이 중복되었습니다: ${binding.structureId}`);
      rigNodes.set(binding.structureId, node);
    }
    for (const binding of pathBindings) {
      if (duplicates.has(binding.nodeId)) throw new Error(`glTF node 이름이 중복되어 path binding이 모호합니다: ${binding.nodeId}`);
      const node = names.get(binding.nodeId);
      if (!node) throw new Error(`manifest path binding을 찾을 수 없습니다: ${binding.nodeId}`);
      if (pathNodes.has(binding.structureId)) throw new Error(`path structure binding이 중복되었습니다: ${binding.structureId}`);
      pathNodes.set(binding.structureId, node);
    }

    for (const track of clip.tracks) {
      const { nodeName } = PropertyBinding.parseTrackName(track.name);
      if (!PropertyBinding.findNode(gltf.scene, nodeName)) throw new Error(`animation track target node가 scene에 없습니다: ${track.name}`);
    }

    const skinnedMeshes = validateSkinnedMeshes(scenes);
    if (asset.representationType === "rigged_mesh" && skinnedMeshes.length === 0) {
      throw new Error("rigged_mesh manifest인데 GLB에 유효한 SkinnedMesh가 없습니다.");
    }
    if (asset.representationType !== "rigged_mesh" && skinnedMeshes.length > 0) {
      throw new Error("bone/path 표현은 수축 조직 SkinnedMesh를 포함하지 않아야 합니다.");
    }

    let disposed = false;
    return {
      assetId: asset.id,
      revision: asset.revision,
      uri: asset.uri,
      sha256: asset.sha256,
      frameId: asset.staticBinding.frameId,
      units: "m",
      representationType: asset.representationType,
      scene: gltf.scene,
      scenes,
      animations: gltf.animations,
      rigNodes,
      pathNodes,
      skinnedMeshCount: skinnedMeshes.length,
      dispose: () => {
        if (disposed) return;
        disposed = true;
        disposeAnimationScenes(scenes);
      },
    };
  } catch (error) {
    disposeAnimationScenes(scenes);
    throw error;
  }
}
