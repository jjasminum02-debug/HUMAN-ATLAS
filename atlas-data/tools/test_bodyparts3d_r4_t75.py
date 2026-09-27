#!/usr/bin/env python3
"""Regression checks for T75 frozen BodyParts3D R4 deltoid surfaces."""
from __future__ import annotations

import binascii
import hashlib
import importlib.util
import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = ["FJ1468", "FJ1468M", "FJ1467", "FJ1467M", "FJ1513", "FJ1513M"]
SIDES = {"FJ1468": "right", "FJ1468M": "left", "FJ1467": "right", "FJ1467M": "left", "FJ1513": "right", "FJ1513M": "left"}
PARTS = {"FJ1468": "clavicular", "FJ1468M": "clavicular", "FJ1467": "acromial", "FJ1467M": "acromial", "FJ1513": "spinal", "FJ1513M": "spinal"}
ACQUISITION = "work/evidence/T75/source-acquisition-attempt-03.json"
GLB = "atlas-data/source-cache/bodyparts3d-r4/converted/t75/T75-deltoid-bilateral-static-source.glb"


def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def central_directory_entry(path: str) -> bytes:
    name = path.encode("ascii")
    return struct.pack(
        "<4s6H3L5H2L", b"PK\x01\x02", 20, 20, 0, 0, 0, 0, 0, 0, 0,
        len(name), 0, 0, 0, 0, 0, 0,
    ) + name


