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
    return {
        "subjects": subjects,
        "structures": structures,
        "instances": instances,
        "claims": claims,
        "evidence": evidence,
        "aiFields": ai_fields,
        "licenses": licenses,
        "sourceLicenses": source_licenses,
        "scenes": scene_contexts,
        "legacyJointActions": {row["id"]: row for row in entities.get("jointActions", [])},
        "sourceIds": {row["id"] for row in entities.get("sources", [])},
        "fixtureAssets": {},
        "fixtureMode": False,
    }


def issue(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def validate_evidence_ref(ref: dict[str, Any], path: str, context: dict[str, Any], issues: list[dict[str, str]]) -> None:
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
        for subject_id in action["subjectIds"]:
            if subject_id not in context["subjects"]:
                issues.append(issue("orphan_action_subject", f"{path}.subjectIds", f"Unknown muscle/part ID {subject_id!r}."))
        joint_state = action["jointBindingState"]
        joint_note = action["jointBindingNote"]
        if joint_state == "canonical_bound" and (not action["targetJointIds"] or joint_note is not None):
            issues.append(issue("bound_joint_ids_missing", f"{path}.targetJointIds", "Canonical-bound actions need joint IDs and no unmapped note."))
        if joint_state == "unmapped" and (action["targetJointIds"] or not isinstance(joint_note, str) or not joint_note.strip()):
            issues.append(issue("unmapped_joint_binding_incomplete", f"{path}.jointBindingNote", "Unmapped actions need an explicit reason and must not invent joint IDs."))
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
        required_scopes = {"action_explanation", "context_role"}
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
        elif action["jointBindingState"] != "canonical_bound":
            issues.append(issue("motion_action_joint_unmapped", f"{path}.actionId", "A motion definition requires canonical joint bindings; text-only unmapped actions cannot define a clip."))
        elif not set(definition["targetJointIds"]).issubset(set(action["targetJointIds"])):
            issues.append(issue("motion_action_joint_mismatch", f"{path}.targetJointIds", "Motion definition joints must be declared by its MuscleAction."))
        if action and action["sideApplicability"] in {"right", "left"} and definition["side"] != action["sideApplicability"]:
            issues.append(issue("motion_action_side_mismatch", f"{path}.side", "Motion laterality conflicts with the MuscleAction side applicability."))
        instance = context["instances"].get(definition["instanceId"])
        if instance is None:
            issues.append(issue("orphan_motion_instance", f"{path}.instanceId", f"Unknown anatomical instance {definition['instanceId']!r}."))
        else:
            if action and instance.get("conceptId") not in action["subjectIds"]:
                issues.append(issue("motion_instance_subject_mismatch", f"{path}.instanceId", "Instance concept is not a subject of the bound MuscleAction."))
            if definition["side"] != instance.get("side"):
                issues.append(issue("motion_instance_side_mismatch", f"{path}.side", "Motion side must match the canonical instance laterality."))
        if definition["startPoseId"] != definition["staticReference"]["poseId"]:
            issues.append(issue("motion_start_pose_mismatch", f"{path}.startPoseId", "Motion must start from the exact static reference pose."))
        if definition["endPoseId"] == definition["startPoseId"]:
            issues.append(issue("motion_pose_range_empty", f"{path}.endPoseId", "Start and end pose IDs must differ."))
        if set(definition["movingStructureIds"]) & set(definition["fixedStructureIds"]):
            issues.append(issue("moving_fixed_structure_overlap", path, "A structure cannot be both moving and fixed in one motion definition."))
        for structure_id in definition["movingStructureIds"]:
            structure = context["structures"].get(structure_id)
            if structure is None or structure.get("kind") != "bone":
                issues.append(issue("invalid_moving_structure", f"{path}.movingStructureIds", f"Moving structure {structure_id!r} must resolve to a canonical bone."))
        for structure_id in definition["fixedStructureIds"]:
            if structure_id not in context["structures"]:
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

        if asset["representationType"] == "rigged_mesh":
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
        else:
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
