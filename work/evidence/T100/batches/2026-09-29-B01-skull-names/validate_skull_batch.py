from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
read = lambda path: json.loads(path.read_text())
sha_bytes = lambda data: hashlib.sha256(data).hexdigest()


def main():
    baseline = read(HERE / "start-baseline.json")
    ledger = read(HERE / "term-and-correspondence-ledger.json")
    overlay_path = ROOT / "atlas-data/overlays/za-local-integration.json"
    overlay = read(overlay_path)
    correspondence = read(HERE / "structure-correspondence.json")
    source = read(ROOT / "work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json")
    scope = read(ROOT / "atlas-data/catalog/target-scope-t96.json")
    frozen_overlay = json.loads(subprocess.check_output(
        ["git", "show", f"{baseline['startingHead']}:atlas-data/overlays/za-local-integration.json"],
        cwd=ROOT,
    ))

    assert baseline["startingHead"] == "a5a528c2a75a67188fc8236763e3885ea47e1f7c"
    assert overlay["schemaVersion"] == frozen_overlay["schemaVersion"] == 1
    assert overlay["scope"] == frozen_overlay["scope"] == {"targets": 542, "memberships": 563, "regions": 12}
    for key in ["datasetRevision", "sourceCatalogSha256", "targetScopeSha256", "sourceHash", "policy"]:
        assert overlay[key] == frozen_overlay[key], key
    assert overlay["sourceHash"] == source["sourceHash"] == ledger["scope"]["zaSourceFileSha256"]
    assert len(overlay["objects"]) == len(frozen_overlay["objects"]) == 960
    assert len(overlay["evidenceSources"]) == len(ledger["sourceEvidence"]) == 12
    assert {x["id"] for x in overlay["evidenceSources"]} == {x["id"] for x in ledger["sourceEvidence"]}
    evidence_ids = {x["id"] for x in overlay["evidenceSources"]}
    assert sum(x["accessMethod"] == "opened_html" for x in overlay["evidenceSources"]) == 6
    assert sum(x["accessMethod"] == "search_index_excerpt" for x in overlay["evidenceSources"]) == 4
    assert sum(x["accessMethod"] == "local_frozen_metadata" for x in overlay["evidenceSources"]) == 2
    rows = {row["sourceKey"]: row for row in overlay["objects"]}
    old_rows = {row["sourceKey"]: row for row in frozen_overlay["objects"]}
    target_scope = {row["id"]: row for row in scope["targets"]}
    source_rows = {row["sourceKey"]: row for row in source["objects"]}
    targets = {row["targetId"]: row for row in ledger["targets"]}
    batch_members = {key for target in targets.values() for key in target["sourceMembers"]}
    assert len(targets) == 10 and len(batch_members) == 14
    assert correspondence["targetCount"] == 10 and correspondence["sourceObjectCount"] == 14
    assert correspondence["unresolvedTargetsBeforeAndAfter"] == 182
    for entry in ledger["targets"]:
        target_rows = [rows[key] for key in entry["sourceMembers"]]
        if len(target_rows) == 2:
            assert {row["side"] for row in target_rows} == {"left", "right"}
        else:
            assert len(target_rows) == 1 and target_rows[0]["side"] is None

    for source_key, row in rows.items():
        assert row["sourceKey"] == old_rows[source_key]["sourceKey"]
        old, new = old_rows[source_key], row
        assert new["bounds"] == old["bounds"]
        for key in ["sourceName", "kind", "regionIds", "side", "haConceptId", "targetId", "targetIds", "mappingStatus",
                    "localDisplayEligible", "inspectionEligible", "defaultVisible", "sourceOnly", "humanReview",
                    "publicRedistribution", "sourceHiddenStatePreserved", "localUseRights", "displayDecisionBasis",
                    "hardHoldReasons", "bounds", "relatedMuscles"]:
            assert new.get(key) == old.get(key), f"protected row field changed: {source_key}.{key}"
        if source_key in batch_members:
            relation = new["targetRelationEvidence"][0]
            target = target_scope[relation["targetId"]]
            entry = next(item for item in ledger["targets"] if item["targetId"] == relation["targetId"])
            assert relation["sourceKey"] == source_key and relation["sourceObjectName"] == new["sourceName"]
            assert relation["targetId"] == new["targetId"] and relation["targetId"] in new["targetIds"]
            assert relation["targetSemanticKind"] == "bone" == target["semanticKind"]
            assert relation["targetEnglish"].casefold() == target["term"]["english"].casefold()
            assert relation["targetLatin"] == target["term"]["latin"] == entry["latin"]
            assert relation["directObjectNameMatch"] is True and relation["ancestorNameAloneUsed"] is False
            assert relation["upstreamFjOrTa2IdClaim"] is False and relation["canonicalHaBindingCreated"] is False
            assert relation["humanReview"] == new["humanReview"] == "not_performed"
            assert relation["sourceSide"] == new["side"] == source_rows[source_key]["sourceLabelSide"]
            suffix = ".l" if new["sourceName"].lower().endswith(".l") else ".r" if new["sourceName"].lower().endswith(".r") else None
            assert {".l": "left", ".r": "right"}.get(suffix) == new["side"]
            assert relation["evaluatedGeometrySha256"] == source_rows[source_key]["evaluatedGeometrySha256"]
            assert new["names"]["koModern"] == entry["koModern"]
            assert new["names"]["koTraditional"] == entry["koTraditional"]
            assert new["names"]["en"] == old["names"]["en"]
            assert new["label"] == entry["koModern"]
            assert entry["latin"] in new["aliases"]
            assert new["haConceptId"] is None and new["sourceOnly"] is True
            assert new["humanReview"] == "not_performed" and new["publicRedistribution"] == "held"
            assert set(new["nameSourceIds"]).issubset(evidence_ids)
            assert set(new["nameEvidence"]["koModern"]["sourceIds"]).issubset(evidence_ids)
            assert set(new["nameEvidence"]["koTraditional"]["sourceIds"]).issubset(evidence_ids)
            assert set(new["nameEvidence"]["en"]["sourceIds"]).issubset(evidence_ids)
            assert all(new["nameEvidence"][field]["value"] == new["names"][field] for field in ["koModern", "koTraditional", "en"])
        else:
            allowed = {"label", "names", "aliases", "nameSourceIds", "nameEvidence", "targetRelationEvidence"}
            assert {k: v for k, v in new.items() if k not in allowed} == {k: v for k, v in old.items() if k not in allowed}
            assert all(k not in new for k in ["nameEvidence", "targetRelationEvidence"])

    assert len([row for row in rows.values() if row.get("targetRelationEvidence")]) == 14
    assert len({row["targetRelationEvidence"][0]["targetId"] for row in rows.values() if row.get("targetRelationEvidence")}) == 10
    assert sum(row["localDisplayEligible"] for row in rows.values()) == 672
    assert sum(row["haConceptId"] is not None for row in rows.values()) == 130
    full_three_names = lambda row: all(row["names"].get(field) for field in ["koModern", "koTraditional", "en"])
    before_three_names = sum(full_three_names(row) for row in frozen_overlay["objects"])
    after_three_names = sum(full_three_names(row) for row in overlay["objects"])
    assert before_three_names == 123
    assert after_three_names == 137
    assert overlay["revision"] == "T100-source-taxonomy-local-display-v1-B01-skull-names"
    result = {
        "schemaVersion": 1,
        "batchId": ledger["batchId"],
        "status": "passed",
        "startingHead": baseline["startingHead"],
        "startingOverlaySha256": baseline["inputSha256"]["atlas-data/overlays/za-local-integration.json"],
        "currentOverlaySha256": sha_bytes(overlay_path.read_bytes()),
        "sourceHash": overlay["sourceHash"],
        "denominators": {"targets": 542, "memberships": 563, "regions": 12},
        "b01": {"exactTargets": 10, "sourceObjectMembers": 14, "pairedTargetIds": 4, "unpairedSourceObjects": 6,
                "directTaxonomyRelations": 10, "surfaceRowsWithThreeNamesBefore": before_three_names,
                "surfaceRowsWithThreeNamesAfter": after_three_names},
        "unchanged": {"sourceObjectCount": 960, "locallyDisplayableRows": 672, "haBoundSurfaceRows": 130,
                      "publicRedistribution": "held", "humanReview": "not_performed", "sourceOnlyForBatchRows": True,
                      "unresolvedTargets": 182},
        "sourceAccess": {"openedHtml": 6, "searchIndexExcerptOnly": 4, "localFrozenMetadata": 2,
                         "exactKMLEditionExposed": False},
        "nonClaims": ["not whole-body completion", "not new geometry", "not upstream FJ/TA2 identity claim",
                       "not HA canonical learner binding", "not human review", "not public redistribution permission"],
    }
    (HERE / "validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