class T75PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.freeze = load_json("work/evidence/T75/frozen-source-set.json")
        cls.acquisition = load_json(ACQUISITION)
        cls.manifest = load_json("atlas-data/manifests/bodyparts3d-r4-t75/source-manifest.json")
        cls.extension = load_json("atlas-data/manifests/bodyparts3d-r4-t75/integration-extension.json")
        cls.validation = load_json("work/evidence/T75/validation.json")
        cls.acquire_tool = load_module("ha_t75_test_acquire", "atlas-data/tools/acquire_bodyparts3d_r4_t75.py")
        cls.builder = load_module("ha_t75_test_builder", "atlas-data/tools/build_bodyparts3d_r4_t75.py")
        cls.qa = load_module("ha_t75_test_glb_qa", "atlas-data/tools/build_bodyparts3d_r4_t53.py")

    def test_frozen_scope_and_exact_part_laterality_are_not_suffix_inferred(self):
        freeze = self.freeze
        self.assertEqual(freeze["task"], "T75")
        self.assertEqual(freeze["sourceElementFileIds"], EXPECTED)
        self.assertEqual([row["count"] for row in freeze["internalBatches"]], [6])
        self.assertLessEqual(max(row["count"] for row in freeze["internalBatches"]), 10)
        self.assertTrue(freeze["doNotInferFromFjSuffixOrCoordinates"] if "doNotInferFromFjSuffixOrCoordinates" in freeze else freeze["policy"]["doNotInferFromFjSuffixOrCoordinates"])
        for row in freeze["uniqueNewSourceAssets"]:
            fid = row["sourceElementFileId"]
            self.assertEqual(row["side"], SIDES[fid])
            self.assertEqual(row["part"], PARTS[fid])
            self.assertEqual(row["declaredProductRegions"], ["shoulder-scapular", "upper-limb"])
        self.assertEqual(freeze["contextOnlyConceptIds"], ["FMA34676", "FMA34677", "FMA34678", "FMA34679"])
        self.assertEqual(freeze["latissimusDorsi"]["status"], "unavailable_in_bodyparts3d_r4_metadata")
        self.assertTrue(freeze["latissimusDorsi"]["noSubstituteOrGeometryAllowed"])

    def test_t75_parser_keeps_explicit_m_suffix_member_as_distinct_zip_id(self):
        archive_index = central_directory_entry("isa_BP3D_4.0_obj_99/FJ1468.obj") + central_directory_entry("isa_BP3D_4.0_obj_99/FJ1468M.obj")
        parsed = self.acquire_tool.parse_t75_central_directory(archive_index, expected_entries=2)
        self.assertEqual(set(parsed), {"FJ1468", "FJ1468M"})
        self.assertEqual(parsed["FJ1468"]["memberPath"], "isa_BP3D_4.0_obj_99/FJ1468.obj")
        self.assertEqual(parsed["FJ1468M"]["memberPath"], "isa_BP3D_4.0_obj_99/FJ1468M.obj")
        self.assertNotEqual(parsed["FJ1468"]["memberPath"], parsed["FJ1468M"]["memberPath"])

    def test_selected_byte_ranges_and_source_bytes_are_complete_and_exact(self):
        acq = self.acquisition
        frozen_raw = (ROOT / "work/evidence/T75/frozen-source-set.json").read_bytes()
        self.assertEqual(acq["result"], "pass")
        self.assertEqual(acq["frozenSourceSetSha256"], sha(frozen_raw))
        self.assertEqual(acq["attemptedIds"], EXPECTED)
        self.assertFalse(acq["fullArchiveDownloaded"])
        self.assertTrue(acq["selectedMemberRangeRequestsOnly"])
        self.assertEqual(len(acq["rangeRequests"]), 20)
        self.assertTrue(acq["allRangeResponsesHttp206"])
        self.assertTrue(all(row["httpStatus"] == 206 and row["bytes"] == row["end"] - row["start"] + 1 for row in acq["rangeRequests"]))
        self.assertTrue(all(row["etag"] == acq["archiveMetadata"]["etag"] for row in acq["rangeRequests"]))
        files = {row["sourceElementFileId"]: row for row in acq["files"]}
        self.assertEqual(set(files), set(EXPECTED))
        for fid, row in files.items():
            raw = (ROOT / row["cacheRelativePath"]).read_bytes()
            self.assertEqual(len(raw), row["bytes"], fid)
            self.assertEqual(sha(raw), row["sha256"], fid)
            self.assertEqual(f"{binascii.crc32(raw) & 0xFFFFFFFF:08x}", row["crc32"].lower(), fid)
            self.assertEqual(row["memberPath"], f"isa_BP3D_4.0_obj_99/{fid}.obj")
        failed_attempts = [load_json("work/evidence/T75/source-acquisition.json"), load_json("work/evidence/T75/source-acquisition-attempt-02.json")]
        self.assertTrue(any(row.get("result") != "pass" for row in failed_attempts))
        self.assertFalse(any(row.get("result") == "pass" for row in failed_attempts))

    def test_obj_rows_actual_surfaces_region_nodes_and_source_only_holds(self):
        rows = {row["sourceElementFileId"]: row for row in self.manifest["sourceAssets"]}
        self.assertEqual(set(rows), set(EXPECTED))
        self.assertEqual(self.manifest["source"]["projectFrame"], "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR")
        self.assertEqual(self.manifest["source"]["pose"], "bodyparts3d-r4-static-reference")
        self.assertEqual(self.manifest["source"]["transform"], "[x,y,z]mm -> [x,z,-y]m; x sign preserved; no mirroring or recentering")
        for fid, row in rows.items():
            self.assertEqual(row["explicitSourceSide"], SIDES[fid])
            self.assertEqual(row["sourceDeltoidPart"], PARTS[fid])
            self.assertTrue(row["lateralityNotInferredFromFjSuffixOrCoordinates"])
            self.assertGreater(row["sourceVertexCount"], 0)
            self.assertEqual(row["sourceNormalCount"], row["sourceVertexCount"])
            self.assertGreater(row["sourceTriangleCount"], 0)
            self.assertEqual(row["canonicalLearnerIds"], [])
            self.assertFalse(row["learnerDefaultVisible"])
            self.assertFalse(row["humanAnatomyReviewed"])
            self.assertEqual(row["learnerPickState"], "source_only_unbound")
            self.assertEqual([item["regionId"] for item in row["regionMemberships"]], ["shoulder-scapular", "upper-limb"])
            self.assertEqual({item["stableRenderNodeId"] for item in row["regionMemberships"]}, {f"HA-MESH-BP3D4-{fid}"})
        self.assertEqual(self.extension["counts"]["t75RegionMembershipRows"], 12)
        self.assertEqual(self.extension["counts"]["t75UniqueSourceNodes"], 6)
        self.assertEqual(self.extension["counts"]["uniqueSourceNodesIncludingT75"], 499)
        self.assertEqual(self.extension["counts"]["packageMembershipsIncludingT75"], 507)
        self.assertEqual(self.validation["result"], "pass")
        self.assertFalse(self.validation["wholeDeltoidComplete"])
        self.assertIsNone(self.validation["wholeBodyCanonicalDenominator"])
        self.assertEqual(self.validation["canonicalLearnerBindings"], 0)
        self.assertFalse(self.validation["defaultVisible"])
        self.assertTrue(self.validation["redistributionHold"])
        self.assertFalse(self.validation["humanAnatomyReviewed"])

    def test_manifest_glb_hash_topology_and_no_duplicate_geometry(self):
        claimed = self.manifest["manifestSha256"]
        unsigned = dict(self.manifest)
        unsigned["manifestSha256"] = None
        canonical = json.dumps(unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(sha(canonical), claimed)
        glb_path = ROOT / GLB
        raw = glb_path.read_bytes()
        self.assertEqual(sha(raw), self.manifest["sceneContract"]["integratedGlbSha256"])
        gltf, binary = self.qa.unpack_glb(raw)
        self.assertEqual(len(gltf["nodes"]), 6)
        self.assertEqual({node["extras"]["sourceElementFileId"] for node in gltf["nodes"]}, set(EXPECTED))
        asset_rows = {row["sourceElementFileId"]: row for row in self.manifest["sourceAssets"]}
        for row in self.manifest["meshRecords"]:
            fid = row["sourceElementFileId"]
            self.assertEqual(gltf["nodes"][row["nodeIndex"]]["name"], f"HA-MESH-BP3D4-{fid}")
            self.assertEqual(self.qa.glb_position_hash(gltf, binary, row["meshIndex"]), asset_rows[fid]["transformedPositionFloat32Sha256"])
            self.assertTrue(row["topologySha256"])
        self.assertEqual(self.validation["duplicateRawSourceHashGroups"], [])
        self.assertEqual(self.validation["duplicateConvertedGeometryTopologyGroups"], [])
        self.assertEqual(len({node["name"] for node in gltf["nodes"]}), 6)

    def test_history_and_private_preview_allowlist_are_bounded(self):
        baseline = load_json("work/evidence/T75/start-baseline.json")
        self.assertEqual(baseline["startingHead"], "d51ab9d51849c840e78ab8fb8f9df30deb75e122")
        for item in baseline["protectedExistingT74SourceAndDerivedFiles"]:
            raw = (ROOT / item["path"]).read_bytes()
            self.assertEqual(len(raw), item["bytes"], item["path"])
            self.assertEqual(sha(raw), item["sha256"], item["path"])
        for package, path, glb_path, expected_nodes in [
            ("T53", "atlas-data/manifests/bodyparts3d-r4-t53/source-manifest.json", GLB.replace("t75/T75-deltoid-bilateral-static-source.glb", "t53/T53-trunk-pelvis-static-source.glb"), 138),
            ("T54", "atlas-data/manifests/bodyparts3d-r4-t54/source-manifest.json", GLB.replace("t75/T75-deltoid-bilateral-static-source.glb", "t54/T54-shoulder-upper-limb-static-source.glb"), 142),
        ]:
            historical = load_json(path)
            glb_hash = sha((ROOT / glb_path).read_bytes())
            declared_hash = historical["sceneContract"].get("integratedGlbSha256") or historical["sceneContract"].get("qaGlbSha256")
            declared_nodes = historical["sceneContract"].get("meshNodeCount") or historical["sceneContract"].get("nodeCount")
            self.assertEqual(glb_hash, declared_hash, package)
            self.assertEqual(declared_nodes, expected_nodes, package)
            self.assertEqual(historical["source"]["projectFrame"], "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR")
            self.assertEqual(historical["source"]["pose"], "bodyparts3d-r4-static-reference")
            self.assertIn("[x,y,z]mm -> [x,z,-y]m", historical["source"]["transform"])
        prepare = load_json("work/evidence/T75/private-preview-preparation.json")
        self.assertTrue(prepare["onlyExactAllowlist"])
        self.assertFalse(prepare["repoRootExposed"])
        self.assertFalse(prepare["sourceCacheExposed"])
        self.assertEqual(prepare["relativeHostPath"], "work/evidence/T75/private-preview-host")
        cleanup = load_json("work/evidence/T75/private-preview-cleanup.json")
        self.assertTrue(cleanup["hostRemoved"])
        self.assertTrue(cleanup["sourceInodesUntouched"])
        self.assertEqual({row["path"] for row in prepare["files"]}, {
            "index.html", "private-preview.mjs", "assets/T53-trunk-pelvis-static-source.glb",
            "assets/T54-shoulder-upper-limb-static-source.glb", "assets/T75-deltoid-bilateral-static-source.glb",
            "vendor/three/build/three.module.js", "vendor/three/build/three.core.js",
            "vendor/three/examples/jsm/loaders/GLTFLoader.js", "vendor/three/examples/jsm/utils/BufferGeometryUtils.js",
            "vendor/three/examples/jsm/utils/SkeletonUtils.js",
        })

    def test_provenance_audit_and_actual_browser_evidence(self):
        audit = load_json("work/evidence/T75/source-audit.json")
        audited = {row["sourceElementFileId"]: row for row in audit["selectedSourceAssets"]}
        self.assertEqual(set(audited), set(EXPECTED))
        self.assertTrue(all(row["vertices"] > 0 and row["normals"] > 0 and row["triangles"] > 0 for row in audited.values()))
        self.assertTrue(all("Share Alike 2.1 Japan" in row["legacyObjLicenseHeader"] for row in audited.values()))
        self.assertTrue(all(row["boundsDeltaUse"].startswith("metadata discrepancy only") for row in audited.values()))
        checks = load_json("work/evidence/T75/official-source-checks.json")
        by_field = {row["field"]: row for row in checks["sources"]}
        self.assertIn("Release 4.0", by_field["99% reduced IS-A polygon mesh archive"]["edition"])
        self.assertIn("CC BY 4.0", by_field["Current database license"]["observed"])
        self.assertIn("held", by_field["Per-file legacy license headers"]["observed"])
        browser = load_json("work/evidence/T75/browser-verification.json")
        self.assertEqual(browser["composition"]["uniqueSceneNodes"], 284)
        self.assertEqual(browser["composition"]["sceneRootCount"], 1)
        self.assertEqual(browser["composition"]["rendererCount"], 1)
        self.assertEqual(set(browser["actualCameraViewsInspected"]), {"front", "back", "side"})
        self.assertEqual([row["selectedSourceElementFileId"] for row in browser["selectionChecks"]], EXPECTED)
        self.assertTrue(all(row["singlePressedRow"] == [row["selectedSourceElementFileId"]] and row["highlightApplied"] for row in browser["selectionChecks"]))
        self.assertEqual(browser["keyboardCheck"]["selectedAfterKey"], "FJ1468M")
        self.assertEqual(browser["consoleErrorWarningLogCount"], 0)
        self.assertEqual(browser["pageUncaughtErrorCount"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
