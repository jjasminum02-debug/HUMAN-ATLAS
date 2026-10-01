import { useEffect, useRef, useState } from 'react';
import { AnatomySceneController, type BodyProgress } from './AnatomySceneController';
import { type BodyManifest, validateManifest } from './contract';
import './wholeBody.css';
import { DatasetSceneAdapter } from '../datasets/DatasetSceneAdapter';
import type { Dataset } from '../datasets/schema';
import type { RuntimeIntegration } from '../datasets/integration';
import { AtlasLoading } from '../../ui/AtlasLoading';

export function WholeBodyViewer({ homeRevision = 0, viewResetRevision = 0, datasetSource, regionIds, selectedId, selectedIds, onSelect, whole, onWholeChange, onEntered }: { homeRevision?: number; viewResetRevision?: number; datasetSource?: { dataset: Dataset; integration: RuntimeIntegration }; onEntered?: (value: boolean) => void; whole: boolean; onWholeChange: (value: boolean) => void; regionIds: string[]; selectedId: string | null; selectedIds: string[]; onSelect: (id: string, side: string | null) => void }) {
  const host = useRef<HTMLDivElement>(null);
  const controller = useRef<AnatomySceneController | DatasetSceneAdapter | null>(null);
  const previousView = useRef<{ regionKey: string; selectedId: string | null; resetRevision: number } | null>(null);
  const select = useRef(onSelect); select.current = onSelect;
  const [bones, setBones] = useState(true);
  const [muscles, setMuscles] = useState(true);
  type Presentation = { dim: boolean; isolated: boolean; hidden: string[]; translucent: string[] };
  const [presentation, setPresentation] = useState<Presentation>({ dim: true, isolated: false, hidden: [], translucent: [] });
  const presentationRef = useRef(presentation);
  const presentationHistory = useRef<Presentation[]>([]);
  const [canUndoPresentation, setCanUndoPresentation] = useState(false);
  const updatePresentation = (next: Presentation, remember = true) => {
    if (remember) {
      presentationHistory.current = [...presentationHistory.current, presentationRef.current].slice(-12);
      setCanUndoPresentation(presentationHistory.current.length > 0);
    }
    presentationRef.current = next;
    setPresentation(next);
  };
  const undoPresentation = () => {
    const previous = presentationHistory.current.pop();
    if (previous) updatePresentation(previous, false);
    setCanUndoPresentation(presentationHistory.current.length > 0);
  };
  useEffect(() => {
    presentationHistory.current = [];
    setCanUndoPresentation(false);
    updatePresentation({ dim: true, isolated: false, hidden: [], translucent: [] }, false);
  }, [viewResetRevision]);
  const [revision, setRevision] = useState(0);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState(false);
  const [progress, setProgress] = useState<BodyProgress | null>(null);
  const [entered, setEntered] = useState(false);
  useEffect(() => { onEntered?.(entered); }, [entered, onEntered]);
  useEffect(() => {
    if (progress && progress.calls > 0 && (progress.loaded === progress.total || progress.failed > 0)) setEntered(true);
  }, [progress]);
  useEffect(() => {
    const abort = new AbortController(); let current: AnatomySceneController | DatasetSceneAdapter | null = null;
    setError(false); setReady(false); setProgress(null);
    const timeout = window.setTimeout(() => { abort.abort(); setError(true); }, 20000);
    if (datasetSource && host.current) {
      window.clearTimeout(timeout);
      current = new DatasetSceneAdapter(host.current, datasetSource.dataset, datasetSource.integration, setProgress, (id, side) => select.current(id, side));
      controller.current = current; setReady(true);
      return () => { abort.abort(); current?.dispose(); controller.current = null; };
    }
    void fetch('/__atlas/body/manifest.json', { signal: abort.signal }).then(async response => {
      if (!response.ok) throw new Error('Unavailable');
      const manifest = await response.json() as BodyManifest; validateManifest(manifest);
      if (abort.signal.aborted || !host.current) return;
      window.clearTimeout(timeout);
      current = new AnatomySceneController(host.current, manifest, setProgress, (id, side) => select.current(id, side));
      controller.current = current; setReady(true);
    }).catch(() => { window.clearTimeout(timeout); if (!abort.signal.aborted) setError(true); });
    return () => { window.clearTimeout(timeout); abort.abort(); current?.dispose(); controller.current = null; };
  }, [revision, datasetSource]);
  useEffect(() => {
    if (!ready) return;
    const regionKey = JSON.stringify(regionIds);
    const previous = previousView.current;
    controller.current?.setView({ region: null, regionIds, selectedId, selectedIds, bones, muscles, supplements: false, dim: presentation.dim, isolate: presentation.isolated && Boolean(selectedId), hiddenSourceKeys: presentation.hidden, translucentSourceKeys: presentation.translucent });
    if (previous === null) {
      if (regionIds.length > 0) controller.current?.focus(regionIds);
    } else if (previous.regionKey !== regionKey || previous.resetRevision !== viewResetRevision) {
      controller.current?.focus(regionIds);
    }
    previousView.current = { regionKey, selectedId, resetRevision: viewResetRevision };
  }, [ready, regionIds, selectedId, selectedIds, bones, muscles, presentation, viewResetRevision]);
  useEffect(() => { if (ready && homeRevision > 0) controller.current?.focus([]); }, [ready, homeRevision]);
  return <div className="whole-body-viewer">
    <div className="whole-body-canvas" inert={!entered} aria-hidden={!entered} ref={host}/>
    {!entered && <AtlasLoading failed={error || Boolean(progress?.failed)} loaded={progress?.loaded} total={progress?.total} onRetry={() => error ? setRevision(r => r + 1) : controller.current?.retry()}/> }
    <div inert={!entered} className="body-tools" aria-label="모형 보기 설정">
      <span className="view-options-label">보기 옵션</span>
      <div className="view-options-row">
        <button aria-pressed={whole} onClick={() => { onWholeChange(true); controller.current?.focus([]); }}>전체 보기</button>
        <button onClick={() => controller.current?.focus(regionIds)}>화면 맞춤</button>
        <button aria-pressed={bones} onClick={() => setBones(!bones)}>뼈</button>
        <button aria-pressed={muscles} onClick={() => setMuscles(!muscles)}>근육</button>
      </div>
      <div className="selection-view-options">
        <button disabled={!selectedId} aria-pressed={presentation.dim} onClick={() => updatePresentation({ ...presentation, dim: !presentation.dim })}>선택 강조</button>
        <button disabled={!selectedId || (!progress?.selectedAvailable && !presentation.isolated)} aria-pressed={presentation.isolated} onClick={() => updatePresentation({ ...presentation, isolated: !presentation.isolated })}>선택만 보기</button>
        <button disabled={!selectedId || !progress?.selectedAvailable} onClick={() => controller.current?.focusSelection()}>선택 맞춤</button>
        <button disabled={!selectedId || (!progress?.selectedAvailable && !presentation.translucent.includes(selectedId))} aria-pressed={Boolean(selectedId && presentation.translucent.includes(selectedId))} onClick={() => selectedId && updatePresentation({ ...presentation, translucent: presentation.translucent.includes(selectedId) ? presentation.translucent.filter(id => id !== selectedId) : [...presentation.translucent, selectedId] })}>선택 반투명</button>
        <button disabled={!selectedId || (!progress?.selectedAvailable && !presentation.hidden.includes(selectedId))} aria-pressed={Boolean(selectedId && presentation.hidden.includes(selectedId))} onClick={() => selectedId && updatePresentation({ ...presentation, hidden: presentation.hidden.includes(selectedId) ? presentation.hidden.filter(id => id !== selectedId) : [...presentation.hidden, selectedId] })}>{selectedId && presentation.hidden.includes(selectedId) ? '선택 다시 표시' : '선택 숨기기'}</button>
        <button disabled={!canUndoPresentation} onClick={undoPresentation}>되돌리기</button>
        <button disabled={presentation.dim && !presentation.isolated && !presentation.hidden.length && !presentation.translucent.length} onClick={() => updatePresentation({ dim: true, isolated: false, hidden: [], translucent: [] })}>보기 복원</button>
        <span className="hidden-count" role="status">{presentation.hidden.length ? `${presentation.hidden.length}개 숨김` : '구조를 선택하여 조절'}</span>
      </div>
    </div>
    <div className="body-status" inert={!entered} aria-hidden={!entered} role="status" aria-live="polite">
      {error ? <><span>이 환경에서 모형 자료를 열 수 없습니다.</span><button onClick={() => setRevision(r => r + 1)}>다시 시도</button></>
        : !ready ? '모형을 준비하고 있습니다…'
        : progress?.contextLost ? '그래픽 연결을 복원하고 있습니다. 현재 시점과 선택을 유지합니다.'
        : progress?.failed ? <><span>일부 모형을 불러오지 못했습니다. 표시 중인 모형은 계속 살펴볼 수 있습니다.</span><button onClick={() => controller.current?.retry()}>다시 불러오기</button></>
        : progress && progress.loaded < progress.total ? `모형 불러오는 중 · ${progress.loaded}/${progress.total}`
        : !bones && !muscles ? '뼈 또는 근육을 켜 주세요.'
        : selectedId && presentation.hidden.includes(selectedId) ? '선택한 모형을 숨겼습니다. 다른 구조를 선택해도 숨김을 유지합니다.'
        : progress && !progress.selectedAvailable ? '선택한 설명에 연결된 모형이 현재 보기에 없습니다.'
        : '드래그하여 회전 · 스크롤하여 확대'}
      <small>현재 확보된 모형을 표시합니다. 일부 구조와 설명은 준비 중입니다.</small>
    </div>
  </div>;
}
