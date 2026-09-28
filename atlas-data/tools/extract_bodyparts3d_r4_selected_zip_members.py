#!/usr/bin/env python3
"""Fetch only frozen T52 BodyParts3D R4 OBJ members via HTTP byte ranges.

The official archives are never downloaded whole. The tool reads the ZIP end
record and central directory, then fetches only the compressed byte ranges for
the allow-listed FJ members in the immutable T52 start manifest.
"""

from __future__ import annotations

import argparse
import binascii
import hashlib
import json
import re
import stat
import struct
import time
import urllib.error
import urllib.request
import zlib
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FREEZE = ROOT / "work/evidence/T52/frozen-source-set.json"
DEFAULT_OUT = ROOT / "atlas-data/source-cache/bodyparts3d-r4/mesh/t52"
ARCHIVES = {
    "IS-A": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip",
    "PART-OF": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/partof_BP3D_4.0_obj_99.zip",
}
FJ_RE = re.compile(r"^FJ[0-9]+M?$")
T103_IDS = ["FJ1473", "FJ1473M", "FJ1474", "FJ1474M", "FJ1481", "FJ1481M", "FJ1514", "FJ1514M", "FJ1515", "FJ1515M"]
T103_MAX_SELECTED_MEMBER_BYTES = 200_000_000
T103_MAX_SELECTED_TOTAL_BYTES = 1_000_000_000
EOCD = b"PK\x05\x06"
CENTRAL = b"PK\x01\x02"
LOCAL = b"PK\x03\x04"


