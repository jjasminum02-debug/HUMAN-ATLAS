// 4-3 U12: the parts every structure card shares with the muscle card — key lines that answer first,
// folding sections with a one-line summary, and (CardLimits) one "자료와 한계" fold at the bottom.
import { useEffect, useRef, type ReactNode } from 'react';

export type KeyLine = { fact: string; label: string; value: string; opens?: string };

/** Lines under the title; a line that names a section opens it. */
export function KeyLines({ lines, onOpen }: { lines: KeyLine[]; onOpen?: (section: string) => void }) {
  const shown = lines.filter(l => l.value);
  if (!shown.length) return null;
  return <dl className="key-facts" aria-label="핵심">
    {shown.map(l => <div key={l.fact} data-fact={l.fact} role={l.opens && onOpen ? 'button' : undefined} tabIndex={l.opens && onOpen ? 0 : undefined}
      onClick={() => l.opens && onOpen?.(l.opens)} onKeyDown={e => { if (l.opens && onOpen && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); onOpen(l.opens); } }}>
      <dt>{l.label}</dt><dd>{l.value}</dd></div>)}
  </dl>;
}

/** A folding section that looks like the muscle card's (details-based, several may be open). */
export function Fold({ id, title, summary, open = false, children, className = '' }: {
  id: string; title: string; summary?: string; open?: boolean; children: ReactNode; className?: string;
}) {
  const ref = useRef<HTMLDetailsElement>(null);
  useEffect(() => { if (open && ref.current) { ref.current.open = true; ref.current.scrollIntoView({ block: 'nearest' }); } }, [open]);
  return <details ref={ref} className={`study-section fold-section ${className}`} data-fold={id}>
    <summary className="study-section-head"><span className="section-title">{title}</span>{summary && <span className="section-summary">{summary}</span>}</summary>
    <div className="study-tab-panel">{children}</div>
  </details>;
}

export const firstSentence = (text: string | null | undefined) => (text ?? '').split(/(?<=[.。])\s+/)[0];
