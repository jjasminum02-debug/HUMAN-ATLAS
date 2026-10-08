import { useEffect, useMemo, useRef, useState } from 'react';
import { AnatomySceneController, type BodyProgress } from './AnatomySceneController';
import { type BodyManifest, validateManifest } from './contract';
import './wholeBody.css';
import { DatasetSceneAdapter } from '../datasets/DatasetSceneAdapter';
import type { Dataset } from '../datasets/schema';
import type { RuntimeIntegration } from '../datasets/integration';
import { AtlasLoading } from '../../ui/AtlasLoading';
import type { SourceMotionHost } from '../datasets/sourceMotionHost';
import { motorRelationsForNerve, nerveConceptForSourceName } from '../../data/learning';

export function WholeBodyViewer({ attachmentRole = null, homeRevision = 0, viewResetRevision = 0, datasetSource, regionIds, selectedId, selectedIds, onSelect, onEntered, onMotionHostChange, onMuscleLayerChange, onBoneLayerChange, onSelectionHiddenChange }: { attachmentRole?: 'origin' | 'insertion' | null; homeRevision?: number; viewResetRevision?: number; datasetSource?: { dataset: Dataset; integration: RuntimeIntegration }; onEntered?: (value: boolean) => void; onMotionHostChange?: (host: SourceMotionHost | null) => void; onMuscleLayerChange?: (enabled: boolean) => void; onBoneLayerChange?: (enabled: boolean) => void; onSelectionHiddenChange?: (hidden: boolean) => void; whole: boolean; onWholeChange: (value: boolean) => void; regionIds: string[]; selectedId: string | null; selectedIds: string[]; onSelect: (id: string, side: string | null) => void }) {
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
  const [bones, setBones] = useState(true);
  const [nerves, setNerves] = useState(false);
  const nerveLayerExplicitlyOff = useRef(false);
  const selectedNerveRow = datasetSource?.integration.objects.find(r => r.sourceKey === selectedId);
  const selectedNerve = selectedNerveRow?.nerve;
  const nerveConceptMuscleKeys = useMemo(() => {
    if (selectedNerveRow?.kind !== 'nerve') return [];
    const concept = nerveConceptForSourceName(selectedNerveRow.names.en);
    if (!concept) return [];
    const targets = new Set(motorRelationsForNerve(concept.key, selectedNerveRow.side).flatMap(r => r.targetSourceKeys));
    return (datasetSource?.integration.objects ?? []).filter(r => targets.has(r.sourceKey) && r.kind === 'muscle'
      && r.localDisplayEligible && r.side === selectedNerveRow.side).map(r => r.sourceKey);
  }, [datasetSource, selectedNerveRow]);
  useEffect(() => {
    // Initial nerve selection is visible; an explicit learner layer-off persists.
    if (selectedNerve && !nerveLayerExplicitlyOff.current) setNerves(true);
  }, [selectedNerve]);
  const staticPose = datasetSource?.integration.objects.find(r => r.nerve)?.nerve?.poseId;
  const [muscles, setMuscles] = useState(true);
  const observationKey = JSON.stringify([selectedId, regionIds, homeRevision, viewResetRevision]);
  const [focusObservationKey, setFocusObservationKey] = useState<string | null>(null);
  const focusObservation = !attachmentRole && focusObservationKey === observationKey;
  useEffect(() => { if (attachmentRole) setFocusObservationKey(null); }, [attachmentRole]);
  // Selection/region/history changes end temporary observation; returning later must not revive it.
  useEffect(() => { setFocusObservationKey(previous => previous === observationKey ? previous : null); }, [observationKey]);
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
    if (datasetSource && host.current) {
      window.clearTimeout(timeout);
      current = new DatasetSceneAdapter(host.current, datasetSource.dataset, datasetSource.integration, setProgress, (id, side) => select.current(id, side));
      controller.current = current; onMotionHostChange?.(current); setReady(true);
      return () => { abort.abort(); onMotionHostChange?.(null); current?.dispose(); controller.current = null; };
    }
    void fetch('/__atlas/body/manifest.json', { signal: abort.signal }).then(async response => {
      if (!response.ok) throw new Error('Unavailable');
      const manifest = await response.json() as BodyManifest; validateManifest(manifest);
      if (abort.signal.aborted || !host.current) return;
      window.clearTimeout(timeout);
      current = new AnatomySceneController(host.current, manifest, setProgress, (id, side) => select.current(id, side));
      controller.current = current; onMotionHostChange?.(null); setReady(true);
    }).catch(() => { window.clearTimeout(timeout); if (!abort.signal.aborted) setError(true); });
    return () => { window.clearTimeout(timeout); abort.abort(); current?.dispose(); controller.current = null; };
  }, [revision, datasetSource, onMotionHostChange]);
  useEffect(() => {
    if (!ready) return;
    stopEntrance();
    const regionKey = JSON.stringify(regionIds);
    const previous = previousView.current;
    if (controller.current instanceof AnatomySceneController) {
      if (focusObservation) { if (controller.current.beginObservation()) controller.current.focusSelection(); }
      else controller.current.endObservation();
    }
    controller.current?.setView({ region: null, regionIds, selectedId, selectedIds, bones, muscles, nerves, focusObservation, attachmentObservation: attachmentRole && selectedId ? {sourceKey: selectedId, role: attachmentRole} : null, poseId: staticPose, nerveConceptMuscleKeys, observeNerves: presentation.observeNerves, highlightInnervation: presentation.highlightInnervation, supplements: false, dim: presentation.dim, isolate: presentation.isolated && Boolean(selectedId), hiddenSourceKeys: presentation.hidden, translucentSourceKeys: presentation.translucent });
    const nerveFramed = controller.current instanceof DatasetSceneAdapter && selectedNerve && nerves
      && !presentation.hidden.includes(selectedId ?? '');
    if (previous === null) {
      // The adapter already fit a supported nerve deep link before its opening orbit.
      if (regionIds.length > 0 && !nerveFramed) controller.current?.focus(regionIds);
    } else if (previous.regionKey !== regionKey || previous.resetRevision !== viewResetRevision) {
      if (nerveFramed) controller.current?.focusSelection(true);
      else controller.current?.focus(regionIds);
    }
    previousView.current = { regionKey, selectedId, resetRevision: viewResetRevision };
  }, [ready, regionIds, selectedId, selectedIds, bones, muscles, nerves, staticPose, nerveConceptMuscleKeys, presentation, focusObservation, attachmentRole, viewResetRevision]);
  useEffect(() => { if (ready && homeRevision > 0) { stopEntrance(); controller.current?.focus([]); } }, [ready, homeRevision]);
  const observationScene = controller.current instanceof DatasetSceneAdapter ? controller.current.scene : controller.current;
  return <div className="whole-body-viewer" onPointerDownCapture={stopEntrance}>
    <div className="whole-body-canvas" inert={!entered} aria-hidden={!entered} ref={host}/>
    {!entered && <AtlasLoading failed={error || Boolean(progress?.failed)} loaded={progress?.loaded} total={progress?.total} onRetry={() => error ? setRevision(r => r + 1) : controller.current?.retry()}/> }
    <div inert={!entered} ref={tools} className="body-tools" aria-label="모형 보기 설정">
      <span className="view-options-label">보기 옵션</span>
      <div className="view-options-row">
        <button onClick={() => controller.current?.focus(regionIds)}>화면 맞춤</button>
        <button aria-pressed={bones} onClick={() => { const enabled = !bones; setBones(enabled); onBoneLayerChange?.(enabled); }}>뼈</button>
        <button aria-pressed={muscles} onClick={() => { const enabled = !muscles; setMuscles(enabled); onMuscleLayerChange?.(enabled); }}>근육</button>
        {staticPose && <button aria-pressed={nerves} onClick={() => { nerveLayerExplicitlyOff.current = nerves; setNerves(!nerves); }}>신경</button>}
      </div>
      <div className="selection-view-options">
        {!selectedNerve && <button disabled={!selectedId} aria-pressed={presentation.dim} onClick={() => updatePresentation({ ...presentation, dim: !presentation.dim })}>선택 강조</button>}
        <details className="observation-menu" onKeyDown={event => { if (event.key === 'Escape') { event.currentTarget.open = false; event.currentTarget.querySelector('summary')?.focus(); } }}>
          <summary>관찰 시점</summary>
          <div className="observation-popover">
            <div role="group" aria-label="해부학적 관찰 방향">{([['front', '앞'], ['back', '뒤'], ['left', '왼쪽'], ['right', '오른쪽']] as const).map(([direction, label]) => <button key={direction} disabled={!observationScene?.canObserveDirections} onClick={() => {
              const current = controller.current; (current instanceof DatasetSceneAdapter ? current.scene : current)?.observeDirection(direction);
            }}>{label}에서 보기</button>)}</div>
            <button disabled={Boolean(attachmentRole) || !focusObservation && (!selectedId || !progress?.selectedAvailable)} aria-pressed={focusObservation} onClick={() => setFocusObservationKey(focusObservation ? null : observationKey)}>{focusObservation ? '집중 관찰 끝내기' : '집중 관찰'}</button>
            <button disabled={!selectedId} aria-pressed={Boolean(selectedId && presentation.hidden.includes(selectedId))} onClick={() => selectedId && updatePresentation({ ...presentation, hidden: presentation.hidden.includes(selectedId) ? presentation.hidden.filter(id => id !== selectedId) : [...presentation.hidden, selectedId] })}>{selectedId && presentation.hidden.includes(selectedId) ? '선택 다시 표시' : '선택 구조 숨기기'}</button>
          </div>
        </details>
        <button disabled={!selectedId || !progress?.selectedAvailable} onClick={() => controller.current?.focusSelection()}>선택 맞춤</button>
        {selectedNerve ? (selectedNerve.muscleKeys.length > 0 || nerveConceptMuscleKeys.length > 0) && <button disabled={!nerves} aria-pressed={presentation.highlightInnervation} onClick={() => updatePresentation({ ...presentation, highlightInnervation: !presentation.highlightInnervation })}>관련 근육 강조</button> : <button disabled={!selectedId || (!progress?.selectedAvailable && !presentation.translucent.includes(selectedId))} aria-pressed={Boolean(selectedId && presentation.translucent.includes(selectedId))} onClick={() => selectedId && updatePresentation({ ...presentation, translucent: presentation.translucent.includes(selectedId) ? presentation.translucent.filter(id => id !== selectedId) : [...presentation.translucent, selectedId] })}>선택 반투명</button>}
      </div>
    </div>
    <div className="body-status" inert={!entered} aria-hidden={!entered} role="status" aria-live="polite">
      {error ? <><span>이 환경에서 모형 자료를 열 수 없습니다.</span><button onClick={() => setRevision(r => r + 1)}>다시 시도</button></>
        : !ready ? '모형을 준비하고 있습니다…'
        : progress?.contextLost ? '그래픽 연결을 복원하고 있습니다. 현재 시점과 선택을 유지합니다.'
        : progress?.failed ? <><span>일부 모형을 불러오지 못했습니다. 표시 중인 모형은 계속 살펴볼 수 있습니다.</span><button onClick={() => controller.current?.retry()}>다시 불러오기</button></>
        : progress && progress.loaded < progress.total ? `모형 불러오는 중 · ${progress.loaded}/${progress.total}`
        : !bones && !muscles && !nerves ? '뼈·근육·신경 중 볼 구조를 켜 주세요.'
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
