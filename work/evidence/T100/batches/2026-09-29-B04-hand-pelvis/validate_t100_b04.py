#!/usr/bin/env python3
"""Strict offline validator for the bounded T100-B04 overlay revision."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
BASELINE = json.loads((HERE / "start-baseline.json").read_text())
EXPECTED = ["TA2:1263", "TA2:1264", "TA2:1265", "TA2:1271", "TA2:1272", "TA2:1277", "TA2:1278", "TA2:1279", "TA2:1281", "TA2:1282"]
REVISION = "c7010a903b75a2fd24a13b1c2c4c3546a9223780"
SOURCE_HASH = "9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd"
OVERLAY_REL = "atlas-data/overlays/za-local-integration.json"
OVERLAY = ROOT / OVERLAY_REL
RESULT = HERE / "validation.json"


def sha_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def sha(path):
    return sha_bytes(path.read_bytes())


def read(path):
    return json.loads(path.read_text())


def fail(message):
    raise SystemExit("T100-B04 validation failed: " + message)


def main():
    scope = read(ROOT / "atlas-data/catalog/target-scope-t96.json")
    catalog = read(ROOT / "work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json")
    rawmeta = read(ROOT / "work/evidence/T100/resolution-2026-09-29/source-metadata.json")
    remaining = read(ROOT / "work/evidence/T100/resolution-2026-09-29/remaining-targets.json")
    compiled = ROOT / "atlas-data/source-cache/datasets/za/compiled/manifest.json"
    batch_scope = read(HERE / "batch-scope.json")
    ledger = read(HERE / "term-and-correspondence-ledger.json")
    corr = read(HERE / "structure-correspondence.json")
    observations = read(HERE / "source-query-observations.json")
    overlay = read(OVERLAY)
    base_raw = subprocess.check_output(["git", "show", f"{BASELINE['startingHead']}:{OVERLAY_REL}"], cwd=ROOT)
    before = json.loads(base_raw)

    if BASELINE["previousBatchGate"] != "pass" or BASELINE["startingHead"] != BASELINE["previousBatchCommit"]:
        fail("B03 precondition not satisfied")
    if batch_scope["status"] != "frozen_before_investigation" or batch_scope["targetIds"] != EXPECTED:
        fail("frozen ten-target B04 scope changed")
    if sha(ROOT / batch_scope["frozenRemainder"]["path"]) != batch_scope["frozenRemainder"]["sha256"]:
        fail("frozen historical remainder hash changed")
    for rel, expected_hash in BASELINE["frozenInputSha256"].items():
        if rel == OVERLAY_REL:
            continue
        if sha(ROOT / rel) != expected_hash:
            fail(f"immutable source hash changed: {rel}")
    if sha_bytes(base_raw) != BASELINE["frozenInputSha256"][OVERLAY_REL]:
        fail("B03 overlay bytes changed")
    if scope["revision"] != "T96-2026-09-28-semantic-freeze-v1" or len(scope["targets"]) != 542:
        fail("frozen T96 target scope differs")
    if catalog["sourceRevision"] != REVISION or catalog["sourceHash"] != SOURCE_HASH or len(catalog["objects"]) != 960:
        fail("pinned Z-Anatomy source identity/count differs")
    if remaining["targets"] != 542 or len(remaining["unresolved"]) != 182:
        fail("historical remainder/target count differs")
    if overlay["scope"] != {"targets": 542, "memberships": 563, "regions": 12}:
        fail("frozen denominators changed")
    if overlay["revision"] != "T100-source-taxonomy-local-display-v1-B04-hand-pelvis":
        fail("overlay revision not B04")
    if len(overlay["objects"]) != 960 or len(before["objects"]) != 960:
        fail("source object row count changed")
    if [x["targetId"] for x in ledger["targets"]] != EXPECTED:
        fail("ledger targets/order differ from frozen scope")
    if ledger["scope"]["historicalRemainingCountAtBatchStart"] != 182 or ledger["scope"]["frozenOffsets"] != [20, 30]:
        fail("ledger does not preserve original B04 remainder/offset")
    if ledger["scope"]["taskTargetDenominator"] != 542 or ledger["scope"]["taskRegionMembershipDenominator"] != 563:
        fail("ledger changed whole-body denominators")

    source_ids = {x["id"] for x in ledger["sourceEvidence"]}
    if len(source_ids) != 9 or len(overlay["evidenceSources"]) != len(before["evidenceSources"]) + 9:
        fail("expected two pinned sources and seven opened KMLE query sources")
    if not source_ids <= {x["id"] for x in overlay["evidenceSources"]}:
        fail("ledger provenance IDs missing from overlay")
    for source in ledger["sourceEvidence"]:
        if source["id"].startswith("kmle-"):
            if source["exactEdition"] is not None or source.get("openedOriginalDictionaryRecord") is not False or source["accessMethod"] != "opened_html":
                fail(f"KMLE source layer/edition misrepresented: {source['id']}")
            if not source["url"].startswith("https://m.kmle.co.kr/search.php?Search="):
                fail(f"KMLE aggregate URL missing: {source['id']}")
    if len(observations["observations"]) != 7 or observations["hanjaCopied"] is not False:
        fail("terminology source observations/Hanja policy changed")
    for obs in observations["observations"]:
        if obs["accessMethod"] != "opened_html" or obs["edition"] is not None or obs["openedOriginalDictionaryRecord"] is not False:
            fail(f"source query access classification differs: {obs['id']}")

    target_source = {x["id"]: x for x in scope["targets"]}
    terms = {x["targetId"]: x for x in ledger["targets"]}
    counts_expected = {"TA2:1263": 0, "TA2:1264": 10, "TA2:1265": 10, "TA2:1271": 27,
                      "TA2:1272": 27, "TA2:1277": 10, "TA2:1278": 8, "TA2:1279": 9,
                      "TA2:1281": 0, "TA2:1282": 0}
    if ledger["memberCountsByTarget"] != counts_expected or corr["memberCountsByTarget"] != counts_expected:
        fail("target relation cardinalities differ")
    if len(ledger["crosswalkRelations"]) != 101 or corr["exactOverlayRelations"] != 101 or corr["sourceObjectMembers"] != 37:
        fail("expected 101 relations over 37 unique source objects")
    if corr["historicalRemainderAfterB04Disposition"] != 152 or corr["historicalRemainingAtBatchStart"] != 182:
        fail("historical remainder accounting differs")
    if corr["inputDenominators"] != {"targets": 542, "memberships": 563, "regions": 12}:
        fail("correspondence evidence denominator changed")

    catalog_rows = {x["sourceKey"]: x for x in catalog["objects"]}
    meta_rows = {x["name"]: x for x in rawmeta["objects"]}
    overlay_after = {x["sourceKey"]: x for x in overlay["objects"]}
    overlay_before = {x["sourceKey"]: x for x in before["objects"]}
    if set(overlay_after) != set(overlay_before):
        fail("source object identity set changed")
    for key in overlay_before:
        old, new = overlay_before[key], overlay_after[key]
        if old["sourceName"] != new["sourceName"]:
            fail("source object name changed")
        changed = {k for k in set(old) | set(new) if old.get(k) != new.get(k)}
        old_rel = old.get("targetRelationEvidence", [])
        new_rel = new.get("targetRelationEvidence", [])
        old_b04 = [r for r in old_rel if r.get("targetId") in EXPECTED]
        new_b04 = [r for r in new_rel if r.get("targetId") in EXPECTED]
        if old_b04:
            fail("B04 relation existed in baseline")
        if new_b04:
            if changed - {"targetIds", "targetRelationEvidence"}:
                fail(f"non-evidence source object field changed: {new['sourceName']} {sorted(changed)}")
        elif changed:
            fail(f"out-of-scope object row changed: {new['sourceName']} {sorted(changed)}")
        for protected in ("haConceptId", "sourceOnly", "humanReview", "publicRedistribution", "localUseRights",
                          "mappingStatus", "localDisplayEligible", "inspectionEligible", "defaultVisible", "bounds",
                          "side", "regionIds", "names", "aliases", "nameEvidence"):
            if old.get(protected) != new.get(protected):
                fail(f"protected learning/review/display field changed: {new['sourceName']}.{protected}")

    relations = ledger["crosswalkRelations"]
    relation_pairs = [(x["targetId"], x["sourceKey"]) for x in relations]
    if len(relation_pairs) != len(set(relation_pairs)):
        fail("duplicate target-source relations")
    counts_actual = {target_id: sum(r["targetId"] == target_id for r in relations) for target_id in EXPECTED}
    if counts_actual != counts_expected:
        fail("ledger relation counts do not reconcile")
    for wrapped in relations:
        rel = wrapped
        key = rel["sourceKey"]
        obj = catalog_rows.get(key)
        row = overlay_after.get(key)
        if not obj or not row or obj["name"] != rel["sourceObjectName"] or row["sourceName"] != rel["sourceObjectName"]:
            fail("source key/name mismatch")
        if rel["sourceHash"] != SOURCE_HASH or rel["sourceRevision"] != REVISION or rel["evaluatedGeometrySha256"] != obj["evaluatedGeometrySha256"]:
            fail(f"source/evaluated hash mismatch: {rel['sourceObjectName']}")
        raw = meta_rows.get(rel["sourceObjectName"])
        if not raw or (raw["parent"], raw["collections"]) != (rel["sourceParent"], rel["sourceCollections"]):
            fail(f"raw parent/collection mismatch: {rel['sourceObjectName']}")
        if (obj["dataName"], obj["parent"], obj["collections"], obj["sourceLabelSide"]) != (rel["sourceDataName"], rel["sourceParent"], rel["sourceCollections"], rel["sourceSide"]):
            fail(f"catalogue data/side mismatch: {rel['sourceObjectName']}")
        if rel["relationKind"] != "class_member" or rel["upstreamFjOrTa2IdClaim"] or rel["canonicalHaBindingCreated"] or rel["humanReview"] != "not_performed":
            fail(f"unsupported source identity/review promotion: {rel['sourceObjectName']}")
        if rel["directObjectNameMatch"] or rel["ancestorNameAloneUsed"] or rel["targetId"] not in EXPECTED:
            fail(f"unsupported relation basis/scope: {rel['sourceObjectName']}")
        if not set(rel["matchEvidenceSourceIds"]) <= source_ids:
            fail(f"relation evidence source refs missing: {rel['sourceObjectName']}")
        if rel["targetId"] not in row["targetIds"] or not any(r.get("targetId") == rel["targetId"] for r in row.get("targetRelationEvidence", [])):
            fail(f"overlay relation projection absent: {rel['sourceObjectName']}")
        match = re.fullmatch(r"(?:Proximal|Middle|Distal) phalanx of (?:first|second|third|fourth|fifth) finger of hand\.([lr])", rel["sourceObjectName"], re.I)
        meta_match = re.fullmatch(r"(?:First|Second|Third|Fourth|Fifth) metacarpal bone\.([lr])", rel["sourceObjectName"], re.I)
        if match or meta_match:
            code = (match or meta_match).group(1).lower()
            side = {"l": "left", "r": "right"}[code]
            expected_limb = "Left upper limb" if side == "left" else "Right upper limb"
            if rel["sourceSide"] != side or expected_limb not in rel["sourceCollections"]:
                fail(f"side must match exact suffix, label and limb hierarchy: {rel['sourceObjectName']}")
            if rel["sourceParent"] != "Bones of free part of upper limb.g":
                fail(f"source parent differs: {rel['sourceObjectName']}")
            if "Right hand" in rel["sourceCollections"] and side == "left" and "Left upper limb" not in rel["sourceCollections"]:
                fail("Right hand collection used to infer left side")
        if rel["sourceObjectName"] == "Distal phalanx of fifth finger of hand.l":
            fail("known dataName conflict was incorrectly linked")

    expected_terms = {x["id"]: x for x in scope["targets"] if x["id"] in EXPECTED}
    overlay_terms = {x["targetId"]: x for x in overlay["targetTerminologyEvidence"]}
    baseline_terms = {x["targetId"] for x in before["targetTerminologyEvidence"]}
    if set(overlay_terms) - baseline_terms != set(EXPECTED):
        fail("overlay target terminology delta is not exactly B04")
    for target_id in EXPECTED:
        term, frozen = terms[target_id], expected_terms[target_id]
        if term["english"] != frozen["term"]["english"] or term["latin"] != frozen["term"]["latin"]:
            fail(f"frozen TA2 English/Latin mismatch: {target_id}")
        if term["semanticKind"] != frozen["semanticKind"] or term["regionIds"] != frozen["regionIds"]:
            fail(f"frozen target classification/region mismatch: {target_id}")
        for field_name, value_key in (("koModern", "koModern"), ("koTraditional", "koTraditional")):
            evidence = term["fieldEvidence"][field_name]
            if evidence["value"] != term["names"][value_key]:
                fail(f"Korean field value/name mismatch: {target_id} {field_name}")
            if evidence["value"] is None and (evidence["status"] != "missing" or not evidence["missingReason"]):
                fail(f"missing Korean field lacks reason: {target_id} {field_name}")
            if evidence["value"] is not None and (evidence["status"] != "evidence_backed" or not evidence["locator"]):
                fail(f"Korean field lacks locator: {target_id} {field_name}")
            if any(sid not in source_ids for sid in evidence["sourceIds"]):
                fail(f"Korean field references unknown source: {target_id} {field_name}")
        hanja = term["fieldEvidence"]["hanja"]
        if hanja["status"] != "not_collected" or hanja["value"] is not None:
            fail(f"Hanja collection policy violated: {target_id}")
        if term["sourceOnly"] is not True or term["humanReview"] != "not_performed" or term["publicRedistribution"] != "held":
            fail(f"review/rights/sourceOnly promoted: {target_id}")
        if term["learnerBindingCreated"] or term["canonicalHaConceptId"] is not None or term["newGeometryCreated"]:
            fail(f"learner binding/canonical ID/geometry created: {target_id}")
        projected = overlay_terms[target_id]
        if projected["names"] != term["names"] or projected["fieldEvidence"] != term["fieldEvidence"]:
            fail(f"internal overlay term differs from ledger: {target_id}")
        if target_id in ("TA2:1263", "TA2:1281", "TA2:1282") and counts_actual[target_id] != 0:
            fail(f"unresolved target has direct source relation: {target_id}")
    target_1282 = terms["TA2:1282"]
    target_1281 = terms["TA2:1281"]
    if target_1282["existingSurface"]["exactTargetRelationAdded"] is not False or len(target_1282["existingSurface"]["observedCollectionMembers"]) != 4:
        fail("bony pelvis observations were asserted as a target crosswalk or omitted")
    if target_1281["existingSurface"]["excludedWrongRegionObjects"][0]["sourceObjectName"] != "Sesamoid bones of foot.l":
        fail("wrong-region sesamoid comparator was not explicitly excluded")
    if len(terms["TA2:1279"]["existingSurface"]["excludedMembers"]) != 1:
        fail("distal-phalanx identity conflict not retained")
    for term in terms.values():
        for candidate in term["unappliedTermCandidates"]:
            if candidate["status"] == "evidence_backed":
                fail("unapplied candidate promoted")
            if candidate["sourceId"] not in source_ids:
                fail("candidate source ID missing")

    han_pattern = re.compile(r"[\u3400-\u9fff]")
    for term in terms.values():
        strings = [term["names"].get("koModern"), term["names"].get("koTraditional")]
        if any(isinstance(s, str) and han_pattern.search(s) for s in strings):
            fail(f"actual Hanja glyph copied: {term['targetId']}")

    if sha(OVERLAY) != corr["overlaySha256"]:
        fail("overlay hash in correspondence evidence differs")
    if corr["targetsWithExactRelations"] != ["TA2:1264", "TA2:1265", "TA2:1271", "TA2:1272", "TA2:1277", "TA2:1278", "TA2:1279"]:
        fail("target direct-relationship summary differs")
    if corr["targetsWithoutExactRelations"] != ["TA2:1263", "TA2:1281", "TA2:1282"]:
        fail("target missing relationship summary differs")
    if corr["preservedCounts"]["sourceObjects"] != 960 or corr["preservedCounts"]["publicRedistribution"] != "held" or corr["preservedCounts"]["humanReview"] != "not_performed":
        fail("source/review/right summary changed")

    result = {
        "status": "pass", "batchId": "T100-B04-hand-pelvis", "targets": 10,
        "exactRelations": 101, "uniqueSourceObjects": 37, "membersByTarget": counts_actual,
        "targetsWithNoDirectRelation": ["TA2:1263", "TA2:1281", "TA2:1282"],
        "phalanxIdentityConflictsExcluded": 1, "pelvisCandidateMembersNotCrosswalked": 4,
        "handSesamoidWrongRegionMeshesExcluded": 2,
        "historicalRemainderAfterDisposition": 152,
        "frozenDenominators": {"targets": 542, "memberships": 563, "regions": 12},
        "sourceObjects": 960, "humanReview": "not_performed", "publicRedistribution": "held", "sourceOnly": True,
        "overlaySha256": sha(OVERLAY),
        "baselineFrozenInputsUnchanged": [k for k in BASELINE["frozenInputSha256"] if k != OVERLAY_REL],
        "learningNamesOrAliasesChanged": False, "canonicalIdsCreated": False, "newGeometryCreated": False,
        "hanjaCopied": False, "termSourceQueryPagesOpened": 7, "underlyingDictionaryRecordsOpened": 0,
        "remainingT100NextUnit": "resolve-remaining-target-part-synonym-coverage-and-korean-name-gaps",
    }
    RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
