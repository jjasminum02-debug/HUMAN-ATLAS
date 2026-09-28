#!/usr/bin/env python3
"""Build a T98-only assessment from already-pinned evidence; never launches Blender."""

from __future__ import annotations

import hashlib
import json
import plistlib
import re
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent


def read_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    freeze = read_json("work/evidence/T98/representative-sample-freeze.json")
    raw_inventory = read_json("work/evidence/T98/blender-raw-object-inventory.json")
    export = read_json("work/evidence/T98/resume-2026-09-28/evaluated-export-manifest.json")
    target_map = read_json("work/evidence/T98/target-reconciliation-t98.json")
    rights = read_json("work/evidence/T98/rights-inheritance-and-base-decision.json")
    t96 = read_json("work/evidence/T96/freeze-summary.json")
    archive = read_json("work/evidence/T97/archive-member-inventory.json")
    blender_350 = read_json("work/evidence/T97/blender-tool.json")
    blender_522 = read_json("work/evidence/T97/blender-tool-current.json")
    prior_runtime = read_json("work/evidence/T98/resume-2026-09-28/runtime-attestation.json")

    hdiutil = subprocess.run(["/usr/bin/hdiutil", "info", "-plist"], capture_output=True, check=True)
    disk_info = plistlib.loads(hdiutil.stdout)
    mounted_images = []
    for image in disk_info.get("images", []):
        entities = image.get("system-entities", [])
        if any(entity.get("mount-point") == "/Volumes/Blender" for entity in entities):
            mounted_images.append({
                "imagePath": image.get("image-path"),
                "mountPoint": "/Volumes/Blender",
                "deviceEntries": [entity.get("dev-entry") for entity in entities],
            })

    current_blender = Path("/Volumes/Blender/Blender.app/Contents/MacOS/Blender")
    bundle_info = plistlib.loads(Path("/Volumes/Blender/Blender.app/Contents/Info.plist").read_bytes())
    recorded_dmg = Path(blender_350["temporaryPath"])
    mounted_image = mounted_images[0] if len(mounted_images) == 1 else None
    mounted_image_sha = sha256(recorded_dmg) if recorded_dmg.is_file() else None
    current_exe_sha = sha256(current_blender) if current_blender.is_file() else None

    raw_objects = raw_inventory["representativeSample"]["objects"]
    raw_by_name = {row["sourceObjectLocator"]["objectIdName"]: row for row in raw_objects}
    evaluated_by_name = {row["objectName"]: row for row in export["sample"]["objects"]}
    targets_by_exact_candidate: dict[str, list[dict]] = defaultdict(list)
    for target in target_map["targets"]:
        for candidate in target.get("zAnatomyObjectNameCandidates", []):
            targets_by_exact_candidate[candidate["objectLabel"]].append(target)

    shared_groups: dict[str, list[str]] = defaultdict(list)
    for row in raw_objects:
        shared_groups[row.get("dataPointer")].append(row["sourceObjectLocator"]["objectIdName"])
    shared_groups = {key: names for key, names in shared_groups.items() if key and len(names) > 1}
    shared_names = {name: names for names in shared_groups.values() for name in names}

    object_rows = []
    for frozen in freeze["objects"]:
        locator = frozen["sourceObjectLocator"]
        name = locator["objectIdName"]
        raw = raw_by_name.get(name)
        evaluated = evaluated_by_name.get(name)
        if raw is None or evaluated is None:
            raise SystemExit(f"Frozen sample entry missing from existing evidence: {name}")
        targets = targets_by_exact_candidate.get(name, [])
        suffix = name.rsplit(".", 1)[1] if "." in name else None
        side_collection_labels = sorted({
            part
            for path in raw.get("collectionPaths", [])
            for part in path
            if part.startswith("Left ") or part.startswith("Right ")
        })
        object_rows.append({
            "objectName": name,
            "role": evaluated.get("role"),
            "frozenLocator": locator,
            "dataKind": raw.get("dataKind"),
            "dataBlockName": raw.get("dataBlockName"),
            "parentObjectName": raw.get("parentObjectName"),
            "collectionPaths": raw.get("collectionPaths", []),
            "literalNameSuffix": suffix,
            "sideCollectionLabels": side_collection_labels,
            "sideConclusion": "unresolved; source labels/collection tags and transform signs are observations, not an independently linked side record",
            "serializedWorldLinearDeterminant": raw.get("serializedObjectMatrixLinearDeterminant"),
            "sharedMeshDataGroupByExistingInventory": shared_names.get(name, []),
            "evaluatedTrianglesFromPriorT98Export": evaluated.get("evaluatedMeshCounts", {}).get("triangles"),
            "evaluatedGeometrySha256FromPriorT98Export": evaluated.get("evaluatedGeometrySha256"),
            "exactUpstreamObjectId": None,
            "exactUpstreamFmaFjBp3dId": None,
            "exactUpstreamSourceFamily": None,
            "objectToRightsFamilyMembership": "unresolved; collection hierarchy is not source/license ancestry",
            "lexicalTa2TargetCandidatesOnly": [
                {
                    "targetId": target["targetId"],
                    "semanticKind": target.get("semanticKind"),
                    "latin": target.get("latin"),
                    "english": target.get("english"),
                    "identityStatus": target.get("identityStatus"),
                    "note": "TA2 target ID is a terminology target, not a mesh/member ID; this row is name matching only.",
                }
                for target in targets
            ],
            "localUseRights": "held_pending_file_level_reconciliation",
            "publicRedistributionRights": "held",
            "humanReview": "not_performed",
            "learnerBinding": "none",
        })

    region_rows = []
    for row in target_map["freeze"]["regionSummary"]:
        region_rows.append({
            "regionId": row["regionId"],
            "regionLabelKo": row["labelKo"],
            "primaryTargets": row["primaryTargetRecords"],
            "membershipTargets": row["membershipTargetRecords"],
            "zAnatomyNameCandidates": row["targetsWithZAnatomyNameCandidate"],
            "bodyParts3dLexicalCandidates": row["targetsWithPriorBp3dLexicalCandidate"],
            "exactTargetSourceJoins": row["targetsWithExactSourceIdentity"],
            "targetGeometryMappedBeforeExactIdentity": row["targetsWithEvaluatedGeometry"],
        })

    archive_files = [member for member in archive["members"] if member.get("kind") == "file"]
    startup_member = next(member for member in archive_files if member["archivePath"].endswith("/Startup.blend"))
    text_files = [
        "atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/__init__.py",
        "atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Anatomy-shortcuts.py",
        "atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Anatomy_Bright.xml",
        "atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Anatomy_Dark.xml",
    ]
    id_pattern = re.compile(r"\b(?:FJ\d{4}|FMA\d+)\b")
    text_scan = []
    for relative in text_files:
        body = (ROOT / relative).read_text(encoding="utf-8", errors="replace")
        ids = sorted(set(id_pattern.findall(body)))
        matched_names = sorted({row["objectName"] for row in object_rows if row["objectName"] in body})
        text_scan.append({
            "path": relative,
            "sha256": sha256(ROOT / relative),
            "fmaOrFjIdentifierTokenCount": len(ids),
            "fmaOrFjIdentifierTokens": ids[:100],
            "frozenObjectLabelStringMatches": matched_names,
            "interpretation": "local script/theme search only; not an inspection or reparse of Startup.blend and not proof that the binary contains no custom properties",
        })

    source_hash_paths = [
        "work/evidence/T50/scene-contract.md",
        "work/reports/T69.md",
        "work/evidence/T69/assessment.json",
        "work/evidence/T69/diagnostic.json",
        "work/evidence/T96/freeze-summary.json",
        "work/evidence/T97/archive-acquisition.json",
        "work/evidence/T97/archive-member-inventory.json",
        "work/evidence/T97/blender-tool.json",
        "work/evidence/T97/blender-tool-current.json",
        "work/evidence/T98/representative-sample-freeze.json",
        "work/evidence/T98/blender-raw-object-inventory.json",
        "work/evidence/T98/target-reconciliation-t98.json",
        "work/evidence/T98/rights-inheritance-and-base-decision.json",
        "work/evidence/T98/resume-2026-09-28/evaluated-export-manifest.json",
        "work/evidence/T98/resume-2026-09-28/runtime-attestation.json",
    ]

    target_count = target_map["freeze"]["canonicalConceptTargetRecords"]
    z_candidates = target_map["candidateTally"]["targetsWithZAnatomyObjectNameCandidates"]
    bp_candidates = target_map["candidateTally"]["targetsWithPriorT96Bp3dLexicalCandidate"]
    manifest_runtime = export["runtime"]
    result = {
        "schemaVersion": "1.0.0",
        "task": "T98",
        "unit": "resolve-frame-unit-pose-side-rights-lineage-and-base-comparison",
        "observedAt": datetime.now().astimezone().isoformat(),
        "status": "partial_existing_metadata_gate_unresolved",
        "priorInventoryAndExportReused": True,
        "noBlenderLaunchSourceDownloadInventoryRerunOrExporterRerun": True,
        "runtimeProvenance": {
            "mountedRuntime": {
                "path": str(current_blender),
                "bundleVersion": bundle_info.get("CFBundleShortVersionString"),
                "bundleBuildVersion": bundle_info.get("CFBundleVersion"),
                "priorObservedRuntimeVersion": manifest_runtime["runtimeVersion"],
                "bytes": current_blender.stat().st_size if current_blender.is_file() else None,
                "sha256": current_exe_sha,
                "matchesPriorT98ExecutableReceipt": current_exe_sha == manifest_runtime["binarySha256"],
            },
            "mountedImageObservation": mounted_image,
            "T97Blender350DownloadReceipt": {
                "receiptPath": "work/evidence/T97/blender-tool.json",
                "version": blender_350["version"],
                "url": blender_350["url"],
                "finalUrl": blender_350["finalUrl"],
                "downloadedAt": blender_350["downloadedAt"],
                "temporaryPath": blender_350["temporaryPath"],
                "recordedBytes": blender_350["downloadedBytes"],
                "recordedSha256": blender_350["sha256"],
                "currentImageExists": recorded_dmg.is_file(),
                "currentImageBytes": recorded_dmg.stat().st_size if recorded_dmg.is_file() else None,
                "currentImageSha256": mounted_image_sha,
                "mountedImagePathMatchesReceiptPath": bool(mounted_image and mounted_image["imagePath"] == blender_350["temporaryPath"]),
                "currentImageHashMatchesReceipt": mounted_image_sha == blender_350["sha256"],
                "official3_5_0ChecksumPresentInExistingReceipt": "officialSha256" in blender_350,
            },
            "T97Blender522OfficialReceipt": {
                "receiptPath": "work/evidence/T97/blender-tool-current.json",
                "version": blender_522["version"],
                "dmgSha256": blender_522["sha256"],
                "officialDmgChecksumMatched": blender_522.get("sha256MatchesOfficial"),
                "matchesMountedBlenderVersion": blender_522["version"] == manifest_runtime["runtimeVersion"],
                "authenticatesMountedBlender350Image": False,
            },
            "codeSignature": prior_runtime["codeSignature"],
            "assessment": {
                "artifactLineageToRecordedT97Blender350Download": "established_by_mount_path_and_matching_local_dmg_hash",
                "officialPublisherAndPackageIntegrity": "unresolved; the existing Blender 3.5.0 receipt has no recorded official checksum and the existing codesign verification failed",
                "runtimePublisherProvenanceVerified": False,
                "retain5_2_2MismatchFact": True,
                "retainInvalidSignatureFact": True,
                "productionBasePermissionGranted": False,
            },
        },
        "frameUnitPoseAndLaterality": {
            "zAnatomySourceFrame": manifest_runtime["sourceCoordinateFrame"],
            "sourceSceneUnitPreferences": manifest_runtime["unitSettings"],
            "sourceDeclaredPhysicalUnit": manifest_runtime["unitSettings"].get("sourceDeclaredPhysicalUnit"),
            "sourceFrameRegistration": manifest_runtime["sceneFrameRegistration"],
            "sourceFrameStartEndAndCurrent": {
                "start": manifest_runtime["sceneFrameStart"],
                "end": manifest_runtime["sceneFrameEnd"],
                "current": manifest_runtime["sceneCurrentFrame"],
            },
            "referenceRestPoseId": manifest_runtime["referenceRestPoseId"],
            "armatureDatablockCount": manifest_runtime["armatureDatablockCount"],
            "T50T69FrameContract": {
                "source": "BodyParts3D Release 4 only",
                "transform": "[x,y,z] mm -> [x,z,-y] m; x sign preserved; no mirroring",
                "T69Scope": "85/85 BodyParts3D bounds and 17 target OBJ-to-GLB vertex values validated internally; not a Z-Anatomy registration or anatomy approval",
            },
            "compatibilityConclusion": "no source-backed Z-Anatomy-to-BodyParts3D frame or unit transform is present in the reviewed evidence; the T50/T69 transform was not applied",
            "lateralityConclusion": "literal object suffixes and Left/Right collection labels are observations only; T69's x-sign rule applies to BodyParts3D R4 and cannot validate Z-Anatomy laterality",
        },
        "exactObjectLineageAndRights": {
            "frozenObjectCount": len(object_rows),
            "anatomicalObjectCount": sum(row["role"] != "non_anatomical_helper" for row in object_rows),
            "helperObjectCount": sum(row["role"] == "non_anatomical_helper" for row in object_rows),
            "exactUpstreamObjectIdsFoundInExistingT98Records": 0,
            "exactFMAFJBp3dSourceIdsFoundInExistingT98Records": 0,
            "exactObjectToRightsFamilyLinksFound": 0,
            "recordsExamined": [
                "T98 representative-sample-freeze.json",
                "T98 blender-raw-object-inventory.json representativeSample.objects",
                "T98 evaluated-export-manifest.json sample.objects",
                "T98 target-reconciliation-t98.json target name candidates",
                "T97 archive-member-inventory.json",
                "T97 pinned local addon/theme text files (read-only static search)",
            ],
            "scopeLimit": "No Startup.blend re-open, custom-property reparse, full inventory rerun or exporter rerun. Existing records expose file offsets, names, parents and classification collections, but not an exact upstream source ID or rights-family member crosswalk.",
            "archiveMembers": [
                {"path": member["archivePath"], "kind": member["kind"], "sha256": member.get("sha256"), "crc32": member.get("crc32")}
                for member in archive_files
            ],
            "pinnedReadmeRightsEvidence": {
                "source": rights["sources"][0],
                "groups": rights["zAnatomyReadmeRightsGroups"],
                "perObjectMembershipConclusion": "none of the 12 exact sample objects can be assigned to the general or exception families from the reviewed object/collection metadata; all remain held",
            },
            "staticTextMetadataSearch": text_scan,
            "objects": object_rows,
            "rightsState": {
                "sourceOnly": True,
                "localUseRights": "held_pending_file_level_reconciliation",
                "publicRedistribution": "held",
                "humanReview": "not_performed",
                "canonicalMappingAdded": False,
                "learnerBindingAdded": False,
            },
        },
        "wholeBodyCoverageCandidateComparison": {
            "targetDenominator": {
                "canonicalConceptTargetRecords": t96["frozenTargets"],
                "regionMembershipRows": t96["productRegionMemberships"],
                "wholeBodyIndividualMuscleDenominator": t96["wholeBodyIndividualMuscleDenominator"],
                "targetKinds": t96["targetKinds"],
            },
            "ZAnatomy": {
                "archiveEntries": target_map["sourceDenominators"]["zAnatomyArchiveEntries"],
                "files": target_map["sourceDenominators"]["zAnatomyArchiveFiles"],
                "blendFiles": target_map["sourceDenominators"]["zAnatomyBlendFiles"],
                "serializedObjects": target_map["sourceDenominators"]["zAnatomySerializedObjects"],
                "meshDatablocks": target_map["sourceDenominators"]["zAnatomyUniqueMeshDatablocks"],
                "collections": target_map["sourceDenominators"]["zAnatomyCollections"],
                "curves": raw_inventory["denominators"]["curveDatablocks"],
                "lexicalNameCandidates": z_candidates,
                "lexicalCandidateRate": round(z_candidates / target_count, 4),
                "exactTargetObjectJoins": target_map["sourceDenominators"]["exactTa2ToZAnatomyObjectTargetJoins"],
                "exactTargetGeometryMappings": 0,
                "sampleTechnicalQuality": {
                    "evaluatedAnatomicalObjects": export["export"]["meshCount"],
                    "triangles": export["counts"]["evaluatedTriangles"],
                    "outputBytes": export["export"]["bytes"],
                    "outputSha256": export["export"]["sha256"],
                    "elapsedSecondsForSampleOpenExportAndPreview": export["performance"]["sourceOpenAndExportAndPreviewSeconds"],
                    "maxRssBytesForSampleProcess": export["performance"]["maxRssReportedByResourceBytes"],
                    "qualityLimit": "sample-level evaluated export; no full-body coverage/quality/cost conclusion",
                },
            },
            "BodyParts3dR4": {
                "existingCacheFiles": target_map["sourceDenominators"]["bp3dExistingCacheFileCount"],
                "existingCacheBytes": target_map["sourceDenominators"]["bp3dExistingCacheBytes"],
                "lexicalCandidates": bp_candidates,
                "lexicalCandidateRate": round(bp_candidates / target_count, 4),
                "exactTa2ToFmaFjJoins": target_map["sourceDenominators"]["exactTa2ToBp3dFmaOrFjTargetJoins"],
                "frameQuality": "T50/T69 verified BodyParts3D R4 subset frame/transform only; not whole-body coverage and not a Z-Anatomy transform",
                "fileAndRightsLimit": "current DB page and legacy OBJ headers differ in stated license; T98 does not resolve per-file scope",
            },
            "byRegion": region_rows,
            "comparisonResult": "candidate-count advantage is lexical only (Z-Anatomy 430/542; BodyParts3D 236/542). Both exact TA2-to-source target join counts remain 0. T96 remains 542 target records / 563 memberships with individual-muscle denominator null. No whole-body production coverage is evidenced.",
        },
        "costAndBaseDecision": {
            "ZAnatomyObserved": {
                "scope": "frozen 11-anatomy-object sample only",
                "sourceArchiveBytes": archive["archiveBytes"],
                "sourceBlendUncompressedBytes": startup_member["uncompressedBytes"],
                "sourceBlendCompressedMemberBytes": startup_member["compressedBytes"],
                "evaluatedGlbBytes": export["export"]["bytes"],
                "evaluatedTriangles": export["counts"]["evaluatedTriangles"],
                "sampleElapsedSeconds": export["performance"]["sourceOpenAndExportAndPreviewSeconds"],
                "sampleMaxRssBytes": export["performance"]["maxRssReportedByResourceBytes"],
                "armatureDatablocks": manifest_runtime["armatureDatablockCount"],
                "animationReadiness": "not_established; no verified rest pose or rig and sample is static",
            },
            "BodyParts3dObserved": {
                "scope": "existing cache aggregate and previously validated subsets only",
                "rawCacheFiles": target_map["sourceDenominators"]["bp3dExistingCacheFileCount"],
                "rawCacheBytes": target_map["sourceDenominators"]["bp3dExistingCacheBytes"],
                "equivalentWholeBodyExportTimingOrRenderCost": None,
                "equivalentWholeBodyTriangleCount": None,
            },
            "costsDirectlyComparable": False,
            "reason": "one measure is a Z-Anatomy 11-object Blender source-open/export/preview run; the other is a BodyParts3D cache byte/file total and selected-subset validation. They do not measure the same scope or pipeline stage.",
            "productionBase": None,
            "baseStatus": "undecided",
            "selectionReason": "runtime publisher integrity, declared unit/frame/reference pose, exact object identity and rights ancestry, whole-body surface coverage and comparable cost remain unresolved",
            "motionStatus": "not_ready",
        },
        "inputHashes": {
            relative: sha256(ROOT / relative)
            for relative in source_hash_paths
        },
        "nextUnit": "resolve-frame-unit-pose-side-rights-lineage-and-base-comparison",
        "nextTaskStarted": False,
    }
    output = HERE / "existing-metadata-assessment.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(output.relative_to(ROOT)),
        "mountedImageMatchesRecordedT97Blender350Dmg": bool(mounted_image and mounted_image["imagePath"] == blender_350["temporaryPath"] and mounted_image_sha == blender_350["sha256"]),
        "runtimePublisherIntegrityVerified": result["runtimeProvenance"]["assessment"]["runtimePublisherProvenanceVerified"],
        "frozenObjects": len(object_rows),
        "exactObjectIds": result["exactObjectLineageAndRights"]["exactUpstreamObjectIdsFoundInExistingT98Records"],
        "exactFmaFjBp3dIds": result["exactObjectLineageAndRights"]["exactFMAFJBp3dSourceIdsFoundInExistingT98Records"],
        "zNameCandidates": z_candidates,
        "bp3dLexicalCandidates": bp_candidates,
        "productionBase": result["costAndBaseDecision"]["productionBase"],
        "nextUnit": result["nextUnit"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
