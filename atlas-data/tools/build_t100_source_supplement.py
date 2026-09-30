#!/usr/bin/env python3
"""Build a bounded T100 supplement from already-cached BodyParts3D R4 assets.

This does not mutate or repack source bytes. It checks the frozen T100 queue,
T96 targets, T78 source identity, T77 compiled frame and local-display decision,
then writes a small server-side composition manifest. The web runtime receives
an allowlisted projection from the TypeScript adapter, never this evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "atlas-data/manifests/bodyparts3d-r4-t100-source-supplement.json"
SOURCE = "atlas-data/source-cache/bodyparts3d-r4"
FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
TRANSFORM = "[x,y,z]mm -> [x,z,-y]m; preserve x sign; no mirror or source-label change"
TODAY = "2026-10-01"
POLICY_PATH = "atlas-data/manifests/bodyparts3d-r4-t77/display-policy.json"
T77_MANIFEST_PATH = "atlas-data/source-cache/bodyparts3d-r4/converted/t77/manifest.json"
T78_SOURCE_PATH = "work/evidence/T78/source-elements.json"
T77_INVENTORY_PATH = "work/evidence/T77/current-inventory.json"
T96_PATH = "atlas-data/catalog/target-scope-t96.json"
QUEUE_PATH = "work/evidence/T100/closure-audit-2026-09-30/action-queue.json"

IDENTITY = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]

# T96 exact target identity, source FMA concept ancestry, and display-name fields.
# This is intentionally small: the six cached candidates in the current queue.
TARGETS = {
    "TA2:1282": {
        "sourceFma": "FMA16580", "english": "bony pelvis", "latin": "pelvis ossea",
        "kind": "bone_group", "owner": "pelvis-perineum", "regionIds": ["pelvis-perineum"],
        "relation": "source_declared_group_member", "name": {"modern": None, "traditional": None},
        "searchAliases": ["bony pelvis", "pelvis ossea"],
    },
    "TA2:2128": {
        "sourceFma": "FMA46727", "english": "levator veli palatini", "latin": "levator veli palatini",
        "kind": "named_muscle", "owner": "head", "regionIds": ["head"],
        "relation": "exact_target_with_explicit_side_child", "name": {"modern": "입천장올림근", "traditional": "구개범거근"},
        "searchAliases": ["levator veli palatini muscle", "musculus levator veli palatini"],
        "koreanUrl": "https://m.kmle.co.kr/search.php?Search=levator+veli+palatini+muscle",
        "koreanLocator": "Search result, 대한해부학회 의학용어 사전 맞춤 결과, Levator veli palatini m.; modern term and [옛 용어] field",
    },
    "TA2:2129": {
        "sourceFma": "FMA46730", "english": "tensor veli palatini", "latin": "tensor veli palatini",
        "kind": "named_muscle", "owner": "head", "regionIds": ["head"],
        "relation": "exact_target_with_explicit_side_child", "name": {"modern": "입천장긴장근", "traditional": "구개범장근"},
        "searchAliases": ["tensor veli palatini muscle", "musculus tensor veli palatini"],
        "koreanUrl": "https://m.kmle.co.kr/search.php?Search=tensor",
        "koreanLocator": "Search result, 대한해부학회 의학용어 사전 맞춤 결과, Tensor veli palatini m.; modern term and [옛 용어] field",
    },
    "TA2:2191": {
        "sourceFma": "FMA46665", "english": "salpingopharyngeus muscle", "latin": "musculus salpingopharyngeus",
        "kind": "named_muscle", "owner": "neck", "regionIds": ["neck"],
        "relation": "exact_target_with_explicit_side_child", "name": {"modern": "귀관인두근", "traditional": None},
        "searchAliases": ["이관인두근"],
        "koreanUrl": "https://m.kmle.co.kr/search.php?Search=salpingo",
        "koreanLocator": "Search result, 대한의협 의학용어 사전 맞춤 결과, salpingopharyngeus muscle; two Korean forms listed without an explicit older-term field",
    },
    "TA2:2202": {
        "sourceFma": "FMA46591", "english": "vocalis muscle", "latin": "musculus vocalis",
        "kind": "named_muscle", "owner": "neck", "regionIds": ["neck"],
        "relation": "exact_target_with_explicit_side_child", "name": {"modern": "성대근", "traditional": "성대근"},
        "searchAliases": ["vocalis", "musculus vocalis"],
        "koreanUrl": "https://m.kmle.co.kr/search.php?Search=musculus+vocalis",
        "koreanLocator": "Search result, KMLE medical terminology exact query, musculus vocalis entry; 성대근",
    },
    "TA2:2283": {
        "sourceFma": "FMA22830", "english": "semispinalis capitis muscle", "latin": "musculus semispinalis capitis",
        "kind": "named_muscle", "owner": "back", "regionIds": ["back"],
        "relation": "exact_target_with_explicit_side_child", "name": {"modern": "머리반가시근", "traditional": "두반극근"},
        "searchAliases": ["semispinalis capitis", "musculus semispinalis capitis"],
        "koreanUrl": "https://m.kmle.co.kr/search.php?Search=semis",
        "koreanLocator": "Search result, 대한해부학회 의학용어 사전 matched entry, Semispinalis capitis m.; modern term and [옛 용어] field",
    },
}

MEMBERS = [
    ("TA2:1282", "FJ3152", "FMA16586", "right", "hip_bone_right", "Hip bone", "볼기뼈", "관골", "skeletal_surface", ["pelvis-perineum"]),
    ("TA2:1282", "FJ3288", "FMA16587", "left", "hip_bone_left", "Hip bone", "볼기뼈", "관골", "skeletal_surface", ["pelvis-perineum"]),
    ("TA2:1282", "FJ3393", "FMA16202", None, "sacrum_midline", "Sacrum", "엉치뼈", "천골", "skeletal_surface", ["pelvis-perineum"]),
    ("TA2:2128", "FJ2741", "FMA46729", "left", "levator_veli_palatini", "Levator veli palatini muscle", "입천장올림근", "구개범거근", "muscle_surface_or_part", ["head"]),
    ("TA2:2128", "FJ2753", "FMA46728", "right", "levator_veli_palatini", "Levator veli palatini muscle", "입천장올림근", "구개범거근", "muscle_surface_or_part", ["head"]),
    ("TA2:2129", "FJ2748", "FMA46732", "left", "tensor_veli_palatini", "Tensor veli palatini muscle", "입천장긴장근", "구개범장근", "muscle_surface_or_part", ["head"]),
    ("TA2:2129", "FJ2760", "FMA46731", "right", "tensor_veli_palatini", "Tensor veli palatini muscle", "입천장긴장근", "구개범장근", "muscle_surface_or_part", ["head"]),
    ("TA2:2191", "FJ2745", "FMA46670", "left", "salpingopharyngeus", "Salpingopharyngeus muscle", "귀관인두근", None, "muscle_surface_or_part", ["neck"]),
    ("TA2:2191", "FJ2757", "FMA46669", "right", "salpingopharyngeus", "Salpingopharyngeus muscle", "귀관인두근", None, "muscle_surface_or_part", ["neck"]),
    ("TA2:2202", "FJ2788", "FMA46593", "left", "vocalis", "Vocalis muscle", "성대근", "성대근", "muscle_surface_or_part", ["neck"]),
    ("TA2:2202", "FJ2806", "FMA46592", "right", "vocalis", "Vocalis muscle", "성대근", "성대근", "muscle_surface_or_part", ["neck"]),
    ("TA2:2283", "FJ1538", "FMA22876", "right", "semispinalis_capitis", "Semispinalis capitis muscle", "머리반가시근", "두반극근", "muscle_surface_or_part", ["back"]),
    ("TA2:2283", "FJ1538M", "FMA22877", "left", "semispinalis_capitis", "Semispinalis capitis muscle", "머리반가시근", "두반극근", "muscle_surface_or_part", ["back"]),
]

def read(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def glb_doc(path: Path):
    data = path.read_bytes()
    if data[:4] != b"glTF" or struct.unpack_from("<I", data, 8)[0] != len(data):
        raise ValueError(f"invalid GLB container: {path}")
    json_len = struct.unpack_from("<I", data, 12)[0]
    json_end = 20 + json_len
    if data[json_end + 4:json_end + 8] != b"BIN\x00":
        raise ValueError(f"GLB binary chunk missing: {path}")
    bin_len = struct.unpack_from("<I", data, json_end)[0]
    binary = data[json_end + 8:json_end + 8 + bin_len]
    if len(binary) != bin_len:
        raise ValueError(f"truncated GLB binary chunk: {path}")
    return data, json.loads(data[20:json_end]), binary

def geometry_metrics(doc: dict, binary: bytes, mesh_index: int):
    mesh = doc["meshes"][mesh_index]
    triangles = vertices = 0
    view_ids: set[int] = set()
    accessors: list[tuple[str, int]] = []
    for primitive in mesh["primitives"]:
        if primitive.get("mode", 4) != 4:
            raise ValueError("only triangle surface resources may enter this supplement")
        index_accessor = doc["accessors"][primitive["indices"]]
        triangles += index_accessor["count"] // 3
        for semantic, accessor_index in [*sorted(primitive["attributes"].items()), ("INDICES", primitive["indices"])]:
            accessor = doc["accessors"][accessor_index]
            if accessor.get("sparse") or "bufferView" not in accessor:
                raise ValueError("sparse/implicit mesh accessors are not supported in this frozen supplement")
            if "bufferView" in accessor:
                view_ids.add(accessor["bufferView"])
            if semantic == "POSITION":
                vertices += accessor["count"]
            accessors.append((semantic, accessor_index))
    geometry_bytes = sum(doc["bufferViews"][i]["byteLength"] for i in view_ids)
    digest = hashlib.sha256()
    for semantic, accessor_index in accessors:
        accessor = doc["accessors"][accessor_index]
        view = doc["bufferViews"][accessor["bufferView"]]
        if view.get("buffer", 0) != 0:
            raise ValueError("external/multiple GLB buffers are not supported")
        offset = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
        stride = view.get("byteStride")
        element_bytes = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}.get(accessor["componentType"])
        component_count = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT2": 4, "MAT3": 9, "MAT4": 16}.get(accessor["type"])
        if element_bytes is None or component_count is None:
            raise ValueError("unknown glTF accessor layout")
        span = (accessor["count"] - 1) * (stride or element_bytes * component_count) + element_bytes * component_count
        payload = binary[offset:offset + span]
        if len(payload) != span:
            raise ValueError("glTF accessor extends outside binary chunk")
        digest.update(semantic.encode())
        digest.update(json.dumps({k: accessor[k] for k in ("componentType", "type", "count", "min", "max") if k in accessor}, sort_keys=True, separators=(",", ":")).encode())
        digest.update(payload)
    return triangles, vertices, geometry_bytes, digest.hexdigest()

def source_relation(target_id: str, source_fma: str, target: dict):
    if target_id == "TA2:1282":
        return {
            "targetId": target_id, "targetFmaGroup": "FMA16580", "targetEnglish": target["english"],
            "targetLatin": target["latin"], "relationKind": "source_declared_group_member",
            "sourceMemberFma": source_fma, "proof": "exact FMA16580 PART-OF row names the candidate FJ member",
            "completeness": "three source-declared members in this exact cached FMA group; not a whole-anatomy completeness claim",
            "canonicalHaBindingCreated": False,
        }
    return {
        "targetId": target_id, "targetFma": target["sourceFma"], "targetEnglish": target["english"],
        "targetLatin": target["latin"], "relationKind": "exact_target_with_explicit_side_child",
        "sourceMemberFma": source_fma,
        "proof": "exact T96 target English/Latin equals the frozen FMA parent concept; FMA child and source name state the explicit side",
        "canonicalHaBindingCreated": False,
    }

def build() -> dict:
    queue = read(QUEUE_PATH)
    scope = read(T96_PATH)
    targets = {t["id"]: t for t in scope["targets"]}
    wanted = set(TARGETS)
    queued = {t["targetId"]: t for t in queue["targets"] if t.get("nextAction") == "review_cached_cross_dataset_correspondence_and_frame"}
    if not wanted.issubset(queued):
        raise ValueError("the six frozen cached candidates are not all present in the current action queue")
    for tid, spec in TARGETS.items():
        actual = targets.get(tid)
        if not actual or actual["term"]["english"].casefold() != spec["english"].casefold() or actual["semanticKind"] != spec["kind"]:
            raise ValueError(f"T96 target identity changed: {tid}")
        if actual["primaryOwner"] != spec["owner"] or actual["regionIds"] != spec["regionIds"]:
            raise ValueError(f"T96 owner/region changed: {tid}")

    source_elements = {x["id"]: x for x in read(T78_SOURCE_PATH)}
    t77_inventory = {x["sourceElementId"]: x for x in read(T77_INVENTORY_PATH)["items"]}
    t77_manifest = read(T77_MANIFEST_PATH)
    t77_chunks = {c["id"]: c for c in t77_manifest["chunks"]}
    policy = read(POLICY_PATH)
    if policy.get("revision") != "T77-local-display-v1" or policy.get("notPublicReleaseApproval") is not True:
        raise ValueError("T77 local-display decision changed or was misread as public release approval")
    partof_path = ROOT / f"{SOURCE}/metadata/partof_element_parts.txt"
    partof_sha = sha(partof_path)
    exact_group_rows = {
        tuple(line.rstrip("\n").split("\t")) for line in partof_path.read_text(encoding="utf-8").splitlines()
        if line.startswith("FMA16580\t")
    }
    expected_group_rows = {("FMA16580", "bony pelvis", fj) for fj in ("FJ3152", "FJ3288", "FJ3393")}
    if exact_group_rows != expected_group_rows:
        raise ValueError("FMA16580 member set changed; do not apply group crosswalk")

    registry = read("atlas-data/source-cache/datasets/bp3d/registry.json")
    cached_files = {entry["id"]: entry for entry in registry["files"]}
    out_chunks: dict[str, dict] = {}
    out_objects = []
    name_sources: dict[str, dict] = {}

    for tid, fj, member_fma, side, group_key, english_display, ko_modern, ko_traditional, mesh_kind, region_ids in MEMBERS:
        target = TARGETS[tid]
        frozen_source = source_elements.get(fj)
        inventory_row = t77_inventory.get(fj)
        if not frozen_source or not inventory_row or inventory_row.get("geometry") != "present":
            raise ValueError(f"source identity/geometry missing for {fj}")
        source_concepts = {x["id"]: x["name"] for x in frozen_source.get("conceptCandidates", [])}
        # T78 stores concept IDs -> labels. Check IDs on both sides; never
        # infer identity from a label string. The group target is validated by
        # the exact PART-OF member set below instead of member ancestry.
        if member_fma not in source_concepts or (tid != "TA2:1282" and target["sourceFma"] not in source_concepts):
            raise ValueError(f"exact FMA identity relation not present in frozen T78 source data: {fj}")
        if inventory_row.get("sourceSha256") != frozen_source["runtime"]["sourceSha256"]:
            raise ValueError(f"T77/T78 source hash disagreement: {fj}")
        if frozen_source["runtime"].get("side") != side:
            raise ValueError(f"explicit source laterality disagrees: {fj}")
        if inventory_row.get("binding") != "source_only_unbound" or inventory_row.get("humanReviewed") is not False or inventory_row.get("publicRedistribution") != "held":
            raise ValueError(f"existing T77 policy changed: {fj}")
        decision = policy.get("items", {}).get(fj)
        if not decision or decision.get("state") != "allowed" or decision.get("sourceSha256") != inventory_row["sourceSha256"]:
            raise ValueError(f"no item-level local-display permission for {fj}")
        if decision.get("runtimeSide") != side or decision.get("publicRedistribution") != "held" or decision.get("humanReviewed") is not False:
            raise ValueError(f"local display/side/rights/review decision mismatch: {fj}")

        chunk = next((c for c in t77_manifest["chunks"] if any(a.get("id") == fj for a in c["assets"])), None)
        if not chunk or chunk["id"] not in cached_files:
            raise ValueError(f"cached compiled chunk missing for {fj}")
        if cached_files[chunk["id"]]["sha256"] != chunk["sha256"] or cached_files[chunk["id"]]["bytes"] != chunk["bytes"]:
            raise ValueError(f"BP3D cache registry differs from T77 source chunk: {chunk['id']}")
        glb_path = ROOT / cached_files[chunk["id"]]["path"]
        chunk_bytes, doc, binary = glb_doc(glb_path)
        if hashlib.sha256(chunk_bytes).hexdigest() != chunk["sha256"]:
            raise ValueError(f"cached chunk bytes changed: {chunk['id']}")
        node = next((n for n in doc["nodes"] if n.get("name") == f"HA-MESH-BP3D4-{fj}"), None)
        if not node or "mesh" not in node:
            raise ValueError(f"exact evaluated resource name missing from GLB: {fj}")
        extras = node.get("extras", {})
        compiled_side = extras.get("lateralityFromExactSourceHeader", extras.get("laterality"))
        if extras.get("externalConceptId") != member_fma or compiled_side != side:
            raise ValueError(f"GLB source concept or exact side mismatch: {fj}")
        if extras.get("atlasFrame", extras.get("projectFrame")) != FRAME:
            raise ValueError(f"registered project frame missing for {fj}")
        source_transform = extras.get("transform")
        if not isinstance(source_transform, str) or not source_transform.startswith("[x,y,z]mm -> [x,z,-y]m"):
            raise ValueError(f"compiled frame/pose provenance changed for {fj}")
        if extras.get("pose", extras.get("sourcePose")) != "bodyparts3d-r4-static-reference":
            raise ValueError(f"compiled pose provenance changed for {fj}")
        if any(k in node for k in ("matrix", "translation", "rotation", "scale")):
            raise ValueError(f"expected baked identity GLB node transform for {fj}")
        asset = next(a for a in chunk["assets"] if a.get("id") == fj)
        if asset["side"] != side or asset["sourceSha256"] != inventory_row["sourceSha256"]:
            raise ValueError(f"compiled asset registry side/hash mismatch: {fj}")
        triangles, vertices, geometry_bytes, geometry_sha256 = geometry_metrics(doc, binary, node["mesh"])
        frozen_geometry_sha = extras.get("geometrySha256")
        resource_key = f"HA-MESH-BP3D4-{fj}"
        chunk_entry = out_chunks.setdefault(chunk["id"], {
            "id": chunk["id"], "sourceNamespace": "bp3d-r4", "url": f"/__atlas/body/{chunk['id']}.glb",
            "sha256": chunk["sha256"], "bytes": chunk["bytes"], "geometryBytes": 0,
            "resources": [], "level": "overview", "selectionScoped": True,
        })
        chunk_entry["resources"].append(resource_key)
        chunk_entry["geometryBytes"] += geometry_bytes

        name_provenance = {}
        if tid == "TA2:1282":
            # A target-level Korean group name was not found; only member names are displayed.
            field_url = "https://m.kmle.co.kr/search.php?Search=hip+bone" if fj != "FJ3393" else "https://m.kmle.co.kr/search.php?Search=sacrum"
            field_locator = "KMLE search-index result, standard anatomical terminology entry for the individual source member; edition not exposed"
        else:
            field_url = target["koreanUrl"]
            field_locator = target["koreanLocator"]
        name_provenance["koModern"] = {
            "value": ko_modern, "url": field_url, "exactEdition": None, "editionExposure": "not_exposed",
            "accessDate": TODAY, "accessMethod": "search_index_excerpt", "locator": field_locator,
            "openedOriginalDictionaryRecord": False,
        }
        if ko_traditional is None:
            name_provenance["koTraditional"] = {
                "value": None, "url": field_url, "exactEdition": None, "editionExposure": "not_exposed",
                "accessDate": TODAY, "accessMethod": "search_index_excerpt", "locator": None,
                "openedOriginalDictionaryRecord": False,
                "missingReason": "검색 결과에 현대명과 대체형은 있으나 이 필드의 옛 용어 판정이 명시되지 않음",
            }
        else:
            name_provenance["koTraditional"] = {
                "value": ko_traditional, "url": field_url, "exactEdition": None, "editionExposure": "not_exposed",
                "accessDate": TODAY, "accessMethod": "search_index_excerpt", "locator": field_locator,
                "openedOriginalDictionaryRecord": False,
            }
        name_provenance["en"] = {
            "value": english_display, "source": "BodyParts3D T77 exact source concept + T96 target record",
            "accessMethod": "local_frozen_metadata", "locator": f"T96 {tid}; T78 source element {fj} / {member_fma}",
        }
        name_sources[fj] = name_provenance

        synonyms = target["searchAliases"] if tid != "TA2:1282" else target["searchAliases"]
        if tid == "TA2:2191":
            synonyms = ["이관인두근"]
        elif tid == "TA2:2202":
            synonyms = ["vocalis", "musculus vocalis"]
        elif tid == "TA2:2283":
            synonyms = ["semispinalis capitis", "musculus semispinalis capitis"]
        obj = {
            "sourceKey": f"BP3D4-{fj}", "sourceName": extras.get("sourceName", asset.get("sourceName", english_display)),
            "resource": resource_key, "chunkId": chunk["id"], "kind": mesh_kind, "side": side,
            "searchGroupKey": f"bp3d-concept-{group_key}",
            # Keep same-named bilateral bone surfaces distinguishable in the
            # list. Muscle pairs intentionally share one concept row and use
            # the card's side selector.
            "label": f"{ko_modern} · {'왼쪽' if side == 'left' else '오른쪽'}" if tid == "TA2:1282" and side else ko_modern,
            "names": {"koModern": ko_modern, "koTraditional": ko_traditional, "en": english_display},
            "aliases": sorted(set([target["english"], target["latin"], *synonyms])),
            "regionIds": target["regionIds"], "sourceRegionIds": asset["regions"], "bounds": asset["bounds"],
            "matrix": IDENTITY, "geometrySpace": "registered_world", "sourceNamespace": "bp3d-r4",
            "lods": {
                "overview": {"resource": resource_key, "chunk": chunk["id"], "triangles": triangles, "vertices": vertices, "geometryBytes": geometry_bytes},
                "detail": {"resource": resource_key, "chunk": chunk["id"], "triangles": triangles, "vertices": vertices, "geometryBytes": geometry_bytes},
            },
            "sourceIdentity": {
                "sourceId": "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0", "sourceRelease": "BodyParts3D Release 4.0",
                "sourceElementFileId": fj, "sourceFmaId": member_fma, "targetFmaId": target["sourceFma"],
                "sourceSha256": inventory_row["sourceSha256"], "priorCompiledGeometrySha256": frozen_geometry_sha,
                "compiledChunkSha256": chunk["sha256"], "sourceFrame": "BodyParts3D R4 static reference; registered by T77/T50/T69 pipeline",
                "sourceUnit": "mm (exact OBJ Bounds(mm) header; T77 transformed output is metres)",
                "projectFrame": FRAME, "conversion": source_transform,
                "pose": "bodyparts3d-r4-static-reference", "nodeTransform": "identity; project coordinates baked into evaluated geometry",
                "triangleCount": triangles, "vertexCount": vertices,
                "compiledMeshAccessorSha256": geometry_sha256,
                "sourceLaterality": side if side else "not_lateralized_by_exact_source_name",
            },
            "rights": {
                "sourceLicense": "CC BY-SA 2.1 Japan", "localDisplay": "allowed_per_T77_item_decision",
                "localDecisionId": "T77-local-display-v1", "publicRedistribution": "held",
                "canonicalHaBinding": None, "sourceOnly": True, "humanReview": "not_performed",
                "retainedNonBlockingReasons": decision.get("retainedHoldReasons", []),
            },
            "nameEvidence": name_provenance,
            "targetAssociation": source_relation(tid, member_fma, target),
        }
        # Keep the hip member crosswalk explicit and don't imply a target-level Korean group name.
        if tid == "TA2:1282":
            obj["targetAssociation"]["exactPartOfTableSha256"] = partof_sha
            obj["targetAssociation"]["sourceGroupMemberSet"] = ["FJ3152", "FJ3288", "FJ3393"]
        out_objects.append(obj)

    if {o["targetAssociation"]["targetId"] for o in out_objects} != wanted or len(out_objects) != 13:
        raise ValueError("supplement must cover exactly the six assigned targets and thirteen exact objects")
    manifest_inputs = [
        QUEUE_PATH, T96_PATH, T78_SOURCE_PATH, T77_INVENTORY_PATH, POLICY_PATH,
        T77_MANIFEST_PATH, "atlas-data/source-cache/datasets/bp3d/registry.json",
        "atlas-data/source-cache/bodyparts3d-r4/metadata/partof_element_parts.txt",
        "work/evidence/T50/scene-contract.md", "work/evidence/T69/diagnostic.json",
    ]
    target_rows = {tid: {
        "targetId": tid, "english": spec["english"], "latin": spec["latin"], "semanticKind": spec["kind"],
        "primaryOwner": spec["owner"], "regionIds": spec["regionIds"],
        "targetKoreanGroupName": spec["name"]["modern"],
        "sourceObjectCount": sum(1 for o in out_objects if o["targetAssociation"]["targetId"] == tid),
        "relationKind": spec["relation"],
        "fullAnatomicalExtentClaim": False,
        "canonicalHaBindingCreated": False,
    } for tid, spec in TARGETS.items()}
    return {
        "schemaVersion": 1,
        "id": "T100-cached-source-supplement-2026-10-01-v1",
        "namespace": "bp3d-r4",
        "revision": "bp3d-r4-t100-cached-candidates-v1",
        "composition": "append validated local source objects into the existing ZA scene and renderer",
        "sourceId": "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0",
        "sourceRelease": "BodyParts3D Release 4.0",
        "sourceLicense": "CC BY-SA 2.1 Japan",
        "attribution": "BodyParts3D, (c) The Database Center for Life Science licensed under CC Attribution-Share Alike 2.1 Japan",
        "sourceFrame": "BodyParts3D Release 4.0 native static reference",
        "sourceUnit": "mm, evidenced per exact OBJ Bounds(mm) header",
        "projectFrame": FRAME,
        "projectUnit": "m",
        "geometrySpace": "registered_world",
        "registration": TRANSFORM,
        "pose": "bodyparts3d-r4-static-reference",
        "nodeTransform": "identity; registered project coordinates baked into T77 evaluated geometry",
        "rightsDecision": {
            "evidencePath": POLICY_PATH,
            "evidenceSha256": sha(ROOT / POLICY_PATH),
            "decisionId": "T77-local-display-v1",
            "decisionRevision": policy["revision"],
            "localDisplay": "per-item allowed only for the thirteen listed objects",
            "publicRedistribution": "held",
            "humanReview": "not_performed",
            "sourceOnly": True,
        },
        "inputSha256": {p: sha(ROOT / p) for p in manifest_inputs},
        "targetScopeSha256": sha(ROOT / T96_PATH),
        "sourceElementCatalogSha256": sha(ROOT / T78_SOURCE_PATH),
        "sourceMeshMetadataPath": "work/evidence/T77/current-inventory.json",
        "sourceMeshMetadataSha256": sha(ROOT / T77_INVENTORY_PATH),
        "sourceGroupMembership": {"FMA16580": {"path": f"{SOURCE}/metadata/partof_element_parts.txt", "sha256": partof_sha, "memberElementFileIds": ["FJ3152", "FJ3288", "FJ3393"], "targetId": "TA2:1282", "extentStatus": "source-declared-three-member-set; not global anatomy completeness"}},
        "localEvidence": {
            "sourceIndexOrExcerptOnly": True,
            "nameFields": name_sources,
            "sourceIdentityAndFrame": "T78 source-elements + T77 compiled GLB manifest/geometry extras + T50 scene contract + T69 frame registration evidence",
            "noNewDownload": True,
            "originalSourceBytesMutated": False,
        },
        "targets": target_rows,
        "chunks": list(out_chunks.values()),
        "objects": out_objects,
        "summary": {
            "assignedTargets": sorted(wanted), "targetCount": 6, "uniqueObjects": len(out_objects),
            "uniqueChunkCount": len(out_chunks), "uniqueRegions": sorted({region for o in out_objects for region in o["regionIds"]}),
            "newCanonicalHaBindings": 0, "humanReview": "not_performed", "publicRedistribution": "held",
            "targetTermEvidenceGapCountChanged": 0, "newSourceGeometry": 0,
            "sourceGeometryNewlyAvailableToMainLearnerScene": len(out_objects),
        },
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = json.dumps(build(), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != generated:
            raise SystemExit("T100 supplement is stale; run without --check to rebuild from pinned local evidence")
        print("T100 cached source supplement is current")
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(generated, encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
