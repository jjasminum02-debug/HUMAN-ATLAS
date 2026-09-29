#!/usr/bin/env python3
"""Strictly validate T100 concept grouping, linked names, and frozen-package gaps."""
import hashlib
import json
import re
import subprocess
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / "work/evidence/T100/semantic-relations-2026-09-30"
BASELINE = json.loads((EVIDENCE / "start-baseline.json").read_text())
OVERLAY_PATH = ROOT / "atlas-data/overlays/za-local-integration.json"
TARGET_PATH = ROOT / "atlas-data/catalog/target-scope-t96.json"
COMPILED_PATH = ROOT / "atlas-data/source-cache/datasets/za/compiled/manifest.json"
COVERAGE_PATH = ROOT / "work/evidence/T100/bulk-continuation-2026-09-29/target-coverage-snapshot.json"

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha(data):
    return hashlib.sha256(data).hexdigest()

def norm(value):
    return "".join(c for c in unicodedata.normalize("NFKC", value).casefold() if c.isalnum())

def fail(message):
    raise SystemExit(message)

overlay_bytes = OVERLAY_PATH.read_bytes()
overlay = json.loads(overlay_bytes)
target_bytes = TARGET_PATH.read_bytes()
target_doc = json.loads(target_bytes)
compiled_bytes = COMPILED_PATH.read_bytes()
compiled_doc = json.loads(compiled_bytes)
coverage = read(COVERAGE_PATH)

if sha(target_bytes) != BASELINE["protectedInputSha256"]["atlas-data/catalog/target-scope-t96.json"]:
    fail("frozen T96 scope hash changed")
if sha(compiled_bytes) != BASELINE["protectedInputSha256"]["atlas-data/source-cache/datasets/za/compiled/manifest.json"]:
    fail("compiled source manifest hash changed")
if (target_doc["denominators"]["frozenTa2NamedTargetRecords"] != 542
        or target_doc["denominators"]["productRegionMembershipRows"] != 563
        or len(target_doc["regions"]) != 12):
    fail("T96 denominator drift")

base_bytes = subprocess.check_output([
    "git", "show", BASELINE["startHead"] + ":atlas-data/overlays/za-local-integration.json"
], cwd=ROOT)
if sha(base_bytes) != BASELINE["protectedInputSha256"]["atlas-data/overlays/za-local-integration.json"]:
    fail("starting overlay baseline hash mismatch")
base_overlay = json.loads(base_bytes)
before = {row["sourceKey"]: row for row in base_overlay["objects"]}
after = {row["sourceKey"]: row for row in overlay["objects"]}
if len(before) != 960 or len(after) != 960 or before.keys() != after.keys():
    fail("source object identity/cardinality changed")

scope = {item["id"]: item for item in target_doc["targets"]}
compiled = {item["sourceKey"]: item for item in compiled_doc.get("objects", compiled_doc.get("instances", []))}
expected_state = {item["sourceKey"]: item for item in BASELINE["preservedUnnamedSurfaceState"]}
linked = [row for row in overlay["objects"] if row.get("learnerConceptLinks")]
if len(linked) != 226 or set(row["sourceKey"] for row in linked) != set(expected_state):
    fail("semantic link set must equal the frozen 226 eligible unnamed rows")