class RangeError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def fetch_range(url: str, start: int, end: int, etag: str) -> tuple[bytes, dict[str, str]]:
    if start < 0 or end < start:
        raise RangeError(f"invalid byte range {start}-{end}")
    request = urllib.request.Request(
        url,
        headers={"Range": f"bytes={start}-{end}", "If-Match": etag, "Accept-Encoding": "identity", "User-Agent": "HUMAN-ATLAS-T52-selected-source-fetch/1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            status = response.status
            headers = {key.lower(): value for key, value in response.headers.items()}
            body = response.read()
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RangeError(f"official range request failed for {start}-{end}: {exc}") from exc
    expected_length = end - start + 1
    if status != 206:
        raise RangeError(f"server returned HTTP {status}; partial content (206) required; full-archive fallback is forbidden")
    content_range = headers.get("content-range", "")
    if not content_range.startswith(f"bytes {start}-{end}/"):
        raise RangeError(f"unexpected Content-Range {content_range!r}")
    if headers.get("etag") != etag:
        raise RangeError("official archive ETag changed during selected-member acquisition")
    if len(body) != expected_length:
        raise RangeError(f"short range: wanted {expected_length} bytes, received {len(body)}")
    return body, headers


def head_archive(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, method="HEAD", headers={"Accept-Encoding": "identity", "User-Agent": "HUMAN-ATLAS-T52-selected-source-fetch/1"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            headers = {key.lower(): value for key, value in response.headers.items()}
            status = response.status
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RangeError(f"official archive metadata request failed: {exc}") from exc
    if status != 200:
        raise RangeError(f"official archive HEAD returned HTTP {status}")
    if headers.get("accept-ranges", "").lower() != "bytes":
        raise RangeError("official archive does not advertise byte-range support; whole-archive download is forbidden")
    etag = headers.get("etag")
    length = headers.get("content-length")
    if not etag or not length or not length.isdigit():
        raise RangeError("official archive HEAD did not provide ETag and Content-Length")
    return {"etag": etag, "contentLength": int(length), "lastModified": headers.get("last-modified"), "acceptRanges": headers["accept-ranges"]}


def parse_eocd(tail: bytes, total_size: int) -> tuple[int, int, int]:
    search_start = max(0, len(tail) - 22 - 65535)
    marker = tail.rfind(EOCD, search_start)
    if marker < 0 or marker + 22 > len(tail):
        raise RangeError("ZIP end-of-central-directory record was not found in bounded archive tail")
    signature, disk_no, cd_disk, entries_disk, entries_total, cd_size, cd_offset, comment_len = struct.unpack_from("<4s4H2LH", tail, marker)
    if signature != EOCD or disk_no or cd_disk or entries_disk != entries_total:
        raise RangeError("multi-disk or malformed ZIP archives are unsupported")
    if entries_total == 0xFFFF or cd_size == 0xFFFFFFFF or cd_offset == 0xFFFFFFFF:
        raise RangeError("ZIP64 archives are outside this small selected-source tool's supported profile")
    if marker + 22 + comment_len != len(tail):
        raise RangeError("ZIP end record/comment does not terminate at the archive tail")
    if cd_offset + cd_size > total_size:
        raise RangeError("central directory lies outside archive size")
    return entries_total, cd_size, cd_offset


def parse_central_directory(data: bytes, expected_entries: int) -> dict[str, dict[str, Any]]:
    members: dict[str, dict[str, Any]] = {}
    cursor = 0
    while cursor < len(data):
        if cursor + 46 > len(data) or data[cursor : cursor + 4] != CENTRAL:
            raise RangeError(f"invalid ZIP central directory at offset {cursor}")
        values = struct.unpack_from("<4s6H3L5H2L", data, cursor)
        _, _made, _needed, flags, method, _mtime, _mdate, crc, compressed, uncompressed, name_len, extra_len, comment_len, disk_start, _internal_attr, external_attr, local_offset = values
        if disk_start != 0 or compressed == 0xFFFFFFFF or uncompressed == 0xFFFFFFFF or local_offset == 0xFFFFFFFF:
            raise RangeError("ZIP64 or split-disk member is outside supported profile")
        name_start = cursor + 46
        name_end = name_start + name_len
        extra_end = name_end + extra_len
        record_end = extra_end + comment_len
        if record_end > len(data):
            raise RangeError("truncated central directory member")
        raw_name = data[name_start:name_end]
        encoding = "utf-8" if flags & 0x800 else "cp437"
        name = raw_name.decode(encoding)
        member_path = PurePosixPath(name)
        if "\\" in name or "\x00" in name or member_path.is_absolute() or any(part in {".", ".."} for part in member_path.parts):
            raise RangeError(f"unsafe ZIP member path rejected: {name!r}")
        cursor = record_end
        if name.endswith("/"):
            continue
        base = PurePosixPath(name).name
        if not base.startswith("FJ") or not base.lower().endswith(".obj"):
            continue
        match = re.fullmatch(r"(FJ[0-9]+M?)\.obj", base, re.IGNORECASE)
        if not match:
            continue
        file_id = match.group(1).upper()
        if file_id in members:
            raise RangeError(f"duplicate FJ member in one official archive: {file_id}")
        members[file_id] = {
            "memberPath": name,
            "flags": flags,
            "compressionMethod": method,
            "crc32": crc,
            "compressedBytes": compressed,
            "uncompressedBytes": uncompressed,
            "localHeaderOffset": local_offset,
            "externalMode": (external_attr >> 16) & 0xFFFF,
        }
    if cursor != len(data):
        raise RangeError("unexpected bytes after ZIP central directory")
    if len(members) > expected_entries:
        raise RangeError("parsed FJ OBJ count exceeds central directory entry count")
    return members


def selected_member_bytes(url: str, archive_meta: dict[str, Any], member: dict[str, Any]) -> tuple[bytes, int]:
    offset = member["localHeaderOffset"]
    header, _ = fetch_range(url, offset, offset + 29, archive_meta["etag"])
    if header[:4] != LOCAL:
        raise RangeError(f"local ZIP member header missing at byte {offset}")
    _sig, _ver, local_flags, method, _time, _date, local_crc, local_comp, local_uncomp, name_len, extra_len = struct.unpack("<4s5H3I2H", header)
    if method != member["compressionMethod"] or method not in (0, 8):
        raise RangeError(f"unsupported/mismatched ZIP compression method: {method}")
    if (local_flags & 0x1) or (member["flags"] & 0x1):
        raise RangeError("encrypted OBJ archive member is not supported")
    variable, _ = fetch_range(url, offset + 30, offset + 30 + name_len + extra_len - 1, archive_meta["etag"])
    name = variable[:name_len].decode("utf-8" if local_flags & 0x800 else "cp437")
    if name != member["memberPath"]:
        raise RangeError("local and central directory member names differ")
    if not (local_flags & 0x8) and (local_crc, local_comp, local_uncomp) != (member["crc32"], member["compressedBytes"], member["uncompressedBytes"]):
        raise RangeError("local and central directory CRC/size fields differ")
    data_start = offset + 30 + name_len + extra_len
    data_end = data_start + member["compressedBytes"] - 1
    compressed, _ = fetch_range(url, data_start, data_end, archive_meta["etag"])
    if method == 0:
        payload = compressed
    else:
        try:
            payload = zlib.decompress(compressed, -15)
        except zlib.error as exc:
            raise RangeError(f"raw DEFLATE member failed to decompress: {exc}") from exc
    if len(payload) != member["uncompressedBytes"]:
        raise RangeError("decompressed OBJ byte count differs from central directory")
    if (binascii.crc32(payload) & 0xFFFFFFFF) != member["crc32"]:
        raise RangeError("decompressed OBJ CRC-32 differs from official ZIP central directory")
    return payload, 30 + name_len + extra_len + member["compressedBytes"]


def load_frozen(path: Path) -> dict[str, Any]:
    frozen = json.loads(path.read_text(encoding="utf-8"))
    is_t52 = frozen.get("revision") == "BodyParts3D-R4-T52-FROZEN-ATOMIC-SOURCE-SET-v1" and frozen.get("task", "T52") == "T52"
    is_t103 = frozen.get("revision") == "BodyParts3D-R4-T103-FROZEN-SOURCE-SET-v1" and frozen.get("task") == "T103"
    if (not is_t52 and not is_t103) or frozen.get("status") != "frozen_before_mesh_acquisition":
        raise RangeError("expected an immutable T52 or bounded T103 source-set freeze manifest")
    files = frozen.get("atomicSourceFiles")
    canonical = "\n".join(e["sourceElementFileId"] + "|" + ",".join(e["regionCandidates"]) + "|" + ",".join(e["expectedArchiveTrees"]) for e in files) + "\n"
    if sha256_bytes(canonical.encode()) != frozen.get("frozenMembershipSha256"):
        raise RangeError("frozen atomic membership hash mismatch")
    ids = [row.get("sourceElementFileId") for row in files]
    if len(ids) != len(set(ids)) or any(not isinstance(value, str) or not FJ_RE.fullmatch(value) for value in ids):
        raise RangeError("frozen source allowlist contains duplicate or malformed FJ IDs")
    if is_t52 and (len(ids) != 85 or any(value.endswith("M") for value in ids)):
        raise RangeError("T52 frozen source allowlist must contain exactly 85 distinct unsuffixed FJ IDs")
    if is_t103 and (ids != T103_IDS or any(row.get("regionCandidates") != ["upper-limb"] or row.get("expectedArchiveTrees") != ["IS-A"] or row.get("preferredArchiveTree") != "IS-A" for row in files)):
        raise RangeError("T103 frozen source allowlist/region/tree differs from its exact ten-ID scope")
    return frozen


def acquire(frozen_path: Path = DEFAULT_FREEZE, out_root: Path = DEFAULT_OUT, receipt_path: Path | None = None) -> dict[str, Any]:
    frozen = load_frozen(frozen_path)
    task = frozen.get("task", "T52")
    by_tree: dict[str, list[dict[str, Any]]] = {key: [] for key in ARCHIVES}
    for row in frozen["atomicSourceFiles"]:
        tree = row["preferredArchiveTree"]
        if tree not in ARCHIVES or tree not in row["expectedArchiveTrees"]:
            raise RangeError(f"frozen row has invalid preferred archive tree: {row['sourceElementFileId']}")
        by_tree[tree].append(row)

    archive_results: dict[str, Any] = {}
    found: dict[str, tuple[str, dict[str, Any]]] = {}
    for tree, rows in by_tree.items():
        if not rows:
            continue
        url = ARCHIVES[tree]
        meta = head_archive(url)
        tail_size = min(meta["contentLength"], 65557)
        tail, _ = fetch_range(url, meta["contentLength"] - tail_size, meta["contentLength"] - 1, meta["etag"])
        entries_count, cd_size, cd_offset = parse_eocd(tail, meta["contentLength"])
        if task == "T103" and cd_size > 64_000_000:
            raise RangeError(f"official central directory exceeds the bounded 64 MB metadata limit: {cd_size}")
        central_data, _ = fetch_range(url, cd_offset, cd_offset + cd_size - 1, meta["etag"])
        members = parse_central_directory(central_data, entries_count)
        requested = {r["sourceElementFileId"] for r in rows}
        absent = sorted(requested - members.keys())
        if absent:
            raise RangeError(f"frozen {tree} source IDs missing from the official archive index: {', '.join(absent)}")
        if task == "T103":
            for file_id in requested:
                member = members[file_id]
                if member["uncompressedBytes"] > T103_MAX_SELECTED_MEMBER_BYTES:
                    raise RangeError(f"selected OBJ exceeds the 200 MB T103 per-member bound: {file_id}")
            if sum(members[file_id]["uncompressedBytes"] for file_id in requested) > T103_MAX_SELECTED_TOTAL_BYTES:
                raise RangeError("selected OBJ total exceeds the 1 GB T103 uncompressed bound")
        archive_results[tree] = {
            **meta,
            "url": url,
            "centralDirectoryEntries": entries_count,
            "centralDirectoryBytes": cd_size,
            "rangeSelectedMemberIds": sorted(requested),
            "rangeSelectedMemberCount": len(requested),
            "rangeBytesRequestedForZipIndex": tail_size + cd_size,
            "rangeBytesRequestedForObjMembers": 0,
        }
        for row in rows:
            file_id = row["sourceElementFileId"]
            member = members[file_id]
            if task == "T103" and ((member.get("externalMode", 0) & 0o170000) == stat.S_IFLNK
                    or PurePosixPath(member["memberPath"]).name != f"{file_id}.obj"
                    or PurePosixPath(member["memberPath"]).parent.as_posix() != "isa_BP3D_4.0_obj_99"):
                raise RangeError(f"T103 selected archive member path/type is unexpected: {member['memberPath']}")
            payload, fetched = selected_member_bytes(url, meta, member)
            if not payload:
                raise RangeError(f"empty source OBJ member: {file_id}")
            matches = [region for region in row["regionCandidates"]]
            if len(matches) != 1:
                raise RangeError(f"unexpected ambiguous region candidate membership for {file_id}: {matches}")
            destination = out_root / matches[0] / f"{file_id}.obj"
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                existing = destination.read_bytes()
                if existing != payload:
                    raise RangeError(f"refusing to overwrite changed source cache member {destination}")
            else:
                temp = destination.with_suffix(".obj.partial")
                temp.write_bytes(payload)
                temp.replace(destination)
            archive_results[tree]["rangeBytesRequestedForObjMembers"] += fetched
            found[file_id] = (tree, {"sourceElementFileId": file_id, "memberPath": member["memberPath"], "cacheRelativePath": destination.relative_to(ROOT).as_posix(), "bytes": len(payload), "sha256": sha256_bytes(payload), "crc32": f"{member['crc32']:08x}", "archiveTree": tree, "archiveUrl": url, "archiveEtag": meta["etag"], "zipCompressionMethod": member["compressionMethod"], "compressedBytes": member["compressedBytes"], "rangeBytesRequested": fetched})

    if set(found) != {row["sourceElementFileId"] for row in frozen["atomicSourceFiles"]}:
        missing = sorted({row["sourceElementFileId"] for row in frozen["atomicSourceFiles"]} - set(found))
        raise RangeError(f"selected acquisition did not account for all frozen FJ IDs: {missing}")
    result = {
        "revision": f"BodyParts3D-R4-{task}-SELECTED-RANGE-ACQUISITION-v1",
        "task": task,
        "acquiredAt": datetime.now(timezone.utc).isoformat(),
        "frozenSourceSetSha256": sha256_bytes(frozen_path.read_bytes()),
        "frozenMembershipSha256": frozen["frozenMembershipSha256"],
        "fullArchivesDownloaded": False,
        "completeSourceFileCount": len(found),
        "selectedSourceFiles": [found[key][1] for key in sorted(found)],
        "archiveRequests": archive_results,
        "rightsBoundary": {
            "currentOfficialDatabaseLicense": "CC BY 4.0 per official license page last updated 2025-02-27",
            "objHeaderLicenseObserved": "retained per-file; verify header after extraction; archived Release 4.0 OBJ may state CC BY-SA 2.1 Japan",
            "redistributionStatus": "held_until_current_database_terms_and_legacy_OBJ_header_scope_are_reconciled",
        },
    }
    report_path = receipt_path or (ROOT / ("work/evidence/T103/source-acquisition.json" if task == "T103" else "work/evidence/T52/source-acquisition.json"))
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frozen-set", type=Path, default=DEFAULT_FREEZE)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--receipt-path", type=Path, help="optional task-owned acquisition receipt output path")
    args = parser.parse_args()
    try:
        result = acquire(args.frozen_set, args.output_root, args.receipt_path)
    except Exception as exc:
        print(f"T52 selected-source acquisition failed closed: {exc}")
        return 2
    print(json.dumps({"files": result["completeSourceFileCount"], "fullArchivesDownloaded": result["fullArchivesDownloaded"], "archiveTrees": {k: {"rangeBytesRequestedForZipIndex": v["rangeBytesRequestedForZipIndex"], "rangeBytesRequestedForObjMembers": v["rangeBytesRequestedForObjMembers"]} for k, v in result["archiveRequests"].items()}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
