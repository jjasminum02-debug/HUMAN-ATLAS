#!/usr/bin/env python3
"""Validate T66 learner nerve concepts, source relations, side scope, and preserved gates."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "work/evidence/T66/nerve-learning-2026-10-05"


def read(path: Path):
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    graph = read(ROOT / "atlas-data/terminology/learner-nerve-graph-t66.json")
    course = read(ROOT / "atlas-data/terminology/nerve-learning-t66.json")
    support = read(ROOT / "atlas-data/overlays/nerve-support-t66.json")
    integration = read(ROOT / "atlas-data/overlays/za-local-integration.json")
    ledger = read(EVIDENCE / "nerve-relation-ledger.json")
    by_key = {row["sourceKey"]: row for row in integration["objects"]}
    concept_by_key = {row["key"]: row for row in graph["concepts"]}
    source_labels = {}
    for row in support["instances"]:
        source_labels.setdefault(row["names"]["en"], []).append(row)
    findings = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            findings.append(message)

    require(len(support["instances"]) == ledger["denominators"]["staticSourceSurfaces"] == 195,
            "static nerve surface denominator changed")
    require(len(source_labels) == ledger["denominators"]["uniqueSourceLabelGroups"] == 98,
            "source label group denominator changed")
    require(ledger["denominators"]["independentAnatomyConceptCount"] == "not inferred from label groups",
            "label groups must not define independent anatomy concept count")
    require(len(ledger["labelGroupDisposition"]) == len(source_labels), "label group disposition is incomplete")
    disposition = {row["labelGroupEnglishName"]: row for row in ledger["labelGroupDisposition"]}
    require(set(disposition) == set(source_labels), "label group names differ from the source inventory")
    for name, group in source_labels.items():
        row = disposition.get(name)
        require(row is not None and row["sourceSurfaceCount"] == len(group), f"label group mismatch: {name}")
        if row:
            key = row["graphConceptKey"]
            require(key is None or key in concept_by_key, f"unknown graph concept for label group: {name}")
            require(row["functionEvidenceClass"] in {
                "mixed_motor_sensory_evidence_and_motor_relation",
                "sensory_course_documented_no_motor_relation",
                "motor_relation_documented_sensory_class_not_assessed",
                "relationship_not_linked",
            }, f"unclassified function evidence state: {name}")

    exact_rows = [row for row in graph["motorRelations"] if row["basis"] == "exact_geometry_motor_relation"]
    literature_rows = [row for row in graph["motorRelations"] if row["basis"] == "literature_concept_motor_relation"]
    require(len({row["relationId"] for row in graph["motorRelations"]}) == len(graph["motorRelations"]), "duplicate relation IDs")
    require(len(exact_rows) == 2, "exact geometry relation count differs from the existing two side-specific rows")
    require(len(literature_rows) == len(graph["motorRelations"]) - len(exact_rows), "untyped relation basis")
    for relation in graph["motorRelations"]:
        evidence_row = next((row for row in ledger["relations"] if row["relationId"] == relation["relationId"]), None)
        require(evidence_row is not None, f"missing evidence row: {relation['relationId']}")
        require(evidence_row is not None and evidence_row["basis"] == relation["basis"], f"relation basis mismatch: {relation['relationId']}")
        require(bool(evidence_row and evidence_row["sourceIds"]), f"relation has no source locator: {relation['relationId']}")
        for source_key in relation["targetSourceKeys"]:
            target = by_key.get(source_key)
            require(bool(target and target.get("kind") == "muscle" and target.get("localDisplayEligible") and target.get("inspectionEligible")),
                    f"relation target absent or ineligible: {relation['relationId']} -> {source_key}")
        if relation["scope"] == "exact_side_matched_source_instance":
            require(relation["targetSide"] in {"left", "right"}, f"exact relation lacks side: {relation['relationId']}")
            require(all(by_key.get(key, {}).get("side") == relation["targetSide"] for key in relation["targetSourceKeys"]),
                    f"exact relation crosses sides: {relation['relationId']}")
        else:
            require(relation["targetSide"] is None, f"literature relation claims exact side: {relation['relationId']}")
            sides = {by_key.get(key, {}).get("side") for key in relation["targetSourceKeys"]}
            require(sides == {"left", "right"}, f"literature concept does not list both existing sides: {relation['relationId']}")
            require(relation["basis"] == "literature_concept_motor_relation", f"non-exact relation claims geometric binding: {relation['relationId']}")
    for name in ("Lateral femoral cutaneous nerve", "Posterior femoral cutaneous nerve"):
        concept = next((row for row in graph["concepts"] if row["names"]["en"] == name), None)
        require(concept is not None, f"missing distinct sensory concept: {name}")
        if concept:
            require(concept["functionEvidenceClass"] == "sensory_course_documented_no_motor_relation", f"sensory state mismatch: {name}")
            require(not any(row["nerveKey"] == concept["key"] for row in graph["motorRelations"]), f"cutaneous nerve assigned motor relation: {name}")
    deep = [row for row in exact_rows if row["nerveKey"] == "deep-fibular"]
    require({row["targetSide"] for row in deep} == {"left", "right"}, "existing deep fibular bilateral relation is incomplete")
    require(all(any("tibialis anterior" in by_key.get(key, {}).get("names", {}).get("en", "").lower() for key in row["targetSourceKeys"]) for row in deep),
            "existing deep fibular relation does not target tibialis anterior")

    snapshots = ledger["sourceSnapshot"]
    require(snapshots["nerveSupportSha256"] == sha(ROOT / "atlas-data/overlays/nerve-support-t66.json"), "nerve source overlay hash changed")
    require(snapshots["zaIntegrationSha256"] == sha(ROOT / "atlas-data/overlays/za-local-integration.json"), "muscle integration hash changed")
    for field_key, item in ledger["learnerFieldEvidence"].items():
        nerve_name, field_name = field_key.split(":", 1)
        value = course.get(nerve_name, {}).get(field_name)
        require(isinstance(value, str) and hashlib.sha256(value.encode()).hexdigest() == item["valueSha256"],
                f"learner field evidence hash mismatch: {field_key}")
        require(bool(item["sourceIds"]) and all(source_id in ledger["sourceRecords"] for source_id in item["sourceIds"]),
                f"learner field lacks source record: {field_key}")
    policy = ledger["preservedPolicy"]
    require(policy["sourceOnly"] is True and policy["localSelection"] == "verified_geometry_only", "source/local-selection policy changed")
    require(policy["humanReview"] == "not_performed" and policy["publicRedistribution"] == "held", "review or rights hold changed")
    require(policy["newCanonicalBindings"] == 0 and policy["newNerveGeometry"] == 0 and policy["newBranchCoordinates"] == 0,
            "new canonical/geometry/branch coordinates were introduced")
    if findings:
        raise SystemExit("; ".join(findings))

    result = {
        "schemaVersion": "t66-nerve-learning-validation-v1",
        "status": "passed" if not findings else "failed",
        "inputHashes": {
            "graph": sha(ROOT / "atlas-data/terminology/learner-nerve-graph-t66.json"),
            "course": sha(ROOT / "atlas-data/terminology/nerve-learning-t66.json"),
            "nerveSupport": sha(ROOT / "atlas-data/overlays/nerve-support-t66.json"),
            "integration": sha(ROOT / "atlas-data/overlays/za-local-integration.json"),
            "ledger": sha(EVIDENCE / "nerve-relation-ledger.json"),
        },
        "sourceInventory": {"staticSourceSurfaces": len(support["instances"]), "sourceLabelGroups": len(source_labels), "independentAnatomyConceptCount": "not_inferred_from_label_groups"},
        "relationshipCounts": {
            "exactSideGeometryRows": len(exact_rows),
            "literatureConceptRows": len(literature_rows),
            "allRelationRows": len(graph["motorRelations"]),
            "uniqueNerveKeysInRelations": len({row["nerveKey"] for row in graph["motorRelations"]}),
            "uniqueTargetSourceKeys": len({key for row in graph["motorRelations"] for key in row["targetSourceKeys"]}),
        },
        "negativeScope": {"LFCNMotorRows": 0, "PFCNMotorRows": 0, "newNerveGeometry": 0, "newBranchCoordinates": 0},
        "policy": policy,
        "findings": findings,
    }
    output = EVIDENCE / "validation.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "relationshipCounts": result["relationshipCounts"], "findings": findings}, ensure_ascii=False))
    if findings:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
