import { lazy, Suspense, useEffect, useMemo, useRef, useState } from "react";
import { loadSceneViewerBundle, type T07ViewerBundle } from "./manifest";
import { sceneRevision } from "./scenePlan";
import { SceneRequestCache } from "./sceneCache";
import type { ViewerMesh } from "./glb";
import { ThreeViewer } from "./ThreeViewer";
import { attachmentContextById, attachmentContexts, buildSpatialDraftContext } from "./attachmentContext";
import {
  drawReadOnlySpatialOverlay,
  readSpatialDraftLayer,
  readSyntheticTestSpatialDraftLayer,
  type SpatialDraftLayer,
} from "./spatialDraftLayer";
const AnnotationWorkbench = import.meta.env.DEV ? lazy(() => import("./AnnotationWorkbench").then(module => ({ default: module.AnnotationWorkbench }))) : null;
import type { AtlasRecord } from "../data/catalog";
import { boneSelectionForMesh } from "../domain/regionNavigation";
import type { BoneSelection, NavigationContract, SceneManifest, Selection } from "../domain/navigation";

const sceneCache = new SceneRequestCache<T07ViewerBundle>();

type Visibility = "visible" | "transparent" | "hidden";
type CameraPreset = "front" | "back" | "lateral";
type Concept = { id: string; entityType?: unknown; parentId?: unknown; displayLabel?: string };

interface Props {
  studyMode?: boolean;
  activeAttachmentId?: string | null;
  selectedEntityId: string | null;
  selectedSelection: Selection | null;
  unmappedMeshId?: string | null;
  navigation: NavigationContract;
  scenes: readonly SceneManifest[];
  concepts: readonly Concept[];
  attachments: readonly AtlasRecord[];
  claims: readonly AtlasRecord[];
  onSelectEntity: (id: string) => void;
  onSelectBone: (selection: BoneSelection) => void;
  onSelectUnmappedMesh: (mesh: { meshAssetId: string; sourceName: string }) => void;
  onClearSelection?: () => void;
  onClearAttachment?: () => void;
}

function targetNames(mesh: ViewerMesh, conceptById: Map<string, Concept>): { label: string; mapped: boolean } {
  if (mesh.targetEntityId && conceptById.has(mesh.targetEntityId)) {
    return { label: conceptById.get(mesh.targetEntityId)?.displayLabel ?? "연결된 구조", mapped: true };
  }
  if (mesh.targetEntityType === "structure" && mesh.targetEntityId) {
    return { label: "뼈 연결 확인 중", mapped: false };
  }
  return { label: "구조 연결 확인 중", mapped: false };
}

function errorText(error: unknown): string {
  return error instanceof Error ? error.message : "T07 GLB viewer를 불러오지 못했습니다.";
}

