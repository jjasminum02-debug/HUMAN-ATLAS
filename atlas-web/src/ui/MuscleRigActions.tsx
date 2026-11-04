// "이 근육의 작용" on the rig (ROADMAP M3): each action plays its joint movement once, with the muscles that
// produce it in red and those that oppose it in blue. Data: /__atlas/v2/actions.json.
import { useEffect, useRef, useState } from 'react';
import type { RigFile } from '../viewer/rig';
import { actionKeyframes, movementLabel, movementRoles, sampleKeyframes, type MuscleActionsFile, type RigHost } from '../viewer/movement';

const DURATION_MS = 2600;

export function MuscleRigActions({ host, sourceKey, visible }: { host: RigHost; sourceKey: string; visible: (key: string) => boolean }) {
  const [data, setData] = useState<{ rig: RigFile; actions: MuscleActionsFile } | null>(null);
  const [playing, setPlaying] = useState<string | null>(null);
  const frame = useRef(0);
  useEffect(() => {
    let live = true;
    Promise.all([host.loadRig(), host.loadMuscleActions()]).then(([rig, actions]) => live && setData({ rig, actions })).catch(() => {});
    return () => { live = false; };
  }, [host]);
  const stop = () => { cancelAnimationFrame(frame.current); frame.current = 0; setPlaying(null); };
  // Leaving this muscle (or the tab) ends a playback and returns to rest.
  useEffect(() => () => {
    if (!frame.current) return;
    cancelAnimationFrame(frame.current); host.setActionHighlight(null);
    void host.loadRig().then(rig => host.setRigPose(rig, null));
  }, [host, sourceKey]);
  const row = data?.actions.muscles[sourceKey];
  if (!data || !row || (!row.actions.length && !row.outside?.length)) return null;
  const play = (dofId: string, sign: 1 | -1) => {
    const { rig, actions } = data;
    const dof = rig.joints[dofId.split(':')[0]]?.dofs.find(d => d.id === dofId);
    if (!dof) return;
    cancelAnimationFrame(frame.current);
    const roles = movementRoles(actions, dofId, sign, visible);
    const highlight = { agonists: roles.agonists.map(r => r.key), antagonists: roles.antagonists.map(r => r.key) };
    const base = { ...(host.rigPose ?? {}), [dofId]: 0 }, frames = actionKeyframes(dof, sign), start = performance.now();
    const duration = frames.length * DURATION_MS / 3;
    let shown = false;
    setPlaying(`${dofId}${sign}`);
    const step = (now: number) => {
      const t = Math.min(1, (now - start) / duration), { value, active } = sampleKeyframes(frames, t);
      if (active !== shown) { shown = active; host.setActionHighlight(active ? highlight : null); }
      host.setRigPose(rig, { ...base, [dofId]: value });
      if (t < 1) frame.current = requestAnimationFrame(step);
      else { frame.current = 0; setPlaying(null); host.setActionHighlight(null); }
    };
    frame.current = requestAnimationFrame(step);
  };
  return <section className="attachment-section rig-actions" aria-label="관절에서 보는 작용">
    <h3>관절에서 보기</h3>
    {row.actions.length > 0 && <ul>{row.actions.map(a => {
      const id = `${a.dof}${a.sign}`;
      return <li key={id}><button aria-pressed={playing === id} onClick={() => playing === id ? stop() : play(a.dof, a.sign)}>
        <span>{movementLabel(data.rig, a.dof, a.sign)}</span><small>{a.role === 'primary' ? '주작용' : '보조'} · {playing === id ? '멈춤' : '재생'}</small>
      </button></li>;
    })}</ul>}
    {row.outside?.length ? <p className="quiet-note">모형에서 아직 움직이지 않는 작용: {row.outside.join(', ')}</p> : null}
    <p className="quiet-note">재생 중 빨간색은 같은 움직임을 만드는 근육, 파란색은 반대로 작용하는 근육입니다.</p>
  </section>;
}
