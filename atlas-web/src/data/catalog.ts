import catalogPayload from "virtual:human-atlas-catalog";

export type AtlasRecord = Record<string, unknown> & { id: string };

export interface PilotCatalog {
  revision: string | null;
  catalogStatus: Record<string, unknown>;
  regions: AtlasRecord[];
  pilotMuscleIds: string[];
  headPartIds: string[];
  concepts: AtlasRecord[];
  terms: AtlasRecord[];
  structures: AtlasRecord[];
  attachments: AtlasRecord[];
  claims: AtlasRecord[];
  evidence: AtlasRecord[];
  sources: AtlasRecord[];
  missingConceptIds: string[];
  warnings: string[];
}

interface Payload extends Partial<PilotCatalog> {
  loadError?: string;
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null && !Array.isArray(value);

function records(value: unknown, label: string): AtlasRecord[] {
  if (!Array.isArray(value)) throw new Error(`카탈로그의 ${label} 목록 형식이 올바르지 않습니다.`);
  return value.filter((row): row is AtlasRecord => isRecord(row) && typeof row.id === "string");
}

export async function loadPilotCatalog(): Promise<PilotCatalog> {
  await Promise.resolve();
  if (!isRecord(catalogPayload)) throw new Error("카탈로그 로더가 올바른 데이터를 반환하지 않았습니다.");
  const payload = catalogPayload as Payload;
  if (typeof payload.loadError === "string") throw new Error(payload.loadError);

  const concepts = records(payload.concepts, "concepts");
  const terms = records(payload.terms, "terms");
  const structures = records(payload.structures, "structures");
  const attachments = records(payload.attachments, "attachments");
  const claims = records(payload.claims, "claims");
  const evidence = records(payload.evidence, "evidence");
  const sources = records(payload.sources, "sources");
  const regions = records(payload.regions, "regions");
  if (!Array.isArray(payload.pilotMuscleIds) || !Array.isArray(payload.headPartIds)) {
    throw new Error("pilot 선택 ID 목록을 읽을 수 없습니다.");
  }

  return {
    revision: typeof payload.revision === "string" ? payload.revision : null,
    catalogStatus: isRecord(payload.catalogStatus) ? payload.catalogStatus : {},
    regions,
    pilotMuscleIds: payload.pilotMuscleIds.filter((id): id is string => typeof id === "string"),
    headPartIds: payload.headPartIds.filter((id): id is string => typeof id === "string"),
    concepts,
    terms,
    structures,
    attachments,
    claims,
    evidence,
    sources,
    missingConceptIds: Array.isArray(payload.missingConceptIds)
      ? payload.missingConceptIds.filter((id): id is string => typeof id === "string")
      : [],
    warnings: Array.isArray(payload.warnings)
      ? payload.warnings.filter((warning): warning is string => typeof warning === "string")
      : [],
  };
}

export function displayTerms(catalog: PilotCatalog, conceptId: string): AtlasRecord[] {
  return catalog.terms.filter((term) => term.conceptId === conceptId);
}

export function termText(catalog: PilotCatalog, conceptId: string, language: string): string | null {
  const term = displayTerms(catalog, conceptId).find((row) => row.language === language && row.text);
  return typeof term?.text === "string" ? term.text : null;
}

export function recordLabel(catalog: PilotCatalog, conceptId: string): string {
  const structure = catalog.structures.find((row) => row.id === conceptId);
  const linkedIds = new Set(
    structure && Array.isArray(structure.termIds)
      ? structure.termIds.filter((id): id is string => typeof id === "string")
      : [],
  );
  const structureTerms = catalog.terms.filter((row) => linkedIds.has(row.id));
  const english = structureTerms.find((row) => row.language === "en" && typeof row.text === "string")?.text;
  const latin = structureTerms.find((row) => row.language === "la" && typeof row.text === "string")?.text;
  return typeof english === "string" ? english : typeof latin === "string" ? latin : termText(catalog, conceptId, "en") ?? termText(catalog, conceptId, "la") ?? conceptId;
}

export function linkedEvidence(catalog: PilotCatalog, ids: unknown): AtlasRecord[] {
  if (!Array.isArray(ids)) return [];
  const evidenceIds = new Set(ids.filter((id): id is string => typeof id === "string"));
  return catalog.evidence.filter((item) => evidenceIds.has(item.id));
}

export function sourceForEvidence(catalog: PilotCatalog, evidence: AtlasRecord): AtlasRecord | undefined {
  return catalog.sources.find((source) => source.id === evidence.sourceId);
}
