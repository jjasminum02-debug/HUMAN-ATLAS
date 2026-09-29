#!/usr/bin/env python3
"""Validate T100-B02 scope, source evidence, exact relations and preservation."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
BASELINE = json.loads((HERE / "start-baseline.json").read_text())
OVERLAY_REL = "atlas-data/overlays/za-local-integration.json"
OVERLAY_PATH = ROOT / OVERLAY_REL
SCOPE_PATH = ROOT / "atlas-data/catalog/target-scope-t96.json"
REMAINING_PATH = ROOT / "work/evidence/T100/resolution-2026-09-29/remaining-targets.json"
CATALOG_PATH = ROOT / "work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json"
META_PATH = ROOT / "work/evidence/T100/resolution-2026-09-29/source-metadata.json"
LEDGER_PATH = HERE / "term-and-correspondence-ledger.json"
CORR_PATH = HERE / "structure-correspondence.json"
EXPECTED = ["TA2:356", "TA2:819", "TA2:830", "TA2:831", "TA2:832",
            "TA2:1032", "TA2:1038", "TA2:1050", "TA2:1059", "TA2:1065"]
SOURCE_SHA = "9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd"
REVISION = "c7010a903b75a2fd24a13b1c2c4c3546a9223780"
MUTABLE_ROW_FIELDS = {"label", "names", "aliases", "nameSourceIds", "nameEvidence", "targetIds", "targetRelationEvidence"}


def read(path: Path):
    return json.loads(path.read_text())


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str):
    raise SystemExit("FAIL: " + message)


def main():
    for rel, expected in BASELINE["inputSha256"].items():
        if sha(ROOT / rel) != expected:
            fail(f"immutable input hash changed: {rel}")
    raw_before = subprocess.check_output(["git", "show", f"{BASELINE['startingHead']}:{OVERLAY_REL}"], cwd=ROOT)
    if hashlib.sha256(raw_before).hexdigest() != BASELINE["contextBaselineSha256"][OVERLAY_REL]:
        fail("starting overlay hash differs from recorded baseline")
    before, after = json.loads(raw_before), read(OVERLAY_PATH)
    scope, remaining, catalog, meta = read(SCOPE_PATH), read(REMAINING_PATH), read(CATALOG_PATH), read(META_PATH)
    ledger, corr = read(LEDGER_PATH), read(CORR_PATH)
    if scope["revision"] != "T96-2026-09-28-semantic-freeze-v1" or len(scope["targets"]) != 542:
        fail("T96 target freeze/denominator changed")
    if before["scope"] != {"targets": 542, "memberships": 563, "regions": 12} or after["scope"] != before["scope"]:
        fail("T96 integration denominator changed")
    if len(before["objects"]) != 960 or len(after["objects"]) != 960:
        fail("source object count changed")
    if (after["policy"]["publicRedistribution"], after["policy"]["humanReview"], after["sourceHash"]) != (
        "held", "not_performed", SOURCE_SHA
    ):
        fail("release/review/source hash policy changed")
    if ledger["scope"]["targetCount"] != 10 or ledger["scope"]["requestedTargetIds"] != EXPECTED:
        fail("B02 target subset differs from requested batch")
    if len(ledger["targets"]) != 10 or [x["targetId"] for x in ledger["targets"]] != EXPECTED:
        fail("B02 target classifications are incomplete or out of order")
    if ledger["scope"]["taskTargetDenominator"] != 542 or ledger["scope"]["taskRegionMembershipDenominator"] != 563:
        fail("B02 changed the frozen denominator")
    if ledger["scope"]["zaSourceFileSha256"] != SOURCE_SHA or ledger["scope"]["zaSourceRevision"] != REVISION:
        fail("pinned ZA source identity differs")
    if remaining["targets"] != 542 or len(remaining["unresolved"]) != 182:
        fail("historical unresolved denominator was modified")
    if not set(EXPECTED) <= {row["targetId"] for row in remaining["unresolved"]}:
        fail("B02 targets are not a subset of the frozen unresolved ledger")
    if ledger["scope"]["historicalRemainingCountAtBatchStart"] != 182 or corr["historicalRemainingAtBatchStart"] != 182 or corr["historicalRemainderAfterB02DispositionPass"] != 172:
        fail("B02 disposition progress count mismatch")

    source_refs = {s["id"]: s for s in after.get("evidenceSources", [])}
    if len(source_refs) != len(after.get("evidenceSources", [])):
        fail("duplicate evidence source IDs")
    terms = {x["targetId"]: x for x in after.get("targetTerminologyEvidence", [])}
    if set(terms) != set(EXPECTED):
        fail("overlay target terminology rows do not match exact B02 scope")
    for term in ledger["targets"]:
        if (term["learnerBindingCreated"], term["canonicalHaConceptId"], term["sourceOnly"],
            term["humanReview"], term["publicRedistribution"], term["newGeometryCreated"]) != (
            False, None, True, "not_performed", "held", False
        ):
            fail(f"target promotion/geometry hold changed: {term['targetId']}")
        if terms[term["targetId"]] != term:
            fail(f"overlay terminology evidence differs from ledger: {term['targetId']}")
        for field, evidence in term["fieldEvidence"].items():
            if any(source_id not in source_refs for source_id in evidence["sourceIds"]):
                fail(f"field evidence has missing source ref: {term['targetId']} {field}")
            for source_id in evidence["sourceIds"]:
                source = source_refs[source_id]
                if not source["url"].startswith("https://") or not source["editionExposure"] or not source["locator"].strip():
                    fail(f"source provenance incomplete: {source_id}")
            if evidence["status"] == "evidence_backed" and (not evidence["value"] or not evidence["locator"] or not evidence["sourceIds"]):
                fail(f"evidence-backed field has no value/locator: {term['targetId']} {field}")
            if evidence["status"] == "missing" and (evidence["value"] is not None or not evidence["missingReason"]):
                fail(f"missing field was filled or lacks reason: {term['targetId']} {field}")
        for ko in (term["names"]["koModern"], term["names"]["koTraditional"]):
            if ko and re.search(r"[\u3400-\u9fff]", ko):
                fail(f"raw Hanja exposed in Korean name: {term['targetId']}")

    source_objects = {o["sourceKey"]: o for o in catalog["objects"]}
    source_meta = {o["name"]: o for o in meta["objects"]}
    before_rows = {o["sourceKey"]: o for o in before["objects"]}
    after_rows = {o["sourceKey"]: o for o in after["objects"]}
    if set(before_rows) != set(after_rows) or set(after_rows) != set(source_objects):
        fail("source identities changed")
    all_relations = [(row, relation) for row in after["objects"] for relation in row.get("targetRelationEvidence", [])]
    b02_relations = [(row, rel) for row, rel in all_relations if rel["targetId"] in EXPECTED]
    expected_counts = {"TA2:1032": 5, "TA2:1038": 1, "TA2:1050": 1, "TA2:1059": 12}
    if len(b02_relations) != 19:
        fail("B02 must contain exactly 19 object relations")
    if {target: sum(rel["targetId"] == target for _, rel in b02_relations) for target in expected_counts} != expected_counts:
        fail("B02 member count mismatch")
    for key, old in before_rows.items():
        new = after_rows[key]
        changed = {k for k in set(old) | set(new) if old.get(k) != new.get(k)}
        expected_changed = MUTABLE_ROW_FIELDS if key in {r["sourceKey"] for r, _ in b02_relations} else set()
        if changed - expected_changed:
            fail(f"unexpected overlay row mutation: {key}: {sorted(changed - expected_changed)}")
        for protected in ("haConceptId", "sourceOnly", "humanReview", "publicRedistribution", "localUseRights",
                          "mappingStatus", "localDisplayEligible", "inspectionEligible", "defaultVisible", "bounds", "side", "regionIds"):
            if new.get(protected) != old.get(protected):
                fail(f"protected row state changed: {key}.{protected}")

    for row, relation in b02_relations:
        source = source_objects.get(relation["sourceKey"])
        if not source or row["sourceKey"] != relation["sourceKey"] or row["sourceName"] != relation["sourceObjectName"]:
            fail("crosswalk source identity mismatch")
        if relation["sourceHash"] != SOURCE_SHA or relation["sourceRevision"] != REVISION:
            fail(f"source hash/revision mismatch: {relation['sourceObjectName']}")
        if relation["evaluatedGeometrySha256"] != source["evaluatedGeometrySha256"]:
            fail(f"evaluated geometry hash mismatch: {relation['sourceObjectName']}")
        if relation["sourceParent"] != source["parent"] or relation["sourceCollections"] != source["collections"]:
            fail(f"source hierarchy mismatch: {relation['sourceObjectName']}")
        raw = source_meta[relation["sourceObjectName"]]
        if raw["parent"] != relation["sourceParent"] or raw["collections"] != relation["sourceCollections"]:
            fail(f"raw source metadata hierarchy mismatch: {relation['sourceObjectName']}")
        if relation["directObjectNameMatch"] or relation["ancestorNameAloneUsed"] or relation["upstreamFjOrTa2IdClaim"] or relation["canonicalHaBindingCreated"]:
            fail(f"unsupported name-only or identity promotion: {relation['sourceObjectName']}")
        if relation["targetId"] not in row["targetIds"] or row["haConceptId"] is not None or not row["sourceOnly"]:
            fail(f"learner binding/source-only changed: {relation['sourceObjectName']}")

    if {rel["targetId"] for _, rel in b02_relations} != set(expected_counts):
        fail("missing/group/variant/subset concept got an invented surface relation")
    if len(ledger["exactSourceNameInventory"]) != 5 or any(x["status"] != "exact_source_object_absent" for x in ledger["exactSourceNameInventory"]):
        fail("exact group/variant source inventory is incomplete")
    if corr["exactOverlayRelations"] != 19 or corr["sourceObjectMembers"] != 19:
        fail("crosswalk summary counts mismatch")
    if corr["preservedCounts"]["sourceObjects"] != 960 or corr["preservedCounts"]["locallyDisplayable"] != 672 or corr["preservedCounts"]["haBoundRows"] != 130:
        fail("local evidence changed source/display/binding counts")
    if sha(OVERLAY_PATH) != corr["overlaySha256"]:
        fail("overlay hash in evidence does not match actual bytes")
    print(json.dumps({"status": "pass", "batchId": ledger["batchId"], "targets": 10, "exactRelations": 19,
                      "unmappedTargets": 6, "sourceObjects": 960, "locallyDisplayable": 672,
                      "haBoundRows": 130, "overlaySha256": corr["overlaySha256"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
