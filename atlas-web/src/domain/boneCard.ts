import type { PilotCatalog } from "../data/catalog";
import type { BoneSelection, NavigationContract } from "./navigation";

export interface BoneCardSource {
  id: string;
  title: string;
  url: string | null;
  edition: string | null;
}

export interface BoneCardLandmark {
  id: string;
  label: string;
  sources: BoneCardSource[];
}

export interface BoneCardRelation {
  muscleOrPartId: string;
  roles: Array<"origin" | "insertion" | "other_attachment">;
  landmarks: string[];
  sources: BoneCardSource[];
}

export interface BoneCardData {
  conceptId: string;
  instanceId: string;
  side: string;
  label: string | null;
  nameSources: BoneCardSource[];
  landmarks: BoneCardLandmark[];
  relations: BoneCardRelation[];
  assetSources: BoneCardSource[];
}

const strings = (value: unknown): string[] => Array.isArray(value)
  ? value.filter((item): item is string => typeof item === "string")
  : [];

function uniqueSources(sources: BoneCardSource[]): BoneCardSource[] {
  return sources.filter((source, index, rows) => rows.findIndex((candidate) => candidate.id === source.id) === index);
}

function sourcesForEvidence(catalog: PilotCatalog, evidenceIds: readonly string[]): BoneCardSource[] {
  const wanted = new Set(evidenceIds);
  const sourceIds = new Set(catalog.evidence
    .filter((row) => wanted.has(row.id))
    .map((row) => row.sourceId)
    .filter((id): id is string => typeof id === "string"));
  return catalog.sources.flatMap((row) => {
    if (!sourceIds.has(row.id)) return [];
    return [{
      id: row.id,
      title: typeof row.title === "string" ? row.title : row.id,
      url: typeof row.urlOrLocalRef === "string" && /^https?:\/\//.test(row.urlOrLocalRef) ? row.urlOrLocalRef : null,
      edition: typeof row.edition === "string" ? row.edition : null,
    }];
  });
}

function termFor(catalog: PilotCatalog, conceptId: string): { label: string; sources: BoneCardSource[] } | null {
  const candidates = catalog.terms.filter((row) => row.conceptId === conceptId && row.language === "en" && typeof row.text === "string");
  for (const term of candidates) {
    const sources = sourcesForEvidence(catalog, strings(term.evidenceIds));
    if (sources.length > 0) return { label: term.text as string, sources };
  }
  return null;
}

function roleLabel(role: unknown): role is BoneCardRelation["roles"][number] {
  return role === "origin" || role === "insertion" || role === "other_attachment";
}

export function buildBoneCardData(
  catalog: PilotCatalog,
  navigation: NavigationContract,
  selection: BoneSelection,
): BoneCardData | null {
  const structure = catalog.structures.find((row) => row.id === selection.conceptId && row.kind === "bone");
  const instance = navigation.structureInstances.find((row) => row.id === selection.instanceId && row.structureId === selection.conceptId);
  if (!structure || !instance) return null;
  const mappings = navigation.structureMeshMappings.filter((row) => row.structureInstanceId === instance.id);
  if (mappings.length === 0 || (selection.meshId && !mappings.some((row) => row.meshIds.includes(selection.meshId!)))) return null;

  const structureById = new Map(catalog.structures.map((row) => [row.id, row]));
  const boneForTarget = (targetId: unknown): { boneId: string; landmarkId: string | null } | null => {
    if (typeof targetId !== "string") return null;
    const target = structureById.get(targetId);
    if (target?.kind === "bone") return { boneId: target.id, landmarkId: null };
    if (target?.kind === "landmark" && typeof target.parentId === "string" && structureById.get(target.parentId)?.kind === "bone") {
      return { boneId: target.parentId, landmarkId: target.id };
    }
    return null;
  };

  const landmarkEvidence = new Map<string, BoneCardSource[]>();
  const relationByOwner = new Map<string, BoneCardRelation>();
  for (const attachment of catalog.attachments) {
    const target = boneForTarget(attachment.targetStructureId);
    const explicitLandmark = typeof attachment.landmarkId === "string" ? boneForTarget(attachment.landmarkId) : null;
    const boneId = target?.boneId ?? explicitLandmark?.boneId;
    if (boneId !== instance.structureId) continue;
    const claim = catalog.claims.find((row) => row.id === attachment.descriptionClaimId && row.subjectId === attachment.id);
    const evidenceIds = strings(claim?.evidenceIds);
    const sources = sourcesForEvidence(catalog, evidenceIds);
    if (!claim || sources.length === 0 || !roleLabel(attachment.role)) continue;

    const landmarkId = target?.landmarkId ?? explicitLandmark?.landmarkId ?? null;
    if (landmarkId) {
      const landmarkTerm = termFor(catalog, landmarkId);
      if (landmarkTerm) {
        landmarkEvidence.set(landmarkId, [...(landmarkEvidence.get(landmarkId) ?? []), ...sources]);
      }
    }

    const ownerId = attachment.muscleOrPartId;
    if (typeof ownerId !== "string") continue;
    const relation = relationByOwner.get(ownerId) ?? {
      muscleOrPartId: ownerId,
      roles: [],
      landmarks: [],
      sources: [],
    };
    if (!relation.roles.includes(attachment.role)) relation.roles.push(attachment.role);
    if (landmarkId && !relation.landmarks.includes(landmarkId)) relation.landmarks.push(landmarkId);
    relation.sources = [...relation.sources, ...sources];
    relationByOwner.set(ownerId, relation);
  }

  const landmarks = [...landmarkEvidence.entries()].flatMap(([id, relationSources]) => {
    const term = termFor(catalog, id);
    return term ? [{ id, label: term.label, sources: uniqueSources([...term.sources, ...relationSources]) }] : [];
  });
  const assetEvidenceIds = mappings.flatMap((mapping) => mapping.evidenceIds ?? []);
  const assetSources = sourcesForEvidence(catalog, assetEvidenceIds);

  return {
    conceptId: structure.id,
    instanceId: instance.id,
    side: instance.side,
    label: termFor(catalog, structure.id)?.label ?? null,
    nameSources: termFor(catalog, structure.id)?.sources ?? [],
    landmarks,
    relations: [...relationByOwner.values()].map((row) => ({
      ...row,
      sources: uniqueSources(row.sources),
    })),
    assetSources,
  };
}

export function boneSourceLabel(sourceId: string): string {
  if (sourceId === "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0") return "BodyParts3D · Release 4.0";
  if (sourceId === "GRAY_ANATOMY_20E_1918") return "Gray · 1918년판";
  return sourceId;
}
