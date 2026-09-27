#!/usr/bin/env python3
"""Read-only regression checks for the frozen T74 BodyParts3D subset."""
from __future__ import annotations

import binascii
import hashlib
import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = ["FJ3274", "FJ3386", "FJ3281", "FJ3392", "FJ3287", "FJ3375", "FJ3269", "FJ3378", "FJ3272"]
REUSE = {"FJ3380": "T52", "FJ3200": "T72", "FJ3289": "T72", "FJ3309": "T72"}


def read_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_module(name: str, relative: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {relative}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class T74PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.freeze = read_json("work/evidence/T74/frozen-source-set.json")
        cls.acquisition = read_json("work/evidence/T74/source-acquisition.json")
        cls.manifest = read_json("atlas-data/manifests/bodyparts3d-r4-t74/source-manifest.json")
        cls.extension = read_json("atlas-data/manifests/bodyparts3d-r4-t74/integration-extension.json")
        cls.validation = read_json("work/evidence/T74/validation.json")
        cls.qa = load_module("ha_t74_test_glb_qa", "atlas-data/tools/build_bodyparts3d_r4_t53.py")
        cls.ingest = load_module("ha_t74_test_ingest", "atlas-data/tools/ingest_bodyparts3d_r4.py")

    def test_frozen_exact_source_scope_and_batches(self):
        self.assertEqual(self.freeze["task"], "T74")
        self.assertEqual(self.freeze["archiveTree"], "PART-OF")
        self.assertEqual(self.freeze["sourceElementFileIds"], EXPECTED)
        self.assertEqual([len(row["sourceElementFileIds"]) for row in self.freeze["internalBatches"]], [5, 4])
        self.assertEqual(set(self.freeze["reuseOnly"]), set(REUSE))
        canonical = "".join(
            f"{row['sourceConceptId']}|{row['sourceRepresentationId']}|{row['sourceElementFileId']}|{row['sourceNameEnglish']}|{row['side']}|PART-OF\n"
            for row in self.freeze["uniqueNewSourceAssets"]
        )
        self.assertEqual(digest(canonical.encode("utf-8")), self.freeze["frozenMembershipSha256"])

    def test_selected_range_acquisition_is_exact_and_reproducible(self):
        acq = self.acquisition
        freeze_raw = (ROOT / "work/evidence/T74/frozen-source-set.json").read_bytes()
        self.assertEqual(acq["result"], "pass")
        self.assertEqual(acq["frozenSourceSetSha256"], digest(freeze_raw))
        self.assertFalse(acq["fullArchiveDownloaded"])
        self.assertTrue(acq["selectedMemberRangeRequestsOnly"])
        self.assertEqual(acq["attemptedIds"], EXPECTED)
        self.assertEqual(acq["acquiredCount"], 9)
        self.assertEqual(acq["failedCount"], 0)
        self.assertEqual(len(acq["rangeRequests"]), 29)
        self.assertTrue(all(r["httpStatus"] == 206 and r["bytes"] == r["end"] - r["start"] + 1 for r in acq["rangeRequests"]))
        self.assertTrue(all(r["url"] == acq["archiveUrl"] and r["etag"] == acq["archiveMetadata"]["etag"] for r in acq["rangeRequests"]))
        self.assertEqual(sum(r["sourceElementFileId"] is None for r in acq["rangeRequests"]), 2)
        for fid in EXPECTED:
            requests = [r for r in acq["rangeRequests"] if r["sourceElementFileId"] == fid]
            self.assertEqual(len(requests), 3, fid)

        by_id = {row["sourceElementFileId"]: row for row in acq["files"]}
        self.assertEqual(set(by_id), set(EXPECTED))
        for fid, row in by_id.items():
            raw = (ROOT / row["cacheRelativePath"]).read_bytes()
            self.assertEqual(len(raw), row["bytes"], fid)
            self.assertEqual(digest(raw), row["sha256"], fid)
            self.assertEqual(f"{binascii.crc32(raw) & 0xffffffff:08x}", row["crc32"].lower(), fid)
            self.assertEqual(row["memberPath"], f"partof_BP3D_4.0_obj_99/{fid}.obj")

    def test_obj_identity_side_and_nonempty_geometry_match_frozen_rows(self):
        acquired = {r["sourceElementFileId"]: r for r in self.acquisition["files"]}
        frozen = {r["sourceElementFileId"]: r for r in self.freeze["uniqueNewSourceAssets"]}
        assets = {r["sourceElementFileId"]: r for r in self.manifest["sourceAssets"]}
        self.assertEqual(set(assets), set(EXPECTED))
        self.assertEqual(set(frozen), set(EXPECTED))
        for fid in EXPECTED:
            target = frozen[fid]
            obj = ROOT / acquired[fid]["cacheRelativePath"]
            header = self.qa.parse_header(obj)
            self.ingest.validate_obj_source_identity(header, self.ingest.load_tables(ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"))
            self.assertEqual(header["fileId"], fid)
            self.assertEqual(header["conceptId"], target["sourceConceptId"])
            self.assertEqual(header["representationId"], target["sourceRepresentationId"])
            self.assertEqual(header["buildUpLogic"], "FMA 3.0 part_of")
            self.assertEqual(header["englishName"].casefold(), target["sourceNameEnglish"].casefold())
            self.assertEqual({s.casefold() for s in re.findall(r"\b(left|right)\b", header["englishName"], re.I)}, {target["side"]})
            self.assertTrue(header["licenseHeader"])
            self.assertTrue(header["boundsMm"])
            row = assets[fid]
            self.assertEqual(row["sourceSha256"], acquired[fid]["sha256"])
            self.assertEqual(row["sourceCrc32"], acquired[fid]["crc32"])
            self.assertGreater(row["sourceVertexCount"], 0)
            self.assertEqual(row["sourceNormalCount"], row["sourceVertexCount"])
            self.assertGreater(row["sourceTriangleCount"], 0)
            self.assertLessEqual(row["sourceBoundsHeaderMaxAbsDeltaMm"], 0.001)
            self.assertEqual(row["explicitSourceSide"], target["side"])
            self.assertTrue(row["lateralityNotInferredFromFjSuffixOrCoordinates"])
            self.assertEqual(row["canonicalLearnerIds"], [])
            self.assertFalse(row["learnerDefaultVisible"])
            self.assertFalse(row["humanAnatomyReviewed"])
            self.assertEqual(row["learnerPickState"], "source_only_unbound")

    def test_source_manifest_hashes_glb_and_official_page_mapping(self):
        manifest = self.manifest
        claimed = manifest["manifestSha256"]
        unhashed = dict(manifest)
        unhashed["manifestSha256"] = None
        canonical = json.dumps(unhashed, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(digest(canonical), claimed)
        self.assertEqual(manifest["source"]["officialMeshMetadataPage"], "https://dbarchive.biosciencedbc.jp/en/bodyparts3d/data-8.html")
        self.assertEqual(manifest["source"]["officialMeshMetadataDoi"], "10.18908/lsdba.nbdc00837-008")
        self.assertEqual(manifest["source"]["officialPartOfRelationMetadataPage"], "https://dbarchive.biosciencedbc.jp/en/bodyparts3d/data-6.html")
        self.assertEqual(manifest["source"]["officialPartOfRelationMetadataDoi"], "10.18908/lsdba.nbdc00837-006")
        self.assertEqual(manifest["source"]["archiveTree"], "PART-OF")
        glb_path = ROOT / manifest["sceneContract"]["integratedGlbLocalCachePath"]
        glb = glb_path.read_bytes()
        self.assertEqual(digest(glb), manifest["sceneContract"]["integratedGlbSha256"])
        gltf, binary = self.qa.unpack_glb(glb)
        self.assertEqual(len(gltf["nodes"]), 9)
        nodes_by_id = {node["name"].rsplit("-", 1)[-1]: node for node in gltf["nodes"]}
        self.assertEqual(set(nodes_by_id), set(EXPECTED))
        mesh_rows = {row["sourceElementFileId"]: row for row in manifest["meshRecords"]}
        asset_rows = {row["sourceElementFileId"]: row for row in manifest["sourceAssets"]}
        for fid, row in mesh_rows.items():
            self.assertEqual(gltf["nodes"][row["nodeIndex"]]["name"], f"HA-MESH-BP3D4-{fid}")
            self.assertEqual(self.qa.glb_position_hash(gltf, binary, row["meshIndex"]), asset_rows[fid]["transformedPositionFloat32Sha256"])

    def test_reuse_references_and_holds_are_not_promoted(self):
        refs = {row["sourceElementFileId"]: row for row in self.manifest["reuseOnlyReferences"]}
        self.assertEqual(set(refs), set(REUSE))
        for fid, task in REUSE.items():
            ref = refs[fid]
            self.assertTrue(ref["reuseOnly"])
            self.assertTrue(ref["mustNotReacquire"])
            self.assertEqual(ref["package"], task)
            self.assertEqual(digest((ROOT / ref["sourceManifestPath"]).read_bytes()), self.manifest["inputs"]["t52ReuseSourceManifestSha256"] if task == "T52" else self.manifest["inputs"]["t72ReuseSourceManifestSha256"])
        self.assertFalse(self.manifest["humanAnatomyReviewed"])
        self.assertFalse(self.manifest["rights"]["publicRelease"])
        self.assertIn("held", self.manifest["rights"]["redistributionStatus"])
        self.assertEqual(self.manifest["scope"]["wholeBodyCanonicalDenominator"], None)
        self.assertFalse(self.manifest["scope"]["fullSkullInventory"])
        self.assertEqual(self.validation["result"], "pass")
        self.assertFalse(self.validation["humanAnatomyReviewed"])
        self.assertFalse(self.validation["wholeSkullInventoryComplete"])
        self.assertFalse(self.validation["wholeBodyCoverageComplete"])

        integration_rows = [row for row in self.extension["assets"] if row.get("primaryPackage") == "T74"]
        self.assertEqual({row["sourceElementFileId"] for row in integration_rows}, set(EXPECTED))
        self.assertTrue(all(row["existingLearnerStableIds"] == [] and not row["learnerDefaultVisible"] and not row["humanAnatomyReviewed"] for row in integration_rows))
        self.assertEqual(self.extension["counts"]["newCanonicalBindings"], 0)
        self.assertEqual(self.extension["counts"]["newHumanReviewed"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
