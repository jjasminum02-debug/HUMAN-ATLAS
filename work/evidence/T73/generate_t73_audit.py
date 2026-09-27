#!/usr/bin/env python3
"""Reproduce the T73 BodyParts3D R4 root-routing and target-source audit.

This is an audit-only tool. It reads the frozen R4 metadata and historic T50–T72
manifests, then writes evidence under work/evidence/T73. It does not download,
convert, bind, or alter meshes and does not generate canonical learner IDs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
META = ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"
OUT = ROOT / "work/evidence/T73"
SOURCE_MANIFEST = ROOT / "atlas-data/manifests/bodyparts3d-r4-source-manifest-t51.json"
T70_SCOPE = ROOT / "atlas-data/manifests/bodyparts3d-r4-t70/scope-inventory.json"
T70_INTEGRATION = ROOT / "atlas-data/manifests/bodyparts3d-r4-t70/integration-manifest.json"
T71_INTEGRATION = ROOT / "atlas-data/manifests/bodyparts3d-r4-t71/integration-manifest.json"
T72_INTEGRATION = ROOT / "atlas-data/manifests/bodyparts3d-r4-t72/integration-extension.json"
T72_VALIDATION = ROOT / "work/evidence/T72/validation.json"
T71_COVERAGE = ROOT / "work/evidence/T71/coverage-recalculation.json"
T58_REPORT = ROOT / "work/reports/T58.md"
T58_CAPTURES = [
    ROOT / "work/evidence/T58/head-front.png",
    ROOT / "work/evidence/T58/head-side.png",
    ROOT / "work/evidence/T58/whole-back.png",
]
TOOL_PATH = ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py"

TARGETS: list[dict[str, Any]] = [
    {
        "task": "T74",
        "targetSet": "bilateral-skull-visual-silhouette",
        "regionIds": ["head"],
        "tree": "partofCompoundElements",
        "conceptIds": ["FMA52788", "FMA52789", "FMA52738", "FMA52739", "FMA52892", "FMA52893", "FMA53649", "FMA53650", "FMA53647", "FMA53648"],
        "scopeNote": "Bounded bilateral visual silhouette subset, not the complete skull inventory.",
    },
    {
        "task": "T75",
        "targetSet": "deltoid-side-specific-parts",
        "regionIds": ["shoulder-scapular", "upper-limb"],
        "tree": "isaCompoundElements",
        "conceptIds": ["FMA34680", "FMA34681", "FMA34682", "FMA34683", "FMA34684", "FMA34685"],
        "sourceContextConceptIds": ["FMA34676", "FMA34677", "FMA34678", "FMA34679"],
        "scopeNote": "Three named deltoid parts on each side; zone/generic part contexts are retained separately and are not extra mesh targets.",
    },
    {
        "task": "T75",
        "targetSet": "latissimus-dorsi-alternate-source-gap",
        "regionIds": ["back", "shoulder-scapular", "upper-limb"],
        "tree": "none-in-BodyParts3D-R4",
        "conceptIds": [],
        "queryNames": ["latissimus", "dorsi"],
        "scopeNote": "Required target row; no R4 FMA concept, FJ, or member is inferred. Separate alternate-source research is T93.",
    },
    {
        "task": "T76",
        "targetSet": "pelvic-floor-muscle-group-and-side-parts",
        "regionIds": ["pelvis-perineum"],
        "tree": "isaCompoundElements",
        "conceptIds": ["FMA19089", "FMA19090", "FMA19092", "FMA19088", "FMA45854", "FMA45855", "FMA45858", "FMA45859", "FMA46443", "FMA46444"],
        "scopeNote": "Ten source concepts, including group/whole concepts and explicit side concepts; existing coccygeus members are reuse-only. Not a full perineal inventory.",
    },
    {
        "task": "T92",
        "targetSet": "trapezius-region-visual-context",
        "regionIds": ["back", "shoulder-scapular"],
        "tree": "isaCompoundElements",
        "conceptIds": ["FMA32529", "FMA32555", "FMA32556", "FMA32557", "FMA33581", "FMA33583", "FMA33584", "FMA33585", "FMA33586", "FMA33587"],
        "scopeNote": "Bounded whole/part/side context for visual continuity across back and shoulder; one shared FJ node per source element.",
    },
]

EXPECTED_T74_NEW_FJ = {"FJ3274", "FJ3386", "FJ3281", "FJ3392", "FJ3287", "FJ3375", "FJ3269", "FJ3378", "FJ3272"}
EXPECTED_T75_DELTOID_FJ = {"FJ1467", "FJ1467M", "FJ1468", "FJ1468M", "FJ1513", "FJ1513M"}
EXPECTED_T76_FJ = {"FJ1453M", "FJ1457M", "FJ1458M", "FJ2544", "FJ2545", "FJ2546", "FJ2549", "FJ2550", "FJ2551", "FJ1449M", "FJ2542", "FJ2547"}
EXPECTED_T92_FJ = {"FJ1520", "FJ1520M", "FJ1554", "FJ1554M", "FJ1521", "FJ1521M"}

METADATA_URLS = {
    "isaConcepts": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_parts_list_e.txt",
    "partofConcepts": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/partof_parts_list_e.txt",
    "isaInclusion": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_inclusion_relation_list.txt",
    "partofInclusion": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/partof_inclusion_relation_list.txt",
    "isaCompoundElements": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_element_parts.txt",
    "partofCompoundElements": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/partof_element_parts.txt",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f, delimiter="\t"))[1:]


def load_module():
    spec = importlib.util.spec_from_file_location("ingest_bodyparts3d_r4", TOOL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load routing implementation: {TOOL_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def source_side(name: str) -> str:
    lower = name.lower()
    if "right" in lower:
        return "right"
    if "left" in lower:
        return "left"
    return "midline_or_unspecified_in_exact_label"


def build_audit() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    module = load_module()
    tables = module.load_tables(META)
    routes, muscle_files, bone_files = module.region_map(ROOT, tables)

    concept_name_isa = {r[0]: r[2] for r in tables["isaConcepts"]}
    concept_name_partof = {r[0]: r[2] for r in tables["partofConcepts"]}
    isa_edges = module.adjacency(tables["isaInclusion"])
    partof_edges = module.adjacency(tables["partofInclusion"])
    all_bone_concepts = module.closure(["FMA5018"], isa_edges)
    all_muscle_concepts = module.closure(["FMA5022"], isa_edges)

    t51_manifest = load_json(ROOT / "atlas-data/manifests/bodyparts3d-r4-source-manifest-t51.json")
    t51_regions = {r["productCategoryId"]: r for r in t51_manifest["productRegions"]}
    t70_scope = load_json(T70_SCOPE)
    t70 = load_json(T70_INTEGRATION)
    t71 = load_json(T71_INTEGRATION)
    t72 = load_json(T72_INTEGRATION)
    t72_validation = load_json(T72_VALIDATION)
    assets70 = {a["sourceElementFileId"]: a for a in t70["assets"]}
    assets71 = {a["sourceElementFileId"]: a for a in t71["assets"]}
    assets72 = {a["sourceElementFileId"]: a for a in t72["assets"]}
    cache_index = load_json(ROOT / "atlas-data/source-cache/bodyparts3d-r4/cache-index.json")
    cache = {r["sourceFileId"]: r for r in cache_index["files"]}
    public_redistribution_state = t72.get("publicRedistribution", t71.get("publicRedistribution", t70.get("publicRedistribution")))

    # Confirm historic manifests are append-only supplements and preserve their denominators.
    assert len(assets70) == 493
    assert len(assets71) == 502 and len(assets72) == 504
    assert t70["counts"]["uniqueSourceNodes"] == 493
    assert t70["counts"]["historicalPackageMemberships"] == 495
    first_pass = t70_scope["productFirstPassMinimum"]
    first_pass_remaining = t72_validation["firstPassResidualCountAfterT71AndT72"]
    bone_gap_count = t72_validation["boneRootResidualCountAfterT71AndT72"]
    original_t70_bone_missing_count = t72_validation["T70BoneRootMissingSourceCount"]

    metadata_rows: dict[str, list[list[str]]] = {}
    metadata_record = {r["logicalName"]: r for r in t51_manifest["source"]["metadataFiles"]}
    metadata_provenance: list[dict[str, Any]] = []
    for logical, filename in module.METADATA_FILES.items():
        p = META / filename
        rows = read_rows(p)
        expected = metadata_record[logical]
        actual_hash = sha256(p)
        if actual_hash != expected["sha256"]:
            raise ValueError(f"source metadata hash drift: {filename}")
        metadata_rows[logical] = rows
        metadata_provenance.append({
            "logicalName": logical,
            "path": p.relative_to(ROOT).as_posix(),
            "url": METADATA_URLS[logical],
            "edition": "BodyParts3D Release 4.0 metadata; official endpoint path is LATEST",
            "retrievedOn": expected["retrievedOn"],
            "rowsExcludingHeader": len(rows),
            "bytes": p.stat().st_size,
            "sha256": actual_hash,
            "openedSource": True,
        })

    # Root closures are reproduced by the production R4 routing function, then compared to T51/T70.
    region_rows = []
    category_lookup = {c["id"]: c for c in module.PRODUCT_CATEGORIES}
    for region_id, route in routes.items():
        region = t51_regions[region_id]
        root_fjs = set(muscle_files[region_id]) | set(bone_files[region_id])
        assigned = {fid: a for fid, a in assets70.items() if region_id in a.get("productRegionIdsFromHistoricalPackages", [])}
        visible = {fid: a for fid, a in assigned.items() if a.get("learnerDefaultVisible") is True}
        hidden = {fid: a for fid, a in assigned.items() if a.get("learnerDefaultVisible") is False}
        held = {fid: a for fid, a in assigned.items() if a.get("holdReasons")}
        source_only = {fid: a for fid, a in assigned.items() if a.get("learnerPickState") == "source_only_unbound"}
        linked = {fid: a for fid, a in assigned.items() if a.get("existingLearnerStableIds")}
        human_pending = {fid: a for fid, a in assigned.items() if a.get("humanAnatomyReviewed") is not True}
        region_rows.append({
            "regionId": region_id,
            "labelKo": category_lookup[region_id]["labelKo"],
            "routingRoots": route["sourceRoots"],
            "sourceConceptCounts": {"muscle": len(route["muscleConceptIds"]), "bone": len(route["boneConceptIds"])},
            "rootCandidateFj": {"muscle": len(muscle_files[region_id]), "bone": len(bone_files[region_id]), "uniqueUnion": len(root_fjs)},
            "T51RootExpectedUniqueFj": region["counts"]["sourceRootExpectedSourceElementFileIdsUniqueWithinCategory"],
            "T51FrozenExpectedUniqueFjIncludingExistingBindingSupplement": region["counts"]["expectedSourceElementFileIdsUniqueWithinCategory"],
            "T51ExistingBindingSourceElementSupplementCount": region["counts"]["existingProductBindingSourceElementFilesSupplement"],
            "T70HistoricalRegionAssignedUniqueFj": len(assigned),
            "T70AssignedAndDefaultVisible": len(visible),
            "T70AssignedButHidden": len(hidden),
            "T70AssignedWithAnyHold": len(held),
            "T70PublicRedistributionHeld": len(assigned) if "held" in str(public_redistribution_state) else None,
            "T70HumanReviewPending": len(human_pending),
            "T70SourceOnlyUnbound": len(source_only),
            "T70WithLearnerBinding": len(linked),
            "T70AssignedOutsideCurrentRootCandidateSet": sorted(set(assigned) - root_fjs),
            "T70AssignedOutsideCurrentRootCandidateCount": len(set(assigned) - root_fjs),
            "CurrentRootCandidateNotAssignedByT70": sorted(root_fjs - set(assigned)),
            "CurrentRootCandidateNotAssignedByT70Count": len(root_fjs - set(assigned)),
            "rootCandidateCachedT50T72": len(root_fjs & set(assets72)),
            "rootCandidateNotInT50T72Packages": len(root_fjs - set(assets72)),
            "denominatorInterpretation": "package/routing inventory only; not canonical anatomy or whole-body coverage",
        })

    regional_muscle_concepts = set().union(*(route["muscleConceptIds"] for route in routes.values()))
    regional_bone_concepts = set().union(*(route["boneConceptIds"] for route in routes.values()))
    regional_muscle_fj = set().union(*muscle_files.values())
    regional_bone_fj = set().union(*bone_files.values())

    # Exact source concept -> ELEMENT rows, plus historic acquisition/visibility/rights status.
    source_by_tree = {
        "isaCompoundElements": metadata_rows["isaCompoundElements"],
        "partofCompoundElements": metadata_rows["partofCompoundElements"],
    }
    names_by_tree = {
        "isaCompoundElements": concept_name_isa,
        "partofCompoundElements": concept_name_partof,
    }
    representations_by_tree = {
        "isaCompoundElements": {r[0]: r[1] for r in metadata_rows["isaConcepts"]},
        "partofCompoundElements": {r[0]: r[1] for r in metadata_rows["partofConcepts"]},
    }
    region_fma = {
        region_id: set(route["muscleConceptIds"]) | set(route["boneConceptIds"])
        for region_id, route in routes.items()
    }
    target_rows = []
    source_context_rows = []
    target_counts: dict[str, dict[str, Any]] = {}
    all_target_members: dict[str, set[str]] = defaultdict(set)
    for target in TARGETS:
        concept_ids = target["conceptIds"]
        tree = target["tree"]
        rows_by_concept: dict[str, list[list[str]]] = defaultdict(list)
        if tree in source_by_tree:
            for row in source_by_tree[tree]:
                if row[0] in concept_ids:
                    rows_by_concept[row[0]].append(row)
        target_members: set[str] = set()
        for cid in concept_ids:
            source_name = names_by_tree[tree].get(cid, "unknown_in_tree")
            member_rows = sorted({(r[1], r[2]) for r in rows_by_concept.get(cid, [])})
            members = []
            for row_name, fj in member_rows:
                target_members.add(fj)
                all_target_members[target["task"]].add(fj)
                asset = assets72.get(fj)
                cache_row = cache.get(fj)
                if asset:
                    acquired_state = "acquired_in_T50_T72_manifest"
                    default_visibility = "visible" if asset.get("learnerDefaultVisible") else "hidden"
                    hold_reasons = asset.get("holdReasons", [])
                    rights_state = "held_pending_file_level_reconciliation" if "held" in str(public_redistribution_state) or any("redistribution" in reason for reason in hold_reasons) else "not_marked_held_in_manifest"
                    review_state = "human_reviewed" if asset.get("humanAnatomyReviewed") else "not_human_reviewed"
                    linkage = "learner_linked" if asset.get("existingLearnerStableIds") else "source_only_unbound"
                    member_hash = asset.get("sourceSha256")
                    member_path = cache_row.get("cacheRelativePath") if cache_row else None
                else:
                    acquired_state = "not_acquired_in_T50_T72; no download attempt recorded"
                    default_visibility = "not_applicable_not_acquired"
                    hold_reasons = []
                    rights_state = "unresolved_not_acquired"
                    review_state = "not_reviewed"
                    linkage = "not_linked"
                    member_hash = None
                    member_path = None
                members.append({
                    "sourceElementFileId": fj,
                    "sourceElementName": row_name,
                    "exactSourceHash": member_hash,
                    "cachedSourcePath": member_path,
                    "sourcePackageReferences": asset.get("packageReferences", []) if asset else [],
                    "acquisitionState": acquired_state,
                    "localDefaultVisibility": default_visibility,
                    "rightsState": rights_state,
                    "holdReasons": hold_reasons,
                    "semanticState": linkage,
                    "humanAnatomyReview": review_state,
                    "sameSourceNodeAcrossRegions": True,
                })
            in_declared_region = [r for r in target["regionIds"] if cid in region_fma.get(r, set())]
            target_rows.append({
                "task": target["task"],
                "targetSet": target["targetSet"],
                "sourceConceptId": cid,
                "sourcePreferredName": source_name,
                "sourceRepresentationId": representations_by_tree[tree].get(cid),
                "sideFromExactSourceLabel": source_side(source_name),
                "declaredProductRegions": target["regionIds"],
                "insideExistingProductRootClosure": bool(in_declared_region),
                "matchingDeclaredRootRegions": in_declared_region,
                "sourceTree": tree,
                "exactMembers": members,
                "memberMissingReason": "No exact ELEMENT row for this concept in the selected official R4 tree." if not members else None,
                "scopeNote": target["scopeNote"],
            })
        if tree not in source_by_tree and target.get("queryNames"):
            all_rows = [r for table in tables.values() for r in table]
            hits = [r for r in all_rows if any(q.lower() in "\t".join(r).lower() for q in target["queryNames"])]
            target_rows.append({
                "task": target["task"], "targetSet": target["targetSet"],
                "sourceConceptId": None, "sourcePreferredName": "latissimus dorsi",
                "sideFromExactSourceLabel": "bilateral_target_required_source_has_no_sided_concepts", "declaredProductRegions": target["regionIds"],
                "insideExistingProductRootClosure": False, "matchingDeclaredRootRegions": [],
                "sourceTree": tree, "exactMembers": [],
                "memberMissingReason": "No latissimus/dorsi string match in any of the six cached official R4 metadata tables; no source FMA/FJ/member/hash exists in this edition inventory. Not a download failure.",
                "metadataSearchQueries": target["queryNames"], "metadataSearchHitRows": hits,
                "scopeNote": target["scopeNote"],
            })
        target_counts[target["targetSet"]] = {
            "task": target["task"],
            "conceptTargetCount": len(concept_ids) if concept_ids else 1,
            "uniqueExactFjCount": len(target_members),
            "acquiredInT50T72": len(target_members & set(assets72)),
            "sourceAvailability": "metadata_members_present" if target_members else ("no_matching_source_in_R4_metadata" if not concept_ids else "metadata_member_rows_missing"),
            "notAcquiredInT50T72": len(target_members - set(assets72)) if target_members else None,
            "membersHeldForRights": sum("held" in str(public_redistribution_state) or any("redistribution" in x for x in assets72[f].get("holdReasons", [])) for f in target_members & set(assets72)),
            "membersHumanReviewPending": sum(assets72[f].get("humanAnatomyReviewed") is not True for f in target_members & set(assets72)),
            "membersDefaultHidden": sum(assets72[f].get("learnerDefaultVisible") is False for f in target_members & set(assets72)),
            "membersSourceOnlyUnbound": sum(assets72[f].get("learnerPickState") == "source_only_unbound" for f in target_members & set(assets72)),
            "membersLearnerLinked": sum(bool(assets72[f].get("existingLearnerStableIds")) for f in target_members & set(assets72)),
            "memberIds": sorted(target_members),
        }
        for context_cid in target.get("sourceContextConceptIds", []):
            context_name = concept_name_isa.get(context_cid, "unknown_in_IS-A_tree")
            context_member_rows = sorted({(r[1], r[2]) for r in metadata_rows["isaCompoundElements"] if r[0] == context_cid})
            context_members = []
            for member_name, fj in context_member_rows:
                asset = assets72.get(fj)
                context_members.append({
                    "sourceElementFileId": fj,
                    "sourceElementName": member_name,
                    "exactSourceHash": asset.get("sourceSha256") if asset else None,
                    "acquired": asset is not None,
                    "localDefaultVisibility": asset.get("learnerDefaultVisible") if asset else None,
                    "publicRedistributionState": public_redistribution_state if asset else "not_acquired_unassessed",
                    "sourceOnlyVsLearnerLinked": "learner_linked" if asset and asset.get("existingLearnerStableIds") else ("source_only_unbound" if asset else "not_linked"),
                    "humanAnatomyReviewed": bool(asset and asset.get("humanAnatomyReviewed")),
                })
            source_context_rows.append({
                "task": target["task"],
                "targetSet": target["targetSet"],
                "role": "source_context_not_additional_geometry_target",
                "sourceConceptId": context_cid,
                "sourcePreferredName": context_name,
                "sourceRepresentationId": representations_by_tree["isaCompoundElements"].get(context_cid),
                "sideFromExactSourceLabel": source_side(context_name),
                "sourceTree": "IS-A",
                "insideExistingProductRootClosure": any(context_cid in region_fma.get(r, set()) for r in target["regionIds"]),
                "exactMembers": context_members,
            })

    # Report all exact table search results for latissimus/dorsi; no fuzzy source mapping.
    latissimus_search = {}
    for logical, rows in metadata_rows.items():
        latissimus_search[logical] = [row for row in rows if "latissimus" in "\t".join(row).lower() or "dorsi" in "\t".join(row).lower()]

    head_root_bones = set(routes["head"]["boneConceptIds"])
    skull_partof = module.closure(["FMA46565"], partof_edges) & all_bone_concepts
    skull_partof_fj = {r[2] for r in metadata_rows["partofCompoundElements"] if r[0] in skull_partof}
    head_root_fj = set(bone_files["head"])
    pelvis_muscle = set(routes["pelvis-perineum"]["muscleConceptIds"])
    pelvic_targets = {"FMA19089", "FMA19090", "FMA19092", "FMA19088", "FMA45854", "FMA45855", "FMA45858", "FMA45859", "FMA46443", "FMA46444"}
    deltoid_targets = {"FMA34676", "FMA34680", "FMA34681", "FMA34682", "FMA34683", "FMA34684", "FMA34685"}
    trapezius_targets = {"FMA32529", "FMA32555", "FMA32556", "FMA32557", "FMA33581", "FMA33583", "FMA33584", "FMA33585", "FMA33586", "FMA33587"}
    all_region_muscles = set().union(*[route["muscleConceptIds"] for route in routes.values()])
    root_reproduction = {
        "method": "Imported atlas-data/tools/ingest_bodyparts3d_r4.py and invoked its region_map() against the six frozen official TSVs; no alternate root algorithm was substituted.",
        "head": {
            "configuredRoot": "FMA7154 (head), PART-OF",
            "intersectingBoneOrganConcepts": len(head_root_bones),
            "intersectingBoneOrganConceptIds": sorted(head_root_bones),
            "intersectingBoneFj": sorted(head_root_fj),
            "rightParietalPresent": "FMA52788" in head_root_bones,
            "leftParietalPresent": "FMA52789" in head_root_bones,
            "skullRootUsedForComparison": "FMA46565 (skull), PART-OF; comparison only, not a silent route replacement",
            "skullSubtreeBoneConceptCount": len(skull_partof),
            "skullSubtreeFjCount": len(skull_partof_fj),
        },
        "deltoid": {
            "conceptTargetIds": sorted(deltoid_targets),
            "intersectingExistingRegionRoots": sorted(deltoid_targets & all_region_muscles),
            "missedByAll12ExistingMuscleRoots": sorted(deltoid_targets - all_region_muscles),
        },
        "latissimus": {
            "exactSubstringSearchResultsByTable": latissimus_search,
            "conceptAndElementMatches": 0,
            "interpretation": "Edition metadata gap, not mesh-download failure; alternate source unresolved.",
        },
        "pelvicFloor": {
            "targetConceptIds": sorted(pelvic_targets),
            "targetConceptsInsidePelvisRootClosure": sorted(pelvic_targets & pelvis_muscle),
            "targetConceptsOutsidePelvisRootClosure": sorted(pelvic_targets - pelvis_muscle),
            "specificMissedBranch": "FMA19089 levator ani -> FMA19090 pubococcygeus / FMA19092 iliococcygeus and side-specific descendants; the configured pelvis roots include FMA19086 coccygeus but not the FMA19089 branch.",
        },
        "trapezius": {
            "conceptTargetIds": sorted(trapezius_targets),
            "intersectingExistingRegionRoots": sorted(trapezius_targets & all_region_muscles),
            "missedByAll12ExistingMuscleRoots": sorted(trapezius_targets - all_region_muscles),
        },
        "causeSummary": [
            "Configured source-root closures are narrow routing rules, not anatomical product-region memberships.",
            "A concept can be outside a configured region root even when exact source concept/ELEMENT rows exist elsewhere in the official source tree.",
            "An exact source row does not mean the corresponding FJ was acquired; missing cached members are not download failures because no full archive acquisition was attempted.",
            "One required target (latissimus dorsi) has no matching entry in this frozen R4 metadata edition; this is distinct from an uncached FJ.",
        ],
    }

    # Validate exact mappings promised by task specs; fail closed if source tables drift.
    task_members = {task: set().union(*(set(t["memberIds"]) for t in target_counts.values() if t["task"] == task)) for task in ("T74", "T75", "T76", "T92")}
    t74_members = set(target_counts["bilateral-skull-visual-silhouette"]["memberIds"])
    t75_members = set(target_counts["deltoid-side-specific-parts"]["memberIds"])
    t76_members = set(target_counts["pelvic-floor-muscle-group-and-side-parts"]["memberIds"])
    t92_members = set(target_counts["trapezius-region-visual-context"]["memberIds"])
    if t74_members - set(assets72) != EXPECTED_T74_NEW_FJ - set(assets72):
        raise ValueError(f"T74 expected source members drift: {sorted(t74_members)}")
    if t75_members != EXPECTED_T75_DELTOID_FJ:
        raise ValueError(f"T75 deltoid source members drift: {sorted(t75_members)}")
    if t76_members != EXPECTED_T76_FJ:
        raise ValueError(f"T76 pelvic source members drift: {sorted(t76_members)}")
    if t92_members != EXPECTED_T92_FJ:
        raise ValueError(f"T92 trapezius source members drift: {sorted(t92_members)}")
    if any(len(x["conceptIds"]) > 10 for x in TARGETS):
        raise ValueError("a bounded target batch exceeds 10 concepts")

    source_research = {
        "accessedOn": "2026-09-28",
        "primarySource": {
            "sourceId": t51_manifest["source"]["sourceId"],
            "version": t51_manifest["source"]["version"],
            "releaseDate": "2013-06-19 (official R4 update history)",
            "metadataEditionNote": "The endpoints use /LATEST/; archived local TSVs are the exact six hashes listed below. The version text is BodyParts3D R4.0; LATEST label itself is not treated as a new release number.",
            "downloadPage": t51_manifest["source"]["archiveListingUrl"],
            "readme": t51_manifest["source"]["readmeUrl"],
            "licensePage": t51_manifest["source"]["licenseUrl"],
            "officialDatabaseLicense": t51_manifest["source"]["license"],
            "meshArchiveFullDownloads": t51_manifest["source"]["meshArchives"],
            "meshArchiveAcquired": False,
            "metadataAccess": "Six official TSVs are present in the project cache and hashed; no mesh archive/download was attempted in T73.",
            "metadataFiles": metadata_provenance,
            "historicLocalMeshHeaderCaveat": "T51 recorded legacy OBJ headers claiming CC BY-SA 2.1 Japan while current official database page says CC BY 4.0; existing file-level redistribution hold remains in force.",
        },
        "alternateSourceCandidate": {
            "name": "Z-Anatomy Models of Human Anatomy",
            "officialRepository": "https://github.com/Z-Anatomy/Models-of-human-anatomy",
            "officialLicenseFile": "https://github.com/Z-Anatomy/Models-of-human-anatomy/blob/master/License.txt",
            "officialReadme": "https://github.com/Z-Anatomy/Models-of-human-anatomy/blob/master/Readme.md",
            "repositoryReadmeClaims": "Blender template includes models derived from BodyParts3D; code/content CC BY-SA 4.0; explicit third-party models include NC items.",
            "latissimusExactObjectId": None,
            "latissimusExactFilePath": None,
            "latissimusExactFileSha256": None,
            "componentLicenseResolved": False,
            "commonFrameAndRestPoseVerified": False,
            "archiveDownloaded": False,
            "decision": "candidate_only; T93 must pin a version/revision and locate the exact object and per-component rights/frame evidence before any acquisition or registration task.",
        },
        "humanAnatomyReview": "not_performed; AI metadata/source identification does not approve anatomy",
    }

    coverage = {
        "task": "T73",
        "auditDate": "2026-09-28",
        "sourceInventory": "BodyParts3D Release 4.0 six cached metadata files",
        "regionCount": len(region_rows),
        "regions": region_rows,
        "rootReproduction": root_reproduction,
        "officialSourceVsProductRootRouting": {
            "officialR4MuscleOrganDescendantConceptCount": len(all_muscle_concepts),
            "uniqueMuscleConceptsIn12ConfiguredRoots": len(regional_muscle_concepts),
            "officialMuscleConceptsOutsideAll12Roots": len(all_muscle_concepts - regional_muscle_concepts),
            "officialR4MuscleOrganDescendantFjCount": len({r[2] for r in metadata_rows["isaCompoundElements"] if r[0] in all_muscle_concepts}),
            "uniqueMuscleFjIn12ConfiguredRoots": len(regional_muscle_fj),
            "officialR4BoneOrganDescendantConceptCount": len(all_bone_concepts),
            "uniqueBoneConceptsIn12ConfiguredRoots": len(regional_bone_concepts),
            "officialBoneConceptsOutsideAll12Roots": len(all_bone_concepts - regional_bone_concepts),
            "officialR4BoneOrganDescendantFjCount": len({r[2] for r in metadata_rows["isaCompoundElements"] if r[0] in all_bone_concepts} | {r[2] for r in metadata_rows["partofCompoundElements"] if r[0] in all_bone_concepts}),
            "uniqueBoneFjIn12ConfiguredRoots": len(regional_bone_fj),
            "interpretation": "These are source hierarchy rows/unique FJ counts under current routing roots, not canonical anatomy denominators or whole-body coverage percentages.",
        },
        "historicT70Denominators": {
            "uniqueT52toT55SourceNodes": t70["counts"]["uniqueSourceNodes"],
            "T52toT55PackageMemberships": t70["counts"]["historicalPackageMemberships"],
            "T70OriginalBoneClosureMissingSourceElements": original_t70_bone_missing_count,
            "T70BoneRootGapRemainingAfterT71T72": bone_gap_count,
            "T70ProductFirstPassMinimumOriginalConceptTargetCount": len(first_pass["conceptTargets"]),
            "T70FirstPassOriginalSourceCandidateCount": t72_validation["T70FirstPassSourceCount"],
            "T71FirstPassResidual": {"value": load_json(ROOT / "work/evidence/T71/coverage-recalculation.json")["remainingProductMinimumSourceIdCount"], "of": t72_validation["T70FirstPassSourceCount"], "basis": "T71 coverage recalculation after its 9-member package"},
            "T72FirstPassResidual": {"value": first_pass_remaining, "of": len(t72_validation["exactFrozenSourceIds"]), "basis": "read from T72's recorded validation against its exact residual batch; not recomputed as whole-body coverage"},
            "separation": "The T70 bone-root gap list and the first-pass 0/11 residual are independent historical counts and are not combined.",
        },
        "T71T72Supplements": {
            "T71AddedSourceNodes": 9,
            "T71DefaultVisible": sum(a.get("learnerDefaultVisible") is True for fid, a in assets71.items() if fid not in assets70),
            "T71SourceOnlyUnbound": sum(a.get("learnerPickState") == "source_only_unbound" for fid, a in assets71.items() if fid not in assets70),
            "T72AddedSourceNodes": 11,
            "T72DefaultVisible": sum(a.get("learnerDefaultVisible") is True for fid, a in assets72.items() if fid not in assets71),
            "T72SourceOnlyUnbound": sum(a.get("learnerPickState") == "source_only_unbound" for fid, a in assets72.items() if fid not in assets71),
            "interpretation": "These supplements are historic source packages; the task-specific manifests retain opt-in/hidden display and rights/human-review holds. They are not added to T70 regional denominator counts.",
        },
        "targetSets": target_counts,
        "targetCountPolicy": "Counts are bounded visual source targets only, not a whole-body muscle/bone denominator.",
    }

    target_matrix = {
        "task": "T73",
        "revision": "T73-target-source-matrix-v1",
        "generatedBy": "work/evidence/T73/generate_t73_audit.py",
        "sourceMetadataEdition": "BodyParts3D Release 4.0 (official /LATEST/ endpoints; local hashes locked)",
        "items": target_rows,
        "sourceContextItems": source_context_rows,
        "orthogonalStatusColumns": ["sourceAvailability", "acquired", "defaultVisibility", "rightsHold", "sourceOnlyVsLearnerLinked", "humanReview"],
        "interpretation": "A field being acquired, visible, source-only, linked, held, or human-reviewed is never inferred from another field.",
    }

    validation = {
        "task": "T73",
        "result": "pass_with_visual_source_gaps",
        "checks": {
            "sixOfficialMetadataFilesHashMatchT51": True,
            "existingRegionMapFunctionExecuted": True,
            "t51RegionCount": len(t51_regions),
            "routedRegionCount": len(region_rows),
            "all12RegionsEnumerated": len(region_rows) == 12 and set(routes) == set(t51_regions),
            "headRootOnlyOneBoneReproduced": len(head_root_bones) == 1 and "FMA52788" in head_root_bones and "FMA52789" not in head_root_bones,
            "deltoidOutsideAllExistingRegionsReproduced": not (deltoid_targets & all_region_muscles),
            "latissimusAbsentFromAllSixR4Tables": not any(latissimus_search.values()),
            "levatorAniBranchExclusionReproduced": {"FMA19090", "FMA19092"}.issubset(pelvic_targets - pelvis_muscle),
            "trapeziusOutsideAllExistingRegionsReproduced": not (trapezius_targets & all_region_muscles),
            "T74Max10ConceptsAndExactMembers": len(next(t for t in TARGETS if t["targetSet"] == "bilateral-skull-visual-silhouette")["conceptIds"]) == 10 and t74_members == EXPECTED_T74_NEW_FJ | (t74_members & set(assets72)),
            "T75DeltoidSixMembers": t75_members == EXPECTED_T75_DELTOID_FJ,
            "T75SourceContextRowsRetainSameSixMembers": (
                {r["sourceConceptId"] for r in source_context_rows if r["task"] == "T75"}
                == {"FMA34676", "FMA34677", "FMA34678", "FMA34679"}
                and set().union(*(
                    {m["sourceElementFileId"] for m in r["exactMembers"]}
                    for r in source_context_rows if r["task"] == "T75"
                )) == EXPECTED_T75_DELTOID_FJ
            ),
            "T76Max10ConceptsAnd12UniqueMembers": len(next(t for t in TARGETS if t["targetSet"] == "pelvic-floor-muscle-group-and-side-parts")["conceptIds"]) == 10 and t76_members == EXPECTED_T76_FJ,
            "T92Max10ConceptsAndSixMembers": len(next(t for t in TARGETS if t["targetSet"] == "trapezius-region-visual-context")["conceptIds"]) == 10 and t92_members == EXPECTED_T92_FJ,
            "T70OriginalBoneGapCountAndResidualAreSeparate": original_t70_bone_missing_count == 35 and bone_gap_count == 26,
            "T70FirstPassResidualMetricSeparatelyRecorded": first_pass_remaining == 0 and len(t72_validation["exactFrozenSourceIds"]) == 11 and t72_validation["T70FirstPassSourceCount"] == 20,
            "noMeshDownloadOrModification": True,
            "noCanonicalOrLearnerBindingCreated": True,
            "noHumanReviewPromotion": True,
        },
        "evidenceInputSha256": {
            p.relative_to(ROOT).as_posix(): sha256(p)
            for p in [SOURCE_MANIFEST, T70_SCOPE, T70_INTEGRATION, T71_INTEGRATION, T72_INTEGRATION, T72_VALIDATION, TOOL_PATH]
            + [T71_COVERAGE, T58_REPORT, *T58_CAPTURES]
            + [META / v for v in module.METADATA_FILES.values()]
        },
        "limitations": [
            "T70 had 35 original missing bone-root ELEMENTs; after T71/T72 the historic bone-root residual is 26. This remains distinct from the first-pass residual 0/11.",
            "T70 first-pass 0/11 denotes only its fixed 11 historic first-pass candidate assets, not all visual minimums and not the full anatomy denominator.",
            "AABB, root membership, source metadata, cached source mesh, and learner visibility are not surface/contact or anatomy-approval evidence.",
            "No current browser was opened because T73 changed no learner UI; the reviewed T58 screenshots are historical artifacts only.",
        ],
    }
    return coverage, target_matrix, source_research, validation


def main() -> int:
    global ROOT, META, OUT, SOURCE_MANIFEST, T70_SCOPE, T70_INTEGRATION, T71_INTEGRATION, T72_INTEGRATION, T72_VALIDATION, T71_COVERAGE, T58_REPORT, T58_CAPTURES, TOOL_PATH
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    ROOT = args.root.resolve()
    META = ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"
    OUT = args.out.resolve()
    SOURCE_MANIFEST = ROOT / "atlas-data/manifests/bodyparts3d-r4-source-manifest-t51.json"
    T70_SCOPE = ROOT / "atlas-data/manifests/bodyparts3d-r4-t70/scope-inventory.json"
    T70_INTEGRATION = ROOT / "atlas-data/manifests/bodyparts3d-r4-t70/integration-manifest.json"
    T71_INTEGRATION = ROOT / "atlas-data/manifests/bodyparts3d-r4-t71/integration-manifest.json"
    T72_INTEGRATION = ROOT / "atlas-data/manifests/bodyparts3d-r4-t72/integration-extension.json"
    T72_VALIDATION = ROOT / "work/evidence/T72/validation.json"
    T71_COVERAGE = ROOT / "work/evidence/T71/coverage-recalculation.json"
    T58_REPORT = ROOT / "work/reports/T58.md"
    T58_CAPTURES = [ROOT / "work/evidence/T58/head-front.png", ROOT / "work/evidence/T58/head-side.png", ROOT / "work/evidence/T58/whole-back.png"]
    TOOL_PATH = ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py"
    coverage, matrix, research, validation = build_audit()
    write_json(OUT / "region-coverage.json", coverage)
    write_json(OUT / "target-source-matrix.json", matrix)
    write_json(OUT / "source-research.json", research)
    write_json(OUT / "validation.json", validation)
    print(json.dumps({"result": validation["result"], "regions": coverage["regionCount"], "targetRows": len(matrix["items"]), "outputs": ["region-coverage.json", "target-source-matrix.json", "source-research.json", "validation.json"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
