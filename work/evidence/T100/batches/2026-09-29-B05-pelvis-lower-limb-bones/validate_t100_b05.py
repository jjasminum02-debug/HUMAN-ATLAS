#!/usr/bin/env python3
"""Strict offline validator for the frozen T100-B05 terminology/member overlay."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
BASELINE = json.loads((HERE / "start-baseline.json").read_text())
EXPECTED = ["TA2:1317", "TA2:1339", "TA2:1346", "TA2:1389", "TA2:1493", "TA2:1494", "TA2:1496", "TA2:1505", "TA2:1510", "TA2:1511"]
REVISION = "c7010a903b75a2fd24a13b1c2c4c3546a9223780"
SOURCE_HASH = "9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd"
OVERLAY_REL = "atlas-data/overlays/za-local-integration.json"


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def read(path: Path):
    return json.loads(path.read_text())


def fail(message: str):
    raise SystemExit("T100-B05 validation failed: " + message)


def main():
    scope = read(ROOT / "atlas-data/catalog/target-scope-t96.json")
    catalog = read(ROOT / "work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json")
    rawmeta = read(ROOT / "work/evidence/T100/resolution-2026-09-29/source-metadata.json")
    remainder = read(ROOT / "work/evidence/T100/resolution-2026-09-29/remaining-targets.json")
    compiled = read(ROOT / "atlas-data/source-cache/datasets/za/compiled/manifest.json")
    frozen = read(HERE / "batch-scope.json")
    ledger = read(HERE / "term-and-correspondence-ledger.json")
    corr = read(HERE / "structure-correspondence.json")
    observations = read(HERE / "source-query-observations.json")
    overlay = read(ROOT / OVERLAY_REL)
    before_raw = subprocess.check_output(["git", "show", f"{BASELINE['startingHead']}:{OVERLAY_REL}"], cwd=ROOT)
    before = json.loads(before_raw)

    if frozen["status"] != "frozen_before_investigation" or frozen["targetIds"] != EXPECTED:
        fail("frozen ten-target scope changed")
    if frozen["predecessorGate"]["result"] != "pass" or frozen["predecessorGate"]["commit"] != BASELINE["startingHead"]:
        fail("B04 predecessor gate/commit differs")
    if sha(ROOT / frozen["frozenRemainder"]["path"]) != frozen["frozenRemainder"]["sha256"]:
        fail("frozen T100 remainder changed")
    for rel, expected_hash in BASELINE["frozenInputs"].items():
        if rel != OVERLAY_REL and sha(ROOT / rel) != expected_hash:
            fail(f"immutable input hash changed: {rel}")
    if sha_bytes(before_raw) != BASELINE["frozenInputs"][OVERLAY_REL]:
        fail("B04 historical overlay bytes changed")
    if scope["revision"] != "T96-2026-09-28-semantic-freeze-v1" or len(scope["targets"]) != 542:
        fail("T96 target scope/count changed")
    if remainder["targets"] != 542 or len(remainder["unresolved"]) != 182:
        fail("historical original 182-entry remainder was mutated")
    if catalog["sourceRevision"] != REVISION or catalog["sourceHash"] != SOURCE_HASH or len(catalog["objects"]) != 960:
        fail("pinned source catalog identity/count changed")
    if compiled["revision"] != overlay["datasetRevision"] or compiled["sourceHash"] != SOURCE_HASH or len(compiled["instances"]) != 960:
        fail("compiled source manifest identity/count changed")
    if overlay["revision"] != "T100-source-taxonomy-local-display-v1-B05-pelvis-lower-limb-bones":
        fail("overlay revision is not B05")
    if overlay["scope"] != {"targets": 542, "memberships": 563, "regions": 12}:
        fail("fixed T96 denominators changed")
    if overlay["sourceHash"] != SOURCE_HASH or len(overlay["objects"]) != 960:
        fail("overlay source bytes/object denominator changed")
    if frozen["targetScopeSha256"] != "bdf7879754e4dc1f3da164488ab6d6418dfd05a642d14f6d08561b41474955f8":
        fail("frozen target-scope hash changed")

    source_ids = {row["id"] for row in ledger["sourceEvidence"]}
    projected_sources = {row["id"]: row for row in overlay["evidenceSources"]}
    baseline_source_ids = {row["id"] for row in before["evidenceSources"]}
    if len(source_ids) != 12 or source_ids & baseline_source_ids:
        fail("expected 2 frozen-source refs plus 10 distinct field-source records")
    if source_ids - set(projected_sources):
        fail("B05 provenance rows missing from overlay")
    for source in ledger["sourceEvidence"]:
        if projected_sources[source["id"]] != source:
            fail(f"overlay/source ledger provenance differs: {source['id']}")
        if source["id"].startswith("kmle-") and source["exactEdition"] is not None:
            fail(f"KMLE edition was invented: {source['id']}")
        if source["accessMethod"] not in {"opened_html", "opened_pdf", "search_index_excerpt", "local_frozen_metadata"}:
            fail(f"source access layer invalid: {source['id']}")
    if len(observations["observations"]) != 12 or observations["hanjaCopied"] is not False or observations["newArchiveOrSourceDownload"] is not False:
        fail("source observations/Hanja/download policy differs")
    for observation in observations["observations"]:
        if observation["accessDate"] != "2026-09-29":
            fail(f"source observation date differs: {observation['id']}")
        if observation["id"].startswith("kmle-") and observation["openedOriginalDictionaryRecord"] is not False:
            fail(f"KMLE aggregate/index layer represented as an original dictionary record: {observation['id']}")
    if not observations["sourceKindSeparation"]["humanAnatomyReview"].startswith("not_performed"):
        fail("human anatomy review status was promoted")

    by_id = {row["id"]: row for row in scope["targets"]}
    expected_counts = {"TA2:1317": 0, "TA2:1339": 0, "TA2:1346": 0, "TA2:1389": 2, "TA2:1493": 0,
                       "TA2:1494": 0, "TA2:1496": 10, "TA2:1505": 28, "TA2:1510": 10, "TA2:1511": 8}
    if ledger["memberCountsByTarget"] != expected_counts or corr["memberCountsByTarget"] != expected_counts:
        fail("per-target relation counts differ")
    if len(ledger["targets"]) != 10 or [row["targetId"] for row in ledger["targets"]] != EXPECTED:
        fail("ledger target list/order differs")
    if len(ledger["crosswalkRelations"]) != 58 or corr["exactOverlayRelations"] != 58 or corr["sourceObjectMembers"] != 40:
        fail("expected 58 relations over 40 unique source objects")
    if corr["historicalRemainderAtBatchStart"] != 152 or corr["historicalRemainderAfterB05Disposition"] != 142:
        fail("batch-local historical disposition count differs")
    if corr["inputDenominators"] != {"targets": 542, "memberships": 563, "regions": 12}:
        fail("correspondence denominator changed")

    catalog_by_key = {row["sourceKey"]: row for row in catalog["objects"]}
    meta_by_name = {row["name"]: row for row in rawmeta["objects"]}
    overlay_after = {row["sourceKey"]: row for row in overlay["objects"]}
    overlay_before = {row["sourceKey"]: row for row in before["objects"]}
    if set(overlay_after) != set(overlay_before) or set(overlay_after) != set(catalog_by_key):
        fail("source object identity set changed")

    relation_pairs = [(row["targetId"], row["sourceKey"]) for row in ledger["crosswalkRelations"]]
    if len(relation_pairs) != len(set(relation_pairs)):
        fail("duplicate target/member relation")
    if {target_id: sum(row["targetId"] == target_id for row in ledger["crosswalkRelations"]) for target_id in EXPECTED} != expected_counts:
        fail("ledger relation cardinalities do not reconcile")

    relation_sources: dict[str, set[str]] = {}
    for wrapped in ledger["crosswalkRelations"]:
        relation = wrapped
        key, name = relation["sourceKey"], relation["sourceObjectName"]
        source = catalog_by_key.get(key)
        post, pre = overlay_after.get(key), overlay_before.get(key)
        if not source or not post or source["name"] != name or post["sourceName"] != name:
            fail(f"source key/name mismatch: {name}")
        if relation["sourceHash"] != SOURCE_HASH or relation["sourceRevision"] != REVISION or relation["evaluatedGeometrySha256"] != source["evaluatedGeometrySha256"]:
            fail(f"source archive/revision/evaluated geometry hash differs: {name}")
        meta = meta_by_name.get(name)
        if not meta or (meta["parent"], meta["collections"]) != (relation["sourceParent"], relation["sourceCollections"]):
            fail(f"raw parent/collection mismatch: {name}")
        if (source["dataName"], source["parent"], source["collections"], source["sourceLabelSide"]) != (relation["sourceDataName"], relation["sourceParent"], relation["sourceCollections"], relation["sourceSide"]):
            fail(f"catalog data/parent/collection/side mismatch: {name}")
        if relation["targetId"] not in EXPECTED or relation["relationKind"] != "class_member" or relation["directObjectNameMatch"]:
            fail(f"unsupported B05 relation or scope: {name}")
        if relation["ancestorNameAloneUsed"] or relation["upstreamFjOrTa2IdClaim"] or relation["canonicalHaBindingCreated"] or relation["humanReview"] != "not_performed":
            fail(f"identity/review promotion: {name}")
        if not set(relation["matchEvidenceSourceIds"]) <= source_ids:
            fail(f"relation provenance reference missing: {name}")
        if relation["targetId"] not in post["targetIds"] or not any(item.get("targetId") == relation["targetId"] for item in post.get("targetRelationEvidence", [])):
            fail(f"overlay relation projection missing: {name}")
        if relation["targetId"] in pre.get("targetIds", []):
            fail(f"B05 target was present before this batch: {name}")
        relation_sources.setdefault(key, set()).add(relation["targetId"])

        if relation["targetId"] == "TA2:1389":
            match = re.fullmatch(r"Patella\.([lr])", name)
            expected_parent = "Bones of free part of lower limb.g"
        elif relation["targetId"] == "TA2:1496":
            match = re.fullmatch(r"(First|Second|Third|Fourth|Fifth) metatarsal bone\.([lr])", name)
            expected_parent = "Metatarsal bones.g"
        else:
            match = re.fullmatch(r"(Proximal|Middle|Distal) phalanx of (first|second|third|fourth|fifth) finger of foot\.([lr])", name)
            expected_parent = "Phalanges of foot.g"
        if not match or relation["sourceParent"] != expected_parent:
            fail(f"exact object part/parent mismatch: {relation['targetId']} {name}")
        suffix = match.groups()[-1]
        expected_side = "left" if suffix == "l" else "right"
        limb_collection = "Left lower limb" if expected_side == "left" else "Right lower limb"
        if relation["sourceSide"] != expected_side or limb_collection not in relation["sourceCollections"]:
            fail(f"side suffix/source label/lower-limb collection disagreement: {name}")
        if name.startswith("Patella"):
            expected_code = "sesamoid:patella:" + expected_side
        elif "metatarsal" in name.lower():
            ordinal = match.group(1).lower()
            expected_code = "metatarsal:" + ordinal + ":" + expected_side
        else:
            level, digit = match.group(1).lower(), match.group(2)
            expected_code = level + ":" + digit + ":" + expected_side
            if relation["targetId"] == "TA2:1510" and level != "proximal":
                fail(f"proximal target linked to nonproximal source: {name}")
            if relation["targetId"] == "TA2:1511" and level != "middle":
                fail(f"middle target linked to nonmiddle source: {name}")
        if relation["memberCode"] != expected_code:
            fail(f"member key differs from exact source part/side: {name}")
        if "foot" in name.lower() and expected_side == "left" and "Right foot" in relation["sourceCollections"]:
            # This source taxonomy anomaly is documented; it never determines side.
            if not corr["ignoredAnomalousFootCollection"]:
                fail("right-foot collection anomaly lacks explicit disposition")

    if len(relation_sources) != 40:
        fail("unique source object count differs")
    expected_member_pairs: set[tuple[str, str]] = set()
    ordinals = ["First", "Second", "Third", "Fourth", "Fifth"]
    digits = ["first", "second", "third", "fourth", "fifth"]
    for side in ("l", "r"):
        expected_member_pairs.add(("TA2:1389", f"Patella.{side}"))
        for ordinal in ordinals:
            expected_member_pairs.add(("TA2:1496", f"{ordinal} metatarsal bone.{side}"))
        for level in ("Proximal", "Middle", "Distal"):
            for index, digit in enumerate(digits):
                if level == "Middle" and index == 0:
                    continue
                expected_member_pairs.add(("TA2:1505", f"{level} phalanx of {digit} finger of foot.{side}"))
                if level == "Proximal":
                    expected_member_pairs.add(("TA2:1510", f"{level} phalanx of {digit} finger of foot.{side}"))
                if level == "Middle":
                    expected_member_pairs.add(("TA2:1511", f"{level} phalanx of {digit} finger of foot.{side}"))
    actual_member_pairs = {(row["targetId"], row["sourceObjectName"]) for row in ledger["crosswalkRelations"]}
    if actual_member_pairs != expected_member_pairs:
        fail("exact source member set differs from frozen B05 class composition")
    for key, old in overlay_before.items():
        new = overlay_after[key]
        changed = {field for field in set(old) | set(new) if old.get(field) != new.get(field)}
        expected_changed = {"targetIds", "targetRelationEvidence"} if key in relation_sources else set()
        if changed != expected_changed:
            fail(f"out-of-scope source row field change: {new['sourceName']} {sorted(changed)}")
        for protected in ("haConceptId", "targetId", "sourceOnly", "names", "aliases", "label", "nameEvidence", "humanReview",
                          "publicRedistribution", "localUseRights", "mappingStatus", "localDisplayEligible", "inspectionEligible",
                          "defaultVisible", "bounds", "side", "regionIds", "sourceHiddenStatePreserved"):
            if old.get(protected) != new.get(protected):
                fail(f"protected existing learner mapping/display state changed: {new['sourceName']}.{protected}")
        if key in relation_sources:
            for target_id in relation_sources[key]:
                if sum(row.get("targetId") == target_id for row in new.get("targetRelationEvidence", [])) != 1:
                    fail(f"expected one B05 overlay evidence relation: {new['sourceName']} {target_id}")
            if new.get("targetIds", []).count(next(iter(relation_sources[key]))) == 0:
                fail(f"B05 targetIds projection missing: {new['sourceName']}")

    baseline_terms = {row["targetId"] for row in before["targetTerminologyEvidence"]}
    terms_post = {row["targetId"]: row for row in overlay["targetTerminologyEvidence"]}
    ledger_terms = {row["targetId"]: row for row in ledger["targets"]}
    if set(terms_post) - baseline_terms != set(EXPECTED) or set(ledger_terms) != set(EXPECTED):
        fail("overlay terminology delta is not exactly the frozen ten targets")
    for target_id in EXPECTED:
        term, frozen_target, projected = ledger_terms[target_id], by_id[target_id], terms_post[target_id]
        if term["english"] != frozen_target["term"]["english"] or term["latin"] != frozen_target["term"]["latin"]:
            fail(f"T96 English/Latin identity differs: {target_id}")
        if term["semanticKind"] != frozen_target["semanticKind"] or term["regionIds"] != frozen_target["regionIds"]:
            fail(f"frozen semantic/region classification differs: {target_id}")
        if projected["names"] != term["names"] or projected["fieldEvidence"] != term["fieldEvidence"]:
            fail(f"ledger/internal terminology evidence differs: {target_id}")
        for field_name, name_field in (("koModern", "koModern"), ("koTraditional", "koTraditional"), ("en", "en"), ("latin", "latin")):
            evidence = term["fieldEvidence"][field_name]
            expected_value = term["names"][name_field] if field_name != "latin" else term["latin"]
            if evidence["value"] != expected_value:
                fail(f"term field/name projection mismatch: {target_id} {field_name}")
            if evidence["status"] == "missing":
                if evidence.get("value") is not None or not evidence.get("missingReason"):
                    fail(f"missing name field lacks a reason: {target_id} {field_name}")
            elif evidence["status"] != "evidence_backed" or not evidence.get("locator") or not evidence["sourceIds"]:
                fail(f"name field evidence lacks locator/source: {target_id} {field_name}")
            if not set(evidence["sourceIds"]) <= source_ids:
                fail(f"name field references unknown source: {target_id} {field_name}")
        if term["fieldEvidence"]["hanja"]["status"] != "not_collected" or term["fieldEvidence"]["hanja"]["value"] is not None:
            fail(f"Hanja collection policy changed: {target_id}")
        if term["sourceOnly"] is not True or term["humanReview"] != "not_performed" or term["publicRedistribution"] != "held":
            fail(f"source/rights/review hold promoted: {target_id}")
        if term["learnerBindingCreated"] or term["canonicalHaConceptId"] is not None or term["newGeometryCreated"]:
            fail(f"learner binding/geometry invented: {target_id}")
    if terms_post["TA2:1389"]["existingSurface"]["status"] != "partial_patella_members_only_fabella_and_cyamella_surface_missing":
        fail("knee sesamoid group was falsely marked complete")
    if corr["targetsWithDirectSourceRelations"] != ["TA2:1389", "TA2:1496", "TA2:1505", "TA2:1510", "TA2:1511"]:
        fail("direct relation target summary differs")
    if corr["targetsWithNoDirectSourceRelation"] != ["TA2:1317", "TA2:1339", "TA2:1346", "TA2:1493", "TA2:1494"]:
        fail("no-direct-relation target summary differs")
    if corr["preservedCounts"]["sourceObjects"] != 960 or corr["preservedCounts"]["publicRedistribution"] != "held" or corr["preservedCounts"]["humanReview"] != "not_performed":
        fail("rights/review/source count summary changed")
    if sha(ROOT / OVERLAY_REL) != corr["overlaySha256"]:
        fail("overlay hash differs from correspondence ledger")

    result = {
        "status": "pass", "batchId": "T100-B05-pelvis-lower-limb-bones", "targets": 10,
        "exactClassMemberRelations": 58, "uniqueSourceObjects": 40, "memberCountsByTarget": expected_counts,
        "targetsWithNoDirectSourceRelation": ["TA2:1317", "TA2:1339", "TA2:1346", "TA2:1493", "TA2:1494"],
        "partialTarget": "TA2:1389", "historicalRemainderAtBatchStart": 152,
        "historicalRemainderAfterDisposition": 142,
        "frozenDenominators": {"targets": 542, "memberships": 563, "regions": 12},
        "sourceObjects": 960, "humanReview": "not_performed", "publicRedistribution": "held", "sourceOnly": True,
        "overlaySha256": sha(ROOT / OVERLAY_REL), "newGeometryCreated": False,
        "canonicalHaBindingsCreated": 0, "learnerSearchAliasesAdded": 0, "hanjaCopied": False,
        "sourceArchiveDownloaded": False, "baselineInputsUnchanged": True,
        "nextUnit": "resolve-remaining-target-part-synonym-coverage-and-korean-name-gaps",
    }
    (HERE / "validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
