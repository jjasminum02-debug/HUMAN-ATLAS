import { lazy, Suspense, useEffect, useMemo, useRef, useState } from 'react';
import { AnatomySceneController, type BodyProgress } from './AnatomySceneController';
import { type LayerId } from './contract';
import './wholeBody.css';
import '../acupoints/entry.css';
import { DatasetSceneAdapter } from '../datasets/DatasetSceneAdapter';
import { layerIdOf } from '../datasets/presentation';
import type { Dataset } from '../datasets/schema';
import type { RuntimeIntegration } from '../datasets/integration';
import { AtlasLoading } from '../../ui/AtlasLoading';
import { motorRelationsForNerve, nerveConceptForSourceName } from '../../data/learning';
import { MovementPanel } from './MovementPanel';
import { SectionPanel } from './SectionPanel';
import type { Section } from '../section';

const AcupointReview = lazy(() => import('../acupoints/AcupointEntry.tsx'));
const SkinControls = lazy(() => import('../skin/SkinControls.tsx'));
const acupointDevelopmentReview = import.meta.env.DEV && new URLSearchParams(window.location.search).get('acupointReview') === '1';
const surfaceSample = import.meta.env.DEV && new URLSearchParams(window.location.search).get('carrierSample') === '1';
const territoryDevelopmentReview = import.meta.env.DEV && window.location.pathname === '/review' && new URLSearchParams(window.location.search).get('territories') === '1';
/** Outer to inner: the order "한 겹 벗기기" removes layers in. Bone and nerve are never peeled. */
const PEEL_ORDER: LayerId[] = ['fascia', 'superficialMuscle', 'deepMuscle', 'joint'];
const LAYER_LABELS: Record<LayerId, string> = { fascia: '근막', superficialMuscle: '얕은 근육', deepMuscle: '깊은 근육', joint: '인대·관절', bone: '뼈', nerve: '신경', vessel: '혈관' };
const DEFAULT_LAYERS: Record<LayerId, boolean> = { fascia: false, superficialMuscle: true, deepMuscle: true, joint: false, bone: true, nerve: false, vessel: false };

