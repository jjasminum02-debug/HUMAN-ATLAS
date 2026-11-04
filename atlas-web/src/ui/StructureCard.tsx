// Card body for ligament/joint, fascia and tendon rows (ROADMAP C3). Data: atlas-data/runtime/structure-cards.json.
import type { RuntimeStructureRecord } from '../viewer/datasets/integration';

export interface StructureCardJoint {
  name: string; names: RuntimeStructureRecord['names']; type: 'synovial' | 'fibrous' | 'cartilaginous' | null; side: string;
  form: string | null; movements: string | null; summary: string | null; members: string[]; bones: string[];
}
export interface StructureCardsFile {
  schemaVersion: 1; revision: string;
  joints: Record<string, StructureCardJoint>;
  cards: Record<string, { text: string | null; bones: string[]; muscles: string[]; joint: string | null }>;
}

const JOINT_TYPE: Record<string, string> = { synovial: '윤활관절', fibrous: '섬유관절', cartilaginous: '연골관절' };

export function StructureCard({ row, cards, rows, onSelect }: {
  row: RuntimeStructureRecord; cards: StructureCardsFile | null; rows: Map<string, RuntimeStructureRecord>; onSelect: (key: string) => void;
}) {
  if (!cards) return <p className="quiet-note">구조 설명을 불러오는 중…</p>;
  const card = cards.cards[row.sourceKey];
  const joint = card?.joint ? cards.joints[card.joint] : undefined;
  const links = (keys: string[], exclude?: string) => keys.filter(key => key !== exclude && rows.get(key)?.localDisplayEligible)
    .map(key => <button key={key} className="bone-related-muscle" onClick={() => onSelect(key)}>{rows.get(key)!.label}</button>);
  const bones = links(card?.bones ?? []);
  const muscles = links(card?.muscles ?? []);
  const members = joint ? links(joint.members, row.sourceKey) : [];
  return <>
    {card?.text && <section className="attachment-section" aria-label="구조 설명"><h3>하는 일</h3><p>{card.text}</p></section>}
    {bones.length > 0 && <section className="attachment-section"><h3>{row.kind === 'joint' && row.tissue === 'bursa' ? '맞닿은 뼈' : '잇는 뼈'}</h3>
      <div className="attachment-bone-links">{bones}</div></section>}
    {muscles.length > 0 && <section className="attachment-section"><h3>{row.kind === 'tendon' ? '이어진 근육' : '감싸거나 맞닿은 근육'}</h3>
      <div className="attachment-bone-links">{muscles}</div></section>}
    {joint && <section className="attachment-section" aria-label="관절">
      <h3>{joint.names.koTraditional ?? joint.names.koModern ?? joint.name}<span>{[joint.names.koModern, joint.type && JOINT_TYPE[joint.type]].filter(Boolean).join(' · ')}</span></h3>
      {joint.summary && <p>{joint.summary}</p>}
      {(joint.form || joint.movements) && <dl className="joint-facts">
        {joint.form && <><dt>형태</dt><dd>{joint.form}</dd></>}
        {joint.movements && <><dt>움직임</dt><dd>{joint.movements}</dd></>}
      </dl>}
      {joint.bones.length > 0 && <><h4>관절을 이루는 뼈</h4><div className="attachment-bone-links">{links(joint.bones)}</div></>}
      {members.length > 0 && <><h4>이 관절의 다른 구조</h4><div className="attachment-bone-links">{members}</div></>}
    </section>}
    {!card?.text && !joint && bones.length === 0 && muscles.length === 0 && <p className="quiet-note">구조 설명을 준비하고 있습니다.</p>}
    <p className="quiet-note">설명은 학습용 요약입니다. 연결된 뼈·근육은 3D 모형의 표면 접촉으로 찾았습니다.</p>
  </>;
}
