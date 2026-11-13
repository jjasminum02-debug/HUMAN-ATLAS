"""Extract every Z-Anatomy structure in scope into per-structure GLBs plus one structures.json.

Run (Blender 5.2, source scripts disabled; the source .blend is never saved):
  blender --background --factory-startup --disable-autoexec \
    atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend \
    --python atlas-data/pipeline/extract_za.py [-- --limit N]

Scope: numbered collections 1 skeletal, 2 muscular insertions, 3 joints, 4 muscular, 5 cardiovascular (Q2-1),
7 nervous (meshes, and beveled curves converted to tubes). Classification lives in za_classify.py.
Geometry stays in object-local space; `matrix` (column-major) applies the source world transform and
the Blender->app axis change [x, z, -y] once. Units are metres. Re-running reuses finished units.
"""
import hashlib
import json
from pathlib import Path
import struct
import sys
import time

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from za_classify import classify, split_name, slug  # noqa: E402

ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
LIMIT = int(ARGS[ARGS.index('--limit') + 1]) if '--limit' in ARGS else None  # smoke test on the first N objects
OUT = ROOT / 'atlas-data/source-cache/datasets' / ('za-full-smoke' if LIMIT else 'za-full')
SOURCE = Path(bpy.data.filepath)
APP_FRAME = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]], dtype='f8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '\n')
    tmp.replace(path)


def arrays(mesh):
    mesh.calc_loop_triangles()
    p = np.empty((len(mesh.vertices), 3), dtype='<f4'); mesh.vertices.foreach_get('co', p.ravel())
    t = np.empty((len(mesh.loop_triangles), 3), dtype='<i4'); mesh.loop_triangles.foreach_get('vertices', t.ravel())
    loops = np.empty((len(mesh.loop_triangles), 3), dtype='<i4'); mesh.loop_triangles.foreach_get('loops', loops.ravel())
    normals = np.empty((len(mesh.loops), 3), dtype='<f4'); mesh.corner_normals.foreach_get('vector', normals.ravel())
    # One indexed vertex per distinct position/normal pair keeps the source smoothing seams.
    packed = np.concatenate((p[t.ravel()], normals[loops.ravel()]), axis=1)
    vertices, index = np.unique(packed, axis=0, return_inverse=True)
    return p, t, vertices[:, :3].copy(), vertices[:, 3:].copy(), index.astype('<u4').reshape((-1, 3))


def glb(p, n, t):
    assert len(p) and len(t) and np.isfinite(p).all() and np.isfinite(n).all()
    idx = t.astype('<u2') if len(p) <= 65535 else t.astype('<u4')
    blobs = [p.astype('<f4').tobytes(), n.astype('<f4').tobytes(), idx.tobytes()]
    binary = bytearray(); views = []
    for b in blobs:
        views.append({'buffer': 0, 'byteOffset': len(binary), 'byteLength': len(b)})
        binary.extend(b); binary.extend(b'\0' * ((-len(binary)) % 4))
    doc = {'asset': {'version': '2.0', 'generator': 'HUMAN ATLAS extract_za'}, 'scene': 0, 'scenes': [{'nodes': [0]}],
           'nodes': [{'mesh': 0, 'name': 'resource'}], 'meshes': [{'primitives': [{'attributes': {'POSITION': 0, 'NORMAL': 1}, 'indices': 2}]}],
           'buffers': [{'byteLength': len(binary)}], 'bufferViews': views, 'accessors': [
               {'bufferView': 0, 'componentType': 5126, 'count': len(p), 'type': 'VEC3', 'min': p.min(0).tolist(), 'max': p.max(0).tolist()},
               {'bufferView': 1, 'componentType': 5126, 'count': len(n), 'type': 'VEC3'},
               {'bufferView': 2, 'componentType': 5123 if idx.dtype.itemsize == 2 else 5125, 'count': idx.size, 'type': 'SCALAR'}]}
    j = json.dumps(doc, separators=(',', ':')).encode(); j += b' ' * ((-len(j)) % 4)
    return (struct.pack('<III', 0x46546c67, 2, 28 + len(j) + len(binary)) + struct.pack('<I4s', len(j), b'JSON') + j
            + struct.pack('<I4s', len(binary), b'BIN\0') + binary)


def emit(pp, nn, tt):
    data = glb(pp, nn, tt); h = sha(data); path = f'resources/{h}.glb'
    target = OUT / path
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
    return {'path': path, 'sha256': h, 'bytes': len(data), 'vertices': len(pp), 'triangles': len(tt)}


def sampled_error(a, at, b, bt, matrix):
    # Deterministic symmetric sampled surface distance in metres; not a Hausdorff guarantee.
    def world(p): return p.astype('f8') @ matrix[:3, :3].T + matrix[:3, 3]
    a, b = world(a), world(b)
    ta = BVHTree.FromPolygons(a.tolist(), at.tolist(), all_triangles=True)
    tb = BVHTree.FromPolygons(b.tolist(), bt.tolist(), all_triangles=True)
    worst = 0.
    for points, tree in [(a, tb), (b, ta)]:
        for i in np.linspace(0, len(points) - 1, min(192, len(points)), dtype=int):
            worst = max(worst, float(tree.find_nearest(Vector(points[i]))[3]))
    return worst