changed_protected = []
for row in overlay["objects"]:
    old = before[row["sourceKey"]]
    for key in ("sourceKey", "sourceName", "kind", "regionIds", "side", "haConceptId", "targetId", "targetIds",
                "mappingStatus", "semanticReview", "targetRelationEvidence", "localDisplayEligible", "inspectionEligible",
                "defaultVisible", "sourceOnly", "humanReview", "publicRedistribution", "sourceHiddenStatePreserved",
                "localUseRights", "displayDecisionBasis", "hardHoldReasons", "bounds", "relatedMuscles"):
        if old.get(key) != row.get(key):
            changed_protected.append((row["sourceName"], key))
    if old.get("learnerConceptLinks") is not None:
        fail("T100 semantic output overwrote a pre-existing learner link")
    old_names, new_names = old.get("names", {}), row.get("names", {})
    for field in ("koTraditional", "en"):
        if old_names.get(field) != new_names.get(field):
            changed_protected.append((row["sourceName"], "names." + field))
    old_evidence = old.get("nameEvidence", {}) or {}
    new_evidence = row.get("nameEvidence", {}) or {}
    if {key: value for key, value in old_evidence.items() if key != "koModern"} != {
        key: value for key, value in new_evidence.items() if key != "koModern"
    }:
        changed_protected.append((row["sourceName"], "nameEvidence.non-koModern"))
if changed_protected:
    fail("protected anatomy/policy/binding fields changed: " + repr(changed_protected[:8]))

concept_doc = read(EVIDENCE / "unnamed-concept-classification.json")
gap_doc = read(EVIDENCE / "target-gap-classification.json")
source_ids = {source["id"] for source in overlay["evidenceSources"]}
groups = concept_doc["groups"]
if concept_doc["denominator"] != {"surfaceRows": 226, "conceptGroups": 113, "bilateralGroups": 111, "conflictGroups": 2}:
    fail("concept grouping denominators")
if len(groups) != 113 or len({group["conceptKey"] for group in groups if group["conceptKey"]}) != 111:
    fail("concept key cardinality/conflict nulling")
if sum(bool(group["conflicts"]) for group in groups) != 2:
    fail("actual conflict groups not preserved")
if len(gap_doc["targets"]) != 163 or len({row["targetId"] for row in gap_doc["targets"]}) != 163:
    fail("candidate-free target denominator")
expected_candidate_free = {row["targetId"] for row in coverage["targets"] if row["candidateSourceSurfaceCount"] == 0}
if {row["targetId"] for row in gap_doc["targets"]} != expected_candidate_free:
    fail("target gap set differs from frozen candidate snapshot")
gap_counts = Counter(row["category"] for row in gap_doc["targets"])
if gap_counts != Counter({
    "no_exact_descendant_or_ancestor_surface_evidence_in_frozen_package": 2,
    "descendant_surface_representation_present_target_specific_surface_unresolved": 20,
    "ancestor_surface_representation_present_target_specific_surface_unresolved": 135,
    "exact_source_label_observation_identity_crosswalk_needed": 6,
}):
    fail("candidate-free expression/representation triage counts")

mapped_target_rows = {}
for row in overlay["objects"]:
    for target_id in set(([row.get("targetId")] if row.get("targetId") else []) + row.get("targetIds", [])):
        if target_id:
            mapped_target_rows.setdefault(target_id, {})[row["sourceKey"]] = row
