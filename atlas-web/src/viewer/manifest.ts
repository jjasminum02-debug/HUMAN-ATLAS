import rawManifest from "virtual:human-atlas-mesh-manifest";
import glbUrl from "../../../atlas-data/assets/derived-glb/bodyparts3d-r4-right-lower-leg/right-lower-leg.glb?url";
import boneGlbUrl from "../../../atlas-data/assets/derived-glb/bodyparts3d-r4-t13-right-bones/right-bones.glb?url";
import { decodeT07Glb, type ExpectedNode, type ViewerMesh } from "./glb";
import type { AnnotationAssetContext } from "./annotationDrafts";
import { Mesh } from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import canonicalData from "../../../atlas-data/catalog/canonical-catalog.json";
import bridgeData from "../../../atlas-data/manifests/canonical-geometry-t12.json";
import boneManifest from "../../../atlas-data/manifests/derived-bones-t13.json";
import attachmentContext from "../../../atlas-data/manifests/attachment-context-t13.json";

interface T07Manifest {
  manifestVersion?: string;
  task?: string;
  status?: string;
  modelId?: string;
  poseId?: string;
  glb?: { bytes?: number; meshCount?: number; sha256?: string; uri?: string };
  attribution?: { requiredCreditVerbatim?: string; license?: string; sourceTitle?: string };
  validation?: { anatomyIdentityReviewed?: boolean; attachmentAnnotationsCreated?: boolean; reviewState?: string };
  meshNodes?: Array<Record<string, unknown>>;
  meshCrosswalk?: Array<Record<string, unknown>>;
  meshAssets?: Array<Record<string, unknown>>;
}

export interface T07ViewerBundle {
  manifest: T07Manifest;
  meshes: ViewerMesh[];
  threeMeshes: Map<string, Mesh>;
  annotationAssets: AnnotationAssetContext[];
  attribution: string;
  sourceTitle: string;
}

function asManifest(value: unknown): T07Manifest {
  if (typeof value !== "object" || value === null || Array.isArray(value)) throw new Error("T07 manifest 형식이 객체가 아닙니다.");
  return value as T07Manifest;
}