OVERVIEW_RATIOS = [.18, .32, .5, .75]
# Q2-1: ZA vessel tubes are tessellated far finer than their few-millimetre radius needs (one retinal artery has 207k
# triangles), so vessels also try lower overview ratios and get a decimated detail level at a third of the tolerance.
VESSEL_OVERVIEW_RATIOS = [.03, .05, .08, .12] + OVERVIEW_RATIOS
VESSEL_DETAIL_RATIOS = [.15, .25, .4, .6]


def overview(mesh, p, t, ip, n, it, matrix, temporary, ratios=OVERVIEW_RATIOS, tolerance_scale=1.):
    world = p.astype('f8') @ matrix[:3, :3].T + matrix[:3, 3]
    tolerance = max(.00015, min(.002, float(np.linalg.norm(world.max(0) - world.min(0))) * .01)) * tolerance_scale
    if len(t) <= 256:
        return (ip, n, it), {'ratio': 1., 'errorMetres': 0., 'toleranceMetres': tolerance}
    for ratio in ratios:
        copy = mesh.copy(); temp = bpy.data.objects.new('extract-temp', copy); temporary.collection.objects.link(temp)
        try:
            mod = temp.modifiers.new('overview', 'DECIMATE'); mod.ratio = max(ratio, 256 / len(t)); mod.use_collapse_triangulate = True
            with bpy.context.temp_override(scene=temporary, view_layer=temporary.view_layers[0]):
                td = bpy.context.evaluated_depsgraph_get(); td.update(); ev = temp.evaluated_get(td); reduced = ev.to_mesh()
                try:
                    rp, rt, op, on, ot = arrays(reduced); error = sampled_error(p, t, rp, rt, matrix)
                finally:
                    ev.to_mesh_clear()
        finally:
            bpy.data.objects.remove(temp, do_unlink=True); bpy.data.meshes.remove(copy)
        if error <= tolerance:
            return (op, on, ot), {'ratio': ratio, 'errorMetres': error, 'toleranceMetres': tolerance}
    return (ip, n, it), {'ratio': 1., 'errorMetres': 0., 'toleranceMetres': tolerance}


def bonus_paths():
    paths = {}
    def walk(col, chain):
        for o in col.objects: paths.setdefault(o.name, []).append(chain + [col.name])
        for c in col.children: walk(c, chain + [col.name])
    walk(bpy.data.collections['Bonus collection'], [])
    return paths


def candidates():
    """Every object in the numbered collections, with its top collection."""
    rows, seen = [], set()
    for top in bpy.context.scene.collection.children:
        if not top.name[:1].isdigit():
            continue
        for o in top.all_objects:
            if o.name not in seen:  # an object linked twice is extracted once, under its first collection
                seen.add(o.name); rows.append((o, top.name))
    return rows


