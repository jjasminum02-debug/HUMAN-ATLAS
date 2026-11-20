// Card body for ligament/joint, fascia and tendon rows (ROADMAP C3). Data: atlas-data/runtime/structure-cards.json.
import { LigamentAttachmentAreas } from './AttachmentAreas';
import { ClinicalTests, useClinicalTests } from './ClinicalTests';
import { firstSentence, Fold, KeyLines, type KeyLine } from './CardParts';
import { testsFor } from '../data/clinicalTests';
import { useEffect, useState } from 'react';
import { CardLimits } from './CardLimits';
import type { RuntimeStructureRecord } from '../viewer/datasets/integration';
import type { RigFile } from '../viewer/rig';
import { movementRoles, rigJointForBones, type MuscleActionsFile } from '../viewer/movement';

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

export function StructureCard({ row, cards, rows, onSelect, rig, onMoveJoint, actions, bonesVisible = true, onFocusAreas }: {
  row: RuntimeStructureRecord; cards: StructureCardsFile | null; rows: Map<string, RuntimeStructureRecord>; onSelect: (key: string) => void;
  /** 4-1 step 6: ligament attachment areas on the bones, and a camera move to them. */
  bonesVisible?: boolean; onFocusAreas?: () => void;
  /** M3: open the movement panel on the rig joint these bones form. */
  rig?: RigFile | null; onMoveJoint?: (jointId: string) => void;
  /** M3 action table: lists the muscles that move this joint, per movement. */
  actions?: MuscleActionsFile | null;
}) {
  const clinicalTests = useClinicalTests();
  const [openFold, setOpenFold] = useState<string | null>(null);
  useEffect(() => setOpenFold(null), [row.sourceKey]);
  if (!cards) return <p className="quiet-note">구조 설명을 불러오는 중…</p>;
  const card = cards.cards[row.sourceKey];
  const joint = card?.joint ? cards.joints[card.joint] : undefined;
  const links = (keys: string[], exclude?: string) => keys.filter(key => key !== exclude && rows.get(key)?.localDisplayEligible)
    .map(key => <button key={key} className="bone-related-muscle" onClick={() => onSelect(key)}>{rows.get(key)!.label}</button>);
  const bones = links(card?.bones ?? []);
  const muscles = links(card?.muscles ?? []);
  const members = joint ? links(joint.members, row.sourceKey) : [];
  const rigJoint = rig ? rigJointForBones(rig, [...joint?.bones ?? [], ...card?.bones ?? []]) : null;
  const movers = rigJoint && actions ? rig!.joints[rigJoint].dofs.filter(dof => !dof.coupledTo).flatMap(dof => ([1, -1] as const).map(sign => ({
    label: sign > 0 ? dof.positive : dof.negative,
    muscles: movementRoles(actions, dof.id, sign, key => rows.get(key)?.localDisplayEligible ?? false).agonists,
  }))).filter(m => m.muscles.length) : [];
  // 4-3 U12: key lines answer first (what it joins, which joint, what it does, which tests), details fold below.
  const label = (key: string) => rows.get(key)?.label;
  const boneNames = (card?.bones ?? []).filter(key => rows.get(key)?.localDisplayEligible).map(label).filter(Boolean).slice(0, 3).join(' · ');
  const jointName = joint ? [joint.names.koTraditional ?? joint.names.koModern ?? joint.name, joint.type && JOINT_TYPE[joint.type]].filter(Boolean).join(' · ') : '';
  const tests = testsFor(clinicalTests, row.names.en);
  const bonesTitle = row.kind === 'joint' && row.tissue === 'bursa' ? '맞닿은 뼈' : '잇는 뼈', musclesTitle = row.kind === 'tendon' ? '이어진 근육' : '감싸거나 맞닿은 근육';
  const lines: KeyLine[] = [
    { fact: 'bones', label: bonesTitle, value: boneNames, opens: 'bones' },
    { fact: 'joint', label: '관절', value: jointName, opens: 'joint' },
    { fact: 'role', label: '하는 일', value: firstSentence(card?.text), opens: 'role' },
    { fact: 'tests', label: '검사', value: tests.map(t => t.name.replace(/ 검사$/, '')).join(' · '), opens: 'tests' },
  ];
  const more = card?.text && card.text.trim() !== firstSentence(card.text).trim();
  return <>
    {rigJoint && onMoveJoint && <button className="attachment-observe rig-joint-move" onClick={() => onMoveJoint!(rigJoint)}>
      {rig!.joints[rigJoint].name} 움직여 보기<span>관절 움직임 창에서 각도를 바꾸고 작용 근육을 봅니다.</span></button>}
    <KeyLines lines={lines} onOpen={setOpenFold}/>
    <div className="card-folds">
    {more && <Fold id="role" title="하는 일" summary="설명 전체" open={openFold === 'role'}><section className="attachment-section" aria-label="구조 설명"><p>{card!.text}</p></section></Fold>}
    {row.kind === 'joint' && <Fold id="areas" title="뼈 위 부착 면" summary="칠한 면으로 시점 이동" open={openFold === 'areas'}>
      <LigamentAttachmentAreas sourceKey={row.sourceKey} rows={rows} bonesVisible={bonesVisible} onSelect={onSelect} onFocus={onFocusAreas}/></Fold>}
    {bones.length > 0 && <Fold id="bones" title={bonesTitle} summary={boneNames} open={openFold === 'bones'}><section className="attachment-section"><div className="attachment-bone-links">{bones}</div></section></Fold>}
    {muscles.length > 0 && <Fold id="muscles" title={musclesTitle} summary={`${muscles.length}개`} open={openFold === 'muscles'}><section className="attachment-section"><div className="attachment-bone-links">{muscles}</div></section></Fold>}
    {joint && <Fold id="joint" title="관절" summary={jointName} open={openFold === 'joint'}><section className="attachment-section" aria-label="관절">
      {joint.summary && <p>{joint.summary}</p>}
      {(joint.form || joint.movements) && <dl className="joint-facts">
        {joint.form && <><dt>형태</dt><dd>{joint.form}</dd></>}
        {joint.movements && <><dt>움직임</dt><dd>{joint.movements}</dd></>}
      </dl>}
      {joint.bones.length > 0 && <><h4>관절을 이루는 뼈</h4><div className="attachment-bone-links">{links(joint.bones)}</div></>}
      {members.length > 0 && <><h4>이 관절의 다른 구조</h4><div className="attachment-bone-links">{members}</div></>}
    </section></Fold>}
    {movers.length > 0 && <Fold id="movers" title="이 관절을 움직이는 근육" summary={rig!.joints[rigJoint!].name} open={openFold === 'movers'}><section className="attachment-section joint-movers" aria-label="이 관절을 움직이는 근육">
      <dl>{movers.map(m => <div key={m.label}><dt>{m.label}</dt><dd className="attachment-bone-links">{m.muscles.map(({ key, role }) =>
        <button key={key} className="bone-related-muscle" onClick={() => onSelect(key)}>{rows.get(key)!.label}{role === 'assist' && <small> 보조</small>}</button>)}</dd></div>)}</dl>
      <p className="card-hint">근육 작용 표(OpenSim 모멘트 팔로 확인)에서 이 관절의 움직임마다 주동근을 모았습니다.</p>
    </section></Fold>}
    {tests.length > 0 && <Fold id="tests" title="평가" summary={tests.map(t => t.name.replace(/ 검사$/, '')).join(' · ')} open={openFold === 'tests'}><ClinicalTests row={row}/></Fold>}
    </div>
    {!card?.text && !joint && bones.length === 0 && muscles.length === 0 && <p className="empty-answer">구조 설명을 준비하고 있습니다.</p>}
    <CardLimits kind="structure"/>
  </>;
}