export function WholeBodyViewer({ attachmentRole = null, homeRevision = 0, viewResetRevision = 0, datasetSource, regionIds, selectedId, selectedIds, onSelect, onEntered, onMotionHostChange, onMuscleLayerChange, onBoneLayerChange, onSelectionHiddenChange }: { attachmentRole?: 'origin' | 'insertion' | null; homeRevision?: number; viewResetRevision?: number; datasetSource: { dataset: Dataset; integration: RuntimeIntegration }; onEntered?: (value: boolean) => void; onMotionHostChange?: (host: DatasetSceneAdapter | null) => void; onMuscleLayerChange?: (enabled: boolean) => void; onBoneLayerChange?: (enabled: boolean) => void; onSelectionHiddenChange?: (hidden: boolean) => void; whole: boolean; onWholeChange: (value: boolean) => void; regionIds: string[]; selectedId: string | null; selectedIds: string[]; onSelect: (id: string, side: string | null) => void }) {
  const host = useRef<HTMLDivElement>(null);
  const tools = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const element = tools.current;
    if (!element) return;
    // Defer layout writes outside ResizeObserver delivery; keep the shared scene clock unchanged.
    let pending: ReturnType<typeof setTimeout> | undefined;
    const measure = () => {
      pending = undefined;
      const parent = element.parentElement;
      const height = `${element.getBoundingClientRect().height}px`;
      if (parent && parent.style.getPropertyValue('--view-tools-height') !== height) {
        parent.style.setProperty('--view-tools-height', height);
      }
    };
    const observer = new ResizeObserver(() => {
      if (pending === undefined) pending = setTimeout(measure, 0);
    });
    observer.observe(element); measure();
    return () => { observer.disconnect(); clearTimeout(pending); };
  }, []);
  const controller = useRef<AnatomySceneController | DatasetSceneAdapter | null>(null);
  const previousView = useRef<{ regionKey: string; selectedId: string | null; resetRevision: number } | null>(null);
  const select = useRef(onSelect); select.current = onSelect;
  const [layers, setLayers] = useState(DEFAULT_LAYERS);
  const [sectionOpen, setSectionOpen] = useState(false);
  const [section, setSection] = useState<Section | null>(null);
  const [peeled, setPeeled] = useState<LayerId[]>([]);
  const [layerOpacity, setLayerOpacity] = useState<Partial<Record<LayerId, number>>>({});
  const [moreOpen, setMoreOpen] = useState(false);
  const [shading, setShading] = useState<boolean | null>(null);
  const [movementOpen, setMovementOpen] = useState(false);
  const [movementRequest, setMovementRequest] = useState<{ jointId: string; revision: number } | null>(null);
  const rowsByKey = useMemo(() => new Map((datasetSource.integration.objects ?? []).map(r => [r.sourceKey, r])), [datasetSource]);
  const sceneOf = () => { const c = controller.current; return c instanceof DatasetSceneAdapter ? c.scene : c; };
  const toggleShading = () => { const scene = sceneOf(); if (!scene) return; scene.ambientOcclusion = !scene.ambientOcclusion; setShading(scene.ambientOcclusion); };
  const bones = layers.bone, nerves = layers.nerve, muscles = layers.superficialMuscle || layers.deepMuscle;
  const setNerves = (on: boolean) => setLayers(previous => ({ ...previous, nerve: on }));
  const toggleLayer = (id: LayerId) => { setPeeled([]); setLayers(previous => ({ ...previous, [id]: !previous[id] })); };
  const peelTarget = PEEL_ORDER.find(id => layers[id]);
  const peel = () => { if (!peelTarget) return; setPeeled(previous => [...previous, peelTarget]); setLayers(previous => ({ ...previous, [peelTarget]: false })); };
  const unpeel = () => { const last = peeled[peeled.length - 1]; if (!last) return; setPeeled(previous => previous.slice(0, -1)); setLayers(previous => ({ ...previous, [last]: true })); };
  const firstLayerRender = useRef(true);
  useEffect(() => {
    if (firstLayerRender.current) { firstLayerRender.current = false; return; }
    onMuscleLayerChange?.(muscles);
  }, [muscles]); // eslint-disable-line react-hooks/exhaustive-deps
  const firstBoneRender = useRef(true);
  useEffect(() => {
    if (firstBoneRender.current) { firstBoneRender.current = false; return; }
    onBoneLayerChange?.(bones);
  }, [bones]); // eslint-disable-line react-hooks/exhaustive-deps
  const nerveLayerExplicitlyOff = useRef(false);
  const selectedSourceRow = datasetSource.integration.objects.find(r => r.sourceKey === selectedId);
  const selectedNerve = selectedSourceRow?.nerve;
  const nerveConceptMuscleKeys = useMemo(() => {
    if (selectedSourceRow?.kind !== 'nerve') return [];
    const concept = nerveConceptForSourceName(selectedSourceRow.names.en);
    if (!concept) return [];
    const targets = new Set(motorRelationsForNerve(concept.key, selectedSourceRow.side).flatMap(r => r.targetSourceKeys));
    return (datasetSource.integration.objects ?? []).filter(r => targets.has(r.sourceKey) && r.kind === 'muscle'
      && r.localDisplayEligible && r.side === selectedSourceRow.side).map(r => r.sourceKey);
  }, [datasetSource, selectedSourceRow]);
  useEffect(() => {
    // Selecting a structure (e.g. from search) turns its layer on; nerves keep their own rule below.
    const layer = selectedSourceRow && selectedSourceRow.kind !== 'nerve' ? layerIdOf(selectedSourceRow) : null;
    if (layer) setLayers(previous => previous[layer] ? previous : { ...previous, [layer]: true });
  }, [selectedSourceRow?.sourceKey]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    // Initial nerve selection is visible; an explicit learner layer-off persists.
    if (selectedNerve && !nerveLayerExplicitlyOff.current) setNerves(true);
  }, [selectedNerve]);
  const staticPose = datasetSource.integration.objects.find(r => r.nerve)?.nerve?.poseId;
  const [acupointsActive, setAcupointsActive] = useState(false);
  type Presentation = { observeNerves: boolean; highlightInnervation: boolean; dim: boolean; isolated: boolean; hidden: string[]; translucent: string[] };
  const [presentation, setPresentation] = useState<Presentation>({ observeNerves: true, highlightInnervation: true, dim: true, isolated: false, hidden: [], translucent: [] });
  useEffect(() => { onSelectionHiddenChange?.(Boolean(selectedId && presentation.hidden.includes(selectedId))); }, [selectedId, presentation.hidden, onSelectionHiddenChange]);
  const updatePresentation = (next: Presentation) => setPresentation(next);
  useEffect(() => {
    updatePresentation({ observeNerves: true, highlightInnervation: true, dim: true, isolated: false, hidden: [], translucent: [] });
  }, [viewResetRevision]);
  const [revision, setRevision] = useState(0);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState(false);
  const [progress, setProgress] = useState<BodyProgress | null>(null);
  const [entered, setEntered] = useState(false);
  const stopEntrance = () => {
    const current = controller.current;
    const scene = current instanceof DatasetSceneAdapter ? current.scene : current;
    scene?.stopEntrance();
  };
  useEffect(() => { onEntered?.(entered); }, [entered, onEntered]);
  useEffect(() => {
    if (!entered) return;
    const current = controller.current;
    const scene = current instanceof DatasetSceneAdapter ? current.scene : current;
    scene?.startEntrance();
  }, [entered]);
  useEffect(() => {
    if (progress && progress.calls > 0 && (progress.loaded === progress.total || progress.failed > 0)) setEntered(true);
  }, [progress]);
  useEffect(() => {
    const abort = new AbortController(); let current: AnatomySceneController | DatasetSceneAdapter | null = null;
    setError(false); setReady(false); setProgress(null); setEntered(false); previousView.current = null;
    const timeout = window.setTimeout(() => { abort.abort(); setError(true); }, 20000);
    if (!host.current) return;
    window.clearTimeout(timeout);
    current = new DatasetSceneAdapter(host.current, datasetSource.dataset, datasetSource.integration, setProgress, (id, side) => select.current(id, side));
    controller.current = current; onMotionHostChange?.(current); setReady(true);
    return () => { abort.abort(); onMotionHostChange?.(null); current?.dispose(); controller.current = null; };
  }, [revision, datasetSource, onMotionHostChange]);
  useEffect(() => {
    if (!ready) return;
    stopEntrance();
    const regionKey = JSON.stringify(regionIds);
    const previous = previousView.current;
    controller.current?.setView({ region: null, regionIds, selectedId, selectedIds, bones, muscles, nerves,
      fascia: layers.fascia, joints: layers.joint, vessels: layers.vessel, superficialMuscles: layers.superficialMuscle, deepMuscles: layers.deepMuscle, layerOpacity, attachmentObservation: attachmentRole && selectedId ? {sourceKey: selectedId, role: attachmentRole} : null, poseId: staticPose, nerveConceptMuscleKeys, observeNerves: presentation.observeNerves, highlightInnervation: presentation.highlightInnervation, supplements: false, dim: presentation.dim, isolate: presentation.isolated && Boolean(selectedId), hiddenSourceKeys: presentation.hidden, translucentSourceKeys: presentation.translucent });
    const nerveFramed = controller.current instanceof DatasetSceneAdapter && selectedNerve && nerves
      && !presentation.hidden.includes(selectedId ?? '');
    if (previous === null) {
      // The adapter already fit a supported nerve deep link before its opening orbit.
      if (regionIds.length > 0 && !nerveFramed) controller.current?.focus(regionIds, false);
    } else if (previous.regionKey !== regionKey || previous.resetRevision !== viewResetRevision) {
      if (nerveFramed) controller.current?.focusSelection(true);
      else controller.current?.focus(regionIds);
    }
    previousView.current = { regionKey, selectedId, resetRevision: viewResetRevision };
  }, [ready, regionIds, selectedId, selectedIds, layers, layerOpacity, staticPose, nerveConceptMuscleKeys, presentation, attachmentRole, viewResetRevision]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { if (ready && homeRevision > 0) { stopEntrance(); controller.current?.focus([]); } }, [ready, homeRevision]);
  useEffect(() => { const c = controller.current; if (ready && c instanceof DatasetSceneAdapter) c.setSection(section); }, [ready, section]);
  // Bookmarks capture and restore what this viewer owns (layers, opacity, section); the scene adds the camera.
  const studyState = useRef({ layers, layerOpacity, section }); studyState.current = { layers, layerOpacity, section };
  useEffect(() => {
    const c = controller.current;
    if (!ready || !(c instanceof DatasetSceneAdapter)) return;
    return c.registerStudyView(() => ({ layers: { ...studyState.current.layers }, layerOpacity: { ...studyState.current.layerOpacity } as Record<string, number>,
      section: studyState.current.section ? { ...studyState.current.section } : null }), view => {
      setPeeled([]);
      setLayers(previous => ({ ...previous, ...Object.fromEntries(Object.entries(view.layers).filter(([id]) => id in previous)) }));
      setLayerOpacity(view.layerOpacity as Partial<Record<LayerId, number>>);
      setSection(view.section as Section | null); setSectionOpen(Boolean(view.section));
    });
  }, [ready]);
  useEffect(() => {
    const c = controller.current;
    if (!ready || !(c instanceof DatasetSceneAdapter)) return;
    // A joint card's "움직여 보기" opens this panel on that joint.
    return c.onOpenMovement(jointId => { setMovementOpen(true); setMovementRequest(previous => ({ jointId, revision: (previous?.revision ?? 0) + 1 })); });
  }, [ready]);
  return <div className="whole-body-viewer" onPointerDownCapture={stopEntrance}>
    <div className="whole-body-canvas" inert={!entered} aria-hidden={!entered} ref={host}/>
    {entered && AcupointReview && controller.current instanceof DatasetSceneAdapter && <Suspense fallback={null}><AcupointReview adapter={controller.current} onModeChange={setAcupointsActive} surfaceSample={surfaceSample} developmentReview={acupointDevelopmentReview} territoryDevelopmentReview={territoryDevelopmentReview}/></Suspense>}
    {!entered && <AtlasLoading failed={error || Boolean(progress?.failed)} loaded={progress?.loaded} total={progress?.total} onRetry={() => error ? setRevision(r => r + 1) : controller.current?.retry()}/> }
    <div inert={!entered} ref={tools} className="body-tools" aria-label="모형 보기 설정">
      <span className="view-options-label">보기 옵션</span>
      {/* V3: one compact toolbar — layers first, then peel/fit; secondary options behind 더보기. */}
      <div className="toolbar-main">
      <div className="layer-row" role="group" aria-label="구조 층">
        {(Object.keys(LAYER_LABELS) as LayerId[]).filter(id => id !== 'nerve' || staticPose).map(id => <button key={id} aria-pressed={layers[id]}
          onClick={() => { if (id === 'nerve') nerveLayerExplicitlyOff.current = nerves; toggleLayer(id); }}>{LAYER_LABELS[id]}</button>)}
      </div>
        <div className="view-options-row">
        <button disabled={!peelTarget} title="바깥쪽 층부터 하나씩 숨겨 안쪽 구조를 봅니다." onClick={peel}>한 겹 벗기기</button>
        <button disabled={!peeled.length} onClick={unpeel}>벗긴 층 되돌리기</button>
        <button onClick={() => {const c=controller.current;if(c instanceof DatasetSceneAdapter&&c.scene.handleObservationFit('all'))return;c?.focus(regionIds);}}>화면 맞춤</button>
          <button aria-expanded={movementOpen} aria-controls="movement-panel" title="관절을 움직이고 작용 근육을 색으로 봅니다." onClick={() => setMovementOpen(open => !open)}>관절 움직임</button>
          <button aria-expanded={sectionOpen} aria-pressed={Boolean(section)} aria-controls="section-panel" title="모형을 한 면에서 잘라 속을 봅니다." onClick={() => setSectionOpen(open => !open)}>단면</button>
          <button aria-expanded={moreOpen} aria-controls="view-more" onClick={() => setMoreOpen(open => !open)}>더보기</button>
        </div>
      </div>
      {moreOpen && <div className="more-panel" id="view-more">
        <div className="more-actions">
        <button aria-pressed={shading ?? Boolean(ready && sceneOf()?.ambientOcclusion)} title="멈춰 있을 때 구조 사이의 그늘을 그립니다. 느린 기기에서는 꺼 주세요." onClick={toggleShading}>음영 효과</button>
        {entered && controller.current instanceof DatasetSceneAdapter && <Suspense fallback={null}><SkinControls adapter={controller.current} acupoints={acupointsActive}/></Suspense>}
        </div>
        <div className="layer-opacity" id="layer-opacity" role="group" aria-label="층 투명도">
        {(Object.keys(LAYER_LABELS) as LayerId[]).filter(id => layers[id]).map(id => <label key={id}><span>{LAYER_LABELS[id]}</span>
          <input type="range" min={10} max={100} step={5} value={Math.round((layerOpacity[id] ?? 1) * 100)}
            onChange={event => setLayerOpacity(previous => ({ ...previous, [id]: Number(event.target.value) / 100 }))}/>
          <output>{Math.round((layerOpacity[id] ?? 1) * 100)}%</output></label>)}
        </div>
      </div>}
      {sectionOpen && entered && controller.current instanceof DatasetSceneAdapter && <SectionPanel section={section} bounds={controller.current.sectionBounds()}
        onChange={setSection} onFace={() => (controller.current as DatasetSceneAdapter).faceSection()}/>}
      {movementOpen && entered && controller.current instanceof DatasetSceneAdapter && <MovementPanel host={controller.current} rows={rowsByKey}
        request={movementRequest} musclesVisible={muscles} onSelect={key => select.current(key, rowsByKey.get(key)?.side ?? null)}/>}
      {selectedId && <div className="selection-view-options">
        {!selectedNerve && <button disabled={!selectedId} aria-pressed={presentation.dim} onClick={() => updatePresentation({ ...presentation, dim: !presentation.dim })}>선택 강조</button>}
        <button disabled={!selectedId || Boolean(selectedNerve) || !progress?.selectedAvailable || presentation.hidden.includes(selectedId)} title="선택한 구조를 숨겨 안쪽 구조를 봅니다." onClick={() => selectedId && setPresentation(previous => previous.hidden.includes(selectedId) ? previous : { ...previous, hidden: [...previous.hidden, selectedId] })}>선택 숨기기</button>
        <button disabled={!selectedId || !progress?.selectedAvailable} onClick={() => {const c=controller.current;if(c instanceof DatasetSceneAdapter&&c.scene.handleObservationFit('selection'))return;c?.focusSelection();}}>선택 맞춤</button>
        {selectedNerve ? (selectedNerve.muscleKeys.length > 0 || nerveConceptMuscleKeys.length > 0) && <button disabled={!nerves} aria-pressed={presentation.highlightInnervation} onClick={() => updatePresentation({ ...presentation, highlightInnervation: !presentation.highlightInnervation })}>관련 근육 강조</button> : <button disabled={!selectedId || (!progress?.selectedAvailable && !presentation.translucent.includes(selectedId))} aria-pressed={Boolean(selectedId && presentation.translucent.includes(selectedId))} onClick={() => selectedId && updatePresentation({ ...presentation, translucent: presentation.translucent.includes(selectedId) ? presentation.translucent.filter(id => id !== selectedId) : [...presentation.translucent, selectedId] })}>선택 반투명</button>}
      </div>}
    </div>
    <div className="body-status" inert={!entered} aria-hidden={!entered} role="status" aria-live="polite">
      {error ? <><span>이 환경에서 모형 자료를 열 수 없습니다.</span><button onClick={() => setRevision(r => r + 1)}>다시 시도</button></>
        : !ready ? '모형을 준비하고 있습니다…'
        : progress?.contextLost ? '그래픽 연결을 복원하고 있습니다. 현재 시점과 선택을 유지합니다.'
        : progress?.failed ? <><span>일부 모형을 불러오지 못했습니다. 표시 중인 모형은 계속 살펴볼 수 있습니다.</span><button onClick={() => controller.current?.retry()}>다시 불러오기</button></>
        : progress && progress.loaded < progress.total ? `모형 불러오는 중 · ${progress.loaded}/${progress.total}`
        : !Object.values(layers).some(Boolean) ? '보기 옵션에서 볼 구조 층을 켜 주세요.'
        : selectedNerve && !nerves ? '신경 보기를 켜면 선택한 주행을 볼 수 있습니다.'
        : selectedId && presentation.hidden.includes(selectedId) ? '선택한 모형을 숨겼습니다. 다른 구조를 선택해도 숨김을 유지합니다.'
        : selectedId && presentation.isolated ? '선택만 보기에서는 주변 뼈와 근육이 숨겨집니다. 관절 움직임을 함께 보려면 선택만 보기를 해제해 주세요.'
        : selectedId && !bones ? '뼈 보기가 꺼져 있습니다. 관절과 부착 문맥을 함께 보려면 뼈 보기를 켜 주세요.'
        : progress && !progress.selectedAvailable ? '선택한 설명에 연결된 모형이 현재 보기에 없습니다.'
        : selectedNerve && nerves && presentation.observeNerves ? '신경 주행 보기 · 주변 구조는 반투명으로 표시합니다.'
        : '드래그하여 회전 · 스크롤하여 확대'}
      <small>현재 확보된 모형을 표시합니다. 일부 구조와 설명은 준비 중입니다.</small>
    </div>
  </div>;
}
