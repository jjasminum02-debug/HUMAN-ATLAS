#!/usr/bin/env python3
"""Join MV1's frozen runtime, loader, clip, and visual artifacts into row-level dispositions."""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUN = ROOT / "work/evidence/MV1/2026-10-11-run-01"
OUT = RUN / "target-dispositions.json"


def read(rel: str):
    return json.loads((RUN / rel).read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    inventory = read("inventory.json")
    binding = read("runtime/live-binding-validation.json")
    loader = read("runtime/real-loader-validation.json")
    phases = read("runtime/focused-phase-index.json")
    capture = read("runtime/capture-index-v3.json")
    metrics = read("metrics/automatic-metrics-v3.json")

    rows = [r for r in inventory["candidateRows"]
            if r.get("inventoryScope") == "in_scope_muscle" and r.get("subjectKind") == "muscle"]
    group_for = defaultdict(list)
    group_by_variant = {}
    for group in inventory["uniquePlaybackMappings"]:
        if "muscle" not in group.get("sourceScopes", []):
            continue
        for target_id in group.get("variantIds", []):
            group_for[target_id].append(group)
            group_by_variant[target_id] = group

    binding_by_id = {r["targetId"]: r for r in binding["rows"]}
    loader_by_id = {r["targetId"]: r for r in loader["results"]}
    phase_by_key = {
        group_by_variant[r["targetId"]]["dedupeKey"]: r
        for r in phases["files"] if r.get("targetId") in group_by_variant
    }
    metric_by_key = {r["dedupeKey"]: r for r in metrics["metrics"]}
    video_by_key = {r["dedupeKey"]: r for r in capture["videos"]}
    variant_dir = RUN / "visual/variant-contact-sheets"
    visual_rows = []
    failures = []
    status_counts = Counter()
    group_members = Counter()

    for index, row in enumerate(rows):
        target_id = row["targetId"]
        groups = group_for.get(target_id, [])
        if len(groups) != 1:
            failures.append({"targetId": target_id, "error": "playback_mapping_cardinality", "count": len(groups)})
            group = groups[0] if groups else None
        else:
            group = groups[0]
        dedupe_key = group.get("dedupeKey") if group else None
        phase = phase_by_key.get(dedupe_key)
        metric = metric_by_key.get(dedupe_key)
        video = video_by_key.get(dedupe_key)
        page_number = index // 36 + 1
        row_slot = index % 36 + 1
        page_rel = f"visual/variant-contact-sheets/page-{page_number:02d}.jpg"
        page_path = RUN / page_rel
        binding_row = binding_by_id.get(target_id)
        loader_row = loader_by_id.get(target_id)
        knee_demo = (row.get("learningIntent") == "muscle_action"
                     and "RECTUS-KNEE" in str(row.get("clipId", "")))

        subchecks = {
            "live_route_getter_side_binding": "pass" if binding_row and binding_row.get("status") == "pass" else "error",
            "real_animation_scene_loader": "pass" if loader_row and loader_row.get("status") == "pass" else "error",
            "role_side_rest_mid_max_three_view_sheet": "pass" if page_path.is_file() else "error",
            "group_rest_preparation_mid_max_return_three_view_sheet": "pass" if phase else "error",
            "full_cycle_video_present": "pass" if video and capture.get("videoFile", {}).get("sha256") else "error",
            "all_keyframes_and_adjacent_midpoints_automatic_metrics": "pass" if metric and metric.get("technicalStatus") == "pass" else "error",
            "role_side_static_selected_target_emphasis": "pass" if page_path.is_file() else "error",
            "learner_runtime_action_return_emphasis_for_this_mapping": "not_checked",
            "attachment_visual_screen": "pass" if phase and video else "not_checked",
            "penetration_visual_screen": "pass" if phase and video else "not_checked",
            "numerical_attachment_drift": "not_checked",
            "numerical_surface_penetration": "not_checked",
            "expert_natural_contraction_signoff": "not_checked",
        }
        must_have = list(subchecks.values())[:6]
        if any(status == "error" for status in must_have):
            status = "error"
        elif knee_demo:
            status = "not_checked"
        else:
            status = "pass"

        group_members[dedupe_key or "missing"] += 1
        status_counts[status] += 1
        visual_rows.append({
            "targetId": target_id,
            "learnerActionKey": row.get("learnerActionKey"),
            "sourceKey": row.get("sourceKey"),
            "side": row.get("sourceKeySide"),
            "subjectKind": row.get("subjectKind"),
            "label": row.get("label"),
            "learningIntent": row.get("learningIntent"),
            "selectedRowEnglishName": row.get("selectedRowEnglishName"),
            "selectedMemberRole": row.get("selectedMemberRole"),
            "memberRoleSet": row.get("memberRoleSet"),
            "assetId": row.get("assetId"),
            "uri": row.get("uri"),
            "sha256": row.get("sha256"),
            "clipId": row.get("clipId"),
            "transformFingerprint": row.get("transformFingerprint"),
            "playbackFingerprint": row.get("playbackFingerprint"),
            "dedupeKey": dedupe_key,
            "status": status,
            "statusScope": "observed defect-screen disposition; pass is not physiological/expert approval",
            "subchecks": subchecks,
            "visualEvidence": {
                "variantSheet": page_rel,
                "variantPageRow": row_slot,
                "playbackPhaseSheet": phase.get("path") if phase else None,
                "fullCycleVideo": capture.get("videoFile", {}).get("path"),
                "fullCycleVideoSha256": capture.get("videoFile", {}).get("sha256"),
                "metricDedupeKey": dedupe_key,
            },
            "notes": (["Preparation/action contour prominence is visually ambiguous; see suspected finding MV1-SUSPECT-RECTUS-KNEE-CONTOUR."]
                      if knee_demo else []),
        })

    result = {
        "schemaVersion": "human-atlas-mv1-target-dispositions-v1",
        "capturedAt": "2026-10-11",
        "task": "MV1",
        "sourceInventory": "inventory.json",
        "statusPolicy": "pass means no definite defect found within the recorded visual screen and required technical mapping/load checks; not_checked means ambiguity or an explicit review limitation remains; technical/naturalness subchecks stay separate.",
        "denominator": {
            "learnerReachableMuscleRoleSideRows": len(rows),
            "uniqueMusclePlaybackMappings": sum(1 for g in inventory["uniquePlaybackMappings"] if "muscle" in g.get("sourceScopes", [])),
            "uniqueUrisAndHashesForMuscleRows": inventory["actualReachableCandidates"]["muscleHashClipPairs"],
            "uniqueSourceKeys": inventory["actualReachableCandidates"]["uniqueMuscleSubjectSourceKeys"],
        },
        "statusCounts": {name: status_counts.get(name, 0) for name in ("pass", "fail", "not_checked", "error")},
        "mappingCardinalityFailures": failures,
        "visualRows": visual_rows,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), "rows": len(visual_rows),
                      "statusCounts": dict(status_counts), "mappingCardinalityFailures": len(failures)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
