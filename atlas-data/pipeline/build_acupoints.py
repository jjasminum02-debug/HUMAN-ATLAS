"""Acupoints on the model (ROADMAP 4-1 step 7: 14 channels).

  blender --background --factory-startup --python atlas-data/pipeline/build_acupoints.py
(Blender only for numpy + mathutils.) Writes atlas-data/runtime/acupoints.json and atlas-data/anatomy/acupoint-checks.json.

Each point of acupoint_locations.py is an anchor expression over the landmark library below, in the app frame
(x = subject left, y = up, z = anterior). Landmarks come from Z-Anatomy bone, muscle and vessel geometry; proportional
cun scales come from landmark distances. From the anchor the builder walks outward along the point's direction through
touching tissue layers and stops at the last surface before open space (muscle, fascia, tendon, joint tissue or bone;
the model has no finished skin). The point rides on the rig segment of the nearest bone, so it follows joint movement.
It is kept only when the comparison source (acupuncture.com point page, cached) states the rule's `check` patterns too.
Nearby structures are those whose surface lies within NEAR of the point. Educational positions, not needling guidance.

atlas-data/anatomy/acupoint-checks.json is the exception list: every point with its status (agree, conflict,
noSource, noLandmark = the model lacks the landmark, geometry = a landmark could not be found).
"""
import html
import json
import math
import os
from pathlib import Path
import re
import struct
import sys

import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from acupoint_locations import CHANNELS, POINTS  # noqa: E402
from sinew_channels import ORDER as SINEW_ORDER, SINEWS  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
D1 = ROOT / 'atlas-data/source-cache/datasets/za-full'
SOURCES = ROOT / 'atlas-data/source-cache/acupoints-2026-11-10'
OUT = ROOT / 'atlas-data/runtime/acupoints.json'
CHECKS = ROOT / 'atlas-data/anatomy/acupoint-checks.json'
SINEW_SOURCES = ROOT / 'atlas-data/source-cache/sinews-2026-11-13'
SINEW_OUT = ROOT / 'atlas-data/runtime/sinews.json'
SINEW_CHECKS = ROOT / 'atlas-data/anatomy/sinew-checks.json'
SINEW_STEP, SINEW_NEAR = .01, .01
NEAR, LIFT, GAP, REACH = .012, .0015, .02, .25
SURFACE_LAYERS = {'muscle', 'fascia', 'joint', 'bone'}
NEAR_LAYERS = {'muscle', 'joint', 'bone', 'vessel', 'nerve', 'fascia'}
ORD = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth', 'eleventh', 'twelfth']
ALIASES = {'LU': 'LU|Lu|L', 'LI': 'LI|L\\.I\\.|Co', 'ST': 'ST|St|S', 'SP': 'SP|Sp', 'HT': 'HT|HE|Ht|H', 'SI': 'SI|S\\.I\\.',
           'BL': 'BL|UB|Bl|B', 'KI': 'KI|KD|Kid|K', 'PC': 'PC|PE|P', 'TE': 'TE|SJ|TB|TW|San ?Jiao', 'GB': 'GB|G\\.B\\.',
           'LR': 'LR|LIV|Liv|LV', 'GV': 'GV|Du|DU', 'CV': 'CV|Ren|REN|RN'}


class Defer(Exception):
    """An anchor refers to a point not computed yet."""


def mesh(s):
    """World positions and triangles of a D1 structure (detail LOD)."""
    data = (D1 / s['lods']['detail']['path']).read_bytes(); size = struct.unpack_from('<I', data, 12)[0]
    doc = json.loads(data[20:20 + size]); binary = data[20 + size + 8:]
    prim = doc['meshes'][0]['primitives'][0]
    def accessor(i, dtype, width):
        a = doc['accessors'][i]; view = doc['bufferViews'][a['bufferView']]
        return np.frombuffer(binary, dtype=dtype, count=a['count'] * width, offset=view.get('byteOffset', 0) + a.get('byteOffset', 0))
    p = accessor(prim['attributes']['POSITION'], '<f4', 3).reshape(-1, 3).astype('f8')
    ia = doc['accessors'][prim['indices']]
    tris = accessor(prim['indices'], {5123: '<u2', 5125: '<u4'}[ia['componentType']], 1).reshape(-1, 3).astype('i8')
    m = np.array(s['matrix'], dtype='f8').reshape(4, 4).T
    return p @ m[:3, :3].T + m[:3, 3], tris


def norm(v):
    v = np.asarray(v, dtype='f8'); return v / np.linalg.norm(v)


def V(x, y, z):
    return np.array([x, y, z], dtype='f8')


def lerp(a, b, t, rows=False):
    if rows:  # cross-section of the bone that a/b are the ends of, at fraction t from a
        pts, axis, lo, hi = a.bone
        u = ((pts - a) @ axis) / ((b - a) @ axis)
        sec = pts[np.abs(u - t) < .06]
        return sec if len(sec) else pts[np.argsort(np.abs(u - t))[:20]]
    return np.asarray(a) + (np.asarray(b) - np.asarray(a)) * t


def mid(a, b):
    return lerp(a, b, .5)


def along(a, b, d):
    return np.asarray(a) + norm(np.asarray(b) - np.asarray(a)) * d


def X(pts, v):
    """Extreme of a point set in direction v (mean of points within 1 mm of the extreme)."""
    pts = np.asarray(pts); proj = pts @ norm(v)
    return pts[proj >= proj.max() - .001].mean(0)


def M(pts):
    return np.asarray(pts).mean(0)


def row(pts, y, w=.006, axis=1):
    for width in (w, w * 2, w * 4, .03):
        sel = pts[np.abs(pts[:, axis] - y) < width]
        if len(sel) >= 3: return sel
    raise ValueError(f'empty row at {y:.3f}')


def atY(a, b, y):
    return lerp(a, b, (y - a[1]) / (b[1] - a[1]))


class End(np.ndarray):
    pass


