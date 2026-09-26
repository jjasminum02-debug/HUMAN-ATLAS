#!/usr/bin/env python3
"""Negative and regression tests for the T15b navigation migration contract."""
from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "atlas-data/navigation/validate_navigation.py"
spec = importlib.util.spec_from_file_location("human_atlas_navigation_validator", VALIDATOR_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("Could not load navigation validator")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
DATA = json.loads((ROOT / "atlas-data/navigation/atlas-navigation.json").read_text(encoding="utf-8"))
SCHEMA = json.loads((ROOT / "atlas-data/schemas/navigation.schema.json").read_text(encoding="utf-8"))


class NavigationContractTests(unittest.TestCase):
    def issue_codes(self, changed: dict) -> set[str]:
        return {issue["code"] for issue in validator.validate(changed, SCHEMA)}

    def test_current_migration_overlay_passes(self):
        self.assertEqual(validator.validate(DATA, SCHEMA), [])

    def test_duplicate_product_membership_is_rejected(self):
        changed = copy.deepcopy(DATA)
        duplicate = copy.deepcopy(changed["memberships"][0])
        duplicate["id"] += "-duplicate"
        changed["memberships"].append(duplicate)
        self.assertIn("duplicate_membership", self.issue_codes(changed))

    def test_orphaned_membership_id_is_rejected(self):
        changed = copy.deepcopy(DATA)
        changed["memberships"][0]["entityId"] = "HA-M-NOT-IN-CATALOG"
        self.assertIn("membership_target_not_muscle", self.issue_codes(changed))

    def test_decision_only_membership_needs_a_recorded_product_decision(self):
        changed = copy.deepcopy(DATA)
        changed["memberships"][0]["productDecisionRef"] = "T15b-DECISION-NOT-RECORDED"
        self.assertIn("missing_product_decision", self.issue_codes(changed))

    def test_muscle_mesh_cannot_be_rebound_as_a_bone(self):
        changed = copy.deepcopy(DATA)
        binding = next(row for row in changed["sceneManifests"][0]["selectableBindings"] if row["selection"]["kind"] == "muscle")
        binding["selection"] = {
            "kind": "bone", "conceptId": "HA-S-TIBIA", "instanceId": "HA-SI-R-HA-S-TIBIA", "meshId": binding["meshAssetId"],
        }
        self.assertIn("bone_binding_mapping_mismatch", self.issue_codes(changed))

    def test_landmark_cannot_be_selected_as_a_whole_bone(self):
        changed = copy.deepcopy(DATA)
        binding = next(row for row in changed["sceneManifests"][0]["selectableBindings"] if row["selection"]["kind"] == "bone")
        binding["selection"]["conceptId"] = "HA-S-TIBIA-LATERAL-CONDYLE"
        self.assertIn("selection_bone_type_mismatch", self.issue_codes(changed))

    def test_right_side_mesh_cannot_be_mapped_to_left_instance(self):
        changed = copy.deepcopy(DATA)
        instance = changed["structureInstances"][0]
        old_id = instance["id"]
        instance["side"] = "left"
        instance["id"] = f"HA-SI-L-{instance['structureId']}"
        for mapping in changed["structureMeshMappings"]:
            if mapping["structureInstanceId"] == old_id:
                mapping["structureInstanceId"] = instance["id"]
        for scene in changed["sceneManifests"]:
            for binding in scene["selectableBindings"]:
                if binding["selection"].get("instanceId") == old_id:
                    binding["selection"]["instanceId"] = instance["id"]
        self.assertIn("mesh_side_mismatch", self.issue_codes(changed))

    def test_unknown_target_mesh_must_remain_context_only(self):
        changed = copy.deepcopy(DATA)
        row = changed["unmappedMeshContexts"][0]
        row["selection"] = {"kind": "bone", "conceptId": "HA-S-CALCANEUS"}
        self.assertIn("schema_type", self.issue_codes(changed))

    def test_human_approval_cannot_be_fabricated(self):
        changed = copy.deepcopy(DATA)
        changed["structureMeshMappings"][0]["humanReviewState"] = "reviewed"
        self.assertIn("human_review_not_available", self.issue_codes(changed))

    def test_mapping_source_hash_must_be_current(self):
        changed = copy.deepcopy(DATA)
        changed["structureMeshMappings"][0]["sourceRefs"][0]["manifestSha256"] = "0" * 64
        self.assertIn("source_manifest_hash_mismatch", self.issue_codes(changed))

    def test_t13_mapping_keeps_the_matching_existing_source_evidence(self):
        changed = copy.deepcopy(DATA)
        row = next(row for row in changed["structureMeshMappings"] if row["sourceLinkageState"] == "inherited_t13_source_crosswalk")
        wrong = "EV-BP3D4-FJ3308-T13-ASSET"
        if row["evidenceIds"] == [wrong]:
            wrong = "EV-BP3D4-FJ3365-T13-ASSET"
        row["evidenceIds"] = [wrong]
        self.assertIn("t13_mapping_evidence_mismatch", self.issue_codes(changed))

    def test_scene_frame_and_pose_must_match_the_exact_source_model(self):
        changed_frame = copy.deepcopy(DATA)
        changed_frame["sceneManifests"][0]["frameId"] = "OTHER_FRAME"
        self.assertIn("scene_frame_pose_model_mismatch", self.issue_codes(changed_frame))
        changed_pose = copy.deepcopy(DATA)
        changed_pose["sceneManifests"][0]["poseId"] = "OTHER_POSE"
        self.assertIn("scene_frame_pose_model_mismatch", self.issue_codes(changed_pose))


if __name__ == "__main__":
    unittest.main(verbosity=2)
