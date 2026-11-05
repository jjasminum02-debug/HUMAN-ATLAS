// Cross-section panel (ROADMAP Q2-2): plane, position across the body, which half stays, and a "look at the cut" view.
import { SECTION_LABELS, sectionCoordinate, type Bounds, type Section, type SectionAxis } from '../section';

const DEFAULT_POSITION: Record<SectionAxis, number> = { axial: .72, sagittal: .5, coronal: .5 };

function readout(section: Section, bounds: Bounds) {
  const c = sectionCoordinate(section, bounds);
  if (section.axis === 'axial') return `바닥에서 ${Math.round((c - bounds[0][1]) * 100)}cm`;
  const i = section.axis === 'sagittal' ? 0 : 2, centre = (bounds[0][i] + bounds[1][i]) / 2, cm = Math.round((c - centre) * 100);
  if (cm === 0) return section.axis === 'sagittal' ? '정중선' : '앞뒤 가운데';
  return section.axis === 'sagittal' ? `정중선에서 ${cm > 0 ? '왼쪽' : '오른쪽'} ${Math.abs(cm)}cm` : `가운데에서 ${cm > 0 ? '앞쪽' : '뒤쪽'} ${Math.abs(cm)}cm`;
}

export function SectionPanel({ section, bounds, onChange, onFace }: {
  section: Section | null; bounds: Bounds; onChange: (section: Section | null) => void; onFace: () => void;
}) {
  const pick = (axis: SectionAxis) => onChange({ axis, position: section?.axis === axis ? section.position : DEFAULT_POSITION[axis], flip: section?.axis === axis ? section.flip : false });
  return <div className="section-panel" id="section-panel" role="group" aria-label="단면 보기">
    <div className="section-axes" role="group" aria-label="단면 방향">
      {(Object.keys(SECTION_LABELS) as SectionAxis[]).map(axis => <button key={axis} aria-pressed={section?.axis === axis} onClick={() => pick(axis)}>{SECTION_LABELS[axis].name}</button>)}
      <button aria-pressed={!section} onClick={() => onChange(null)}>끄기</button>
    </div>
    {section ? <>
      <label className="section-position"><span>위치</span>
        <input type="range" min={0} max={1000} step={1} value={Math.round(section.position * 1000)} aria-label={`${SECTION_LABELS[section.axis].name} 위치`}
          onChange={event => onChange({ ...section, position: Number(event.target.value) / 1000 })}/>
        <output>{readout(section, bounds)}</output></label>
      <div className="section-actions">
        <button onClick={() => onChange({ ...section, flip: !section.flip })}>{SECTION_LABELS[section.axis].kept[section.flip ? 0 : 1]} 남기기</button>
        <button onClick={onFace}>단면 바라보기</button>
      </div>
      <p className="quiet-note">{SECTION_LABELS[section.axis].kept[section.flip ? 1 : 0]} 절반을 남기고 잘린 면을 진하게 칠합니다. 잘려 나간 쪽은 선택되지 않습니다.</p>
    </> : <p className="quiet-note">면을 고르면 모형을 그 면에서 잘라 속을 봅니다.</p>}
  </div>;
}
