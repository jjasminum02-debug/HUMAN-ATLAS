// Acupoints on the rig (ROADMAP 4-1 step 7). Data: /__atlas/v2/acupoints.json (atlas-data/pipeline/build_acupoints.py).
// Educational positions on the model: computed from bony landmarks and proportional cun, checked against a second
// source; not needling guidance.
export interface AcupointConcept { code: string; nameKo: string; hanja: string; location: string; channel: string }
export interface AcupointInstance { code: string; side: 'left' | 'right' | 'midline'; segment: string; position: [number, number, number];
  normal: [number, number, number]; surfaceOf: string | null; near: string[];
  /** Vessels and nerves under the point: within 1 cm of the line straight inward, to 6 cm, nearest first (depth in mm, model). */
  beneath?: { key: string; depth: number }[] }
export interface AcupointChannel { nameKo: string; nameHanja: string; en: string; codes: string[]; midline?: boolean; breaks?: string[] }
/** Bony reference points palpated in the diagnosis practicum (on the bone; navel and snuffbox at their points). */
export interface Landmark { id: string; nameKo: string; side: 'left' | 'right' | 'midline'; position: [number, number, number]; segment: string; bone: string | null }
/** A two-point distance compared left and right to find the short side; a midline end is shared by both sides. */
export interface LandmarkMeasure { id: string; nameKo: string; from: string; to: string; reads: string }
export interface AcupointFile { schemaVersion: number; channels: Record<string, AcupointChannel>; concepts: AcupointConcept[]; points: AcupointInstance[];
  landmarks?: Landmark[]; measures?: LandmarkMeasure[] }
export const landmarkId = (m: { id: string; side: string }) => `${m.id}:${m.side}`;
/** The landmark at one end of a measure on a side (midline ends are shared). */
export const measureEnd = (file: AcupointFile, id: string, side: 'left' | 'right') =>
  file.landmarks?.find(m => m.id === id && (m.side === side || m.side === 'midline'));
export const acupointId = (p: { code: string; side: string }) => `${p.code}:${p.side}`;

/**
 * How a point is found, read from its standard location text: straight on a landmark (a hollow between tendons, a bone
 * edge, a pulse), as a ratio between two landmarks (midpoint, 1/3), by finger breadth, or by proportional cun from a
 * landmark. Points found on a landmark are the easiest to press in the same place every time.
 * 0.1 cun (beside a nail corner) counts as on the landmark.
 */
export type LocationBasis = { kind: 'landmark' | 'between' | 'finger' | 'cun'; cun?: number; marks: string[] };
const MARKS: [string, RegExp][] = [['뼈', /뼈|융기|돌기|관절|복사|가시|구멍|모서리|이음|결합|거친면|결절/], ['힘줄', /힘줄/], ['주름', /주름/], ['오목', /오목|패임/],
  ['맥', /동맥|박동/], ['털경계', /털경계/], ['피부 경계', /피부 경계/], ['손발톱', /발톱|손톱/]];
export function locationBasis(location: string): LocationBasis {
  const marks = MARKS.filter(([, re]) => re.test(location)).map(([name]) => name);
  const cuns = [...location.matchAll(/(\d+(?:\.\d+)?)\s*촌/g)].map(m => Number(m[1])).filter(n => n > .1);
  if (cuns.length) return { kind: 'cun', cun: Math.max(...cuns), marks };
  if (/손가락 너비|횡지/.test(location)) return { kind: 'finger', marks };
  // A ratio along the line joining two landmarks (곡지: midpoint of 척택–lateral epicondyle); the midpoint of one crease is on it.
  if (/\d\/\d|잇는 선/.test(location)) return { kind: 'between', marks };
  return { kind: 'landmark', marks };
}
export const LOCATION_BASIS_LABEL: Record<LocationBasis['kind'], string> = {
  landmark: '표지에서 바로', between: '두 표지 사이 비율', finger: '표지에서 손가락 너비', cun: '표지에서 비례촌' };
/** What a muscle card's 경락 tab asks the acupoint panel to show: a point ("PC6:right") or a meridian sinew on one side. */
export type AcupointTarget = { point: string } | { sinew: string; side: 'right' | 'left' };

