#!/usr/bin/env python3
"""Read-only integrity and boundary checks for the T53 static QA package."""

from __future__ import annotations

import hashlib
import json
import struct
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "atlas-data/manifests/bodyparts3d-r4-t53/source-manifest.json"
VALIDATION = ROOT / "work/evidence/T53/validation.json"
GLB = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t53/T53-trunk-pelvis-static-source.glb"
EXPECTED_UNRESOLVED = {"FJ1450", "FJ1451", "FJ1454", "FJ1455", "FJ1525", "FJ1543", "FJ1547", "FJ1548"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class T53PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
        cls.regions = {
            region: json.loads((ROOT / path["path"]).read_text(encoding="utf-8"))
            for region, path in cls.manifest["regionPackages"].items()
        }

    def test_frozen_asset_counts_and_batch_bound(self):
        self.assertEqual(138, self.manifest["scope"]["sourceElementFileCount"])
        self.assertEqual(138, self.manifest["assetCounts"]["uniqueMeshIds"])
        self.assertEqual(14, self.manifest["scope"]["internalBatchCount"])
        self.assertLessEqual(self.validation["maxBatches"], 10)
        self.assertTrue(self.validation["allFrozenItemsAcquired"])

    def test_each_region_manifest_reuses_one_stable_node_per_source_id(self):
        all_region_refs = []
        for region, package in self.regions.items():
            self.assertEqual(package["sourceElementFileCount"], len(package["sourceElementFileIds"]))
            self.assertEqual(package["sourceElementFileCount"], len(package["uniqueSceneNodeIds"]))
            for file_id, node_id in zip(package["sourceElementFileIds"], package["uniqueSceneNodeIds"]):
                self.assertEqual(f"HA-MESH-BP3D4-{file_id}", node_id)
                all_region_refs.append((region, file_id, node_id))
        unique_source_ids = {row["sourceElementFileId"] for row in self.manifest["sourceAssets"]}
        self.assertEqual(138, len(unique_source_ids))
        self.assertEqual(138, len({node_id for _, _, node_id in all_region_refs}))
        self.assertTrue(self.validation["regionMembershipsReuseNodeIds"])

    def test_header_identity_gaps_are_preserved_as_gaps(self):
        rows = {row["sourceElementFileId"]: row for row in self.manifest["sourceAssets"]}
        unresolved = {key for key, row in rows.items() if row["sourceIdentityState"] != "header_identity_validated_against_release_metadata"}
        self.assertEqual(EXPECTED_UNRESOLVED, unresolved)
        for source_id in unresolved:
            row = rows[source_id]
            self.assertIsNone(row["sourceConceptId"])
            self.assertIsNone(row["sourceRepresentationId"])
            self.assertIsNone(row["sourceName"])
            self.assertEqual("incomplete_not_inferred", row["sourceHeaderFmaBpPairState"])
            self.assertEqual("unknown_header_name_missing", row["lateralityFromExactSourceHeader"])
            self.assertTrue(row["sourceContextCandidates"])

    def test_no_canonical_membership_or_review_promotion(self):
        self.assertIsNone(self.manifest["scope"]["wholeBodyCanonicalDenominator"])
        self.assertFalse(self.manifest["scope"]["deepMuscleCoverageComplete"])
        self.assertEqual(0, self.manifest["assetCounts"]["canonicalLearnerBindings"])
        self.assertEqual(0, self.manifest["assetCounts"]["humanReviewed"])
        self.assertEqual(0, self.manifest["assetCounts"]["reviewedPromotions"])

    def test_header_bounds_are_compared_with_vertices_without_replacing_geometry(self):
        reconciliation = self.manifest["sourceBoundsHeaderReconciliation"]
        self.assertEqual(138, reconciliation["matchCount"] + len(reconciliation["mismatchIds"]))
        self.assertEqual(reconciliation["mismatchIds"], self.validation["sourceBoundsHeaderMismatchIds"])
        self.assertLess(reconciliation["maxAbsoluteDeltaMm"], 0.5)
        self.assertIn("actual vertex coordinates drive transformed geometry", reconciliation["policy"])

    def test_source_and_glb_hashes_are_bound_and_duplicate_geometry_absent(self):
        self.assertEqual(self.manifest["sceneContract"]["integratedGlbSha256"], sha256(GLB))
        self.assertEqual([], self.manifest["assetCounts"]["duplicateExactGeometryGroups"])
        self.assertEqual(0, self.manifest["assetCounts"]["sourceMeshEmpty"])
        self.assertTrue(self.validation["allSourcePositionsMatchProjectGlbFloat32"])

    def test_known_regional_bone_gaps_remain_explicit(self):
        self.assertEqual(0, len(self.regions["back"]["sourceBoneConceptIds"]))
        self.assertEqual(0, len(self.regions["abdomen-lumbar"]["sourceBoneConceptIds"]))
        self.assertEqual(0, len(self.regions["pelvis-perineum"]["sourceBoneConceptIds"]))
        self.assertEqual(38, self.regions["thorax"]["sourceMeshClassCounts"]["boneContextElements"])
        self.assertEqual(2, self.regions["gluteal-hip"]["sourceMeshClassCounts"]["boneContextElements"])

    def test_aabb_candidates_are_not_surface_intersection_claims(self):
        self.assertGreater(self.manifest["bounds"]["pairwiseAabbOverlapCandidateCount"], 0)
        self.assertIn("cannot prove penetration", self.manifest["bounds"]["diagnosticLimit"])
        self.assertTrue(self.validation["aabbOverlapIsNotTreatedAsPenetrationProof"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
