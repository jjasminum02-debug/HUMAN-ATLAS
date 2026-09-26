import rawCrosschecks from "../../../atlas-data/terminology/learning-attachment-crosschecks.json" with { type: "json" };

export interface AttachmentCrosscheckSource {
  id: string;
  title: string;
  citation: string;
  url: string;
  edition: string;
  locator: string;
  accessDate: string;
  accessMethod: string;
  textAccess: string;
}

export interface AttachmentCrosscheck {
  conceptId: string;
  role: "origin" | "insertion";
  directness: string;
  comparison: string;
  sourceIds: string[];
}

const data = rawCrosschecks as {
  items: AttachmentCrosscheck[];
  sources: AttachmentCrosscheckSource[];
};
const sourceById = new Map(data.sources.map((source) => [source.id, source]));

export function attachmentCrosscheckFor(conceptId: string, role: string): {
  item: AttachmentCrosscheck;
  sources: AttachmentCrosscheckSource[];
} | undefined {
  const item = data.items.find((row) => row.conceptId === conceptId && row.role === role);
  if (!item) return undefined;
  const sources = item.sourceIds.flatMap((id) => {
    const source = sourceById.get(id);
    return source ? [source] : [];
  });
  return sources.length === item.sourceIds.length ? { item, sources } : undefined;
}
