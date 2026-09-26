import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { buildBoneCardData } from "./boneCard.ts";
import type { PilotCatalog } from "../data/catalog";
import type { NavigationContract } from "./navigation.ts";

const navigation = JSON.parse(readFileSync(new URL("../../../atlas-data/navigation/atlas-navigation.json", import.meta.url), "utf8")) as NavigationContract;
const raw = JSON.parse(readFileSync(new URL("../../../atlas-data/catalog/canonical-catalog.json", import.meta.url), "utf8"));
const catalog = {
  structures: raw.entities.structures,
  terms: raw.entities.terms,
  attachments: raw.entities.attachments,
  claims: raw.entities.claims,
  evidence: raw.entities.evidence,
  sources: raw.entities.sources,
  concepts: raw.entities.muscleConcepts,
} as PilotCatalog;

test("bone card uses source-backed names, right instance, explicit landmarks and evidence-backed muscle relations", () => {
  const card = buildBoneCardData(catalog, navigation, {
    kind: "bone", conceptId: "HA-S-FEMUR", instanceId: "HA-SI-R-HA-S-FEMUR", meshId: "HA-MESH-BP3D4-FJ3365",
  });
  assert.ok(card);
  assert.equal(card.label, "Femur");
  assert.equal(card.side, "right");
  assert.ok(card.nameSources.some((source) => source.id === "GRAY_ANATOMY_20E_1918"));
  assert.ok(card.landmarks.some((row) => row.id === "HA-S-FEMORAL-CONDYLE-LATERAL"));
  assert.ok(card.landmarks.every((row) => row.id !== card.conceptId));
  assert.deepEqual(card.relations.map((row) => row.muscleOrPartId).sort(), ["HA-P-000001", "HA-P-000002"]);
  assert.ok(card.relations.every((row) => row.sources.some((source) => source.id === "GRAY_ANATOMY_20E_1918")));
});

test("bone card does not promote unsupported attachment relations or accept a landmark as a whole bone", () => {
  const noEvidence: PilotCatalog = {
    ...catalog,
    claims: catalog.claims.map((row) => ["HA-C-T05-GASTRO-LAT-FEMUR-ORIGIN", "HA-C-T05-GASTRO-LAT-FEMUR-POSTERIOR-ORIGIN"].includes(row.id) ? { ...row, evidenceIds: [] } : row),
  };
  const card = buildBoneCardData(noEvidence, navigation, {
    kind: "bone", conceptId: "HA-S-FEMUR", instanceId: "HA-SI-R-HA-S-FEMUR", meshId: "HA-MESH-BP3D4-FJ3365",
  });
  assert.ok(card);
  assert.ok(!card.relations.some((row) => row.muscleOrPartId === "HA-P-000001"));
  assert.ok(!card.landmarks.some((row) => row.id === "HA-S-FEMORAL-CONDYLE-LATERAL"));
  assert.equal(buildBoneCardData(catalog, navigation, {
    kind: "bone", conceptId: "HA-S-FEMORAL-CONDYLE-LATERAL", instanceId: "HA-SI-R-HA-S-FEMUR",
  }), null);
});