def main():
    d1 = json.loads((D1 / 'structures.json').read_text())['structures']
    runtime = {s['id']: s for s in json.loads((ROOT / 'atlas-data/runtime/structures.json').read_text())['structures']}
    rig = json.loads((ROOT / 'atlas-data/runtime/rig.json').read_text())
    visible = [s for s in d1 if runtime.get(s['id'], {}).get('learner', {}).get('visible')]
    layer = lambda s: runtime[s['id']]['layer']
    cache = {}
    def geo(s):
        if s['id'] not in cache: cache[s['id']] = mesh(s)
        return cache[s['id']]
    by_name = {}
    for s in visible: by_name.setdefault(s['name'], []).append(s)

    # One BVH over the surface layers; face -> structure.
    verts, polys, owners = [], [], []
    for s in visible:
        if layer(s) not in SURFACE_LAYERS: continue
        pts, tris = geo(s); base = len(verts)
        verts.extend(map(Vector, pts)); polys.extend((tris + base).tolist()); owners.extend([s['id']] * len(tris))
    tree = BVHTree.FromPolygons(verts, polys, all_triangles=True)
    print('surface BVH', len(verts), 'vertices', len(polys), 'triangles', flush=True)
    layer_of = {s['id']: layer(s) for s in visible}
    def cast(p, d, dist):
        hit, _, face, t = tree.ray_cast(Vector(p), Vector(d), dist)
        return (np.array(hit), t, face) if hit is not None else (None, None, None)
    def surface(anchor, d):
        """Last surface before open space, walking outward from the anchor along d (or the first surface inward
        when the anchor already lies outside the body)."""
        p = anchor - d * .002; last = None; face_last = None; travelled = 0.
        while travelled < REACH:
            hit, t, face = cast(p, d, REACH - travelled)
            if hit is None or (last is not None and t > GAP) or (last is None and t > GAP + .002): break
            last, face_last = hit, face; p = hit + d * 1e-4; travelled += t
        if last is None:  # anchor outside: nearest surface back along -d
            hit, t, face = cast(anchor + d * .05, -d, .1)
            if hit is None: return None, None
            last, face_last = hit, face
        return last + d * LIFT, runtime[owners[face_last]]['key']
    def outer(q, d, reach=.3):
        """First surface met coming from outside along -d (for drawn lines between known surface points)."""
        hit, _, face = cast(q + d * reach, -d, reach * 1.2)
        if hit is None: return None, None
        # The structure under the line: the outer face, or the first muscle within 2 cm below a fascia or tendon sheath.
        owner, p_, depth = owners[face], hit - d * 1e-4, 0.
        while layer_of[owner] != 'muscle' and depth < .02:
            h2, t2, f2 = cast(p_, -d, .02 - depth)
            if h2 is None: break
            depth += t2; p_ = h2 - d * 1e-4
            if layer_of[owners[f2]] == 'muscle': owner = owners[f2]; break
        return hit + d * LIFT, owner
    surface.outer = outer

    # Rig segment of the nearest bone vertex.
    seg_of = {}
    for name, seg in rig['segments'].items():
        for b in seg['bones']: seg_of[b] = name
    bone_pts, bone_seg = [], []
    for s in visible:
        if runtime[s['id']]['key'] in seg_of:
            pts = geo(s)[0][::3]; bone_pts.append(pts); bone_seg += [seg_of[runtime[s['id']]['key']]] * len(pts)
    bone_pts = np.concatenate(bone_pts)
    bkd = KDTree(len(bone_pts))
    for i, p in enumerate(bone_pts): bkd.insert(Vector(p), i)
    bkd.balance()
    segment = lambda p: bone_seg[bkd.find(Vector(p))[1]]

    GROUPS = {'Trapezius': 'Ascending part of trapezius muscle|Transverse part of trapezius muscle|Descending part of trapezius muscle'}
    def S(names, side):
        out = []
        for n in '|'.join(GROUPS.get(n, n) for n in names.split('|')).split('|'):
            rows = [s for s in by_name.get(n.strip(), []) if side == 'unpaired' or s['side'] in (side, 'unpaired')]
            out += [geo(s)[0] for s in rows]
        if not out: raise ValueError(f'missing {names} {side}')
        return np.concatenate(out)
    rest_joint = lambda jid: np.array(rig['joints'][jid]['centre'])
    up, down, ant, post = V(0, 1, 0), V(0, -1, 0), V(0, 0, 1), V(0, 0, -1)

    # ── unpaired landmarks ──
    U = {}
    def unpaired(f):
        U[f.__name__] = f; return f
    memo = {}
    def u(name):
        if name not in memo: memo[name] = U[name]()
        return memo[name]
    vert_name = lambda v: {'C1': 'Atlas (C1)', 'C2': 'Axis (C2)'}.get(v, f'Vertebra {v}')
    NEXT = {**{f'C{i}': f'C{i + 1}' for i in range(1, 7)}, 'C7': 'T1', **{f'T{i}': f'T{i + 1}' for i in range(1, 12)}, 'T12': 'L1',
            **{f'L{i}': f'L{i + 1}' for i in range(1, 5)}, 'L5': 'S'}
    def spinousTip(v):
        P = S('Sacrum', 'unpaired') if v == 'S' else S(vert_name(v), 'unpaired')
        P = P[np.abs(P[:, 0]) < .01]
        return X(P, post)
    def spinousPost(v):
        P = S('Sacrum', 'unpaired') if v == 'S' else S(vert_name(v), 'unpaired')
        tip = spinousTip(v); return P[(np.abs(P[:, 0]) < .01) & (P[:, 2] < tip[2] + .01)]
    def spinousTop(v):
        return X(spinousPost(v), up)
    def belowSp(v):
        lo = spinousPost(v)[:, 1].min(); nxt = spinousPost(NEXT[v]) if v != 'L5' else S('Sacrum', 'unpaired')
        if v == 'L5': nxt = nxt[(np.abs(nxt[:, 0]) < .01)]; nxt = nxt[nxt[:, 2] < M(nxt)[2]]   # posterior half; the crest top is not its most posterior part
        hi = nxt[:, 1].max()
        return V(0, (lo + hi) / 2, min(spinousTip(v)[2], X(nxt, post)[2]))
    @unpaired
    def headC():
        return M(np.concatenate([S('Parietal bone', 'unpaired'), S('Frontal bone', 'unpaired'), S('Occipital bone', 'unpaired')]))
    @unpaired
    def cHeadX():
        tips = [mastoid(s) for s in ('left', 'right')]
        return abs(tips[0][0] - tips[1][0]) / 9
    def mastoid(side):
        T = S('Temporal bone', side); c = u('headC')
        lat_s = 1 if side == 'left' else -1
        T = T[(T[:, 2] < c[2]) & (np.sign(T[:, 0]) == lat_s)]
        T = T[lat_s * T[:, 0] > np.percentile(lat_s * T[:, 0], 50)]   # lateral half: the mastoid, not the styloid process
        return X(T, down)
    @unpaired
    def arc():
        """Outer head and neck outline in the midsagittal plane, glabella over the vertex to the C7 spinous process."""
        c = u('headC'); F = S('Frontal bone', 'unpaired'); F = F[np.abs(F[:, 0]) < .006]
        # Glabella: the most prominent midline point of the frontal bone just above the orbits (pupil level + 3.5 cm).
        py = M([X(S(m, 'right'), ant) for m in ('Superior rectus muscle', 'Inferior rectus muscle')])[1]
        g = X(F[(F[:, 1] > py) & (F[:, 1] < py + .035)], ant); c7 = spinousTip('C7'); e = u('eop')
        a0 = math.atan2(g[1] - c[1], g[2] - c[2]); a1 = math.atan2(e[1] - c[1], e[2] - c[2])
        if a1 < a0: a1 += 2 * math.pi   # over the top: angle increases from front (z) to up (y) to back (-z)
        angles, radii = [], []
        for a in np.linspace(a0, a1, 600):
            d = V(0, math.sin(a), math.cos(a)); hit, _, _ = cast(c + d * .4 + V(.0005, 0, 0), -d, .4)
            if hit is not None: angles.append(a); radii.append(np.linalg.norm(hit - c))
        # Outermost envelope, smoothed: separate tissue layers make the raw outline zigzag and inflate its length.
        r = np.array(radii); r = np.array([r[max(0, i - 3):i + 4].max() for i in range(len(r))])
        r = np.array([np.median(r[max(0, i - 6):i + 7]) for i in range(len(r))])
        out = [c + V(0, math.sin(a), math.cos(a)) * ri for a, ri in zip(angles, r)]
        # Below the external occipital protuberance: the back of the neck, swept downward to the C7 spinous process.
        for y in np.arange(e[1] - .002, c7[1], -.002):
            hit, _, _ = cast(V(.0005, y, -.4), V(0, 0, 1), .45)
            if hit is not None and hit[2] < c[2]: out.append(hit)
        out.append(c7); out = np.array(out); out[:, 0] = 0
        s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(out, axis=0), axis=1))])
        return out, s
    @unpaired
    def vertexS():
        pts, s = u('arc'); return s[int(np.argmax(pts[:, 1]))]
    @unpaired
    def cHead():
        return u('vertexS') / 8
    def headArc(a, latCun=0, side='right'):
        # Glabella to C7 is 18 cun with GV20 (5 cun above the anterior hairline, i.e. 8 cun from the glabella) at the
        # vertex; the two parts are scaled separately because this model's neck is long for its skull.
        pts, s = u('arc'); sv = u('vertexS')
        t = a / 8 * sv if a <= 8 else sv + (a - 8) / 10 * (s[-1] - sv)
        i = min(np.searchsorted(s, t), len(pts) - 1)
        lat = 1 if side == 'left' else -1
        return pts[i] + V(lat, 0, 0) * latCun * u('cHeadX')
    @unpaired
    def eop():
        # The nuchal ligament's upper attachment marks the external occipital protuberance (the most posterior point of
        # the skull is higher, the opisthocranion).
        top = X(S('Nuchal ligament', 'unpaired'), up)
        O = S('Occipital bone', 'unpaired'); O = O[(np.abs(O[:, 0]) < .008) & (np.abs(O[:, 1] - top[1]) < .004)]
        return X(O, post)
    @unpaired
    def notch():
        Mn = S('Manubrium of sternum', 'unpaired'); return X(Mn[np.abs(Mn[:, 0]) < .01], up)
    @unpaired
    def xiphY():
        return S('Xiphoid process', 'unpaired')[:, 1].max()
    @unpaired
    def pubis():
        Hp = np.concatenate([S('Hip bone', 'left'), S('Hip bone', 'right')]); Hp = Hp[np.abs(Hp[:, 0]) < .015]
        Hp = Hp[Hp[:, 2] > np.percentile(Hp[:, 2], 60)]
        return Hp[:, 1].max(), Hp[:, 1].min()
    @unpaired
    def umbY():
        return u('xiphY') - 8 / 13 * (u('xiphY') - u('pubis')[0])
    @unpaired
    def thyroidY():
        return X(S('Thyroid cartilage', 'unpaired'), ant)[1]
    @unpaired
    def cricoidY():
        return X(S('Cricoid cartilage', 'unpaired'), ant)[1]
    @unpaired
    def hyoidTop():
        Hy = S('Hyoid bone', 'unpaired'); return X(Hy[np.abs(Hy[:, 0]) < .01], up + ant)
    @unpaired
    def coccyxTip():
        return X(S('Coccyx', 'unpaired'), down)
    @unpaired
    def anus():
        return M(S('External anal sphincter', 'unpaired'))
    @unpaired
    def sacrumTree():
        P, T = [], []
        for s in by_name['Sacrum']:
            p, t = geo(s); T.append(t + sum(len(x) for x in P)); P.append(p)
        P = np.concatenate(P); T = np.concatenate(T)
        return BVHTree.FromPolygons([Vector(p) for p in P], T.tolist(), all_triangles=True), P
    def holes(bvh, xs, ys, z0, dz, deeper=.006, dirz=1.):
        """Grid of rays along z; cells whose first hit is much deeper than the surrounding surface (or missing)."""
        depth = np.full((len(ys), len(xs)), np.nan)
        for i, y in enumerate(ys):
            for j, x in enumerate(xs):
                hit, _, _, t = bvh.ray_cast(Vector((x, y, z0)), Vector((0, 0, dirz)), dz)
                depth[i, j] = t if hit is not None else np.inf
        finite = depth[np.isfinite(depth)]
        base = np.median(finite) if len(finite) else 0
        mask = depth > base + deeper
        # local surface: compare with the row median too (the sacrum curves)
        for i in range(len(ys)):
            r = depth[i][np.isfinite(depth[i])]
            if len(r): mask[i] = depth[i] > np.median(r) + deeper
        seen = np.zeros_like(mask); comps = []
        for i in range(len(ys)):
            for j in range(len(xs)):
                if not mask[i, j] or seen[i, j]: continue
                stack, cells = [(i, j)], []; seen[i, j] = True
                while stack:
                    a, b = stack.pop(); cells.append((a, b))
                    for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        na, nb = a + da, b + db
                        if 0 <= na < len(ys) and 0 <= nb < len(xs) and mask[na, nb] and not seen[na, nb]:
                            seen[na, nb] = True; stack.append((na, nb))
                comps.append(cells)
        return [(np.mean([xs[b] for _, b in c]), np.mean([ys[a] for a, _ in c]), len(c)) for c in comps]
    def foramina(side):
        bvh, P = u('sacrumTree'); lat = 1 if side == 'left' else -1
        top, bot = P[:, 1].max(), P[:, 1].min()
        xs = lat * np.arange(.006, .04, .0015); ys = np.arange(top - .005, bot + .01, -.0015)
        # Posterior foramina lie 12-30 mm from the midline; nearer is the sacral canal and the lumbosacral gap,
        # farther the lateral edge of the sacrum and the lumbosacral facet gaps.
        raw = holes(bvh, xs, ys, P[:, 2].min() - .05, .15)
        if os.environ.get('ACUPOINT_DEBUG'): print('HOLES', side, [(round(float(x), 4), round(float(y), 4), n) for x, y, n in raw])
        found = [(x, y, n) for x, y, n in raw if n >= 4 and .012 < abs(x) < .03]
        found = sorted(found, key=lambda h: -h[1])
        # merge components closer than 8 mm vertically, keep the 4 highest
        merged = []
        for h in found:
            if merged and abs(merged[-1][1] - h[1]) < .008: continue
            merged.append(h)
        if len(merged) < 4: raise ValueError(f'found {len(merged)} sacral foramina')
        return merged[:4]
    @unpaired
    def sacralHiatus():
        bvh, P = u('sacrumTree'); top, bot = P[:, 1].max(), P[:, 1].min()
        ys = np.arange(bot + (top - bot) * .45, bot - .005, -.0015); xs = np.arange(-.006, .0061, .0015)
        found = [h for h in holes(bvh, xs, ys, P[:, 2].min() - .05, .15, deeper=.004) if h[2] >= 3]
        if not found: raise ValueError('no sacral hiatus')
        h = max(found, key=lambda h: h[2]); row_ = P[np.abs(P[:, 1] - h[1]) < .004]
        return V(0, h[1], X(row_[np.abs(row_[:, 0]) < .01], post)[2])

    def side_ns(side):
        lat_s = 1 if side == 'left' else -1; s = side[0]
        lat, med = V(lat_s, 0, 0), V(-lat_s, 0, 0)
        L = {}
        def lm(f):
            L[f.__name__] = f; return f
        ns_cache = {}
        def g(name):
            if name not in ns_cache: ns_cache[name] = L[name]()
            return ns_cache[name]
        SS = lambda n: S(n, side)
        half = lambda P: P[np.sign(P[:, 0]) == lat_s]
        # arm
        @lm
        def elbow(): return rest_joint(f'elbow_{s}')
        @lm
        def styloid():
            R = SS('Radius'); low = R[R[:, 1] < np.percentile(R[:, 1], 5)]; return X(low, lat)
        @lm
        def wristY(): return g('styloid')[1] + .005
        @lm
        def biceps(): return np.concatenate([SS('Long head of biceps brachii'), SS('Short head of biceps brachii')])
        @lm
        def fold():
            H, pec = SS('Humerus'), SS('Sternocostal head of pectoralis major muscle')
            near_arm = pec[lat_s * pec[:, 0] > lat_s * H[:, 0].mean() - .06]; return X(near_arm, down)
        @lm
        def foldP():
            H = SS('Humerus'); P = np.concatenate([SS('Latissimus dorsi muscle'), SS('Teres major muscle')])
            P = P[(lat_s * P[:, 0] > lat_s * H[:, 0].mean() - .06) & (P[:, 2] < H[:, 2].mean())]; return X(P, down)
        @lm
        def tendon():
            B = g('biceps'); return M(B[np.abs(B[:, 1] - g('elbow')[1]) < .02])
        @lm
        def cubital(): t = g('tendon'); return V(t[0], g('elbow')[1] + .01, t[2])
        @lm
        def creaseR(): return g('cubital') + lat * .012
        @lm
        def creaseU(): return g('cubital') + med * .012
        @lm
        def cArm(): return (g('fold')[1] - g('cubital')[1]) / 9
        @lm
        def cFore(): return (g('cubital')[1] - g('wristY')) / 12
        def bicepsLat(cun):
            y = g('fold')[1] + (g('cubital')[1] - g('fold')[1]) * cun / 9
            return X(row(g('biceps'), y), lat) + lat * .003
        def bicepsMed(cun):
            y = g('fold')[1] + (g('cubital')[1] - g('fold')[1]) * cun / 9
            return X(row(g('biceps'), y), med)
        def bicepsGap(cun):
            y = g('fold')[1] - cun * g('cArm')
            return mid(M(row(SS('Long head of biceps brachii'), y)), M(row(SS('Short head of biceps brachii'), y)))
        @lm
        def epiL(): H = SS('Humerus'); return X(H[H[:, 1] < np.percentile(H[:, 1], 12)], lat)
        @lm
        def epiM(): H = SS('Humerus'); return X(H[H[:, 1] < np.percentile(H[:, 1], 12)], med)
        @lm
        def olecranon(): Ul = SS('Ulna'); return X(Ul[Ul[:, 1] > np.percentile(Ul[:, 1], 94)], post)
        @lm
        def ulnStyloid(): Ul = SS('Ulna'); return M(Ul[Ul[:, 1] <= np.percentile(Ul[:, 1], 1)])
        @lm
        def greaterTub(): H = SS('Humerus'); return X(H[H[:, 1] > np.percentile(H[:, 1], 92)], lat + .2 * ant)
        @lm
        def axilla():
            A = SS('Axillary artery'); y = (g('fold')[1] + rest_joint(f'shoulder_{s}')[1]) / 2; return M(row(A, y))
        def artery(y):
            A = SS('Radial artery'); r = A[np.abs(A[:, 1] - y) < .004]
            return (M(r) if len(r) else A[np.argmin(np.abs(A[:, 1] - y))]) + lat * .004
        def fcuRadial(cun):
            F = SS('Humeral head of flexor carpi ulnaris|Ulnar head of flexor carpi ulnaris')
            return X(row(F, g('wristY') + cun * g('cFore')), lat) + lat * .003
        def plFcr(cun):
            y = g('wristY') + cun * g('cFore')
            try: pl = M(row(SS('Palmaris longus muscle'), y, w=.004))
            except ValueError: pl = None
            fcr = M(row(SS('Flexor carpi radialis'), y, w=.004))
            return mid(pl, fcr) if pl is not None else fcr + med * .006
        def between(y):
            return mid(M(row(SS('Radius'), y)), M(row(SS('Ulna'), y)))
        def nail(d, v):
            T = SS(f'Distal phalanx of {ORD[d - 1]} finger of hand'); tip, base = T[:, 1].min(), T[:, 1].max()
            return X(row(T, tip + (base - tip) * .3, w=.003), v)
        def ends(name):
            P = SS(name); c = P.mean(0); axis = np.linalg.svd(P - c, full_matrices=False)[2][0]
            t = (P - c) @ axis; lo, hi = P[t <= t.min() + .1 * (t.max() - t.min())].mean(0), P[t >= t.max() - .1 * (t.max() - t.min())].mean(0)
            foot = 'foot' in name or 'metatarsal' in name
            prox, dist = (lo, hi) if (lo[2] < hi[2] if foot else lo[1] > hi[1]) else (hi, lo)
            out = []
            for e in (prox, dist):
                a = e.view(End); a.bone = (P, axis, None, None); out.append(a)
            return tuple(out)
        # shoulder and scapula
        @lm
        def scap(): return SS('Scapula')
        @lm
        def acrTip(): P = g('scap'); return X(P[P[:, 1] > np.percentile(P[:, 1], 80)], lat)
        @lm
        def acromion():
            P, t = g('scap'), g('acrTip'); return P[(lat_s * P[:, 0] > lat_s * t[0] - .018) & (P[:, 1] > t[1] - .02)]
        @lm
        def acrAnt(): return X(g('acromion'), ant + .3 * lat)
        @lm
        def acrAngle(): return X(g('acromion'), post + .3 * lat)
        @lm
        def clavLat(): return X(SS('Clavicle'), lat)
        @lm
        def clavMed(): return X(SS('Clavicle'), med)
        def spineAt(x0):
            P = g('scap'); col = P[(np.abs(P[:, 0] - x0) < .005) & (P[:, 1] > np.percentile(P[:, 1], 40))]
            return X(col, post), col
        @lm
        def spineRoot():
            P = g('scap'); xm = P[np.argmin(lat_s * P[:, 0]), 0]
            return spineAt(xm + lat_s * .01)[0]
        @lm
        def spineMid(): return spineAt((g('spineRoot')[0] + g('acrAngle')[0]) / 2)[0]
        @lm
        def spineLat(): return spineAt(g('clavLat')[0] - lat_s * .02)[0]
        def spineLowAt(x0):
            crest, col = spineAt(x0); sel = col[(col[:, 2] < crest[2] + .012) & (np.abs(col[:, 1] - crest[1]) < .03)]
            return sel[:, 1].min() - .004
        @lm
        def infAngle(): return X(g('scap'), down)
        @lm
        def supAngle():
            P = g('scap'); return X(P[lat_s * P[:, 0] < np.median(lat_s * P[:, 0])], up)
        @lm
        def supraFossa():
            crest, col = spineAt(g('spineMid')[0]); top = col[:, 1].max(); y = (crest[1] + top) / 2
            return X(row(col, y, w=.004), post)
        @lm
        def cBack(): return abs(g('spineRoot')[0]) / 3
        def back(v, cun):
            b = belowSp(v); return V(lat_s * cun * g('cBack'), b[1], b[2])
        def sacral(i, cun):
            x, y, _ = foramina(side)[i - 1]; P = u('sacrumTree')[1]; r = P[(np.abs(P[:, 1] - y) < .004) & (np.abs(P[:, 0]) < .015)]
            return V(lat_s * cun * g('cBack'), y, X(r, post)[2])
        def foramen(i):
            x, y, _ = foramina(side)[i - 1]; P = u('sacrumTree')[1]; r = P[(np.abs(P[:, 1] - y) < .004) & (np.abs(P[:, 0] - x) < .01)]
            return V(x, y, X(r, post)[2])
        # chest and abdomen
        @lm
        def cChX(): return abs((g('clavMed')[0] + g('clavLat')[0]) / 2) / 4
        @lm
        def cChY(): return (u('notch')[1] - u('xiphY')) / 9
        @lm
        def cAbU(): return (u('xiphY') - u('umbY')) / 8
        @lm
        def cAbL(): return (u('umbY') - u('pubis')[0]) / 5
        def clavBelow(cun, drop=.006):
            Cl = SS('Clavicle'); b = Cl[np.abs(Cl[:, 0] - lat_s * cun * g('cChX')) < .008]
            return X(b, down) + V(0, -drop, .004)
        def clavAbove(cun):
            Cl = SS('Clavicle'); b = Cl[np.abs(Cl[:, 0] - lat_s * cun * g('cChX')) < .008]
            return X(b, up) + up * .008 + post * .008
        def rib(n):
            names = f'{ORD[n - 1].capitalize()} rib' + (f'|Costal cartilage of {ORD[n - 1]} rib' if n <= 10 else '')
            return SS(names)
        def ics(n, cun):
            x0 = lat_s * cun * g('cChX'); zmid = M(rib(4))[2]
            def band(k):
                P = rib(k); P = P[P[:, 2] > zmid - .02]
                for w in (.006, .012, .02):
                    b = P[np.abs(P[:, 0] - x0) < w]
                    if len(b) >= 3: return b[b[:, 2] > X(b, ant)[2] - .015]
                return b
            a, b = band(n), band(n + 1)
            if len(a) < 3 or len(b) < 3: raise ValueError(f'no rib {n}/{n + 1} at {cun} cun')
            lo = a[:, 1].min(); b = b[b[:, 1] < lo + .005]
            if len(b) < 3: raise ValueError(f'rib {n + 1} not below rib {n}')
            y = (lo + b[:, 1].max()) / 2
            return V(x0, y, max(X(a, ant)[2], X(b, ant)[2]) - .006)
        def icsAx(n):
            z0 = (g('fold')[2] + g('foldP')[2]) / 2
            def band(k):
                P = rib(k); return P[(np.abs(P[:, 2] - z0) < .006) & (lat_s * P[:, 0] > 0)]
            a, b = band(n), band(n + 1); lo = a[:, 1].min(); b = b[b[:, 1] < lo + .005]
            if len(a) < 3 or len(b) < 3: raise ValueError(f'no rib {n}/{n + 1} on the midaxillary line')
            return V(max(X(a, lat)[0], X(b, lat)[0], key=abs) - lat_s * .006, (lo + b[:, 1].max()) / 2, z0)
        def abd(c, cun):
            y = u('umbY') + (c * g('cAbU') if c >= 0 else c * g('cAbL'))
            ra = SS('Rectus abdominis muscle')
            try: zc = M(row(ra, y, w=.008))[2] - .02
            except ValueError: zc = M(ra)[2] - .02
            return V(lat_s * cun * g('cChX'), y, zc)
        def ribTip(name):
            P = SS(name); head = P[np.argmin(np.abs(P[:, 0]))]
            return P[np.argmax(np.linalg.norm(P - head, axis=1))]
        # neck and face
        @lm
        def scmGap():
            Sc = SS('Sternocleidomastoid muscle'); y = X(SS('Clavicle'), med + up)[1] + .012; r = row(Sc, y)
            return V((X(r, med)[0] + X(r, lat)[0]) / 2, y, M(r)[2])
        @lm
        def mastoidTip(): return mastoid(side)
        @lm
        def mandible(): return half(S('Mandible', 'unpaired'))
        @lm
        def mandAngle(): return X(g('mandible'), down + post)
        @lm
        def ramus():
            P, a = g('mandible'), g('mandAngle'); return P[(lat_s * P[:, 0] > lat_s * a[0] - .015) & (P[:, 1] > a[1] + .02)]
        @lm
        def ramusProfile():
            P = g('ramus'); zs = np.arange(P[:, 2].min(), P[:, 2].max(), .002)
            prof = [(z, X(P[np.abs(P[:, 2] - z) < .0015], up)) for z in zs if (np.abs(P[:, 2] - z) < .0015).sum() >= 2]
            return prof
        @lm
        def condyle():
            prof = g('ramusProfile'); n = len(prof); back = prof[:n // 2]; return max(back, key=lambda r: r[1][1])[1]
        @lm
        def mandNotch():
            prof = g('ramusProfile'); n = len(prof)
            ic = max(range(n // 2), key=lambda i: prof[i][1][1]); ik = max(range(n // 2, n), key=lambda i: prof[i][1][1])
            return min(prof[ic:ik + 1], key=lambda r: r[1][1])[1]
        @lm
        def condylePost():
            P, c = g('ramus'), g('condyle'); return X(P[P[:, 1] > c[1] - .012], post) + post * .003
        @lm
        def masseterFrontLow():
            Ms = SS('Superficial part of masseter'); return X(Ms[Ms[:, 1] < Ms[:, 1].min() + .01], ant)
        @lm
        def archAbove():
            n = g('mandNotch'); B = np.concatenate([SS('Zygomatic bone'), SS('Temporal bone')])
            col = B[(np.abs(B[:, 2] - n[2]) < .005) & (B[:, 1] > n[1]) & (B[:, 1] < n[1] + .04)]
            col = col[lat_s * col[:, 0] > np.percentile(lat_s * col[:, 0], 80)]
            t = X(col, up); return t + up * .006
        @lm
        def pupil():
            ends_ = [X(SS(m), ant) for m in ('Medial rectus muscle', 'Lateral rectus muscle', 'Superior rectus muscle', 'Inferior rectus muscle')]
            c = M(ends_); return V(c[0], c[1], max(e[2] for e in ends_) + .008)
        @lm
        def faceBone(): return np.concatenate([SS('Maxilla'), SS('Zygomatic bone'), SS('Frontal bone'), SS('Lacrimal bone'), SS('Nasal bone')])
        @lm
        def orbitInf():
            p, B = g('pupil'), g('faceBone')
            c = B[(np.abs(B[:, 0] - p[0]) < .004) & (B[:, 1] < p[1]) & (B[:, 1] > p[1] - .03) & (B[:, 2] > p[2] - .025)]
            return X(c[c[:, 2] >= np.percentile(c[:, 2], 70)], up)
        @lm
        def infraorbitalForamen():
            p, r = g('pupil'), g('orbitInf'); Mx = by_name['Maxilla']
            P, T = [], []
            for s_ in Mx:
                if s_['side'] not in (side, 'unpaired'): continue
                pp, tt = geo(s_); T.append(tt + sum(len(x) for x in P)); P.append(pp)
            P = np.concatenate(P); bvh = BVHTree.FromPolygons([Vector(q) for q in P], np.concatenate(T).tolist(), all_triangles=True)
            xs = np.arange(p[0] - .01, p[0] + .0101, .001); ys = np.arange(r[1] - .003, r[1] - .016, -.001)
            found = [h for h in holes(bvh, xs, ys, p[2] + .05, .1, deeper=.003, dirz=-1.) if h[2] >= 3]
            if not found: raise ValueError('no infraorbital foramen within 16 mm below the orbital margin')
            h = max(found, key=lambda h: h[1]); near_ = P[(np.abs(P[:, 0] - h[0]) < .004) & (np.abs(P[:, 1] - h[1]) < .004)]
            return V(h[0], h[1], X(near_, ant)[2])
        @lm
        def canthusMed():
            p, B = g('pupil'), g('faceBone')
            c = B[(lat_s * B[:, 0] > .004) & (lat_s * B[:, 0] < lat_s * p[0]) & (np.abs(B[:, 1] - p[1]) < .004) & (B[:, 2] > p[2] - .025)]
            return X(c, lat) + lat * .003
        @lm
        def canthusLat():
            p, B = g('pupil'), g('faceBone')
            c = B[(lat_s * B[:, 0] > lat_s * p[0]) & (np.abs(B[:, 1] - p[1]) < .004) & (B[:, 2] > p[2] - .03)]
            return X(c, med) + med * .002
        def brow(x0):
            p, F = g('pupil'), SS('Frontal bone')
            # Supraorbital margin: the lowest frontal-bone point near the front of the orbit (the roof lies further back).
            c = F[(np.abs(F[:, 0] - x0) < .004) & (F[:, 1] > p[1]) & (F[:, 1] < p[1] + .04) & (F[:, 2] > p[2] - .008)]
            if len(c) < 3: c = F[(np.abs(F[:, 0] - x0) < .004) & (F[:, 1] > p[1]) & (F[:, 1] < p[1] + .04) & (F[:, 2] > p[2] - .02)]
            return X(c, down) + up * .003
        @lm
        def browY(): return brow(g('pupil')[0])[1]
        @lm
        def browMed(): return brow(g('canthusMed')[0])
        @lm
        def browLat(): return brow(g('canthusLat')[0] + med[0] * .004)
        def zygoLowBelow(x0):
            Z = SS('Zygomatic bone'); return X(Z[np.abs(Z[:, 0] - x0) < .005], down) + down * .004
        @lm
        def ala(): return half(S('Major alar cartilage', 'unpaired'))
        @lm
        def alaLat(): return X(g('ala'), lat)
        @lm
        def alaLow(): return X(g('ala'), down)
        @lm
        def noseTip(): A = S('Major alar cartilage', 'unpaired'); return X(A, ant)
        @lm
        def mouthCorner(): return X(half(S('Orbicularis oris muscle', 'unpaired')), lat)
        def lipUpper(x0):
            top = min(X(S('Major alar cartilage', 'unpaired'), down)[1], X(S('Nasal septal cartilage', 'unpaired'), down)[1])
            y = top - (top - g('mouthCorner')[1]) / 3; O = S('Orbicularis oris muscle', 'unpaired')
            r = O[(np.abs(O[:, 1] - y) < .003) & (np.abs(O[:, 0] - x0) < .006)]
            return V(x0, y, X(r, ant)[2] - .003)
        @lm
        def lipTubercle():
            O = S('Orbicularis oris muscle', 'unpaired'); y0 = g('mouthCorner')[1]
            return X(O[(np.abs(O[:, 0]) < .004) & (O[:, 1] > y0) & (O[:, 1] < y0 + .012)], ant)
        @lm
        def mentolabial():
            P = np.concatenate([S(n, 'unpaired') for n in ('Orbicularis oris muscle', 'Mandible')] + [S(n, side) for n in ('Mentalis muscle', 'Depressor labii inferioris')])
            P = P[np.abs(P[:, 0]) < .004]; y0 = g('mouthCorner')[1]
            ys = np.arange(y0, P[:, 1].min(), -.001)
            prof = [(y, P[np.abs(P[:, 1] - y) < .0008][:, 2].max()) for y in ys if (np.abs(P[:, 1] - y) < .0008).sum()]
            lip = max(prof[:15], key=lambda r: r[1]); rest = [r for r in prof if r[0] < lip[0] - .006]
            chin = max(rest, key=lambda r: r[1]); between_ = [r for r in prof if chin[0] < r[0] < lip[0]]
            y, z = min(between_, key=lambda r: r[1]); return V(0, y, z - .003)
        # lower limb
        @lm
        def kneeY(): return rest_joint(f'knee_{s}')[1]
        @lm
        def popliteal(): return rest_joint(f'knee_{s}')
        @lm
        def ankleY(): return rest_joint(f'ankle_{s}')[1]
        @lm
        def fib(): return SS('Fibula')
        @lm
        def tib(): return SS('Tibia')
        @lm
        def fem(): return SS('Femur')
        @lm
        def latMall(): F = g('fib'); return X(F[F[:, 1] < F[:, 1].min() + .03], lat)
        @lm
        def latMallTip(): return X(g('fib'), down)
        @lm
        def medMall(): T = g('tib'); return X(T[T[:, 1] < T[:, 1].min() + .03], med)
        @lm
        def medCondLowY():
            T = g('tib'); top = T[:, 1].max(); ys = np.arange(top - .002, top - .12, -.002)
            ext = np.array([lat_s * -X(row(T, y, w=.002), med)[0] for y in ys])
            c, shaft = ext[:15].max(), ext[-1]
            i = int(np.argmax(ext[:15])); thr = shaft + .3 * (c - shaft)
            for j in range(i, len(ys)):
                if ext[j] < thr: return ys[j]
            return ys[-1]
        @lm
        def cLegL(): return (g('kneeY') - g('latMall')[1]) / 16
        @lm
        def cLegM(): return (g('medCondLowY') - g('medMall')[1]) / 13
        @lm
        def greaterTroch(): F = g('fem'); return X(F[F[:, 1] > np.percentile(F[:, 1], 88)], lat)
        @lm
        def femEpiLat(): F = g('fem'); return X(F[F[:, 1] < np.percentile(F[:, 1], 10)], lat)
        @lm
        def femEpiMed(): F = g('fem'); return X(F[F[:, 1] < np.percentile(F[:, 1], 10)], med)
        @lm
        def cThigh(): return (g('greaterTroch')[1] - g('kneeY')) / 19
        @lm
        def cThighM(): return (u('pubis')[0] - g('femEpiMed')[1]) / 18
        @lm
        def pubisTopY(): return u('pubis')[0]
        @lm
        def pubisLowY(): return u('pubis')[1]
        @lm
        def asis():
            Hp = SS('Hip bone'); return X(Hp[(lat_s * Hp[:, 0] > .05) & (Hp[:, 1] > u('pubis')[0] + .04)], ant)
        @lm
        def patella(): return SS('Patella')
        @lm
        def patBaseLat(): P = g('patella'); return X(P[P[:, 1] > P[:, 1].max() - .01], lat)
        @lm
        def patBaseMed(): P = g('patella'); return X(P[P[:, 1] > P[:, 1].max() - .01], med)
        @lm
        def kneeEyeLat():
            apex = X(g('patella'), down); T = g('tib'); plateau = T[:, 1].max(); y = (apex[1] + plateau) / 2
            cond = X(row(np.concatenate([g('fem'), T]), y, w=.004), lat + ant)
            return V(mid(apex, cond)[0], y, max(apex[2], cond[2]) - .004)
        def tibCrest(y): return X(row(g('tib'), y), ant)
        def tibMedBorder(y): return X(row(g('tib'), y), med + .6 * post) + post * .004
        def tibMedFace(y):
            r = row(g('tib'), y); return mid(X(r, ant), X(r, med + .6 * post))
        @lm
        def fibHead(): F = g('fib'); return X(F[F[:, 1] > F[:, 1].max() - .015], lat)
        @lm
        def navTub(): return X(SS('Navicular bone'), med + .3 * down)
        @lm
        def heelBack(): return X(SS('Calcaneus'), post)
        @lm
        def glutealFold():
            Gm, F = SS('Gluteus maximus muscle'), g('fem'); xf = M(F[F[:, 1] > np.percentile(F[:, 1], 60)])[0]
            return X(Gm[np.abs(Gm[:, 0] - xf) < .012], down)
        @lm
        def gastroJoin():
            return mid(X(SS('Medial head of gastrocnemius'), down), X(SS('Lateral head of gastrocnemius'), down))
        def below(P, p):
            c = P[(np.abs(P[:, 0] - p[0]) < .006) & (np.abs(P[:, 2] - p[2]) < .006) & (P[:, 1] < p[1])]
            return X(c, up)
        def toeNail(d, v):
            T = SS(f'Distal phalanx of {ORD[d - 1]} finger of foot'); tip, base = T[:, 2].max(), T[:, 2].min()
            return X(row(T, tip + (base - tip) * .3, w=.003, axis=2), v)
        # scalars shared with the unpaired set
        for k in ('cHeadX', 'cHead', 'eop', 'notch', 'umbY', 'thyroidY', 'cricoidY', 'hyoidTop', 'coccyxTip', 'anus', 'sacralHiatus', 'headC'):
            L[k] = (lambda k=k: u(k))
        L['eopBelow'] = lambda: hairP(1)
        def hairA(c, latCun=0): return headArc(3 + c, latCun, side)
        def hairP(c, latCun=0): return headArc(15 - c, latCun, side)
        fns = dict(S=SS, row=row, X=X, M=M, V=V, lerp=lerp, mid=mid, along=along, norm=norm, atY=atY, abs=abs,
                   bicepsLat=bicepsLat, bicepsMed=bicepsMed, bicepsGap=bicepsGap, artery=artery, fcuRadial=fcuRadial, plFcr=plFcr,
                   between=between, nail=nail, ends=ends, spineLowAt=spineLowAt, back=back, sacral=sacral, foramen=foramen,
                   clavBelow=clavBelow, clavAbove=clavAbove, ics=ics, icsAx=icsAx, abd=abd, ribTip=ribTip, brow=brow,
                   zygoLowBelow=zygoLowBelow, lipUpper=lipUpper, tibCrest=tibCrest, tibMedBorder=tibMedBorder, tibMedFace=tibMedFace,
                   below=below, toeNail=toeNail, hairA=hairA, hairP=hairP, spinousTip=spinousTip, spinousTop=spinousTop, belowSp=belowSp,
                   lat=lat, med=med, ant=ant, post=post, up=up, down=down)
        return L, g, fns

    codes = {p['code'] for p in POINTS}
    class NS(dict):
        def __init__(self, L, g, done):
            super().__init__(); self.L, self.g, self.done = L, g, done
        def __missing__(self, key):
            if key in self.done: return self.done[key]
            if key in codes: raise Defer(key)
            if key in self.L: return self.g(key)
            raise KeyError(key)

    points, failures, anchor_at = [], {}, {}
    midline = {k for k, v in CHANNELS.items() if v.get('midline')}
    for side in ('right', 'left'):
        L, g, fns = side_ns(side)
        anchors, todo = {}, [p for p in POINTS if p['at']]
        while todo:
            progress, rest = False, []
            for p in todo:
                try:
                    a = np.asarray(eval(p['at'], fns, NS(L, g, anchors)), dtype='f8')
                    if p['code'][:2] in midline: a = a.copy(); a[0] = .0005   # just off the left/right mesh seam
                    anchors[p['code']] = a; progress = True
                except Defer: rest.append(p)
                except Exception as e:  # noqa: BLE001
                    failures[p['code']] = f'{type(e).__name__}: {e}'; progress = True
            if not progress:
                for p in rest: failures[p['code']] = 'unresolved reference'
                break
            todo = rest
        for p in POINTS:
            c = p['code']
            if c not in anchors or (side == 'left' and c[:2] in midline): continue
            a = anchors[c]; anchor_at.setdefault(c, {})[side] = [round(float(v), 4) for v in a]
            if p['dir'] == 'radial': d = norm(a - u('headC'))
            else: d = norm(eval(p['dir'], fns, {}))
            if c[:2] in midline: d = d.copy(); d[0] = 0; d = norm(d)
            pos, on = surface(a, d)
            if pos is None: failures[c] = 'no surface along the direction'; continue
            near = []
            for x in visible:
                if layer(x) not in NEAR_LAYERS: continue
                b = runtime[x['id']]['geometry']['bounds']
                if not all(b[0][i] - NEAR < pos[i] < b[1][i] + NEAR for i in range(3)): continue
                dist = float(np.min(np.linalg.norm(geo(x)[0] - pos, axis=1)))
                if dist <= NEAR: near.append((dist, runtime[x['id']]['key']))
            points.append({'code': c, 'side': 'midline' if c[:2] in midline else side, 'segment': segment(pos),
                           'position': [round(float(v), 5) for v in pos], 'normal': [round(float(v), 4) for v in d],
                           'surfaceOf': on, 'near': list(dict.fromkeys(k for _, k in sorted(near)))[:8]})
        print(side, len(anchors), 'anchors', flush=True)

    # Comparison source.
    def expand(pattern):
        return re.sub(r'@([A-Z]{2})(\d+)', lambda m: rf'\b(?:{ALIASES[m[1]]})[\s.\-]?{m[2]}\b', pattern)
    # Source wording normalised before matching (same rules for every point; recorded in the checks file).
    NORMALIZE = [(r'(\d)\.0\b', r'\1'), (r'(?<![\d.])\.(\d)', r'0.\1'), (r'(?<=[a-z])-(?=[a-z])', ''), (r'\s*\([^)]*\)', ''),
                 (r'external malleolus', 'lateral malleolus'), (r'internal malleolus', 'medial malleolus'),
                 (r'great trochanter', 'greater trochanter'), (r'metatarsodigital', 'metatarsophalangeal'),
                 (r'metacarpodigital', 'metacarpophalangeal'), (r'floating rib', 'rib'), (r'calcaneum', 'calcaneus')]
    NORMALIZE += [(rf'\b{n}(st|nd|rd|th)\b', w) for n, w in zip(range(12, 0, -1), ORD[::-1])]   # 1st -> first
    def normalize(s):
        for a, b in NORMALIZE: s = re.sub(a, b, s, flags=re.I)
        return s
    manifest = json.loads((SOURCES / 'acupuncture-com-manifest.json').read_text()) if (SOURCES / 'acupuncture-com-manifest.json').exists() else {}
    manifest |= {f'LU{i}': f'lung/lu{i}.htm' for i in range(1, 12)}
    checks = {}
    for p in POINTS:
        c = p['code']; page = SOURCES / f'acupuncture-com-{c.lower()}.html'
        text = page.read_text(errors='ignore') if page.exists() else ''
        text = ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'<script.*?</script>|<style.*?</style>', '', text, flags=re.S))).split())
        i = text.find('Location:'); location = text[i + 9:text.find('Classification', i) if text.find('Classification', i) > 0 else i + 400].strip() if i >= 0 else ''
        # The source sentence is matched but not stored (third-party wording stays in the git-ignored cache).
        row_ = {'anchor': p['at'], 'anchorAt': anchor_at.get(c), 'check': p['check'],
                'source': 'https://www.acupuncture.com/education/points/' + manifest[c] if c in manifest else None}
        if p['at'] is None: row_ |= {'status': 'noLandmark', 'missing': p['dir']}
        elif c in failures: row_ |= {'status': 'geometry', 'error': failures[c]}
        elif not location: row_['status'] = 'noSource'
        else:
            found = [bool(re.search(expand(k), normalize(location), re.I)) for k in p['check']]
            row_['status'] = 'agree' if all(found) else 'conflict'
            if not all(found): row_['unmatched'] = [k for k, f in zip(p['check'], found) if not f]
        checks[c] = row_
    agreed = {c for c, v in checks.items() if v['status'] == 'agree'}
    if os.environ.get('ACUPOINT_PREVIEW'):  # development view of every computed point, checked or not
        agreed = {p['code'] for p in points}
    kept = [p for p in points if p['code'] in agreed]
    concepts = [{k: p[k] for k in ('code', 'nameKo', 'hanja')} | {'location': p['ko'], 'channel': p['code'][:2]} for p in POINTS if p['code'] in agreed]
    channels = {}
    for k, v in CHANNELS.items():
        cs = [p['code'] for p in POINTS if p['code'][:2] == k and p['code'] in agreed]
        channels[k] = {kk: vv for kk, vv in v.items() if kk not in ('breaks',)} | {'codes': cs, 'breaks': [b for b in v.get('breaks', []) if b in cs]}
    OUT.write_text(json.dumps({'schemaVersion': 2, 'note': 'Educational acupoint positions on the Z-Anatomy model (rules + proportional cun); '
                               'not needling guidance. See atlas-data/anatomy/acupoint-checks.json.',
                               'channels': channels, 'concepts': concepts, 'points': kept}, ensure_ascii=False, indent=1) + '\n')
    CHECKS.write_text(json.dumps({'schemaVersion': 2, 'sources': {'draft': 'atlas-data/pipeline/acupoint_locations.py (AI-written, WHO 2008 conventions)',
        'acupunctureCom': 'www.acupuncture.com point pages, accessed 2026-11-10 (location sentence matched; not copied here or to the runtime)'},
        'normalization': [f'{a} -> {b}' for a, b in NORMALIZE],
        'points': checks}, ensure_ascii=False, indent=1) + '\n')
    sinews(points, surface, segment, visible, layer, geo, runtime)
    print('HEAD', {'cHead': round(float(u('cHead')), 4), 'cHeadX': round(float(u('cHeadX')), 4), 'arc': round(float(u('arc')[1][-1]), 3), 'vertex': round(float(u('vertexS')), 3)})
    print('ACUPOINTS', json.dumps({'concepts': len(concepts), 'instances': len(kept),
                                   'statuses': {s: sum(v['status'] == s for v in checks.values()) for s in ('agree', 'conflict', 'noSource', 'noLandmark', 'geometry')}}))


