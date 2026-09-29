#!/usr/bin/env python3
"""Fail-closed scope, provenance, relation and source-preservation checks for T100-B03."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
BASELINE = json.loads((HERE / "start-baseline.json").read_text())
EXPECTED = [
    "TA2:1068", "TA2:1115", "TA2:1116", "TA2:1117", "TA2:1118",
    "TA2:1137", "TA2:1138", "TA2:1248", "TA2:1249", "TA2:1262",
]
SOURCE_HASH = "9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd"
REVISION = "c7010a903b75a2fd24a13b1c2c4c3546a9223780"
OVERLAY_REL = "atlas-data/overlays/za-local-integration.json"
OVERLAY_PATH = ROOT / OVERLAY_REL
SCOPE_PATH = ROOT / "atlas-data/catalog/target-scope-t96.json"
REMAINING_PATH = ROOT / "work/evidence/T100/resolution-2026-09-29/remaining-targets.json"
CATALOG_PATH = ROOT / "work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json"
META_PATH = ROOT / "work/evidence/T100/resolution-2026-09-29/source-metadata.json"
COMPILED_PATH = ROOT / "atlas-data/source-cache/datasets/za/compiled/manifest.json"
LEDGER_PATH = HERE / "term-and-correspondence-ledger.json"
CORR_PATH = HERE / "structure-correspondence.json"


def read(path: Path):
    return json.loads(path.read_text())


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message):
    raise SystemExit("FAIL: " + message)


def git_file(commit, rel):
    return subprocess.check_output(["git", "show", f"{commit}:{rel}"], cwd=ROOT)


def expected_names():
    ordinals = ["First", "Second", "Third", "Fourth", "Fifth", "Sixth",
                "Seventh", "Eighth", "Ninth", "Tenth", "Eleventh", "Twelfth"]
    names = {f"TA2:1068": [f"Vertebra L{i}" for i in range(1, 6)]}
    names["TA2:1118"] = [f"{ordinal} rib.{side}" for ordinal in ordinals for side in ("l", "r")]
    names["TA2:1249"] = [
        f"{bone} bone.{side}" for bone in
        ["Scaphoid", "Lunate", "Triquetrum", "Pisiform", "Trapezium", "Trapezoid", "Capitate", "Hamate"]
        for side in ("l", "r")
    ]
    return names


def main():
    immutable = [
        "atlas-data/catalog/target-scope-t96.json",
        "work/evidence/T100/resolution-2026-09-29/remaining-targets.json",
        "work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json",
        "work/evidence/T100/resolution-2026-09-29/source-metadata.json",
        "atlas-data/source-cache/datasets/za/compiled/manifest.json",
    ]
    for rel in immutable:
        expected = BASELINE["inputSha256"][rel]
        if sha(ROOT / rel) != expected:
            fail(f"frozen input mutated: {rel}")
    before_raw = git_file(BASELINE["rootHead"], OVERLAY_REL)
    if hashlib.sha256(before_raw).hexdigest() != BASELINE["overlaySha256"]:
        fail("baseline overlay commit hash differs")
    before = json.loads(before_raw)
    after = read(OVERLAY_PATH)
    scope, remaining = read(SCOPE_PATH), read(REMAINING_PATH)
    catalog, metadata = read(CATALOG_PATH), read(META_PATH)
    compiled = read(COMPILED_PATH)
    ledger, corr = read(LEDGER_PATH), read(CORR_PATH)
    frozen_batch = read(HERE / "batch-scope.json")
    observations = read(HERE / "source-query-observations.json")

    if frozen_batch["targetIds"] != EXPECTED or frozen_batch["targetCount"] != 10:
        fail("frozen B03 target scope changed")
    if ledger["scope"]["requestedTargetIds"] != EXPECTED or [t["targetId"] for t in ledger["targets"]] != EXPECTED:
        fail("ledger target scope/order changed")
    if ledger["scope"]["targetCount"] != 10 or len(ledger["targets"]) != 10:
        fail("ledger target count changed")
    if scope["revision"] != "T96-2026-09-28-semantic-freeze-v1" or len(scope["targets"]) != 542:
        fail("T96 semantic freeze changed")
    if before["scope"] != {"targets": 542, "memberships": 563, "regions": 12} or after["scope"] != before["scope"]:
        fail("canonical denominators changed")
    if remaining["targets"] != 542 or len(remaining["unresolved"]) != 182:
        fail("historical frozen remainder inventory was edited")
    if ledger["scope"]["historicalRemainingCountAtBatchStart"] != 172:
        fail("B03 start remainder should be 172 after B02")
    if corr["historicalRemainderAfterB03DispositionPass"] != 162 or corr["batchDispositionCount"] != 10:
        fail("B03 disposition delta is incorrect")
    if corr["inputDenominators"] != {"targets": 542, "memberships": 563, "regions": 12}:
        fail("B03 changed whole-body denominator")
    if corr["wholeBodyComplete"] if "wholeBodyComplete" in corr else False:
        fail("whole-body completion was asserted")
    if catalog["sourceHash"] != SOURCE_HASH or catalog["sourceRevision"] != REVISION or len(catalog["objects"]) != 960:
        fail("pinned source catalog identity/count changed")
    if compiled["sourceHash"] != SOURCE_HASH or compiled["revision"] != after["datasetRevision"] or len(compiled["instances"]) != 960:
        fail("compiled runtime source identity/count changed")
    if after["datasetRevision"] != before["datasetRevision"] or after["sourceCatalogSha256"] != before["sourceCatalogSha256"]:
        fail("B03 changed source dataset/catalog identity")
    if after["sourceHash"] != SOURCE_HASH or after["policy"] != before["policy"]:
        fail("source or policy state changed")
    if len(before["objects"]) != 960 or len(after["objects"]) != 960:
        fail("B03 changed source surface count")

    expected_members = expected_names()
    member_target_ids = set(expected_members)
    refs = {s["id"]: s for s in after["evidenceSources"]}
    if len(refs) != len(after["evidenceSources"]):
        fail("overlay has duplicate provenance source IDs")
    previous_ids = {s["id"] for s in before.get("evidenceSources", [])}
    if not previous_ids <= set(refs):
        fail("prior B01/B02 evidence source refs were removed")
    b03_sources = {s["id"]: s for s in ledger["sourceEvidence"]}
    if len(b03_sources) != len(ledger["sourceEvidence"]) or not set(b03_sources) <= set(refs):
        fail("B03 evidence source refs are duplicate or absent from overlay")
    prior_sources = before.get("evidenceSources", [])
    if after["evidenceSources"][:len(prior_sources)] != prior_sources:
        fail("prior evidence source rows changed")
    prior_terms = before.get("targetTerminologyEvidence", [])
    if after.get("targetTerminologyEvidence", [])[:len(prior_terms)] != prior_terms:
        fail("prior B02 terminology evidence was overwritten")
    b03_terms = after.get("targetTerminologyEvidence", [])[len(prior_terms):]
    if [x["targetId"] for x in b03_terms] != EXPECTED:
        fail("only the frozen B03 term rows may be appended")
    if [x["targetId"] for x in ledger["targets"]] != [x["targetId"] for x in b03_terms]:
        fail("ledger and overlay terminology rows differ")
    for term in b03_terms:
        if term != next(x for x in ledger["targets"] if x["targetId"] == term["targetId"]):
            fail(f"overlay term/ledger mismatch: {term['targetId']}")
        if (term["learnerBindingCreated"], term["canonicalHaConceptId"], term["sourceOnly"],
            term["humanReview"], term["publicRedistribution"], term["newGeometryCreated"]) != (
            False, None, True, "not_performed", "held", False
        ):
            fail(f"promotion/geometry/review/rights hold changed: {term['targetId']}")
        for key in ("koModern", "koTraditional"):
            value = term["names"][key]
            if value and re.search(r"[\u3400-\u9fff]", value):
                fail(f"Hanja was copied into Korean field: {term['targetId']}.{key}")
        for field_name, field in term["fieldEvidence"].items():
            if field["value"] is None:
                if field["status"] != "missing" or field["locator"] is not None or not field.get("missingReason"):
                    fail(f"unsubstantiated value was not kept missing: {term['targetId']}.{field_name}")
            else:
                if field["status"] != "evidence_backed" or not field["locator"] or not field["sourceIds"]:
                    fail(f"field lacks exact locator/source: {term['targetId']}.{field_name}")
            for source_id in field["sourceIds"]:
                source = refs.get(source_id)
                if not source or not source["url"].startswith("https://") or not source.get("editionExposure") or not source["locator"].strip():
                    fail(f"field source reference incomplete: {term['targetId']}.{field_name}:{source_id}")
                if source["accessMethod"] not in ("opened_html", "search_index_excerpt", "local_frozen_metadata"):
                    fail(f"source access type conflated: {source_id}")

    if observations["batchId"] != "T100-B03-lumbar-ribs-hand-groups" or observations["hanjaCopied"] is not False:
        fail("KMLE observation scope/Hanja policy changed")
    if observations["sourceKindSeparation"]["kmle"].find("underlying dictionary records/edition") < 0:
        fail("search-index/open-page source distinction missing")
    for source in ledger["sourceEvidence"]:
        if source["accessMethod"] == "opened_html" and not source["locator"].strip():
            fail(f"opened source locator absent: {source['id']}")
        if source["accessMethod"] == "local_frozen_metadata" and source["exactEdition"] is None:
            fail(f"frozen source edition is not documented: {source['id']}")

    before_rows = {r["sourceKey"]: r for r in before["objects"]}
    after_rows = {r["sourceKey"]: r for r in after["objects"]}
    catalog_rows = {r["sourceKey"]: r for r in catalog["objects"]}
    meta_rows = {r["name"]: r for r in metadata["objects"]}
    if set(before_rows) != set(after_rows) or set(after_rows) != set(catalog_rows):
        fail("stable source object set changed")
    relations = [(row, rel) for row in after["objects"] for rel in row.get("targetRelationEvidence", [])
                 if rel["targetId"] in EXPECTED]
    if len(relations) != 45 or len({rel["sourceKey"] for _, rel in relations}) != 45:
        fail("B03 must contain 45 unique exact class-member relations")
    counts = {target_id: sum(rel["targetId"] == target_id for _, rel in relations) for target_id in EXPECTED}
    if counts != {**{x: 0 for x in EXPECTED}, "TA2:1068": 5, "TA2:1118": 24, "TA2:1249": 16}:
        fail(f"unexpected per-target relation counts: {counts}")
    if corr["memberCountsByTarget"] != counts or ledger["memberCountsByTarget"] != counts:
        fail("crosswalk count summaries differ")
    if {x["sourceObjectName"] for _, x in relations if x["targetId"] == "TA2:1068"} != set(expected_members["TA2:1068"]):
        fail("lumbar member set differs")
    if {x["sourceObjectName"] for _, x in relations if x["targetId"] == "TA2:1118"} != set(expected_members["TA2:1118"]):
        fail("ordinary rib member set differs")
    if {x["sourceObjectName"] for _, x in relations if x["targetId"] == "TA2:1249"} != set(expected_members["TA2:1249"]):
        fail("carpal member set differs")

    changed_members = set()
    for key, old in before_rows.items():
        new = after_rows[key]
        changed = {field for field in set(old) | set(new) if old.get(field) != new.get(field)}
        current_b03 = [r for r in new.get("targetRelationEvidence", []) if r["targetId"] in EXPECTED]
        if current_b03:
            changed_members.add(key)
            if changed - {"targetIds", "targetRelationEvidence"}:
                fail(f"non-evidence surface field changed: {new['sourceName']}:{sorted(changed)}")
        elif changed:
            fail(f"out-of-scope source row changed: {key}:{sorted(changed)}")
        for protected in ("haConceptId", "sourceOnly", "humanReview", "publicRedistribution", "localUseRights",
                          "mappingStatus", "localDisplayEligible", "inspectionEligible", "defaultVisible",
                          "bounds", "side", "regionIds", "names", "aliases", "nameEvidence"):
            if old.get(protected) != new.get(protected):
                fail(f"protected learner/review/display data changed: {key}.{protected}")
    if len(changed_members) != 45:
        fail(f"unexpected number of touched surface rows: {len(changed_members)}")

    for row, relation in relations:
        obj = catalog_rows.get(relation["sourceKey"])
        if not obj or row["sourceKey"] != relation["sourceKey"] or row["sourceName"] != relation["sourceObjectName"]:
            fail("crosswalk identity/source object mismatch")
        if relation["sourceObjectName"] not in expected_members[relation["targetId"]]:
            fail(f"out-of-scope object relation: {relation['sourceObjectName']}")
        if relation["sourceHash"] != SOURCE_HASH or relation["sourceRevision"] != REVISION:
            fail(f"source hash/revision mismatch: {relation['sourceObjectName']}")
        if relation["evaluatedGeometrySha256"] != obj["evaluatedGeometrySha256"]:
            fail(f"evaluated hash mismatch: {relation['sourceObjectName']}")
        raw_obj = meta_rows[relation["sourceObjectName"]]
        if (relation["sourceParent"], relation["sourceCollections"]) != (obj["parent"], obj["collections"]):
            fail(f"evaluated catalogue hierarchy mismatch: {relation['sourceObjectName']}")
        if (raw_obj["parent"], raw_obj["collections"]) != (relation["sourceParent"], relation["sourceCollections"]):
            fail(f"raw hierarchy mismatch: {relation['sourceObjectName']}")
        if relation["sourceDataName"] != obj["dataName"] or relation["sourceSide"] != obj["sourceLabelSide"] or row["side"] != obj["sourceLabelSide"]:
            fail(f"data name/side does not match exact catalogue: {relation['sourceObjectName']}")
        if relation["upstreamFjOrTa2IdClaim"] or relation["canonicalHaBindingCreated"] or relation["humanReview"] != "not_performed":
            fail(f"unsupported identity or review promotion: {relation['sourceObjectName']}")
        if relation["directObjectNameMatch"] or relation["ancestorNameAloneUsed"] or relation["relationKind"] != "class_member":
            fail(f"unsupported relation method: {relation['sourceObjectName']}")
        if not set(relation["matchEvidenceSourceIds"]) <= set(refs):
            fail(f"missing source evidence ref: {relation['sourceObjectName']}")
        if relation["targetId"] not in row["targetIds"]:
            fail(f"relation absent from target IDs list: {relation['sourceObjectName']}")
        if relation["targetId"] == "TA2:1068":
            if relation["sourceSegmentCode"] not in {"L1", "L2", "L3", "L4", "L5"} or relation["sourceSide"] is not None:
                fail("lumbar vertebrae were given unsupported side/level")
        elif relation["targetId"] == "TA2:1118":
            suffix = relation["sourceObjectName"][-1]
            if suffix not in "lr" or relation["sourceSide"] != {"l": "left", "r": "right"}[suffix]:
                fail(f"rib side does not follow exact source suffix and label: {relation['sourceObjectName']}")
        elif relation["targetId"] == "TA2:1249":
            suffix = relation["sourceObjectName"][-1]
            if suffix not in "lr" or relation["sourceSide"] != {"l": "left", "r": "right"}[suffix]:
                fail(f"carpal side does not follow exact source suffix and label: {relation['sourceObjectName']}")
            if suffix == "l" and "Right hand" in relation["sourceCollections"] and "Left upper limb" not in relation["sourceCollections"]:
                fail("known hand collection anomaly was used as side evidence")

    for term in ledger["targets"]:
        status = term["existingSurface"]["status"]
        if term["targetId"] in ("TA2:1115", "TA2:1116", "TA2:1117", "TA2:1137", "TA2:1138", "TA2:1262"):
            if any(rel["targetId"] == term["targetId"] for _, rel in relations):
                fail(f"unavailable/variant source surface was substituted: {term['targetId']}")
            if "missing" not in status:
                fail(f"missing exact surface not represented as missing: {term['targetId']}")
        if term["targetId"] == "TA2:1248" and any(rel["targetId"] == "TA2:1248" for _, rel in relations):
            fail("carpal child surfaces were used to claim whole-hand group coverage")
    if corr["targetsWithExactRelations"] != ["TA2:1068", "TA2:1118", "TA2:1249"]:
        fail("target-level coverage summary is not exact")
    if corr["targetsWithoutExactRelations"] != ["TA2:1115", "TA2:1116", "TA2:1117", "TA2:1137", "TA2:1138", "TA2:1248", "TA2:1262"]:
        fail("target-level missing list is not exact")
    if sha(OVERLAY_PATH) != corr["overlaySha256"]:
        fail("overlay checksum in correspondence evidence differs")

    result = {
        "status": "pass",
        "batchId": "T100-B03-lumbar-ribs-hand-groups",
        "targets": 10,
        "exactRelations": 45,
        "membersByTarget": counts,
        "targetsWithNoDirectRelation": 7,
        "historicalRemainderAfterDisposition": 162,
        "frozenDenominators": {"targets": 542, "memberships": 563, "regions": 12},
        "sourceObjects": 960,
        "humanReview": "not_performed",
        "publicRedistribution": "held",
        "sourceOnly": True,
        "overlaySha256": sha(OVERLAY_PATH),
        "baselineFrozenInputsUnchanged": immutable,
        "learningNamesOrAliasesChanged": False,
        "canonicalIdsCreated": False,
        "newGeometryCreated": False,
    }
    (HERE / "validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
