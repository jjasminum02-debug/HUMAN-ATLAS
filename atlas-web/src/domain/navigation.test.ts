import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  parseAtlasRoute,
  resolveSceneMeshPick,
  serializeAtlasRoute,
  validateNavigationContract,
  validateSelection,
  type NavigationContract,
  type SceneManifest,
  type SelectionReferences,
} from "./navigation.ts";

const navigation = JSON.parse(readFileSync(new URL("../../../atlas-data/navigation/atlas-navigation.json", import.meta.url), "utf8")) as NavigationContract;
const catalog = JSON.parse(readFileSync(new URL("../../../atlas-data/catalog/canonical-catalog.json", import.meta.url), "utf8")).entities;
const structureInstances = new Map(navigation.structureInstances.map((row) => [row.id, { structureId: row.structureId, side: row.side }]));
const refs: SelectionReferences = {
  muscles: new Map(catalog.muscleConcepts.map((row: { id: string; entityType: string }) => [row.id, { entityType: row.entityType }])),
  muscleInstances: new Map(catalog.instances.map((row: { id: string; conceptId: string; side: "left" | "right" | "midline" | "unpaired" }) => [row.id, { conceptId: row.conceptId, side: row.side }])),
  muscleParts: new Map(catalog.muscleConcepts.filter((row: { entityType: string }) => row.entityType === "muscle_part").map((row: { id: string; parentId: string }) => [row.id, { parentId: row.parentId }])),
  structures: new Map(catalog.structures.map((row: { id: string; kind: string; parentId?: string }) => [row.id, { kind: row.kind, parentId: row.parentId }])),
  structureInstances,
  meshAssets: new Map(catalog.meshAssets.map((row: { id: string; laterality?: string }) => [row.id, { laterality: row.laterality }])),
  muscleMeshMappings: new Map(catalog.meshMappings.map((row: { id: string; instanceIds: string[]; partIds: string[]; meshIds: string[] }) => [row.id, { instanceIds: row.instanceIds, partIds: row.partIds, meshIds: row.meshIds }])),
  structureMeshMappings: new Map(navigation.structureMeshMappings.map((row) => [row.id, { structureInstanceId: row.structureInstanceId, meshIds: row.meshIds }])),
};
const categories = new Set(navigation.categories.map((row) => row.id));
const legScene = navigation.sceneManifests[0] as SceneManifest;

test("current partial navigation contract resolves all typed references without promoting review", () => {
  assert.deepEqual(validateNavigationContract(navigation, refs), []);
  assert.equal(navigation.categories.length, 12);
  assert.equal(navigation.sceneManifests[0].availability, "partial");
  assert.equal(navigation.sceneManifests[0].stateDimensions.humanAnatomyReview, "not_reviewed");
  assert.equal(navigation.sceneManifests[0].stateDimensions.motion, "absent");
});

test("mesh picks resolve through one typed mapping into a bone selection", () => {
  const result = resolveSceneMeshPick(legScene, "HA-MESH-BP3D4-FJ3387", refs);
  assert.deepEqual(result, {
    status: "selection",
    selection: {
      kind: "bone", conceptId: "HA-S-TIBIA", instanceId: "HA-SI-R-HA-S-TIBIA", meshId: "HA-MESH-BP3D4-FJ3387",
    },
  });
});

test("unconfirmed and absent scene bindings do not retain the previous typed selection", () => {
  assert.deepEqual(resolveSceneMeshPick(legScene, "HA-MESH-BP3D4-FJ3385", refs), {
    status: "context", reasonCode: "canonical_target_unconfirmed",
  });
  assert.deepEqual(resolveSceneMeshPick(legScene, "HA-MESH-NOT-IN-SCENE", refs), { status: "unbound" });
});

test("muscle, whole bone, and landmark selections reject cross-kind references", () => {
  assert.equal(validateSelection({ kind: "muscle", conceptId: "HA-S-TIBIA" }, refs), null);
  assert.equal(validateSelection({ kind: "bone", conceptId: "HA-M-000001" }, refs), null);
  assert.equal(validateSelection({ kind: "bone", conceptId: "HA-S-TIBIA-LATERAL-CONDYLE" }, refs), null);
  assert.equal(validateSelection({ kind: "landmark", conceptId: "HA-S-TIBIA" }, refs), null);
  assert.equal(validateSelection({ kind: "bone", conceptId: "HA-S-TIBIA", instanceId: "HA-SI-L-HA-S-TIBIA" }, refs), null);
});

test("region, typed selection, and legacy muscle URL adapters preserve explicit user choice", () => {
  const parsed = parseAtlasRoute("?region=leg&kind=muscle&id=HA-M-000001&side=right", categories, refs);
  assert.deepEqual(parsed, {
    regionId: "leg", side: "right", selection: { kind: "muscle", conceptId: "HA-M-000001" }, legacyRoute: false,
  });
  const old = parseAtlasRoute("?muscle=HA-M-000001", categories, refs);
  assert.deepEqual(old, {
    regionId: null, side: null, selection: { kind: "muscle", conceptId: "HA-M-000001" }, legacyRoute: true,
  });
  assert.equal(parseAtlasRoute("?region=eye&kind=muscle&id=HA-S-TIBIA", categories, refs), null);
  assert.equal(parseAtlasRoute("?region=not-a-category", categories, refs), null);
  assert.equal(serializeAtlasRoute("?muscle=old&tab=structure", parsed!), "tab=structure&region=leg&kind=muscle&id=HA-M-000001&side=right");
});

test("synthetic obturator internus membership is multi-region only in this test fixture", () => {
  const syntheticId = "TEST-ONLY-OBTURATOR-INTERNUS";
  const syntheticRefs = { ...refs, muscles: new Map(refs.muscles).set(syntheticId, { entityType: "individual_muscle" }) };
  const fixture = structuredClone(navigation) as NavigationContract;
  fixture.memberships = [
    ...fixture.memberships,
    { id: "TEST-MEMBERSHIP-PELVIS", categoryId: "pelvis-perineum", entityKind: "muscle", entityId: syntheticId, reason: "Synthetic regression fixture only.", productDecisionRef: "TEST-ONLY", status: "decision_only" },
    { id: "TEST-MEMBERSHIP-GLUTEAL", categoryId: "gluteal-hip", entityKind: "muscle", entityId: syntheticId, reason: "Synthetic regression fixture only.", productDecisionRef: "TEST-ONLY", status: "decision_only" },
  ];
  assert.deepEqual(validateNavigationContract(fixture, syntheticRefs), []);
  assert.equal(navigation.memberships.some((row) => row.entityId === syntheticId), false, "the synthetic structure must not enter product data");
});
