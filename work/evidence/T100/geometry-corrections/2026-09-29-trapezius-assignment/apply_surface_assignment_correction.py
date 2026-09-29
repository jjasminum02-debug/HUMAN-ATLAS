#!/usr/bin/env python3
"""Reassign only the four trapezius learner semantics to their observed surfaces."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
OVERLAY_PATH = ROOT / "atlas-data/overlays/za-local-integration.json"
DATASET_PATH = ROOT / "atlas-data/source-cache/datasets/za/compiled/manifest.json"
EVIDENCE_PATH = Path(__file__).resolve().parent / "surface-assignment.json"
OLD_REVISION = "T100-source-taxonomy-local-display-v1-B02-vertebral-variant-coverage"
NEW_REVISION = "T100-source-taxonomy-local-display-v1-B02-trapezius-surface-correction"
CORRECTION_ID = "T100-TRAPEZIUS-SURFACE-ASSIGNMENT-2026-09-29-v1"
REVIEW_STATE = "ai_crosschecked_geometry_location_with_upstream_source_label_conflict"
EVIDENCE_RELATIVE = "work/evidence/T100/geometry-corrections/2026-09-29-trapezius-assignment/surface-assignment.json"
SEMANTIC_FIELDS = (
    "label", "names", "aliases", "nameSourceIds", "haConceptId", "targetId", "targetIds",
)
EXPECTED = {
    "Ascending": {
        "evaluatedGeometrySha256": "576353abfdb0fd286ce49a9ca454da5ff5f4d6d1ef03a33955ebcc901593846b",
        "displayedPart": "superior",
        "label": "승모근 상부",
        "koModern": "등세모근 위부분",
        "english": "Descending part of trapezius muscle",
        "concept": "HA-P-000009",
        "target": "TA2:2227",
    },
    "Descending": {
        "evaluatedGeometrySha256": "bba204c6fac7acb06200db7ad8eef4e88ec8694c32c0ab60b2147bbbeed3df43",
        "displayedPart": "inferior",
        "label": "승모근 하부",
        "koModern": "등세모근 아래부분",
        "english": "Ascending part of trapezius muscle",
        "concept": "HA-P-000011",
        "target": "TA2:2229",
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    raw_overlay = OVERLAY_PATH.read_bytes()
    overlay = json.loads(raw_overlay)
    dataset_bytes = DATASET_PATH.read_bytes()
    dataset = json.loads(dataset_bytes)
    if overlay["revision"] == NEW_REVISION:
        current = json.loads(EVIDENCE_PATH.read_text())
        if current["overlayAfterSha256"] != sha256(raw_overlay):
            raise SystemExit("corrected overlay changed after the recorded correction")
        print("Correction already applied and hash-matched.")
        return
    if overlay["revision"] != OLD_REVISION:
        raise SystemExit(f"unexpected overlay revision: {overlay['revision']}")
    if overlay["sourceHash"] != dataset["sourceHash"] or overlay["datasetRevision"] != dataset["revision"]:
        raise SystemExit("overlay/source dataset identity mismatch")

    records = overlay["objects"]
    dataset_instances = {row["sourceKey"]: row for row in dataset["instances"]}
    found = {}
    for row in records:
        if row["sourceName"].startswith(("Ascending part of trapezius muscle.", "Descending part of trapezius muscle.")):
            name_part = "Ascending" if row["sourceName"].startswith("Ascending") else "Descending"
            key = (name_part, row["side"])
            if key in found:
                raise SystemExit(f"duplicate trapezius side row: {key}")
            found[key] = row
    if set(found) != {(part, side) for part in EXPECTED for side in ("left", "right")}:
        raise SystemExit("expected exact four left/right trapezius source instances")

    before_rows = []
    chunk_ids = set()
    for key, row in sorted(found.items()):
        instance = dataset_instances.get(row["sourceKey"])
        if not instance or instance["sourceName"] != row["sourceName"]:
            raise SystemExit(f"source identity mismatch: {row['sourceKey']}")
        if instance.get("geometrySpace") != "source_local" or instance.get("transformAppliedToGeometry") is not False:
            raise SystemExit(f"unexpected geometry transform: {row['sourceKey']}")
        if instance.get("evaluatedGeometrySha256") != EXPECTED[key[0]]["evaluatedGeometrySha256"]:
            raise SystemExit(f"unexpected evaluated geometry identity: {row['sourceKey']}")
        if row.get("surfaceAssignmentCorrection"):
            raise SystemExit(f"correction already present in baseline row: {row['sourceKey']}")
        before_rows.append(copy.deepcopy(row))
        chunk_ids.add(instance["lods"]["detail"]["chunk"])

    original_semantics = {
        key: {field: copy.deepcopy(found[key][field]) for field in SEMANTIC_FIELDS}
        for key in found
    }
    for side in ("left", "right"):
        ascending = found[("Ascending", side)]
        descending = found[("Descending", side)]
        ascending_semantics = original_semantics[("Ascending", side)]
        descending_semantics = original_semantics[("Descending", side)]
        for field in SEMANTIC_FIELDS:
            ascending[field] = copy.deepcopy(descending_semantics[field])
            descending[field] = copy.deepcopy(ascending_semantics[field])

    for (source_part, side), row in found.items():
        meaning = EXPECTED[source_part]
        instance = dataset_instances[row["sourceKey"]]
        if row["names"]["en"] != meaning["english"] or row["haConceptId"] != meaning["concept"] or row["targetId"] != meaning["target"]:
            raise SystemExit(f"semantic pair swap failed: {row['sourceKey']}")
        row["mappingStatus"] = "source_name_geometry_conflict_resolved_for_local_display"
        row["semanticReview"] = REVIEW_STATE
        row["surfaceAssignmentCorrection"] = {
            "correctionId": CORRECTION_ID,
            "sourceNameObservation": row["sourceName"],
            "sourceLabelConflict": True,
            "displayedPart": meaning["displayedPart"],
            "evaluatedGeometrySha256": instance["evaluatedGeometrySha256"],
            "detailResourceSha256": instance["lods"]["detail"]["resource"],
            "worldYBoundsMetres": [row["bounds"][0][1], row["bounds"][1][1]],
            "evidencePath": EVIDENCE_RELATIVE,
        }

    overlay["revision"] = NEW_REVISION
    after_bytes = (json.dumps(overlay, ensure_ascii=False, indent=2) + "\n").encode()

    chunk_records = []
    for chunk_id in sorted(chunk_ids):
        chunk = next(row for row in dataset["chunks"] if row["id"] == chunk_id)
        file_path = DATASET_PATH.parent / f"{chunk_id}.glb"
        file_sha = sha256(file_path.read_bytes())
        if file_sha != chunk["sha256"]:
            raise SystemExit(f"compiled GLB chunk hash mismatch: {chunk_id}")
        chunk_records.append({"path": str(file_path.relative_to(ROOT)), "id": chunk_id,
                              "manifestSha256": chunk["sha256"], "actualSha256": file_sha,
                              "bytes": file_path.stat().st_size})
    OVERLAY_PATH.write_bytes(after_bytes)
    after_rows = [copy.deepcopy(found[key]) for key in sorted(found)]
    report = {
        "schemaVersion": 1,
        "taskId": "T100",
        "unit": "correct-trapezius-upper-lower-source-label-geometry-conflict",
        "correctionId": CORRECTION_ID,
        "sourceOverlay": str(OVERLAY_PATH.relative_to(ROOT)),
        "overlayRevisionBefore": OLD_REVISION,
        "overlayRevisionAfter": NEW_REVISION,
        "overlayBeforeSha256": sha256(raw_overlay),
        "overlayAfterSha256": sha256(after_bytes),
        "compiledManifest": str(DATASET_PATH.relative_to(ROOT)),
        "compiledManifestSha256": sha256(dataset_bytes),
        "sourceHash": dataset["sourceHash"],
        "datasetRevision": dataset["revision"],
        "sourceFileSha256": dataset["sourceHash"],
        "rawObjectsUnchanged": True,
        "compiledManifestAndChunksUnchanged": True,
        "publicRedistribution": "held",
        "humanReview": "not_performed",
        "geometryOrTransformChanged": False,
        "beforeRows": before_rows,
        "afterRows": after_rows,
        "compiledDetailChunks": chunk_records,
    }
    EVIDENCE_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"Updated four trapezius presentation records: {report['overlayAfterSha256']}")


if __name__ == "__main__":
    main()
