#!/usr/bin/env python3
"""Verify the T100 trapezius display correction without modifying source geometry."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
OVERLAY = ROOT / "atlas-data/overlays/za-local-integration.json"
MANIFEST = ROOT / "atlas-data/source-cache/datasets/za/compiled/manifest.json"
ASSIGNMENT = HERE / "surface-assignment.json"
OUTPUT = HERE / "verification.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    overlay_bytes = OVERLAY.read_bytes()
    manifest_bytes = MANIFEST.read_bytes()
    overlay = json.loads(overlay_bytes)
    manifest = json.loads(manifest_bytes)
    evidence = json.loads(ASSIGNMENT.read_text())
    assert sha256(OVERLAY) == evidence["overlayAfterSha256"]
    assert sha256(MANIFEST) == evidence["compiledManifestSha256"]
    assert overlay["sourceHash"] == evidence["sourceHash"] == manifest["sourceHash"]
    assert overlay["datasetRevision"] == evidence["datasetRevision"] == manifest["revision"]
    assert evidence["rawObjectsUnchanged"] is True
    assert evidence["compiledManifestAndChunksUnchanged"] is True
    assert evidence["geometryOrTransformChanged"] is False
    assert evidence["publicRedistribution"] == overlay["policy"]["publicRedistribution"] == "held"
    assert evidence["humanReview"] == "not_performed"

    current = {row["sourceKey"]: row for row in overlay["objects"]}
    instances = {row["sourceKey"]: row for row in manifest["instances"]}
    expected = {
        "ZA-c7010a9-e07069f3efea3d66c4e25ac2": ("left", "superior", "승모근 상부", "등세모근 위부분", "Descending part of trapezius muscle", "HA-P-000009", "TA2:2227", "neck"),
        "ZA-c7010a9-951e9d95076ad0635ead80e3": ("right", "superior", "승모근 상부", "등세모근 위부분", "Descending part of trapezius muscle", "HA-P-000009", "TA2:2227", "neck"),
        "ZA-c7010a9-949cdee8e7b16d22f295af1e": ("left", "inferior", "승모근 하부", "등세모근 아래부분", "Ascending part of trapezius muscle", "HA-P-000011", "TA2:2229", None),
        "ZA-c7010a9-935a4aed2c3c6c262ba36166": ("right", "inferior", "승모근 하부", "등세모근 아래부분", "Ascending part of trapezius muscle", "HA-P-000011", "TA2:2229", None),
    }
    correction_rows = [row for row in overlay["objects"] if row.get("surfaceAssignmentCorrection", {}).get("correctionId") == evidence["correctionId"]]
    assert len(correction_rows) == len(expected) == 4
    checks = []
    for key, values in expected.items():
        side, part, label, modern, english, concept, target, region = values
        row = current[key]
        source = instances[key]
        correction = row["surfaceAssignmentCorrection"]
        assert correction["sourceNameObservation"] == row["sourceName"]
        assert correction["sourceLabelConflict"] is True
        assert correction["displayedPart"] == part
        assert row["side"] == side
        assert row["label"] == row["names"]["koTraditional"] == label
        assert row["names"]["koModern"] == modern and row["names"]["en"] == english
        assert row["haConceptId"] == concept and row["targetId"] == target and target in row["targetIds"]
        assert correction["evaluatedGeometrySha256"] == source["evaluatedGeometrySha256"]
        assert correction["detailResourceSha256"] == source["lods"]["detail"]["resource"]
        assert correction["worldYBoundsMetres"] == [row["bounds"][0][1], row["bounds"][1][1]]
        assert row["humanReview"] == "not_performed" and row["publicRedistribution"] == "held"
        assert row["sourceKey"] == source["sourceKey"] and row["sourceName"] == source["sourceName"]
        assert (region in row["regionIds"]) if region else ("neck" not in row["regionIds"])
        checks.append({
            "sourceKey": key,
            "side": side,
            "displayedPart": part,
            "cardLabel": label,
            "sourceNameObservation": row["sourceName"],
            "evaluatedGeometrySha256": source["evaluatedGeometrySha256"],
            "detailResourceSha256": source["lods"]["detail"]["resource"],
            "worldYBoundsMetres": correction["worldYBoundsMetres"],
            "sourceGeometryAndTransformModified": False,
        })

    chunks = []
    for item in evidence["compiledDetailChunks"]:
        path = ROOT / item["path"]
        assert sha256(path) == item["actualSha256"] == item["manifestSha256"]
        chunks.append({"path": item["path"], "sha256": sha256(path), "bytes": path.stat().st_size})

    result = {
        "schemaVersion": 1,
        "taskId": "T100",
        "unit": "correct-trapezius-upper-lower-source-label-geometry-conflict",
        "result": "passed_for_local_display_assignment",
        "notAClaimOf": ["human_anatomy_review", "public_redistribution_approval", "source_label_correction", "new_geometry"],
        "checks": {
            "four_exact_source_instances": len(checks) == 4,
            "both_sides_have_superior_and_inferior": True,
            "card_label_and_displayed_surface_assignment": True,
            "raw_source_name_conflict_preserved": True,
            "source_and_detail_chunk_hashes": True,
            "source_hash_and_dataset_revision_preserved": True,
            "geometry_transform_and_coordinates_unchanged": True,
            "public_redistribution_held": True,
            "human_review_not_performed": True,
        },
        "overlay": {"path": str(OVERLAY.relative_to(ROOT)), "sha256": sha256(OVERLAY), "revision": overlay["revision"]},
        "compiledManifest": {"path": str(MANIFEST.relative_to(ROOT)), "sha256": sha256(MANIFEST), "sourceHash": manifest["sourceHash"], "revision": manifest["revision"], "instanceCount": len(manifest["instances"])},
        "sourceRows": checks,
        "compiledDetailChunks": chunks,
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"result": result["result"], "rows": len(checks), "chunks": len(chunks), "overlaySha256": result["overlay"]["sha256"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
