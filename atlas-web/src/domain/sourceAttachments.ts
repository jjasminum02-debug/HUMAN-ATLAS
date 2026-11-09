import type { RuntimeStructureRecord } from '../viewer/datasets/integration.ts';
import { namedAttachmentBones } from './attachmentTextContext.ts';

type AttachmentSource = {
  id: string;
  url?: string | null;
  localFilename?: string;
  sha256?: string;
  pageCount?: number;
  edition?: string;
  rights?: string;
  accessMethod: string;
  locator?: string;
  originalHtmlSha256: string | null;
  originalHtmlRetrieved: boolean;
  reviewNotesPath?: string;
  reviewNotesSha256?: string;
};
type AttachmentRecord = {
  sourceName: string;
  sourceEvidenceName?: string;
  sourceDispositionName?: string;
  sourceKeys: string[];
  sourceSides?: string[];
  instanceCoverage?: string;
  excludedSourceKeys?: string[];
  excludedSourceReason?: string;
  scopeType: string;
  evidenceState?: 'single_source_summary' | 'conflicted_source_summary';
  sourceOnly: boolean;
  canonicalBindingCreated: boolean;
  humanReview: string;
  publicRedistribution: string;
  origin: string;
  insertion: string;
  contextBones: { origin: string[]; insertion: string[] };
  fieldEvidence: { origin: { sourceIds: string[]; locator: string; learnerValueSha256?: string; reviewNotesSha256?: string };
    insertion: { sourceIds: string[]; locator: string; learnerValueSha256?: string; reviewNotesSha256?: string } };
};
export interface SourceAttachmentContent {
  contract: { sourceOnly: boolean; humanReview: string; publicRedistribution: string; canonicalBindingsCreated: number; geometryCreated: number };
  sourceCatalogSha256?: string;
  reviewNotesPath?: string;
  reviewNotesSha256?: string;
  sources: AttachmentSource[];
  records: AttachmentRecord[];
}
export type AttachmentContexts = Record<string, { origin: string[]; insertion: string[] }>;

