#!/usr/bin/env python3
"""Reproducibly add T100-B02 evidence to the existing ZA overlay; no geometry work."""
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
SOURCE_META_PATH = ROOT / "work/evidence/T100/resolution-2026-09-29/source-metadata.json"
REMAINING_PATH = ROOT / "work/evidence/T100/resolution-2026-09-29/remaining-targets.json"
COMPILED_PATH = ROOT / "atlas-data/source-cache/datasets/za/compiled/manifest.json"
OVERLAY_REL = "atlas-data/overlays/za-local-integration.json"
OVERLAY_PATH = ROOT / OVERLAY_REL
OUT = HERE / "term-and-correspondence-ledger.json"
CORRESPONDENCE = HERE / "structure-correspondence.json"
DATE = "2026-09-29"
REVISION = "c7010a903b75a2fd24a13b1c2c4c3546a9223780"
SOURCE_HASH = "9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd"

TARGET_IDS = [
    "TA2:356", "TA2:819", "TA2:830", "TA2:831", "TA2:832",
    "TA2:1032", "TA2:1038", "TA2:1050", "TA2:1059", "TA2:1065",
]
SOURCE_IDS = {
    "ta2": "fipat-ta2-t100-b02-frozen-target-terms",
    "za": "za-t99-t100-b02-frozen-source-objects",
    "facial": "kmle-t100-facial-bones-opened",
    "sutural": "kmle-t100-sutural-bone-index",
    "interparietal": "kmle-t100-interparietal-bone-opened",
    "cervical": "kmle-t100-cervical-vertebra-opened",
    "atlas": "kmle-t100-atlas-opened",
    "axis": "kmle-t100-axis-opened",
    "thoracic": "kmle-t100-thoracic-vertebra-opened",
    "japonicum": "kmle-t100-os-japonicum-index",
    "accessory": "kmle-t100-accessory-cranium-index",
    "lowerThoracic": "kmle-t100-lower-thoracic-index",
}


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def read(path: Path):
    return json.loads(path.read_text())


def local_term_source(source_id: str, term: str | None, locator: str, *, access_date=DATE):
    return {
        "id": source_id,
        "url": "https://ta2viewer.openanatomy.org/" if source_id == SOURCE_IDS["ta2"] else
        "https://github.com/z-anatomy/Models-of-human-anatomy/tree/" + REVISION if source_id == SOURCE_IDS["za"] else "",
        "sourceLabel": "FIPAT Terminologia Anatomica, 2nd edition, online vocabulary 2.07; T96 frozen target rows" if source_id == SOURCE_IDS["ta2"] else
        "T98/T99 local frozen Z-Anatomy source object catalogue and evaluated scene manifest",
        "exactEdition": "Terminologia Anatomica 2nd edition, vocabulary 2.07" if source_id == SOURCE_IDS["ta2"] else REVISION,
        "editionExposure": "exact vocabulary/version and source hash recorded in frozen T96 scope" if source_id == SOURCE_IDS["ta2"] else "exact source commit pinned; object upstream IDs are not declared by this catalogue",
        "accessDate": access_date,
        "accessMethod": "local_frozen_metadata",
        "locator": locator,
        "term": term,
        "koModern": None,
        "koTraditional": None,
    }


def kmle_source(source_id: str, query: str, section: str, access: str, locator: str,
                term: str | None = None, modern: str | None = None, traditional: str | None = None):
    return {
        "id": source_id,
        "url": f"https://m.kmle.co.kr/search.php?Search={query}",
        "sourceLabel": f"KMLE aggregation, {section}",
        "exactEdition": None,
        "editionExposure": "underlying dictionary edition/revision not exposed by KMLE",
        "accessDate": DATE,
        "accessMethod": access,
        "locator": locator,
        "term": term,
        "koModern": modern,
        "koTraditional": traditional,
    }


