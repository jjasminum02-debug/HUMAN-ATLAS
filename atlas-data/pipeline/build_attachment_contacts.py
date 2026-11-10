"""Estimated attachment areas where Z-Anatomy has no patch (ROADMAP C4, second half).

  blender --background --factory-startup --python atlas-data/pipeline/build_attachment_contacts.py
(Blender only for numpy + mathutils.kdtree.) Run after build_attachments.py; adds `contact` rows to
atlas-data/runtime/attachments.json.

For each visible muscle missing an origin or insertion patch: bone triangles whose centroid lies within 3 mm of the
muscle's surface (runtime geometry, so triangle indices match what the app renders), grouped into touching clusters
(8 mm link). Only clusters reaching an end of the muscle (outer 25 % along its main axis) count: a belly lying on a
bone is not an attachment. Role: when Z-Anatomy gives one side, the other end gets the complementary role; otherwise
the area is an unlabelled 'attachment'. Clusters at an end Z-Anatomy already covers are skipped.
Rows in attachments.json carry role, bone and area; the triangle indices per bone resource (overview and detail, base64
little-endian uint32) go to source-cache/datasets/za-v2/attachments/<muscle key>.json (git-ignored, like skin weights),
which the app fetches when that muscle is selected.

Ligaments, capsules, membranes, labra and menisci (4-1 step 6) get the same contact clusters without the end rule (a
ligament attaches along its ends and sometimes its edge) and without a role: they are 'attachment' areas, the largest
LIGAMENT_AREAS per structure, in attachments.json `ligaments`.
"""
import base64
import json
from pathlib import Path
import struct

import numpy as np
from mathutils import Vector
from mathutils.kdtree import KDTree

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / 'atlas-data/runtime'
GEOMETRY = ROOT / 'atlas-data/source-cache/datasets/za-v2'
OUT = GEOMETRY / 'attachments'
CONTACT, LINK, END, MIN_TRIS, MIN_AREA = .003, .008, .25, 6, 20e-6
LIGAMENT_KINDS, LIGAMENT_AREAS = {'ligament', 'capsule', 'membrane', 'labrum', 'meniscus'}, 6


def chunk_meshes(path):
    """resource key -> (local positions, triangle indices) from a packed chunk GLB."""
    data = path.read_bytes(); size = struct.unpack_from('<I', data, 12)[0]
    doc = json.loads(data[20:20 + size]); binary = data[20 + size + 8:]

    def accessor(i, dtype, width):
        a = doc['accessors'][i]; view = doc['bufferViews'][a['bufferView']]
        return np.frombuffer(binary, dtype=dtype, count=a['count'] * width, offset=view.get('byteOffset', 0) + a.get('byteOffset', 0))
    out = {}
    for mesh in doc['meshes']:
        prim = mesh['primitives'][0]
        index_type = {5123: '<u2', 5125: '<u4'}[doc['accessors'][prim['indices']]['componentType']]
        out[mesh['name']] = (accessor(prim['attributes']['POSITION'], '<f4', 3).reshape(-1, 3).astype('f8'),
                             accessor(prim['indices'], index_type, 1).reshape(-1, 3).astype('i8'))
    return out


def world(points, matrix):
    m = np.array(matrix, dtype='f8').reshape(4, 4).T
    return points @ m[:3, :3].T + m[:3, 3]


def kdtree(points):
    kd = KDTree(len(points))
    for i, p in enumerate(points): kd.insert(Vector(p), i)
    kd.balance(); return kd


def clusters(points):
    """Connected groups of points within LINK of each other (indices)."""
    kd, seen, out = kdtree(points), np.zeros(len(points), bool), []
    for start in range(len(points)):
        if seen[start]: continue
        stack, group = [start], []
        seen[start] = True
        while stack:
            i = stack.pop(); group.append(i)
            for _, j, _ in kd.find_range(Vector(points[i]), LINK):
                if not seen[j]: seen[j] = True; stack.append(j)
        out.append(np.array(group))
    return out


