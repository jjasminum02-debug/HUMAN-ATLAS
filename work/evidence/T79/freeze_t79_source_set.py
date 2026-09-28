#!/usr/bin/env python3
"""Build/check T79's exact official BodyParts3D R4 IS-A source allowlist."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "work/evidence/T79"
METADATA = ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"
ARCHIVE_URL = "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip"
IDS = ["FJ1512", "FJ1512M", "FJ1478", "FJ1478M", "FJ1479", "FJ1479M", "FJ1480", "FJ1480M", "FJ1477", "FJ1477M"]
EXACT_NAMES = {
    "FJ1512": "short head of right biceps brachii",
    "FJ1512M": "short head of left biceps brachii",
    "FJ1478": "long head of right biceps brachii",
    "FJ1478M": "long head of left biceps brachii",
    "FJ1479": "long head of right triceps brachii",
    "FJ1479M": "long head of left triceps brachii",
    "FJ1480": "medial head of right triceps brachii",
    "FJ1480M": "medial head of left triceps brachii",
    "FJ1477": "lateral head of right triceps brachii",
    "FJ1477M": "lateral head of left triceps brachii",
}
FILES = {
    "isaConcepts": "isa_parts_list_e.txt",
    "isaRelations": "isa_inclusion_relation_list.txt",
    "isaElements": "isa_element_parts.txt",
}
EXPECTED_HEADERS = {
    "isaConcepts": ["concept id", "representation id", "en"],
    "isaRelations": ["parent id", "parent name", "child id", "child name"],
    "isaElements": ["concept id", "name", "element file id"],
}
OUT = EVIDENCE / "frozen-source-set.json"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_rows(key: str) -> list[list[str]]:
    path = METADATA / FILES[key]
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.reader(stream, delimiter="\t"))
    if not rows or rows[0] != EXPECTED_HEADERS[key]:
        raise ValueError(f"unexpected official metadata header: {path}")
    return [row for row in rows[1:] if row and any(cell.strip() for cell in row)]


def build() -> dict:
    concepts = read_rows("isaConcepts")
    relations = read_rows("isaRelations")
    elements = read_rows("isaElements")
    concept_map: dict[str, list[str]] = {}
    for row in concepts:
        concept_map[row[0]] = row
    source_map: dict[str, list[list[str]]] = {fid: [] for fid in IDS}
    for row in elements:
        if row[2] in source_map:
            source_map[row[2]].append(row)
    targets = []
    canonical_membership = []
    for fid in IDS:
        expected_name = EXACT_NAMES[fid]
        exact = [row for row in source_map[fid] if row[1] == expected_name]
        if len(exact) != 1:
            raise ValueError(f"exact source relation is missing or ambiguous for {fid}: {exact}")
        fma = exact[0][0]
        concept = concept_map.get(fma)
        if concept is None or concept[2] != expected_name:
            raise ValueError(f"exact source concept row is missing for {fid}/{fma}")
        side = "right" if "right " in expected_name else "left"
        side_relations = [row for row in relations if row[2] == fma]
        if len(side_relations) != 1:
            raise ValueError(f"exact IS-A parent relationship is missing or ambiguous for {fid}/{fma}")
        all_rows = sorted({tuple(row) for row in source_map[fid]})
        targets.append({
            "sourceElementFileId": fid,
            "sourceConceptId": fma,
            "sourceRepresentationId": concept[1],
            "sourceNameEnglish": expected_name,
            "sourceSide": side,
            "sourceSideEvidence": "exact official IS-A side-specific concept/element names and exact inclusion relation; not inferred from FJ suffix or coordinates",
            "sourceTree": "IS-A",
            "officialElementRow": exact[0],
            "officialConceptRow": concept,
            "officialParentRelationRow": side_relations[0],
            "sharedAndHigherContextRows": [list(row) for row in all_rows if row[0] != fma],
            "allOfficialElementRowsForSameFj": [list(row) for row in all_rows],
            "acquisitionStateAtFreeze": "not_attempted",
        })
        canonical_membership.append(f"{fma}|{concept[1]}|{fid}|{expected_name}|{side}|IS-A\n")

    baseline = json.loads((EVIDENCE / "start-baseline.json").read_text(encoding="utf-8"))
    input_hashes = {"atlas-data/source-cache/bodyparts3d-r4/metadata/" + name: sha((METADATA / name).read_bytes()) for name in FILES.values()}
    for path, digest in input_hashes.items():
        if baseline["inputSha256"].get(path) != digest:
            raise ValueError(f"source metadata drift since T79 start: {path}")
    ids_by_element = [row["sourceElementFileId"] for row in targets]
    if ids_by_element != IDS or len(set(ids_by_element)) != 10:
        raise ValueError("T79 must freeze the exact ten unique source IDs in requested order")
    membership_hash = sha("".join(canonical_membership).encode("utf-8"))
    result = {
        "revision": "BodyParts3D-R4-T79-FROZEN-BILATERAL-BICEPS-TRICEPS-v1",
        "task": "T79",
        "status": "frozen_before_mesh_acquisition",
        "sourceVersion": "BodyParts3D Release 4.0",
        "archiveTree": "IS-A",
        "archiveUrl": ARCHIVE_URL,
        "sourceNamespace": "BodyParts3D ELEMENT FJ file ID",
        "sourceConceptCount": 10,
        "sourceElementFileCount": 10,
        "sourceElementFileIds": IDS,
        "internalBatchMaximum": 10,
        "internalBatches": [{"batchId": "T79-B01-BILATERAL-BICEPS-TRICEPS", "count": 10, "sourceElementFileIds": IDS}],
        "uniqueNewSourceAssets": targets,
        "membershipSha256": membership_hash,
        "sidePolicy": "use exact side-specific official FMA concept and IS-A name; never infer left/right from M suffix or coordinates",
        "sourceOnlyPolicy": "no canonical learner binding, no three-name card, no anatomy claim, no human review promotion",
        "rightsPolicy": "retain per-file legacy OBJ header verbatim; public redistribution remains held independently from local technical display",
        "humanAnatomyReview": "not_performed",
        "wholeMusclePartPolicy": "inspect exact source parent surface availability and real surfaces; if a parent representation overlaps parts, avoid duplicate display with an explicit reversible product representation policy without modifying source bytes",
        "inputSha256": input_hashes,
        "targetInputSource": "work/evidence/T96/target-scope-t96.json and work/evidence/T78/execution-queue.json; this freeze retains the exact user-authorized FJ subset and exact official metadata join",
        "fullArchiveDownloadAllowed": False,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    current = build()
    if args.write:
        if OUT.exists():
            old = json.loads(OUT.read_text(encoding="utf-8"))
            if old != current:
                raise SystemExit("refusing to overwrite changed T79 freeze")
        else:
            OUT.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        if not OUT.is_file() or json.loads(OUT.read_text(encoding="utf-8")) != current:
            raise SystemExit("T79 freeze differs from reproducible official metadata projection")
    print(json.dumps({"status": "pass", "sourceCount": len(current["uniqueNewSourceAssets"]), "membershipSha256": current["membershipSha256"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
