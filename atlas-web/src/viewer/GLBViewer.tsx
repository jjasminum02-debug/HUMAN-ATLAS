import { useEffect, useMemo, useRef, useState } from "react";
import { loadT07ViewerBundle, type T07ViewerBundle } from "./manifest";
import { T07WebGLViewer, type ViewerMesh } from "./glb";
import { AnnotationWorkbench } from "./AnnotationWorkbench";
import type { AtlasRecord } from "../data/catalog";

type Visibility = "visible" | "transparent" | "hidden";
type CameraPreset = "front" | "back" | "lateral";
type Concept = { id: string; entityType?: unknown; parentId?: unknown };

interface Props {
  selectedEntityId: string | null;
  concepts: readonly Concept[];
  attachments: readonly AtlasRecord[];
  claims: readonly AtlasRecord[];
  onSelectEntity: (id: string) => void;
}

function targetNames(mesh: ViewerMesh, conceptById: Map<string, Concept>): { label: string; mapped: boolean } {
  if (mesh.targetEntityId && conceptById.has(mesh.targetEntityId)) {
    return { label: mesh.targetEntityId, mapped: true };
  }
  return { label: mesh.targetEntityId ?? "catalog ID 미확인", mapped: false };
}

function errorText(error: unknown): string {
  return error instanceof Error ? error.message : "T07 GLB viewer를 불러오지 못했습니다.";
}

