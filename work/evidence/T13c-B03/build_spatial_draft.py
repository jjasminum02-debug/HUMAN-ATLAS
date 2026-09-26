#!/usr/bin/env python3
"""Build the one-record, geometry-held B03 layer from current canonical references."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "spatial-draft-layer.json"
TARGET = "HA-A-T05-TA-TIBIA-SURFACE-ORIGIN"
CLAIM_ID = "HA-C-T05-TA-TIBIA-SURFACE-ORIGIN"
ASSET_ID = "HA-MESH-BP3D4-FJ3387"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def stable_hash(value) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> None:
    catalog = load(ROOT / "atlas-data/catalog/canonical-catalog.json")["entities"]
    context = load(ROOT / "atlas-data/manifests/attachment-context-t13.json")
    t07 = load(ROOT / "atlas-data/manifests/derived-assets-t07.json")
    claims = [row for row in catalog["claims"] if row.get("id") == CLAIM_ID]
    attachments = [row for row in catalog["attachments"] if row.get("id") == TARGET]
    contexts = [row for row in context["records"] if row.get("attachmentId") == TARGET]
    assets = [row for row in t07["meshAssets"] if row.get("id") == ASSET_ID]
    if any(len(rows) != 1 for rows in (claims, attachments, contexts, assets)):
        raise ValueError("B03 requires exactly one canonical claim, attachment, context row, and mesh asset.")
    claim, attachment, source, asset = claims[0], attachments[0], contexts[0], assets[0]
    if attachment.get("descriptionClaimId") != CLAIM_ID or claim.get("subjectId") != TARGET:
        raise ValueError("B03 claim/attachment links disagree.")
    if source.get("side") != "right" or source.get("instanceId") != "HA-I-R-HA-M-000003":
        raise ValueError("B03 context does not identify the assigned right tibialis anterior instance.")
    if source.get("contextMeshAssetId") != ASSET_ID or source.get("contextStatus") != "whole_bone_search_context_only":
        raise ValueError("B03 must retain the T13 whole-bone context as context only.")
    record = {
        "id": "T13C-B03-HA-A-T05-TA-TIBIA-SURFACE-ORIGIN",
        "status": "context_only",
        "attachmentId": TARGET,
        "descriptionClaimId": CLAIM_ID,
        "sourceClaimHash": stable_hash(claim),
        "instanceId": source["instanceId"],
        "side": source["side"],
        "assetId": asset["id"],
        "assetRevision": asset["revision"],
        "assetRevisionHash": asset["hash"],
        "topologyHash": asset["topologyHash"],
        "geometry": None,
        "frameId": asset["axes"]["frameId"],
        "units": asset["units"],
        "poseId": asset["pose"]["id"],
        "precision": None,
        "method": None,
        "evidenceIds": source["claimEvidenceIds"],
        "reviewId": None,
        "staleReason": None,
        "migrationSource": f"atlas-data/manifests/attachment-context-t13.json#records/{TARGET}",
    }
    layer = {
        "schemaVersion": "HA-spatial-draft-layer-v1",
        "syntheticFixture": False,
        "sourceContextVersion": "T13-attachment-context-v2",
        "records": [record],
    }
    OUT.write_text(json.dumps(layer, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"path": OUT.relative_to(ROOT).as_posix(), "recordId": record["id"], "claimHash": record["sourceClaimHash"], "assetRevisionHash": record["assetRevisionHash"], "topologyHash": record["topologyHash"], "status": record["status"], "geometry": record["geometry"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
