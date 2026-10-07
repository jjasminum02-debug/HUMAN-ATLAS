import type { RuntimeStructureRecord } from '../viewer/datasets/integration.ts';

// Parent bone names describe whole-bone context, never a measured surface location.
// Existing verified attachment prose uses these component/alternate names.
const contextNames: Record<string, string[]> = {
  'Hip bone': ['엉덩뼈', '두덩뼈', '궁둥뼈', '장골능', '치골결절', '치골결합', '치골능', '좌골결절'],
  'Ulna': ['팔꿈치뼈'],
  'First metatarsal bone': ['첫째 중족골', '제1중족골', '첫째 발허리뼈'],
  'Body of sternum': ['복장뼈자루·몸통'],
};

/** Whole-bone display context from already verified text, never a surface footprint. */
export function namedAttachmentBones(text: string, side: string | null, rows: RuntimeStructureRecord[], options: { wholeBoneContext?: boolean } = {}) {
  const names = new Map<string, RuntimeStructureRecord[]>();
  for (const row of rows) {
    if (row.kind !== 'bone' || !row.localDisplayEligible || !row.defaultVisible || row.hardHoldReasons.length
      || row.sourceHiddenStatePreserved.hideViewport || (row.side !== side && row.side !== null && row.side !== 'midline')) continue;
    for (const name of new Set([...Object.values(row.names), ...(options.wholeBoneContext ? [...(row.aliases ?? []), ...(contextNames[row.names.en] ?? [])] : [])].filter((name): name is string => Boolean(name)))) {
      if (name.length < 2) continue;
      names.set(name, [...names.get(name) ?? [], row]);
    }
  }
  const matches: Array<{ start: number; end: number; keys: string[] }> = [];
  for (const [name, bones] of names) {
    const needle = name.toLocaleLowerCase(); const haystack = text.toLocaleLowerCase();
    let offset = 0;
    while ((offset = haystack.indexOf(needle, offset)) !== -1) {
      const start = offset; const end = offset + needle.length; offset = end;
      // A bone name embedded in a muscle name or "ulnar/radial side" is not an attachment.
      if (start && (options.wholeBoneContext ? /[a-z0-9]/i : /[\p{L}\p{N}]/u).test(haystack[start - 1])) continue;
      if (/^[a-z0-9]/i.test(haystack.slice(end)) || (options.wholeBoneContext ? /^(?:쪽|근|신경|힘줄)/ : /^쪽/).test(haystack.slice(end))) continue;
      matches.push({ start, end, keys: [...new Set(bones.map(bone => bone.sourceKey))] });
    }
  }
  const longest = matches.filter(match => !matches.some(other => other.start <= match.start && other.end >= match.end
    && other.end - other.start > match.end - match.start));
  return {
    keys: [...new Set(longest.filter(match => match.keys.length === 1).flatMap(match => match.keys))],
    ambiguousMentions: longest.filter(match => match.keys.length !== 1).map(match => text.slice(match.start, match.end)),
  };
}