function expectedNodes(manifest: T07Manifest): ExpectedNode[] {
  if (manifest.task !== "T07" || manifest.manifestVersion !== "T07-derived-assets-v1") {
    throw new Error("현재 viewer는 확인된 T07-derived-assets-v1 manifest만 읽습니다.");
  }
  if (manifest.modelId !== "HA-MODEL-BP3D4-R4-RIGHT-LOWER-LEG-STATIC" || manifest.status !== "local_candidate_needs_review") {
    throw new Error("T07 model ID 또는 검토 대기 상태가 예상과 다릅니다.");
  }
  if (!manifest.glb || !Number.isInteger(manifest.glb.bytes) || manifest.glb.bytes !== 712192 || manifest.glb.meshCount !== 11 ||
    manifest.glb.sha256 !== "044450c3230bd23869a099d545151cb3d7518da3240a6e59f911f82786edc341") {
    throw new Error("T07 GLB의 크기/hash/mesh count가 고정 manifest 값과 다릅니다.");
  }
  if (manifest.validation?.anatomyIdentityReviewed !== false || manifest.validation?.attachmentAnnotationsCreated !== false || manifest.validation?.reviewState !== "needs_review") {
    throw new Error("T07의 anatomy review/annotation 경계가 예상과 다릅니다.");
  }
  const nodes = manifest.meshNodes;
  const crosswalk = manifest.meshCrosswalk;
  if (!nodes || !crosswalk || nodes.length !== 11 || crosswalk.length !== 11) throw new Error("T07 manifest에 예상한 11개 node/crosswalk가 없습니다.");
  const canonical = canonicalData.entities;
  const canonicalAssets = new Map(canonical.meshAssets.map((row) => [row.id, row]));
  const instances = new Map(canonical.instances.map((row) => [row.id, row]));
  const mappings = canonical.meshMappings;
  if (canonicalAssets.size !== 20 || instances.size !== 6 || mappings.length !== 7 ||
    bridgeData.coverage.meshAssets !== 11 || bridgeData.coverage.rightMuscleInstances !== 6 || bridgeData.coverage.muscleMeshMappings !== 7 ||
    bridgeData.sourceGlbSha256 !== manifest.glb.sha256 || bridgeData.poseId !== manifest.poseId ||
    bridgeData.frameId !== "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR" || bridgeData.units !== "m" ||
    bridgeData.unmappedStructureAssets.length !== 4 ||
    !bridgeData.unmappedStructureAssets.some((row) => row.fileId === "FJ3385" && row.structureId === null)) {
    throw new Error("T12b canonical geometry bridge의 coverage/frame/talus 제외가 예상과 다릅니다.");
  }
  const mappingTarget = new Map<string, string>();
  for (const mapping of mappings) {
    if (mapping.reviewState !== "needs_review" || mapping.meshIds.length !== 1 || mapping.instanceIds.length !== 1 || mapping.evidenceIds.length < 1) {
      throw new Error(`T12b canonical mesh mapping이 미검토 단일 관계가 아닙니다: ${mapping.id}`);
    }
    const instance = instances.get(mapping.instanceIds[0]);
    if (!instance || instance.side !== "right" || !canonicalAssets.has(mapping.meshIds[0])) throw new Error(`T12b mapping 참조가 없습니다: ${mapping.id}`);
    const target = mapping.partIds.length === 1 ? mapping.partIds[0] : instance.conceptId;
    if (mappingTarget.has(mapping.meshIds[0])) throw new Error(`T12b mesh mapping 중복: ${mapping.meshIds[0]}`);
    mappingTarget.set(mapping.meshIds[0], target);
  }
  const crosswalkById = new Map(crosswalk.map((row) => [row.meshAssetId, row]));
  const mapped = nodes.map((node) => {
    const id = node.meshAssetId;
    const relation = typeof id === "string" ? crosswalkById.get(id) : undefined;
    if (!relation || typeof id !== "string" || relation.reviewState !== "needs_review" || relation.meshAssetId !== id) {
      throw new Error(`T07 manifest crosswalk 또는 needs_review 상태가 mesh와 맞지 않습니다: ${String(id)}`);
    }
    const sourceName = node.sourceName;
    const sourceFileId = node.sourceFileId;
    const targetEntityType = node.targetEntityType;
    const targetEntityId = node.targetEntityId;
    const relationStatus = node.relationStatus;
    const nodeIndex = node.nodeIndex;
    const meshIndex = node.meshIndex;
    if (typeof sourceName !== "string" || typeof sourceFileId !== "string" || typeof targetEntityType !== "string" ||
      typeof relationStatus !== "string" || !Number.isInteger(nodeIndex) || !Number.isInteger(meshIndex) ||
      (targetEntityId !== null && typeof targetEntityId !== "string")) {
      throw new Error(`T07 mesh node 필드가 불완전합니다: ${id}`);
    }
    if (relation.sourceFileId !== sourceFileId || relation.targetEntityType !== targetEntityType ||
      relation.targetEntityId !== targetEntityId || relation.relationStatus !== relationStatus) {
      throw new Error(`T07 crosswalk와 node record의 target/source가 다릅니다: ${id}`);
    }
    const canonicalAsset = canonicalAssets.get(id);
    const t07Asset = manifest.meshAssets?.find((asset) => asset.id === id);
    if (!canonicalAsset || !t07Asset || JSON.stringify(canonicalAsset) !== JSON.stringify(t07Asset)) {
      throw new Error(`T12b canonical mesh asset이 T07 자산 계약과 다릅니다: ${id}`);
    }
    if (targetEntityType === "structure") {
      if (mappingTarget.has(id) || !bridgeData.unmappedStructureAssets.some((row) => row.meshAssetId === id && row.structureId === targetEntityId)) {
        throw new Error(`T12b 구조물 mesh 제외 기록이 다릅니다: ${id}`);
      }
    } else if (mappingTarget.get(id) !== targetEntityId || !bridgeData.muscleLinks.some((row) => row.meshAssetId === id && row.reviewState === "needs_review")) {
      throw new Error(`T12b canonical muscle mapping이 T07 crosswalk와 다릅니다: ${id}`);
    }
    return {
      meshAssetId: id,
      nodeIndex: nodeIndex as number,
      meshIndex: meshIndex as number,
      sourceName,
      sourceFileId,
      targetEntityId: targetEntityId as string | null,
      targetEntityType,
      relationStatus,
      reviewState: "needs_review",
    } satisfies ExpectedNode;
  });
  if (new Set(mapped.map((node) => node.meshAssetId)).size !== 11 || new Set(mapped.map((node) => node.nodeIndex)).size !== 11 || new Set(mapped.map((node) => node.meshIndex)).size !== 11) {
    throw new Error("T07 manifest의 stable mesh/node/index가 중복되었습니다.");
  }
  return mapped;
}

