#!/usr/bin/env python3
"""Validate T22 source/derived motion asset survey without importing model assets."""
from __future__ import annotations

import hashlib
import json
import struct
import sys
from urllib.parse import urlparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "atlas-data/motion/motion-asset-sources.json"
SCHEMA = ROOT / "atlas-data/schemas/motion-asset-sources.schema.json"
MOTION = ROOT / "atlas-data/motion/motion-learning.json"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    motion = json.loads(MOTION.read_text(encoding="utf-8"))
    registry = json.loads((ROOT / "atlas-data/sources/registry.json").read_text(encoding="utf-8"))
    source_ids = {source["id"] for source in registry.get("sources", [])}
    required_top = set(schema["required"])
    require(set(manifest) == required_top, "manifest keys do not match schema required set")
    require(manifest.get("schemaVersion") == schema["properties"]["schemaVersion"]["const"], "schema version mismatch")
    require(manifest.get("coordinateContract", {}).get("linearUnits") == "m", "glTF linear unit must be meters")
    require(manifest.get("coordinateContract", {}).get("handedness") == "right", "glTF frame must be right-handed")
    require(manifest.get("coordinateContract", {}).get("upAxis") == "+Y", "glTF up axis must be +Y")
    require(manifest.get("coordinateContract", {}).get("angularUnits") == "rad", "glTF angular unit must be radians")
    require(manifest.get("firstAnkleDemonstration", {}).get("notPatientExerciseInstruction") is True, "first demo scope flag missing")
    require(manifest.get("firstAnkleDemonstration", {}).get("status") == "method_selected_asset_held", "T22 must not claim an authored asset")
    demo = manifest.get("firstAnkleDemonstration", {})
    require(set(demo) == set(schema["properties"]["firstAnkleDemonstration"]["required"]), "first demo fields differ from schema")
    require(demo.get("subjectMuscleId") == "HA-M-000003" and demo.get("side") == "right" and
            demo.get("candidateAction") == "오른쪽 발목 배측굴곡의 교육용 시범", "first demo target is not right tibialis anterior dorsiflexion")
    require(manifest.get("assetPipeline", {}).get("outputFormat") == "self-contained GLB only; external buffer/image URI rejected",
            "first motion input must be self-contained GLB")

    entries = manifest.get("candidateSources", [])
    ids = [row.get("id") for row in entries]
    require(len(ids) == len(set(ids)), "duplicate source candidate ID")
    for row in entries:
        candidate_schema = schema["$defs"]["CandidateSource"]
        require(set(row) == set(candidate_schema["required"]), f"candidate keys do not match schema: {row.get('id')}")
        require(row["sourceId"] in source_ids, f"source registry ID not found: {row['sourceId']}")
        require(row["format"] in {"glb", "osim"}, f"unsupported candidate format: {row['format']}")
        for key in ("sourceLocator", "licenseUrl"):
            parsed = urlparse(row[key])
            require(parsed.scheme == "https" and bool(parsed.netloc), f"invalid {key} URL for {row['id']}")
        require(isinstance(row["observed"], dict) and bool(row["observed"]), f"missing source observations: {row['id']}")
        local_path = (ROOT / row["localPath"]).resolve()
        require(local_path.is_relative_to(ROOT), f"candidate path escapes repository: {row['localPath']}")
        require(local_path.is_file(), f"candidate source file missing: {row['localPath']}")
        require(digest(local_path) == row["sha256"], f"candidate source hash changed: {row['localPath']}")
        require(row.get("motionEligible") is False, f"unreviewed source promoted to eligible: {row['id']}")
        if row["format"] == "glb":
            data = local_path.read_bytes()
            require(len(data) >= 20, f"truncated GLB: {row['localPath']}")
            magic, version, length = struct.unpack_from("<4sII", data, 0)
            require(magic == b"glTF" and version == 2 and length == len(data), f"invalid GLB container: {row['localPath']}")
            json_length = struct.unpack_from("<I", data, 12)[0]
            document = json.loads(data[20:20 + json_length])
            observed = {
                "scenes": len(document.get("scenes", [])), "nodes": len(document.get("nodes", [])),
                "meshes": len(document.get("meshes", [])), "skins": len(document.get("skins", [])),
                "animations": len(document.get("animations", [])),
                "morphTargets": sum(len(primitive.get("targets", [])) for mesh in document.get("meshes", []) for primitive in mesh.get("primitives", [])),
            }
            require(observed == row["observed"], f"GLB structure audit changed: {row['localPath']}")
        elif row["format"] == "osim":
            text = local_path.read_text(encoding="utf-8", errors="replace")
            require("Creative Commons" in text and "CCBY 3.0" in text, "model-specific CC BY 3.0 credit not found in exact .osim file")
    motion_ids = sorted(asset["id"] for asset in motion.get("motionAssets", []))
    require(sorted(manifest.get("productionMotionAssetIds", [])) == motion_ids, "production asset IDs differ from motion-learning.json")
    print(f"PASS: {len(entries)} source candidates verified; production motion assets={len(motion_ids)}; source bytes unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
