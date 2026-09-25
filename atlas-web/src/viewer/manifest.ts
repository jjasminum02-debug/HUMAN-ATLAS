import rawManifest from "virtual:human-atlas-mesh-manifest";
import glbUrl from "../../../atlas-data/assets/derived-glb/bodyparts3d-r4-right-lower-leg/right-lower-leg.glb?url";
import { decodeT07Glb, type ExpectedNode, type ViewerMesh } from "./glb";
import type { AnnotationAssetContext } from "./annotationDrafts";

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

function annotationAssets(manifest: T07Manifest, meshes: readonly ViewerMesh[]): AnnotationAssetContext[] {
  const sources = manifest.meshAssets;
  if (!sources || sources.length !== meshes.length) throw new Error("T07 mesh asset metadata가 GLB mesh 수와 일치하지 않습니다.");
  const meshById = new Map(meshes.map((mesh) => [mesh.meshAssetId, mesh]));
  const frameId = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR";
  const revisionHash = manifest.glb?.sha256;
  if (!revisionHash) throw new Error("T07 GLB revision hash가 없습니다.");
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

export async function loadT07ViewerBundle(): Promise<T07ViewerBundle> {
  const manifest = asManifest(rawManifest);
  const expected = expectedNodes(manifest);
  const response = await fetch(glbUrl);
  if (!response.ok) throw new Error(`T07 GLB를 불러오지 못했습니다 (HTTP ${response.status}).`);
  const buffer = await response.arrayBuffer();
  if (buffer.byteLength !== manifest.glb?.bytes) throw new Error("T07 GLB byte count가 manifest와 다릅니다.");
  const digest = await sha256(buffer);
  if (digest !== manifest.glb?.sha256) throw new Error("T07 GLB SHA-256이 manifest와 다릅니다.");
  const meshes = decodeT07Glb(buffer, expected);
  if (meshes.length !== manifest.glb?.meshCount) throw new Error("T07 manifest GLB mesh count와 decode 결과가 다릅니다.");
  const assets = annotationAssets(manifest, meshes);
  return {
    manifest,
    meshes,
    annotationAssets: assets,
    attribution: manifest.attribution?.requiredCreditVerbatim ?? "필수 귀속 문구가 T07 manifest에 없습니다.",
    sourceTitle: manifest.attribution?.sourceTitle ?? "출처 미기록",
  };
}
