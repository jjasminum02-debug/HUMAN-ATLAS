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
import { DATASET_BUDGET } from "./datasets/schema.ts";

/** Explicitly retained, source-specific motion frames. No cross-frame alignment is implied. */
export const SUPPORTED_MOTION_FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR";
export const SUPPORTED_MOTION_FRAMES = new Set([
  SUPPORTED_MOTION_FRAME,
  "HA_OSIM_GAIT2392_TIBIA_LOCAL_XLEFT_YHEAD_ZANTERIOR_M",
]);

export interface AnimationSceneLoadOptions {
  /** Retained for caller compatibility; external GLB dependencies are never resolved. */
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
  /** SourceKey-to-node map for the current-scene surface binding contract. */
  readonly sourceNodes: ReadonlyMap<string, Object3D>;
  readonly skinnedMeshCount: number;
  readonly morphMeshCount: number;
  /** Conservative active-memory estimate: fetched GLB plus geometry and animation buffers. */
  readonly memoryEstimateBytes: number;
  readonly geometryBytes: number;
  readonly animationBytes: number;
  readonly sourceBytes: number;
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
  if (!SUPPORTED_MOTION_FRAMES.has(asset.staticBinding.frameId)) {
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
  } else if (asset.representationType === "source_bound_surface") {
    const binding = asset.sourceBinding;
    if (!binding || !["t59-source-motion-binding-v1", "t66-typed-source-motion-v2"].includes(binding.contractVersion) || binding.members.length === 0
      || !binding.datasetNamespace || !binding.datasetRevision || !binding.integrationRevision
      || !/^[a-f0-9]{64}$/.test(binding.sourceOverlaySha256)
      || !binding.subjectSourceKey
      || binding.frameId !== SUPPORTED_MOTION_FRAME || binding.frameId !== asset.staticBinding.frameId
      || binding.units !== "m" || binding.units !== asset.staticBinding.units
      || binding.referencePoseId !== asset.staticBinding.referencePoseId
      || !["morph_targets", "skinning", "morph_and_skinning"].includes(binding.deformation)) {
      throw new Error("source_bound_surface는 정확한 현재 scene/source/pose 결속이 필요합니다.");
    }
    const sourceKeys = binding.members.map((row) => row.sourceKey);
    const nodeIds = binding.members.map((row) => row.nodeId);
    if (new Set(sourceKeys).size !== sourceKeys.length || new Set(nodeIds).size !== nodeIds.length
      || binding.members.some((row) => !row.sourceKey || !row.nodeId || !row.sourceNamespace || !row.resourceKey
        || !["deforming_muscle_surface", "deforming_passive_surface", "moving_structure", "co_moving_context", "fixed_structure", "passive_context"].includes(row.role)
        || !/^[a-f0-9]{64}$/.test(row.sourceChunkSha256) || !/^[a-f0-9]{64}$/.test(row.geometrySha256)
        || row.instanceMatrix.length !== 16 || !row.instanceMatrix.every(Number.isFinite))) {
      throw new Error("source_bound_surface의 source instance binding이 유효하지 않습니다.");
    }
    const subjectRoles = binding.subjectKind === "bone"
      ? new Set(["moving_structure", "fixed_structure"])
      : new Set(["deforming_muscle_surface", "deforming_passive_surface"]);
    if (!binding.members.some((row) => subjectRoles.has(row.role) && row.sourceKey === binding.subjectSourceKey
      && row.side === asset.staticBinding.side)) {
      throw new Error("source_bound_surface에 선택된 source instance와 일치하는 같은 쪽 변형 표면 또는 관절 구조가 없습니다.");
    }
    if (asset.illustration) throw new Error("source_bound_surface는 별도 경로 illustration을 허용하지 않습니다.");
  } else if (!asset.rig || !asset.illustration || asset.rig.nodeBindings.length === 0 || asset.illustration.trajectoryBindings.length === 0) {
    throw new Error("bone_motion_with_illustrative_path는 뼈 node와 단순 경로 binding을 각각 가져야 합니다.");
  }
}

function collectNodes(scene: Object3D): { names: Map<string, Object3D>; duplicates: Set<string> } {
  const names = new Map<string, Object3D>();
  const duplicates = new Set<string>();
  scene.traverse((object) => {
    if (!object.name) return;
    if (names.has(object.name)) duplicates.add(object.name);
    else names.set(object.name, object);
  });
  return { names, duplicates };
}

