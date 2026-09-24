#!/usr/bin/env python3
"""Task-specific structural and preservation verification for the T02 pilot."""
from __future__ import annotations
import hashlib
import json
import re
import struct
import subprocess
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "work/evidence/T02"


def read_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def project_path(value: str) -> Path:
    prefix = "HUMAN ATLAS/"
    if value.startswith(prefix):
        value = value[len(prefix):]
    return ROOT / value


checks = []

def check(name: str, passed: bool, observed):
    checks.append({"name": name, "passed": bool(passed), "observed": observed})

manifest = read_json("atlas-data/manifests/assets.json")
transfer = read_json("work/evidence/T02/source-transfer.json")
inspection = read_json("work/evidence/T02/geometry-inspection.json")
crosswalk = read_json("work/evidence/T02/source-crosswalk.json")

# Official source and bounded transport record.
source = manifest["source"]
check("official_release_and_bounded_range_transfer",
      source["sourceId"] == "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0"
      and source["fullArchiveSavedLocally"] is False
      and transfer["retrieved_transport"].startswith("HTTP Range")
      and transfer["archive_size_bytes"] == 142903898
      and transfer["range_request_bytes_including_retries_and_probe"] < transfer["archive_size_bytes"]
      and transfer["range_request_bytes_including_retries_and_probe"] <= transfer["range_transfer_budget_bytes"],
      {"archive_bytes": transfer["archive_size_bytes"],
       "range_bytes": transfer["range_request_bytes_including_retries_and_probe"],
       "full_zip_saved": source["fullArchiveSavedLocally"]})

# Rights notes and preservation of the archived OBJ notices.
license_record = manifest["license"]
check("archive_license_and_embedded_notice_recorded",
      license_record["archivePageLicense"] == "CC BY 4.0"
      and "CC Attribution 4.0 International" in license_record["archivePageRequiredCredit"]
      and "CC BY-SA 2.1 Japan" in license_record["embeddedObjHeaderNotice"]
      and "embedded_legacy_notice_preserved" in license_record["rightsStatus"]
      and license_record["publicReleasePerformed"] is False,
      {"archive_license": license_record["archivePageLicense"],
       "required_credit": license_record["archivePageRequiredCredit"],
       "legacy_notice": license_record["embeddedObjHeaderNotice"],
       "public_release": license_record["publicReleasePerformed"]})

# All six concepts are mapped; gastrocnemius remains two explicit head records.
expected_concepts = {"gastrocnemius", "soleus", "tibialis_anterior", "tibialis_posterior", "fibularis_longus", "fibularis_brevis"}
pilot_rows = crosswalk["pilot_muscles"]
concepts = {row["pilot_concept"] for row in pilot_rows}
gastroc = [row for row in pilot_rows if row["pilot_concept"] == "gastrocnemius"]
check("six_pilot_concepts_have_traceable_source_ids",
      concepts == expected_concepts and len(pilot_rows) == 7
      and len(gastroc) == 2
      and all(row["concept_id"].startswith("FMA") and row["representation_id"].startswith("BP") and row["element_file_id"].startswith("FJ") for row in pilot_rows),
      {"concepts": sorted(concepts), "muscle_mesh_rows": len(pilot_rows), "gastrocnemius_parts": [row["part"] for row in gastroc]})

# Crosswalk inventory has nine candidate bones, with four acquired and five availability-only.
bones = crosswalk["region_bone_inventory"]
acquired_bones = [row for row in bones if row["availability"] == "subset_acquired"]
listed_bones = [row for row in bones if row["availability"] == "listed_mapped_not_acquired"]
check("related_bone_crosswalk_counts",
      len(bones) == 9 and len(acquired_bones) == 4 and len(listed_bones) == 5,
      {"total": len(bones), "acquired": len(acquired_bones), "listed_only": len(listed_bones)})

# Transform is an orientation-preserving right-handed rotation plus mm-to-m scale.
g = manifest["geometry"]
transform = g["sourceToAtlasTransform"]
matrix = transform["matrix"]
det = (matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
       - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
       + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0]))
rotation_det = det / (0.001 ** 3)
check("coordinate_unit_axis_transform_and_pose_limit",
      g["sourceUnit"] == "mm" and g["atlasInternalUnit"] == "m"
      and transform["formula"] == "[x_atlas,y_atlas,z_atlas]m = [x_source,z_source,-y_source]mm / 1000"
      and abs(rotation_det - 1.0) < 1e-12 and transform["rotationDeterminant"] == 1
      and "do not label this as a verified standardized anatomical pose" in g["pose"]["description"],
      {"formula": transform["formula"], "computed_full_transform_determinant": det,
       "computed_rotation_determinant": rotation_det, "pose": g["pose"]["id"]})

