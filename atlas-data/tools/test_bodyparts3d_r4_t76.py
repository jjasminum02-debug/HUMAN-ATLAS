#!/usr/bin/env python3
"""Regression checks for T76's bounded BodyParts3D R4 pelvic-floor package."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NEW = ["FJ1453M", "FJ1457M", "FJ1458M", "FJ2544", "FJ2545", "FJ2546", "FJ2549", "FJ2550", "FJ2551"]
REUSE = ["FJ1449M", "FJ2542", "FJ2547"]
ALL = ["FJ1449M", "FJ1453M", "FJ1457M", "FJ1458M", "FJ2542", "FJ2544", "FJ2545", "FJ2546", "FJ2547", "FJ2549", "FJ2550", "FJ2551"]
GLB = "atlas-data/source-cache/bodyparts3d-r4/converted/t76/T76-pelvic-floor-static-source.glb"


def read(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


class T76PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.freeze = read("work/evidence/T76/frozen-source-set.json")
        cls.failed_acquisition = read("work/evidence/T76/source-acquisition.json")
        cls.acquisition = read("work/evidence/T76/source-acquisition-attempt-02.json")
        cls.manifest = read("atlas-data/manifests/bodyparts3d-r4-t76/source-manifest.json")
        cls.extension = read("atlas-data/manifests/bodyparts3d-r4-t76/integration-extension.json")
        cls.validation = read("work/evidence/T76/validation.json")
        cls.acquirer = module("ha_t76_test_acquirer", "atlas-data/tools/acquire_bodyparts3d_r4_t76.py")
        cls.builder = module("ha_t76_test_builder", "atlas-data/tools/build_bodyparts3d_r4_t76.py")
        cls.qa = module("ha_t76_test_qa", "atlas-data/tools/build_bodyparts3d_r4_t53.py")

    def test_exact_frozen_scope_batches_and_concept_mesh_distinction(self):
        freeze = self.freeze
        self.assertEqual(freeze["sourceConceptCount"], 10)
        self.assertEqual(freeze["targetElementFileIds"], ALL)
        self.assertEqual(freeze["newSourceElementFileIds"], NEW)
        self.assertEqual([row["count"] for row in freeze["internalBatches"]], [5, 4])
        self.assertLessEqual(max(row["count"] for row in freeze["internalBatches"]), 10)
        concepts = {row["sourceConceptId"]: row for row in freeze["sourceConcepts"]}
        self.assertEqual(concepts["FMA19089"]["sourceSemanticLabel"], "group_or_zone")
        self.assertEqual(len(concepts["FMA19089"]["officialElementRows"]), 9)
        self.assertTrue(all(row["sourceRepresentationKind"] == "COMPOUND" for row in concepts.values()))
        self.assertEqual(sum(len(row["officialElementRows"]) for row in concepts.values()), 27)
        self.assertEqual(len(set(fid for row in concepts.values() for _fma, _name, fid in row["officialElementRows"])), 12)
        self.assertFalse(freeze["sourceRepresentationInterpretation"]["zoneConcept"].find("not a tenth") < 0)
        self.assertTrue(freeze["policy"]["neverInferFromFjSuffixOrCoordinates"])
        self.assertIsNone(freeze["policy"]["wholeBodyCanonicalDenominator"])

    def test_selected_acquisition_exact_ids_and_failed_attempt_are_not_misreported(self):
        self.assertNotEqual(self.failed_acquisition["result"], "pass")
        self.assertFalse(self.failed_acquisition["fullArchiveDownloaded"])
        acq = self.acquisition
        self.assertEqual(acq["result"], "pass")
        self.assertEqual(acq["attemptedIds"], NEW)
        self.assertEqual(len(acq["rangeRequests"]), 29)
        self.assertTrue(acq["allRangeResponsesHttp206"])
        self.assertFalse(acq["fullArchiveDownloaded"])
        self.assertTrue(acq["selectedMemberRangeRequestsOnly"])
        self.assertTrue(all(row["httpStatus"] == 206 and row["bytes"] == row["end"] - row["start"] + 1 for row in acq["rangeRequests"]))
        self.assertEqual(self.acquirer.check()["acquiredCount"], 9)
        self.assertEqual({row["sourceElementFileId"] for row in acq["files"]}, set(NEW))

    def test_headers_laterality_surfaces_and_extra_header_names_are_separate(self):
        rows = {row["sourceElementFileId"]: row for row in self.manifest["sourceAssets"]}
        self.assertEqual(set(rows), set(NEW))
        expected_names = {
            "FJ1453M": ("FMA45859", "BP8007", "Left iliococcygeus", "left"),
            "FJ1457M": ("FMA45855", "BP7791", "Left pubococcygeus", "left"),
            "FJ1458M": ("FMA45857", "BP8228", "Left puborectalis", "left"),
            "FJ2544": ("FMA45859", "BP8007", "Left iliococcygeus", "left"),
            "FJ2545": ("FMA45855", "BP7791", "Left pubococcygeus", "left"),
            "FJ2546": ("FMA45857", "BP8228", "Left puborectalis", "left"),
            "FJ2549": ("FMA45858", "BP8874", "Right iliococcygeus", "right"),
            "FJ2550": ("FMA45854", "BP9143", "Right pubococcygeus", "right"),
            "FJ2551": ("FMA45856", "BP8202", "Right puborectalis", "right"),
        }
        for fid, row in rows.items():
            header = row["sourceHeaderIdentity"]
            self.assertEqual((header["sourceFmaConceptId"], header["sourceRepresentationId"], header["sourceEnglishNameExactHeader"], row["exactSourceSideFromHeader"]), expected_names[fid])
            self.assertGreater(row["sourceVertexCount"], 0)
            self.assertEqual(row["sourceNormalCount"], row["sourceVertexCount"])
            self.assertGreater(row["sourceTriangleCount"], 0)
            self.assertTrue(row["lateralityNotInferredFromFjSuffixOrCoordinates"])
            self.assertGreaterEqual(row["sourceBoundsHeaderMaxAbsDeltaMm"], 0)
            self.assertTrue(row["sourceBoundsHeaderWithin001mm"])
        self.assertEqual({fid for fid, row in rows.items() if row["sourceHeaderConceptOutsideFrozenTenConceptRows"]}, {"FJ1458M", "FJ2546", "FJ2551"})
        self.assertTrue(self.validation["puborectalisHeaderConceptsRecordedWithoutExpandingFrozenTargetSet"])
        self.assertEqual({fid for fid, row in rows.items() if row["surfaceSideDiagnostic"]["crossesMidline"]}, {"FJ2549", "FJ2550", "FJ2551"})
        self.assertTrue(all(rows[fid]["surfaceSideDiagnostic"]["boundsWhollyOppositeToSourceLabel"] is False for fid in rows))

    def test_reuse_identity_hold_and_existing_bone_context_are_references_only(self):
        reuse = {row["sourceElementFileId"]: row for row in self.freeze["reuseOnly"]}
        self.assertEqual(list(reuse), REUSE)
        self.assertTrue(all(row["mustNotReacquireOrCopy"] and row["packageAlreadyPresentInT70"] for row in reuse.values()))
        for fid, row in reuse.items():
            path = ROOT / f"atlas-data/source-cache/bodyparts3d-r4/mesh/t53/{fid}.obj"
            self.assertEqual(sha(path.read_bytes()), row["sourceSha256"])
        sample = self.freeze["existingPelvisPerineumReference"]
        self.assertEqual(len(sample["sourceElementFileIds"]), 7)
        self.assertEqual(sample["distinctEnglishNameFamiliesObserved"], ["External anal sphincter", "coccygeus"])
        self.assertEqual(sample["existingIdentityHold"]["sourceElementFileId"], "FJ1450")
        self.assertEqual(sample["existingIdentityHold"]["sourceIdentityState"], "header_identity_blank_context_only")
        bones = {row["sourceElementFileId"]: row for row in self.freeze["relatedExistingBoneContext"]}
        self.assertEqual(set(bones), {"FJ3152", "FJ3288"})
        self.assertTrue(all(row["sameFrameAndPose"] and row["alreadyInT70"] for row in bones.values()))
        self.assertTrue(all("no perineal attachment" in row["relationship"] for row in bones.values()))
        self.assertEqual(self.manifest["scope"]["relatedBoneContextReferencesOnly"], self.freeze["relatedExistingBoneContext"])

    def test_manifest_glb_integrity_and_integration_counts(self):
        claimed = self.manifest["manifestSha256"]
        unsigned = dict(self.manifest)
        unsigned["manifestSha256"] = None
        canonical = json.dumps(unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(sha(canonical), claimed)
        raw = (ROOT / GLB).read_bytes()
        self.assertEqual(sha(raw), self.manifest["sceneContract"]["integratedGlbSha256"])
        gltf, binary = self.qa.unpack_glb(raw)
        self.assertEqual(len(gltf["nodes"]), 9)
        self.assertEqual({node["extras"]["sourceElementFileId"] for node in gltf["nodes"]}, set(NEW))
        rows = {row["sourceElementFileId"]: row for row in self.manifest["sourceAssets"]}
        for mesh in self.manifest["meshRecords"]:
            fid = mesh["sourceElementFileId"]
            self.assertEqual(self.qa.glb_position_hash(gltf, binary, mesh["meshIndex"]), rows[fid]["transformedPositionFloat32Sha256"])
            self.assertTrue(mesh["topologySha256"])
        self.assertEqual(self.validation["duplicateRawGroups"], [])
        self.assertEqual(self.validation["duplicateConvertedGeometryTopologyGroups"], [])
        self.assertEqual(self.extension["counts"]["historicalPackageMembershipsBeforeT76"], 495)
        self.assertEqual(self.extension["counts"]["packageMembershipsIncludingT76"], 504)
        self.assertEqual(self.extension["counts"]["uniqueSourceNodesIncludingT76"], 502)
        self.assertEqual(self.extension["counts"]["t76ReuseOnlySourceNodeCount"], 3)
        self.assertEqual(self.extension["counts"]["t76RelatedBoneContextReferenceCount"], 2)
        self.assertEqual(self.extension["t76TargetConceptCrosswalk"], self.manifest["targetConceptToElementCrosswalk"])

    def test_no_learner_promotion_rights_or_coverage_overclaim(self):
        self.assertEqual(self.validation["canonicalLearnerBindings"], 0)
        self.assertFalse(self.validation["defaultVisible"])
        self.assertFalse(self.validation["humanAnatomyReviewed"])
        self.assertTrue(self.validation["redistributionHold"])
        self.assertFalse(self.validation["perinealDenominatorComplete"])
        self.assertIsNone(self.validation["wholeBodyCanonicalDenominator"])
        self.assertFalse(self.manifest["learnerPolicyChanged"])
        self.assertFalse(self.manifest["rights"]["publicRelease"])
        self.assertFalse(self.manifest["humanAnatomyReviewed"])
        self.assertFalse(any("contact" in key.lower() or "nonpenetration" in key.lower() for key in self.validation))

    def test_history_inputs_and_open_sim_worktree_preserved(self):
        baseline = read("work/evidence/T76/start-baseline.json")
        for path, digest in baseline["workspaceInputSha256"].items():
            if Path(path).is_file():
                self.assertEqual(sha((ROOT / path).read_bytes()), digest, path)
        self.assertTrue(baseline["openSimModels"]["clean"])
        self.assertEqual(baseline["openSimModels"]["head"], "d9b05d470b1a481c222372c85b75772faf8f7792")
        self.assertEqual(self.validation["historicalT50T53T70T74T75InputsPreserved"], True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