function expectedBoneNodes(): ExpectedNode[] {
  if (boneManifest.manifestVersion !== "T13-derived-bones-v2" || boneManifest.reviewState !== "needs_review" ||
    boneManifest.glb.meshCount !== 9 || boneManifest.meshAssets.length !== 9 || boneManifest.viewerNodes.length !== 9 ||
    boneManifest.transform.frameId !== bridgeData.frameId || boneManifest.transform.targetUnits !== bridgeData.units ||
    boneManifest.transform.poseId !== bridgeData.poseId || boneManifest.sourceId !== bridgeData.sourceId ||
    attachmentContext.assetSets[1]?.glbSha256 !== boneManifest.glb.sha256 ||
    attachmentContext.coverage.t05Attachments !== 41 || attachmentContext.coverage.locatedSurfaceAnnotations !== 0) {
    throw new Error("T13 뼈 자산과 부착 검토 계약이 맞지 않습니다.");
  }
  const canonicalAssets = new Map(canonicalData.entities.meshAssets.map((row) => [row.id, row]));
  const structures = new Set(canonicalData.entities.structures.map((row) => row.id));
  const nodes = boneManifest.viewerNodes.map((node) => {
    const asset = canonicalAssets.get(node.meshAssetId);
    const fromManifest = boneManifest.meshAssets.find((row) => row.id === node.meshAssetId);
    if (!asset || !fromManifest || JSON.stringify(asset) !== JSON.stringify(fromManifest) ||
      asset.hash !== boneManifest.glb.sha256 || asset.units !== "m" || asset.laterality !== "right" ||
      asset.axes.frameId !== bridgeData.frameId || asset.pose.id !== bridgeData.poseId ||
      node.targetEntityType !== "structure" || (node.targetEntityId !== null && !structures.has(node.targetEntityId)) ||
      (node.targetEntityId === null && !["FJ3353", "FJ3355", "FJ3357"].includes(node.sourceFileId)) ||
      node.reviewState !== "needs_review") {
      throw new Error(`T13 뼈 mesh 계약/구조 후보가 맞지 않습니다: ${node.meshAssetId}`);
    }
    return node satisfies ExpectedNode;
  });
  if (new Set(nodes.map((row) => row.meshAssetId)).size !== 9) throw new Error("T13 뼈 mesh ID가 중복됩니다.");
  return nodes;
}

function annotationAssets(sources: readonly Record<string, unknown>[], revisionHash: string, meshes: readonly ViewerMesh[]): AnnotationAssetContext[] {
  if (sources.length !== meshes.length) throw new Error("mesh asset metadata가 GLB mesh 수와 일치하지 않습니다.");
  const meshById = new Map(meshes.map((mesh) => [mesh.meshAssetId, mesh]));
  const frameId = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR";
  return sources.map((row) => {
    const id = row.id;
    const revision = row.revision;
    const hash = row.hash;
    const topologyHash = row.topologyHash;
    const laterality = row.laterality;
    const units = row.units;
    const axes = row.axes;
    const pose = row.pose;
    const mesh = typeof id === "string" ? meshById.get(id) : undefined;
    if (typeof id !== "string" || !mesh || typeof revision !== "string" || typeof hash !== "string" || hash !== revisionHash ||
      typeof topologyHash !== "string" || !/^[a-f0-9]{64}$/.test(topologyHash) || laterality !== "right" || units !== "m" ||
      typeof axes !== "object" || axes === null || (axes as Record<string, unknown>).frameId !== frameId ||
      typeof pose !== "object" || pose === null || typeof (pose as Record<string, unknown>).id !== "string") {
      throw new Error(`T07 annotation asset metadata가 지원 계약과 일치하지 않습니다: ${String(id)}`);
    }
    return {
      assetId: id,
      assetRevision: revision,
      assetRevisionHash: hash,
      topologyHash,
      laterality,
      frameId,
      units,
      poseId: (pose as Record<string, unknown>).id as string,
      triangleCount: mesh.indices.length / 3,
      targetEntityId: mesh.targetEntityId,
    };
  });
}

async function sha256(buffer: ArrayBuffer): Promise<string> {
  if (!globalThis.crypto?.subtle) throw new Error("브라우저 Web Crypto API가 없어 GLB SHA-256을 확인할 수 없습니다.");
  const digest = await globalThis.crypto.subtle.digest("SHA-256", buffer);
  return [...new Uint8Array(digest)].map((value) => value.toString(16).padStart(2, "0")).join("");
}

