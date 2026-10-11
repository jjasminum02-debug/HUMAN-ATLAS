#!/usr/bin/env python3
"""Read-only consistency check for the MV1 2026-10-12 follow-up evidence."""

from __future__ import annotations

import collections
import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
FOLLOWUP = ROOT / "work/evidence/MV1/2026-10-12-followup-01"
FROZEN = ROOT / "work/evidence/MV1/2026-10-11-run-01"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def learner_label(value: str) -> str:
    value = re.sub(r"\s*자세에서\s*(?:관찰|살펴보기)", "", value)
    value = re.sub(r"\s*자세\s*관찰", "", value)
    value = re.sub(r"\s+관찰(?=\s|$)", "", value)
    return re.sub(r"\s+", " ", value).strip()


def identity(row: dict) -> tuple[str, str, str, str]:
    return (
        row["sourceKey"],
        row["sourceKeySide"],
        learner_label(row["label"]),
        row["learningIntent"],
    )


def identity_lines(rows: list[dict]) -> str:
    return "\n".join(sorted("\t".join(identity(row)) for row in rows)) + "\n"


def main() -> int:
    failures: list[str] = []
    inventory = read_json(FROZEN / "inventory.json")
    capture = read_json(FROZEN / "runtime/capture-index-v3.json")
    start = read_json(FOLLOWUP / "start.json")
    ui = read_json(FOLLOWUP / "learner-runtime-checks.json")
    loader = read_json(FOLLOWUP / "runtime/real-loader-validation.json")
    dense = read_json(FOLLOWUP / "dense-sheet-review.json")
    groups = read_json(FOLLOWUP / "playback-group-review.json")
    visual_dispositions = read_json(FOLLOWUP / "target-visual-dispositions.json")
    ambiguities = read_json(FOLLOWUP / "ambiguous-observations.json")
    queue = read_json(FOLLOWUP / "repair-queue.json")
    visual = read_json(FOLLOWUP / "visual-evidence-index.json")

    # The immutable inventory input set and the frozen playback/contact evidence must remain unchanged.
    frozen_checks = read_json(FOLLOWUP / "frozen-input-check.json")
    current_input_results = []
    for rel, expected in inventory["inputHashes"].items():
        path = ROOT / rel
        actual = sha256(path) if path.is_file() else None
        ok = actual == expected.get("sha256")
        current_input_results.append(ok)
        if not ok:
            failures.append(f"frozen-input hash changed or missing: {rel}")
    if len(current_input_results) != 17 or not all(current_input_results):
        failures.append("not all 17 frozen source hashes currently match")
    if frozen_checks.get("pass") != 17 or frozen_checks.get("fail") != 0:
        failures.append("recorded start hash gate is not 17/17")
    protected_run_file = "work/evidence/MV1/2026-10-11-run-01/runtime/real-loader-validation.json"
    baseline_status = (FOLLOWUP / start["startStatusSnapshot"]).read_bytes()
    if protected_run_file.encode() in baseline_status:
        failures.append("frozen loader result was already dirty at the follow-up baseline; cannot assert clean restore")
    current_status = subprocess.run(
        ["git", "status", "--porcelain=v2", "--", protected_run_file],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        check=True,
    ).stdout
    if current_status:
        failures.append("frozen loader result has a worktree change")
    head_blob = subprocess.run(
        ["git", "show", f"HEAD:{protected_run_file}"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        check=True,
    ).stdout
    frozen_file = ROOT / protected_run_file
    if hashlib.sha256(head_blob).hexdigest() != sha256(frozen_file):
        failures.append("frozen loader result does not match the unchanged HEAD blob")

    target_rows = [row for row in inventory["candidateRows"] if row.get("subjectKind") == "muscle"]
    expected_identities = [identity(row) for row in target_rows]
    ui_rows = ui.get("checks", [])
    ui_identities = [
        (row["sourceKey"], row["side"], row["label"], row["learningIntent"])
        for row in ui_rows
    ]
    if len(target_rows) != 332 or len(ui_rows) != 332:
        failures.append(f"learner UI row counts differ: expected 332, got {len(ui_rows)}")
    if sorted(expected_identities) != sorted(ui_identities):
        failures.append("learner UI identities do not exactly match frozen muscle inventory")
    expected_sha = hashlib.sha256(identity_lines(target_rows).encode("utf-8")).hexdigest()
    observed_sha = ui.get("method", {}).get("observedIdentitySetSha256")
    if expected_sha != observed_sha or not ui.get("method", {}).get("identitySetMatch"):
        failures.append("learner UI identity digest does not match the frozen candidate set")
    if any(row.get("flowCheckStatus") != "pass" for row in ui_rows):
        failures.append("at least one learner UI flow row is not pass")
    required_flow_flags = ("routeLoaded", "optionSelected", "emphasisEnabled", "playStarted", "returnTriggered", "restAtZero")
    if any(not all(row.get("observed", {}).get(flag) is True for flag in required_flow_flags) for row in ui_rows):
        failures.append("at least one learner UI flow row is missing an observed control state")
    route_counts = collections.Counter((row["sourceKey"], row["sourceKeySide"]) for row in target_rows)
    route_rows = collections.Counter((row["sourceKey"], row["side"]) for row in ui_rows)
    if len(route_counts) != 134 or route_counts != route_rows:
        failures.append("learner route coverage does not match the 134 frozen source-side routes")
    if loader.get("targets") != 332 or loader.get("pass") != 332 or loader.get("error") != 0:
        failures.append("actual animation scene loader result is not 332/332 pass")
    if loader.get("uniqueGlbFiles") != 71:
        failures.append("actual animation scene loader GLB denominator is not 71")

    # Each of the 220 frozen v3 sheets must be indexed once and still match its original hash.
    frozen_sheet_index = {item["path"]: item for item in capture["playbackSheetsV3"]}
    reviewed = dense.get("sheets", [])
    if len(frozen_sheet_index) != 220 or len(reviewed) != 220:
        failures.append("dense interframe sheet denominator is not 220")
    seen_sheets = set()
    for item in reviewed:
        rel = item["path"].replace("../2026-10-11-run-01/", "")
        if rel in seen_sheets:
            failures.append(f"duplicate dense-sheet review row: {rel}")
        seen_sheets.add(rel)
        expected = frozen_sheet_index.get(rel)
        path = FROZEN / rel
        if not expected or not path.is_file():
            failures.append(f"dense-sheet file missing from frozen index: {rel}")
            continue
        if item.get("sha256") != expected.get("sha256") or sha256(path) != expected.get("sha256"):
            failures.append(f"dense-sheet hash mismatch: {rel}")
        if item.get("manualReviewStatus") != "reviewed":
            failures.append(f"dense-sheet not marked reviewed: {rel}")
    if seen_sheets != set(frozen_sheet_index):
        failures.append("reviewed dense-sheet paths do not equal the frozen 220-path set")
    group_rows = groups.get("groups", [])
    if len(group_rows) != 74 or groups.get("reviewed") != 74:
        failures.append("playback-group visual review denominator is not 74/74")
    if sum(row.get("visualReviewStatus") == "observed_ambiguous" for row in group_rows) != 34:
        failures.append("playback-group ambiguity count is not 34")
    if any(row.get("naturalnessAssessment") != "not_approved_by_this_review" for row in group_rows):
        failures.append("a playback group was incorrectly marked naturally contracting")
    visual_rows = visual_dispositions.get("rows", [])
    visual_ids = {row.get("targetId") for row in visual_rows}
    ambiguous_ids = {
        target.get("targetId")
        for finding in ambiguities.get("findings", [])
        for mapping in finding.get("mappings", [])
        for target in mapping.get("impactTargets", [])
    }
    if len(visual_rows) != 332 or len(visual_ids) != 332:
        failures.append("supplemental visual disposition denominator is not 332 unique targets")
    if ambiguous_ids != {row.get("targetId") for row in visual_rows if row.get("observationState") == "observed_ambiguous"}:
        failures.append("observed ambiguity target set does not match the repair queue")
    if visual_dispositions.get("statusCounts") != {"pass": 298, "fail": 0, "not_checked": 34, "error": 0}:
        failures.append("supplemental visual status counts are not pass 298 / ambiguous-not_checked 34")
    if visual_dispositions.get("uninspectedRows") != 0 or visual_dispositions.get("naturalnessApprovedRows") != 0:
        failures.append("visual disposition has an uninspected or naturalness-approval count mismatch")

    required_queue_fields = (
        "queueId", "status", "severity", "candidateCauseGroup", "phase",
        "reproduction", "expectedAppearance", "actualObservation", "mappings", "nextAction",
    )
    findings = ambiguities.get("findings", [])
    if len(findings) != 5 or len(queue.get("candidateGroups", [])) != 5:
        failures.append("observed ambiguity queue must contain five grouped candidates")
    for finding in findings:
        for field in required_queue_fields:
            if not finding.get(field):
                failures.append(f"ambiguity {finding.get('queueId')} missing {field}")
        if finding.get("status") != "observed_ambiguous":
            failures.append(f"ambiguity {finding.get('queueId')} was normalized away")
        for mapping in finding.get("mappings", []):
            if not all(mapping.get(field) for field in ("sourceKey", "side", "assetUri", "assetSha256", "clipId")):
                failures.append(f"ambiguity {finding.get('queueId')} has incomplete asset mapping")
    if sum(len(group.get("mappings", [])) for group in findings if group["queueId"].startswith("MV1-Q04")) != 26:
        failures.append("distal hand ambiguity group no longer lists all 26 asset/clip mappings")

    # Reused screenshot evidence must be present, hash-matched, and outside the follow-up output tree.
    for screenshot in visual.get("reusedFrozenLearnerScreens", []):
        rel = screenshot["path"].replace("../2026-10-11-run-01/", "")
        path = FROZEN / rel
        if not path.is_file() or sha256(path) != screenshot.get("sha256"):
            failures.append(f"reused actual learner screenshot missing or changed: {rel}")

    result = {
        "status": "pass" if not failures else "fail",
        "frozenInputHashes": f"{sum(current_input_results)}/17",
        "learnerMappings": len(ui_rows),
        "learnerSourceSideRoutes": len(route_counts),
        "learnerIdentitySetSha256": expected_sha,
        "denseSheets": len(reviewed),
        "playbackGroups": len(group_rows),
        "targetVisualRows": len(visual_rows),
        "ambiguityGroups": len(findings),
        "reusedLearnerScreens": len(visual.get("reusedFrozenLearnerScreens", [])),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
