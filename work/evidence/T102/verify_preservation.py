#!/usr/bin/env python3
"""Recheck T102's recorded inputs, independent concurrent changes, and protected trees."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASELINE = ROOT / "work/evidence/T102/start-baseline.json"
SOURCE = ROOT / "atlas-data/manifests/bodyparts3d-r4-t102/source-manifest.json"
OUT = ROOT / "work/evidence/T102/preservation.json"
MUTABLE_WORKFLOW_CONTEXT = {"work/STATUS.md", "work/task-registry-r15.json"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
source = json.loads(SOURCE.read_text(encoding="utf-8"))
start_inputs = baseline["inputSha256"]
source_inputs = source["inputs"]
allowed_concurrent_paths = {
    "design/2026-09-25-muscle-atlas/22-EFFICIENT-DELIVERY-AND-PERFORMANCE.md",
    "design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md",
    "work/STATUS.md",
    "work/task-registry-r15.json",
}
baseline_changes = []
manifest_mismatches = []
workflow_context_hashes = []
freeze_control_hashes = {}
for relative, start_hash in start_inputs.items():
    path = ROOT / relative
    current_hash = sha(path) if path.is_file() else None
    if current_hash != start_hash:
        baseline_changes.append({"path": relative, "startSha256": start_hash, "currentSha256": current_hash})
for relative, frozen_hash in source_inputs.items():
    if relative in {"frozenSourceSetSha256", "sourceAcquisitionSha256"}:
        freeze_control_hashes[relative] = frozen_hash
        continue
    path = ROOT / relative
    current_hash = sha(path) if path.is_file() else None
    if relative in MUTABLE_WORKFLOW_CONTEXT:
        workflow_context_hashes.append({"path": relative, "freezeTimeSha256": frozen_hash,
                                        "currentSha256": current_hash,
                                        "isGeometryInput": False,
                                        "currentMayAdvance": True})
        continue
    if current_hash != frozen_hash:
        manifest_mismatches.append({"path": relative, "frozenSha256": frozen_hash, "currentSha256": current_hash})

status_delta = json.loads((ROOT / "work/evidence/T102/status-registry-delta.json").read_text(encoding="utf-8"))
for row in workflow_context_hashes:
    details = status_delta["files"].get(row["path"], {})
    row["deltaBeforeSha256"] = details.get("sha256BeforeT102Delta")
    row["deltaAfterSha256"] = details.get("sha256AfterT102Delta")
    row["matchesRecordedT102Delta"] = row["currentSha256"] == row["deltaAfterSha256"]
workflow_context_matches = len(workflow_context_hashes) == len(MUTABLE_WORKFLOW_CONTEXT) and all(
    row["matchesRecordedT102Delta"] for row in workflow_context_hashes
)

open_sim_path = ROOT / "OpenSim_Models"
open_sim_head = git("rev-parse", "HEAD", cwd=open_sim_path)
open_sim_status = git("status", "--porcelain", "--untracked-files=all", cwd=open_sim_path)
start_head = baseline["baselineHead"]
current_head = git("rev-parse", "HEAD")
head_ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", start_head, current_head], cwd=ROOT).returncode == 0
commits = []
if head_ancestor and start_head != current_head:
    for commit in git("rev-list", "--reverse", f"{start_head}..{current_head}").splitlines():
        commits.append({
            "commit": commit,
            "subject": git("show", "-s", "--format=%s", commit),
            "paths": git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).splitlines(),
        })

prior_t13 = baseline.get("priorT13Drafts", {"paths": [], "sha256": {}})
prior_t13_current = []
for relative in prior_t13.get("paths", []):
    path = ROOT / relative
    prior_t13_current.append({"path": relative, "sha256": sha(path) if path.is_file() else None,
                              "baselineSha256": prior_t13.get("sha256", {}).get(relative)})

actual_status = git("status", "--porcelain", "--untracked-files=all").splitlines()
result = {
    "task": "T102",
    "startHead": start_head,
    "currentHeadBeforeT102Commit": current_head,
    "startIndexEmpty": baseline["baselineIndexEmpty"],
    "startStatusPathCountIncludingSnapshot": baseline["baselineStatusPathCount"],
    "currentStatusPathCount": len(actual_status),
    "commitsSinceStart": commits,
    "concurrentChangesAfterStart": {
        "expectedSharedInputPaths": sorted(allowed_concurrent_paths),
        "startVsCurrentHashChanges": baseline_changes,
        "onlyExpectedSharedFilesChanged": {x["path"] for x in baseline_changes} == allowed_concurrent_paths,
        "currentBuildManifestInputsMatch": not manifest_mismatches and workflow_context_matches,
        "buildManifestInputMismatches": manifest_mismatches,
        "workflowContextFreezeHashes": workflow_context_hashes,
        "sourceFreezeControlHashes": freeze_control_hashes,
        "interpretation": "Immutable geometry/scene inputs remain byte-identical to their freeze hashes. STATUS and R15 registry retain their freeze-time hashes as historical context, while current values are checked against the recorded T102 delta because workflow state advances independently of geometry.",
    },
    "openSimModels": {
        "startHead": baseline["openSimModels"]["head"],
        "currentHead": open_sim_head,
        "startClean": baseline["openSimModels"]["clean"],
        "currentClean": open_sim_status == "",
        "currentPorcelain": open_sim_status,
        "unchanged": open_sim_head == baseline["openSimModels"]["head"] and open_sim_status == "",
    },
    "priorT13Drafts": {
        "baselinePaths": prior_t13.get("paths", []),
        "current": prior_t13_current,
        "unchanged": all(x["sha256"] == x["baselineSha256"] for x in prior_t13_current),
    },
    "protectedParentManifestsMatchFrozenT102Inputs": not manifest_mismatches,
    "mutableWorkflowContextMatchesRecordedDelta": workflow_context_matches,
    "result": "pass" if (head_ancestor and not manifest_mismatches and workflow_context_matches and open_sim_head == baseline["openSimModels"]["head"] and open_sim_status == "") else "fail",
}
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"result": result["result"], "startHead": start_head, "currentHead": current_head,
                  "baselineHashChanges": [x["path"] for x in baseline_changes],
                  "manifestInputMismatches": [x["path"] for x in manifest_mismatches],
                  "workflowContextMatchesRecordedDelta": workflow_context_matches,
                  "openSimUnchanged": result["openSimModels"]["unchanged"]}, ensure_ascii=False, indent=2))
