#!/usr/bin/env python3
"""Build or check the T62 source-only text nerve registry from frozen T61/T98 inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RAW = "work/evidence/T98/blender-raw-object-inventory.json"
FRAME = "work/evidence/T98/astra-resolution-2026-09-29/frame-contract.json"
RUNTIME = "work/evidence/T62/runtime-check.json"
HANDOFF = "work/evidence/T61/T62-handoff.json"
REFERENCES = "work/evidence/T62/source-references.json"
COMPILED = "atlas-data/source-cache/datasets/za/compiled/manifest.json"
ZA_OVERLAY = "atlas-data/overlays/za-local-integration.json"
OUT_REGISTRY = "atlas-data/overlays/nerve-support-t62.json"
OUT_GEOMETRY = "work/evidence/T62/geometry-review.json"


def read(path: str) -> Any:
    return json.loads((ROOT / path).read_text())


def sha(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def build() -> dict[str, bytes]:
    raw = read(RAW)
    frame = read(FRAME)
    runtime = read(RUNTIME)
    handoff = read(HANDOFF)
    references = read(REFERENCES)  # Parse and hash the opened-source claim ledger before registry creation.
    compiled = read(COMPILED)
    za = read(ZA_OVERLAY)
    raw_by_name = {
        obj["sourceObjectLocator"]["objectIdName"]: (index, obj)
        for index, obj in enumerate(raw["allObjects"])
    }

    selected_names = [
        "Common fibular nerve.l", "Common fibular nerve.r",
        "Deep fibular nerve.l", "Deep fibular nerve.r",
        "Superficial fibular nerve.l", "Superficial fibular nerve.r",
    ]
    context_names = ["Sciatic nerve.l", "Sciatic nerve.r"]
    all_names = selected_names + context_names
    missing = [name for name in all_names if name not in raw_by_name]
    if missing:
        raise ValueError(f"exact raw object missing: {missing}")
    if runtime.get("blendLoaded") or runtime.get("evaluatedExporterRun"):
        raise ValueError("T62 must not use a Blender/.blend evaluated export")

    handoff_ids = {row["id"] for row in handoff["prioritizedSourceObservations"]}
    for name in selected_names:
        _, obj = raw_by_name[name]
        locator = obj["sourceObjectLocator"]
        node_id = f"za-c7010a9:raw:{locator['objectDataBlockPointer']}"
        if node_id not in handoff_ids:
            raise ValueError(f"T61 handoff object mismatch: {name} => {node_id}")
        if obj["dataKind"] != "Curve":
            raise ValueError(f"expected raw Curve observation: {name}")

    za_objects = {obj["sourceKey"]: (index, obj) for index, obj in enumerate(za["objects"])}
    compiled_by_name = {obj["name"]: obj for obj in compiled["instances"]}
    ta = {}
    for side, suffix in (("left", ".l"), ("right", ".r")):
        name = "Tibialis anterior muscle" + suffix
        source_key = compiled_by_name[name]["sourceKey"]
        if source_key not in za_objects:
            raise ValueError(f"existing target route missing: {name}")
        overlay_index, overlay = za_objects[source_key]
        if (overlay["targetId"], overlay["haConceptId"], overlay["side"], overlay["kind"]) != (
            "TA2:2644", "HA-M-000003", side, "muscle"
        ):
            raise ValueError(f"existing TA route identity/side mismatch: {name}")
        if not overlay["localDisplayEligible"]:
            raise ValueError(f"existing TA route not locally supported: {name}")
        ta[side] = {"sourceKey": source_key, "sourceName": name, "overlayIndex": overlay_index,
                    "targetId": overlay["targetId"], "existingHaConceptId": overlay["haConceptId"],
                    "side": side, "regionIds": overlay["regionIds"]}

    raw_sha, frame_sha = sha(RAW), sha(FRAME)
    runtime_sha, refs_sha = sha(RUNTIME), sha(REFERENCES)
    handoff_sha, overlay_sha = sha(HANDOFF), sha(ZA_OVERLAY)

    def reference_locator(source_id: str, claim_id: str) -> str:
        for source_index, source in enumerate(references["sources"]):
            if source["id"] != source_id:
                continue
            for claim_index, claim in enumerate(source["claims"]):
                if claim["id"] == claim_id:
                    return f"/sources/{source_index}/claims/{claim_index}"
        raise ValueError(f"opened reference claim locator not found: {source_id}/{claim_id}")

    objects = []
    for name in all_names:
        index, obj = raw_by_name[name]
        loc = obj["sourceObjectLocator"]
        matrix = obj["transformRaw"]["obmat"]
        side = "left" if name.endswith(".l") else "right"
        expected_region = "Left lower limb" if side == "left" else "Right lower limb"
        collections = [path[-1] for path in obj["collectionPaths"]]
        if expected_region not in collections:
            raise ValueError(f"explicit source-side collection missing: {name}")
        sign_consistent = matrix[12] > 0 if side == "left" else matrix[12] < 0
        if not sign_consistent:
            raise ValueError(f"raw transform side cross-check failed: {name}")
        objects.append({
            "sourceObjectId": loc["objectDataBlockPointer"],
            "sourceObjectName": loc["objectIdName"],
            "sourceFileSha256": loc["sourceFileSha256"],
            "dataKind": obj["dataKind"], "dataBlockPointer": obj["dataPointer"],
            "dataBlockName": obj["dataBlockName"], "sideFromExactSourceLabel": side,
            "explicitRegionCollection": expected_region,
            "sideCoordinateCrosscheck": {
                "frameContractId": frame["sourceFrameId"],
                "positiveX": frame["sourceAxes"]["positiveX"],
                "rawObjectTranslationX": matrix[12],
                "expectedSubjectSide": "subject_left" if side == "left" else "subject_right",
                "signConsistent": sign_consistent,
                "meaning": "serialized object-transform consistency only; not evaluated curve side or placement approval"
            },
            "sourceParent": {"pointer": obj["parentObjectPointer"], "name": obj["parentObjectName"]},
            "collectionPaths": obj["collectionPaths"], "rawObjectMatrix": matrix,
            "rawLinearDeterminant": obj["serializedObjectMatrixLinearDeterminant"],
            "modifiers": obj["modifierEvidence"], "constraints": obj["constraintEvidence"],
            "animationDataPointer": obj["animationDataPointer"],
            "collectionInstancePointer": obj["collectionInstancePointer"],
            "sourceUnitContext": "m from source-scene setting; curve-point evaluation was not performed",
            "sourcePoseId": None, "registeredTargetFrameId": None,
            "evaluatedGeometryHash": None, "topologyHash": None,
            "geometryStatus": "not_evaluated_or_accepted", "placementStatus": "not_registered",
            "reason": "No approved evaluated-curve export, nerve-specific pose binding, or target-frame placement proof."
        })

    geometry = {
        "schemaVersion": "t62-nerve-geometry-review-v1", "taskId": "T62", "sourceOnly": True,
        "references": {
            "rawInventory": {"path": RAW, "sha256": raw_sha},
            "frameContract": {"path": FRAME, "sha256": frame_sha},
            "runtimeCheck": {"path": RUNTIME, "sha256": runtime_sha},
            "T61Handoff": {"path": HANDOFF, "sha256": handoff_sha}
        },
        "runtimeDecision": {
            "version": runtime["observedVersion"], "executableSha256": runtime["executableSha256"],
            "codesignStatus": runtime["codesignVerification"]["status"],
            "historicalAttestation": runtime["historicalAttestation"],
            "sourceArchiveExecuted": False, "blendLoaded": False, "evaluatedExporterRun": False
        },
        "frameAndPoseDecision": {
            "observedSceneFrameId": frame["sourceFrameId"], "sourceUnit": frame["sourceUnit"],
            "sourceAxes": frame["sourceAxes"], "useForNerveSideCrosscheckOnly": True,
            "registeredNerveSourceFrameId": None, "registeredTargetFrameId": None,
            "sourcePoseId": None,
            "whyNotAccepted": "Scene-level frame evidence is not nerve-specific evaluated-geometry, pose, or placement proof."
        },
        "counts": {"rawNerveObjectObservations": len(objects), "rawCurveObjects": sum(x["dataKind"] == "Curve" for x in objects),
                   "evaluatedGeometryAccepted": 0, "registeredPlacement": 0, "validatedPose": 0},
        "objects": objects, "sideMatchedExistingTAMuscleTargets": ta,
        "limitations": [
            "Raw Object matrices are serialized source metadata, not evaluated nerve curves.",
            "Source nerve objects are not rendered, picked, or accepted as 3D paths.",
            "No branch point or course coordinate is derived from bounds or object origin.",
            "No geometry is modified, mirrored, split, or exported."
        ]
    }

    evidence: list[dict[str, Any]] = []
    instances = []
    relations = []
    targets = []
    regional_bindings = []

    def add_ev(eid: str, source: str, source_sha: str, locator: str, subject: str, predicate: str,
               object_id: str | None = None, status: str = "verified_local", value: str | None = None) -> str:
        row = {"id": eid, "sourcePath": source, "sourceSha256": source_sha, "locator": locator,
               "subjectId": subject, "predicate": predicate, "objectId": object_id, "status": status}
        if value is not None:
            row["value"] = value
        evidence.append(row)
        return eid

    def row_id(name: str) -> str:
        return "za-c7010a9:raw:" + raw_by_name[name][1]["sourceObjectLocator"]["objectDataBlockPointer"]

    node_meta = {
        "Sciatic nerve.l": ("neural_context", [], "Sciatic nerve", "context"),
        "Sciatic nerve.r": ("neural_context", [], "Sciatic nerve", "context"),
        "Common fibular nerve.l": ("branch", ["leg"], "Common fibular nerve", "supported"),
        "Common fibular nerve.r": ("branch", ["leg"], "Common fibular nerve", "supported"),
        "Deep fibular nerve.l": ("branch", ["leg"], "Deep fibular nerve", "supported"),
        "Deep fibular nerve.r": ("branch", ["leg"], "Deep fibular nerve", "supported"),
        "Superficial fibular nerve.l": ("branch", ["leg"], "Superficial fibular nerve", "supported"),
        "Superficial fibular nerve.r": ("branch", ["leg"], "Superficial fibular nerve", "supported")
    }

    for name in all_names:
        index, obj = raw_by_name[name]
        locator = obj["sourceObjectLocator"]
        nid = row_id(name)
        side = "left" if name.endswith(".l") else "right"
        suffix = ".l" if side == "left" else ".r"
        scope, region_ids, base_name, class_name = node_meta[name]
        loc = f"/allObjects/{index}"
        ids = [
            add_ev(nid + ":identity", RAW, raw_sha, loc + "/sourceObjectLocator/objectIdName", nid, "identity",
                   value=f"Exact pinned source object name {name}; Curve object label identity only."),
            add_ev(nid + ":side", RAW, raw_sha, loc + "/sourceObjectLocator/objectIdName and collectionPaths[*]", nid, "side",
                   value=f"Exact source suffix {suffix} and explicit {('Left' if side == 'left' else 'Right')} lower limb collection agree."),
            add_ev(nid + ":side-axis-crosscheck", FRAME, frame_sha,
                   "/sourceAxes/positiveX plus " + loc + "/transformRaw/obmat[12]", nid, "side",
                   value=f"Scene axis says +X is subject-left; raw translation X={obj['transformRaw']['obmat'][12]:.9f} has matching sign; not target placement."),
        ]
        claim_id = "sciatic-common-and-terminal-branch-hierarchy"
        ids.append(add_ev(nid + ":scope-literature", REFERENCES, refs_sha,
                          reference_locator("shekhawat-2025-fibular-branches", claim_id), nid, "scope",
                          value=f"Opened academic text classifies {base_name} in the fibular branch hierarchy; scope={scope}; taxonomy only."))
        ids.append(add_ev(nid + ":scope-source-context", RAW, raw_sha, loc + "/collectionPaths and parentObjectName",
                          nid, "scope", value=f"Exact source nerve hierarchy; parent={obj['parentObjectName'] or 'none'}."))
        if class_name == "supported":
            region_name = "Left lower limb" if side == "left" else "Right lower limb"
            region_evidence_id = add_ev(nid + ":region-context", RAW, raw_sha,
                                        loc + "/collectionPaths[*] ending in " + region_name,
                                        nid, "scope",
                                        value="Leg is a text-only teaching context corroborated by lower-limb object collection and opened lower-leg branch literature; not full course extent.")
            ids.extend([
                region_evidence_id,
                add_ev(nid + ":pose-pending", RAW, raw_sha, loc + "/transformRaw and raw-only method", nid, "pose",
                       status="candidate", value="Serialized transform only; no nerve-specific evaluated rest-pose ID was established."),
                add_ev(nid + ":frame-pending", FRAME, frame_sha, "/sourceFrameId and sourceAxes", nid, "frame",
                       status="candidate", value="Scene frame used only for side cross-check; no nerve-specific target-frame binding accepted."),
                add_ev(nid + ":placement-pending", RAW, raw_sha, loc + "/transformRaw/obmat", nid, "placement",
                       status="candidate", value="Object origin/matrix is not evaluated nerve geometry or anatomical placement proof.")
            ])
            regional_bindings.append({"instanceId": nid, "regionIds": ["leg"], "evidenceIds": [region_evidence_id],
                                     "extentMeaning": "display_context_only"})
            selection, holds = "text_only", []
        else:
            ids.append(add_ev(nid + ":geometry-not-selected", RAW, raw_sha, loc + "/dataKind and raw-only scopeLimit",
                              nid, "placement", status="candidate", value="Context ancestor only; no region route or learner selection."))
            selection, holds = "unsupported", ["ancestor_context_only_no_learner_route"]
        instances.append({
            "id": nid, "sourceNamespace": "za-c7010a9", "sourceObjectId": locator["objectDataBlockPointer"],
            "conceptId": None, "side": side, "scope": scope,
            "names": {"koTraditional": None, "koModern": None, "en": base_name},
            "regionIds": region_ids, "identity": "verified_local", "evidenceIds": ids,
            "geometry": None, "localSelection": selection, "hardHolds": holds,
            "sourceOnly": True, "humanReview": "not_performed", "publicRedistribution": "held"
        })

    # Use already existing side-specific tibialis anterior routes as relation targets, not new HA IDs.
    for side in ("left", "right"):
        target = ta[side]
        tid = target["sourceKey"]
        overlay_index = target["overlayIndex"]
        target_evidence = [
            add_ev(tid + ":identity", ZA_OVERLAY, overlay_sha, f"/objects/{overlay_index}", tid, "identity",
                   value=f"Existing source route {target['sourceName']} -> {target['targetId']}; HA {target['existingHaConceptId']} unchanged."),
            add_ev(tid + ":side", ZA_OVERLAY, overlay_sha, f"/objects/{overlay_index}/side", tid, "side",
                   value=f"Existing route side is explicitly {side}; no side inferred from a generic parent."),
            add_ev(tid + ":scope", ZA_OVERLAY, overlay_sha, f"/objects/{overlay_index}/learnerConceptLinks", tid, "scope",
                   value="Existing exact tibialis anterior target route; T62 does not revalidate its full surface extent.")
        ]
        targets.append({"id": tid, "kind": "muscle", "side": side, "evidenceIds": target_evidence})

    def branch(child_name: str, parent_name: str, claim_id: str) -> None:
        child, parent = row_id(child_name), row_id(parent_name)
        index, child_obj = raw_by_name[child_name]
        e1 = add_ev(child + ":branch-parent", RAW, raw_sha,
                    f"/allObjects/{index}/parentObjectPointer and parentObjectName", child, "branch", parent,
                    value=f"Exact source parent pointer resolves to {child_obj['parentObjectName']}; no branch-point coordinates." )
        e2 = add_ev(child + ":branch-literature", REFERENCES, refs_sha,
                    reference_locator("shekhawat-2025-fibular-branches", claim_id), child, "branch", parent,
                    value="Opened academic text supports general branch topology; not an individual variant course.")
        relations.append({"id": child + ":branch_of:" + parent, "fromId": child, "toId": parent,
                          "kind": "branch_of", "targetKind": "nerve", "evidenceIds": [e1, e2],
                          "status": "verified_local"})

    for side_suffix in ("l", "r"):
        branch("Common fibular nerve." + side_suffix, "Sciatic nerve." + side_suffix,
               "sciatic-common-and-terminal-branch-hierarchy")
        branch("Deep fibular nerve." + side_suffix, "Common fibular nerve." + side_suffix,
               "sciatic-common-and-terminal-branch-hierarchy")
        branch("Superficial fibular nerve." + side_suffix, "Common fibular nerve." + side_suffix,
               "sciatic-common-and-terminal-branch-hierarchy")
    for side, suffix in (("left", "l"), ("right", "r")):
        nerve_id, target_id = row_id("Deep fibular nerve." + suffix), ta[side]["sourceKey"]
        evidence_id = add_ev(nerve_id + ":motor-innervation:" + side, REFERENCES, refs_sha,
                             reference_locator("congio-2026-deep-fibular-ta-innervation", "deep-fibular-to-tibialis-anterior"),
                             nerve_id, "motor_innervation", target_id,
                             value="Presence only: deep fibular branches enter side-matched tibialis anterior; not sole supply, full course, or model entry coordinates.")
        relations.append({"id": nerve_id + ":motor_innervates:" + target_id, "fromId": nerve_id,
                          "toId": target_id, "kind": "motor_innervation", "targetKind": "muscle",
                          "targetSide": side, "evidenceIds": [evidence_id], "status": "verified_local"})

    registry = {
        "schemaVersion": "nerve-support-v1", "contractRevision": "T62-verified-local-text-branches-2026-10-01",
        "instances": instances, "evidence": evidence, "relations": relations, "targets": targets,
        "regionalBindings": regional_bindings,
        "registrationScope": {
            "selectedT61PriorityObjects": 6, "contextOnlyAncestors": 2, "textOnlySelectable": 6,
            "evaluatedGeometryAccepted": 0, "publicRedistribution": "held", "humanReview": "not_performed",
            "sourceOnly": True, "canonicalHaIdsCreated": 0,
            "denominatorsPreserved": {"targets": 542, "memberships": 563, "regions": 12,
                "existingCanonicalHaBindings": 130, "historical163": {"total": 163, "classes": [6, 20, 135, 2]}}
        },
        "geometryReview": OUT_GEOMETRY, "referenceReview": REFERENCES
    }
    return {OUT_GEOMETRY: canonical(geometry), OUT_REGISTRY: canonical(registry)}


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true", help="write task-owned outputs")
    group.add_argument("--check", action="store_true", help="compare outputs without writing")
    args = parser.parse_args()
    outputs = build()
    errors = []
    for path, contents in outputs.items():
        target = ROOT / path
        if args.write:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(contents)
            print(f"WROTE {path} sha256={hashlib.sha256(contents).hexdigest()}")
        elif not target.is_file() or target.read_bytes() != contents:
            errors.append(path)
        else:
            print(f"OK {path} sha256={hashlib.sha256(contents).hexdigest()}")
    if errors:
        print("STALE_OR_MISSING " + ", ".join(errors))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