def main():
    structures = json.loads((RUNTIME / 'structures.json').read_text())['structures']
    attachments = json.loads((RUNTIME / 'attachments.json').read_text())
    by_key = {s['key']: s for s in structures}
    bones = [s for s in structures if s['learner']['visible'] and s['layer'] == 'bone']
    muscles = [s for s in structures if s['learner']['visible'] and s['layer'] == 'muscle']
    cache = {}
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob('*.json'): old.unlink()

    def mesh(s, level):
        lod = s['geometry']['lods'][level]
        if lod['chunk'] not in cache: cache[lod['chunk']] = chunk_meshes(GEOMETRY / 'chunks' / f"{lod['chunk']}.glb")
        p, tris = cache[lod['chunk']][lod['resource']]
        return lod['resource'], world(p, s['geometry']['matrix']), tris

    def bounds(s):
        b = s['geometry']['bounds']; return np.array(b[0]), np.array(b[1])

    stats = {'muscles': 0, 'rows': 0, 'labelled': 0, 'unlabelled': 0, 'noContact': 0}
    for m in muscles:
        za = attachments['muscles'].get(m['key'], [])
        roles = {r['role'] for r in za}
        if {'origin', 'insertion'} <= roles: continue
        _, pts, _ = mesh(m, 'detail')
        # Main axis and position along it (0..1) of every muscle vertex.
        centre = pts.mean(0); axis = np.linalg.svd(pts - centre, full_matrices=False)[2][0]
        along = (pts - centre) @ axis; lo, hi = along.min(), along.max()
        t_of = lambda p: ((p - centre) @ axis - lo) / max(hi - lo, 1e-9)
        known_end = {}
        for r in za:
            _, patch_pts, _ = mesh(by_key[r['key']], 'overview')
            known_end[r['role']] = 'a' if t_of(patch_pts.mean(0)) < .5 else 'b'
        kd = kdtree(pts)
        mlo, mhi = pts.min(0) - .005, pts.max(0) + .005
        rows = []
        for bone in bones:
            blo, bhi = bounds(bone)
            if (blo > mhi).any() or (bhi < mlo).any(): continue
            per_level = {}
            for level in ('detail', 'overview'):
                resource, bp, tris = mesh(bone, level)
                cent = bp[tris].mean(1)
                near = np.array([kd.find(Vector(c))[2] <= CONTACT for c in cent])
                per_level[level] = (resource, bp, tris, cent, np.flatnonzero(near))
            resource, bp, tris, cent, hit = per_level['detail']
            if len(hit) < MIN_TRIS: continue
            for group in clusters(cent[hit]):
                sel = hit[group]
                area = np.linalg.norm(np.cross(bp[tris[sel, 1]] - bp[tris[sel, 0]], bp[tris[sel, 2]] - bp[tris[sel, 0]]), axis=1).sum() / 2
                if len(sel) < MIN_TRIS or area < MIN_AREA: continue
                t = t_of(cent[sel])
                end = 'a' if t.min() <= END else 'b' if t.max() >= 1 - END else None
                if end is None: continue
                if end in known_end.values(): continue  # Z-Anatomy already draws this end
                if known_end:
                    role = 'insertion' if 'origin' in known_end else 'origin'
                else: role = 'attachment'
                # Same area on the overview mesh: contact triangles near this cluster.
                o_res, _, _, o_cent, o_hit = per_level['overview']
                ckd = kdtree(cent[sel])
                o_sel = [i for i in o_hit if ckd.find(Vector(o_cent[i]))[2] <= LINK]
                if not o_sel:  # coarse overview: its triangle centres sit farther than CONTACT from the muscle
                    o_sel = [i for i in range(len(o_cent)) if ckd.find(Vector(o_cent[i]))[2] <= LINK / 2]
                pack = lambda ids: base64.b64encode(np.asarray(sorted(ids), '<u4').tobytes()).decode()
                rows.append({'role': role, 'bone': bone['key'], 'source': 'contact', 'areaMm2': round(area * 1e6),
                             'tris': {resource: pack(sel), o_res: pack(o_sel)}})
        # With Z-Anatomy on one side, only the single largest opposite-end area is the attachment.
        if known_end and rows:
            rows = [max(rows, key=lambda r: r['areaMm2'])]
        if rows:
            (OUT / f"{m['key']}.json").write_text(json.dumps({'rows': [r.pop('tris') for r in rows]}, separators=(',', ':')) + '\n')
            attachments['muscles'].setdefault(m['key'], []).extend(rows)
            stats['muscles'] += 1; stats['rows'] += len(rows)
            stats['labelled' if known_end else 'unlabelled'] += 1
        else: stats['noContact'] += 1
    # Ligaments and other joint tissue: every contact cluster with a bone, largest first.
    ligaments, lig_stats = {}, {'structures': 0, 'rows': 0, 'noContact': 0}
    for m in (s for s in structures if s['learner']['visible'] and s['layer'] == 'joint' and s['kind'] in LIGAMENT_KINDS):
        _, pts, _ = mesh(m, 'detail')
        kd = kdtree(pts); mlo, mhi = pts.min(0) - .005, pts.max(0) + .005
        rows = []
        for bone in bones:
            blo, bhi = bounds(bone)
            if (blo > mhi).any() or (bhi < mlo).any(): continue
            per_level = {}
            for level in ('detail', 'overview'):
                resource, bp, tris = mesh(bone, level)
                cent = bp[tris].mean(1)
                per_level[level] = (resource, bp, tris, cent, np.flatnonzero([kd.find(Vector(c))[2] <= CONTACT for c in cent]))
            resource, bp, tris, cent, hit = per_level['detail']
            if len(hit) < MIN_TRIS: continue
            for group in clusters(cent[hit]):
                sel = hit[group]
                area = np.linalg.norm(np.cross(bp[tris[sel, 1]] - bp[tris[sel, 0]], bp[tris[sel, 2]] - bp[tris[sel, 0]]), axis=1).sum() / 2
                if len(sel) < MIN_TRIS or area < MIN_AREA: continue
                o_res, _, _, o_cent, o_hit = per_level['overview']
                ckd = kdtree(cent[sel])
                o_sel = [i for i in o_hit if ckd.find(Vector(o_cent[i]))[2] <= LINK] or [i for i in range(len(o_cent)) if ckd.find(Vector(o_cent[i]))[2] <= LINK / 2]
                pack = lambda ids: base64.b64encode(np.asarray(sorted(ids), '<u4').tobytes()).decode()
                rows.append({'role': 'attachment', 'bone': bone['key'], 'source': 'contact', 'areaMm2': round(area * 1e6),
                             'tris': {resource: pack(sel), o_res: pack(o_sel)}})
        rows = sorted(rows, key=lambda r: -r['areaMm2'])[:LIGAMENT_AREAS]
        if rows:
            (OUT / f"{m['key']}.json").write_text(json.dumps({'rows': [r.pop('tris') for r in rows]}, separators=(',', ':')) + '\n')
            ligaments[m['key']] = rows; lig_stats['structures'] += 1; lig_stats['rows'] += len(rows)
        else: lig_stats['noContact'] += 1
    attachments['ligaments'] = ligaments
    attachments['missing'] = sorted(m['key'] for m in muscles if m['key'] not in attachments['muscles'])
    attachments['note'] = ('Z-Anatomy origin/insertion patches per muscle, plus estimated contact areas for muscles and ligaments '
                           '(build_attachments.py, build_attachment_contacts.py)')
    (RUNTIME / 'attachments.json').write_text(json.dumps(attachments, ensure_ascii=False, separators=(',', ':')) + '\n')
    print('CONTACTS', json.dumps({**stats, 'missing': len(attachments['missing']), 'ligaments': lig_stats}), flush=True)


main()
