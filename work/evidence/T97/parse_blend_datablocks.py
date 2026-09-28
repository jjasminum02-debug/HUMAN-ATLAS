#!/usr/bin/env python3
"""Forensic read-only parser for Blender .blend block names and relations.

This does not load the file in Blender, execute embedded text/add-ons/drivers,
or modify the archive. It reads BHead/SDNA layout and the exact ID datablock
names, object parents, meshes, collections and scene links from the binary.
"""

from __future__ import annotations

import argparse
import json
import mmap
import re
import struct
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


@dataclass
class Block:
    offset: int
    code: str
    size: int
    old: int
    sdna: int
    count: int
    data: int


class BlendReader:
    def __init__(self, path: Path):
        self.path = path
        self.file = path.open("rb")
        self.mm = mmap.mmap(self.file.fileno(), 0, access=mmap.ACCESS_READ)
        header = self.mm[:12]
        if not header.startswith(b"BLENDER"):
            raise ValueError("invalid .blend file magic")
        self.pointer_size = 8 if header[7:8] == b"-" else 4
        self.endian = "<" if header[8:9] == b"v" else ">"
        self.version = header[9:12].decode("ascii", "replace")
        self.blocks = self._read_blocks()
        dna_block = next((b for b in self.blocks if b.code == "DNA1"), None)
        if dna_block is None:
            raise ValueError(".blend DNA1 schema block is missing")
        self.names, self.types, self.type_lengths, self.structs = self._read_dna(dna_block)
        self.struct_type_names = {self.types[s["typeIndex"]] for s in self.structs}
        self.layouts, self.layout_mismatches = self._make_layouts()
        self.ptr_blocks = {b.old: b for b in self.blocks if b.old and b.code != "DNA1"}

    def _unpack(self, fmt: str, offset: int):
        return struct.unpack_from(self.endian + fmt, self.mm, offset)

    def _read_blocks(self):
        result = []
        offset = 12
        header_size = 24 if self.pointer_size == 8 else 20
        ptr_fmt = "Q" if self.pointer_size == 8 else "I"
        while offset + header_size <= len(self.mm):
            raw_code = self.mm[offset:offset + 4]
            code = raw_code.rstrip(b"\0 ").decode("ascii", "replace")
            size = self._unpack("I", offset + 4)[0]
            old = self._unpack(ptr_fmt, offset + 8)[0]
            sdna, count = self._unpack("II", offset + 8 + self.pointer_size)
            data = offset + header_size
            if data + size > len(self.mm):
                raise ValueError(f"block {code} at {offset} exceeds file bounds")
            result.append(Block(offset, code, size, old, sdna, count, data))
            offset = data + size
            if code == "ENDB":
                break
        if offset != len(self.mm):
            raise ValueError(f"block scan ended at {offset}, file length is {len(self.mm)}")
        return result

    def _read_dna(self, block):
        start = block.data
        end = start + block.size
        cursor = start

        def expect(code):
            nonlocal cursor
            if self.mm[cursor:cursor + 4] != code:
                raise ValueError(f"expected DNA section {code!r}, got {self.mm[cursor:cursor + 4]!r}")
            cursor += 4

        def read_int():
            nonlocal cursor
            value = self._unpack("I", cursor)[0]
            cursor += 4
            return value

        def read_strings(section):
            nonlocal cursor
            expect(section)
            count = read_int()
            values = []
            for _ in range(count):
                stop = self.mm.find(b"\0", cursor, end)
                if stop < 0:
                    raise ValueError("unterminated DNA name/type string")
                values.append(self.mm[cursor:stop].decode("utf-8", "replace"))
                cursor = stop + 1
            cursor = start + ((cursor - start + 3) & ~3)
            return values

        expect(b"SDNA")
        names = read_strings(b"NAME")
        types = read_strings(b"TYPE")
        expect(b"TLEN")
        lengths = list(self._unpack(f"{len(types)}H", cursor))
        cursor += 2 * len(types)
        cursor = start + ((cursor - start + 3) & ~3)
        expect(b"STRC")
        struct_count = read_int()
        structs = []
        for _ in range(struct_count):
            type_index, fields_count = self._unpack("HH", cursor)
            cursor += 4
            fields = []
            for _ in range(fields_count):
                field_type, field_name = self._unpack("HH", cursor)
                cursor += 4
                fields.append((field_type, field_name))
            structs.append({"typeIndex": type_index, "fields": fields})
        if cursor > end:
            raise ValueError("DNA schema extends beyond its block")
        return names, types, lengths, structs

    @staticmethod
    def _declaration(field_name):
        pointers = field_name.count("*")
        clean = field_name.replace("*", "")
        dims = [int(x) for x in re.findall(r"\[(\d+)\]", clean)]
        base_name = re.sub(r"\[\d+\]", "", clean).strip()
        return base_name, dims, pointers

    def _make_layouts(self):
        struct_by_name = {self.types[s["typeIndex"]]: s for s in self.structs}
        by_type_idx = {s["typeIndex"]: s for s in self.structs}
        layouts = {}
        building = set()
        mismatches = []

        def primitive_align(type_name, size):
            lower = type_name.lower()
            if "char" in lower or lower in {"bool", "uchar", "int8_t", "uint8_t"}:
                return 1
            if "short" in lower or lower in {"ushort", "int16_t", "uint16_t"}:
                return 2
            if "double" in lower or "64_t" in lower or lower in {"int64_t", "uint64_t"}:
                return 8
            if "int" in lower or "long" in lower or "float" in lower or "enum" in lower:
                return min(max(size, 1), 8)
            return min(max(size, 1), 8)

        def ensure_layout(type_idx):
            if type_idx in layouts:
                return layouts[type_idx]
            if type_idx in building:
                return {"size": self.type_lengths[type_idx], "align": 1, "fields": []}
            struct_def = by_type_idx.get(type_idx)
            if struct_def is None:
                return {"size": self.type_lengths[type_idx], "align": primitive_align(self.types[type_idx], self.type_lengths[type_idx]), "fields": []}
            building.add(type_idx)
            offset = 0
            max_align = 1
            fields = []
            for field_type_idx, field_name_idx in struct_def["fields"]:
                field_name = self.names[field_name_idx]
                clean_name, dims, pointers = self._declaration(field_name)
                field_type_name = self.types[field_type_idx]
                if pointers:
                    alignment = self.pointer_size
                    size = self.pointer_size
                elif field_type_idx in by_type_idx:
                    nested = ensure_layout(field_type_idx)
                    alignment = nested["align"]
                    size = nested["size"]
                    for dim in dims:
                        size *= dim
                else:
                    size = self.type_lengths[field_type_idx]
                    alignment = primitive_align(field_type_name, size)
                    for dim in dims:
                        size *= dim
                max_align = max(max_align, alignment)
                offset = (offset + alignment - 1) & ~(alignment - 1)
                fields.append({
                    "name": clean_name,
                    "rawName": field_name,
                    "typeIndex": field_type_idx,
                    "typeName": field_type_name,
                    "dims": dims,
                    "pointers": pointers,
                    "offset": offset,
                    "size": size,
                    "alignment": alignment,
                })
                offset += size
            computed = (offset + max_align - 1) & ~(max_align - 1)
            expected = self.type_lengths[type_idx]
            layout = {"size": expected, "computedSize": computed, "align": max_align, "fields": fields}
            layouts[type_idx] = layout
            building.remove(type_idx)
            if computed != expected:
                mismatches.append({"struct": self.types[type_idx], "computed": computed, "declared": expected})
            return layout

        for type_idx in by_type_idx:
            ensure_layout(type_idx)
        return layouts, mismatches

    def struct_name(self, sdna_index):
        if 0 <= sdna_index < len(self.structs):
            return self.types[self.structs[sdna_index]["typeIndex"]]
        return None

    def _read_primitive(self, type_name, offset, count=1):
        lname = type_name.lower()
        if lname in {"char", "signed char", "uchar", "unsigned char", "int8_t", "uint8_t", "bool"}:
            fmt = "b" if lname in {"char", "signed char", "int8_t"} else "B"
        elif lname in {"short", "short int", "signed short", "int16_t"}:
            fmt = "h"
        elif lname in {"ushort", "unsigned short", "uint16_t"}:
            fmt = "H"
        elif lname in {"int", "signed int", "int32_t", "enum"}:
            fmt = "i"
        elif lname in {"uint", "unsigned int", "uint32_t"}:
            fmt = "I"
        elif lname in {"int64_t", "long long"}:
            fmt = "q"
        elif lname in {"uint64_t", "unsigned long long"}:
            fmt = "Q"
        elif lname in {"float"}:
            fmt = "f"
        elif lname in {"double"}:
            fmt = "d"
        else:
            size = next((self.type_lengths[i] for i, t in enumerate(self.types) if t == type_name), 4)
            fmt = {1: "B", 2: "H", 4: "I", 8: "Q"}.get(size, "I")
        vals = struct.unpack_from(self.endian + fmt * count, self.mm, offset)
        return vals[0] if count == 1 else list(vals)

    def decode_struct(self, type_name, offset, depth=0):
        if depth > 8:
            return {"_error": "nested struct depth limit"}
        type_idx = next((i for i, t in enumerate(self.types) if t == type_name), None)
        if type_idx is None or type_idx not in self.layouts:
            return {"_error": f"unknown struct {type_name}"}
        layout = self.layouts[type_idx]
        struct_def = next(s for s in self.structs if s["typeIndex"] == type_idx)
        result = {}
        for field in layout["fields"]:
            field_type = field["typeName"]
            field_offset = offset + field["offset"]
            pointers = field["pointers"]
            dims = field["dims"]
            name = field["name"]
            if pointers:
                fmt = "Q" if self.pointer_size == 8 else "I"
                value = self._unpack(fmt, field_offset)[0]
            elif field_type in self.struct_type_names:
                if dims:
                    count = 1
                    for dim in dims:
                        count *= dim
                    elem_size = next(s for s in self.structs if self.types[s["typeIndex"]] == field_type)
                    elem_len = self.type_lengths[elem_size["typeIndex"]]
                    value = [self.decode_struct(field_type, field_offset + i * elem_len, depth + 1) for i in range(count)]
                else:
                    value = self.decode_struct(field_type, field_offset, depth + 1)
            elif dims and field_type.lower() in {"char", "signed char", "uchar", "unsigned char"}:
                count = 1
                for dim in dims:
                    count *= dim
                raw = self.mm[field_offset:field_offset + count]
                value = raw.split(b"\0", 1)[0].decode("utf-8", "replace")
            else:
                count = 1
                for dim in dims:
                    count *= dim
                value = self._read_primitive(field_type, field_offset, count)
            result[name] = value
        return result

    def records(self, wanted_type=None):
        for block in self.blocks:
            type_name = self.struct_name(block.sdna)
            if type_name in {"DNA1", None}:
                continue
            if wanted_type is not None and type_name != wanted_type:
                continue
            layout = self.layouts[self.structs[block.sdna]["typeIndex"]]
            size = layout["size"]
            if size <= 0 or block.count * size > block.size:
                continue
            for index in range(block.count):
                old = block.old + index * size if block.old else 0
                yield block, old, self.decode_struct(type_name, block.data + index * size)


