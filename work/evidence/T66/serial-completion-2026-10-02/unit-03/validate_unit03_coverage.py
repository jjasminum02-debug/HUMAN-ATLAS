#!/usr/bin/env python3
"""Validate U03 source/action responsibility against typed runtime registrations."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
UNIT = ROOT / "work/evidence/T66/serial-completion-2026-10-02/unit-03"
QUEUE = UNIT / "serial-queue.json"
REGISTRATION = UNIT / "registration.json"
LEARNING = ROOT / "atlas-data/motion/motion-learning.json"
DATASET = ROOT / "atlas-data/source-cache/datasets/za/compiled/manifest.json"

def read(p): return json.loads(p.read_text())
def sha(data): return hashlib.sha256(data).hexdigest()
def enc(value): return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()

def main():
    queue, receipt, bundle, dataset = map(read, [QUEUE, REGISTRATION, LEARNING, DATASET])
    if receipt["schemaVersion"] != "t66-u03-registration-r4":
        raise SystemExit("U03 registration revision mismatch")
    if receipt["datasetSha256"] != sha((ROOT / "atlas-data/source-cache/datasets/za/compiled/manifest.json").read_bytes()):
        raise SystemExit("source dataset hash drift")
    ds = {row["sourceKey"]: row for row in dataset["instances"]}
    runtime = {}
    for asset in bundle["motionAssets"]:
        binding = asset.get("sourceBinding", {})
        if asset.get("id", "").startswith("T66-U03-"):
            runtime[(binding.get("sourceFamilyId"), binding.get("subjectSourceKey"))] = asset
    candidate_rows = [row for row in queue["responsibilityKeys"] if row["role"] == "source_action_candidate"]
    by_action = {a["action"]: a for a in queue["actionSpecs"]}
    # The frozen queue omitted the directly supported, source-bound serratus
    # protraction candidates even though this unit has an authored protraction
    # package and the opened official table explicitly assigns that action.
    # Add only these exact two side-labelled source rows; do not infer a new
    # action for pectoralis minor or a trapezius part.
    existing = {(r["key"]["family"], r["key"]["side"], r["key"]["sourceKey"]) for r in candidate_rows}
    serratus = {
        "left": {"sourceKey": "ZA-c7010a9-0bb829c1053a80f6ef177bcd", "sourceName": "Serratus anterior muscle.l",
                 "geometrySha256": "c71fa0afde5a8dd4547d79dee9a5bdba18957e581bfd6057f31ce67b29366c9b"},
        "right": {"sourceKey": "ZA-c7010a9-6bc46621886fbf8f62657278", "sourceName": "Serratus anterior muscle.r",
                  "geometrySha256": "3223ba9095bcc7656bebb00a40b366d5e68758d5b05698119ab46400ad7de38d"},
    }
    for side, item in serratus.items():
        identity = ("shoulder-girdle-protraction", side, item["sourceKey"])
        if identity in existing: continue
        queue["responsibilityKeys"].append({
            "key": {"family": identity[0], "side": side, "action": identity[0], "sourceKey": item["sourceKey"]},
            "sourceName": item["sourceName"], "subjectKind": "muscle", "role": "source_action_candidate",
            "sourceRefs": [{"url": "https://openstax.org/books/anatomy-and-physiology/pages/11-5-muscles-of-the-pectoral-girdle-and-upper-limbs",
                            "locator": "§Muscles That Position the Pectoral Girdle, Table 11.8; lines 29–45; Serratus anterior row: scapula protraction; rib elevation is also listed"}],
            "attachmentScope": {"origin": None, "insertion": None, "coordinateUse": "none; posture-only binding"},
            "implementationStatus": "queued_for_authoring_and_runtime_registration",
            "sourceGeometrySha256": item["geometrySha256"], "sourceOnly": False,
            "humanReview": "not_performed", "publicRedistribution": "held",
            "wholeTargetExtentApproved": False, "canonicalBindingAdded": False,
        })
    candidate_rows = [row for row in queue["responsibilityKeys"] if row["role"] == "source_action_candidate"]
    outcomes = []
    for row in candidate_rows:
        key = row["key"]
        action = by_action[key["action"]]
        family = f"{action['family']}-{key['side']}"
        asset = runtime.get((family, key["sourceKey"]))
        source = ds.get(key["sourceKey"])
        if not source:
            raise SystemExit(f"candidate source missing from pinned source manifest: {key}")
        if source.get("sourceLabelSide") not in (None, key["side"]):
            raise SystemExit(f"side mismatch: {key} -> {source.get('sourceLabelSide')}")
        if asset:
            pose_label = asset.get("poseControl", {}).get("label", "")
            if not pose_label or "관찰" not in pose_label:
                raise SystemExit(f"pose observation label mismatch for {key}: {pose_label}")
            if asset.get("technicalStatus") != "binding_verified":
                raise SystemExit(f"runtime binding is not verified: {key}")
            row["implementationStatus"] = "implemented_verified"
            row["implementationScope"] = "exact_source_bound_posture_observation"
            row["primeMoverDemonstration"] = "not_claimed"
            row["evidence"] = {"registration": "work/evidence/T66/serial-completion-2026-10-02/unit-03/registration.json",
                                "assetId": asset["id"], "motionSha256": asset["sha256"],
                                "sourceGeometrySha256": source["lods"]["overview"]["sha256"],
                                "actionEvidence": action["evidence"]}
            outcomes.append({"key": key, "status": row["implementationStatus"], "assetId": asset["id"]})
        else:
            if key["family"] == "wrist-ulnar-deviation" and row["sourceName"].startswith("Ulnar head of flexor carpi ulnaris"):
                row["implementationStatus"] = "processed_with_content_gaps"
                row["implementationScope"] = "not_bound_to_directional_deviation; source claim is group-level wrist flexion and sideward wording is not normalized"
                row["primeMoverDemonstration"] = "not_claimed"
                row["evidence"] = {"gap": "qualitative_direction_unresolved", "actionClaim": "whole flexor carpi ulnaris group only; assists wrist flexion; sideward direction is described relative to body and not normalized to radial/ulnar",
                                    "sourceReference": "work/evidence/T66/serial-completion-2026-10-02/unit-03/action-scope-ledger.json#wrist_flexor_carpi_ulnaris_group",
                                    "sourceGeometrySha256": source["lods"]["overview"]["sha256"]}
            else:
                row["implementationStatus"] = "blocked_by_product_defect"
                row["implementationScope"] = "missing_expected_source_bound_posture_observation"
                row["primeMoverDemonstration"] = "not_claimed"
                row["evidence"] = {"missingPackage": family, "sourceGeometrySha256": source["lods"]["overview"]["sha256"]}
            outcomes.append({"key": key, "status": row["implementationStatus"], "assetId": None})

    status_counts = {}
    for row in candidate_rows:
        status_counts[row["implementationStatus"]] = status_counts.get(row["implementationStatus"], 0) + 1
    output = {"schemaVersion": "t66-u03-responsibility-disposition-v1", "registrationSha256": sha(REGISTRATION.read_bytes()),
              "queueInputSha256": queue["sourceQueueBaselineSha256"], "candidateResponsibilities": len(candidate_rows),
              "statusCounts": status_counts, "activeMuscleContractionClaims": 0,
              "scopeLimit": "registered selectors are source-bound posture observations with passive surface deformation; they are not prime-mover demos, muscle activation, measured axes/footprints, approved ROM, or human review",
              "items": outcomes}
    # Single-writer task-owned queue update. All 674 out-of-action-scope rows remain unchanged.
    QUEUE.write_bytes(enc(queue))
    path = UNIT / "responsibility-disposition-r2.json"
    path.write_bytes(enc(output))
    if status_counts.get("blocked_by_product_defect", 0):
        raise SystemExit(f"unregistered U03 action candidate source rows: {status_counts}")
    print(json.dumps({"candidateResponsibilities": len(candidate_rows), "statusCounts": status_counts,
                      "outOfScopeRowsPreserved": sum(x["role"] != "source_action_candidate" for x in queue["responsibilityKeys"])}, ensure_ascii=False))

if __name__ == "__main__": main()
