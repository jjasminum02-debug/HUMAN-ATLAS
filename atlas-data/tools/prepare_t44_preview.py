#!/usr/bin/env python3
"""Stage only T44 preview assets in a fresh temp folder for localhost render QA."""
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[2]
THREE = ROOT / "atlas-web/node_modules/three"
ASSET = ROOT / "atlas-data/assets/derived-glb/opensim-gait2392-t44-right-ankle/right-ankle-rest.glb"
HTML = ROOT / "work/evidence/T44/rest-preview.html"


def main():
    dest = Path(tempfile.mkdtemp(prefix="t44-rest-preview-", dir="/private/tmp"))
    (dest / "three/examples").mkdir(parents=True)
    (dest / "scene").mkdir()
    shutil.copy2(HTML, dest / "index.html")
    for name in ("three.module.js", "three.core.js"):
        shutil.copy2(THREE / "build" / name, dest / "three" / name)
    shutil.copytree(THREE / "examples/jsm", dest / "three/examples", dirs_exist_ok=True)
    shutil.copy2(ASSET, dest / "scene/right-ankle-rest.glb")
    print(dest)
    print(f"Serve with: python3 -m http.server 8764 --bind 127.0.0.1 --directory '{dest}'")


if __name__ == "__main__":
    main()