# Manifest, transfer, inspection, and actual local OBJ bytes agree.
asset_records = manifest["acquiredAssets"]
transfer_records = transfer["assets"]
inspection_records = inspection["assets"]
by_file_transfer = {Path(row["archive_member"]).name: row for row in transfer_records}
by_file_inspection = {Path(row["file"]).name: row for row in inspection_records}
by_file_manifest = {Path(row["file"]).name: row for row in asset_records}
asset_names = set(by_file_transfer)
all_asset_consistent = (asset_names == set(by_file_inspection) == set(by_file_manifest) and len(asset_names) == 11)
observed_assets = []
all_asset_consistent = all_asset_consistent and len(list((ROOT / manifest["assetFolder"]).glob("FJ*.obj"))) == 11
for name in sorted(asset_names):
    t = by_file_transfer[name]
    i = by_file_inspection[name]
    m = by_file_manifest[name]
    local = project_path(t["file"])
    same = local.is_file()
    if same:
        actual_sha = digest(local)
        actual_size = local.stat().st_size
        same = (actual_sha == t["sha256"] == i["sha256"] == m["sha256"]
                and actual_size == t["bytes"] == i["bytes"] == m["bytes"]
                and i["vertex_count"] > 0 and i["polygon_count"] > 0
                and i["right_side_coordinate_check"] == "pass_source_x_max_lt_0"
                and i["measured_source_bounds_mm"]["max_mm"][0] < 0
                and len(t["zip_crc32"]) == 8)
        all_asset_consistent = all_asset_consistent and same
        observed_assets.append({"file": name, "bytes": actual_size, "sha256": actual_sha,
                                "zip_crc32": t["zip_crc32"], "vertices": i["vertex_count"],
                                "faces": i["polygon_count"], "source_x_max_mm": i["measured_source_bounds_mm"]["max_mm"][0]})
    else:
        all_asset_consistent = False
        observed_assets.append({"file": name, "missing": True})
check("all_eleven_obj_hashes_headers_geometry_and_right_side",
      all_asset_consistent and inspection["summary"]["all_vertices_strictly_in_right_half_space"] is True,
      {"asset_count": len(asset_names), "total_bytes": inspection["summary"]["total_bytes"],
       "total_vertices": inspection["summary"]["total_vertices"],
       "total_polygon_faces": inspection["summary"]["total_polygons"], "assets": observed_assets})

# Every archived face record is triangular, so the viewer's face count maps 1:1 to source rows.
face_arity = {}
for name in sorted(asset_names):
    arities = []
    with project_path(by_file_transfer[name]["file"]).open(encoding="ascii", errors="replace") as obj:
        for line in obj:
            if line.startswith("f "):
                arities.append(len(line.split()) - 1)
    face_arity[name] = {"face_records": len(arities), "min_vertices": min(arities), "max_vertices": max(arities)}
check("source_obj_faces_are_triangles_for_viewer_count",
      all(v["min_vertices"] == v["max_vertices"] == 3 for v in face_arity.values())
      and sum(v["face_records"] for v in face_arity.values()) == inspection["summary"]["total_polygons"],
      {"total_face_records": sum(v["face_records"] for v in face_arity.values()), "assets": face_arity})

# Original OBJ comments remain present in every exact archived local member.
legacy_notice = b"Creative Commons Attribution-Share Alike 2.1 Japan"
comment_assets = []
for name in sorted(asset_names):
    raw = project_path(by_file_transfer[name]["file"]).read_bytes()
    if legacy_notice in raw:
        comment_assets.append(name)
all_comments = all(legacy_notice in project_path(by_file_transfer[name]["file"]).read_bytes() for name in asset_names)
check("legacy_obj_license_comment_preserved", all_comments,
      {"assets_with_legacy_comment": comment_assets})

# PNG chunks: signature, IHDR size, each CRC, and terminal IEND.
png_path = EVIDENCE / "calf-viewer-trial.png"
png = png_path.read_bytes()
png_valid = png[:8] == b"\x89PNG\r\n\x1a\n"
width = height = None
chunks = []
offset = 8
saw_iend = False
while png_valid and offset + 12 <= len(png):
    length = struct.unpack(">I", png[offset:offset + 4])[0]
    kind = png[offset + 4:offset + 8]
    end = offset + 12 + length
    if end > len(png):
        png_valid = False
        break
    payload = png[offset + 8:offset + 8 + length]
    stored_crc = struct.unpack(">I", png[offset + 8 + length:end])[0]
    actual_crc = zlib.crc32(kind + payload) & 0xffffffff
    chunks.append(kind.decode("ascii", errors="replace"))
    if stored_crc != actual_crc:
        png_valid = False
        break
    if kind == b"IHDR" and length == 13:
        width, height = struct.unpack(">II", payload[:8])
    if kind == b"IEND":
        saw_iend = length == 0 and end == len(png)
        offset = end
        break
    offset = end
