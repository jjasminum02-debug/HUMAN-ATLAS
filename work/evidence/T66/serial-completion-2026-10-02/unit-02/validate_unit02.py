#!/usr/bin/env python3
"""Validate the T66 unit-02 registration, source-bound GLBs, and saved browser evidence."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
EVIDENCE = ROOT / "work/evidence/T66/serial-completion-2026-10-02/unit-02"


def load(relative: str):
    return json.loads((ROOT / relative).read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


registration = load("work/evidence/T66/serial-completion-2026-10-02/unit-02/registration.json")
unit_queue = load("work/evidence/T66/serial-completion-2026-10-02/unit-02/serial-queue.json")
scene_catalog = load("atlas-data/motion/motion-scenes.json")
asset_sources = load("atlas-data/motion/motion-asset-sources.json")
learning = load("atlas-data/motion/motion-learning.json")
authoring = load("atlas-data/motion/authoring/registry.json")
interpolation = load("work/evidence/T66/serial-completion-2026-10-02/unit-02/candidate-interpolation-r1.json")
browser = load("work/evidence/T66/serial-completion-2026-10-02/unit-02/browser/browser-checks.json")
baseline = load("work/evidence/T66/serial-completion-2026-10-02/unit-02/start-baseline.json")

expected_families = {
    "hip-flexion-left", "hip-flexion-right", "knee-flexion-left", "knee-flexion-right"
}
need(set(registration["families"]) == expected_families, "family set differs from the frozen unit scope")
rows = registration["registeredRows"]
need(len(rows) == 178, f"expected 178 selected subject rows, got {len(rows)}")
need(len(unit_queue["responsibilityKeys"]) == 178, "unit responsibility queue is incomplete")
need(unit_queue["counts"]["registeredSelectors"] == 178, "queue selector count mismatch")
need(len({(x["key"]["family"], x["key"]["side"], x["key"]["action"], x["key"]["sourceKey"]) for x in unit_queue["responsibilityKeys"]}) == 178,
     "duplicate family/side/action/sourceKey responsibility")
need(Counter(x["subjectKind"] for x in rows) == Counter({"bone": 128, "muscle": 50}), "selector kind counts changed")
need(Counter(x["role"] for x in rows) == Counter({"moving_structure": 122, "fixed_structure": 6, "deforming_passive_surface": 50}),
     "selector role counts changed")
need(all(x["implementationStatus"] == "implemented_verified" for x in unit_queue["responsibilityKeys"]), "unverified unit work key")
need(unit_queue["authority"] == {
    "sourceOnly": True, "localTechnicalOnly": True, "publicRedistribution": "held", "humanReview": "not_performed", "canonicalBindingAdded": False
}, "source-only/rights/review authority changed")

manifest_sha = sha(ROOT / "atlas-data/source-cache/datasets/za/compiled/manifest.json")
overlay_sha = sha(ROOT / "atlas-data/overlays/za-local-integration.json")
need(manifest_sha == registration["sourceManifestSha256"], "pinned compiled source manifest changed")
need(overlay_sha == registration["sourceOverlaySha256"], "pinned local source overlay changed")

actions = {x["id"]: x for x in learning["muscleActions"]}
definitions = {x["id"]: x for x in learning["motionDefinitions"]}
assets = {x["id"]: x for x in learning["motionAssets"]}
need(sum(x["id"].startswith("T66-U02-") for x in learning["muscleActions"]) == 178, "unit actions are not fully in learner data")
need(sum(x["id"].startswith("T66-U02-") for x in learning["motionDefinitions"]) == 178, "unit definitions are not fully in learner data")
need(sum(x["id"].startswith("T66-U02-") for x in learning["motionAssets"]) == 178, "unit assets are not fully in learner data")
need(sum(x.startswith("T66-U02-") for x in asset_sources["productionMotionAssetIds"]) == 178, "asset source policy list is incomplete")
need(sum(x["id"].startswith("T66-U02-") for x in authoring["records"]) == 4, "authoring registry does not contain exactly four unit packages")
scene_ids = {x["id"] for x in scene_catalog["sceneManifests"]}
need({f"T66-U02-{x}-REFERENCE" for x in registration["families"]} <= scene_ids, "unit scenes missing from shared scene catalog")

package_hashes: dict[str, dict] = {}
for family in sorted(expected_families):
    family_rows = [r for r in rows if r["familyId"] == family]
    need(family_rows, f"no registered rows for {family}")
    uri = family_rows[0]["motionUri"]
    digest = family_rows[0]["motionSha256"]
    motion_path = ROOT / uri
    need(motion_path.exists() and sha(motion_path) == digest, f"motion GLB hash mismatch: {family}")
    derived_path = ROOT / "atlas-data/assets/derived-glb" / f"t66-unit02-{family}" / "reference.glb"
    need(derived_path.exists(), f"derived scene GLB missing: {family}")
    scene_id = family_rows[0]["sceneId"]
    scene = next((x for x in scene_catalog["sceneManifests"] if x["id"] == scene_id), None)
    need(scene is not None and scene["assetUri"] == f"atlas-data/assets/derived-glb/t66-unit02-{family}/reference.glb", f"scene URI mismatch: {family}")
    package_hashes[family] = {
        "motionUri": uri, "motionBytes": motion_path.stat().st_size, "motionSha256": digest,
        "derivedUri": str(derived_path.relative_to(ROOT)), "derivedBytes": derived_path.stat().st_size, "derivedSha256": sha(derived_path),
        "selectorRows": len(family_rows),
    }
    for row in family_rows:
        action_id = row["assetId"].removesuffix("-ASSET") + "-ACTION"
        action = actions.get(action_id)
        need(action is not None and action["sourceSubjectKeys"] == [row["sourceKey"]], f"action/source key mismatch: {action_id}")
        need(action["subjectIds"] == [] and action["targetJointIds"] == [], f"canonical learner binding added: {action_id}")
        definition_id = action_id.removesuffix("-ACTION") + "-MOTION"
        definition = definitions.get(definition_id)
        need(definition is not None and definition["side"] == row["side"], f"definition side mismatch: {definition_id}")
        asset_id = action_id.removesuffix("-ACTION") + "-ASSET"
        asset = assets.get(asset_id)
        need(asset is not None and asset["sha256"] == digest, f"motion asset hash mismatch: {asset_id}")
        need(asset["staticBinding"]["side"] == row["side"], f"static binding side mismatch: {asset_id}")
        need(row["localTechnicalOnly"] is True and row["publicRedistribution"] == "held" and row["humanReview"] == "not_performed",
             f"review/rights policy changed: {asset_id}")
        need(row["role"] in {"moving_structure", "fixed_structure", "deforming_passive_surface"}, f"unexpected role: {asset_id}")

need(interpolation["passed"] is True and interpolation["continuousCollisionFreedomClaimed"] is False, "interpolation/contact result invalid")
need(len(interpolation["rows"]) == 50 and all(x["passed"] for x in interpolation["rows"]), "not all passive surfaces passed sampled interpolation")
need(all(x["contact"]["newContainmentMaximum"] == 0 for x in interpolation["rows"]), "new containment found")
need(all(x["geometry"]["flippedFaceSamples"] == 0 for x in interpolation["rows"]), "face flip found")
minimum_area = min(x["geometry"]["minimumAreaRatio"] for x in interpolation["rows"])

need(browser["pass"] is True and len(browser["checks"]) == 9, "real browser QA did not pass its nine scenarios")
need(not browser["consoleErrors"] and not browser["pageErrors"], "browser console/page error")
need(browser["overflow"]["scrollWidth"] <= browser["overflow"]["viewport"], "mobile horizontal overflow")
need(all(x["status"] == 200 and x.get("sha256") for x in browser["motionResponses"]), "motion GLB HTTP/hash response failure")
need({x["side"] for x in browser["checks"] if x["kind"] in {"muscle", "bone-fixed", "bone-moving"}} == {"왼쪽", "오른쪽"}, "bilateral UI evidence missing")

protected_owned_prefixes = (
    "work/evidence/T66/serial-completion-2026-10-02/unit-02/",
    "atlas-data/assets/motion/t66-unit02-",
    "atlas-data/assets/derived-glb/t66-unit02-",
    "atlas-data/motion/authoring/t66-unit02-",
)
owned_exact = {
    "atlas-data/motion/motion-learning.json", "atlas-data/motion/authoring/registry.json",
    "atlas-data/motion/motion-scenes.json", "atlas-data/motion/motion-asset-sources.json",
    "atlas-data/schemas/validate_motion_learning.py", "atlas-web/src/data/learnerMotionRuntime.generated.ts",
    # sync_execution.py rewrites these derived projections after the T66 record update.
    "work/NEXT.md", "design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md",
    "work/task-registry-r15.json",
    "atlas-web/src/domain/motionLearning.ts", "atlas-web/src/domain/motionLearning.test.ts",
    "atlas-web/src/domain/motionSubjectPresentation.ts", "atlas-web/src/domain/motionSubjectPresentation.test.ts",
    "atlas-web/src/ui/App.tsx", "atlas-web/src/ui/MotionLearningPanel.tsx",
    "atlas-web/src/viewer/animationSceneAdapter.ts", "atlas-web/src/viewer/datasets/DatasetSceneAdapter.ts",
    "atlas-web/src/viewer/unit02HipKneeMotion.test.ts", "work/EXECUTION.json", "work/reports/T66.md",
    "work/tasks/T66-APP-COMPLETION.md", "work/STATUS.md",
}
protected_checked = 0
for item in baseline["dirtyPaths"]:
    rel = item["path"]
    if item.get("kind") != "file" or not item.get("sha256") or rel in owned_exact or rel.startswith(protected_owned_prefixes):
        continue
    path = ROOT / rel
    need(path.exists() and sha(path) == item["sha256"], f"preexisting WIP changed: {rel}")
    protected_checked += 1

result = {
    "schemaVersion": "t66-unit02-validation-v1",
    "status": "implemented_verified",
    "taskStatus": "in_progress_partial",
    "families": sorted(expected_families),
    "counts": {
        "registeredSelectorRows": len(rows), "muscleSelectorRows": 50, "boneSelectorRows": 128,
        "uniqueAddedMuscleSourceKeys": len(registration["uniqueAddedMuscleSourceKeys"]),
        "uniqueAddedBoneSourceKeys": len(registration["uniqueAddedBoneSourceKeys"]),
        "interpolationSurfaceRowsPassed": len(interpolation["rows"]),
        "browserScenariosPassed": len(browser["checks"]),
        "protectedPreexistingFilesHashChecked": protected_checked,
    },
    "geometry": {
        "sampledTriangleFlips": 0, "sampledNewContainment": 0,
        "minimumSampledAreaRatio": minimum_area,
        "interpolationSubdivisionsPerAuthoredSegment": interpolation["subdivisionsPerSegment"],
        "continuousCollisionFreedomClaimed": False,
        "authoredTrajectoryIsMeasuredNormalAxis": False,
    },
    "packages": package_hashes,
    "browserEvidence": {
        "path": "work/evidence/T66/serial-completion-2026-10-02/unit-02/browser/browser-checks.json",
        "browser": browser["browser"], "viewports": browser["viewports"],
        "consoleErrors": len(browser["consoleErrors"]), "pageErrors": len(browser["pageErrors"]),
        "motionResponses": len(browser["motionResponses"]), "failedMotionGlbResponses": 0,
        "initialBootstrapRequestCancellations": sum(x.get("error") == "net::ERR_ABORTED" for x in browser.get("failedRequests", [])),
        "mobileOverflow": browser["overflow"],
    },
    "preservation": {
        "baselineHead": baseline["head"], "dirtyEntriesAtStart": baseline["dirtyEntryCount"],
        "hashedRegularFilesAtStart": baseline["hashedRegularFiles"],
        "nonOwnedBaselineFilesRecheckedUnchanged": protected_checked,
        "OpenSimStatusAtStart": baseline["preservation"]["OpenSim_ModelsStatus"],
        "sourceManifestSha256": manifest_sha, "sourceOverlaySha256": overlay_sha,
        "haCanonicalBindingAdded": False, "sourceOnly": True,
        "humanReview": "not_performed", "publicRedistribution": "held",
    },
    "limitations": [
        "Authored poses are educational source observations, not measured normal joint axes, attachment coordinates, force/activation, or normal range of motion.",
        "Quadriceps attachment evidence is qualitative and does not establish a measured footprint or independent patellar glide.",
        "Geometry/contact checks sample authored keys and eight subdivisions; continuous collision freedom is not claimed.",
        "Browser checks cover bilateral representative muscle and bone selections, not every selector row or whole-target extent.",
        "Unit 01 learner-browser evidence remains blocked_by_environment and was not relabeled as a pass by this unit.",
    ],
    "passed": True,
}
(EVIDENCE / "validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(result, ensure_ascii=False, indent=2))
