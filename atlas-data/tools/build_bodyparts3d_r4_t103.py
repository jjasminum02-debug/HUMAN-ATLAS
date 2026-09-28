#!/usr/bin/env python3
"""Build/check T103's ten exact R4 part meshes as one source-only scene extension."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import struct
import sys
import zlib
from pathlib import Path
from statistics import median
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / "work/evidence/T103/frozen-source-set.json"
ACQUISITION = ROOT / "work/evidence/T103/source-acquisition.json"
METADATA = ROOT / "atlas-data/source-cache/bodyparts3d-r4/metadata"
SOURCE_CACHE = ROOT / "atlas-data/source-cache/bodyparts3d-r4/mesh/t103"
DERIVED = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t103"
OUT = ROOT / "atlas-data/manifests/bodyparts3d-r4-t103"
SOURCE_MANIFEST = OUT / "source-manifest.json"
EXTENSION = OUT / "integration-extension.json"
EVIDENCE = ROOT / "work/evidence/T103/validation.json"
BROWSER_EVIDENCE = ROOT / "work/evidence/T103/browser-validation.json"
T77_MANIFEST = ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t77/manifest.json"
T95_OVERLAY = ROOT / "atlas-data/manifests/bodyparts3d-r4-t95/product-context-overlay.json"
T79_SOURCE = ROOT / "atlas-data/manifests/bodyparts3d-r4-t79/source-manifest.json"
T79_EXTENSION = ROOT / "atlas-data/manifests/bodyparts3d-r4-t79/integration-extension.json"
T101_SOURCE = ROOT / "atlas-data/manifests/bodyparts3d-r4-t101/source-manifest.json"
T101_EXTENSION = ROOT / "atlas-data/manifests/bodyparts3d-r4-t101/integration-extension.json"
T102_SOURCE = ROOT / "atlas-data/manifests/bodyparts3d-r4-t102/source-manifest.json"
T102_EXTENSION = ROOT / "atlas-data/manifests/bodyparts3d-r4-t102/integration-extension.json"
T54_SOURCE = ROOT / "atlas-data/manifests/bodyparts3d-r4-t54/source-manifest.json"
T54_RAW_DIR = ROOT / "atlas-data/source-cache/bodyparts3d-r4/mesh/t54"
T50_CONTRACT = ROOT / "work/evidence/T50/scene-contract.md"
T69_DIAGNOSTIC = ROOT / "work/evidence/T69/diagnostic.json"
T69_ASSESSMENT = ROOT / "work/evidence/T69/assessment.json"
FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
POSE = "bodyparts3d-r4-static-reference"
SOURCE_ID = "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0"
CHUNK_ID = "t103-upper-limb-muscle-parts"
EXPECTED = ["FJ1473", "FJ1473M", "FJ1474", "FJ1474M", "FJ1481", "FJ1481M", "FJ1514", "FJ1514M", "FJ1515", "FJ1515M"]
HOLDS = ["no_canonical_learner_binding", "human_anatomy_review_not_performed", "public_redistribution_held"]
MUTABLE_WORKFLOW_CONTEXT_HASHES = {"work/STATUS.md", "work/task-registry-r15.json"}
BOUNDS = re.compile(r"^#\s*Bounds\(mm\):\s*\(([^)]+)\)-\(([^)]+)\)\s*$")


class BuildError(RuntimeError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise BuildError(f"cannot import existing R4 parser/converter: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def parse_header_bounds(path: Path) -> tuple[str, list[float], str]:
    name = None
    bounds = None
    license_header = None
    with path.open("r", encoding="utf-8", errors="strict") as handle:
        for line in handle:
            if not line.startswith("#"):
                break
            if line.startswith("# English name :"):
                name = line.split(":", 1)[1].strip()
            match = BOUNDS.match(line.rstrip("\r\n"))
            if match:
                bounds = [float(value.strip()) for value in match.group(1).split(",") + match.group(2).split(",")]
            if "license for this database" in line.lower():
                license_header = line.lstrip("# ").strip()
    if not name or not bounds or len(bounds) != 6 or not license_header or not all(math.isfinite(v) for v in bounds):
        raise BuildError(f"OBJ exact name/bounds/license header missing or invalid: {path.name}")
    return name, bounds, license_header


def unpack_glb(raw: bytes) -> tuple[dict[str, Any], bytes]:
    if len(raw) < 28 or raw[:4] != b"glTF" or struct.unpack_from("<I", raw, 4)[0] != 2:
        raise BuildError("derived file is not a GLB 2.0 container")
    size, kind = struct.unpack_from("<II", raw, 12)
    if kind != 0x4E4F534A:
        raise BuildError("GLB JSON chunk missing")
    doc = json.loads(raw[20:20 + size].decode())
    offset = 20 + size
    binary_size, binary_kind = struct.unpack_from("<II", raw, offset)
    if binary_kind != 0x004E4942:
        raise BuildError("GLB BIN chunk missing")
    binary = raw[offset + 8:offset + 8 + binary_size]
    if len(binary) != binary_size:
        raise BuildError("GLB BIN chunk truncated")
    return doc, binary


def repack_glb(doc: dict[str, Any], binary: bytes) -> bytes:
    encoded = json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    encoded += b" " * (-len(encoded) % 4)
    binary += b"\0" * (-len(binary) % 4)
    total = 12 + 8 + len(encoded) + 8 + len(binary)
    return b"".join((struct.pack("<4sII", b"glTF", 2, total), struct.pack("<II", len(encoded), 0x4E4F534A), encoded,
                     struct.pack("<II", len(binary), 0x004E4942), binary))


def mesh_points(vertices: list[tuple[float, float, float]], triangles: list[tuple[int, int, int]]) -> list[tuple[float, float, float]]:
    points = list(vertices)
    for a, b, c in triangles:
        va, vb, vc = vertices[a], vertices[b], vertices[c]
        points.append(tuple((va[i] + vb[i] + vc[i]) / 3 for i in range(3)))
        points.append(tuple((va[i] + vb[i]) * 0.5 for i in range(3)))
        points.append(tuple((vb[i] + vc[i]) * 0.5 for i in range(3)))
        points.append(tuple((vc[i] + va[i]) * 0.5 for i in range(3)))
    return points


def point_triangle_distance_sq(p, a, b, c) -> float:
    # Closest point on a triangle (Ericson region tests), using original mesh triangles.
    ab = tuple(b[i] - a[i] for i in range(3)); ac = tuple(c[i] - a[i] for i in range(3)); ap = tuple(p[i] - a[i] for i in range(3))
    dot = lambda x, y: sum(x[i] * y[i] for i in range(3))
    d1, d2 = dot(ab, ap), dot(ac, ap)
    if d1 <= 0 and d2 <= 0: q = a
    else:
        bp = tuple(p[i] - b[i] for i in range(3)); d3, d4 = dot(ab, bp), dot(ac, bp)
        if d3 >= 0 and d4 <= d3: q = b
        else:
            vc = d1 * d4 - d3 * d2
            if vc <= 0 and d1 >= 0 and d3 <= 0:
                v = d1 / (d1 - d3); q = tuple(a[i] + v * ab[i] for i in range(3))
            else:
                cp = tuple(p[i] - c[i] for i in range(3)); d5, d6 = dot(ab, cp), dot(ac, cp)
                if d6 >= 0 and d5 <= d6: q = c
                else:
                    vb = d5 * d2 - d1 * d6
                    if vb <= 0 and d2 >= 0 and d6 <= 0:
                        w = d2 / (d2 - d6); q = tuple(a[i] + w * ac[i] for i in range(3))
                    else:
                        va = d3 * d6 - d5 * d4
                        if va <= 0 and (d4 - d3) >= 0 and (d5 - d6) >= 0:
                            w = (d4 - d3) / ((d4 - d3) + (d5 - d6)); q = tuple(b[i] + w * (c[i] - b[i]) for i in range(3))
                        else:
                            denom = 1 / (va + vb + vc); v, w = vb * denom, vc * denom
                            q = tuple(a[i] + ab[i] * v + ac[i] * w for i in range(3))
    return sum((p[i] - q[i]) ** 2 for i in range(3))


class TriangleBvh:
    """Small exact-triangle nearest-distance index; boxes only prune, never assert overlap."""
    def __init__(self, vertices, triangles, leaf_size=12):
        self.vertices, self.triangles, self.leaf_size = vertices, triangles, leaf_size
        self.root = self._build(list(range(len(triangles))))

    def _build(self, ids):
        tri_points = [[self.vertices[index] for index in self.triangles[tid]] for tid in ids]
        lo = tuple(min(p[axis] for tri in tri_points for p in tri) for axis in range(3))
        hi = tuple(max(p[axis] for tri in tri_points for p in tri) for axis in range(3))
        if len(ids) <= self.leaf_size:
            return (lo, hi, ids, None, None)
        centers = {tid: tuple(sum(self.vertices[v][axis] for v in self.triangles[tid]) / 3 for axis in range(3)) for tid in ids}
        axis = max(range(3), key=lambda a: max(centers[i][a] for i in ids) - min(centers[i][a] for i in ids))
        ids.sort(key=lambda i: centers[i][axis]); mid = len(ids) // 2
        return (lo, hi, None, self._build(ids[:mid]), self._build(ids[mid:]))

    @staticmethod
    def _box_sq(p, lo, hi):
        return sum((lo[i] - p[i]) ** 2 if p[i] < lo[i] else (p[i] - hi[i]) ** 2 if p[i] > hi[i] else 0.0 for i in range(3))

    def distance_sq(self, p):
        best = float("inf")
        stack = [self.root]
        while stack:
            node = stack.pop(); lo, hi, ids, left, right = node
            if self._box_sq(p, lo, hi) > best: continue
            if ids is not None:
                for tid in ids:
                    a, b, c = (self.vertices[i] for i in self.triangles[tid])
                    best = min(best, point_triangle_distance_sq(p, a, b, c))
            else:
                children = [left, right]
                children.sort(key=lambda n: self._box_sq(p, n[0], n[1]), reverse=True)
                stack.extend(children)
        return math.sqrt(best)


def surface_distance_summary(source_vertices, source_triangles, target_vertices, target_triangles) -> dict[str, Any]:
    bvh = TriangleBvh(target_vertices, target_triangles)
    distances = sorted(bvh.distance_sq(point) ** 0.5 for point in mesh_points(source_vertices, source_triangles))
    count = len(distances)
    def percentile(q: float) -> float:
        return distances[min(count - 1, round((count - 1) * q))]
    return {"sampleMethod": "every_source_vertex_plus_each_triangle_centroid_and_edge_midpoint; exact point-to-target-triangle nearest distance; bidirectional calls are reported separately",
            "sourceSurfaceSampleCount": count, "targetTriangleCount": len(target_triangles),
            "nearestDistanceMm": distances[0], "medianDistanceMm": median(distances), "p95DistanceMm": percentile(0.95),
            "maximumSampleDistanceMm": distances[-1],
            "sampleFractionsWithinMm": {str(t): sum(distance <= t for distance in distances) / count for t in (0.1, 0.5, 1.0, 2.0)},
            "continuousIntersectionProven": False, "aabbUsedAsOverlapProof": False}


def write_owned(path: Path, raw: bytes, owner: str, frozen_hash: str) -> None:
    if path.exists() and path.read_bytes() != raw:
        try: old = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): old = {}
        if old.get("task") != owner or old.get("frozenSourceSetSha256") != frozen_hash:
            raise BuildError(f"refusing to overwrite unowned/differently frozen output: {path.relative_to(ROOT)}")
    path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)


def load_inputs() -> dict[str, Any]:
    if not FREEZE.is_file() or not ACQUISITION.is_file(): raise BuildError("T103 exact source freeze and acquisition receipt are required")
    freeze_raw, acquisition_raw = FREEZE.read_bytes(), ACQUISITION.read_bytes()
    frozen, acquisition = json.loads(freeze_raw), json.loads(acquisition_raw)
    if frozen.get("task") != "T103" or frozen.get("status") != "frozen_before_mesh_acquisition" or frozen.get("sourceElementFileIds") != EXPECTED:
        raise BuildError("T103 frozen source IDs/status differ from the exact task")
    if acquisition.get("task") != "T103" or acquisition.get("result") != "pass" or acquisition.get("fullArchivesDownloaded") is not False or acquisition.get("completeSourceFileCount") != len(EXPECTED):
        raise BuildError("T103 acquisition receipt is incomplete or indicates full-archive retrieval")
    if acquisition.get("frozenSourceSetSha256") != sha(freeze_raw) or acquisition.get("frozenMembershipSha256") != frozen.get("frozenMembershipSha256"):
        raise BuildError("T103 acquisition is bound to a different exact freeze")
    acquired = acquisition.get("selectedSourceFiles", [])
    if [row.get("sourceElementFileId") for row in acquired] != EXPECTED: raise BuildError("T103 acquired member sequence differs from exact frozen IDs")
    if len({row.get("sourceElementFileId") for row in acquired}) != len(EXPECTED): raise BuildError("T103 acquisition has duplicate members")

    input_hashes = dict(frozen.get("inputSha256", {}))
    parent_paths = [T77_MANIFEST, T95_OVERLAY, T79_SOURCE, T79_EXTENSION, T101_SOURCE, T101_EXTENSION, T102_SOURCE, T102_EXTENSION,
                    T50_CONTRACT, T69_DIAGNOSTIC, T69_ASSESSMENT, T54_SOURCE]
    for path in parent_paths:
        if not path.is_file(): raise BuildError(f"required scene/frame/representation input missing: {path.relative_to(ROOT)}")
        input_hashes[path.relative_to(ROOT).as_posix()] = sha(path.read_bytes())
    for rel, expected in frozen.get("inputSha256", {}).items():
        path = ROOT / rel
        if rel in MUTABLE_WORKFLOW_CONTEXT_HASHES:
            if not path.is_file(): raise BuildError(f"historical workflow context input missing: {rel}")
            continue
        if not path.is_file() or sha(path.read_bytes()) != expected: raise BuildError(f"frozen T103 input hash changed: {rel}")

    ingest = load_module("ha_t103_ingest", ROOT / "atlas-data/tools/ingest_bodyparts3d_r4.py")
    converter = load_module("ha_t103_converter", ROOT / "atlas-data/tools/convert_bodyparts3d_obj_to_glb.py")
    tables = ingest.load_tables(METADATA)
    metadata_hashes = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in sorted(METADATA.glob("*.txt"))}
    raw_files = {path: path.read_bytes() for path in [T77_MANIFEST, T95_OVERLAY, T79_SOURCE, T79_EXTENSION, T101_SOURCE, T101_EXTENSION, T102_SOURCE, T102_EXTENSION, T54_SOURCE]}
    raw_files[T50_CONTRACT] = T50_CONTRACT.read_bytes(); raw_files[T69_DIAGNOSTIC] = T69_DIAGNOSTIC.read_bytes(); raw_files[T69_ASSESSMENT] = T69_ASSESSMENT.read_bytes()
    return {"frozen": frozen, "freezeRaw": freeze_raw, "acquisition": acquisition, "acquisitionRaw": acquisition_raw,
            "acquired": acquired, "inputHashes": input_hashes, "metadataHashes": metadata_hashes, "tables": tables,
            "ingest": ingest, "converter": converter, "rawFiles": raw_files}


def verify_parent_chain(data: dict[str, Any]) -> dict[str, Any]:
    get = lambda path: json.loads(data["rawFiles"][path])
    t77_raw = data["rawFiles"][T77_MANIFEST]; overlay_raw = data["rawFiles"][T95_OVERLAY]
    t79_raw = data["rawFiles"][T79_SOURCE]; t79_ext_raw = data["rawFiles"][T79_EXTENSION]
    t101_raw = data["rawFiles"][T101_SOURCE]; t101_ext_raw = data["rawFiles"][T101_EXTENSION]
    t102_raw = data["rawFiles"][T102_SOURCE]; t102_ext_raw = data["rawFiles"][T102_EXTENSION]
    base, overlay, t79, t101, t102 = map(json.loads, [t77_raw, overlay_raw, t79_ext_raw, t101_ext_raw, t102_ext_raw])
    t79_source, t101_source, t102_source = map(json.loads, [t79_raw, t101_raw, t102_raw])
    if overlay.get("sourceManifestSha256") != sha(t77_raw): raise BuildError("T95 overlay is detached from exact T77 scene manifest")
    if t79.get("parentSourceManifestSha256") != sha(t77_raw) or t79.get("parentProductContextOverlaySha256") != sha(overlay_raw) or t79.get("sourceManifestSha256") != sha(t79_raw) or t79_source.get("task") != "T79":
        raise BuildError("T79 source/extension chain is invalid")
    if t101.get("parentSourceManifestSha256") != sha(t77_raw) or t101.get("parentProductContextOverlaySha256") != sha(overlay_raw) or t101.get("parentT79SourceManifestSha256") != sha(t79_raw) or t101.get("parentT79IntegrationExtensionSha256") != sha(t79_ext_raw) or t101.get("sourceManifestSha256") != sha(t101_raw) or t101_source.get("task") != "T101":
        raise BuildError("T101 source/extension chain is invalid")
    if t102.get("parentSourceManifestSha256") != sha(t77_raw) or t102.get("parentProductContextOverlaySha256") != sha(overlay_raw) or t102.get("parentT79SourceManifestSha256") != sha(t79_raw) or t102.get("parentT79IntegrationExtensionSha256") != sha(t79_ext_raw) or t102.get("parentT101SourceManifestSha256") != sha(t101_raw) or t102.get("parentT101IntegrationExtensionSha256") != sha(t101_ext_raw) or t102.get("sourceManifestSha256") != sha(t102_raw) or t102_source.get("task") != "T102":
        raise BuildError("T102 source/extension chain is invalid")
    return {"t77": base, "t95": overlay, "t79Source": t79_source, "t79Extension": t79,
            "t101Source": t101_source, "t101Extension": t101, "t102Source": t102_source, "t102Extension": t102}


def convert() -> dict[str, Any]:
    data = load_inputs(); chain = verify_parent_chain(data)
    frozen_by_id = {row["sourceElementFileId"]: row for row in data["frozen"]["sourceMappings"]}
    acquired_by_id = {row["sourceElementFileId"]: row for row in data["acquired"]}
    tables, ingest, converter = data["tables"], data["ingest"], data["converter"]
    concepts = {tuple(row) for row in tables["isaConcepts"]}
    elements = {tuple(row) for row in tables["isaCompoundElements"]}
    inclusions = {tuple(row) for row in tables["isaInclusion"]}
    source_assets, identity_extras, mesh_inputs, parsed_meshes = [], [], [], {}
    for fid in EXPECTED:
        mapping, acquired = frozen_by_id[fid], acquired_by_id[fid]
        path = ROOT / acquired["cacheRelativePath"]
        if not path.is_file(): raise BuildError(f"exact selected OBJ is missing: {fid}")
        raw = path.read_bytes()
        if len(raw) != acquired.get("bytes") or sha(raw) != acquired.get("sha256"): raise BuildError(f"OBJ byte count/SHA mismatch: {fid}")
        crc = f"{zlib.crc32(raw) & 0xffffffff:08x}"
        if crc != acquired.get("crc32"): raise BuildError(f"selected archive member CRC32 mismatch: {fid}")
        header = ingest.read_obj_header(path); ingest.validate_obj_source_identity(header, tables)
        name, header_bounds, license_header = parse_header_bounds(path)
        exact_concept = tuple(mapping["officialConceptRow"])
        exact_element = tuple(mapping["officialExactElementRow"])
        generic_element = tuple(mapping["officialGenericPartElementRow"])
        parent_relation = tuple(mapping["officialParentRelationRow"])
        if exact_concept not in concepts or exact_element not in elements or generic_element not in elements or parent_relation not in inclusions:
            raise BuildError(f"frozen official FMA/BP/ELEMENT/IS-A row absent: {fid}")
        if tuple(mapping["officialConceptRow"])[0] != header.get("conceptId") or tuple(mapping["officialConceptRow"])[1] != header.get("representationId") or tuple(mapping["officialExactElementRow"])[2] != fid:
            raise BuildError(f"OBJ header FJ/FMA/BP identity disagrees with frozen official rows: {fid}")
        if (header.get("fileId"), header.get("conceptId"), header.get("representationId"), header.get("buildUpLogic")) != (fid, mapping["sourceConceptId"], mapping["sourceRepresentationId"], "FMA 3.0 is_a"):
            raise BuildError(f"OBJ header file/tree/FMA/BP differs from exact freeze: {fid}")
        if name.casefold() != exact_element[1].casefold():
            raise BuildError(f"OBJ English header does not match the exact side-specific element row: {fid}")
        side = mapping["sideFromExactOfficialName"]
        if side not in ("right", "left") or side not in name.casefold() or mapping["sideEvidence"].get("notInferredFromFjSuffixOrBounds") is not True:
            raise BuildError(f"laterality is not supported by exact named source row: {fid}")
        vertices, normals, triangles = converter.parse_obj(path)
        if not vertices or not triangles: raise BuildError(f"OBJ has no renderable triangle surface: {fid}")
        actual_bounds = [min(v[i] for v in vertices) for i in range(3)] + [max(v[i] for v in vertices) for i in range(3)]
        max_delta = max(abs(header_bounds[i] - actual_bounds[i]) for i in range(6))
        # R4's human-readable header rounds differently from several actual OBJ vertices.
        # Preserve both values and fail only beyond the 0.11 mm range observed/allowed for this profile.
        if max_delta > 0.11: raise BuildError(f"OBJ Bounds(mm) header and actual vertices diverge >0.11mm: {fid}")
        # Coordinate sign is a sanity check only after side was established by official exact labels.
        sign_consistent = max(v[0] for v in vertices) < 0 if side == "right" else min(v[0] for v in vertices) > 0
        if not sign_consistent: raise BuildError(f"actual source X sign contradicts exact side under T50/T69; no mirroring/relabel: {fid}")
        transformed = [converter.transform_vertex(v) for v in vertices]
        project_bounds = [[min(point[axis] for point in transformed) for axis in range(3)],
                          [max(point[axis] for point in transformed) for axis in range(3)]]
        geometry = {"sourceVertexCount": len(vertices), "sourceNormalCount": len(normals), "sourceTriangleCount": len(triangles),
                    "sourceHeaderBoundsMm": header_bounds, "sourceActualVertexBoundsMm": actual_bounds,
                    "headerActualMaxDeltaMm": max_delta, "projectBoundsM": project_bounds,
                    "sideXAxisSanityCheckOnly": {"exactNamedSourceSide": side, "consistent": sign_consistent}}
        identity = {"sourceElementFileId": fid, "sourceConceptId": header["conceptId"], "sourceRepresentationId": header["representationId"],
                    "sourceConceptEnglishName": mapping["sourceNameEnglish"], "sourceObjEnglishHeader": name,
                    "sourceSide": side, "sourceSideEvidence": mapping["sideEvidence"],
                    "sourceUnit": "mm_from_exact_OBJ_Bounds_header", "projectUnit": "m", "projectFrame": FRAME,
                    "sourcePose": POSE, "transform": mapping["transform"], "humanAnatomyReviewed": False, "publicRedistribution": "held"}
        source_assets.append({**identity, "sourceArchiveTree": "IS-A", "sourceArchiveMemberPath": acquired["memberPath"],
                              "archiveMemberCrc32": acquired["crc32"], "sourceBytes": len(raw), "sourceSha256": acquired["sha256"],
                              "sourceHeader": {"fileId": header["fileId"], "conceptId": header["conceptId"], "representationId": header["representationId"],
                                               "buildUpLogic": header["buildUpLogic"], "englishNameExact": name, "boundsHeaderUnit": "mm",
                                               "boundsHeaderMm": header_bounds, "legacyLicenseHeaderExact": license_header},
                              "officialConceptRow": list(exact_concept), "officialSideSpecificElementRow": list(exact_element),
                              "officialGenericPartElementRowSameFj": list(generic_element), "officialGenericToSideRelationRow": list(parent_relation),
                              "allOfficialSemanticRowsForSameFj": mapping["allOfficialElementRowsForSameFj"],
                              "oneFjOneNodePolicy": True, "geometry": geometry})
        identity_extras.append(identity)
        parsed_meshes[fid] = (vertices, triangles)
        mesh_inputs.append({"file_id": fid, "source_path": path, "source_relative_path": acquired["cacheRelativePath"], "source_sha256": acquired["sha256"],
                            "asset": {"bytes": len(raw), "vertex_count": len(vertices), "polygon_count": len(triangles),
                                      "concept_id": header["conceptId"], "representation_id": header["representationId"]}})

    # Confirm no duplicate FJ/node already exists in the active T77→T102 chain.
    parent_assets = [asset for chunk in chain["t77"]["chunks"] for asset in chunk["assets"]]
    for key in ("t79Extension", "t101Extension", "t102Extension"):
        parent_assets.extend(asset for chunk in chain[key]["chunks"] for asset in chunk["assets"])
    parent_ids = [asset["id"] for asset in parent_assets]
    parent_nodes = [asset["nodeId"] for asset in parent_assets]
    if len(parent_ids) != len(set(parent_ids)) or len(parent_nodes) != len(set(parent_nodes)): raise BuildError("parent scene already contains duplicate IDs or nodes")
    if set(EXPECTED) & set(parent_ids): raise BuildError("T103 exact FJ is already in active parent; duplicate rendering refused")
    t54 = json.loads(data["rawFiles"][T54_SOURCE])
    t54_assets = {row["sourceElementFileId"]: row for row in t54.get("sourceAssets", []) if row.get("sourceElementFileId") in {"FJ1469", "FJ1469M"}}
    active_parent = {asset["id"]: asset for asset in parent_assets}
    parent_policy = []
    surface_comparisons = []
    for parent_fid in ("FJ1469", "FJ1469M"):
        prior = t54_assets.get(parent_fid); runtime = active_parent.get(parent_fid)
        if not prior or not runtime or runtime.get("defaultVisible") is not False or runtime.get("pickState") != "held" or "T54_source_label_surface_pair_conflict" not in runtime.get("holdReasons", []):
            raise BuildError(f"T54 flexor-pollicis-brevis parent must remain held/hidden without edits: {parent_fid}")
        path = T54_RAW_DIR / f"{parent_fid}.obj"
        if not path.is_file() or sha(path.read_bytes()) != prior.get("sourceSha256"): raise BuildError(f"T54 original parent bytes changed/missing: {parent_fid}")
        p_vertices, _, p_triangles = converter.parse_obj(path)
        parent_label = prior.get("sourceName")
        parent_policy.append({"sourceElementFileId": parent_fid, "sourceSha256": prior["sourceSha256"], "sourceNameExact": parent_label,
                              "sourceHeaderSide": prior.get("lateralityFromExactSourceHeader"),
                              "sourceXBoundsMm": prior.get("lateralitySurfaceDiagnostic", {}).get("xBoundsMm"),
                              "activeParentDefaultVisible": runtime.get("defaultVisible"), "activeParentPickState": runtime.get("pickState"),
                              "activeParentHoldReasons": runtime.get("holdReasons"), "preserved": True})
        for part_fid in ("FJ1514", "FJ1514M"):
            c_vertices, c_triangles = parsed_meshes[part_fid]
            # Bounds here only validate scale/frame plausibility; the comparison itself measures points to the actual target triangles.
            p_to_c = surface_distance_summary(p_vertices, p_triangles, c_vertices, c_triangles)
            c_to_p = surface_distance_summary(c_vertices, c_triangles, p_vertices, p_triangles)
            surface_comparisons.append({"parentWholeCandidateFj": parent_fid, "parentHeaderName": parent_label,
                                        "partHeadFj": part_fid, "partHeaderName": frozen_by_id[part_fid]["sourceNameEnglish"],
                                        "parentSourceIdentityConflictRetained": True,
                                        "parentToPartSurfaceSamples": p_to_c, "partToParentSurfaceSamples": c_to_p,
                                        "pairwiseSameSourceXSide": "same" if (max(v[0] for v in p_vertices) < 0) == (max(v[0] for v in c_vertices) < 0) else "opposite",
                                        "interpretation": "sampled distances use actual mesh triangles; they estimate near-surface overlap but do not prove continuous surface intersection. Held whole candidates remain hidden regardless."})

    # Record exact metadata concept/member candidates. Do not emit enclosing FMA ancestors as surfaces.
    by_fma = {row[0]: row for row in tables["isaConcepts"]}
    element_fjs: dict[str, set[str]] = {}
    for fma, _name, fj in tables["isaCompoundElements"]: element_fjs.setdefault(fma, set()).add(fj)
    whole_candidates = []
    for fma, name in [("FMA37378", "flexor pollicis brevis")]:
        concept = by_fma.get(fma)
        whole_candidates.append({"fma": fma, "name": name, "officialConceptRow": concept,
                                 "memberFjs": sorted(element_fjs.get(fma, set())),
                                 "activeParentSceneFjs": sorted(set(element_fjs.get(fma, set())) & set(parent_ids)),
                                 "activeParentState": {fid: {"defaultVisible": active_parent[fid].get("defaultVisible"), "pickState": active_parent[fid].get("pickState"), "holdReasons": active_parent[fid].get("holdReasons")}
                                                       for fid in sorted(set(element_fjs.get(fma, set())) & set(active_parent))}})
    no_exact_whole = []
    for fma, name in [("FMA38615", "humeral head of flexor carpi ulnaris"), ("FMA38558", "humeral head of pronator teres"),
                      ("FMA46119", "oblique head of adductor pollicis"), ("FMA46120", "transverse head of adductor pollicis")]:
        no_exact_whole.append({"targetGenericPartFma": fma, "targetName": name,
                               "sourceRows": sorted([list(row) for row in tables["isaCompoundElements"] if row[0] == fma]),
                               "result": "R4 source rows identify this part/head; no separate exact whole-muscle concept/member row was found for this named target set; ancestor concept rows are not used as replacements"})

    converter.MODEL_ID = "HA-MODEL-BP3D4-T103-UPPER-LIMB-PARTS-SOURCE"
    glb, mesh_records = converter.build_glb(mesh_inputs)
    gltf, binary = unpack_glb(glb)
    if len(gltf.get("scenes", [])) != 1 or len(gltf.get("nodes", [])) != len(EXPECTED) or len(gltf.get("meshes", [])) != len(EXPECTED): raise BuildError("converter output is not one static node/mesh per exact T103 FJ")
    if gltf.get("animations") or gltf.get("skins") or gltf.get("images"): raise BuildError("static T103 surfaces unexpectedly contain animation/skin/image payload")
    for i, identity in enumerate(identity_extras):
        gltf["nodes"][i].setdefault("extras", {}).update(identity); gltf["meshes"][i].setdefault("extras", {}).update(identity)
    gltf["asset"]["generator"] = "HUMAN ATLAS T103; existing BodyParts3D R4 OBJ-to-GLB converter; static source surfaces"
    glb = repack_glb(gltf, binary)
    glb_path = DERIVED / f"{CHUNK_ID}.glb"
    cache_manifest_path = DERIVED / "manifest.json"
    if glb_path.exists() and glb_path.read_bytes() != glb:
        if not cache_manifest_path.is_file() or json.loads(cache_manifest_path.read_text()).get("task") != "T103": raise BuildError("refusing to overwrite an unowned T103 ignored cache asset")

    runtime_assets = []
    records = {row["sourceFileId"]: row for row in mesh_records}
    by_source = {row["sourceElementFileId"]: row for row in source_assets}
    for fid in EXPECTED:
        source, record = by_source[fid], records[fid]
        bounds = [record["atlasBoundsM"]["min"], record["atlasBoundsM"]["max"]]
        local_display = {"beforeDefaultVisible": False, "afterDefaultVisible": True, "state": "allowed", "sourceSha256": source["sourceSha256"],
                         "integrityHolds": [], "evidenceIds": ["work/evidence/T103/source-acquisition.json", "atlas-data/manifests/bodyparts3d-r4-t103/source-manifest.json", "work/evidence/T103/browser-validation.json"],
                         "retainedHoldReasons": HOLDS, "bindingState": "source_only_unbound", "publicRedistribution": "held", "humanReviewed": False,
                         "basis": "verified_local_source_context_only"}
        runtime_assets.append({"id": fid, "nodeId": f"HA-MESH-BP3D4-{fid}", "sourceSha256": source["sourceSha256"], "regions": ["upper-limb"],
                               "primaryOwner": "upper-limb", "side": source["sourceSide"], "layer": "muscle", "defaultVisible": True, "supplement": False,
                               "pickState": "source_only_unbound", "stableIds": [], "holdReasons": HOLDS, "humanReviewed": False, "bounds": bounds,
                               "localDisplay": local_display, "publicRedistribution": "held", "sourcePackage": "T103",
                               "sourceConceptIdObservation": source["sourceConceptId"], "sourceRepresentationIdObservation": source["sourceRepresentationId"],
                               "sourceNameObservation": source["sourceConceptEnglishName"], "sourceGeometrySha256": record["geometrySha256"],
                               "sourceTopologySha256": record["topologySha256"]})
    chunk = {"id": CHUNK_ID, "url": f"/__atlas/body/{CHUNK_ID}.glb", "sha256": sha(glb), "bytes": len(glb), "assets": runtime_assets}
    scene_contract = {"projectFrame": FRAME, "projectUnit": "m", "sourceId": SOURCE_ID, "pose": POSE,
                     "transform": "[x,y,z] source mm -> [x,z,-y] HUMAN ATLAS m; preserve x sign; no mirror/recenter",
                     "oneAnatomySceneRoot": True, "oneRenderer": True, "cameraOwner": "existing AnatomySceneController",
                     "extensionMode": "append T103 exact source-only meshes after the T102 extension in the same T77/T95/T79/T101/T102 scene"}
    source_manifest = {"revision": "BodyParts3D-R4-T103-SOURCE-MANIFEST-v1", "task": "T103",
                       "frozenSourceSetSha256": sha(data["freezeRaw"]), "frozenMembershipSha256": data["frozen"]["frozenMembershipSha256"],
                       "source": {"sourceId": SOURCE_ID, "version": "BodyParts3D Release 4.0", "tree": "IS-A",
                                  "archiveUrl": data["acquisition"]["selectedSourceFiles"][0]["archiveUrl"],
                                  "archiveEtag": data["acquisition"]["selectedSourceFiles"][0]["archiveEtag"],
                                  "fullArchiveDownloaded": False, "selectedMemberRangeTransferBytes": data["acquisition"]["rangeTransferBytes"]},
                       "sceneContract": scene_contract,
                       "inputs": {"frozenSourceSetSha256": sha(data["freezeRaw"]), "sourceAcquisitionSha256": sha(data["acquisitionRaw"]),
                                  **data["inputHashes"], **data["metadataHashes"]},
                       "rights": {"localDisplay": "allowed only for this exact technical subset after item identity, frame, GLB, duplicate-node and actual-browser validation",
                                  "publicRedistribution": "held; exact OBJ headers state CC BY-SA 2.1 Japan; no file-level/current-terms reconciliation or approval is claimed",
                                  "humanAnatomyReview": "not_performed"},
                       "sourceOnlyPolicy": {"canonicalLearnerBinding": "none", "learnerPickable": False, "humanReviewed": False,
                                            "threeNameOverlay": "deferred to the later target batch; no canonical ID or learner label created"},
                       "wholeMusclePartRepresentation": {"exactWholeMuscleCandidates": whole_candidates,
                           "noExactWholeCandidatesForOtherTargetFamilies": no_exact_whole,
                           "T54FlexorPollicisBrevisParents": parent_policy, "actualTriangleSurfaceSampleComparisons": surface_comparisons,
                           "sameFjSemanticRowsPolicy": "an exact FJ is a source mesh identity; generic-head and side-specific semantic rows reusing one FJ produce one node only",
                           "productRepresentationPolicy": "T103 contributes only its ten distinct head/part FJs. T54 whole-FPB candidates remain hidden and held because their exact source labels conflict with frame laterality. The T103 superficial-head surfaces can therefore never co-render with those held whole candidates in the default scene. No T54 source/manifests are changed. Surface comparisons use actual parent/part triangles and bidirectional mesh vertex/triangle-centroid/edge-midpoint samples; distance fractions are evidence about sampled proximity only, not proof of continuous intersection. AABB is not used to infer overlap.",
                           "ancestorOnlyBindingOrSurface": "none"},
                       "sourceAssets": source_assets, "meshRecords": mesh_records,
                       "derivedChunk": {"id": CHUNK_ID, "path": f"atlas-data/source-cache/bodyparts3d-r4/converted/t103/{CHUNK_ID}.glb", "sha256": sha(glb), "bytes": len(glb), "nodeCount": len(EXPECTED)}}
    source_raw = json_bytes(source_manifest)
    extension = {"revision": "BodyParts3D-R4-T103-SAME-SCENE-EXTENSION-v1", "task": "T103", "frozenSourceSetSha256": sha(data["freezeRaw"]),
                 "parentSourceManifestPath": T77_MANIFEST.relative_to(ROOT).as_posix(), "parentSourceManifestSha256": sha(data["rawFiles"][T77_MANIFEST]),
                 "parentProductContextOverlayPath": T95_OVERLAY.relative_to(ROOT).as_posix(), "parentProductContextOverlaySha256": sha(data["rawFiles"][T95_OVERLAY]),
                 "parentT79SourceManifestPath": T79_SOURCE.relative_to(ROOT).as_posix(), "parentT79SourceManifestSha256": sha(data["rawFiles"][T79_SOURCE]),
                 "parentT79IntegrationExtensionPath": T79_EXTENSION.relative_to(ROOT).as_posix(), "parentT79IntegrationExtensionSha256": sha(data["rawFiles"][T79_EXTENSION]),
                 "parentT101SourceManifestPath": T101_SOURCE.relative_to(ROOT).as_posix(), "parentT101SourceManifestSha256": sha(data["rawFiles"][T101_SOURCE]),
                 "parentT101IntegrationExtensionPath": T101_EXTENSION.relative_to(ROOT).as_posix(), "parentT101IntegrationExtensionSha256": sha(data["rawFiles"][T101_EXTENSION]),
                 "parentT102SourceManifestPath": T102_SOURCE.relative_to(ROOT).as_posix(), "parentT102SourceManifestSha256": sha(data["rawFiles"][T102_SOURCE]),
                 "parentT102IntegrationExtensionPath": T102_EXTENSION.relative_to(ROOT).as_posix(), "parentT102IntegrationExtensionSha256": sha(data["rawFiles"][T102_EXTENSION]),
                 "sourceManifestPath": SOURCE_MANIFEST.relative_to(ROOT).as_posix(), "sourceManifestSha256": sha(source_raw), "sceneContract": scene_contract,
                 "sourceOnly": True, "localOnly": True, "publicRedistribution": "held", "humanReview": "not_performed",
                 "learnerBinding": "none; no canonical or ancestor-only binding created",
                 "displayPolicy": "exact T103 subset source-only local technical display after individual validation; rights and human review remain held",
                 "chunks": [chunk], "counts": {"sourceMembers": len(EXPECTED), "uniqueNodes": len({a["nodeId"] for a in runtime_assets}),
                    "upperLimb": len(runtime_assets), "right": sum(a["side"] == "right" for a in runtime_assets), "left": sum(a["side"] == "left" for a in runtime_assets),
                    "learnerBindings": 0, "humanReviewed": 0, "publicRedistributionReleased": 0},
                 "inputs": {"frozenSourceSetSha256": sha(data["freezeRaw"]), "sourceAcquisitionSha256": sha(data["acquisitionRaw"]),
                            "parentT77ManifestSha256": sha(data["rawFiles"][T77_MANIFEST]), "parentT95OverlaySha256": sha(data["rawFiles"][T95_OVERLAY]),
                            "parentT79SourceManifestSha256": sha(data["rawFiles"][T79_SOURCE]), "parentT79IntegrationExtensionSha256": sha(data["rawFiles"][T79_EXTENSION]),
                            "parentT101SourceManifestSha256": sha(data["rawFiles"][T101_SOURCE]), "parentT101IntegrationExtensionSha256": sha(data["rawFiles"][T101_EXTENSION]),
                            "parentT102SourceManifestSha256": sha(data["rawFiles"][T102_SOURCE]), "parentT102IntegrationExtensionSha256": sha(data["rawFiles"][T102_EXTENSION]),
                            "sourceManifestSha256": sha(source_raw)}}
    extension_raw = json_bytes(extension)
    cache_manifest = json_bytes({"revision": extension["revision"], "task": "T103", "frozenSourceSetSha256": sha(data["freezeRaw"]), "chunks": [chunk]})
    return {"data": data, "chain": chain, "sourceAssets": source_assets, "runtimeAssets": runtime_assets, "meshRecords": mesh_records,
            "glb": glb, "glbPath": glb_path, "sourceManifest": source_manifest, "sourceRaw": source_raw, "extension": extension,
            "extensionRaw": extension_raw, "cacheManifestRaw": cache_manifest, "chunk": chunk, "parentAssets": parent_assets}


def check_result(result: dict[str, Any], compare_outputs: bool) -> dict[str, Any]:
    gltf, _binary = unpack_glb(result["glb"])
    if gltf.get("scene") != 0 or len(gltf.get("scenes", [])) != 1 or len(gltf.get("nodes", [])) != len(EXPECTED) or len(gltf.get("meshes", [])) != len(EXPECTED):
        raise BuildError("T103 GLB must contain one static source node/mesh for each exact frozen FJ")
    source_by_id = {row["sourceElementFileId"]: row for row in result["sourceAssets"]}
    seen = set(); glb_bounds = {}
    acquired = {row["sourceElementFileId"]: row for row in result["data"]["acquired"]}
    for index, fid in enumerate(EXPECTED):
        node, mesh, source, runtime = gltf["nodes"][index], gltf["meshes"][index], source_by_id[fid], next(a for a in result["runtimeAssets"] if a["id"] == fid)
        if node.get("name") != f"HA-MESH-BP3D4-{fid}" or node.get("extras", {}).get("sourceElementFileId") != fid or node.get("extras", {}).get("sourceSha256") != source["sourceSha256"]:
            raise BuildError(f"T103 GLB node identity/hash mismatch: {fid}")
        if any(key in node for key in ("children", "matrix", "translation", "rotation", "scale", "skin")): raise BuildError(f"unexpected pivot/transform/skin in shared-frame mesh: {fid}")
        if node["name"] in seen: raise BuildError(f"duplicate GLB mesh node {fid}")
        seen.add(node["name"])
        if mesh.get("name") != node["name"] or len(mesh.get("primitives", [])) != 1: raise BuildError(f"GLB mesh/node mapping not one-to-one: {fid}")
        if set(mesh["primitives"][0].get("attributes", {})) != {"POSITION", "NORMAL"}: raise BuildError(f"unexpected primitive attributes: {fid}")
        accessor = gltf["accessors"][mesh["primitives"][0]["attributes"]["POSITION"]]
        bounds = [accessor["min"], accessor["max"]]
        expected_bounds = runtime["bounds"]
        if any(abs(bounds[s][axis] - expected_bounds[s][axis]) > 1e-6 for s in range(2) for axis in range(3)): raise BuildError(f"runtime bounds differ from actual GLB accessors: {fid}")
        source_path = ROOT / acquired[fid]["cacheRelativePath"]
        vertices, _, _ = result["data"]["converter"].parse_obj(source_path)
        transformed = [result["data"]["converter"].transform_vertex(v) for v in vertices]
        exact = [[min(v[a] for v in transformed) for a in range(3)], [max(v[a] for v in transformed) for a in range(3)]]
        if any(abs(exact[s][axis] - bounds[s][axis]) > 1e-6 for s in range(2) for axis in range(3)): raise BuildError(f"T50/T69 transform not preserved by GLB: {fid}")
        glb_bounds[fid] = bounds
    if seen != {f"HA-MESH-BP3D4-{fid}" for fid in EXPECTED}: raise BuildError("GLB node set differs from exact frozen source members")
    if len({a["id"] for a in result["runtimeAssets"]}) != len(EXPECTED) or {a["id"] for a in result["runtimeAssets"]} != set(EXPECTED): raise BuildError("runtime ID membership is incomplete/duplicated/expanded")
    if any(a["sourcePackage"] != "T103" or a["pickState"] != "source_only_unbound" or a["stableIds"] or a["humanReviewed"] is not False or a["publicRedistribution"] != "held" or a["defaultVisible"] is not True or a["localDisplay"]["state"] != "allowed" for a in result["runtimeAssets"]):
        raise BuildError("T103 source-only/local technical visibility/rights/review policy changed")
    if compare_outputs:
        outputs = {SOURCE_MANIFEST: result["sourceRaw"], EXTENSION: result["extensionRaw"], DERIVED / "manifest.json": result["cacheManifestRaw"], result["glbPath"]: result["glb"]}
        for path, raw in outputs.items():
            if not path.is_file() or path.read_bytes() != raw: raise BuildError(f"T103 deterministic output differs: {path.relative_to(ROOT)}")
    browser = json.loads(BROWSER_EVIDENCE.read_text()) if BROWSER_EVIDENCE.is_file() else None
    browser_pass = bool(browser and browser.get("result") == "pass" and browser.get("runtimeManifest", {}).get("t103Chunk", {}).get("ids") == EXPECTED
                        and browser.get("runtimeManifest", {}).get("t103Chunk", {}).get("uniqueNodeCount") == 10
                        and browser.get("runtimeManifest", {}).get("rootCount") == 1 and browser.get("runtimeManifest", {}).get("rendererCount") == 1
                        and browser.get("checks", {}).get("fullBody") is True and browser.get("checks", {}).get("upperLimbClose") is True
                        and browser.get("checks", {}).get("lateralityPairs") is True and browser.get("checks", {}).get("muscleLayerOffOn") is True
                        and browser.get("browser", {}).get("consoleErrors") == 0 and browser.get("browser", {}).get("consoleWarnings") == 0)
    evidence = {"revision": "T103-local-technical-validation-v1", "task": "T103", "status": "passed_local_technical_validation" if browser_pass else "pending_actual_browser_validation",
                "browserEvidenceSha256": sha(BROWSER_EVIDENCE.read_bytes()) if browser_pass else None,
                "ids": EXPECTED, "sourceMemberCount": len(EXPECTED), "frozenSourceSetSha256": sha(result["data"]["freezeRaw"]),
                "frozenMembershipSha256": result["data"]["frozen"]["frozenMembershipSha256"], "sourceAcquisitionSha256": sha(result["data"]["acquisitionRaw"]),
                "fullArchiveDownloaded": False, "selectedRangeTransferBytes": result["data"]["acquisition"]["rangeTransferBytes"],
                "sourceSha256": {r["sourceElementFileId"]: r["sourceSha256"] for r in result["sourceAssets"]},
                "sourceCrc32": {r["sourceElementFileId"]: r["archiveMemberCrc32"] for r in result["sourceAssets"]},
                "sourceSideFromExactOfficialRows": {r["sourceElementFileId"]: r["sourceSide"] for r in result["sourceAssets"]},
                "sourceBoundsHeaderActualMaxDeltaMm": {r["sourceElementFileId"]: r["geometry"]["headerActualMaxDeltaMm"] for r in result["sourceAssets"]},
                "sourceVertexCount": {r["sourceElementFileId"]: r["geometry"]["sourceVertexCount"] for r in result["sourceAssets"]},
                "sourceTriangleCount": {r["sourceElementFileId"]: r["geometry"]["sourceTriangleCount"] for r in result["sourceAssets"]},
                "projectBoundsM": glb_bounds, "derivedGlbSha256": sha(result["glb"]), "derivedGlbBytes": len(result["glb"]),
                "parentScene": {"extensionOrder": ["T77", "T79", "T101", "T102", "T103"], "t102ExtensionSha256": sha(result["data"]["rawFiles"][T102_EXTENSION]),
                                "frame": FRAME, "unit": "m", "pose": POSE, "root": "AnatomySceneRoot", "oneRenderer": True},
                "wholeMusclePartReview": result["sourceManifest"]["wholeMusclePartRepresentation"],
                "sourceOnlyAndRights": {"canonicalBindingCount": 0, "stableIds": 0, "humanAnatomyReview": "not_performed", "publicRedistribution": "held",
                                         "localDisplay": "allowed only for the individually verified T103 subset"},
                "browserValidation": {"status": "pass" if browser_pass else "pending", "evidence": "work/evidence/T103/browser-validation.json"},
                "assertions": ["exact FJ/FMA/BP/header/official rows, CRC, SHA, side, mm units and vertex bounds per source member",
                               "T50/T69 shared transform, frame and reference pose; no mirror/recenter or side swap",
                               "one GLB node per exact FJ, no duplicate active parent IDs or ancestor-derived binding",
                               "actual mesh triangle surface sample comparisons against held T54 whole-FPB candidates; source-only and rights holds retained",
                               "same T77/T95/T79/T101/T102 root, renderer, camera and append-only scene contract"]}
    if not compare_outputs:
        EVIDENCE.parent.mkdir(parents=True, exist_ok=True); EVIDENCE.write_bytes(json_bytes(evidence))
    else:
        if not EVIDENCE.is_file() or EVIDENCE.read_bytes() != json_bytes(evidence): raise BuildError("T103 validation evidence stale or not reproducible")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build", action="store_true"); mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        result = convert()
        if args.build:
            frozen_hash = sha(result["data"]["freezeRaw"]); DERIVED.mkdir(parents=True, exist_ok=True)
            result["glbPath"].write_bytes(result["glb"])
            write_owned(SOURCE_MANIFEST, result["sourceRaw"], "T103", frozen_hash)
            write_owned(EXTENSION, result["extensionRaw"], "T103", frozen_hash)
            write_owned(DERIVED / "manifest.json", result["cacheManifestRaw"], "T103", frozen_hash)
            evidence = check_result(result, compare_outputs=False)
        else: evidence = check_result(result, compare_outputs=True)
        print(json.dumps({"status": evidence["status"], "sourceMembers": len(EXPECTED), "glbSha256": evidence["derivedGlbSha256"],
                          "evidence": "work/evidence/T103/validation.json"}, indent=2))
        return 0
    except Exception as exc:
        print(f"T103 build/check failed closed: {type(exc).__name__}: {exc}", file=sys.stderr); return 1


if __name__ == "__main__": raise SystemExit(main())
