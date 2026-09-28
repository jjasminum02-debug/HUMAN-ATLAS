#!/usr/bin/env python3
"""Acquire only T104's ten frozen official R4 OBJ members via existing ZIP range primitives."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import stat
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / "work/evidence/T104/frozen-source-set.json"
OUT_ROOT = ROOT / "atlas-data/source-cache/bodyparts3d-r4/mesh/t104"
RECEIPT = ROOT / "work/evidence/T104/source-acquisition.json"
HELPER = ROOT / "atlas-data/tools/extract_bodyparts3d_r4_selected_zip_members.py"
MAX_RANGE_TRANSFER = 120_000_000
MAX_CENTRAL_DIRECTORY = 64_000_000
MAX_SELECTED_UNCOMPRESSED = 1_000_000_000
MAX_SINGLE_MEMBER = 200_000_000
EXPECTED = ["FJ1516", "FJ1516M", "FJ1518", "FJ1518M", "FJ1557", "FJ1600", "FJ1601", "FJ2774", "FJ2781", "FJ2783"]
EXPECTED_REGIONS = {"FJ1516": "upper-limb", "FJ1516M": "upper-limb", "FJ1518": "upper-limb", "FJ1518M": "upper-limb",
                    "FJ1557": "neck", "FJ1600": "neck", "FJ1601": "neck", "FJ2774": "neck", "FJ2781": "neck", "FJ2783": "neck"}


class AcquireError(RuntimeError):
    pass


def load_helper():
    spec = importlib.util.spec_from_file_location("t104_existing_r4_range_primitives", HELPER)
    if not spec or not spec.loader:
        raise AcquireError("could not load the existing bounded R4 range primitives")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def validate_freeze(helper) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frozen = json.loads(FREEZE.read_text(encoding="utf-8"))
    if frozen.get("revision") != "BodyParts3D-R4-T104-FROZEN-SOURCE-SET-v1" or frozen.get("task") != "T104" or frozen.get("status") != "frozen_before_mesh_acquisition":
        raise AcquireError("T104 acquisition requires the immutable T104 source freeze")
    if frozen.get("sourceElementFileIds") != EXPECTED:
        raise AcquireError("T104 frozen source ID order differs from the task allowlist")
    files = frozen.get("atomicSourceFiles")
    if not isinstance(files, list) or [row.get("sourceElementFileId") for row in files] != EXPECTED:
        raise AcquireError("T104 atomic member allowlist differs from the exact ten IDs")
    canonical = "\n".join(row["sourceElementFileId"] + "|" + ",".join(row["regionCandidates"]) + "|" + ",".join(row["expectedArchiveTrees"]) for row in files) + "\n"
    if sha(canonical.encode()) != frozen.get("frozenMembershipSha256"):
        raise AcquireError("T104 frozen membership hash mismatch")
    for row in files:
        fid = row.get("sourceElementFileId")
        region = row.get("regionCandidates")
        if (region != [EXPECTED_REGIONS[fid]] or row.get("expectedArchiveTrees") != ["IS-A"]
                or row.get("preferredArchiveTree") != "IS-A"):
            raise AcquireError(f"unexpected T104 archive tree/region assignment for {fid}")
    return frozen, files


def acquire() -> dict[str, Any]:
    helper = load_helper()
    frozen, rows = validate_freeze(helper)
    calls: list[dict[str, Any]] = []
    transferred = 0
    original_fetch = helper.fetch_range

    def fetch_recorded(url: str, start: int, end: int, etag: str):
        nonlocal transferred
        wanted = end - start + 1
        if transferred + wanted > MAX_RANGE_TRANSFER:
            raise AcquireError(f"selected archive ranges would exceed {MAX_RANGE_TRANSFER} bytes")
        raw, headers = original_fetch(url, start, end, etag)
        transferred += len(raw)
        calls.append({"url": url, "startByte": start, "endByte": end, "httpStatus": 206,
                      "contentRange": headers.get("content-range"), "etag": headers.get("etag"), "bytes": len(raw)})
        if transferred > MAX_RANGE_TRANSFER:
            raise AcquireError("T104 archive-range transfer exceeded its 120 MB bound")
        return raw, headers

    helper.fetch_range = fetch_recorded
    try:
        tree = "IS-A"
        url = helper.ARCHIVES[tree]
        meta = helper.head_archive(url)
        tail_size = min(meta["contentLength"], 65557)
        tail, _ = helper.fetch_range(url, meta["contentLength"] - tail_size, meta["contentLength"] - 1, meta["etag"])
        entries_count, cd_size, cd_offset = helper.parse_eocd(tail, meta["contentLength"])
        if cd_size > MAX_CENTRAL_DIRECTORY:
            raise AcquireError(f"official R4 ZIP central directory exceeds {MAX_CENTRAL_DIRECTORY} bytes")
        directory, _ = helper.fetch_range(url, cd_offset, cd_offset + cd_size - 1, meta["etag"])
        members = helper.parse_central_directory(directory, entries_count)
        requested = set(EXPECTED)
        if requested - members.keys():
            raise AcquireError(f"frozen T104 members absent from official R4 index: {sorted(requested - members.keys())}")
        total_uncompressed = 0
        for fid in EXPECTED:
            member = members[fid]
            if member.get("externalMode", 0) & 0o170000 == stat.S_IFLNK:
                raise AcquireError(f"refusing linked source member: {fid}")
            member_path = PurePosixPath(member["memberPath"])
            if member_path.is_absolute() or any(part in {".", ".."} for part in member_path.parts) or "\\" in member["memberPath"]:
                raise AcquireError(f"unsafe official archive path rejected: {member['memberPath']}")
            if member_path.as_posix() != f"isa_BP3D_4.0_obj_99/{fid}.obj":
                raise AcquireError(f"unexpected official archive member path for {fid}: {member['memberPath']}")
            if member["uncompressedBytes"] > MAX_SINGLE_MEMBER:
                raise AcquireError(f"selected OBJ exceeds {MAX_SINGLE_MEMBER} bytes: {fid}")
            total_uncompressed += member["uncompressedBytes"]
        if total_uncompressed > MAX_SELECTED_UNCOMPRESSED:
            raise AcquireError("selected OBJ total exceeds the T104 uncompressed bound")

        selected: dict[str, dict[str, Any]] = {}
        requested_index_bytes = tail_size + cd_size
        member_range_bytes = 0
        for row in rows:
            fid = row["sourceElementFileId"]
            member = members[fid]
            payload, fetched = helper.selected_member_bytes(url, meta, member)
            if not payload:
                raise AcquireError(f"empty official source OBJ member: {fid}")
            out_path = OUT_ROOT / row["regionCandidates"][0] / f"{fid}.obj"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            if out_path.exists():
                if out_path.read_bytes() != payload:
                    raise AcquireError(f"refusing to overwrite changed T104 source cache file: {out_path}")
            else:
                partial = out_path.with_suffix(".obj.partial")
                partial.write_bytes(payload)
                partial.replace(out_path)
            member_range_bytes += fetched
            selected[fid] = {"sourceElementFileId": fid, "memberPath": member["memberPath"],
                             "cacheRelativePath": out_path.relative_to(ROOT).as_posix(), "bytes": len(payload),
                             "sha256": sha(payload), "crc32": f"{member['crc32']:08x}", "archiveTree": tree,
                             "archiveUrl": url, "archiveEtag": meta["etag"], "zipCompressionMethod": member["compressionMethod"],
                             "compressedBytes": member["compressedBytes"], "rangeBytesRequested": fetched,
                             "uncompressedBytesFromDirectory": member["uncompressedBytes"]}
        if list(selected) != EXPECTED:
            raise AcquireError("selected acquisition did not return the T104 ordered exact source set")
        archive = {**meta, "url": url, "centralDirectoryEntries": entries_count, "centralDirectoryBytes": cd_size,
                   "rangeSelectedMemberIds": EXPECTED, "rangeSelectedMemberCount": len(EXPECTED),
                   "rangeBytesRequestedForZipIndex": requested_index_bytes, "rangeBytesRequestedForObjMembers": member_range_bytes}
        result = {"revision": "BodyParts3D-R4-T104-SELECTED-RANGE-ACQUISITION-v1", "task": "T104",
                  "acquiredAt": datetime.now(timezone.utc).isoformat(), "frozenSourceSetSha256": sha(FREEZE.read_bytes()),
                  "frozenMembershipSha256": frozen["frozenMembershipSha256"], "fullArchivesDownloaded": False,
                  "completeSourceFileCount": len(selected), "selectedSourceFiles": [selected[fid] for fid in EXPECTED],
                  "archiveRequests": {tree: archive}, "rangeTransferBytes": transferred, "rangeResponses": calls,
                  "bounds": {"maxRangeTransferBytes": MAX_RANGE_TRANSFER, "maxCentralDirectoryBytes": MAX_CENTRAL_DIRECTORY,
                             "maxSelectedUncompressedBytes": MAX_SELECTED_UNCOMPRESSED, "maxSingleMemberBytes": MAX_SINGLE_MEMBER},
                  "rightsBoundary": {"officialCurrentDatabaseLicenseReference": "CC BY 4.0 per LSDB Archive license page; original OBJ header retained per member",
                                     "redistributionStatus": "held_pending_file_level_project_reconciliation"}}
        if RECEIPT.exists() and RECEIPT.read_text(encoding="utf-8") != json.dumps(result, ensure_ascii=False, indent=2) + "\n":
            old = json.loads(RECEIPT.read_text(encoding="utf-8"))
            if old.get("task") != "T104":
                raise AcquireError("refusing to overwrite a non-T104 acquisition receipt")
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return result
    finally:
        helper.fetch_range = original_fetch


def check() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    frozen = json.loads(FREEZE.read_text(encoding="utf-8"))
    if (receipt.get("task") != "T104" or receipt.get("completeSourceFileCount") != len(EXPECTED)
            or receipt.get("fullArchivesDownloaded") is not False
            or receipt.get("frozenSourceSetSha256") != sha(FREEZE.read_bytes())):
        raise SystemExit("T104 acquisition receipt does not bind to the exact frozen source set")
    if [row.get("sourceElementFileId") for row in receipt.get("selectedSourceFiles", [])] != EXPECTED:
        raise SystemExit("T104 receipt IDs differ from the frozen allowlist")
    for row in receipt["selectedSourceFiles"]:
        path = ROOT / row["cacheRelativePath"]
        if not path.is_file() or path.stat().st_size != row["bytes"] or sha(path.read_bytes()) != row["sha256"]:
            raise SystemExit(f"T104 selected source file missing/size/hash changed: {path}")
        if row.get("sourceElementFileId") not in frozen["sourceElementFileIds"] or row.get("archiveTree") != "IS-A":
            raise SystemExit(f"T104 receipt member is outside the exact allowlist: {row.get('sourceElementFileId')}")
    print(json.dumps({"result": "pass", "files": len(receipt["selectedSourceFiles"]), "offlineCheck": True}, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate receipt and source files without network access")
    args = parser.parse_args()
    if args.check:
        check()
    else:
        result = acquire()
        print(json.dumps({"result": "pass", "files": result["completeSourceFileCount"],
                          "fullArchivesDownloaded": result["fullArchivesDownloaded"],
                          "rangeTransferBytes": result["rangeTransferBytes"],
                          "centralDirectoryBytes": result["archiveRequests"]["IS-A"]["centralDirectoryBytes"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
