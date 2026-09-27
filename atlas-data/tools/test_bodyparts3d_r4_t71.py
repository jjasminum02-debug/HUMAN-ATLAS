#!/usr/bin/env python3
"""Offline regressions for the exact, source-only T71 package."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IDS = ["FJ3153", "FJ3157", "FJ3159", "FJ3162", "FJ3165", "FJ3168", "FJ3178", "FJ3290", "FJ3393"]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


ACQUIRE = load("t71_acquire", ROOT / "atlas-data/tools/acquire_bodyparts3d_r4_t71.py")
BUILD = load("t71_build", ROOT / "atlas-data/tools/build_bodyparts3d_r4_t71.py")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class T71PackageTests(unittest.TestCase):
    def test_frozen_batch_is_exact_nine_and_one_batch_below_ten(self):
        frozen = read_json(BUILD.FROZEN)
        self.assertEqual(frozen["sourceElementFileIds"], IDS)
        self.assertEqual(len(frozen["uniqueSourceAssets"]), 9)
        self.assertEqual([len(batch["sourceElementFileIds"]) for batch in frozen["internalBatches"]], [9])
        self.assertEqual(frozen["internalBatchSizeLimit"], 10)
        self.assertEqual(frozen["status"], "frozen_before_mesh_acquisition")

    def test_acquisition_exact_ids_crc_sha_and_no_full_archive(self):
        check = ACQUIRE.check()
        acquisition = read_json(BUILD.ACQUISITION)
        self.assertEqual(check["sourceElementFileCount"], 9)
        self.assertEqual({row["sourceElementFileId"] for row in acquisition["files"]}, set(IDS))
        self.assertTrue(all(row["sourceAcquisitionMethod"] == "official_HTTP_206_selected_member_range" for row in acquisition["files"]))
        self.assertTrue(all(row["status"] == "acquired" for row in acquisition["files"]))
        self.assertFalse(acquisition["fullArchivesDownloaded"])
        self.assertTrue(acquisition["selectedMemberRangeRequestsOnly"])

    def test_source_identity_mesh_payload_and_review_rights_held(self):
        manifest = read_json(BUILD.OUT_MANIFEST)
        validation = read_json(BUILD.OUT_VALIDATION)
        glb = BUILD.OUT_GLB.read_bytes()
        gltf, _ = BUILD.T53_QA.unpack_glb(glb)
        self.assertEqual([row["sourceElementFileId"] for row in manifest["sourceAssets"]], IDS)
        self.assertEqual(len(gltf["nodes"]), 9)
        self.assertEqual(len({node["name"] for node in gltf["nodes"]}), 9)
        self.assertTrue(validation["allHeadersMatchExactFjAndExpectedFma"])
        self.assertTrue(validation["allHeaderBpFmaPairsInOfficialMetadata"])
        self.assertTrue(validation["sourceHeaderAndOfficialIndexEnglishNameMatch"])
        self.assertTrue(validation["positionPayloadMatchesExactSourceTransform"])
        self.assertEqual(validation["exactDuplicateGeometryTopologyGroups"], [])
        self.assertEqual(validation["canonicalLearnerBindings"], 0)
        self.assertFalse(validation["humanAnatomyReviewed"])
        self.assertFalse(validation["publicRelease"])
        self.assertTrue(all(row["sourceTriangleCount"] > 0 for row in manifest["sourceAssets"]))
        self.assertTrue(all(row["lateralityFromExactSourceName"] == "not_lateralized_by_exact_source_name" for row in manifest["sourceAssets"]))
        self.assertTrue(all("x sign" in row["transform"] for row in manifest["sourceAssets"]))
        self.assertTrue(all("held_pending_file_level_license_reconciliation" in row["redistributionStatus"] for row in manifest["sourceAssets"]))

    def test_shared_scene_inputs_and_new_t70_contract_extension(self):
        t53 = read_json(ROOT / "atlas-data/manifests/bodyparts3d-r4-t53/source-manifest.json")
        t55 = read_json(ROOT / "atlas-data/manifests/bodyparts3d-r4-t55/source-manifest.json")
        base = read_json(BUILD.T70_INTEGRATION)
        extended = read_json(BUILD.OUT_INTEGRATION)
        for package in (t53, t55):
            self.assertEqual(package["source"]["projectFrame"], BUILD.FRAME)
            self.assertEqual(package["source"]["pose"], BUILD.POSE)
        old_ids = {row["sourceElementFileId"] for row in base["assets"]}
        new_ids = {row["sourceElementFileId"] for row in extended["assets"]} - old_ids
        self.assertEqual(new_ids, set(IDS))
        self.assertEqual(extended["parentIntegrationManifest"]["sha256"], sha(BUILD.T70_INTEGRATION))
        self.assertTrue(extended["parentIntegrationManifest"]["historicalManifestUnchanged"])
        self.assertEqual(extended["counts"]["uniqueSourceNodesIncludingT71"], 502)
        self.assertEqual(extended["counts"]["newCanonicalBindings"], 0)
        self.assertEqual(extended["counts"]["newHumanReviewed"], 0)
        self.assertTrue(all(next(a for a in extended["assets"] if a["sourceElementFileId"] == fid)["learnerPickState"] == "source_only_unbound" for fid in IDS))

    def test_recalculate_first_pass_and_remaining_source_bone_gaps(self):
        scope = read_json(BUILD.T70_SCOPE)
        remaining_minimum = set(scope["productFirstPassMinimum"]["remainingAfterT71Batch"])
        self.assertEqual(len(remaining_minimum), 11)
        bone_gap = {row["sourceElementFileId"] for row in scope["boneClosureMissingSourceElements"]}
        t71_bone_root_ids = {fid for fid in IDS if any(ctx["sourceFmaConceptId"] in {"FMA5018", "FMA7477", "FMA9914", "FMA9921", "FMA16202"} for ctx in next(row for row in read_json(BUILD.FROZEN)["uniqueSourceAssets"] if row["sourceElementFileId"] == fid)["sourceContexts"])}
        remaining_bone_gap = bone_gap - t71_bone_root_ids
        self.assertEqual(len(bone_gap), 35)
        self.assertEqual(t71_bone_root_ids, {"FJ3157", "FJ3159", "FJ3162", "FJ3165", "FJ3168", "FJ3393"})
        self.assertEqual(len(remaining_bone_gap), 29)
        self.assertFalse(set(IDS) & remaining_minimum)

    def test_history_hashes_stay_pinned_by_frozen_baseline(self):
        baseline = read_json(ROOT / "work/evidence/T71/start-baseline.json")
        immutable = [
            "work/reports/T70.md",
            "atlas-data/manifests/bodyparts3d-r4-t70/scope-inventory.json",
            "atlas-data/manifests/bodyparts3d-r4-t70/integration-manifest.json",
            "atlas-data/manifests/bodyparts3d-r4-source-manifest-t51.json",
            "atlas-data/manifests/bodyparts3d-r4-t52/head-neck.json",
            "atlas-data/manifests/bodyparts3d-r4-t53/source-manifest.json",
            "atlas-data/manifests/bodyparts3d-r4-t54/source-manifest.json",
            "atlas-data/manifests/bodyparts3d-r4-t55/source-manifest.json",
            "work/evidence/T51/source-cache-file-inventory.json",
            "work/evidence/T53/frozen-source-set.json",
            "work/evidence/T53/source-acquisition.json",
            "work/evidence/T55/frozen-source-set.json",
            "work/evidence/T55/source-acquisition.json",
        ]
        for path in immutable:
            digest = baseline["requiredInputSha256"][path]
            self.assertEqual(sha(ROOT / path), digest, path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
