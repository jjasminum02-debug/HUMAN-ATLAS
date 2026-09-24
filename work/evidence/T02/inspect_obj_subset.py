#!/usr/bin/env python3
"""Inspect extracted BodyParts3D pilot OBJ headers, geometry bounds, and hashes."""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

ROOT = Path("HUMAN ATLAS/atlas-data/assets/bodyparts3d-v4-pilot")
OUT = Path("HUMAN ATLAS/work/evidence/T02/geometry-inspection.json")
EXPECTED = {
    "FJ1394.obj": ("BP5541", "FMA45960", "Lateral head of right gastrocnemius", "muscle"),
    "FJ1397.obj": ("BP5539", "FMA45957", "Medial head of right gastrocnemius", "muscle"),
    "FJ1409.obj": ("BP5015", "FMA22554", "Right fibularis brevis", "muscle"),
    "FJ1410.obj": ("BP5013", "FMA22552", "Right fibularis longus", "muscle"),
    "FJ1437.obj": ("BP4999", "FMA22558", "Right soleus", "muscle"),
    "FJ1439.obj": ("BP5018", "FMA22544", "Right tibialis anterior", "muscle"),
    "FJ1440.obj": ("BP5004", "FMA65018", "Right tibialis posterior", "muscle"),
    "FJ3360.obj": ("BP9040", "FMA24497", "Right calcaneus", "bone"),
    "FJ3366.obj": ("BP8009", "FMA24480", "Right fibula", "bone"),
    "FJ3385.obj": ("BP8033", "FMA24482", "Right talus", "bone"),
    "FJ3387.obj": ("BP8031", "FMA24477", "Right tibia", "bone"),
}
PATTERNS = {
    "file_id": r"^# File ID\s*:\s*(.+)$",
    "representation_id": r"^# Representation ID\s*:\s*(.+)$",
    "concept_id": r"^# Concept ID\s*:\s*(.+)$",
    "english_name": r"^# English name\s*:\s*(.+)$",
    "build_up_logic": r"^# Build-up logic\s*:\s*(.+)$",
    "bounds_mm": r"^# Bounds\(mm\)\s*:\s*(.+)$",
    "volume_cm3": r"^# Volume\(cm3\)\s*:\s*(.+)$",
}


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def inspect(path: Path) -> dict:
    meta={}
    lo=[float("inf")]*3; hi=[float("-inf")]*3
    vertex_count=face_count=0
    license_lines=[]
    with path.open(encoding="ascii",errors="replace") as f:
        for line in f:
            for key,pattern in PATTERNS.items():
                m=re.match(pattern,line.rstrip())
                if m: meta[key]=m.group(1)
            if line.startswith("# The license") or line.startswith("# http://dbarchive"):
                license_lines.append(line[2:].strip())
            if line.startswith("v "):
                parts=line.split()
                if len(parts)>=4:
                    xyz=tuple(float(x) for x in parts[1:4]); vertex_count+=1
                    for i,x in enumerate(xyz):lo[i]=min(lo[i],x);hi[i]=max(hi[i],x)
            elif line.startswith("f "):
                face_count+=1
    source_bounds={"min_mm":lo,"max_mm":hi}
    atlas_bounds={"min_m":[lo[0]/1000,lo[2]/1000,-hi[1]/1000],"max_m":[hi[0]/1000,hi[2]/1000,-lo[1]/1000]}
    expected=EXPECTED[path.name]
    if meta.get("file_id") != path.stem: raise ValueError(f"File ID/header mismatch: {path}")
    if meta.get("concept_id") != expected[1]: raise ValueError(f"Concept ID mismatch: {path}")
    if meta.get("english_name") != expected[2]: raise ValueError(f"English name mismatch: {path}: {meta.get('english_name')!r}")
    if meta.get("representation_id") != expected[0]: raise ValueError(f"Representation ID mismatch: {path}")
    if expected[3] == "muscle" and hi[0] >= 0: raise ValueError(f"right muscle crosses/enters non-right X half-space: {path.name}")
    if expected[3] == "bone" and hi[0] >= 0: raise ValueError(f"right bone crosses/enters non-right X half-space: {path.name}")
    return {
        "file":str(path), "kind":expected[3], "sha256":sha256(path), "bytes":path.stat().st_size,
        **meta, "vertex_count":vertex_count,"polygon_count":face_count,
        "measured_source_bounds_mm":source_bounds,"derived_atlas_bounds_m":atlas_bounds,
        "right_side_coordinate_check":"pass_source_x_max_lt_0" if hi[0] < 0 else "fail",
        "embedded_license_header":license_lines,
    }


def main() -> None:
    paths=sorted(ROOT.glob("FJ*.obj"))
    if {p.name for p in paths} != set(EXPECTED):
        raise ValueError(f"Expected exactly {len(EXPECTED)} selected OBJ files, found {[p.name for p in paths]}")
    assets=[inspect(p) for p in paths]
    result={
        "task":"T02", "source_dataset":"BodyParts3D Release 4.0; IS-A tree; OBJ reduction rate 99%",
        "inspection_method":"header parsing, raw vertex/face counts, SHA-256, and geometry-bound sign checks; no remeshing or in-place edits",
        "assets":assets,
        "summary":{"asset_count":len(assets),"all_vertices_strictly_in_right_half_space":all(a["right_side_coordinate_check"].startswith("pass") for a in assets),"total_bytes":sum(a["bytes"] for a in assets),"total_vertices":sum(a["vertex_count"] for a in assets),"total_polygons":sum(a["polygon_count"] for a in assets)},
    }
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result["summary"],ensure_ascii=False,indent=2))

if __name__=="__main__": main()
