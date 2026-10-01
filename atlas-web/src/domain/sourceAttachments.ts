import type { RuntimeStructureRecord } from '../viewer/datasets/integration.ts';

export interface SourceAttachmentContent {
  contract: { sourceOnly: boolean; humanReview: string; publicRedistribution: string; canonicalBindingsCreated: number; geometryCreated: number };
  sources: { id: string; url: string; accessMethod: string; locator: string; originalHtmlSha256: string; originalHtmlRetrieved: boolean }[];
  records: { sourceName: string; sourceKeys: string[]; scopeType: string; sourceOnly: boolean; canonicalBindingCreated: boolean; humanReview: string; publicRedistribution: string;
    origin: string; insertion: string; contextBones: { origin: string[]; insertion: string[] };
    fieldEvidence: { origin: { sourceIds: string[]; locator: string }; insertion: { sourceIds: string[]; locator: string } } }[];
}
export type AttachmentContexts = Record<string, { origin: string[]; insertion: string[] }>;

/** Text pointers and whole-bone context only. This creates no canonical or surface attachment binding. */
export function projectSourceAttachments(content: SourceAttachmentContent, rows: RuntimeStructureRecord[]) {
  const contract = content.contract;
  if (!contract.sourceOnly || contract.humanReview !== 'not_performed' || contract.publicRedistribution !== 'held'
    || contract.canonicalBindingsCreated !== 0 || contract.geometryCreated !== 0) throw Error('Attachment authority');
  const sources = new Map(content.sources.map(s => [s.id, s]));
  const contexts: AttachmentContexts = {}, text: Record<string, { origin: string; insertion: string }> = {};
  for (const item of content.records) {
    if (item.scopeType !== 'named_source_muscle' || !item.sourceOnly || item.canonicalBindingCreated
      || item.humanReview !== 'not_performed' || item.publicRedistribution !== 'held') throw Error('Attachment scope');
    for (const role of ['origin', 'insertion'] as const) {
      const field = item.fieldEvidence[role];
      if (!field.locator || !field.sourceIds.length || field.sourceIds.some(id => {
        const source = sources.get(id); return !source || source.accessMethod !== 'opened_html' || !source.locator || !source.url.startsWith('https://')
          || !source.originalHtmlRetrieved || !/^[a-f0-9]{64}$/.test(source.originalHtmlSha256);
      })) throw Error('Attachment field source');
      if (!item[role]?.trim() || /[\u3400-\u9fff]|https?:\/\/|\b(?:T\d{2,3}[-:]|HA-[A-Z]-|ZA-c7010a9|not_performed|single_source)\b/.test(item[role])) throw Error('Attachment learner text');
    }
    for (const sourceKey of item.sourceKeys) {
      const muscle = rows.find(r => r.sourceKey === sourceKey);
      if (!/^ZA-[a-z0-9]+-[a-f0-9]{24}$/.test(sourceKey) || contexts[sourceKey] || !muscle || muscle.kind !== 'muscle'
        || !muscle.localDisplayEligible || !muscle.defaultVisible || muscle.names.en !== item.sourceName
        || !['left', 'right'].includes(muscle.side ?? '')) throw Error('Attachment muscle identity');
      text[sourceKey] = { origin: item.origin, insertion: item.insertion };
      contexts[sourceKey] = { origin: [], insertion: [] };
      for (const role of ['origin', 'insertion'] as const) {
        for (const name of item.contextBones[role]) {
          const bones = rows.filter(r => r.kind === 'bone' && r.names.en === name && r.localDisplayEligible && r.defaultVisible
            && (r.side === muscle.side || r.side === null));
          if (bones.length !== 1) throw Error('Attachment bone identity: ' + name);
          contexts[sourceKey][role].push(bones[0].sourceKey);
        }
      }
    }
  }
  return { text, contexts };
}
