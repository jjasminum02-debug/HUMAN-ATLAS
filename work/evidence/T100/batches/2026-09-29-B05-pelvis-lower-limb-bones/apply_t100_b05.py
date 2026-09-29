#!/usr/bin/env python3
"""Rebuild only the frozen T100-B05 terminology and member-evidence overlay."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
BASELINE = json.loads((HERE / "start-baseline.json").read_text())
SCOPE_PATH = ROOT / "atlas-data/catalog/target-scope-t96.json"
CATALOG_PATH = ROOT / "work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json"
META_PATH = ROOT / "work/evidence/T100/resolution-2026-09-29/source-metadata.json"
REMAINDER_PATH = ROOT / "work/evidence/T100/resolution-2026-09-29/remaining-targets.json"
OVERLAY_PATH = ROOT / "atlas-data/overlays/za-local-integration.json"
OBS_PATH = HERE / "source-query-observations.json"
SOURCE_REVISION = "c7010a903b75a2fd24a13b1c2c4c3546a9223780"
SOURCE_HASH = "9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd"
TA2_SOURCE = "fipat-ta2-t100-b05-frozen-target-terms"
ZA_SOURCE = "za-t99-t100-b05-frozen-source-objects"
EXPECTED = ["TA2:1317", "TA2:1339", "TA2:1346", "TA2:1389", "TA2:1493",
            "TA2:1494", "TA2:1496", "TA2:1505", "TA2:1510", "TA2:1511"]
SOURCE_IDS = {
    "ilium": "kmle-t100-b05-ilium-opened", "ischium": "kmle-t100-b05-ischium-opened",
    "pubis": "kmle-t100-b05-pubis-opened", "metatarsal": "kmle-t100-b05-metatarsal-search-index",
    "phalanges": "kmle-t100-b05-phalanges-opened", "osTrigonum": "kmle-t100-b05-os-trigonum-search-index",
    "sesamoid": "kmle-t100-b05-sesamoid-generic-search-index", "pelvis": "asan-t100-b05-pelvis-opened",
    "knee": "imaios-t100-b05-knee-sesamoids-opened", "accessoryFoot": "koa-t100-b05-accessory-tarsal-paper-opened",
}


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def read(path: Path):
    return json.loads(path.read_text())


def write(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def need(condition: bool, message: str):
    if not condition:
        raise SystemExit(message)


def verify_frozen_inputs():
    frozen = read(HERE / "batch-scope.json")
    need(frozen["predecessorGate"]["result"] == "pass", "B04 predecessor gate failed")
    need(frozen["predecessorGate"]["commit"] == BASELINE["startingHead"], "B05 start HEAD is not the passing B04 commit")
    need(subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == BASELINE["startingHead"],
         "HEAD moved after B05 scope freeze")
    need(frozen["status"] == "frozen_before_investigation" and frozen["targetIds"] == EXPECTED, "B05 frozen target list differs")
    need(sha_file(REMAINDER_PATH) == frozen["frozenRemainder"]["sha256"], "T100 historical remainder source changed")
    for rel, digest in BASELINE["frozenInputs"].items():
        if rel != "atlas-data/overlays/za-local-integration.json":
            need(sha_file(ROOT / rel) == digest, f"frozen input changed: {rel}")
    prior = subprocess.check_output(["git", "show", f"{BASELINE['startingHead']}:atlas-data/overlays/za-local-integration.json"], cwd=ROOT)
    need(sha_bytes(prior) == BASELINE["frozenInputs"]["atlas-data/overlays/za-local-integration.json"], "B04 overlay baseline hash differs")


def field(value, source_ids, locator=None, missing_reason=None):
    return {"value": value, "sourceIds": source_ids, "locator": locator if value is not None else None,
            "status": "evidence_backed" if value is not None else "missing",
            "missingReason": missing_reason if value is None else None}


def source_rows(observations, scope, catalog):
    observed = {item["id"]: item for item in observations["observations"]}
    out = [
        {"id": TA2_SOURCE, "url": "https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf",
         "sourceLabel": "FIPAT Terminologia Anatomica, 2nd edition, online vocabulary 2.07; frozen T96 target rows",
         "exactEdition": "Terminologia Anatomica, 2nd edition, vocabulary 2.07",
         "editionExposure": "Exact version and hash are recorded in the T96 frozen source-scope metadata; not freshly reopened during B05.",
         "accessDate": "2026-09-29", "accessMethod": "local_frozen_metadata",
         "locator": f"atlas-data/catalog/target-scope-t96.json rows {', '.join(EXPECTED)}; target-scope SHA256 {sha_file(SCOPE_PATH)}"},
        {"id": ZA_SOURCE, "url": "https://github.com/z-anatomy/Models-of-human-anatomy/tree/" + SOURCE_REVISION,
         "sourceLabel": "Pinned T98/T99 source catalogue and evaluated Z-Anatomy metadata",
         "exactEdition": SOURCE_REVISION,
         "editionExposure": "Commit and source archive hash are frozen in prior evidence; upstream FJ IDs are not available in this catalogue.",
         "accessDate": "2026-09-29", "accessMethod": "local_frozen_metadata",
         "locator": f"T98 source-catalog.json and T100 source-metadata.json; 960 source rows; archive SHA256 {SOURCE_HASH}; catalog SHA256 {sha_file(CATALOG_PATH)}"},
    ]
    for key, source_id in SOURCE_IDS.items():
        obs = observed[source_id]
        out.append({"id": source_id, "url": obs["url"], "sourceLabel": obs["retrievalLayer"],
                    "exactEdition": obs.get("exactEdition"), "editionExposure": obs["editionExposure"],
                    "accessDate": obs["accessDate"], "accessMethod": obs["accessMethod"],
                    "retrievalLayer": obs["retrievalLayer"], "openedOriginalDictionaryRecord": obs.get("openedOriginalDictionaryRecord", False),
                    "openedOriginalSourcePage": bool(obs.get("openedOriginalSourcePage", False)),
                    "locator": obs["locator"]})
    need(len({x["id"] for x in out}) == len(out), "duplicate provenance source id")
    return out


def source_ref(obj, metadata_by_name):
    raw = metadata_by_name.get(obj["name"])
    need(raw is not None and (raw["parent"], raw["collections"]) == (obj["parent"], obj["collections"]),
         "raw metadata hierarchy mismatch: " + obj["name"])
    loc = obj["sourceLocator"]
    need(loc["archivePath"] == "Z-Anatomy/Startup.blend" and loc["sourceFileSha256"] == SOURCE_HASH, "source locator/hash mismatch")
    need(re.fullmatch(r"ZA-c7010a9-[a-f0-9]{24}", obj["sourceKey"]) is not None, "source key contract mismatch")
    need(re.fullmatch(r"[a-f0-9]{64}", obj["evaluatedGeometrySha256"]) is not None, "evaluated geometry hash missing")
    return {"sourceKey": obj["sourceKey"], "sourceObjectName": obj["name"], "sourceDataName": obj["dataName"],
            "sourceParent": obj["parent"], "sourceCollections": obj["collections"], "sourceSide": obj["sourceLabelSide"],
            "evaluatedGeometrySha256": obj["evaluatedGeometrySha256"], "sourceHash": SOURCE_HASH,
            "sourceRevision": SOURCE_REVISION, "sourceLocator": loc}


def member_code(name):
    met = re.fullmatch(r"(First|Second|Third|Fourth|Fifth) metatarsal bone\.([lr])", name)
    if met:
        return f"metatarsal:{met[1].lower()}:{'left' if met[2] == 'l' else 'right'}"
    toe = re.fullmatch(r"(Proximal|Middle|Distal) phalanx of (first|second|third|fourth|fifth) finger of foot\.([lr])", name)
    if toe:
        return f"{toe[1].lower()}:{toe[2]}:{'left' if toe[3] == 'l' else 'right'}"
    patella = re.fullmatch(r"Patella\.([lr])", name)
    if patella:
        return f"sesamoid:patella:{'left' if patella[1] == 'l' else 'right'}"
    return None


def main():
    verify_frozen_inputs()
    frozen = read(HERE / "batch-scope.json")
    observations = read(OBS_PATH)
    scope = read(SCOPE_PATH)
    catalog = read(CATALOG_PATH)
    raw_metadata = read(META_PATH)
    overlay_raw = subprocess.check_output(["git", "show", f"{BASELINE['startingHead']}:atlas-data/overlays/za-local-integration.json"], cwd=ROOT)
    overlay = json.loads(overlay_raw)
    need(observations["batchId"] == frozen["batchId"] and observations["hanjaCopied"] is False, "B05 observation file differs")
    need(scope["revision"] == "T96-2026-09-28-semantic-freeze-v1" and len(scope["targets"]) == 542, "T96 scope changed")
    need(catalog["sourceRevision"] == SOURCE_REVISION and catalog["sourceHash"] == SOURCE_HASH and len(catalog["objects"]) == 960, "pinned ZA inventory changed")
    need(overlay["scope"] == {"targets": 542, "memberships": 563, "regions": 12} and len(overlay["objects"]) == 960, "B04 overlay denominator or inventory differs")
    need(overlay["revision"] == "T100-source-taxonomy-local-display-v1-B04-hand-pelvis", "B04 overlay revision mismatch")
    targets = {row["id"]: row for row in scope["targets"]}
    frozen_targets = {row["targetId"]: row for row in frozen["targets"]}
    need(set(frozen_targets) == set(EXPECTED), "B05 frozen target set differs")
    need([row["targetId"] for row in frozen["targets"]] == EXPECTED, "B05 target order differs")
    need(scope["targets"] and all(targets[x]["term"]["english"] == frozen_targets[x]["english"] for x in EXPECTED), "T96 exact terms changed")
    source_by_name = {row["name"]: row for row in catalog["objects"]}
    raw_by_name = {row["name"]: row for row in raw_metadata["objects"]}
    overlay_by_name = {row["sourceName"]: row for row in overlay["objects"]}
    need(set(source_by_name) == set(overlay_by_name) and len(raw_by_name) == len(raw_metadata["objects"]), "source inventory join mismatch")
    base_terms = {x["targetId"] for x in overlay.get("targetTerminologyEvidence", [])}
    base_evidence = {x["id"] for x in overlay.get("evidenceSources", [])}
    need(not (set(EXPECTED) & base_terms), "B05 terms already exist in B04 baseline")

    objects = catalog["objects"]
    metatarsals = sorted([x for x in objects if re.fullmatch(r"(?:First|Second|Third|Fourth|Fifth) metatarsal bone\.[lr]", x["name"])], key=lambda x: x["name"])
    phalanges = sorted([x for x in objects if re.fullmatch(r"(?:Proximal|Middle|Distal) phalanx of (?:first|second|third|fourth|fifth) finger of foot\.[lr]", x["name"])], key=lambda x: x["name"])
    proximal = [x for x in phalanges if x["name"].startswith("Proximal phalanx")]
    middle = [x for x in phalanges if x["name"].startswith("Middle phalanx")]
    patellae = sorted([x for x in objects if re.fullmatch(r"Patella\.[lr]", x["name"])], key=lambda x: x["name"])
    need((len(metatarsals), len(phalanges), len(proximal), len(middle), len(patellae)) == (10, 28, 10, 8, 2), "B05 exact source member counts changed")
    members = {target_id: [] for target_id in EXPECTED}
    for target_id, chosen in (("TA2:1389", patellae), ("TA2:1496", metatarsals),
                              ("TA2:1505", phalanges), ("TA2:1510", proximal), ("TA2:1511", middle)):
        for obj in chosen:
            ref = source_ref(obj, raw_by_name)
            side_suffix = re.search(r"\.([lr])$", obj["name"])[1]
            expected_side = "left" if side_suffix == "l" else "right"
            need(obj["sourceLabelSide"] == expected_side, "name/side label conflict: " + obj["name"])
            if "metatarsal" in obj["name"].lower() or "phalanx" in obj["name"].lower():
                expected_parent = "Metatarsal bones.g" if "metatarsal" in obj["name"].lower() else "Phalanges of foot.g"
                expected_collection = "Left lower limb" if expected_side == "left" else "Right lower limb"
                need(obj["parent"] == expected_parent and expected_collection in obj["collections"], "foot member parent/side collection mismatch: " + obj["name"])
            else:
                expected_collection = "Left lower limb" if expected_side == "left" else "Right lower limb"
                need(obj["parent"] == "Bones of free part of lower limb.g" and expected_collection in obj["collections"], "patella parent/side collection mismatch")
            code = member_code(obj["name"])
            need(code is not None, "unrecognized member code")
            members[target_id].append({**ref, "memberCode": code})
    expected_counts = {"TA2:1317": 0, "TA2:1339": 0, "TA2:1346": 0, "TA2:1389": 2, "TA2:1493": 0,
                       "TA2:1494": 0, "TA2:1496": 10, "TA2:1505": 28, "TA2:1510": 10, "TA2:1511": 8}
    need({k: len(v) for k, v in members.items()} == expected_counts, "exact B05 target member counts differ")
    unique_keys = {row["sourceKey"] for values in members.values() for row in values}
    need(len(unique_keys) == 40 and len(overlay["objects"]) == 960, "unique source geometry count differs")

    excluded_pelvis_names = ["Ilium.i", "Ilium.j", "Ilium.s", "Ilium.t", "Ischium.i", "Ischium.j", "Ischium.s", "Ischium.t",
                             "Pubis.i", "Pubis.j", "Pubis.s", "Pubis.t"]
    exclusions = {row["name"]: row for row in catalog["exclusions"]}
    need(all(name in exclusions and exclusions[name]["reason"] == "label_or_group_or_landmark_representation" for name in excluded_pelvis_names), "pelvic names are no longer excluded label/group objects")
    for name in ["Ilium.i", "Ischium.i", "Pubis.i"]:
        need(exclusions[name]["dataName"].endswith(".j"), "known i/j metadata conflict changed")
    missing_source_names = [row["name"] for row in objects if re.search(r"os trigonum|fabella|cyamella|accessory navicular|accessory tarsal", row["name"], re.I)]
    need(not missing_source_names, "unexpected accessory source object found; reclassify before applying")

    term_defs = {
        "TA2:1317": {"modern": "엉덩뼈", "traditional": "장골", "mSource": [SOURCE_IDS["ilium"], SOURCE_IDS["pelvis"]], "tSource": [SOURCE_IDS["ilium"], SOURCE_IDS["pelvis"]],
            "mLoc": "Opened KMLE aggregate HTML, 대한해부학회 exact-result row Ilium -> 엉덩뼈 [장골]; Asan pelvis page lines 43-44 gives the same component name.", "tLoc": "Opened KMLE aggregate HTML, KAS old term for Ilium: 장골; Asan pelvis page lines 43-44.",
            "class": "individual paired bone component of hip bone; source exact rendering surface unavailable", "surface": {"status": "no_direct_evaluated_surface; label_or_group_nodes_excluded", "sourceNamesNotBound": ["Ilium.i", "Ilium.j", "Ilium.s", "Ilium.t"], "exactTargetRelationAdded": False, "note": "i/j mesh exclusions are categorized as label/group/landmark representation; source dataName mismatch prevents side assignment. s/t are font labels. The whole Hip bone surface is not substituted for ilium."}, "candidates": []},
        "TA2:1339": {"modern": "궁둥뼈", "traditional": "좌골", "mSource": [SOURCE_IDS["ischium"], SOURCE_IDS["pelvis"]], "tSource": [SOURCE_IDS["ischium"], SOURCE_IDS["pelvis"]],
            "mLoc": "Opened KMLE aggregate HTML, 대한해부학회 exact-result row Ischium -> 궁둥뼈 [좌골]; Asan pelvis page lines 35-41 identifies the component.", "tLoc": "Opened KMLE aggregate HTML, KAS old term for Ischium: 좌골; Asan pelvis page lines 39-41.",
            "class": "individual paired bone component of hip bone; source exact rendering surface unavailable", "surface": {"status": "no_direct_evaluated_surface; label_or_group_nodes_excluded", "sourceNamesNotBound": ["Ischium.i", "Ischium.j", "Ischium.s", "Ischium.t"], "exactTargetRelationAdded": False, "note": "i/j mesh exclusions are categorized as label/group/landmark representation; source dataName mismatch prevents side assignment. s/t are font labels. The whole Hip bone surface is not substituted for ischium."}, "candidates": []},
        "TA2:1346": {"modern": "두덩뼈", "traditional": "치골", "mSource": [SOURCE_IDS["pubis"], SOURCE_IDS["pelvis"]], "tSource": [SOURCE_IDS["pubis"], SOURCE_IDS["pelvis"]],
            "mLoc": "Opened KMLE aggregate HTML, 대한의협 exact-result row pubis -> 두덩뼈, 치골; Asan pelvis page lines 48-50 identifies 두덩뼈 as a hip-bone component.", "tLoc": "Opened KMLE aggregate HTML, 대한의협 same exact row includes 치골; Asan pelvis page lines 48-50 lists 치골(두덩뼈). KAS exact row was absent in the exact pubis query.",
            "class": "individual paired bone component of hip bone; source exact rendering surface unavailable", "surface": {"status": "no_direct_evaluated_surface; label_or_group_nodes_excluded", "sourceNamesNotBound": ["Pubis.i", "Pubis.j", "Pubis.s", "Pubis.t"], "exactTargetRelationAdded": False, "note": "i/j mesh exclusions are categorized as label/group/landmark representation; source dataName mismatch prevents side assignment. s/t are font labels. The whole Hip bone surface is not substituted for pubis."}, "candidates": []},
        "TA2:1389": {"modern": None, "traditional": None, "mSource": [SOURCE_IDS["knee"], SOURCE_IDS["sesamoid"]], "tSource": [SOURCE_IDS["knee"], SOURCE_IDS["sesamoid"]],
            "modernMissing": "No exact Korean label for the knee-specific group was found. Generic 종자뼈 is retained only as an unapplied candidate.", "traditionalMissing": "No exact knee-group traditional name was found. Generic 종자골 is not applied to the target.",
            "class": "bone group; source page enumerates patella, fabella, and cyamella as noteworthy members", "surface": {"status": "partial_patella_members_only_fabella_and_cyamella_surface_missing", "relationKind": "class_member", "sourceMembers": members["TA2:1389"], "notFoundObjectNames": ["Fabella", "Cyamella"], "note": "Two existing patella side surfaces are explicitly member candidates. No fabella or cyamella evaluated object exists in the frozen 960-object inventory; do not call the knee group complete."},
            "candidates": [{"value": "종자뼈", "sourceId": SOURCE_IDS["sesamoid"], "locator": "KMLE search excerpt; generic Sesamoid bones row.", "status": "unapplied_generic_candidate", "reason": "The source row is not knee-specific."}, {"value": "종자골", "sourceId": SOURCE_IDS["sesamoid"], "locator": "KMLE search excerpt; generic old term.", "status": "unapplied_generic_candidate", "reason": "The source row is not knee-specific."}]},
        "TA2:1493": {"modern": None, "traditional": None, "mSource": [SOURCE_IDS["accessoryFoot"]], "tSource": [SOURCE_IDS["accessoryFoot"]],
            "modernMissing": "No exact Korean name for the full accessory tarsal-bones group was located. The opened Korean article uses examples, not a full group name.", "traditionalMissing": "No exact traditional Korean name for the entire group was located; do not promote generic 부골 or one variant to the whole group.",
            "class": "bone group of accessory tarsal variants with an unspecified full member denominator in this source snapshot", "surface": {"status": "no_exact_accessory_tarsal_surface_in_frozen_source", "sourceNamesNotFound": ["accessory tarsal bone", "accessory navicular", "os trigonum"], "exactTargetRelationAdded": False, "note": "The source has no evaluated object with the group or named accessory-variant labels. Standard navicular/talus objects are not substituted."}, "candidates": [{"value": "부골", "sourceId": SOURCE_IDS["accessoryFoot"], "locator": "Opened 2011 Korean Foot and Ankle Society article title/body uses 족부 부골 as a generic phrase.", "status": "unapplied_generic_candidate", "reason": "Generic term does not name the exact accessory-tarsal-bones target or define members."}]},
        "TA2:1494": {"modern": "발세모뼈", "traditional": "삼각골", "mSource": [SOURCE_IDS["osTrigonum"]], "tSource": [SOURCE_IDS["osTrigonum"], SOURCE_IDS["accessoryFoot"]],
            "mLoc": "KMLE search-index excerpt, KAS similar-result row (Os trigonum) -> (발세모뼈). Direct page fetch failed with cache miss; not an opened source dictionary record.", "tLoc": "KMLE search-index excerpt, same row old term 삼각골; corroborating opened 2011 KFA article page 0 lines 37-38 uses 삼각골(os trigonum).",
            "class": "optional accessory bone variant under accessory tarsal-bones group; no source side specified", "surface": {"status": "optional_variant_surface_missing", "sourceNamesNotFound": ["os trigonum", "trigonal bone"], "exactTargetRelationAdded": False, "note": "The opened foot/ankle paper distinguishes os trigonum from accessory navicular; no corresponding evaluated ZA object appears. A talus process is not substituted."}, "candidates": []},
        "TA2:1496": {"modern": "발허리뼈", "traditional": "중족골", "mSource": [SOURCE_IDS["metatarsal"]], "tSource": [SOURCE_IDS["metatarsal"]],
            "mLoc": "KMLE search-index excerpt for exact metatarsal bone query: current 대한의협 result -> 발허리뼈; direct HTML fetch returned Unicode decoding error. Not an opened dictionary record.", "tLoc": "KMLE search-index excerpt for exact query includes current/older 대한의협 row -> 중족골; direct HTML fetch returned Unicode decoding error.",
            "class": "individual bone class represented by five rays per source side", "surface": {"status": "ten_exact_named_class_member_surfaces", "relationKind": "class_member", "sourceMembers": members["TA2:1496"], "exactAggregateSourceObject": None, "note": "Five metatarsal objects on each side. Same nodes remain one geometry each; no aggregate mesh is asserted."}, "candidates": []},
        "TA2:1505": {"modern": None, "traditional": None, "mSource": [SOURCE_IDS["phalanges"]], "tSource": [SOURCE_IDS["phalanges"]],
            "modernMissing": "Opened KMLE HTML provides exact plural Phalanges [Toes] -> 발가락뼈, but not an exact singular phalanx-of-foot row. The plural term is not copied into the singular target field.", "traditionalMissing": "The opened KAS row's older generic label 지골 applies to the plural toes row, not a singular foot-phalanx target.",
            "class": "individual bone class with 28 evaluated members in this source snapshot (10 proximal, 8 middle, 10 distal); this is source-snapshot coverage, not a frozen anatomical denominator", "surface": {"status": "28_exactly_named_source_class_members", "relationKind": "class_member", "sourceMembers": members["TA2:1505"], "note": "The object names identify digit and level. Left objects also carry a Right foot collection; side is determined by object suffix, source label, and matching Left/Right lower limb collection, not by the Right foot collection."},
            "candidates": [{"value": "발가락뼈", "sourceId": SOURCE_IDS["phalanges"], "locator": "Opened KMLE HTML, KAS exact plural Phalanges [Toes] rows at lines 89-92.", "status": "unapplied_plural_target_candidate", "reason": "TA2:1505 is frozen as singular phalanx of foot; do not substitute a plural group label."}]},
        "TA2:1510": {"modern": None, "traditional": None, "mSource": [SOURCE_IDS["phalanges"]], "tSource": [SOURCE_IDS["phalanges"]],
            "modernMissing": "Opened source contains generic Proximal phalanges -> 첫마디뼈, without a foot-specific target label; do not compose a new Korean compound.", "traditionalMissing": "Generic Proximal phalanges -> 기절골 omits the exact foot qualification and is not applied.",
            "class": "proximal part class with 10 exact source members, five named digits per side", "surface": {"status": "ten_exact_named_class_member_surfaces", "relationKind": "class_member", "sourceMembers": members["TA2:1510"], "note": "Every selected exact member name includes Proximal and finger of foot; side is separately verified."},
            "candidates": [{"value": "첫마디뼈", "sourceId": SOURCE_IDS["phalanges"], "locator": "Opened KMLE HTML, generic Proximal phalanges row at lines 144-147.", "status": "unapplied_generic_candidate", "reason": "Row does not state foot-specific target."}, {"value": "기절골", "sourceId": SOURCE_IDS["phalanges"], "locator": "Opened KMLE HTML, generic old term at lines 144-147.", "status": "unapplied_generic_candidate", "reason": "Row does not state foot-specific target."}]},
        "TA2:1511": {"modern": None, "traditional": None, "mSource": [SOURCE_IDS["phalanges"]], "tSource": [SOURCE_IDS["phalanges"]],
            "modernMissing": "Opened source contains generic Middle phalanges -> 중간마디뼈, without a foot-specific target label; do not compose a new Korean compound.", "traditionalMissing": "Generic Middle phalanges -> 중절골 omits the exact foot qualification and is not applied.",
            "class": "middle part class with 8 exact source members (digits two through five on each side); no great-toe middle element is invented", "surface": {"status": "eight_exact_named_class_member_surfaces", "relationKind": "class_member", "sourceMembers": members["TA2:1511"], "note": "Eight exact objects are named; source has no great-toe middle phalanx member."},
            "candidates": [{"value": "중간마디뼈", "sourceId": SOURCE_IDS["phalanges"], "locator": "Opened KMLE HTML, generic Middle phalanges row at lines 139-142.", "status": "unapplied_generic_candidate", "reason": "Row does not state foot-specific target."}, {"value": "중절골", "sourceId": SOURCE_IDS["phalanges"], "locator": "Opened KMLE HTML, generic old term at lines 139-142.", "status": "unapplied_generic_candidate", "reason": "Row does not state foot-specific target."}]}
    }

    evidence = source_rows(observations, scope, catalog)
    source_ids = {row["id"] for row in evidence}
    need(not (base_evidence & source_ids), "B05 source id collision")
    need(all(src in source_ids for d in term_defs.values() for src in d["mSource"] + d["tSource"]), "term references missing source evidence")
    overlay["evidenceSources"] = overlay.get("evidenceSources", []) + evidence
    term_rows = []
    for target_id in EXPECTED:
        target, definition = targets[target_id], term_defs[target_id]
        english, latin = target["term"]["english"], target["term"]["latin"]
        modern, traditional = definition["modern"], definition["traditional"]
        fields = {
            "koModern": field(modern, definition["mSource"], definition.get("mLoc"), definition.get("modernMissing")),
            "koTraditional": field(traditional, definition["tSource"], definition.get("tLoc"), definition.get("traditionalMissing")),
            "en": field(english, [TA2_SOURCE], f"Pinned T96 exact target {target_id} English term: {english}"),
            "latin": field(latin, [TA2_SOURCE], f"Pinned T96 exact target {target_id} Latin term: {latin}"),
            "sourceSynonyms": [{"language": lang, "value": value, "sourceIds": [TA2_SOURCE],
                                "locator": f"Pinned T96 exact TA2 source synonym ({lang}): {value}", "status": "evidence_backed"}
                               for lang, values in target["term"].get("sourceSynonyms", {}).items() for value in values],
            "hanja": {"value": None, "sourceIds": [], "locator": None, "status": "not_collected",
                      "missingReason": "Actual Hanja glyphs are not collected in this task."}
        }
        term_rows.append({
            "targetId": target_id, "targetTermSourceIds": [TA2_SOURCE], "english": english, "latin": latin,
            "sourceSynonyms": target["term"].get("sourceSynonyms", {}), "relatedTerms": target["sourceFlags"].get("relatedTerms", []),
            "semanticKind": target["semanticKind"], "primaryOwner": target["primaryOwner"], "regionIds": target["regionIds"],
            "sourceParentId": target["sourceParentId"], "sourceAncestryIds": target["sourceAncestryIds"], "sourceFlags": target["sourceFlags"],
            "classification": {"meaningType": definition["class"], "sourceAndHumanReview": "web_source_layers_recorded; humanReview=not_performed"},
            "names": {"koModern": modern, "koTraditional": traditional, "en": english}, "fieldEvidence": fields,
            "unappliedTermCandidates": definition["candidates"], "existingSurface": definition["surface"],
            "observedSurfacesNotBound": definition["surface"].get("sourceNamesNotBound", definition["surface"].get("sourceMembers", [])),
            "learnerBindingCreated": False, "canonicalHaConceptId": None, "sourceOnly": True,
            "humanReview": "not_performed", "publicRedistribution": "held", "newGeometryCreated": False
        })

    relation_rows = []
    relation_evidence = []
    for target_id in EXPECTED:
        target = targets[target_id]
        for member in members[target_id]:
            obj = source_by_name[member["sourceObjectName"]]
            row = overlay_by_name[obj["name"]]
            side = member["sourceSide"]
            relation = {
                "targetId": target_id, "targetEnglish": target["term"]["english"], "targetLatin": target["term"]["latin"],
                "targetSemanticKind": target["semanticKind"], "targetPrimaryOwner": target["primaryOwner"], "targetRegionIds": target["regionIds"],
                "targetLaterality": target["sourceCardinality"]["lateralityState"], "sourceKey": obj["sourceKey"],
                "sourceObjectName": obj["name"], "sourceDataName": obj["dataName"], "sourceParent": obj["parent"],
                "sourceCollections": obj["collections"], "sourceSide": side, "evaluatedGeometrySha256": obj["evaluatedGeometrySha256"],
                "sourceHash": SOURCE_HASH, "sourceRevision": SOURCE_REVISION,
                "matchBasis": "Pinned T96 target semantics plus exact evaluated source object name/part level, matching skeletal parent and source side label; side is corroborated by exact .l/.r suffix and Left/Right lower-limb collection. The generic Right foot collection appears on both sides and is not used for laterality. No upstream FJ ID or HA learner binding is asserted.",
                "directObjectNameMatch": False, "ancestorNameAloneUsed": False, "upstreamFjOrTa2IdClaim": False,
                "canonicalHaBindingCreated": False, "humanReview": "not_performed", "relationKind": "class_member",
                "matchedTargetSynonym": None, "sourceSegmentCode": None, "memberCode": member["memberCode"],
                "matchEvidenceSourceIds": [ZA_SOURCE, TA2_SOURCE]
            }
            need(target_id not in row.get("targetIds", []), "target ID already present in overlay row")
            row.setdefault("targetIds", []).append(target_id)
            relations = row.setdefault("targetRelationEvidence", [])
            need(not any(existing.get("targetId") == target_id for existing in relations), "duplicate target/source relation")
            relations.append(relation)
            relation_rows.append(relation)
            relation_evidence.append({**relation, "sourceMember": member})
    overlay["targetTerminologyEvidence"] = overlay.get("targetTerminologyEvidence", []) + term_rows
    overlay["revision"] = "T100-source-taxonomy-local-display-v1-B05-pelvis-lower-limb-bones"
    write(OVERLAY_PATH, overlay)

    counts = {target_id: len(members[target_id]) for target_id in EXPECTED}
    ledger = {
        "schemaVersion": 1, "batchId": "T100-B05-pelvis-lower-limb-bones", "capturedOn": "2026-09-29",
        "scope": {"targetCount": 10, "requestedTargetIds": EXPECTED, "taskTargetDenominator": 542,
                  "taskRegionMembershipDenominator": 563, "regions": 12, "targetScopeRevision": scope["revision"],
                  "targetScopeSha256": frozen["targetScopeSha256"], "sourceRevision": SOURCE_REVISION,
                  "sourceFileSha256": SOURCE_HASH, "historicalRemainderOriginalCount": 182,
                  "historicalRemainderAtBatchStart": 152, "historicalRemainderAfterDisposition": 142,
                  "frozenArrayOffsets": [30, 40]},
        "sourceEvidence": evidence, "terminologyObservations": observations["observations"], "targets": term_rows,
        "crosswalkRelations": relation_evidence, "memberCountsByTarget": counts,
        "uniqueSourceObjects": len(unique_keys), "rightsAndReview": {"sourceOnly": True, "publicRedistribution": "held", "humanReview": "not_performed"},
        "nonClaims": ["not whole-body completion", "no upstream FJ identity claim", "no canonical HA learner binding or search alias",
                       "no new geometry", "no source rights promotion", "no human anatomy review", "a source label node is not an evaluated surface",
                       "the group sesamoid target remains partial because fabella/cyamella surfaces are missing",
                       "source snapshot phalanx counts are not an independent anatomical denominator"]
    }
    write(HERE / "term-and-correspondence-ledger.json", ledger)
    relation_targets = [x for x in EXPECTED if counts[x] > 0]
    correspondence = {
        "schemaVersion": 1, "batchId": "T100-B05-pelvis-lower-limb-bones", "targetCount": 10,
        "exactOverlayRelations": len(relation_rows), "sourceObjectMembers": len(unique_keys),
        "memberCountsByTarget": counts, "targetsWithDirectSourceRelations": relation_targets,
        "targetsWithNoDirectSourceRelation": [x for x in EXPECTED if counts[x] == 0],
        "partialTargets": ["TA2:1389"], "targetsMissingSurface": ["TA2:1317", "TA2:1339", "TA2:1346", "TA2:1493", "TA2:1494"],
        "unboundPelvisLabelAndGroupNodes": excluded_pelvis_names,
        "ignoredAnomalousFootCollection": "Right foot is present on both .l and .r object collections; side was derived only from suffix/sourceLabelSide and matching Left/Right lower limb collection.",
        "historicalRemainderAtBatchStart": 152, "batchDispositionCount": 10, "historicalRemainderAfterB05Disposition": 142,
        "inputDenominators": {"targets": 542, "memberships": 563, "regions": 12},
        "preservedCounts": {"sourceObjects": 960, "locallyDisplayable": sum(1 for x in overlay["objects"] if x["localDisplayEligible"]),
                            "haBoundRows": sum(1 for x in overlay["objects"] if x["haConceptId"]),
                            "publicRedistribution": "held", "humanReview": "not_performed"},
        "overlaySha256": sha_file(OVERLAY_PATH)
    }
    write(HERE / "structure-correspondence.json", correspondence)
    print(json.dumps({"batchId": ledger["batchId"], "relations": len(relation_rows), "uniqueSourceObjects": len(unique_keys),
                      "membersByTarget": counts, "overlaySha256": correspondence["overlaySha256"]}, indent=2))


if __name__ == "__main__":
    main()
