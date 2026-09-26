#!/usr/bin/env python3
"""Regression checks for the T15g planning-only inventory generator."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_t15g_inventory as t15g  # noqa: E402


class T15gInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifacts = t15g.build()

    def test_partial_muscle_inventory_is_unique_and_type_separated(self):
        inventory = self.artifacts["inventory"]
        entries = inventory["currentMuscleConceptInventory"]
        ids = [row["id"] for row in entries]
        self.assertEqual(len(ids), 85)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(inventory["counts"]["muscleConcepts"]["byEntityType"], {
            "muscle_group": 16,
            "individual_muscle": 48,
            "muscle_part": 21,
        })
        self.assertEqual(inventory["counts"]["muscleConcepts"]["sourceCrosswalkRows"], 85)

    def test_unfrozen_denominator_never_emits_coverage_percentage(self):
        inventory = self.artifacts["inventory"]
        self.assertFalse(inventory["denominatorFrozen"])
        self.assertIsNone(inventory["wholeBodyIndividualMuscleCount"])
        self.assertIsNone(inventory["coveragePercent"])
        self.assertIsNone(inventory["knownGaps"]["wholeBodyMissingConceptIds"])

    def test_name_gaps_and_lookup_only_entries_are_not_promoted(self):
        counts = self.artifacts["inventory"]["counts"]["muscleConcepts"]
        self.assertEqual(counts["learningNameOverlayEntries"], 81)
        self.assertEqual(counts["learningNameCanonicalOverlap"], 79)
        self.assertEqual(len(counts["learningNameMissingCanonicalIds"]), 6)
        self.assertEqual(len(counts["lookupOnlyOverlayIdsNotInCanonicalCatalog"]), 2)
        missing = set(counts["learningNameMissingCanonicalIds"])
        for row in self.artifacts["inventory"]["currentMuscleConceptInventory"]:
            if row["id"] in missing:
                self.assertIsNone(row["learningNameOverlay"]["korean"])
                self.assertEqual(row["learningNameOverlay"]["status"], "missing_overlay_entry")

    def test_product_memberships_are_existing_only_and_region_scope_is_complete(self):
        crosswalk = self.artifacts["crosswalk"]
        self.assertEqual(len(crosswalk["sourceRegions"]), 18)
        self.assertTrue(all(row["membershipRowsCreated"] == 0 for row in crosswalk["sourceRegions"]))
        inventory = self.artifacts["inventory"]
        categories = inventory["counts"]["navigation"]["categoryMatrix"]
        self.assertEqual(len(categories), 12)
        self.assertEqual(sum(row["muscleMembershipCount"] for row in categories), 6)
        self.assertEqual(sum(row["boneMembershipCount"] for row in categories), 0)
        self.assertEqual(sum(row["sceneAvailability"] == "partial" for row in categories), 1)
        self.assertEqual(len(inventory["knownUnmappedMeshContexts"]), 4)

    def test_bone_inventory_separates_stable_ids_from_scene_bindings(self):
        inventory = self.artifacts["inventory"]
        bone_counts = inventory["counts"]["bones"]
        self.assertEqual(bone_counts["uniqueCanonicalBoneIds"], 10)
        self.assertEqual(bone_counts["uniqueRightSceneBoundBoneIds"], 9)
        self.assertEqual(len(inventory["currentCanonicalBoneInventory"]), 10)
        self.assertEqual(bone_counts["currentBoneProductMembershipRows"], 0)
        checks = inventory["counts"]["localAssets"]["t13SourceAssetHashChecks"]
        self.assertEqual(len(checks), 9)
        self.assertTrue(all(row["passed"] for row in checks))

    def test_expansion_batches_are_bounded_and_unissued(self):
        plan = self.artifacts["batches"]
        t33 = next(row for row in plan["gates"] if row["taskId"] == "T33")
        self.assertLessEqual(t33["maxConcepts"], 10)
        self.assertEqual(t33["targetStableIds"], [])
        self.assertEqual(plan["sceneBatchRule"]["maxScenesPerTask"], 1)
        self.assertTrue(plan["doNotStartAutomatically"])
        self.assertEqual(plan["sceneBatchRule"]["runtimeValidationDependency"]["taskId"], "T15f-FU01")

    def test_generated_files_match_current_source_hashes(self):
        self.assertEqual(t15g.validate_existing(self.artifacts), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
