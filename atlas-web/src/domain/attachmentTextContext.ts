import type { RuntimeStructureRecord } from '../viewer/datasets/integration.ts';

/** Whole-bone display context from already verified text, never a surface footprint. */
export function namedAttachmentBones(text: string, side: string | null, rows: RuntimeStructureRecord[]) {
  const names = new Map<string, RuntimeStructureRecord[]>();
  for (const row of rows) {
    if (row.kind !== 'bone' || !row.localDisplayEligible || !row.defaultVisible || row.hardHoldReasons.length
      || row.sourceHiddenStatePreserved.hideViewport || (row.side !== side && row.side !== null)) continue;
    for (const name of new Set(Object.values(row.names).filter((name): name is string => Boolean(name)))) {
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
      if (start && /[\p{L}\p{N}]/u.test(haystack[start - 1])) continue;
      if (/^[a-z0-9]/i.test(haystack.slice(end)) || haystack.slice(end).startsWith('쪽')) continue;
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