target_by_numeric_id = {int(target_id.split(":")[1]): target for target_id, target in scope.items()}
for gap in gap_doc["targets"]:
    target = scope[gap["targetId"]]
    self_id = int(target["id"].split(":")[1])
    ordered_ancestor_ids = [f"TA2:{value}" for value in target.get("sourceAncestryIds", []) if value != self_id]
    if gap.get("targetAncestryIds") != ordered_ancestor_ids:
        fail("target ancestry locator differs from frozen T96 scope: " + gap["targetId"])
    expected_ancestors = []
    for depth, ancestor_id in enumerate(ordered_ancestor_ids, start=1):
        ancestor = scope.get(ancestor_id)
        for source_key, row in mapped_target_rows.get(ancestor_id, {}).items():
            expected_ancestors.append((ancestor_id, depth, source_key, row))
    actual_ancestors = gap.get("ancestorSurfaceRepresentations", [])
    actual_ancestor_keys = {(item["ancestorTargetId"], item["ancestryDepth"], item["sourceKey"]) for item in actual_ancestors}
    expected_ancestor_keys = {(ancestor_id, depth, source_key) for ancestor_id, depth, source_key, _ in expected_ancestors}
    if actual_ancestor_keys != expected_ancestor_keys:
        fail("ancestor surface observations do not match exact T96 ancestry and overlay mappings: " + gap["targetId"])
    for item in actual_ancestors:
        row = mapped_target_rows[item["ancestorTargetId"]][item["sourceKey"]]
        ancestor = scope[item["ancestorTargetId"]]
        if (item.get("ancestorEnglish") != ancestor.get("term", {}).get("english")
                or item.get("sourceName") != row.get("sourceName")
                or item.get("side") != row.get("side")
                or item.get("regionIds") != row.get("regionIds", [])
                or item.get("targetSpecificGeometryProven") is not False
                or item.get("learnerBindingCreated") is not False):
            fail("ancestor observation altered or overstated source representation: " + gap["targetId"])
    if gap["category"] == "ancestor_surface_representation_present_target_specific_surface_unresolved" and not actual_ancestors:
        fail("ancestor category lacks mapped ancestor surface evidence")
    if gap["category"] == "no_exact_descendant_or_ancestor_surface_evidence_in_frozen_package":
        if gap.get("exactSourceLabelObservations") or gap.get("descendantSurfaceRepresentations") or actual_ancestors:
            fail("no-hierarchy-evidence category contains a representation")

link_counts = Counter()
for row in linked:
    if len(row["learnerConceptLinks"]) != 1:
        fail("one explicit link required per current unnamed surface")
    link = row["learnerConceptLinks"][0]
    link_counts[link["relationKind"]] += 1
    if link["humanReview"] != "not_performed" or row["publicRedistribution"] != "held":
        fail("review or public-rights hold promoted")
    if row["haConceptId"] != before[row["sourceKey"]].get("haConceptId"):
        fail("pre-existing canonical HA binding changed")
    if link["conceptKey"] and link["conceptKey"].startswith("HA-"):
        fail("opaque concept key replaced with canonical HA binding")
    if any("\u3400" <= character <= "\u9fff" for character in (row["names"].get("koModern") or "")):
        fail("unexpected Han characters in modern Korean field")
    if any(evidence_id not in source_ids for evidence_id in link["evidenceIds"]):
        fail("learner/source relation has dangling evidence ID")
    if link["relationKind"] == "paired_source_concept" and "za-t99-frozen-source-objects" not in link["evidenceIds"]:
        fail("source-pair learner concept lacks frozen source object evidence")
    allowed_target_kinds = ({"bone", "bone_group", "bone_series"} if row.get("kind") == "bone" else
                            {"named_muscle", "muscle_part", "muscle_group", "muscle_complex", "repeated_muscle_family"})
    for target_id in link["targetIds"]:
        if target_id not in scope or scope[target_id].get("semanticKind") not in allowed_target_kinds:
            fail("source kind and target concept kind disagree: " + row["sourceName"] + " -> " + target_id)
    for match in link["targetTermMatches"]:
        target = scope.get(match["targetId"])
        if not target:
            fail("link references target outside frozen T96 scope")
        label = re.sub(r"\.[lr]$", "", row["sourceName"], flags=re.I)
        exact_terms = [target["term"]["english"], target["term"]["latin"], *sum(target["term"]["sourceSynonyms"].values(), [])]
        expected_values = sorted({term for term in exact_terms if term and norm(term) == norm(label)})
        if not expected_values or sorted(match["matchedValues"]) != expected_values:
            fail("term relation is not exact against frozen target/source synonym fields")
    if link["relationKind"] == "verified_class_member":
        side_code = link["memberCode"] + ":" + str(row.get("side"))
        matches = [rel for rel in row.get("targetRelationEvidence", [])
                   if rel["targetId"] in link["targetIds"] and rel.get("relationKind") == "class_member"
                   and (rel.get("memberCode") == side_code
                        or rel.get("memberCode") == link["memberCode"] and rel.get("sourceSide") == row.get("side"))]
        if not matches:
            fail("class member link lost source member/side relation")

