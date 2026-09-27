import './atlasLoading.css';

/** Real pending/error state only: no timer or synthetic progress. */
export function AtlasLoading({ failed = false, onRetry, loaded, total }: {
  failed?: boolean; onRetry?: () => void; loaded?: number; total?: number;
}) {
  return <div className="atlas-loading" aria-label="앱 준비">
    <h1>HUMAN ATLAS</h1>
    <div role="status" aria-live="polite">
      <p>{failed ? '모형 자료를 불러오지 못했습니다.' : '해부학 모형을 준비하고 있습니다'}</p>
      {!failed && (total ? <progress aria-label="모형 불러오기" max={total} value={loaded ?? 0}/> : <progress aria-label="자료 연결 중"/>)}
      {failed && <><p className="atlas-loading-help">자료 연결을 확인한 뒤 다시 시도해 주세요.</p><button onClick={onRetry}>다시 시도</button></>}
    </div>
  </div>;
}
