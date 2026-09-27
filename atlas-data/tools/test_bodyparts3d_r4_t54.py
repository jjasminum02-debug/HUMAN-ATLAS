#!/usr/bin/env python3
"""Regression checks for the frozen, source-only T54 shoulder/upper-limb package."""

from __future__ import annotations

import hashlib
import json
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "atlas-data/tools"))

FROZEN = ROOT / "work/evidence/T54/frozen-source-set.json"
ACQUISITION = ROOT / "work/evidence/T54/source-acquisition.json"
VALIDATION = ROOT / "work/evidence/T54/validation.json"
MISSING_POLICY = ROOT / "work/evidence/T54/scope-and-missing-policy.json"
MANIFEST = ROOT / "atlas-data/manifests/bodyparts3d-r4-t54/source-manifest.json"
T53_MANIFEST = ROOT / "atlas-data/manifests/bodyparts3d-r4-t53/source-manifest.json"
GLB = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t54/T54-shoulder-upper-limb-static-source.glb"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


class T54PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen = load(FROZEN)
        cls.acquisition = load(ACQUISITION)
        cls.validation = load(VALIDATION)
        cls.missing_policy = load(MISSING_POLICY)
        cls.manifest = load(MANIFEST)
        cls.t53 = load(T53_MANIFEST)

    def test_frozen_ids_batches_and_memberships_are_bounded(self):
        self.assertEqual(self.frozen["status"], "frozen_before_T54_acquisition")
        self.assertEqual(len(self.frozen["uniqueSourceAssets"]), 142)
        self.assertEqual(self.frozen["sourceMembershipCount"], 144)
        regions = {row["regionId"]: row for row in self.frozen["regionSets"]}
        self.assertEqual(len(regions["shoulder-scapular"]["sourceElementFileIds"]), 26)
        self.assertEqual(len(regions["upper-limb"]["sourceElementFileIds"]), 118)
        batches = self.frozen["internalBatches"]
        self.assertEqual(len(batches), 15)
        self.assertTrue(all(1 <= len(row["sourceElementFileIds"]) <= 10 for row in batches))
        self.assertEqual(set(self.frozen["duplicatedMembershipReferences"]), {"FJ3362", "FJ3384"})
        flattened = [fid for row in regions.values() for fid in row["sourceElementFileIds"]]
        self.assertEqual(len(flattened), 144)
        self.assertEqual(len(set(flattened)), 142)
        self.assertEqual(self.missing_policy["frozenMembershipSha256"], self.frozen["frozenMembershipSha256"])
        self.assertEqual(self.missing_policy["selectedUniqueSourceCount"], 142)
        self.assertEqual(self.missing_policy["missingFrozenSourceElementFileIds"], [])
        self.assertEqual(set(self.missing_policy["scopeBoundary"]["regionIds"]), {"shoulder-scapular", "upper-limb"})

    def test_acquisition_is_exactly_the_frozen_set_and_hashes(self):
        expected = {row["sourceElementFileId"] for row in self.frozen["uniqueSourceAssets"]}
        acquired = {row["sourceElementFileId"] for row in self.acquisition["files"]}
        self.assertEqual(acquired, expected)
        self.assertTrue(all(row["status"] == "acquired" for row in self.acquisition["files"]))
        self.assertFalse(self.acquisition["fullArchivesDownloaded"])
        self.assertTrue(self.validation["explicitMissingPolicyBoundToFrozenSet"])
        for row in self.acquisition["files"]:
            path = ROOT / row["cacheRelativePath"]
            self.assertTrue(path.is_file(), row["sourceElementFileId"])
            self.assertEqual(path.stat().st_size, row["bytes"], row["sourceElementFileId"])
            self.assertEqual(digest(path), row["sha256"], row["sourceElementFileId"])

    def test_unique_source_nodes_shared_connectors_and_glb_hashes(self):
        assets = self.manifest["sourceAssets"]
        by_id = {row["sourceElementFileId"]: row for row in assets}
        self.assertEqual(len(assets), 142)
        self.assertEqual(len(by_id), 142)
        self.assertEqual(len({row["stableSourceMeshNodeId"] for row in assets}), 142)
        self.assertEqual(digest(GLB), self.validation["integratedGlb"]["sha256"])
        self.assertEqual(GLB.stat().st_size, self.validation["integratedGlb"]["bytes"])
        self.assertEqual(self.validation["integratedGlb"]["nodeCount"], 142)
        t53_by_id = {row["sourceElementFileId"]: row for row in self.t53["sourceAssets"]}
        for fid in ("FJ3237", "FJ3279"):
            current, previous = by_id[fid], t53_by_id[fid]
            self.assertEqual(current["sourceSha256"], previous["sourceSha256"])
            self.assertEqual(current["stableSourceMeshNodeId"], f"HA-MESH-BP3D4-{fid}")
            self.assertEqual(current["stableSourceMeshNodeId"], previous["stableMeshAssetId"])
            self.assertEqual(current["projectFrame"], previous["projectFrame"])
            self.assertEqual(current["regionMemberships"], ["shoulder-scapular"])
            self.assertEqual(current["sharedSourceNodeWithTask"], "T53")
        for fid in ("FJ3362", "FJ3384"):
            self.assertEqual(by_id[fid]["regionMemberships"], ["shoulder-scapular", "upper-limb"])
            self.assertEqual(by_id[fid]["stableSourceMeshNodeId"], f"HA-MESH-BP3D4-{fid}")
        self.assertTrue(self.validation["sourcePositionHashesMatchGlbAccessors"])
        self.assertEqual(self.validation["emptySourceMeshes"], 0)
        self.assertEqual(self.validation["exactDuplicateGeometryGroups"], [])

    def test_hand_bone_and_muscle_picking_remain_independent_of_lod(self):
        assets = self.manifest["sourceAssets"]
        bones = [row for row in assets if row["handBonePickCandidate"]]
        muscles = [row for row in assets if row["handMusclePickCandidate"]]
        self.assertEqual(len(bones), 38)
        self.assertEqual(len(muscles), 12)
        self.assertEqual(Counter(row["lateralityFromExactSourceHeader"] for row in bones), {"left": 19, "right": 19})
        self.assertEqual(Counter(row["lateralityFromExactSourceHeader"] for row in muscles), {"left": 6, "right": 6})
        for row in bones + muscles:
            self.assertEqual(row["pickingTargetId"], f"HA-MESH-BP3D4-{row['sourceElementFileId']}")
            self.assertTrue(row["sourceName"])
            self.assertTrue(row["handPickContexts"], row["sourceElementFileId"])
            self.assertNotIn(row["sourceName"].lower(), {"hand", "hand bone", "hand muscle", "phalanx", "metacarpal"})
            self.assertTrue(row["lod"]["lodAssignmentId"].startswith("HA-LOD-BP3D4-R4-99REDUCED-"))
            self.assertNotIn("pickingTargetId", row["lod"])
            self.assertNotEqual(row["lod"]["lodAssignmentId"], row["pickingTargetId"])
            self.assertEqual(row["lod"]["sourceLevelCount"], 1)
            self.assertEqual(row["lod"]["alternateSourceLevels"], [])
            self.assertFalse(row["lod"]["generatedDecimation"])
        self.assertEqual(len({row["pickingTargetId"] for row in bones + muscles}), 50)
        self.assertEqual(self.validation["alternateSourceLodCount"], 0)
        self.assertEqual(self.validation["generatedLodCount"], 0)
        self.assertEqual(self.validation["lodAndPickingAreSeparateFields"], True)
        self.assertEqual(self.manifest["inputs"]["scopeAndMissingPolicySha256"], digest(MISSING_POLICY))

    def test_source_side_conflict_is_held_without_geometry_edit(self):
        by_id = {row["sourceElementFileId"]: row for row in self.manifest["sourceAssets"]}
        self.assertEqual(self.manifest["laterality"]["sourceLabels"], {"left": 71, "right": 71})
        self.assertEqual(set(self.manifest["laterality"]["whollyOppositeSourceLabelIds"]), {"FJ1469", "FJ1469M"})
        left, right = by_id["FJ1469"], by_id["FJ1469M"]
        self.assertEqual((left["sourceName"], left["sourceConceptId"], left["lateralityFromExactSourceHeader"]), ("Left flexor pollicis brevis", "FMA37389", "left"))
        self.assertEqual((right["sourceName"], right["sourceConceptId"], right["lateralityFromExactSourceHeader"]), ("Right flexor pollicis brevis", "FMA37388", "right"))
        self.assertEqual(left["lateralitySurfaceDiagnostic"]["xBoundsMm"], [-301.25, -256.014])
        self.assertEqual(right["lateralitySurfaceDiagnostic"]["xBoundsMm"], [256.014, 301.25])
        self.assertTrue(left["lateralitySurfaceDiagnostic"]["boundsWhollyOppositeToSourceLabel"])
        self.assertTrue(right["lateralitySurfaceDiagnostic"]["boundsWhollyOppositeToSourceLabel"])
        self.assertIn("preserve x sign", left["transform"])
        self.assertEqual(left["reviewState"], "source_only_not_human_anatomy_reviewed")
        self.assertEqual(self.validation["whollyOppositeSourceLabelIds"], ["FJ1469", "FJ1469M"])
        self.assertTrue(self.validation["sourceLabelSurfaceConflictHeldWithoutEdit"])
        self.assertFalse(self.validation["sourceSideSwapMirrorOrRelabelPerformed"])
        self.assertEqual(self.validation["sourceHeaderIdentityValidatedCount"], 142)

    def test_no_canonical_or_review_promotion_and_manifest_digest(self):
        self.assertEqual(self.manifest["status"], "local_static_source_package_partial_lod_and_license_review_pending")
        self.assertTrue(all(row["canonicalLearnerIds"] == [] for row in self.manifest["sourceAssets"]))
        self.assertEqual(self.manifest["scope"]["canonicalLearnerMembershipCreated"], False)
        self.assertEqual(self.manifest["scope"]["humanReviewPromotions"], 0)
        self.assertIsNone(self.manifest["scope"]["canonicalWholeBodyDenominator"])
        self.assertEqual(self.manifest["rights"]["publicRelease"], False)
        expected = dict(self.manifest)
        recorded = expected.pop("manifestSha256")
        actual = hashlib.sha256(json.dumps(expected, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(recorded, actual)
        self.assertTrue(self.validation["sourceRightsHeldForFileLevelReconciliation"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
