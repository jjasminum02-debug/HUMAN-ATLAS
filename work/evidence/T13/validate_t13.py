"""Audit T13 source, asset, claim, context, and review boundaries."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_context(context: dict, catalog: dict, t07: dict, t13: dict) -> None:
    entities = catalog["entities"]
    attachments = {row["id"]: row for row in entities["attachments"]}
    claims = {row["id"]: row for row in entities["claims"]}
    evidence = {row["id"]: row for row in entities["evidence"]}
    structures = {row["id"]: row for row in entities["structures"]}
    assets = {row["id"]: row for row in entities["meshAssets"]}
    instances = {row["id"]: row for row in entities["instances"]}
    concepts = {row["id"]: row for row in entities["muscleConcepts"]}
    nodes = {row["meshAssetId"]: row for row in t07["meshNodes"] + t13["viewerNodes"]}
    assert context["schemaVersion"] == "T13-attachment-context-v2"
    assert context["sourceCatalogRevision"] == catalog["revision"]
    assert context["assetSourceId"] == t13["sourceId"]
    assert (context["frameId"], context["units"], context["poseId"]) == (
        t13["transform"]["frameId"], "m", t13["transform"]["poseId"])
    assert context["assetSets"] == [
        {"manifest": "atlas-data/manifests/derived-assets-t07.json", "glbSha256": t07["glb"]["sha256"], "meshCount": 11},
        {"manifest": "atlas-data/manifests/derived-bones-t13.json", "glbSha256": t13["glb"]["sha256"], "meshCount": 9},
    ]
    rows = context["records"]
    assert len(rows) == len(attachments) == 41
    assert {row["attachmentId"] for row in rows} == set(attachments)
    assert len({row["attachmentId"] for row in rows}) == 41
    available = held = 0
    for row in rows:
        att = attachments[row["attachmentId"]]
        claim = claims[att["descriptionClaimId"]]
        assert row["descriptionClaimId"] == claim["id"]
        assert claim["subjectId"] == att["id"]
        assert claim["field"] == "attachment_description" and claim["reviewState"] == "needs_review"
        assert claim["value"]["targetStructureId"] == att["targetStructureId"]
        assert claim["value"]["summary"] and claim["value"]["edition"]
        assert row["claimEvidenceIds"] == claim["evidenceIds"] and row["claimEvidenceIds"]
        assert all(evidence[eid]["sourceId"] != t13["sourceId"] for eid in row["claimEvidenceIds"])
        assert all(evidence[eid]["locator"] for eid in row["claimEvidenceIds"])
        assert row["ownerConceptId"] == att["muscleOrPartId"]
        owner = concepts[row["ownerConceptId"]]
        parent = owner.get("parentId") if owner["entityType"] == "muscle_part" else owner["id"]
        instance = instances[row["instanceId"]]
        assert instance["conceptId"] == parent and instance["side"] == row["side"] == "right"
        assert row["role"] == att["role"] and row["targetStructureId"] == att["targetStructureId"]
        assert row["targetStructureId"] in structures
        assert row["spatialAnnotationId"] is row["geometry"] is row["precision"] is None
        assert row["surfaceReviewState"] == "not_started" and row["reason"]
        mesh_id = row["contextMeshAssetId"]
        assert row["sourceBoneFileId"] == (mesh_id.rsplit("-", 1)[-1] if mesh_id else None)
        if mesh_id:
            available += 1
            assert row["contextStatus"] == "whole_bone_search_context_only"
            if row["targetBoneId"] is not None:
                assert row["targetBoneId"] in structures
                target = structures[row["targetStructureId"]]
                assert row["targetBoneId"] in (target["id"], target.get("parentId"))
            else:
                assert row["targetStructureId"] in {"HA-S-BASE-METATARSAL-2", "HA-S-BASE-METATARSAL-3", "HA-S-BASE-METATARSAL-4"}
            assert nodes[mesh_id]["targetEntityId"] == row["targetBoneId"]
            assert nodes[mesh_id]["targetEntityType"] == "structure"
            assert assets[mesh_id]["laterality"] == "right"
            assert assets[mesh_id]["pose"]["id"] == context["poseId"]
            assert assets[mesh_id]["axes"]["frameId"] == context["frameId"]
            assert assets[mesh_id]["units"] == "m"
        else:
            held += 1
            assert row["targetBoneId"] is None and row["contextStatus"] == "held_no_matching_target_mesh"
    assert (available, held) == (28, 13)
    assert context["coverage"] == {
        "t05Attachments": 41, "wholeBoneContexts": 28, "heldWithoutTargetMesh": 13,
        "locatedSurfaceAnnotations": 0, "humanReviewedSurfaces": 0,
    }
    assert entities["spatialAnnotations"] == [] and entities["reviews"] == []


def main() -> None:
    schema = load("atlas-data/schemas/atlas.schema.json")
    catalog = load("atlas-data/catalog/canonical-catalog.json")
    context = load("atlas-data/manifests/attachment-context-t13.json")
    t07 = load("atlas-data/manifests/derived-assets-t07.json")
    t13 = load("atlas-data/manifests/derived-bones-t13.json")
    transfer = load("work/evidence/T13/source-transfer.json")
    additional = load("work/evidence/T13/additional-transfer.json")
    t02 = load("atlas-data/manifests/assets.json")
    spec = importlib.util.spec_from_file_location("atlas_validate", ROOT / "atlas-data/schemas/validate.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.validate_dataset(catalog, schema) == []
    assets = catalog["entities"]["meshAssets"]
    assert len(assets) == 20 and len(t13["meshAssets"]) == len(t13["meshNodes"]) == len(t13["sourceAssets"]) == 9
    assert {row["id"] for row in assets} == {row["id"] for row in t07["meshAssets"] + t13["meshAssets"]}
    assert t13["sourceArchiveUrl"] == transfer["sourceArchiveUrl"] == t02["source"]["archiveUrl"]
    assert t13["sourceArchiveEtag"] == transfer["archiveEtag"] == t02["source"]["etag"]
    assert t13["sourceLicenseUrl"] == transfer["licensePage"]
    assert t13["requiredCredit"] == transfer["requiredCredit"] == t02["license"]["archivePageRequiredCredit"]
    assert transfer["archiveSizeBytes"] == t02["source"]["archiveSizeBytes"]
    assert all(additional[key] == transfer[key] for key in ("sourceArchiveUrl", "archiveSizeBytes", "archiveLastModified", "archiveEtag", "licensePage", "requiredCredit", "sourceCoordinates"))
    for name, digest in additional["sourceTableSha256"].items():
        assert sha(ROOT / "work/evidence/T13" / name) == digest == t13["sourceTableSha256"][name]
    assert t13["transform"]["matrix"] == t07["transform"]["combinedLinearMatrix"]
    assert t13["transform"]["frameId"] == t07["transform"]["targetFrameId"]
    assert t13["transform"]["poseId"] == t07["poseId"]
    assert t13["transform"]["handedness"] == "right" and t13["transform"]["targetUnits"] == "m"
    for manifest in (t07, t13):
        glb = manifest["glb"]
        path = ROOT / glb["uri"]
        assert path.stat().st_size == glb["bytes"] and sha(path) == glb["sha256"]
    listed = {row["element_file_id"]: row for row in t02["relatedBoneInventory"]}
    source_record = next(row for row in catalog["entities"]["sources"] if row["id"] == t13["sourceId"])
    assert source_record["license"]["spdxId"] == "CC-BY-4.0"
    originals = sorted(transfer["assets"] + additional["assets"], key=lambda row: row["fileId"])
    for original, source, node, asset in zip(originals, t13["sourceAssets"], t13["meshNodes"], t13["meshAssets"]):
        assert source == original and original["fileId"] == node["sourceFileId"]
        if original["fileId"] in listed:
            assert original["sourceTableRows"] == listed[original["fileId"]]["table_rows"]
            assert original["representationId"] == listed[original["fileId"]]["representation_id"]
            assert original["externalConceptId"] == listed[original["fileId"]]["concept_id"]
        else:
            for name, line in original["sourceTableRows"].items():
                parts = (ROOT / "work/evidence/T13" / name).read_text().splitlines()[line - 1].split("\t")
                assert parts[0] == original["externalConceptId"]
                assert parts[-1] == (original["fileId"] if name == "isa_element_parts.txt" else original["sourceName"])
        path = ROOT / original["localPath"]
        assert path.stat().st_size == original["bytes"] and sha(path) == original["sha256"] == node["sourceSha256"]
        assert node["meshAssetId"] == asset["id"]
        assert asset["hash"] == t13["glb"]["sha256"] and asset["topologyHash"] == node["topologySha256"]
        assert asset["sourceId"] == t13["sourceId"] and asset["licenseId"] == source_record["license"]["id"]
        assert node["sourceBoundsMm"]["max"][0] < 0  # right side remains right after [x,z,-y]
    validate_context(context, catalog, t07, t13)
    bridge = load("atlas-data/manifests/canonical-geometry-t12.json")
    assert next(row for row in bridge["unmappedStructureAssets"] if row["fileId"] == "FJ3385")["structureId"] is None
    wrong = copy.deepcopy(context)
    wrong["records"][0]["descriptionClaimId"] = "nonexistent-claim"
    try:
        validate_context(wrong, catalog, t07, t13)
    except AssertionError:
        pass
    else:
        raise AssertionError("Broken claim reference was not rejected")
    wrong = copy.deepcopy(context)
    wrong["records"][0]["geometry"] = {"kind": "point"}
    try:
        validate_context(wrong, catalog, t07, t13)
    except AssertionError:
        pass
    else:
        raise AssertionError("Unreviewed surface geometry was not rejected")
    print(json.dumps({"passed": True, "meshAssets": 20, "newBoneAssets": 9,
                      "rightInstances": 6, "muscleMappings": 7, "attachments": 41,
                      "wholeBoneContexts": 28, "heldWithoutTargetMesh": 13,
                      "locatedSurfaceAnnotations": 0, "humanReviewedSurfaces": 0,
                      "negativeClaimReferenceRejected": True, "negativeUnreviewedGeometryRejected": True,
                      "talusStructureId": None}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
