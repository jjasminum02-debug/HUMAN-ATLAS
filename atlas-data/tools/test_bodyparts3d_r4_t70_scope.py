#!/usr/bin/env python3
"""Independent, read-only checks for the T70 source and integration revision."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import build_bodyparts3d_r4_t70_scope as t70


class T70ScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scope = t70.load(t70.SCOPE)
        cls.integration = t70.load(t70.INTEGRATION)

    def test_recomputed_revision_is_byte_identical(self) -> None:
        scope, integration = t70.build()
        self.assertEqual(t70.encoded(scope), (t70.ROOT / t70.SCOPE).read_bytes())
        self.assertEqual(t70.encoded(integration), (t70.ROOT / t70.INTEGRATION).read_bytes())

    def test_source_closure_region_and_product_denominators_stay_separate(self) -> None:
        counts = self.scope["sourceTaxonomy"]
        self.assertEqual((counts["boneClosureUniqueElementFileCount"], counts["boneRegionAssignedUniqueElementFileCount"], counts["boneClosureAbsentFromHistoricalPackages"]), (203, 168, 35))
        self.assertEqual((counts["muscleClosureUniqueElementFileCount"], counts["muscleRegionAssignedUniqueElementFileCount"]), (323, 323))
        self.assertEqual(len(self.scope["boneClosureMissingSourceElements"]), 35)
        self.assertEqual(self.scope["productFirstPassMinimum"]["sourceElementFileCount"], 20)
        self.assertIsNone(self.scope["productFirstPassMinimum"]["canonicalWholeBodyIndividualMuscleDenominator"])

    def test_compound_and_part_elements_are_exact_official_relations(self) -> None:
        targets = {r["sourceFmaConceptId"]: r for r in self.scope["productFirstPassMinimum"]["conceptTargets"]}
        self.assertEqual(targets["FMA7485"]["sourceElementFileIds"], ["FJ3153", "FJ3178", "FJ3290"])
        self.assertEqual(targets["FMA22430"]["sourceElementFileIds"], ["FJ1433", "FJ1433M"])
        self.assertEqual(targets["FMA34687"]["sourceElementFileIds"], ["FJ1447", "FJ1447M"])
        self.assertEqual(targets["FMA34696"]["sourceElementFileIds"], ["FJ1464", "FJ1464M"])
        self.assertEqual(targets["FMA34699"]["sourceElementFileIds"], ["FJ1446", "FJ1446M"])
        self.assertEqual(targets["FMA22430"]["sourceRelation"]["parentConceptId"], "FMA22429")
        self.assertEqual(targets["FMA34696"]["sourceClassification"], ["outside_bone_and_muscle_organ_roots"])
        self.assertEqual(targets["FMA7485"]["productDecision"]["regionId"], "thorax")

    def test_next_batch_is_bounded_and_missing_from_old_packages(self) -> None:
        batch = self.scope["nextAcquisitionBatch"]
        ids = batch["sourceElementFileIds"]
        self.assertEqual(batch["taskId"], "T71")
        self.assertEqual(len(ids), 9)
        self.assertLessEqual(len(ids), batch["maxSourceElements"])
        self.assertTrue(set(ids) <= set(self.scope["productFirstPassMinimum"]["sourceElementFileIds"]))
        self.assertFalse(set(ids) & {r["sourceElementFileId"] for r in self.integration["assets"]})
        self.assertEqual(len(self.scope["productFirstPassMinimum"]["remainingAfterT71Batch"]), 11)

    def test_integration_deduplicates_real_packages_and_preserves_identity(self) -> None:
        rows = self.integration["assets"]
        self.assertEqual(len(rows), 493)
        self.assertEqual(sum(len(c["sourceElementFileIds"]) for c in self.integration["localQaChunks"]), 495)
        self.assertEqual(sum(len(c["suppressDuplicateSourceElementFileIds"]) for c in self.integration["localQaChunks"]), 2)
        by_id = {r["sourceElementFileId"]: r for r in rows}
        self.assertEqual({r["sourceElementFileId"] for r in rows if r["existingLearnerStableIds"]}, {r["sourceElementFileId"] for r in rows if r["learnerPickState"] == "existing_binding_unreviewed"})
        self.assertEqual(by_id["FJ1439"]["existingLearnerStableIds"], ["HA-M-000003"])
        self.assertEqual(by_id["FJ1439"]["renderNodeId"], "HA-MESH-BP3D4-FJ1439")
        self.assertEqual(self.integration["sceneContract"]["sourceLodLevelsAvailable"], 1)
        self.assertFalse(self.integration["sceneContract"]["highLodAvailable"])

    def test_laterality_and_blank_identity_holds_survive_integration(self) -> None:
        by_id = {r["sourceElementFileId"]: r for r in self.integration["assets"]}
        for fj in t70.EXPECTED_LATERALITY_HOLDS | t70.EXPECTED_IDENTITY_HOLDS:
            self.assertEqual(by_id[fj]["learnerPickState"], "held")
            self.assertFalse(by_id[fj]["learnerDefaultVisible"])
            self.assertTrue(by_id[fj]["holdReasons"])
        for fj in t70.EXPECTED_IDENTITY_HOLDS:
            self.assertIsNone(by_id[fj]["sourceNameObservation"])
            self.assertIsNone(by_id[fj]["sourceConceptIdObservation"])
        self.assertFalse(self.integration["holdPolicy"]["allStructuresRequireHumanReviewBeforeIndependentLocalEngineering"])
        self.assertFalse(self.integration["holdPolicy"]["heldNodesLearnerPickable"])

    def test_validator_rejects_lost_hold_duplicate_and_fictional_lod(self) -> None:
        damaged = copy.deepcopy(self.integration)
        item = next(r for r in damaged["assets"] if r["sourceElementFileId"] == "FJ2742")
        item["holdReasons"] = []
        item["learnerPickState"] = "source_only_unbound"
        with self.assertRaises(t70.ContractError):
            t70.validate(self.scope, damaged)
        damaged = copy.deepcopy(self.integration)
        damaged["assets"][0]["renderNodeId"] = damaged["assets"][1]["renderNodeId"]
        with self.assertRaises(t70.ContractError):
            t70.validate(self.scope, damaged)
        damaged = copy.deepcopy(self.integration)
        damaged["sceneContract"]["highLodAvailable"] = True
        with self.assertRaises(t70.ContractError):
            t70.validate(self.scope, damaged)

    def test_live_queue_status_and_t56_lod_scope_agree(self) -> None:
        registry = t70.load(Path("work/task-registry-r15.json"))
        status = (t70.ROOT / "work/STATUS.md").read_text(encoding="utf-8")
        t56 = (t70.ROOT / "work/tasks/T56.md").read_text(encoding="utf-8")
        self.assertEqual(registry["nextTask"], "T71")
        self.assertEqual(registry["nextUnallocatedNumericId"], 72)
        self.assertEqual(registry["activeQueue"][registry["activeQueue"].index("T55") + 1:registry["activeQueue"].index("T56")], ["T70", "T71"])
        self.assertEqual(registry["taskStatuses"]["T70"], "passed_with_gaps")
        self.assertEqual(registry["taskStatuses"]["T71"], "planned_not_started")
        self.assertTrue(any(line.startswith("- CURRENT_TASK: T70 — passed_with_gaps") for line in status.splitlines()[:10]))
        self.assertTrue(any(line.startswith("- NEXT_TASK: T71 / Luna Max") for line in status.splitlines()[:10]))
        self.assertIn("실제 source는 99%-reduced 단일 해상도", t56)
        self.assertNotIn("coarse body→필요한 high LOD", t56)


if __name__ == "__main__":
    unittest.main(verbosity=2)