EVIDENCE_SOURCES = [
    local_term_source(SOURCE_IDS["ta2"], None,
        "atlas-data/catalog/target-scope-t96.json; TA2 IDs 356, 819, 830-832, 1032, 1038, 1050, 1059, 1065; English/Latin term, source synonym/related-term flags, parent, semantic kind and cardinality frozen; scope sha256 " + BASELINE["frozenScope"]["sha256"]),
    local_term_source(SOURCE_IDS["za"], None,
        "work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json and atlas-data/manifests/za-c7010a9/compiled-manifest.json; exact sourceKey/name/dataName/parent/collections/evaluatedGeometrySha256; archive sha256 " + SOURCE_HASH),
    kmle_source(SOURCE_IDS["facial"], "facial", "KI 의학용어 사전 section (opened HTML)", "opened_html",
        "Opened KMLE Search=facial HTML: KI dictionary result `facial bone` → 얼굴뼈, 안면골 (tool page lines 674-677); the same opened page's facial-bones definition says source dictionaries differ on group members (lines 933-937).",
        "facial bone(s)", "얼굴뼈", "안면골"),
    kmle_source(SOURCE_IDS["sutural"], "sutural+bone", "대한의협 의학용어 사전 검색 유사결과 excerpt (not opened)", "search_index_excerpt",
        "Search index excerpt for the KMLE query `sutural bone` gives `sutural bone` → 봉합뼈. The original result page was not opened; no edition/revision is exposed.",
        "sutural bone", "봉합뼈", None),
    kmle_source(SOURCE_IDS["interparietal"], "bone", "대한해부학회 의학용어 사전 유사결과 section (opened HTML)", "opened_html",
        "Opened KMLE Search=bone HTML, lines 780-784: `(Interparietal bone)` → `(마루사이뼈)`, old term 두정간골.",
        "interparietal bone", "마루사이뼈", "두정간골"),
    kmle_source(SOURCE_IDS["cervical"], "thoracic+vertebra", "대한의협 의학용어 사전 유사결과 section (opened HTML)", "opened_html",
        "Opened KMLE Search=thoracic+vertebra HTML, lines 53-55: `cervical vertebra` → 목뼈, 경추; lines 332-341 show the Korean Anatomical Society range term Cervical/Thoracic vertebrae.",
        "cervical vertebra", "목뼈", "경추"),
    kmle_source(SOURCE_IDS["atlas"], "atlas", "대한해부학회 의학용어 사전 맞춤결과 section (opened HTML)", "opened_html",
        "Opened KMLE Search=atlas HTML, lines 83-91: `Atlas [First cervical vertebra]` → 고리뼈 [환추골], old term 환추(제1경추).",
        "Atlas [First cervical vertebra]", "고리뼈", "환추골"),
    kmle_source(SOURCE_IDS["axis"], "thoracic+vertebra", "대한해부학회 의학용어 사전 맞춤결과 section (opened HTML)", "opened_html",
        "Opened KMLE Search=thoracic+vertebra HTML, lines 378-381: `Axis [Second cervical vertebra]` → 중쇠뼈 [축추골], old term 축추(제2경추).",
        "Axis [Second cervical vertebra]", "중쇠뼈", "축추골"),
    kmle_source(SOURCE_IDS["thoracic"], "thoracic+vertebra", "대한의협/Korean Anatomical Society sections (opened HTML)", "opened_html",
        "Opened KMLE Search=thoracic+vertebra HTML, lines 73-81: `thoracic vertebra` → 등뼈, 흉추; lines 332-341: `Thoracic vertebrae(first-twelfth)` → 등(척추)뼈(첫째-열두째) [흉추골], old term 흉추골.",
        "thoracic vertebra(s), first-twelfth", "등뼈", "흉추골"),
    kmle_source(SOURCE_IDS["japonicum"], "os+japonicum", "KMLE search index check (exact entry not found; no page opened)", "search_index_excerpt",
        "Exact KMLE index query for `os japonicum` did not surface a Korean terminology entry; FIPAT's frozen synonym `bipartite zygomatic bone` is retained separately and is not translated here.",
        "os japonicum", None, None),
    kmle_source(SOURCE_IDS["accessory"], "accessory+bones+of+cranium", "KMLE search index check (no exact group entry; no page opened)", "search_index_excerpt",
        "KMLE index checks for `accessory bones of cranium/skull` surfaced a generic `accessory bone`/extra-ossicle result, not an exact cranial group entry; no Korean group label is inferred.",
        "accessory bones of cranium", None, None),
    kmle_source(SOURCE_IDS["lowerThoracic"], "lower+thoracic+vertebra", "KMLE search index check (no exact lower-thoracic term found; page retrieval failed)", "search_index_excerpt",
        "Exact KMLE query produced no exact Korean lower-thoracic vertebra term in available search output; direct open of this URL was inaccessible through the retrieval tool. No T9-T12 subset boundary inferred.",
        "lower thoracic vertebra", None, None),
]


def map_field(value: str | None, source_ids: list[str], locator: str, missing_reason: str | None = None):
    return {"value": value, "sourceIds": source_ids, "locator": locator if value else None,
            "status": "evidence_backed" if value else "missing", "missingReason": missing_reason}


def row_surface(source_obj: dict, source_meta: dict):
    meta = source_meta.get(source_obj["name"])
    if not meta:
        raise ValueError(f"source metadata missing object: {source_obj['name']}")
    if meta["parent"] != source_obj["parent"] or meta["collections"] != source_obj["collections"]:
        raise ValueError(f"source parent/collection differs: {source_obj['name']}")
    locator = source_obj["sourceLocator"]
    if locator.get("sourceFileSha256") != SOURCE_HASH or locator.get("archivePath") != "Z-Anatomy/Startup.blend":
        raise ValueError(f"source locator/hash differs: {source_obj['name']}")
    if not re.fullmatch(r"[a-f0-9]{64}", source_obj["evaluatedGeometrySha256"]):
        raise ValueError(f"evaluated geometry hash missing: {source_obj['name']}")
    return {
        "sourceKey": source_obj["sourceKey"], "sourceObjectName": source_obj["name"],
        "sourceDataName": source_obj["dataName"], "sourceParent": source_obj["parent"],
        "sourceCollections": source_obj["collections"], "sourceSide": source_obj["sourceLabelSide"],
        "evaluatedGeometrySha256": source_obj["evaluatedGeometrySha256"],
        "sourceHash": SOURCE_HASH, "sourceRevision": REVISION,
        "sourceLocator": locator,
    }