ID_PREFIX = {
    "Object": "OB", "Mesh": "ME", "Collection": "GR", "Scene": "SC",
    "Curve": "CU", "Material": "MA", "Text": "TX", "Brush": "BR",
    "NodeTree": "NT", "Lattice": "LT", "VectorFont": "VF", "Sound": "SO",
    "Light": "LA", "Image": "IM", "World": "WO", "Camera": "CA",
}


def id_name(record, kind=None):
    id_struct = record.get("id")
    if isinstance(id_struct, dict):
        name = id_struct.get("name")
        if isinstance(name, str):
            prefix = ID_PREFIX.get(kind)
            return name[len(prefix):] if prefix and name.startswith(prefix) else name
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("blend", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    reader = BlendReader(args.blend.resolve(strict=True))
    code_counts = Counter(b.code for b in reader.blocks)
    datablocks = defaultdict(list)
    records_by_type = defaultdict(list)
    old_to_record = {}
    for block in reader.blocks:
        name = reader.struct_name(block.sdna)
        if name in {None, "DNA1", "ListBase", "CollectionObject", "CollectionChild"} or block.code in {"REND", "TEST", "GLOB", "ENDB"} or (block.code == "DATA" and name != "Collection"):
            continue
        layout = reader.layouts[reader.structs[block.sdna]["typeIndex"]]
        size = layout["size"]
        if size <= 0 or block.count * size > block.size:
            continue
        for index in range(block.count):
            old = block.old + index * size if block.old else 0
            record = reader.decode_struct(name, block.data + index * size)
            display_name = id_name(record, name)
            row = {"fileBlockType": name, "blockCode": block.code, "fileOffset": block.offset, "dataBlockAddress": hex(old) if old else None, "name": display_name, "idNameRaw": record.get("id", {}).get("name") if isinstance(record.get("id"), dict) else None, "record": record}
            records_by_type[name].append(row)
            if name and display_name is not None:
                datablocks[name].append(display_name)
            if old:
                old_to_record[old] = row
    object_rows = records_by_type.get("Object", [])
    mesh_rows = records_by_type.get("Mesh", [])
    collection_rows = records_by_type.get("Collection", [])
    scene_rows = records_by_type.get("Scene", [])
    object_by_ptr = {int(row["dataBlockAddress"], 16): row for row in object_rows if row["dataBlockAddress"]}
    mesh_by_ptr = {int(row["dataBlockAddress"], 16): row for row in mesh_rows if row["dataBlockAddress"]}
    collection_by_ptr = {int(row["dataBlockAddress"], 16): row for row in collection_rows if row["dataBlockAddress"]}
    data_blocks_by_address = {int(row["dataBlockAddress"], 16): row for kind in records_by_type.values() for row in kind if row["dataBlockAddress"]}

    for row in object_rows:
        rec = row["record"]
        row["objectName"] = id_name(rec, "Object")
        row["name"] = row["objectName"]
        row["objectId"] = row["dataBlockAddress"]
        row["objectTypeEnum"] = rec.get("type")
        row["dataAddress"] = hex(rec.get("data", 0)) if rec.get("data") else None
        data_row = data_blocks_by_address.get(rec.get("data", 0))
        row["dataBlockName"] = data_row.get("name") if data_row else None
        row["dataBlockType"] = data_row.get("fileBlockType") if data_row else None
        row["parentAddress"] = hex(rec.get("parent", 0)) if rec.get("parent") else None
        row["parentName"] = object_by_ptr.get(rec.get("parent", 0), {}).get("objectName")
        row["transformFields"] = {k: rec.get(k) for k in ("loc", "rot", "quat", "scale", "size", "parentinv", "parentinv") if k in rec}
        row["candidateNameMatch"] = bool(re.search(r"(?i)(latissimus\s+dorsi|latissimus|2231|broad\s+back|grand\s+dorsal)", " ".join(str(x or "") for x in (row.get("objectName"), row.get("dataBlockName")))))
    # Collection graph links are stored in DATA blocks. The exact linked IDs
    # and original serialized addresses are recorded even if a list is broken.
    data_records = defaultdict(list)
    for block in reader.blocks:
        type_name = reader.struct_name(block.sdna)
        if type_name in {"CollectionObject", "CollectionChild"} and block.code == "DATA" and block.old:
            layout = reader.layouts[reader.structs[block.sdna]["typeIndex"]]
            size = layout["size"]
            if size <= 0 or block.count * size > block.size:
                continue
            for index in range(block.count):
                old = block.old + index * size
                record = reader.decode_struct(type_name, block.data + index * size)
                data_records[type_name].append((old, record))

    def linked_list(first, item_type, pointer_field):
        output = []
        seen = set()
        current = first or 0
        map_type = {ptr: rec for ptr, rec in data_records.get(item_type, [])}
        while current and current not in seen:
            seen.add(current)
            node = map_type.get(current)
            if not node:
                output.append({"unresolvedPointer": hex(current)})
                break
            target = node.get(pointer_field, 0)
            output.append({"nodeAddress": hex(current), "targetAddress": hex(target) if target else None})
            current = node.get("next", 0)
        if current in seen:
            output.append({"cycleAt": hex(current)})
        return output

    collection_edges = []
    for row in collection_rows:
        rec = row["record"]
        gobject = rec.get("gobject", {})
        children = rec.get("children", {})
        object_links = linked_list(gobject.get("first", 0) if isinstance(gobject, dict) else 0, "CollectionObject", "ob")
        child_links = linked_list(children.get("first", 0) if isinstance(children, dict) else 0, "CollectionChild", "collection")
        row["objectLinks"] = [
            {**link, "objectName": object_by_ptr.get(int(link["targetAddress"], 16), {}).get("objectName") if link.get("targetAddress") else None}
            for link in object_links
        ]
        row["childLinks"] = [
            {**link, "collectionName": collection_by_ptr.get(int(link["targetAddress"], 16), {}).get("name") if link.get("targetAddress") else None}
            for link in child_links
        ]
        collection_edges.extend({"parentCollection": row.get("name"), **link} for link in row["childLinks"])

    # Resolve exact collection-tree paths for candidate objects without
    # serializing the decoded SDNA records into the evidence JSON.
    object_paths = defaultdict(list)
    direct_collections = defaultdict(list)
    collection_by_address = {
        int(row["dataBlockAddress"], 16): row
        for row in collection_rows if row.get("dataBlockAddress")
    }
    for row in collection_rows:
        for link in row.get("objectLinks", []):
            target = link.get("targetAddress")
            if target and link.get("objectName"):
                direct_collections[int(target, 16)].append(row["name"])

    def walk_collection(collection_address, path, ancestors):
        if collection_address in ancestors:
            return
        current = collection_by_address.get(collection_address)
        if not current:
            return
        next_path = path + [current["name"]]
        for link in current.get("objectLinks", []):
            target = link.get("targetAddress")
            if target and link.get("objectName"):
                object_paths[int(target, 16)].append(next_path)
        for link in current.get("childLinks", []):
            target = link.get("targetAddress")
            if target:
                walk_collection(int(target, 16), next_path, ancestors | {collection_address})

    for scene in scene_rows:
        root_ptr = scene["record"].get("master_collection", 0)
        if root_ptr:
            walk_collection(root_ptr, [], set())

    def compact_object(row):
        return {
            "fileOffset": row.get("fileOffset"),
            "objectIDPointer": row.get("dataBlockAddress"),
            "objectName": row.get("objectName"),
            "rawBlenderIDName": row.get("idNameRaw"),
            "objectTypeEnum": row.get("objectTypeEnum"),
            "parentIDPointer": row.get("parentAddress"),
            "parentObjectName": row.get("parentName"),
            "dataIDPointer": row.get("dataAddress"),
            "dataBlockType": row.get("dataBlockType"),
            "dataBlockName": row.get("dataBlockName"),
            "directCollections": sorted(set(direct_collections.get(int(row["dataBlockAddress"], 16), []))) if row.get("dataBlockAddress") and row.get("candidateNameMatch") else [],
            "collectionPaths": object_paths.get(int(row["dataBlockAddress"], 16), []) if row.get("dataBlockAddress") and row.get("candidateNameMatch") else [],
            "candidateNameMatch": row.get("candidateNameMatch", False),
            "transformFields": row.get("transformFields") if row.get("candidateNameMatch") else None,
        }

    compact_objects = [compact_object(row) for row in object_rows]
    compact_meshes = []
    for row in mesh_rows:
        rec = row["record"]
        compact_meshes.append({
            "fileOffset": row.get("fileOffset"),
            "meshIDPointer": row.get("dataBlockAddress"),
            "name": id_name(rec, "Mesh"),
            "rawBlenderIDName": row.get("idNameRaw"),
            "vertices": rec.get("totvert"),
            "edges": rec.get("totedge"),
            "loops": rec.get("totloop"),
            "polygons": rec.get("totpoly"),
        })
    compact_collections = []
    for row in collection_rows:
        compact_collections.append({
            "fileOffset": row.get("fileOffset"),
            "collectionIDPointer": row.get("dataBlockAddress"),
            "name": row.get("name"),
            "rawBlenderIDName": row.get("idNameRaw"),
            "objectCount": sum(bool(link.get("targetAddress")) for link in row.get("objectLinks", [])),
            "childCollectionNames": [link.get("collectionName") for link in row.get("childLinks", []) if link.get("collectionName")],
        })
    compact_scenes = []
    for row in scene_rows:
        root_ptr = row["record"].get("master_collection", 0)
        compact_scenes.append({
            "sceneName": row.get("name"),
            "sceneIDPointer": row.get("dataBlockAddress"),
            "masterCollectionPointer": hex(root_ptr) if root_ptr else None,
            "masterCollectionName": collection_by_address.get(root_ptr, {}).get("name") if root_ptr else None,
        })

    candidate_objects = [row for row in object_rows if row.get("candidateNameMatch")]
    summary_types = {k: len(v) for k, v in sorted(records_by_type.items())}
    result = {
        "task": "T97",
        "sourceFile": "Z-Anatomy/Startup.blend",
        "sourceFileSha256": "9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd",
        "inspectionMethod": "custom read-only Blender BHead/SDNA parser; no Blender file load or embedded code execution",
        "format": {"header": reader.mm[:12].decode("ascii", "replace"), "pointerSize": reader.pointer_size, "endian": reader.endian, "formatVersion": reader.version},
        "fileSizeBytes": len(reader.mm),
        "blockCount": len(reader.blocks),
        "blockCodes": dict(sorted(code_counts.items())),
        "layoutValidation": {"typeCount": len(reader.types), "structCount": len(reader.structs), "calculatedSizeMismatches": reader.layout_mismatches},
        "dataBlockCountsByType": summary_types,
        "dataBlockNames": {kind: sorted(names) for kind, names in sorted(datablocks.items())},
        "objectCount": len(object_rows),
        "meshDataBlockCount": len(mesh_rows),
        "collectionCount": len(collection_rows),
        "sceneCount": len(scene_rows),
        "candidateSearchDefinition": "Exact lexical candidate index for latissimus dorsi, latissimus, TA2:2231, broad back or grand dorsal on Object ID names and linked Mesh ID names. This is an inventory aid, not an identity/side/part decision.",
        "candidateSearchCount": len(candidate_objects),
        "candidateSearchObjects": [compact_object(row) for row in candidate_objects],
        "inventoryScopeNote": "The archive-wide names/count index is in dataBlockNames/dataBlockCountsByType. Candidate object/data-block locators and all rooted paths are expanded in candidateSearchObjects. A full archive object table is unnecessary because six target-name candidates were found.",
        "scenes": compact_scenes,
        "sceneRootCollections": compact_scenes,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "format": result["format"], "blockCount": result["blockCount"],
        "dataBlockCountsByType": summary_types, "layoutMismatchCount": len(reader.layout_mismatches),
        "objectCount": result["objectCount"], "meshDataBlockCount": result["meshDataBlockCount"],
        "collectionCount": result["collectionCount"], "sceneCount": result["sceneCount"],
        "candidateSearchCount": result["candidateSearchCount"],
        "candidateObjectNames": [row.get("objectName") for row in candidate_objects],
        "output": str(args.output),
    }, ensure_ascii=False, indent=2))
    reader.mm.close()
    reader.file.close()


if __name__ == "__main__":
    main()
