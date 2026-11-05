// Muscle card list of the attachment areas drawn on the bones (ROADMAP C4). Data: /__atlas/v2/attachments.json.
import { useEffect, useState } from 'react';
import type { RuntimeStructureRecord } from '../viewer/datasets/integration';

type Row = { key?: string; role: 'origin' | 'insertion' | 'attachment'; bone: string | null; source: 'za' | 'contact' };
let file: Promise<{ muscles: Record<string, Row[]> } | null> | undefined;
const load = () => file ??= fetch('/__atlas/v2/attachments.json').then(r => r.ok ? r.json() : null).catch(() => { file = undefined; return null; });

const ROLE = { origin: '기시', insertion: '정지', attachment: '부착' } as const;

export function AttachmentAreas({ sourceKey, rows, bonesVisible, onSelect }: {
  sourceKey: string; rows: Map<string, RuntimeStructureRecord>; bonesVisible: boolean; onSelect: (key: string) => void;
}) {
  const [areas, setAreas] = useState<Row[] | null>(null);
  useEffect(() => { let live = true; void load().then(f => { if (live) setAreas(f?.muscles[sourceKey] ?? []); }); return () => { live = false; }; }, [sourceKey]);
  if (!areas?.length) return null;
  const estimated = areas.some(a => a.source === 'contact');
  return <section className="attachment-section attachment-areas" aria-label="모형에 표시한 부착 면">
    <h3>뼈 위 부착 면</h3>
    <ul>{areas.map((a, i) => <li key={`${a.key ?? a.bone}:${i}`} className={`area-${a.role}`}>
      <i aria-hidden="true"/><span>{ROLE[a.role]}</span>
      {a.bone && rows.get(a.bone) ? <button className="bone-related-muscle" onClick={() => onSelect(a.bone!)}>{rows.get(a.bone)!.label}</button> : <span>뼈 정보 없음</span>}
      <small>{a.source === 'za' ? 'Z-Anatomy 표시' : '접촉 추정'}</small>
    </li>)}</ul>
    <p className="quiet-note">{bonesVisible ? '근육을 고르면 뼈 위에 색으로 칠합니다. 근육에 가려지면 ‘선택 반투명’이나 기시·정지 관찰로 봅니다.' : '뼈 층을 켜면 뼈 위에 칠한 면을 볼 수 있습니다.'}
      {estimated && ' ‘접촉 추정’은 근육 끝이 뼈에 3mm 안으로 닿는 면이며, 기시·정지를 모를 때는 보라색 ‘부착’으로 표시합니다.'}</p>
  </section>;
}
