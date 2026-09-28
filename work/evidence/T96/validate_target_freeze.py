#!/usr/bin/env python3
"""Validate the T96 TA2 semantic freeze and its twelve bounded packages."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "work/evidence/T96"
REVISION = "T96-2026-09-28-semantic-freeze-v1"
REGIONS = {
    "T110": "head", "T111": "neck", "T112": "back",
    "T113": "shoulder-scapular", "T114": "thorax", "T115": "abdomen-lumbar",
    "T116": "pelvis-perineum", "T117": "gluteal-hip", "T118": "thigh",
    "T119": "leg", "T120": "foot", "T121": "upper-limb",
}
EXPECTED_EXCLUDED = set(range(367, 377)) | {
    1010, 1141, 1305, 1359, 2450, 2592, 2370, 2371, 2504, 2647,
}
EXPECTED_PROMOTED = {880, 1105, 1118, 1282, 2605, 2636}
EXPECTED_TASK_TITLES = {
    "T110": "머리 구조 식별·이름·선택 연결 패키지",
    "T111": "목 구조 식별·이름·선택 연결 패키지",
    "T112": "등 구조 식별·이름·선택 연결 패키지",
    "T113": "어깨·어깨뼈 구조 식별·이름·선택 연결 패키지",
    "T114": "가슴우리 구조 식별·이름·선택 연결 패키지",
    "T115": "배·허리 구조 식별·이름·선택 연결 패키지",
    "T116": "골반·샅 구조 식별·이름·선택 연결 패키지",
    "T117": "볼기·깊은엉덩이 구조 식별·이름·선택 연결 패키지",
    "T118": "넙다리 구조 식별·이름·선택 연결 패키지",
    "T119": "종아리 구조 식별·이름·선택 연결 패키지",
    "T120": "발 구조 식별·이름·선택 연결 패키지",
    "T121": "팔·손 구조 식별·이름·선택 연결 패키지",
}
INPUT_PATHS = [
    "design/2026-09-25-muscle-atlas/22-EFFICIENT-DELIVERY-AND-PERFORMANCE.md",
    "design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md",
    "work/tasks/T96.md",
    "work/tasks/T110.md", "work/tasks/T111.md", "work/tasks/T112.md",
    "work/tasks/T113.md", "work/tasks/T114.md", "work/tasks/T115.md",
    "work/tasks/T116.md", "work/tasks/T117.md", "work/tasks/T118.md",
    "work/tasks/T119.md", "work/tasks/T120.md", "work/tasks/T121.md",
    "work/evidence/T78/reference/source.json",
    "work/evidence/T78/reference/ta2-scope.json",
    "work/evidence/T78/classification-ledger.json",
    "work/evidence/T78/targets.json",
    "work/evidence/T78/source-elements.json",
    "work/evidence/T78/inventory-summary.json",
    "work/evidence/T78/target-task-map.json",
    "work/reports/T78.md", "work/reports/T95.md",
    "work/evidence/T95/overlay-validation.json",
    "atlas-data/catalog/canonical-catalog.json",
    "atlas-data/catalog/source-crosswalk.json",
    "atlas-data/catalog/whole-body-inventory-t15g.json",
    "atlas-data/terminology/learning-names.json",
    "atlas-data/terminology/ai-evidence-overlay.json",
    "atlas-data/motion/motion-learning.json",
    "atlas-data/navigation/atlas-navigation.json",
    "atlas-data/source-cache/bodyparts3d-r4/converted/t77/manifest.json",
]


def read(path: str | Path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def source_english(row: dict):
    term = row.get("term", {})
    return term.get("en") or term.get("en_US") or term.get("en_GB")


def ancestry_ids(row_id: int, rows_by_id: dict[int, dict]) -> list[int]:
    path = []
    seen = set()
    current = rows_by_id.get(row_id)
    while current is not None:
        current_id = current["id"]
        check(current_id not in seen, f"source parent cycle at TA2:{current_id}")
        seen.add(current_id)
        path.append(current_id)
        parent = current.get("parent")
        current = rows_by_id.get(parent) if parent is not None else None
    return path


def source_side(row: dict) -> str | None:
    joined = " ".join([
        source_english(row) or "", row.get("term", {}).get("la") or "",
    ]).lower()
    right = "right " in joined or " dexter" in joined or joined.startswith("dexter")
    left = "left " in joined or " sinister" in joined or joined.startswith("sinister")
    if right and left:
        return "conflicted_source_side"
    if right:
        return "right"
    if left:
        return "left"
    return None


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    failures = []
    input_manifest = read("work/evidence/T96/input-hashes.json")
    source_rows = read("work/evidence/T78/reference/ta2-scope.json")
    prior_ledger_rows = read("work/evidence/T78/classification-ledger.json")
    prior_targets = read("work/evidence/T78/targets.json")
    ledger = read("work/evidence/T96/semantic-classification-ledger.json")
    aliases = read("work/evidence/T96/ta2-usage-aliases.json")
    rules = read("work/evidence/T96/decision-rules.json")
    scope = read("atlas-data/catalog/target-scope-t96.json")
    package_index = read("atlas-data/manifests/region-packages-t96.json")
    state_crosscheck = read("work/evidence/T96/content-state-crosscheck.json")
    summary = read("work/evidence/T96/freeze-summary.json")
    reverse_scan = read("work/evidence/T96/supporting-muscle-reverse-scan.json")

    check(input_manifest["revision"] == REVISION and scope["revision"] == REVISION, "revision mismatch")
    expected_inputs = {path: sha((ROOT / path).read_bytes()) for path in INPUT_PATHS}
    check(input_manifest["hashes"] == expected_inputs, "one or more T96 inputs drifted")
    check(input_manifest["sourceRowCount"] == 2422, "source snapshot row count changed")
    check(input_manifest["sourceSnapshotSha256"] == sha((ROOT / "work/evidence/T78/reference/ta2-scope.json").read_bytes()), "source snapshot hash mismatch")

    registry = read("work/task-registry-r15.json")
    registry_tasks = {row["id"]: row for row in registry["tasks"]}
    check(registry.get("taskStatuses", {}).get("T96") == "passed_with_gaps", "R15 T96 task status is not updated")
    check(all(registry.get("taskStatuses", {}).get(task_id) == "planned_not_started" for task_id in REGIONS), "T110-T121 must remain not started after freeze")
    check(registry.get("nextTask") == "T79" and registry.get("efficiencyAmendment", {}).get("nextTask") == "T79", "R15 next task pointer does not follow T96 default")
    for task_id, title in EXPECTED_TASK_TITLES.items():
        task = registry_tasks.get(task_id)
        check(task is not None and task["title"] == title, f"registry task mapping is not the assigned region: {task_id}")
        check(task["spec"] == f"work/tasks/{task_id}.md" and task["model"] == "Luna Max", f"task ownership/spec mismatch: {task_id}")
        check("T96" in task.get("prerequisiteIds", []), f"package task does not depend on T96 freeze: {task_id}")

    source_by_id = {row["id"]: row for row in source_rows}
    prior_by_id = {row["ta2Id"]: row for row in prior_ledger_rows}
    prior_target_by_id = {int(row["id"].split(":", 1)[1]): row for row in prior_targets}
    ledger_by_id = {row["ta2Id"]: row for row in ledger}
    scope_targets = scope["targets"]
    frozen_target_row_ids = {target["ta2Id"] for target in scope_targets}
    check(len(source_rows) == 2422 and len(source_by_id) == len(source_rows), "source IDs duplicate/missing")
    check(len(ledger) == 2422 and len(ledger_by_id) == len(ledger), "all-row ledger IDs duplicate/missing")
    check(set(ledger_by_id) == set(source_by_id), "all-row ledger omitted or added a source row")
    source_attrs_excluded = {
        "id", "level", "term", "synonyms", "related_terms", "note_references", "parent",
        "inconstant", "sex", "primary_usage", "secondary_usage",
    }
    for row_id, row in source_by_id.items():
        item = ledger_by_id[row_id]
        expected_projection = {
            "sourceLevel": row.get("level"), "sourceTerm": row.get("term", {}),
            "sourceSynonyms": row.get("synonyms", {}), "sourceRelatedTerms": row.get("related_terms", []),
            "sourceNoteReferences": row.get("note_references", []), "parentId": row.get("parent"),
            "ta2PrimaryUsage": row.get("primary_usage"), "ta2SecondaryUsage": row.get("secondary_usage"),
            "ta2Inconstant": row.get("inconstant") == "true", "ta2Sex": row.get("sex"),
            "sourceOtherAttributes": {k: v for k, v in row.items() if k not in source_attrs_excluded},
        }
        check(all(item.get(k) == v for k, v in expected_projection.items()), f"source data projection mismatch: TA2:{row_id}")
        check(item.get("priorT78Kind") == prior_by_id[row_id]["kind"], f"prior classification not retained: TA2:{row_id}")

    muscle_rows = [row for row in source_rows if 1974 in ancestry_ids(row["id"], source_by_id)]
    reverse_scan_rows = {row["ta2Id"]: row for row in reverse_scan["supportRowsRequiringSemanticReview"]}
    expected_scan_ids = set()
    for row in muscle_rows:
        if row["id"] in frozen_target_row_ids:
            continue
        searchable = json.dumps({"term": row.get("term", {}), "synonyms": row.get("synonyms", {})}, ensure_ascii=False).lower()
        if "muscle" in searchable or "muscul" in searchable:
            expected_scan_ids.add(row["id"])
    check(reverse_scan["muscularSystemSubtreeRowCount"] == len(muscle_rows), "muscular subtree scan count mismatch")
    check(reverse_scan["nonTargetSubtreeRows"] == sum(1 for row in muscle_rows if row["id"] not in frozen_target_row_ids), "muscular subtree non-target count mismatch")
    check(set(reverse_scan_rows) == expected_scan_ids and len(expected_scan_ids) == 113, "support lexical reverse-scan missed/added row")
    for row_id, item in reverse_scan_rows.items():
        row = source_by_id[row_id]
        check(item["term"] == row.get("term", {}) and item["synonyms"] == row.get("synonyms", {}), f"reverse scan source mismatch: TA2:{row_id}")
        check(item["parentChainIds"] == list(reversed(ancestry_ids(row_id, source_by_id))), f"reverse scan hierarchy mismatch: TA2:{row_id}")
        check(item["decisionReason"] == ledger_by_id[row_id]["decisionReason"], f"reverse scan decision mismatch: TA2:{row_id}")
    check(reverse_scan["restoredNamedMusclesFromSupport"] == [
        {"ta2Id": 2605, "term": source_by_id[2605].get("term", {}), "reason": "named deep gluteal muscle, exact TA2 child of deep gluteal muscles"},
        {"ta2Id": 2636, "term": source_by_id[2636].get("term", {}), "reason": "named medial thigh muscle, exact TA2 child of medial thigh compartment"},
    ], "support reverse scan promoted-muscle evidence mismatch")

    target_by_id = {target["ta2Id"]: target for target in scope_targets}
    check(len(prior_targets) == 556 and len(prior_target_by_id) == 556, "T78 candidate ledger is not 556 unique rows")
    check(len(target_by_id) == 542 and len(scope_targets) == 542, "frozen target count/uniqueness mismatch")
    excluded = {int(row["id"].split(":", 1)[1]) for row in rules["explicitCandidateExclusions"]}
    promoted = {int(row["id"].split(":", 1)[1]) for row in rules["promotionsFromSupport"]}
    check(excluded == EXPECTED_EXCLUDED and len(excluded) == 20, "candidate exclusion ledger mismatch")
    check(promoted == EXPECTED_PROMOTED and len(promoted) == 6, "support promotion ledger mismatch")
    check(excluded <= set(prior_target_by_id), "excluded row was not a T78 candidate")
    check(promoted.isdisjoint(prior_target_by_id), "promoted row already existed as T78 candidate")
    check(all(prior_by_id[row_id]["kind"] == "supporting_nomenclature_not_geometry_target" for row_id in promoted), "promoted row was not in T78 supporting ledger")
    expected_final = (set(prior_target_by_id) - excluded) | promoted
    check(set(target_by_id) == expected_final, "candidate -> frozen target reconciliation omitted/added IDs")
    check(556 - len(excluded) + len(promoted) == 542, "reconciliation arithmetic invalid")
    for row_id in set(source_by_id):
        entry = ledger_by_id[row_id]
        if row_id in expected_final:
            check(entry["disposition"] == "included_target" and entry["targetId"] == f"TA2:{row_id}", f"included disposition wrong: TA2:{row_id}")
            check(entry["primaryOwner"] == target_by_id[row_id]["primaryOwner"], f"ledger owner mismatch: TA2:{row_id}")
        elif row_id in excluded:
            check(entry["disposition"] == "excluded_candidate_with_explicit_reconciliation" and bool(entry["decisionReason"]), f"excluded candidate lacks reason: TA2:{row_id}")
            check(entry["targetId"] is None, f"excluded candidate remains target: TA2:{row_id}")
        else:
            check(entry["disposition"] == "supporting_nomenclature_not_region_target" and bool(entry["decisionReason"]), f"support row lacks disposition/reason: TA2:{row_id}")

    exception_review = read("work/evidence/T96/semantic-exception-review.json")
    audit_rows = {row["ta2Id"]: row for row in exception_review["rows"]}
    check(set(audit_rows) == excluded | promoted and len(audit_rows) == 26, "semantic exception audit does not cover exactly all changes")
    for row_id, audit in audit_rows.items():
        source = source_by_id[row_id]
        check(audit["sourceTerm"] == source.get("term", {}) and audit["sourceSynonyms"] == source.get("synonyms", {}), f"exception audit source text mismatch: TA2:{row_id}")
        check(audit["sourceLocator"]["snapshotRowId"] == row_id and audit["sourceLocator"]["snapshotSha256"] == input_manifest["sourceSnapshotSha256"], f"exception audit locator/hash mismatch: TA2:{row_id}")
        expected_decision = "exclude_candidate" if row_id in excluded else "promote_support_row"
        check(audit["t96Decision"] == expected_decision and audit["decisionReason"], f"exception decision/reason mismatch: TA2:{row_id}")
        if row_id in excluded:
            check(audit["frozenTarget"] is None, f"excluded audit row points to a target: TA2:{row_id}")
        else:
            check(audit["frozenTarget"]["id"] == f"TA2:{row_id}" and audit["frozenTarget"]["primaryOwner"] == target_by_id[row_id]["primaryOwner"], f"promoted audit row target mismatch: TA2:{row_id}")

    target_ids = {target["id"] for target in scope_targets}
    check(len(target_ids) == 542, "duplicate stable source target IDs")
    target_kinds = Counter(target["semanticKind"] for target in scope_targets)
    check(sum(target_kinds.values()) == 542, "target-kind counts do not sum to frozen targets")
    for target in scope_targets:
        row = source_by_id[target["ta2Id"]]
        check(target["id"] == f"TA2:{target['ta2Id']}", "target ID is not exact TA2 source row")
        check(target["term"]["latin"] == row.get("term", {}).get("la"), f"Latin source term mismatch: {target['id']}")
        check(target["term"]["english"] == source_english(row), f"English source term mismatch: {target['id']}")
        check(target["term"]["sourceSynonyms"] == row.get("synonyms", {}), f"source synonyms mismatch: {target['id']}")
        check(target["sourceFlags"]["inconstant"] == row.get("inconstant"), f"inconstant source flag mismatch: {target['id']}")
        check(target["sourceFlags"]["sex"] == row.get("sex"), f"sex source flag mismatch: {target['id']}")
        check(target["sourceFlags"]["primaryUsage"] == row.get("primary_usage") and target["sourceFlags"]["secondaryUsage"] == row.get("secondary_usage"), f"usage source flags mismatch: {target['id']}")
        check(target["sourceFlags"]["relatedTerms"] == row.get("related_terms", []) and target["sourceFlags"]["noteReferences"] == row.get("note_references", []), f"related/note source fields mismatch: {target['id']}")
        check(target["scopeFlags"]["ta2Inconstant"] == (row.get("inconstant") == "true"), f"inconstant scope flag mismatch: {target['id']}")
        check(target["scopeFlags"]["sourceSex"] == row.get("sex") and target["scopeFlags"]["explicitSourceSide"] == source_side(row), f"sex/side scope flag mismatch: {target['id']}")
        expected_member_count = None if target["semanticKind"] == "repeated_muscle_family" else "not_applicable_or_not_source_specified"
        check(target["scopeFlags"]["repeatedFamilyMemberCount"] == expected_member_count, f"repeat count expanded without source data: {target['id']}")
        cardinality = target["sourceCardinality"]
        expected_laterality_state = "explicit_source_side" if source_side(row) else "not_specified_by_source"
        check(cardinality["lateralityState"] == expected_laterality_state and cardinality["explicitSourceSide"] == source_side(row), f"source laterality field mismatch: {target['id']}")
        check(cardinality["bilateralInstanceCount"] is None and cardinality["midlineInstanceCount"] is None and cardinality["expansionPerformed"] is False, f"bilateral/midline cardinality was inferred: {target['id']}")
        check(cardinality["repeatedFamilyMemberCount"] == expected_member_count, f"source repeated-family count was expanded: {target['id']}")
        owner = target["primaryOwner"]
        check(owner in set(REGIONS.values()), f"target lacks valid primary owner: {target['id']}")
        check(target["regionIds"] and owner in target["regionIds"], f"primary owner not represented in regionIds: {target['id']}")
        check(set(target["regionIds"]) <= set(REGIONS.values()), f"unknown region membership: {target['id']}")
        check(target["contentState"]["humanReview"] is False, f"human review was promoted: {target['id']}")
        check(target["contentState"]["rights"] == "not_promoted", f"rights promoted: {target['id']}")
        check(target["contentState"]["sourceIdentity"] == "not_approved_by_lexical_match", f"identity promoted: {target['id']}")
        check(target["contentState"]["canonicalBinding"] != "reviewed", f"binding reviewed without review: {target['id']}")
        check(target["contentState"]["geometry"] in {"unresolved", "unresolved_not_in_T78_target_list", "candidate_in_scene", "candidate_not_acquired", "missing"}, f"unexpected geometry state: {target['id']}")
    check(scope["denominators"]["wholeBodyIndividualMuscleDenominator"] is None, "individual-muscle denominator was falsely fixed")
    check(scope["denominators"]["primaryOwnerAssignments"] == 542 and scope["denominators"]["productRegionMembershipRows"] == 563, "primary-owner/membership denominators mismatch")
    check(summary["wholeBodyIndividualMuscleDenominator"] is None, "summary falsely fixes individual-muscle denominator")

    # Verify that source-native usage references are retained as alias edges, not target rows.
    expected_aliases = []
    for row in source_rows:
        if row.get("primary_usage") is not None:
            expected_aliases.append({"sourceId": row["id"], "relation": "primary_usage", "referencedId": row["primary_usage"]})
        if row.get("secondary_usage") is not None:
            expected_aliases.append({"sourceId": row["id"], "relation": "secondary_usage", "referencedId": row["secondary_usage"]})
    check(aliases["aliases"] == expected_aliases and aliases["count"] == len(expected_aliases) == 33, "TA2 alias edges changed or were counted as targets")

    # Exact-row crosswalk is availability evidence only; never lexical/fuzzy mapping.
    crosswalk = read("atlas-data/catalog/source-crosswalk.json")["catalogItems"]
    cw_by_row = {item["tableRow"]: item for item in crosswalk}
    check(len(crosswalk) == 85 and len(cw_by_row) == 85, "canonical crosswalk rows duplicate or count changed")
    for target in scope_targets:
        item = cw_by_row.get(target["ta2Id"])
        actual = target["existingEvidence"]["canonicalStableConceptId"]
        check(actual == (item["stableConceptId"] if item else None), f"canonical relation is not exact tableRow: {target['id']}")
    check(state_crosscheck["canonicalCrosswalkRowsWithoutFrozenTargetOrExplicitExclusion"] == [], "crosswalk rows are unaccounted")
    check(state_crosscheck["exactCanonicalJoinCount"] == 83, "exact canonical joins changed")
    check(state_crosscheck["canonicalClaimsCreated"] == 0 and state_crosscheck["bindingsCreated"] == 0, "T96 created a claim/binding")
    check(state_crosscheck["humanReviewPromotions"] == 0 and state_crosscheck["rightsPromotions"] == 0, "T96 promoted a review/rights state")
    check(state_crosscheck["aiAndMotionNoFuzzyJoin"] is True, "AI/motion evidence fuzzy join rule not recorded")
    state_by_id = {row["targetId"]: row for row in state_crosscheck["targets"]}
    check(len(state_by_id) == 542, "content-state crosscheck target rows not unique")
    for target in scope_targets:
        state = state_by_id[target["id"]]
        content = target["contentState"]
        for field in ["geometry", "sourceIdentity", "side", "frame", "canonicalBinding", "threeNames", "originInsertion", "function", "animation", "humanReview", "rights"]:
            check(state[field] == content[field], f"content-state crosscheck drift {field}: {target['id']}")
        check(state["runtimeAssetCandidates"] == target["existingEvidence"]["runtimeAssetIdsFromLexicalCandidates"], f"runtime candidate evidence mismatch: {target['id']}")

    # Twelve packages: one primary-owner membership per target, with bounded workUnits.
    package_paths = {p["taskId"]: p for p in package_index["packages"]}
    check(set(package_paths) == set(REGIONS), "package task IDs differ from T110-T121")
    check(package_index["targetCount"] == 542 and package_index["wholeBodyIndividualMuscleDenominator"] is None, "package index denominator/count mismatch")
    check(package_index["downstreamTasksStarted"] is False, "downstream work was started")
    owners_seen = Counter()
    total_memberships = 0
    unit_count = 0
    for task_id, region_id in REGIONS.items():
        pkg_path = f"atlas-data/manifests/region-target-packages-t96/{task_id}.json"
        pkg_bytes = (ROOT / pkg_path).read_bytes()
        package = json.loads(pkg_bytes)
        index_row = package_paths[task_id]
        check(index_row["path"] == pkg_path and index_row["sha256"] == sha(pkg_bytes), f"package index hash/path mismatch: {task_id}")
        check(package["taskId"] == task_id and package["regionId"] == region_id, f"package owner/region mismatch: {task_id}")
        check(package["status"] == "frozen_input_not_started" and package["progress"]["completedUnits"] == 0, f"package started or status drift: {task_id}")
        check(package["inputHashes"] == expected_inputs, f"package input hashes drifted: {task_id}")
        check(package["targetCount"] == len(package["targetIds"]) == index_row["targetCount"], f"package target count mismatch: {task_id}")
        check(index_row["primaryTargetCount"] == len(package["targetIds"]), f"primary target count mismatch: {task_id}")
        check(index_row["regionMembershipCount"] == sum(1 for t in scope_targets if region_id in t["regionIds"]), f"product membership count mismatch: {task_id}")
        check(package["workUnitLimit"] == 10 and index_row["workUnitCount"] == len(package["workUnits"]), f"workUnit contract mismatch: {task_id}")
        check(package["nextUnit"] == package["workUnits"][0]["unitId"], f"next unit mismatch: {task_id}")
        package_ids = package["targetIds"]
        check(len(package_ids) == len(set(package_ids)), f"duplicate target inside package: {task_id}")
        check(package_ids == sorted(package_ids, key=lambda value: int(value.split(":")[1])), f"package order unstable: {task_id}")
        check(all(target_by_id[int(value.split(":")[1])]["primaryOwner"] == region_id for value in package_ids), f"wrong primary owner in {task_id}")
        check(all(region_id in target_by_id[int(value.split(":")[1])]["regionIds"] for value in package_ids), f"package membership mismatch: {task_id}")
        units = package["workUnits"]
        check(units and all(0 < u["targetCount"] <= 10 and u["targetCount"] == len(u["targetIds"]) for u in units), f"workUnit empty/over limit: {task_id}")
        flat_units = [value for unit in units for value in unit["targetIds"]]
        check(flat_units == package_ids and len(flat_units) == len(set(flat_units)), f"workUnit partition has missing/duplicate target: {task_id}")
        for unit in units:
            unit_count += 1
            members = [target_by_id[int(value.split(":")[1])] for value in unit["targetIds"]]
            check(unit["status"] == "planned_not_started", f"work unit started: {unit['unitId']}")
            check(unit["targetsSha256"] == sha(canonical_json(members)), f"work unit payload hash mismatch: {unit['unitId']}")
        for value in package_ids:
            owners_seen[value] += 1
        total_memberships += sum(1 for t in scope_targets if region_id in t["regionIds"])
    check(set(owners_seen) == target_ids and all(count == 1 for count in owners_seen.values()), "primary package ownership is not exact-one")
    check(package_index["allTargetIdsExactlyOnce"] is True, "package index exact-once flag false")
    check(package_index["productRegionMembershipCount"] == 563, "package index membership denominator mismatch")
    check(package_index["scopeSha256"] == sha((ROOT / "atlas-data/catalog/target-scope-t96.json").read_bytes()), "target scope hash in package index mismatches bytes")
    check(sum(package_paths[t]["targetCount"] for t in REGIONS) == 542, "primary owner region counts do not sum to 542")
    check(sum(len(t["regionIds"]) for t in scope_targets) == 563, "secondary product membership total mismatch")
    region_rows = {row["taskId"]: row for row in scope["regions"]}
    check(set(region_rows) == set(REGIONS), "scope region/task assignment is not exactly T110-T121")
    for task_id, region_id in REGIONS.items():
        expected_primary = package_paths[task_id]["targetCount"]
        expected_membership = sum(1 for target in scope_targets if region_id in target["regionIds"])
        check(region_rows[task_id]["regionId"] == region_id, f"scope region identity mismatch: {task_id}")
        check(region_rows[task_id]["primaryTargetCount"] == expected_primary, f"scope primary owner count mismatch: {task_id}")
        check(region_rows[task_id]["regionMembershipCount"] == expected_membership, f"scope product membership count mismatch: {task_id}")

    # Confirm the builder is deterministic and protected source subtree did not drift.
    build = subprocess.run([sys.executable, str(EVIDENCE / "build_target_freeze.py"), "--check"], cwd=ROOT, capture_output=True, text=True)
    check(build.returncode == 0, f"deterministic build check failed: {build.stdout}{build.stderr}")
    opensim = ROOT / "OpenSim_Models"
    opensim_head = subprocess.run(["git", "-C", str(opensim), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    opensim_status = subprocess.run(["git", "-C", str(opensim), "status", "--porcelain=v1"], capture_output=True, text=True, check=True).stdout
    baseline = read("work/evidence/T96/start-baseline.json")
    check(opensim_head == baseline["openSimModels"]["head"] and not opensim_status, "OpenSim_Models changed from task baseline")
    check(baseline["taskStartHead"] == "c2ea5b42f302d1def21a75183b2a2085a83a024f", "unexpected T96 start commit")
    check(baseline["taskStartStatusSha256"] == "1d685761e8ba141c26bca22755b0054c186f6ef4d26fbdd7d453e4af8b8260ad", "unexpected T96 start status snapshot")
    preservation_after = read("work/evidence/T96/preservation-after.json")
    check(preservation_after["preexistingStatusEntriesPreserved"] is True, "pre-existing worktree entries changed/disappeared")
    check(preservation_after["openSimModels"]["head"] == baseline["openSimModels"]["head"] and preservation_after["openSimModels"]["clean"] is True, "OpenSim preservation after check failed")
    check(preservation_after["T78HistoricalInputHashesMatch"] is True, "T78 historical inputs changed")

    result = {
        "task": "T96", "revision": REVISION, "status": "passed_with_gaps",
        "checks": "passed",
        "sourceRowsAndExactProjection": len(source_rows),
        "priorCandidateReconciliation": {"prior": 556, "explicitlyExcluded": len(excluded), "promotedFromSupport": len(promoted), "frozenTargetRecords": len(scope_targets)},
        "targetKinds": dict(sorted(target_kinds.items())),
        "primaryOwners": {task_id: package_paths[task_id]["targetCount"] for task_id in REGIONS},
        "productRegionMembershipsIncludingSecondaryContexts": sum(len(t["regionIds"]) for t in scope_targets),
        "targetVariantAndSideCounts": {
            "ta2Inconstant": scope["denominators"]["ta2InconstantTargets"],
            "sexSpecific": scope["denominators"]["sexSpecificTargetRecords"],
            "sourceExplicitSide": scope["denominators"]["explicitSideTargetRecords"],
            "bilateralIndividualMuscleInstanceCount": None,
            "midlineIndividualMuscleInstanceCount": None,
            "repeatedFamilyMemberCounts": None,
        },
        "packageCount": len(package_paths), "workUnitCount": unit_count, "maxTargetsPerWorkUnit": 10,
        "aliasEdgesNotTargets": len(expected_aliases), "exactCanonicalCrosswalkRows": len(crosswalk),
        "exactCanonicalTargetJoins": state_crosscheck["exactCanonicalJoinCount"],
        "humanReviewPromotions": 0, "rightsPromotions": 0, "canonicalClaimsCreated": 0, "bindingsCreated": 0,
        "wholeBodyIndividualMuscleDenominator": None,
        "allPackagesNotStarted": True, "OpenSimModelsHead": opensim_head, "OpenSimModelsClean": True,
        "downstreamTasksStarted": False,
    }
    out = EVIDENCE / "validation-result.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
