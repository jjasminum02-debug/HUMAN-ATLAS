#!/usr/bin/env python3
"""Stage only a local BodyParts3D test page and its viewer dependencies in /private/tmp."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[3]
THREE = ROOT / "atlas-web/node_modules/three"
ASSET = ROOT / "atlas-data/assets/derived-glb/bodyparts3d-r4-right-lower-leg/right-lower-leg.glb"
HTML = ROOT / "work/evidence/T50/private-spike-preview.html"
OUT = ROOT / "work/evidence/T50/private-preview-stage.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    destination = Path(tempfile.mkdtemp(prefix="t50-private-spike-", dir="/private/tmp"))
    (destination / "three/examples").mkdir(parents=True)
    (destination / "scene").mkdir()
    shutil.copy2(HTML, destination / "index.html")
    for name in ("three.module.js", "three.core.js"):
        shutil.copy2(THREE / "build" / name, destination / "three" / name)
    shutil.copytree(THREE / "examples/jsm", destination / "three/examples", dirs_exist_ok=True)
    shutil.copy2(ASSET, destination / "scene/right-lower-leg.glb")
    record = {
        "task": "T50",
        "createdOn": datetime.now(timezone.utc).isoformat(),
        "privateTempDirectory": "<ephemeral /private/tmp preview; removed after QA>",
        "bindHost": "127.0.0.1",
        "learnerProduct": False,
        "files": [
            {"path": "index.html", "bytes": (destination / "index.html").stat().st_size, "sha256": digest(destination / "index.html")},
            {"path": "three/three.module.js", "bytes": (destination / "three/three.module.js").stat().st_size, "sha256": digest(destination / "three/three.module.js")},
            {"path": "three/three.core.js", "bytes": (destination / "three/three.core.js").stat().st_size, "sha256": digest(destination / "three/three.core.js")},
            {"path": "scene/right-lower-leg.glb", "bytes": (destination / "scene/right-lower-leg.glb").stat().st_size, "sha256": digest(destination / "scene/right-lower-leg.glb")},
        ],
        "threeExamplesModuleTreeCopied": True,
        "notes": [
            "No repository-wide server; only this preview, Three.js local runtime modules, and one existing derived GLB are staged.",
            "All geometry edits happen in browser memory and are restored before exit; original OBJ/GLB files are read-only inputs.",
            "The temp directory is disposable QA material and is not a product asset or evidence payload."
        ]
    }
    OUT.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(destination)
    print(json.dumps(record, ensure_ascii=False, indent=2))
    print(f"Serve with: python3 -m http.server 8765 --bind 127.0.0.1 --directory '{destination}'")


if __name__ == "__main__":
    main()
