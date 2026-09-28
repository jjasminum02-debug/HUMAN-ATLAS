#!/usr/bin/env python3
"""Recheck T93's bounded source decision, preservation, and queue handoff."""
# -*- coding: utf-8 -*-
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "work/evidence/T93"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


baseline = load(EVIDENCE / "start-baseline.json")
decision = load(EVIDENCE / "decision.json")
matrix = load(EVIDENCE / "candidate-matrix.json")
registry = load(ROOT / "work/task-registry-r15.json")
status_text = (ROOT / "work/STATUS.md").read_text(encoding="utf-8")
task94 = (ROOT / "work/tasks/T94.md").read_text(encoding="utf-8")
access = load(EVIDENCE / "source-access-log.json")
state_after = load(EVIDENCE / "state-update-after.json")

checks: dict[str, bool] = {}
checks["decision_is_allowed_and_expected"] = (
    decision["result"] in {
        "no_exact_source_found",
        "candidate_requires_registration",
        "metadata_candidate_frame_compatible",
    }
    and decision["result"] == "no_exact_source_found"
)
checks["no_mesh_or_archive_was_downloaded"] = (
    decision["downloadedArchiveOrMesh"] is False
    and all("no archive" in access["accessBoundary"].lower() or "did not" in e.get("method", "").lower()
            for e in access["events"] if e["kind"] != "search_index_only")
)
checks["no_identity_binding_ui_or_review_promotion"] = (
    decision["newAnatomyOrMeshOrCanonicalIdOrBindingOrUi"] is False
    and decision["humanReviewPromoted"] is False
    and decision["rightsHoldPromoted"] is False
)
checks["no_exact_mesh_locator_or_object_hash_is_invented"] = all(
    c.get("exactGeometryObject", {}).get("exactTargetMeshDirectlyEstablished") is False
    and c.get("exactGeometryObject", {}).get("objectId") is None
    and c.get("exactGeometryObject", {}).get("officialPerObjectHash") is None
    for c in matrix["candidates"] if c["candidateId"] == "ZA-MODELS-PINNED"
)
checks["frame_and_component_rights_remain_unverified"] = (
    decision["t50FrameCompatibility"] == "unverified"
    and matrix["candidates"][0]["unitFrameRestPose"]["compatibleWithT50"] is False
    and matrix["candidates"][0]["rights"]["targetComponentLicense"] is None
)
queue = registry["activeQueue"]
checks["T94_is_registered_once_immediately_before_T77"] = (
    queue.count("T94") == 1 and queue.index("T94") + 1 == queue.index("T77")
)
checks["next_task_and_status_are_consistent"] = (
    registry["nextTask"] == "T94"
    and registry["taskStatuses"].get("T93") == "passed_with_gaps"
    and registry["taskStatuses"].get("T94") == "planned_not_started"
    and "NEXT_TASK: T94" in status_text
    and "CURRENT_TASK: T93" in status_text
)
checks["shared_status_registry_delta_is_recorded_and_unstaged"] = (
    state_after["sharedStateFilesStaged"] is False
    and state_after["afterSha256"]["work/STATUS.md"] == sha(ROOT / "work/STATUS.md")
    and state_after["afterSha256"]["work/task-registry-r15.json"] == sha(ROOT / "work/task-registry-r15.json")
    and state_after["queueDelta"]["insertedId"] == "T94"
    and state_after["queueDelta"]["insertedBefore"] == "T77"
)
checks["followup_is_bounded_and_does_not_acquire_mesh"] = (
    "대형 archive와 aggregate FBX는 받지 않는다." in task94
    and "mesh conversion" in task94
    and "learner binding/UI" in task94
)
checks["baseline_commit_is_current_head"] = (
    subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    == baseline["head"]
)

protected = baseline["protectedInputs"]["sha256"]
protected_checks = {}
for rel, expected in protected.items():
    if rel in {"work/STATUS.md", "work/task-registry-r15.json"}:
        # These two shared user-WIP files receive the documented T93 delta and are not staged.
        continue
    path = ROOT / rel
    protected_checks[rel] = path.exists() and sha(path) == expected
checks["protected_input_hashes_unchanged_except_documented_shared_state"] = all(protected_checks.values())
checks["OpenSim_Models_head_clean_and_unchanged"] = (
    subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT / "OpenSim_Models", text=True).strip()
    == baseline["openSimModels"]["head"]
    and not subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT / "OpenSim_Models", text=True).strip()
)

result = {
    "revision": "T93-validation-v1",
    "task": "T93",
    "result": "passed" if all(checks.values()) else "failed",
    "checks": checks,
    "protectedInputCount": len(protected_checks),
    "protectedInputPassed": sum(protected_checks.values()),
    "protectedInputFailures": [k for k, v in protected_checks.items() if not v],
    "sharedStateFilesExpectedToChangeAndRemainUnstaged": [
        "work/STATUS.md",
        "work/task-registry-r15.json",
    ],
    "sourceDownloadPerformed": False,
}
(EVIDENCE / "validation.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(result, ensure_ascii=False, indent=2))
if not all(checks.values()):
    raise SystemExit(1)
