#!/usr/bin/env python3
"""Freeze T75's six side-specific deltoid source meshes from the T73 audit."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work/evidence/T75/frozen-source-set.json"
MATRIX = ROOT / "work/evidence/T73/target-source-matrix.json"
META = ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"
BASE = ROOT / "atlas-data/manifests/bodyparts3d-r4-t70/integration-manifest.json"
T53 = ROOT / "atlas-data/manifests/bodyparts3d-r4-t53/source-manifest.json"
T54 = ROOT / "atlas-data/manifests/bodyparts3d-r4-t54/source-manifest.json"
T74 = ROOT / "atlas-data/manifests/bodyparts3d-r4-t74/source-manifest.json"
T74_EXT = ROOT / "atlas-data/manifests/bodyparts3d-r4-t74/integration-extension.json"
EXPECTED = [
    ("FMA34680", "BP7573", "FJ1468", "clavicular part of right deltoid", "right", "clavicular"),
    ("FMA34681", "BP8259", "FJ1468M", "clavicular part of left deltoid", "left", "clavicular"),
    ("FMA34682", "BP7571", "FJ1467", "acromial part of right deltoid", "right", "acromial"),
    ("FMA34683", "BP9075", "FJ1467M", "acromial part of left deltoid", "left", "acromial"),
    ("FMA34684", "BP5607", "FJ1513", "spinal part of right deltoid", "right", "spinal"),
    ("FMA34685", "BP8151", "FJ1513M", "spinal part of left deltoid", "left", "spinal"),
]
GENERIC_BY_PART = {"clavicular": "FMA34677", "acromial": "FMA34678", "spinal": "FMA34679"}
BATCH = {"batchId": "T75-B01-DELTOID-SURFACES", "sourceElementFileIds": [row[2] for row in EXPECTED]}
META_FILES = [
    "isa_element_parts.txt", "isa_inclusion_relation_list.txt", "isa_parts_list_e.txt",
    "partof_element_parts.txt", "partof_inclusion_relation_list.txt", "partof_parts_list_e.txt",
]
ARCHIVE_URL = "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip"


class FreezeError(RuntimeError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_ingest():
    path = ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py"
    spec = importlib.util.spec_from_file_location("ha_t75_freeze_ingest", path)
    if spec is None or spec.loader is None:
        raise FreezeError(f"cannot load existing R4 parser: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def generate() -> dict[str, Any]:
    if OUT.exists():
        raise FreezeError("T75 exact-source freeze already exists; refusing to revise after work starts")
    matrix = load_json(MATRIX)
    t73 = [row for row in matrix.get("items", []) if row.get("task") == "T75"]
    expected_fmas = {row[0] for row in EXPECTED}
    by_fma = {row.get("sourceConceptId"): row for row in t73 if row.get("targetSet") == "deltoid-side-specific-parts"}
    if set(by_fma) != expected_fmas or len(by_fma) != 6:
        raise FreezeError("T73 must freeze exactly six side-specific deltoid concepts")
    if any(row.get("sourceTree") != "isaCompoundElements" for row in by_fma.values()):
        raise FreezeError("T73 exact deltoid targets must point to the R4 IS-A relation tree")

    ingest = load_ingest()
    tables = ingest.load_tables(META)
    concept_rows = tables["isaConcepts"]
    element_rows = tables["isaCompoundElements"]
    targets: list[dict[str, Any]] = []
    canonical: list[str] = []
    for fma, bp, fid, name, side, part in EXPECTED:
        target = by_fma[fma]
        members = target.get("exactMembers", [])
        if len(members) != 1 or (members[0].get("sourceElementFileId"), members[0].get("sourceElementName")) != (fid, name):
            raise FreezeError(f"T73 exact FMA/FJ/name assignment differs for {fma}/{fid}")
        if target.get("sourceRepresentationId") != bp or target.get("sourcePreferredName") != name or target.get("sideFromExactSourceLabel") != side:
            raise FreezeError(f"T73 representation/name/source-side differs for {fma}/{fid}; suffixes are not used")
        exact_concepts = [row for row in concept_rows if row == [fma, bp, name]]
        exact_relations = [row for row in element_rows if row == [fma, name, fid]]
        if len(exact_concepts) != 1 or len(exact_relations) != 1:
            raise FreezeError(f"official cached R4 IS-A concept/relation rows are not unique for {fma}/{fid}")
        generic_id = GENERIC_BY_PART[part]
        generic_rows = sorted({tuple(row) for row in element_rows if row[0] in {"FMA34676", generic_id} and row[2] == fid})
        required_generic = {("FMA34676", "zone of deltoid", fid), (generic_id, f"{part} part of deltoid", fid)}
        if set(generic_rows) != required_generic:
            raise FreezeError(f"shared deltoid zone/generic-part context rows differ for {fid}: {generic_rows}")
        all_fj_rows = sorted({tuple(row) for row in element_rows if row[2] == fid})
        targets.append({
            "sourceConceptId": fma,
            "sourceRepresentationId": bp,
            "sourceElementFileId": fid,
            "sourceNameEnglish": name,
            "side": side,
            "part": part,
            "sourceTree": "IS-A",
            "officialElementRow": exact_relations[0],
            "officialConceptRow": exact_concepts[0],
            "genericAndZoneContextRows": [list(row) for row in generic_rows],
            "allOfficialIsaRowsForSameFj": [list(row) for row in all_fj_rows],
            "declaredProductRegions": target["declaredProductRegions"],
            "singleStableNodeAcrossRegions": True,
            "acquisitionStateAtFreeze": "not_attempted",
        })
        canonical.append(f"{fma}|{bp}|{fid}|{name}|{side}|{part}|IS-A\n")

    if [row["sourceElementFileId"] for row in targets] != [row[2] for row in EXPECTED]:
        raise FreezeError("T75 source ordering changed")
    all_historical = set()
    for path in [BASE, T53, T54, T74]:
        doc = load_json(path)
        for key in ("assets", "sourceAssets", "meshAssets", "meshRecords"):
            for row in doc.get(key, []):
                fid = row.get("sourceElementFileId") if isinstance(row, dict) else None
                if fid:
                    all_historical.add(fid)
    collisions = all_historical & {row[2] for row in EXPECTED}
    if collisions:
        raise FreezeError(f"T75 target FJ already exists in historical source manifests: {sorted(collisions)}")

    input_paths = [MATRIX, *(META / name for name in META_FILES), BASE, T53, T54, T74, T74_EXT]
    frozen = {
        "revision": "BodyParts3D-R4-T75-FROZEN-DELTOID-EXACT-SOURCE-SET-v1",
        "task": "T75",
        "status": "frozen_before_mesh_acquisition",
        "sourceVersion": "BodyParts3D Release 4.0",
        "archiveTree": "IS-A",
        "archiveUrl": ARCHIVE_URL,
        "sourceConceptCount": 6,
        "uniqueSourceElementFileCount": 6,
        "sourceElementFileIds": [row[2] for row in EXPECTED],
        "internalBatchMaximum": 10,
        "internalBatches": [{**BATCH, "count": len(BATCH["sourceElementFileIds"])}],
        "uniqueNewSourceAssets": targets,
        "sameSourceZoneAndGenericPartRowsAreContextOnly": True,
        "contextOnlyConceptIds": ["FMA34676", "FMA34677", "FMA34678", "FMA34679"],
        "membershipSha256": sha("".join(canonical).encode("utf-8")),
        "latissimusDorsi": {
            "status": "unavailable_in_bodyparts3d_r4_metadata",
            "frozenByT73": True,
            "noSubstituteOrGeometryAllowed": True,
            "alternateSourceResearchTask": "T93",
        },
        "inputSha256": {path.relative_to(ROOT).as_posix(): sha_file(path) for path in input_paths},
        "policy": {
            "lateralityFromExactFmaAndObjNameOnly": True,
            "doNotInferFromFjSuffixOrCoordinates": True,
            "doNotTreatLateralDeltoidAsWholeDeltoid": True,
            "noMirrorOrRecenter": True,
            "oneStableRenderNodePerUniqueFjAcrossRegionMemberships": True,
            "noCanonicalLearnerBindingOrMotion": True,
            "defaultVisibility": "hidden",
            "rights": "held_pending_reconciliation_of_per_file_legacy_OBJ_header_and_current_database_terms",
            "humanAnatomyReview": "not_performed",
        },
    }
    write_json(OUT, frozen)
    return frozen


if __name__ == "__main__":
    try:
        print(json.dumps(generate(), ensure_ascii=False, indent=2))
    except Exception as exc:
        print(f"T75 source freeze failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(2)
