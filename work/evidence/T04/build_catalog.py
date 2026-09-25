#!/usr/bin/env python3
"""Build the T04 partial, source-located catalog from a bounded TA2 row register.

The row register below transcribes only terms exposed in official FIPAT-hosted
TA2 Part 2 search-index excerpts. It is not a full extraction of the PDF.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "atlas-data" / "catalog"
SCOPE = json.loads((ROOT / "atlas-data/manifests/scope.json").read_text())
ASSETS = json.loads((ROOT / "atlas-data/manifests/assets.json").read_text())
PDF_URL = "https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf"
EDITION = "Terminologia Anatomica, 2nd edition (TA2), Part 2; online edition published 2019"

# Groups: id, scope region IDs, Latin row label, English row label, TA2 row,
# printed PDF page, parent group ID or None.
GROUPS = [
    ("HA-G-000001", ["head"], "MUSCULI CAPITIS", "MUSCLES OF HEAD", 2040, 74, None),
    ("HA-G-000002", ["eye"], "Musculi externi bulbi oculi", "Extraocular muscles", 2041, 74, "HA-G-000001"),
    ("HA-G-000003", ["mastication"], "Musculi masticatorii", "Masticatory muscles", 2104, 77, "HA-G-000001"),
    ("HA-G-000004", ["tongue"], "Musculi linguae", "Muscles of tongue", 2116, 77, "HA-G-000001"),
    ("HA-G-000005", ["back"], "MUSCULI HYPAXIALES DORSI", "HYPAXIAL MUSCLES OF BACK", 2225, 81, None),
    ("HA-G-000006", ["thorax_respiratory"], "MUSCULI THORACIS", "MUSCLES OF THORAX", 2299, 83, None),
    ("HA-G-000007", ["upper_extremity"], "MUSCULI MEMBRI SUPERIORIS", "MUSCLES OF UPPER LIMB", 2450, 89, None),
    ("HA-G-000008", ["shoulder"], "Musculi scapulohumerales", "Scapulohumeral muscles", 2451, 89, "HA-G-000007"),
    ("HA-G-000009", ["shoulder"], "Musculi cuffiae musculotendineae", "Rotator cuff muscles", 2456, 89, "HA-G-000008"),
    ("HA-G-000010", ["lower_extremity"], "MUSCULI MEMBRI INFERIORIS", "MUSCLES OF LOWER LIMB", 2592, 94, None),
    ("HA-G-000011", ["gluteal"], "Musculi glutei superficiales", "Superficial gluteal muscles", 2597, 94, "HA-G-000010"),
    ("HA-G-000012", ["gluteal"], "Musculi glutei profundi", "Deep gluteal muscles", 2603, 94, "HA-G-000010"),
    ("HA-G-000013", ["lower_extremity"], "Compartimentum anterius cruris", "Anterior compartment of leg", 2643, 95, "HA-G-000010"),
    ("HA-G-000014", ["lower_extremity"], "Compartimentum laterale cruris", "Lateral compartment of leg", 2651, 95, "HA-G-000010"),
    ("HA-G-000015", ["lower_extremity"], "Compartimentum posterius cruris", "Posterior compartment of leg", 2654, 95, "HA-G-000010"),
    ("HA-G-000016", ["foot"], "Musculi pedis", "Muscles of foot", 2669, 96, "HA-G-000010"),
]

# Individual muscles: id, regions, Latin row label, English row label, row,
# printed page, parent group, optional T02 pilot key.
MUSCLES = [
    ("HA-M-000001", ["lower_extremity"], "Musculus gastrocnemius", "Gastrocnemius muscle", 2657, 96, "HA-G-000015", "gastrocnemius"),
    ("HA-M-000002", ["lower_extremity"], "Musculus soleus", "Soleus muscle", 2660, 96, "HA-G-000015", "soleus"),
    ("HA-M-000003", ["lower_extremity"], "Musculus tibialis anterior", "Tibialis anterior muscle", 2644, 95, "HA-G-000013", "tibialis_anterior"),
    ("HA-M-000004", ["lower_extremity"], "Musculus tibialis posterior", "Tibialis posterior muscle", 2666, 96, "HA-G-000015", "tibialis_posterior"),
    ("HA-M-000005", ["lower_extremity"], "Musculus fibularis longus", "Fibularis longus muscle", 2652, 95, "HA-G-000014", "fibularis_longus"),
    ("HA-M-000006", ["lower_extremity"], "Musculus fibularis brevis", "Fibularis brevis muscle", 2653, 95, "HA-G-000014", "fibularis_brevis"),
    ("HA-M-000007", ["eye"], "Musculus rectus superior", "Superior rectus muscle", 2042, 74, "HA-G-000002", None),
    ("HA-M-000008", ["eye"], "Musculus rectus inferior", "Inferior rectus muscle", 2043, 74, "HA-G-000002", None),
    ("HA-M-000009", ["eye"], "Musculus rectus medialis", "Medial rectus muscle", 2044, 74, "HA-G-000002", None),
    ("HA-M-000010", ["eye"], "Musculus rectus lateralis bulbi oculi", "Lateral rectus muscle", 2045, 74, "HA-G-000002", None),
    ("HA-M-000011", ["eye"], "Musculus obliquus superior bulbi oculi", "Superior oblique muscle", 2048, 74, "HA-G-000002", None),
    ("HA-M-000012", ["mastication"], "Masseter", "Masseter muscle", 2105, 77, "HA-G-000003", None),
    ("HA-M-000013", ["mastication"], "Musculus temporalis", "Temporalis muscle", 2108, 77, "HA-G-000003", None),
    ("HA-M-000014", ["mastication"], "Musculus pterygoideus lateralis", "Lateral pterygoid muscle", 2109, 77, "HA-G-000003", None),
    ("HA-M-000015", ["mastication"], "Musculus pterygoideus medialis", "Medial pterygoid muscle", 2113, 77, "HA-G-000003", None),
    ("HA-M-000016", ["tongue"], "Musculus genioglossus", "Genioglossus muscle", 2117, 77, "HA-G-000004", None),
    ("HA-M-000017", ["tongue"], "Musculus hyoglossus", "Hyoglossus muscle", 2118, 77, "HA-G-000004", None),
    ("HA-M-000018", ["tongue"], "Musculus styloglossus", "Styloglossus muscle", 2121, 77, "HA-G-000004", None),
    ("HA-M-000019", ["back"], "Musculus trapezius", "Trapezius muscle", 2226, 81, "HA-G-000005", None),
    ("HA-M-000020", ["back"], "Musculus latissimus dorsi", "Latissimus dorsi muscle", 2231, 81, "HA-G-000005", None),
    ("HA-M-000021", ["back"], "Musculus rhomboideus major", "Rhomboid major muscle", 2232, 81, "HA-G-000005", None),
    ("HA-M-000022", ["back"], "Musculus rhomboideus minor", "Rhomboid minor muscle", 2233, 81, "HA-G-000005", None),
    ("HA-M-000023", ["back"], "Musculus levator scapulae", "Levator scapulae muscle", 2234, 81, "HA-G-000005", None),
    ("HA-M-000024", ["thorax_respiratory"], "Musculus pectoralis major", "Pectoralis major muscle", 2301, 83, "HA-G-000006", None),
    ("HA-M-000025", ["thorax_respiratory"], "Musculus pectoralis minor", "Pectoralis minor muscle", 2305, 83, "HA-G-000006", None),
    ("HA-M-000026", ["thorax_respiratory"], "Musculus subclavius", "Subclavius muscle", 2306, 83, "HA-G-000006", None),
    ("HA-M-000027", ["thorax_respiratory"], "Musculus serratus anterior", "Serratus anterior muscle", 2307, 83, "HA-G-000006", None),
    ("HA-M-000028", ["abdominal_wall"], "Musculus obliquus internus abdominis", "Internal abdominal oblique muscle", 2373, 86, None, None),
    ("HA-M-000029", ["abdominal_wall"], "Musculus transversus abdominis", "Transversus abdominis muscle", 2375, 86, None, None),
    ("HA-M-000030", ["shoulder"], "Musculus deltoideus", "Deltoid muscle", 2452, 89, "HA-G-000008", None),
    ("HA-M-000031", ["shoulder"], "Musculus supraspinatus", "Supraspinatus muscle", 2457, 89, "HA-G-000009", None),
    ("HA-M-000032", ["shoulder"], "Musculus infraspinatus", "Infraspinatus muscle", 2458, 89, "HA-G-000009", None),
    ("HA-M-000033", ["shoulder"], "Musculus teres minor", "Teres minor muscle", 2459, 89, "HA-G-000009", None),
    ("HA-M-000034", ["shoulder"], "Musculus subscapularis", "Subscapularis muscle", 2460, 89, "HA-G-000009", None),
    ("HA-M-000035", ["upper_extremity"], "Musculus biceps brachii", "Biceps brachii muscle", 2464, 89, "HA-G-000007", None),
    ("HA-M-000036", ["upper_extremity"], "Musculus coracobrachialis", "Coracobrachialis muscle", 2468, 89, "HA-G-000007", None),
    ("HA-M-000037", ["upper_extremity"], "Musculus brachialis", "Brachialis muscle", 2469, 89, "HA-G-000007", None),
    ("HA-M-000038", ["upper_extremity"], "Musculus triceps brachii", "Triceps brachii muscle", 2471, 89, "HA-G-000007", None),
    ("HA-M-000039", ["gluteal"], "Musculus gluteus maximus", "Gluteus maximus muscle", 2598, 94, "HA-G-000011", None),
    ("HA-M-000040", ["gluteal"], "Musculus gluteus medius", "Gluteus medius muscle", 2599, 94, "HA-G-000011", None),
    ("HA-M-000041", ["gluteal"], "Musculus gluteus minimus", "Gluteus minimus muscle", 2600, 94, "HA-G-000011", None),
    ("HA-M-000042", ["gluteal"], "Musculus piriformis", "Piriformis muscle", 2604, 94, "HA-G-000012", None),
    ("HA-M-000043", ["gluteal"], "Musculus obturatorius internus", "Obturator internus muscle", 2605, 94, "HA-G-000012", None),
    ("HA-M-000044", ["gluteal"], "Musculus gemellus superior", "Superior gemellus muscle", 2606, 94, "HA-G-000012", None),
    ("HA-M-000045", ["gluteal"], "Musculus gemellus inferior", "Inferior gemellus muscle", 2607, 94, "HA-G-000012", None),
    ("HA-M-000046", ["gluteal"], "Musculus quadratus femoris", "Quadratus femoris muscle", 2608, 94, "HA-G-000012", None),
    ("HA-M-000047", ["foot"], "Musculus flexor hallucis brevis", "Flexor hallucis brevis muscle", 2673, 96, "HA-G-000016", None),
    ("HA-M-000048", ["foot"], "Musculus adductor hallucis", "Adductor hallucis muscle", 2676, 96, "HA-G-000016", None),
]

# Parts: id, region IDs, Latin row label, English row label, row, page,
# parent muscle ID, kind (head/part).
PARTS = [
    ("HA-P-000001", ["lower_extremity"], "Caput laterale musculi gastrocnemii", "Lateral head of gastrocnemius", 2658, 96, "HA-M-000001", "head"),
    ("HA-P-000002", ["lower_extremity"], "Caput mediale musculi gastrocnemii", "Medial head of gastrocnemius", 2659, 96, "HA-M-000001", "head"),
    ("HA-P-000003", ["mastication"], "Pars superficialis masseteris", "Superficial part of masseter", 2106, 77, "HA-M-000012", "part"),
    ("HA-P-000004", ["mastication"], "Pars profunda masseteris", "Deep part of masseter", 2107, 77, "HA-M-000012", "part"),
    ("HA-P-000005", ["mastication"], "Caput superius musculi pterygoidei lateralis", "Superior head of lateral pterygoid muscle", 2110, 77, "HA-M-000014", "head"),
    ("HA-P-000006", ["mastication"], "Caput inferius musculi pterygoidei lateralis", "Inferior head of lateral pterygoid muscle", 2111, 77, "HA-M-000014", "head"),
    ("HA-P-000007", ["mastication"], "Caput profundum musculi pterygoidei medialis", "Deep head of medial pterygoid muscle", 2114, 77, "HA-M-000015", "head"),
    ("HA-P-000008", ["mastication"], "Caput superficiale musculi pterygoidei medialis", "Superficial head of medial pterygoid muscle", 2115, 77, "HA-M-000015", "head"),
    ("HA-P-000009", ["back"], "Pars descendens musculi trapezii", "Descending part of trapezius muscle", 2227, 81, "HA-M-000019", "part"),
    ("HA-P-000010", ["back"], "Pars transversa musculi trapezii", "Transverse part of trapezius muscle", 2228, 81, "HA-M-000019", "part"),
    ("HA-P-000011", ["back"], "Pars ascendens musculi trapezii", "Ascending part of trapezius muscle", 2229, 81, "HA-M-000019", "part"),
    ("HA-P-000012", ["thorax_respiratory"], "Pars clavicularis musculi pectoralis majoris", "Clavicular head of pectoralis major muscle", 2302, 83, "HA-M-000024", "head"),
    ("HA-P-000013", ["thorax_respiratory"], "Pars sternocostalis musculi pectoralis majoris", "Sternocostal head of pectoralis major muscle", 2303, 83, "HA-M-000024", "head"),
    ("HA-P-000014", ["shoulder"], "Pars clavicularis musculi deltoidei", "Clavicular part of deltoid muscle", 2453, 89, "HA-M-000030", "part"),
    ("HA-P-000015", ["shoulder"], "Pars acromialis musculi deltoidei", "Acromial part of deltoid muscle", 2454, 89, "HA-M-000030", "part"),
    ("HA-P-000016", ["shoulder"], "Pars spinalis scapularis musculi deltoidei", "Scapular spinal part of deltoid muscle", 2455, 89, "HA-M-000030", "part"),
    ("HA-P-000017", ["upper_extremity"], "Caput longum musculi bicipitis brachii", "Long head of biceps brachii", 2465, 89, "HA-M-000035", "head"),
    ("HA-P-000018", ["upper_extremity"], "Caput breve musculi bicipitis brachii", "Short head of biceps brachii", 2466, 89, "HA-M-000035", "head"),
    ("HA-P-000019", ["upper_extremity"], "Caput longum musculi tricipitis brachii", "Long head of triceps brachii", 2472, 89, "HA-M-000038", "head"),
    ("HA-P-000020", ["upper_extremity"], "Caput laterale musculi tricipitis brachii", "Lateral head of triceps brachii", 2473, 89, "HA-M-000038", "head"),
    ("HA-P-000021", ["upper_extremity"], "Caput mediale musculi tricipitis brachii", "Medial head of triceps brachii", 2474, 89, "HA-M-000038", "head"),
]

# Each tuple represents an exact item label observed in the indexed primary PDF.
# Parenthetical items, where classification is ambiguous, are held in the gap queue.

def row_ref(row: int, page: int) -> dict:
    return {
        "scheme": "FIPAT TA2 Part 2 table row",
        "identifier": f"row {row}; printed page {page}",
        "edition": EDITION,
        "uri": PDF_URL,
    }

def item_object(ident: str, kind: str, regions: list[str], latin: str, english: str,
                row: int, page: int, parent: str | None, part_kind: str | None = None) -> dict:
    entity_type = {"group": "muscle_group", "muscle": "individual_muscle", "part": "muscle_part"}[kind]
    obj = {
        "id": ident,
        "entityType": entity_type,
        "regionIds": regions,
        "standardRefs": [row_ref(row, page)],
        "applicability": {"populations": ["adult_human"], "notes": "Population scope inherited from T01; source-specific applicability not reviewed."},
    }
    if parent:
        obj["parentId"] = parent
    return {"concept": obj, "kind": kind, "latin": latin, "english": english,
            "row": row, "page": page, "parentId": parent, "partKind": part_kind}

def build():
    rows = []
    for ident, regions, latin, english, row, page, parent in GROUPS:
        rows.append(item_object(ident, "group", regions, latin, english, row, page, parent))
    for ident, regions, latin, english, row, page, parent, pilot in MUSCLES:
        rows.append(item_object(ident, "muscle", regions, latin, english, row, page, parent))
        rows[-1]["pilotKey"] = pilot
    for ident, regions, latin, english, row, page, parent, part_kind in PARTS:
        rows.append(item_object(ident, "part", regions, latin, english, row, page, parent, part_kind))
    rows.sort(key=lambda item: item["concept"]["id"])

    concepts = [r["concept"] for r in rows]
    row_to_evidence = {}
    evidence = []
    terms = []
    term_crosswalk = []
    term_seq = 1
    for r in rows:
        row, page = r["row"], r["page"]
        evid = row_to_evidence.get(row)
        if evid is None:
            evid = f"EV-TA2-P2-R{row}"
            row_to_evidence[row] = evid
            evidence.append({
                "id": evid,
                "sourceId": "FIPAT_TA2",
                "locator": f"TA2 Part 2, printed page {page}, table row {row}; exact row excerpt surfaced in FIPAT-hosted PDF search index on 2026-09-25. PDF binary not locally acquired or visually checked.",
                "supportedClaimIds": [],
                "evidenceKind": "primary",
            })
        for lang, script, value, role in [
            ("la", "Latn", r["latin"], "standard"),
            ("en", "Latn", r["english"], "standard"),
        ]:
            terms.append({
                "id": f"HA-T-{term_seq:06d}", "conceptId": r["concept"]["id"],
                "language": lang, "script": script, "text": value,
                "termRole": role, "edition": f"TA2 2nd ed. (2019), Part 2, row {row}",
                "evidenceIds": [evid], "reviewState": "needs_review",
            })
            term_crosswalk.append({"termId": f"HA-T-{term_seq:06d}", "conceptId": r["concept"]["id"],
                                   "sourceLanguage": lang, "sourceTextObserved": value,
                                   "sourceTermCategory": "cell role pending local PDF visual verification",
                                   "sourceEvidenceId": evid})
            term_seq += 1
        for lang, script, field in [("ko", "Hang", "Korean Hangul"), ("ko", "Hani", "Korean Hanja")]:
            terms.append({
                "id": f"HA-T-{term_seq:06d}", "conceptId": r["concept"]["id"],
                "language": lang, "script": script, "text": None,
                "termRole": "standard", "edition": None, "evidenceIds": [],
                "reviewState": "held",
                "missingReason": f"{field} term not entered: primary Korean anatomical terminology source and exact item locator were not available; no translation or inferred name was supplied.",
            })
            term_crosswalk.append({"termId": f"HA-T-{term_seq:06d}", "conceptId": r["concept"]["id"],
                                   "sourceLanguage": lang, "sourceTextObserved": None,
                                   "sourceTermCategory": "missing_unverified", "sourceEvidenceId": None})
            term_seq += 1

    scope_regions = SCOPE["regions"]
    used_regions = {rid for c in concepts for rid in c["regionIds"]}
    coverage = {
        "head": "partial_located_group_and_eye_rows",
        "face": "not_enumerated_in_captured_source_rows",
        "mastication": "partial_located_group_and_selected_muscles",
        "eye": "partial_located_group_and_selected_muscles",
        "tongue": "partial_located_group_and_selected_muscles",
        "pharynx": "not_enumerated_in_captured_source_rows",
        "larynx": "not_enumerated_in_captured_source_rows",
        "neck": "not_enumerated_in_captured_source_rows",
        "back": "partial_located_group_and_selected_muscles",
        "thorax_respiratory": "partial_located_group_and_selected_muscles",
        "abdominal_wall": "partial_located_muscle_rows_no_full_region_extract",
        "pelvic_floor_perineum": "not_enumerated_scope_match_unresolved",
        "shoulder": "partial_located_group_and_selected_muscles",
        "upper_extremity": "partial_located_group_and_selected_muscles",
        "hand": "not_enumerated_in_captured_source_rows",
        "gluteal": "partial_located_group_and_selected_muscles",
        "lower_extremity": "partial_located_groups_and_selected_muscles",
        "foot": "partial_located_group_and_selected_muscles",
    }
    region_entities = [{"id": "HA-R-ROOT", "label": "Adult human skeletal muscle scope (T01)",
                        "notes": "Project scope root only; not a TA2 anatomical region heading."}]
    region_entities.extend({"id": r["id"], "parentId": "HA-R-ROOT", "label": r["label"],
                           "notes": r.get("note") or f"T01 scope region; coverage={coverage[r['id']]}."}
                          for r in scope_regions)
    region_tree = {
        "schema_version": "0.1", "revision": "T04-region-tree-partial-v1",
        "status": "scope_complete_catalog_partial", "root_id": "HA-R-ROOT",
        "source_of_region_nodes": "atlas-data/manifests/scope.json (T01-policy-v1)",
        "hierarchy_policy": "T01's 18 scope regions are direct children of a synthetic project root. This is not a claim that TA2 uses the same region hierarchy; no unsourced subregion nodes were invented.",
        "regions": [{"id": r["id"], "label": r["label"], "parentId": "HA-R-ROOT",
                     "includedByT01": True, "coverageStatus": coverage[r["id"]],
                     "partialCatalogEntryCount": sum(r["id"] in c["regionIds"] for c in concepts)}
                    for r in scope_regions],
        "t03RegionEntities": region_entities,
    }

    fma_assets = [a for a in ASSETS["acquiredAssets"] if a["kind"] == "muscle"]
    pilot_ids = {r["pilotKey"]: r["concept"]["id"] for r in rows if r.get("pilotKey")}
    external_mappings = []
    for key, concept_id in pilot_ids.items():
        records = [p for p in ASSETS["pilotMuscles"] if p["pilot_concept"] == key]
        for rec in records:
            entries = [a for a in fma_assets if a["concept_id"] == rec["concept_id"]]
            for asset in entries:
                target_id = concept_id
                relation = "provisional_name_match"
                if key == "gastrocnemius":
                    target_id = "HA-P-000002" if rec["part"] == "medial head" else "HA-P-000001"
                    relation = "provisional_head_name_match"
                external_mappings.append({
                    "stableConceptId": target_id,
                    "sourceId": "BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0",
                    "externalConceptId": rec["concept_id"],
                    "externalRepresentationId": rec["representation_id"],
                    "elementFileId": rec["element_file_id"],
                    "localAsset": rec["local_asset"],
                    "sourceName": rec["source_name"],
                    "support": rec["support"],
                    "sourceTableLocators": rec["table_rows"],
                    "relationStatus": relation + "; no independent anatomy review in T04",
                })
    catalog_rows = [{
        "stableConceptId": r["concept"]["id"],
        "entityType": r["concept"]["entityType"],
        "regionIds": r["concept"]["regionIds"],
        "parentConceptId": r.get("parentId"),
        "sourceId": "FIPAT_TA2",
        "edition": EDITION,
        "part": "Part 2, Muscular System",
        "printedPage": r["page"], "tableRow": r["row"],
        "latinTextObservation": r["latin"], "englishTextObservation": r["english"],
        "termCellRoleStatus": "unverified_without_local_visual_review_of_the_source_table",
        "reviewState": "needs_review",
        "denominatorTreatment": "count_once" if r["concept"]["entityType"] == "individual_muscle" else "exclude_from_individual_muscle_denominator",
        **({"partKind": r["partKind"]} if r["kind"] == "part" else {}),
    } for r in rows]
    crosswalk = {
        "schema_version": "0.1", "revision": "T04-source-crosswalk-partial-v1",
        "status": "partial_source_row_crosswalk_pending_visual_review",
        "ta2SourceId": "FIPAT_TA2", "ta2Part2Pdf": PDF_URL,
        "sourceAccess": "Official FIPAT-hosted PDF search index returned exact table-row excerpts and printed page labels. Original PDF binary could not be downloaded in this environment (DNS failure); no PDF was saved or visually inspected.",
        "termCrosswalkPolicy": "Observed source strings are retained as unreviewed Latin/English source-term observations. Exact table-column role (official/equivalent/synonym) remains unverified in the local rendering; no Korean/Hanja translation is inferred.",
        "catalogItems": catalog_rows,
        "termRecords": term_crosswalk,
        "bodyParts3dMappings": external_mappings,
        "wholeGastrocnemiusMapping": {
            "stableConceptId": "HA-M-000001",
            "status": "no_whole_muscle_asset_in_T02; two right-head meshes map only to child part IDs",
            "childPartMappings": ["HA-P-000001", "HA-P-000002"],
        },
        "rowExcerptEvidence": [
            {"evidenceId": f"EV-TA2-P2-R{r['row']}", "printedPage": r["page"], "tableRow": r["row"], "sourceUrl": PDF_URL}
            for r in sorted(rows, key=lambda x: x["row"])
        ],
    }

    counts = {k: sum(c["entityType"] == v for c in concepts) for k, v in {
        "individualMuscles": "individual_muscle", "groups": "muscle_group",
        "parts": "muscle_part", "variants": "variant"}.items()}
    status = {
        "schema_version": "0.1", "revision": "T04-partial-catalog-v1",
        "status": "partial_source_index_extract", "taskStatus": "complete_with_partial_catalog",
        "catalogComplete": False, "wholeBodyGate": "blocked",
        "denominatorFrozen": False, "wholeBodyIndividualMuscleCount": None,
        "partialEntryCounts": counts,
        "partialSourceRows": len(evidence),
        "sourceEdition": EDITION,
        "sourceBinaryAcquired": False,
        "reasons": [
            "The exact official TA2 Part 2 PDF could not be acquired locally; the accessible official search index exposes only excerpts.",
            "The 18-region catalog is not systematically enumerated from a full source table.",
            "Official/equivalent/synonym table-cell roles have not been visually checked against the PDF.",
            "The Korean primary nomenclature source and exact edition/item locators remain unavailable.",
        ],
        "nextAllowedWork": "T05 pilot text may proceed using the six stable individual-muscle IDs below, while retaining missing Korean/Hanja terms and all anatomy claims as unreviewed.",
        "pilotConceptIds": {k: pilot_ids[k] for k in sorted(pilot_ids)},
        "notImplied": ["anatomical review", "complete muscle denominator", "public reuse permission", "clinical readiness"],
    }

    dataset = {
        "schemaVersion": "1.0.0", "revision": "T04-TA2-2019-partial-v1",
        "entities": {
            "regions": region_entities, "muscleConcepts": concepts,
            "instances": [], "muscleParts": [], "terms": terms, "structures": [],
            "attachments": [], "spatialAnnotations": [], "meshAssets": [],
            "meshMappings": [], "jointActions": [], "innervations": [],
            "assessments": [], "sources": [{
                "id": "FIPAT_TA2", "title": "Terminologia Anatomica, 2nd edition (TA2), Part 2",
                "authors": ["Federative International Programme on Anatomical Terminologies (FIPAT)"],
                "edition": EDITION, "year": 2019, "urlOrLocalRef": PDF_URL,
                "accessDate": "2026-09-25",
                "license": {
                    "id": "LIC-FIPAT-CC-BY-ND-4.0", "name": "Creative Commons Attribution-NoDerivatives 4.0 International",
                    "spdxId": "CC-BY-ND-4.0", "allowedUses": ["internal"],
                    "attributionRequired": True,
                    "attributionText": "FIPAT/IFAA, Terminologia Anatomica, 2nd edition (TA2), Part 2; row and printed-page locators are recorded per item. https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf",
                    "derivativesAllowed": False, "redistributionAllowed": False,
                },
            }],
            "evidence": evidence, "claims": [], "reviews": [], "modelElements": [],
        },
        "publicationManifests": [],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    for name, obj in [("canonical-catalog.json", dataset), ("region-tree.json", region_tree),
                      ("source-crosswalk.json", crosswalk), ("catalog-status.json", status)]:
        (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"concepts": len(concepts), "terms": len(terms), "evidenceRows": len(evidence), "counts": counts,
                      "pilotConceptIds": status["pilotConceptIds"]}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    build()
