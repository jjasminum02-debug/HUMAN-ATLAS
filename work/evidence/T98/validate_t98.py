#!/usr/bin/env python3
"""Validate T98 scope, raw inventory, holds, sync projections, and preservation."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_hash(value):
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def check(checks, name, condition, details):
    checks.append({"name": name, "passed": bool(condition), "details": details})


def main():
    checks = []
    baseline = json.loads((EVIDENCE / "start-baseline.json").read_text(encoding="utf-8"))
    scope = json.loads((ROOT / "atlas-data/catalog/target-scope-t96.json").read_text(encoding="utf-8"))
    reconciliation = json.loads((EVIDENCE / "target-reconciliation-t98.json").read_text(encoding="utf-8"))
    raw = json.loads((EVIDENCE / "blender-raw-object-inventory.json").read_text(encoding="utf-8"))
    raw_summary = json.loads((EVIDENCE / "blender-raw-object-inventory-summary.json").read_text(encoding="utf-8"))
    sample_freeze = json.loads((EVIDENCE / "representative-sample-freeze.json").read_text(encoding="utf-8"))
    attempts = json.loads((EVIDENCE / "exporter-attempts.json").read_text(encoding="utf-8"))
    rights = json.loads((EVIDENCE / "rights-inheritance-and-base-decision.json").read_text(encoding="utf-8"))
    execution_delta = json.loads((EVIDENCE / "execution-record-delta.json").read_text(encoding="utf-8"))
    generated_delta = json.loads((EVIDENCE / "generated-sync-delta.json").read_text(encoding="utf-8"))
    progress = json.loads((EVIDENCE / "progress.json").read_text(encoding="utf-8"))

    check(checks, "frozen T96 denominator", len(scope["targets"]) == 542 and scope["denominators"]["primaryOwnerAssignments"] == 542 and scope["denominators"]["productRegionMembershipRows"] == 563, {"targets": len(scope["targets"]), "primaryOwners": scope["denominators"]["primaryOwnerAssignments"], "memberships": scope["denominators"]["productRegionMembershipRows"], "individualMuscleDenominator": scope["denominators"]["wholeBodyIndividualMuscleDenominator"]})
    region_counts = [(r["regionId"], r["primaryTargetCount"], r["regionMembershipCount"]) for r in reconciliation["freeze"]["regionRows"]]
    check(checks, "all 12 T96 region packages exact", len(region_counts) == 12 and sum(x[1] for x in region_counts) == 542 and sum(x[2] for x in region_counts) == 563 and reconciliation["freeze"]["membershipTargetIds"] == 542, region_counts)
    check(checks, "target candidate and identity states separated", len(reconciliation["targets"]) == 542 and all(t["identityStatus"] == "unresolved_no_exact_target_to_source_object_crosswalk" for t in reconciliation["targets"]) and all(t["geometryStatus"] == "not_evaluated_not_exported" for t in reconciliation["targets"]) and reconciliation["candidateTally"]["targetsWithZAnatomyObjectNameCandidates"] <= 542, reconciliation["candidateTally"])

    d = raw["denominators"]
    count_check = {"objects": d["objects"] == 7184, "meshDatablocks": d["meshDatablocks"] == 2910, "curves": d["curveDatablocks"] == 1898, "collections": d["collections"] == 1945, "scenes": d["scenes"] == 1, "archiveEntries": d["fileArchiveEntries"] == 7, "archiveFiles": d["fileArchiveFiles"] == 6, "sourceBlendFiles": d["sourceBlendFiles"] == 1}
    check(checks, "raw datablock denominators match T97 source inventory", all(count_check.values()), count_check)
    sample = raw["representativeSample"]
    sample_names = [row["sourceObjectLocator"]["objectIdName"] for row in sample["objects"]]
    case = sample["caseCoverage"]
    sample_ok = len(sample_names) == 12 and len(set(sample_names)) == 12 and sample["anatomicalObjectCount"] == 11 and len(case["serializedModifierObjectNames"]) >= 1 and case["serializedConstraintObjectNames"] == ["Cross Section X"] and len(case["sharedMeshPointersInSample"]) >= 1 and len(case["negativeSerializedMatrixDeterminantObjects"]) >= 1
    check(checks, "exact 12-object sample is locatable and covers serialized edge cases", sample_ok, {"names": sample_names, "caseCoverage": case})
    check(checks, "sample locator freeze matches inventory and remains unevaluated", sample_freeze["frozenObjectCount"] == 12 and sample_freeze["geometryHash"] is None and sample_freeze["previewPath"] is None and sample_freeze["evaluatedExportVerified"] is False and sample_freeze["objects"] == sample["objects"] and sample_freeze["source"]["memberSha256"] == raw["source"]["memberSha256"], {"frozenCount": sample_freeze["frozenObjectCount"], "geometryHash": sample_freeze["geometryHash"], "previewPath": sample_freeze["previewPath"], "evaluatedExportVerified": sample_freeze["evaluatedExportVerified"]})
    check(checks, "legacy collection instance absence is not misreported as evaluated instance coverage", d["objectsWithCollectionInstancePointer"] == 0 and case["collectionInstanceInSource"] is False and raw["source"].get("evaluatedInstanceCount") is None, {"legacyCollectionInstancePointerObjects": d["objectsWithCollectionInstancePointer"], "evaluatedInstanceCount": None, "nodesModifierCount": d["modifierNodeTypes"].get("NodesModifierData", 0)})

    check(checks, "exporter and evaluated preview gate remains open", attempts["decision"]["evaluatedExportVerified"] is False and attempts["decision"]["representativePreviewGenerated"] is False and attempts["decision"]["baseSelectionAllowed"] is False and attempts["attempts"][0]["exitCode"] == 134 and attempts["attempts"][0]["followupRetries"] == 0, {"attempt": attempts["attempts"][0], "decision": attempts["decision"]})
    check(checks, "source rights and human review holds preserved", rights["baseDecision"]["productionBase"] is None and rights["baseDecision"]["status"] == "undecided_evaluated_conversion_gate_failed" and all(item["redistributionRights"] in {"held", "held_pending_file_level_reconciliation"} for item in rights["sources"]) and len(rights["zAnatomyReadmeRightsGroups"]) >= 7, {"base": rights["baseDecision"]["status"], "groups": len(rights["zAnatomyReadmeRightsGroups"]), "sourceRights": [item["redistributionRights"] for item in rights["sources"]]})
    check(checks, "EXECUTION T98 row only changed", execution_delta["onlyTaskRecordChanged"] is True and execution_delta["afterT98Row"]["acceptance"] == "partial" and execution_delta["afterT98Row"]["progress"]["nextUnit"] == "verified-evaluated-exporter-and-12-object-preview" and execution_delta["unchangedOtherTaskRecordsSha256"] == canonical_hash({k: v for k, v in json.loads((ROOT / "work/EXECUTION.json").read_text())["tasks"].items() if k != "T98"}), execution_delta)
    check(checks, "progress keeps same task for resume", progress["executionStatus"] == "in_progress" and progress["acceptance"] == "partial" and progress["nextUnit"] == "verified-evaluated-exporter-and-12-object-preview" and progress["nextId"] == "T98" and progress["nextPromptPath"] == "work/evidence/T98/NEXT-T98-RESUME.md" and (ROOT / progress["nextPromptPath"]).is_file() and progress["gate"]["nextTaskExecutionStarted"] is False, {"executionStatus": progress["executionStatus"], "acceptance": progress["acceptance"], "nextId": progress["nextId"], "nextUnit": progress["nextUnit"], "nextPromptPath": progress["nextPromptPath"]})

    unchanged = []
    changed = []
    missing = []
    expected_task_deltas = []
    for rel, expected in baseline["protectedInputs"].items():
        path = ROOT / rel
        if not path.is_file():
            missing.append(rel)
            continue
        actual = sha(path)
        if actual == expected["sha256"]:
            unchanged.append(rel)
        elif rel == "work/EXECUTION.json" and actual == execution_delta["afterFileSha256"] and expected["sha256"] == execution_delta["beforeFileSha256"]:
            expected_task_deltas.append(rel)
        elif rel == "work/STATUS.md" and actual == generated_delta["statusFile"]["afterSha256"] and expected["sha256"] == generated_delta["statusFile"]["startSha256"]:
            expected_task_deltas.append(rel)
        else:
            changed.append({"path": rel, "expected": expected["sha256"], "actual": actual})
    check(checks, "protected inputs preserved except T98 and generated STATUS deltas", len(unchanged) == baseline["protectedInputCount"] - 2 and set(expected_task_deltas) == {"work/EXECUTION.json", "work/STATUS.md"} and not changed and not missing, {"baselineProtectedCount": baseline["protectedInputCount"], "unchanged": len(unchanged), "authorizedTaskDeltas": expected_task_deltas, "changedUnexpectedly": changed, "missing": missing})

    old_status_lines = (EVIDENCE / "start-status-porcelain.txt").read_text(encoding="utf-8").splitlines()
    old_paths = [line[3:] for line in old_status_lines if len(line) >= 4]
    missing_old_paths = [p for p in old_paths if not (ROOT / p.rstrip("/")).exists()]
    check(checks, "existing user WIP paths preserved", len(old_paths) == baseline["statusPathCount"] and not missing_old_paths, {"baselinePathCount": len(old_paths), "missing": missing_old_paths})

    cache_counts = {}
    for label, rel in (("bodyparts3dR4", "atlas-data/source-cache/bodyparts3d-r4"), ("zAnatomyPinned", "atlas-data/source-cache/z-anatomy/t97")):
        base = ROOT / rel
        files = [p for p in base.rglob("*") if p.is_file()]
        cache_counts[label] = {"fileCount": len(files), "bytes": sum(p.stat().st_size for p in files)}
        expected = baseline["sourceCaches"][label]
        if cache_counts[label]["fileCount"] != expected["fileCount"] or cache_counts[label]["bytes"] != expected["bytes"]:
            cache_counts[label]["matchesStart"] = False
        else:
            cache_counts[label]["matchesStart"] = True
    check(checks, "source cache inventories preserved without redownload", all(v["matchesStart"] for v in cache_counts.values()), cache_counts)

    source = baseline["openSimModels"]
    opensim = ROOT / "OpenSim_Models"
    head = subprocess.check_output(["git", "-C", str(opensim), "rev-parse", "HEAD"], text=True).strip()
    status = subprocess.check_output(["git", "-C", str(opensim), "status", "--porcelain"], text=True).strip()
    check(checks, "OpenSim_Models preserved read-only", head == source["head"] and not status, {"expectedHead": source["head"], "actualHead": head, "status": status})

    compile_results = []
    for name in ["inspect_t98_blend.py", "reconcile_t96_targets.py", "update_execution_record.py", "validate_t98.py"]:
        path = EVIDENCE / name
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
            compile_results.append({"path": name, "passed": True})
        except SyntaxError as exc:
            compile_results.append({"path": name, "passed": False, "error": str(exc)})
    check(checks, "T98 Python tools syntax", all(row["passed"] for row in compile_results), compile_results)

    sync = subprocess.run([sys.executable, str(ROOT / "work/tools/sync_execution.py"), "--check"], cwd=ROOT, text=True, capture_output=True)
    check(checks, "generated execution projections in sync", sync.returncode == 0, {"exitCode": sync.returncode, "stdout": sync.stdout.strip(), "stderr": sync.stderr.strip()})

    result = {
        "schemaVersion": "1.0.0",
        "task": "T98",
        "result": "partial" if all(item["passed"] for item in checks) else "partial_validation_failure",
        "validationScope": "source inventory and preservation/data contract only; actual evaluated export, preview and production base are intentionally not marked passed",
        "checks": checks,
        "summary": {"checkCount": len(checks), "passedCount": sum(item["passed"] for item in checks), "failedCount": sum(not item["passed"] for item in checks), "protectedInputsUnchanged": len(unchanged), "authorizedTaskDeltas": expected_task_deltas, "targetRecords": len(reconciliation["targets"]), "regionMemberships": reconciliation["freeze"]["regionMembershipRows"], "representativeObjectCount": sample["frozenObjectCount"], "evaluatedExportVerified": attempts["decision"]["evaluatedExportVerified"], "productionBaseSelected": rights["baseDecision"]["productionBase"] is not None},
    }
    (EVIDENCE / "validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    if not all(item["passed"] for item in checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
