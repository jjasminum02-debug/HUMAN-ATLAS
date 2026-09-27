#!/usr/bin/env python3
"""Regression tests for the frozen T55 bilateral lower-limb source package."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
import sys
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "atlas-data/tools"))

FROZEN = ROOT / "work/evidence/T55/frozen-source-set.json"
ACQUISITION = ROOT / "work/evidence/T55/source-acquisition.json"
MISSING_POLICY = ROOT / "work/evidence/T55/scope-and-missing-policy.json"
VALIDATION = ROOT / "work/evidence/T55/validation.json"
MANIFEST = ROOT / "atlas-data/manifests/bodyparts3d-r4-t55/source-manifest.json"
GLB = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t55/T55-bilateral-lower-limb-static-source.glb"
T07_CROSSWALK = ROOT / "atlas-data/manifests/mesh-crosswalk-t07.json"
T07_DERIVED = ROOT / "atlas-data/manifests/derived-assets-t07.json"
T07_GLB = ROOT / "atlas-data/assets/derived-glb/bodyparts3d-r4-right-lower-leg/right-lower-leg.glb"
T53_MANIFEST = ROOT / "atlas-data/manifests/bodyparts3d-r4-t53/source-manifest.json"
T54_MANIFEST = ROOT / "atlas-data/manifests/bodyparts3d-r4-t54/source-manifest.json"
REGION_ROOT = ROOT / "atlas-data/manifests/bodyparts3d-r4-t55"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"cannot load QA helper {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INGEST = load_module("ha_t55_test_ingest", ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py")
QA = load_module("ha_t55_test_qa", ROOT / "atlas-data/tools/build_bodyparts3d_r4_t53.py")


class T55PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen = load(FROZEN)
        cls.acquisition = load(ACQUISITION)
        cls.missing = load(MISSING_POLICY)
        cls.validation = load(VALIDATION)
        cls.manifest = load(MANIFEST)
        cls.acq_by_id = {row["sourceElementFileId"]: row for row in cls.acquisition["files"]}
        cls.asset_by_id = {row["sourceElementFileId"]: row for row in cls.manifest["sourceAssets"]}

    def test_frozen_source_membership_is_exact_and_batches_are_bounded(self):
        self.assertEqual(self.frozen["status"], "frozen_before_T55_acquisition")
        self.assertEqual(self.frozen["uniqueSourceElementFileCount"], 130)
        regions = {row["regionId"]: row for row in self.frozen["regionSets"]}
        self.assertEqual(set(regions), {"thigh", "leg", "foot"})
        self.assertEqual({key: len(row["sourceElementFileIds"]) for key, row in regions.items()}, {"thigh": 20, "leg": 30, "foot": 80})
        flattened = [file_id for row in regions.values() for file_id in row["sourceElementFileIds"]]
        self.assertEqual(len(flattened), 130)
        self.assertEqual(len(set(flattened)), 130)
        self.assertEqual(self.frozen["sourceMembershipCount"], 130)
        batches = self.frozen["internalBatches"]
        self.assertEqual(len(batches), 13)
        self.assertTrue(all(1 <= len(row["sourceElementFileIds"]) <= 10 for row in batches))
        self.assertEqual(set(flattened), {file_id for batch in batches for file_id in batch["sourceElementFileIds"]})
        self.assertEqual(self.frozen["duplicatedMembershipReferences"], {})

    def test_selected_acquisition_is_complete_and_verified_against_official_members(self):
        expected = {row["sourceElementFileId"] for row in self.frozen["uniqueSourceAssets"]}
        self.assertEqual(set(self.acq_by_id), expected)
        self.assertEqual(self.acquisition["sourceElementFileCountFailed"], 0)
        self.assertFalse(self.acquisition["fullArchivesDownloaded"])
        self.assertEqual(self.acquisition["sourceElementFileCountAcquired"], 130)
        self.assertEqual(self.acquisition["acquisitionMethods"].get("official_HTTP_206_selected_member_range"), 110)
        self.assertEqual(self.acquisition["acquisitionMethods"].get("existing_T51_or_T07_source_copy_verified_against_official_member_crc"), 20)
        for file_id, row in self.acq_by_id.items():
            path = ROOT / row["cacheRelativePath"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), row["bytes"], file_id)
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"], file_id)
            self.assertEqual(f"{zlib.crc32(payload) & 0xFFFFFFFF:08x}", row["crc32"], file_id)
            header = INGEST.read_obj_header(path)
            self.assertEqual(header["fileId"], file_id)
            tree = {"FMA 3.0 is_a": "IS-A", "FMA 3.0 part_of": "PART-OF"}.get(header["buildUpLogic"])
            self.assertEqual(tree, row["archiveTree"])

    def test_scene_nodes_are_source_faithful_bilateral_and_include_surfaces(self):
        self.assertEqual(len(self.asset_by_id), 130)
        self.assertEqual(len({row["stableSourceMeshNodeId"] for row in self.asset_by_id.values()}), 130)
        self.assertEqual(self.validation["integratedGlb"]["nodeCount"], 130)
        self.assertEqual(sha256_file(GLB), self.validation["integratedGlb"]["sha256"])
        self.assertEqual(GLB.stat().st_size, self.validation["integratedGlb"]["bytes"])
        self.assertEqual(self.manifest["assetCounts"]["emptyMeshes"], 0)
        self.assertGreater(self.manifest["assetCounts"]["boneContextNodes"], 0)
        self.assertGreater(self.manifest["assetCounts"]["muscleContextNodes"], 0)
        left = self.manifest["laterality"]["sourceLabels"].get("left", 0)
        right = self.manifest["laterality"]["sourceLabels"].get("right", 0)
        self.assertEqual((left, right), (64, 66))
        self.assertEqual(self.validation["whollyOppositeSourceLabelCount"], 0)
        self.assertEqual(self.validation["midlineCrossingCount"], 0)
        self.assertEqual(self.validation["sourceLabelsNotMirroredOrSwapped"], True)
        self.assertEqual(self.validation["sourcePositionHashesMatchGlbAccessors"], True)
        self.assertEqual(self.validation["exactDuplicateGeometryGroups"], [])
        self.assertEqual(self.validation["unresolvedSourceIdentityIds"], [])
        outside_roots = ["FJ1394", "FJ1397"]
        self.assertEqual(self.validation["outsideT51BoneOrMuscleRootContextSourceIds"], outside_roots)
        self.assertEqual(self.manifest["assetCounts"]["outsideT51BoneOrMuscleRootContextSourceIds"], outside_roots)
        self.assertEqual(self.manifest["assetCounts"]["outsideT51BoneOrMuscleRootContextNodes"], 2)
        legacy_exceptions = {row["sourceElementFileId"]: row for row in self.manifest["scope"]["T07LegacyMeshesOutsideT51BoneOrMuscleRoots"]}
        self.assertEqual(set(legacy_exceptions), set(outside_roots))
        self.assertEqual(legacy_exceptions["FJ1394"]["canonicalLearnerIds"], ["HA-P-000001"])
        self.assertEqual(legacy_exceptions["FJ1397"]["canonicalLearnerIds"], ["HA-P-000002"])
        self.assertTrue(all(row["legacyRelationStatus"] == "provisional_head_name_match_no_independent_anatomy_review" for row in legacy_exceptions.values()))

    def test_t07_legacy_mesh_and_canonical_ids_are_preserved_exactly(self):
        crosswalk = {row["fileId"]: row for row in load(T07_CROSSWALK)["entries"]}
        derived = load(T07_DERIVED)
        old_nodes = {row["sourceFileId"]: row for row in derived["meshNodes"]}
        overlaps = sorted(set(crosswalk) & set(self.asset_by_id))
        self.assertEqual(len(overlaps), 11)
        self.assertEqual(overlaps, self.manifest["legacyT07FragmentComparison"]["sourceIDsCompared"])
        self.assertTrue(self.manifest["legacyT07FragmentComparison"]["allSourceHashesVertexCountsTriangleCountsGeometryAndTopologyHashesMatch"])
        for file_id in overlaps:
            row = self.asset_by_id[file_id]
            self.assertEqual(row["canonicalLearnerIds"], [crosswalk[file_id]["targetEntityId"]] if crosswalk[file_id].get("targetEntityId") else [])
            self.assertEqual(row["legacyT07MappingPreservation"]["legacyRelationStatusPreserved"], crosswalk[file_id]["relationStatus"])
            self.assertEqual(row["sourceSha256"], old_nodes[file_id]["sourceSha256"])
            self.assertEqual(row["geometrySha256"], old_nodes[file_id]["geometrySha256"])
            self.assertEqual(row["topologySha256"], old_nodes[file_id]["topologySha256"])
        tibialis = self.asset_by_id["FJ1439"]
        self.assertEqual(tibialis["stableSourceMeshNodeId"], "HA-MESH-BP3D4-FJ1439")
        self.assertEqual(tibialis["canonicalLearnerIds"], ["HA-M-000003"])
        self.assertEqual(tibialis["sourceName"], "Right tibialis anterior")
        self.assertEqual(tibialis["sourceVertices"], 2204)
        self.assertEqual(tibialis["sourceTriangles"], 2510)
        self.assertEqual(tibialis["topologySha256"], "17aa54b23b003e253001abc360b19ad35d0ca004a1716e120be0e339895da1eb")
        self.assertEqual(tibialis["reviewState"], "source_only_not_human_anatomy_reviewed")
        self.assertEqual(self.validation["existingTibialisAnteriorSourceHashAndTopologyPreserved"], True)
        self.assertEqual(self.manifest["scope"]["canonicalLearnerMembershipCreated"], False)
        self.assertEqual(self.manifest["scope"]["humanReviewPromotions"], 0)

    def test_same_source_boundary_pairs_and_header_bounds_gaps_are_explicit(self):
        self.assertEqual(self.validation["T53T54SameSourceFrameAndPose"], True)
        self.assertEqual(self.validation["T55CrossTaskOverlap"], {"T53": [], "T54": []})
        pairs = self.manifest["lowerLimbBoundaryQA"]["sameLateralityBoundaryPairs"]
        self.assertEqual(len(pairs), 6)
        self.assertEqual({row["boundaryId"] for row in pairs}, {"pelvis-to-thigh", "thigh-to-leg", "leg-to-foot"})
        self.assertEqual({row["laterality"] for row in pairs}, {"right", "left"})
        self.assertTrue(all(row["aabbRelation"]["aabbOverlap"] for row in pairs))
        self.assertTrue(all("does not prove surface contact" in row["aabbRelation"]["interpretation"] for row in pairs))
        source_bounds = self.manifest["sourceBoundsHeaderReconciliation"]
        self.assertEqual(source_bounds["matchCount"] + len(source_bounds["mismatchIds"]), 130)
        self.assertEqual(len(source_bounds["mismatchIds"]), 35)
        self.assertLess(source_bounds["maxAbsoluteDeltaMm"], 0.5)
        self.assertTrue(source_bounds["geometryDerivedFromActualVertices"])
        for region in ("thigh", "leg", "foot"):
            doc = load(REGION_ROOT / f"{region}.json")
            self.assertEqual(doc["sourceElementFileCount"], {"thigh": 20, "leg": 30, "foot": 80}[region])
            self.assertEqual(len(set(doc["sourceElementFileIds"])), doc["sourceElementFileCount"])

    def test_static_preview_contract_and_browser_interaction_evidence(self):
        html = (ROOT / "work/evidence/T55/private-preview.html").read_text(encoding="utf-8")
        script = (ROOT / "work/evidence/T55/private-preview.mjs").read_text(encoding="utf-8")
        self.assertEqual(html.count("<canvas"), 1)
        self.assertIn('new THREE.WebGLRenderer', script)
        self.assertIn('anatomySceneRoot.name = "AnatomySceneRoot"', script)
        self.assertNotIn("requestAnimationFrame(", script)
        self.assertNotIn("renderer.setAnimationLoop", script)
        browser = load(ROOT / "work/evidence/T55/browser-verification.json")
        self.assertEqual(browser["result"], "passed_static_source_browser_review")
        self.assertEqual(browser["uniqueMeshCount"], 408)
        self.assertEqual(browser["rendererCount"], 1)
        self.assertEqual(browser["anatomySceneRootCount"], 1)
        self.assertEqual(set(browser["testedViewportWidths"]), {1440, 1024, 390})
        self.assertEqual(set(browser["verifiedCameraViews"]), {"front", "back", "side"})
        selection = browser["keyboardSelection"]
        self.assertEqual(selection["sourceElementFileId"], "FJ1439")
        self.assertEqual(selection["stableSourceMeshNodeId"], "HA-MESH-BP3D4-FJ1439")
        self.assertEqual(selection["canonicalLearnerId"], "HA-M-000003")
        self.assertTrue(browser["uncaughtPageErrorEvents"] == 0)

    def test_manifests_bind_inputs_and_leave_whole_body_denominator_open(self):
        self.assertEqual(self.manifest["inputs"]["frozenSetSha256"], sha256_file(FROZEN))
        self.assertEqual(self.manifest["inputs"]["acquisitionSha256"], sha256_file(ACQUISITION))
        self.assertEqual(self.manifest["inputs"]["scopeAndMissingPolicySha256"], sha256_file(MISSING_POLICY))
        self.assertEqual(self.missing["frozenSourceSetSha256"], sha256_file(FROZEN))
        self.assertEqual(self.missing["missingFrozenSourceElementFileIds"], [])
        self.assertEqual(self.missing["acquisitionFailureSourceElementFileIds"], [])
        self.assertFalse(self.manifest["rights"]["publicRelease"])
        self.assertIsNone(self.manifest["scope"]["wholeBodyCanonicalDenominator"])
        self.assertEqual(self.manifest["source"]["pose"], "bodyparts3d-r4-static-reference")
        expected = dict(self.manifest)
        recorded = expected.pop("manifestSha256")
        actual = hashlib.sha256(json.dumps(expected, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        self.assertEqual(recorded, actual)
        self.assertEqual(self.validation["result"], "source_package_built_static_only; learner/anatomy review_lod_and_public_rights_pending")


if __name__ == "__main__":
    unittest.main(verbosity=2)
