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
import {
  boneSelectionForMesh,
  categoriesForMuscleConcept,
  categoryMemberships,
  defaultLearnerRoute,
  resolveLearnerRoute,
  routeForCategory,
  routeForMuscleSelection,
  routeForBoneSelection,
} from "./regionNavigation.ts";

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

test("sourced bone mesh selection round-trips through an explicit typed URL and stays separate from landmarks", () => {
  const selection = boneSelectionForMesh(navigation, "HA-MESH-BP3D4-FJ3387");
  assert.deepEqual(selection, {
    kind: "bone", conceptId: "HA-S-TIBIA", instanceId: "HA-SI-R-HA-S-TIBIA", meshId: "HA-MESH-BP3D4-FJ3387",
  });
  assert.deepEqual(routeForBoneSelection(navigation, selection!), {
    regionId: "leg", side: "right", selection, legacyRoute: false,
  });
  const route = parseAtlasRoute("?region=leg&kind=bone&id=HA-S-TIBIA&instance=HA-SI-R-HA-S-TIBIA&mesh=HA-MESH-BP3D4-FJ3387&side=right", categories, refs);
  assert.deepEqual(route?.selection, selection);
  assert.equal(serializeAtlasRoute("", route!), "region=leg&kind=bone&id=HA-S-TIBIA&instance=HA-SI-R-HA-S-TIBIA&mesh=HA-MESH-BP3D4-FJ3387&side=right");
  assert.equal(parseAtlasRoute("?region=leg&kind=bone&id=HA-S-TIBIA-LATERAL-CONDYLE&instance=HA-SI-R-HA-S-TIBIA", categories, refs), null);
  assert.equal(parseAtlasRoute("?region=leg&kind=bone&id=HA-S-TIBIA&instance=HA-SI-R-HA-S-TIBIA&mesh=HA-MESH-BP3D4-FJ3360&side=right", categories, refs), null);
});

test("all nine source-linked bone mappings can be typed while the four unconfirmed meshes stay unbound", () => {
  for (const mapping of navigation.structureMeshMappings) {
    assert.equal(mapping.reviewState, "needs_review");
    for (const meshId of mapping.meshIds) {
      const selection = boneSelectionForMesh(navigation, meshId);
      assert.ok(selection, `${meshId} should resolve through its existing source mapping`);
      assert.equal(selection.kind, "bone");
      assert.equal(navigation.structureInstances.find((row) => row.id === selection.instanceId)?.side, "right");
    }
  }
  for (const context of navigation.unmappedMeshContexts ?? []) assert.equal(boneSelectionForMesh(navigation, context.meshAssetId), null);
  const directBoneRoute = resolveLearnerRoute("?kind=bone&id=HA-S-FEMUR", navigation, refs);
  assert.equal(directBoneRoute.route.regionId, "leg");
  assert.deepEqual(directBoneRoute.route.selection, {
    kind: "bone", conceptId: "HA-S-FEMUR", instanceId: "HA-SI-R-HA-S-FEMUR", meshId: "HA-MESH-BP3D4-FJ3365",
  });
  assert.equal(directBoneRoute.canonicalize, true);
});

test("unconfirmed and absent scene bindings do not retain the previous typed selection", () => {
  assert.deepEqual(resolveSceneMeshPick(legScene, "HA-MESH-BP3D4-FJ3385", refs), {
    status: "context", reasonCode: "canonical_target_unconfirmed",
  });
  assert.deepEqual(resolveSceneMeshPick(legScene, "HA-MESH-NOT-IN-SCENE", refs), { status: "unbound" });
});

test("T13 scene keeps six sourced bones selectable and three source meshes unbound", () => {
  const scene = navigation.sceneManifests[1];
  assert.equal(scene.selectableBindings.length, 6);
  assert.equal(scene.contextBindings.length, 3);
  assert.deepEqual(resolveSceneMeshPick(scene, "HA-MESH-BP3D4-FJ3365", refs), {
    status: "selection", selection: {
      kind: "bone", conceptId: "HA-S-FEMUR", instanceId: "HA-SI-R-HA-S-FEMUR", meshId: "HA-MESH-BP3D4-FJ3365",
    },
  });
  assert.deepEqual(resolveSceneMeshPick(scene, "HA-MESH-BP3D4-FJ3353", refs), { status: "context", reasonCode: "canonical_target_unconfirmed" });
});

