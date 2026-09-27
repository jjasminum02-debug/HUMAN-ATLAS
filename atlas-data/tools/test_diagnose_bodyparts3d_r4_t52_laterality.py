from __future__ import annotations

import tempfile
import json
import struct
import unittest
from pathlib import Path

from diagnose_bodyparts3d_r4_t52_laterality import (
    DiagnosticError,
    EXPECTED_FRAME,
    EXPECTED_TRANSFORM,
    bounds_center_side_diagnostic,
    clipped_triangle_area,
    compare_obj_to_glb_transform,
    expected_laterality_fraction,
    frame_contract_matches,
    find_official_bilateral_counterpart,
    parse_obj,
    sha256_file,
    source_frame_transform,
    source_identity_matches,
    validate_assessment,
)


class LateralityDiagnosticTests(unittest.TestCase):
    def test_frame_transform_preserves_x_side_and_converts_mm_to_m(self) -> None:
        self.assertEqual(source_frame_transform((10.0, -20.0, 30.0)), (0.01, 0.03, 0.02))
        self.assertGreater(source_frame_transform((10.0, 0.0, 0.0))[0], 0)
        self.assertLess(source_frame_transform((-10.0, 0.0, 0.0))[0], 0)

    def test_wrong_frame_and_sign_transform_are_rejected(self) -> None:
        self.assertTrue(frame_contract_matches(EXPECTED_FRAME, EXPECTED_TRANSFORM))
        self.assertFalse(frame_contract_matches(EXPECTED_FRAME, "[-x,z,y]m; mirrored"))
        self.assertFalse(frame_contract_matches("OpenSim", EXPECTED_TRANSFORM))

    def test_wrong_source_identity_is_rejected(self) -> None:
        expected = {"fileId": "FJ2742", "conceptId": "FMA46633", "representationId": "BP7915", "englishName": "Right middle pharyngeal constrictor"}
        self.assertTrue(source_identity_matches(expected, fj_id="FJ2742", fma_id="FMA46633", bp_id="BP7915", english_name="Right middle pharyngeal constrictor"))
        self.assertFalse(source_identity_matches(expected, fj_id="FJ2754", fma_id="FMA46633", bp_id="BP7915", english_name="Right middle pharyngeal constrictor"))
        self.assertFalse(source_identity_matches(expected, fj_id="FJ2742", fma_id="FMA46634", bp_id="BP7915", english_name="Right middle pharyngeal constrictor"))

    def test_surface_is_clipped_on_both_sides_not_rejected_for_aabb_crossing(self) -> None:
        tri = ((-1.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 2.0, 0.0))
        neg = clipped_triangle_area(tri, keep_positive=False)
        pos = clipped_triangle_area(tri, keep_positive=True)
        self.assertAlmostEqual(neg, 1.0)
        self.assertAlmostEqual(pos, 1.0)
        self.assertAlmostEqual(neg + pos, 2.0)

    def test_aabb_center_opposite_to_source_label_does_not_override_surface_distribution(self) -> None:
        obj = """v 1 0 0
v 4 0 0
v 1 4 0
v -8 0 0
v -4 0 0
v -8 0.2 0
f 1 2 3
f 4 5 6
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "center-opposes.obj"
            path.write_text(obj, encoding="utf-8")
            metrics = parse_obj(path)
        self.assertEqual(bounds_center_side_diagnostic(metrics), "negative_x")
        self.assertGreater(expected_laterality_fraction(metrics, "left"), 0.85)
        # The diagnostic reports independent observations; there is no automatic
        # error/review state attached to the AABB-center signal.

    def test_unlabeled_side_is_rejected_instead_of_defaulting_to_right(self) -> None:
        obj = """v -1 0 0
