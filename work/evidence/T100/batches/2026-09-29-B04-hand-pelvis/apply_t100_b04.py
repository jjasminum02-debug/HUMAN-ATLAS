#!/usr/bin/env python3
"""Rebuild the bounded T100-B04 terminology and source correspondence overlay."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
BASELINE = json.loads((HERE / "start-baseline.json").read_text())
SCOPE_FILE = ROOT / "atlas-data/catalog/target-scope-t96.json"
CATALOG_FILE = ROOT / "work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json"
META_FILE = ROOT / "work/evidence/T100/resolution-2026-09-29/source-metadata.json"
REMAINDER_FILE = ROOT / "work/evidence/T100/resolution-2026-09-29/remaining-targets.json"
COMPILED_FILE = ROOT / "atlas-data/source-cache/datasets/za/compiled/manifest.json"
OBS_FILE = HERE / "source-query-observations.json"
OVERLAY_REL = "atlas-data/overlays/za-local-integration.json"
OVERLAY_FILE = ROOT / OVERLAY_REL
LEDGER_FILE = HERE / "term-and-correspondence-ledger.json"
CORR_FILE = HERE / "structure-correspondence.json"
DATE = "2026-09-29"
REVISION = "c7010a903b75a2fd24a13b1c2c4c3546a9223780"
SOURCE_HASH = "9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd"
EXPECTED = [
    "TA2:1263", "TA2:1264", "TA2:1265", "TA2:1271", "TA2:1272",
    "TA2:1277", "TA2:1278", "TA2:1279", "TA2:1281", "TA2:1282",
]
TA2_SOURCE = "fipat-ta2-t100-b04-frozen-target-terms"
ZA_SOURCE = "za-t99-t100-b04-frozen-source-objects"
KMLE_IDS = {
    "metacarpalBones": "kmle-t100-b04-metacarpal-bones-opened",
    "metacarpalBone": "kmle-t100-b04-metacarpal-bone-opened",
    "phalangesHand": "kmle-t100-b04-phalanges-hand-opened",
    "phalanx": "kmle-t100-b04-phalanx-opened",
    "sesamoidHand": "kmle-t100-b04-sesamoid-hand-opened",
    "osCentrale": "kmle-t100-b04-os-centrale-opened",
    "bonyPelvis": "kmle-t100-b04-bony-pelvis-opened",
}


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def read(path: Path):
    return json.loads(path.read_text())


def write(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def require(condition: bool, message: str):
    if not condition:
        raise SystemExit(message)


def validate_frozen_inputs():
    require(BASELINE["previousBatchGate"] == "pass", "B03 did not pass its gate")
    require(BASELINE["startingHead"] == BASELINE["previousBatchCommit"], "B04 baseline is not the B03 commit")
    require(subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == BASELINE["startingHead"],
            "HEAD changed after B04 scope freeze; do not rebuild against a moved base")
    scope_freeze = read(HERE / "batch-scope.json")
    require(scope_freeze["status"] == "frozen_before_investigation", "scope freeze is not immutable initial scope")
    require(scope_freeze["targetIds"] == EXPECTED and len(scope_freeze["targets"]) == 10, "frozen B04 target set differs")
    require(sha_file(REMAINDER_FILE) == scope_freeze["frozenRemainder"]["sha256"], "frozen remainder hash changed")
    for rel, digest in BASELINE["frozenInputSha256"].items():
        if rel == OVERLAY_REL:
            continue
        require(sha_file(ROOT / rel) == digest, f"immutable source changed: {rel}")


def source_ref(obj: dict, raw: dict) -> dict:
    meta = raw.get(obj["name"])
    require(meta is not None, f"source metadata missing: {obj['name']}")
    require((meta["parent"], meta["collections"]) == (obj["parent"], obj["collections"]),
            f"source hierarchy mismatch: {obj['name']}")
    locator = obj["sourceLocator"]
    require(locator["archivePath"] == "Z-Anatomy/Startup.blend" and locator["sourceFileSha256"] == SOURCE_HASH,
            f"source archive locator/hash mismatch: {obj['name']}")
    require(re.fullmatch(r"ZA-c7010a9-[a-f0-9]{24}", obj["sourceKey"]) is not None,
            f"unexpected derived source key: {obj['name']}")
    require(re.fullmatch(r"[a-f0-9]{64}", obj["evaluatedGeometrySha256"]) is not None,
            f"evaluated geometry hash missing: {obj['name']}")
    return {
        "sourceKey": obj["sourceKey"], "sourceObjectName": obj["name"], "sourceDataName": obj["dataName"],
        "sourceParent": obj["parent"], "sourceCollections": obj["collections"],
        "sourceSide": obj["sourceLabelSide"], "evaluatedGeometrySha256": obj["evaluatedGeometrySha256"],
        "sourceHash": SOURCE_HASH, "sourceRevision": REVISION, "sourceLocator": locator,
    }


def field(value, source_ids, locator, missing_reason=None):
    return {"value": value, "sourceIds": source_ids, "locator": locator if value is not None else None,
            "status": "evidence_backed" if value is not None else "missing",
            "missingReason": missing_reason if value is None else None}


def evidence_sources(observations: dict, scope: dict, catalog: dict):
    rows = [
        {"id": TA2_SOURCE, "url": "https://ta2viewer.openanatomy.org/",
         "sourceLabel": "FIPAT Terminologia Anatomica, 2nd edition, online vocabulary 2.07; frozen T96 target rows",
         "exactEdition": "Terminologia Anatomica 2nd edition, vocabulary 2.07",
         "editionExposure": "Exact vocabulary/version and file hash are recorded in the frozen T96 target scope.",
         "accessDate": DATE, "accessMethod": "local_frozen_metadata",
         "locator": f"atlas-data/catalog/target-scope-t96.json, rows {', '.join(EXPECTED)}; exact English/Latin terms, source synonyms, hierarchy and semantic kind; SHA256 {sha_file(SCOPE_FILE)}",
         "term": None, "koModern": None, "koTraditional": None},
        {"id": ZA_SOURCE, "url": f"https://github.com/z-anatomy/Models-of-human-anatomy/tree/{REVISION}",
         "sourceLabel": "Pinned T98/T99 Z-Anatomy source catalogue and T100 evaluated scene metadata",
         "exactEdition": REVISION,
         "editionExposure": "Source commit and archive SHA are pinned; upstream FJ identifiers are unavailable in this catalogue.",
         "accessDate": DATE, "accessMethod": "local_frozen_metadata",
         "locator": f"source-catalog.json + source-metadata.json; source object/data name, sourceKey, parent, collections, label side and evaluated geometry hash; archive SHA256 {SOURCE_HASH}; catalogue SHA256 {sha_file(CATALOG_FILE)}",
         "term": None, "koModern": None, "koTraditional": None},
    ]
    obs_by_id = {x["id"]: x for x in observations["observations"]}
    obs_keys = {
        "metacarpalBones": "kmle-b04-metacarpal-bones", "metacarpalBone": "kmle-b04-metacarpal-bone",
        "phalangesHand": "kmle-b04-phalanges-hand", "phalanx": "kmle-b04-phalanx",
        "sesamoidHand": "kmle-b04-sesamoid-hand", "osCentrale": "kmle-b04-os-centrale",
        "bonyPelvis": "kmle-b04-bony-pelvis",
    }
    for key, observation_id in obs_keys.items():
        obs = obs_by_id[observation_id]
        rows.append({"id": KMLE_IDS[key], "observationId": obs["id"], "url": obs["url"],
                     "sourceLabel": "KMLE aggregate terminology search; opened HTML result tree",
                     "exactEdition": None,
                     "editionExposure": "The KMLE result page does not expose the underlying dictionary edition or revision.",
                     "accessDate": DATE, "accessMethod": obs["accessMethod"], "retrievalLayer": obs["retrievalLayer"],
                     "openedOriginalDictionaryRecord": False, "locator": obs["locator"],
                     "term": None, "koModern": None, "koTraditional": None})
    return rows


def member_code(obj_name: str):
    match = re.fullmatch(r"(Proximal|Middle|Distal) phalanx of (first|second|third|fourth|fifth) finger of hand\.([lr])", obj_name, re.I)
    if match:
        level, finger, side = match.groups()
        return f"{level.lower()}:{finger}:{'left' if side == 'l' else 'right'}"
    match = re.fullmatch(r"(First|Second|Third|Fourth|Fifth) metacarpal bone\.([lr])", obj_name, re.I)
    if match:
        bone, side = match.groups()
        return f"metacarpal:{bone.lower()}:{'left' if side == 'l' else 'right'}"
    return None


def main():
    validate_frozen_inputs()
    scope = read(SCOPE_FILE)
    catalog = read(CATALOG_FILE)
    metadata = read(META_FILE)
    remainder = read(REMAINDER_FILE)
    observations = read(OBS_FILE)
    frozen = read(HERE / "batch-scope.json")
    require(scope["revision"] == "T96-2026-09-28-semantic-freeze-v1" and len(scope["targets"]) == 542,
            "T96 revision/target denominator differs")
    require(observations["batchId"] == "T100-B04-hand-pelvis" and len(observations["observations"]) == 7,
            "B04 source query observations differ")
    require(remainder["targets"] == 542 and len(remainder["unresolved"]) == 182,
            "historical remainder snapshot changed")
    require(catalog["sourceHash"] == SOURCE_HASH and catalog["sourceRevision"] == REVISION and len(catalog["objects"]) == 960,
            "pinned source catalogue identity/count differs")
    raw_overlay = subprocess.check_output(["git", "show", f"{BASELINE['startingHead']}:{OVERLAY_REL}"], cwd=ROOT)
    require(sha_bytes(raw_overlay) == BASELINE["frozenInputSha256"][OVERLAY_REL], "B03 overlay bytes differ from B04 baseline")
    overlay = json.loads(raw_overlay)
    require(overlay["scope"] == {"targets": 542, "memberships": 563, "regions": 12}, "fixed T96 denominator changed")
    require(overlay["revision"] == "T100-source-taxonomy-local-display-v1-B03-lumbar-ribs-hand-groups", "prior overlay revision mismatch")

    targets = {x["id"]: x for x in scope["targets"]}
    source_objs = {x["name"]: x for x in catalog["objects"]}
    raw_objs = {x["name"]: x for x in metadata["objects"]}
    overlay_rows = {x["sourceName"]: x for x in overlay["objects"]}
    require(len(overlay_rows) == 960 and set(overlay_rows) == set(source_objs), "overlay/catalogue object inventory differs")
    require(all(x not in overlay_rows or not any(r.get("targetId") in EXPECTED for r in overlay_rows[x].get("targetRelationEvidence", [])) for x in overlay_rows),
            "B04 target relations already exist in B03 baseline")

    metacarpals = sorted([x for x in catalog["objects"] if re.fullmatch(r"(First|Second|Third|Fourth|Fifth) metacarpal bone\.[lr]", x["name"])], key=lambda x: x["name"])
    phalanx_re = re.compile(r"(Proximal|Middle|Distal) phalanx of (first|second|third|fourth|fifth) finger of hand\.([lr])", re.I)
    phalanges_all = sorted([x for x in catalog["objects"] if phalanx_re.fullmatch(x["name"])], key=lambda x: x["name"])
    require(len(metacarpals) == 10 and len(phalanges_all) == 28, "exact metacarpal/phalanx source object counts changed")

    valid_phalanges = []
    conflicts = []
    for obj in phalanges_all:
        match = phalanx_re.fullmatch(obj["name"])
        side = {"l": "left", "r": "right"}[match.group(3).lower()]
        if obj["name"] == "Distal phalanx of fifth finger of hand.l":
            conflicts.append({**source_ref(obj, raw_objs), "disposition": "excluded_from_target_relations",
                              "conflict": "object name ends .l and sourceLabelSide is left, but dataName names the .r object",
                              "action": "Do not auto-correct; keep unassigned pending source-owner or human review."})
            continue
        require(obj["sourceLabelSide"] == side, f"source suffix/side mismatch: {obj['name']}")
        require(obj["kind"] == "skeletal_surface" and obj["parent"] == "Bones of free part of upper limb.g",
                f"phalanx class/hierarchy mismatch: {obj['name']}")
        expected_limb = "Left upper limb" if side == "left" else "Right upper limb"
        require(expected_limb in obj["collections"], f"source collection does not corroborate exact side: {obj['name']}")
        valid_phalanges.append(obj)
    require(len(conflicts) == 1 and len(valid_phalanges) == 27, "expected one excluded phalanx identity conflict")

    for obj in metacarpals:
        suffix_side = {"l": "left", "r": "right"}[obj["name"][-1]]
        require(obj["sourceLabelSide"] == suffix_side, f"metacarpal suffix/side mismatch: {obj['name']}")
        require(obj["kind"] == "skeletal_surface" and obj["parent"] == "Bones of free part of upper limb.g",
                f"metacarpal class/hierarchy mismatch: {obj['name']}")
        expected_limb = "Left upper limb" if suffix_side == "left" else "Right upper limb"
        require(expected_limb in obj["collections"], f"metacarpal side collection missing: {obj['name']}")

    members = {target_id: [] for target_id in EXPECTED}
    for target_id, chosen in (("TA2:1264", metacarpals), ("TA2:1265", metacarpals),
                              ("TA2:1271", valid_phalanges), ("TA2:1272", valid_phalanges)):
        for obj in chosen:
            members[target_id].append({**source_ref(obj, raw_objs), "memberCode": member_code(obj["name"])})
    for target_id, level in (("TA2:1277", "Proximal"), ("TA2:1278", "Middle"), ("TA2:1279", "Distal")):
        for obj in valid_phalanges:
            if obj["name"].startswith(level + " phalanx"):
                members[target_id].append({**source_ref(obj, raw_objs), "memberCode": member_code(obj["name"])})
    require([len(members[x]) for x in EXPECTED] == [0, 10, 10, 27, 27, 10, 8, 9, 0, 0], "target member cardinalities differ")
    unique_member_keys = {m["sourceKey"] for rows in members.values() for m in rows}
    require(len(unique_member_keys) == 37, "expected 37 distinct source objects across 101 target relations")

    pelvis_candidates = []
    for obj in catalog["objects"]:
        if "Bony pelvis" in obj["collections"]:
            pelvis_candidates.append({**source_ref(obj, raw_objs), "disposition": "observed_collection_candidate_only",
                                      "reason": "TA2:1282 is frozen as supporting nomenclature, not a geometry target; no exact table-row join or complete group definition is available."})
    pelvis_candidates.sort(key=lambda x: x["sourceObjectName"])
    require([x["sourceObjectName"] for x in pelvis_candidates] == ["Coccyx", "Hip bone.l", "Hip bone.r", "Sacrum"],
            "observed Bony pelvis collection members differ")
    foot_sesamoids = []
    for obj in catalog["objects"]:
        if obj["name"].startswith("Sesamoid bones of foot."):
            foot_sesamoids.append({**source_ref(obj, raw_objs), "disposition": "explicitly_excluded_wrong_region",
                                   "reason": "Foot sesamoid object cannot establish the hand sesamoid target or member set."})
    foot_sesamoids.sort(key=lambda x: x["sourceObjectName"])
    require([x["sourceObjectName"] for x in foot_sesamoids] == ["Sesamoid bones of foot.l", "Sesamoid bones of foot.r"],
            "expected foot-only sesamoid comparator objects missing")

    source_evidence = evidence_sources(observations, scope, catalog)
    evidence_by_id = {x["id"]: x for x in source_evidence}
    require(len(evidence_by_id) == len(source_evidence), "duplicate B04 evidence source id")
    old_evidence_ids = {x["id"] for x in overlay.get("evidenceSources", [])}
    require(not (old_evidence_ids & set(evidence_by_id)), "B04 provenance IDs collide with existing overlay")
    old_term_ids = {x["targetId"] for x in overlay.get("targetTerminologyEvidence", [])}
    require(not (old_term_ids & set(EXPECTED)), "B04 target evidence already exists in base overlay")
    overlay["evidenceSources"] = overlay.get("evidenceSources", []) + source_evidence

    definitions = {
        "TA2:1263": {
            "modern": None, "traditional": None, "modernSource": KMLE_IDS["osCentrale"], "traditionalSource": KMLE_IDS["osCentrale"],
            "modernMissing": "No exact current Korean KAS term was observed in the opened query. The older generic candidate 중심골 was a similar/index result only and is not promoted to this target field.",
            "traditionalMissing": "No exact target-specific traditional term was exposed. The older similar result 중심골 is retained only as an unapplied candidate.",
            "classification": {"meaningType": "optional inconstant bone variant", "groupPartVariant": "os centrale is an optional accessory carpal variant; it is distinct from os centrale tarsi.", "laterality": "not specified; do not expand to sides"},
            "surface": {"status": "exact_surface_missing_optional_variant", "exactSourceObject": None, "exactMemberCrosswalkAdded": False,
                        "note": "No exact os centrale evaluated object exists in the frozen 960-object inventory. Foot os centrale tarsi is excluded."},
            "candidates": [{"value": "중심골", "sourceId": KMLE_IDS["osCentrale"], "locator": "Opened KMLE aggregate query; older 대한의협 3 similar-result node 54.", "status": "unapplied_similar_index_candidate", "reason": "Not an exact current target row."}],
        },
        "TA2:1264": {
            "modern": "손허리뼈(첫째-다섯째)", "traditional": "중수(장)골", "modernSource": KMLE_IDS["metacarpalBones"], "traditionalSource": KMLE_IDS["metacarpalBones"],
            "modernLocator": "Opened KMLE aggregate query, current 대한해부학회 exact-result nodes 119-120: Metacarpal bones(first-fifth) → 손허리뼈(첫째-다섯째).",
            "traditionalLocator": "Opened KMLE aggregate query, same exact-result nodes 119-120: old term 중수(장)골; no Hanja glyphs copied.",
            "classification": {"meaningType": "five-bone series", "groupPartVariant": "first through fifth metacarpal bones; ten exact evaluated objects, five per source side.", "laterality": "per-member side only from exact .l/.r object suffix corroborated by sourceLabelSide and upper-limb collection"},
            "surface": {"status": "ten_exact_named_class_member_surfaces", "relationKind": "class_member", "sourceMembers": members["TA2:1264"], "exactAggregateSourceObject": None,
                        "note": "Five numbered bones on each source side. Left objects can also carry the inconsistent Right hand collection; that collection is not used to assign side."},
            "candidates": [],
        },
        "TA2:1265": {
            "modern": "손허리뼈", "traditional": "중수골", "modernSource": KMLE_IDS["metacarpalBone"], "traditionalSource": KMLE_IDS["metacarpalBone"],
            "modernLocator": "Opened KMLE aggregate query, current 대한의협 exact-result node 109: metacarpal bone → 손허리뼈.",
            "traditionalLocator": "Opened KMLE aggregate query, current 대한의협 node 109 lists 중수골; older exact rows 196/284 also report 손허리뼈/중수골. Underlying dictionary edition is not exposed.",
            "classification": {"meaningType": "individual bone class", "groupPartVariant": "the generic metacarpal class has five named ray members per side; no single aggregate mesh is claimed.", "laterality": "source members are individually paired; target itself has no explicit side"},
            "surface": {"status": "ten_exact_named_class_member_surfaces", "relationKind": "class_member", "sourceMembers": members["TA2:1265"], "exactAggregateSourceObject": None,
                        "note": "This generic class and TA2:1264 series reference the same ten source nodes; this is one set of source geometry, not duplicated assets."},
            "candidates": [],
        },
        "TA2:1271": {
            "modern": None, "traditional": None, "modernSource": KMLE_IDS["phalangesHand"], "traditionalSource": KMLE_IDS["phalangesHand"],
            "modernMissing": "No exact current Korean hand-specific group row was observed. The fuzzy generic candidate 손가락뼈 remains unapplied.",
            "traditionalMissing": "No exact hand-specific traditional group row was observed; no name is composed from generic phalanx terms.",
            "classification": {"meaningType": "hand phalanx series", "groupPartVariant": "27 exact source member rows are eligible; the left distal fifth-finger object is excluded because dataName names the right object.", "laterality": "side follows exact member suffix/sourceLabelSide; inconsistent Right hand collection on left objects is ignored"},
            "surface": {"status": "27_exact_named_members_one_identity_conflict_excluded", "relationKind": "class_member", "sourceMembers": members["TA2:1271"], "exactAggregateSourceObject": None,
                        "excludedMembers": conflicts, "note": "Source snapshot has 28 hand-phalanx candidates. Twenty-seven are related; one .l object/dataName conflict is held unassigned."},
            "candidates": [{"value": "손가락뼈", "sourceId": KMLE_IDS["phalangesHand"], "locator": "Opened KMLE aggregate query, older 대한의협 2/3 fuzzy result AX nodes 117/164.", "status": "unapplied_fuzzy_index_candidate", "reason": "Generic phalanges row, not an exact opened hand-specific source record."}],
        },
        "TA2:1272": {
            "modern": None, "traditional": None, "modernSource": KMLE_IDS["phalanx"], "traditionalSource": KMLE_IDS["phalanx"],
            "modernMissing": "Opened query provides generic phalanx headwords but no exact hand-specific term; retain all as candidates without composing a hand qualifier.",
            "traditionalMissing": "Older generic 지골 rows do not establish this hand-specific target field.",
            "classification": {"meaningType": "individual bone class", "groupPartVariant": "all three levels and five fingers are source children; 27 eligible evaluated members after one identity conflict exclusion.", "laterality": "per-member side only; target itself is not side-expanded"},
            "surface": {"status": "27_exact_named_members_one_identity_conflict_excluded", "relationKind": "class_member", "sourceMembers": members["TA2:1272"], "exactAggregateSourceObject": None,
                        "excludedMembers": conflicts, "note": "The source exact names establish hand phalanx membership; Korean exact target naming remains missing."},
            "candidates": [{"value": "가락뼈", "sourceId": KMLE_IDS["phalanx"], "locator": "Opened KMLE aggregate query, current 대한의협 exact node 35.", "status": "unapplied_generic_index_candidate", "reason": "Generic phalanx headword; not hand-specific."},
                           {"value": "마디뼈", "sourceId": KMLE_IDS["phalanx"], "locator": "Opened KMLE aggregate query, current 대한의협 exact node 35.", "status": "unapplied_generic_index_candidate", "reason": "Generic phalanx headword; not hand-specific."},
                           {"value": "손발가락뼈", "sourceId": KMLE_IDS["phalanx"], "locator": "Opened KMLE aggregate query, required terminology glossary exact node 61.", "status": "unapplied_generic_index_candidate", "reason": "Glossary term spans hand and foot; not an exact hand-only row."},
                           {"value": "지골", "sourceId": KMLE_IDS["phalanx"], "locator": "Opened KMLE aggregate query, older exact result nodes 108-110 and 139-141.", "status": "unapplied_generic_index_candidate", "reason": "Older generic finger/toe scope, without hand qualifier."}],
        },
        "TA2:1277": {
            "modern": None, "traditional": None, "modernSource": KMLE_IDS["phalanx"], "traditionalSource": KMLE_IDS["phalanx"],
            "modernMissing": "Generic first/proximal phalanx terminology is not an exact hand-specific target label; do not compose a new phrase.",
            "traditionalMissing": "Generic older proximal-phalanx wording is not an exact hand-specific term row.",
            "classification": {"meaningType": "proximal phalanx part class", "groupPartVariant": "ten exact named members (five fingers per side); each is a constituent of the hand series.", "laterality": "per-member source suffix/label"},
            "surface": {"status": "ten_exact_named_class_member_surfaces", "relationKind": "class_member", "sourceMembers": members["TA2:1277"], "exactAggregateSourceObject": None,
                        "note": "All ten source objects have proximal level in exact object names and parent hand-bone hierarchy."},
            "candidates": [{"value": "첫마디뼈", "sourceId": KMLE_IDS["phalangesHand"], "locator": "Opened aggregate result, generic current level-term row.", "status": "unapplied_generic_index_candidate", "reason": "The hand qualifier is absent from the source row."},
                           {"value": "기절골", "sourceId": KMLE_IDS["phalangesHand"], "locator": "Opened aggregate result, generic older level-term row.", "status": "unapplied_generic_index_candidate", "reason": "The hand qualifier and exact target headword are absent."}],
        },
        "TA2:1278": {
            "modern": None, "traditional": None, "modernSource": KMLE_IDS["phalangesHand"], "traditionalSource": KMLE_IDS["phalangesHand"],
            "modernMissing": "Generic middle-phalanx terminology is not an exact hand-specific target label; do not compose a new phrase.",
            "traditionalMissing": "Generic older middle-phalanx wording is not an exact hand-specific term row.",
            "classification": {"meaningType": "middle phalanx part class", "groupPartVariant": "eight exact named members; the first finger/thumb has no middle-phalanx objects in the source naming pattern.", "laterality": "four eligible members per source side; one side per exact suffix/label"},
            "surface": {"status": "eight_exact_named_class_member_surfaces", "relationKind": "class_member", "sourceMembers": members["TA2:1278"], "exactAggregateSourceObject": None,
                        "note": "No thumb middle-phalanx object is invented; eight exact named source objects are observed."},
            "candidates": [{"value": "중간마디뼈", "sourceId": KMLE_IDS["phalangesHand"], "locator": "Opened aggregate result, generic current level-term row.", "status": "unapplied_generic_index_candidate", "reason": "The hand qualifier is absent from the source row."},
                           {"value": "중절골", "sourceId": KMLE_IDS["phalangesHand"], "locator": "Opened aggregate result, generic older level-term row.", "status": "unapplied_generic_index_candidate", "reason": "The hand qualifier and exact target headword are absent."}],
        },
        "TA2:1279": {
            "modern": None, "traditional": None, "modernSource": KMLE_IDS["phalangesHand"], "traditionalSource": KMLE_IDS["phalangesHand"],
            "modernMissing": "Generic distal-phalanx terminology is not an exact hand-specific target label; do not compose a new phrase.",
            "traditionalMissing": "Generic older distal-phalanx wording is not an exact hand-specific term row.",
            "classification": {"meaningType": "distal phalanx part class", "groupPartVariant": "nine eligible named members; the left fifth-finger row is excluded due its object/data name side conflict.", "laterality": "per-member exact suffix/label except held conflict"},
            "surface": {"status": "nine_exact_members_one_identity_conflict_excluded", "relationKind": "class_member", "sourceMembers": members["TA2:1279"], "exactAggregateSourceObject": None,
                        "excludedMembers": conflicts, "note": "Ten candidate objects exist; one .l object names the .r data object, so no relation is emitted for it."},
            "candidates": [{"value": "끝마디뼈", "sourceId": KMLE_IDS["phalangesHand"], "locator": "Opened aggregate result, generic current level-term row.", "status": "unapplied_generic_index_candidate", "reason": "The hand qualifier is absent from the source row."},
                           {"value": "말절골", "sourceId": KMLE_IDS["phalangesHand"], "locator": "Opened aggregate result, generic older level-term row.", "status": "unapplied_generic_index_candidate", "reason": "The hand qualifier and exact target headword are absent."}],
        },
        "TA2:1281": {
            "modern": None, "traditional": None, "modernSource": KMLE_IDS["sesamoidHand"], "traditionalSource": KMLE_IDS["sesamoidHand"],
            "modernMissing": "No exact hand sesamoid group term was observed. Generic 종자뼈 is retained only as an unapplied candidate.",
            "traditionalMissing": "No exact hand-specific traditional group label was observed. Generic old term 종자골 is not applied to this target.",
            "classification": {"meaningType": "hand sesamoid bone group", "groupPartVariant": "target source representation and member set remain undetermined; do not substitute foot sesamoids.", "laterality": "not specified by target; no side expansion"},
            "surface": {"status": "hand_group_surface_missing", "exactSourceObject": None, "exactMemberCrosswalkAdded": False,
                        "excludedWrongRegionObjects": foot_sesamoids, "note": "Only foot sesamoid meshes occur in this inventory; they are explicitly excluded."},
            "candidates": [{"value": "종자뼈", "sourceId": KMLE_IDS["sesamoidHand"], "locator": "Opened aggregate result, generic current exact/similar row.", "status": "unapplied_generic_index_candidate", "reason": "Generic sesamoid term does not establish hand-specific target."},
                           {"value": "종자골", "sourceId": KMLE_IDS["sesamoidHand"], "locator": "Opened aggregate result, generic old-term column.", "status": "unapplied_generic_index_candidate", "reason": "Generic old term does not establish hand-specific target."}],
        },
        "TA2:1282": {
            "modern": None, "traditional": None, "modernSource": KMLE_IDS["bonyPelvis"], "traditionalSource": KMLE_IDS["bonyPelvis"],
            "modernMissing": "No exact Korean headword for bony pelvis was observed. The generic pelvis term 골반 is not promoted by adding a modifier.",
            "traditionalMissing": "No exact traditional Korean label for bony pelvis was observed; no compound is inferred.",
            "classification": {"meaningType": "supporting nomenclature group, not a frozen geometry target", "groupPartVariant": "four exact collection members are observations only; group completeness and direct target mapping are not established.", "laterality": "the two hip objects carry source side; sacrum and coccyx are unpaired; this does not define complete target cardinality"},
            "surface": {"status": "candidate_collection_members_observed_not_crosswalked", "exactTargetRelationAdded": False,
                        "observedCollectionMembers": pelvis_candidates,
                        "note": "Frozen T96 row is supporting_nomenclature_not_geometry_target with no exact table-row join; do not claim a complete bony-pelvis geometry group."},
            "candidates": [{"value": "골반", "sourceId": KMLE_IDS["bonyPelvis"], "locator": "Opened aggregate result, similar current KAS nodes 225-226 and required glossary node 72 for generic Pelvis.", "status": "unapplied_generic_index_candidate", "reason": "Generic pelvis is not an exact bony-pelvis label."}],
        },
    }

    terms = []
    for target_id in EXPECTED:
        target, definition = targets[target_id], definitions[target_id]
        english, latin = target["term"]["english"], target["term"]["latin"]
        ko_modern, ko_traditional = definition["modern"], definition["traditional"]
        modern_key = "modernLocator" if ko_modern is not None else "modernMissing"
        traditional_key = "traditionalLocator" if ko_traditional is not None else "traditionalMissing"
        field_evidence = {
            "koModern": field(ko_modern, [definition["modernSource"]], definition.get(modern_key) if ko_modern is not None else None,
                              definition["modernMissing"] if ko_modern is None else None),
            "koTraditional": field(ko_traditional, [definition["traditionalSource"]], definition.get(traditional_key) if ko_traditional is not None else None,
                                   definition["traditionalMissing"] if ko_traditional is None else None),
            "en": field(english, [TA2_SOURCE], f"Frozen T96 {target_id} exact English: {english}"),
            "latin": field(latin, [TA2_SOURCE], f"Frozen T96 {target_id} exact Latin: {latin}"),
            "sourceSynonyms": [{"language": lang, "value": val, "sourceIds": [TA2_SOURCE],
                                "locator": f"Frozen T96 {target_id} exact source synonym ({lang}): {val}", "status": "evidence_backed"}
                               for lang, values in target["term"].get("sourceSynonyms", {}).items() for val in values],
            "hanja": {"value": None, "sourceIds": [], "locator": None, "status": "not_collected",
                      "missingReason": "Actual Hanja glyphs are outside this batch's collection policy; Korean terms are stored in Hangul only."},
        }
        term = {
            "targetId": target_id, "targetTermSourceIds": [TA2_SOURCE], "english": english, "latin": latin,
            "sourceSynonyms": target["term"].get("sourceSynonyms", {}), "relatedTerms": target["sourceFlags"].get("relatedTerms", []),
            "semanticKind": target["semanticKind"], "primaryOwner": target["primaryOwner"], "regionIds": target["regionIds"],
            "sourceParentId": target["sourceParentId"], "sourceAncestryIds": target["sourceAncestryIds"], "sourceFlags": target["sourceFlags"],
            "classification": definition["classification"],
            "names": {"koModern": ko_modern, "koTraditional": ko_traditional, "en": english},
            "fieldEvidence": field_evidence, "unappliedTermCandidates": definition["candidates"],
            "existingSurface": definition["surface"],
            "observedSurfacesNotBound": definition["surface"].get("observedCollectionMembers", definition["surface"].get("excludedMembers", definition["surface"].get("excludedWrongRegionObjects", []))),
            "learnerBindingCreated": False, "canonicalHaConceptId": None,
            "sourceOnly": True, "humanReview": "not_performed", "publicRedistribution": "held", "newGeometryCreated": False,
        }
        terms.append(term)

    relation_records = []
    for target_id in EXPECTED:
        target = targets[target_id]
        for member in members[target_id]:
            obj = source_objs[member["sourceObjectName"]]
            row = overlay_rows[obj["name"]]
            side = member["sourceSide"]
            relation = {
                "targetId": target_id, "targetEnglish": target["term"]["english"], "targetLatin": target["term"]["latin"],
                "targetSemanticKind": target["semanticKind"], "targetPrimaryOwner": target["primaryOwner"], "targetRegionIds": target["regionIds"],
                "targetLaterality": target["sourceCardinality"]["lateralityState"], "sourceKey": obj["sourceKey"],
                "sourceObjectName": obj["name"], "sourceDataName": obj["dataName"], "sourceParent": obj["parent"],
                "sourceCollections": obj["collections"], "sourceSide": side, "evaluatedGeometrySha256": obj["evaluatedGeometrySha256"],
                "sourceHash": SOURCE_HASH, "sourceRevision": REVISION,
                "matchBasis": "Frozen T96 class/member semantics plus exact evaluated source object part/level/ray name, hand skeletal parent and matching source hierarchy; side uses exact .l/.r suffix and sourceLabelSide, with matching limb collection corroboration. No upstream FJ ID or HA binding is asserted.",
                "directObjectNameMatch": False, "ancestorNameAloneUsed": False, "upstreamFjOrTa2IdClaim": False,
                "canonicalHaBindingCreated": False, "humanReview": "not_performed", "relationKind": "class_member",
                "matchedTargetSynonym": None, "sourceSegmentCode": None, "memberCode": member["memberCode"],
                "matchEvidenceSourceIds": [ZA_SOURCE, TA2_SOURCE],
            }
            require(row["sourceOnly"] and row["haConceptId"] is None, f"source row unexpectedly learner-bound: {obj['name']}")
            require(target_id not in row.get("targetIds", []), f"duplicate B04 source target id: {obj['name']} {target_id}")
            row.setdefault("targetIds", []).append(target_id)
            relation_list = row.setdefault("targetRelationEvidence", [])
            require(not any(x["targetId"] == target_id for x in relation_list), f"duplicate B04 relation: {obj['name']} {target_id}")
            relation_list.append(relation)
            relation_records.append({**relation, "sourceMember": member})

    overlay["targetTerminologyEvidence"] = overlay.get("targetTerminologyEvidence", []) + terms
    overlay["revision"] = "T100-source-taxonomy-local-display-v1-B04-hand-pelvis"
    write(OVERLAY_FILE, overlay)

    counts = {target_id: len(members[target_id]) for target_id in EXPECTED}
    exact_inventory = {
        "metacarpals": [{**source_ref(x, raw_objs), "relationTargets": ["TA2:1264", "TA2:1265"], "sourceSideBasis": "object .l/.r plus sourceLabelSide and upper-limb collection"} for x in metacarpals],
        "handPhalanges": [{**source_ref(x, raw_objs), "relationTargets": [t for t in ("TA2:1271", "TA2:1272", "TA2:1277", "TA2:1278", "TA2:1279") if any(m["sourceKey"] == x["sourceKey"] for m in members[t])], "sourceSideBasis": "object .l/.r plus sourceLabelSide and upper-limb collection"} for x in phalanges_all],
        "excludedPhalanxIdentityConflicts": conflicts,
        "bonyPelvisCollectionCandidates": pelvis_candidates,
        "wrongRegionSesamoidObjects": foot_sesamoids,
        "unmatchedExactTargets": ["TA2:1263", "TA2:1281", "TA2:1282"],
    }
    ledger = {
        "schemaVersion": 1, "batchId": "T100-B04-hand-pelvis", "capturedOn": DATE,
        "scope": {"targetCount": 10, "requestedTargetIds": EXPECTED, "taskTargetDenominator": 542,
                  "taskRegionMembershipDenominator": 563, "regions": 12, "targetScopeRevision": scope["revision"],
                  "targetScopeSha256": sha_file(SCOPE_FILE), "zaSourceRevision": REVISION, "zaSourceFileSha256": SOURCE_HASH,
                  "historicalRemainingCountAtBatchStart": 182, "historicalRemainingTargetInventorySha256": sha_file(REMAINDER_FILE),
                  "sourceObjectCatalogueSha256": sha_file(CATALOG_FILE), "sourceMetadataSha256": sha_file(META_FILE),
                  "compiledManifestSha256": sha_file(COMPILED_FILE), "startingHead": BASELINE["startingHead"],
                  "frozenOffsets": [20, 30]},
        "sourceEvidence": source_evidence,
        "fieldSourceSeparation": {"fipat": "T96 frozen local metadata, exact Terminologia Anatomica 2nd edition vocabulary 2.07; not freshly reopened in this batch.",
                                  "kmle": "Opened aggregate HTML query pages. Exact/fuzzy labels are search-result/index outputs; underlying dictionary edition is not exposed and no direct original dictionary records were opened.",
                                  "za": "Pinned local T98/T99 source catalogue and evaluated geometry metadata; source archive/hash exact, but no upstream FJ identity is claimed.",
                                  "humanAnatomyReview": "not_performed; source/term inspection is not human anatomy approval."},
        "targets": terms, "exactSourceNameInventory": exact_inventory, "crosswalkRelations": relation_records,
        "memberCountsByTarget": counts,
        "nonClaims": ["not whole-body completion", "not a new or upstream FJ identity claim", "not canonical HA learner binding or search alias",
                      "not new geometry", "not rights promotion", "not human anatomy review", "not proof of anatomical absence for missing surfaces",
                      "candidate bony-pelvis collection membership is not a target geometry crosswalk", "one conflicted fifth distal phalanx row is deliberately unassigned"],
    }
    write(LEDGER_FILE, ledger)
    corr = {
        "schemaVersion": 1, "batchId": ledger["batchId"], "targetCount": 10, "exactOverlayRelations": len(relation_records),
        "sourceObjectMembers": len(unique_member_keys), "memberCountsByTarget": counts,
        "targetsWithExactRelations": [x for x in EXPECTED if counts[x]], "targetsWithoutExactRelations": [x for x in EXPECTED if not counts[x]],
        "targetsWithPartialOrHeldCoverage": ["TA2:1271", "TA2:1272", "TA2:1279", "TA2:1281", "TA2:1282"],
        "unresolvedGeometryAndIdentityRemain": True,
        "candidateOnlyCollectionMembersForTA2_1282": [x["sourceObjectName"] for x in pelvis_candidates],
        "excludedIdentityConflictCount": len(conflicts),
        "inputDenominators": {"targets": 542, "memberships": 563, "regions": 12},
        "historicalRemainingAtBatchStart": 182, "batchDispositionCount": 10, "historicalRemainderAfterB04Disposition": 152,
        "preservedCounts": {"sourceObjects": len(overlay["objects"]),
                            "locallyDisplayable": sum(bool(x.get("localDisplayEligible")) for x in overlay["objects"]),
                            "haBoundRows": sum(bool(x.get("haConceptId")) for x in overlay["objects"]),
                            "publicRedistribution": "held", "humanReview": "not_performed"},
        "overlaySha256": sha_file(OVERLAY_FILE),
    }
    write(CORR_FILE, corr)
    print(json.dumps({"batchId": ledger["batchId"], "targets": 10, "exactRelations": len(relation_records),
                      "uniqueSourceObjects": len(unique_member_keys), "missingDirectTargets": corr["targetsWithoutExactRelations"],
                      "overlaySha256": corr["overlaySha256"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
