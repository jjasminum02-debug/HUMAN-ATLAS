#!/usr/bin/env python3
"""T13c-B01 provenance/schema/preservation checks; no mesh coordinates are inferred."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "atlas-data/schemas"))
import validate as atlas_validate  # noqa: E402

EVIDENCE = ROOT / "work/evidence/T13c-B01"
TARGET = "HA-A-T05-GASTRO-LAT-FEMUR-ORIGIN"
CLAIM_ID = "HA-C-T05-GASTRO-LAT-FEMUR-ORIGIN"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def stable_hash(value) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def main() -> int:
    layer = load(EVIDENCE / "spatial-draft-layer.json")
    schema = load(ROOT / "atlas-data/schemas/spatial-draft-layer.schema.json")
    catalog = load(ROOT / "atlas-data/catalog/canonical-catalog.json")["entities"]
    t13 = load(ROOT / "atlas-data/manifests/attachment-context-t13.json")
    t12 = load(ROOT / "atlas-data/manifests/canonical-geometry-t12.json")
    t13_asset = load(ROOT / "atlas-data/manifests/derived-bones-t13.json")
    record = layer["records"][0]
    context = next(row for row in t13["records"] if row["attachmentId"] == TARGET)
    attachment = next(row for row in catalog["attachments"] if row["id"] == TARGET)
    claim = next(row for row in catalog["claims"] if row["id"] == CLAIM_ID)
    instance = next(row for row in catalog["instances"] if row["id"] == context["instanceId"])
    asset = next(row for row in t13_asset["meshAssets"] if row["id"] == context["contextMeshAssetId"])
    problems = []

    problems.extend(atlas_validate.check_schema(schema))
    problems.extend(atlas_validate.schema_issues(schema, layer))
    expected = {
        "attachmentId": TARGET,
        "descriptionClaimId": CLAIM_ID,
        "sourceClaimHash": stable_hash(claim),
        "instanceId": context["instanceId"],
        "side": "right",
        "assetId": asset["id"],
        "assetRevision": asset["revision"],
        "assetRevisionHash": asset["hash"],
        "topologyHash": asset["topologyHash"],
        "frameId": asset["axes"]["frameId"],
        "units": asset["units"],
        "poseId": asset["pose"]["id"],
        "evidenceIds": context["claimEvidenceIds"],
    }
    for key, value in expected.items():
        if record.get(key) != value:
            problems.append({"code": "reference_mismatch", "path": f"$.records[0].{key}", "message": f"Expected {value!r}; got {record.get(key)!r}."})
    if record.get("status") != "context_only" or record.get("geometry") is not None:
        problems.append({"code": "geometry_not_held", "path": "$.records[0]", "message": "B01 must remain context_only with geometry null."})
    if layer.get("syntheticFixture") is not False or len(layer.get("records", [])) != 1:
        problems.append({"code": "scope_violation", "path": "$.records", "message": "Expected one production (non-synthetic) B01 record only."})
    if attachment.get("descriptionClaimId") != CLAIM_ID or claim.get("subjectId") != TARGET:
        problems.append({"code": "claim_link_invalid", "path": "$.records[0]", "message": "Canonical attachment/claim cross-link does not agree."})
    if instance.get("side") != "right" or context.get("side") != "right":
        problems.append({"code": "side_invalid", "path": "$.records[0].side", "message": "Source and canonical instance must both be right-sided."})
    if t12.get("frameId") not in (None, asset["axes"]["frameId"]):
        problems.append({"code": "t12_frame_disagreement", "path": "$.records[0].frameId", "message": "T12 and T13 frame do not agree."})

    result = {
        "passed": not problems,
        "target": TARGET,
        "recordCount": len(layer.get("records", [])),
        "geometry": record.get("geometry"),
        "status": record.get("status"),
        "claimHash": record.get("sourceClaimHash"),
        "instanceSide": instance.get("side"),
        "assetId": asset.get("id"),
        "assetRevisionHash": asset.get("hash"),
        "topologyHash": asset.get("topologyHash"),
        "schemaAndReferenceErrors": problems,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
