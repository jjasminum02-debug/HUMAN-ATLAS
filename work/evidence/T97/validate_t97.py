#!/usr/bin/env python3
"""Fail-closed evidence validation for the bounded T97 Z-Anatomy inspection."""

import hashlib
import json
import os
import re
import stat
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
E = ROOT / "work/evidence/T97"
CACHE = ROOT / "atlas-data/source-cache/z-anatomy/t97"
EXPECTED_NAMES = [
    "Latissimus dorsi muscle.el", "Latissimus dorsi muscle.er",
    "Latissimus dorsi muscle.l", "Latissimus dorsi muscle.ol",
    "Latissimus dorsi muscle.or", "Latissimus dorsi muscle.r",
]


def fail(message):
    raise SystemExit("T97 VALIDATION FAIL: " + message)


def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(name):
    return json.loads((E / name).read_text(encoding="utf-8"))


def main():
    checks = []
    receipt = load("archive-acquisition.json")
    archive = ROOT / receipt["cacheRelativePath"]
    if receipt["repository"] != "Z-Anatomy/Models-of-human-anatomy" or receipt["commit"] != "c7010a903b75a2fd24a13b1c2c4c3546a9223780":
        fail("pinned source identity changed")
    if receipt["downloadedBytes"] > 120_000_000 or archive.stat().st_size != receipt["downloadedBytes"]:
        fail("download transfer cap/size mismatch")
    if sha256_file(archive) != receipt["sha256"]:
        fail("source archive hash mismatch")
    checks.append("pinned archive URL/commit/response/bytes/SHA256")

    member = load("archive-member-inventory.json")
    if not member["receiptMatches"] or member["preflight"]["advertisedUnpackedBytes"] > 1_000_000_000:
        fail("unpack cap or acquisition receipt mismatch")
    if member["preflight"]["fileCount"] > 10_000 or member["preflight"]["symlinkEntries"]:
        fail("archive member count or symlink policy")
    if member["preflight"]["allMemberCrcsVerifiedByZipfile"] is not True:
        fail("archive CRCs were not all verified")
    extracted = CACHE / "extracted"
    actual_files = []
    actual_bytes = 0
    for info in member["members"]:
        if info["kind"] != "file":
            continue
        rel = Path(info["archivePath"])
        if rel.is_absolute() or ".." in rel.parts or "\\" in info["archivePath"]:
            fail("unsafe archive relative path")
        path = extracted.joinpath(*rel.parts)
        if not path.resolve().is_relative_to(extracted.resolve()) or path.is_symlink() or not path.is_file():
            fail("extracted member missing, escaped, or symlinked")
        if path.stat().st_size != info["uncompressedBytes"] or sha256_file(path) != info["sha256"]:
            fail("extracted member size/SHA mismatch: " + info["archivePath"])
        actual_files.append(path)
        actual_bytes += path.stat().st_size
    if len(actual_files) != member["preflight"]["actualExtractedFiles"] or actual_bytes != member["preflight"]["actualExtractedBytes"]:
        fail("extracted file inventory totals differ")
    with zipfile.ZipFile(archive) as zf:
        if zf.testzip() is not None:
            fail("zip CRC recheck failed")
        if len(zf.infolist()) > 10_000:
            fail("archive member cap exceeded")
        if sum(i.file_size for i in zf.infolist()) > 1_000_000_000:
            fail("archive unpack cap exceeded")
    checks.append("archive path/symlink/file-count/unpacked-byte/CRC/member SHA preflight")

    inv = load("blender-object-inventory.json")
    if inv["sourceFileSha256"] != next(x["sha256"] for x in member["members"] if x["archivePath"] == "Z-Anatomy/Startup.blend"):
        fail("binary inventory source hash does not match archive member")
    if (inv["objectCount"], inv["meshDataBlockCount"], inv["collectionCount"], inv["sceneCount"]) != (7184, 2910, 1945, 1):
        fail("archive-wide ID inventory counts changed")
    candidates = inv["candidateSearchObjects"]
    if [x["objectName"] for x in candidates] != EXPECTED_NAMES:
        fail("candidate object-name inventory changed")
    if inv["candidateSearchCount"] != 6 or inv["sceneRootCollections"][0]["masterCollectionName"] != "Scene Collection":
        fail("candidate count or rooted scene metadata invalid")
    target_layouts = {"Object", "Mesh", "Collection", "Scene", "MVert", "MLoop", "MPoly"}
    bad_target_layouts = [x["struct"] for x in inv["layoutValidation"]["calculatedSizeMismatches"] if x["struct"] in target_layouts]
    if bad_target_layouts:
        fail("target SDNA layout size mismatch: " + str(bad_target_layouts))
    object_names = set(inv["dataBlockNames"].get("Object", []))
    mesh_names = set(inv["dataBlockNames"].get("Mesh", []))
    if not set(EXPECTED_NAMES).issubset(object_names):
        fail("target object names missing from archive-wide object-name index")
    if not {"Latissimus dorsi muscle", "Latissimus dorsi muscle.e", "Latissimus dorsi muscle.o"}.issubset(mesh_names):
        fail("target mesh data-block names missing")
    if any(not x["collectionPaths"] for x in candidates):
        fail("one or more candidate object paths are unresolved")
    checks.append("read-only full datablock-name index and six exact object IDs/rooted paths")

    extraction = load("latissimus-extraction.json")
    objects = extraction["objects"]
    if [x["objectName"] for x in objects] != EXPECTED_NAMES or extraction["candidateCount"] != 6:
        fail("extracted candidate set is not the exact six-object subset")
    if extraction["distinctMeshDataBlockCount"] != 3:
        fail("expected three shared source mesh data blocks")
    if extraction["promotion"] != {"mesh": "none", "canonicalBinding": "none", "learnerScene": "none", "rights": "held", "humanReview": "not_performed"}:
        fail("source-only/rights/human-review holds changed")
    expected_parents = {
        "Latissimus dorsi muscle.el": "Scapula.l",
        "Latissimus dorsi muscle.er": "Scapula.r",
        "Latissimus dorsi muscle.l": "Hypaxial muscles of back.g",
        "Latissimus dorsi muscle.ol": "Hip bone.l",
        "Latissimus dorsi muscle.or": "Hip bone.r",
        "Latissimus dorsi muscle.r": "Hypaxial muscles of back.g",
    }
    for row in objects:
        if row["parentObjectName"] != expected_parents[row["objectName"]]:
            fail("candidate parent ancestry mismatch: " + row["objectName"])
        lineage = row["sourceAncestry"]
        if lineage["repository"] != receipt["repository"] or lineage["commit"] != receipt["commit"] or lineage["archiveSha256"] != receipt["sha256"]:
            fail("candidate source ancestry does not trace to the pinned archive")
        if lineage["objectIDName"] != row["rawBlenderIDName"] or lineage["objectIDPointer"] != row["objectIDPointer"] or lineage["meshDataBlockName"] != row["meshDataBlockName"]:
            fail("candidate source ancestry locator mismatch")
        if "not located" not in lineage["objectSpecificUpstreamCrosswalk"]:
            fail("unverified object-to-upstream crosswalk was elevated")
        if not re.fullmatch(r"[0-9a-f]{64}", row["geometrySha256"]):
            fail("geometry hash malformed")
        if row["partInterpretation"].startswith("unresolved") is not True:
            fail("part interpretation must remain unresolved")
        props_text = json.dumps(row["customPropertiesReadOnly"], ensure_ascii=False)
        if "TA2:2231" in props_text or "FMA:2231" in props_text:
            fail("candidate custom property contains a canonical crosswalk that this inspection did not review")
        obj_path = ROOT / row["qaObjRelativePath"]
        if not obj_path.resolve().is_relative_to(CACHE.resolve()) or obj_path.is_symlink():
            fail("QA derivative outside ignored cache or symlinked")
        if sha256_file(obj_path) != row["qaObjSha256"] or obj_path.stat().st_size != row["qaObjBytes"]:
            fail("QA OBJ receipt mismatch")
        vertex_count = sum(line.startswith("v ") for line in obj_path.read_text(encoding="ascii").splitlines())
        face_count = sum(line.startswith("f ") for line in obj_path.read_text(encoding="ascii").splitlines())
        if vertex_count != row["meshCounts"]["vertices"] or face_count != row["triangleCountForQaObj"]:
            fail("QA OBJ geometry count mismatch")
    main_l = next(x for x in objects if x["objectName"] == "Latissimus dorsi muscle.l")
    main_r = next(x for x in objects if x["objectName"] == "Latissimus dorsi muscle.r")
    if main_l["meshDataBlockPointer"] != main_r["meshDataBlockPointer"] or main_l["geometrySha256"] != main_r["geometrySha256"]:
        fail("bilateral primary surfaces do not share expected source mesh datablock")
    if main_l["objectMatrixRowMajor"][0] >= 0 or main_r["objectMatrixRowMajor"][0] <= 0:
        fail("bilateral saved object matrices do not show opposing X reflection")
    checks.append("six-object subset, parent/collection ancestry, source geometry/object transform hashes, bilateral mesh sharing")

    preview = load("surface-preview.json")
    if preview["sourceScriptsOrDriversExecuted"] or preview["sourceBlenderFileOpened"]:
        fail("preview indicates archive code execution or source blend load")
    if len(preview["inputObjects"]) != 6:
        fail("preview does not use exact six-object candidate subset")
    for name, view in preview["renders"].items():
        path = E / view["file"]
        raw = path.read_bytes()
        if not raw.startswith(b"\x89PNG\r\n\x1a\n") or len(raw) < 2048:
            fail("surface preview PNG malformed or empty: " + name)
        width, height = struct.unpack(">II", raw[16:24])
        if (width, height) != (720, 720) or sha256_file(path) != view["sha256"] or view["depthBufferWrites"] <= 0:
            fail("surface render hash/dimensions/depth result mismatch: " + name)
    checks.append("actual three-view source-surface raster previews and hashes")

    reproducibility = load("reproducibility.json")
    if reproducibility["result"] != "reproducible" or not reproducibility["allOutputHashesIdentical"]:
        fail("deterministic rerun failed")
    if reproducibility["outputSha256Before"] != reproducibility["outputSha256After"]:
        fail("before/after rerun hashes differ")
    for relpath, expected in reproducibility["outputSha256After"].items():
        if sha256_file(ROOT / relpath) != expected:
            fail("reproducibility receipt no longer matches output: " + relpath)
    checks.append("inventory/extraction/render pipeline reruns with identical output hashes")

    blender = load("blender-load-attempts.json")
    if any("--disable-autoexec" not in attempt["commandFlags"] for attempt in blender["attempts"]):
        fail("a Blender attempt did not disable embedded autoexec")
    if any(attempt["exitCode"] != 139 for attempt in blender["attempts"]):
        fail("Blender attempt outcome changed")
    if sha256_file(Path(blender["attempts"][-1]["crashLogPath"])) != blender["attempts"][-1]["crashLogSha256"]:
        fail("captured current Blender crash log does not match receipt")
    checks.append("Blender startup failure is recorded; archive autoexec remains disabled")

    baseline = load("start-baseline.json")
    for path, expected in baseline["inputSha256"].items():
        if path in {"work/STATUS.md", "work/task-registry-r15.json"}:
            continue
        actual = sha256_file(ROOT / path)
        if expected != actual:
            fail("T97 input changed during execution: " + path)
    for path in ("work/evidence/T93/decision.json", "work/evidence/T94/decision.json"):
        decision = json.loads((ROOT / path).read_text(encoding="utf-8"))
        if decision.get("result") != "no_exact_source_found":
            fail("historic no_exact_source_found state was modified: " + path)
    registry = json.loads((ROOT / "work/task-registry-r15.json").read_text(encoding="utf-8"))
    if registry["taskStatuses"].get("T97") != "passed_with_gaps":
        fail("R15 T97 task status was not updated")
    if registry["taskStatuses"].get("T93") != "passed_with_gaps" or registry["taskStatuses"].get("T94") != "passed_with_gaps":
        fail("T93/T94 registry task statuses changed")
    if registry["taskStatuses"].get("T101") != "planned_not_started":
        fail("next task was started")
    status_text = (ROOT / "work/STATUS.md").read_text(encoding="utf-8")
    if "CURRENT_TASK: T97 - passed_with_gaps" not in status_text or "NEXT_TASK: T101 / Luna Max" not in status_text or "LAST_REPORT: work/reports/T97.md" not in status_text:
        fail("shared STATUS current task/report/next task fields are stale")
    if "## T97 — pinned Z-Anatomy latissimus object candidate review" not in status_text:
        fail("T97 STATUS report section missing")
    checks.append("T93/T94 historical inputs/no_exact_source_found and registry states are preserved; T101 remains planned")

    ignore = subprocess.run(["git", "check-ignore", "-q", "atlas-data/source-cache/z-anatomy/t97/Z-Anatomy.zip"], cwd=ROOT, check=False).returncode
    if ignore != 0:
        fail("large archive cache is not ignored")
    checks.append("large source archive and QA OBJ derivatives remain in ignored cache")

    opensim = subprocess.run(["git", "-C", str(ROOT / "OpenSim_Models"), "status", "--porcelain"], capture_output=True, text=True, check=True)
    opensim_head = subprocess.run(["git", "-C", str(ROOT / "OpenSim_Models"), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    if opensim.stdout or opensim_head != baseline["startingOpenSimHead"]:
        fail("OpenSim_Models changed")
    checks.append("OpenSim_Models HEAD and clean state preserved")

    status_proc = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True, check=True)
    current_paths = {line[3:] for line in status_proc.stdout.splitlines() if len(line) >= 4}
    missing_preexisting = []
    preserved_preexisting = []
    for row in baseline["startingUserWipPaths"]:
        rel = row[3:]
        if rel == "work/evidence/T97" or rel.startswith("work/evidence/T97/"):
            continue  # T97-owned baseline evidence is expected to be committed.
        found = rel in current_paths or (rel.endswith("/") and any(p.startswith(rel) for p in current_paths))
        if found:
            preserved_preexisting.append(rel)
        else:
            missing_preexisting.append(rel)
    if missing_preexisting:
        fail("pre-existing user WIP path disappeared from working tree status: " + str(missing_preexisting))
    preservation = {
        "task": "T97",
        "startingHead": baseline["startingHead"],
        "startingStatusPorcelainSha256": baseline["startingWorktreeStatusPorcelainSha256"],
        "startingPreexistingWipPathCount": baseline["startingWorktreeChangedPathCount"],
        "taskOwnedBaselineEvidencePathExcludedFromWipComparison": "work/evidence/T97/",
        "preservedPreexistingWipPathsChecked": len(preserved_preexisting),
        "missingPreexistingWipPaths": missing_preexisting,
        "allOtherPreexistingWipPathsStillPresent": not missing_preexisting,
        "OpenSimHead": opensim_head,
        "OpenSimClean": not bool(opensim.stdout),
        "currentStatusPorcelainSha256": hashlib.sha256(status_proc.stdout.encode()).hexdigest(),
    }
    (E / "preservation.json").write_text(json.dumps(preservation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    checks.append("pre-existing user WIP paths preserved; T97-owned baseline evidence identified separately")

    out = {
        "task": "T97",
        "result": "passed_with_gaps",
        "validatedAt": "2026-09-28",
        "checks": checks,
        "unresolved": [
            "TA2:2231-to-Blender-object identity is not established beyond candidate names; no canonical binding was created",
            "the literal .e/.o object suffix roles remain unresolved; parent/collection clues were recorded without origin/insertion relabeling",
            "file-level rights, T50 frame compatibility, learner scene/selection eligibility and human review remain held",
            "official Blender process exited 139; source-surface preview was independently rasterized from binary geometry arrays and saved object matrices"
        ]
    }
    (E / "validation.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import struct
    main()
