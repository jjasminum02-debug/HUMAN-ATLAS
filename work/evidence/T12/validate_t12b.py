"""T12b geometry coverage and contract regression against the T07 manifest."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCHEMAS = ROOT / "atlas-data/schemas"


def read(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text())


def main() -> None:
    spec = importlib.util.spec_from_file_location("atlas_validate", SCHEMAS / "validate.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    schema = read("atlas-data/schemas/atlas.schema.json")
    catalog = read("atlas-data/catalog/canonical-catalog.json")
    t07 = read("atlas-data/manifests/derived-assets-t07.json")
    bridge = read("atlas-data/manifests/canonical-geometry-t12.json")
    entities = catalog["entities"]
    nodes = {row["sourceFileId"]: row for row in t07["meshNodes"]}
    t07_assets = {row["id"]: row for row in t07["meshAssets"]}
    assets = {row["id"]: row for row in entities["meshAssets"] if row["id"] in t07_assets}
    instances = {row["id"]: row for row in entities["instances"]}
    mappings = {row["id"]: row for row in entities["meshMappings"]}
    evidence = {row["id"]: row for row in entities["evidence"]}
    source = {row["id"]: row for row in entities["sources"]}
    concepts = {row["id"]: row for row in entities["muscleConcepts"]}

    assert module.validate_dataset(catalog, schema) == []
    assert (len(nodes), len(assets), len(instances), len(mappings)) == (11, 11, 6, 7)
    assert bridge["coverage"] == {"meshAssets": 11, "rightMuscleInstances": 6, "muscleMeshMappings": 7, "unmappedStructureAssets": 4}
    glb_path = ROOT / t07["glb"]["uri"]
    assert glb_path.stat().st_size == t07["glb"]["bytes"]
    assert hashlib.sha256(glb_path.read_bytes()).hexdigest() == t07["glb"]["sha256"] == bridge["sourceGlbSha256"]
    transform = t07["transform"]
    assert transform["combinedLinearMatrix"] == [[0.001, 0, 0], [0, 0, 0.001], [0, -0.001, 0]]
    assert transform["targetFrameId"] == bridge["frameId"] and bridge["units"] == "m" and bridge["poseId"] == t07["poseId"]
    assert all(asset == t07_assets[asset_id] for asset_id, asset in assets.items())
    assert all(asset["hash"] == bridge["sourceGlbSha256"] and asset["laterality"] == "right" and asset["pose"]["id"] == bridge["poseId"] for asset in assets.values())
    assert all(instance["side"] == "right" and concepts[instance["conceptId"]]["entityType"] == "individual_muscle" for instance in instances.values())
    assert bridge["sourceId"] in source and source[bridge["sourceId"]]["license"]["spdxId"] == "CC-BY-4.0"
    assert len(bridge["muscleLinks"]) == 7
    for link in bridge["muscleLinks"]:
        node = nodes[link["fileId"]]
        mapping = mappings[link["mappingId"]]
        assert node["meshAssetId"] == link["meshAssetId"] and node["targetEntityType"] != "structure"
        assert mapping["meshIds"] == [link["meshAssetId"]] and mapping["instanceIds"] == [link["instanceId"]]
        assert mapping["reviewState"] == link["reviewState"] == "needs_review"
        assert mapping["partIds"] == ([link["partConceptId"]] if link["partConceptId"] else [])
        assert node["targetEntityId"] == (link["partConceptId"] or instances[link["instanceId"]]["conceptId"])
        assert all(evidence[eid]["sourceId"] == bridge["sourceId"] and "line" in evidence[eid]["locator"] for eid in mapping["evidenceIds"])
    excluded = bridge["unmappedStructureAssets"]
    assert len(excluded) == 4 and {row["fileId"] for row in excluded} == {"FJ3360", "FJ3366", "FJ3385", "FJ3387"}
    assert all(nodes[row["fileId"]]["targetEntityType"] == "structure" and row["meshAssetId"] in assets and row["reviewState"] == "needs_review" for row in excluded)
    assert next(row for row in excluded if row["fileId"] == "FJ3385")["structureId"] is None
    assert not entities["spatialAnnotations"]

    wrong_parent = copy.deepcopy(catalog)
    wrong_parent["entities"]["meshMappings"][0]["instanceIds"] = ["HA-I-R-HA-M-000002"]
    parent_codes = {issue["code"] for issue in module.validate_dataset(wrong_parent, schema)}
    assert "mesh_part_instance_parent_mismatch" in parent_codes
    wrong_side = copy.deepcopy(catalog)
    wrong_side["entities"]["instances"][0]["side"] = "left"
    side_codes = {issue["code"] for issue in module.validate_dataset(wrong_side, schema)}
    assert "mesh_laterality_mismatch" in side_codes
    print(json.dumps({"passed": True, "meshAssets": 11, "rightMuscleInstances": 6, "muscleMeshMappings": 7,
                      "structureAssetsExplicitlyUnmapped": 4, "talusIdExcluded": True, "glbHash": bridge["sourceGlbSha256"],
                      "frame": bridge["frameId"], "units": bridge["units"], "pose": bridge["poseId"],
                      "negativeParentMismatchRejected": True, "negativeSideMismatchRejected": True,
                      "spatialAnnotationsUnchanged": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
