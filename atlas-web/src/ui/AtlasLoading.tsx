import './atlasLoading.css';

/** Real pending/error state only: no timer or synthetic progress. */
export function AtlasLoading({ failed = false, onRetry, loaded, total }: {
  failed?: boolean; onRetry?: () => void; loaded?: number; total?: number;
}) {
  const count = total && total > 0 ? Math.min(total, Math.max(0, loaded ?? 0)) : null;
  return <div className="atlas-loading" aria-label="앱 준비" data-state={failed ? 'failed' : 'pending'}>
    <div className="atlas-loading-card">
      <h1><span aria-hidden="true"/>HUMAN ATLAS</h1>
      <div role="status" aria-live="polite">
        <h2>{failed ? '모형을 불러오지 못했어요' : '모형을 준비하고 있어요'}</h2>
        <p>{failed ? '연결을 확인한 뒤 다시 시도해 주세요.' : '뼈와 근육을 살펴볼 공간을 준비합니다.'}</p>
      </div>
      {!failed && <div className="atlas-loading-progress">
        {count !== null ? <progress aria-label="모형 불러오기" max={total} value={count}/> : <progress aria-label="자료 연결 중"/>}
        <span>{count !== null ? `${count} / ${total} 자료 준비` : '자료 연결 중'}</span>
      </div>}
      {failed && onRetry && <button onClick={onRetry}>다시 시도</button>}
    </div>
  </div>;
}
