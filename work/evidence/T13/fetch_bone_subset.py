"""Acquire the five T02-listed, missing right-bone OBJ members by bounded HTTP ranges.

The source archive is never saved; source OBJ bytes and transport metadata are
kept separately from the immutable T02 and OpenSim inputs.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[3]
T02_SCRIPT = ROOT / "work/evidence/T02/extract_subset_via_http_ranges.py"
OUT = ROOT / "atlas-data/assets/bodyparts3d-v4-t13-bones"
EVIDENCE = ROOT / "work/evidence/T13/source-transfer.json"
TARGET_IDS = ("FJ3308", "FJ3351", "FJ3359", "FJ3365", "FJ3377")


def main() -> None:
    spec = importlib.util.spec_from_file_location("t02_ranges", T02_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    t02 = json.loads((ROOT / "atlas-data/manifests/assets.json").read_text())
    listed = {row["element_file_id"]: row for row in t02["relatedBoneInventory"]}
    assert all(listed[file_id]["availability"] == "listed_mapped_not_acquired" for file_id in TARGET_IDS)
    assert all(not (OUT / f"{file_id}.obj").exists() for file_id in TARGET_IDS)
    remote = module.HttpRangeFile(t02["source"]["archiveUrl"])
    assert remote.size == t02["source"]["archiveSizeBytes"]
    assert remote.etag == t02["source"]["etag"]
    assert remote.last_modified == t02["source"]["lastModified"]
    records = []
    OUT.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(remote) as archive:
        available = {Path(item.filename).name: item for item in archive.infolist() if item.filename.endswith(".obj")}
        assert all(f"{file_id}.obj" in available for file_id in TARGET_IDS)
        for file_id in TARGET_IDS:
            info = available[f"{file_id}.obj"]
            destination = OUT / f"{file_id}.obj"
            with archive.open(info) as source, destination.open("xb") as output:
                digest = hashlib.sha256()
                while block := source.read(1024 * 1024):
                    output.write(block)
                    digest.update(block)
            records.append({
                "fileId": file_id,
                "archiveMember": info.filename,
                "localPath": str(destination.relative_to(ROOT)),
                "bytes": destination.stat().st_size,
                "sha256": digest.hexdigest(),
                "zipCrc32": f"{info.CRC:08x}",
                "representationId": listed[file_id]["representation_id"],
                "externalConceptId": listed[file_id]["concept_id"],
                "sourceName": listed[file_id]["source_name"],
                "sourceTableRows": listed[file_id]["table_rows"],
            })
    result = {
        "sourceArchiveUrl": remote.url,
        "archiveSizeBytes": remote.size,
        "archiveLastModified": remote.last_modified,
        "archiveEtag": remote.etag,
        "retrieval": "HTTP byte ranges from exact T02 archive; full ZIP not saved",
        "rangeBytesTransferred": remote.total_range_bytes,
        "rangeBudgetBytes": module.MAX_RANGE_BYTES,
        "licensePage": t02["source"]["licensePage"],
        "requiredCredit": t02["license"]["archivePageRequiredCredit"],
        "sourceCoordinates": t02["geometry"],
        "assets": records,
    }
    EVIDENCE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"assets": len(records), "rangeBytes": remote.total_range_bytes}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        raise