export function GLBViewer({ selectedEntityId, selectedSelection, unmappedMeshId = null, navigation, scenes, concepts, attachments, claims, onSelectEntity, onSelectBone, onSelectUnmappedMesh, onClearSelection, onClearAttachment, studyMode = false, activeAttachmentId = null }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const overlayCanvasRef = useRef<HTMLCanvasElement>(null);
  const viewerRef = useRef<ThreeViewer | null>(null);
  const onMeshPickRef = useRef<(mesh: ViewerMesh) => void>(() => undefined);
  const [viewer, setViewer] = useState<ThreeViewer | null>(null);
  const [bundle, setBundle] = useState<T07ViewerBundle | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pickedMeshId, setPickedMeshId] = useState<string | null>(null);
  const [visibility, setVisibility] = useState<Record<string, Visibility>>({});
  const [isolating, setIsolating] = useState(false);
  const [contextTransparent, setContextTransparent] = useState(false);
  const [bonesVisible, setBonesVisible] = useState(true);
  const [cameraPreset, setCameraPreset] = useState<CameraPreset>("front");
  const [learnerOverlay, setLearnerOverlay] = useState<{ count: number; syntheticTest: boolean; error: boolean }>({ count: 0, syntheticTest: false, error: false });

  const conceptById = useMemo(() => new Map(concepts.map((concept) => [concept.id, concept])), [concepts]);
  const selectedMeshIds = useMemo(() => {
    if (!bundle) return [];
    if (selectedSelection?.kind === "bone") {
      const meshIds = selectedSelection.meshId
        ? [selectedSelection.meshId]
        : navigation.structureMeshMappings.filter((mapping) => mapping.structureInstanceId === selectedSelection.instanceId).flatMap((mapping) => mapping.meshIds);
      return meshIds.filter((id) => bundle.meshes.some((mesh) => mesh.meshAssetId === id));
    }
    if (!selectedEntityId) return [];
    const targets = new Set([selectedEntityId]);
    for (const concept of concepts) if (concept.parentId === selectedEntityId) targets.add(concept.id);
    return bundle.meshes
      .filter((mesh) => mesh.targetEntityId !== null && targets.has(mesh.targetEntityId))
      .map((mesh) => mesh.meshAssetId);
  }, [bundle, concepts, navigation, selectedEntityId, selectedSelection]);
  const pickedMesh = bundle?.meshes.find((mesh) => mesh.meshAssetId === pickedMeshId) ?? null;
  const reviewFocusIds = pickedMesh?.targetEntityType === "structure"
    ? [pickedMesh.meshAssetId]
    : selectedMeshIds.length > 0 ? selectedMeshIds : pickedMeshId ? [pickedMeshId] : [];
  const activeContext = activeAttachmentId ? attachmentContextById.get(activeAttachmentId) : undefined;
  const reviewOwners = new Set([selectedEntityId, ...concepts.filter((concept) => concept.parentId === selectedEntityId).map((concept) => concept.id)]);
  const reviewContexts = attachmentContexts.filter((row) => reviewOwners.has(row.ownerConceptId));
  const spatialContext = useMemo(() => bundle ? buildSpatialDraftContext(bundle.annotationAssets) : null, [bundle]);
  const revision = sceneRevision(scenes);

  useEffect(() => {
    let active = true;
    const controller = new AbortController();
    setBundle(null);
    setError(null);
    setPickedMeshId(null);
    setLearnerOverlay({ count: 0, syntheticTest: false, error: false });
    sceneCache.acquire(revision, (signal) => loadSceneViewerBundle(scenes, signal), controller.signal)
      .then((loaded) => {
        if (active) setBundle(loaded);
      })
      .catch((loadError: unknown) => {
        if (active && !(loadError instanceof DOMException && loadError.name === "AbortError")) setError(errorText(loadError));
      });
    return () => { active = false; controller.abort(); };
    // The revision contains every scene ID and asset hash. A changed revision starts a new request.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [revision]);

  useEffect(() => {
    if (!bundle || !canvasRef.current) return;
    let renderer: ThreeViewer | null = null;
    try {
      renderer = new ThreeViewer(canvasRef.current, (mesh) => onMeshPickRef.current(mesh));
      renderer.setScene(bundle.meshes);
      viewerRef.current = renderer;
      setViewer(renderer);
      setError(null);
    } catch (viewerError) {
      renderer?.dispose();
      setError(errorText(viewerError));
      return;
    }
    const mounted = renderer;
    return () => {
      mounted.dispose();
      if (viewerRef.current === mounted) {
        viewerRef.current = null;
        setViewer((current) => current === mounted ? null : current);
      }
    };
    // Renderer construction is tied to the immutable loaded bundle.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [bundle]);

  useEffect(() => {
    const renderer = viewerRef.current;
    if (!renderer) return;
    if (selectedMeshIds.length === 0) {
      const pendingMesh = unmappedMeshId && bundle?.meshes.some((mesh) => mesh.meshAssetId === unmappedMeshId) ? unmappedMeshId : null;
      renderer.selectMeshes(pendingMesh ? [pendingMesh] : [], false);
      setPickedMeshId(pendingMesh);
      if (!selectedSelection && !selectedEntityId && !unmappedMeshId) {
        renderer.setIsolation(null);
        setIsolating(false);
      }
      return;
    }
    renderer.selectMeshes(selectedMeshIds, !studyMode);
    if (studyMode) renderer.focus(selectedMeshIds, 1.4);
    setPickedMeshId((current) => selectedMeshIds.includes(current ?? "") ? current : selectedMeshIds[0]);
  }, [bundle, selectedMeshIds, studyMode, unmappedMeshId]);

  useEffect(() => {
    if (!studyMode || !viewer) return;
    const contextId = activeContext?.contextMeshAssetId;
    if (contextId && bundle?.meshes.some((mesh) => mesh.meshAssetId === contextId)) {
      viewer.selectMeshes([...selectedMeshIds, contextId]);
      setPickedMeshId(contextId);
    } else if (selectedMeshIds.length > 0) {
      viewer.selectMeshes(selectedMeshIds);
      viewer.focus(selectedMeshIds, 1.4);
      setPickedMeshId(selectedMeshIds[0]);
    }
  }, [activeContext, bundle, selectedMeshIds, studyMode, viewer]);

  useEffect(() => {
    if (!studyMode || !bundle || !viewer) return;
    for (const mesh of bundle.meshes) {
      const emphasized = selectedMeshIds.includes(mesh.meshAssetId) || mesh.meshAssetId === activeContext?.contextMeshAssetId;
      const state = mesh.targetEntityType === "structure"
        ? mesh.meshAssetId === activeContext?.contextMeshAssetId ? "visible" : bonesVisible ? activeContext ? "transparent" : "visible" : "hidden"
        : activeContext?.contextMeshAssetId ? "transparent" : contextTransparent && !emphasized ? "transparent" : "visible";
      viewer.setVisibility(mesh.meshAssetId, state);
    }
  }, [studyMode, bundle, viewer, contextTransparent, bonesVisible, selectedMeshIds, activeContext]);

  useEffect(() => {
    if (!studyMode || !bundle || !viewer || !spatialContext || !overlayCanvasRef.current) return;
    const canvas = overlayCanvasRef.current;
    const ownerIds = new Set([selectedEntityId, ...concepts.filter((row) => row.parentId === selectedEntityId).map((row) => row.id)].filter((id): id is string => !!id));
    let active = true;
    let layer: SpatialDraftLayer | null = null;
    const testPreview = import.meta.env.DEV && new URL(window.location.href).searchParams.get("__t13bTestOverlay") === "1";
    const redraw = () => {
      if (!active || !layer) return;
      const count = drawReadOnlySpatialOverlay(canvas, viewer, layer.records, spatialContext.t13Records, ownerIds);
      setLearnerOverlay({ count, syntheticTest: testPreview && layer.syntheticFixture && layer.records.length > 0, error: false });
    };
    const load = async () => {
      try {
        layer = testPreview
          ? await readSyntheticTestSpatialDraftLayer(window.localStorage, spatialContext)
          : await readSpatialDraftLayer(window.localStorage, spatialContext);
        if (!active) return;
        redraw();
      } catch {
        if (!active) return;
        layer = null;
        const context = canvas.getContext("2d");
        context?.clearRect(0, 0, canvas.width, canvas.height);
        setLearnerOverlay({ count: 0, syntheticTest: false, error: true });
      }
    };
    const onStorage = (event: StorageEvent) => {
      if (event.key === null || event.key === (testPreview ? "human-atlas:t13b:test-only:spatial-drafts" : "human-atlas:t13b:spatial-drafts:v1")) void load();
    };
    const onLayerChanged = () => { void load(); };
    const frame = () => redraw();
    void load();
    viewer.setFrameCallback(frame);
    window.addEventListener("storage", onStorage);
    window.addEventListener("human-atlas:spatial-draft-layer-changed", onLayerChanged);
    return () => {
      active = false;
      viewer.setFrameCallback(null);
      window.removeEventListener("storage", onStorage);
      window.removeEventListener("human-atlas:spatial-draft-layer-changed", onLayerChanged);
      const context = canvas.getContext("2d");
      context?.clearRect(0, 0, canvas.width, canvas.height);
    };
  }, [bundle, concepts, selectedEntityId, spatialContext, studyMode, viewer]);

  function chooseMesh(mesh: ViewerMesh, updateCard: boolean, focus = true) {
    if (isolating) {
      viewerRef.current?.setIsolation(null);
      setIsolating(false);
    }
    setPickedMeshId(mesh.meshAssetId);
    viewerRef.current?.selectMeshes([mesh.meshAssetId], focus);
    if (!updateCard) return;
    const sceneBinding = scenes.flatMap((scene) => scene.selectableBindings)
      .find((binding) => binding.meshAssetId === mesh.meshAssetId);
    if (sceneBinding?.selection.kind === "muscle") {
      const entityId = sceneBinding.selection.partId ?? sceneBinding.selection.conceptId;
      const target = conceptById.get(entityId);
      if (target && (target.entityType === "individual_muscle" || target.entityType === "muscle_part")) {
        onSelectEntity(entityId);
        return;
      }
    }
    const boneSelection = boneSelectionForMesh(navigation, mesh.meshAssetId);
    if (boneSelection) {
      onSelectBone(boneSelection);
      return;
    }
    onSelectUnmappedMesh({ meshAssetId: mesh.meshAssetId, sourceName: studyMode ? "연결 확인이 필요한 모델 구성요소" : mesh.sourceName });
  }
  onMeshPickRef.current = (mesh) => chooseMesh(mesh, true);

  function applyVisibility(meshId: string, next: Visibility) {
    viewerRef.current?.setVisibility(meshId, next);
    setVisibility((current) => ({ ...current, [meshId]: next }));
  }

  function restoreAll() {
    viewerRef.current?.restoreAll();
    viewerRef.current?.setPreset("front");
    if (studyMode) {
      onClearAttachment?.();
      if (selectedMeshIds.length > 0) {
        viewerRef.current?.selectMeshes(selectedMeshIds);
        viewerRef.current?.focus(selectedMeshIds, 1.4);
        setPickedMeshId(selectedMeshIds[0]);
      }
    }
    setVisibility({});
    setContextTransparent(false);
    setBonesVisible(true);
    setIsolating(false);
    setCameraPreset("front");
  }

  function toggleIsolation() {
    if (isolating) {
      viewerRef.current?.setIsolation(null);
      setIsolating(false);
      return;
    }
    const targets = reviewFocusIds;
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
    const targets = reviewFocusIds;
    if (targets.length > 0) viewerRef.current?.focus(targets, margin);
  }

  if (studyMode) return <section className="study-viewer" aria-label="3D 근육과 뼈 탐색">
    <div className={`study-canvas-wrap ${bundle && selectedSelection && selectedMeshIds.length === 0 ? "no-model" : ""}`}>
      <div className="study-canvas-stage">
        <canvas ref={canvasRef} className="viewer-canvas" tabIndex={0} aria-label="근육과 뼈 모형. 드래그로 회전, 휠로 확대, 화살표 키로 회전" data-testid="anatomy-viewer"/>
        <canvas ref={overlayCanvasRef} className="viewer-overlay" aria-hidden="true" data-testid="learner-spatial-overlay"/>
        {learnerOverlay.syntheticTest && <span className="learner-overlay-warning" role="status">합성 검증 미리보기 · 학습 자료가 아닙니다</span>}
        {!learnerOverlay.syntheticTest && learnerOverlay.count > 0 && <span className="learner-overlay-warning" role="status">미검토 표면 후보가 읽기 전용으로 표시됩니다</span>}
        {learnerOverlay.error && <span className="learner-overlay-warning" role="status">공간 초안을 확인하지 못해 표시를 보류했습니다</span>}
      </div>
      {error ? <div className="model-message" role="alert"><h3>3D를 불러오지 못했습니다</h3><p>근육 설명과 검색은 계속 이용할 수 있습니다.</p></div> : !bundle ? <div className="model-message" role="status">모형을 불러오는 중…</div> : selectedSelection && selectedMeshIds.length === 0 ? <div className="model-message"><span>◎</span><h3>선택 구조의 3D는 준비 중입니다</h3><p>오른쪽 카드에서 이름과 자료 상태를 확인할 수 있습니다.</p></div> : null}
    </div>
    {bundle && <>
      <div className="study-camera" aria-label="모형 방향">
        {(["front", "back", "lateral"] as CameraPreset[]).map(preset => <button key={preset} aria-pressed={cameraPreset === preset} onClick={() => chooseCamera(preset)}>{{front:"정면",back:"후면",lateral:"측면"}[preset]}</button>)}
      </div>
      <div className="study-view-tools" aria-label="모형 보기">
        <button aria-pressed={isolating} onClick={toggleIsolation}>선택만 보기</button>
        <button aria-pressed={contextTransparent} onClick={() => setContextTransparent(v => !v)}>주변 투명하게</button>
        <button aria-pressed={bonesVisible} onClick={() => setBonesVisible(v => !v)}>뼈</button>
        <button onClick={showAll}>전체 보기</button>
        <button onClick={restoreAll}>보기 초기화</button>
        <button onClick={onClearSelection} disabled={!selectedSelection && !unmappedMeshId}>선택 해제</button>
      </div>
      <p className="study-gesture">드래그하여 회전 · 스크롤하여 확대</p>
      {activeContext && <p className="study-attachment-context" role="status">{activeContext.contextMeshAssetId
        ? "관련 뼈 전체를 검토 대상으로 강조했습니다. 정확한 부착 영역은 아직 표시되지 않습니다."
        : "이 설명의 표적 구조는 현재 3D 자산에 없습니다. 부착 영역 표시는 보류했습니다."}</p>}
    </>}
  </section>;

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
            {bundle && !studyMode && <span className="viewer-axis">RH · m · +X 좌 / +Y 머리 / +Z 앞</span>}
            {studyMode && learnerOverlay.syntheticTest && <span className="learner-overlay-warning" role="status">합성 검증 미리보기 · 학습 자료가 아닙니다</span>}
            {studyMode && !learnerOverlay.syntheticTest && learnerOverlay.count > 0 && <span className="learner-overlay-warning" role="status">미검토 표면 후보가 읽기 전용으로 표시됩니다</span>}
            {studyMode && learnerOverlay.error && <span className="learner-overlay-warning" role="status">공간 초안을 확인하지 못해 표시를 보류했습니다</span>}
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
                <strong>{studyMode ? targetNames(pickedMesh, conceptById).label : pickedMesh.sourceName}</strong>
                {!studyMode && <code>{pickedMesh.meshAssetId}</code>}
                <span>{studyMode
                  ? targetNames(pickedMesh, conceptById).mapped ? "선택한 학습 구조" : "학습 카드 연결을 확인하지 못했습니다."
                  : targetNames(pickedMesh, conceptById).mapped ? `연결 ID ${pickedMesh.targetEntityId}` : `파일럿 카드 연결 없음 · ${targetNames(pickedMesh, conceptById).label}`}</span>
              </>
            ) : <span className="muted">카드 또는 목록에서 구조를 선택해 보세요.</span>}
          </div>

          <div className="mesh-list-wrap">
            <div className="section-heading mesh-list-heading">
              <div><p className="eyebrow">{studyMode ? "학습 구조" : "SOURCE MESHES"}</p><h3>{studyMode ? "선택 가능한 구조" : "이 영역에 확보된 메시"}</h3></div>
              <span className="section-count">{bundle?.meshes.filter((mesh) => !studyMode || (mesh.targetEntityId !== null && conceptById.has(mesh.targetEntityId))).length ?? 0}</span>
            </div>
            {studyMode && <p className="learner-mesh-note">연결이 확인되지 않은 일부 모델 구성요소는 선택 카드에 표시하지 않습니다.</p>}
            <div className="mesh-list" role="list" aria-label={studyMode ? "선택 가능한 학습 구조" : "원본 mesh 목록"}>
              {bundle?.meshes.filter((mesh) => !studyMode || (mesh.targetEntityId !== null && conceptById.has(mesh.targetEntityId))).map((mesh) => {
                const state = visibility[mesh.meshAssetId] ?? "visible";
                const isolatedOut = isolating && !reviewFocusIds.includes(mesh.meshAssetId);
                const displayName = studyMode ? targetNames(mesh, conceptById).label : mesh.sourceName;
                return (
                  <div className={`mesh-row ${pickedMeshId === mesh.meshAssetId ? "is-current" : ""} ${state === "hidden" || isolatedOut ? "is-hidden" : ""}`} key={mesh.meshAssetId} role="listitem" {...(!studyMode ? { "data-mesh-id": mesh.meshAssetId } : {})}>
                    <button className="mesh-select" type="button" aria-pressed={pickedMeshId === mesh.meshAssetId} aria-label={`${displayName} 선택`} onClick={() => chooseMesh(mesh, true)}>
                      <span className="mesh-source-name">{displayName}</span>
                      {!studyMode && <code>{mesh.meshAssetId}</code>}
                      <span className="mesh-link-state">{studyMode ? "확인된 학습 구조" : isolatedOut ? "격리 중 제외" : targetNames(mesh, conceptById).mapped ? `대상 ${mesh.targetEntityId}` : mesh.targetEntityId ? `구조 후보 ${mesh.targetEntityId}` : "대상 ID 미확인"}</span>
                    </button>
                    <div className="mesh-controls" aria-label={`${displayName} 표시 상태`}>
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

          {bundle && reviewContexts.length > 0 && <section className="attachment-review-context" aria-label="부착 표면 검토 대상">
            <h3>부착 표면 검토 대상</h3>
            <p>원문 설명과 관련 뼈 전체를 연결했습니다. 면·선·점 좌표는 아직 기록되지 않았습니다.</p>
            <ul>{reviewContexts.map((row) => {
              const claim = claims.find((item) => item.id === row.descriptionClaimId);
              const value = claim?.value;
              const summary = value && typeof value === "object" && "summary" in value && typeof value.summary === "string" ? value.summary : row.targetStructureId;
              const mesh = bundle.meshes.find((item) => item.meshAssetId === row.contextMeshAssetId);
              return <li key={row.attachmentId}>
                <span>{row.role === "origin" ? "기시" : row.role === "insertion" ? "정지" : "그 외 부착"} · {summary}</span>
                {mesh ? <button type="button" onClick={() => chooseMesh(mesh, true)}>관련 뼈 선택 · 표면 미지정</button> : <em>대상 메시 없음 · 보류</em>}
              </li>;
            })}</ul>
          </section>}

          {bundle && (
            <div className="viewer-provenance">
              <strong>{bundle.sourceTitle} · local candidate</strong>
              <span>{bundle.attribution}</span>
              <span>Crosswalk는 provisional / needs_review입니다. 3D 표시·선택은 해부학적 동일성이나 부착 위치의 검토 완료를 뜻하지 않습니다.</span>
            </div>
          )}
          {!studyMode && bundle && AnnotationWorkbench && (
            <Suspense fallback={<p>제작 도구를 불러오는 중…</p>}><AnnotationWorkbench
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
            /></Suspense>
          )}
        </>
      )}
    </section>
  );
}
