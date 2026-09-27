#!/usr/bin/env python3
"""Regression checks for the bounded T92 BodyParts3D R4 trapezius package."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_FJS = ["FJ1520", "FJ1520M", "FJ1554", "FJ1554M", "FJ1521", "FJ1521M"]
EXPECTED_FMAS = {"FMA32529", "FMA32555", "FMA32556", "FMA32557", "FMA33581", "FMA33583", "FMA33584", "FMA33585", "FMA33586", "FMA33587"}
SOURCE_MANIFEST = "atlas-data/manifests/bodyparts3d-r4-t92/source-manifest.json"
INTEGRATION = "atlas-data/manifests/bodyparts3d-r4-t92/integration-extension.json"
GLB = "atlas-data/source-cache/bodyparts3d-r4/converted/t92/T92-trapezius-static-source.glb"


def read(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    value = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


class T92PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.freeze = read("work/evidence/T92/frozen-source-set.json")
        cls.acq = read("work/evidence/T92/source-acquisition.json")
        cls.manifest = read(SOURCE_MANIFEST)
        cls.extension = read(INTEGRATION)
        cls.validation = read("work/evidence/T92/validation.json")
        cls.builder = module("ha_t92_test_builder", "atlas-data/tools/build_bodyparts3d_r4_t92.py")
        cls.acquirer = module("ha_t92_test_acquirer", "atlas-data/tools/acquire_bodyparts3d_r4_t92.py")
        cls.freezer = module("ha_t92_test_freezer", "atlas-data/tools/freeze_bodyparts3d_r4_t92.py")

    def test_scope_is_exactly_t73_t92_freeze_one_six_member_batch(self):
        self.assertEqual(self.freeze["status"], "frozen_before_mesh_acquisition")
        self.assertEqual(self.freeze["sourceConceptCount"], 10)
        self.assertEqual(self.freeze["conceptToElementRelationCount"], 14)
        self.assertEqual({row["sourceConceptId"] for row in self.freeze["sourceConcepts"]}, EXPECTED_FMAS)
        self.assertEqual(self.freeze["uniqueSourceElementFileIds"], EXPECTED_FJS)
        self.assertEqual([len(row["sourceElementFileIds"]) for row in self.freeze["internalBatches"]], [6])
        self.assertEqual(self.freezer.build_freeze(), self.freeze)
        self.assertTrue(all(row["sourceContextCandidates"] == ["back", "shoulder-scapular"] for row in self.freeze["uniqueSourceAssets"]))

    def test_selected_archive_acquisition_uses_exact_206_member_ranges_only(self):
        self.assertEqual(self.acq["result"], "pass")
        self.assertFalse(self.acq["fullArchiveDownloaded"])
        self.assertTrue(self.acq["selectedMemberRangeRequestsOnly"])
        self.assertEqual(self.acq["officialArchive"]["contentLength"], 142903898)
        self.assertEqual(self.acq["officialArchive"]["etag"], '"8848a5a-4dd48ec9df000"')
        self.assertEqual([row["sourceElementFileId"] for row in self.acq["files"]], EXPECTED_FJS)
        self.assertEqual(self.acq["officialArchive"]["selectedMemberCount"], 6)
        self.assertTrue(all(row["httpStatus"] == 206 and row["bytes"] == row["end"] - row["start"] + 1 for row in self.acq["rangeRequests"]))
        self.assertTrue(all(row["memberPath"].endswith(f"/{row['sourceElementFileId']}.obj") for row in self.acq["files"]))
        checked = self.acquirer.check()
        self.assertEqual(checked["sourceElementFileCount"], 6)
        self.assertEqual(checked["evidencePath"], "work/evidence/T92/source-acquisition.json")

    def test_obj_headers_official_identity_and_sided_names_are_exact(self):
        rows = {row["sourceElementFileId"]: row for row in self.manifest["sourceAssets"]}
        expected = {
            "FJ1520": ("FMA33581", "BP5638", "Ascending part of right trapezius", "right"),
            "FJ1520M": ("FMA33583", "BP8225", "Ascending part of left trapezius", "left"),
            "FJ1554": ("FMA33584", "BP5610", "Transverse part of right trapezius", "right"),
            "FJ1554M": ("FMA33585", "BP8252", "Transverse part of left trapezius", "left"),
            "FJ1521": ("FMA33586", "BP5636", "Descending part of right trapezius", "right"),
            "FJ1521M": ("FMA33587", "BP8267", "Descending part of left trapezius", "left"),
        }
        self.assertEqual(set(rows), set(EXPECTED_FJS))
        for file_id, (fma, bp, name, side) in expected.items():
            row = rows[file_id]
            identity = row["sourceHeaderIdentity"]
            self.assertEqual((identity["sourceFmaConceptId"], identity["sourceRepresentationId"], identity["sourceEnglishNameHeaderExact"]), (fma, bp, name))
            self.assertEqual(row["sideFromExactOfficialConceptRelation"], side)
            self.assertTrue(row["sideWasNotInferredFromFjSuffixOrCoordinates"])
            self.assertEqual(identity["boundsHeaderUnit"], "mm")
            self.assertTrue(row["boundsHeaderVsRawVertexExtremaMm"]["differenceMm"])
            self.assertGreater(row["sourceVertexCount"], 0)
            self.assertEqual(row["sourceNormalCount"], row["sourceVertexCount"])
            self.assertGreater(row["sourceTriangleCount"], 0)
        self.assertTrue(self.validation["allObjHeadersMatchExactFjFmaBpBuildTreeAndEnglishConceptName"])

    def test_concepts_and_two_regions_reference_one_stable_node_per_fj(self):
        crosswalk = self.manifest["targetConceptToElementCrosswalk"]
        self.assertEqual(len(crosswalk), 10)
        relation_rows = [relation for concept in crosswalk for relation in concept["renderNodeRelations"]]
        self.assertEqual(len(relation_rows), 14)
        self.assertEqual({row["sourceElementFileId"] for row in relation_rows}, set(EXPECTED_FJS))
        self.assertTrue(all(row["sameNodeSharedAcrossConcepts"] for row in relation_rows))
        ext_assets = {row["sourceElementFileId"]: row for row in self.extension["assets"] if row.get("primaryPackage") == "T92"}
        self.assertEqual(set(ext_assets), set(EXPECTED_FJS))
        for file_id, row in ext_assets.items():
            self.assertFalse(row["learnerDefaultVisible"])
            self.assertEqual(row["learnerPickState"], "source_only_unbound")
            self.assertFalse(row["humanAnatomyReviewed"])
            self.assertEqual(row["existingLearnerStableIds"], [])
            contexts = row["regionMembershipRows"]
            self.assertEqual([entry["regionId"] for entry in contexts], ["back", "shoulder-scapular"])
            self.assertEqual({entry["stableRenderNodeId"] for entry in contexts}, {row["renderNodeId"]})
            self.assertTrue(row["oneNodeSharedAcrossTwoCandidateContexts"])

    def test_glb_is_deterministic_and_matches_source_transform(self):
        raw = (ROOT / GLB).read_bytes()
        gltf, binary = self.builder.unpack_glb(raw)
        self.assertEqual(len(gltf["nodes"]), 6)
        self.assertEqual({node["extras"]["sourceElementFileId"] for node in gltf["nodes"]}, set(EXPECTED_FJS))
        rows = {row["sourceElementFileId"]: row for row in self.manifest["sourceAssets"]}
        for index, node in enumerate(gltf["nodes"]):
            file_id = node["extras"]["sourceElementFileId"]
            self.assertEqual(node["name"], f"HA-MESH-BP3D4-{file_id}")
            self.assertEqual(sha(self.builder.position_bytes(gltf, binary, index)), rows[file_id]["transformedPositionFloat32Sha256"])
        before = {path: sha((ROOT / path).read_bytes()) for path in [GLB, SOURCE_MANIFEST, INTEGRATION, "work/evidence/T92/validation.json"]}
        self.builder.build()
        after = {path: sha((ROOT / path).read_bytes()) for path in before}
        self.assertEqual(before, after)

    def test_separate_review_rights_and_learner_states_remain_held(self):
        self.assertFalse(self.manifest["identityAndReview"]["humanAnatomyReviewed"])
        self.assertFalse(self.manifest["identityAndReview"]["learnerDefaultVisible"])
        self.assertFalse(self.manifest["identityAndReview"]["learnerPolicyChanged"])
        self.assertEqual(self.manifest["identityAndReview"]["canonicalLearnerBindings"], 0)
        self.assertFalse(self.manifest["rights"]["publicRelease"])
        self.assertEqual(self.manifest["rights"]["redistributionStatus"], self.extension["publicRedistribution"])
        self.assertIsNone(self.manifest["scope"]["wholeBodyCanonicalDenominator"])
        self.assertEqual(self.extension["counts"]["t92UniqueNewSourceNodes"], 6)
        self.assertEqual(self.extension["counts"]["t92CandidateRegionContextReferences"], 12)

    def test_t70_t71_t72_t53_t54_inputs_match_t92_start_baseline(self):
        baseline = read("work/evidence/T92/start-baseline.json")
        starting = {row["path"]: row["sha256"] for row in baseline["preservedInputs"]}
        for relpath in [
            "atlas-data/manifests/bodyparts3d-r4-t70/scope-inventory.json",
            "atlas-data/manifests/bodyparts3d-r4-t70/integration-manifest.json",
            "atlas-data/manifests/bodyparts3d-r4-t71/source-manifest.json",
            "atlas-data/manifests/bodyparts3d-r4-t71/integration-manifest.json",
            "atlas-data/manifests/bodyparts3d-r4-t72/source-manifest.json",
            "atlas-data/manifests/bodyparts3d-r4-t72/integration-extension.json",
            "atlas-data/source-cache/bodyparts3d-r4/converted/t53/T53-trunk-pelvis-static-source.glb",
            "atlas-data/source-cache/bodyparts3d-r4/converted/t54/T54-shoulder-upper-limb-static-source.glb",
        ]:
            self.assertIn(relpath, starting)
            self.assertEqual(sha((ROOT / relpath).read_bytes()), starting[relpath], relpath)
        self.assertEqual(self.extension["parentIntegrationManifest"]["sha256"], starting["atlas-data/manifests/bodyparts3d-r4-t70/integration-manifest.json"])

    def test_actual_browser_qa_covers_three_views_and_exact_selected_node(self):
        browser = read("work/evidence/T92/browser-qa.json")
        self.assertEqual(browser["scene"]["rendererCount"], 1)
        self.assertEqual(browser["scene"]["canvasCount"], 1)
        self.assertEqual(browser["scene"]["anatomySceneRootCount"], 1)
        self.assertEqual(browser["scene"]["uniqueSourceNodeCount"], 284)
        self.assertEqual({row["view"] for row in browser["views"]}, {"front", "back", "side"})
        self.assertTrue(all(row["allSixTargetsVisible"] and row["anatomySceneRootCount"] == 1 and row["screenshotCapturedAndVisuallyInspected"] for row in browser["views"]))
        self.assertEqual(browser["selectionCheck"]["sourceElementFileId"], "FJ1520M")
        self.assertEqual(browser["selectionCheck"]["stableSourceMeshNodeId"], "HA-MESH-BP3D4-FJ1520M")
        self.assertEqual(browser["selectionCheck"]["contexts"], ["back", "shoulder-scapular"])
        self.assertTrue(browser["selectionCheck"]["highlightAppliedAndVisuallyInspected"])
        self.assertEqual(browser["console"], {"errors": 0, "warnings": 0})

    def test_final_preservation_check_has_no_unexpected_baseline_or_opensim_changes(self):
        preservation = read("work/evidence/T92/preservation-final.json")
        self.assertEqual(preservation["result"], "pass")
        self.assertEqual(preservation["baselineInputCount"], 735)
        self.assertEqual(preservation["unchangedBaselineInputCount"], 733)
        self.assertEqual(preservation["unexpectedChangedBaselineInputs"], [])
        self.assertEqual(preservation["missingBaselineInputs"], [])
        self.assertEqual(preservation["openSimModels"]["currentHead"], preservation["openSimModels"]["baselineHead"])
        self.assertTrue(preservation["openSimModels"]["currentClean"])

    def test_manifest_integrity_and_no_source_node_duplication(self):
        unsigned = dict(self.manifest)
        claimed = unsigned.pop("manifestSha256")
        self.assertEqual(sha(json.dumps({**unsigned, "manifestSha256": None}, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()), claimed)
        parent = {row.get("sourceElementFileId") for row in read("atlas-data/manifests/bodyparts3d-r4-t70/integration-manifest.json")["assets"]}
        self.assertFalse(parent & set(EXPECTED_FJS))
        self.assertTrue(self.validation["oneGlbNodePerUniqueFj"])
        self.assertEqual(self.validation["derivedGlb"]["sha256"], sha((ROOT / GLB).read_bytes()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
