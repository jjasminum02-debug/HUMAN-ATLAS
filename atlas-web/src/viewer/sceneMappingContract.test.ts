import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync } from "node:fs";
import { sceneMappingTargets } from "./sceneMappingContract.ts";

const assets = [{ id: "scene-mesh" }, { id: "other-mesh" }];
const instances = [
  { id: "right-instance", conceptId: "muscle", side: "right" },
  { id: "left-instance", conceptId: "other-muscle", side: "left" },
];
const mappings = [
  { id: "scene-map", meshIds: ["scene-mesh"], instanceIds: ["right-instance"], partIds: ["part"], evidenceIds: ["evidence"], reviewState: "needs_review" },
  { id: "other-map", meshIds: ["other-mesh"], instanceIds: ["left-instance"], partIds: [], evidenceIds: ["other-evidence"], reviewState: "reviewed" },
];

test("scene subset stays valid when other regions and left records are added or review states change", () => {
  assert.deepEqual([...sceneMappingTargets(["scene-mesh"], assets, instances, mappings, "right")], [["scene-mesh", "part"]]);
  const updated = mappings.map((row) => ({ ...row, reviewState: "reviewed" }));
  assert.deepEqual([...sceneMappingTargets(["scene-mesh"], assets, instances, updated, "right")], [["scene-mesh", "part"]]);
});

test("scene subset rejects missing asset, missing mapping, duplicate mapping and wrong-side selected instance", () => {
  assert.throws(() => sceneMappingTargets(["missing"], assets, instances, mappings, "right"), /asset 참조/);
  assert.throws(() => sceneMappingTargets(["scene-mesh"], assets, instances, [], "right"), /없거나 중복/);
  assert.throws(() => sceneMappingTargets(["scene-mesh"], assets, instances, [...mappings, mappings[0]], "right"), /없거나 중복/);
  assert.throws(() => sceneMappingTargets(["other-mesh"], assets, instances, mappings, "right"), /좌우/);
});

test("actual seven calf meshes survive unrelated region and left records plus review progression", () => {
  const catalog = JSON.parse(readFileSync(new URL("../../../atlas-data/catalog/canonical-catalog.json", import.meta.url), "utf8")).entities;
  const manifest = JSON.parse(readFileSync(new URL("../../../atlas-data/manifests/derived-assets-t07.json", import.meta.url), "utf8"));
  const sceneIds = manifest.meshNodes.filter((row: { targetEntityType: string }) => row.targetEntityType !== "structure")
    .map((row: { meshAssetId: string }) => row.meshAssetId);
  const extra = {
    assets: [...catalog.meshAssets, { id: "HA-MESH-OTHER-LEFT" }],
    instances: [...catalog.instances, { id: "HA-I-L-OTHER", conceptId: "OTHER", side: "left" }],
    mappings: [...catalog.meshMappings.map((row: { reviewState: string }) => ({ ...row, reviewState: "reviewed" })),
      { id: "HA-MAP-OTHER", meshIds: ["HA-MESH-OTHER-LEFT"], instanceIds: ["HA-I-L-OTHER"], partIds: [], evidenceIds: ["EV-OTHER"], reviewState: "reviewed" }],
  };
  const targets = sceneMappingTargets(sceneIds, extra.assets, extra.instances, extra.mappings, "right");
  assert.equal(targets.size, 7);
  for (const row of manifest.meshNodes.filter((item: { targetEntityType: string }) => item.targetEntityType !== "structure")) {
    assert.equal(targets.get(row.meshAssetId), row.targetEntityId);
  }
});