def main():
    start = time.time()
    assert not bpy.context.preferences.filepaths.use_scripts_auto_execute, 'run with --disable-autoexec'
    source_hash = sha(SOURCE.read_bytes())
    code = Path(__file__).read_bytes() + (Path(__file__).with_name('za_classify.py')).read_bytes()
    fingerprint = sha(code + source_hash.encode() + bpy.app.version_string.encode())
    dg = bpy.context.evaluated_depsgraph_get(); dg.update()
    temporary = bpy.data.scenes.new('extract temporary - never saved')
    bonus = bonus_paths()
    structures, exceptions = [], []
    excluded = {}
    reused = 0
    rows = candidates()[:LIMIT] if LIMIT else candidates()
    for number, (obj, top) in enumerate(rows, 1):
        def exclude(reason):
            excluded[reason] = excluded.get(reason, 0) + 1
        if obj.type not in ('MESH', 'CURVE'):
            exclude('non_geometry_' + obj.type.lower()); continue
        info = classify(obj.name, top, bonus.get(obj.name, []), obj.parent.name if obj.parent else None)
        if 'exclude' in info:
            exclude(info['exclude']); continue
        if obj.type == 'CURVE' and info['system'] not in ('nervous', 'cardiovascular'):
            exclude('curve_outside_nervous_or_vessels'); continue
        if obj.type == 'MESH' and len(obj.data.vertices) <= 2:
            exclude('label_leader_line'); continue
        checkpoint = OUT / 'units' / f'{slug(obj.name)}.json'
        if checkpoint.exists():
            try:
                prev = json.loads(checkpoint.read_text())
                if prev['fingerprint'] == fingerprint and all((OUT / r['path']).exists() for r in prev['lods'].values()):
                    structures.append(prev); reused += 1; continue
            except (OSError, ValueError, KeyError):
                pass
        evaluated = obj.evaluated_get(dg)
        try:
            mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=dg)
            if mesh is None or not len(mesh.polygons):
                exceptions.append({'id': info['id'], 'sourceName': obj.name, 'reason': 'empty_geometry'}); continue
            p, t, ip, n, it = arrays(mesh)
            matrix = np.array(evaluated.matrix_world, dtype='f8'); assert np.isfinite(matrix).all()
            app = APP_FRAME @ matrix
            world = p.astype('f8') @ app[:3, :3].T + app[:3, 3]
            vessel = info['system'] == 'cardiovascular'
            if vessel:
                (ip, n, it), detail_quality = overview(mesh, p, t, ip, n, it, matrix, temporary, VESSEL_DETAIL_RATIOS, 1 / 3)
            lods = {'detail': emit(ip, n, it)}
            (op, on, ot), quality = overview(mesh, p, t, ip, n, it, matrix, temporary, VESSEL_OVERVIEW_RATIOS if vessel else OVERVIEW_RATIOS)
            lods['overview'] = emit(op, on, ot) if quality['ratio'] < 1. else lods['detail']
            unit = {**info, 'sourceName': obj.name, 'sourceType': obj.type, 'topCollection': top,
                    'bonusPaths': bonus.get(obj.name, []), 'fingerprint': fingerprint,
                    'matrix': app.T.ravel().tolist(), 'mirrored': bool(np.linalg.det(app[:3, :3]) < 0),
                    'bounds': {'min': world.min(0).tolist(), 'max': world.max(0).tolist()},
                    'lods': lods, 'overviewQuality': quality, **({'detailQuality': detail_quality} if vessel else {})}
            save(checkpoint, unit); structures.append(unit)
        except Exception as error:  # one bad object never stops the batch
            exceptions.append({'id': info['id'], 'sourceName': obj.name, 'reason': 'extract_failed', 'detail': repr(error)})
        finally:
            evaluated.to_mesh_clear()
        if number % 100 == 0:
            print(f'EXTRACT {number}/{len(rows)} structures={len(structures)} exceptions={len(exceptions)}', flush=True)

    # Cross-links: attachment -> owning structure(s) and bone. The owner is the muscle of the same name and
    # side, else the unpaired one (diaphragm), else a ligament/tendon of that name, else the muscle's parts
    # (ZA splits e.g. masseter or deltoid into named parts/heads "... of <muscle>").
    by_source = {s['sourceName']: s['id'] for s in structures}
    owners = {}
    for s in structures:
        if s['system'] != 'attachment':
            owners.setdefault((s['name'].lower(), s['side']), []).append(s)
    for s in structures:
        if s['system'] == 'attachment':
            name = s['name'].lower()
            found = owners.get((name, s['side'])) or owners.get((name, 'unpaired'))
            if not found:
                stem = name[:-len(' muscle')] if name.endswith(' muscle') else name
                found = [o for (n, side), group in owners.items() if side == s['side'] and
                         (n.endswith(' of ' + name) or n.endswith(' of ' + stem)) for o in group if o['system'] == 'muscular']
            s['ownerIds'] = sorted(o['id'] for o in found or [])
            s['boneId'] = by_source.get(s.get('bone'))
            if not s['ownerIds']:
                exceptions.append({'id': s['id'], 'sourceName': s['sourceName'], 'reason': 'attachment_owner_not_found'})
            if not s['boneId']:
                exceptions.append({'id': s['id'], 'sourceName': s['sourceName'], 'reason': 'attachment_bone_not_extracted', 'detail': s.get('bone')})
        if s['kind'] is None:
            exceptions.append({'id': s['id'], 'sourceName': s['sourceName'], 'reason': 'unclassified_kind', 'detail': s['system']})

    structures.sort(key=lambda s: s['id'])
    counts = {}
    for s in structures:
        key = f"{s['system']}/{s['kind']}"; counts[key] = counts.get(key, 0) + 1
    run = {'source': str(SOURCE.relative_to(ROOT)), 'sourceSha256': source_hash, 'blender': bpy.app.version_string,
           'fingerprint': fingerprint, 'frame': 'app = [x, z, -y] of Blender world; metres', 'structures': len(structures),
           'reused': reused, 'counts': dict(sorted(counts.items())), 'excluded': dict(sorted(excluded.items())),
           'exceptions': len(exceptions), 'seconds': round(time.time() - start, 1),
           'detailTriangles': sum(s['lods']['detail']['triangles'] for s in structures),
           'overviewTriangles': sum(s['lods']['overview']['triangles'] for s in structures)}
    save(OUT / 'structures.json', {'schemaVersion': 1, 'run': run,
                                   'structures': [{k: v for k, v in s.items() if k != 'fingerprint'} for s in structures]})
    save(OUT / 'exceptions.json', {'schemaVersion': 1, 'exceptions': exceptions})
    print('EXTRACT_DONE', json.dumps(run), flush=True)


main()
