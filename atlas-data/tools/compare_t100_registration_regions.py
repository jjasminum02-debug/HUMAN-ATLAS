#!/usr/bin/env python3
"""Compare exact cached BodyParts3D/ZA bone pairs across body regions.

This is diagnostic only. It does not write a transform into source geometry or
the learner manifest; the existing T100 pelvis registration remains a
candidate and cross-region offset differences are reported, not normalized.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work/evidence/T100/source-completion-2026-10-01/integration/registration-regional-comparison.json"
REGISTRATION = "work/evidence/T100/source-completion-2026-10-01/integration/registration-evidence.json"
FREEZES = ["work/evidence/T71/frozen-source-set.json", "work/evidence/T72/frozen-source-set.json"]
ANCHORS = [
    ("pelvis", "FJ3152", "Hip bone.r", "ZA-c7010a9-74a765dc396d690d1642153e", "06-gluteal-hip-bone-0", "right"),
    ("pelvis", "FJ3288", "Hip bone.l", "ZA-c7010a9-ecb65ff4cc3da710e5a2d157", "06-gluteal-hip-bone-0", "left"),
    ("pelvis", "FJ3393", "Sacrum", "ZA-c7010a9-95b8d859c84ae9e56cacdafc", "15-pelvis-perineum-bone-1", None),
    ("lumbar", "FJ3157", "Vertebra L1", "ZA-c7010a9-484ccd540149a7cdad5c74a8", "01-back-bone-1", None),
    ("lumbar", "FJ3159", "Vertebra L2", "ZA-c7010a9-0bc91f56657c8ad942f9f283", "01-back-bone-1", None),
    ("lumbar", "FJ3162", "Vertebra L3", "ZA-c7010a9-4ce8a03807489dbb188edadb", "01-back-bone-1", None),
    ("lumbar", "FJ3165", "Vertebra L4", "ZA-c7010a9-aae2ed33f4a0bf4f1ad5387a", "01-back-bone-1", None),
    ("lumbar", "FJ3168", "Vertebra L5", "ZA-c7010a9-0532a0f965344c7db7218160", "01-back-bone-1", None),
    ("thorax", "FJ3153", "Xiphoid process", "ZA-c7010a9-492b8564566beb4155afe719", "25-thorax-bone-1", None),
    ("thorax", "FJ3178", "Body of sternum", "ZA-c7010a9-a7c8e4f4119fede30c949007", "25-thorax-bone-1", None),
    ("thorax", "FJ3290", "Manubrium of sternum", "ZA-c7010a9-52e3a5b946ff5a2410b74a61", "25-thorax-bone-1", None),
    ("head", "FJ3200", "Frontal bone", "ZA-c7010a9-78bbaa2bb395956fc914364b", "09-head-bone-1", None),
    ("head", "FJ3289", "Mandible", "ZA-c7010a9-179fa204ccffef5f88aa335f", "09-head-bone-1", None),
    ("head", "FJ3309", "Occipital bone", "ZA-c7010a9-06ebb84f8a0406bd37b531c1", "09-head-bone-1", None),
]


def sha(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def load_registration_module():
    path = ROOT / "atlas-data/tools/register_t100_to_za.py"
    spec = importlib.util.spec_from_file_location("t100_register", path)
    if not spec or not spec.loader:
        raise RuntimeError("cannot load existing registration diagnostic")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main_data():
    module = load_registration_module()
    by_region = {}
    rows = []
    input_hashes = {REGISTRATION: sha(REGISTRATION), **{path: sha(path) for path in FREEZES}}
    for group in sorted({row[0] for row in ANCHORS}):
        selected = [row for row in ANCHORS if row[0] == group]
        module.ANCHORS = [dict(fj=fj, zaName=name, sourceKey=key, chunk=chunk, memberSide=side)
                          for _, fj, name, key, chunk, side in selected]
        result = module.run()
        by_region[group] = {
            "translationBp3dToZaMetres": result["method"]["translationBp3dToZaM"],
            "anchors": [{
                "sourceElementFileId": anchor["sourceElementFileId"],
                "zaSourceKey": anchor["zaSourceKey"], "zaSourceName": anchor["zaSourceName"],
                "bp3dSourceSha256": anchor["sourceSha256"],
                "zaEvaluatedGeometrySha256": anchor["zaEvaluatedGeometrySha256"],
                "centroidDerivedTranslationMetres": anchor["centroidDerivedBp3dToZaTranslationM"],
                "residualFromRegionalMedianMetres": anchor["translationResidualFromRobustMedianM"],
                "residualNormMetres": anchor["translationResidualNormM"],
                "preRegistrationSurface": anchor["preRegistrationSurface"],
                "regionalFitSurface": anchor["postRegistrationSurface"],
            } for anchor in result["anchors"]],
        }
        input_hashes.update(result["inputSha256"])
        rows.extend({"region": group, **anchor} for anchor in by_region[group]["anchors"])

    module.ANCHORS = [dict(fj=fj, zaName=name, sourceKey=key, chunk=chunk, memberSide=side)
                      for _, fj, name, key, chunk, side in ANCHORS]
    global_result = module.run()
    input_hashes.update(global_result["inputSha256"])
    return {
        "schemaVersion": "t100-multiregion-registration-diagnostic-v1",
        "taskId": "T100",
        "status": "single-global-transform-not-established",
        "method": "Use exact source IDs and source-named ZA counterparts already present in T71/T72/T77. For each evaluated GLB, compare arithmetic vertex centroids and deterministic bidirectional sampled nearest-vertex distances. Report pelvis/lumbar/thorax/head robust translations and the all-region robust translation; do not infer anatomy approval from these diagnostics.",
        "allRegionTranslationBp3dToZaMetres": global_result["method"]["translationBp3dToZaM"],
        "regionalFits": by_region,
        "allRegionResiduals": [{
            "sourceElementFileId": a["sourceElementFileId"], "zaSourceKey": a["zaSourceKey"],
            "translationResidualNormMetres": a["translationResidualNormM"],
            "postRegistrationSurface": a["postRegistrationSurface"],
        } for a in global_result["anchors"]],
        "interpretation": {
            "aabbUsed": False,
            "singleTransformAccepted": False,
            "regionalTranslationsAreApplied": False,
            "existingPelvisTransformStatus": "pelvis-local geometric candidate only; not independently established for all 13 supplement objects",
            "anatomicalHumanReview": "not_performed",
            "rights": "unchanged; local item decisions only, public redistribution held",
            "sourceBytesModified": False,
            "reason": "Matched exact bone pairs yield materially different regional centroid-derived translations and all-region residuals. A one-transform fit is not accepted solely from shared axes, labels, or visual plausibility. New muscle surfaces remain source observations until cross-region placement is supported.",
        },
        "inputSha256": dict(sorted(input_hashes.items())),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    content = json.dumps(main_data(), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not args.out.is_file() or args.out.read_text(encoding="utf-8") != content:
            raise SystemExit("registration diagnostic is stale")
    elif args.write:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        if args.out.exists():
            raise SystemExit("refusing to overwrite existing registration diagnostic")
        args.out.write_text(content, encoding="utf-8")
    else:
        print(content, end="")


if __name__ == "__main__":
    main()
