#!/usr/bin/env python3
"""Reproducibly register the four unit-02 hip/knee source-frame packages.

The script refuses to rebase or overwrite unit evidence and verifies the two
shared learner files that were already dirty at the unit-02 baseline.
"""
from __future__ import annotations

import copy
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
UNIT = ROOT / "work/evidence/T66/serial-completion-2026-10-02/unit-02"
TRIALS = UNIT / "trials-r1"
DATASET_REL = "atlas-data/source-cache/datasets/za/compiled/manifest.json"
EXPECTED_FAMILIES = (
    "hip-flexion-left", "hip-flexion-right", "knee-flexion-left", "knee-flexion-right"
)
BASELINE_SHA = {
    "atlas-data/motion/motion-scenes.json": "2a23cd4cb79a98bafe00740eddcf5c992aac7912dc3ad8c7a801bc79c703c7d0",
    "atlas-data/motion/motion-asset-sources.json": "a6ed4ab0257a0e83053b341a23aac37eec0041b773980ccf72c9ef8b610fa72f",
}
PREFLIGHT = {
    "atlas-data/motion/motion-learning.json": "d080d8bc9640f0797f327834ce8c4279105ff4182a1108c40e022bb3fc932389",
    "atlas-data/motion/authoring/registry.json": "a4f033de6054681fd910d0082cb20e10bac0ad90e4fe3f72cdb0e246c2678bcd",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read(rel: str):
    return json.loads((ROOT / rel).read_text())


def encode(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()


def write_new_or_identical(path: Path, payload: bytes):
    if path.exists():
        if path.read_bytes() != payload:
            raise RuntimeError(f"refusing to overwrite non-identical existing output: {path.relative_to(ROOT)}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)


def value_hash(value) -> str:
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())


def main():
    for rel, expected in BASELINE_SHA.items():
        actual = sha((ROOT / rel).read_bytes())
        if actual != expected:
            raise RuntimeError(f"shared pre-existing WIP changed since unit baseline: {rel}: {actual}")
    for rel, expected in PREFLIGHT.items():
        actual = sha((ROOT / rel).read_bytes())
        if actual != expected:
            raise RuntimeError(f"clean shared input changed after registration preflight: {rel}: {actual}")

    manifest_path = ROOT / DATASET_REL
    manifest = json.loads(manifest_path.read_text())
    manifest_sha = sha(manifest_path.read_bytes())
    name_by_key = {row["sourceKey"]: row["name"] for row in manifest["instances"]}
    row_by_key = {row["sourceKey"]: row for row in manifest["instances"]}
    overlay_rel = "atlas-data/overlays/za-local-integration.json"
    overlay_sha = sha((ROOT / overlay_rel).read_bytes())

    summary_path = TRIALS / "summary.json"
    summary = json.loads(summary_path.read_text())
    if set(row["familyId"] for row in summary) != set(EXPECTED_FAMILIES):
        raise RuntimeError("unit-02 candidate family set differs from frozen four-family scope")
    if not all(row["sampledContactFailures"] == 0 and row["newContainmentMaximum"] == 0
               and row["keyPoseFrameReplayPass"] and row["movingPatella"] == (row["kind"] == "knee")
               for row in summary):
        raise RuntimeError("candidate contact / exact replay / patella contract did not pass")

    # Keep the prior unit's learner-safe template as the schema contract.
    bundle = read("atlas-data/motion/motion-learning.json")
    template = next(a for a in bundle["motionAssets"]
                    if a.get("sourceBinding", {}).get("sourceFamilyId") == "elbow-flexion-left")
    registry = read("atlas-data/motion/authoring/registry.json")
    scenes = read("atlas-data/motion/motion-scenes.json")
    sources = read("atlas-data/motion/motion-asset-sources.json")
    if any(row["id"].startswith("T66-U02-") for group in ("muscleActions", "motionDefinitions", "motionAssets")
           for row in bundle[group]):
        raise RuntimeError("unit-02 records already exist; use the recorded registration output")
    if any(row["id"].startswith("T66-U02-") for row in registry["records"]):
        raise RuntimeError("unit-02 authoring registry entries already exist")
    if any(row["id"].startswith("T66-U02-") for row in scenes["sceneManifests"]):
        raise RuntimeError("unit-02 scenes already exist")

    source_claims = read("atlas-data/terminology/muscle-attachment-content-2026-10-02.json")["records"]
    claims_by_key = {}
    for row in source_claims:
        for key in row.get("sourceKeys", []):
            claims_by_key.setdefault(key, row)

    registration_rows = []
    added_actions, added_definitions, added_assets, added_scenes, added_authors = [], [], [], [], []
    for family_id in EXPECTED_FAMILIES:
        candidate_dir = TRIALS / family_id
        payload_path = candidate_dir / "input.json"
        record_path = candidate_dir / "authoring-record.json"
        contact_path = candidate_dir / "contact-qc.json"
        pose_path = candidate_dir / "glb-pose-qc.json"
        interpolation_path = UNIT / "candidate-interpolation-r1.json"
        payload = json.loads(payload_path.read_text())
        record = json.loads(record_path.read_text())
        contact_qc = json.loads(contact_path.read_text())
        pose_qc = json.loads(pose_path.read_text())
        if payload["family"]["id"] != family_id or payload["dataset"]["sha256"] != manifest_sha:
            raise RuntimeError(f"frozen source/manifest mismatch: {family_id}")
        if payload["dataset"]["path"] != DATASET_REL or payload["family"]["frameId"] != manifest["frameContract"]["targetFrameId"]:
            raise RuntimeError(f"dataset frame contract mismatch: {family_id}")
        if record["rights"] != {"sourceOnly": True, "localUseRights": "inherits_pinned_source_decision",
                                 "publicRedistribution": "held", "humanReview": "not_performed"}:
            raise RuntimeError(f"rights/review state drift: {family_id}")
        if contact_qc.get("failures") or not pose_qc.get("passed"):
            raise RuntimeError(f"candidate QC failure: {family_id}")

        interp = json.loads(interpolation_path.read_text())
        own_interp = [row for row in interp["rows"] if row["familyId"] == family_id]
        expected_deformers = {m["sourceKey"] for m in payload["members"] if m["role"] == "deforming_passive_surface"}
        if {row["targetSourceKey"] for row in own_interp} != expected_deformers or not all(row["passed"] for row in own_interp):
            raise RuntimeError(f"full actual emitted-GLB interpolation ledger missing/failing: {family_id}")

        side = payload["side"]
        if side not in ("left", "right"):
            raise RuntimeError(f"candidate side is not explicit: {family_id}")
        for member in payload["members"]:
            source_row = row_by_key.get(member["sourceKey"])
            if source_row is None:
                raise RuntimeError(f"unresolved exact source object: {family_id}/{member['sourceKey']}")
            label_side = source_row.get("sourceLabelSide")
            if label_side in ("left", "right") and label_side != side:
                raise RuntimeError(f"side mismatch: {family_id}/{source_row['name']}")
            if source_row.get("appDisplayRights") != "held_not_approved_by_this_task":
                raise RuntimeError(f"source display-rights state changed: {family_id}/{source_row['name']}")
            if source_row.get("publicRedistribution") != "held" or source_row.get("humanReview") != "not_performed":
                raise RuntimeError(f"source rights/review state changed: {family_id}/{source_row['name']}")

        moving = [m for m in record["members"] if m["role"] == "moving_structure"]
        fixed = [m for m in record["members"] if m["role"] == "fixed_structure"]
        deforming = [m for m in record["members"] if m["role"] == "deforming_passive_surface"]
        co_moving = [m for m in record["members"] if m["role"] == "co_moving_context"]
        if len(record["members"]) != len(payload["members"]) or not moving or not fixed or not deforming:
            raise RuntimeError(f"source roles/inventory mismatch: {family_id}")

        # Side-specific direct selectors include only explicit side-bearing bones
        # and deformed side-bearing muscle surfaces. Midline vertebrae remain
        # fixed scene context and are not presented as bilateral selections.
        subjects = []
        for role_rows in (moving, fixed, deforming):
            for member in role_rows:
                source_key = member["sourceKey"]
                source_row = row_by_key[source_key]
                if source_row.get("sourceLabelSide") != side:
                    continue
                subjects.append(member)
        if not subjects:
            raise RuntimeError(f"no exact side-specific learner subjects: {family_id}")

        stem = "T66-U02-" + family_id
        motion_src = candidate_dir / "motion.glb"
        reference_src = candidate_dir / "reference.glb"
        motion_rel = f"atlas-data/assets/motion/t66-unit02-{family_id}/motion.glb"
        reference_rel = f"atlas-data/assets/derived-glb/t66-unit02-{family_id}/reference.glb"
        motion_bytes, reference_bytes = motion_src.read_bytes(), reference_src.read_bytes()
        motion_sha, reference_sha = sha(motion_bytes), sha(reference_bytes)
        write_new_or_identical(ROOT / motion_rel, motion_bytes)
        write_new_or_identical(ROOT / reference_rel, reference_bytes)

        context_id = stem + "-POSE-CONTEXT"
        end_pose = stem + "-END"
        label = payload["family"]["label"]
        action_text = f"{label} 자세에서 선택한 표면과 주변 구조의 변화를 관찰합니다."
        posture_text = "고정된 시작 자세를 기준으로 같은 장면의 관절 자세를 보는 교육용 관찰입니다."
        context_text = "표면 변형과 뼈의 공동 이동을 보여 줍니다. 근육 활성도·수축량·정상 운동 범위를 계산하지 않습니다."
        claims = [
            {"id": stem + "-ACTION-FIELD", "field": "action", "appliesTo": "action_explanation", "contextId": None, "value": action_text},
            {"id": stem + "-POSTURE-FIELD", "field": "model_posture", "appliesTo": "posture_condition", "contextId": None, "value": posture_text},
            {"id": stem + "-CONTEXT-FIELD", "field": "model_context", "appliesTo": "context_role", "contextId": context_id, "value": context_text},
        ]
        qualitative_context = []
        if payload["family"]["type"] == "knee":
            # Existing T90 summaries tie the actual quadriceps source surfaces
            # to patella/tibial-tuberosity context; those summaries are not human
            # approved and do not define coordinates or attachment footprints.
            for key in ("ZA-c7010a9-afb0624c66f652ea012c7534", "ZA-c7010a9-eb0a993e09d73159468116ce",
                        "ZA-c7010a9-b27a5408d40608e18136196f", "ZA-c7010a9-f7d29d55434cdeb56f269047"):
                source_claim = claims_by_key.get(key)
                if source_claim is None:
                    continue
                for field in ("origin", "insertion"):
                    evidence = source_claim.get("fieldEvidence", {}).get(field)
                    if evidence and evidence.get("sourceIds") == ["UAMS_LOWER_LIMB"]:
                        qualitative_context.append({
                            "sourceKey": key, "side": "left" if key in source_claim.get("sourceKeys", []) and source_claim.get("sourceSides", [])[source_claim.get("sourceKeys", []).index(key)] == "left" else "right",
                            "field": field, "learnerSummary": source_claim[field],
                            "evidenceState": source_claim.get("evidenceState"),
                            "summaryExtent": source_claim.get("summaryExtent"),
                            "sourceId": "UAMS_LOWER_LIMB", "locator": evidence.get("locator"),
                            "learnerValueSha256": evidence.get("learnerValueSha256"),
                            "reviewNotesSha256": evidence.get("reviewNotesSha256"),
                            "humanReview": source_claim.get("humanReview"),
                            "publicRedistribution": source_claim.get("publicRedistribution"),
                            "useLimit": "qualitative_attachment_context_only_not_coordinates_not_measured_footprint_not_anatomical_axis",
                        })
        unique_context = {row["sourceKey"] for row in qualitative_context}
        if payload["family"]["type"] == "knee" and not unique_context.intersection(expected_deformers):
            raise RuntimeError("existing quadriceps attachment context did not resolve to candidate source surface")

        dep_paths = [str(payload_path.relative_to(ROOT)), str(record_path.relative_to(ROOT)),
                     str(contact_path.relative_to(ROOT)), str(pose_path.relative_to(ROOT)),
                     str(interpolation_path.relative_to(ROOT)), motion_rel, reference_rel,
                     DATASET_REL, overlay_rel]
        authoring = {
            "schemaVersion": "t66-authoring-family-record-v1", "id": stem + "-AUTHORING",
            "sourceFamilyId": family_id, "side": side, "rights": copy.deepcopy(record["rights"]),
            "claims": claims, "supportedSubjectKeys": [m["sourceKey"] for m in subjects],
            "movingBoneKeys": [m["sourceKey"] for m in moving], "fixedBoneKeys": [m["sourceKey"] for m in fixed],
            "coMovingContextKeys": [m["sourceKey"] for m in co_moving],
            "passiveDeformationKeys": [m["sourceKey"] for m in deforming],
            "poseRange": {"referencePoseId": payload["family"]["referencePoseId"], "endPoseId": end_pose,
                "axis": payload["family"]["axis"], "pivotMetres": payload["family"]["pivotMetres"],
                "endDegrees": payload["family"]["endDegrees"],
                "meaning": "authored educational pose range, not a measured anatomical axis or normal physiological ROM"},
            "motionSha256": motion_sha, "restSha256": reference_sha,
            "measuredAnatomicalAxis": False, "measuredAttachmentFootprints": False,
            "anatomicalMotorRoleClaimed": False, "scope": "exact_source_surface_pose_observation",
            "qualitativeDirectionEvidence": payload["family"].get("qualitativeEvidence", []),
            "qualitativeAttachmentContext": qualitative_context,
            "cooperativeMotionLimits": (["Patella is included as a moving source bone in the shared educational flexion transform.",
                "No independent patellar glide/tilt or physiological tracking trajectory is asserted.",
                "Quadriceps attachment summaries justify contextual association only; they do not author attachment coordinates."]
                if payload["family"]["type"] == "knee" else [
                "Hip-bone/femur contact is an authored scene-fit adjustment, not a measured instantaneous axis."]),
            "geometryRecordPath": str(record_path.relative_to(ROOT)),
            "contactQcPath": str(contact_path.relative_to(ROOT)),
            "glbPoseQcPath": str(pose_path.relative_to(ROOT)),
            "interpolationQcPath": str(interpolation_path.relative_to(ROOT)),
            "verificationDependencies": [{"path": p, "sha256": sha((ROOT / p).read_bytes())} for p in dep_paths],
            "sourceManifestSha256": manifest_sha, "sourceOverlaySha256": overlay_sha,
        }
        authoring_rel = f"atlas-data/motion/authoring/t66-unit02-{family_id}.json"
        author_bytes = encode(authoring)
        write_new_or_identical(ROOT / authoring_rel, author_bytes)
        added_authors.append({"id": authoring["id"], "path": authoring_rel, "sha256": sha(author_bytes)})

        scene_id = stem + "-REFERENCE"
        scene = {
            "id": scene_id, "revision": manifest["revision"], "modelId": manifest["namespace"],
            "sourceAssetSha256": reference_sha, "frameId": payload["family"]["frameId"], "units": "m",
            "poseId": payload["family"]["referencePoseId"], "assetUri": reference_rel, "side": side,
            "sourceJoint": "authored-source-family-not-canonical-joint", "separateFromNavigationFrame": False,
            "annotationPolicy": {"verifiedBoneLocalBindings": [], "hideAllSpatialAnnotationsDuringMotion": True},
        }
        added_scenes.append(scene)
        static = {"sceneRevision": scene["revision"], "modelId": scene["modelId"],
                  "sourceAssetSha256": reference_sha, "frameId": scene["frameId"],
                  "units": "m", "sceneId": scene_id, "poseId": scene["poseId"]}
        for subject in subjects:
            role = subject["role"]
            kind = "muscle" if role == "deforming_passive_surface" else "bone"
            key = subject["sourceKey"]
            ident = stem + "-" + key
            refs = []
            for claim in claims if kind == "muscle" else claims[:1]:
                refs.append({"layer": "source_family_record", "field": claim["field"],
                    "appliesTo": claim["appliesTo"], "contextId": claim["contextId"],
                    "claimId": claim["id"], "valueHash": value_hash(claim["value"]),
                    "evidenceId": authoring["id"], "fieldEvidenceId": None})
            action = {
                "id": ident + "-ACTION", "subjectKind": kind, "subjectIds": [], "sourceSubjectKeys": [key],
                "sideApplicability": side, "jointBindingState": "source_family_bound", "sourceFamilyId": family_id,
                "jointBindingNote": "Exact pinned source-family pose observation; no canonical joint or muscle-activation claim.",
                "targetJointIds": [], "actionLabel": label + " 자세에서 관찰", "explanation": action_text,
                "postureConditions": [posture_text] if kind == "muscle" else [], "stabilizationConditions": [],
                "stabilizationNote": "주변의 고정·이동 구조를 함께 보여 주는 교육용 자세이며 정상 운동 범위가 아닙니다.",
                "contextRoles": ([{"contextId": context_id, "role": "unspecified", "contractionRole": "unspecified",
                                   "explanation": context_text}] if kind == "muscle" else []),
                "sourceRefs": refs, "legacyJointActionId": None,
            }
            definition = {
                "id": ident + "-MOTION", "actionId": action["id"], "instanceId": key, "side": side,
                "sourceFamilyId": family_id, "targetJointIds": [],
                "movingStructureIds": authoring["movingBoneKeys"], "fixedStructureIds": authoring["fixedBoneKeys"],
                "staticReference": static, "startPoseId": payload["family"]["referencePoseId"],
                "endPoseId": end_pose,
                "poseSourceRefs": [{"layer": "authoring_record", "field": "motion_pose_range",
                    "appliesTo": "motion_pose_range", "contextId": None,
                    "claimId": authoring["id"], "valueHash": value_hash(authoring["poseRange"]),
                    "evidenceId": authoring["id"], "fieldEvidenceId": None}],
            }
            asset = copy.deepcopy(template)
            asset.update({"id": ident + "-ASSET", "motionDefinitionId": definition["id"],
                "uri": motion_rel, "sha256": motion_sha,
                "revision": "t66-unit02-hip-knee-authored-r1", "technicalStatus": "binding_verified",
                "staticBinding": {"modelId": manifest["namespace"], "sourceAssetSha256": reference_sha,
                    "frameId": scene["frameId"], "units": "m", "sceneRevision": scene["revision"],
                    "sceneId": scene_id, "side": side, "referencePoseId": scene["poseId"]},
                "rig": {"id": stem + "-RIG", "nodeBindings": [
                    {"structureId": m["sourceKey"], "nodeId": m["nodeId"]} for m in moving]},
                "clip": {"id": payload["clipId"], "durationSeconds": payload["family"]["durationSeconds"],
                    "startPoseId": scene["poseId"], "endPoseId": end_pose},
                "poseControl": {"label": label, "startDegrees": 0,
                    "endDegrees": payload["family"]["endDegrees"], "combination": "single_dof_only"}})
            asset["sourceBinding"].update({"contractVersion": "t66-typed-source-motion-v2",
                "datasetNamespace": manifest["namespace"], "datasetRevision": manifest["revision"],
                "sourceOverlaySha256": overlay_sha, "subjectKind": kind,
                "subjectSourceKey": key, "sourceFamilyId": family_id,
                "frameId": scene["frameId"], "units": "m", "referencePoseId": scene["poseId"],
                "members": copy.deepcopy(record["members"])})
            added_actions.append(action)
            added_definitions.append(definition)
            added_assets.append(asset)
            registration_rows.append({"familyId": family_id, "side": side, "sourceKey": key,
                "sourceName": name_by_key[key], "subjectKind": kind, "role": role,
                "assetId": asset["id"], "motionUri": motion_rel, "motionSha256": motion_sha,
                "sceneId": scene_id, "authoringEvidenceId": authoring["id"],
                "scope": "exact_source_surface_pose_observation", "localTechnicalOnly": True,
                "publicRedistribution": "held", "humanReview": "not_performed"})

    bundle["muscleActions"].extend(added_actions)
    bundle["motionDefinitions"].extend(added_definitions)
    bundle["motionAssets"].extend(added_assets)
    bundle["revision"] = "t66-unit02-hip-knee-r1"
    registry["records"].extend(added_authors)
    scenes["sceneManifests"].extend(added_scenes)
    added_asset_ids = [row["id"] for row in added_assets]
    sources["productionMotionAssetIds"] = list(dict.fromkeys(sources["productionMotionAssetIds"] + added_asset_ids))

    output_paths = {
        "atlas-data/motion/motion-learning.json": encode(bundle),
        "atlas-data/motion/authoring/registry.json": encode(registry),
        "atlas-data/motion/motion-scenes.json": encode(scenes),
        "atlas-data/motion/motion-asset-sources.json": encode(sources),
    }
    for rel, data in output_paths.items():
        (ROOT / rel).write_bytes(data)

    out = {
        "schemaVersion": "t66-unit02-registration-v1", "families": list(EXPECTED_FAMILIES),
        "sourceManifestSha256": manifest_sha, "sourceOverlaySha256": overlay_sha,
        "addedFamilyScenes": len(added_scenes), "addedSelectors": len(registration_rows),
        "addedMuscleSelectors": sum(row["subjectKind"] == "muscle" for row in registration_rows),
        "addedBoneSelectors": sum(row["subjectKind"] == "bone" for row in registration_rows),
        "uniqueAddedBoneSourceKeys": sorted({row["sourceKey"] for row in registration_rows if row["subjectKind"] == "bone"}),
        "uniqueAddedMuscleSourceKeys": sorted({row["sourceKey"] for row in registration_rows if row["subjectKind"] == "muscle"}),
        "uniqueGlbPackages": 4, "registeredRows": registration_rows,
        "counts": {"motionActions": len(bundle["muscleActions"]), "motionDefinitions": len(bundle["motionDefinitions"]),
                   "motionAssets": len(bundle["motionAssets"]), "sceneManifests": len(scenes["sceneManifests"]),
                   "authoringRecords": len(registry["records"])},
        "claims": {"canonicalBindingCreated": False, "measuredAxis": False,
            "measuredAttachmentFootprints": False, "normalPhysiologicalRomApproved": False,
            "muscleActivationOrForceClaimed": False, "sourceOnly": True,
            "publicRedistribution": "held", "humanReview": "not_performed"},
        "quadricepsAttachmentContext": "per-family authoring records contain source-linked UAMS summaries; they do not specify geometry coordinates or footprints",
    }
    (UNIT / "registration.json").write_bytes(encode(out))
    print(json.dumps({k: out[k] for k in ("families", "addedFamilyScenes", "addedSelectors", "addedMuscleSelectors",
        "addedBoneSelectors", "uniqueGlbPackages", "counts")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