export function GLBViewer({ selectedEntityId, concepts, attachments, claims, onSelectEntity }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const overlayCanvasRef = useRef<HTMLCanvasElement>(null);
  const viewerRef = useRef<T07WebGLViewer | null>(null);
  const [viewer, setViewer] = useState<T07WebGLViewer | null>(null);
  const [bundle, setBundle] = useState<T07ViewerBundle | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pickedMeshId, setPickedMeshId] = useState<string | null>(null);
  const [visibility, setVisibility] = useState<Record<string, Visibility>>({});
  const [isolating, setIsolating] = useState(false);
  const [cameraPreset, setCameraPreset] = useState<CameraPreset>("front");

  const conceptById = useMemo(() => new Map(concepts.map((concept) => [concept.id, concept])), [concepts]);
  const selectedMeshIds = useMemo(() => {
    if (!bundle || !selectedEntityId) return [];
    const targets = new Set([selectedEntityId]);
    for (const concept of concepts) if (concept.parentId === selectedEntityId) targets.add(concept.id);
    return bundle.meshes
      .filter((mesh) => mesh.targetEntityId !== null && targets.has(mesh.targetEntityId))
      .map((mesh) => mesh.meshAssetId);
  }, [bundle, concepts, selectedEntityId]);
  const pickedMesh = bundle?.meshes.find((mesh) => mesh.meshAssetId === pickedMeshId) ?? null;

  useEffect(() => {
    let active = true;
    loadT07ViewerBundle()
      .then((loaded) => {
        if (active) setBundle(loaded);
      })
      .catch((loadError: unknown) => {
        if (active) setError(errorText(loadError));
      });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!bundle || !canvasRef.current) return;
    let renderer: T07WebGLViewer;
    try {
      renderer = new T07WebGLViewer(canvasRef.current, (mesh) => chooseMesh(mesh, true));
      renderer.setScene(bundle.meshes);
      viewerRef.current = renderer;
      setViewer(renderer);
      setError(null);
    } catch (viewerError) {
      setError(errorText(viewerError));
      return;
    }
    return () => {
      renderer.dispose();
      if (viewerRef.current === renderer) {
        viewerRef.current = null;
        setViewer((current) => current === renderer ? null : current);
      }
    };
    // Renderer construction is tied to the immutable loaded bundle.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [bundle]);

  useEffect(() => {
    const renderer = viewerRef.current;
    if (!renderer || selectedMeshIds.length === 0) return;
    renderer.selectMeshes(selectedMeshIds, true);
    setPickedMeshId((current) => selectedMeshIds.includes(current ?? "") ? current : selectedMeshIds[0]);
  }, [selectedMeshIds]);

  function chooseMesh(mesh: ViewerMesh, updateCard: boolean, focus = true) {
    setPickedMeshId(mesh.meshAssetId);
    viewerRef.current?.selectMeshes([mesh.meshAssetId], focus);
    if (!updateCard || !mesh.targetEntityId) return;
    const target = conceptById.get(mesh.targetEntityId);
    if (target && (target.entityType === "individual_muscle" || target.entityType === "muscle_part")) {
      onSelectEntity(mesh.targetEntityId);
    }
  }

  function applyVisibility(meshId: string, next: Visibility) {
    viewerRef.current?.setVisibility(meshId, next);
    setVisibility((current) => ({ ...current, [meshId]: next }));
  }

  function restoreAll() {
    viewerRef.current?.restoreAll();
    viewerRef.current?.setPreset("front");
    setVisibility({});
    setIsolating(false);
    setCameraPreset("front");
  }

  function toggleIsolation() {
    if (isolating) {
      viewerRef.current?.setIsolation(null);
      setIsolating(false);
      return;
    }
    const targets = selectedMeshIds.length > 0
      ? selectedMeshIds
      : pickedMeshId
        ? [pickedMeshId]
        : [];
    if (targets.length > 0) {
      viewerRef.current?.setIsolation(targets);
      setIsolating(true);
    }
  }

  function chooseCamera(preset: CameraPreset) {
    viewerRef.current?.setPreset(preset);
    setCameraPreset(preset);
  }

  function showAll() {
    viewerRef.current?.fitAll();
    viewerRef.current?.setPreset("front");
    setCameraPreset("front");
  }

  function focusSelected(margin: number) {
    const targets = selectedMeshIds.length > 0 ? selectedMeshIds : pickedMeshId ? [pickedMeshId] : [];
    if (targets.length > 0) viewerRef.current?.focus(targets, margin);
  }

  return (
    <section className="viewer-panel" aria-labelledby="viewer-heading">
      <header className="viewer-heading">
        <div>
          <p className="eyebrow">STATIC 3D PILOT · RIGHT LOWER LEG</p>
          <h2 id="viewer-heading">3D 구조 탐색</h2>
        </div>
        <span className="badge badge-review">mesh 검토 대기</span>
      </header>

      {error ? (
        <div className="viewer-error" role="alert">
          <strong>3D 화면을 열지 못했습니다</strong>
          <p>{error}</p>
          <p className="muted">텍스트 근육 목록과 출처는 계속 사용할 수 있습니다.</p>
        </div>
      ) : (
        <>
          <div className="viewer-canvas-wrap">
            <canvas
              ref={canvasRef}
              className="viewer-canvas"
              aria-label="정적 오른쪽 종아리 mesh. 드래그로 회전, 휠로 확대·축소, 화살표 키로 회전, Home으로 전체 보기"
              tabIndex={0}
              data-testid="anatomy-viewer"
            />
            <canvas ref={overlayCanvasRef} className="viewer-overlay" aria-hidden="true" />
            {!bundle && <div className="viewer-loading" role="status">GLB와 manifest를 확인하고 있습니다…</div>}
            {bundle && <span className="viewer-axis">RH · m · +X 좌 / +Y 머리 / +Z 앞</span>}
          </div>

          <div className="viewer-toolbar" aria-label="카메라와 메시 표시 조작">
            <div className="camera-buttons" role="group" aria-label="카메라 방향">
              <button type="button" aria-pressed={cameraPreset === "front"} onClick={() => chooseCamera("front")}>정면</button>
              <button type="button" aria-pressed={cameraPreset === "back"} onClick={() => chooseCamera("back")}>후면</button>
              <button type="button" aria-pressed={cameraPreset === "lateral"} onClick={() => chooseCamera("lateral")}>우측 측면</button>
            </div>
            <div className="camera-buttons" role="group" aria-label="보기 범위">
              <button type="button" onClick={showAll}>전체 보기</button>
              <button type="button" onClick={() => focusSelected(2.3)}>주변 보기</button>
              <button type="button" onClick={() => focusSelected(1.05)}>선택 구조 확대</button>
            </div>
          </div>

          <div className="viewer-actions">
            <button type="button" className={isolating ? "is-active" : ""} aria-pressed={isolating} onClick={toggleIsolation} disabled={!selectedEntityId && !pickedMeshId}>
              {isolating ? "격리 해제" : "선택만 보기"}
            </button>
            <button type="button" onClick={restoreAll}>모두 복원</button>
            <span className="viewer-help">드래그 회전 · 휠 확대/축소 · 숨김 및 투명 메시를 통한 선택은 차단합니다.</span>
          </div>

          <div className="viewer-selected" aria-live="polite" data-testid="viewer-selection">
            {pickedMesh ? (
              <>
                <span className="eyebrow">선택 메시</span>
                <strong>{pickedMesh.sourceName}</strong>
                <code>{pickedMesh.meshAssetId}</code>
                <span>{targetNames(pickedMesh, conceptById).mapped ? `연결 ID ${pickedMesh.targetEntityId}` : `파일럿 카드 연결 없음 · ${targetNames(pickedMesh, conceptById).label}`}</span>
              </>
            ) : <span className="muted">카드 또는 목록에서 구조를 선택해 보세요.</span>}
          </div>

          <div className="mesh-list-wrap">
            <div className="section-heading mesh-list-heading">
              <div><p className="eyebrow">T07 MESHES</p><h3>이 영역에 확보된 메시</h3></div>
              <span className="section-count">{bundle?.meshes.length ?? 0}</span>
            </div>
            <div className="mesh-list" role="list" aria-label="T07 mesh 목록">
              {bundle?.meshes.map((mesh) => {
                const state = visibility[mesh.meshAssetId] ?? "visible";
                const isolatedOut = isolating && !selectedMeshIds.includes(mesh.meshAssetId) && mesh.meshAssetId !== pickedMeshId;
                return (
                  <div className={`mesh-row ${pickedMeshId === mesh.meshAssetId ? "is-current" : ""} ${state === "hidden" || isolatedOut ? "is-hidden" : ""}`} key={mesh.meshAssetId} role="listitem" data-mesh-id={mesh.meshAssetId}>
                    <button className="mesh-select" type="button" aria-pressed={pickedMeshId === mesh.meshAssetId} onClick={() => chooseMesh(mesh, true)}>
                      <span className="mesh-source-name">{mesh.sourceName}</span>
                      <code>{mesh.meshAssetId}</code>
                      <span className="mesh-link-state">{isolatedOut ? "격리 중 제외" : targetNames(mesh, conceptById).mapped ? `대상 ${mesh.targetEntityId}` : "대상 ID 미확인"}</span>
                    </button>
                    <div className="mesh-controls" aria-label={`${mesh.meshAssetId} 표시 상태`}>
                      <button type="button" aria-pressed={state === "transparent"} onClick={() => applyVisibility(mesh.meshAssetId, state === "transparent" ? "visible" : "transparent")}>
                        {state === "transparent" ? "불투명" : "투명"}
                      </button>
                      <button type="button" aria-pressed={state === "hidden"} onClick={() => applyVisibility(mesh.meshAssetId, state === "hidden" ? "visible" : "hidden")}>
                        {state === "hidden" ? "복원" : "숨김"}
                      </button>
                      <span className="mesh-state-label">{isolatedOut ? "격리" : state === "hidden" ? "숨김" : state === "transparent" ? "투명" : "표시"}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {bundle && (
            <div className="viewer-provenance">
              <strong>{bundle.sourceTitle} · local candidate</strong>
              <span>{bundle.attribution}</span>
              <span>Crosswalk는 provisional / needs_review입니다. 3D 표시·선택은 해부학적 동일성이나 부착 위치의 검토 완료를 뜻하지 않습니다.</span>
            </div>
          )}
          {bundle && (
            <AnnotationWorkbench
              viewer={viewer}
              overlayCanvas={overlayCanvasRef.current}
              assets={bundle.annotationAssets}
              meshes={bundle.meshes}
              concepts={concepts}
              attachments={attachments}
              claims={claims}
              selectedEntityId={selectedEntityId}
              pickedMesh={pickedMesh}
              visibility={visibility}
              onSelectMesh={(mesh) => chooseMesh(mesh, false, false)}
            />
          )}
        </>
      )}
    </section>
  );
}
