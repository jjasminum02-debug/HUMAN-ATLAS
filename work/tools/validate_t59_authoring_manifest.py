#!/usr/bin/env python3
"""Fail-closed validation for the T59 full-scope T66 authoring handoff."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from build_t59_authoring_manifest import AUTHORING_NEXT_UNIT, AUTHORING_RUN_ID, BASELINE_PATH, MANIFEST_OUT, RECON_OUT, ROOT, build, canonical, read, R2_PATH, COMPILED_PATH


def fail(message: str) -> None:
    raise ValueError(message)


def validate(manifest: dict[str, Any], reconciliation: dict[str, Any], expected: tuple[dict[str, Any], dict[str, Any]], *, compare_to_expected: bool = True) -> dict[str, Any]:
    expected_manifest, expected_reconciliation = expected
    if compare_to_expected and canonical(manifest) != canonical(expected_manifest):
        fail("authoring-run-manifest differs from the current frozen inputs or deterministic builder")
    if compare_to_expected and canonical(reconciliation) != canonical(expected_reconciliation):
        fail("worker-reconciliation differs from original worker files/current frozen inputs")
    if manifest.get("task") != "T59" or manifest.get("contractRevision") != "t59-source-bound-same-scene-motion-v1":
        fail("task/contract revision mismatch")
    baseline = read(BASELINE_PATH)
    expected_baseline_evidence = {"path": BASELINE_PATH.as_posix(), "sha256": __import__("hashlib").sha256((ROOT / BASELINE_PATH).read_bytes()).hexdigest()}
    if manifest.get("runId") != AUTHORING_RUN_ID or manifest.get("nextUnit") != AUTHORING_NEXT_UNIT:
        fail("authoring run identity or next unit is missing/incorrect")
    if manifest.get("baselineHead") != baseline.get("baselineHead") or manifest.get("baselineEvidence") != expected_baseline_evidence:
        fail("manifest does not reference the original T59 HEAD and baseline evidence")
    denominator = manifest["denominators"]
    required = {"productTargets": 542, "productMemberships": 563, "regions": 12, "muscleTargets": 429,
                "muscleMemberships": 447, "sourceConcepts": 232, "sourceSurfaceInstances": 462,
                "existingCanonicalHaBindings": 130, "historical163": [6, 20, 135, 2]}
    if denominator != required:
        fail("product/muscle denominators or preservation values drifted")
    if not manifest.get("authoringContractInputs"):
        fail("manifest does not pin the source exporter and shared motion contracts")
    for dependency_id, contract_input in manifest["authoringContractInputs"].items():
        shared = manifest["sharedInputsAndDependencies"].get(dependency_id)
        path = Path(contract_input.get("path", ""))
        resolved = (ROOT / path).resolve()
        if shared != contract_input or not resolved.is_relative_to(ROOT) or not resolved.is_file():
            fail(f"invalid authoring contract input reference: {dependency_id}")
        if __import__("hashlib").sha256(resolved.read_bytes()).hexdigest() != contract_input.get("sha256"):
            fail(f"authoring contract input hash mismatch: {dependency_id}")
    assignments = manifest["workers"]
    target_packages = manifest["targetPackages"]
    concept_packages = manifest["sourceConceptPackages"]
    if len(target_packages) != 429 or len(concept_packages) != 232:
        fail("whole-scope package counts are incomplete")
    target_ids = [target for package in target_packages for target in package["assignedTargetIds"]]
    membership_keys = [key for package in target_packages for key in package["assignedMembershipKeys"]]
    concept_ids = [key for package in concept_packages for key in package["assignedSourceConceptKeys"]]
    source_keys = [key for package in concept_packages for key in package["assignedSourceKeys"]]
    if len(set(target_ids)) != 429 or len(set(membership_keys)) != 447 or len(set(concept_ids)) != 232 or len(set(source_keys)) != 462:
        fail("target, membership, source concept, or source surface package overlap/gap")
    if set(target_ids) != {target for worker in assignments.values() for target in worker["assignedTargetIds"]}:
        fail("target packages differ from the frozen worker assignment union")
    if set(concept_ids) != {concept for worker in assignments.values() for concept in worker["assignedSourceConceptKeys"]}:
        fail("source concept packages differ from the frozen worker assignment union")
    if set(source_keys) != {source for worker in assignments.values() for source in worker["assignedSourceKeys"]}:
        fail("source surface packages differ from the frozen worker assignment union")
    for worker_id, worker in assignments.items():
        if worker["owner"] != worker_id or worker["mayEditSharedRigOrActionContract"] is not False:
            fail(f"invalid worker ownership boundary: {worker_id}")
        prefix = f"work/evidence/T66/authoring-candidates/{worker_id}/"
        if worker["outputDirectory"] != prefix.rstrip("/"):
            fail(f"unsafe or mismatched output directory for {worker_id}")
        if any(not path.startswith(prefix) or ".." in Path(path).parts for path in worker["candidatePackagePathPrefix"].split("|")):
            fail(f"unsafe package path for {worker_id}")
    for package in target_packages + concept_packages:
        if package["owner"] not in assignments or package["authoringStatus"] == "ready":
            fail(f"package was incorrectly marked production-authorable: {package['packageId']}")
        if package["preservation"] != {"sourceOnlyStatusPreserved": True, "humanReview": "not_performed", "localRights": "held_per_source", "publicRedistribution": "held", "canonicalHaIdCreated": False}:
            fail(f"source-only/rights/review/canonical preservation changed: {package['packageId']}")
        output_path = package["outputPath"]
        if not output_path.startswith(f"work/evidence/T66/authoring-candidates/{package['owner']}/") or ".." in Path(output_path).parts:
            fail(f"unsafe output path: {output_path}")
        if set(package["dependencyIds"]) - set(manifest["sharedInputsAndDependencies"]):
            fail(f"unknown dependency ID: {package['packageId']}")
    compiled = read(COMPILED_PATH)
    compiled_instances = {row["sourceKey"]: row for row in compiled["instances"]}
    for package in concept_packages:
        for member in package["members"]:
            row = compiled_instances.get(member["sourceKey"])
            if row is None:
                fail(f"source surface absent from current compiled manifest: {member['sourceKey']}")
            if member["sourceGeometrySha256"] != row.get("evaluatedGeometrySha256") or member["instanceMatrix"] != row.get("matrix"):
                fail(f"source geometry identity/matrix drift: {member['sourceKey']}")
            if member["publicRedistribution"] != "held" or member["humanReview"] != "not_performed" or member["sourceOnly"] != row.get("sourceOnly"):
                fail(f"source policy promoted: {member['sourceKey']}")
    r2 = read(R2_PATH)
    for worker_id, worker in reconciliation["workers"].items():
        proposal_path = ROOT / worker["proposalPath"]
        if not proposal_path.is_file() or worker["proposalSha256"] != __import__("hashlib").sha256(proposal_path.read_bytes()).hexdigest():
            fail(f"worker proposal changed since reconciliation: {worker_id}")
        if worker["recordedRunId"] == r2["runId"] or not worker["stale"] or worker["fullResearchIntegrated"]:
            fail(f"worker staleness or integration state was promoted: {worker_id}")
        if not worker["originalProposalUnmodified"] or not worker["staleInputPaths"]:
            fail(f"worker original stale history not preserved: {worker_id}")
    if manifest["currentReadiness"]["authorableProductionPackages"] != 0:
        fail("production authorability was inferred without exact motion inputs")
    if manifest["preservation"]["sourceOnlyStatusPreserved"] is not True or manifest["preservation"]["humanReview"] != "not_performed" or manifest["preservation"]["publicRedistribution"] != "held":
        fail("top-level source/rights/review hold was not preserved")
    return {"valid": True, "targets": len(target_ids), "memberships": len(membership_keys), "sourceConcepts": len(concept_ids), "sourceSurfaces": len(source_keys), "workers": {worker: {"targets": len(row["assignedTargetIds"]), "memberships": len(row["assignedMembershipKeys"]), "sourceConcepts": len(row["assignedSourceConceptKeys"]), "sourceSurfaces": len(row["assignedSourceKeys"])} for worker, row in assignments.items()}, "productionAuthorable": 0}


def run_fixtures(manifest: dict[str, Any], reconciliation: dict[str, Any], expected: tuple[dict[str, Any], dict[str, Any]]) -> list[dict[str, Any]]:
    results = []
    cases = [
        ("duplicate-target", lambda value: value["targetPackages"].append(value["targetPackages"][0])),
        ("wrong-source-hash", lambda value: value["sourceConceptPackages"][0]["members"][0].__setitem__("sourceGeometrySha256", "0" * 64)),
        ("unsafe-output-path", lambda value: value["targetPackages"][0].__setitem__("outputPath", "../outside/glb")),
    ]
    for case, mutate in cases:
        corrupted = json.loads(json.dumps(manifest))
        mutate(corrupted)
        try:
            validate(corrupted, reconciliation, expected, compare_to_expected=False)
            results.append({"case": case, "passed": False, "reason": "validator unexpectedly accepted corrupt manifest"})
        except (ValueError, KeyError, IndexError) as error:
            results.append({"case": case, "passed": True, "rejectedBy": str(error)})
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--fixtures", action="store_true")
    args = parser.parse_args()
    manifest_path, reconciliation_path = ROOT / MANIFEST_OUT, ROOT / RECON_OUT
    if not manifest_path.is_file() or not reconciliation_path.is_file():
        raise SystemExit("T59 manifest/reconciliation evidence is missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    reconciliation = json.loads(reconciliation_path.read_text(encoding="utf-8"))
    expected = build()
    summary = validate(manifest, reconciliation, expected)
    if args.fixtures:
        fixture_results = run_fixtures(manifest, reconciliation, expected)
        summary["fixtures"] = fixture_results
        if not all(row["passed"] for row in fixture_results):
            raise SystemExit(json.dumps(summary, ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
