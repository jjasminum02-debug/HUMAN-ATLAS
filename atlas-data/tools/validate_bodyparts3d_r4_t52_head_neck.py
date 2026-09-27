#!/usr/bin/env python3
"""Fail-closed integrity checks for the frozen T52 head/neck package."""

from __future__ import annotations

import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str, checks: dict[str, bool]) -> None:
    checks[message] = bool(condition)
    if not condition:
        raise ValueError(message)


def validate() -> dict:
    checks: dict[str, bool] = {}
    frozen_path = ROOT / "work/evidence/T52/frozen-source-set.json"
    acquisition_path = ROOT / "work/evidence/T52/source-acquisition.json"
    baseline_path = ROOT / "work/evidence/T52/start-baseline.json"
    frozen = json.loads(frozen_path.read_text(encoding="utf-8"))
    acquisition = json.loads(acquisition_path.read_text(encoding="utf-8"))
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    package_path = ROOT / "atlas-data/manifests/bodyparts3d-r4-t52/head-neck.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    verification = json.loads((ROOT / "work/evidence/T52/package-verification.json").read_text(encoding="utf-8"))
    require(package["status"] == "partial_static_source_package_pending_human_laterality_review", "package status fails closed while source-name/bounds laterality oppositions need human review", checks)
    require(package["scope"]["sourceNameBoundsCenterOppositionsHumanCheckRequired"] == 3, "all three source-name/bounds laterality oppositions remain explicit", checks)
    require(package["scope"]["sourceNameBoundsCrossMidlineInconclusive"] == 14, "fourteen non-opposition records retain an inconclusive midline-bounds status", checks)
    ids = [row["sourceElementFileId"] for row in frozen["atomicSourceFiles"]]
    expected_by_region = {region: sorted(row["sourceElementFileId"] for row in frozen["atomicSourceFiles"] if region in row["regionCandidates"]) for region in ("head", "neck")}
    records = package["sourceAssets"]
    record_by_id = {row["sourceElementFileId"]: row for row in records}
    require(frozen["revision"] == "BodyParts3D-R4-T52-FROZEN-ATOMIC-SOURCE-SET-v1", "frozen source manifest revision", checks)
    require(len(ids) == 85 and len(set(ids)) == 85, "85 unique frozen FJ source IDs", checks)
    require([batch["count"] for batch in frozen["internalBatches"]] == [10,10,10,10,10,10,10,10,5], "internal batch sizes are at most 10", checks)
    require(package["sourceFreezeSha256"] == digest(frozen_path), "package binds frozen source-set bytes", checks)
    require(package["sourceAcquisitionSha256"] == digest(acquisition_path), "package binds acquisition record bytes", checks)
    require(acquisition["frozenSourceSetSha256"] == digest(frozen_path), "range acquisition used the frozen source set", checks)
    require(acquisition["fullArchivesDownloaded"] is False and verification["fullArchiveDownloaded"] is False, "full source archives were not downloaded", checks)
    require(acquisition["completeSourceFileCount"] == 85 and set(row["sourceElementFileId"] for row in acquisition["selectedSourceFiles"]) == set(ids), "all frozen source IDs acquired", checks)
    require(set(record_by_id) == set(ids) and len(records) == 85, "all frozen source IDs represented exactly once in package", checks)
    require(len(record_by_id) == len(records), "no duplicate FJ source IDs", checks)
    require(package["scope"]["crossRegionDuplicateFJIds"] == [], "cross-region source FJ duplicate accounting", checks)
    require(package["scope"]["emptyOrInvalidMeshes"] == 0 and verification["emptyMeshes"] == 0, "no empty or invalid mesh", checks)
    require(package["scope"]["sourceNameConflicts"] == 0 and verification["nameConflicts"] == [], "OBJ source names match official FMA index (case-insensitive)", checks)
    require(package["scope"]["canonicalStableLearnerBindings"] == 0 and package["scope"]["sourceOnlyMeshAssets"] == 85, "no learner ID invented for unmapped source mesh", checks)
    side_oppositions = [row for row in package["lateralityBoundsDiagnostics"] if row["status"].startswith("bounds_center_opposes_source_name_human_check_required")]
    require({row["sourceElementFileId"] for row in side_oppositions} == {"FJ2742", "FJ2754", "FJ2780"}, "all three source-label/bounds-center side diagnostics are explicitly held for human check", checks)
    midline_crossings = [row for row in package["lateralityBoundsDiagnostics"] if row["bounds"]["min"][0] < 0 < row["bounds"]["max"][0]]
    require(len(midline_crossings) == 16, "sixteen total AABBs cross the median plane: fourteen inconclusive plus two opposition overlaps", checks)
    require(package["scope"]["sourceNameBoundsCenterOppositionsHumanCheckRequired"] == 3, "laterality geometry diagnostic count is explicit", checks)
    require(package["reviewBoundary"]["humanAnatomyReviewed"] is False and package["reviewBoundary"]["reviewedPromotions"] == 0, "no human review or reviewed promotion asserted", checks)
    require(package["reviewBoundary"]["canonicalCatalogChanged"] is False and package["reviewBoundary"]["learnerNavigationChanged"] is False, "canonical catalog and learner navigation untouched", checks)
    require(package["rights"]["redistributionStatus"] == "held_until_current_database_terms_and_legacy_OBJ_header_scope_are_reconciled", "legacy OBJ header license remains a distribution hold", checks)

    acquired_by_id = {row["sourceElementFileId"]: row for row in acquisition["selectedSourceFiles"]}
    local_obj_paths = sorted((ROOT / "atlas-data/source-cache/bodyparts3d-r4/mesh/t52").glob("*/*.obj"))
    require({path.stem for path in local_obj_paths} == set(ids) and len(local_obj_paths) == 85, "local T52 cache contains only the 85 frozen OBJ files", checks)
    for file_id, row in record_by_id.items():
        acquired = acquired_by_id[file_id]
        path = ROOT / acquired["cacheRelativePath"]
        require(path.is_file() and path.stat().st_size == acquired["bytes"] and digest(path) == acquired["sha256"] == row["sourceSha256"], f"source OBJ size/hash {file_id}", checks)
        require(row["sourceElementFileId"] == file_id and row["selectionId"] == f"HA-MESH-BP3D4-{file_id}", f"stable mesh key remains distinct from FJ ID {file_id}", checks)
        require(row["existingLearnerStableId"] is None and row["identityStatus"] == "source_only_no_existing_HA_mesh_crosswalk", f"source-only canonical mapping state {file_id}", checks)
        require(row["acquisitionStatus"] == "acquired_selected_official_zip_member" and row["validationStatus"] == "passed_source_identity_mesh_and_bounds_checks" and row["conversionStatus"] == "converted_to_internal_qa_batch_glb", f"acquire/validate/convert status {file_id}", checks)
        require(row["sourceName"] and row["laterality"] in {"left", "right", "bilateral", "not_stated_in_source_name"}, f"source-backed name and laterality label {file_id}", checks)
        require(bool(row["lateralityEvidence"]) and row["lateralityBoundsDiagnostic"], f"source laterality provenance and geometry diagnostic status {file_id}", checks)
        require(row["sourceHeaderLicense"] and row["sourceHeaderBounds"]["unit"] == "mm" and row["sourceVertexBounds"]["unit"] == "mm", f"header license and unit evidence {file_id}", checks)
        require(row["atlasBounds"]["frame"] == "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR" and row["atlasBounds"]["unit"] == "m", f"T50 frame transform metadata {file_id}", checks)
        require(row["regionIds"] == sorted(next(x["regionCandidates"] for x in frozen["atomicSourceFiles"] if x["sourceElementFileId"] == file_id)), f"source region routing retained {file_id}", checks)

    for region in ("head", "neck"):
        region_path = ROOT / f"atlas-data/manifests/bodyparts3d-r4-t52/{region}.json"
        region_package = json.loads(region_path.read_text(encoding="utf-8"))
        package_ids = [row["sourceElementFileId"] for row in region_package["meshAssets"]]
        require(sorted(package_ids) == expected_by_region[region] and len(package_ids) == len(set(package_ids)), f"{region} source set matches frozen membership", checks)
        require(region_package["visibleSubcategoryMenu"] is False, f"{region} has no visible subcategory menu", checks)
        require(region_package["sourceScope"]["acquired"] == region_package["sourceScope"]["validated"] == region_package["sourceScope"]["converted"] == len(package_ids), f"{region} all source FJ items accounted", checks)
        require(region_package["sourceScope"]["failed"] == 0 and region_package["sourceScope"]["notAttempted"] == 0, f"{region} no unaccounted items", checks)
        bounds = region_package["regionBounds"]
        require(bounds["min"] != bounds["max"] and bounds["vertexCount"] > 0, f"{region} computed nonempty region bounds", checks)

    for batch in package["internalBatches"]:
        glb_path = ROOT / batch["glbPath"]
        raw = glb_path.read_bytes()
        require(digest(glb_path) == batch["glbSha256"], f"internal QA GLB hash {batch['batchId']}", checks)
        require(raw[:4] == b"glTF", f"valid GLB header {batch['batchId']}", checks)
        json_len, json_kind = struct.unpack_from("<II", raw, 12)
        require(json_kind == 0x4E4F534A, f"GLB JSON chunk {batch['batchId']}", checks)
        gltf = json.loads(raw[20:20+json_len].decode("utf-8"))
        source_file_ids = sorted(node["extras"]["sourceFileId"] for node in gltf["nodes"])
        require(source_file_ids == sorted(batch["sourceElementFileIds"]) and len(source_file_ids) == len(set(source_file_ids)), f"GLB nodes cover batch source IDs exactly {batch['batchId']}", checks)
        require(not gltf.get("animations") and not gltf.get("skins"), f"static source GLB has no fabricated rig or animation {batch['batchId']}", checks)
        for node in gltf["nodes"]:
            extras = node["extras"]
            require(node["name"] == extras["stableMeshAssetId"] == extras["selectionId"] if "selectionId" in extras else node["name"] == extras["stableMeshAssetId"], f"GLB node stable mesh identity {node['name']}", checks)
            require(extras["learnerStableId"] is None and extras["reviewState"] == "needs_review" and extras["humanAnatomyReviewed"] is False, f"GLB source identity not promoted {node['name']}", checks)

    protected = baseline["protectedInputsSha256"]
    intentionally_mutable_status_files = {"work/STATUS.md", "work/task-registry-r15.json"}
    for path, expected in protected.items():
        if path in intentionally_mutable_status_files:
            continue
        require(digest(ROOT / path) == expected, f"pre-existing protected input unchanged: {path}", checks)
    opensim = ROOT / "OpenSim_Models"
    opensim_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=opensim, text=True).strip()
    opensim_status = subprocess.check_output(["git", "status", "--porcelain=v1", "-uall"], cwd=opensim, text=True).strip()
    require(opensim_head == baseline["OpenSim_Models"]["head"], "OpenSim_Models HEAD preserved", checks)
    require(not opensim_status and not baseline["OpenSim_Models"]["statusPorcelain"], "OpenSim_Models remains clean", checks)
    require(package["scope"]["wholeBodyCanonicalDenominator"] is None, "no whole-body denominator invented", checks)
    return {"revision": "T52-VALIDATOR-RESULT-v1", "status": "pass", "checkCount": len(checks), "checks": checks}


if __name__ == "__main__":
    try:
        result = validate()
    except Exception as exc:
        print(f"T52 package validation failed: {exc}", file=sys.stderr)
        raise SystemExit(2)
    output = ROOT / "work/evidence/T52/package-validator-result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "checkCount": result["checkCount"], "evidence": output.relative_to(ROOT).as_posix()}, ensure_ascii=False))
