import { useEffect, useRef, useState } from 'react';
import { AnatomySceneController, type BodyProgress } from './AnatomySceneController';
import { type BodyManifest, validateManifest } from './contract';
import './wholeBody.css';
import { AtlasLoading } from '../../ui/AtlasLoading';

export function WholeBodyViewer({ region, selectedId, selectedIds, onSelect, whole, onWholeChange, onEntered }: { onEntered?: (value: boolean) => void; whole: boolean; onWholeChange: (value: boolean) => void; region: string | null; selectedId: string | null; selectedIds: string[]; onSelect: (id: string, side: string | null) => void }) {
  const host = useRef<HTMLDivElement>(null);
  const controller = useRef<AnatomySceneController | null>(null);
  const select = useRef(onSelect); select.current = onSelect;
  const [bones, setBones] = useState(true);
  const [muscles, setMuscles] = useState(true);
  const [supplements, setSupplements] = useState(false);
  const [dim, setDim] = useState(true);
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
    const abort = new AbortController(); let current: AnatomySceneController | null = null;
    setError(false); setReady(false); setProgress(null);
    const timeout = window.setTimeout(() => { abort.abort(); setError(true); }, 20000);
    void fetch('/__atlas/body/manifest.json', { signal: abort.signal }).then(async response => {
      if (!response.ok) throw new Error('Unavailable');
      const manifest = await response.json() as BodyManifest; validateManifest(manifest);
      if (abort.signal.aborted || !host.current) return;
      window.clearTimeout(timeout);
      current = new AnatomySceneController(host.current, manifest, setProgress, (id, side) => select.current(id, side));
      controller.current = current; setReady(true);
    }).catch(() => { window.clearTimeout(timeout); if (!abort.signal.aborted) setError(true); });
    return () => { window.clearTimeout(timeout); abort.abort(); current?.dispose(); controller.current = null; };
  }, [revision]);
  useEffect(() => {
    if (ready) controller.current?.setView({ region: whole ? null : region, selectedId, selectedIds, bones, muscles, supplements, dim });
  }, [ready, region, whole, selectedId, selectedIds, bones, muscles, supplements, dim]);
  return <div className="whole-body-viewer">
    <div className="whole-body-canvas" inert={!entered} aria-hidden={!entered} ref={host}/>
    {!entered && <AtlasLoading failed={error || Boolean(progress?.failed)} loaded={progress?.loaded} total={progress?.total} onRetry={() => error ? setRevision(r => r + 1) : controller.current?.retry()}/> }
    <div inert={!entered} className="body-tools" aria-label="모형 보기 설정">
      <button aria-pressed={whole} onClick={() => { onWholeChange(true); controller.current?.focus(null); }}>전체 보기</button>
      <button onClick={() => controller.current?.focus(whole ? null : region)}>화면 맞춤</button>
      <button aria-pressed={bones} onClick={() => setBones(!bones)}>뼈</button>
      <button aria-pressed={muscles} onClick={() => setMuscles(!muscles)}>근육</button>
      {selectedId && <button aria-pressed={dim} onClick={() => setDim(!dim)}>선택 강조</button>}
      <details><summary>보기 옵션</summary><label><input type="checkbox" checked={supplements} onChange={e => setSupplements(e.target.checked)}/>보완 모형 보기</label><p>설명 연결 전인 모형을 함께 봅니다. 선택과 학습 설명은 제공하지 않습니다.</p></details>
    </div>
    <div className="body-status" inert={!entered} aria-hidden={!entered} role="status" aria-live="polite">
      {error ? <><span>이 환경에서 모형 자료를 열 수 없습니다.</span><button onClick={() => setRevision(r => r + 1)}>다시 시도</button></>
        : !ready ? '모형을 준비하고 있습니다…'
        : progress?.contextLost ? '그래픽 연결을 복원하고 있습니다. 현재 시점과 선택을 유지합니다.'
        : progress?.failed ? <><span>일부 모형을 불러오지 못했습니다. 표시 중인 모형은 계속 살펴볼 수 있습니다.</span><button onClick={() => controller.current?.retry()}>다시 불러오기</button></>
        : progress && progress.loaded < progress.total ? `모형 불러오는 중 · ${progress.loaded}/${progress.total}`
        : !bones && !muscles ? '뼈 또는 근육을 켜 주세요.'
        : progress && !progress.selectedAvailable ? '선택한 설명에 연결된 모형이 현재 보기에 없습니다.'
        : '드래그하여 회전 · 스크롤하여 확대'}
      <small>현재 확보된 모형을 표시합니다. 일부 구조와 설명은 준비 중입니다.</small>
    </div>
  </div>;
}
