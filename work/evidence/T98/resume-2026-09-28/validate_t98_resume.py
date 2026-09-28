#!/usr/bin/env python3
"""Independent stdlib checks for the T98 evaluated exporter resume artifacts."""

from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import sys
import zlib
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def check(rows, name, ok, evidence):
    rows.append({"name": name, "passed": bool(ok), "evidence": evidence})


def read_glb(path):
    data = path.read_bytes()
    if len(data) < 20:
        raise ValueError("GLB too small")
    magic, version, total = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or total != len(data):
        raise ValueError("GLB header or total length mismatch")
    json_length, json_type = struct.unpack_from("<I4s", data, 12)
    if json_type != b"JSON":
        raise ValueError("first GLB chunk is not JSON")
    json_start = 20
    json_end = json_start + json_length
    document = json.loads(data[json_start:json_end].decode("utf-8").rstrip(" \t\r\n\0"))
    bin_length, bin_type = struct.unpack_from("<I4s", data, json_end)
    if bin_type != b"BIN\0":
        raise ValueError("second GLB chunk is not BIN")
    bin_start = json_end + 8
    binary = data[bin_start:bin_start + bin_length]
    if len(binary) != bin_length or bin_start + bin_length != len(data):
        raise ValueError("GLB BIN bounds mismatch")
    if document.get("buffers", [{}])[0].get("byteLength") > bin_length:
        raise ValueError("GLB buffer byteLength exceeds binary chunk")
    return document, binary, len(data)


def png_stats(path):
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("not PNG")
    pos = 8
    idat = bytearray()
    width = height = bit_depth = color_type = interlace = None
    while pos + 12 <= len(data):
        length = struct.unpack_from(">I", data, pos)[0]
        kind = data[pos + 4:pos + 8]
        content = data[pos + 8:pos + 8 + length]
        if kind == b"IHDR":
            width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(">IIBBBBB", content)
        elif kind == b"IDAT":
            idat.extend(content)
        pos += 12 + length
        if kind == b"IEND":
            break
    if bit_depth != 8 or color_type not in (2, 6) or interlace != 0:
        raise ValueError(f"unsupported PNG layout: depth={bit_depth} colorType={color_type} interlace={interlace}")
    bpp = 3 if color_type == 2 else 4
    stride = width * bpp
    raw = zlib.decompress(idat)
    if len(raw) != height * (stride + 1):
        raise ValueError("PNG decompressed scanline size mismatch")
    previous = bytearray(stride)
    colors = Counter()
    offset = 0
    for _ in range(height):
        filter_type = raw[offset]
        encoded = raw[offset + 1:offset + 1 + stride]
        offset += stride + 1
        row = bytearray(stride)
        for i, value in enumerate(encoded):
            a = row[i - bpp] if i >= bpp else 0
            b = previous[i]
            c = previous[i - bpp] if i >= bpp else 0
            if filter_type == 0:
                predictor = 0
            elif filter_type == 1:
                predictor = a
            elif filter_type == 2:
                predictor = b
            elif filter_type == 3:
                predictor = (a + b) // 2
            elif filter_type == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                predictor = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
            else:
                raise ValueError("unknown PNG filter")
            row[i] = (value + predictor) & 255
        for i in range(0, stride, bpp):
            colors[tuple(row[i:i + bpp])] += 1
        previous = row
    if not colors:
        raise ValueError("empty PNG pixels")
    background, background_count = colors.most_common(1)[0]
    return {
        "width": width,
        "height": height,
        "uniquePixelColors": len(colors),
        "nonBackgroundPixels": width * height - background_count,
        "backgroundColor": list(background),
    }