/** Scene side of the acupoint panel (implemented by DatasetSceneAdapter). */
export interface AcupointHost {
  showAcupoints(file: AcupointFile | null, onPick?: (id: string) => void): void;
  selectAcupoint(id: string | null, focus?: boolean): void;
  /** Show one channel's markers and lines (null: every channel). */
  showAcupointChannel(channel: string | null): void;
  /** Meridian sinews: lines through the binding regions, one sinew at a time (null hides them). */
  showSinew(file: SinewFile | null, sinew: string | string[] | null): void;
  /** Colour the muscles of a sinew's region (null clears). */
  setSinewRegion(keys: string[] | null): void;
  /** Teaching landmarks and the measuring lines (null hides); selecting one enlarges it. */
  showLandmarks(file: AcupointFile | null): void;
  selectLandmark(id: string | null): void;
  /** Current (posed) left and right length of each measure, in metres. */
  measureLengths(): Record<string, { right: number; left: number }>;
  onRigPoseChange?(listener: (pose: unknown) => void): () => void;
  /** 4-2 step 10: colour a posture pattern (short/tight red, weak blue; null clears). */
  setPostureHighlight?(groups: { short: string[]; weak: string[] } | null): void;
}
export const isAcupointHost = (host: unknown): host is AcupointHost => typeof (host as AcupointHost | null)?.showAcupoints === 'function';

/** Points of one channel on one side, in channel order (the line is drawn through them). */
export function channelPath(file: AcupointFile, channel: string, side: string) {
  const order = file.channels[channel]?.codes ?? [];
  return order.map(code => file.points.find(p => p.code === code && p.side === side)).filter((p): p is AcupointInstance => Boolean(p));
}

/** Side a channel's points are listed under: midline vessels (GV, CV) have one set. */
export const channelSide = (file: AcupointFile, channel: string, side: string) => file.channels[channel]?.midline ? 'midline' : side;

/** The channel line in drawable pieces: a new piece starts at each break code (where the pathway jumps). */
export function channelSegments(file: AcupointFile, channel: string, side: string) {
  const breaks = new Set(file.channels[channel]?.breaks ?? []), out: AcupointInstance[][] = [];
  for (const p of channelPath(file, channel, side)) {
    if (!out.length || breaks.has(p.code)) out.push([]);
    out[out.length - 1].push(p);
  }
  return out.filter(piece => piece.length > 1);
}

// Meridian sinews (經筋, 4-1 step 7 ③). Data: /__atlas/v2/sinews.json (built with the acupoints).
export interface SinewNode { label: string; anchor: string }
export interface Sinew { nameKo: string; hanja: string; strands: SinewNode[][]; internal: string[]; muscles: Record<'right' | 'left', string[]> }
export interface SinewPath { sinew: string; side: 'right' | 'left'; strand: number; points: [number, number, number][]; segments: string[];
  nodes: { anchor: string; position: [number, number, number]; segment: string }[] }
export interface SinewFile { schemaVersion: number; order: string[]; sinews: Record<string, Sinew>; paths: SinewPath[] }
/** A binding place (結) of the sinew course, as 『영추·경근』 names it: where the sinew fastens on bone or at a joint. */
export const isBinding = (node: SinewNode) => node.label.includes('結');
/** The six channel names (六經): a hand and a foot channel share each name, and their sinews join at the head or chest. */
export const SIX_CHANNELS: { name: string; hanja: string; hand: string; foot: string }[] = [
  { name: '태양', hanja: '太陽', hand: 'SI', foot: 'BL' }, { name: '양명', hanja: '陽明', hand: 'LI', foot: 'ST' }, { name: '소양', hanja: '少陽', hand: 'TE', foot: 'GB' },
  { name: '태음', hanja: '太陰', hand: 'LU', foot: 'SP' }, { name: '소음', hanja: '少陰', hand: 'HT', foot: 'KI' }, { name: '궐음', hanja: '厥陰', hand: 'PC', foot: 'LR' }];
export const sixChannelOf = (code: string) => SIX_CHANNELS.find(c => c.hand === code || c.foot === code);
