#!/usr/bin/env python3
"""Regenerate synthetic-only T03 positive and negative validator fixtures."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
FIXTURES = Path(__file__).resolve().parent
COLLECTIONS = [
    "regions", "muscleConcepts", "instances", "muscleParts", "terms", "structures",
    "attachments", "spatialAnnotations", "meshAssets", "meshMappings", "jointActions",
    "innervations", "assessments", "sources", "evidence", "claims", "reviews", "modelElements"
]
ATLAS_FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
SOURCE_FRAME = "BODYPARTS3D_R4_SOURCE_MM"
REVIEWABLE = {"terms", "spatialAnnotations", "meshMappings", "jointActions", "innervations", "assessments", "claims"}


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def revision_hash(entity: dict) -> str:
    payload = {key: value for key, value in entity.items() if key != "reviewState"}
    return hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()


def find_reviewable(data: dict, target_id: str) -> dict:
    for collection in REVIEWABLE:
        for item in data["entities"][collection]:
            if item["id"] == target_id:
                return item
    raise KeyError(target_id)


def resign(data: dict, target_id: str) -> None:
    wanted_hash = revision_hash(find_reviewable(data, target_id))
    for review in data["entities"]["reviews"]:
        if review["targetId"] == target_id:
            review["targetRevisionHash"] = wanted_hash


def make_positive() -> dict:
    e = {collection: [] for collection in COLLECTIONS}
    e["regions"] = [{"id": "fixture:region", "parentId": None, "label": "Synthetic region", "notes": "Fixture only; not an anatomical assertion."}]
    e["muscleConcepts"] = [
        {"id": "fixture:muscle", "entityType": "individual_muscle", "regionIds": ["fixture:region"], "standardRefs": [], "applicability": {"populations": ["synthetic fixture"]}},
        {"id": "fixture:group", "entityType": "muscle_group", "regionIds": ["fixture:region"], "standardRefs": [], "applicability": {"populations": ["synthetic fixture"]}}
    ]
    e["instances"] = [
        {"id": "fixture:instance-left", "conceptId": "fixture:muscle", "side": "left"},
        {"id": "fixture:instance-right", "conceptId": "fixture:muscle", "side": "right"}
    ]
    e["muscleParts"] = [{"id": "fixture:part", "parentMuscleId": "fixture:muscle", "partKind": "other", "termIds": []}]
    e["terms"] = [
        {"id": "fixture:term-en", "conceptId": "fixture:muscle", "language": "en", "script": "Latn", "text": "Synthetic Muscle Name", "termRole": "preferred", "edition": "synthetic fixture edition 1", "evidenceIds": ["fixture:evidence-term"], "reviewState": "reviewed"},
        {"id": "fixture:term-hani-missing", "conceptId": "fixture:muscle", "language": "zh-Hans", "script": "Hani", "text": None, "termRole": "preferred", "edition": None, "evidenceIds": [], "reviewState": "draft", "missingReason": "No terminology source is supplied in this synthetic fixture."}
    ]
    e["structures"] = [
        {"id": "fixture:structure-tendon", "kind": "tendon", "termIds": []},
        {"id": "fixture:structure-landmark", "kind": "landmark", "termIds": []},
        {"id": "fixture:structure-joint", "kind": "joint", "termIds": []},
        {"id": "fixture:structure-nerve", "kind": "nerve", "termIds": []}
    ]
    e["attachments"] = [{"id": "fixture:attachment", "muscleOrPartId": "fixture:muscle", "role": "undifferentiated", "targetStructureId": "fixture:structure-tendon", "landmarkId": "fixture:structure-landmark", "descriptionClaimId": "fixture:claim-attachment", "variantContext": None}]
    e["sources"] = [{
        "id": "fixture:source", "title": "Synthetic validator fixture source", "authors": ["Synthetic test generator"], "edition": "fixture edition", "year": 2026,
        "urlOrLocalRef": "fixture://not-a-real-source", "accessDate": "2026-09-25",
        "license": {"id": "fixture:license", "name": "Synthetic test-only terms", "spdxId": None, "allowedUses": ["internal", "learning"], "attributionRequired": True, "attributionText": "Synthetic validator fixture; no real anatomy source.", "derivativesAllowed": False, "redistributionAllowed": False}
    }]
    e["meshAssets"] = [{
        "id": "fixture:mesh-right", "revision": "fixture:mesh-rev-1", "sourceId": "fixture:source", "hash": "a" * 64, "topologyHash": "b" * 64,
        "uri": "fixture://synthetic-right-mesh", "format": "obj", "units": "mm",
        "axes": {"frameId": SOURCE_FRAME, "handedness": "right", "positiveX": "patient_left", "positiveY": "posterior", "positiveZ": "superior"},
        "pose": {"id": "fixture:static-pose", "description": "Synthetic fixed reference pose; not an anatomical pose."},
        "licenseId": "fixture:license", "laterality": "right"
    }]
    e["claims"] = [
        {"id": "fixture:claim-attachment", "subjectId": "fixture:attachment", "field": "description", "value": {"text": "Synthetic attachment description; not an anatomy claim."}, "evidenceIds": ["fixture:evidence-attachment"], "attribution": "source_summary", "reviewState": "reviewed"},
        {"id": "fixture:claim-mapping", "subjectId": "fixture:mapping", "field": "mapping", "value": "Synthetic mapping fixture.", "evidenceIds": ["fixture:evidence-mapping"], "attribution": "user_note", "reviewState": "reviewed"},
        {"id": "fixture:claim-annotation", "subjectId": "fixture:annotation", "field": "coordinate", "value": "Synthetic coordinate fixture in meters.", "evidenceIds": ["fixture:evidence-annotation"], "attribution": "user_note", "reviewState": "reviewed"},
        {"id": "fixture:claim-term", "subjectId": "fixture:term-en", "field": "text", "value": "Synthetic Muscle Name", "evidenceIds": ["fixture:evidence-term"], "attribution": "user_note", "reviewState": "reviewed"}
    ]
    e["evidence"] = [
        {"id": "fixture:evidence-attachment", "sourceId": "fixture:source", "locator": "synthetic fixture locator: attachment", "supportedClaimIds": ["fixture:claim-attachment"], "evidenceKind": "synthetic_fixture"},
        {"id": "fixture:evidence-mapping", "sourceId": "fixture:source", "locator": "synthetic fixture locator: mapping", "supportedClaimIds": ["fixture:claim-mapping"], "evidenceKind": "synthetic_fixture"},
        {"id": "fixture:evidence-annotation", "sourceId": "fixture:source", "locator": "synthetic fixture locator: annotation and known-marker gate", "supportedClaimIds": ["fixture:claim-annotation"], "evidenceKind": "synthetic_fixture"},
        {"id": "fixture:evidence-term", "sourceId": "fixture:source", "locator": "synthetic fixture locator: term gate", "supportedClaimIds": ["fixture:claim-term"], "evidenceKind": "synthetic_fixture"}
    ]
    e["meshMappings"] = [{"id": "fixture:mapping", "instanceIds": ["fixture:instance-right"], "partIds": ["fixture:part"], "meshIds": ["fixture:mesh-right"], "representationType": "muscle_part", "evidenceIds": ["fixture:evidence-mapping"], "reviewState": "reviewed"}]
    e["spatialAnnotations"] = [{
        "id": "fixture:annotation", "attachmentId": "fixture:attachment", "instanceId": "fixture:instance-right", "assetId": "fixture:mesh-right",
        "assetRevision": "fixture:mesh-rev-1", "assetRevisionHash": "a" * 64,
        "geometry": {"kind": "point", "position": [0.1, 0.2, 0.3]}, "frameId": ATLAS_FRAME, "units": "m", "poseId": "fixture:static-pose",
        "precision": "representative", "method": "manual_mapping",
        "transformChain": [{"sourceFrameId": SOURCE_FRAME, "targetFrameId": ATLAS_FRAME, "sourceUnits": "mm", "targetUnits": "m", "scale": 0.001,
                            "rotationDeterminant": 1.0, "rotationMatrix": [[1, 0, 0], [0, 0, 1], [0, -1, 0]], "evidenceId": "fixture:evidence-annotation"}],
        "landmarkChecks": [{"landmarkId": "fixture:structure-landmark", "expectedAtlasPositionM": [0.1, 0.2, 0.3], "observedAtlasPositionM": [0.1, 0.2, 0.3], "toleranceM": 0.001, "evidenceId": "fixture:evidence-annotation"}],
        "evidenceIds": ["fixture:evidence-annotation"], "reviewState": "reviewed"
    }]
    e["jointActions"] = [{"id": "fixture:action", "muscleOrPartIds": ["fixture:muscle"], "jointIds": ["fixture:structure-joint"], "action": "synthetic action placeholder", "postureConditions": [], "contractionRole": "unspecified", "evidenceIds": [], "reviewState": "draft"}]
    e["innervations"] = [{"id": "fixture:innervation", "muscleOrPartId": "fixture:muscle", "nerveStructureId": "fixture:structure-nerve", "rootLevels": [], "context": "synthetic placeholder", "evidenceIds": [], "reviewState": "draft"}]
    e["assessments"] = [{"id": "fixture:assessment", "targetFunctionIds": ["fixture:action"], "relatedMuscleIds": ["fixture:muscle"], "scope": "individual", "purpose": "Synthetic contract placeholder", "protocol": {"variantId": "fixture:protocol-variant", "steps": []}, "observations": [], "interpretations": [], "limitations": ["Synthetic fixture only; no protocol is asserted."], "safety": [], "evidenceIds": [], "reviewState": "draft"}]
    e["modelElements"] = [
        {"id": "fixture:model-element-mapped", "sourceId": "fixture:source", "modelVersion": "synthetic-only", "elementType": "actuator", "elementRef": "fixtureActuator", "mappingStatus": "provisional", "muscleConceptId": "fixture:group"},
        {"id": "fixture:model-element-unmapped", "sourceId": "fixture:source", "modelVersion": "synthetic-only", "elementType": "path", "elementRef": "fixturePath", "mappingStatus": "unmapped"}
    ]
    review_targets = ["fixture:term-en", "fixture:mapping", "fixture:annotation", *[claim["id"] for claim in e["claims"]]]
    for index, target_id in enumerate(review_targets, 1):
        target = next(row for collection in REVIEWABLE for row in e[collection] if row["id"] == target_id)
        e["reviews"].append({"id": f"fixture:review-{index}", "targetId": target_id, "targetRevisionHash": revision_hash(target), "reviewerKind": "human", "reviewerId": "fixture-reviewer-id", "decision": "approved", "reviewedAt": "2026-09-25T00:00:00Z", "notes": "Synthetic approval record for exercising validator gates only; not a real person review."})
    data = {
        "schemaVersion": "1.0.0", "revision": "fixture:dataset-v1", "entities": e,
        "publicationManifests": [{
            "id": "fixture:learning-manifest", "scope": "learning", "generatedAt": "2026-09-25T00:00:00Z",
            "includedClaimIds": [claim["id"] for claim in e["claims"]], "includedTermIds": ["fixture:term-en"],
            "includedSpatialAnnotationIds": ["fixture:annotation"], "includedMeshMappingIds": ["fixture:mapping"], "includedMeshAssetIds": ["fixture:mesh-right"],
            "includedJointActionIds": [], "includedInnervationIds": [], "includedAssessmentIds": [],
            "attributions": [{"sourceId": "fixture:source", "text": "Synthetic validator fixture; no real anatomy source."}]
        }]
    }
    return data


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    positive = make_positive()
    write_json(FIXTURES / "positive.json", positive)
    negatives = []
    def negative(name: str, code: str, mutate, resign_targets: tuple[str, ...] = ()) -> None:
        data = copy.deepcopy(positive)
        mutate(data)
        for target in resign_targets:
            resign(data, target)
        write_json(FIXTURES / "negative" / f"{name}.json", data)
        negatives.append({"name": name, "path": f"work/evidence/T03/fixtures/negative/{name}.json", "expectedValid": False, "expectedDiagnostics": [code]})

    negative("orphan-id", "missing_reference", lambda d: d["entities"]["attachments"][0].update(targetStructureId="fixture:missing-structure"))
    negative("duplicate-id", "duplicate_id", lambda d: d["entities"]["muscleParts"][0].update(id="fixture:term-en"))
    negative("left-right-mismatch", "mesh_laterality_mismatch", lambda d: d["entities"]["meshMappings"][0].update(instanceIds=["fixture:instance-left"]), ("fixture:mapping",))
    negative("stale-annotation", "stale_annotation_reviewed", lambda d: d["entities"]["spatialAnnotations"][0].update(assetRevision="fixture:mesh-rev-0", assetRevisionHash="c" * 64), ("fixture:annotation",))
    negative("unsupported-reviewed", "reviewed_item_missing_evidence", lambda d: next(x for x in d["entities"]["claims"] if x["id"] == "fixture:claim-attachment").update(evidenceIds=[]), ("fixture:claim-attachment",))
    negative("ai-reviewer-cannot-approve", "reviewed_item_without_current_human_approval", lambda d: next(x for x in d["entities"]["reviews"] if x["targetId"] == "fixture:claim-attachment").update(reviewerKind="ai"))
    negative("thousand-fold-marker-error", "landmark_check_out_of_tolerance", lambda d: (d["entities"]["spatialAnnotations"][0]["geometry"].update(position=[100.0, 200.0, 300.0]), d["entities"]["spatialAnnotations"][0]["landmarkChecks"][0].update(observedAtlasPositionM=[100.0, 200.0, 300.0])), ("fixture:annotation",))
    negative("learning-license-not-granted", "publication_source_permission_missing", lambda d: d["entities"]["sources"][0]["license"].update(allowedUses=["internal"]))
    negative("learning-attribution-wrong", "publication_attribution_missing_or_wrong", lambda d: d["publicationManifests"][0]["attributions"][0].update(text="Wrong synthetic attribution."))
    negative("missing-annotation-units", "schema_required", lambda d: d["entities"]["spatialAnnotations"][0].pop("units"))
    negative("annotation-not-in-internal-meters", "schema_const", lambda d: d["entities"]["spatialAnnotations"][0].update(units="mm"))
    negative("t02-wrong-transform-scale", "t02_transform_contract_mismatch", lambda d: d["entities"]["spatialAnnotations"][0]["transformChain"][0].update(scale=1.0), ("fixture:annotation",))
    negative("t02-wrong-rotation", "t02_transform_contract_mismatch", lambda d: d["entities"]["spatialAnnotations"][0]["transformChain"][0].update(rotationMatrix=[[1,0,0],[0,1,0],[0,0,1]]), ("fixture:annotation",))
    negative("stale-review-content-hash", "reviewed_item_without_current_human_approval", lambda d: d["entities"]["spatialAnnotations"][0].update(precision="approximate_extent"))
    negative("parent-cycle", "parent_cycle", lambda d: d["entities"]["structures"][0].update(parentId="fixture:structure-tendon"))
    negative("missing-hani-not-auto-translated", "unreviewed_hani_term_filled", lambda d: next(x for x in d["entities"]["terms"] if x["id"] == "fixture:term-hani-missing").update(text="合成翻譯", missingReason=None))

    index = {
        "purpose": "Synthetic-only contract fixtures; no anatomy source data, actual approval, or clinical values.",
        "positiveFixture": "work/evidence/T03/fixtures/positive.json",
        "expectedIndividualMuscleConceptCount": 1,
        "fixtures": [{"name": "positive-complete-synthetic-contract", "path": "work/evidence/T03/fixtures/positive.json", "expectedValid": True}, *negatives]
    }
    write_json(FIXTURES / "index.json", index)


if __name__ == "__main__":
    main()
