// Structure bookmarks (ROADMAP Q2-3): the learner's saved structures, kept in this browser only.
import { safeStorage } from './quiz.ts';

export interface Bookmark { key: string; label: string; kind: string; savedAt: string }
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
