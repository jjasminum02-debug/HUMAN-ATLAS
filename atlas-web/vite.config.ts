import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import type { Plugin } from "vite";
import { defineConfig } from "vite";

type AnyRecord = Record<string, unknown>;
type EntityCollections = Record<string, AnyRecord[]>;

const projectRoot = fileURLToPath(new URL("../", import.meta.url));
const catalogPath = new URL("../atlas-data/catalog/canonical-catalog.json", import.meta.url);
const statusPath = new URL("../atlas-data/catalog/catalog-status.json", import.meta.url);
const virtualModuleId = "virtual:human-atlas-catalog";
const resolvedVirtualModuleId = `\0${virtualModuleId}`;

function records(entities: EntityCollections, key: string): AnyRecord[] {
  const value = entities[key];
  return Array.isArray(value) ? value : [];
}

function collectIds(values: unknown[]): string[] {
  return values.filter((value): value is string => typeof value === "string");
}

async function readPilotCatalog(): Promise<unknown> {
  try {
    const [catalogText, statusText] = await Promise.all([
      readFile(catalogPath, "utf8"),
      readFile(statusPath, "utf8"),
    ]);
    const rawCatalog = JSON.parse(catalogText) as { revision?: string; entities?: EntityCollections };
    const status = JSON.parse(statusText) as AnyRecord;
    const entities = rawCatalog.entities;

    if (!entities || typeof entities !== "object") {
      throw new Error("canonical-catalog.json에 entities 객체가 없습니다.");
    }

    const pilot = status.pilotStructureText as AnyRecord | undefined;
    const muscleIds = collectIds(Array.isArray(pilot?.pilotMuscleConcepts) ? pilot.pilotMuscleConcepts : []);
    const partIds = collectIds(Array.isArray(pilot?.gastrocnemiusHeadParts) ? pilot.gastrocnemiusHeadParts : []);
    if (muscleIds.length === 0) {
      throw new Error("catalog-status.json에 pilot muscle ID 목록이 없습니다.");
    }

    const conceptsSource = records(entities, "muscleConcepts");
    const conceptsById = new Map(conceptsSource.map((row) => [row.id, row]));
    const expectedIds = [...muscleIds, ...partIds];
    const missingConceptIds = expectedIds.filter((id) => !conceptsById.has(id));
    const concepts = expectedIds.flatMap((id) => {
      const row = conceptsById.get(id);
      return row ? [row] : [];
    });
    const conceptIdSet = new Set(concepts.map((row) => row.id as string));

    const attachments = records(entities, "attachments").filter((row) =>
      conceptIdSet.has(row.muscleOrPartId as string),
    );
    const attachmentIdSet = new Set(attachments.map((row) => row.id as string));
    const claims = records(entities, "claims").filter((row) =>
      conceptIdSet.has(row.subjectId as string) || attachmentIdSet.has(row.subjectId as string),
    );
    const claimIds = new Set(claims.map((row) => row.id as string));

    const structureIds = new Set<string>();
    for (const row of attachments) {
      if (typeof row.targetStructureId === "string") structureIds.add(row.targetStructureId);
      if (typeof row.landmarkId === "string") structureIds.add(row.landmarkId);
    }
    for (const claim of claims) {
      const value = claim.value as AnyRecord | undefined;
      if (typeof value?.targetStructureId === "string") structureIds.add(value.targetStructureId);
      if (Array.isArray(value?.relatedStructureIds)) {
        collectIds(value.relatedStructureIds).forEach((id) => structureIds.add(id));
      }
    }

    const allStructures = records(entities, "structures");
    const structures = allStructures.filter((row) => structureIds.has(row.id as string));
    const structureTermIds = new Set(
      structures.flatMap((row) => collectIds(Array.isArray(row.termIds) ? row.termIds : [])),
    );
    const allTerms = records(entities, "terms");
    const terms = allTerms.filter((row) =>
      conceptIdSet.has(row.conceptId as string) || structureTermIds.has(row.id as string),
    );

    const evidenceIds = new Set<string>();
    for (const term of terms) {
      collectIds(Array.isArray(term.evidenceIds) ? term.evidenceIds : []).forEach((id) => evidenceIds.add(id));
    }
    for (const claim of claims) {
      collectIds(Array.isArray(claim.evidenceIds) ? claim.evidenceIds : []).forEach((id) => evidenceIds.add(id));
    }
    const evidence = records(entities, "evidence").filter((row) => evidenceIds.has(row.id as string));
    const sourceIds = new Set(evidence.map((row) => row.sourceId).filter((id): id is string => typeof id === "string"));
    const sources = records(entities, "sources").filter((row) => sourceIds.has(row.id as string));

    const warnings: string[] = [];
    if (missingConceptIds.length > 0) warnings.push("pilot_id_missing_from_catalog");
    if (status.catalogComplete !== true) warnings.push("catalog_is_partial");
    if (claims.some((row) => row.reviewState !== "reviewed")) warnings.push("claims_need_review");

    return {
      revision: rawCatalog.revision ?? null,
      catalogStatus: status,
      pilotMuscleIds: muscleIds,
      headPartIds: partIds,
      concepts,
      regions: records(entities, "regions"),
      terms,
      structures,
      attachments,
      claims: claims.filter((row) => claimIds.has(row.id as string)),
      evidence,
      sources,
      missingConceptIds,
      warnings,
    };
  } catch (error) {
    return {
      loadError: error instanceof Error ? error.message : "카탈로그 파일을 읽지 못했습니다.",
      concepts: [],
      regions: [],
      terms: [],
      structures: [],
      attachments: [],
      claims: [],
      evidence: [],
      sources: [],
      pilotMuscleIds: [],
      headPartIds: [],
      missingConceptIds: [],
      warnings: [],
    };
  }
}

function catalogPlugin(): Plugin {
  return {
    name: "human-atlas-catalog-loader",
    resolveId(id) {
      if (id === virtualModuleId) return resolvedVirtualModuleId;
    },
    async load(id) {
      if (id !== resolvedVirtualModuleId) return;
      const data = await readPilotCatalog();
      return `export default ${JSON.stringify(data)};`;
    },
    configureServer(server) {
      server.watcher.add([
        fileURLToPath(catalogPath),
        fileURLToPath(statusPath),
      ]);
    },
    handleHotUpdate({ file, server }) {
      const catalogFile = fileURLToPath(catalogPath);
      const statusFile = fileURLToPath(statusPath);
      if (file !== catalogFile && file !== statusFile) return;
      const module = server.moduleGraph.getModuleById(resolvedVirtualModuleId);
      if (module) {
        server.moduleGraph.invalidateModule(module);
        return [module];
      }
    },
  };
}

export default defineConfig({
  root: projectRoot + "atlas-web",
  plugins: [catalogPlugin()],
  server: { strictPort: true },
  preview: { strictPort: true },
});
