#!/usr/bin/env python3
"""Rebuild the bounded T100-B03 terminology and source-class-member overlay."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
BASELINE = json.loads((HERE / "start-baseline.json").read_text())
OBS_PATH = HERE / "source-query-observations.json"
SCOPE_PATH = ROOT / "atlas-data/catalog/target-scope-t96.json"
CATALOG_PATH = ROOT / "work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json"
SOURCE_META_PATH = ROOT / "work/evidence/T100/resolution-2026-09-29/source-metadata.json"
REMAINING_PATH = ROOT / "work/evidence/T100/resolution-2026-09-29/remaining-targets.json"
COMPILED_PATH = ROOT / "atlas-data/source-cache/datasets/za/compiled/manifest.json"
OVERLAY_REL = "atlas-data/overlays/za-local-integration.json"
OVERLAY_PATH = ROOT / OVERLAY_REL
LEDGER_PATH = HERE / "term-and-correspondence-ledger.json"
CORR_PATH = HERE / "structure-correspondence.json"
DATE = "2026-09-29"
REVISION = "c7010a903b75a2fd24a13b1c2c4c3546a9223780"
SOURCE_HASH = "9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd"
EXPECTED = [
    "TA2:1068", "TA2:1115", "TA2:1116", "TA2:1117", "TA2:1118",
    "TA2:1137", "TA2:1138", "TA2:1248", "TA2:1249", "TA2:1262",
]
TA2_SOURCE = "fipat-ta2-t100-b03-frozen-target-terms"
ZA_SOURCE = "za-t99-t100-b03-frozen-source-objects"
KMLE_SOURCES = {
    "lumbar": "kmle-t100-b03-lumbar-vertebra-opened",
    "rib": "kmle-t100-b03-rib-opened",
    "lumbarRib": "kmle-t100-b03-lumbar-rib-opened",
    "accessoryThorax": "kmle-t100-b03-accessory-thorax-opened",
    "suprasternal": "kmle-t100-b03-suprasternal-opened",
    "hand": "kmle-t100-b03-hand-opened",
    "carpal": "kmle-t100-b03-carpal-opened",
    "accessoryCarpal": "kmle-t100-b03-accessory-carpal-opened",
}
KMLE_OBSERVATION_IDS = {
    "lumbar": "kmle-b03-lumbar-vertebra",
    "rib": "kmle-b03-rib",
    "lumbarRib": "kmle-b03-lumbar-rib",
    "accessoryThorax": "kmle-b03-accessory-thorax",
    "suprasternal": "kmle-b03-suprasternal",
    "hand": "kmle-b03-hand",
    "carpal": "kmle-b03-carpal",
    "accessoryCarpal": "kmle-b03-accessory-carpal",
}
ORDINALS = ["First", "Second", "Third", "Fourth", "Fifth", "Sixth",
            "Seventh", "Eighth", "Ninth", "Tenth", "Eleventh", "Twelfth"]
CARPALS = ["Scaphoid", "Lunate", "Triquetrum", "Pisiform",
           "Trapezium", "Trapezoid", "Capitate", "Hamate"]


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def read(path: Path):
    return json.loads(path.read_text())


def write(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def verify_immutable_inputs():
    immutable = [
        "atlas-data/catalog/target-scope-t96.json",
        "work/evidence/T100/resolution-2026-09-29/remaining-targets.json",
        "work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json",
        "work/evidence/T100/resolution-2026-09-29/source-metadata.json",
        "atlas-data/source-cache/datasets/za/compiled/manifest.json",
    ]
    for rel in immutable:
        expected = BASELINE["inputSha256"][rel]
        actual = sha_file(ROOT / rel)
        if actual != expected:
            raise SystemExit(f"frozen B03 input changed: {rel}: {actual} != {expected}")


def evidence_sources(observations):
    source_rows = [
        {
            "id": TA2_SOURCE,
            "url": "https://ta2viewer.openanatomy.org/",
            "sourceLabel": "FIPAT Terminologia Anatomica, 2nd edition, online vocabulary 2.07; T96 frozen target rows",
            "exactEdition": "Terminologia Anatomica 2nd edition, vocabulary 2.07",
            "editionExposure": "Exact vocabulary/version and source hash recorded in frozen T96 scope.",
            "accessDate": DATE,
            "accessMethod": "local_frozen_metadata",
            "locator": "atlas-data/catalog/target-scope-t96.json; frozen T96 rows for "
                       + ", ".join(EXPECTED) + "; exact English/Latin, semantic kind, parent, ancestry and source flags; SHA256 "
                       + sha_file(SCOPE_PATH),
            "term": None, "koModern": None, "koTraditional": None,
        },
        {
            "id": ZA_SOURCE,
            "url": "https://github.com/z-anatomy/Models-of-human-anatomy/tree/" + REVISION,
            "sourceLabel": "T98/T99 frozen Z-Anatomy source-object catalogue and evaluated scene metadata",
            "exactEdition": REVISION,
            "editionExposure": "Exact source commit and archive hash pinned; catalogue does not declare upstream FJ object IDs.",
            "accessDate": DATE,
            "accessMethod": "local_frozen_metadata",
            "locator": "work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json and "
                       "work/evidence/T100/resolution-2026-09-29/source-metadata.json; exact sourceKey/name/dataName/parent/collections/sourceLabelSide/evaluatedGeometrySha256; archive SHA256 "
                       + SOURCE_HASH,
            "term": None, "koModern": None, "koTraditional": None,
        },
    ]
    obs_by_id = {o["id"]: o for o in observations["observations"]}
    for key, source_id in KMLE_SOURCES.items():
        obs = obs_by_id[KMLE_OBSERVATION_IDS[key]]
        source_rows.append({
            "id": source_id,
            "observationId": obs["id"],
            "url": obs["url"],
            "sourceLabel": "KMLE aggregate terminology search; " + obs["accessMethod"],
            "exactEdition": None,
            "editionExposure": "Underlying dictionary edition/revision is not exposed by KMLE.",
            "accessDate": DATE,
            "accessMethod": obs["accessMethod"],
            "locator": obs["locator"],
            "term": obs.get("observedEntries", [None])[0],
            "koModern": None,
            "koTraditional": None,
        })
    return source_rows


def source_ref(source_obj, source_meta):
    meta = source_meta.get(source_obj["name"])
    if not meta or meta["parent"] != source_obj["parent"] or meta["collections"] != source_obj["collections"]:
        raise ValueError(f"source hierarchy differs: {source_obj['name']}")
    locator = source_obj["sourceLocator"]
    if locator["archivePath"] != "Z-Anatomy/Startup.blend" or locator["sourceFileSha256"] != SOURCE_HASH:
        raise ValueError(f"source locator/hash mismatch: {source_obj['name']}")
    if source_obj["sourceKey"] != "ZA-c7010a9-" + source_obj["sourceKey"].split("ZA-c7010a9-", 1)[-1]:
        raise ValueError(f"unexpected source key: {source_obj['name']}")
    if not re.fullmatch(r"[a-f0-9]{64}", source_obj["evaluatedGeometrySha256"]):
        raise ValueError(f"evaluated hash missing: {source_obj['name']}")
    return {
        "sourceKey": source_obj["sourceKey"],
        "sourceObjectName": source_obj["name"],
        "sourceDataName": source_obj["dataName"],
        "sourceParent": source_obj["parent"],
        "sourceCollections": source_obj["collections"],
        "sourceSide": source_obj["sourceLabelSide"],
        "evaluatedGeometrySha256": source_obj["evaluatedGeometrySha256"],
        "sourceHash": SOURCE_HASH,
        "sourceRevision": REVISION,
        "sourceLocator": locator,
    }


def field(value, source_ids, locator, missing_reason=None):
    return {
        "value": value,
        "sourceIds": source_ids,
        "locator": locator if value is not None else None,
        "status": "evidence_backed" if value is not None else "missing",
        "missingReason": missing_reason if value is None else None,
    }


def main():
    verify_immutable_inputs()
    scope = read(SCOPE_PATH)
    catalog = read(CATALOG_PATH)
    metadata = read(SOURCE_META_PATH)
    remaining = read(REMAINING_PATH)
    observations = read(OBS_PATH)
    if scope["revision"] != "T96-2026-09-28-semantic-freeze-v1" or len(scope["targets"]) != 542:
        raise SystemExit("T96 scope revision/denominator changed")
    if observations["batchId"] != "T100-B03-lumbar-ribs-hand-groups":
        raise SystemExit("B03 KMLE observation inventory is not this batch")
    requested = [t["targetId"] for t in read(HERE / "batch-scope.json")["targets"]]
    if requested != EXPECTED or read(HERE / "batch-scope.json")["targetCount"] != 10:
        raise SystemExit("B03 frozen target list differs")
    if remaining["targets"] != 542 or len(remaining["unresolved"]) != 182:
        raise SystemExit("historical target denominator changed")
    if not set(EXPECTED) <= {r["targetId"] for r in remaining["unresolved"]}:
        raise SystemExit("B03 target is not in the frozen unresolved inventory")
    if catalog["sourceHash"] != SOURCE_HASH or catalog["sourceRevision"] != REVISION or len(catalog["objects"]) != 960:
        raise SystemExit("pinned source catalogue identity/count changed")

    raw_overlay = subprocess.check_output(
        ["git", "show", f"{BASELINE['rootHead']}:{OVERLAY_REL}"], cwd=ROOT)
    if sha_bytes(raw_overlay) != BASELINE["overlaySha256"]:
        raise SystemExit("starting overlay bytes differ from B03 baseline")
    overlay = json.loads(raw_overlay)
    if overlay["scope"] != {"targets": 542, "memberships": 563, "regions": 12}:
        raise SystemExit("frozen task denominator changed")

    target_rows = {t["id"]: t for t in scope["targets"]}
    surface_rows = {o["name"]: o for o in catalog["objects"]}
    source_rows = {o["sourceKey"]: o for o in overlay["objects"]}
    source_meta = {o["name"]: o for o in metadata["objects"]}
    if len(source_rows) != 960 or set(source_rows) != set(surface_rows[k]["sourceKey"] for k in surface_rows):
        raise SystemExit("compiled overlay/source object inventory differs")

    members: dict[str, list[dict]] = {target_id: [] for target_id in EXPECTED}
    expectations = {
        "TA2:1068": [(f"Vertebra L{i}", f"lumbar:L{i}", None) for i in range(1, 6)],
        "TA2:1118": [
            (f"{ordinal} rib.{side_code}", f"rib:{index:02d}", side)
            for index, ordinal in enumerate(ORDINALS, 1)
            for side_code, side in (("l", "left"), ("r", "right"))
        ],
        "TA2:1249": [
            (f"{name} bone.{side_code}", f"carpal:{name.lower()}", side)
            for name in CARPALS
            for side_code, side in (("l", "left"), ("r", "right"))
        ],
    }
    for target_id, expected_members in expectations.items():
        for name, code, side in expected_members:
            obj = surface_rows.get(name)
            if not obj:
                raise SystemExit(f"frozen exact source member missing: {target_id}:{name}")
            ref = source_ref(obj, source_meta)
            if obj["kind"] != "skeletal_surface" or obj["sourceLabelSide"] != side:
                if side is not None or obj["kind"] != "skeletal_surface":
                    raise SystemExit(f"source class/side differs: {name}")
            expected_parent = (
                "Lumbar vertebrae.g" if target_id == "TA2:1068" else
                ("True ribs.g" if int(code.split(":")[1]) <= 7 else
                 "False ribs.g" if int(code.split(":")[1]) <= 10 else "Floating ribs.g") if target_id == "TA2:1118" else
                "Bones of free part of upper limb.g"
            )
            if obj["parent"] != expected_parent:
                raise SystemExit(f"source parent differs: {name}: {obj['parent']}")
            if target_id == "TA2:1068" and not {"Back", "Lumbar vertebrae", "Vertebral column"} <= set(obj["collections"]):
                raise SystemExit(f"lumbar hierarchy collections missing: {name}")
            if target_id == "TA2:1118" and not {"Ribs", "Thorax"} <= set(obj["collections"]):
                raise SystemExit(f"rib hierarchy collections missing: {name}")
            if target_id == "TA2:1249":
                expected_limb = "Left upper limb" if side == "left" else "Right upper limb"
                if expected_limb not in obj["collections"] or "Right hand" not in obj["collections"]:
                    raise SystemExit(f"carpal hierarchy/collection observation changed: {name}")
            row = source_rows[obj["sourceKey"]]
            if row["kind"] != "bone" or row["side"] != side:
                raise SystemExit(f"overlay source side/kind mismatch: {name}")
            members[target_id].append({**ref, "memberCode": code})

    if [len(members[x]) for x in ("TA2:1068", "TA2:1118", "TA2:1249")] != [5, 24, 16]:
        raise SystemExit("B03 exact member counts differ from frozen sets")
    if len({x["sourceKey"] for values in members.values() for x in values}) != 45:
        raise SystemExit("B03 members are not 45 unique source objects")

    raw_names = [o["name"] for o in metadata["objects"]]
    surface_names = list(surface_rows)
    exact_candidates = {
        "TA2:1115": ["Supernumerary ribs"],
        "TA2:1116": ["Cervical rib"],
        "TA2:1117": ["Lumbar rib"],
        "TA2:1137": ["Accessory bones of thorax"],
        "TA2:1138": ["Suprasternal bones"],
        "TA2:1248": ["Bones of hand"],
        "TA2:1249": ["Carpal bones"],
        "TA2:1262": ["Accessory carpal bones"],
    }
    exact_inventory = []
    for target_id, candidates in exact_candidates.items():
        for candidate in candidates:
            raw_matches = sorted(x for x in raw_names if x.casefold() == candidate.casefold()
                                 or x.casefold() in {candidate.casefold() + ".g", candidate.casefold() + ".j"})
            surface_matches = sorted(x for x in surface_names if x.casefold() == candidate.casefold())
            exact_inventory.append({
                "targetId": target_id, "queriedExactObjectName": candidate,
                "rawObjectOrGroupMatches": raw_matches,
                "evaluatedSurfaceNameMatches": surface_matches,
                "status": "named_surface_missing" if not surface_matches else "exact_surface_candidate_requires_review",
                "interpretation": (
                    "No exact evaluated surface with this target name is in the frozen T98 catalogue; a raw group/helper name is not geometry."
                    if raw_matches else
                    "No exact raw object or evaluated surface name is present in the frozen T100/T98 local inventories; this is not proof of anatomical absence."
                ),
            })

    all_evidence = evidence_sources(observations)
    source_by_id = {s["id"]: s for s in all_evidence}
    if len(source_by_id) != len(all_evidence):
        raise SystemExit("duplicate B03 provenance source id")
    old_ids = {s["id"] for s in overlay.get("evidenceSources", [])}
    if old_ids & set(source_by_id):
        raise SystemExit("B03 provenance ID collides with a prior batch")
    overlay["evidenceSources"] = overlay.get("evidenceSources", []) + all_evidence

    target_definitions = {
        "TA2:1068": {
            "modern": "허리뼈", "traditional": "요추골", "modernSource": KMLE_SOURCES["lumbar"],
            "traditionalSource": KMLE_SOURCES["lumbar"],
            "modernLocator": "Opened KMLE Search=lumbar+vertebra, 대한의협 맞춤결과 node 46: lumbar vertebra → 허리뼈, 요추.",
            "traditionalLocator": "Opened KMLE Search=lumbar+vertebra, 대한해부학회 맞춤결과 node 248: Lumbar vertebrae(first-fifth) → 허리(척추)뼈(첫째-다섯째) [요추골], old term 요추골.",
            "classification": {"meaningType": "individual bone class", "groupPartVariant": "five exact named class members Vertebra L1-L5; no parent series object is claimed", "laterality": "midline/nonpaired source labels"},
            "surface": {"status": "five_exact_class_member_surfaces", "relationKind": "class_member", "sourceMembers": members["TA2:1068"], "exactAggregateSourceObject": None, "note": "Only exact L1-L5 evaluated mesh objects under Lumbar vertebrae.g are related; no vertebral series object or side is inferred."},
        },
        "TA2:1115": {
            "modern": "과잉갈비뼈", "traditional": "과잉늑골", "modernSource": KMLE_SOURCES["rib"],
            "traditionalSource": KMLE_SOURCES["rib"],
            "modernLocator": "Opened KMLE Search=rib, 대한의협 맞춤결과 node 158: supernumerary rib → 과잉갈비뼈, 과잉늑골. The opened result is a singular headword; no member count is derived from it.",
            "traditionalLocator": "Opened KMLE Search=rib, 대한의협 맞춤결과 node 158: supernumerary rib → 과잉갈비뼈, 과잉늑골. The opened result is a singular headword; series cardinality remains unresolved.",
            "classification": {"meaningType": "bone series", "groupPartVariant": "supernumerary rib series; no exact series or variant member object in the frozen source inventory", "laterality": "not specified; no bilateral expansion"},
            "surface": {"status": "exact_surface_missing", "exactSourceObject": None, "exactMemberCrosswalkAdded": False, "note": "Ordinary rib surfaces are not reused as supernumerary members; absence from this frozen source inventory is not anatomical absence."},
        },
        "TA2:1116": {
            "modern": "목갈비뼈", "traditional": "경늑골", "modernSource": KMLE_SOURCES["rib"],
            "traditionalSource": KMLE_SOURCES["rib"],
            "modernLocator": "Opened KMLE Search=rib, 대한해부학회 similar-result nodes 376-377: (Cervical rib) → (목갈비뼈).",
            "traditionalLocator": "Opened KMLE Search=rib, 대한해부학회 similar-result nodes 376-377: cervical rib old term 경늑골.",
            "classification": {"meaningType": "individual inconstant bone variant", "groupPartVariant": "cervical rib variant of the supernumerary-rib series; not a cervical vertebra", "laterality": "not specified; no side expansion"},
            "surface": {"status": "variant_surface_missing", "exactSourceObject": None, "exactMemberCrosswalkAdded": False, "note": "No exact cervical-rib surface is present; ordinary ribs and cervical vertebrae are not substituted."},
        },
        "TA2:1117": {
            "modern": None, "traditional": "요추늑골", "modernSource": KMLE_SOURCES["lumbarRib"],
            "traditionalSource": KMLE_SOURCES["lumbarRib"],
            "modernMissing": "No exact current modern Korean entry was surfaced for lumbar rib. Do not compose a modern name from 허리뼈/갈비뼈.",
            "traditionalLocator": "Opened KMLE Search=lumbar+rib, old 대한의협 3 exact-match section node 162: lumbar rib → 요추늑골. No current KAS/KMA exact row surfaced.",
            "classification": {"meaningType": "individual inconstant bone variant", "groupPartVariant": "lumbar rib variant in the supernumerary-rib series; exact source member absent", "laterality": "not specified; no side expansion"},
            "surface": {"status": "variant_surface_missing", "exactSourceObject": None, "exactMemberCrosswalkAdded": False, "note": "No exact lumbar-rib object is present in the frozen source inventory; ordinary ribs are not substituted."},
        },
        "TA2:1118": {
            "modern": "갈비뼈", "traditional": "늑골", "modernSource": KMLE_SOURCES["rib"],
            "traditionalSource": KMLE_SOURCES["rib"],
            "modernLocator": "Opened KMLE Search=rib, 대한해부학회 맞춤결과 nodes 354-358: Rib → 갈비뼈 [늑골].",
            "traditionalLocator": "Opened KMLE Search=rib, 대한해부학회 맞춤결과 nodes 354-358: Rib → 갈비뼈 [늑골], old term 늑골.",
            "classification": {"meaningType": "individual bone class", "groupPartVariant": "12 ordinary named rib levels with left/right source surfaces; supernumerary/cervical/lumbar variants remain separate targets", "laterality": "explicit source suffix and catalogue side metadata for each paired surface"},
            "surface": {"status": "24_exact_class_member_surfaces", "relationKind": "class_member", "sourceMembers": members["TA2:1118"], "exactAggregateSourceObject": None, "note": "First through twelfth ordinary ribs, left and right. Source parents split as true ribs (1-7), false ribs (8-10), and floating ribs (11-12); costal cartilage is excluded."},
        },
        "TA2:1137": {
            "modern": None, "traditional": None, "modernSource": KMLE_SOURCES["accessoryThorax"],
            "traditionalSource": KMLE_SOURCES["accessoryThorax"],
            "modernMissing": "No exact Korean terminology entry for the accessory-bones-of-thorax group appeared in the opened aggregate result; the suprasternal child is not substituted.",
            "traditionalMissing": "No exact traditional Korean group entry appeared; do not infer a Sino-Korean label from child names.",
            "classification": {"meaningType": "bone group", "groupPartVariant": "accessory thoracic bone group; exact group/member composition and surface are unresolved", "laterality": "not specified; no side expansion"},
            "surface": {"status": "group_surface_missing", "exactSourceObject": None, "exactMemberCrosswalkAdded": False, "note": "The exact parent group and member set are not represented by evaluated source surfaces in this frozen inventory."},
        },
        "TA2:1138": {
            "modern": "복장위뼈", "traditional": "흉상골", "modernSource": KMLE_SOURCES["suprasternal"],
            "traditionalSource": KMLE_SOURCES["suprasternal"],
            "modernLocator": "Opened KMLE Search=suprasternal+bones, 대한해부학회 similar-result nodes 114-115: (Suprasternal bones) → (복장위뼈).",
            "traditionalLocator": "Opened KMLE Search=suprasternal+bones, 대한해부학회 similar-result nodes 114-115: old term 흉상골.",
            "classification": {"meaningType": "inconstant bone group", "groupPartVariant": "suprasternal-bones group under accessory thoracic bones; exact source surface absent", "laterality": "not specified; no side expansion"},
            "surface": {"status": "variant_group_surface_missing", "exactSourceObject": None, "exactMemberCrosswalkAdded": False, "note": "No exact suprasternal surface is present; no sternum or neighboring thoracic bone is substituted."},
        },
        "TA2:1248": {
            "modern": "손뼈", "traditional": "수골", "modernSource": KMLE_SOURCES["hand"],
            "traditionalSource": KMLE_SOURCES["hand"],
            "modernLocator": "Opened KMLE Search=bones+of+hand, 대한해부학회 exact result nodes 201-202: Bones of hand → 손뼈.",
            "traditionalLocator": "Opened KMLE Search=bones+of+hand, 대한해부학회 exact result nodes 201-202: old term 수골.",
            "classification": {"meaningType": "bone group", "groupPartVariant": "whole-hand bone group; exact aggregate surface and complete member denominator are not established by the 16 carpal surfaces", "laterality": "group is not side-expanded; observed descendants have source-specific sides"},
            "surface": {"status": "aggregate_surface_missing_descendant_members_not_bound_to_parent", "exactAggregateSourceObject": None, "exactMemberCrosswalkAdded": False, "observedDescendantSurfacesNotBound": [m for target_members in [members["TA2:1249"]] for m in target_members], "note": "Sixteen carpal surfaces are linked only to child target TA2:1249. They do not complete or directly bind the whole-hand group; metacarpal/phalangeal and other member coverage is not asserted here."},
        },
        "TA2:1249": {
            "modern": "손목뼈", "traditional": "수근골", "modernSource": KMLE_SOURCES["carpal"],
            "traditionalSource": KMLE_SOURCES["carpal"],
            "modernLocator": "Opened KMLE Search=carpal+bones, 대한해부학회 exact result nodes 171-172: Carpal bones → 손목뼈.",
            "traditionalLocator": "Opened KMLE Search=carpal+bones, 대한해부학회 exact result nodes 171-172: old term 수근골.",
            "classification": {"meaningType": "bone group", "groupPartVariant": "eight named standard carpal bones with bilateral surfaces observed; group remains partial because accessory carpal child TA2:1262 is unresolved", "laterality": "member surfaces carry explicit .l/.r suffix and catalogue side metadata"},
            "surface": {"status": "partial_eight_named_class_members_sixteen_surfaces_accessory_child_missing", "relationKind": "class_member", "sourceMembers": members["TA2:1249"], "exactAggregateSourceObject": None, "note": "The eight named standard carpals are observed. Accessory carpal bones TA2:1262 have no exact surface in the frozen source inventory. Raw Right hand collection membership is inconsistent for .l objects; side is taken only from the exact object suffix and sourceLabelSide."},
        },
        "TA2:1262": {
            "modern": None, "traditional": None, "modernSource": KMLE_SOURCES["accessoryCarpal"],
            "traditionalSource": KMLE_SOURCES["accessoryCarpal"],
            "modernMissing": "No exact Korean entry for accessory carpal bones appeared in the opened KMLE aggregate result; do not compose one from 손목뼈.",
            "traditionalMissing": "No exact traditional Korean group entry appeared; do not infer one from generic carpal terminology.",
            "classification": {"meaningType": "bone group", "groupPartVariant": "accessory carpal-bones group; child os centrale is outside the source surface inventory here", "laterality": "not specified; no side expansion"},
            "surface": {"status": "group_surface_missing", "exactSourceObject": None, "exactMemberCrosswalkAdded": False, "note": "No exact accessory-carpal or os centrale evaluated surface is present in the frozen source inventory; standard carpals are not substituted."},
        },
    }

    terms = []
    for target_id in EXPECTED:
        definition = target_definitions[target_id]
        target = target_rows[target_id]
        english = target["term"]["english"]
        latin = target["term"]["latin"]
        modern = definition["modern"]
        traditional = definition["traditional"]

        def name_field(value, source_key, locator_key, missing_key):
            source_id = definition[source_key]
            if value is None:
                return field(None, [source_id], None, definition[missing_key])
            return field(value, [source_id], definition[locator_key])

        source_ids_for_ko = sorted({definition["modernSource"], definition["traditionalSource"]})
        term = {
            "targetId": target_id,
            "targetTermSourceIds": [TA2_SOURCE],
            "english": english,
            "latin": latin,
            "sourceSynonyms": target["term"].get("sourceSynonyms", {}),
            "relatedTerms": target["sourceFlags"].get("relatedTerms", []),
            "semanticKind": target["semanticKind"],
            "primaryOwner": target["primaryOwner"],
            "regionIds": target["regionIds"],
            "sourceParentId": target["sourceParentId"],
            "sourceAncestryIds": target["sourceAncestryIds"],
            "sourceFlags": target["sourceFlags"],
            "classification": definition["classification"],
            "names": {"koModern": modern, "koTraditional": traditional, "en": english},
            "fieldEvidence": {
                "koModern": name_field(modern, "modernSource", "modernLocator", "modernMissing"),
                "koTraditional": name_field(traditional, "traditionalSource", "traditionalLocator", "traditionalMissing"),
                "en": field(english, [TA2_SOURCE], f"T96 {target_id} exact English term: {english}"),
                "latin": field(latin, [TA2_SOURCE], f"T96 {target_id} exact Latin term: {latin}"),
            },
            "existingSurface": definition["surface"],
            "observedSurfacesNotBound": definition["surface"].get("observedDescendantSurfacesNotBound", []),
            "learnerBindingCreated": False,
            "canonicalHaConceptId": None,
            "sourceOnly": True,
            "humanReview": "not_performed",
            "publicRedistribution": "held",
            "newGeometryCreated": False,
        }
        terms.append(term)

    evidence_map = {source["id"]: source for source in all_evidence}
    relation_records = []
    for target_id in expectations:
        target = target_rows[target_id]
        target_members = members[target_id]
        for member in target_members:
            obj = surface_rows[member["sourceObjectName"]]
            expected_overlay = source_rows[member["sourceKey"]]
            side = member["sourceSide"]
            name = member["sourceObjectName"]
            relation = {
                "targetId": target_id,
                "targetEnglish": target["term"]["english"],
                "targetLatin": target["term"]["latin"],
                "targetSemanticKind": target["semanticKind"],
                "targetPrimaryOwner": target["primaryOwner"],
                "targetRegionIds": target["regionIds"],
                "targetLaterality": target["sourceCardinality"]["lateralityState"],
                "sourceKey": member["sourceKey"],
                "sourceObjectName": name,
                "sourceDataName": obj["dataName"],
                "sourceParent": obj["parent"],
                "sourceCollections": obj["collections"],
                "sourceSide": side,
                "evaluatedGeometrySha256": obj["evaluatedGeometrySha256"],
                "sourceHash": SOURCE_HASH,
                "sourceRevision": REVISION,
                "matchBasis": "Frozen T96 class/member semantics plus exact evaluated Z-Anatomy object name, exact parent and collection; sourceLabelSide corroborates only the explicit .l/.r suffix when present. No upstream FJ ID, learner identity or geometry is inferred.",
                "directObjectNameMatch": False,
                "ancestorNameAloneUsed": False,
                "upstreamFjOrTa2IdClaim": False,
                "canonicalHaBindingCreated": False,
                "humanReview": "not_performed",
                "relationKind": "class_member",
                "matchedTargetSynonym": None,
                "sourceSegmentCode": re.search(r"L[1-5]$", name).group(0) if target_id == "TA2:1068" else None,
                "memberCode": member["memberCode"],
                "matchEvidenceSourceIds": [ZA_SOURCE, TA2_SOURCE],
            }
            if not expected_overlay["sourceOnly"] or expected_overlay["haConceptId"] is not None:
                raise SystemExit(f"source row unexpectedly learner-bound: {name}")
            overlay_row = expected_overlay
            if target_id not in overlay_row["targetIds"]:
                overlay_row["targetIds"].append(target_id)
            relations = overlay_row.setdefault("targetRelationEvidence", [])
            if any(r["targetId"] == target_id for r in relations):
                raise SystemExit(f"duplicate B03 source-target relation: {name}")
            relations.append(relation)
            relation_records.append({**relation, "sourceMember": member})

    old_terms = overlay.get("targetTerminologyEvidence", [])
    if {t["targetId"] for t in old_terms} & set(EXPECTED):
        raise SystemExit("B03 terminology was already appended; baseline is not clean")
    overlay["targetTerminologyEvidence"] = old_terms + terms
    overlay["revision"] = "T100-source-taxonomy-local-display-v1-B03-lumbar-ribs-hand-groups"
    write(OVERLAY_PATH, overlay)

    target_counts = {target_id: sum(r["targetId"] == target_id for r in relation_records) for target_id in EXPECTED}
    ledger = {
        "schemaVersion": 1,
        "batchId": "T100-B03-lumbar-ribs-hand-groups",
        "capturedOn": DATE,
        "scope": {
            "targetCount": 10, "requestedTargetIds": EXPECTED,
            "taskTargetDenominator": 542, "taskRegionMembershipDenominator": 563, "regions": 12,
            "targetScopeRevision": scope["revision"], "targetScopeSha256": sha_file(SCOPE_PATH),
            "zaSourceRevision": REVISION, "zaSourceFileSha256": SOURCE_HASH,
            "historicalRemainingCountAtBatchStart": 172,
            "historicalRemainingTargetInventorySha256": sha_file(REMAINING_PATH),
            "sourceObjectCatalogueSha256": sha_file(CATALOG_PATH),
            "sourceMetadataSha256": sha_file(SOURCE_META_PATH),
            "compiledManifestSha256": sha_file(COMPILED_PATH),
            "startingHead": BASELINE["rootHead"],
        },
        "sourceEvidence": all_evidence,
        "fieldSourceSeparation": {
            "fipat": "T96 frozen local metadata, exact vocabulary 2.07; not a fresh viewer-page read in this batch.",
            "kmle": "Opened aggregate HTML result pages. Search-result/index text is distinguished from a dictionary record; underlying dictionary edition is not exposed.",
            "za": "Pinned local T98/T99 catalogue and evaluated geometry metadata; this catalogue declares no upstream FJ IDs.",
        },
        "targets": terms,
        "exactSourceNameInventory": exact_inventory,
        "crosswalkRelations": relation_records,
        "memberCountsByTarget": target_counts,
        "nonClaims": [
            "not a whole-body completion claim",
            "not an upstream FJ object-ID claim",
            "not a canonical HA learner binding or learner alias",
            "not a new geometry or rights decision",
            "not human anatomy review",
            "not proof of anatomical absence for missing source surfaces",
        ],
    }
    write(LEDGER_PATH, ledger)
    corr = {
        "schemaVersion": 1, "batchId": ledger["batchId"], "targetCount": 10,
        "exactOverlayRelations": len(relation_records),
        "sourceObjectMembers": len({r["sourceKey"] for r in relation_records}),
        "memberCountsByTarget": target_counts,
        "targetsWithExactRelations": [t for t in EXPECTED if target_counts[t]],
        "targetsWithoutExactRelations": [t for t in EXPECTED if not target_counts[t]],
        "targetsWithPartialGroupCoverage": ["TA2:1248", "TA2:1249"],
        "unresolvedGeometryAndIdentityRemain": True,
        "targetRows": [{
            "targetId": term["targetId"], "semanticKind": term["semanticKind"],
            "classification": term["classification"], "existingSurface": term["existingSurface"],
            "koreanNames": term["names"], "fieldEvidence": term["fieldEvidence"],
            "learnerBindingCreated": False, "canonicalHaConceptId": None, "newGeometryCreated": False,
            "sourceOnly": True, "humanReview": "not_performed", "publicRedistribution": "held",
        } for term in terms],
        "inputDenominators": {"targets": 542, "memberships": 563, "regions": 12},
        "historicalRemainingAtBatchStart": 172,
        "batchDispositionCount": 10,
        "historicalRemainderAfterB03DispositionPass": 162,
        "preservedCounts": {
            "sourceObjects": len(overlay["objects"]),
            "locallyDisplayable": sum(r["localDisplayEligible"] for r in overlay["objects"]),
            "haBoundRows": sum(bool(r["haConceptId"]) for r in overlay["objects"]),
            "publicRedistribution": "held", "humanReview": "not_performed",
        },
        "overlaySha256": sha_file(OVERLAY_PATH),
    }
    write(CORR_PATH, corr)
    print(json.dumps({
        "batchId": ledger["batchId"], "targets": 10, "exactRelations": len(relation_records),
        "missingExactRelations": len(EXPECTED) - len(corr["targetsWithExactRelations"]),
        "overlaySha256": corr["overlaySha256"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
