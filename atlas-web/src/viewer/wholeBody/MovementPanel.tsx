// Joint movement panel (ROADMAP M3): pick a joint, move its dofs with sliders, see which muscles produce the
// movement (agonists, red) and which oppose it (antagonists, blue).
import { useEffect, useState } from 'react';
import type { RigFile, RigPose } from '../rig';
import { groupDofs, groupOfJoint, MOVEMENT_GROUPS, movementRoles, type MuscleActionsFile, type RigHost } from '../movement';

type Row = { label: string; localDisplayEligible: boolean };

export function MovementPanel({ host, rows, request, musclesVisible, onSelect }: {
  host: RigHost; rows: Map<string, Row>; request: { jointId: string; revision: number } | null; musclesVisible: boolean; onSelect: (key: string) => void;
}) {
  const [rig, setRig] = useState<RigFile | null>(null);
  const [actions, setActions] = useState<MuscleActionsFile | null>(null);
  const [failed, setFailed] = useState(false);
  const [group, setGroup] = useState('knee');
  const [side, setSide] = useState<'l' | 'r'>('r');
  const [pose, setPose] = useState<RigPose | null>(host.rigPose);
  const [active, setActive] = useState<string | null>(null);
  useEffect(() => {
    let live = true;
    Promise.all([host.loadRig(), host.loadMuscleActions()]).then(([r, a]) => { if (live) { setRig(r); setActions(a); } }).catch(() => live && setFailed(true));
    const off = host.onRigPoseChange(setPose);
    return () => { live = false; off(); };
  }, [host]);
  useEffect(() => {
    const target = request && groupOfJoint(request.jointId);
    if (target) { setGroup(target.group); setSide(target.side); setActive(null); }
  }, [request]);
  // Closing the panel returns the body to rest.
  useEffect(() => () => { host.setActionHighlight(null); void host.loadRig().then(r => host.setRigPose(r, null)).catch(() => {}); }, [host]);
  const value = active ? pose?.[active] ?? 0 : 0;
  const roles = actions && active && value ? movementRoles(actions, active, value > 0 ? 1 : -1, key => rows.get(key)?.localDisplayEligible ?? false) : null;
  useEffect(() => {
    host.setActionHighlight(roles ? { agonists: roles.agonists.map(r => r.key), antagonists: roles.antagonists.map(r => r.key) } : null);
  }, [host, active, value > 0, value < 0, actions]); // eslint-disable-line react-hooks/exhaustive-deps
  if (failed) return <div className="movement-panel" id="movement-panel"><p className="quiet-note">관절 자료를 불러오지 못했습니다.</p></div>;
  if (!rig || !actions) return <div className="movement-panel" id="movement-panel"><p className="quiet-note">관절 자료를 불러오는 중…</p></div>;
  const dofs = groupDofs(rig, group, side);
  const set = (dofId: string, degrees: number) => { setActive(dofId); host.setRigPose(rig, { ...(host.rigPose ?? {}), [dofId]: degrees }); };
  const names = (list: { key: string; role: string }[]) => list.slice(0, 8).map(({ key, role }) => <button key={key} className="bone-related-muscle"
    onClick={() => onSelect(key)}>{rows.get(key)?.label ?? key}{role === 'assist' && <small> 보조</small>}</button>);
  const activeDof = dofs.find(d => d.dof.id === active)?.dof;
  return <div className="movement-panel" id="movement-panel">
    <div className="movement-joints" role="group" aria-label="관절">
      {MOVEMENT_GROUPS.map(g => <button key={g.id} aria-pressed={group === g.id} onClick={() => { setGroup(g.id); setActive(null); }}>{g.label}</button>)}
    </div>
    {group !== 'back' && <div className="movement-side" role="group" aria-label="몸의 쪽">
      {(['r', 'l'] as const).map(s => <button key={s} aria-pressed={side === s} onClick={() => { setSide(s); setActive(null); }}>{s === 'r' ? '오른쪽' : '왼쪽'}</button>)}
    </div>}
    <div className="movement-dofs">
      {dofs.map(({ joint, jointName, dof }) => {
        const degrees = Math.round(pose?.[dof.id] ?? 0);
        const label = degrees === 0 ? '중립' : `${degrees > 0 ? dof.positive : dof.negative} ${Math.abs(degrees)}°`;
        return <label key={dof.id} className={active === dof.id ? 'active' : undefined}>
          <span className="movement-dof-name">{dofs.some(d => d.joint !== joint) ? `${jointName.replace(/ \(.+\)$/, '')} · ` : ''}{dof.positive} / {dof.negative}</span>
          <span className="movement-slider"><small>{dof.negative}</small>
            <input type="range" min={dof.range[0]} max={dof.range[1]} step={1} value={degrees} aria-label={`${jointName} ${dof.positive}/${dof.negative}`}
              onChange={event => set(dof.id, Number(event.target.value))} onFocus={() => setActive(dof.id)}/>
            <small>{dof.positive}</small></span>
          <output>{label}</output>
        </label>;
      })}
    </div>
    <div className="movement-actions">
      <button disabled={!pose} onClick={() => { setActive(null); host.setRigPose(rig, null); }}>처음 자세로</button>
    </div>
    {roles && activeDof && <div className="movement-roles" aria-live="polite">
      <h4><span className="swatch agonist"/>{value > 0 ? activeDof.positive : activeDof.negative}을 만드는 근육 · {roles.agonists.length}</h4>
      <div className="attachment-bone-links">{roles.agonists.length ? names(roles.agonists) : <span className="quiet-note">자료에 없음</span>}</div>
      <h4><span className="swatch antagonist"/>반대로 작용하는 근육 · {roles.antagonists.length}</h4>
      <div className="attachment-bone-links">{roles.antagonists.length ? names(roles.antagonists) : <span className="quiet-note">자료에 없음</span>}</div>
      {!musclesVisible && <p className="quiet-note">근육 층을 켜면 색으로 볼 수 있습니다.</p>}
    </div>}
    <p className="quiet-note">{group === 'back' ? '허리는 요추 전체의 움직임을 한 관절로 단순화했습니다. ' : ''}
      작용 근육은 교과서 표를 OpenSim 모델의 모멘트 팔로 확인한 학습용 요약입니다. 어깨뼈·손가락은 아직 움직이지 않습니다.</p>
  </div>;
}