async function checkedThreeMeshes(buffer: ArrayBuffer, meshes: readonly ViewerMesh[]): Promise<Map<string, Mesh>> {
  const parsed = await new Promise<Awaited<ReturnType<GLTFLoader["loadAsync"]>>>((resolve, reject) => {
    new GLTFLoader().parse(buffer, "", resolve, reject);
  });
  const nodes = new Map<string, Mesh>();
  parsed.scene.traverse((object) => {
    if (!(object instanceof Mesh)) return;
    if (nodes.has(object.name)) throw new Error(`GLTFLoader가 중복 mesh ID를 읽었습니다: ${object.name}`);
    nodes.set(object.name, object);
  });
  if (nodes.size !== meshes.length) throw new Error("GLTFLoader와 T07 decoder의 mesh 수가 다릅니다.");
  for (const raw of meshes) {
    const loaded = nodes.get(raw.meshAssetId);
    if (!loaded || loaded.userData.stableMeshAssetId !== raw.meshAssetId || loaded.parent !== parsed.scene ||
      loaded.position.lengthSq() !== 0 || loaded.rotation.x !== 0 || loaded.rotation.y !== 0 || loaded.rotation.z !== 0 ||
      loaded.scale.x !== 1 || loaded.scale.y !== 1 || loaded.scale.z !== 1) {
      throw new Error(`${raw.meshAssetId}: Three scene의 stable ID 또는 identity transform이 다릅니다.`);
    }
    const position = loaded.geometry.getAttribute("position")?.array;
    const normal = loaded.geometry.getAttribute("normal")?.array;
    const index = loaded.geometry.index?.array;
    if (!position || !normal || !index || position.length !== raw.positions.length || normal.length !== raw.normals.length || index.length !== raw.indices.length) {
      throw new Error(`${raw.meshAssetId}: Three geometry 길이가 T07과 다릅니다.`);
    }
    for (let i = 0; i < position.length; i += 1) if (position[i] !== raw.positions[i]) throw new Error(`${raw.meshAssetId}: position 순서가 달라졌습니다.`);
    for (let i = 0; i < normal.length; i += 1) if (normal[i] !== raw.normals[i]) throw new Error(`${raw.meshAssetId}: normal 순서가 달라졌습니다.`);
    for (let i = 0; i < index.length; i += 1) if (index[i] !== raw.indices[i]) throw new Error(`${raw.meshAssetId}: triangle index가 달라졌습니다. 기존 annotation을 사용하지 않습니다.`);
  }
  return nodes;
}

export async function loadT07ViewerBundle(): Promise<T07ViewerBundle> {
  const manifest = asManifest(rawManifest);
  const expected = expectedNodes(manifest);
  const boneExpected = expectedBoneNodes();
  const [response, boneResponse] = await Promise.all([fetch(glbUrl), fetch(boneGlbUrl)]);
  if (!response.ok) throw new Error(`T07 GLB를 불러오지 못했습니다 (HTTP ${response.status}).`);
  const buffer = await response.arrayBuffer();
  if (buffer.byteLength !== manifest.glb?.bytes) throw new Error("T07 GLB byte count가 manifest와 다릅니다.");
  const digest = await sha256(buffer);
  if (digest !== manifest.glb?.sha256) throw new Error("T07 GLB SHA-256이 manifest와 다릅니다.");
  const meshes = decodeT07Glb(buffer, expected);
  if (meshes.length !== manifest.glb?.meshCount) throw new Error("T07 manifest GLB mesh count와 decode 결과가 다릅니다.");
  const threeMeshes = await checkedThreeMeshes(buffer, meshes);
  if (!boneResponse.ok) throw new Error(`T13 뼈 GLB를 불러오지 못했습니다 (HTTP ${boneResponse.status}).`);
  const boneBuffer = await boneResponse.arrayBuffer();
  if (boneBuffer.byteLength !== boneManifest.glb.bytes || await sha256(boneBuffer) !== boneManifest.glb.sha256) {
    throw new Error("T13 뼈 GLB 크기 또는 SHA-256이 manifest와 다릅니다.");
  }
  const boneMeshes = decodeT07Glb(boneBuffer, boneExpected);
  const boneThreeMeshes = await checkedThreeMeshes(boneBuffer, boneMeshes);
  for (const [id, mesh] of boneThreeMeshes) {
    if (threeMeshes.has(id)) throw new Error(`T07/T13 mesh ID가 중복됩니다: ${id}`);
    threeMeshes.set(id, mesh);
  }
  const assets = [
    ...annotationAssets(manifest.meshAssets ?? [], manifest.glb?.sha256 ?? "", meshes),
    ...annotationAssets(boneManifest.meshAssets, boneManifest.glb.sha256, boneMeshes),
  ];
  return {
    manifest,
    meshes: [...meshes, ...boneMeshes],
    threeMeshes,
    annotationAssets: assets,
    attribution: manifest.attribution?.requiredCreditVerbatim ?? "필수 귀속 문구가 T07 manifest에 없습니다.",
    sourceTitle: manifest.attribution?.sourceTitle ?? "출처 미기록",
  };
}
