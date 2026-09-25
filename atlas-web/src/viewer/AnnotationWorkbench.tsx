import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { AtlasRecord } from "../data/catalog";
import {
  AnnotationValidationError,
  serializeAnnotationDraftExchange,
  validateAnnotationDraftExchange,
  type AnnotationAssetContext,
  type AnnotationAttachmentContext,
  type AnnotationDraft,
  type AnnotationGeometry,
} from "./annotationDrafts";
import type { AnnotationSurfaceHit, T07WebGLViewer, ViewerMesh } from "./glb";

const STORAGE_KEY = "human-atlas:t09:annotation-drafts:v1";
const FRAME_ID = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR";
type GeometryKind = AnnotationGeometry["kind"];
type ConceptRef = { id: string; entityType?: unknown; parentId?: unknown };
type Visibility = "visible" | "transparent" | "hidden";

interface AttachmentOption extends AnnotationAttachmentContext {
  ownerId: string;
  role: string;
  summary: string;
}

interface PendingGeometry {
  assetId: string;
  kind: GeometryKind;
  positions: [number, number, number][];
  triangleIds: number[];
  topologyHash: string;
}

interface Props {
  viewer: T07WebGLViewer | null;
  overlayCanvas: HTMLCanvasElement | null;
  assets: readonly AnnotationAssetContext[];
  meshes: readonly ViewerMesh[];
  concepts: readonly ConceptRef[];
  attachments: readonly AtlasRecord[];
  claims: readonly AtlasRecord[];
  selectedEntityId: string | null;
  pickedMesh: ViewerMesh | null;
  visibility: Readonly<Record<string, Visibility>>;
  onSelectMesh: (mesh: ViewerMesh) => void;
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null && !Array.isArray(value);

function stringValue(value: unknown): string | null {
  return typeof value === "string" ? value : null;
}

function listStrings(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((id): id is string => typeof id === "string") : [];
}

function claimSummary(claim: AtlasRecord | undefined): string {
  if (!claim || !isRecord(claim.value)) return "연결된 설명 claim이 없습니다.";
  return stringValue(claim.value.summary) ?? "설명 문장이 없습니다.";
}

function newId(): string {
  const token = globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  return `HA-ANN-DRAFT-${token}`;
}

function roleLabel(role: string): string {
  if (role === "origin") return "기시";
  if (role === "insertion") return "정지";
  return role;
}

function geometryLabel(kind: GeometryKind): string {
  if (kind === "point") return "점";
  if (kind === "polyline") return "선";
  return "면 패치";
}

function annotationColor(attachment: AttachmentOption | undefined): string {
  if (attachment?.role === "origin") return "#07876d";
  if (attachment?.role === "insertion") return "#c88412";
  return "#496f9b";
}

function drawDot(ctx: CanvasRenderingContext2D, x: number, y: number, color: string, label: string) {
  ctx.beginPath();
  ctx.arc(x, y, 6, 0, Math.PI * 2);
  ctx.fillStyle = "#ffffff";
  ctx.fill();
  ctx.lineWidth = 3;
  ctx.strokeStyle = color;
  ctx.stroke();
  ctx.font = "700 10px ui-sans-serif, sans-serif";
  ctx.lineWidth = 3;
  ctx.strokeStyle = "rgba(255,255,255,.95)";
  ctx.strokeText(label, x + 8, y - 8);
  ctx.fillStyle = color;
  ctx.fillText(label, x + 8, y - 8);
}

export function AnnotationWorkbench({
  viewer, overlayCanvas, assets, meshes, concepts, attachments, claims, selectedEntityId, pickedMesh, visibility, onSelectMesh,
}: Props) {
  const [drafts, setDrafts] = useState<AnnotationDraft[]>([]);
  const [selectedAttachmentId, setSelectedAttachmentId] = useState("");
  const [kind, setKind] = useState<GeometryKind>("point");
  const [activeKind, setActiveKind] = useState<GeometryKind | null>(null);
  const [pending, setPending] = useState<PendingGeometry | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [message, setMessage] = useState("도형 도구를 선택해 표면을 클릭하세요. 모든 좌표는 카메라가 아닌 asset frame에 저장됩니다.");
  const [jsonText, setJsonText] = useState("");
  const [storageReady, setStorageReady] = useState(false);
  const [storageBlocked, setStorageBlocked] = useState(false);
  const drawRef = useRef<() => void>(() => undefined);

  const selectedConcept = concepts.find((concept) => concept.id === selectedEntityId);
  const availableOwners = useMemo(() => {
    const owners = new Set<string>();
    if (selectedEntityId) owners.add(selectedEntityId);
    if (selectedConcept?.entityType === "individual_muscle") {
      concepts.filter((concept) => concept.parentId === selectedEntityId).forEach((concept) => owners.add(concept.id));
    }
    return owners;
  }, [concepts, selectedConcept?.entityType, selectedEntityId]);

  const attachmentOptions = useMemo<AttachmentOption[]>(() => {
    if (!pickedMesh?.targetEntityId || pickedMesh.targetEntityType === "structure") return [];
    return attachments.flatMap((attachment) => {
      const ownerId = stringValue(attachment.muscleOrPartId);
      const id = stringValue(attachment.id);
      const descriptionClaimId = stringValue(attachment.descriptionClaimId);
      if (!id || !ownerId || !descriptionClaimId || !availableOwners.has(ownerId) || ownerId !== pickedMesh.targetEntityId) return [];
      const claim = claims.find((row) => row.id === descriptionClaimId);
      if (!claim || claim.subjectId !== id || claim.reviewState !== "needs_review") return [];
      return [{
        id,
        descriptionClaimId,
        evidenceIds: listStrings(claim.evidenceIds),
        ownerId,
        role: stringValue(attachment.role) ?? "attachment",
        summary: claimSummary(claim),
      }];
    });
  }, [attachments, availableOwners, claims, pickedMesh]);

  const allAttachmentContexts = useMemo<AnnotationAttachmentContext[]>(() => attachments.flatMap((attachment) => {
    const id = stringValue(attachment.id);
    const ownerId = stringValue(attachment.muscleOrPartId);
    const descriptionClaimId = stringValue(attachment.descriptionClaimId);
    const claim = descriptionClaimId ? claims.find((row) => row.id === descriptionClaimId) : undefined;
    if (!id || !ownerId || !descriptionClaimId || !claim || claim.subjectId !== id || claim.reviewState !== "needs_review") return [];
    return [{ id, ownerId, descriptionClaimId, evidenceIds: listStrings(claim.evidenceIds) }];
  }), [attachments, claims]);

  useEffect(() => {
    if (!assets.length || storageReady) return;
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) {
        setStorageReady(true);
        return;
      }
      const parsed: unknown = JSON.parse(raw);
      const loaded = validateAnnotationDraftExchange(parsed, { assets, attachments: allAttachmentContexts, instanceIds: [] }, { changedAssetPolicy: "mark_stale" });
      if (loaded.syntheticFixture) throw new Error("합성 검증 fixture는 개인 초안 저장소에 불러오지 않습니다.");
      setDrafts(loaded.annotations);
      setStorageReady(true);
      setMessage(`${loaded.annotations.length}개 로컬 초안을 불러왔습니다. stale 표시는 현재 mesh revision과 다시 대조한 결과입니다.`);
    } catch (error) {
      setStorageBlocked(true);
      setStorageReady(true);
      setMessage(`기존 로컬 JSON은 그대로 보존했습니다. 형식 확인 후 유효한 JSON을 가져오면 저장을 다시 시작할 수 있습니다. ${error instanceof Error ? error.message : "저장 자료를 읽지 못했습니다."}`);
    }
  }, [allAttachmentContexts, assets, storageReady]);

  useEffect(() => {
    if (!storageReady || storageBlocked) return;
    try {
      localStorage.setItem(STORAGE_KEY, serializeAnnotationDraftExchange(drafts));
    } catch (error) {
      setStorageBlocked(true);
      setMessage(`브라우저 저장소에 쓸 수 없어 편집을 멈췄습니다. 내보내기로 초안을 보존하세요. ${error instanceof Error ? error.message : "저장 실패"}`);
    }
  }, [drafts, storageBlocked, storageReady]);

  const attachmentById = useMemo(() => new Map(attachmentOptions.map((row) => [row.id, row])), [attachmentOptions]);
  const activeAttachment = attachmentById.get(selectedAttachmentId);

  const drawOverlay = useCallback(() => {
    if (!overlayCanvas || !viewer) return;
    const rect = overlayCanvas.getBoundingClientRect();
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    const width = Math.max(1, Math.round(rect.width * ratio));
    const height = Math.max(1, Math.round(rect.height * ratio));
    if (overlayCanvas.width !== width) overlayCanvas.width = width;
    if (overlayCanvas.height !== height) overlayCanvas.height = height;
    const ctx = overlayCanvas.getContext("2d");
    if (!ctx) return;
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    ctx.clearRect(0, 0, rect.width, rect.height);

    const renderOne = (annotation: AnnotationDraft, isPending = false) => {
      if (annotation.reviewState === "stale" || visibility[annotation.assetId] === "hidden") return;
      const mesh = viewer.getMesh(annotation.assetId);
      if (!mesh) return;
      const related = attachmentOptions.find((row) => row.id === annotation.attachmentId);
      const color = annotationColor(related);
      const label = related ? `${roleLabel(related.role)} · draft` : "draft";
      ctx.save();
      ctx.globalAlpha = visibility[annotation.assetId] === "transparent" ? 0.65 : 1;
      ctx.setLineDash(isPending ? [4, 3] : [6, 4]);
      ctx.lineWidth = 3;
      ctx.strokeStyle = color;
      ctx.fillStyle = `${color}35`;

      if (annotation.geometry.kind === "point") {
        const point = viewer.projectPoint(annotation.geometry.position);
        if (point.visible) drawDot(ctx, point.x, point.y, color, label);
      } else if (annotation.geometry.kind === "polyline") {
        const points = annotation.geometry.vertices.map((vertex) => viewer.projectPoint(vertex));
        if (points.length >= 2 && points.every((point) => point.visible)) {
          ctx.beginPath();
          points.forEach((point, index) => index === 0 ? ctx.moveTo(point.x, point.y) : ctx.lineTo(point.x, point.y));
          ctx.stroke();
          points.forEach((point, index) => drawDot(ctx, point.x, point.y, color, index === 0 ? label : ""));
        }
      } else {
        ctx.setLineDash(isPending ? [4, 3] : []);
        for (const triangleId of annotation.geometry.triangleIds) {
          const base = triangleId * 3;
          const indices = [mesh.indices[base], mesh.indices[base + 1], mesh.indices[base + 2]];
          const points = indices.map((vertexId) => {
            const offset = vertexId * 3;
            return viewer.projectPoint([mesh.positions[offset], mesh.positions[offset + 1], mesh.positions[offset + 2]]);
          });
          if (points.some((point) => !point.visible)) continue;
          ctx.beginPath();
          ctx.moveTo(points[0].x, points[0].y);
          ctx.lineTo(points[1].x, points[1].y);
          ctx.lineTo(points[2].x, points[2].y);
          ctx.closePath();
          ctx.fill();
          ctx.stroke();
        }
      }
      ctx.restore();
    };

    drafts.forEach((draft) => renderOne(draft));
    if (pending && activeAttachment) {
      const asset = assets.find((row) => row.assetId === pending.assetId);
      if (!asset) return;
      const preview: AnnotationDraft = {
        id: "HA-ANN-DRAFT-PENDING",
        attachmentId: activeAttachment.id,
        descriptionClaimId: activeAttachment.descriptionClaimId,
        instanceId: null,
        side: asset.laterality === "left" ? "left" : "right",
        assetId: asset.assetId,
        assetRevision: asset.assetRevision,
        assetRevisionHash: asset.assetRevisionHash,
        topologyHash: asset.topologyHash,
        geometry: pending.kind === "point"
          ? { kind: "point", position: pending.positions[0] }
          : pending.kind === "polyline"
            ? { kind: "polyline", vertices: pending.positions }
            : { kind: "surface_patch", triangleIds: pending.triangleIds, topologyHash: pending.topologyHash },
        frameId: asset.frameId,
        units: "m",
        poseId: asset.poseId,
        precision: pending.kind === "point" ? "representative" : "approximate_extent",
        method: "manual_mapping",
        transformChain: [],
        landmarkChecks: [],
        evidenceIds: activeAttachment.evidenceIds,
        reviewState: "draft",
        synthetic: false,
      };
      const enoughGeometry = pending.kind === "point" ? pending.positions.length === 1 : pending.kind === "polyline" ? pending.positions.length > 0 : pending.triangleIds.length > 0;
      if (enoughGeometry) renderOne(preview, true);
    }
  }, [activeAttachment, assets, drafts, overlayCanvas, pending, viewer, visibility]);

  drawRef.current = drawOverlay;
  useEffect(() => {
    if (!viewer) return;
    viewer.setFrameCallback(() => drawRef.current());
    return () => {
      viewer.setAnnotationPickHandler(null);
      viewer.setFrameCallback(null);
    };
  }, [viewer]);
  useEffect(() => { drawOverlay(); }, [drawOverlay]);

  useEffect(() => {
    if (!activeKind || !viewer) {
      viewer?.setAnnotationPickHandler(null);
      return;
    }
    viewer.setAnnotationPickHandler((hit: AnnotationSurfaceHit) => {
      if (!activeAttachment || !pickedMesh) {
        setMessage("먼저 현재 mesh에 연결된 T05 기시·정지 설명을 선택하세요.");
        return;
      }
      if (hit.mesh.meshAssetId !== pickedMesh.meshAssetId || hit.mesh.targetEntityId !== activeAttachment.ownerId) {
        setMessage("선택한 초안의 mesh/attachment 대상과 다른 표면입니다. 이 클릭은 좌표에 추가하지 않았습니다.");
        return;
      }
      const asset = assets.find((row) => row.assetId === hit.mesh.meshAssetId);
      if (!asset || asset.laterality !== "right" || asset.frameId !== FRAME_ID || asset.units !== "m") {
        setMessage("현재 도구는 manifest에서 검증한 우측 Atlas frame의 meter 좌표만 허용합니다.");
        return;
      }
      if (editingId) {
        const existing = drafts.find((draft) => draft.id === editingId);
        if (!existing || existing.assetId !== hit.mesh.meshAssetId || existing.attachmentId !== activeAttachment.id) {
          setMessage("편집 중인 초안의 attachment/mesh 연결은 바꿀 수 없습니다. 삭제 후 새 draft를 시작하세요.");
          return;
        }
      }
      setPending((previous) => {
        if (!previous || previous.assetId !== hit.mesh.meshAssetId || previous.kind !== activeKind) {
          return { assetId: hit.mesh.meshAssetId, kind: activeKind, positions: [hit.position], triangleIds: [hit.triangleId], topologyHash: asset.topologyHash };
        }
        if (activeKind === "point") return { ...previous, positions: [hit.position] };
        if (activeKind === "polyline") return { ...previous, positions: [...previous.positions, hit.position] };
        return previous.triangleIds.includes(hit.triangleId)
          ? previous
          : { ...previous, triangleIds: [...previous.triangleIds, hit.triangleId] };
      });
      onSelectMesh(hit.mesh);
      setMessage(activeKind === "point" ? "표면 점을 기록했습니다. 저장을 눌러 초안으로 보관하세요." : activeKind === "polyline" ? "선의 점을 추가했습니다. 두 점 이상에서 초안을 저장할 수 있습니다." : "삼각형을 면 패치에 추가했습니다. 패치에 포함할 표면을 더 클릭한 뒤 저장하세요.");
    });
    return () => viewer.setAnnotationPickHandler(null);
  }, [activeAttachment, activeKind, assets, drafts, editingId, onSelectMesh, pickedMesh, viewer]);

  useEffect(() => {
    if (attachmentOptions.some((row) => row.id === selectedAttachmentId)) return;
    setSelectedAttachmentId(attachmentOptions[0]?.id ?? "");
  }, [attachmentOptions, selectedAttachmentId]);

  function beginNew(nextKind: GeometryKind) {
    if (storageBlocked) {
      setMessage("기존 저장 JSON을 보존하기 위해 쓰기를 막았습니다. 유효한 초안 JSON을 가져온 뒤 다시 시도하세요.");
      return;
    }
    if (!pickedMesh || !activeAttachment) {
      setMessage("현재 선택한 근육/근두 mesh와 연결된 T05 부착 설명이 필요합니다.");
      return;
    }
    if (!assets.some((asset) => asset.assetId === pickedMesh.meshAssetId)) {
      setMessage("선택 mesh의 T07 asset revision을 찾을 수 없습니다.");
      return;
    }
    setKind(nextKind);
    setPending(null);
    setEditingId(null);
    setActiveKind(nextKind);
    setMessage(`${geometryLabel(nextKind)} 입력 중입니다. 모델 표면을 클릭해 주세요. 초안은 저장될 때까지 목록에 반영되지 않습니다.`);
  }

  function savePending() {
    if (!pending || !activeAttachment) return;
    const asset = assets.find((row) => row.assetId === pending.assetId);
    if (!asset) {
      setMessage("선택 asset을 현재 manifest에서 찾지 못했습니다. 초안을 저장하지 않았습니다.");
      return;
    }
    if (pending.kind === "polyline" && pending.positions.length < 2) {
      setMessage("선은 두 점 이상을 찍어야 저장할 수 있습니다.");
      return;
    }
    if (pending.kind === "surface_patch" && pending.triangleIds.length < 1) {
      setMessage("면 패치는 하나 이상의 표면 삼각형이 필요합니다.");
      return;
    }
    const geometry: AnnotationGeometry = pending.kind === "point"
      ? { kind: "point", position: pending.positions[0] }
      : pending.kind === "polyline"
        ? { kind: "polyline", vertices: pending.positions }
        : { kind: "surface_patch", triangleIds: pending.triangleIds, topologyHash: pending.topologyHash };
    const annotation: AnnotationDraft = {
      id: editingId ?? newId(),
      attachmentId: activeAttachment.id,
      descriptionClaimId: activeAttachment.descriptionClaimId,
      instanceId: null,
      side: asset.laterality === "left" ? "left" : "right",
      assetId: asset.assetId,
      assetRevision: asset.assetRevision,
      assetRevisionHash: asset.assetRevisionHash,
      topologyHash: asset.topologyHash,
      geometry,
      frameId: asset.frameId,
      units: "m",
      poseId: asset.poseId,
      precision: pending.kind === "point" ? "representative" : "approximate_extent",
      method: "manual_mapping",
      transformChain: [],
      landmarkChecks: [],
      evidenceIds: activeAttachment.evidenceIds,
      reviewState: "draft",
      synthetic: false,
    };
    setDrafts((rows) => {
      const next = editingId ? rows.map((row) => row.id === editingId ? annotation : row) : [...rows, annotation];
      const context = { assets, attachments: allAttachmentContexts, instanceIds: [] };
      return validateAnnotationDraftExchange({ schemaVersion: "HA-annotation-draft-exchange-v1", syntheticFixture: false, annotations: next }, context).annotations;
    });
    setPending(null);
    setEditingId(null);
    setActiveKind(null);
    setMessage("검토 전 로컬 초안을 저장했습니다. Canonical spatial annotation이나 해부학적으로 확정된 위치가 아닙니다.");
  }

  function cancelDrawing() {
    setPending(null);
    setEditingId(null);
    setActiveKind(null);
    setMessage("입력을 취소했습니다. 이미 저장한 draft만 로컬에 남습니다.");
  }

  function beginEdit(annotation: AnnotationDraft) {
    if (annotation.reviewState === "stale") {
      setMessage("stale annotation은 이 도구에서 편집할 수 없습니다. 현재 revision에서 새 초안을 시작하세요.");
      return;
    }
    const attachment = attachmentOptions.find((row) => row.id === annotation.attachmentId);
    const mesh = meshes.find((row) => row.meshAssetId === annotation.assetId);
    if (!attachment || !mesh) {
      setMessage("현재 선택/manifest에서 annotation의 원래 attachment 또는 mesh를 찾지 못했습니다.");
      return;
    }
    setSelectedAttachmentId(attachment.id);
    onSelectMesh(mesh);
    setKind(annotation.geometry.kind);
    setPending(null);
    setEditingId(annotation.id);
    setActiveKind(annotation.geometry.kind);
    setMessage(`기존 ${geometryLabel(annotation.geometry.kind)}의 재입력 모드입니다. 클릭으로 새 geometry를 만들고 변경 저장하세요.`);
  }

  function deleteDraft(id: string) {
    setDrafts((rows) => rows.filter((row) => row.id !== id));
    if (editingId === id) cancelDrawing();
    setMessage("선택한 draft를 로컬 저장소와 목록에서 삭제했습니다.");
  }

  function exportJson() {
    const text = serializeAnnotationDraftExchange(drafts);
    setJsonText(text);
    const url = URL.createObjectURL(new Blob([text], { type: "application/json" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = "human-atlas-annotation-drafts.json";
    link.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1_000);
    setMessage(`${drafts.length}개 검토 전 draft를 JSON으로 내보냈습니다.`);
  }

  function importJson() {
    try {
      const parsed: unknown = JSON.parse(jsonText);
      const result = validateAnnotationDraftExchange(parsed, { assets, attachments: allAttachmentContexts, instanceIds: [] });
      setDrafts(result.annotations);
      setStorageBlocked(false);
      setMessage(`${result.annotations.length}개 검증된 JSON draft를 불러왔습니다. 잘못된 입력은 저장값을 바꾸지 않습니다.`);
    } catch (error) {
      const detail = error instanceof AnnotationValidationError ? `${error.code}: ${error.message}` : error instanceof Error ? error.message : "JSON을 읽지 못했습니다.";
      setMessage(`가져오기를 거부했습니다. 기존 저장 초안은 변경하지 않았습니다. ${detail}`);
    }
  }

  function downloadStoredJson() {
    setJsonText(serializeAnnotationDraftExchange(drafts));
    setMessage("현재 초안을 JSON text area에 준비했습니다. 가져오기 전 파일 내용을 확인하세요.");
  }

  function annotationPreview(annotation: AnnotationDraft) {
    const source = attachments.find((row) => row.id === annotation.attachmentId);
    const claimId = source?.descriptionClaimId;
    const claim = claims.find((row) => row.id === claimId);
    const geometryCount = annotation.geometry.kind === "point" ? 1 : annotation.geometry.kind === "polyline" ? annotation.geometry.vertices.length : annotation.geometry.triangleIds.length;
    return { source, claim, geometryCount };
  }

  const pendingComplete = !!pending && (pending.kind === "point" ? pending.positions.length === 1 : pending.kind === "polyline" ? pending.positions.length >= 2 : pending.triangleIds.length > 0);

  return (
    <section className="annotation-workbench" aria-labelledby="annotation-heading">
      <header className="annotation-heading">
        <div>
          <p className="eyebrow">T09 · LOCAL REVIEW DRAFTS</p>
          <h3 id="annotation-heading">부착부 annotation 검토 모드</h3>
        </div>
        <span className="badge badge-review">draft · 미검토</span>
      </header>
      <p className="annotation-warning">T05 원문 설명을 참조하는 로컬 제안만 저장합니다. 현재 catalog의 anatomical instances는 0개이므로 이 기록은 canonical SpatialAnnotation으로 승격할 수 없습니다. 좌표·mesh 연결은 anatomy review가 아닙니다.</p>
      <div className="annotation-link-row">
        <label htmlFor="annotation-attachment">연결할 T05 부착 설명</label>
        <select id="annotation-attachment" value={selectedAttachmentId} onChange={(event) => setSelectedAttachmentId(event.currentTarget.value)} disabled={attachmentOptions.length === 0 || activeKind !== null}>
          {attachmentOptions.length === 0 && <option value="">현재 mesh와 일치하는 source 설명 없음</option>}
          {attachmentOptions.map((option) => (
            <option key={option.id} value={option.id}>{roleLabel(option.role)} · {option.summary} · {option.id}</option>
          ))}
        </select>
      </div>
      {activeAttachment && (
        <p className="annotation-source-note" data-testid="annotation-source-note">
          claim {activeAttachment.descriptionClaimId} · {activeAttachment.evidenceIds.length ? activeAttachment.evidenceIds.join(", ") : "근거 ID 미기록"} · {activeAttachment.summary}
        </p>
      )}
      <div className="annotation-tools" role="group" aria-label="도형 종류">
        <label htmlFor="annotation-kind">도형</label>
        <select id="annotation-kind" value={kind} onChange={(event) => setKind(event.currentTarget.value as GeometryKind)} disabled={activeKind !== null}>
          <option value="point">점</option>
          <option value="polyline">선</option>
          <option value="surface_patch">면 패치</option>
        </select>
        <button type="button" onClick={() => beginNew(kind)} disabled={activeKind !== null || !pickedMesh || !activeAttachment || storageBlocked}>새 {geometryLabel(kind)} 입력</button>
        {activeKind && <button type="button" onClick={savePending} disabled={!pendingComplete}>{editingId ? "변경 저장" : "초안 저장"}</button>}
        {activeKind && <button type="button" onClick={cancelDrawing}>취소</button>}
      </div>
      <p className="annotation-message" role="status" aria-live="polite" data-testid="annotation-message">{message}</p>
      <div className="annotation-list" role="list" aria-label="저장된 검토 초안">
        {drafts.length === 0 ? <p className="empty-note">저장된 annotation 초안이 없습니다.</p> : drafts.map((draft) => {
          const { source, claim, geometryCount } = annotationPreview(draft);
          const stale = draft.reviewState === "stale";
          return (
            <article className={`annotation-row ${stale ? "is-stale" : ""}`} key={draft.id} role="listitem" data-annotation-id={draft.id} data-testid="annotation-row">
              <div className="annotation-row-copy">
                <strong>{geometryLabel(draft.geometry.kind)} · {draft.id}</strong>
                <span>{stale ? "stale · 편집/표시 차단" : "draft · review 전"} · {draft.side} · {draft.assetId}</span>
                <span>{source ? `${roleLabel(String(source.role))}: ${claimSummary(claim)}` : draft.attachmentId}</span>
                <code>{geometryCount} vertex/triangle · {draft.topologyHash.slice(0, 12)}…</code>
                {draft.instanceId === null && <span className="annotation-unbound">instance 미생성 — canonical 데이터가 아님</span>}
              </div>
              <div className="annotation-row-actions">
                <button type="button" onClick={() => beginEdit(draft)} disabled={stale || storageBlocked}>편집</button>
                <button type="button" onClick={() => deleteDraft(draft.id)} disabled={storageBlocked}>삭제</button>
              </div>
            </article>
          );
        })}
      </div>
      <div className="annotation-json-actions">
        <button type="button" onClick={exportJson}>JSON 내보내기</button>
        <button type="button" onClick={downloadStoredJson}>JSON text 준비</button>
        <button type="button" onClick={importJson}>JSON 가져오기</button>
        <span>저장소: 이 브라우저의 localStorage · T05/atlas-data 파일은 수정하지 않음</span>
      </div>
      <label className="annotation-json-label" htmlFor="annotation-json">JSON draft 교환</label>
      <textarea id="annotation-json" aria-label="annotation JSON" value={jsonText} onChange={(event) => setJsonText(event.currentTarget.value)} spellCheck={false} />
    </section>
  );
}