function validateSkinnedMeshes(scene: Object3D): SkinnedMesh[] {
  const skinned: SkinnedMesh[] = [];
  const sceneObjects = new Set<Object3D>();
  scene.traverse((object) => sceneObjects.add(object));
  scene.traverse((object) => {
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

function estimateAnimationBytes(scene: Object3D, clips: readonly AnimationClip[], sourceBytes: number) {
  const geometryBuffers = new Set<ArrayBufferLike>();
  const geometryViews = new Set<BufferGeometry>();
  let skeletonBytes = 0;
  scene.traverse((object) => {
    const mesh = object as Object3D & { geometry?: BufferGeometry; skeleton?: Skeleton };
    if (!mesh.geometry?.isBufferGeometry || geometryViews.has(mesh.geometry)) return;
    geometryViews.add(mesh.geometry);
    for (const attribute of Object.values(mesh.geometry.attributes)) geometryBuffers.add(attribute.array.buffer);
    for (const attributes of Object.values(mesh.geometry.morphAttributes)) for (const attribute of attributes) geometryBuffers.add(attribute.array.buffer);
    if (mesh.geometry.index) geometryBuffers.add(mesh.geometry.index.array.buffer);
    skeletonBytes += (mesh.skeleton?.boneInverses ?? []).reduce((sum, inverse) => sum + inverse.elements.length * 4, 0);
  });
  const geometryBytes = [...geometryBuffers].reduce((sum, buffer) => sum + buffer.byteLength, 0) + skeletonBytes;
  const trackBuffers = new Set<ArrayBufferLike>();
  for (const clip of clips) for (const track of clip.tracks) {
    trackBuffers.add(track.times.buffer);
    trackBuffers.add(track.values.buffer);
  }
  const animationBytes = [...trackBuffers].reduce((sum, buffer) => sum + buffer.byteLength, 0);
  return { sourceBytes, geometryBytes, animationBytes, memoryEstimateBytes: sourceBytes + geometryBytes + animationBytes };
}

/** Inspect the GLB container before GLTFLoader can resolve a URI or issue a request. */
function assertSelfContainedGlb(bytes: ArrayBuffer): void {
  if (bytes.byteLength < 20) throw new Error("motion 입력은 self-contained GLB여야 합니다.");
  const view = new DataView(bytes);
  if (view.getUint32(0, true) !== 0x46546c67 || view.getUint32(4, true) !== 2 ||
      view.getUint32(8, true) !== bytes.byteLength || view.getUint32(16, true) !== 0x4e4f534a) {
    throw new Error("motion 입력은 유효한 GLB 2.0이어야 합니다.");
  }
  const jsonLength = view.getUint32(12, true);
  if (jsonLength === 0 || jsonLength > bytes.byteLength - 20) throw new Error("GLB JSON chunk가 유효하지 않습니다.");
  let document: { buffers?: Array<{ uri?: unknown }>; images?: Array<{ uri?: unknown }> };
  try {
    document = JSON.parse(new TextDecoder().decode(new Uint8Array(bytes, 20, jsonLength)));
  } catch {
    throw new Error("GLB JSON chunk를 읽을 수 없습니다.");
  }
  if (!document || !Array.isArray(document.buffers) || document.buffers.length !== 1 ||
      document.buffers.some((buffer) => !buffer || buffer.uri !== undefined) ||
      (document.images !== undefined && (!Array.isArray(document.images) || document.images.some((image) => !image || image.uri !== undefined)))) {
    throw new Error("motion GLB의 외부 buffer/image URI는 허용하지 않습니다.");
  }
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
  if (bytes.byteLength > DATASET_BUDGET.geometryBytes) throw new Error("motion GLB가 활성 장면 형상 예산을 초과합니다.");
  if (await sha256(bytes) !== asset.sha256) throw new Error(`motion GLB SHA-256이 manifest와 다릅니다: ${asset.id}`);
  if (options.signal?.aborted) throw abortError();
  assertSelfContainedGlb(bytes);

  const loader = new GLTFLoader();
  const gltf = await loader.parseAsync(bytes, "");
  const scenes = gltf.scenes.length ? gltf.scenes : [gltf.scene];
  try {
    if (options.signal?.aborted) throw abortError();
    if (gltf.animations.length === 0) throw new Error(`motion asset에 animation clip이 없습니다: ${asset.id}`);

    const clip = gltf.animations.find((candidate) => candidate.name === asset.clip.id);
    if (!clip) throw new Error(`manifest clip을 찾을 수 없습니다: ${asset.clip.id}`);
    if (Math.abs(clip.duration - asset.clip.durationSeconds) > 1e-4) {
      throw new Error(`manifest와 GLB clip duration이 다릅니다: ${asset.clip.durationSeconds} != ${clip.duration}`);
    }

    // The playback root is gltf.scene. Other glTF scenes are retained for disposal only.
    const activeObjects = new Set<Object3D>();
    gltf.scene.traverse((object) => activeObjects.add(object));
    const { names, duplicates } = collectNodes(gltf.scene);
    const rigBindings = asset.rig?.nodeBindings ?? [];
    const pathBindings = asset.illustration?.trajectoryBindings.map(({ structureId, trajectoryId }) => ({ structureId, nodeId: trajectoryId })) ?? [];
    const allStructureIds = [...rigBindings.map((row) => row.structureId), ...pathBindings.map((row) => row.structureId)];
    if (new Set(allStructureIds).size !== allStructureIds.length) throw new Error("rig와 path structure binding이 겹칩니다.");
    const allNodeIds = [...rigBindings.map((row) => row.nodeId), ...pathBindings.map((row) => row.nodeId)];
    if (new Set(allNodeIds).size !== allNodeIds.length) throw new Error("rig와 path node binding이 겹칩니다.");
    const rigNodes = new Map<string, Object3D>();
    const pathNodes = new Map<string, Object3D>();
    const sourceNodes = new Map<string, Object3D>();
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

    for (const animation of gltf.animations) for (const track of animation.tracks) {
      const { nodeName } = PropertyBinding.parseTrackName(track.name);
      const target = PropertyBinding.findNode(gltf.scene, nodeName);
      if (!(target instanceof Object3D) || !activeObjects.has(target)) throw new Error(`animation track target node가 active scene에 없습니다: ${track.name}`);
    }

    const skinnedMeshes = validateSkinnedMeshes(gltf.scene);
    const memory = estimateAnimationBytes(gltf.scene, gltf.animations, bytes.byteLength);
    if (memory.memoryEstimateBytes > DATASET_BUDGET.geometryBytes) throw new Error("motion GLB·변형 형상·clip 버퍼의 합이 motion 메모리 예산을 초과합니다.");
    const morphMeshes: Object3D[] = [];
    gltf.scene.traverse((object) => {
      const mesh = object as Object3D & { morphTargetInfluences?: number[]; geometry?: BufferGeometry };
      if (mesh.morphTargetInfluences?.length || Object.values(mesh.geometry?.morphAttributes ?? {}).some((rows) => rows.length > 0)) morphMeshes.push(object);
    });
    if (asset.representationType === "rigged_mesh" && skinnedMeshes.length === 0) {
      throw new Error("rigged_mesh manifest인데 GLB에 유효한 SkinnedMesh가 없습니다.");
    }
    if (asset.representationType === "source_bound_surface") {
      const deformation = asset.sourceBinding!.deformation;
      if ((deformation === "morph_targets" || deformation === "morph_and_skinning") && morphMeshes.length === 0) {
        throw new Error("source_bound_surface manifest인데 GLB에 morph target mesh가 없습니다.");
      }
      if ((deformation === "skinning" || deformation === "morph_and_skinning") && skinnedMeshes.length === 0) {
        throw new Error("source_bound_surface manifest인데 GLB에 유효한 skinned mesh가 없습니다.");
      }
      const sourceBinding = asset.sourceBinding!;
      const sourceIdsByNode = new Map(sourceBinding.members.map((row) => [row.nodeId, row]));
      const meshTargetsByNode = new Map<string, number>();
      for (const member of sourceBinding.members) {
        if (duplicates.has(member.nodeId)) throw new Error(`source GLB node 이름이 중복되어 결속이 모호합니다: ${member.nodeId}`);
        const node = names.get(member.nodeId);
        if (!node || !(node as Object3D & { isMesh?: boolean }).isMesh) throw new Error(`source GLB mesh binding을 찾을 수 없습니다: ${member.nodeId}`);
        sourceNodes.set(member.sourceKey, node);
        const mesh = node as Object3D & { morphTargetInfluences?: number[] };
        meshTargetsByNode.set(member.nodeId, mesh.morphTargetInfluences?.length ?? 0);
      }
      const visibleMeshNames: string[] = [];
      gltf.scene.traverse((object) => { if ((object as Object3D & { isMesh?: boolean }).isMesh) visibleMeshNames.push(object.name); });
      if (visibleMeshNames.some((name) => !sourceIdsByNode.has(name))) throw new Error("source motion GLB에 manifest에 없는 surface mesh가 포함되어 있습니다.");
      for (const animation of gltf.animations) for (const track of animation.tracks) {
        const { nodeName, propertyName } = PropertyBinding.parseTrackName(track.name);
        const member = sourceIdsByNode.get(nodeName);
        if (!member) throw new Error(`source motion track가 고정된 source node를 벗어납니다: ${track.name}`);
        if (member.role === "fixed_structure" || member.role === "passive_context") throw new Error(`fixed/passive source node를 움직이는 track은 허용되지 않습니다: ${track.name}`);
        if (["deforming_muscle_surface", "deforming_passive_surface"].includes(member.role) && propertyName !== "morphTargetInfluences") {
          throw new Error(`근육 전체 transform track은 허용되지 않습니다: ${track.name}`);
        }
        if (["deforming_muscle_surface", "deforming_passive_surface"].includes(member.role) && !(meshTargetsByNode.get(member.nodeId) ?? 0)) {
          throw new Error(`변형 근육 표면에 morph target이 없습니다: ${member.nodeId}`);
        }
        if (["moving_structure", "co_moving_context"].includes(member.role) && propertyName === "scale") throw new Error(`moving structure scale track은 허용되지 않습니다: ${track.name}`);
        if (["moving_structure", "co_moving_context"].includes(member.role) && !["position", "quaternion", "rotation"].includes(propertyName)) {
          throw new Error(`moving structure에는 위치/회전 track만 허용됩니다: ${track.name}`);
        }
      }
    }
    if (asset.representationType !== "rigged_mesh" && skinnedMeshes.length > 0) {
      if (asset.representationType !== "source_bound_surface") throw new Error("bone/path 표현은 수축 조직 SkinnedMesh를 포함하지 않아야 합니다.");
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
      sourceNodes,
      skinnedMeshCount: skinnedMeshes.length,
      morphMeshCount: morphMeshes.length,
      ...memory,
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
