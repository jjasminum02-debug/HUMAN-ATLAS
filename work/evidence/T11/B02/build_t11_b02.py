"""Build the bounded T11-B02 terminology evidence and display-name overlay."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CHECKED = "2026-09-25"
FIPAT_ID = "fipat-ta2-b02-index"
FIPAT_URL = "https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf"
FIPAT_EDITION = "Terminologia Anatomica, second edition (TA2), Part 2; online edition published 2019; hosted PDF path dated 2020-09."
KMLE_EDITION = "KMLE web aggregation; underlying dictionary editions/publication years are not exposed on the relevant page."

NAMES_PATH = ROOT / "atlas-data/terminology/learning-names.json"
BATCH_PATH = ROOT / "atlas-data/terminology/term-review-batches.json"

SOURCES = {
    FIPAT_ID: {
        "title": "FIPAT Terminologia Anatomica, second edition, Part 2 — B02 rows",
        "url": FIPAT_URL,
        "locator": "Part 2 printed pp. 74, 77, 81, 83, 89, 94; rows 2040, 2041, 2104, 2116, 2225, 2299, 2450, 2451, 2456, 2592. Official web search index exposes row text; original PDF open returned HTTP 502 in this check; no local visual review.",
        "edition": FIPAT_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "official_pdf_search_index_only; direct PDF fetch failed HTTP 502; no page image or local visual review",
        "scope": "Terminology observations only; exact table-column role and anatomical equivalence remain unreviewed.",
    },
    "kmle-b02-head-groups": {
        "title": "KMLE indexed terminology: head and mastication group names",
        "url": "https://m.kmle.co.kr/search.php?Page=4&Search=group+of+muscles",
        "locator": "Search-index excerpt, result section for group of muscles: 'muscles of head / musculi capitis' with 머리근육, 두부근(頭部筋); used only for the exact observed spellings.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "search_result_excerpt_only",
        "scope": "Terminology spelling only; no anatomical claim imported.",
    },
    "kmle-b02-extraocular": {
        "title": "KMLE extraocular terminology page",
        "url": "https://m.kmle.co.kr/search.php?Search=extraocular",
        "locator": "Opened HTML text: current association result 'extraocular muscle' → 바깥눈근육, 외안근; legacy association section gives extraocular muscles → 외안근(外眼筋). Opened lines 22–24 and 55–61 in the captured page text.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "opened_html_page_text",
        "scope": "Terminology spelling only; underlying dictionary revision is not exposed.",
    },
    "kmle-b02-mastication": {
        "title": "KMLE indexed terminology: muscles of mastication",
        "url": "https://m.kmle.co.kr/search.php?Page=4&Search=transversospinalis+muscles",
        "locator": "Search-index excerpt for 'muscles of mastication': 저작근(咀嚼筋); KMLE's named current Korean anatomy-term section also surfaced 씹기근육 in the separate 'musc' result (see kmle-b02-muscle-terms).",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "search_result_excerpt_only",
        "scope": "Terminology spelling only; no anatomical claim imported.",
    },
    "kmle-b02-muscle-terms": {
        "title": "KMLE indexed Korean anatomy terminology: muscle groups",
        "url": "https://m.kmle.co.kr/search.php?Search=musc",
        "locator": "Search-index excerpt, named 대한해부학회 dictionary section: Muscles of mastication → 씹기근육 [old term] 저작근; Muscles of tongue → 혀근육 [old term] 설근; Pectoralis muscles → 가슴근육 [old term] 흉근.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "search_result_excerpt_only",
        "scope": "Observed terminology and collision notes only; edition/revision of the indexed dictionary is not exposed.",
    },
    "kmle-b02-back-groups": {
        "title": "KMLE indexed terminology: generic muscles of back",
        "url": "https://m.kmle.co.kr/search.php?Search=back",
        "locator": "Search-index excerpt gives generic 'muscles of back / musculi dorsi' → 등근육, 배부근(背部筋). It does not name the narrower TA2 hypaxial-muscle group.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "search_result_excerpt_only",
        "scope": "Near-match used to prevent conflating a generic back group with hypaxial muscles.",
    },
    "kmle-b02-thorax": {
        "title": "KMLE indexed terminology: muscles of thorax",
        "url": "https://m.kmle.co.kr/search.php?Search=thorax",
        "locator": "Search-index excerpt, old 대한의협 3 section: 'muscles of thorax / musculi thoracis' → 가슴근육, 흉부근(胸部筋). The '가슴근육' string also appears under Pectoralis muscles in the KMLE anatomy-dictionary index, so it is not adopted as a unique search alias.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "search_result_excerpt_only",
        "scope": "Legacy terminology spelling only; group-level Korean term remains unresolved because of a lexical collision.",
    },
    "kmle-b02-upper-limb": {
        "title": "KMLE indexed terminology: muscles of upper limb",
        "url": "https://m.kmle.co.kr/search.php?Page=2&Search=upper",
        "locator": "Search-index excerpt row 'muscles of upper limb' → 팔근육; no Hanja value shown in the row.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "search_result_excerpt_only",
        "scope": "Terminology spelling only; exact underlying dictionary revision is not exposed.",
    },
    "kmle-b02-scapulohumeral": {
        "title": "KMLE indexed terminology: scapulohumeral modifier",
        "url": "https://m.kmle.co.kr/search.php?FuzzyTrack=scapula&IsFuzzy=YES&Search=scapulo",
        "locator": "Search-index excerpt lists the modifier 'scapulohumeral' → 어깨위팔-, 견갑상완(골)- and reflex entries; no exact Korean muscle-group entry is exposed. The modifier was not composed into a group name.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "search_result_excerpt_only",
        "scope": "Negative/near-match lookup only; not an attested name for the TA2 group row.",
    },
    "kmle-b02-rotator-cuff": {
        "title": "KMLE opened rotator-cuff terminology page",
        "url": "https://m.kmle.co.kr/search.php?Search=rotator+cuff",
        "locator": "Opened HTML text: current term rotator cuff → 돌림근띠, 회전근개 (lines 14–16); legacy rows include 근육둘레띠 and 回旋腱板 for the cuff term (lines 77–87 and 132–138). This does not attest that any one term names the complete TA2 muscle-group entity.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "opened_html_page_text",
        "scope": "Related-term observation only; group equivalence was not established.",
    },
    "kmle-b02-lower-limb": {
        "title": "KMLE indexed terminology: muscles of lower limb",
        "url": "https://m.kmle.co.kr/search.php?Page=4&Search=transversospinalis+muscles",
        "locator": "Search-index excerpt row 'muscles of lower limb' → 다리근육; exact dictionary edition is not exposed.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "search_result_excerpt_only",
        "scope": "Terminology spelling only; no anatomical claim imported.",
    },
}

# Values are populated only where the checked source directly exposed the term.
# The TA2 table-cell role is retained as unverified in each field-evidence row.
KOREAN = {
    "HA-G-000001": {
        "label": "두부근", "korean": "머리근육", "hanja": "頭部筋",
        "labelSource": ["kmle-b02-head-groups"], "koreanSource": ["kmle-b02-head-groups"], "hanjaSource": ["kmle-b02-head-groups"],
    },
    "HA-G-000002": {
        "label": "외안근", "korean": "바깥눈근육", "hanja": "外眼筋",
        "labelSource": ["kmle-b02-extraocular"], "koreanSource": ["kmle-b02-extraocular"], "hanjaSource": ["kmle-b02-extraocular"],
    },
    "HA-G-000003": {
        "label": "저작근", "korean": "씹기근육", "hanja": "咀嚼筋",
        "labelSource": ["kmle-b02-mastication"], "koreanSource": ["kmle-b02-muscle-terms"], "hanjaSource": ["kmle-b02-mastication"],
    },
    "HA-G-000004": {
        "label": "혀근육", "korean": "혀근육", "hanja": None,
        "labelSource": ["kmle-b02-muscle-terms"], "koreanSource": ["kmle-b02-muscle-terms"], "hanjaSource": ["kmle-b02-muscle-terms"],
        "hanjaMissing": "KMLE index shows the older Hangul form 설근, but no source Hanja for this group; the form is also lexically ambiguous, so neither 舌筋 nor 설근 was added.",
    },
    "HA-G-000005": {
        "label": None, "korean": None, "hanja": None,
        "labelSource": ["kmle-b02-back-groups"], "koreanSource": ["kmle-b02-back-groups"], "hanjaSource": ["kmle-b02-back-groups"],
        "labelMissing": "The accessible KMLE result attests only generic muscles of back / 등근육, not the narrower TA2 hypaxial group. No Korean or Hanja translation was inferred.",
        "koreanMissing": "No source-attested Korean form for this exact hypaxial group was found in the checked results; the generic back term is not equivalent.",
        "hanjaMissing": "No source Hanja for the hypaxial group was found; 背部筋 belongs to the generic back term and was not mapped.",
    },
    "HA-G-000006": {
        "label": "흉부근", "korean": None, "hanja": "胸部筋",
        "labelSource": ["kmle-b02-thorax"], "koreanSource": ["kmle-b02-thorax", "kmle-b02-muscle-terms"], "hanjaSource": ["kmle-b02-thorax"],
        "koreanMissing": "The indexed legacy row also gives 가슴근육, but KMLE's current anatomy-term result uses 가슴근육 for Pectoralis muscles. Held out as a non-unique group alias pending human terminology review.",
    },
    "HA-G-000007": {
        "label": "팔근육", "korean": "팔근육", "hanja": None,
        "labelSource": ["kmle-b02-upper-limb"], "koreanSource": ["kmle-b02-upper-limb"], "hanjaSource": ["kmle-b02-upper-limb"],
        "hanjaMissing": "No Hanja value is exposed for this group in the checked result; none was generated from Korean syllables.",
    },
    "HA-G-000008": {
        "label": None, "korean": None, "hanja": None,
        "labelSource": ["kmle-b02-scapulohumeral"], "koreanSource": ["kmle-b02-scapulohumeral"], "hanjaSource": ["kmle-b02-scapulohumeral"],
        "labelMissing": "The accessible result attests only the adjective scapulohumeral → 어깨위팔-/견갑상완(골)-, not a Korean name for the group. No compositional group label was fabricated.",
        "koreanMissing": "No exact group-name item was located; the adjective alone does not establish a preferred group term.",
        "hanjaMissing": "No Hanja value for the exact group was located; no characters were composed from the modifier.",
    },
    "HA-G-000009": {
        "label": None, "korean": None, "hanja": None,
        "labelSource": ["kmle-b02-rotator-cuff"], "koreanSource": ["kmle-b02-rotator-cuff"], "hanjaSource": ["kmle-b02-rotator-cuff"],
        "labelMissing": "The opened page attests rotator cuff / 회전근개 / 돌림근띠 as a related cuff term, but not an exact preferred Korean label for the TA2 muscles group. It is held pending group-level equivalence review.",
        "koreanMissing": "The Korean cuff forms are recorded as related candidates only; group-level equivalence is unresolved.",
        "hanjaMissing": "回旋腱板 is displayed for the cuff term, not specifically for this muscle-group entry; it was not attached to this ID.",
    },
    "HA-G-000010": {
        "label": "다리근육", "korean": "다리근육", "hanja": None,
        "labelSource": ["kmle-b02-lower-limb"], "koreanSource": ["kmle-b02-lower-limb"], "hanjaSource": ["kmle-b02-lower-limb"],
        "hanjaMissing": "No Hanja value is exposed for this group in the checked result; none was generated from Korean syllables.",
    },
}

DISPLAY_ENGLISH = {
    "HA-G-000001": "Muscles of head",
    "HA-G-000002": "Extraocular muscles",
    "HA-G-000003": "Masticatory muscles",
    "HA-G-000004": "Muscles of tongue",
    "HA-G-000005": "Hypaxial muscles of back",
    "HA-G-000006": "Muscles of thorax",
    "HA-G-000007": "Muscles of upper limb",
    "HA-G-000008": "Scapulohumeral muscles",
    "HA-G-000009": "Rotator cuff muscles",
    "HA-G-000010": "Muscles of lower limb",
}

LABEL_STATES = {
    "HA-G-000001": "attested_legacy_customary_name",
    "HA-G-000002": "attested_current_and_legacy_forms",
    "HA-G-000003": "attested_legacy_customary_name",
    "HA-G-000004": "attested_current_name",
    "HA-G-000006": "attested_legacy_customary_name",
    "HA-G-000007": "attested_current_name",
    "HA-G-000010": "attested_current_name",
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def evidence(source_id: str, locator: str, edition: str, mode: str):
    return {
        "sourceId": source_id,
        "locator": locator,
        "verificationMode": mode,
        "sourceEdition": edition,
        "checkedDate": CHECKED,
    }


def source_ev(source_id: str, locator: str | None = None):
    source = SOURCES[source_id]
    return evidence(source_id, locator or source["locator"], source["edition"], source["verificationMode"])


def main():
    names = read_json(NAMES_PATH)
    batches = read_json(BATCH_PATH)
    rows = [row for row in batches["canonicalCoverage"] if row["batchId"] == "T11-B02"]
    expected_ids = [f"HA-G-{i:06d}" for i in range(1, 11)]
    if [row["id"] for row in rows] != expected_ids:
        raise SystemExit("T11-B02 assignment no longer matches the authorized 10 group IDs")
    if any(row["status"] != "not_started" for row in rows):
        raise SystemExit("T11-B02 is already modified; refusing a non-idempotent rebuild")

    source_crosswalk = read_json(ROOT / "atlas-data/catalog/source-crosswalk.json")
    raw_terms = {term["conceptId"]: term for term in source_crosswalk["termRecords"]}
    # Every selected B02 row has one Latin and one English observation in the T04 crosswalk.
    for identifier in expected_ids:
        terms = [term for term in source_crosswalk["termRecords"] if term["conceptId"] == identifier]
        if not {term["sourceLanguage"] for term in terms} >= {"la", "en"}:
            raise SystemExit(f"T04 crosswalk is missing English/Latin term rows for {identifier}")

    names["sources"].update(SOURCES)
    concepts = {item["id"]: item for item in read_json(ROOT / "atlas-data/catalog/canonical-catalog.json")["entities"]["muscleConcepts"]}
    new_entries = []
    flat_field_evidence = []
    records = []

    for row in rows:
        identifier = row["id"]
        loc = row["sourceCrosswalkLocator"]
        latin_value = loc["latinTextObservation"]
        english_observation = loc["englishTextObservation"]
        english_value = DISPLAY_ENGLISH[identifier]
        values = KOREAN[identifier]
        concept = concepts[identifier]

        la_ev = source_ev(FIPAT_ID, f"TA2 Part 2 printed p. {loc['printedPage']}, table row {loc['tableRow']}; Latin observation: {latin_value!r}; column role remains unverified.")
        en_ev = source_ev(FIPAT_ID, f"TA2 Part 2 printed p. {loc['printedPage']}, table row {loc['tableRow']}; English observation: {english_observation!r}; column role remains unverified.")

        def korean_evidence(key: str):
            source_ids = values.get(key + "Source", [])
            output = []
            for sid in source_ids:
                locator = SOURCES[sid]["locator"]
                output.append(source_ev(sid, locator))
            return output

        def field(field_name, value, state, evs, missing_reason=None, source_value=None):
            record = {
                "entryId": identifier,
                "field": field_name,
                "value": value,
                "state": state,
                "evidence": evs,
                "sourceValue": source_value,
                "missingReason": missing_reason,
                "humanAnatomyReviewStatus": "not_performed",
                "humanReviewed": False,
            }
            flat_field_evidence.append(record)
            return record

        label = values["label"]
        korean = values["korean"]
        hanja = values["hanja"]
        label_evidence = korean_evidence("label")
        if label is None:
            label_ev = field("label", None, "missing_exact_korean_group_name", label_evidence, values.get("labelMissing"))
        else:
            label_ev = field("label", label, LABEL_STATES[identifier], label_evidence, source_value=label)

        if korean is None:
            korean_ev = field("korean", None, "missing_or_held_korean_equivalent", korean_evidence("korean"), values.get("koreanMissing"))
        else:
            korean_ev = field("korean", korean, "attested_current_name", korean_evidence("korean"), source_value=korean)

        if hanja is None:
            hanja_ev = field("hanja", None, "missing_or_not_group_specific", korean_evidence("hanja"), values.get("hanjaMissing"))
        else:
            hanja_ev = field("hanja", hanja, "attested_source_hanja", korean_evidence("hanja"), source_value=hanja)

        english_ev = field("english", english_value, "TA2_source_observation_case_normalized_cell_role_unverified", [en_ev], source_value=english_observation)
        latin_ev = field("aliases[0]", latin_value, "TA2_source_observation_cell_role_unverified", [la_ev], source_value=latin_value)
        item_evidence = [label_ev, korean_ev, hanja_ev, english_ev, latin_ev]
        raw = [term for term in source_crosswalk["termRecords"] if term["conceptId"] == identifier]
        english_rows = [term for term in raw if term["sourceLanguage"] == "en"]
        latin_rows = [term for term in raw if term["sourceLanguage"] == "la"]
        if len(english_rows) != 1 or len(latin_rows) != 1:
            raise SystemExit(f"Expected exactly one existing TA2 English/Latin row for {identifier}")

        record = {
            "id": identifier,
            "isCanonical": True,
            "entityType": "muscle_group",
            "parentId": concept.get("parentId"),
            "lookupOnly": False,
            "canonicalStatus": "canonical_existing_id",
            "canonicalSourceRow": {"sourceId": "FIPAT_TA2", "tableRow": loc["tableRow"], "printedPage": loc["printedPage"]},
            "displayField": "label",
            "displayValue": label,
            "fieldEvidence": item_evidence,
            "unadoptedCandidates": [],
            "webVerificationStatus": "web_checked_with_gaps",
            "humanAnatomyReviewStatus": "not_performed",
            "humanReviewer": None,
            "humanReviewed": False,
            "fieldEvidenceCount": len(item_evidence),
        }
        if identifier == "HA-G-000004":
            record["unadoptedCandidates"].append({
                "field": "hanja/aliases",
                "value": "설근",
                "state": "ambiguous_legacy_form_held",
                "evidence": korean_evidence("hanja"),
                "reason": "Indexed as an older form for muscles of tongue, but no source Hanja is exposed and the string is ambiguous; not added to display or search aliases.",
            })
        if identifier == "HA-G-000005":
            record["unadoptedCandidates"].append({
                "field": "label/korean/hanja",
                "value": "등근육 / 배부근(背部筋)",
                "state": "generic_back_near_match_held",
                "evidence": [source_ev("kmle-b02-back-groups")],
                "reason": "The source row is generic muscles of back, not the exact hypaxial group in the assigned TA2 row.",
            })
        if identifier == "HA-G-000006":
            record["unadoptedCandidates"].append({
                "field": "korean",
                "value": "가슴근육",
                "state": "lexical_collision_held",
                "evidence": [source_ev("kmle-b02-thorax"), source_ev("kmle-b02-muscle-terms")],
                "reason": "The same Korean spelling is indexed for Pectoralis muscles; it is withheld as a unique synonym for the broader thorax group.",
            })
        if identifier == "HA-G-000008":
            record["unadoptedCandidates"].append({
                "field": "label/korean",
                "value": "어깨위팔-",
                "state": "modifier_only_not_group_name",
                "evidence": [source_ev("kmle-b02-scapulohumeral")],
                "reason": "Only the adjectival modifier was located; no group label is synthesized from it.",
            })
        if identifier == "HA-G-000009":
            record["unadoptedCandidates"].append({
                "field": "label/korean/hanja",
                "value": "회전근개 / 돌림근띠 / 回旋腱板",
                "state": "related_cuff_term_not_group_equivalence",
                "evidence": [source_ev("kmle-b02-rotator-cuff")],
                "reason": "The opened source displays these for the cuff term but does not establish a field-specific synonym for the TA2 muscle-group entity.",
            })

        if label is not None:
            overlay = {
                "id": identifier,
                "label": label,
                "korean": korean or "",
                "english": english_value,
                "hanja": hanja,
                "aliases": [latin_value],
                "sourceIds": sorted(set([FIPAT_ID, *values.get("labelSource", [])])),
                "parentId": concept.get("parentId"),
                "entityType": "muscle_group",
                "lookupOnly": False,
                "status": "web_attested_with_gaps",
                "humanReviewed": False,
                "hanjaNote": values.get("hanjaMissing"),
            }
            new_entries.append(overlay)
        records.append(record)

    names["entries"].extend(new_entries)
    names["revision"] = "T11-B02-web-attested-terms-v1"
    names["accessedAt"] = CHECKED
    names.setdefault("notes", []).append("T11-B02: 10 existing muscle_group IDs received field-level TA2 index observations; 7 Korean display labels are source-attested and 3 group labels remain withheld. No human anatomy review was performed.")

    for source_record in SOURCES.values():
        # Keep the existing lightweight registry conventions and the full B02 access metadata.
        source_record.setdefault("url", None)

    for row, record in zip(rows, records):
        row["status"] = "web_checked_with_gaps"
        row["statusReason"] = (
            "English/Latin source-index terms and checked Korean/Hanja fields are recorded in this B02 ledger; "
            "field gaps/collisions remain explicit and human anatomy review was not performed."
        )

    for batch in batches["batchOrder"]:
        if batch["batchId"] == "T11-B02":
            batch["status"] = "complete_with_gaps"
    batches["checkedDate"] = CHECKED
    batches["revision"] = "T11-B02-web-checked-2026-09-25"
    batches["overallT11Status"] = "in_progress_partial"
    batches["sources"].update(SOURCES)
    batches["entries"].extend(records)
    batches["fieldEvidence"].extend(flat_field_evidence)
    batches["notes"].append("T11-B02 completed with gaps: fieldEvidence contains 50 B02 rows; TA2 PDF search-index observations are not local visual review; KMLE source edition is not exposed; human anatomy review was not performed.")

    write_json(NAMES_PATH, names)
    write_json(BATCH_PATH, batches)
    print(json.dumps({
        "batchId": "T11-B02",
        "canonicalIds": expected_ids,
        "batchFieldEvidence": len(flat_field_evidence),
        "totalFieldEvidence": len(batches["fieldEvidence"]),
        "newLearningNames": len(new_entries),
        "totalLearningNames": len(names["entries"]),
        "batchStatus": "complete_with_gaps",
        "humanReviewed": False,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
