#!/usr/bin/env python3
"""Preflight and safely extract the one T97 ZIP under strict size/path limits."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import sys
import zipfile
from datetime import datetime
from pathlib import Path, PurePosixPath
from zoneinfo import ZoneInfo

MAX_ARCHIVE_BYTES = 120_000_000
MAX_TOTAL_UNPACKED = 1_000_000_000
MAX_FILES = 10_000
CHUNK_SIZE = 1024 * 1024


def safe_relative(name: str, is_dir: bool) -> PurePosixPath:
    if not name or "\x00" in name or "\\" in name:
        raise ValueError(f"unsafe member path syntax: {name!r}")
    path = PurePosixPath(name)
    parts = path.parts
    if path.is_absolute() or not parts or any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"absolute, empty, dot, or traversal member path: {name!r}")
    if any(":" in part for part in parts):
        raise ValueError(f"drive-qualified/colon member path: {name!r}")
    if is_dir and name.endswith("/"):
        path = PurePosixPath(*parts)
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--extract-to", type=Path, required=True)
    args = parser.parse_args()
    root = args.project_root.resolve(strict=True)
    archive = args.archive.resolve(strict=True)
    cache_root = (root / "atlas-data/source-cache/z-anatomy/t97").resolve(strict=True)
    if not archive.is_relative_to(cache_root) or archive.is_symlink():
        raise RuntimeError("archive must be a regular file inside the ignored T97 source cache")
    for output in (args.receipt, args.inventory):
        if not output.resolve().is_relative_to(root / "work/evidence/T97"):
            raise RuntimeError("inspection outputs must remain in work/evidence/T97")
    extract_to = args.extract_to.absolute()
    if not extract_to.parent.resolve().is_relative_to(cache_root):
        raise RuntimeError("extraction directory must remain in the ignored T97 source cache")
    if extract_to.exists() or extract_to.is_symlink():
        raise RuntimeError("refusing to reuse or overwrite an existing extraction directory")

    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    archive_bytes = archive.stat().st_size
    archive_hash = hashlib.sha256(archive.read_bytes()).hexdigest()
    result: dict[str, object] = {
        "task": "T97",
        "inspectedAt": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(),
        "archivePath": archive.relative_to(root).as_posix(),
        "archiveBytes": archive_bytes,
        "archiveSha256": archive_hash,
        "archiveLimitBytes": MAX_ARCHIVE_BYTES,
        "unpackedLimitBytes": MAX_TOTAL_UNPACKED,
        "fileLimit": MAX_FILES,
        "receiptMatches": archive_hash == receipt.get("sha256") and archive_bytes == receipt.get("downloadedBytes"),
        "status": "preflight_failed",
        "preflight": {},
        "members": [],
        "blenderCandidates": [],
        "extractRoot": None,
    }
    try:
        if not result["receiptMatches"]:
            raise ValueError("download receipt SHA-256 or byte length does not match cached archive")
        if archive_bytes > MAX_ARCHIVE_BYTES:
            raise ValueError(f"compressed archive exceeds transfer cap: {archive_bytes}")
        seen: set[str] = set()
        entries: list[tuple[zipfile.ZipInfo, PurePosixPath, bool]] = []
        symlinks: list[str] = []
        total = 0
        file_count = 0
        with zipfile.ZipFile(archive, "r") as zf:
            for info in zf.infolist():
                is_dir = info.is_dir()
                relative = safe_relative(info.filename, is_dir)
                unix_mode = (info.external_attr >> 16) & 0xFFFF
                is_symlink = stat.S_ISLNK(unix_mode)
                if is_symlink:
                    symlinks.append(info.filename)
                key = relative.as_posix().casefold()
                if key in seen:
                    raise ValueError(f"duplicate/case-colliding archive path: {info.filename!r}")
                seen.add(key)
                if not is_dir:
                    file_count += 1
                    total += info.file_size
                    if info.flag_bits & 0x1:
                        raise ValueError(f"encrypted archive member is not inspectable safely: {info.filename}")
                entries.append((info, relative, is_dir))
            result["preflight"] = {
                "archiveEntryCount": len(entries),
                "fileCount": file_count,
                "directoryCount": sum(1 for _, _, is_dir in entries if is_dir),
                "advertisedUnpackedBytes": total,
                "symlinkEntries": symlinks,
            }
            if file_count > MAX_FILES:
                raise ValueError(f"archive file count exceeds cap: {file_count}")
            if total > MAX_TOTAL_UNPACKED:
                raise ValueError(f"archive advertised expansion exceeds cap: {total}")
            if symlinks:
                raise ValueError(f"archive contains symlink entries; refusing extraction: {symlinks[:20]}")

            result["status"] = "safe_to_extract"
            result["extractRoot"] = extract_to.relative_to(root).as_posix()
            extract_to.mkdir(parents=True, exist_ok=False)
            extracted_total = 0
            actual_files = 0
            member_rows = []
            for info, relative, is_dir in entries:
                destination = extract_to.joinpath(*relative.parts)
                resolved = destination.resolve(strict=False)
                if not resolved.is_relative_to(extract_to.resolve(strict=True)):
                    raise ValueError(f"resolved member path escapes extraction root: {info.filename}")
                if is_dir:
                    destination.mkdir(parents=True, exist_ok=True)
                    member_rows.append({
                        "archivePath": info.filename,
                        "kind": "directory",
                        "uncompressedBytes": 0,
                        "compressedBytes": info.compress_size,
                        "crc32": f"{info.CRC:08x}",
                    })
                    continue
                if destination.exists() or destination.is_symlink():
                    raise ValueError(f"refusing overwrite/collision: {info.filename}")
                destination.parent.mkdir(parents=True, exist_ok=True)
                digest = hashlib.sha256()
                written = 0
                with zf.open(info, "r") as src, destination.open("xb") as dst:
                    while True:
                        chunk = src.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        written += len(chunk)
                        extracted_total += len(chunk)
                        if extracted_total > MAX_TOTAL_UNPACKED:
                            raise ValueError(f"actual extracted bytes exceeded cap: {extracted_total}")
                        digest.update(chunk)
                        dst.write(chunk)
                    dst.flush()
                    os.fsync(dst.fileno())
                if written != info.file_size:
                    raise ValueError(f"member byte count mismatch: {info.filename}: {written} != {info.file_size}")
                actual_files += 1
                member_rows.append({
                    "archivePath": info.filename,
                    "kind": "file",
                    "uncompressedBytes": written,
                    "compressedBytes": info.compress_size,
                    "crc32": f"{info.CRC:08x}",
                    "sha256": digest.hexdigest(),
                })
            if actual_files != file_count or extracted_total != total:
                raise ValueError(f"actual extraction totals differ: files={actual_files}/{file_count}, bytes={extracted_total}/{total}")
            result["members"] = member_rows
            result["blenderCandidates"] = [
                row for row in member_rows
                if row["kind"] == "file" and str(row["archivePath"]).lower().endswith((".blend", ".blend1"))
            ]
            result["preflight"].update({
                "actualExtractedFiles": actual_files,
                "actualExtractedBytes": extracted_total,
                "allMemberCrcsVerifiedByZipfile": True,
                "allFileSha256Recorded": True,
            })
            result["status"] = "extracted"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        if result.get("status") == "safe_to_extract":
            result["status"] = "extract_failed"
            if extract_to.exists() and not extract_to.is_symlink():
                shutil.rmtree(extract_to)
        elif result.get("status") != "preflight_failed":
            result["status"] = "preflight_failed"
    args.inventory.parent.mkdir(parents=True, exist_ok=True)
    args.inventory.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "members"}, ensure_ascii=False, indent=2))
    print(f"archive_member_rows={len(result['members'])}")
    print(f"blender_candidates={len(result['blenderCandidates'])}")
    return 0 if result["status"] == "extracted" else 2


if __name__ == "__main__":
    raise SystemExit(main())
