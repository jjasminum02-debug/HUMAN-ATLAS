import rawBoneNames from "../../../atlas-data/terminology/bone-name-overlay-t42.json" with { type: "json" };
import type { PilotCatalog } from "./catalog";
import { learnerSearchEntry, searchEntries, type SearchMatch } from "../domain/search.ts";
import type { BoneSelection, NavigationContract } from "../domain/navigation";

export interface BoneNameEntry {
  id: string;
  displayTitle: string;
  koModern: string;
  koTraditional: string;
  english: string;
  humanAnatomyReview: "not_reviewed";
  aliases: Array<{ text: string; sourceIds: string[]; locator: string }>;
}

export interface BoneSearchMatch extends SearchMatch {
  selection: BoneSelection;
}

const entries = (rawBoneNames as { entries: BoneNameEntry[] }).entries;
const entryById = new Map(entries.map((entry) => [entry.id, entry]));

/** Learner-facing name fields; provenance remains in the source overlay. */
export function boneNameForLearner(id: string) {
  const entry = entryById.get(id);
  if (!entry) return { label: "설명 정리 중", koTraditional: "", koModern: "", en: "" };
  return {
    label: entry.displayTitle,
    koTraditional: entry.koTraditional,
    koModern: entry.koModern,
    en: entry.english,
  };
}

function selectionForBone(navigation: NavigationContract, conceptId: string): BoneSelection | null {
  const instances = navigation.structureInstances.filter((row) => row.structureId === conceptId);
  if (instances.length !== 1) return null;
  const instance = instances[0];
  const mappings = navigation.structureMeshMappings.filter((row) => row.structureInstanceId === instance.id);
  const meshIds = [...new Set(mappings.flatMap((mapping) => mapping.meshIds))];
  const isSelectable = navigation.sceneManifests.some((scene) => scene.availability !== "unavailable" &&
    scene.selectableBindings.some((binding) => binding.selection.kind === "bone" &&
      binding.selection.conceptId === conceptId && binding.selection.instanceId === instance.id));
  if (!isSelectable || meshIds.length !== 1) return null;
  return { kind: "bone", conceptId, instanceId: instance.id, meshId: meshIds[0] };
}

/** Search only the source-backed bone overlay entries with a verified learner selection route. */
export function searchSelectableBones(
  catalog: Pick<PilotCatalog, "structures" | "terms">,
  navigation: NavigationContract,
  query: string,
): BoneSearchMatch[] {
  const eligible = entries.flatMap((entry) => {
    const structure = catalog.structures.find((row) => row.id === entry.id && row.kind === "bone");
    const selection = structure && selectionForBone(navigation, entry.id);
    if (!structure || !selection) return [];
    const terms = catalog.terms.filter((term) => term.conceptId === entry.id &&
      typeof term.text === "string" && ["ko", "en", "la"].includes(String(term.language)));
    const searchEntry = learnerSearchEntry(entry.id, entry.displayTitle, [
      entry.koModern,
      entry.koTraditional,
      entry.english,
      ...entry.aliases.map((alias) => alias.text),
      ...terms.map((term) => term.text),
    ]);
    return [{ entry: searchEntry, selection }];
  });
  const entryBySearchId = new Map(eligible.map((row) => [row.entry.id, row]));
  return searchEntries(eligible.map((row) => row.entry), query).flatMap((match) => {
    const selected = entryBySearchId.get(match.entry.id);
    return selected ? [{ ...match, selection: selected.selection }] : [];
  });
}