png_valid = png_valid and saw_iend and (width, height) == (1544, 902)
check("viewer_png_crc_dimensions_and_terminal_chunk",
      png_valid,
      {"valid": png_valid, "width": width, "height": height, "bytes": len(png), "chunks": chunks})

# UI/device/error evidence and accessible console capture.
viewer_log = (EVIDENCE / "viewer-trial.log").read_text(encoding="utf-8")
viewer_log_lower = viewer_log.lower()
console = read_json("work/evidence/T02/browser-console.json")
check("actual_viewer_trial_and_reference_device_recorded",
      "11/11" in viewer_log and "810 x 752 css px" in viewer_log_lower and "devicepixelratio 2" in viewer_log_lower
      and "runtime/load error counter: 0" in viewer_log_lower and "dragged the scene" in viewer_log_lower
      and "scrolled over the canvas" in viewer_log_lower and console["entries"] == [],
      {"console_entries": len(console["entries"]), "device": "macOS desktop / Codex In-app Browser / 810x752 CSS px / DPR 2",
       "record_file": "work/evidence/T02/viewer-trial.log"})

# User instructions/design files match the task-start hashes; OpenSim checkout is clean and untouched.
preservation = read_json("work/evidence/T02/preexisting-files-check.json")
check("preexisting_readme_instructions_and_design_unchanged",
      preservation["all_unchanged"] and len(preservation["files"]) == 10,
      {"files_checked": len(preservation["files"]), "all_unchanged": preservation["all_unchanged"]})
opensim_record = (EVIDENCE / "opensim-comparison.txt").read_text(encoding="utf-8")
opensim = ROOT / "OpenSim_Models"
open_head = subprocess.run(["git", "-C", str(opensim), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
open_status = subprocess.run(["git", "-C", str(opensim), "status", "--short", "--branch"], capture_output=True, text=True, check=True).stdout.strip()
open_diff = subprocess.run(["git", "-C", str(opensim), "diff", "--quiet", "HEAD", "--"])
model_path = opensim / "Models/Rajagopal/Rajagopal2016.osim"
expected_open_head = "d9b05d470b1a481c222372c85b75772faf8f7792"
check("opensim_original_checkout_read_only",
      open_head == expected_open_head and open_status.splitlines() == ["## master...origin/master"]
      and open_diff.returncode == 0 and digest(model_path) in opensim_record
      and all(f"- {n}: present" in opensim_record for n in ["gasmed_r", "gaslat_r", "soleus_r", "tibant_r", "tibpost_r", "perlong_r", "perbrev_r"]),
      {"head": open_head, "status": open_status, "diff_exit": open_diff.returncode,
       "model_sha256": digest(model_path)})

# Work-state records and next task are complete, with no auto-start.
task_text = (ROOT / "work/tasks/T02.md").read_text(encoding="utf-8")
status_text = (ROOT / "work/STATUS.md").read_text(encoding="utf-8")
report_text = (ROOT / "work/reports/T02.md").read_text(encoding="utf-8")
check("task_report_status_and_next_task_recorded",
      "상태: complete" in task_text and "CURRENT_TASK: 없음" in status_text
      and "NEXT_TASK: T03" in status_text and "T03 — 공통 스키마와 검증기" in report_text,
      {"T02": "complete", "next_task": "T03", "automatic_start": False})

result = {
    "task": "T02",
    "checked_at_local_date": "2026-09-25",
    "command": "python3 work/evidence/T02/validate_t02.py",
    "passed": all(row["passed"] for row in checks),
    "checks_passed": sum(row["passed"] for row in checks),
    "checks_total": len(checks),
    "checks": checks,
    "interpretation": "Technical source/hash/geometry/coordinate/viewer/preservation checks only. Not an anatomy, attachment, clinical, or app approval."
}
out = EVIDENCE / "validation.json"
out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"passed": result["passed"], "checks_passed": result["checks_passed"], "checks_total": result["checks_total"],
                  "failed": [c["name"] for c in checks if not c["passed"]], "result": str(out)}, ensure_ascii=False, indent=2))
if not result["passed"]:
    raise SystemExit(1)
