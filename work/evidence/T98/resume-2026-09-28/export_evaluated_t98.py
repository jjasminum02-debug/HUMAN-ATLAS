#!/usr/bin/env python3
"""Read-only evaluated-geometry spike for the already frozen T98 sample.

Run only inside the approved Blender process with --factory-startup and
--disable-autoexec. This script never saves the source .blend file.
"""

import bpy
import argparse
import hashlib
import json
import math
import os
import resource
import struct
import sys
import time
from pathlib import Path
from mathutils import Vector


def cli_args():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--freeze-json", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--source-blend", required=True)
    parsed = parser.parse_args(args)
    return Path(parsed.repo_root).resolve(), Path(parsed.freeze_json).resolve(), Path(parsed.output_dir).resolve(), Path(parsed.source_blend).resolve()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def json_write(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def matrix_rows(matrix):
    return [[float(matrix[r][c]) for c in range(4)] for r in range(4)]


def matrix_delta(a, b):
    return max(abs(float(a[r][c]) - float(b[r][c])) for r in range(4) for c in range(4))


def v3(v):
    return [float(v.x), float(v.y), float(v.z)]


def world_bounds(points):
    if not points:
        return None
    return {
        "min": [min(p[i] for p in points) for i in range(3)],
        "max": [max(p[i] for p in points) for i in range(3)],
    }


def canonical_geometry_hash(points, triangles):
    h = hashlib.sha256()
    h.update(b"HUMAN-ATLAS-T98-EVALUATED-WORLD-GEOMETRY-V1\0")
    h.update(struct.pack("<QQ", len(points), len(triangles)))
    for p in points:
        h.update(struct.pack("<3d", *p))
    for tri in triangles:
        h.update(struct.pack("<3I", *tri))
    return h.hexdigest()


def flat_triangle_arrays(points, triangles):
    positions = []
    normals = []
    degenerates = 0
    for tri in triangles:
        a, b, c = (Vector(points[i]) for i in tri)
        n = (b - a).cross(c - a)
        if n.length_squared < 1e-30:
            degenerates += 1
            normal = Vector((0.0, 0.0, 0.0))
        else:
            normal = n.normalized()
        for point in (a, b, c):
            positions.extend((float(point.x), float(point.y), float(point.z)))
            normals.extend((float(normal.x), float(normal.y), float(normal.z)))
    indices = list(range(len(positions) // 3))
    return positions, normals, indices, degenerates


def pack_f32(values):
    return struct.pack("<" + "f" * len(values), *values) if values else b""


def pack_u32(values):
    return struct.pack("<" + "I" * len(values), *values) if values else b""


def build_glb(mesh_rows, output_path):
    binary = bytearray()
    buffer_views = []
    accessors = []
    meshes = []
    nodes = []

    def add_view(data, target):
        while len(binary) % 4:
            binary.append(0)
        offset = len(binary)
        binary.extend(data)
        row = {"buffer": 0, "byteOffset": offset, "byteLength": len(data)}
        if target is not None:
            row["target"] = target
        buffer_views.append(row)
        return len(buffer_views) - 1

    def add_accessor(view_index, component_type, count, kind, minimum=None, maximum=None):
        row = {"bufferView": view_index, "componentType": component_type, "count": count, "type": kind}
        if minimum is not None:
            row["min"] = minimum
        if maximum is not None:
            row["max"] = maximum
        accessors.append(row)
        return len(accessors) - 1

    for row in mesh_rows:
        if not row["triangles"]:
            continue
        positions, normals, indices, degenerates = flat_triangle_arrays(row["worldVertices"], row["triangles"])
        vertex_count = len(indices)
        position_triplets = [positions[i:i + 3] for i in range(0, len(positions), 3)]
        position_min = [min(p[i] for p in position_triplets) for i in range(3)]
        position_max = [max(p[i] for p in position_triplets) for i in range(3)]
        pos_view = add_view(pack_f32(positions), 34962)
        nor_view = add_view(pack_f32(normals), 34962)
        idx_view = add_view(pack_u32(indices), 34963)
        pos_accessor = add_accessor(pos_view, 5126, vertex_count, "VEC3", position_min, position_max)
        nor_accessor = add_accessor(nor_view, 5126, vertex_count, "VEC3")
        idx_accessor = add_accessor(idx_view, 5125, vertex_count, "SCALAR", [0], [max(indices)])
        meshes.append({
            "name": row["objectName"],
            "primitives": [{"attributes": {"POSITION": pos_accessor, "NORMAL": nor_accessor}, "indices": idx_accessor, "material": 0, "mode": 4}],
            "extras": {"purpose": "T98 local evaluated-geometry QA; no canonical binding or rights approval", "sourceObjectName": row["objectName"], "triangleCount": len(row["triangles"]), "flatNormalDegenerateTriangleCount": degenerates},
        })
        nodes.append({"name": row["objectName"], "mesh": len(meshes) - 1, "extras": {"sourceDataBlockName": row["dataBlockName"], "role": "unapproved anatomical sample"}})

    gltf = {
        "asset": {"version": "2.0", "generator": "HUMAN ATLAS T98 read-only evaluated exporter spike"},
        "scene": 0,
        "scenes": [{"nodes": list(range(len(nodes)))}],
        "nodes": nodes,
        "meshes": meshes,
        "materials": [{"name": "T98 neutral technical preview only", "pbrMetallicRoughness": {"baseColorFactor": [0.66, 0.69, 0.73, 1.0], "metallicFactor": 0.0, "roughnessFactor": 0.82}, "doubleSided": True}],
        "bufferViews": buffer_views,
        "accessors": accessors,
        "buffers": [{"byteLength": len(binary)}],
        "extras": {"task": "T98", "sourceOnly": True, "publicRedistribution": "held", "humanAnatomyReview": "not_performed", "frame": "source Blender coordinates; not registered to T50/T69 project frame"},
    }
    json_chunk = json.dumps(gltf, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    while len(json_chunk) % 4:
        json_chunk += b" "
    while len(binary) % 4:
        binary.append(0)
    total_length = 12 + 8 + len(json_chunk) + 8 + len(binary)
    output = bytearray(struct.pack("<4sII", b"glTF", 2, total_length))
    output.extend(struct.pack("<I4s", len(json_chunk), b"JSON"))
    output.extend(json_chunk)
    output.extend(struct.pack("<I4s", len(binary), b"BIN\0"))
    output.extend(binary)
    output_path.write_bytes(output)
    return {"gltf": gltf, "bytes": len(output), "sha256": sha256_file(output_path), "meshCount": len(meshes), "binaryBytes": len(binary)}


def write_helper_obj(row, output_path):
    points = row["worldVertices"]
    triangles = row["triangles"]
    lines = ["# T98 evaluated helper geometry; not an anatomical target", "o Cross_Section_X_helper"]
    for p in points:
        lines.append("v %.9g %.9g %.9g" % tuple(p))
    for tri in triangles:
        a, b, c = (i + 1 for i in tri)
        lines.append("f %d %d %d" % (a, b, c))
    output_path.write_text("\n".join(lines) + "\n", encoding="ascii")
    return {"path": str(output_path), "bytes": output_path.stat().st_size, "sha256": sha256_file(output_path)}


def configure_preview_scene(scene):
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "SINGLE"
    scene.display.shading.single_color = (0.66, 0.69, 0.73)
    scene.display.shading.background_type = "WORLD"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "BOTH"
    scene.display.shading.curvature_ridge_factor = 1.1
    scene.display.shading.curvature_valley_factor = 1.0
    scene.world.color = (0.07, 0.08, 0.10)
    scene.render.film_transparent = False
    scene.camera.data.type = "ORTHO"


def render_previews(scene, qa_objects, bounds, output_dir):
    for obj in qa_objects:
        obj.hide_render = False
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.eevee.taa_render_samples = 16
    scene.render.film_transparent = False
    if hasattr(scene.render, "use_freestyle"):
        scene.render.use_freestyle = False
    lo, hi = Vector(bounds["min"]), Vector(bounds["max"])
    center = (lo + hi) * 0.5
    extent = max(float(hi[i] - lo[i]) for i in range(3))
    if extent <= 0:
        raise RuntimeError("sample evaluated bounds are empty")
    camera_data = bpy.data.cameras.new("T98 temporary QA camera")
    camera = bpy.data.objects.new("T98 temporary QA camera", camera_data)
    scene.collection.objects.link(camera)
    camera.hide_render = False
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = extent * 1.12
    camera.data.clip_start = 0.001
    camera.data.clip_end = extent * 20.0
    scene.camera = camera
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    if background is not None:
        background.inputs["Color"].default_value = (0.09, 0.10, 0.12, 1.0)
        background.inputs["Strength"].default_value = 0.45
    light_names = []
    for light_name, direction, energy in (
        ("key", Vector((1.0, -1.4, 1.6)), 1800.0),
        ("fill", Vector((-1.2, 0.9, 0.7)), 1100.0),
        ("rim", Vector((0.2, 0.7, -1.0)), 900.0),
    ):
        light_data = bpy.data.lights.new("T98 temporary " + light_name, "AREA")
        light_data.energy = energy
        light_data.shape = "DISK"
        light_data.size = extent * 2.0
        light_obj = bpy.data.objects.new("T98 temporary " + light_name, light_data)
        scene.collection.objects.link(light_obj)
        light_obj.location = center + direction.normalized() * extent * 1.8
        light_obj.rotation_euler = (center - light_obj.location).to_track_quat("-Z", "Y").to_euler()
        light_obj.hide_render = False
        light_names.append(light_obj.name)
    views = [
        ("normal-x-positive", Vector((1, 0, 0))),
        ("normal-y-positive", Vector((0, 1, 0))),
        ("normal-z-positive", Vector((0, 0, 1))),
    ]
    receipts = []
    for name, direction in views:
        camera.location = center + direction * extent * 2.5
        camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
        scene.camera = camera
        scene.render.filepath = str(output_dir / (name + ".png"))
        started = time.perf_counter()
        bpy.ops.render.render(write_still=True, scene=scene.name)
        image_path = Path(scene.render.filepath)
        receipts.append({"path": str(image_path), "bytes": image_path.stat().st_size, "sha256": sha256_file(image_path), "viewNormal": name, "renderSeconds": round(time.perf_counter() - started, 4), "resolution": [1100, 1100]})
    observations = {
        "engine": scene.render.engine,
        "previewSceneName": scene.name,
        "previewSceneObjectCount": len(scene.objects),
        "qaObjectCount": len(qa_objects),
        "qaObjects": [{"name": obj.name, "vertices": len(obj.data.vertices), "polygons": len(obj.data.polygons), "hideRender": bool(obj.hide_render), "hideViewport": bool(obj.hide_viewport)} for obj in qa_objects],
        "temporaryLights": light_names,
    }
    return receipts, observations


def main():
    started = time.perf_counter()
    root, freeze_path, output_dir, requested_source_path = cli_args()
    output_dir.mkdir(parents=True, exist_ok=True)
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    source_path = root / "atlas-data/source-cache/z-anatomy/t97/extracted" / freeze["source"]["memberPath"]
    if requested_source_path != source_path.resolve():
        raise RuntimeError("requested source path differs from the frozen extracted member")
    if Path(bpy.data.filepath).resolve() != source_path.resolve():
        result = bpy.ops.wm.open_mainfile(filepath=str(source_path), load_ui=False, use_scripts=False)
        if "FINISHED" not in result:
            raise RuntimeError("Blender did not finish opening the frozen source blend")
    archive_path = root / freeze["source"]["archivePath"]
    expected_source_hash = freeze["source"]["memberSha256"]
    expected_archive_hash = freeze["source"]["archiveSha256"]
    actual_source_hash = sha256_file(source_path)
    actual_archive_hash = sha256_file(archive_path)
    if actual_source_hash != expected_source_hash or actual_archive_hash != expected_archive_hash:
        raise RuntimeError("pinned source/archive hash mismatch; source was not evaluated")
    if Path(bpy.data.filepath).resolve() != source_path.resolve():
        raise RuntimeError("Blender opened a path other than the frozen Startup.blend")
    if len(freeze["objects"]) != 12:
        raise RuntimeError("frozen sample count drift")

    scene = bpy.context.scene
    source_scene_object_count = len(scene.objects)
    source_datablock_object_count = len(bpy.data.objects)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    bpy.context.view_layer.update()
    depsgraph.update()
    frozen_by_name = {row["sourceObjectLocator"]["objectIdName"]: row for row in freeze["objects"]}
    shared_data = {}
    for name in frozen_by_name:
        original = bpy.data.objects.get(name)
        if original is not None and original.data is not None:
            shared_data.setdefault(hex(int(original.data.as_pointer())), []).append(name)
    instance_counts = {name: 0 for name in frozen_by_name}
    depsgraph_instances = 0
    for instance in depsgraph.object_instances:
        if not instance.is_instance:
            continue
        depsgraph_instances += 1
        candidates = [getattr(instance, "object", None), getattr(instance, "instance_object", None)]
        for candidate in candidates:
            if candidate is None:
                continue
            source_obj = getattr(candidate, "original", candidate)
            if source_obj.name in instance_counts:
                instance_counts[source_obj.name] += 1

    rows = []
    qa_mesh_objects = []
    sample_objects = []
    for name, frozen in frozen_by_name.items():
        locator = frozen["sourceObjectLocator"]
        obj = bpy.data.objects.get(name)
        if obj is None or obj.name != name:
            raise RuntimeError("exact frozen object name missing or renamed: " + name)
        sample_objects.append(obj)
        data_name = obj.data.name if obj.data is not None else None
        parent_name = obj.parent.name if obj.parent is not None else None
        expected_data_name = frozen.get("dataBlockName")
        expected_parent_name = frozen.get("parentObjectName")
        if data_name != expected_data_name or parent_name != expected_parent_name:
            raise RuntimeError("frozen object identity relation changed: " + name)
        actual_collection_names = sorted(c.name for c in obj.users_collection)
        expected_collection_leaves = {path[-1] for path in frozen.get("collectionPaths", []) if path}
        if expected_collection_leaves and not (expected_collection_leaves & set(actual_collection_names)):
            raise RuntimeError("frozen collection locator has no matching direct collection: " + name)
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
        if mesh is None:
            raise RuntimeError("evaluated mesh unavailable: " + name)
        try:
            mesh.calc_loop_triangles()
            transform = evaluated.matrix_world.copy()
            determinant = float(transform.to_3x3().determinant())
            points = [v3(transform @ vertex.co) for vertex in mesh.vertices]
            triangles = []
            for triangle in mesh.loop_triangles:
                indices = list(triangle.vertices)
                if determinant < 0:
                    indices[1], indices[2] = indices[2], indices[1]
                triangles.append(indices)
            bounds = world_bounds(points)
            animation = obj.animation_data
            drivers = [] if animation is None else [
                {"dataPath": driver.data_path, "expression": driver.driver.expression, "driverType": driver.driver.type, "muted": bool(driver.mute)}
                for driver in animation.drivers
            ]
            modifiers = [{"name": m.name, "type": m.type, "showViewport": bool(m.show_viewport), "showRender": bool(m.show_render)} for m in obj.modifiers]
            constraints = [{"name": c.name, "type": c.type, "mute": bool(c.mute)} for c in obj.constraints]
            visibility = {}
            try:
                visibility["visibleInCurrentViewLayer"] = bool(obj.visible_get(view_layer=bpy.context.view_layer))
            except Exception as exc:
                visibility["visibleInCurrentViewLayer"] = None
                visibility["visibilityError"] = repr(exc)
            visibility["hideRender"] = bool(obj.hide_render)
            visibility["hideViewport"] = bool(obj.hide_viewport)
            eval_tri_count = len(mesh.loop_triangles)
            eval_poly_count = len(mesh.polygons)
            row = {
                "objectName": name,
                "role": "non_anatomical_helper" if name == "Cross Section X" else "unapproved_anatomical_sample",
                "frozenLocator": {"objectDataBlockPointer": locator.get("objectDataBlockPointer"), "serializedFileBlockOffset": locator.get("serializedFileBlockOffset"), "dataPointer": frozen.get("dataPointer"), "collectionPathLeaves": sorted(expected_collection_leaves)},
                "sourceDataBlockName": expected_data_name,
                "dataBlockName": data_name,
                "parentObjectName": parent_name,
                "collectionNames": actual_collection_names,
                "locatorNameAndRelationshipMatched": True,
                "frozenSerializedPointerCompared": False,
                "sourceSuffixSideLabel": "l/r literal only; not approved laterality" if name.endswith((".l", ".r")) else None,
                "baseMeshCounts": {"vertices": len(obj.data.vertices), "edges": len(obj.data.edges), "polygons": len(obj.data.polygons)},
                "evaluatedMeshCounts": {"vertices": len(mesh.vertices), "edges": len(mesh.edges), "polygons": eval_poly_count, "triangles": eval_tri_count},
                "evaluatedLooseVertexCount": len(set(range(len(mesh.vertices))) - {i for tri in triangles for i in tri}),
                "evaluatedMinusBase": {"vertices": len(mesh.vertices) - len(obj.data.vertices), "polygons": eval_poly_count - len(obj.data.polygons)},
                "worldDeterminant": determinant,
                "windingReversedForBakedWorldTransform": determinant < 0,
                "sourceObjectMatrixWorld": matrix_rows(obj.matrix_world),
                "evaluatedObjectMatrixWorld": matrix_rows(transform),
                "evaluatedMatrixMaxAbsDelta": matrix_delta(obj.matrix_world, transform),
                "worldBoundsInSourceBlenderCoordinates": bounds,
                "evaluatedGeometrySha256": canonical_geometry_hash(points, triangles),
                "runtimeSharedMeshDataPointer": hex(int(obj.data.as_pointer())),
                "serializedCaseSharedDataGroup": None,
                "dependencyGraphGeneratedInstanceReferences": instance_counts[name],
                "modifiers": modifiers,
                "constraints": constraints,
                "driversListedButNeverExecutedByThisScript": drivers,
                "visibility": visibility,
                "worldVertices": points,
                "triangles": triangles,
            }
            rows.append(row)
        finally:
            evaluated.to_mesh_clear()

    for row in rows:
        for names in shared_data.values():
            if row["objectName"] in names and len(names) > 1:
                row["serializedCaseSharedDataGroup"] = names
                break

    anatomical_rows = [row for row in rows if row["role"] != "non_anatomical_helper"]
    helper_rows = [row for row in rows if row["role"] == "non_anatomical_helper"]
    if len(anatomical_rows) != 11 or len(helper_rows) != 1:
        raise RuntimeError("frozen sample role counts changed")
    if any(not row["evaluatedMeshCounts"]["triangles"] for row in anatomical_rows):
        raise RuntimeError("one or more frozen anatomical sample objects has no evaluated triangles")
    anatomical_bound_corners = []
    for row in anatomical_rows:
        if row["worldBoundsInSourceBlenderCoordinates"] is not None:
            anatomical_bound_corners.extend([row["worldBoundsInSourceBlenderCoordinates"]["min"], row["worldBoundsInSourceBlenderCoordinates"]["max"]])
    if not anatomical_bound_corners:
        raise RuntimeError("empty combined anatomical sample bounds")
    combined_bounds = world_bounds(anatomical_bound_corners)

    out_glb = output_dir / "t98-frozen-11-anatomical-objects-evaluated.glb"
    glb_receipt = build_glb(anatomical_rows, out_glb)
    helper_obj = output_dir / "cross-section-x-helper-evaluated.obj"
    helper_receipt = write_helper_obj(helper_rows[0], helper_obj)

    # Create a separate ephemeral scene for render-only copies. All edits here die
    # with this process; the source Startup.blend is never saved or modified.
    preview_scene = bpy.data.scenes.new("T98 temporary isolated QA preview")
    preview_scene.world = bpy.data.worlds.new("T98 temporary QA world")
    preview_material = bpy.data.materials.new("T98 temporary neutral QA material")
    preview_material.diffuse_color = (0.66, 0.69, 0.73, 1.0)
    preview_material.use_nodes = True
    bsdf = preview_material.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = (0.66, 0.69, 0.73, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.82
    for row in anatomical_rows:
        mesh_data = bpy.data.meshes.new("T98_QA_" + row["objectName"])
        mesh_data.from_pydata(row["worldVertices"], [], row["triangles"])
        mesh_data.update()
        qa_obj = bpy.data.objects.new("T98_QA_" + row["objectName"], mesh_data)
        preview_scene.collection.objects.link(qa_obj)
        qa_obj.data.materials.append(preview_material)
        qa_obj.hide_render = False
        qa_obj.hide_viewport = False
        try:
            qa_obj.hide_set(False)
        except Exception:
            pass
        qa_mesh_objects.append(qa_obj)
    preview_error = None
    preview_observations = None
    try:
        preview_receipts, preview_observations = render_previews(preview_scene, qa_mesh_objects, combined_bounds, output_dir)
    except Exception as exc:
        preview_receipts = []
        preview_error = repr(exc)

    runtime_path = Path(bpy.app.binary_path).resolve()
    runtime = {
        "binaryPath": str(runtime_path),
        "runtimeVersion": bpy.app.version_string,
        "binarySha256": sha256_file(runtime_path),
        "factoryStartup": True,
        "autoexecDisabledByCommand": True,
        "sourceFileScriptsOrDriversExecuted": False,
        "sourceBlendPath": bpy.data.filepath,
        "sourceBlendSha256": actual_source_hash,
        "sourceArchiveSha256": actual_archive_hash,
        "sourceOpenMode": "bpy.ops.wm.open_mainfile(load_ui=False, use_scripts=False); no save operator invoked",
        "currentScene": scene.name,
        "sceneFrameStart": scene.frame_start,
        "sceneFrameEnd": scene.frame_end,
        "sceneCurrentFrame": scene.frame_current,
        "unitSettings": {"system": scene.unit_settings.system, "scaleLength": float(scene.unit_settings.scale_length), "lengthUnit": scene.unit_settings.length_unit, "sourceDeclaredPhysicalUnit": None},
        "sourceCoordinateFrame": "native Blender scene coordinates; not registered to T50/T69",
        "sceneFrameRegistration": "unresolved",
        "referenceRestPoseId": None,
        "sourceSceneObjectCountBeforeQACopies": source_scene_object_count,
        "sourceObjectDatablockCountBeforeQACopies": source_datablock_object_count,
        "sourceSceneObjectCountAfterEvaluation": len(scene.objects),
        "previewSceneObjectCountAfterQACopies": len(preview_scene.objects),
        "depsgraphObjectInstanceCount": len(list(depsgraph.object_instances)),
        "depsgraphGeneratedInstanceCount": depsgraph_instances,
        "sampleInstanceReferences": instance_counts,
        "sampleSharedMeshGroupsByRuntimePointer": [names for names in shared_data.values() if len(names) > 1],
        "armatureDatablockCount": len(bpy.data.armatures),
        "officialBlenderPackageReceipt": "work/evidence/T97/blender-tool-current.json (verified official 5.2.2 LTS DMG; not the current 3.5.0 executable)",
        "officialPackageReceiptMatchesRuntimeBinary": False,
        "sourceTimestampsOrExternalIDMappingsAdded": False,
    }
    elapsed = round(time.perf_counter() - started, 4)
    usage = resource.getrusage(resource.RUSAGE_SELF)
    manifest = {
        "schemaVersion": "1.0.0",
        "task": "T98",
        "unit": "resume-evaluated-exporter",
        "status": "evaluated_geometry_exported_frame_and_rights_gates_open",
        "source": {"archivePath": str(archive_path), "archiveSha256": actual_archive_hash, "blendPath": str(source_path), "blendSha256": actual_source_hash, "blendBytes": source_path.stat().st_size, "frozenSourceHashMatched": True},
        "sourceRights": {"sourceOnly": True, "localUseRights": "held_pending_file_level_reconciliation", "publicRedistribution": "held", "humanAnatomyReview": "not_performed", "objectToUpstreamFamilyLineage": "unresolved"},
        "runtime": runtime,
        "sample": {"frozenCount": 12, "anatomicalObjectCount": 11, "helperObjectCount": 1, "exactNamesMatched": len(rows), "combinedSourceBounds": combined_bounds, "sourceSuffixAndSpaceObservationsAreNotAnatomicalLateralityApproval": True, "objects": [{k: v for k, v in row.items() if k not in {"worldVertices", "triangles"}} for row in rows]},
        "export": {"path": str(out_glb), "bytes": glb_receipt["bytes"], "sha256": glb_receipt["sha256"], "meshCount": glb_receipt["meshCount"], "binaryBytes": glb_receipt["binaryBytes"], "helperObj": helper_receipt, "normalMethod": "flat triangle normals recalculated from world-baked evaluated vertices for QA only", "negativeDeterminantPolicy": "reverse triangle winding when evaluated world linear determinant is negative", "sourceTransformsApplied": "evaluated matrix_world baked into exported source-coordinate vertices", "exportIsProductAsset": False},
        "preview": {"method": "three orthographic EEVEE renders in a separate ephemeral preview scene containing only evaluated geometry copies; source scene and file not saved", "views": preview_receipts, "observations": preview_observations, "error": preview_error, "helperExcludedFromAnatomicalPreview": True, "axisSemantics": "source Blender coordinate axes only; not anatomical front/back/side labels"},
        "counts": {"baseVertices": sum(row["baseMeshCounts"]["vertices"] for row in anatomical_rows), "evaluatedVertices": sum(row["evaluatedMeshCounts"]["vertices"] for row in anatomical_rows), "basePolygons": sum(row["baseMeshCounts"]["polygons"] for row in anatomical_rows), "evaluatedPolygons": sum(row["evaluatedMeshCounts"]["polygons"] for row in anatomical_rows), "evaluatedTriangles": sum(row["evaluatedMeshCounts"]["triangles"] for row in anatomical_rows), "evaluatedHelperTriangles": sum(row["evaluatedMeshCounts"]["triangles"] for row in helper_rows)},
        "performance": {"sourceOpenAndExportAndPreviewSeconds": elapsed, "maxRssReportedByResourceBytes": int(usage.ru_maxrss)},
        "limitations": ["the exact source object ancestry to upstream license family is unresolved", "scene metric settings are not an independent source-unit declaration", "source Blender coordinates are not registered to the T50/T69 BodyParts3D project frame", "current Blender executable is 3.5.0 and is not proven by the official 5.2.2 package receipt", "laterality strings and coordinate signs are observations only", "no canonical crosswalk or learner binding was created", "no production base selection was made"],
    }
    json_write(output_dir / "evaluated-export-manifest.json", manifest)
    (output_dir / "evaluated-export-manifest.sha256").write_text(sha256_file(output_dir / "evaluated-export-manifest.json") + "  evaluated-export-manifest.json\n", encoding="ascii")
    marker = "ATLAS_T98_EVALUATED_EXPORT_OK" if preview_receipts else "ATLAS_T98_EVALUATED_EXPORT_PARTIAL"
    print(marker, json.dumps({"glb": glb_receipt, "counts": manifest["counts"], "preview": preview_receipts, "previewError": preview_error, "elapsedSeconds": elapsed, "runtimeVersion": bpy.app.version_string, "sourceSha256": actual_source_hash}, ensure_ascii=False))


main()
