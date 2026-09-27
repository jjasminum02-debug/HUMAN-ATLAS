import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { boneNameForLearner, searchSelectableBones } from "./boneNames.ts";
import type { NavigationContract } from "../domain/navigation.ts";
import type { PilotCatalog } from "./catalog.ts";
import { hasHanScript } from "../domain/search.ts";

const overlay = JSON.parse(readFileSync(new URL("../../../atlas-data/terminology/bone-name-overlay-t42.json", import.meta.url), "utf8")) as {
  entries: Array<{ id: string; displayTitle: string; koModern: string; koTraditional: string; english: string; aliases: Array<{ text: string; sourceIds: string[]; locator: string }> }>;
};
const catalogJson = JSON.parse(readFileSync(new URL("../../../atlas-data/catalog/canonical-catalog.json", import.meta.url), "utf8")) as {
  entities: { structures: PilotCatalog["structures"]; terms: PilotCatalog["terms"] };
};
const navigation = JSON.parse(readFileSync(new URL("../../../atlas-data/navigation/atlas-navigation.json", import.meta.url), "utf8")) as NavigationContract;
const catalog = { structures: catalogJson.entities.structures, terms: catalogJson.entities.terms };

test("the bone overlay supplies three Hangul-safe names without changing IDs or human review", () => {
  assert.equal(overlay.entries.length, 9);
  for (const entry of overlay.entries) {
    const projection = boneNameForLearner(entry.id);
    assert.deepEqual(projection, {
      label: entry.displayTitle,
      koTraditional: entry.koTraditional,
      koModern: entry.koModern,
      en: entry.english,
    });
    assert.ok(entry.koModern && entry.koTraditional && entry.english, entry.id);
    assert.equal(hasHanScript(JSON.stringify(entry)), false, entry.id);
    assert.ok(entry.aliases.every((alias) => alias.sourceIds.length > 0 && alias.locator.trim()), entry.id);
  }
});

test("every source-backed name and synonym selects the existing matching selectable bone instance", () => {
  const checks: Array<[string, string]> = [
    ["대퇴골", "HA-S-FEMUR"], ["넓적다리뼈", "HA-S-FEMUR"], ["thigh bone", "HA-S-FEMUR"], ["os femoris", "HA-S-FEMUR"],
    ["정강뼈", "HA-S-TIBIA"], ["경골", "HA-S-TIBIA"], ["shin bone", "HA-S-TIBIA"],
    ["종아리뼈", "HA-S-FIBULA"], ["비골", "HA-S-FIBULA"], ["os fibulare", "HA-S-FIBULA"],
    ["발꿈치뼈", "HA-S-CALCANEUS"], ["종골", "HA-S-CALCANEUS"], ["os calcis", "HA-S-CALCANEUS"],
    ["입방뼈", "HA-S-CUBOID"], ["입방골", "HA-S-CUBOID"], ["cuboid bone", "HA-S-CUBOID"],
    ["안쪽쐐기뼈", "HA-S-MEDIAL-CUNEIFORM"], ["내측설상골", "HA-S-MEDIAL-CUNEIFORM"], ["os cuneiforme primum", "HA-S-MEDIAL-CUNEIFORM"],
    ["발배뼈", "HA-S-NAVICULAR"], ["주상골", "HA-S-NAVICULAR"], ["os naviculare pedis", "HA-S-NAVICULAR"],
    ["첫째발허리뼈", "HA-S-METATARSAL-1"], ["first metatarsal bone", "HA-S-METATARSAL-1"], ["os i metatarsi", "HA-S-METATARSAL-1"],
    ["다섯째발허리뼈", "HA-S-METATARSAL-5"], ["fifth metatarsal bone", "HA-S-METATARSAL-5"], ["os v metatarsi", "HA-S-METATARSAL-5"],
  ];
  for (const [query, id] of checks) {
    const result = searchSelectableBones(catalog as Pick<PilotCatalog, "structures" | "terms">, navigation, query);
    assert.equal(result[0]?.entry.id, id, query);
    assert.equal(result[0]?.selection.conceptId, id, `${query} route ID`);
    assert.equal(result[0]?.selection.kind, "bone", `${query} route type`);
    assert.ok(result[0]?.selection.instanceId && result[0]?.selection.meshId, `${query} must be bound to an existing instance and mesh`);
  }
});

test("the common metatarsal term remains an explicit two-result ambiguity", () => {
  const ids = searchSelectableBones(catalog as Pick<PilotCatalog, "structures" | "terms">, navigation, "중족골").map((row) => row.entry.id);
  assert.deepEqual(new Set(ids), new Set(["HA-S-METATARSAL-1", "HA-S-METATARSAL-5"]));
});

test("unmapped bone concepts are not added to learner search", () => {
  assert.deepEqual(searchSelectableBones(catalog as Pick<PilotCatalog, "structures" | "terms">, navigation, "talus"), []);
});
