// Structure bookmarks (ROADMAP Q2-3): the learner's saved structures, kept in this browser only.
import { safeStorage } from './quiz.ts';

/** What the learner was looking at when saving (4-1 step 6): camera, layers, their opacity and the cross-section. */
export interface StudyView {
  camera: { position: number[]; target: number[]; zoom: number };
  layers: Record<string, boolean>; layerOpacity: Record<string, number>;
  section: { axis: string; position: number; flip: boolean } | null;
}
export interface Bookmark { key: string; label: string; kind: string; savedAt: string; view?: StudyView }
/** Scene side: capture the current view, and restore one (layers first, then the camera). */
export interface StudyViewHost { captureStudyView(): StudyView | null; restoreStudyView(view: StudyView): void }
export const isStudyViewHost = (host: unknown): host is StudyViewHost => typeof (host as StudyViewHost | null)?.captureStudyView === 'function';
/** A saved view is usable only if it has a finite camera and known shapes. */
export function validStudyView(view: unknown): view is StudyView {
  const v = view as StudyView | null;
  const finite = (a: unknown, n: number) => Array.isArray(a) && a.length === n && a.every(Number.isFinite);
  return Boolean(v && finite(v.camera?.position, 3) && finite(v.camera?.target, 3) && Number.isFinite(v.camera?.zoom) && v.layers && typeof v.layers === 'object'
    && (v.section === null || (v.section && typeof v.section.axis === 'string' && Number.isFinite(v.section.position))));
}
const KEY = 'atlas.bookmarks.v1';

export function readBookmarks(storage: Pick<Storage, 'getItem'> | null = safeStorage()): Bookmark[] {
  try { const v = JSON.parse(storage?.getItem(KEY) ?? '[]'); return Array.isArray(v) ? v.filter(b => b && typeof b.key === 'string') : []; }
  catch { return []; }
}
export function writeBookmarks(list: Bookmark[], storage: Pick<Storage, 'setItem'> | null = safeStorage()) {
  try { storage?.setItem(KEY, JSON.stringify(list)); } catch { /* blocked storage: the list lives for this session */ }
}
/** Newest first; saving an existing key removes it (toggle). */
export function toggleBookmark(list: Bookmark[], entry: Omit<Bookmark, 'savedAt'>, now = new Date()): Bookmark[] {
  return list.some(b => b.key === entry.key) ? list.filter(b => b.key !== entry.key) : [{ ...entry, savedAt: now.toISOString() }, ...list];
}
/** Drop bookmarks whose structure is no longer in the runtime (e.g. after a data rebuild changed keys). */
export function liveBookmarks(list: Bookmark[], exists: (key: string) => boolean) { return list.filter(b => exists(b.key)); }
