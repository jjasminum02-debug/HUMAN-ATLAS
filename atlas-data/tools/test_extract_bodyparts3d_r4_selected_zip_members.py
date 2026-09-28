from __future__ import annotations

import io
import struct
import unittest
import zipfile
from unittest.mock import patch

import extract_bodyparts3d_r4_selected_zip_members as selected


class SelectedZipRangeTests(unittest.TestCase):
    def make_archive(self) -> tuple[bytes, zipfile.ZipFile]:
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("FJ1555.obj", b"# BodyParts3D\nvertex payload\n")
            archive.writestr("isa_BP3D_4.0_obj_99/FJ1473M.obj", b"# BodyParts3D M fixture\n")
            archive.writestr("not-an-OBJ.txt", b"index")
        payload = output.getvalue()
        return payload, zipfile.ZipFile(io.BytesIO(payload))

    def test_reads_only_member_ranges_and_checks_crc(self):
        raw, archive = self.make_archive()
        info = archive.getinfo("FJ1555.obj")
        cd_offset = archive.start_dir
        cd_size = len(raw[cd_offset : raw.find(b"PK\x05\x06")])
        central = raw[cd_offset : cd_offset + cd_size]
        entries = selected.parse_central_directory(central, len(archive.infolist()))
        archive.close()
        calls = []

        def fake_range(_url, start, end, _etag):
            calls.append((start, end))
            return raw[start : end + 1], {"etag": '"fixture"'}

        with patch.object(selected, "fetch_range", side_effect=fake_range):
            data, range_bytes = selected.selected_member_bytes(
                "https://fixture.invalid/archive.zip",
                {"etag": '"fixture"'},
                entries["FJ1555"],
            )
        self.assertEqual(data, b"# BodyParts3D\nvertex payload\n")
        self.assertEqual(calls[-1][1] - calls[-1][0] + 1, info.compress_size)
        self.assertGreater(range_bytes, info.compress_size)
        self.assertLessEqual(sum(end - start + 1 for start, end in calls), range_bytes)

    def test_central_directory_recognizes_suffix_m_as_a_distinct_fj_id(self):
        raw, archive = self.make_archive()
        cd_offset = archive.start_dir
        cd_size = len(raw[cd_offset : raw.find(b"PK\x05\x06")])
        entries = selected.parse_central_directory(raw[cd_offset : cd_offset + cd_size], len(archive.infolist()))
        archive.close()
        self.assertIn("FJ1473M", entries)
        self.assertEqual(entries["FJ1473M"]["memberPath"], "isa_BP3D_4.0_obj_99/FJ1473M.obj")

    def test_rejects_nonpartial_http_response(self):
        from unittest.mock import MagicMock

        response = MagicMock()
        response.status = 200
        response.headers = {"Content-Length": "10"}
        response.read.return_value = b"0123456789"
        response.__enter__.return_value = response
        with patch.object(selected.urllib.request, "urlopen", return_value=response):
            with self.assertRaisesRegex(selected.RangeError, "full-archive fallback is forbidden"):
                selected.fetch_range("https://fixture.invalid/a.zip", 0, 9, '"fixture"')

    def test_eocd_rejects_zip64_sentinel(self):
        # EOCD with the entry-count/offset sentinel is intentionally unsupported.
        record = struct.pack("<4s4H2LH", selected.EOCD, 0, 0, 0xFFFF, 0xFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0)
        with self.assertRaisesRegex(selected.RangeError, "ZIP64"):
            selected.parse_eocd(record, len(record))

    def test_frozen_source_guard_rejects_unexpected_revision(self):
        import json
        from pathlib import Path
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "freeze.json"
            path.write_text(json.dumps({"revision": "fixture", "atomicSourceFiles": []}), encoding="utf-8")
            with self.assertRaisesRegex(selected.RangeError, "immutable T52"):
                selected.load_frozen(path)

    def test_t103_freeze_accepts_only_its_exact_ten_ids(self):
        import hashlib
        import json
        from pathlib import Path
        import tempfile

        rows = [{"sourceElementFileId": fid, "regionCandidates": ["upper-limb"],
                 "expectedArchiveTrees": ["IS-A"], "preferredArchiveTree": "IS-A"} for fid in selected.T103_IDS]
        canonical = "\n".join(f"{row['sourceElementFileId']}|upper-limb|IS-A" for row in rows) + "\n"
        freeze = {"revision": "BodyParts3D-R4-T103-FROZEN-SOURCE-SET-v1", "task": "T103",
                  "status": "frozen_before_mesh_acquisition", "atomicSourceFiles": rows,
                  "frozenMembershipSha256": hashlib.sha256(canonical.encode()).hexdigest()}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "freeze.json"
            path.write_text(json.dumps(freeze), encoding="utf-8")
            self.assertEqual(selected.load_frozen(path)["task"], "T103")
            freeze["atomicSourceFiles"].pop()
            canonical = "\n".join(f"{row['sourceElementFileId']}|upper-limb|IS-A" for row in freeze["atomicSourceFiles"]) + "\n"
            freeze["frozenMembershipSha256"] = hashlib.sha256(canonical.encode()).hexdigest()
            path.write_text(json.dumps(freeze), encoding="utf-8")
            with self.assertRaisesRegex(selected.RangeError, "exact ten-ID scope"):
                selected.load_frozen(path)


if __name__ == "__main__":
    unittest.main()
