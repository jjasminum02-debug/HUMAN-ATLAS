#!/usr/bin/env python3
"""Validate the T13c-B02 held spatial draft against canonical provenance."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "atlas-data/schemas"))
import validate as atlas_validate  # noqa: E402

EVIDENCE = ROOT / "work/evidence/T13c-B02"
TARGET = "HA-A-T05-TA-TIBIA-CONDYLE-ORIGIN"
CLAIM_ID = "HA-C-T05-TA-TIBIA-CONDYLE-ORIGIN"
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
    t07_assets = load(ROOT / "atlas-data/manifests/derived-assets-t07.json")
    problems: list[dict[str, str]] = []

    problems.extend(atlas_validate.check_schema(schema))
    problems.extend(atlas_validate.schema_issues(schema, layer))
    records = layer.get("records", [])
    if len(records) != 1:
        problems.append({"code": "scope_violation", "path": "$.records", "message": "B02 must contain exactly its one assigned record."})
    if layer.get("syntheticFixture") is not False:
        problems.append({"code": "scope_violation", "path": "$.syntheticFixture", "message": "Production evidence layer must not be marked synthetic."})

    record = records[0] if records else {}
    context_rows = [row for row in context_manifest["records"] if row.get("attachmentId") == TARGET]
    context = context_rows[0] if len(context_rows) == 1 else {}
    attachment_rows = [row for row in catalog["attachments"] if row.get("id") == TARGET]
    attachment = attachment_rows[0] if len(attachment_rows) == 1 else {}
    claim_rows = [row for row in catalog["claims"] if row.get("id") == CLAIM_ID]
    claim = claim_rows[0] if len(claim_rows) == 1 else {}
    instance_rows = [row for row in catalog["instances"] if row.get("id") == context.get("instanceId")]
    instance = instance_rows[0] if len(instance_rows) == 1 else {}
    t07_asset_rows = [row for row in t07_assets["meshAssets"] if row.get("id") == ASSET_ID]
    t07_asset = t07_asset_rows[0] if len(t07_asset_rows) == 1 else {}
    catalog_asset_rows = [row for row in catalog["meshAssets"] if row.get("id") == ASSET_ID]
    catalog_asset = catalog_asset_rows[0] if len(catalog_asset_rows) == 1 else {}

    if not context or not attachment or not claim or not instance or not t07_asset or not catalog_asset:
        problems.append({"code": "canonical_reference_missing", "path": "$.records[0]", "message": "One or more canonical attachment/claim/instance/asset references are missing or ambiguous."})

    expected = {
        "attachmentId": TARGET,
        "descriptionClaimId": CLAIM_ID,
        "sourceClaimHash": stable_hash(claim) if claim else None,
        "instanceId": context.get("instanceId"),
        "side": "right",
        "assetId": ASSET_ID,
        "assetRevision": t07_asset.get("revision"),
        "assetRevisionHash": t07_asset.get("hash"),
        "topologyHash": t07_asset.get("topologyHash"),
        "frameId": t07_asset.get("axes", {}).get("frameId"),
        "units": t07_asset.get("units"),
        "poseId": t07_asset.get("pose", {}).get("id"),
        "evidenceIds": context.get("claimEvidenceIds"),
    }
    for key, value in expected.items():
        if value is None or record.get(key) != value:
            problems.append({"code": "reference_mismatch", "path": f"$.records[0].{key}", "message": f"Expected {value!r}; got {record.get(key)!r}."})

    if record.get("status") != "context_only" or record.get("geometry") is not None or record.get("reviewId") is not None:
        problems.append({"code": "geometry_not_held", "path": "$.records[0]", "message": "B02 must remain context_only with null geometry and no review approval."})
    if context.get("side") != "right" or instance.get("side") != "right" or t07_asset.get("laterality") != "right":
        problems.append({"code": "side_invalid", "path": "$.records[0].side", "message": "Attachment context, instance, and asset must all be right-sided."})
    if attachment.get("descriptionClaimId") != CLAIM_ID or claim.get("subjectId") != TARGET:
        problems.append({"code": "claim_link_invalid", "path": "$.records[0]", "message": "Canonical attachment and claim cross-links do not agree."})
    if context.get("contextMeshAssetId") != ASSET_ID or context.get("contextStatus") != "whole_bone_search_context_only":
        problems.append({"code": "context_link_invalid", "path": "$.records[0].assetId", "message": "T13 context must refer to the whole-bone search asset only."})
    if t07_asset and catalog_asset:
        for key in ("hash", "topologyHash", "revision", "units", "laterality", "axes", "pose", "uri"):
            if t07_asset.get(key) != catalog_asset.get(key):
                problems.append({"code": "asset_manifest_disagreement", "path": f"$.records[0].assetId.{key}", "message": f"T07 manifest and canonical catalog differ for {key}."})
    if t12.get("frameId") != expected["frameId"] or t12.get("units") != expected["units"] or t12.get("poseId") != expected["poseId"]:
        problems.append({"code": "t12_coordinate_disagreement", "path": "$.records[0]", "message": "T12 and target asset frame, unit, and pose metadata must agree."})
    asset_path = ROOT / t07_asset.get("uri", "") if t07_asset else ROOT / "__missing__"
    if not asset_path.is_file() or file_hash(asset_path) != expected["assetRevisionHash"]:
        problems.append({"code": "asset_hash_mismatch", "path": "$.records[0].assetRevisionHash", "message": "Referenced GLB is missing or differs from the recorded SHA-256."})

    result = {
        "passed": not problems,
        "target": TARGET,
        "recordCount": len(records),
        "geometry": record.get("geometry"),
        "status": record.get("status"),
        "claimHash": record.get("sourceClaimHash"),
        "instanceSide": instance.get("side"),
        "assetId": t07_asset.get("id"),
        "assetRevisionHash": t07_asset.get("hash"),
        "assetFileSha256": file_hash(asset_path) if asset_path.is_file() else None,
        "topologyHash": t07_asset.get("topologyHash"),
        "schemaAndReferenceErrors": problems,
    }
    output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    (EVIDENCE / "validator-result.json").write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