/** Text pointers and whole-bone context only. This creates no canonical or surface attachment binding. */
export function projectSourceAttachments(
  content: SourceAttachmentContent,
  rows: RuntimeStructureRecord[],
  options: { verifiedWebReaderSourceIds?: ReadonlySet<string>; verifiedPdfSourceIds?: ReadonlySet<string> } = {},
) {
  const contract = content.contract;
  if (!contract.sourceOnly || contract.humanReview !== 'not_performed' || contract.publicRedistribution !== 'held'
    || contract.canonicalBindingsCreated !== 0 || contract.geometryCreated !== 0) throw Error('Attachment authority');
  const sources = new Map(content.sources.map((source) => [source.id, source]));
  if (sources.size !== content.sources.length) throw Error('Duplicate attachment source id');
  const contexts: AttachmentContexts = {}, text: Record<string, { origin: string; insertion: string }> = {};
  const claimedKeys = new Set<string>();
  const sourceNotesMatch = (source: AttachmentSource) => !content.reviewNotesPath || !content.reviewNotesSha256
    || (source.reviewNotesPath === content.reviewNotesPath && source.reviewNotesSha256 === content.reviewNotesSha256);

  for (const item of content.records) {
    if (!['named_source_muscle', 'named_source_part', 'named_source_group'].includes(item.scopeType) || !item.sourceOnly || item.canonicalBindingCreated
      || item.humanReview !== 'not_performed' || item.publicRedistribution !== 'held') throw Error('Attachment scope');
    const sourceNameIsPart = /\b(?:parts? of|head of|belly of|portion of)\b/i.test(item.sourceName);
    if (sourceNameIsPart !== (item.scopeType === 'named_source_part')) throw Error('Attachment part scope must match exact source name');
    if (!item.sourceKeys.length || new Set(item.sourceKeys).size !== item.sourceKeys.length) throw Error('Attachment source key set');
    const sideMode = item.instanceCoverage ?? 'legacy_bilateral';
    if (sideMode === 'partial_selected_keys' && (!item.excludedSourceKeys?.length || !item.excludedSourceReason)) {
      throw Error('Partial source-key coverage must name excluded keys and reason');
    }
    const selectedSides = new Set<string>();
    for (const sourceKey of item.sourceKeys) {
      const muscle = rows.find((row) => row.sourceKey === sourceKey);
      if (!/^ZA-[a-z0-9]+-[a-f0-9]{24}$/.test(sourceKey) || claimedKeys.has(sourceKey) || !muscle || muscle.kind !== 'muscle'
        || !muscle.localDisplayEligible || !muscle.defaultVisible || muscle.names.en !== item.sourceName) throw Error('Attachment muscle identity');
      claimedKeys.add(sourceKey);
      selectedSides.add(muscle.side === null ? 'midline' : muscle.side ?? 'unknown');
      if (item.contextBones.origin.length || item.contextBones.insertion.length) {
        for (const role of ['origin', 'insertion'] as const) {
          for (const name of item.contextBones[role]) {
            const bones = rows.filter((row) => row.kind === 'bone' && row.names.en === name && row.localDisplayEligible && row.defaultVisible
              && (row.side === muscle.side || row.side === null));
            if (bones.length !== 1) throw Error('Attachment bone identity: ' + name);
          }
        }
      }
    }
    const declaredSides = new Set(item.sourceSides ?? ['left', 'right']);
    if ([...selectedSides].some((side) => !declaredSides.has(side)) || [...declaredSides].some((side) => !selectedSides.has(side))) {
      throw Error('Attachment side declaration does not match selected source instances');
    }
    if (declaredSides.has('midline') && (declaredSides.size !== 1 || sideMode !== 'bilateral_or_exact_source_set')) {
      throw Error('Midline requires explicit source evidence and an exact singleton scope');
    }
    if (sideMode === 'legacy_bilateral' || sideMode === 'bilateral_or_exact_source_set') {
      if (declaredSides.size === 2 && (!declaredSides.has('left') || !declaredSides.has('right') || item.sourceKeys.length !== 2)) {
        throw Error('Bilateral attachment must select exactly one left and one right source instance');
      }
      if (declaredSides.has('midline') && item.sourceKeys.length !== 1) throw Error('Midline attachment must select exactly one source instance');
    } else if (sideMode === 'partial_selected_keys') {
      if (declaredSides.has('midline') || item.sourceKeys.length >= (item.sourceKeys.length + (item.excludedSourceKeys?.length ?? 0))) {
        throw Error('Partial attachment selection is not partial or contains a midline source');
      }
    } else if (sideMode !== 'legacy_bilateral' && sideMode !== 'bilateral_or_exact_source_set') {
      throw Error('Unknown attachment instance coverage');
    }

    for (const role of ['origin', 'insertion'] as const) {
      const field = item.fieldEvidence[role];
      if (!field.locator || !field.sourceIds.length || (field.learnerValueSha256 !== undefined
        && !/^[a-f0-9]{64}$/.test(field.learnerValueSha256)) || field.sourceIds.some((id) => {
        const source = sources.get(id);
        if (!source || !sourceNotesMatch(source)) return true;
        if (source.accessMethod === 'user_provided_pdf_text_extraction_and_selected_visual_page_review') {
          return !options.verifiedPdfSourceIds?.has(id) || source.url !== null || !source.localFilename
            || !/^[a-f0-9]{64}$/.test(source.sha256 ?? '') || !Number.isInteger(source.pageCount) || (source.pageCount ?? 0) < 1
            || source.edition !== 'not_exposed' || source.originalHtmlRetrieved || source.originalHtmlSha256 !== null
            || !/held/i.test(source.rights ?? '') || !/^[a-f0-9]{64}$/.test(source.reviewNotesSha256 ?? '');
        }
        if (!source.url?.startsWith('https://')) return true;
        if (source.accessMethod === 'opened_html') return !source.originalHtmlRetrieved || !/^[a-f0-9]{64}$/.test(source.originalHtmlSha256 ?? '');
        if (source.accessMethod === 'web_reader_opened_fulltext') return !options.verifiedWebReaderSourceIds?.has(id)
          || source.originalHtmlRetrieved || source.originalHtmlSha256 !== null
          || !/^[a-f0-9]{64}$/.test(source.reviewNotesSha256 ?? '');
        return true;
      })) throw Error('Attachment field source');
      if (!item[role]?.trim() || /[\u3400-\u9fff]|https?:\/\/|\b(?:T\d{2,3}[-:]|HA-[A-Z]-|ZA-c7010a9|not_performed|single_source)\b/.test(item[role])) throw Error('Attachment learner text');
    }
    if (item.evidenceState !== undefined && !['single_source_summary', 'conflicted_source_summary'].includes(item.evidenceState)) {
      throw Error('Attachment evidence state');
    }
    for (const sourceKey of item.sourceKeys) {
      text[sourceKey] = { origin: item.origin, insertion: item.insertion };
      contexts[sourceKey] = { origin: [], insertion: [] };
      const muscle = rows.find((row) => row.sourceKey === sourceKey)!;
      for (const role of ['origin', 'insertion'] as const) {
        for (const name of item.contextBones[role]) {
          const bones = rows.filter((row) => row.kind === 'bone' && row.names.en === name && row.localDisplayEligible && row.defaultVisible
            && (row.side === muscle.side || row.side === null));
          if (bones.length !== 1) throw Error('Attachment bone identity: ' + name);
          contexts[sourceKey][role].push(bones[0].sourceKey);
        }
        // Empty worker context lists do not erase bones explicitly named in a
        // verified description. Keep curated lists and ambiguous wording intact.
        if (!item.contextBones[role].length) {
          contexts[sourceKey][role] = namedAttachmentBones(item[role], muscle.side, rows).keys;
        }
      }
    }
  }
  return { text, contexts };
}
