"""Build T12b canonical geometry links from the immutable T07 manifest.

This script adds only T12b entities. It never infers anatomical identity beyond
the existing provisional T07 crosswalk and keeps every mapping needs_review.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "atlas-data/catalog/canonical-catalog.json"
MANIFEST = ROOT / "atlas-data/manifests/derived-assets-t07.json"
BRIDGE = ROOT / "atlas-data/manifests/canonical-geometry-t12.json"
SOURCE_ID = "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0"


def main() -> None:
    catalog = json.loads(CATALOG.read_text())
    manifest = json.loads(MANIFEST.read_text())
    entities = catalog["entities"]
    assert catalog["revision"] == "T05-pilot-structure-text-v1"
    assert not entities["instances"] and not entities["meshAssets"] and not entities["meshMappings"]
    assert manifest["glb"]["meshCount"] == 11
    nodes = {row["sourceFileId"]: row for row in manifest["meshNodes"]}
    assets = {row["id"]: row for row in manifest["meshAssets"]}
    concepts = {row["id"]: row for row in entities["muscleConcepts"]}
    structures = {row["id"]: row for row in entities["structures"]}
    crosswalk = {row["sourceFileId"]: row for row in manifest["meshCrosswalk"]}
    assert len(nodes) == len(assets) == len(crosswalk) == 11

    entities["sources"].append({
        "id": SOURCE_ID,
        "title": "BodyParts3D downloadable dataset, Release 4.0",
        "authors": ["The Database Center for Life Science"],
        "edition": "LSDB Archive Release 4.0, data update 2013-06-19; archive license notice updated 2025-02-27",
        "year": 2013,
        "urlOrLocalRef": manifest["attribution"]["sourceArchiveUrl"],
        "accessDate": "2026-09-26",
        "license": {
            "id": manifest["attribution"]["licenseId"],
            "name": "Creative Commons Attribution 4.0 International",
            "spdxId": "CC-BY-4.0",
            "allowedUses": ["internal", "research", "learning"],
            "attributionRequired": True,
            "attributionText": manifest["attribution"]["requiredCreditVerbatim"],
            "derivativesAllowed": True,
            "redistributionAllowed": True,
        },
    })

    muscle_crosswalk = [row for row in manifest["meshCrosswalk"] if row["targetEntityType"] != "structure"]
    assert len(muscle_crosswalk) == 7
    parent_ids = sorted({
        concepts[row["targetEntityId"]].get("parentId", row["targetEntityId"])
        if row["targetEntityType"] == "muscle_part" else row["targetEntityId"]
        for row in muscle_crosswalk
    })
    assert len(parent_ids) == 6 and all(concepts[id]["entityType"] == "individual_muscle" for id in parent_ids)
    instances = {concept_id: f"HA-I-R-{concept_id}" for concept_id in parent_ids}
    entities["instances"] = [
        {"id": instance_id, "conceptId": concept_id, "side": "right", "variantId": None}
        for concept_id, instance_id in instances.items()
    ]
    entities["meshAssets"] = copy.deepcopy(manifest["meshAssets"])

    mappings = []
    linked = []
    for row in muscle_crosswalk:
        file_id = row["sourceFileId"]
        node = nodes[file_id]
        target = row["targetEntityId"]
        parent = concepts[target].get("parentId") if row["targetEntityType"] == "muscle_part" else target
        assert parent in instances
        assert row["meshAssetId"] in assets
        assert node["targetEntityId"] == target and node["relationStatus"] == row["relationStatus"]
        evidence_id = f"EV-BP3D4-{file_id}-CROSSWALK"
        locators = node["sourceTableLocators"]
        locator = "; ".join(f"{name} line {line}" for name, line in sorted(locators.items()))
        entities["evidence"].append({
            "id": evidence_id,
            "sourceId": SOURCE_ID,
            "locator": f"LSDB Archive Release 4.0 IS-A crosswalk, {file_id}; {locator}; source OBJ SHA-256 {node['sourceSha256']}. Provisional name/ID relation, no independent anatomy review.",
            "supportedClaimIds": [],
            "evidenceKind": "dataset",
        })
        mappings.append({
            "id": f"HA-MAP-BP3D4-{file_id}",
            "instanceIds": [instances[parent]],
            "partIds": [target] if row["targetEntityType"] == "muscle_part" else [],
            "meshIds": [row["meshAssetId"]],
            "representationType": row["representationType"],
            "evidenceIds": [evidence_id],
            "reviewState": "needs_review",
        })
        linked.append({"fileId": file_id, "meshAssetId": row["meshAssetId"], "instanceId": instances[parent], "partConceptId": target if row["targetEntityType"] == "muscle_part" else None, "mappingId": mappings[-1]["id"], "reviewState": "needs_review"})
    entities["meshMappings"] = mappings

    excluded = []
    for row in manifest["meshCrosswalk"]:
        if row["targetEntityType"] != "structure": continue
        target = row["targetEntityId"]
        excluded.append({
            "fileId": row["sourceFileId"],
            "meshAssetId": row["meshAssetId"],
            "structureId": target,
            "structureExists": target in structures if target else False,
            "reason": "MeshMapping has no structure-target field; asset remains canonical, mapping is excluded" if target else "No canonical talus structure ID; do not invent one. Asset remains canonical with null crosswalk target, mapping excluded",
            "reviewState": "needs_review",
        })
    assert len(excluded) == 4 and any(row["fileId"] == "FJ3385" and row["structureId"] is None for row in excluded)
    bridge = {
        "schemaVersion": "T12b-canonical-geometry-bridge-v1",
        "modelId": manifest["modelId"],
        "sourceId": SOURCE_ID,
        "sourceManifest": "atlas-data/manifests/derived-assets-t07.json",
        "sourceGlbSha256": manifest["glb"]["sha256"],
        "frameId": manifest["transform"]["targetFrameId"],
        "units": manifest["transform"]["targetUnits"],
        "poseId": manifest["poseId"],
        "reviewState": "needs_review",
        "muscleLinks": linked,
        "unmappedStructureAssets": excluded,
        "coverage": {"meshAssets": 11, "rightMuscleInstances": 6, "muscleMeshMappings": 7, "unmappedStructureAssets": 4},
    }
    catalog["revision"] = "T12b-canonical-geometry-links-v1"
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    BRIDGE.write_text(json.dumps(bridge, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(bridge["coverage"], ensure_ascii=False))


if __name__ == "__main__":
    main()
