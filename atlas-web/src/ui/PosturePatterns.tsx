// 4-2 step 10: posture pattern colouring (short/tight magenta, weak green; 4-3 U1) and the line on a muscle's 기능 tab.
import { useEffect, useState } from 'react';
import type { RuntimeStructureRecord } from '../viewer/datasets/integration';
import { patternKeys, patternsFor, type PosturePatternsFile } from '../data/posturePatterns';

let patternFile: Promise<PosturePatternsFile | null> | undefined;
const loadPatterns = () => patternFile ??= fetch('/__atlas/v2/posture-patterns.json').then(r => r.ok ? r.json() : null).catch(() => { patternFile = undefined; return null; });
export function usePosturePatterns() {
  const [file, setFile] = useState<PosturePatternsFile | null>(null);
  useEffect(() => { let live = true; void loadPatterns().then(f => { if (live) setFile(f); }); return () => { live = false; }; }, []);
  return file;
}

export const POSTURE_CAVEAT = '임상 관찰에서 나온 학습용 패턴이며 검증된 진단은 아닙니다. 사람마다 다르게 나타납니다.';

/** Pattern list with a colour toggle (one pattern at a time). */
export function PosturePatternList({ host, rows }: {
  host: { setPostureHighlight?(groups: { short: string[]; weak: string[] } | null): void };
  rows: Map<string, RuntimeStructureRecord>;
}) {
  const file = usePosturePatterns();
  const [on, setOn] = useState<string | null>(null);
  useEffect(() => {
    const pattern = file?.patterns.find(p => p.id === on);
    host.setPostureHighlight?.(pattern ? patternKeys(pattern, rows.values()) : null);
  }, [host, file, on, rows]);
  useEffect(() => () => host.setPostureHighlight?.(null), [host]);
  if (!file || !host.setPostureHighlight) return null;
  return <div className="posture-patterns"><h5>체형 패턴</h5>
    <ul>{file.patterns.map(p => <li key={p.id}>
      <button aria-pressed={on === p.id} onClick={() => setOn(on === p.id ? null : p.id)}>{p.name}</button>
      <span>{p.signs}</span>
      {on === p.id && p.note && <small>{p.note}</small>}
    </li>)}</ul>
    {on && <p className="posture-legend"><span><i className="posture-short"/>긴장·짧아지는 쪽</span><span><i className="posture-weak"/>약해지는 쪽</span></p>}
    <p className="quiet-note">{POSTURE_CAVEAT}</p>
  </div>;
}

/** On a muscle's 기능 tab: which pattern names it and on which side. */
export function MusclePosture({ muscle }: { muscle: RuntimeStructureRecord }) {
  const hits = patternsFor(usePosturePatterns(), muscle.names.en);
  if (!hits.length) return null;
  return <section className="attachment-section posture-membership" aria-label="체형 패턴">
    <h3>체형 패턴에서</h3>
    <ul>{hits.map(({ pattern, role }) => <li key={pattern.id}><strong>{pattern.name}</strong> — {role === 'short' ? '긴장·짧아지는 쪽' : '약해지는 쪽'}<span>{pattern.signs}</span></li>)}</ul>
    <p className="card-hint">도구 막대 더보기의 체형 패턴에서 패턴 전체를 색으로 볼 수 있습니다.</p>
  </section>;
}
