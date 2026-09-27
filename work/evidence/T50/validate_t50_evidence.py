#!/usr/bin/env python3
"""Read-only checks for T50 source/sample evidence and scope invariants."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "work/evidence/T50"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    decision = json.loads((EVIDENCE / "source-and-asset-decision.json").read_text())
    samples = json.loads((EVIDENCE / "asset-sample-inspection.json").read_text())
    browser = json.loads((EVIDENCE / "browser-qa.json").read_text())
    preservation = json.loads((EVIDENCE / "preservation-after.json").read_text())
    registry = json.loads((ROOT / "work/task-registry-r15.json").read_text())
    status_text = (ROOT / "work/STATUS.md").read_text()
    expected = {
        "atlas-data/assets/derived-glb/bodyparts3d-r4-right-lower-leg/right-lower-leg.glb": "044450c3230bd23869a099d545151cb3d7518da3240a6e59f911f82786edc341",
        "atlas-data/assets/derived-glb/bodyparts3d-r4-t13-right-bones/right-bones.glb": "a5b16cf1e6991b52f66706dee7cf3c77d9832b1a3bde0e3dffd5de5619db6662",
        "atlas-data/assets/derived-glb/opensim-gait2392-t44-right-ankle/right-ankle-rest.glb": "a33f043be46c7b628bc649777e190c9e7d7cba345f07795e080820545261bed0",
        "atlas-data/assets/motion/t24-right-tibialis-anterior/ankle-dorsiflexion.glb": "956bb0e3664f325157e116a539aa9d8ea6db7c812dcc963d34d73fef1473596a",
        "atlas-data/assets/bodyparts3d-v4-pilot/FJ1439.obj": "b03d2f54644969d153d3dfe4025ee629858e72c1e5ee3b0e7d5f16f54dc505b3",
        "atlas-data/assets/bodyparts3d-v4-pilot/FJ3387.obj": "01879d7310938e82eecc02e1115332497e94085ff5cc1fa8eeee47ad1f5d3578",
        "atlas-data/assets/bodyparts3d-v4-pilot/FJ3366.obj": "d03fee02cf8eefad1ecfcb9246e3f43ad3c4615c21ce08dc5e2b6901c6395a86",
        "atlas-data/assets/bodyparts3d-v4-pilot/FJ3385.obj": "8b35f0132c1a05b64f26746fdd0496a2495280cd0c2ac90dbf637fd74f79f54f",
        "atlas-data/assets/bodyparts3d-v4-pilot/FJ3360.obj": "b53e7970e822e997e1b05f94f42514d07a3f98edcc63ec7dd7219354ce1d8176",
    }
    checks = {}
    for rel, expected_hash in expected.items():
        checks[f"hash:{rel}"] = sha256(ROOT / rel) == expected_hash
    glbs = {row["file"]: row for row in samples["glbSamples"]}
    body = glbs["atlas-data/assets/derived-glb/bodyparts3d-r4-right-lower-leg/right-lower-leg.glb"]
    opensim = glbs["atlas-data/assets/motion/t24-right-tibialis-anterior/ankle-dorsiflexion.glb"]
    checks["BodyParts3D has 11 distinct mesh nodes"] = body["nodeCount"] == body["meshCount"] == 11
    checks["BodyParts3D GLB has no skin/animation/external URI"] = body["skinCount"] == body["animationCount"] == 0 and body["externalUris"] == []
    checks["BodyParts3D GLB primitives have no morph target"] = all(primitive["morphTargetCount"] == 0 for node in body["nodes"] for primitive in node["primitives"])
    checks["T24 morph belongs to 3-point line path"] = any(node.get("name") == "tib_ant_r_model_path_q0" and any(p["mode"] == 1 and p["vertexCount"] == 3 and p["morphTargetCount"] == 2 for p in node["primitives"]) for node in opensim["nodes"])
    checks["BodyParts3D provisional decision states unstandardized pose"] = "standardized articulated neutral/anatomical pose" in decision["decision"]["notSelectedFor"]
    checks["license and preserved legacy header caveat are explicit"] = "CC BY 4.0" in decision["rights"]["officialCurrentArchiveTerms"] and "CC BY-SA 2.1 Japan" in decision["rights"]["observedLegacyObjComments"]
    checks["no full archive acquisition"] = decision["assetProperties"]["lod"]["downloaded"] is False
    checks["T24 remains a separate reference model"] = "not the single body-surface source" in decision["comparison"]["OpenSim Gait2392 (T24/T44)"]["decision"]
    checks["browser used one real mesh renderer and root"] = browser["page"]["canvasCount"] == browser["page"]["anatomySceneRootCount"] == 1
    checks["browser localized mesh change was not whole-muscle scale"] = browser["operations"][1]["localizedSubset"] and not browser["operations"][1]["uniformWholeMuscleScaling"]
    checks["browser synthetic bone transform stayed anatomically unclaimed"] = browser["operations"][2]["matrixChanged"] and not browser["operations"][2]["pivotIsAnatomicalJointCenter"] and not browser["operations"][2]["anatomicalMotion"]
    checks["browser restored geometry pose camera and same scene"] = browser["operations"][3]["passed"] and browser["operations"][3]["secondViewportCreated"] is False
    checks["browser console clean"] = browser["console"] == {"errors": 0, "warnings": 0}
    checks["pre-existing inputs and OpenSim preserved"] = preservation["passed"] is True and preservation["openSimModels"]["sameAsStart"] is True
    checks["R15 task status and next item updated"] = registry["taskStatuses"]["T50"] == "passed_with_gaps" and registry["nextTask"] == "T51" and registry["activeQueue"][:2] == ["T50", "T51"]
    checks["STATUS records T51 as next and preserves T24 blocked"] = "NEXT_TASK: T51 / Sol High" in status_text and "T24의 원래 앞정강근 surface CTA는 여전히 `blocked`" in status_text
    record = {"task": "T50", "checks": checks, "passed": all(checks.values())}
    output = EVIDENCE / "validation-results.json"
    output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(record, ensure_ascii=False, indent=2))
    if not record["passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
