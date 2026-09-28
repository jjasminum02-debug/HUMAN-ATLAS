#!/usr/bin/env python3
"""Validate T95's product-only region overlay against actual T77 and T78 evidence."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t77/manifest.json"
OVERLAY = ROOT / "atlas-data/manifests/bodyparts3d-r4-t95/product-context-overlay.json"
DIAGNOSTIC = ROOT / "work/evidence/T78/region-diagnostic.json"
EXPECTED_IDS = {"FJ3237", "FJ3279", "FJ3362", "FJ3384"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"T95 overlay validation failed: {message}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    raw_manifest = MANIFEST.read_bytes()
    source = json.loads(raw_manifest)
    overlay = json.loads(OVERLAY.read_text())
    diagnostic = json.loads(DIAGNOSTIC.read_text())
    overlay_hash = sha256(OVERLAY.read_bytes())
    manifest_hash = sha256(raw_manifest)

    if manifest_hash != overlay["sourceManifestSha256"]:
        fail("the frozen T77 manifest hash changed")
    if source["publicRedistribution"] != "held" or source["localOnly"] is not True:
        fail("the source-level rights gate changed")
    if source["frame"] != overlay["sourceFrame"] or source["unit"] != overlay["sourceUnit"]:
        fail("frame or unit differs from overlay contract")
    rows = [asset for chunk in source["chunks"] for asset in chunk["assets"]]
    by_id = {asset["id"]: asset for asset in rows}
    entries = {entry["sourceId"]: entry for entry in overlay["entries"]}
    if len(entries) != len(overlay["entries"]) or set(entries) != EXPECTED_IDS:
        fail("overlay must cover exactly four unique source IDs")

    diagnostic_assets = diagnostic["assets"]
    effective = copy.deepcopy(source)
    effective_by_id = {asset["id"]: asset for chunk in effective["chunks"] for asset in chunk["assets"]}
    checked: list[dict[str, object]] = []
    for source_id in sorted(EXPECTED_IDS):
        actual = by_id.get(source_id)
        entry = entries[source_id]
        prior = diagnostic_assets.get(source_id)
        if actual is None or prior is None:
            fail(f"source or T78 diagnostic row missing: {source_id}")
        expected = {
            "nodeId": entry["nodeId"], "sourceSha256": entry["sourceSha256"],
            "regions": entry["sourceRegions"], "side": entry["side"], "layer": "bone",
            "defaultVisible": True, "supplement": False, "pickState": "source_only_unbound",
            "stableIds": [], "holdReasons": [], "humanReviewed": False,
        }
        for field, value in expected.items():
            if actual.get(field) != value:
                fail(f"source {source_id} {field} differs from frozen T78 row")
            diagnostic_field = "sourceSha256" if field == "sourceSha256" else field
            if prior.get(diagnostic_field) != value:
                fail(f"T78 diagnostic {source_id} {diagnostic_field} differs from T77 source")
        if actual.get("publicRedistribution") != "held" or actual.get("localDisplay", {}).get("publicRedistribution") != "held":
            fail(f"source rights hold changed for {source_id}")
        if actual.get("localDisplay", {}).get("humanReviewed") is not False:
            fail(f"human-review hold changed for {source_id}")
        if entry.get("productRegions") != sorted(set(entry.get("productRegions", []))):
            fail(f"product regions are duplicated or not canonical for {source_id}")
        effective_asset = effective_by_id[source_id]
        effective_asset["regions"] = list(dict.fromkeys([*actual["regions"], *entry["productRegions"]]))
        changed = [region for region in entry["productRegions"] if region not in actual["regions"]]
        checked.append({
            "id": source_id, "side": actual["side"], "sourceRegions": actual["regions"],
            "productRegions": entry["productRegions"], "newProductRegions": changed,
            "sourceSha256": actual["sourceSha256"],
            "sourceOnlyUnbound": actual["pickState"] == "source_only_unbound" and actual["stableIds"] == [],
            "humanReviewed": actual["humanReviewed"], "publicRedistribution": actual["publicRedistribution"],
        })

    added = {row["id"] for row in checked if row["newProductRegions"]}
    if added != {"FJ3279"}:
        fail(f"expected only left scapula to gain a product region, got {sorted(added)}")
    if "upper-limb" not in effective_by_id["FJ3279"]["regions"] or "upper-limb" not in effective_by_id["FJ3384"]["regions"]:
        fail("bilateral scapula context is incomplete")
    if effective_by_id["FJ3237"]["regions"] != by_id["FJ3237"]["regions"] or effective_by_id["FJ3362"]["regions"] != by_id["FJ3362"]["regions"]:
        fail("comparison-only clavicle membership changed")
    if len(rows) != len({asset["nodeId"] for asset in rows}):
        fail("overlapping regions must not duplicate source nodes")

    result = {
        "task": "T95", "status": "passed", "manifestSha256": manifest_hash,
        "overlaySha256": overlay_hash, "sourceAssetCount": len(rows),
        "sourceBytesMutated": False, "sourceRegionsMutated": False,
        "effectiveManifestChanges": {"regionMembershipOnly": True, "addedRegionBySourceId": {"FJ3279": ["upper-limb"]}},
        "checked": checked,
        "invariants": {
            "exactlyFourFrozenSourceRows": True, "sideMatchesT78": True,
            "sourceOnlyAndNoStableId": True, "humanReviewNotPromoted": True,
            "publicRedistributionHeld": True, "claviclesComparisonOnly": True,
            "uniqueNodePerSourceAsset": True,
        },
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