def main():
    checks = []
    baseline = json.loads((HERE / "baseline.json").read_text(encoding="utf-8"))
    manifest_path = HERE / "evaluated-export-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    freeze = json.loads((ROOT / "work/evidence/T98/representative-sample-freeze.json").read_text(encoding="utf-8"))
    execution = json.loads((ROOT / "work/EXECUTION.json").read_text(encoding="utf-8"))
    row = execution["tasks"]["T98"]

    source_hashes_match = True
    source_hash_details = {}
    for rel in ("atlas-data/source-cache/z-anatomy/t97/Z-Anatomy.zip", "atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend"):
        actual = sha(ROOT / rel)
        expected = baseline["protectedInputs"][rel]["sha256"]
        source_hash_details[rel] = {"expected": expected, "actual": actual, "matches": actual == expected}
        source_hashes_match &= actual == expected
    check(checks, "pinned archive and Startup.blend bytes unchanged", source_hashes_match, source_hash_details)

    runtime = manifest["runtime"]
    binary = runtime["binaryPath"]
    binary_matches = Path(binary).is_file() and sha(Path(binary)) == baseline["currentBlenderSha256"] == runtime["binarySha256"]
    check(checks, "runtime binary path and hash match resume baseline", binary_matches, {"path": binary, "version": runtime["runtimeVersion"], "sha256": runtime["binarySha256"], "baselineSha256": baseline["currentBlenderSha256"], "packageReceiptMatchesRuntimeBinary": runtime["officialPackageReceiptMatchesRuntimeBinary"]})

    frozen_names = [x["sourceObjectLocator"]["objectIdName"] for x in freeze["objects"]]
    rows = manifest["sample"]["objects"]
    names = [x["objectName"] for x in rows]
    anatomical_names = [x["objectName"] for x in rows if x["role"] != "non_anatomical_helper"]
    helper = [x for x in rows if x["role"] == "non_anatomical_helper"]
    locator_ok = len(frozen_names) == 12 and len(set(frozen_names)) == 12 and set(names) == set(frozen_names) and len(rows) == 12 and all(x["locatorNameAndRelationshipMatched"] and x["frozenLocator"]["objectDataBlockPointer"] for x in rows)
    check(checks, "all 12 frozen name/data/parent/collection locators reconciled", locator_ok, {"frozen": len(frozen_names), "evaluated": len(rows), "missing": sorted(set(frozen_names) - set(names)), "extra": sorted(set(names) - set(frozen_names))})
    check(checks, "11 anatomy candidates and helper are counted separately", len(anatomical_names) == 11 and len(helper) == 1 and helper[0]["objectName"] == "Cross Section X" and helper[0]["evaluatedMeshCounts"]["triangles"] == 0 and helper[0]["objectName"] not in anatomical_names, {"anatomicalObjectCount": len(anatomical_names), "helper": helper[0]["objectName"], "helperTriangles": helper[0]["evaluatedMeshCounts"]["triangles"], "glbNames": None})

    glb_path = HERE / "t98-frozen-11-anatomical-objects-evaluated.glb"
    gltf, binary_data, glb_bytes = read_glb(glb_path)
    glb_hash = sha(glb_path)
    expected_export_names = sorted(anatomical_names)
    glb_names = sorted(node["name"] for node in gltf["nodes"])
    mesh_validations = []
    for mesh in gltf["meshes"]:
        primitive = mesh["primitives"][0]
        pos = gltf["accessors"][primitive["attributes"]["POSITION"]]
        nor = gltf["accessors"][primitive["attributes"]["NORMAL"]]
        idx = gltf["accessors"][primitive["indices"]]
        index_view = gltf["bufferViews"][idx["bufferView"]]
        byte_start = index_view.get("byteOffset", 0)
        indices = struct.unpack_from("<" + "I" * idx["count"], binary_data, byte_start)
        mesh_validations.append({"name": mesh["name"], "positionCount": pos["count"], "normalCount": nor["count"], "indexCount": idx["count"], "indicesInRange": bool(indices) and max(indices) < pos["count"], "triangleCount": idx["count"] // 3})
    glb_ok = glb_hash == manifest["export"]["sha256"] and glb_bytes == manifest["export"]["bytes"] and len(gltf["meshes"]) == 11 and glb_names == expected_export_names and all(m["indicesInRange"] and m["positionCount"] == m["normalCount"] == m["indexCount"] and m["indexCount"] % 3 == 0 for m in mesh_validations) and all(node.get("extras", {}).get("role") != "anatomical" for node in gltf["nodes"])
    check(checks, "GLB container, 11 named meshes, accessors, indices, size and SHA-256 valid", glb_ok, {"sha256": glb_hash, "bytes": glb_bytes, "meshes": mesh_validations, "glbNodes": glb_names, "expected": expected_export_names})

    preview_results = []
    for view in manifest["preview"]["views"]:
        path = Path(view["path"])
        stats = png_stats(path)
        file_ok = path.is_file() and path.stat().st_size == view["bytes"] and sha(path) == view["sha256"]
        pixels_ok = stats["width"] == 1100 and stats["height"] == 1100 and stats["uniquePixelColors"] > 16 and stats["nonBackgroundPixels"] > 500
        preview_results.append({"path": str(path.relative_to(ROOT)), "fileHashAndBytesMatch": file_ok, "pixels": stats, "nonBlank": pixels_ok})
    preview_ok = len(preview_results) == 3 and manifest["preview"]["error"] is None and manifest["preview"]["observations"]["engine"] == "BLENDER_EEVEE" and all(x["fileHashAndBytesMatch"] and x["nonBlank"] for x in preview_results)
    check(checks, "three axis previews are real nonblank renders with matching hashes", preview_ok, preview_results)

    by_name = {x["objectName"]: x for x in rows}
    ol = by_name["Clavicular part of deltoid muscle.ol"]
    helper_row = by_name["Cross Section X"]
    shared = {tuple(names) for names in runtime["sampleSharedMeshGroupsByRuntimePointer"]}
    data_name_groups = {}
    for frozen in freeze["objects"]:
        data_name_groups.setdefault(frozen.get("dataPointer"), []).append(frozen["sourceObjectLocator"]["objectIdName"])
    expected_shared = {tuple(sorted(names)) for names in data_name_groups.values() if len(names) > 1}
    expected_negative = set(freeze["caseCoverage"]["negativeSerializedMatrixDeterminantObjects"])
    observed_negative = {x["objectName"] for x in rows if x["worldDeterminant"] < 0}
    modifier_ok = len(ol["modifiers"]) == 2 and {m["type"] for m in ol["modifiers"]} == {"SOLIDIFY", "SUBSURF"} and ol["evaluatedMeshCounts"]["vertices"] > ol["baseMeshCounts"]["vertices"] and ol["evaluatedMeshCounts"]["polygons"] > ol["baseMeshCounts"]["polygons"]
    edge_ok = modifier_ok and len(shared) == 3 and expected_shared == shared and expected_negative <= observed_negative and len(helper_row["constraints"]) == 1 and helper_row["evaluatedMatrixMaxAbsDelta"] == 0 and runtime["depsgraphGeneratedInstanceCount"] > 0 and all(runtime["sampleInstanceReferences"][name] == 0 for name in names)
    check(checks, "Solidify/Subsurf evaluation, shared meshes, negative transforms, constraint helper and depsgraph instances observed", edge_ok, {"olModifierTypes": [m["type"] for m in ol["modifiers"]], "olBaseEvaluatedCounts": {"vertices": [ol["baseMeshCounts"]["vertices"], ol["evaluatedMeshCounts"]["vertices"]], "polygons": [ol["baseMeshCounts"]["polygons"], ol["evaluatedMeshCounts"]["polygons"]]}, "sharedGroups": [list(x) for x in sorted(shared)], "negativeDeterminantCount": len(observed_negative), "constraintHelper": {"name": helper_row["objectName"], "constraint": helper_row["constraints"], "matrixDelta": helper_row["evaluatedMatrixMaxAbsDelta"], "triangles": helper_row["evaluatedMeshCounts"]["triangles"]}, "depsgraphInstanceCount": runtime["depsgraphObjectInstanceCount"], "generatedInstances": runtime["depsgraphGeneratedInstanceCount"], "sampleReferences": runtime["sampleInstanceReferences"]})

    unresolved = runtime["sceneFrameRegistration"] == "unresolved" and runtime["referenceRestPoseId"] is None and runtime["unitSettings"]["sourceDeclaredPhysicalUnit"] is None and runtime["officialPackageReceiptMatchesRuntimeBinary"] is False
    holds_ok = unresolved and manifest["sourceRights"]["sourceOnly"] is True and manifest["sourceRights"]["localUseRights"].startswith("held") and manifest["sourceRights"]["publicRedistribution"] == "held" and manifest["sourceRights"]["humanAnatomyReview"] == "not_performed" and manifest["export"]["exportIsProductAsset"] is False
    check(checks, "frame/unit/rest pose, rights, human review and product status remain held or unresolved", holds_ok, {"frame": runtime["sceneFrameRegistration"], "unit": runtime["unitSettings"], "pose": runtime["referenceRestPoseId"], "rights": manifest["sourceRights"], "productAsset": manifest["export"]["exportIsProductAsset"]})

    t98_ok = row["executionStatus"] == "in_progress" and row["acceptance"] == "partial" and row["progress"]["nextUnit"] == "resolve-frame-unit-pose-side-rights-lineage-and-base-comparison" and row["progress"]["nextUnit"] != "T99" and row["progress"]["gate"]["evaluatedExportVerified"] is True and row["progress"]["gate"]["representativeSurfacePreview"] is True and row["progress"]["gate"]["productionBaseSelected"] is False and row["progress"]["gate"]["nextTaskExecutionStarted"] is False
    check(checks, "EXECUTION remains at same partial T98 unit and does not start T99", t98_ok, {"executionStatus": row["executionStatus"], "acceptance": row["acceptance"], "progress": row["progress"]})

    unchanged = []
    unexpected = []
    allowed = {"work/EXECUTION.json", "work/reports/T98.md", "work/evidence/T98/progress.json", "work/STATUS.md", "work/NEXT.md", "work/task-registry-r15.json"}
    for rel, expected in baseline["protectedInputs"].items():
        actual_path = ROOT / rel
        if not actual_path.is_file():
            unexpected.append({"path": rel, "reason": "missing"})
            continue
        actual = sha(actual_path)
        if actual == expected["sha256"] or rel in allowed:
            unchanged.append(rel)
        else:
            unexpected.append({"path": rel, "expected": expected["sha256"], "actual": actual})
    check(checks, "all resume inputs preserved except declared T98/generated projections", not unexpected, {"protectedInputs": len(baseline["protectedInputs"]), "allowedTaskDeltas": sorted(allowed), "preservedOrAuthorized": len(unchanged), "unexpected": unexpected})

    # `git status --porcelain` can emit either a leading blank status column
    # (`" M path"`) or, in this checkout, a left-aligned status (`"M path"`).
    # Re-parse the frozen raw lines instead of trusting the lossy path list
    # captured by the first baseline writer.
    def status_path(line):
        if len(line) >= 3 and line[2] == " ":
            return line[3:]
        return line[2:]

    old_paths = [status_path(line) for line in baseline["preexistingStatusRaw"].splitlines()]
    old_paths_missing = [p for p in old_paths if not (ROOT / p.rstrip("/")).exists()]
    check(checks, "all pre-existing WIP paths still exist", not old_paths_missing, {"baselineStatusPathCount": baseline["preexistingStatusPathCount"], "missing": old_paths_missing})
    open_sim = baseline["openSim"]
    actual_os_head = subprocess.check_output(["git", "-C", str(ROOT / "OpenSim_Models"), "rev-parse", "HEAD"], text=True).strip()
    actual_os_status = subprocess.check_output(["git", "-C", str(ROOT / "OpenSim_Models"), "status", "--porcelain"], text=True).strip()
    check(checks, "OpenSim_Models HEAD and clean state unchanged", actual_os_head == open_sim["head"] and actual_os_status == open_sim["status"], {"before": open_sim, "after": {"head": actual_os_head, "status": actual_os_status}})

    sync = subprocess.run([sys.executable, str(ROOT / "work/tools/sync_execution.py"), "--check"], cwd=ROOT, text=True, capture_output=True)
    check(checks, "generated EXECUTION projections synchronized", sync.returncode == 0, {"exitCode": sync.returncode, "stdout": sync.stdout.strip(), "stderr": sync.stderr.strip()})
    syntax_details = []
    for path in [HERE / "export_evaluated_t98.py", HERE / "validate_t98_resume.py"]:
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
            syntax_details.append({"path": path.name, "passed": True})
        except SyntaxError as exc:
            syntax_details.append({"path": path.name, "passed": False, "error": str(exc)})
    check(checks, "T98 script and validator syntax", all(x["passed"] for x in syntax_details), syntax_details)

    head_execution = json.loads(subprocess.check_output(["git", "show", baseline["head"] + ":work/EXECUTION.json"], cwd=ROOT, text=True))
    head_tasks = {k: v for k, v in head_execution["tasks"].items() if k != "T98"}
    current_tasks = {k: v for k, v in execution["tasks"].items() if k != "T98"}
    check(checks, "no other EXECUTION task record changed", head_tasks == current_tasks, {"nonT98TaskRecordsMatchBaselineHead": head_tasks == current_tasks})

    result = {
        "schemaVersion": "1.0.0",
        "task": "T98",
        "unit": "resume-evaluated-exporter",
        "result": "passed_with_remaining_gates" if all(x["passed"] for x in checks) else "validation_failed",
        "status": "partial",
        "checks": checks,
        "summary": {"checkCount": len(checks), "passedCount": sum(x["passed"] for x in checks), "failedCount": sum(not x["passed"] for x in checks), "evaluatedExportVerified": glb_ok, "representativeSurfacePreview": preview_ok, "productionBaseSelected": False, "nextTaskStarted": False},
    }
    out = HERE / "resume-validation.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    if not all(x["passed"] for x in checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
