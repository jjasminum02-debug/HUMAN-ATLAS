#!/usr/bin/env python3
"""T51 regression checks for the BodyParts3D source ingest pipeline."""

from __future__ import annotations

import importlib.util
import json
import shutil
import struct
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("t51_ingest", Path(__file__).with_name("ingest_bodyparts3d_r4.py"))
INGEST = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(INGEST)


class BodyParts3dR4IngestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "atlas-data/manifests/bodyparts3d-r4-source-manifest-t51.json").read_text())
        cls.files = {row["sourceElementFileId"]: row for row in cls.manifest["sourceElementFiles"]}

    def test_complete_source_ids_keep_fma_bp_fj_and_ha_namespaces_separate(self):
        counts = self.manifest["counts"]
        self.assertEqual(counts["sourceConceptRowsIS-A"], 2905)
        self.assertEqual(counts["sourceConceptRowsPART-OF"], 1368)
        self.assertEqual(counts["uniqueSourceFmaConceptIds"], 3432)
        self.assertEqual(counts["uniqueExpectedSourceElementFileIdsIS-A"], 2234)
        self.assertEqual(counts["uniqueExpectedSourceElementFileIdsPART-OF"], 1258)
        self.assertEqual(counts["sharedFileIdsAcrossTrees"], 1258)
        self.assertEqual(counts["uniqueExpectedSourceElementFileIdsAcrossTrees"], 2234)
        self.assertEqual(len(self.files), 2234)
        self.assertTrue(all(row["sourceElementFileId"].startswith("FJ") for row in self.files.values()))
        self.assertTrue(all(row["learnerIdentity"]["stableIds"] is not None for row in self.files.values()))
        self.assertTrue(all(row["sourceContextIndex"].startswith("sourceConcepts") for row in self.files.values()))

    def test_atomic_elements_are_deduplicated_across_compound_tree_references(self):
        row = self.files["FJ3360"]
        self.assertEqual(row["expectedInOfficialArchiveTrees"], ["IS-A", "PART-OF"])
        self.assertEqual(len(self.files), self.manifest["counts"]["uniqueExpectedSourceElementFileIdsAcrossTrees"])
        concept_rows = self.manifest["sourceConcepts"]
        referenced_ids = [file_id for concept in concept_rows for file_id in concept["elementFileIds"]]
        self.assertGreater(len(referenced_ids), len(set(referenced_ids)))
        self.assertEqual(len(set(referenced_ids)), 2234)

    def test_cache_preserves_source_bytes_and_side_without_mirroring(self):
        baseline = json.loads((ROOT / "work/evidence/T51/start-baseline.json").read_text())
        historical = json.loads((ROOT / "atlas-data/catalog/whole-body-inventory-t15g.json").read_text())
        self.assertEqual(INGEST.sha256_file(ROOT / "atlas-data/catalog/whole-body-inventory-t15g.json"), baseline["protectedRelevantInputHashes"]["atlas-data/catalog/whole-body-inventory-t15g.json"]["sha256"])
        self.assertEqual(self.manifest["t15gDrift"]["historicalWholeBodyIndividualMuscleCount"], historical["wholeBodyIndividualMuscleCount"])
        self.assertFalse(self.manifest["t15gDrift"]["historicalDenominatorFrozen"])
        self.assertIsNone(self.manifest["t15gDrift"]["historicalWholeBodyIndividualMuscleCount"])
        self.assertEqual(len(self.manifest["t15gDrift"]["historicalBoneStructureIds"]), 10)
        self.assertEqual(self.manifest["t15gDrift"]["currentCanonicalBoneCount"], 11)
        self.assertEqual(self.manifest["t15gDrift"]["addedCanonicalBoneIdsSinceHistoricalInventory"], ["HA-S-TALUS"])
        self.assertEqual(self.manifest["t15gDrift"]["historicalBoneIdsMissingFromCurrentCanonical"], [])
        for fma in ("FJ1394", "FJ1397", "FJ1439", "FJ3308", "FJ3387"):
            row = self.files[fma]
            self.assertEqual(row["cachedSource"]["status"], "acquired_cached_local")
            self.assertEqual(INGEST.sha256_file(ROOT / row["cachedSource"]["path"]), row["cachedSource"]["sha256"])
            self.assertEqual(row["laterality"], "right")
        self.assertFalse(any(row["laterality"] == "left" for row in self.files.values() if row["cachedSource"]["status"] == "acquired_cached_local"))

    def test_unmapped_and_not_attempted_are_distinct_from_download_failure(self):
        mapped_gap = self.files["FJ3385"]
        self.assertEqual(mapped_gap["cachedSource"]["status"], "acquired_cached_local")
        self.assertEqual(mapped_gap["learnerIdentity"]["mappingStatus"], "no_existing_HA_file_id_crosswalk")
        not_downloaded = next(row for row in self.files.values() if row["cachedSource"]["status"] == "not_acquired_download_not_attempted")
        self.assertEqual(not_downloaded["learnerIdentity"]["mappingStatus"], "no_existing_HA_file_id_crosswalk")
        self.assertFalse(not_downloaded["cachedSource"]["downloadFailure"])
        self.assertEqual(self.manifest["counts"]["downloadFailures"], 0)
        self.assertEqual(self.manifest["counts"]["notAcquiredAndNotAttempted"], 2214)

    def test_regions_have_separate_expected_acquired_converted_and_selectable_counts(self):
        chunks = ROOT / "atlas-data/manifests/bodyparts3d-r4-regions-t51"
        rows = {path.stem: json.loads(path.read_text()) for path in chunks.glob("*.json")}
        self.assertEqual(set(rows), {item["id"] for item in INGEST.PRODUCT_CATEGORIES})
        self.assertEqual(rows["leg"]["counts"]["expectedSourceMuscleConceptIds"], 42)
        self.assertEqual(rows["leg"]["counts"]["expectedSourceBoneConceptIds"], 4)
        self.assertEqual(rows["leg"]["counts"]["sourceRootExpectedSourceElementFileIdsUniqueWithinCategory"], 28)
        self.assertEqual(rows["leg"]["counts"]["existingProductBindingSourceElementFilesSupplement"], 2)
        self.assertEqual(rows["leg"]["counts"]["expectedSourceElementFileIdsUniqueWithinCategory"], 30)
        self.assertEqual(rows["leg"]["counts"]["acquiredCachedSourceElementFiles"], 9)
        self.assertEqual(rows["leg"]["counts"]["convertedCachedSourceElementFiles"], 9)
        self.assertEqual(rows["leg"]["counts"]["currentSelectableStableIds"], 6)
        self.assertEqual(rows["leg"]["counts"]["acquiredFilesBoundToCurrentlySelectableStableIds"], 7)
        supplement = set(rows["leg"]["existingProductBindingSourceFileIds"])
        self.assertEqual(supplement, {"FJ1394", "FJ1397"})
        self.assertEqual(rows["foot"]["counts"]["acquiredCachedSourceElementFiles"], 10)
        self.assertIsNone(rows["leg"]["counts"]["canonicalWholeBodyMuscleDenominatorContribution"])
        self.assertEqual(rows["leg"]["status"], "source_acquisition_candidates_plus_existing_bindings_no_membership_created")

    def test_sample_conversion_is_deterministic_and_frame_units_side_and_identity_are_explicit(self):
        cache = json.loads((ROOT / "work/evidence/T51/source-cache-file-inventory.json").read_text())["files"]
        with tempfile.TemporaryDirectory(prefix="t51-convert-a-") as a, tempfile.TemporaryDirectory(prefix="t51-convert-b-") as b:
            first = INGEST.converted_sample(ROOT, cache, Path(a) / "sample.glb")
            second = INGEST.converted_sample(ROOT, cache, Path(b) / "sample.glb")
            raw = (Path(a) / "sample.glb").read_bytes()
        self.assertEqual(first["sha256"], second["sha256"])
        self.assertEqual(first["meshCount"], 20)
        self.assertEqual(first["sidePolicy"], "preserve source laterality; no bilateral duplication or mirroring")
        self.assertEqual(first["lodPolicy"], "no decimation; no synthetic LOD; source resolution status remains unverified")
        self.assertEqual(INGEST.transform_vertex((1.0, 2.0, 3.0)), (0.001, 0.003, -0.002))
        self.assertEqual(INGEST.transform_normal((1.0, 2.0, 3.0)), (1.0, 3.0, -2.0))
        self.assertTrue(all(item["laterality"] == "right" for item in first["sourceIdentityOverlay"]))
        self.assertEqual(raw[:4], b"glTF")
        json_len, chunk_type = struct.unpack_from("<II", raw, 12)
        self.assertEqual(chunk_type, 0x4E4F534A)
        gltf = json.loads(raw[20:20 + json_len].decode("utf-8"))
        self.assertEqual(len(gltf["nodes"]), 20)
        self.assertEqual(gltf["nodes"][0]["extras"]["frame"], "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR")
        self.assertIn("sourceConceptId", gltf["nodes"][0]["extras"])
        self.assertIn("learnerStableIds", gltf["nodes"][0]["extras"])

    def test_source_metadata_inventory_rebuilds_byte_for_byte(self):
        with tempfile.TemporaryDirectory(prefix="t51-inventory-a-") as a, tempfile.TemporaryDirectory(prefix="t51-inventory-b-") as b:
            for output in (a, b):
                INGEST.build_inventory(ROOT, Path(output) / "source-manifest.json", Path(output) / "regions")
            self.assertEqual(INGEST.sha256_file(Path(a) / "source-manifest.json"), INGEST.sha256_file(Path(b) / "source-manifest.json"))
            for category in INGEST.PRODUCT_CATEGORIES:
                first = Path(a) / "regions" / f"{category['id']}.json"
                second = Path(b) / "regions" / f"{category['id']}.json"
                self.assertEqual(INGEST.sha256_file(first), INGEST.sha256_file(second))
        self.assertEqual(INGEST.validate_manifest(self.manifest), [])

    def test_explicit_local_obj_ingest_requires_official_ids_and_preserves_exact_bytes(self):
        source_row = next(row for row in json.loads((ROOT / "work/evidence/T51/source-cache-file-inventory.json").read_text())["files"] if row["sourceFileId"] == "FJ1439")
        source_obj = ROOT / source_row["sourceRelativePath"]
        with tempfile.TemporaryDirectory(prefix="t51-explicit-ingest-") as temporary:
            temp_root = Path(temporary)
            metadata = temp_root / "atlas-data/source-cache/bodyparts3d-r4/metadata"
            metadata.mkdir(parents=True)
            for filename in INGEST.METADATA_FILES.values():
                shutil.copyfile(ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata" / filename, metadata / filename)
            record = INGEST.ingest_obj_file(source_obj, temp_root)
            self.assertEqual(record["sourceFileId"], "FJ1439")
            self.assertEqual(record["acquisitionMethod"], "explicit_local_obj_import_no_network_request")
            self.assertFalse(record["downloadAttempt"])
            cached = temp_root / record["cacheRelativePath"]
            self.assertEqual(INGEST.sha256_file(cached), source_row["sha256"])
            index = INGEST.load_json(temp_root / "atlas-data/source-cache/bodyparts3d-r4/cache-index.json")
            self.assertEqual([row["sourceFileId"] for row in index["files"]], ["FJ1439"])
            self.assertIn("do not distribute", index["rightsBoundary"])
            INGEST.validate_cached_source_records(temp_root, index["files"])
            cached.write_bytes(b"corrupt test-only copy")
            with self.assertRaisesRegex(ValueError, "size/hash changed"):
                INGEST.validate_cached_source_records(temp_root, index["files"])

    def test_explicit_local_obj_ingest_rejects_unmapped_id_without_calling_it_download_failure(self):
        with tempfile.TemporaryDirectory(prefix="t51-ingest-reject-") as temporary:
            temp_root = Path(temporary)
            metadata = temp_root / "atlas-data/source-cache/bodyparts3d-r4/metadata"
            metadata.mkdir(parents=True)
            for filename in INGEST.METADATA_FILES.values():
                shutil.copyfile(ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata" / filename, metadata / filename)
            candidate = temp_root / "FJ999999.obj"
            candidate.write_text("# File ID: FJ999999\n# Representation ID: BP999999\n# Build-up logic: FMA 3.0 is_a\n# Concept ID: FMA999999\nv 0 0 0\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "mapping gap, not a download failure"):
                INGEST.ingest_obj_file(candidate, temp_root)
            self.assertFalse((temp_root / "atlas-data/source-cache/bodyparts3d-r4/mesh/ingested/FJ999999.obj").exists())
            self.assertFalse((temp_root / "atlas-data/source-cache/bodyparts3d-r4/cache-index.json").exists())

    def test_explicit_local_obj_ingest_rejects_valid_but_wrong_fma_pair_for_fj(self):
        source_row = next(row for row in json.loads((ROOT / "work/evidence/T51/source-cache-file-inventory.json").read_text())["files"] if row["sourceFileId"] == "FJ1439")
        source_obj = ROOT / source_row["sourceRelativePath"]
        original = source_obj.read_text(encoding="utf-8")
        mismatched = original.replace("# Concept ID : FMA22544", "# Concept ID : FMA22554").replace("# Representation ID : BP5018", "# Representation ID : BP5015")
        with tempfile.TemporaryDirectory(prefix="t51-ingest-crosswalk-reject-") as temporary:
            temp_root = Path(temporary)
            metadata = temp_root / "atlas-data/source-cache/bodyparts3d-r4/metadata"
            metadata.mkdir(parents=True)
            for filename in INGEST.METADATA_FILES.values():
                shutil.copyfile(ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata" / filename, metadata / filename)
            candidate = temp_root / "mismatched-header.obj"
            candidate.write_text(mismatched, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "FJ/FMA association"):
                INGEST.ingest_obj_file(candidate, temp_root)
            self.assertFalse((temp_root / "atlas-data/source-cache/bodyparts3d-r4/mesh/ingested/FJ1439.obj").exists())


if __name__ == "__main__":
    unittest.main()
