// Attachment areas drawn on the bones (ROADMAP C4; ligaments and the merged origin/insertion view in 4-1 step 6).
// Data: /__atlas/v2/attachments.json (`muscles`: Z-Anatomy patches + contact estimates; `ligaments`: contact estimates).
import { useEffect, useState } from 'react';
import type { RuntimeStructureRecord } from '../viewer/datasets/integration';

export type AreaRow = { key?: string; role: 'origin' | 'insertion' | 'attachment'; bone: string | null; source: 'za' | 'contact'; areaMm2?: number };
type Group = 'muscles' | 'ligaments';
let file: Promise<Partial<Record<Group, Record<string, AreaRow[]>>> | null> | undefined;
const load = () => file ??= fetch('/__atlas/v2/attachments.json').then(r => r.ok ? r.json() : null).catch(() => { file = undefined; return null; });

export function useAttachmentAreas(sourceKey: string | null, group: Group = 'muscles') {
  const [areas, setAreas] = useState<AreaRow[] | null>(null);
  useEffect(() => {
    let live = true; setAreas(null);
    if (sourceKey) void load().then(f => { if (live) setAreas(f?.[group]?.[sourceKey] ?? []); });
    return () => { live = false; };
  }, [sourceKey, group]);
  return areas;
}

/** One chip per drawn area: its colour, the bone (selectable) and whether Z-Anatomy draws it or it is a contact estimate. */
export function AreaChips({ areas, rows, onSelect }: { areas: AreaRow[]; rows: Map<string, RuntimeStructureRecord>; onSelect: (key: string) => void }) {
  return <ul className="attachment-area-chips">{areas.map((a, i) => <li key={`${a.key ?? a.bone}:${i}`} className={`area-${a.role}`}>
    <i aria-hidden="true"/>
    {a.bone && rows.get(a.bone) ? <button className="bone-related-muscle" onClick={() => onSelect(a.bone!)}>{rows.get(a.bone)!.label}</button> : <span>뼈 정보 없음</span>}
    <small>{a.source === 'za' ? 'Z-Anatomy 표시' : '접촉 추정'}</small>
  </li>)}</ul>;
}

/** Muscle areas whose role Z-Anatomy does not give ("부착"); origin and insertion areas sit in their own card blocks. */
export function UnlabelledAttachmentAreas({ areas, rows, bonesVisible, onSelect }: {
  areas: AreaRow[] | null; rows: Map<string, RuntimeStructureRecord>; bonesVisible: boolean; onSelect: (key: string) => void;
}) {
  const unlabelled = (areas ?? []).filter(a => a.role === 'attachment');
  if (!unlabelled.length) return null;
  return <section className="attachment-section attachment-areas" aria-label="기시·정지를 모르는 부착 면">
    <h3><i className="attachment"/>부착<span>기시·정지 미상</span></h3>
    <AreaChips areas={unlabelled} rows={rows} onSelect={onSelect}/>
    <p className="quiet-note">{bonesVisible ? '' : '뼈 층을 켜면 뼈 위에 칠한 면이 보입니다. '}근육 끝이 뼈에 3mm 안으로 닿는 면을 보라색으로 칠했습니다. 자료에 기시인지 정지인지 없어 ‘부착’으로 둡니다.</p>
  </section>;
}

/** Ligament / capsule card: where it meets each bone, and a button that turns the camera to those areas. */
export function LigamentAttachmentAreas({ sourceKey, rows, bonesVisible, onSelect, onFocus }: {
  sourceKey: string; rows: Map<string, RuntimeStructureRecord>; bonesVisible: boolean; onSelect: (key: string) => void; onFocus?: () => void;
}) {
  const areas = useAttachmentAreas(sourceKey, 'ligaments');
  if (!areas?.length) return null;
  return <section className="attachment-section attachment-areas" aria-label="뼈 위 부착 면">
    <h3><i className="attachment"/>뼈 위 부착 면<span>ATTACHMENT</span></h3>
    {onFocus && <button className="attachment-observe" onClick={onFocus}>부착 면 관찰<span>칠한 면으로 시점 이동</span></button>}
    <AreaChips areas={areas} rows={rows} onSelect={onSelect}/>
    <p className="quiet-note">{bonesVisible ? '' : '뼈 층을 켜면 뼈 위에 칠한 면이 보입니다. '}인대 표면이 뼈에 3mm 안으로 닿는 면을 계산해 보라색으로 칠한 추정입니다.</p>
  </section>;
}
