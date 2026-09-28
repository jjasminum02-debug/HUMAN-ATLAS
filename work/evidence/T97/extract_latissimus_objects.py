#!/usr/bin/env python3
"""Extract only the six T97 latissimus-named objects from the pinned blend.

The input .blend is read as binary data blocks by the adjacent forensic parser.
No Blender file is loaded and no embedded script, driver, modifier, or animation
is evaluated. OBJ outputs are local QA derivatives under the ignored cache.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "work/evidence/T97"
BLEND = ROOT / "atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend"
OUT = ROOT / "atlas-data/source-cache/z-anatomy/t97/latissimus-obj"
PARSER_PATH = EVIDENCE / "parse_blend_datablocks.py"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_reader():
    spec = importlib.util.spec_from_file_location("t97_blend_parser", PARSER_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module, module.BlendReader(BLEND)


def clean_id_name(raw: str, prefix: str) -> str:
    return raw[len(prefix):] if raw.startswith(prefix) else raw


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    module, reader = load_reader()
    objs = {}
    meshes = {}
    collections = {}
    for _, ptr, rec in reader.records("Object"):
        objs[ptr] = rec
    for _, ptr, rec in reader.records("Mesh"):
        meshes[ptr] = rec
    for _, ptr, rec in reader.records("Collection"):
        collections[ptr] = rec
    id_properties = {ptr: rec for _, ptr, rec in reader.records("IDProperty")}

    # Preserve exact collection object/child references and traverse from the
    # scene master root. This gives reproducible paths, not UI visibility.
    list_rows = defaultdict(dict)
    for b in reader.blocks:
        typ = reader.struct_name(b.sdna)
        if typ in {"CollectionObject", "CollectionChild"} and b.code == "DATA" and b.old:
            layout = reader.layouts[reader.structs[b.sdna]["typeIndex"]]
            size = layout["size"]
            for i in range(b.count):
                addr = b.old + i * size
                list_rows[typ][addr] = reader.decode_struct(typ, b.data + i * size)

    def linked(first, typ, target):
        out, seen = [], set()
        while first and first not in seen:
            seen.add(first)
            row = list_rows[typ].get(first)
            if not row:
                break
            out.append(row.get(target, 0))
            first = row.get("next", 0)
        return out

    def property_tree(address, depth=0):
        if not address or depth > 8:
            return []
        parent = id_properties.get(address)
        if not parent:
            return [{"unresolvedPropertyPointer": hex(address)}]
        first = parent.get("data", {}).get("group", {}).get("first", 0)
        items, seen = [], set()
        while first and first not in seen:
            seen.add(first)
            prop = id_properties.get(first)
            if not prop:
                items.append({"unresolvedPropertyPointer": hex(first)})
                break
            data = prop.get("data", {})
            item = {"name": prop.get("name"), "rawTypeCode": prop.get("type"), "length": prop.get("len")}
            if data.get("val") or data.get("val2"):
                item["integerPayload"] = [data.get("val"), data.get("val2")]
            if data.get("pointer"):
                item["pointerPayload"] = hex(data["pointer"])
            if prop.get("type") == 6:
                item["children"] = property_tree(first, depth + 1)
            items.append(item)
            first = prop.get("next", 0)
        return items

    scene_record = next(rec for _, _, rec in reader.records("Scene"))
    root_ptr = scene_record.get("master_collection", 0)
    paths = defaultdict(list)

    def walk_collection(ptr, chain, ancestors):
        if ptr in ancestors or ptr not in collections:
            return
        rec = collections[ptr]
        label = rec.get("id", {}).get("name", "")
        label = clean_id_name(label, "GR")
        next_chain = chain + [label]
        for obj_ptr in linked(rec.get("gobject", {}).get("first", 0), "CollectionObject", "ob"):
            if obj_ptr in objs:
                paths[obj_ptr].append(next_chain)
        for child_ptr in linked(rec.get("children", {}).get("first", 0), "CollectionChild", "collection"):
            walk_collection(child_ptr, next_chain, ancestors | {ptr})

    walk_collection(root_ptr, [], set())
    candidates = []
    for ptr, rec in objs.items():
        raw_name = rec.get("id", {}).get("name", "")
        name = clean_id_name(raw_name, "OB")
        if name.startswith("Latissimus dorsi muscle."):
            data_ptr = rec.get("data", 0)
            mesh_rec = meshes.get(data_ptr)
            if not mesh_rec:
                raise ValueError(f"candidate {name} has no Mesh datablock at {data_ptr:#x}")
            candidates.append((ptr, name, rec, data_ptr, mesh_rec))
    candidates.sort(key=lambda x: x[1])
    expected_names = [
        "Latissimus dorsi muscle.el", "Latissimus dorsi muscle.er",
        "Latissimus dorsi muscle.l", "Latissimus dorsi muscle.ol",
        "Latissimus dorsi muscle.or", "Latissimus dorsi muscle.r",
    ]
    if [x[1] for x in candidates] != expected_names:
        raise ValueError(f"expected exact six candidate objects, got {[x[1] for x in candidates]}")

    # Relevant binary layout type names are verified against the file DNA.
    layout_sizes = {}
    for type_name in ("MVert", "MLoop", "MPoly", "Object", "Mesh", "Collection"):
        idx = reader.types.index(type_name)
        layout_sizes[type_name] = {
            "declared": reader.type_lengths[idx],
            "computed": reader.layouts[idx].get("computedSize"),
        }

    ptr_blocks = defaultdict(list)
    for b in reader.blocks:
        if b.old:
            ptr_blocks[b.old].append(b)

    mesh_results = {}
    objects_out = []
    for ptr, name, obj, mesh_ptr, mesh in candidates:
        mesh_name = clean_id_name(mesh.get("id", {}).get("name", ""), "ME")
        vcount, lcount, pcount = mesh["totvert"], mesh["totloop"], mesh["totpoly"]
        arrays = {}
        for key, typename, count in (("mvert", "MVert", vcount), ("mloop", "MLoop", lcount), ("mpoly", "MPoly", pcount)):
            addr = mesh.get(key, 0)
            matches = [b for b in ptr_blocks.get(addr, []) if reader.struct_name(b.sdna) == typename]
            # Blender's serialized old-address field is reused by packed DATA
            # arrays. Resolve the pointer only when the datablock's recorded
            # element count gives one exact candidate; otherwise fail closed.
            exact = [b for b in matches if b.count == count]
            if len(exact) != 1:
                raise ValueError(f"{name}: {key} block mismatch pointer={addr:#x} count={count} exactCandidates={[(b.count,b.size) for b in exact]} allCandidates={[(b.count,b.size) for b in matches]}")
            block = exact[0]
            struct_size = reader.layouts[reader.structs[block.sdna]["typeIndex"]]["size"]
            raw = reader.mm[block.data:block.data + count * struct_size]
            arrays[key] = {"block": block, "raw": raw, "type": typename, "count": count, "structSize": struct_size}
        if mesh_name not in mesh_results:
            geom_digest = hashlib.sha256()
            for key in ("mvert", "mloop", "mpoly"):
                geom_digest.update(key.encode("ascii") + b"\0")
                geom_digest.update(arrays[key]["raw"])
            verts = []
            vinfo = arrays["mvert"]
            for i in range(vcount):
                vals = reader._unpack("3f", vinfo["block"].data + i * vinfo["structSize"])
                verts.append(vals)
            loops = []
            linfo = arrays["mloop"]
            for i in range(lcount):
                loops.append(reader._unpack("2i", linfo["block"].data + i * linfo["structSize"])[0])
            polys = []
            pinfo = arrays["mpoly"]
            for i in range(pcount):
                start, total = reader._unpack("2i", pinfo["block"].data + i * pinfo["structSize"])
                polys.append((start, total))
            mesh_results[mesh_name] = {
                "dataAddress": hex(mesh_ptr),
                "counts": {"vertices": vcount, "edges": mesh["totedge"], "loops": lcount, "polygons": pcount},
                "geometrySha256": geom_digest.hexdigest(),
                "arrays": {key: {"count": v["count"], "structSizeBytes": v["structSize"], "sha256": sha256(v["raw"]), "sourceBlockOffset": v["block"].offset} for key, v in arrays.items()},
                "vertices": verts,
                "loopVertexIndices": loops,
                "polygons": polys,
            }
        # Blender stores obmat as 4x4 row vectors, translation in row 4.
        matrix = obj["obmat"]
        if len(matrix) != 16:
            raise ValueError(f"unexpected matrix dimensions for {name}")
        meshdata = mesh_results[mesh_name]
        transformed = []
        for x, y, z in meshdata["vertices"]:
            transformed.append((
                x * matrix[0] + y * matrix[4] + z * matrix[8] + matrix[12],
                x * matrix[1] + y * matrix[5] + z * matrix[9] + matrix[13],
                x * matrix[2] + y * matrix[6] + z * matrix[10] + matrix[14],
            ))
        faces = []
        for start, total in meshdata["polygons"]:
            if total < 3 or start < 0 or start + total > len(meshdata["loopVertexIndices"]):
                raise ValueError(f"invalid polygon loop range in {name}")
            poly = meshdata["loopVertexIndices"][start:start + total]
            if any(v < 0 or v >= len(transformed) for v in poly):
                raise ValueError(f"invalid polygon vertex index in {name}")
            for j in range(1, len(poly) - 1):
                faces.append((poly[0] + 1, poly[j] + 1, poly[j + 1] + 1))
        out_path = OUT / (name.replace(" ", "_") + ".obj")
        with out_path.open("w", encoding="ascii", newline="\n") as f:
            f.write(f"# Read-only QA derivative from {BLEND.name}; no modifier/driver evaluation\n")
            f.write(f"o {name.replace(' ', '_')}\n")
            for v in transformed:
                f.write("v %.9g %.9g %.9g\n" % v)
            for face in faces:
                f.write("f %d %d %d\n" % face)
        obj_bytes = out_path.read_bytes()
        mins = [min(v[i] for v in transformed) for i in range(3)]
        maxs = [max(v[i] for v in transformed) for i in range(3)]
        parent = obj.get("parent", 0)
        parent_name = clean_id_name(objs[parent].get("id", {}).get("name", ""), "OB") if parent in objs else None
        side_label = None
        if name.endswith(".l") or name.endswith(".r"):
            side_label = "left" if name.endswith(".l") else "right"
            side_basis = "literal Blender object suffix; official Z-Anatomy add-on clean_name() removes .l/.r as suffixes"
        elif parent_name and (parent_name.endswith(".l") or parent_name.endswith(".r")):
            side_label = "left" if parent_name.endswith(".l") else "right"
            side_basis = f"parent Object ID name {parent_name!r} carries literal .l/.r suffix; candidate suffix itself is not interpreted"
        else:
            side_basis = "unresolved"
        objects_out.append({
            "objectName": name,
            "sourceAncestry": {
                "repository": "Z-Anatomy/Models-of-human-anatomy",
                "commit": "c7010a903b75a2fd24a13b1c2c4c3546a9223780",
                "archive": "Z-Anatomy.zip",
                "archiveSha256": "e029688545627bd0214b269e1063143abb580aad72b2c2445d6d8a9a0d9da736",
                "archiveMember": "Z-Anatomy/Startup.blend",
                "archiveMemberSha256": "9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd",
                "objectIDName": obj["id"]["name"],
                "objectIDPointer": hex(ptr),
                "parentObjectName": parent_name,
                "meshDataBlockName": mesh_name,
                "meshDataBlockPointer": hex(mesh_ptr),
                "objectSpecificUpstreamCrosswalk": "not located; archive-object name is a candidate, not a TA2/FMA/FJ identity",
            },
            "rawBlenderIDName": obj["id"]["name"],
            "objectIDPointer": hex(ptr),
            "sourceObjectBlockOffset": next(b.offset for b in reader.blocks if b.old == ptr and reader.struct_name(b.sdna) == "Object"),
            "parentObjectName": parent_name,
            "parentObjectIDPointer": hex(parent) if parent else None,
            "collectionPaths": paths.get(ptr, []),
            "customPropertiesReadOnly": property_tree(obj.get("id", {}).get("properties", 0)),
            "meshDataBlockName": mesh_name,
            "meshDataBlockPointer": hex(mesh_ptr),
            "meshCounts": meshdata["counts"],
            "geometrySha256": meshdata["geometrySha256"],
            "objectMatrixRowMajor": matrix,
            "objectMatrixSha256": sha256(json.dumps(matrix, separators=(",", ":")).encode()),
            "sideLabelFromSourceSuffixOrParent": side_label,
            "sideEvidence": side_basis,
            "partInterpretation": "unresolved; source object suffix/anchor membership is preserved literally and not renamed as origin/insertion",
            "worldBoundsFromSavedObjectMatrix": {"min": mins, "max": maxs},
            "triangleCountForQaObj": len(faces),
            "qaObjRelativePath": str(out_path.relative_to(ROOT)),
            "qaObjBytes": len(obj_bytes),
            "qaObjSha256": sha256(obj_bytes),
        })

    compact_meshes = {name: {k: v for k, v in row.items() if k not in {"vertices", "loopVertexIndices", "polygons"}} for name, row in mesh_results.items()}
    result = {
        "task": "T97",
        "sourceRepository": "Z-Anatomy/Models-of-human-anatomy",
        "sourceCommit": "c7010a903b75a2fd24a13b1c2c4c3546a9223780",
        "sourceArchiveRequestedUrl": "https://github.com/Z-Anatomy/Models-of-human-anatomy/raw/c7010a903b75a2fd24a13b1c2c4c3546a9223780/Z-Anatomy.zip",
        "sourceArchiveSha256": "e029688545627bd0214b269e1063143abb580aad72b2c2445d6d8a9a0d9da736",
        "sourceBlendRelativePath": str(BLEND.relative_to(ROOT)),
        "sourceBlendSha256": "9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd",
        "method": "read-only BHead/SDNA extraction; no source Blender startup file opened by Blender; no scripts, drivers, modifiers or animation executed",
        "candidateCount": len(objects_out),
        "distinctMeshDataBlockCount": len(compact_meshes),
        "layoutSizes": layout_sizes,
        "objects": objects_out,
        "distinctMeshDataBlocks": compact_meshes,
        "sourceSideNameRule": {
            "file": "Z-Anatomy/__init__.py",
            "sha256": "bd4df0dd92872bd07d9d883d7c724584b72640a016df8d067fc7c5c3d5d85306",
            "lineRange": "344-351",
            "text": "clean_name(name) recognizes terminal '.r' and '.l' as suffixes before other suffix classes.",
        },
        "promotion": {"mesh": "none", "canonicalBinding": "none", "learnerScene": "none", "rights": "held", "humanReview": "not_performed"},
    }
    out_json = EVIDENCE / "latissimus-extraction.json"
    out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out_json), "objects": len(objects_out), "distinctMeshDataBlocks": list(compact_meshes), "objFiles": len(objects_out), "totalObjBytes": sum(x["qaObjBytes"] for x in objects_out)}, indent=2))
    reader.mm.close()
    reader.file.close()


if __name__ == "__main__":
    main()
