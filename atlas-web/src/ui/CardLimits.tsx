// 4-3 U1: one "자료와 한계" fold at the bottom of a card instead of a notice under every section.
export type CardKind = 'muscle' | 'structure';

const COMMON = '해부 내용은 AI가 만든 표를 서로 다른 두 출처와 대조해 일치한 것만 보여 줍니다. 사람 검토는 아직 거치지 않았습니다.';
const ITEMS: Record<CardKind, string[]> = {
  muscle: [
    '기시·정지는 주요 부위를 요약했습니다. 뼈 위에 칠한 면은 근육 끝이 뼈에 3mm 안으로 닿는 곳을 계산한 추정입니다.',
    '신경 분지와 혈관의 분포·주행에는 개인차가 있습니다.',
    '검사는 이름과 보는 대상만 적었습니다. 한 검사로 진단하지 않으며, 하는 법은 진단학 실습에서 익힙니다.',
    '체형 패턴(교차 증후군)은 임상 관찰에서 나온 학습용 패턴이며 검증된 진단이 아닙니다.',
    '경혈은 뼈 표지와 골도분촌으로 이 모형에 계산한 위치이고, 경근은 『영추·경근』의 경로를 이 모형에 이어 그린 것입니다. 진단·치료 지침이 아닙니다.',
  ],
  structure: [
    '연결된 뼈·근육은 3D 모형의 표면 접촉으로 찾았습니다. 뼈 위에 칠한 면은 3mm 안으로 닿는 곳을 계산한 추정입니다.',
    '검사는 이름과 보는 대상만 적었습니다. 한 검사로 진단하지 않으며, 하는 법은 진단학 실습에서 익힙니다.',
  ],
};

export function CardLimits({ kind }: { kind: CardKind }) {
  return <details className="card-limits">
    <summary>자료와 한계</summary>
    <ul>{[COMMON, ...ITEMS[kind]].map(t => <li key={t}>{t}</li>)}</ul>
  </details>;
}
