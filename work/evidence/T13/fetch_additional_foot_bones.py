"""Acquire source-table verified right cuboid and metatarsals 2–4."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[3]
T02_SCRIPT = ROOT / "work/evidence/T02/extract_subset_via_http_ranges.py"
OUT = ROOT / "atlas-data/assets/bodyparts3d-v4-t13-bones"
EVIDENCE = ROOT / "work/evidence/T13/additional-transfer.json"
TARGETS = {
    "FJ3353": ("FMA24509", "right second metatarsal bone"),
    "FJ3355": ("FMA24511", "right third metatarsal bone"),
    "FJ3357": ("FMA24513", "right fourth metatarsal bone"),
    "FJ3364": ("FMA24528", "right cuboid bone"),
}


def main() -> None:
    spec = importlib.util.spec_from_file_location("t02_ranges", T02_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    t02 = json.loads((ROOT / "atlas-data/manifests/assets.json").read_text())
    tables = {}
    table_hashes = {}
    for name in ("isa_parts_list_e.txt", "isa_element_parts.txt"):
        path = ROOT / "work/evidence/T13" / name
        raw = path.read_bytes()
        table_hashes[name] = hashlib.sha256(raw).hexdigest()
        tables[name] = raw.decode("utf-8").splitlines()
    lookup = {}
    for file_id, (fma, name) in TARGETS.items():
        concept = next((i, row.split("\t")) for i, row in enumerate(tables["isa_parts_list_e.txt"], 1) if row.startswith(fma + "\t"))
        element = next((i, row.split("\t")) for i, row in enumerate(tables["isa_element_parts.txt"], 1) if row.endswith("\t" + file_id) and row.startswith(fma + "\t"))
        assert concept[1][2] == element[1][1] == name
        assert not (OUT / f"{file_id}.obj").exists()
        lookup[file_id] = (fma, name, concept[1][1], {"isa_parts_list_e.txt": concept[0], "isa_element_parts.txt": element[0]})
    remote = module.HttpRangeFile(t02["source"]["archiveUrl"])
    assert remote.size == t02["source"]["archiveSizeBytes"]
    assert remote.etag == t02["source"]["etag"] and remote.last_modified == t02["source"]["lastModified"]
    records = []
    with zipfile.ZipFile(remote) as archive:
        members = {Path(item.filename).name: item for item in archive.infolist() if item.filename.endswith(".obj")}
        for file_id, (fma, name, representation, rows) in lookup.items():
            item = members[f"{file_id}.obj"]
            path = OUT / f"{file_id}.obj"
            with archive.open(item) as source, path.open("xb") as output:
                digest = hashlib.sha256()
                while block := source.read(1024 * 1024):
                    output.write(block)
                    digest.update(block)
            records.append({"fileId": file_id, "archiveMember": item.filename,
                            "localPath": str(path.relative_to(ROOT)), "bytes": path.stat().st_size,
                            "sha256": digest.hexdigest(), "zipCrc32": f"{item.CRC:08x}",
                            "representationId": representation, "externalConceptId": fma,
                            "sourceName": name, "sourceTableRows": rows})
    result = {"sourceArchiveUrl": remote.url, "archiveSizeBytes": remote.size,
              "archiveLastModified": remote.last_modified, "archiveEtag": remote.etag,
              "retrieval": "HTTP byte ranges from exact T02 archive; full ZIP not saved",
              "rangeBytesTransferred": remote.total_range_bytes, "rangeBudgetBytes": module.MAX_RANGE_BYTES,
              "licensePage": t02["source"]["licensePage"],
              "requiredCredit": t02["license"]["archivePageRequiredCredit"],
              "sourceCoordinates": t02["geometry"], "sourceTableSha256": table_hashes,
              "assets": records}
    EVIDENCE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"assets": len(records), "rangeBytes": remote.total_range_bytes}))


if __name__ == "__main__":
    main()
