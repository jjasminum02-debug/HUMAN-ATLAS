#!/usr/bin/env python3
"""Validate the T65 learner projection and preservation boundaries."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str):
    return json.loads((ROOT / path).read_text())


def sha(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main():
    baseline = read("work/evidence/T65/baseline.json")
    attachments = read("atlas-data/terminology/muscle-attachment-content-t65.json")
    nerve_content = read("atlas-data/terminology/nerve-learning-content-t65.json")
    runtime = read("atlas-data/terminology/learner-card-runtime.json")
    contexts = read("atlas-data/terminology/learner-attachment-context.json")
    integration = read("atlas-data/overlays/za-local-integration.json")
    nerve_support = read("atlas-data/overlays/nerve-support-t63.json")
    notes_path = attachments["reviewNotesPath"]
    notes_hash = sha(notes_path)

    assert notes_hash == attachments["reviewNotesSha256"] == nerve_content["reviewNotesSha256"]
    assert attachments["sourceOverlaySha256"] == sha("atlas-data/overlays/za-local-integration.json")
    assert attachments["contract"] == {
        "sourceOnly": True,
        "humanReview": "not_performed",
        "publicRedistribution": "held",
        "canonicalBindingsCreated": 0,
        "geometryCreated": 0,
        "contextMeaning": "whole existing bone context only; no landmark, point or complete extent claim",
    }
    sources = {source["id"]: source for source in attachments["sources"]}
    objects = integration["objects"]
    rows_by_key = {row["sourceKey"]: row for row in objects}
    assert len(attachments["records"]) == 9
    attached_keys = set()
    for record in attachments["records"]:
        expected_part = "part of" in record["sourceName"].lower() or "head of" in record["sourceName"].lower()
        assert (record["scopeType"] == "named_source_part") == expected_part
        assert record["sourceOnly"] and not record["canonicalBindingCreated"]
        assert record["humanReview"] == "not_performed" and record["publicRedistribution"] == "held"
        assert len(record["sourceKeys"]) == 2
        source_rows = [rows_by_key[key] for key in record["sourceKeys"]]
        assert {row["side"] for row in source_rows} == {"left", "right"}
        assert all(row["kind"] == "muscle" and row["names"]["en"] == record["sourceName"]
                   and row["defaultVisible"] and row["localDisplayEligible"] for row in source_rows)
        assert not (attached_keys & set(record["sourceKeys"]))
        attached_keys.update(record["sourceKeys"])
        for field in ("origin", "insertion"):
            value = record[field]
            proof = record["fieldEvidence"][field]
            assert hashlib.sha256(value.encode()).hexdigest() == proof["learnerValueSha256"]
            assert proof["reviewNotesSha256"] == notes_hash and proof["locator"]
            assert proof["sourceIds"] and all(source_id in sources for source_id in proof["sourceIds"])
            assert not any(char in value for char in "網址")
        for muscle in source_rows:
            for field in ("origin", "insertion"):
                expected_bone_keys = []
                for bone_name in record["contextBones"][field]:
                    candidates = [row for row in objects if row["kind"] == "bone" and row["names"]["en"] == bone_name
                                  and row["defaultVisible"] and row["localDisplayEligible"]
                                  and (row["side"] in {None, muscle["side"]})]
                    assert len(candidates) == 1, (record["sourceName"], muscle["side"], field, bone_name)
                    expected_bone_keys.append(candidates[0]["sourceKey"])
                assert contexts[muscle["sourceKey"]][field] == expected_bone_keys, (record["sourceName"], muscle["side"], field)
    assert len(attached_keys) == 18
    assert attached_keys <= set(runtime["structure"]["bySource"])
    assert attached_keys <= set(contexts)

    expected_nerve_names = {"Common fibular nerve", "Deep fibular nerve", "Superficial fibular nerve"}
    supported_nerve_names = {row["names"]["en"] for row in nerve_support["instances"]
                             if row["localSelection"] == "verified_geometry"}
    assert supported_nerve_names == expected_nerve_names
    assert set(runtime["nerveLearning"]) == expected_nerve_names
    assert len([row for row in nerve_support["instances"] if row["localSelection"] == "verified_geometry"]) == 6
    safe_text = json.dumps(runtime["nerveLearning"], ensure_ascii=False)
    assert not any(token in safe_text for token in ("https://", "ZA-c7010a9", "T65", "not_performed", "sourceHash", "locator"))
    assert all(set(row) == {"courseContext", "compressionContext", "functionContext"}
               for row in runtime["nerveLearning"].values())
    for row in nerve_content["records"]:
        assert row["nerveName"] in expected_nerve_names
        for field, proof in row["fieldEvidence"].items():
            value = row[field]
            assert hashlib.sha256(value.encode()).hexdigest() == proof["learnerValueSha256"]
            assert proof["sourceIds"] and proof["locator"] and proof["reviewNotesSha256"] == notes_hash

    coverage = read("work/evidence/T65/muscle-attachment-coverage.json")
    counts = coverage["currentCounts"]
    assert coverage["denominators"]["targets"] == 542
    assert coverage["denominators"]["memberships"] == 563
    assert coverage["denominators"]["regions"] == 12
    assert coverage["denominators"]["existingCanonicalHaBindings"] == 130
    assert coverage["denominators"]["historical163"]["categories"] == {"6": 6, "20": 20, "135": 135, "2": 2}
    assert counts == {"sourceConceptsWithDescriptionOrConflictNotice": 31,
                      "sourceSurfacesWithDescriptionOrConflictNotice": 62,
                      "missingSourceConcepts": 201, "missingSourceSurfaces": 400,
                      "remainingOriginConflicts": 1}
    for protected in ("atlas-data/terminology/muscle-attachment-content-t90.json",
                      "work/evidence/T90/muscle-attachment-coverage.json",
                      "atlas-data/overlays/nerve-support-t63.json",
                      "atlas-data/overlays/za-local-integration.json"):
        assert sha(protected) == baseline["sha256"][protected], f"protected input changed: {protected}"
    disposition = read("work/evidence/T65/muscle-attachment-dispositions.json")
    t90_coverage = read("work/evidence/T90/muscle-attachment-coverage.json")
    assert disposition["basedOn"]["T90LedgerSha256"] == sha("work/evidence/T90/muscle-attachment-coverage.json")
    assert disposition["basedOn"]["T65ContentSha256"] == sha("atlas-data/terminology/muscle-attachment-content-t65.json")
    assert disposition["basedOn"]["IntegrationSha256"] == sha("atlas-data/overlays/za-local-integration.json")
    assert disposition["denominators"]["uniqueSupportedSourceConcepts"] == 232
    assert disposition["denominators"]["supportedSurfaces"] == 462
    assert disposition["denominators"]["targets"] == 542 and disposition["denominators"]["memberships"] == 563
    assert disposition["denominators"]["regions"] == 12 and disposition["denominators"]["existingCanonicalHaBindings"] == 130
    assert disposition["denominators"]["historical163"]["categories"] == [6, 20, 135, 2]
    covered_keys = {key for row in disposition["T65Added"]["records"] for key in row["sourceKeys"]}
    assert covered_keys == attached_keys
    assert disposition["currentDisposition"]["conceptsWithDescriptionOrConflictNotice"] == 31
    assert disposition["currentDisposition"]["surfacesWithDescriptionOrConflictNotice"] == 62
    assert len(disposition["remainingWithoutDescriptions"]) == 201
    assert sum(len(row["sourceKeys"]) for row in disposition["remainingWithoutDescriptions"]) == 400
    assert len(disposition["priorT90WithDescriptionOrConflictNotice"]) == 22
    assert (len(disposition["priorT90WithDescriptionOrConflictNotice"])
            + len(disposition["T65Added"]["records"])
            + len(disposition["remainingWithoutDescriptions"])) == 232
    assert {row["sourceConceptKey"] for row in disposition["remainingWithoutDescriptions"]} == (
        set(t90_coverage["remaining"]["withoutDescriptions"])
        - {row["sourceConceptKey"] for row in disposition["T65Added"]["records"]}
    )
    assert len(disposition["remainingConflicts"]) == 1
    conflict = disposition["remainingConflicts"][0]
    assert conflict["exactSourceName"] == "Fibularis longus muscle"
    assert conflict["originStatus"] == "conflicted_not_asserted"
    assert disposition["authority"] == {"sourceOnly": True, "humanReview": "not_performed",
                                         "publicRedistribution": "held", "newCanonicalBindings": 0,
                                         "newGeometry": 0}
    print(json.dumps({"status": "passed", "newAttachmentConcepts": 9, "newAttachmentSurfaces": 18,
                      "currentAttachmentCoverage": counts, "nerveConcepts": len(expected_nerve_names),
                      "remainingConceptsFullyEnumerated": len(disposition["remainingWithoutDescriptions"]),
                      "supportedConceptDispositionCount": (len(disposition["priorT90WithDescriptionOrConflictNotice"])
                                                            + len(disposition["T65Added"]["records"])
                                                            + len(disposition["remainingWithoutDescriptions"])),
                      "nerveInstancesUnchanged": 6, "sourceReviewNotesSha256": notes_hash,
                      "canonicalBindingsCreated": 0, "geometryCreated": 0,
                      "humanReview": "not_performed", "publicRedistribution": "held"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