def main():
    for path, expected in BASELINE["inputSha256"].items():
        actual = sha_file(ROOT / path)
        if actual != expected:
            raise SystemExit(f"frozen B02 input changed: {path}: {actual} != {expected}")
    scope = read(SCOPE_PATH)
    catalog = read(CATALOG_PATH)
    remaining = read(REMAINING_PATH)
    source_meta = {x["name"]: x for x in read(SOURCE_META_PATH)["objects"]}
    target_rows = {row["id"]: row for row in scope["targets"]}
    objects = {row["sourceKey"]: row for row in catalog["objects"]}
    overlay_base = json.loads(subprocess.check_output(
        ["git", "show", f"{BASELINE['startingHead']}:{OVERLAY_REL}"], cwd=ROOT))
    if sha_bytes((json.dumps(overlay_base, ensure_ascii=False, indent=2) + "\n").encode()) != BASELINE["contextBaselineSha256"][OVERLAY_REL]:
        # Git's file bytes are the hash authority; serialize equality above is only a portability check.
        base_raw = subprocess.check_output(["git", "show", f"{BASELINE['startingHead']}:{OVERLAY_REL}"], cwd=ROOT)
        if sha_bytes(base_raw) != BASELINE["contextBaselineSha256"][OVERLAY_REL]:
            raise SystemExit("starting commit overlay does not match recorded baseline SHA256")
    base_raw = subprocess.check_output(["git", "show", f"{BASELINE['startingHead']}:{OVERLAY_REL}"], cwd=ROOT)
    if sha_bytes(base_raw) != BASELINE["contextBaselineSha256"][OVERLAY_REL]:
        raise SystemExit("starting commit overlay does not match recorded baseline SHA256")
    if catalog["sourceHash"] != SOURCE_HASH or catalog["sourceRevision"] != REVISION:
        raise SystemExit("pinned Z-Anatomy source identity changed")
    if scope["revision"] != "T96-2026-09-28-semantic-freeze-v1" or len(scope["targets"]) != 542:
        raise SystemExit("T96 frozen scope changed")
    remaining_rows = remaining.get("unresolved", [])
    remaining_ids = {row["targetId"] for row in remaining_rows}
    if remaining["targets"] != 542 or len(remaining_rows) != 182 or not set(TARGET_IDS) <= remaining_ids:
        raise SystemExit("B02 targets are not the exact frozen remainder subset")
    if overlay_base["scope"] != {"targets": 542, "memberships": 563, "regions": 12}:
        raise SystemExit("overlay denominator changed")
    source_rows = {x["sourceKey"]: x for x in overlay_base["objects"]}
    if len(objects) != 960 or len(source_rows) != 960:
        raise SystemExit("source object denominator changed")

    surface_by_name = {row["name"]: row for row in catalog["objects"]}
    full_names = {x["name"] for x in read(SOURCE_META_PATH)["objects"]}
    exact_missing_names = {
        "facial bones", "os japonicum", "accessory bones of cranium", "sutural bone", "interparietal bone"
    }
    exact_object_inventory = []
    for name in sorted(exact_missing_names):
        matches = sorted(x for x in full_names if x.casefold() == name.casefold())
        surface_matches = sorted(x for x in surface_by_name if x.casefold() == name.casefold())
        exact_object_inventory.append({"queriedName": name, "rawObjectNameMatches": matches,
                                       "evaluatedSurfaceNameMatches": surface_matches,
                                       "status": "exact_source_object_absent" if not matches and not surface_matches else "name_match_requires_semantic_review"})
        if matches or surface_matches:
            raise SystemExit(f"unexpected exact source name candidate requires review: {name}: {matches or surface_matches}")

    # The only object sets eligible for this batch are explicitly frozen here.
    requested_names = ["Atlas (C1)", "Axis (C2)"] + [f"Vertebra C{i}" for i in range(3, 8)] + [f"Vertebra T{i}" for i in range(1, 13)]
    expected_names = {
        "TA2:1038": ["Atlas (C1)"],
        "TA2:1050": ["Axis (C2)"],
        "TA2:1032": [f"Vertebra C{i}" for i in range(3, 8)],
        "TA2:1059": [f"Vertebra T{i}" for i in range(1, 13)],
    }
    for target_id, names in expected_names.items():
        if target_id not in target_rows or target_rows[target_id]["semanticKind"] != "bone":
            raise SystemExit(f"unexpected frozen target kind: {target_id}")
        if any(name not in surface_by_name for name in names):
            raise SystemExit(f"required existing source surface absent for {target_id}")
    if len(requested_names) != 19 or len(set(requested_names)) != 19:
        raise SystemExit("B02 exact object subset must remain 19 unique surfaces")
    # Every member must carry the matching skeletal parent and collection; no AABB/name-only join.
    for name in requested_names:
        obj = surface_by_name[name]
        expected_parent, collection = (("Cervical vertebrae.g", "Cervical vertebrae") if " C" in name or name.startswith(("Atlas", "Axis")) else ("Thoracic vertebrae.g", "Thoracic vertebrae"))
        if obj["parent"] != expected_parent or collection not in obj["collections"] or obj["kind"] != "skeletal_surface":
            raise SystemExit(f"source hierarchy/member evidence insufficient: {name}")
        row = source_rows[obj["sourceKey"]]
        if row["side"] != obj["sourceLabelSide"] or row["kind"] != "bone":
            raise SystemExit(f"source side/kind mismatch: {name}")

    evidence_map = {x["id"]: x for x in EVIDENCE_SOURCES}
    if len(evidence_map) != len(EVIDENCE_SOURCES):
        raise SystemExit("duplicate evidence source IDs")
    if not all(x["url"] for x in EVIDENCE_SOURCES):
        raise SystemExit("source URL missing")

    def target_term(target_id: str, *, classification: dict, geometry: dict, modern: str | None,
                    traditional: str | None, modern_source_ids: list[str], traditional_source_ids: list[str],
                    name_locator: str, modern_missing: str | None = None, traditional_missing: str | None = None,
                    observed_surfaces: list[dict] | None = None):
        target = target_rows[target_id]
        english, latin = target["term"]["english"], target["term"]["latin"]
        synonyms = target["term"].get("sourceSynonyms", {})
        names = {"koModern": modern, "koTraditional": traditional, "en": english}
        return {
            "targetId": target_id, "targetTermSourceIds": [SOURCE_IDS["ta2"]],
            "english": english, "latin": latin, "sourceSynonyms": synonyms,
            "relatedTerms": target["sourceFlags"].get("relatedTerms", []),
            "semanticKind": target["semanticKind"], "primaryOwner": target["primaryOwner"],
            "regionIds": target["regionIds"], "sourceParentId": target["sourceParentId"],
            "sourceAncestryIds": target["sourceAncestryIds"], "sourceFlags": target["sourceFlags"],
            "classification": classification,
            "names": names,
            "fieldEvidence": {
                "koModern": map_field(modern, modern_source_ids, name_locator, modern_missing),
                "koTraditional": map_field(traditional, traditional_source_ids, name_locator, traditional_missing),
                "en": map_field(english, [SOURCE_IDS["ta2"]], f"T96 target {target_id} exact English term: {english}"),
                "latin": map_field(latin, [SOURCE_IDS["ta2"]], f"T96 target {target_id} exact Latin term: {latin}"),
            },
            "existingSurface": geometry,
            "observedSurfacesNotBound": observed_surfaces or [],
            "learnerBindingCreated": False, "canonicalHaConceptId": None,
            "sourceOnly": True, "humanReview": "not_performed", "publicRedistribution": "held",
            "newGeometryCreated": False,
        }

    def surfaces_for(names: list[str]):
        return [row_surface(surface_by_name[name], source_meta) for name in names]

    zygomatic = surfaces_for(["Zygomatic bone.l", "Zygomatic bone.r"])
    face_nearby_names = [n for n in ["Nasal bone", "Nasal bone.l", "Nasal bone.r", "Maxilla", "Maxilla.l", "Maxilla.r", "Mandible", "Zygomatic bone.l", "Zygomatic bone.r", "Lacrimal bone.l", "Lacrimal bone.r", "Vomer"] if n in surface_by_name]
    face_nearby = surfaces_for(face_nearby_names)
    lower_candidates = surfaces_for([f"Vertebra T{i}" for i in range(9, 13)])

    target_terms = [
        target_term("TA2:356", classification={"meaningType":"bone group","groupPartVariant":"group; source/KMLE definitions disagree on constituent membership","laterality":"not specified; no side expansion"},
            geometry={"status":"group_surface_missing_composition_conflicted","exactAggregateSourceObject":None,"exactMemberCrosswalkAdded":False,"note":"Individual face-bone surfaces exist, but the opened KMLE definition gives differing member lists; no universal group geometry is claimed."},
            modern="얼굴뼈", traditional="안면골", modern_source_ids=[SOURCE_IDS["facial"]], traditional_source_ids=[SOURCE_IDS["facial"]],
            name_locator="Opened KMLE Search=facial HTML, KI result facial bone → 얼굴뼈, 안면골; retrieved page lines 674-677.", observed_surfaces=face_nearby),
        target_term("TA2:819", classification={"meaningType":"individual bone variant","groupPartVariant":"inconstant variant of zygomatic bone; TA2 exact English synonym bipartite zygomatic bone","laterality":"not specified"},
            geometry={"status":"variant_surface_missing","exactSourceObject":None,"exactMemberCrosswalkAdded":False,"note":"Ordinary left/right zygomatic bone surfaces are present, but no split/bipartite variant object is named or evaluated."},
            modern=None, traditional=None, modern_source_ids=[], traditional_source_ids=[], name_locator="", modern_missing="No exact Korean entry found in the KMLE index; do not translate the variant name by composition.", traditional_missing="No source-backed Sino-Korean Hangul name found.", observed_surfaces=zygomatic),
        target_term("TA2:830", classification={"meaningType":"bone group","groupPartVariant":"accessory cranium bone group; no frozen member enumeration in this batch","laterality":"not specified"},
            geometry={"status":"group_surface_missing","exactAggregateSourceObject":None,"exactMemberCrosswalkAdded":False,"note":"No exact aggregate source object or stable group member list was found."},
            modern=None, traditional=None, modern_source_ids=[], traditional_source_ids=[], name_locator="", modern_missing="KMLE index checks did not surface an exact cranial group entry; generic accessory bone is not substituted.", traditional_missing="No source-backed group label found."),
        target_term("TA2:831", classification={"meaningType":"individual bone variation","groupPartVariant":"inconstant sutural bone; TA2 related term wormian bone is retained as related, not promoted to an exact synonym","laterality":"not specified"},
            geometry={"status":"exact_surface_missing","exactSourceObject":None,"exactMemberCrosswalkAdded":False,"note":"No exact evaluated source object named sutural/Wormian bone."},
            modern="봉합뼈", traditional=None, modern_source_ids=[SOURCE_IDS["sutural"]], traditional_source_ids=[],
            name_locator="KMLE search-index excerpt: sutural bone → 봉합뼈; original result page not opened.", traditional_missing="No older/Sino-Korean Hangul form was verified."),
        target_term("TA2:832", classification={"meaningType":"individual bone variation","groupPartVariant":"inconstant accessory interparietal bone; TA2 synonyms os incae/inca bone and related term os inca are kept in their distinct source fields","laterality":"not specified"},
            geometry={"status":"exact_surface_missing","exactSourceObject":None,"exactMemberCrosswalkAdded":False,"note":"No exact interparietal/inca evaluated surface; nearby parietal/occipital surfaces are not a substitute."},
            modern="마루사이뼈", traditional="두정간골", modern_source_ids=[SOURCE_IDS["interparietal"]], traditional_source_ids=[SOURCE_IDS["interparietal"]],
            name_locator="Opened KMLE Search=bone HTML, Korean Anatomical Society similar result, lines 780-784."),
        target_term("TA2:1032", classification={"meaningType":"named bone type","groupPartVariant":"general cervical vertebra concept; C3-C7 are exact class members in this source, while C1/C2 have separately named target rows","laterality":"midline/nonpaired source labels; no side expansion"},
            geometry={"status":"five_exact_class_member_surfaces","exactSourceObject":None,"relationKind":"class_member","sourceMembers":surfaces_for([f"Vertebra C{i}" for i in range(3, 8)]),"note":"C1/C2 are recorded under their exact TA2:1038/1050 concepts, not duplicated into this generic row."},
            modern="목뼈", traditional="경추", modern_source_ids=[SOURCE_IDS["cervical"]], traditional_source_ids=[SOURCE_IDS["cervical"]],
            name_locator="Opened KMLE Search=thoracic+vertebra HTML, `cervical vertebra` entry lines 53-55."),
        target_term("TA2:1038", classification={"meaningType":"individual bone","groupPartVariant":"named first cervical vertebra (atlas); exact TA2 synonym vertebra C1","laterality":"midline/nonpaired source label"},
            geometry={"status":"one_exact_qualified_source_object","exactSourceObject":"Atlas (C1)","relationKind":"qualified_target_synonym","sourceMembers":surfaces_for(["Atlas (C1)"]),"note":"Exact object name plus target's exact synonym vertebra C1; parent and cervical collection corroborate region."},
            modern="고리뼈", traditional="환추골", modern_source_ids=[SOURCE_IDS["atlas"]], traditional_source_ids=[SOURCE_IDS["atlas"]],
            name_locator="Opened KMLE Search=atlas HTML, Korean Anatomical Society result, lines 83-91."),
        target_term("TA2:1050", classification={"meaningType":"individual bone","groupPartVariant":"named second cervical vertebra (axis); exact TA2 synonym vertebra C2","laterality":"midline/nonpaired source label"},
            geometry={"status":"one_exact_qualified_source_object","exactSourceObject":"Axis (C2)","relationKind":"qualified_target_synonym","sourceMembers":surfaces_for(["Axis (C2)"]),"note":"Exact object name plus target's exact synonym vertebra C2; parent and cervical collection corroborate region."},
            modern="중쇠뼈", traditional="축추골", modern_source_ids=[SOURCE_IDS["axis"]], traditional_source_ids=[SOURCE_IDS["axis"]],
            name_locator="Opened KMLE Search=thoracic+vertebra HTML, Korean Anatomical Society result, lines 378-381."),
        target_term("TA2:1059", classification={"meaningType":"named bone type","groupPartVariant":"general thoracic vertebra concept; 12 source objects T1-T12 are exact class members; distinct series target TA2:1058 is not replaced","laterality":"midline/nonpaired source labels"},
            geometry={"status":"twelve_exact_class_member_surfaces","exactSourceObject":None,"relationKind":"class_member","sourceMembers":surfaces_for([f"Vertebra T{i}" for i in range(1, 13)]),"note":"All 12 source names are explicit; the KMLE range term independently names first through twelfth thoracic vertebrae."},
            modern="등뼈", traditional="흉추골", modern_source_ids=[SOURCE_IDS["thoracic"]], traditional_source_ids=[SOURCE_IDS["thoracic"]],
            name_locator="Opened KMLE Search=thoracic+vertebra HTML, lines 73-81 and Korean Anatomical Society range entry lines 332-341."),
        target_term("TA2:1065", classification={"meaningType":"individual lower-thoracic vertebra concept","groupPartVariant":"lower subset boundary/member enumeration not fixed by this target row; T9-T12 are candidates only","laterality":"midline/nonpaired source labels"},
            geometry={"status":"subset_membership_unresolved","exactSourceObject":None,"exactMemberCrosswalkAdded":False,"candidateSurfaces":lower_candidates,"note":"T9-T12 surfaces exist, but no authoritative lower-thoracic subset boundary was located; no target relation is written."},
            modern=None, traditional=None, modern_source_ids=[], traditional_source_ids=[], name_locator="", modern_missing="No exact KMLE Korean term for lower thoracic vertebra was found; do not infer `아래등뼈`.", traditional_missing="No source-backed older/Sino-Korean Hangul term was verified.", observed_surfaces=lower_candidates),
    ]
    terms = {x["targetId"]: x for x in target_terms}
    if list(terms) != TARGET_IDS:
        raise SystemExit("B02 target order/identity changed")

    # Localize only source objects that have exact target/member evidence.
    name_specs = {}
    for target_id, code in [("TA2:1038", "C1"), ("TA2:1050", "C2")]:
        obj_name = "Atlas (C1)" if code == "C1" else "Axis (C2)"
        item = terms[target_id]
        name_specs[obj_name] = {
            "targetId": target_id, "modern": item["names"]["koModern"], "traditional": item["names"]["koTraditional"],
            "modernSource": SOURCE_IDS["atlas"] if code == "C1" else SOURCE_IDS["axis"],
            "traditionalSource": SOURCE_IDS["atlas"] if code == "C1" else SOURCE_IDS["axis"],
            "modernValue": item["names"]["koModern"], "traditionalValue": item["names"]["koTraditional"],
            "englishSourceName": obj_name,
        }
    cervical_ordinals = {3:"셋째",4:"넷째",5:"다섯째",6:"여섯째",7:"일곱째"}
    for i, ordinal in cervical_ordinals.items():
        obj_name = f"Vertebra C{i}"
        name_specs[obj_name] = {"targetId":"TA2:1032","modern":f"{ordinal} 목뼈","traditional":"경추",
            "modernSource":SOURCE_IDS["cervical"],"traditionalSource":SOURCE_IDS["cervical"],
            "modernValue":f"{ordinal} 목뼈","traditionalValue":"경추","englishSourceName":obj_name}
    thoracic_ordinals = {1:"첫째",2:"둘째",3:"셋째",4:"넷째",5:"다섯째",6:"여섯째",7:"일곱째",8:"여덟째",9:"아홉째",10:"열째",11:"열한째",12:"열두째"}
    for i, ordinal in thoracic_ordinals.items():
        obj_name = f"Vertebra T{i}"
        name_specs[obj_name] = {"targetId":"TA2:1059","modern":f"{ordinal} 등뼈","traditional":"흉추골",
            "modernSource":SOURCE_IDS["thoracic"],"traditionalSource":SOURCE_IDS["thoracic"],
            "modernValue":f"{ordinal} 등뼈","traditionalValue":"흉추골","englishSourceName":obj_name}
    if len(name_specs) != 19:
        raise SystemExit("B02 localized object count changed")

    crosswalk = []
    for name, spec in name_specs.items():
        target = target_rows[spec["targetId"]]
        source_obj = surface_by_name[name]
        row = source_rows[source_obj["sourceKey"]]
        frozen = row_surface(source_obj, source_meta)
        if row["haConceptId"] is not None or row["sourceOnly"] is not True or row["humanReview"] != "not_performed" or row["publicRedistribution"] != "held":
            raise SystemExit(f"protected learner/review/right state is not eligible: {name}")
        row["label"] = spec["modern"]
        row["names"]["koModern"] = spec["modern"]
        row["names"]["koTraditional"] = spec["traditional"]
        row["aliases"] = sorted(set(row["aliases"] + [target["term"]["english"], target["term"]["latin"], spec["traditional"], name.split(" (")[0]]))
        row["nameSourceIds"] = sorted(set(row["nameSourceIds"] + [SOURCE_IDS["ta2"], SOURCE_IDS["za"], spec["modernSource"], spec["traditionalSource"]]))
        region_label = "neck" if spec["targetId"] in {"TA2:1032", "TA2:1038", "TA2:1050"} else "back"
        row["nameEvidence"] = {
            "koModern": {"value": spec["modern"], "sourceIds": [spec["modernSource"], SOURCE_IDS["za"]],
                "locator": f"KMLE exact range/name entry plus exact source object `{name}`; sourceKey {source_obj['sourceKey']}; target {spec['targetId']}; evaluated geometry sha256 {source_obj['evaluatedGeometrySha256']}."},
            "koTraditional": {"value": spec["traditional"], "sourceIds": [spec["traditionalSource"]],
                "locator": f"KMLE exact terminology entry for {target['term']['english']}; source object `{name}` is the matching segment; T96 target {spec['targetId']}."},
            "en": {"value": row["names"]["en"], "sourceIds": [SOURCE_IDS["za"], SOURCE_IDS["ta2"]],
                "locator": f"Exact source object `{name}`; sourceKey {source_obj['sourceKey']}; parent `{source_obj['parent']}`; {region_label} collection; evaluated geometry sha256 {source_obj['evaluatedGeometrySha256']}; target {spec['targetId']} frozen English/Latin term."},
        }
        relation_kind = "qualified_target_synonym" if name in {"Atlas (C1)", "Axis (C2)"} else "class_member"
        matched_synonym = {"Atlas (C1)":"vertebra C1","Axis (C2)":"vertebra C2"}.get(name)
        target_id = spec["targetId"]
        if target_id not in row["targetIds"]:
            row["targetIds"].append(target_id)
        relation = {
            "targetId": target_id,
            "targetEnglish": target["term"]["english"], "targetLatin": target["term"]["latin"],
            "targetSemanticKind": target["semanticKind"], "targetPrimaryOwner": target["primaryOwner"],
            "targetRegionIds": target["regionIds"], "targetLaterality": target["sourceCardinality"]["lateralityState"],
            "sourceKey": source_obj["sourceKey"], "sourceObjectName": name, "sourceDataName": source_obj["dataName"],
            "sourceParent": source_obj["parent"], "sourceCollections": source_obj["collections"], "sourceSide": source_obj["sourceLabelSide"],
            "evaluatedGeometrySha256": source_obj["evaluatedGeometrySha256"], "sourceHash": SOURCE_HASH, "sourceRevision": REVISION,
            "matchBasis": (f"Exact frozen TA2 synonym `{matched_synonym}` plus exact Z-Anatomy object name `{name}` and C1/C2 level; parent/collection corroborate cervical region." if matched_synonym else
                f"Exact named source member `{name}` in parent `{source_obj['parent']}` and explicit skeletal collection `{('Cervical vertebrae' if target_id == 'TA2:1032' else 'Thoracic vertebrae')}`; the frozen target is the matching vertebra type."),
            "directObjectNameMatch": False, "ancestorNameAloneUsed": False, "upstreamFjOrTa2IdClaim": False,
            "canonicalHaBindingCreated": False, "humanReview": "not_performed",
            "relationKind": relation_kind, "matchedTargetSynonym": matched_synonym,
            "sourceSegmentCode": ("C1" if name == "Atlas (C1)" else "C2" if name == "Axis (C2)" else re.search(r"\b([CT]\d+)$", name).group(1)),
            "matchEvidenceSourceIds": ([SOURCE_IDS["za"], SOURCE_IDS["ta2"], spec["modernSource"]]),
        }
        row["targetRelationEvidence"] = list(row.get("targetRelationEvidence") or []) + [relation]
        crosswalk.append({**frozen, "targetId": target_id, "relationKind": relation_kind,
                          "matchedTargetSynonym": matched_synonym, "matchEvidenceSourceIds": relation["matchEvidenceSourceIds"],
                          "learnerBindingCreated": False, "sourceOnly": True, "humanReview": "not_performed",
                          "publicRedistribution": "held"})

    # Attach term-only records for the ten frozen target concepts. This property is evidence, not UI/search input.
    overlay = overlay_base
    existing_sources = {x["id"] for x in overlay.get("evidenceSources", [])}
    if existing_sources.intersection(evidence_map):
        raise SystemExit("B02 evidence source ID already exists in B01 overlay")
    overlay["evidenceSources"] = list(overlay.get("evidenceSources", [])) + [
        x for x in EVIDENCE_SOURCES if x["id"] not in existing_sources
    ]
    overlay["targetTerminologyEvidence"] = target_terms
    by_key = {x["sourceKey"]: x for x in overlay["objects"]}
    for relation in crosswalk:
        row = by_key[relation["sourceKey"]]
        # Retain existing T98/T99 identity, visibility, region, side, local-use and review states.
        original = source_rows[relation["sourceKey"]]
        for protected in ["sourceKey","sourceName","kind","regionIds","side","haConceptId","targetId","mappingStatus",
                          "localDisplayEligible","inspectionEligible","defaultVisible","sourceOnly","humanReview","publicRedistribution",
                          "sourceHiddenStatePreserved","localUseRights","displayDecisionBasis","hardHoldReasons","bounds"]:
            if row[protected] != original[protected]:
                raise SystemExit(f"protected overlay field changed: {relation['sourceObjectName']}.{protected}")

    overlay["revision"] = "T100-source-taxonomy-local-display-v1-B02-vertebral-variant-coverage"
    OVERLAY_PATH.write_text(json.dumps(overlay, ensure_ascii=False, indent=2) + "\n")

    # Record exact surfaces absent from both the full source-object inventory and evaluated catalogue.
    ledger = {
        "schemaVersion": 1, "batchId": "T100-B02-vertebral-variant-coverage", "capturedOn": DATE,
        "scope": {"targetCount":10,"requestedTargetIds":TARGET_IDS,"taskTargetDenominator":542,
                  "taskRegionMembershipDenominator":563,"regions":12,"targetScopeRevision":scope["revision"],
                  "targetScopeSha256":sha_file(SCOPE_PATH),"zaSourceRevision":REVISION,"zaSourceFileSha256":SOURCE_HASH,
                  "historicalRemainingCountAtBatchStart":len(remaining_rows),"historicalRemainingTargetInventorySha256":sha_file(REMAINING_PATH),
                  "sourceObjectCatalogueSha256":sha_file(CATALOG_PATH),"sourceMetadataSha256":sha_file(SOURCE_META_PATH),
                  "compiledManifestSha256":sha_file(COMPILED_PATH),"startingHead":BASELINE["startingHead"]},
        "sourceEvidence":EVIDENCE_SOURCES,
        "targets":target_terms,
        "exactSourceNameInventory":exact_object_inventory,
        "crosswalkRelations":crosswalk,
        "nonClaims":["not a whole-body completion claim","not an upstream FJ/object ID claim","not a canonical HA learner binding",
                     "not new geometry","not a human review","not a public redistribution permission decision"],
    }
    OUT.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n")
    corr = {
        "schemaVersion":1,"batchId":ledger["batchId"],"targetCount":10,
        "exactOverlayRelations":len(crosswalk),"sourceObjectMembers":len({x['sourceKey'] for x in crosswalk}),
        "memberCountsByTarget":{target_id:sum(1 for x in crosswalk if x["targetId"]==target_id) for target_id in TARGET_IDS},
        "targetsWithExactRelations":[x for x in TARGET_IDS if any(r["targetId"]==x for r in crosswalk)],
        "targetsWithoutExactRelations":[x for x in TARGET_IDS if not any(r["targetId"]==x for r in crosswalk)],
        "unresolvedGeometryAndIdentityRemain":True,
        "targetRows": [{"targetId":t["targetId"],"semanticKind":t["semanticKind"],"classification":t["classification"],
                        "existingSurface":t["existingSurface"],"koreanNames":t["names"],"fieldEvidence":t["fieldEvidence"],
                        "learnerBindingCreated":False,"canonicalHaConceptId":None,"newGeometryCreated":False,
                        "sourceOnly":True,"humanReview":"not_performed","publicRedistribution":"held"} for t in target_terms],
        "inputDenominators":{"targets":542,"memberships":563,"regions":12},
        "historicalRemainingAtBatchStart":182,"batchDispositionCount":10,"historicalRemainderAfterB02DispositionPass":172,
        "preservedCounts":{"sourceObjects":len(overlay["objects"]),"locallyDisplayable":sum(r["localDisplayEligible"] for r in overlay["objects"]),
                           "haBoundRows":sum(bool(r["haConceptId"]) for r in overlay["objects"]),"humanReview":"not_performed","publicRedistribution":"held"},
        "overlaySha256":sha_file(OVERLAY_PATH),
    }
    CORRESPONDENCE.write_text(json.dumps(corr, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"batchId":ledger["batchId"],"targets":10,"exactSurfaceRelations":len(crosswalk),
                      "overlaySha256":corr["overlaySha256"],"targetScopeSha256":ledger["scope"]["targetScopeSha256"]},ensure_ascii=False))


if __name__ == "__main__":
    main()