if link_counts != Counter({"verified_class_member": 67, "normalized_exact_target_term": 154,
                           "paired_source_concept": 4, "side_or_source_identity_conflict": 1}):
    fail("semantic link type counts")
name_updates = concept_doc["nameUpdates"]
if len(name_updates) != 67:
    fail("supported modern name update count")
for item in name_updates:
    row = after[item["sourceKey"]]
    evidence = row.get("nameEvidence", {}).get("koModern", {})
    if (row["names"].get("koModern") != item["value"] or row.get("label") != item["value"]
            or evidence.get("value") != item["value"] or any(sid not in source_ids for sid in evidence.get("sourceIds", []))):
        fail("new Korean name missing field-level evidence")

if len([row for row in overlay["objects"] if row.get("localDisplayEligible")]) != 672:
    fail("local-display surface denominator drift")
ha_bindings = [(row["sourceKey"], row["haConceptId"]) for row in overlay["objects"] if row.get("haConceptId")]
if len(ha_bindings) != 130 or set(ha_bindings) != {(item["sourceKey"], item["haConceptId"]) for item in BASELINE["preexistingHaConceptBindings"]}:
    fail("pre-existing canonical binding map changed")

result = {
    "schemaVersion": 1,
    "taskId": "T100",
    "status": "pass_partial",
    "checks": {
        "frozenTargetDenominators": {"targets": 542, "memberships": 563, "regions": 12},
        "sourceObjects": len(after),
        "eligibleSurfaceRows": 672,
        "previouslyUnnamedRowsClassified": len(linked),
        "sideDeduplicatedConceptGroups": len(groups),
        "explicitBilateralGroups": concept_doc["denominator"]["bilateralGroups"],
        "conflictGroupsHeld": concept_doc["denominator"]["conflictGroups"],
        "sourceAndTargetLearnerRelations": dict(link_counts),
        "newEvidenceBackedModernKoreanSurfaceNames": len(name_updates),
        "modernKoreanNameCoverageAfter": sum(bool(row.get("names", {}).get("koModern")) for row in overlay["objects"] if row.get("localDisplayEligible")),
        "candidateFreeTargetsClassified": len(gap_doc["targets"]),
        "candidateFreeTriage": dict(gap_counts),
        "candidateFreeTargetsWithMappedAncestorSurfaceOnly": sum(
            row["category"] == "ancestor_surface_representation_present_target_specific_surface_unresolved"
            for row in gap_doc["targets"]
        ),
        "candidateFreeTargetsWithoutExactDescendantOrAncestorSurface": sum(
            row["category"] == "no_exact_descendant_or_ancestor_surface_evidence_in_frozen_package"
            for row in gap_doc["targets"]
        ),
        "preexistingCanonicalHaBindingsPreserved": len(ha_bindings),
        "sourceOnlyAndHumanReviewState": "preserved per original row; no human review added",
        "publicRedistribution": "held",
        "newGeometry": 0,
    },
    "inputSha256": {
        "baselineOverlay": sha(base_bytes),
        "currentOverlay": sha(overlay_bytes),
        "targetScopeT96": sha(target_bytes),
        "compiledManifest": sha(compiled_bytes),
        "conceptClassification": sha((EVIDENCE / "unnamed-concept-classification.json").read_bytes()),
        "candidateFreeTargetTriage": sha((EVIDENCE / "target-gap-classification.json").read_bytes()),
    },
    "remaining": [
        "159/672 eligible surfaces still lack a modern Korean name.",
        "163 candidate-free targets are classified within the frozen package, not resolved as anatomical absence; ancestor surfaces are not target-specific geometry.",
        "Whole-body exact visual/member coverage and active scene FPS/GPU/memory acceptance are still open.",
    ],
}
(EVIDENCE / "semantic-validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(result, ensure_ascii=False, indent=2))
