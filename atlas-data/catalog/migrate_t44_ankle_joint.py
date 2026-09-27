#!/usr/bin/env python3
"""Idempotent T44 canonical ankle joint/action migration; no review promotion."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "atlas-data/catalog/canonical-catalog.json"
REVISION = "T44-right-ankle-input-v1"
JOINT = "HA-S-JOINT-R-ANKLE-TALOCRURAL"
ACTION = "HA-JA-T44-R-TIBANT-ANKLE-DF"

ITEMS = {
  "sources": [
    {"id": "OPENSIM_GAIT2392_T44", "title": "OpenSim Gait2392 Simbody Thelen2003 model",
     "authors": ["Delp SL", "Loan JP", "Hoy MG", "Zajac FE", "Topp EL", "Rosen JM", "Thelen DG", "Anderson FC", "Seth A"],
     "edition": "Local OpenSim_Models Gait2392_Simbody/gait2392_thelen2003muscle.osim",
     "year": None, "urlOrLocalRef": "OpenSim_Models/Models/Gait2392_Simbody/gait2392_thelen2003muscle.osim",
     "accessDate": "2026-09-27", "license": {"id": "LIC-OPENSIM-GAIT2392-CC-BY-3.0",
       "name": "Creative Commons Attribution 3.0", "spdxId": "CC-BY-3.0",
       "allowedUses": ["internal", "research", "learning", "derivative", "redistribute"],
       "attributionRequired": True,
       "attributionText": "OpenSim Gait2392 model: Delp, Loan, Hoy, Zajac, Topp, Rosen, Thelen, Anderson, Seth; CC BY 3.0.",
       "derivativesAllowed": True, "redistributionAllowed": True}},
    {"id": "MJMS_MMT_T44", "title": "Structured Manual Muscle Testing of the Lower Limbs",
     "authors": ["Lim XY", "Wong JKC", "Idris Z", "Ghani ARI", "Abdul Halim S", "Abdullah JM"],
     "edition": "Malays J Med Sci. 2023;30(5):206-220; doi:10.21315/mjms2023.30.5.17",
     "year": 2023, "urlOrLocalRef": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10624435/",
     "accessDate": "2026-09-27", "license": {"id": "LIC-MJMS-MMT-CC-BY-4.0",
       "name": "Creative Commons Attribution 4.0", "spdxId": "CC-BY-4.0",
       "allowedUses": ["internal", "research", "learning", "public_learning", "derivative", "redistribute"],
       "attributionRequired": True,
       "attributionText": "Lim XY et al., Structured Manual Muscle Testing of the Lower Limbs, Malays J Med Sci 2023; CC BY 4.0.",
       "derivativesAllowed": True, "redistributionAllowed": True}}
  ],
  "evidence": [
    {"id": "EV-T44-OSIM-ANKLE-R", "sourceId": "OPENSIM_GAIT2392_T44",
     "locator": "CustomJoint ankle_r: tibia_r_offset translation, talus_r_offset, ankle_angle_r default_value, SpatialTransform rotation1 axis; associated tib_ant_r GeometryPath and model credits",
     "supportedClaimIds": [], "evidenceKind": "dataset"},
    {"id": "EV-T44-MJMS-TIBANT-DF", "sourceId": "MJMS_MMT_T44",
     "locator": "Ankle > Foot dorsiflexion and inversion: test movement and primary muscle; T21-E-HA-M-000003-action-2 previously opened full text and linked to T21-C-HA-M-000003-action",
     "supportedClaimIds": [], "evidenceKind": "primary"}
  ],
  "terms": [
    {"id": "HA-T-T44-R-ANKLE-EN", "conceptId": JOINT, "language": "en", "script": "Latn",
     "text": "Right ankle joint", "termRole": "preferred", "edition": "Gait2392 ankle_r model designation",
     "evidenceIds": ["EV-T44-OSIM-ANKLE-R"], "reviewState": "needs_review"}
  ],
  "structures": [{"id": JOINT, "kind": "joint", "termIds": ["HA-T-T44-R-ANKLE-EN"]}],
  "jointActions": [{"id": ACTION, "muscleOrPartIds": ["HA-M-000003"], "jointIds": [JOINT],
     "action": "Right ankle dorsiflexion", "postureConditions": [],
     "contractionRole": "unspecified", "taskContext": "T44 static model input only; no motion clip or measured contribution",
     "roleInTask": None, "evidenceIds": ["EV-T44-MJMS-TIBANT-DF", "EV-T44-OSIM-ANKLE-R"],
     "reviewState": "needs_review"}]
}


def migrate(data):
    if data["revision"] not in ("T13-attachment-context-v2", REVISION):
        raise ValueError("Unexpected canonical revision; audit concurrent changes before migration")
    for collection, entries in ITEMS.items():
        existing = {item["id"]: item for item in data["entities"][collection]}
        for item in entries:
            if item["id"] in existing:
                if existing[item["id"]] != item:
                    raise ValueError(f"Conflicting {collection} record {item['id']}")
            else:
                data["entities"][collection].append(item)
    data["revision"] = REVISION
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    original = CATALOG.read_bytes()
    data = migrate(json.loads(original))
    output = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode()
    if args.check:
        assert output == original, "T44 catalog migration not current"
        print("T44 canonical migration current")
    else:
        CATALOG.write_bytes(output)
        print("T44 canonical ankle joint/action migrated")


if __name__ == "__main__":
    main()
