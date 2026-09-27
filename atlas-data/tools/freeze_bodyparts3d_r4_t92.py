#!/usr/bin/env python3
"""Freeze T92's exact T73 trapezius concept/member set before acquisition."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work/evidence/T92/frozen-source-set.json"
MATRIX = ROOT / "work/evidence/T73/target-source-matrix.json"
META = ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"
ARCHIVE_URL = "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip"
EXPECTED_CONCEPTS = [
    ("FMA32529", "BP8254", "zone of trapezius", "group_or_zone"),
    ("FMA32555", "BP8226", "ascending part of trapezius", "part_concept"),
    ("FMA32556", "BP8253", "transverse part of trapezius", "part_concept"),
    ("FMA32557", "BP8268", "descending part of trapezius", "part_concept"),
    ("FMA33581", "BP5638", "ascending part of right trapezius", "side_specific_part_concept"),
    ("FMA33583", "BP8225", "ascending part of left trapezius", "side_specific_part_concept"),
    ("FMA33584", "BP5610", "transverse part of right trapezius", "side_specific_part_concept"),
    ("FMA33585", "BP8252", "transverse part of left trapezius", "side_specific_part_concept"),
    ("FMA33586", "BP5636", "descending part of right trapezius", "side_specific_part_concept"),
    ("FMA33587", "BP8267", "descending part of left trapezius", "side_specific_part_concept"),
]
EXPECTED_FJS = ["FJ1520", "FJ1520M", "FJ1554", "FJ1554M", "FJ1521", "FJ1521M"]
BATCHES = [{"batchId": "T92-B01-TRAPEZIUS-SOURCE", "count": 6, "sourceElementFileIds": EXPECTED_FJS}]
SOURCE_INPUTS = [
    "work/evidence/T73/target-source-matrix.json",
    "work/evidence/T73/region-coverage.json",
    "work/evidence/T50/scene-contract.md",
    "atlas-data/manifests/bodyparts3d-r4-t70/scope-inventory.json",
    "atlas-data/manifests/bodyparts3d-r4-t70/integration-manifest.json",
    "atlas-data/manifests/bodyparts3d-r4-t71/source-manifest.json",
    "atlas-data/manifests/bodyparts3d-r4-t71/integration-manifest.json",
    "atlas-data/manifests/bodyparts3d-r4-t72/source-manifest.json",
    "atlas-data/manifests/bodyparts3d-r4-t72/integration-extension.json",
    "atlas-data/manifests/bodyparts3d-r4-t53/source-manifest.json",
    "atlas-data/manifests/bodyparts3d-r4-t54/source-manifest.json",
    "atlas-data/manifests/bodyparts3d-r4-t53/back.json",
    "atlas-data/manifests/bodyparts3d-r4-t54/shoulder-scapular.json",
    "work/evidence/T70/validation.json",
    "work/evidence/T71/validation.json",
    "work/evidence/T72/validation.json",
    "work/evidence/T73/validation.json",
]
META_FILES = [
    "isa_parts_list_e.txt",
    "isa_inclusion_relation_list.txt",
    "isa_element_parts.txt",
    "partof_parts_list_e.txt",
    "partof_inclusion_relation_list.txt",
    "partof_element_parts.txt",
]


class FreezeError(RuntimeError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def read_tsv(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle, delimiter="\t"))[1:]


def side_from_exact_name(name: str) -> str | None:
    values = {value.casefold() for value in re.findall(r"\b(left|right)\b", name, flags=re.I)}
    if len(values) > 1:
        raise FreezeError(f"source laterality label conflicts: {name}")
    return next(iter(values), None)


def build_freeze() -> dict[str, Any]:
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    targets = [row for row in matrix.get("items", []) if row.get("task") == "T92"]
    if len(targets) != 10:
        raise FreezeError(f"T73 T92 source target count changed: expected 10, found {len(targets)}")
    by_fma = {row.get("sourceConceptId"): row for row in targets}
    expected_fmas = {row[0] for row in EXPECTED_CONCEPTS}
    if set(by_fma) != expected_fmas:
        raise FreezeError(f"T73 T92 exact FMA set differs: {sorted(by_fma)}")

    concepts = read_tsv(META / "isa_parts_list_e.txt")
    inclusion = read_tsv(META / "isa_inclusion_relation_list.txt")
    elements = read_tsv(META / "isa_element_parts.txt")
    concept_table = {row[0]: row for row in concepts if len(row) >= 3}
    element_rows_by_fma: dict[str, list[list[str]]] = {}
    element_rows_by_fj: dict[str, list[list[str]]] = {}
    for row in elements:
        if len(row) < 3:
            continue
        element_rows_by_fma.setdefault(row[0], []).append(row[:3])
        element_rows_by_fj.setdefault(row[2], []).append(row[:3])

    source_concepts = []
    concept_members: dict[str, list[dict[str, Any]]] = {}
    member_hash_rows: list[str] = []
    matrix_member_names: dict[str, set[str]] = {}
    for fma, bp, name, kind in EXPECTED_CONCEPTS:
        matrix_row = by_fma[fma]
        if matrix_row.get("targetSet") != "trapezius-region-visual-context":
            raise FreezeError(f"T73 target-set changed for {fma}")
        if matrix_row.get("sourceTree") != "isaCompoundElements":
            raise FreezeError(f"T73 expected IS-A source tree changed for {fma}")
        if matrix_row.get("sourceRepresentationId") != bp or matrix_row.get("sourcePreferredName") != name:
            raise FreezeError(f"T73 frozen source identity/name changed for {fma}")
        if concept_table.get(fma) != [fma, bp, name]:
            raise FreezeError(f"official R4 IS-A concept/representation row mismatch for {fma}")
        actual = sorted(element_rows_by_fma.get(fma, []))
        matrix_fjs = sorted(member.get("sourceElementFileId") for member in matrix_row.get("exactMembers", []))
        if not actual or sorted(row[2] for row in actual) != matrix_fjs:
            raise FreezeError(f"T73 exact members and official R4 ELEMENT rows differ for {fma}")
        if matrix_row.get("declaredProductRegions") != ["back", "shoulder-scapular"]:
            raise FreezeError(f"T73 back/shoulder source context changed for {fma}")
        source_concepts.append({
            "sourceConceptId": fma,
            "sourceRepresentationId": bp,
            "sourceNameEnglish": name,
            "sourceTree": "IS-A",
            "sourceSemanticLabel": kind,
            "officialConceptRow": [fma, bp, name],
            "officialElementRows": actual,
            "sourceParentRelations": [row[:4] for row in inclusion if len(row) >= 4 and (row[0] == fma or row[2] == fma)],
            "declaredSourceContextCandidates": ["back", "shoulder-scapular"],
            "meshInterpretation": "COMPOUND source concepts share atomic ELEMENT meshes; concept count does not create mesh nodes or canonical memberships",
        })
        member_hash_rows.append(f"{fma}|{bp}|{name}|{','.join(row[2] for row in actual)}\n")
        for relation in actual:
            concept_members.setdefault(relation[2], []).append({"sourceConceptId": fma, "sourceRepresentationId": bp, "sourceNameEnglish": name, "sourceSemanticLabel": kind})
        for member in matrix_row.get("exactMembers", []):
            matrix_member_names.setdefault(member["sourceElementFileId"], set()).add(member.get("sourceElementName", ""))

    if set(concept_members) != set(EXPECTED_FJS):
        raise FreezeError(f"exact source union changed: {sorted(concept_members)}")
    if [len(batch["sourceElementFileIds"]) for batch in BATCHES] != [6] or set(sum((batch["sourceElementFileIds"] for batch in BATCHES), [])) != set(EXPECTED_FJS):
        raise FreezeError("T92 must be one exact six-member internal batch")

    assets = []
    for file_id in EXPECTED_FJS:
        relations = sorted(element_rows_by_fj.get(file_id, []))
        frozen_relations = sorted([row for row in relations if row[0] in expected_fmas])
        expected_names = matrix_member_names.get(file_id, set())
        if len(frozen_relations) == 0 or not expected_names:
            raise FreezeError(f"T73/official source relation is missing for {file_id}")
        if expected_names != {row[1] for row in frozen_relations}:
            raise FreezeError(f"T73 exact member label differs from official relation rows for {file_id}")
        side_values = {side_from_exact_name(concept["sourceNameEnglish"]) for concept in concept_members[file_id]}
        side_values.discard(None)
        if len(side_values) > 1:
            raise FreezeError(f"official exact source labels disagree on side for {file_id}: {sorted(side_values)}")
        assets.append({
            "sourceElementFileId": file_id,
            "stableMeshAssetId": f"HA-MESH-BP3D4-{file_id}",
            "archiveTree": "IS-A",
            "archiveMemberPathExpectation": f"isa_BP3D_4.0_obj_99/{file_id}.obj",
            "officialTargetElementRows": frozen_relations,
            "allOfficialIsAElementRowsForFj": sorted(relations),
            "sourceConceptMemberships": sorted(concept_members[file_id], key=lambda row: row["sourceConceptId"]),
            "exactSideFromSourceConceptNames": next(iter(side_values), None),
            "matrixSourceNameObservations": sorted(expected_names),
            "sourceContextCandidates": ["back", "shoulder-scapular"],
            "sourceOnlyAtFreeze": True,
            "learnerDefaultVisibleAtFreeze": False,
            "humanAnatomyReviewedAtFreeze": False,
            "publicRedistributionHeldAtFreeze": True,
            "acquisitionStateAtFreeze": "not_attempted",
        })

    input_paths = [ROOT / value for value in SOURCE_INPUTS]
    missing = [path.relative_to(ROOT).as_posix() for path in input_paths if not path.is_file()]
    if missing:
        raise FreezeError(f"T92 required historical/source inputs are missing: {missing}")
    metadata_hashes = {name: sha_file(META / name) for name in META_FILES}
    input_hashes = {path.relative_to(ROOT).as_posix(): sha_file(path) for path in input_paths}
    input_hashes.update({(META / name).relative_to(ROOT).as_posix(): metadata_hashes[name] for name in META_FILES})
    membership_text = "".join(member_hash_rows)
    return {
        "revision": "BodyParts3D-R4-T92-FROZEN-TRAPEZIUS-SOURCE-SET-v1",
        "task": "T92",
        "status": "frozen_before_mesh_acquisition",
        "sourceId": "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0",
        "sourceVersion": "BodyParts3D Release 4.0; official endpoints use /LATEST/; 3D release date 2013-06-19",
        "officialReadme": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/README_e.html",
        "officialDownloadPage": "https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html",
        "archiveTree": "IS-A",
        "selectedArchiveUrl": ARCHIVE_URL,
        "sourceConceptCount": len(source_concepts),
        "conceptToElementRelationCount": sum(len(row["officialElementRows"]) for row in source_concepts),
        "uniqueSourceElementFileIds": EXPECTED_FJS,
        "uniqueSourceElementFileCount": len(assets),
        "oneNodePerUniqueFj": True,
        "internalBatches": BATCHES,
        "sourceConcepts": source_concepts,
        "uniqueSourceAssets": assets,
        "sourceConceptMembershipSha256": sha(membership_text.encode("utf-8")),
        "sourceAssetMembershipSha256": sha("".join(f"{row['sourceElementFileId']}|IS-A|back,shoulder-scapular\n" for row in assets).encode("utf-8")),
        "sourceMetadata": {
            "retrievedOn": "2026-09-27; pinned T51 cache, rechecked at T92 start",
            "fileHashes": metadata_hashes,
            "editionLocator": "Official BodyParts3D R4 download page: IS-A concepts, inclusion relation and compound-to-ELEMENT table; rows keyed by FMA/BP/FJ in the six pinned TSVs.",
        },
        "inputSha256": input_hashes,
        "historicalContract": {
            "parentIntegrationManifest": {"path": "atlas-data/manifests/bodyparts3d-r4-t70/integration-manifest.json", "sha256": input_hashes["atlas-data/manifests/bodyparts3d-r4-t70/integration-manifest.json"]},
            "T71SiblingPackagePreserved": input_hashes["atlas-data/manifests/bodyparts3d-r4-t71/source-manifest.json"],
            "T72SiblingPackagePreserved": input_hashes["atlas-data/manifests/bodyparts3d-r4-t72/source-manifest.json"],
            "T50SceneContractSha256": input_hashes["work/evidence/T50/scene-contract.md"],
        },
        "policy": {
            "sameStableSourceNodeAcrossConceptAndRegionContext": True,
            "candidateRegionContextsAreNotCanonicalMemberships": True,
            "sideMustComeFromExactOfficialConceptNameAndRelation": True,
            "neverInferSideFromFjSuffixOrCoordinates": True,
            "noMirroringOrRecentering": True,
            "canonicalLearnerBindingsCreated": False,
            "learnerPolicyChanged": False,
            "humanAnatomyReviewed": False,
            "publicRedistributionHeldPendingFileLevelLicenseReconciliation": True,
            "wholeBodyCanonicalDenominator": None,
        },
    }


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--freeze", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        expected = json_bytes(build_freeze())
        if args.freeze:
            if OUT.exists():
                raise FreezeError("T92 frozen source set already exists; it is immutable after creation")
            OUT.parent.mkdir(parents=True, exist_ok=True)
            OUT.write_bytes(expected)
        else:
            if not OUT.is_file() or OUT.read_bytes() != expected:
                raise FreezeError("T92 frozen source set differs from deterministic T73/official metadata reconstruction")
        print(json.dumps({"result": "pass", "task": "T92", "conceptCount": 10, "relationCount": 14, "memberCount": 6, "batchCounts": [6], "freezeSha256": sha_file(OUT)}, indent=2))
        return 0
    except Exception as exc:
        print(f"T92 freeze failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
