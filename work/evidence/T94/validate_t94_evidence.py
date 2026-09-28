#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate T94 source disposition, state delta, and preservation invariants."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "work/evidence/T94"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


baseline = load(EVIDENCE / "start-baseline.json")
decision = load(EVIDENCE / "decision.json")
matrix = load(EVIDENCE / "candidate-matrix.json")
access = load(EVIDENCE / "source-access-log.json")
state_after = load(EVIDENCE / "state-update-after.json")
registry = load(ROOT / "work/task-registry-r15.json")
status_text = (ROOT / "work/STATUS.md").read_text(encoding="utf-8")
checks: dict[str, bool] = {}

checks["result_enum_and_expected_no_exact_finding"] = (
    decision["result"] in {
        "no_exact_source_found",
        "candidate_requires_registration",
        "metadata_candidate_frame_compatible",
    }
    and decision["result"] == "no_exact_source_found"
    and decision["taskStatus"] == "passed_with_gaps"
)
checks["no_large_archive_aggregate_or_mesh_download"] = (
    decision["archiveAggregateOrMeshDownloaded"] is False
    and "No Z-Anatomy.zip" in access["downloadBoundary"]
    and "MuscularSystem100.fbx" in access["downloadBoundary"]
)
checks["target_geometry_identity_and_hash_remain_null"] = (
    decision["exactTargetObjectLocated"] is False
    and decision["officialObjectOrMemberHash"] is None
    and all(c.get("exactLatissimusObjectLocated") is False for c in matrix["candidates"]
            if c["id"] == "ZA-PC-APP-MUSCULARSYSTEM-AGGREGATE")
    and matrix["candidates"][0]["packageAsset"]["internalObjectId"] is None
    and matrix["candidates"][0]["packageAsset"]["internalMemberPath"] is None
)
checks["side_frame_pose_and_component_rights_are_unresolved"] = (
    decision["sourceSideOrPart"] is None
    and decision["sourceUnitFrameRestPose"] is None
    and decision["t50FrameCompatibility"] == "unverified"
    and decision["localTechnicalUseRights"] == "unresolved/held"
    and decision["redistributionRights"] == "held"
)
checks["no_id_geometry_binding_ui_or_hold_promotion"] = (
    decision["anatomyIdGeometryBindingUiAdded"] is False
    and decision["humanReviewOrRightsHoldPromoted"] is False
)
checks["latissimus_and_T77_visual_gate_remain_partial"] = (
    decision["latissimusStatus"].startswith("missing")
    and "partial" in decision["visualGate"].lower()
    and registry["taskStatuses"].get("T77") == "planned_not_started"
)
queue = registry["activeQueue"]
checks["T94_precedes_T77_and_T77_is_next"] = (
    registry["nextTask"] == "T77"
    and queue.index("T94") + 1 == queue.index("T77")
    and registry["taskStatuses"].get("T94") == "passed_with_gaps"
)
checks["registry_and_status_record_the_partial_handoff"] = (
    "NEXT_TASK: T77" in status_text
    and "CURRENT_TASK: T94 - passed_with_gaps" in status_text
    and "LAST_REPORT: work/reports/T94.md" in status_text
    and "no_exact_source_found" in next(t for t in registry["tasks"] if t["id"] == "T77").get("coverageGateAmendment", "")
)
checks["state_delta_hashes_match_working_files_and_remain_unstaged"] = (
    state_after["afterSha256"]["work/STATUS.md"] == sha(ROOT / "work/STATUS.md")
    and state_after["afterSha256"]["work/task-registry-r15.json"] == sha(ROOT / "work/task-registry-r15.json")
    and state_after["sharedStateFilesStaged"] is False
)
checks["start_commit_and_unique_unused_id_cursor_preserved"] = (
    subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == baseline["head"]
    and registry["nextUnallocatedNumericId"] == 95
)

protected = baseline["protectedInputs"]["sha256"]
protected_checks = {}
for rel, expected in protected.items():
    if rel in {"work/STATUS.md", "work/task-registry-r15.json"}:
        continue  # documented, preexisting shared WIP with T94 state delta; left unstaged
    path = ROOT / rel
    protected_checks[rel] = path.exists() and sha(path) == expected
checks["all_other_start_inputs_unchanged"] = all(protected_checks.values())
checks["OpenSim_Models_head_and_clean_state_preserved"] = (
    subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT / "OpenSim_Models", text=True).strip()
    == baseline["openSimModels"]["head"]
    and not subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT / "OpenSim_Models", text=True).strip()
)

result = {
    "revision": "T94-validation-v1",
    "task": "T94",
    "result": "passed" if all(checks.values()) else "failed",
    "checks": checks,
    "protectedInputCount": len(protected_checks),
    "protectedInputPassed": sum(protected_checks.values()),
    "protectedInputFailures": [name for name, passed in protected_checks.items() if not passed],
    "sharedStateFilesChangedButNotStaged": ["work/STATUS.md", "work/task-registry-r15.json"],
    "sourceOrModelDownloadPerformed": False
}
(EVIDENCE / "validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
if not all(checks.values()):
    raise SystemExit(1)
