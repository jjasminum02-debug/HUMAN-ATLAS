#!/usr/bin/env python3
"""Freeze T74's exact T73 skull source members before acquisition."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work/evidence/T74/frozen-source-set.json"
T73_MATRIX = ROOT / "work/evidence/T73/target-source-matrix.json"
METADATA = ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"
EXPECTED = [
    ("FMA52789", "FJ3274", "left parietal bone", "left"),
    ("FMA52738", "FJ3386", "right temporal bone", "right"),
    ("FMA52739", "FJ3281", "left temporal bone", "left"),
    ("FMA52892", "FJ3392", "right zygomatic bone", "right"),
    ("FMA52893", "FJ3287", "left zygomatic bone", "left"),
    ("FMA53649", "FJ3375", "right maxilla", "right"),
    ("FMA53650", "FJ3269", "left maxilla", "left"),
    ("FMA53647", "FJ3378", "right nasal bone", "right"),
    ("FMA53648", "FJ3272", "left nasal bone", "left"),
]
BATCHES = {
    "T74-B01": ["FJ3274", "FJ3386", "FJ3281", "FJ3392", "FJ3287"],
    "T74-B02": ["FJ3375", "FJ3269", "FJ3378", "FJ3272"],
}
META_FILES = [
    "isa_element_parts.txt", "partof_element_parts.txt",
    "isa_inclusion_relation_list.txt", "partof_inclusion_relation_list.txt",
    "isa_parts_list_e.txt", "partof_parts_list_e.txt",
]
SOURCE_ROOT = "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/"
ARCHIVE_URL = SOURCE_ROOT + "partof_BP3D_4.0_obj_99.zip"


class FreezeError(RuntimeError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("ha_t74_ingest", path)
    if spec is None or spec.loader is None:
        raise FreezeError(f"cannot load existing R4 metadata parser: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def generate() -> dict[str, Any]:
    if OUT.exists():
        raise FreezeError("T74 freeze already exists; it must not be regenerated after acquisition")
    matrix = json.loads(T73_MATRIX.read_text(encoding="utf-8"))
    rows = [item for item in matrix["items"] if item.get("task") == "T74"]
    expected_by_fma = {fma: (fid, name, side) for fma, fid, name, side in EXPECTED}
    if len(rows) != 10:
        raise FreezeError(f"T73 must freeze 10 concepts including one reuse-only item; found {len(rows)}")
    matrix_by_fma = {item.get("sourceConceptId"): item for item in rows}
    if set(matrix_by_fma) != set(expected_by_fma) | {"FMA52788"}:
        raise FreezeError("T73 T74 concept set differs from the reviewed exact skull target")

    ingest = load_module(ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py")
    tables = ingest.load_tables(METADATA)
    part_rows = tables["partofCompoundElements"]
    part_concepts = tables["partofConcepts"]
    members: list[dict[str, Any]] = []
    canonical_lines: list[str] = []
    for fma, fid, name, side in EXPECTED:
        target = matrix_by_fma.get(fma)
        if not target or target.get("sourceTree") != "partofCompoundElements":
            raise FreezeError(f"T73 lacks exact PART-OF source target for {fma}/{fid}")
        if target.get("sourceRepresentationId") is None or target.get("sourcePreferredName") != name:
            raise FreezeError(f"T73 identity/name/representation missing or changed for {fid}")
        if target.get("sideFromExactSourceLabel") != side:
            raise FreezeError(f"T73 side evidence changed for {fid}; do not infer it from FJ spelling")
        exact = [row for row in part_rows if row == [fma, name, fid]]
        if len(exact) != 1:
            raise FreezeError(f"official cached PART-OF ELEMENT row is not unique for {fma}/{name}/{fid}")
        representation = [row for row in part_concepts if row == [fma, target["sourceRepresentationId"], name]]
        if len(representation) != 1:
            raise FreezeError(f"official cached PART-OF concept row differs for {fma}/{target['sourceRepresentationId']}")
        other_rows = sorted({(row[0], row[1]) for row in part_rows if row[2] == fid})
        members.append({
            "sourceConceptId": fma,
            "sourceRepresentationId": target["sourceRepresentationId"],
            "sourceElementFileId": fid,
            "sourceNameEnglish": name,
            "side": side,
            "selectedArchiveTree": "PART-OF",
            "officialElementRow": exact[0],
            "officialConceptRow": representation[0],
            "otherPartOfRowsForSameFJ": [{"fmaConceptId": row[0], "nameEnglish": row[1]} for row in other_rows if row != (fma, name)],
            "metadataIdentityBasis": "exact FMA/name/FJ row plus exact FMA/BP/name concept row; source left/right token, not FJ suffix",
            "acquisitionStateAtFreeze": "not_yet_attempted",
        })
        canonical_lines.append(f"{fma}|{target['sourceRepresentationId']}|{fid}|{name}|{side}|PART-OF\n")

    if [row["sourceElementFileId"] for row in members] != [entry[1] for entry in EXPECTED]:
        raise FreezeError("frozen source order changed")
    reuse = {
        "FJ3380": {"sourceConceptId": "FMA52788", "side": "right", "package": "T52", "sourceManifestPath": "atlas-data/manifests/bodyparts3d-r4-t52/head.json", "mustNotReacquire": True, "reuseEvidencePath": "work/evidence/T73/target-source-matrix.json"},
        "FJ3200": {"sourceConceptId": "FMA52734", "side": None, "package": "T72", "sourceManifestPath": "atlas-data/manifests/bodyparts3d-r4-t72/source-manifest.json", "mustNotReacquire": True, "reuseEvidencePath": "atlas-data/manifests/bodyparts3d-r4-t72/source-manifest.json"},
        "FJ3289": {"sourceConceptId": "FMA52748", "side": None, "package": "T72", "sourceManifestPath": "atlas-data/manifests/bodyparts3d-r4-t72/source-manifest.json", "mustNotReacquire": True, "reuseEvidencePath": "atlas-data/manifests/bodyparts3d-r4-t72/source-manifest.json"},
        "FJ3309": {"sourceConceptId": "FMA52735", "side": None, "package": "T72", "sourceManifestPath": "atlas-data/manifests/bodyparts3d-r4-t72/source-manifest.json", "mustNotReacquire": True, "reuseEvidencePath": "atlas-data/manifests/bodyparts3d-r4-t72/source-manifest.json"},
    }
    t72_source = json.loads((ROOT / "atlas-data/manifests/bodyparts3d-r4-t72/source-manifest.json").read_text(encoding="utf-8"))
    t72_assets = {row["sourceElementFileId"]: row for row in t72_source["sourceAssets"]}
    t52_head = json.loads((ROOT / "atlas-data/manifests/bodyparts3d-r4-t52/head.json").read_text(encoding="utf-8"))
    t52_assets = {row["sourceElementFileId"]: row for row in t52_head["meshAssets"]}
    for fid, target in reuse.items():
        source_assets = t52_assets if target["package"] == "T52" else t72_assets
        source = source_assets.get(fid)
        source_concept = source.get("sourceFmaConceptId", source.get("sourceConceptId")) if source else None
        if source is None or source_concept != target["sourceConceptId"]:
            raise FreezeError(f"historical source manifest lacks exact reuse evidence for {fid}")
        target["sourceSha256"] = source.get("sourceSha256")
        target["renderNodeId"] = source.get("stableMeshAssetId", source.get("selectionId"))
    input_paths = [T73_MATRIX, *(METADATA / file for file in META_FILES), *[ROOT / item["sourceManifestPath"] for item in reuse.values()]]
    input_hashes = {p.relative_to(ROOT).as_posix(): sha_file(p) for p in input_paths}
    frozen = {
        "revision": "BodyParts3D-R4-T74-FROZEN-EXACT-SOURCE-SET-v1",
        "task": "T74",
        "status": "frozen_before_mesh_acquisition",
        "frozenSourceVersion": "BodyParts3D Release 4.0",
        "archiveUrl": ARCHIVE_URL,
        "archiveTree": "PART-OF",
        "sourceElementFileIds": [row["sourceElementFileId"] for row in members],
        "sourceElementFileCount": len(members),
        "sourceConceptCount": 10,
        "internalBatchSizeMaximum": 10,
        "internalBatches": [{"batchId": key, "sourceElementFileIds": value} for key, value in BATCHES.items()],
        "uniqueNewSourceAssets": members,
        "reuseOnly": reuse,
        "frozenMembershipSha256": sha("".join(canonical_lines).encode("utf-8")),
        "inputHashes": input_hashes,
        "policy": {
            "noMirroring": True,
            "lateralityFromExplicitSourceRelationOnly": True,
            "noCanonicalBindingOrLearnerPolicyChange": True,
            "rightsHold": "held_pending_file_level_reconciliation_with_legacy_OBJ_headers",
            "humanAnatomyReview": "not_performed",
            "scope": "T73's ten-concept bilateral skull silhouette target only; nine exact new FJ members plus FJ3380 reuse",
            "reuseOnlyIds": ["FJ3380", "FJ3200", "FJ3289", "FJ3309"],
        },
    }
    write_json(OUT, frozen)
    return frozen


if __name__ == "__main__":
    try:
        print(json.dumps(generate(), ensure_ascii=False, indent=2))
    except Exception as exc:
        print(f"T74 freeze failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
