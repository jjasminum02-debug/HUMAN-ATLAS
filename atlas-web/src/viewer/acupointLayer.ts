// Acupoints on the rig (ROADMAP 4-1 step 7). Data: /__atlas/v2/acupoints.json (atlas-data/pipeline/build_acupoints.py).
// Educational positions on the model: computed from bony landmarks and proportional cun, checked against a second
// source; not needling guidance.
export interface AcupointConcept { code: string; nameKo: string; hanja: string; location: string; channel: string }
export interface AcupointInstance { code: string; side: 'left' | 'right' | 'midline'; segment: string; position: [number, number, number];
  normal: [number, number, number]; surfaceOf: string | null; near: string[] }
export interface AcupointChannel { nameKo: string; nameHanja: string; en: string; codes: string[]; midline?: boolean; breaks?: string[] }
export interface AcupointFile { schemaVersion: number; channels: Record<string, AcupointChannel>; concepts: AcupointConcept[]; points: AcupointInstance[] }
export const acupointId = (p: { code: string; side: string }) => `${p.code}:${p.side}`;

/** Scene side of the acupoint panel (implemented by DatasetSceneAdapter). */
export interface AcupointHost {
  showAcupoints(file: AcupointFile | null, onPick?: (id: string) => void): void;
  selectAcupoint(id: string | null, focus?: boolean): void;
  /** Show one channel's markers and lines (null: every channel). */
  showAcupointChannel(channel: string | null): void;
  /** Meridian sinews: lines through the binding regions, one sinew at a time (null hides them). */
  showSinew(file: SinewFile | null, sinew: string | null): void;
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
