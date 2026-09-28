#!/usr/bin/env python3
"""Render T97 source-extracted OBJ triangle surfaces to PNG using stdlib only.

This is an orthographic flat-shaded depth-buffer preview from saved object
matrix coordinates. It is an inspection aid, not a scene import/approval.
No Blender source file, script, driver, modifier or animation is executed.
"""

import hashlib
import json
import math
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "work/evidence/T97"
OBJ_DIR = ROOT / "atlas-data/source-cache/z-anatomy/t97/latissimus-obj"
WIDTH = HEIGHT = 720
ORTHO_SCALE = 0.56
TARGET = (0.0, 0.07, 1.14)
BACKGROUND = (20, 25, 32)
BASE = (105, 156, 188)


def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def dot(a, b): return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def norm(v):
    m = math.sqrt(dot(v, v))
    return tuple(x / m for x in v) if m else (0.0, 0.0, 0.0)


def read_obj(path):
    vertices, faces = [], []
    for line in path.read_text(encoding="ascii").splitlines():
        if line.startswith("v "):
            vertices.append(tuple(float(x) for x in line.split()[1:4]))
        elif line.startswith("f "):
            faces.append(tuple(int(x.split("/")[0]) - 1 for x in line.split()[1:4]))
    if not vertices or not faces:
        raise ValueError(f"empty target surface {path}")
    if any(i < 0 or i >= len(vertices) for face in faces for i in face):
        raise ValueError(f"out-of-range mesh index {path}")
    return vertices, faces


def png_chunk(kind, data):
    body = kind + data
    return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xffffffff)


def write_png(path, rgb):
    scanlines = b"".join(b"\0" + bytes(rgb[y*WIDTH*3:(y+1)*WIDTH*3]) for y in range(HEIGHT))
    data = b"\x89PNG\r\n\x1a\n"
    data += png_chunk(b"IHDR", struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0))
    data += png_chunk(b"IDAT", zlib.compress(scanlines, 8))
    data += png_chunk(b"IEND", b"")
    path.write_bytes(data)


def render(view_name, camera_position, objs):
    forward = norm(sub(TARGET, camera_position))
    right = norm(cross(forward, (0.0, 0.0, 1.0)))
    up = norm(cross(right, forward))
    light = norm((0.35, -0.45, 0.82))
    zbuf = [float("inf")] * (WIDTH * HEIGHT)
    pixels = bytearray(BACKGROUND * (WIDTH * HEIGHT))
    triangle_count = 0
    visible_samples = 0

    def project(p):
        rel = sub(p, TARGET)
        sx = (dot(rel, right) / ORTHO_SCALE + 0.5) * (WIDTH - 1)
        sy = (0.5 - dot(rel, up) / ORTHO_SCALE) * (HEIGHT - 1)
        depth = dot(sub(p, camera_position), forward)
        return sx, sy, depth

    for obj_name, vertices, faces, source_hash in objs:
        projected = [project(v) for v in vertices]
        for face in faces:
            tri = [projected[i] for i in face]
            (x0,y0,z0),(x1,y1,z1),(x2,y2,z2) = tri
            area = (x1-x0)*(y2-y0) - (y1-y0)*(x2-x0)
            if abs(area) < 1e-8:
                continue
            xmin = max(0, int(math.floor(min(x0,x1,x2))))
            xmax = min(WIDTH-1, int(math.ceil(max(x0,x1,x2))))
            ymin = max(0, int(math.floor(min(y0,y1,y2))))
            ymax = min(HEIGHT-1, int(math.ceil(max(y0,y1,y2))))
            if xmin > xmax or ymin > ymax:
                continue
            p0, p1, p2 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
            normal = norm(cross(sub(p1,p0), sub(p2,p0)))
            diffuse = max(0.0, dot(normal, light))
            # Preserve visible shape if the source polygon winding is reversed.
            diffuse = max(diffuse, 0.55 * abs(dot(normal, light)))
            shade = 0.34 + 0.66 * diffuse
            color = tuple(min(255, max(0, int(c * shade))) for c in BASE)
            inv_area = 1.0 / area
            triangle_count += 1
            for py in range(ymin, ymax+1):
                cy = py + 0.5
                for px in range(xmin, xmax+1):
                    cx = px + 0.5
                    w0 = ((x1-cx)*(y2-cy) - (y1-cy)*(x2-cx)) * inv_area
                    w1 = ((x2-cx)*(y0-cy) - (y2-cy)*(x0-cx)) * inv_area
                    w2 = 1.0 - w0 - w1
                    if w0 < -1e-7 or w1 < -1e-7 or w2 < -1e-7:
                        continue
                    depth = w0*z0 + w1*z1 + w2*z2
                    index = py * WIDTH + px
                    if depth < zbuf[index]:
                        zbuf[index] = depth
                        off = index * 3
                        pixels[off:off+3] = bytes(color)
                        visible_samples += 1
    output = EVIDENCE / f"surface-{view_name}.png"
    write_png(output, pixels)
    return {"file": output.name, "sha256": sha256_file(output), "trianglesSubmitted": triangle_count, "depthBufferWrites": visible_samples, "cameraPosition": camera_position, "target": TARGET, "orthographicScale": ORTHO_SCALE}


def main():
    objs = []
    for path in sorted(OBJ_DIR.glob("Latissimus_dorsi_muscle.*.obj")):
        vertices, faces = read_obj(path)
        objs.append((path.stem, vertices, faces, sha256_file(path)))
    if len(objs) != 6:
        raise SystemExit(f"expected six source-derived object meshes, found {len(objs)}")
    # These are source-coordinate directions only. T97 does not establish the
    # anatomical orientation of the archive's world Y/X axes.
    views = {
        "y-minus": (0.0, -2.7, 1.15),
        "y-plus": (0.0, 2.7, 1.15),
        "x-plus": (2.7, 0.07, 1.15),
    }
    renders = {name: render(name, pos, objs) for name, pos in views.items()}
    result = {
        "task": "T97",
        "renderer": "T97 stdlib flat-shaded triangle rasterizer with orthographic projection and per-pixel depth buffer",
        "source": "raw MVert/MLoop/MPoly arrays read from pinned Startup.blend by parse_blend_datablocks.py; transformed only by saved Object obmat",
        "sourceScriptsOrDriversExecuted": False,
        "sourceBlenderFileOpened": False,
        "blenderAutoexecSettingForFailedAttempts": "--disable-autoexec",
        "inputObjects": [{"name": name, "vertexCount": len(v), "triangleCount": len(f), "objSha256": h} for name,v,f,h in objs],
        "renders": renders,
    }
    out = EVIDENCE / "surface-preview.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(out), "renders": renders}, indent=2))


if __name__ == "__main__":
    main()
