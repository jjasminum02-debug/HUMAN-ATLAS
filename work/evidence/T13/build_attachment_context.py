"""Link all T05 pilot attachments to provenance and optional whole-bone review context.

This deliberately creates no SpatialAnnotation or inferred surface coordinates.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "atlas-data/catalog/canonical-catalog.json"
T07 = ROOT / "atlas-data/manifests/derived-assets-t07.json"
T13 = ROOT / "atlas-data/manifests/derived-bones-t13.json"
OUT = ROOT / "atlas-data/manifests/attachment-context-t13.json"
SOURCE_ID = "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0"


def main() -> None:
    catalog = json.loads(CATALOG.read_text())
    t07 = json.loads(T07.read_text())
    t13 = json.loads(T13.read_text())
    entities = catalog["entities"]
    assert catalog["revision"] in ("T12b-canonical-geometry-links-v1", "T13-attachment-context-v1", "T13-attachment-context-v2")
    assert entities["spatialAnnotations"] == []
    existing_assets = {row["id"]: row for row in entities["meshAssets"]}
    if catalog["revision"] == "T12b-canonical-geometry-links-v1":
        for row in t13["meshAssets"]:
            assert row["id"] not in existing_assets
            entities["meshAssets"].append(row)
        for source in t13["sourceAssets"]:
            entities["evidence"].append({
                "id": f"EV-BP3D4-{source['fileId']}-T13-ASSET",
                "sourceId": SOURCE_ID,
                "locator": f"LSDB Archive Release 4.0 IS-A: isa_parts_list_e.txt line {source['sourceTableRows']['isa_parts_list_e.txt']}; isa_element_parts.txt line {source['sourceTableRows']['isa_element_parts.txt']}; OBJ {source['fileId']} SHA-256 {source['sha256']}; provisional structure context, no attachment-surface review.",
                "supportedClaimIds": [], "evidenceKind": "dataset",
            })
        catalog["revision"] = "T13-attachment-context-v2"
        CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    elif catalog["revision"] == "T13-attachment-context-v1":
        old_ids = {row["id"] for row in entities["meshAssets"] if row["revision"] == "BP3D-R4-T13-BONES-GLB-V1"}
        assert len(old_ids) == 5 and old_ids <= {row["id"] for row in t13["meshAssets"]}
        entities["meshAssets"] = [row for row in entities["meshAssets"] if row["id"] not in old_ids] + t13["meshAssets"]
        prior_evidence = {row["id"] for row in entities["evidence"]}
        for source in t13["sourceAssets"]:
            evidence_id = f"EV-BP3D4-{source['fileId']}-T13-ASSET"
            if evidence_id not in prior_evidence:
                entities["evidence"].append({
                    "id": evidence_id, "sourceId": SOURCE_ID,
                    "locator": f"LSDB Archive Release 4.0 IS-A: isa_parts_list_e.txt line {source['sourceTableRows']['isa_parts_list_e.txt']}; isa_element_parts.txt line {source['sourceTableRows']['isa_element_parts.txt']}; OBJ {source['fileId']} SHA-256 {source['sha256']}; provisional structure context, no attachment-surface review.",
                    "supportedClaimIds": [], "evidenceKind": "dataset",
                })
        catalog["revision"] = "T13-attachment-context-v2"
        CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    else:
        assert all(existing_assets[row["id"]] == row for row in t13["meshAssets"])

    structures = {row["id"]: row for row in entities["structures"]}
    claims = {row["id"]: row for row in entities["claims"]}
    evidence = {row["id"]: row for row in entities["evidence"]}
    concepts = {row["id"]: row for row in entities["muscleConcepts"]}
    instances = {row["conceptId"]: row for row in entities["instances"]}
    bone_by_id = {
        "HA-S-FEMUR": "HA-MESH-BP3D4-FJ3365",
        "HA-S-TIBIA": "HA-MESH-BP3D4-FJ3387",
        "HA-S-FIBULA": "HA-MESH-BP3D4-FJ3366",
        "HA-S-CALCANEUS": "HA-MESH-BP3D4-FJ3360",
        "HA-S-NAVICULAR": "HA-MESH-BP3D4-FJ3308",
        "HA-S-METATARSAL-1": "HA-MESH-BP3D4-FJ3351",
        "HA-S-METATARSAL-5": "HA-MESH-BP3D4-FJ3359",
        "HA-S-MEDIAL-CUNEIFORM": "HA-MESH-BP3D4-FJ3377",
        "HA-S-CUBOID": "HA-MESH-BP3D4-FJ3364",
        "HA-S-BASE-METATARSAL-2": "HA-MESH-BP3D4-FJ3353",
        "HA-S-BASE-METATARSAL-3": "HA-MESH-BP3D4-FJ3355",
        "HA-S-BASE-METATARSAL-4": "HA-MESH-BP3D4-FJ3357",
    }
    assert set(bone_by_id.values()) <= {row["id"] for row in entities["meshAssets"]}
    rows = []
    for attachment in entities["attachments"]:
        if not attachment["id"].startswith("HA-A-T05-"):
            continue
        claim = claims[attachment["descriptionClaimId"]]
        assert claim["subjectId"] == attachment["id"] and claim["reviewState"] == "needs_review"
        assert claim["evidenceIds"] and all(evidence[eid]["sourceId"] != SOURCE_ID for eid in claim["evidenceIds"])
        target_id = attachment["targetStructureId"]
        target = structures[target_id]
        bone_id = target_id if target_id in bone_by_id else target.get("parentId")
        mesh_id = bone_by_id.get(bone_id)
        owner = attachment["muscleOrPartId"]
        parent_concept = concepts[owner].get("parentId") if concepts[owner]["entityType"] == "muscle_part" else owner
        assert parent_concept in instances and instances[parent_concept]["side"] == "right"
        status = "whole_bone_search_context_only" if mesh_id else "held_no_matching_target_mesh"
        rows.append({
            "attachmentId": attachment["id"], "descriptionClaimId": claim["id"],
            "claimEvidenceIds": claim["evidenceIds"], "ownerConceptId": owner,
            "instanceId": instances[parent_concept]["id"], "side": "right", "role": attachment["role"],
            "targetStructureId": target_id,
            "targetBoneId": bone_id if mesh_id and bone_id not in {"HA-S-BASE-METATARSAL-2", "HA-S-BASE-METATARSAL-3", "HA-S-BASE-METATARSAL-4"} else None,
            "sourceBoneFileId": mesh_id.rsplit("-", 1)[-1] if mesh_id else None,
            "contextMeshAssetId": mesh_id, "contextStatus": status,
            "spatialAnnotationId": None, "geometry": None,
            "precision": None, "surfaceReviewState": "not_started",
            "reason": "T05 prose and a whole-bone mesh do not locate attachment triangles or extent; manual multi-view review required." if mesh_id else "No source-confirmed mesh for this exact target in the T13 acquired subset; surface mapping held.",
        })
    assert len(rows) == 41
    assert {row["ownerConceptId"] for row in rows} == {
        "HA-P-000001", "HA-P-000002", "HA-M-000001", "HA-M-000002",
        "HA-M-000003", "HA-M-000004", "HA-M-000005", "HA-M-000006",
    }
    context_count = sum(row["contextMeshAssetId"] is not None for row in rows)
    payload = {
        "schemaVersion": "T13-attachment-context-v2", "sourceCatalogRevision": catalog["revision"],
        "t05SourceBoundary": "Gray 1918 historical claim/evidence, all needs_review; no independent modern or human anatomy approval.",
        "assetSourceId": SOURCE_ID, "frameId": t13["transform"]["frameId"],
        "units": "m", "poseId": t13["transform"]["poseId"],
        "assetSets": [
            {"manifest": "atlas-data/manifests/derived-assets-t07.json", "glbSha256": t07["glb"]["sha256"], "meshCount": 11},
            {"manifest": "atlas-data/manifests/derived-bones-t13.json", "glbSha256": t13["glb"]["sha256"], "meshCount": 9},
        ],
        "coverage": {"t05Attachments": 41, "wholeBoneContexts": context_count,
                     "heldWithoutTargetMesh": len(rows) - context_count,
                     "locatedSurfaceAnnotations": 0, "humanReviewedSurfaces": 0},
        "records": rows,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(payload["coverage"], ensure_ascii=False))


if __name__ == "__main__":
    main()
