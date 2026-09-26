#!/usr/bin/env python3
"""Validate the single B03 held spatial draft against canonical provenance and T12/T13."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "work/evidence/T13c-B03"
sys.path.insert(0, str(ROOT / "atlas-data/schemas"))
import validate as atlas_validate  # noqa: E402

TARGET = "HA-A-T05-TA-TIBIA-SURFACE-ORIGIN"
CLAIM_ID = "HA-C-T05-TA-TIBIA-SURFACE-ORIGIN"
ASSET_ID = "HA-MESH-BP3D4-FJ3387"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def stable_hash(value) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    layer = load(EVIDENCE / "spatial-draft-layer.json")
    schema = load(ROOT / "atlas-data/schemas/spatial-draft-layer.schema.json")
    catalog = load(ROOT / "atlas-data/catalog/canonical-catalog.json")["entities"]
    context_manifest = load(ROOT / "atlas-data/manifests/attachment-context-t13.json")
    t12 = load(ROOT / "atlas-data/manifests/canonical-geometry-t12.json")
    t07 = load(ROOT / "atlas-data/manifests/derived-assets-t07.json")
    problems: list[dict[str, str]] = []
    problems.extend(atlas_validate.check_schema(schema))
    problems.extend(atlas_validate.schema_issues(schema, layer))
    records = layer.get("records", [])
    if len(records) != 1 or layer.get("syntheticFixture") is not False:
        problems.append({"code": "scope_violation", "path": "$.records", "message": "B03 must contain exactly one non-synthetic production evidence record."})
    record = records[0] if records else {}
    contexts = [row for row in context_manifest["records"] if row.get("attachmentId") == TARGET]
    attachments = [row for row in catalog["attachments"] if row.get("id") == TARGET]
    claims = [row for row in catalog["claims"] if row.get("id") == CLAIM_ID]
    instances = [row for row in catalog["instances"] if row.get("id") == "HA-I-R-HA-M-000003"]
    assets_t07 = [row for row in t07["meshAssets"] if row.get("id") == ASSET_ID]
    assets_catalog = [row for row in catalog["meshAssets"] if row.get("id") == ASSET_ID]
    if any(len(rows) != 1 for rows in (contexts, attachments, claims, instances, assets_t07, assets_catalog)):
        problems.append({"code": "canonical_reference_missing", "path": "$.records[0]", "message": "A canonical B03 reference is absent or ambiguous."})
    context = contexts[0] if len(contexts) == 1 else {}
    attachment = attachments[0] if len(attachments) == 1 else {}
    claim = claims[0] if len(claims) == 1 else {}
    instance = instances[0] if len(instances) == 1 else {}
    asset = assets_t07[0] if len(assets_t07) == 1 else {}
    catalog_asset = assets_catalog[0] if len(assets_catalog) == 1 else {}
    expected = {
        "id": "T13C-B03-HA-A-T05-TA-TIBIA-SURFACE-ORIGIN",
        "attachmentId": TARGET,
        "descriptionClaimId": CLAIM_ID,
        "sourceClaimHash": stable_hash(claim) if claim else None,
        "instanceId": "HA-I-R-HA-M-000003",
        "side": "right",
        "assetId": ASSET_ID,
        "assetRevision": asset.get("revision"),
        "assetRevisionHash": asset.get("hash"),
        "topologyHash": asset.get("topologyHash"),
        "frameId": asset.get("axes", {}).get("frameId"),
        "units": asset.get("units"),
        "poseId": asset.get("pose", {}).get("id"),
        "evidenceIds": context.get("claimEvidenceIds"),
    }
    for key, value in expected.items():
        if value is None or record.get(key) != value:
            problems.append({"code": "reference_mismatch", "path": f"$.records[0].{key}", "message": f"Expected {value!r}; got {record.get(key)!r}."})
    if record.get("status") != "context_only" or record.get("geometry") is not None or record.get("reviewId") is not None:
        problems.append({"code": "geometry_not_held", "path": "$.records[0]", "message": "B03 must remain context_only with null geometry and no review approval."})
    if context.get("side") != "right" or instance.get("side") != "right" or asset.get("laterality") != "right":
        problems.append({"code": "side_invalid", "path": "$.records[0].side", "message": "Context, canonical instance, and mesh asset must all be right-sided."})
    if attachment.get("descriptionClaimId") != CLAIM_ID or claim.get("subjectId") != TARGET:
        problems.append({"code": "claim_link_invalid", "path": "$.records[0]", "message": "Canonical attachment and description claim do not agree."})
    if context.get("instanceId") != record.get("instanceId") or context.get("contextMeshAssetId") != ASSET_ID or context.get("contextStatus") != "whole_bone_search_context_only":
        problems.append({"code": "context_link_invalid", "path": "$.records[0]", "message": "Draft does not match the T13 whole-bone context row."})
    if assets_t07 and assets_catalog:
        for key in ("hash", "topologyHash", "revision", "units", "laterality", "axes", "pose", "uri"):
            if asset.get(key) != catalog_asset.get(key):
                problems.append({"code": "asset_manifest_disagreement", "path": f"$.records[0].assetId.{key}", "message": f"T07 and canonical catalog disagree for {key}."})
    if t12.get("frameId") != expected["frameId"] or t12.get("units") != expected["units"] or t12.get("poseId") != expected["poseId"]:
        problems.append({"code": "t12_coordinate_disagreement", "path": "$.records[0]", "message": "T12 and target asset frame/unit/pose differ."})
    asset_path = ROOT / asset.get("uri", "") if asset else ROOT / "__missing__"
    actual_file_hash = file_hash(asset_path) if asset_path.is_file() else None
    if actual_file_hash != expected["assetRevisionHash"]:
        problems.append({"code": "asset_hash_mismatch", "path": "$.records[0].assetRevisionHash", "message": "The referenced GLB is missing or its bytes differ from the asset manifest."})
    result = {
        "passed": not problems,
        "target": TARGET,
        "recordCount": len(records),
        "status": record.get("status"),
        "geometry": record.get("geometry"),
        "reviewId": record.get("reviewId"),
        "claimHash": record.get("sourceClaimHash"),
        "instanceSide": instance.get("side"),
        "assetId": asset.get("id"),
        "assetRevisionHash": asset.get("hash"),
        "assetFileSha256": actual_file_hash,
        "topologyHash": asset.get("topologyHash"),
        "schemaAndReferenceErrors": problems,
    }
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    (EVIDENCE / "validator-result.json").write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