v -1 1 0
v -1 0 1
f 1 2 3
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "no-side.obj"
            path.write_text(obj, encoding="utf-8")
            metrics = parse_obj(path)
        with self.assertRaises(DiagnosticError):
            expected_laterality_fraction(metrics, "")
        with self.assertRaises(DiagnosticError):
            expected_laterality_fraction(metrics, None)  # type: ignore[arg-type]

    def test_direct_official_siblings_can_be_linked_without_geometry_mirroring(self) -> None:
        edges = [
            {"parentId": "FMA0", "parentName": "middle pharyngeal constrictor", "childId": "FMA1", "childName": "left middle pharyngeal constrictor"},
            {"parentId": "FMA0", "parentName": "middle pharyngeal constrictor", "childId": "FMA2", "childName": "right middle pharyngeal constrictor"},
        ]
        assets = {"FMA1": [{"sourceElementFileId": "FJ1", "sourceName": "Left middle pharyngeal constrictor"}], "FMA2": [{"sourceElementFileId": "FJ2", "sourceName": "Right middle pharyngeal constrictor"}]}
        elements = {"IS-A": [{"conceptId": "FMA2", "elementFileId": "FJ2"}], "PART-OF": []}
        relation = find_official_bilateral_counterpart("FMA1", "Left middle pharyngeal constrictor", edges, assets, elements)
        self.assertEqual(relation["status"], "official_source_index_opposite_side_relation_found")
        self.assertEqual(relation["concepts"][0]["counterpartFjElementIds"], ["FJ2"])
        self.assertEqual(relation["concepts"][0]["counterpartAssetsInT52FrozenPackage"], ["FJ2"])

    def test_assessment_must_cover_exact_ids_and_never_promote_human_review(self) -> None:
        good = {
            "revision": "T69-SOURCE-VS-GEOMETRY-ASSESSMENT-v1",
            "sources": [{"id": "official"}],
            "records": [{
                "sourceElementFileId": "FJ1", "aiConclusion": {"code": "observation", "text": "measured", "correctionAction": "none"},
                "unresolvedReason": None,
                "humanReview": {"status": "not_performed", "promoted": False},
                "learnerUse": {"status": "source_only_held", "canonicalBinding": None},
                "evidenceRefs": ["official"],
            }],
        }
        self.assertEqual(set(validate_assessment(good, {"FJ1"})), {"FJ1"})
        bad = {**good, "records": [{**good["records"][0], "humanReview": {"status": "reviewed", "promoted": True}}]}
        with self.assertRaises(DiagnosticError):
            validate_assessment(bad, {"FJ1"})
        with self.assertRaises(DiagnosticError):
            validate_assessment(good, {"FJ1", "FJ2"})

    def test_near_plane_and_multiple_components_are_observations(self) -> None:
        obj = """# File ID: FJ0001
# Representation ID: BP0001
# Concept ID: FMA0001
# English name: Left sample
# Bounds(mm): (-0.001000,0.000000,0.000000)-(5.000000,2.000000,1.000000)
v 0.0005 0 0
v 1 0 0
v 0 1 0
v 5 0 0
v 5 1 0
v 5 0 1
v 10 0 0
f 1 2 3
f 4 5 6
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.obj"
            path.write_text(obj, encoding="utf-8")
            metrics = parse_obj(path)
        self.assertEqual(metrics.vertex_count, 7)
        self.assertEqual(metrics.surface_vertex_count, 6)
        self.assertEqual(metrics.orphan_vertex_count, 1)
        self.assertEqual(metrics.orphan_positive_x_vertex_count, 1)
        self.assertEqual(metrics.triangle_count, 2)
        self.assertEqual(metrics.near_plane_vertex_count, 2)
        self.assertEqual(metrics.component_count, 2)
        self.assertTrue(metrics.bounds_min_mm[0] <= 0 <= metrics.bounds_max_mm[0])
        self.assertEqual(metrics.surface_bounds_max_mm[0], 5)
        self.assertGreater(metrics.positive_x_surface_area_mm2, 0)

    def test_actual_glb_position_accessor_is_checked_against_obj_transform_and_node_offset(self) -> None:
        def write_glb(path: Path, positions: list[tuple[float, float, float]], source_sha: str, *, translation=None) -> None:
            binary = b"".join(struct.pack("<3f", *position) for position in positions)
            document = {
                "asset": {"version": "2.0"},
                "scene": 0,
                "scenes": [{"nodes": [0]}],
                "nodes": [{
                    "name": "HA-MESH-BP3D4-FJ0001",
                    "mesh": 0,
                    "extras": {
                        "sourceFileId": "FJ0001", "sourceSha256": source_sha,
                        "sourceFrame": "native BodyParts3D R4 static reference; not registered to OpenSim",
                        "atlasFrame": EXPECTED_FRAME, "transform": EXPECTED_TRANSFORM,
                    },
                }],
                "meshes": [{"primitives": [{"attributes": {"POSITION": 0}, "mode": 4}]}],
                "accessors": [{"bufferView": 0, "componentType": 5126, "count": len(positions), "type": "VEC3"}],
                "bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": len(binary)}],
                "buffers": [{"byteLength": len(binary)}],
            }
            if translation is not None:
                document["nodes"][0]["translation"] = translation
            json_bytes = json.dumps(document, separators=(",", ":")).encode()
            json_bytes += b" " * ((4 - len(json_bytes) % 4) % 4)
            binary += b"\0" * ((4 - len(binary) % 4) % 4)
            total_length = 12 + 8 + len(json_bytes) + 8 + len(binary)
            path.write_bytes(
                struct.pack("<4sII", b"glTF", 2, total_length)
                + struct.pack("<II", len(json_bytes), 0x4E4F534A) + json_bytes
                + struct.pack("<II", len(binary), 0x004E4942) + binary
            )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            obj = root / "FJ0001.obj"
            obj.write_text("v 1000 2000 3000\nv -2000 4000 -5000\n", encoding="utf-8")
            source_sha = sha256_file(obj)
            good = root / "good.glb"
            write_glb(good, [(1.0, 3.0, -2.0), (-2.0, -5.0, -4.0)], source_sha)
            good_result = compare_obj_to_glb_transform(obj, good, "FJ0001", source_sha, sha256_file(good), {})
            self.assertTrue(good_result["passed"], good_result)
            self.assertEqual(good_result["maxAbsoluteVertexDeltaM"], 0.0)

            translated = root / "translated.glb"
            expected_vertices = [(1.0, 3.0, -2.0), (-2.0, -5.0, -4.0)]
            write_glb(translated, expected_vertices, source_sha, translation=[0.1, 0.0, 0.0])
            bad_result = compare_obj_to_glb_transform(obj, translated, "FJ0001", source_sha, sha256_file(translated), {})
            self.assertFalse(bad_result["passed"])
            self.assertFalse(bad_result["nodeTransformIdentity"])

            mirrored = root / "mirrored.glb"
            write_glb(mirrored, [(-1.0, 3.0, -2.0), (2.0, -5.0, -4.0)], source_sha)
            mirror_result = compare_obj_to_glb_transform(obj, mirrored, "FJ0001", source_sha, sha256_file(mirrored), {})
            self.assertFalse(mirror_result["passed"])
            self.assertTrue(mirror_result["nodeTransformIdentity"])
            self.assertGreater(mirror_result["maxAbsoluteVertexDeltaM"], 0.0)


if __name__ == "__main__":
    unittest.main()