def sinews(points, surface, segment, visible, layer, geo, runtime):
    """Meridian sinews (sinew_channels.py): nodes checked against the Lingshu chapter and an English description,
    drawn on the body surface through the agreed nodes, with the muscles the line lies over on this model."""
    # Sources: Lingshu 經筋第十三 (Chinese Wikisource, 靈樞第四卷) and acupuncture-notes.com sinew channel pages.
    # 四庫全書 edition (unpunctuated); standard variant forms (異體字) mapped to the forms the draft uses.
    chapter = (SINEW_SOURCES / 'lingshu-siku-卷04.wiki').read_text()
    VARIANTS = [('于', '於'), ('斜', '邪'), ('隂', '陰'), ('内', '內'), ('㢘', '廉'), ('亷', '廉'), ('胷', '胸'), ('挟', '挾'),
                ('脇', '脅'), ('鋭', '銳'), ('顔', '顏'), ('别', '別'), ('齊', '臍'), ('並', '并'), ('眀', '明'), ('兎', '兔'),
                ('頬', '頰'), ('属', '屬'), ('乗', '乘'),
                # unencoded glyphs of this edition, where other editions read 脊 (挾脊, 屬脊, 循脊內) and 眥 (目外眥)
                ('{{SKchar|3394}}', '脊'), ('{{SKchar|3115}}', '眥')]
    for a, b in VARIANTS: chapter = chapter.replace(a, b)
    chapter = re.sub(r'[，。、；：○\s]', '', chapter)
    heads = [SINEWS[c]['head'] for c in SINEW_ORDER]
    starts = sorted((chapter.find(h), h) for h in heads if chapter.find(h) >= 0)
    paragraphs = [chapter[a:(starts[i + 1][0] if i + 1 < len(starts) else a + 400)] for i, (a, _) in enumerate(starts)]
    PAGES = {'LU': 'lung', 'LI': 'large_intestine', 'ST': 'stomach', 'SP': 'spleen', 'HT': 'heart', 'SI': 'small_intestine',
             'BL': 'bladder', 'KI': 'kidney', 'PC': 'pericardium', 'TE': 'triple_burner', 'GB': 'gallbladder', 'LR': 'liver'}
    def english(ch):
        text = (SINEW_SOURCES / f'acupuncture-notes-{PAGES[ch]}.html')
        text = text.read_text(errors='ignore') if text.exists() else (SINEW_SOURCES / f'acunotes-{PAGES[ch]}.html').read_text(errors='ignore')
        text = ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'<script.*?</script>|<style.*?</style>', '', text, flags=re.S))).split())
        i = text.find('Pathway'); j = text.find('Symptoms', i)
        return text[i + 7:j if j > i else i + 1500].strip()
    pos = {(p['code'], p['side']): p for p in points}
    other = {'right': 'left', 'left': 'right'}
    # Muscle lookup: every muscle vertex (thinned) with its structure key.
    mus_pts, mus_key = [], []
    for s in visible:
        if layer(s) == 'muscle':
            q = geo(s)[0][::2]; mus_pts.append(q); mus_key += [runtime[s['id']]['key']] * len(q)
    mus_pts = np.concatenate(mus_pts); mkd = KDTree(len(mus_pts))
    for i, q in enumerate(mus_pts): mkd.insert(Vector(q), i)
    mkd.balance()
    checks, out, paths, surface_of = {}, {}, [], []
    muscle_ids = {s['id'] for s in visible if layer(s) == 'muscle'}
    axis_z = float(np.mean([p['position'][2] for p in points if p['code'][:2] in ('GV', 'CV')]))   # body front-back middle
    for ch in SINEW_ORDER:
        s = SINEWS[ch]; para = next((x for x in paragraphs if x.startswith(s['head'])), '')
        en = english(ch); rows = []
        for si, strand in enumerate(s['strands']):
            for ni, (anchor, ko, lz, enp) in enumerate(strand):
                hit_l, hit_e = bool(para) and bool(re.search(lz, para)), bool(re.search(enp, en, re.I))
                code = anchor.lstrip('~')
                placed = any((code, side) in pos for side in ('right', 'left', 'midline'))
                status = 'agree' if hit_l and hit_e and placed else 'noPlace' if not placed else 'conflict'
                rows.append({'strand': si, 'node': ni, 'anchor': anchor, 'label': ko, 'lingshu': lz, 'english': enp, 'status': status,
                             **({'unmatched': [n for n, ok in (('lingshu', hit_l), ('english', hit_e)) if not ok]} if status == 'conflict' else {})})
        # Lingshu (public domain) paragraph kept for review; the English page is matched but not quoted.
        checks[ch] = {'lingshu': para[:400], 'englishSource': f'https://acupuncture-notes.com/{PAGES[ch]}_sinew_channel', 'nodes': rows}
        ok = {(r['strand'], r['node']) for r in rows if r['status'] == 'agree'}
        strands = []
        for si, strand in enumerate(s['strands']):
            nodes = [(ni, n) for ni, n in enumerate(strand) if (si, ni) in ok]
            if nodes: strands.append([{'label': n[1], 'anchor': n[0]} for _, n in nodes])
            for side in ('right', 'left'):
                at = []
                for _, (anchor, ko, _, _) in nodes:
                    code = anchor.lstrip('~'); sd = other[side] if anchor.startswith('~') else side
                    p = pos.get((code, sd)) or pos.get((code, 'midline'))
                    at.append(p)
                if len(at) < 2: continue
                line, segs, on = [], [], []
                for a, b in zip(at, at[1:]):
                    A, B = np.array(a['position']), np.array(b['position']); nA, nB = np.array(a['normal']), np.array(b['normal'])
                    k = max(1, int(np.linalg.norm(B - A) / SINEW_STEP))
                    for i in range(k):
                        t = i / k; q = A + (B - A) * t; d = nA * (1 - t) + nB * t
                        d = d / (np.linalg.norm(d) or 1)
                        owner = None
                        if i:
                            # Outer surface near the straight line: blended direction first, then each node's direction,
                            # then horizontally outward from the body axis; the closest hit within 8 cm wins.
                            radial = np.array([q[0], 0, q[2] - axis_z]); radial = radial / (np.linalg.norm(radial) or 1)
                            best = None
                            for dd in (d, nA, nB, radial):
                                h, o = surface.outer(q, dd)
                                if h is None: continue
                                dist = np.linalg.norm(np.asarray(h) - q)
                                if dist < .08 and (best is None or dist < best[0]): best = (dist, h, o)
                            if best: q, owner = np.asarray(best[1]), best[2]
                        line.append(q); segs.append(segment(q)); on.append(owner)
                line.append(B); segs.append(b['segment']); on.append(None)
                surface_of.append(on)
                paths.append({'sinew': ch, 'side': side, 'strand': len(strands) - 1, 'points': [[round(float(v), 5) for v in q] for q in line],
                              'segments': segs, 'nodes': [{'anchor': n[0], 'position': p['position'], 'segment': p['segment']} for (_, n), p in zip(nodes, at)]})
        # Muscles the drawn line lies on: the nearest muscle under each sample, in order along the course, per side.
        muscles = {}
        for side in ('right', 'left'):
            counts, first = {}, {}
            for i, (path, on) in enumerate((x, o) for x, o in zip(paths, surface_of) if x['sinew'] == ch and x['side'] == side):
                for j, (q, owner) in enumerate(zip(path['points'], on)):
                    if owner in muscle_ids: key = runtime[owner]['key']        # the muscle the line lies on
                    else:                                                    # fascia, tendon or bone on top: nearest muscle
                        _, idx, dist = mkd.find(Vector(q))
                        if dist > SINEW_NEAR: continue
                        key = mus_key[idx]
                    counts[key] = counts.get(key, 0) + 1; first.setdefault(key, (i, j))
            muscles[side] = sorted((k for k, n in counts.items() if n >= 2), key=lambda k: first[k])
        out[ch] = {'nameKo': s['nameKo'], 'hanja': s['hanja'], 'strands': strands, 'internal': s['internal'], 'muscles': muscles}
    SINEW_OUT.write_text(json.dumps({'schemaVersion': 1, 'note': 'Meridian sinews (經筋) drawn on the Z-Anatomy model through binding regions '
                                     'from Lingshu ch. 13; educational course and nearby muscles only. See atlas-data/anatomy/sinew-checks.json.',
                                     'order': SINEW_ORDER, 'sinews': out, 'paths': paths}, ensure_ascii=False, separators=(',', ':')) + '\n')
    SINEW_CHECKS.write_text(json.dumps({'schemaVersion': 1, 'sources': {
        'draft': 'atlas-data/pipeline/sinew_channels.py (AI-written from Lingshu ch. 13)',
        'lingshu': 'zh.wikisource.org 靈樞經 (四庫全書本)/卷04 經筋第十三, accessed 2026-11-13',
        'english': 'acupuncture-notes.com <channel>_sinew_channel pages (Pathway section matched, not quoted), accessed 2026-11-13'},
        'variants': [f'{a} -> {b}' for a, b in VARIANTS], 'sinews': checks}, ensure_ascii=False, indent=1) + '\n')
    st = [r['status'] for c in checks.values() for r in c['nodes']]
    print('SINEWS', json.dumps({'nodes': len(st), **{k: st.count(k) for k in ('agree', 'conflict', 'noPlace')}, 'paths': len(paths),
                                'muscles': {k: len(v['muscles']['right']) for k, v in out.items()}}))


main()
