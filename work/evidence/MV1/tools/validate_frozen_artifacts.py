#!/usr/bin/env python3
"""Integrity/checksum audit for frozen MV1 evidence without changing product inputs."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUN = ROOT / "work/evidence/MV1/2026-10-11-run-01"


def load(rel: str):
    return json.loads((RUN / rel).read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    inventory = load("inventory.json")
    disposition = load("target-dispositions.json")
    capture = load("runtime/capture-index-v3.json")
    phases = load("runtime/focused-phase-index.json")
    metrics = load("metrics/automatic-metrics-v3.json")
    loader = load("runtime/real-loader-validation.json")
    binding = load("runtime/live-binding-validation.json")
    failures: list[dict] = []

    muscle_rows = [r for r in inventory["candidateRows"] if r.get("inventoryScope") == "in_scope_muscle" and r.get("subjectKind") == "muscle"]
    if len(muscle_rows) != 332:
        failures.append({"check": "muscle_target_denominator", "actual": len(muscle_rows), "expected": 332})
    sides = Counter(r.get("sourceKeySide") for r in muscle_rows)
    if sides != Counter({"left": 166, "right": 166}):
        failures.append({"check": "muscle_side_counts", "actual": dict(sides)})
    role_counts = Counter(r.get("selectedMemberRole") for r in muscle_rows)
    mappings = [g for g in inventory["uniquePlaybackMappings"] if "muscle" in g.get("sourceScopes", [])]
    for row in muscle_rows:
        groups = [g for g in mappings if row["targetId"] in g.get("variantIds", [])]
        if len(groups) != 1:
            failures.append({"check": "target_mapping_cardinality", "targetId": row["targetId"], "actual": len(groups)})

    for row in inventory["glbFiles"]:
        if not row.get("pathExists") or not row.get("hashMatches") or row.get("glbStatus") != "pass":
            failures.append({"check": "glb_hash_or_parse", "uri": row.get("uri"), "actual": row})

    source_input_hash_passes = 0
    for rel, expected in inventory.get("inputHashes", {}).items():
        path = ROOT / rel
        actual = digest(path) if path.is_file() else None
        if actual != expected.get("sha256") or (path.is_file() and path.stat().st_size != expected.get("bytes")):
            failures.append({"check": "source_input_hash", "path": rel, "expected": expected.get("sha256"), "actual": actual})
        else:
            source_input_hash_passes += 1

    authoring = inventory["authoringInputs"]
    authoring_hash_passes = sum(bool(row.get("hashMatches")) for row in authoring["records"])
    if authoring_hash_passes != authoring["registryRecordCount"]:
        failures.append({"check": "authoring_input_hashes", "passed": authoring_hash_passes, "total": authoring["registryRecordCount"]})

    video_file = capture.get("videoFile", {})
    video_path = RUN / (video_file.get("path") or "")
    video_hash_ok = video_path.is_file() and digest(video_path) == video_file.get("sha256")
    if not video_hash_ok:
        failures.append({"check": "full_playback_video_hash", "path": video_file.get("path")})
    videos = capture.get("videos", [])
    phase_files = phases.get("files", [])
    dense_files = capture.get("playbackSheetsV3", [])
    if len(videos) != 74 or len(phase_files) != 74 or len(dense_files) != 220:
        failures.append({"check": "visual_artifact_cardinality", "videos": len(videos), "phaseSheets": len(phase_files), "denseSheets": len(dense_files)})
    if capture.get("failuresV3") or phases.get("report", {}).get("failures"):
        failures.append({"check": "visual_capture_errors", "captureFailures": capture.get("failuresV3"), "phaseFailures": phases.get("report", {}).get("failures")})
    for entry in [*phase_files, *dense_files]:
        rel = entry.get("path")
        path = RUN / rel if rel else None
        if not path or not path.is_file():
            failures.append({"check": "visual_sheet_path", "path": rel})

    samples = sum(len(m.get("sampleTimesSeconds", [])) for m in metrics.get("metrics", []))
    metric_summary = {
        "groups": len(metrics.get("metrics", [])),
        "samples": samples,
        "failures": len(metrics.get("failures", [])),
        "allRestNormalFlipFractionZero": all(m.get("peakRestNormalFlipFraction") == 0 for m in metrics.get("metrics", [])),
        "groupsWithRestDegenerateFaces": sum(m.get("restDegenerateTriangleFraction", 0) > 0 for m in metrics.get("metrics", [])),
        "maxAdditionalDegenerateTriangleFraction": max((m.get("maxAdditionalDegenerateTriangleFraction", 0) for m in metrics.get("metrics", [])), default=None),
        "maxReturnResidualMetres": max((v.get("returnResidualMaxMetres", 0) for v in videos), default=None),
        "maxDisplacementMetres": max((m.get("subjectLocalMaxDisplacementMetres", 0) for m in metrics.get("metrics", [])), default=None),
    }
    if metric_summary["groups"] != 74 or metric_summary["failures"] or not metric_summary["allRestNormalFlipFractionZero"] or metric_summary["maxAdditionalDegenerateTriangleFraction"] != 0:
        failures.append({"check": "automatic_geometry_metrics", "actual": metric_summary})

    if loader.get("targets") != 332 or loader.get("pass") != 332 or loader.get("error") != 0:
        failures.append({"check": "real_loader_validation", "actual": {k: loader.get(k) for k in ("targets", "pass", "error")}})
    if binding.get("targets") != 332 or binding.get("pass") != 332 or binding.get("fail") != 0 or binding.get("error") != 0:
        failures.append({"check": "live_binding_validation", "actual": {k: binding.get(k) for k in ("targets", "pass", "fail", "error")}})
    disposition_counts = disposition.get("statusCounts", {})
    if disposition_counts != {"pass": 330, "fail": 0, "not_checked": 2, "error": 0}:
        failures.append({"check": "target_dispositions", "actual": disposition_counts})
    row_statuses = [r.get("status") for r in disposition.get("visualRows", [])]
    disposition_ids = [r.get("targetId") for r in disposition.get("visualRows", [])]
    if len(row_statuses) != 332 or len(set(disposition_ids)) != 332 or any(s not in {"pass", "fail", "not_checked", "error"} for s in row_statuses):
        failures.append({"check": "target_status_enum_and_denominator", "rows": len(row_statuses), "uniqueIds": len(set(disposition_ids)), "invalid": [s for s in row_statuses if s not in {"pass", "fail", "not_checked", "error"}]})

    variant_pages = sorted((RUN / "visual/variant-contact-sheets").glob("page-*.jpg"))
    if len(variant_pages) != 10:
        failures.append({"check": "variant_contact_sheet_pages", "actual": len(variant_pages), "expected": 10})
    for row in disposition.get("visualRows", []):
        rel = row.get("visualEvidence", {}).get("variantSheet")
        if not rel or not (RUN / rel).is_file():
            failures.append({"check": "target_variant_sheet_link", "targetId": row.get("targetId"), "path": rel})

    screenshot_dir = RUN / "visual/live-runtime"
    screenshot_index = []
    for path in sorted(screenshot_dir.glob("*.png")):
        screenshot_index.append({"path": path.relative_to(RUN).as_posix(), "bytes": path.stat().st_size, "sha256": digest(path)})
    if len(screenshot_index) != 8:
        failures.append({"check": "live_runtime_screenshot_count", "actual": len(screenshot_index), "expected": 8})
    (screenshot_dir / "screenshots-index.json").write_text(json.dumps({
        "capturedAt": "2026-10-11",
        "captureMode": "actual local learner runtime screen; no view-option menu changes",
        "files": screenshot_index,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = {
        "capturedAt": datetime.now(timezone.utc).isoformat(),
        "task": "MV1",
        "status": "pass" if not failures else "fail",
        "scope": "frozen inventory, actual GLB hashes/parsing, runtime mapping/loader, capture completeness, and evidence-file integrity",
        "counts": {
            "muscleRows": len(muscle_rows),
            "sideCounts": dict(sides),
            "selectedMemberRoleCounts": dict(role_counts),
            "uniqueMusclePlaybackMappings": len(mappings),
            "muscleUriHashClipPairs": inventory["actualReachableCandidates"]["muscleHashClipPairs"],
            "actualReachableUriHashPairs": len(inventory["glbFiles"]),
            "glbHashAndParsePass": sum(bool(r.get("pathExists") and r.get("hashMatches") and r.get("glbStatus") == "pass") for r in inventory["glbFiles"]),
            "authoringInputHashesPass": authoring_hash_passes,
            "authoringInputHashTotal": authoring["registryRecordCount"],
            "sourceInputHashesPass": source_input_hash_passes,
            "sourceInputHashesTotal": len(inventory.get("inputHashes", {})),
            "targetStatusCounts": disposition_counts,
        },
        "metricSummary": metric_summary,
        "visualAssets": {
            "fullCycleVideo": {"path": video_file.get("path"), "bytes": video_file.get("bytes"), "sha256": video_file.get("sha256"), "hashPass": video_hash_ok},
            "fullCyclePlaybackGroups": len(videos),
            "focusedPhaseThreeViewSheets": len(phase_files),
            "denseKeyframeMidpointThreeViewSheets": len(dense_files),
            "roleSideVariantContactSheetPages": len(variant_pages),
            "liveRuntimeScreenshots": len(screenshot_index),
            "liveRuntimeScreenshotIndex": "visual/live-runtime/screenshots-index.json",
        },
        "limitations": [
            "Per-target status is scoped to the documented review; two rectus femoris knee-demo rows remain not_checked because contour prominence is ambiguous.",
            "Attachment drift has no authored landmarks for numerical measurement; visible detach screen only.",
            "Surface penetration has no collision oracle; visible screen only.",
            "Expert physiological natural-contraction signoff was not performed.",
            "The 220 dense interval sheets are generated and integrity-checked; manual visual judgement used the 74 five-phase sheets, per-target variant pages, and end-to-end 12 fps playback, not an image-by-image review of all 220 sheets.",
            "A repeat Node-side loopback fetch was unavailable in the sandbox; its failed attempt is retained. Live runtime values come from the successful browser-backed validation artifact at its timestamp.",
        ],
        "failures": failures,
    }
    output = RUN / "runtime/frozen-artifact-check.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": str(output.relative_to(ROOT)), "failures": len(failures), "metricSamples": samples}, ensure_ascii=False))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