test("explicit empty typed selection survives URL normalization and reload", () => {
  const state = resolveLearnerRoute("?region=leg&side=right", navigation, refs);
  assert.equal(state.route.selection, null);
  assert.equal(state.canonicalize, false);
  assert.equal(serializeAtlasRoute("", state.route), "region=leg&side=right");
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
  const part = parseAtlasRoute("?region=leg&kind=muscle&id=HA-M-000001&part=HA-P-000001", categories, refs);
  assert.deepEqual(part, {
    regionId: "leg", side: null, selection: { kind: "muscle", conceptId: "HA-M-000001", partId: "HA-P-000001" }, legacyRoute: false,
  });
  assert.equal(serializeAtlasRoute("", part!), "region=leg&kind=muscle&id=HA-M-000001&part=HA-P-000001");
});

test("learner category routes expose twelve regions but only the six sourced leg memberships", () => {
  assert.equal(navigation.categories.length, 12);
  assert.deepEqual(categoryMemberships(navigation, "leg").map((row) => row.entityId), [
    "HA-M-000001", "HA-M-000002", "HA-M-000003", "HA-M-000004", "HA-M-000005", "HA-M-000006",
  ]);
  for (const category of navigation.categories.filter((row) => row.id !== "leg")) {
    assert.deepEqual(categoryMemberships(navigation, category.id), [], `${category.id} must not gain inferred members`);
  }
  assert.deepEqual(categoriesForMuscleConcept(navigation, "HA-M-000001"), ["leg"]);
  assert.deepEqual(categoriesForMuscleConcept(navigation, "HA-M-000030"), []);
});

test("home and category navigation never implicitly select a muscle", () => {
  assert.deepEqual(defaultLearnerRoute(navigation), {
    regionId: null, side: null, selection: null, legacyRoute: false,
  });
  assert.deepEqual(resolveLearnerRoute("", navigation, refs).route, defaultLearnerRoute(navigation));
  assert.deepEqual(routeForCategory(navigation, "head", { kind: "muscle", conceptId: "HA-M-000001" }), {
    regionId: "head", side: null, selection: null, legacyRoute: false,
  });
  assert.deepEqual(routeForCategory(navigation, "leg", null), {
    regionId: "leg", side: null, selection: null, legacyRoute: false,
  });
  const unsupported = resolveLearnerRoute("?region=foot", navigation, refs);
  assert.equal(unsupported.route.regionId, "foot");
  assert.equal(unsupported.route.selection, null);
  const mismatch = resolveLearnerRoute("?region=foot&kind=muscle&id=HA-M-000001", navigation, refs);
  assert.equal(mismatch.route.regionId, "foot");
  assert.equal(mismatch.route.selection, null);
  assert.match(mismatch.notice ?? "", /연결되어 있지 않습니다/);
});

test("legacy pilot links canonicalize to leg, while unassigned search selections stay unassigned", () => {
  const legacy = resolveLearnerRoute("?muscle=HA-M-000001", navigation, refs);
  assert.equal(legacy.canonicalize, true);
  assert.deepEqual(legacy.route, {
    regionId: "leg", side: "right", selection: { kind: "muscle", conceptId: "HA-M-000001" }, legacyRoute: false,
  });
  const unassigned = resolveLearnerRoute("?kind=muscle&id=HA-M-000030", navigation, refs);
  assert.equal(unassigned.route.regionId, null);
  assert.deepEqual(unassigned.route.selection, { kind: "muscle", conceptId: "HA-M-000030" });
});

test("search selection routes parts through their existing parent without inventing a region", () => {
  assert.deepEqual(routeForMuscleSelection(navigation, "HA-M-000001", "HA-P-000001", "leg"), {
    regionId: "leg", side: "right", selection: { kind: "muscle", conceptId: "HA-M-000001", partId: "HA-P-000001" }, legacyRoute: false,
  });
  assert.deepEqual(routeForMuscleSelection(navigation, "HA-M-000030", undefined, null), {
    regionId: null, side: null, selection: { kind: "muscle", conceptId: "HA-M-000030" }, legacyRoute: false,
  });
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
