#!/usr/bin/env python3
"""Fail-closed validation for source-linked muscle actions and motion bindings."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "atlas-data/schemas/motion-learning.schema.json"
DATA_PATH = ROOT / "atlas-data/motion/motion-learning.json"
CATALOG_PATH = ROOT / "atlas-data/catalog/canonical-catalog.json"
AI_OVERLAY_PATH = ROOT / "atlas-data/terminology/ai-evidence-overlay.json"
NAVIGATION_PATH = ROOT / "atlas-data/navigation/atlas-navigation.json"
MOTION_SCENES_PATH = ROOT / "atlas-data/motion/motion-scenes.json"
SOURCE_DATASET_PATH = ROOT / "atlas-data/source-cache/datasets/za/compiled/manifest.json"
FIXTURE_INDEX_PATH = ROOT / "work/evidence/T20/fixtures/index.json"

_T03_SPEC = importlib.util.spec_from_file_location("human_atlas_t03_validator", Path(__file__).with_name("validate.py"))
if _T03_SPEC is None or _T03_SPEC.loader is None:
    raise RuntimeError("Could not load the T03 schema validator")
_T03 = importlib.util.module_from_spec(_T03_SPEC)
sys.modules[_T03_SPEC.name] = _T03
_T03_SPEC.loader.exec_module(_T03)


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def value_hash(value: Any) -> str:
    return sha256_bytes(canonical(value).encode("utf-8"))


def load_production_context() -> dict[str, Any]:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    overlay = json.loads(AI_OVERLAY_PATH.read_text(encoding="utf-8"))
    navigation = json.loads(NAVIGATION_PATH.read_text(encoding="utf-8"))
    entities = catalog["entities"]
    subjects = {row["id"] for group in ("muscleConcepts", "muscleParts") for row in entities.get(group, [])}
    structures = {row["id"]: row for row in entities.get("structures", [])}
    instances = {row["id"]: row for row in entities.get("instances", [])}
    source_manifest = json.loads(SOURCE_DATASET_PATH.read_text(encoding="utf-8"))
    source_instances = {row["sourceKey"]: row for row in source_manifest.get("instances", [])}
    claims = {row["id"]: row for row in entities.get("claims", [])}
    evidence = {row["id"]: row for row in entities.get("evidence", [])}
    ai_fields = {row["id"]: row for row in overlay.get("items", [])}
    licenses = {
        source.get("license", {}).get("id")
        for source in entities.get("sources", [])
        if source.get("license", {}).get("id")
    }
    source_licenses = {
        source["id"]: ([source.get("license", {}).get("id")] if source.get("license", {}).get("id") else [])
        for source in entities.get("sources", [])
    }
    authoring_records = {}
    registry_path = ROOT / "atlas-data/motion/authoring/registry.json"
    if registry_path.is_file():
        registry = json.loads(registry_path.read_text())
        for entry in registry.get("records", []):
            record_path = (ROOT / entry["path"]).resolve()
            if not record_path.is_relative_to(ROOT / "atlas-data/motion/authoring") or sha256_bytes(record_path.read_bytes()) != entry["sha256"]:
                raise ValueError("Motion authoring record path/hash mismatch")
            record = json.loads(record_path.read_text())
            if record["id"] != entry["id"] or record.get("schemaVersion") not in {"t59-authoring-record-v1", "t66-authoring-family-record-v1"} or record.get("rights") != {
                    "sourceOnly": True, "localUseRights": "inherits_pinned_source_decision", "publicRedistribution": "held", "humanReview": "not_performed"}:
                raise ValueError("Authoring identity/source-only/rights contract differs")
            if record.get("schemaVersion") == "t66-authoring-family-record-v1":
                dependencies = record.get("verificationDependencies", [])
                if not dependencies or record.get("measuredAnatomicalAxis") is not False:
                    raise ValueError("Source family needs explicit hashed verification and authored-axis distinction")
                for dependency in dependencies:
                    dep = (ROOT / dependency["path"]).resolve()
                    if not dep.is_relative_to(ROOT) or sha256_bytes(dep.read_bytes()) != dependency["sha256"]:
                        raise ValueError("Source family verification dependency drift")
                qc = json.loads((ROOT / record["contactQcPath"]).read_text())
                geometry = json.loads((ROOT / record["geometryRecordPath"]).read_text())
                glb_qc = json.loads((ROOT / record["glbPoseQcPath"]).read_text())
                frame_rows = {r["sourceKey"]: r for r in glb_qc.get("rows", [])}
                deformation_rows = [r for r in frame_rows.values() if r.get("sourceFrameComparison") == "authored_surface_deformation"]
                interpolation_qcs = {}
                interpolation_paths = record.get("glbInterpolationQcPaths", {})
                if interpolation_paths:
                    if not isinstance(interpolation_paths, dict):
                        raise ValueError("Per-surface interpolation QC paths must be a sourceKey map")
                    interpolation_qcs = {source_key: json.loads((ROOT / path).read_text())
                        for source_key, path in interpolation_paths.items()}
                elif deformation_rows and record.get("glbInterpolationQcPath"):
                    # Backward-compatible one-target package used by earlier T66 units.
                    legacy_qc = json.loads((ROOT / record["glbInterpolationQcPath"]).read_text())
                    interpolation_qcs = {legacy_qc.get("targetSourceKey"): legacy_qc}
                exact_frame_rows_pass = all(
                    r.get("sourceFrameComparison", "exact_rigid_source_frame") == "exact_rigid_source_frame"
                    and r.get("passed") is True and r.get("maximumWorldErrorMetres", float("inf")) <= 1e-6
                    for r in frame_rows.values() if r.get("sourceFrameComparison", "exact_rigid_source_frame") == "exact_rigid_source_frame"
                )
                deformation_rows_pass = bool(deformation_rows) and all(
                    (interpolation_qc := interpolation_qcs.get(r.get("sourceKey"))) is not None
                    and r.get("requiresGeometryQc") is True
                    and r.get("passed") is True
                    and r.get("geometryQcPath") in {record.get("glbInterpolationQcPath"), interpolation_paths.get(r.get("sourceKey"))}
                    and r.get("geometryQcSha256") == sha256_bytes((ROOT / r["geometryQcPath"]).read_bytes())
                    and r.get("sourceKey") == interpolation_qc.get("targetSourceKey")
                    and interpolation_qc.get("motionGlbSha256") == record["motionSha256"]
                    and interpolation_qc.get("passed") is True
                    and interpolation_qc.get("geometry", {}).get("passed") is True
                    and interpolation_qc.get("contact", {}).get("passed") is True
                    for r in deformation_rows
                )
                if (glb_qc.get("passed") is not True or glb_qc.get("motionSha256") != record["motionSha256"]
                        or glb_qc.get("testedKeys") != geometry["family"]["samples"] + 1
                        or glb_qc.get("familyId") != record["sourceFamilyId"]
                        or set(frame_rows) != {r["sourceKey"] for r in geometry["members"]}
                        or not exact_frame_rows_pass
                        or any(r.get("sourceFrameComparison") == "authored_surface_deformation" for r in frame_rows.values()) and not deformation_rows_pass):
                    raise ValueError("Emitted GLB must preserve actual source-frame poses/reflections")
                if qc["failures"] or qc["newContainmentMaximum"] or any(m["flips"] or m["minimumAreaRatio"] < .1 for m in geometry["surfaceMetrics"]):
                    raise ValueError("Source family cannot register failed geometry/contact")
                if record.get("sourceFamilyId") != geometry["family"]["id"] or record["side"] not in {"left", "right"}:
                    raise ValueError("Source family identity/side differs")
                motion_hash_matches = record["motionSha256"] == geometry["motionSha256"] or any(
                    qc.get("motionGlbSha256") == record["motionSha256"] and qc.get("targetSourceKey") in frame_rows
                    for qc in interpolation_qcs.values()
                )
                if (not motion_hash_matches or record["restSha256"] != geometry["restSha256"]
                        or any(record["poseRange"][k] != geometry["family"][k] for k in ["axis", "pivotMetres", "endDegrees", "referencePoseId"])
                        or not {record["contactQcPath"], record["geometryRecordPath"], record["glbPoseQcPath"], *interpolation_paths.values()}.issubset({d["path"] for d in dependencies})):
                    raise ValueError("Source family pose/geometry/verification differs")
            authoring_records[entry["id"]] = record
        for entry in registry.get("sources", []):
            for prefix in ("dataset", "rightsEvidence"):
                dep = (ROOT / entry[prefix + "Path"]).resolve()
                if not dep.is_relative_to(ROOT) or sha256_bytes(dep.read_bytes()) != entry[prefix + "Sha256"]:
                    raise ValueError("Motion local source rights/dataset dependency drift")
            if entry["publicRedistribution"] != "held" or entry["humanReview"] != "not_performed" or entry["localUse"] != "inherits_pinned_source_decision":
                raise ValueError("Motion authoring source cannot promote rights/review")
            source_licenses[entry["id"]] = [entry["licenseId"]]
            licenses.add(entry["licenseId"])
    scene_contexts: dict[str, dict[str, Any]] = {}
    for scene in navigation.get("sceneManifests", []):
        refs = scene.get("assetRefs", [])
        if len(refs) != 1:
            continue
        ref = refs[0]
        scene_contexts[scene["id"]] = {
            "sceneId": scene["id"],
            "sceneRevision": scene.get("revision"),
            "modelId": scene.get("modelId"),
            "sourceAssetSha256": ref.get("sha256"),
            "frameId": scene.get("frameId"),
            "units": scene.get("units"),
            "poseId": scene.get("poseId"),
            "assetUri": ref.get("uri"),
        }
    if MOTION_SCENES_PATH.exists():
        motion_scenes = json.loads(MOTION_SCENES_PATH.read_text(encoding="utf-8"))
        for scene in motion_scenes.get("sceneManifests", []):
            if scene["id"] in scene_contexts:
                raise ValueError(f"Duplicate motion scene ID: {scene['id']}")
            uri = scene["assetUri"]
            path = (ROOT / uri).resolve()
            if not uri.startswith("atlas-data/assets/derived-glb/") or not path.is_relative_to(ROOT) or not path.is_file():
                raise ValueError(f"Motion static scene path missing or unsafe: {uri}")
            if sha256_bytes(path.read_bytes()) != scene["sourceAssetSha256"]:
                raise ValueError(f"Motion static scene hash mismatch: {uri}")
            scene_contexts[scene["id"]] = {
                "sceneId": scene["id"], "sceneRevision": scene["revision"],
                "modelId": scene["modelId"], "sourceAssetSha256": scene["sourceAssetSha256"],
                "frameId": scene["frameId"], "units": scene["units"],
                "poseId": scene["poseId"], "assetUri": uri,
            }
    return {
        "subjects": subjects,
        "structures": structures,
        "instances": instances,
        "sourceInstances": source_instances,
        "claims": claims,
        "evidence": evidence,
        "aiFields": ai_fields,
        "licenses": licenses,
        "sourceLicenses": source_licenses,
        "scenes": scene_contexts,
        "legacyJointActions": {row["id"]: row for row in entities.get("jointActions", [])},
        "sourceIds": set(source_licenses),
        "authoringRecords": authoring_records,
        "fixtureAssets": {},
        "fixtureMode": False,
    }


def issue(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def validate_evidence_ref(ref: dict[str, Any], path: str, context: dict[str, Any], issues: list[dict[str, str]]) -> None:
    if ref["layer"] == "source_family_record":
        record = context.get("authoringRecords", {}).get(ref["evidenceId"])
        claim = next((c for c in record.get("claims", []) if c["id"] == ref["claimId"]), None) if record else None
        if (not record or record.get("schemaVersion") != "t66-authoring-family-record-v1" or not claim
                or ref["fieldEvidenceId"] is not None or claim["field"] != ref["field"]
                or claim["appliesTo"] != ref["appliesTo"] or claim["contextId"] != ref["contextId"]
                or value_hash(claim["value"]) != ref["valueHash"]):
            issues.append(issue("invalid_source_family_reference", path, "Exact adopted source-family field/context/hash required; no canonical claim approval inferred."))
        return
    if ref["layer"] == "authoring_record":
        record = context.get("authoringRecords", {}).get(ref["evidenceId"])
        if (ref["appliesTo"] != "motion_pose_range" or ref["field"] != "motion_pose_range"
                or ref["contextId"] is not None or ref["fieldEvidenceId"] is not None or not record
                or record.get("id") != ref["claimId"] or value_hash(record.get("poseRange")) != ref["valueHash"]):
            issues.append(issue("invalid_authoring_pose_reference", path, "Authored pose must resolve to its exact hashed authoring record; cannot stand in for anatomical action/attachment evidence."))
        return
    if ref["layer"] == "canonical_claim":
        if ref["fieldEvidenceId"] is not None:
            issues.append(issue("canonical_ref_has_ai_field", f"{path}.fieldEvidenceId", "Canonical claim references do not carry an AI field ID."))
        claim = context["claims"].get(ref["claimId"])
        evidence = context["evidence"].get(ref["evidenceId"])
        if claim is None:
            issues.append(issue("orphan_claim_reference", f"{path}.claimId", f"Unknown canonical claim {ref['claimId']!r}."))
        else:
            if claim.get("field") != ref["field"]:
                issues.append(issue("canonical_claim_field_mismatch", f"{path}.field", "Claim field name differs from the recorded source field."))
            if value_hash(claim.get("value")) != ref["valueHash"]:
                issues.append(issue("claim_value_hash_mismatch", f"{path}.valueHash", "Claim value hash does not match the current canonical claim."))
            if ref["evidenceId"] not in claim.get("evidenceIds", []):
                issues.append(issue("claim_evidence_binding_mismatch", f"{path}.evidenceId", "Canonical claim does not link this evidence ID."))
        if evidence is None:
            issues.append(issue("orphan_evidence_reference", f"{path}.evidenceId", f"Unknown canonical evidence {ref['evidenceId']!r}."))
    else:
        field_id = ref["fieldEvidenceId"]
        field = context["aiFields"].get(field_id) if field_id else None
        if field is None:
            issues.append(issue("orphan_ai_field_reference", f"{path}.fieldEvidenceId", f"Unknown AI field evidence {field_id!r}."))
            return
        if field.get("field") != ref["field"]:
            issues.append(issue("ai_field_name_mismatch", f"{path}.field", "AI field name differs from the recorded source field."))
        claim = next((row for row in field.get("claims", []) if row.get("id") == ref["claimId"]), None)
        if claim is None:
            issues.append(issue("orphan_ai_claim_reference", f"{path}.claimId", f"Field {field_id!r} does not contain claim {ref['claimId']!r}."))
        else:
            if claim.get("valueHash") != ref["valueHash"]:
                issues.append(issue("ai_claim_value_hash_mismatch", f"{path}.valueHash", "AI field claim hash differs from the referenced overlay claim."))
            if ref["evidenceId"] not in claim.get("evidenceIds", []):
                issues.append(issue("ai_claim_evidence_binding_mismatch", f"{path}.evidenceId", "AI field claim does not link this evidence ID."))
        if not any(row.get("id") == ref["evidenceId"] for row in field.get("evidence", [])):
            issues.append(issue("orphan_ai_evidence_reference", f"{path}.evidenceId", f"Field {field_id!r} does not contain evidence {ref['evidenceId']!r}."))


def static_reference_mismatches(reference: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    return [key for key in ("sceneId", "sceneRevision", "modelId", "sourceAssetSha256", "frameId", "units", "poseId") if reference.get(key) != expected.get(key)]


def asset_path(uri: str, context: dict[str, Any]) -> Path | None:
    if uri.startswith("fixture://"):
        if not context["fixtureMode"]:
            return None
        relative = context["fixtureAssets"].get(uri)
        return ROOT / relative if relative else None
    if uri.startswith("/") or "://" in uri:
        return None
    parts = Path(uri).parts
    if ".." in parts or not uri.startswith("atlas-data/assets/motion/"):
        return None
    path = (ROOT / uri).resolve()
    try:
        path.relative_to((ROOT / "atlas-data/assets/motion").resolve())
    except ValueError:
        return None
    return path


def validate_bundle(payload: Any, schema: dict[str, Any], context: dict[str, Any], *, allow_fixture: bool = False) -> list[dict[str, str]]:
    issues = [issue(row["code"], row["path"], row["message"]) for row in _T03.schema_issues(schema, payload)]
    if issues:
        return issues
    if context["fixtureMode"] and not allow_fixture:
        return [issue("fixture_context_in_production", "$", "Synthetic contexts may only be used by --fixtures.")]

    actions: dict[str, dict[str, Any]] = {}
    definitions: dict[str, dict[str, Any]] = {}
    assets: dict[str, dict[str, Any]] = {}
    for collection, target, path_name in (
        ("muscleActions", actions, "muscleActions"),
        ("motionDefinitions", definitions, "motionDefinitions"),
        ("motionAssets", assets, "motionAssets"),
    ):
        for index, row in enumerate(payload[collection]):
            path = f"$.{path_name}[{index}]"
            if row["id"] in target:
                issues.append(issue("duplicate_entity_id", f"{path}.id", f"Duplicate ID {row['id']!r}."))
            target[row["id"]] = row

    for index, action in enumerate(payload["muscleActions"]):
        path = f"$.muscleActions[{index}]"
        source_subjects = action.get("sourceSubjectKeys", [])
        if not action["subjectIds"] and not source_subjects:
            issues.append(issue("action_subject_missing", path, "An action must bind at least one canonical concept or exact source instance."))
        for subject_id in action["subjectIds"]:
            if subject_id not in context["subjects"]:
                issues.append(issue("orphan_action_subject", f"{path}.subjectIds", f"Unknown muscle/part ID {subject_id!r}."))
        for source_key in source_subjects:
            source_instance = context.get("sourceInstances", {}).get(source_key)
            if source_instance is None or source_instance.get("kind") not in ({"skeletal_surface"} if action.get("subjectKind") == "bone" else {"muscle_surface_or_part", "muscle"}):
                issues.append(issue("orphan_source_action_subject", f"{path}.sourceSubjectKeys", f"Unknown exact muscle sourceKey {source_key!r}."))
        joint_state = action["jointBindingState"]
        joint_note = action["jointBindingNote"]
        if joint_state == "canonical_bound" and (not action["targetJointIds"] or joint_note is not None):
            issues.append(issue("bound_joint_ids_missing", f"{path}.targetJointIds", "Canonical-bound actions need joint IDs and no unmapped note."))
        if joint_state == "unmapped" and (action["targetJointIds"] or not isinstance(joint_note, str) or not joint_note.strip()):
            issues.append(issue("unmapped_joint_binding_incomplete", f"{path}.jointBindingNote", "Unmapped actions need an explicit reason and must not invent joint IDs."))
        source_family = action.get("sourceFamilyId")
        family_record = next((r for r in context.get("authoringRecords", {}).values() if r.get("sourceFamilyId") == source_family), None) if source_family else None
        if joint_state == "source_family_bound":
            if (not family_record or action["targetJointIds"] or not source_subjects or action["subjectIds"]
                    or not isinstance(joint_note, str) or not joint_note.strip()
                    or action["sideApplicability"] != family_record["side"]
                    or not set(source_subjects).issubset(set(family_record["supportedSubjectKeys"]))):
                issues.append(issue("source_family_action_binding_invalid", path, "Verified exact source family/subjects/side required, with no canonical joint/concept promotion."))
            if family_record and any(ref["evidenceId"] != family_record["id"] or ref["layer"] != "source_family_record" for ref in action["sourceRefs"]):
                issues.append(issue("source_family_action_evidence_mismatch", path, "Source action fields must bind the adopted family record."))
        elif source_family:
            issues.append(issue("unexpected_source_family_binding", path, "Source family IDs require the explicit source_family_bound state."))
        for joint_id in action["targetJointIds"]:
            structure = context["structures"].get(joint_id)
            if structure is None or structure.get("kind") != "joint":
                issues.append(issue("invalid_action_joint_binding", f"{path}.targetJointIds", f"Target {joint_id!r} does not resolve to a canonical joint structure."))
        for condition_index, condition in enumerate(action["stabilizationConditions"]):
            for structure_id in condition["structureIds"]:
                if structure_id not in context["structures"]:
                    issues.append(issue("orphan_stabilization_structure", f"{path}.stabilizationConditions[{condition_index}].structureIds", f"Unknown canonical structure {structure_id!r}."))
        if not action["stabilizationConditions"] and (not isinstance(action["stabilizationNote"], str) or not action["stabilizationNote"].strip()):
            issues.append(issue("stabilization_absence_unexplained", f"{path}.stabilizationNote", "If no stabilization condition is recorded, explain the gap instead of implying none exists."))
        context_ids = [row["contextId"] for row in action["contextRoles"]]
        if len(set(context_ids)) != len(context_ids):
            issues.append(issue("duplicate_action_context_role", f"{path}.contextRoles", "Role assignments must be unique per action/context pair."))
        scopes: set[str] = set()
        context_ids = {row["contextId"] for row in action["contextRoles"]}
        for ref_index, ref in enumerate(action["sourceRefs"]):
            scopes.add(ref["appliesTo"])
            if ref["appliesTo"] == "context_role" and ref["contextId"] not in context_ids:
                issues.append(issue("role_source_context_mismatch", f"{path}.sourceRefs[{ref_index}].contextId", "Role evidence must bind to one declared action/context role."))
            if ref["appliesTo"] != "context_role" and ref["contextId"] is not None:
                issues.append(issue("unexpected_source_context", f"{path}.sourceRefs[{ref_index}].contextId", "Only a context-role source link may carry a context ID."))
            validate_evidence_ref(ref, f"{path}.sourceRefs[{ref_index}]", context, issues)
        if action.get("subjectKind", "muscle") == "muscle" and (not action["postureConditions"] or not action["contextRoles"]):
            issues.append(issue("muscle_context_required", path, "Muscle actions retain the posture and contraction/context contract; bone co-movement cannot weaken it."))
        required_scopes = {"action_explanation", "context_role"}
        if action.get("subjectKind") == "bone" and not context_ids:
            required_scopes.remove("context_role")
        if action["postureConditions"]:
            required_scopes.add("posture_condition")
        if action["stabilizationConditions"]:
            required_scopes.add("stabilization_condition")
        missing_scopes = required_scopes - scopes
        if missing_scopes:
            issues.append(issue("action_source_scope_missing", f"{path}.sourceRefs", f"Missing source links for action fields: {', '.join(sorted(missing_scopes))}."))
        missing_role_contexts = context_ids - {ref["contextId"] for ref in action["sourceRefs"] if ref["appliesTo"] == "context_role"}
        if missing_role_contexts:
            issues.append(issue("context_role_source_missing", f"{path}.sourceRefs", f"Missing source links for action contexts: {', '.join(sorted(missing_role_contexts))}."))
        legacy_id = action.get("legacyJointActionId")
        if legacy_id and legacy_id not in context["legacyJointActions"]:
            issues.append(issue("orphan_legacy_joint_action", f"{path}.legacyJointActionId", f"No original JointAction {legacy_id!r} exists."))

    for index, definition in enumerate(payload["motionDefinitions"]):
        path = f"$.motionDefinitions[{index}]"
        action = actions.get(definition["actionId"])
        if action is None:
            issues.append(issue("orphan_motion_action", f"{path}.actionId", f"Unknown MuscleAction {definition['actionId']!r}."))
        elif action["jointBindingState"] == "source_family_bound":
            family = next((r for r in context.get("authoringRecords", {}).values() if r.get("sourceFamilyId") == definition.get("sourceFamilyId")), None)
            if (not family or definition.get("sourceFamilyId") != action.get("sourceFamilyId")
                    or definition["targetJointIds"] or definition["side"] != family["side"]
                    or definition["endPoseId"] != family["poseRange"]["endPoseId"]
                    or definition["staticReference"]["poseId"] != family["poseRange"]["referencePoseId"]
                    or set(definition["movingStructureIds"]) != set(family["movingBoneKeys"])
                    or set(definition["fixedStructureIds"]) != set(family["fixedBoneKeys"])):
                issues.append(issue("motion_source_family_mismatch", path, "Definition must match adopted family side/pose/moving/fixed source structures."))
        elif action["jointBindingState"] != "canonical_bound":
            issues.append(issue("motion_action_joint_unmapped", f"{path}.actionId", "A motion definition requires canonical joint bindings; text-only unmapped actions cannot define a clip."))
        elif not set(definition["targetJointIds"]).issubset(set(action["targetJointIds"])):
            issues.append(issue("motion_action_joint_mismatch", f"{path}.targetJointIds", "Motion definition joints must be declared by its MuscleAction."))
        if action and action["jointBindingState"] == "canonical_bound" and (not definition["targetJointIds"] or definition.get("sourceFamilyId")):
            issues.append(issue("motion_canonical_joint_required", path, "Canonical motions retain nonempty canonical joint bindings and cannot use authored family IDs."))
        if action and action["sideApplicability"] in {"right", "left"} and definition["side"] != action["sideApplicability"]:
            issues.append(issue("motion_action_side_mismatch", f"{path}.side", "Motion laterality conflicts with the MuscleAction side applicability."))
        instance = context["instances"].get(definition["instanceId"])
        source_instance = context.get("sourceInstances", {}).get(definition["instanceId"])
        if instance is None and source_instance is None:
            issues.append(issue("orphan_motion_instance", f"{path}.instanceId", f"Unknown anatomical instance {definition['instanceId']!r}."))
        elif instance is not None:
            if action and instance.get("conceptId") not in action["subjectIds"]:
                issues.append(issue("motion_instance_subject_mismatch", f"{path}.instanceId", "Instance concept is not a subject of the bound MuscleAction."))
            if definition["side"] != instance.get("side"):
                issues.append(issue("motion_instance_side_mismatch", f"{path}.side", "Motion side must match the canonical instance laterality."))
        else:
            if not action or definition["instanceId"] not in action.get("sourceSubjectKeys", []):
                issues.append(issue("motion_source_subject_mismatch", f"{path}.instanceId", "Exact source instance is not a sourceSubjectKey of the bound action."))
            if definition["side"] != source_instance.get("sourceLabelSide"):
                issues.append(issue("motion_source_side_mismatch", f"{path}.side", "Motion side must match the source's explicit side label."))
        if definition["startPoseId"] != definition["staticReference"]["poseId"]:
            issues.append(issue("motion_start_pose_mismatch", f"{path}.startPoseId", "Motion must start from the exact static reference pose."))
        if definition["endPoseId"] == definition["startPoseId"]:
            issues.append(issue("motion_pose_range_empty", f"{path}.endPoseId", "Start and end pose IDs must differ."))
        if set(definition["movingStructureIds"]) & set(definition["fixedStructureIds"]):
            issues.append(issue("moving_fixed_structure_overlap", path, "A structure cannot be both moving and fixed in one motion definition."))
        for structure_id in definition["movingStructureIds"]:
            structure = context["structures"].get(structure_id)
            source_structure = context.get("sourceInstances", {}).get(structure_id)
            if (structure is None or structure.get("kind") != "bone") and not (source_structure and source_structure.get("kind") == "skeletal_surface" and source_structure.get("sourceLabelSide") == definition["side"]):
                issues.append(issue("invalid_moving_structure", f"{path}.movingStructureIds", f"Moving structure {structure_id!r} must resolve to a canonical bone."))
        for structure_id in definition["fixedStructureIds"]:
            source_fixed = context.get("sourceInstances", {}).get(structure_id, {})
            adopted = next((r for r in context.get("authoringRecords", {}).values() if r.get("sourceFamilyId") == definition.get("sourceFamilyId") and r.get("sourceFamilyId")), None)
            nullable_axial_context = bool(adopted and structure_id in adopted["fixedBoneKeys"] and source_fixed.get("sourceLabelSide") is None)
            if structure_id not in context["structures"] and not (source_fixed.get("kind") == "skeletal_surface" and (source_fixed.get("sourceLabelSide") == definition["side"] or nullable_axial_context)):
                issues.append(issue("orphan_fixed_structure", f"{path}.fixedStructureIds", f"Unknown canonical fixed structure {structure_id!r}."))
        for joint_id in definition["targetJointIds"]:
            structure = context["structures"].get(joint_id)
            if structure is None or structure.get("kind") != "joint":
                issues.append(issue("invalid_motion_joint_binding", f"{path}.targetJointIds", f"Target {joint_id!r} does not resolve to a canonical joint structure."))
        scene = context["scenes"].get(definition["staticReference"]["sceneId"])
        if scene is None:
            issues.append(issue("unknown_static_scene", f"{path}.staticReference.sceneId", "Static reference must resolve to a retained scene manifest."))
        else:
            mismatches = static_reference_mismatches(definition["staticReference"], scene)
            if mismatches:
                issues.append(issue("static_scene_binding_mismatch", f"{path}.staticReference", f"Static context differs from its scene manifest fields: {', '.join(mismatches)}."))
        for ref_index, ref in enumerate(definition["poseSourceRefs"]):
            if ref["appliesTo"] != "motion_pose_range":
                issues.append(issue("pose_source_scope_mismatch", f"{path}.poseSourceRefs[{ref_index}].appliesTo", "Motion pose evidence must be scoped to the pose range."))
            if ref["contextId"] is not None:
                issues.append(issue("unexpected_pose_source_context", f"{path}.poseSourceRefs[{ref_index}].contextId", "Motion pose evidence is definition-scoped, not action-context-scoped."))
            validate_evidence_ref(ref, f"{path}.poseSourceRefs[{ref_index}]", context, issues)

    for index, asset in enumerate(payload["motionAssets"]):
        path = f"$.motionAssets[{index}]"
        if asset["clip"]["durationSeconds"] <= 0:
            issues.append(issue("invalid_motion_duration", f"{path}.clip.durationSeconds", "Clip duration must be greater than zero."))
        definition = definitions.get(asset["motionDefinitionId"])
        if definition is None:
            issues.append(issue("orphan_motion_definition", f"{path}.motionDefinitionId", f"Unknown motion definition {asset['motionDefinitionId']!r}."))
            continue
        asset_issue_start = len(issues)
        reference = definition["staticReference"]
        binding = asset["staticBinding"]
        expected_binding = {
            "sceneId": reference["sceneId"], "sceneRevision": reference["sceneRevision"], "modelId": reference["modelId"],
            "sourceAssetSha256": reference["sourceAssetSha256"], "frameId": reference["frameId"],
            "units": reference["units"], "side": definition["side"], "referencePoseId": reference["poseId"],
        }
        binding_mismatches = [key for key, expected in expected_binding.items() if binding.get(key) != expected]
        pose_mismatch = binding.get("referencePoseId") != definition["startPoseId"] or asset["clip"]["startPoseId"] != definition["startPoseId"] or asset["clip"]["endPoseId"] != definition["endPoseId"]
        if pose_mismatch:
            issues.append(issue("asset_static_pose_mismatch", f"{path}.clip", "Asset start/end poses must exactly match the definition and its static reference pose."))
        if binding_mismatches:
            issues.append(issue("asset_frame_side_revision_mismatch", f"{path}.staticBinding", f"Asset binding differs from its motion definition: {', '.join(binding_mismatches)}."))
        if asset["licenseId"] not in context["licenses"]:
            issues.append(issue("unregistered_motion_license", f"{path}.licenseId", f"License {asset['licenseId']!r} is not registered in source/catalog data."))
        if asset["sourceId"] not in context["sourceIds"]:
            issues.append(issue("unregistered_motion_source", f"{path}.sourceId", f"Source {asset['sourceId']!r} is not registered in the canonical source catalog."))
        elif asset["licenseId"] not in context["sourceLicenses"].get(asset["sourceId"], []):
            issues.append(issue("motion_source_license_mismatch", f"{path}.licenseId", "Motion asset license must match the registered license of its source."))

        resolved = asset_path(asset["uri"], context)
        if resolved is None:
            issues.append(issue("unsafe_or_unregistered_motion_asset", f"{path}.uri", "Asset URI must be a registered fixture URI or a project-local atlas-data/assets/motion path."))
        elif not resolved.is_file():
            issues.append(issue("motion_asset_file_missing", f"{path}.uri", f"Motion asset file does not exist: {asset['uri']!r}."))
        elif sha256_bytes(resolved.read_bytes()) != asset["sha256"]:
            issues.append(issue("motion_asset_hash_mismatch", f"{path}.sha256", "Motion asset file content does not match its recorded SHA-256."))

        if asset["representationType"] == "source_bound_surface":
            source_binding = asset.get("sourceBinding")
            if not isinstance(source_binding, dict):
                issues.append(issue("missing_source_motion_binding", f"{path}.sourceBinding", "A source-bound surface clip needs an exact runtime scene/source binding."))
                source_binding = {}
            if source_binding.get("contractVersion") not in ["t59-source-motion-binding-v1", "t66-typed-source-motion-v2"]:
                issues.append(issue("invalid_source_motion_contract", f"{path}.sourceBinding.contractVersion", "Source motion binding must use the T59 contract."))
            source_members = source_binding.get("members", [])
            family_id = definition.get("sourceFamilyId")
            if family_id:
                family = next((r for r in context.get("authoringRecords", {}).values() if r.get("sourceFamilyId") == family_id), None)
                if (not family or source_binding.get("sourceFamilyId") != family_id
                        or asset["sha256"] != family["motionSha256"]
                        or asset["staticBinding"]["sourceAssetSha256"] != family["restSha256"]
                        or asset.get("poseControl", {}).get("endDegrees") != family["poseRange"]["endDegrees"]
                        or asset.get("poseControl", {}).get("actionDirection", "forward") != family["poseRange"].get("actionDirection", "forward")):
                    issues.append(issue("source_family_asset_mismatch", path, "Exact adopted family/motion/rest bytes and authored angle required."))
            elif source_binding.get("sourceFamilyId"):
                issues.append(issue("unexpected_asset_source_family", path, "An asset cannot add a family missing from its definition."))
            source_keys = [row.get("sourceKey") for row in source_members if isinstance(row, dict)]
            node_ids = [row.get("nodeId") for row in source_members if isinstance(row, dict)]
            if not source_members or len(source_keys) != len(source_members) or len(set(source_keys)) != len(source_keys) or len(set(node_ids)) != len(node_ids):
                issues.append(issue("invalid_source_motion_members", f"{path}.sourceBinding.members", "Source instance and GLB node bindings must be present and unique."))
            required_hashes = ("sourceOverlaySha256",)
            for field in required_hashes:
                if not isinstance(source_binding.get(field), str) or len(source_binding[field]) != 64:
                    issues.append(issue("invalid_source_motion_hash", f"{path}.sourceBinding.{field}", "Source runtime binding hashes must be SHA-256."))
            if source_binding.get("frameId") != binding.get("frameId") or source_binding.get("units") != binding.get("units"):
                issues.append(issue("source_motion_frame_mismatch", f"{path}.sourceBinding", "Source motion and static binding frame/unit must match exactly."))
            if source_binding.get("referencePoseId") != binding.get("referencePoseId"):
                issues.append(issue("source_motion_pose_mismatch", f"{path}.sourceBinding.referencePoseId", "Source motion must bind the exact static reference pose."))
            subject_kind = source_binding.get("subjectKind", "muscle")
            subject_roles = {"moving_structure", "fixed_structure"} if subject_kind == "bone" else {"deforming_muscle_surface", "deforming_passive_surface"}
            subject_members = [row for row in source_members if isinstance(row, dict)
                and row.get("role") in subject_roles]
            source_subject = context.get("sourceInstances", {}).get(definition["instanceId"], {})
            if subject_kind == "bone" and (source_binding.get("contractVersion") != "t66-typed-source-motion-v2" or source_subject.get("kind") != "skeletal_surface"):
                issues.append(issue("source_motion_subject_kind", path, "Bone motion requires a typed actual skeletal instance."))
            subject_role_in_pose = None
            if subject_kind == "bone":
                if definition["instanceId"] in definition.get("movingStructureIds", []):
                    subject_role_in_pose = "moving_structure"
                elif definition["instanceId"] in definition.get("fixedStructureIds", []):
                    subject_role_in_pose = "fixed_structure"
            else:
                exact_subject_roles = [row.get("role") for row in source_members if isinstance(row, dict)
                    and row.get("sourceKey") == definition["instanceId"]
                    and row.get("side") == definition["side"]
                    and row.get("role") in subject_roles]
                subject_role_in_pose = exact_subject_roles[0] if len(exact_subject_roles) == 1 else None
            if (source_binding.get("subjectSourceKey") != definition["instanceId"] or not any(
                    row.get("sourceKey") == definition["instanceId"]
                    and row.get("side") == definition["side"]
                    and row.get("role") == subject_role_in_pose for row in subject_members)):
                issues.append(issue("source_motion_subject_side_mismatch", f"{path}.sourceBinding.members",
                    "The exact source instance, side, and moving/fixed/deforming role must match the authored pose."))
            for member_index, member in enumerate(source_members):
                if not isinstance(member, dict):
                    continue
                corrective_bound = member.get("passiveCorrectiveMaxMetres")
                if corrective_bound is not None and (member.get("role") != "co_moving_context"
                        or not isinstance(corrective_bound, (int, float)) or not 0 < corrective_bound <= .001):
                    issues.append(issue("invalid_passive_contact_corrective", f"{path}.sourceBinding.members[{member_index}]", "Only bounded passive co-moving surface correctives are allowed."))
                source_instance = context.get("sourceInstances", {}).get(member.get("sourceKey"))
                if source_instance:
                    source_lod = source_instance.get("lods", {}).get(member.get("lod"), {})
                    if member.get("resourceKey") != source_lod.get("resource") or member.get("sourceChunkSha256") != source_lod.get("chunk") or member.get("instanceMatrix") != source_instance.get("matrix") or member.get("side") != source_instance.get("sourceLabelSide"):
                        issues.append(issue("source_motion_member_drift", f"{path}.sourceBinding.members[{member_index}]", "Source member resource/LOD/chunk/side/matrix differs from immutable source."))
                else:
                    issues.append(issue("unknown_source_motion_member", f"{path}.sourceBinding.members[{member_index}]", "Source member must resolve in the actual dataset."))
                for field in ("sourceChunkSha256", "geometrySha256"):
                    value = member.get(field)
                    if not isinstance(value, str) or len(value) != 64:
                        issues.append(issue("invalid_source_motion_member_hash", f"{path}.sourceBinding.members[{member_index}].{field}", "Each source instance needs an exact chunk and base-geometry SHA-256."))
                if not isinstance(member.get("instanceMatrix"), list) or len(member["instanceMatrix"]) != 16 or not all(isinstance(value, (int, float)) for value in member["instanceMatrix"]):
                    issues.append(issue("invalid_source_motion_instance_matrix", f"{path}.sourceBinding.members[{member_index}].instanceMatrix", "The source instance transform must be copied exactly from the frozen dataset manifest."))
            rig_bindings = asset["rig"]["nodeBindings"] if asset["rig"] is not None else []
            rig_structure_ids = [row["structureId"] for row in rig_bindings]
            rig_node_ids = [row["nodeId"] for row in rig_bindings]
            if asset["rig"] is not None and (len(set(rig_structure_ids)) != len(rig_structure_ids) or len(set(rig_node_ids)) != len(rig_node_ids)):
                issues.append(issue("duplicate_source_motion_rig_binding", f"{path}.rig.nodeBindings", "Source motion rig bindings must be unique."))
            if source_binding.get("deformation") in ("skinning", "morph_and_skinning") and not rig_bindings:
                issues.append(issue("missing_source_motion_rig", f"{path}.rig", "Skinned source motion requires a rig binding."))
            if asset["illustration"] is not None:
                issues.append(issue("source_motion_illustration_not_allowed", f"{path}.illustration", "Source-bound surface motion cannot use an illustrative path as a deformation substitute."))
        elif asset["representationType"] == "rigged_mesh":
            if asset["rig"] is None:
                issues.append(issue("missing_rig_binding", f"{path}.rig", "A rigged mesh requires a rig/node binding."))
            if asset["illustration"] is not None:
                issues.append(issue("conflicting_representation_binding", f"{path}.illustration", "A rigged mesh cannot also carry path-illustration bindings."))
            node_bindings = asset["rig"]["nodeBindings"] if asset["rig"] is not None else []
            structure_ids = [row["structureId"] for row in node_bindings]
            node_ids = [row["nodeId"] for row in node_bindings]
            if len(set(structure_ids)) != len(structure_ids) or len(set(node_ids)) != len(node_ids):
                issues.append(issue("duplicate_rig_binding", f"{path}.rig.nodeBindings", "Rig node bindings must be unique by structure and node."))
            if set(structure_ids) != set(definition["movingStructureIds"]):
                issues.append(issue("rig_moving_structure_binding_mismatch", f"{path}.rig.nodeBindings", "A rigged asset must bind exactly the moving structures declared by its definition."))
        elif asset["representationType"] == "illustrative_path":
            if asset["rig"] is not None:
                issues.append(issue("conflicting_representation_binding", f"{path}.rig", "An illustrative path cannot declare a rigged mesh binding."))
            illustration = asset["illustration"]
            if illustration is None:
                issues.append(issue("missing_trajectory_binding", f"{path}.illustration", "An illustrative path requires trajectory bindings."))
            else:
                trajectory_bindings = illustration["trajectoryBindings"]
                structure_ids = [row["structureId"] for row in trajectory_bindings]
                trajectory_ids = [row["trajectoryId"] for row in trajectory_bindings]
                if len(set(structure_ids)) != len(structure_ids) or len(set(trajectory_ids)) != len(trajectory_ids):
                    issues.append(issue("duplicate_trajectory_binding", f"{path}.illustration.trajectoryBindings", "Trajectory bindings must be unique by structure and trajectory."))
                if set(structure_ids) != set(definition["movingStructureIds"]):
                    issues.append(issue("illustration_moving_structure_binding_mismatch", f"{path}.illustration.trajectoryBindings", "An illustrative path must bind exactly the moving structures declared by its definition."))
        else:
            rig_bindings = asset["rig"]["nodeBindings"] if asset["rig"] is not None else []
            trajectory_bindings = asset["illustration"]["trajectoryBindings"] if asset["illustration"] is not None else []
            rig_structure_ids = [row["structureId"] for row in rig_bindings]
            rig_node_ids = [row["nodeId"] for row in rig_bindings]
            path_structure_ids = [row["structureId"] for row in trajectory_bindings]
            trajectory_ids = [row["trajectoryId"] for row in trajectory_bindings]
            if not rig_bindings:
                issues.append(issue("missing_bone_node_binding", f"{path}.rig.nodeBindings", "Bone motion with an illustrative path requires animated structure-to-node bindings."))
            if not trajectory_bindings:
                issues.append(issue("missing_muscle_trajectory_binding", f"{path}.illustration.trajectoryBindings", "Bone motion with an illustrative path requires separate path bindings."))
            if len(set(rig_structure_ids)) != len(rig_structure_ids) or len(set(rig_node_ids)) != len(rig_node_ids):
                issues.append(issue("duplicate_rig_binding", f"{path}.rig.nodeBindings", "Rig node bindings must be unique by structure and node."))
            if len(set(path_structure_ids)) != len(path_structure_ids) or len(set(trajectory_ids)) != len(trajectory_ids):
                issues.append(issue("duplicate_trajectory_binding", f"{path}.illustration.trajectoryBindings", "Trajectory bindings must be unique by structure and trajectory."))
            if set(rig_structure_ids) != set(definition["movingStructureIds"]):
                issues.append(issue("combined_bone_binding_mismatch", f"{path}.rig.nodeBindings", "Bone-node bindings must cover exactly the definition's moving bones."))
            bound_action = actions.get(definition["actionId"])
            expected_path_subjects = set(bound_action["subjectIds"]) if bound_action else set()
            if set(path_structure_ids) != expected_path_subjects:
                issues.append(issue("combined_path_subject_binding_mismatch", f"{path}.illustration.trajectoryBindings", "Illustrative paths must bind the action's muscle/part subjects separately from moving bones."))
        if asset["technicalStatus"] == "binding_verified" and len(issues) > asset_issue_start:
            issues.append(issue("false_binding_verified_status", f"{path}.technicalStatus", "Technical binding status cannot be verified while required asset, pose, frame, side, or revision checks fail."))

    return issues


def load_schema() -> dict[str, Any]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    problems = _T03.check_schema(schema)
    if problems:
        raise ValueError(json.dumps([dict(row) for row in problems], ensure_ascii=False, indent=2))
    return schema


def run_fixtures(schema: dict[str, Any]) -> dict[str, Any]:
    index = json.loads(FIXTURE_INDEX_PATH.read_text(encoding="utf-8"))
    context = json.loads((ROOT / index["context"]).read_text(encoding="utf-8"))
    context["fixtureMode"] = True
    context.setdefault("fixtureAssets", {})
    results = []
    for case in index["cases"]:
        bundle = json.loads((ROOT / case["bundle"]).read_text(encoding="utf-8"))
        issues = validate_bundle(bundle, schema, context, allow_fixture=True)
        codes = sorted({row["code"] for row in issues})
        expected = sorted(case.get("expectedIssueCodes", []))
        passed = (not issues) if case["expectPass"] else all(code in codes for code in expected)
        results.append({"id": case["id"], "expectPass": case["expectPass"], "passed": passed, "issueCodes": codes, "issues": issues})
    source_key = "ZA-T59-FIXTURE-SOURCE-R"
    source_context = json.loads((ROOT / index["context"]).read_text(encoding="utf-8"))
    source_context["fixtureMode"] = True
    source_context.setdefault("fixtureAssets", {})
    source_context["sourceInstances"] = {source_key: {"sourceKey": source_key, "kind": "muscle_surface_or_part", "sourceLabelSide": "right"}}
    source_bundle = json.loads((ROOT / "work/evidence/T20/fixtures/positive-valid-motion.json").read_text(encoding="utf-8"))
    source_bundle["muscleActions"][0]["subjectIds"] = []
    source_bundle["muscleActions"][0]["sourceSubjectKeys"] = [source_key]
    source_bundle["muscleActions"][0]["learnerActionKey"] = "fixture-source-action"
    source_bundle["motionDefinitions"][0]["instanceId"] = source_key
    source_bundle["motionAssets"][0]["representationType"] = "source_bound_surface"
    source_bundle["motionAssets"][0]["illustration"] = None
    source_bundle["motionAssets"][0]["sourceBinding"] = {
        "contractVersion": "t59-source-motion-binding-v1", "datasetNamespace": "fixture-dataset", "datasetRevision": "fixture-r1",
        "integrationRevision": "fixture-integration-r1", "sourceOverlaySha256": "a" * 64, "subjectSourceKey": source_key,
        "frameId": source_bundle["motionDefinitions"][0]["staticReference"]["frameId"], "units": "m",
        "referencePoseId": source_bundle["motionDefinitions"][0]["startPoseId"], "deformation": "morph_targets",
        "members": [{"sourceKey": source_key, "nodeId": "FixtureMuscleSurface", "sourceNamespace": "za-fixture", "role": "deforming_muscle_surface",
                     "side": "right", "resourceKey": "fixture-resource", "lod": "overview", "sourceChunkSha256": "b" * 64,
                     "geometrySha256": "c" * 64, "instanceMatrix": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]}],
    }
    source_context['sourceInstances'][source_key].update({
        'lods': {'overview': {'resource': 'fixture-resource', 'chunk': 'b' * 64}},
        'matrix': [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    })
    source_issues = validate_bundle(source_bundle, schema, source_context, allow_fixture=True)
    results.append({"id": "source-only-action-by-exact-sourceKey", "expectPass": True, "passed": not source_issues,
                    "issueCodes": sorted({row["code"] for row in source_issues}), "issues": source_issues})
    wrong_side_bundle = json.loads(json.dumps(source_bundle))
    wrong_side_bundle["motionDefinitions"][0]["side"] = "left"
    wrong_side_bundle["motionAssets"][0]["staticBinding"]["side"] = "left"
    wrong_side_bundle["motionAssets"][0]["sourceBinding"]["members"][0]["side"] = "left"
    wrong_side_issues = validate_bundle(wrong_side_bundle, schema, source_context, allow_fixture=True)
    wrong_side_codes = sorted({row["code"] for row in wrong_side_issues})
    results.append({"id": "source-only-action-rejects-declared-side-mismatch", "expectPass": False,
                    "passed": "motion_action_side_mismatch" in wrong_side_codes, "issueCodes": wrong_side_codes, "issues": wrong_side_issues})
    unknown_source_bundle = json.loads(json.dumps(source_bundle))
    unknown_source_bundle["muscleActions"][0]["sourceSubjectKeys"] = ["ZA-T59-UNKNOWN"]
    unknown_source_bundle["motionDefinitions"][0]["instanceId"] = "ZA-T59-UNKNOWN"
    unknown_source_bundle["motionAssets"][0]["sourceBinding"]["subjectSourceKey"] = "ZA-T59-UNKNOWN"
    unknown_source_bundle["motionAssets"][0]["sourceBinding"]["members"][0]["sourceKey"] = "ZA-T59-UNKNOWN"
    unknown_issues = validate_bundle(unknown_source_bundle, schema, source_context, allow_fixture=True)
    unknown_codes = sorted({row["code"] for row in unknown_issues})
    results.append({"id": "source-only-action-rejects-unregistered-sourceKey", "expectPass": False,
                    "passed": "orphan_source_action_subject" in unknown_codes, "issueCodes": unknown_codes, "issues": unknown_issues})
    return {"fixtureCount": len(results), "passed": sum(row["passed"] for row in results), "failed": sum(not row["passed"] for row in results), "cases": results}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate the production contract and bundle")
    parser.add_argument("--fixtures", action="store_true", help="run isolated synthetic contract fixtures")
    args = parser.parse_args()
    if not args.check and not args.fixtures:
        parser.error("use --check and/or --fixtures")
    schema = load_schema()
    output: dict[str, Any] = {}
    if args.check:
        context = load_production_context()
        bundle = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        problems = validate_bundle(bundle, schema, context)
        output["production"] = {"valid": not problems, "actionCount": len(bundle.get("muscleActions", [])), "definitionCount": len(bundle.get("motionDefinitions", [])), "assetCount": len(bundle.get("motionAssets", [])), "issues": problems}
    if args.fixtures:
        output["fixtures"] = run_fixtures(schema)
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 1 if any(not group.get("valid", group.get("failed", 0) == 0) for group in output.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
