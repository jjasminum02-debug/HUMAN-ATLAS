#!/usr/bin/env python3
"""Independent read-only checks for the T98 existing-metadata resume unit."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def add(checks, name, condition, evidence):
    checks.append({"name": name, "passed": bool(condition), "evidence": evidence})


def status_path(line: str) -> str:
    return line[3:] if len(line) >= 3 and line[2] == " " else line[2:]


def main() -> None:
    checks = []
    baseline = json.loads((HERE / "baseline.json").read_text(encoding="utf-8"))
    assessment = json.loads((HERE / "existing-metadata-assessment.json").read_text(encoding="utf-8"))
    execution = json.loads((ROOT / "work/EXECUTION.json").read_text(encoding="utf-8"))
    progress = json.loads((ROOT / "work/evidence/T98/progress.json").read_text(encoding="utf-8"))
    row = execution["tasks"]["T98"]
    source = assessment["runtimeProvenance"]
    objects = assessment["exactObjectLineageAndRights"]["objects"]
    target = assessment["wholeBodyCoverageCandidateComparison"]

    add(checks, "resume starts from recorded HEAD", baseline["startingHead"] == "3f385d6cf5bc52871244a53babf6309de8bb0138", baseline["startingHead"])
    add(checks, "start index was unstaged", baseline["workingTree"]["stagedCount"] == 0 and not baseline["workingTree"]["stagedPaths"], baseline["workingTree"])

    allowed = {
        "work/EXECUTION.json", "work/evidence/T98/progress.json", "work/reports/T98.md",
        "work/NEXT.md", "work/STATUS.md", "work/task-registry-r15.json",
    }
    protected_mismatches = []
    for relative, expected in baseline["inputFiles"].items():
        path = ROOT / relative
        if not expected["exists"]:
            if path.exists():
                continue
            protected_mismatches.append({"path": relative, "reason": "missing at baseline and current"})
            continue
        if not path.is_file():
            protected_mismatches.append({"path": relative, "reason": "missing"})
            continue
        actual = sha(path)
        if actual != expected["sha256"] and relative not in allowed:
            protected_mismatches.append({"path": relative, "expected": expected["sha256"], "actual": actual})
    add(checks, "resume source/design/evidence inputs unchanged outside owned deltas", not protected_mismatches, {"inputCount": len(baseline["inputFiles"]), "allowedTaskOrGeneratedPaths": sorted(allowed), "mismatches": protected_mismatches})

    old_paths = [status_path(line).rstrip("/") for line in baseline["workingTree"]["statusLines"]]
    missing_old_paths = [relative for relative in old_paths if not (ROOT / relative).exists()]
    add(checks, "all pre-existing WIP paths still exist", not missing_old_paths, {"baselineCount": baseline["workingTree"]["pathCount"], "missing": missing_old_paths})

    source_inputs = assessment["inputHashes"]
    changed_sources = []
    for relative, expected in source_inputs.items():
        actual = sha(ROOT / relative)
        if actual != expected:
            changed_sources.append({"path": relative, "expected": expected, "actual": actual})
    add(checks, "T50/T69/T96/T97/T98 source evidence hashes unchanged", not changed_sources, {"inputCount": len(source_inputs), "mismatches": changed_sources})

    source_archive = ROOT / "atlas-data/source-cache/z-anatomy/t97/Z-Anatomy.zip"
    source_blend = ROOT / "atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend"
    expected_archive = baseline["inputFiles"]["atlas-data/source-cache/z-anatomy/t97/Z-Anatomy.zip"]["sha256"]
    expected_blend = baseline["inputFiles"]["atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend"]["sha256"]
    add(checks, "pinned archive and Startup.blend bytes preserved", sha(source_archive) == expected_archive and sha(source_blend) == expected_blend, {"archiveSha256": sha(source_archive), "startupSha256": sha(source_blend)})

    open_sim = baseline["openSimModels"]
    actual_os_head = subprocess.check_output(["git", "-C", str(ROOT / "OpenSim_Models"), "rev-parse", "HEAD"], text=True).strip()
    actual_os_status = subprocess.check_output(["git", "-C", str(ROOT / "OpenSim_Models"), "status", "--porcelain"], text=True).strip()
    add(checks, "OpenSim_Models read-only checkout preserved", actual_os_head == open_sim["head"] and actual_os_status == open_sim["status"], {"expected": open_sim, "actual": {"head": actual_os_head, "status": actual_os_status}})

    runtime = assessment["runtimeProvenance"]
    dmgreceipt = runtime["T97Blender350DownloadReceipt"]
    add(checks, "mounted Blender 3.5.0 is linked to existing T97 recorded DMG", runtime["mountedImageObservation"] is not None and dmgreceipt["mountedImagePathMatchesReceiptPath"] and dmgreceipt["currentImageHashMatchesReceipt"], {"mount": runtime["mountedImageObservation"], "receipt": dmgreceipt})
    external_dmg = baseline["externalReadOnlyArtifacts"]["/private/tmp/t97-blender-3.5.0-arm64.dmg"]
    external_path = Path("/private/tmp/t97-blender-3.5.0-arm64.dmg")
    external_dmg_matches = external_path.is_file() and sha(external_path) == external_dmg["sha256"] == dmgreceipt["recordedSha256"]
    add(checks, "existing local Blender 3.5.0 DMG still matches start hash and T97 receipt", external_dmg_matches, {"baseline": external_dmg, "receiptSha256": dmgreceipt["recordedSha256"], "currentExists": external_path.is_file()})
    add(checks, "5.2.2 receipt mismatch and invalid signature retained; authenticity not promoted", runtime["T97Blender522OfficialReceipt"]["authenticatesMountedBlender350Image"] is False and runtime["codeSignature"]["exitCode"] == 1 and runtime["assessment"]["runtimePublisherProvenanceVerified"] is False, {"Blender522Receipt": runtime["T97Blender522OfficialReceipt"], "codeSignature": runtime["codeSignature"], "assessment": runtime["assessment"]})
    add(checks, "current Blender executable hash equals the prior evaluated-export receipt", runtime["mountedRuntime"]["matchesPriorT98ExecutableReceipt"] and runtime["mountedRuntime"]["sha256"] == "23171ca8704539b44c94cb370894cb3b38908530c012267bed079326d7be95b0", runtime["mountedRuntime"])

    freeze = json.loads((ROOT / "work/evidence/T98/representative-sample-freeze.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "work/evidence/T98/resume-2026-09-28/evaluated-export-manifest.json").read_text(encoding="utf-8"))
    expected_names = {item["sourceObjectLocator"]["objectIdName"] for item in freeze["objects"]}
    recorded_names = {item["objectName"] for item in objects}
    evaluated_names = {item["objectName"] for item in manifest["sample"]["objects"]}
    add(checks, "assessment reuses the exact 12 frozen object locators and prior evaluated output", len(expected_names) == 12 and recorded_names == expected_names and evaluated_names == expected_names, {"freeze": len(expected_names), "assessment": len(recorded_names), "previousManifest": len(evaluated_names)})
    add(checks, "no upstream source IDs or per-object rights-family links were inferred", all(item["exactUpstreamObjectId"] is None and item["exactUpstreamFmaFjBp3dId"] is None and item["objectToRightsFamilyMembership"].startswith("unresolved") for item in objects), {"rows": len(objects), "exactExternalIds": assessment["exactObjectLineageAndRights"]["exactFMAFJBp3dSourceIdsFoundInExistingT98Records"], "lineageLimit": assessment["exactObjectLineageAndRights"]["scopeLimit"]})
    add(checks, "TA2 IDs remain lexical terminology candidates, not mesh IDs", all(all(candidate["note"].startswith("TA2 target ID is a terminology target") for candidate in item["lexicalTa2TargetCandidatesOnly"]) for item in objects), {"candidateRows": sum(len(item["lexicalTa2TargetCandidatesOnly"]) for item in objects)})

    frame = assessment["frameUnitPoseAndLaterality"]
    add(checks, "Z-Anatomy physical unit/frame/rest-pose remains unresolved and no BP3D transform applied", frame["sourceDeclaredPhysicalUnit"] is None and frame["sourceFrameRegistration"] == "unresolved" and frame["referenceRestPoseId"] is None and "not applied" in frame["compatibilityConclusion"], frame)
    rights = assessment["exactObjectLineageAndRights"]["rightsState"]
    add(checks, "source-only, rights hold, human review, and no learner mapping preserved", rights == {"sourceOnly": True, "localUseRights": "held_pending_file_level_reconciliation", "publicRedistribution": "held", "humanReview": "not_performed", "canonicalMappingAdded": False, "learnerBindingAdded": False}, rights)

    denominator = target["targetDenominator"]
    add(checks, "T96 542/563 denominators and null individual-muscle denominator preserved", denominator["canonicalConceptTargetRecords"] == 542 and denominator["regionMembershipRows"] == 563 and denominator["wholeBodyIndividualMuscleDenominator"] is None, denominator)
    add(checks, "regional lexical candidates sum to 430 Z and 236 BP3D; exact target joins remain zero", sum(x["zAnatomyNameCandidates"] for x in target["byRegion"]) == 430 and sum(x["bodyParts3dLexicalCandidates"] for x in target["byRegion"]) == 236 and all(x["exactTargetSourceJoins"] == 0 for x in target["byRegion"]), {"regions": target["byRegion"], "z": target["ZAnatomy"]["exactTargetObjectJoins"], "bp3d": target["BodyParts3dR4"]["exactTa2ToFmaFjJoins"]})
    add(checks, "sample costs are not presented as whole-body costs and base remains undecided", assessment["costAndBaseDecision"]["costsDirectlyComparable"] is False and assessment["costAndBaseDecision"]["productionBase"] is None and assessment["costAndBaseDecision"]["baseStatus"] == "undecided", assessment["costAndBaseDecision"])

    add(checks, "EXECUTION remains partial at the exact same T98 nextUnit; no T99 started", row["executionStatus"] == "in_progress" and row["acceptance"] == "partial" and row["progress"]["nextUnit"] == "resolve-frame-unit-pose-side-rights-lineage-and-base-comparison" and row["progress"]["nextId"] == "T98" and not row["progress"]["gate"]["nextTaskExecutionStarted"], {"executionStatus": row["executionStatus"], "acceptance": row["acceptance"], "progress": row["progress"]})
    old_execution = json.loads(subprocess.check_output(["git", "show", baseline["startingHead"] + ":work/EXECUTION.json"], cwd=ROOT, text=True))
    non_t98_before = {key: value for key, value in old_execution["tasks"].items() if key != "T98"}
    non_t98_now = {key: value for key, value in execution["tasks"].items() if key != "T98"}
    add(checks, "no other EXECUTION task record changed", non_t98_before == non_t98_now, {"matches": non_t98_before == non_t98_now})

    sync = subprocess.run([sys.executable, str(ROOT / "work/tools/sync_execution.py"), "--check"], cwd=ROOT, text=True, capture_output=True)
    add(checks, "generated execution projections synchronized", sync.returncode == 0, {"exit": sync.returncode, "stdout": sync.stdout.strip(), "stderr": sync.stderr.strip()})
    syntax = []
    for path in [HERE / "build_assessment.py", HERE / "validate_resume.py"]:
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
            syntax.append({"path": path.name, "passed": True})
        except SyntaxError as exc:
            syntax.append({"path": path.name, "passed": False, "error": str(exc)})
    add(checks, "T98 assessment tools parse as Python", all(item["passed"] for item in syntax), syntax)

    result = {
        "schemaVersion": "1.0.0",
        "task": "T98",
        "unit": "resolve-frame-unit-pose-side-rights-lineage-and-base-comparison",
        "result": "passed_with_gates_unresolved" if all(item["passed"] for item in checks) else "validation_failed",
        "taskStatus": "partial",
        "checks": checks,
        "summary": {
            "checkCount": len(checks),
            "passedCount": sum(1 for item in checks if item["passed"]),
            "failedCount": sum(1 for item in checks if not item["passed"]),
            "runtimeArtifactLineageToRecorded3_5_0Dmg": dmgreceipt["mountedImagePathMatchesReceiptPath"] and dmgreceipt["currentImageHashMatchesReceipt"],
            "runtimePublisherIntegrityVerified": runtime["assessment"]["runtimePublisherProvenanceVerified"],
            "exactObjectLineageResolved": False,
            "framePoseResolved": False,
            "productionBaseSelected": False,
            "nextUnit": row["progress"]["nextUnit"],
            "nextTaskStarted": False,
        },
    }
    output = HERE / "runtime-chain-validation.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    if result["summary"]["failedCount"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
