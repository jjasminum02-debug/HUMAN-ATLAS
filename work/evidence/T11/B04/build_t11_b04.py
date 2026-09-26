"""Build only the assigned T11-B04 existing-ID name evidence and learner overlay."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CHECKED = "2026-09-25"
IDS = [f"HA-M-{number:06d}" for number in [11, 12, 13, 14, 15, 16, 17, 18, 20, 21]]
FIPAT_ID = "fipat-ta2-b04-index"
FIPAT_URL = "https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf"
FIPAT_EDITION = "Terminologia Anatomica, second edition (TA2), Part 2; online edition published 2019; hosted PDF path dated 2020-09."
KMLE_EDITION = "KMLE web aggregation; exact underlying dictionary edition/revision is not exposed in the checked page or index excerpt."
NAMES_PATH = ROOT / "atlas-data/terminology/learning-names.json"
BATCH_PATH = ROOT / "atlas-data/terminology/term-review-batches.json"

ROWS = {
    "HA-M-000011": (2048, 74), "HA-M-000012": (2105, 77),
    "HA-M-000013": (2108, 77), "HA-M-000014": (2109, 77),
    "HA-M-000015": (2113, 77), "HA-M-000016": (2117, 77),
    "HA-M-000017": (2118, 77), "HA-M-000018": (2121, 77),
    "HA-M-000020": (2231, 81), "HA-M-000021": (2232, 81),
}

SOURCES = {
    FIPAT_ID: {
        "title": "FIPAT Terminologia Anatomica, second edition, Part 2 — B04 rows",
        "url": FIPAT_URL,
        "locator": "Part 2, Muscular System: printed p. 74 row 2048; p. 77 rows 2105, 2108–2109, 2113, 2117–2118, 2121; p. 81 rows 2231–2232. The official hosted PDF search index exposes row text. Direct PDF open returned HTTP 502; no local download, page image, column header role, or errata were inspected.",
        "edition": FIPAT_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "official_hosted_PDF_search_index_text_only; direct_PDF_open_failed_HTTP_502; no_local_or_visual_inspection",
        "scope": "TA2 nomenclature observations only; English/Latin cell roles and anatomical equivalence are not human-reviewed.",
    },
    "kmle-b04-superior-oblique": {
        "title": "KMLE superior oblique term entry",
        "url": "https://m.kmle.co.kr/search.php?Page=1&Search=superior+oblique",
        "locator": "Opened HTML, old 대한의협 3 result lines 239–255: superior oblique muscle → 상사근(上斜筋), 위빗근, 상사근/위경사근; 대한해부학회 section lines 338–347 gives 위빗근 and [옛 용어] 상사근; 대한신경외과학회 section lines 430–442 pairs 위빗근·상사근 with 上斜筋. Underlying dictionary revisions are not exposed.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "opened_HTML_page_text; dictionary_sections_visible_but_source_revisions_unexposed",
        "scope": "Term spelling only; no muscle action, attachment, or clinical claim imported.",
    },
    "kmle-b04-masseter": {
        "title": "KMLE masseter term entry",
        "url": "https://m.kmle.co.kr/search.php?Search=masseter",
        "locator": "Search-result excerpt: 대한해부학회 Masseter m. → 깨물근 [옛 용어] 교근; old 대한의협 3 musculus masseter → 교근(咬筋); 대한신경외과학회 masseter m. → 깨물근·교근 / 咬筋. Direct HTML open failed with Unicode decoding error; exact underlying dictionary edition/revision is not exposed.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "search_result_excerpt_only; direct_HTML_open_failed_Unicode_decoding_error",
        "scope": "Term spelling only; no muscle action, attachment, or clinical claim imported.",
    },
    "kmle-b04-temporalis": {
        "title": "KMLE temporalis term entry",
        "url": "https://m.kmle.co.kr/search.php?Search=temporalis",
        "locator": "Search-result excerpt: 대한해부학회 Temporalis m. → 관자근 [옛 용어] 측두근; 대한신경외과학회 temporalis m. → 측두근 / 側頭筋. Direct HTML open failed with Unicode decoding error; exact underlying dictionary edition/revision is not exposed.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "search_result_excerpt_only; direct_HTML_open_failed_Unicode_decoding_error",
        "scope": "Term spelling only; no muscle action, attachment, or clinical claim imported.",
    },
    "kmle-b04-lateral-pterygoid": {
        "title": "KMLE lateral pterygoid term entry",
        "url": "https://www.kmle.co.kr/search.php?Search=nervus+pterygoideus",
        "locator": "Search-result excerpt, old 대한의협 3 row for musculus pterygoideus lateralis: 외측날개근·외측익돌근(外側翼突筋); 대한해부학회 Lateral pterygoid m. → 가쪽날개근 [옛 용어] 외측익돌근. Open attempt failed; exact underlying dictionary edition/revision is not exposed.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "search_result_excerpt_only; direct_open_attempt_failed; dictionary_revision_unexposed",
        "scope": "Term spelling only; no muscle action, attachment, or clinical claim imported.",
    },
    "kmle-b04-medial-pterygoid": {
        "title": "KMLE medial pterygoid term entry",
        "url": "https://www.kmle.co.kr/search.php?Search=nervus+pterygoideus",
        "locator": "Search-result excerpt, old 대한의협 3 row for musculus pterygoideus medialis: 내측날개근·내측익돌근(內側翼突筋); 대한해부학회 Medial pterygoid m. → 안쪽날개근 [옛 용어] 내측익돌근. Open attempt on the shared KMLE query failed; exact underlying dictionary edition/revision is not exposed.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "search_result_excerpt_only; direct_open_attempt_failed; dictionary_revision_unexposed",
        "scope": "Term spelling only; no muscle action, attachment, or clinical claim imported.",
    },
    "kmle-b04-genioglossus": {
        "title": "KMLE genioglossus term entry",
        "url": "https://kmle.co.kr/search.php?Search=geni",
        "locator": "Search-result excerpt, 대한의협 term list: genioglossus muscle → 턱끝혀근, 이설근. A separate legacy dictionary excerpt lists 이설근·턱끝혀근 and an incomplete form (舌筋), not a complete Hanja name for this muscle. Exact underlying dictionary edition/revision is not exposed; direct page open failed.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "search_result_excerpt_only; direct_HTML_open_failed; incomplete_Hanja_fragment_not_adopted",
        "scope": "Term spelling only; incomplete Hanja fragment is recorded as an unresolved near-match, not as a term.",
    },
    "kmle-b04-genioglossus-hanja-fragment": {
        "title": "KMLE legacy genioglossal Hanja fragment check",
        "url": "https://m.kmle.co.kr/search.php?Page=5&Search=posterior+papillary+muscle",
        "locator": "Search-result excerpt, old 대한의협 2 row ‘genioglossal muscle’: 이설근·턱끝혀근(舌筋). Only the fragment 舌筋 is displayed, not a complete compound for this muscle. Direct open failed with cache miss; underlying edition/revision is not exposed.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "search_result_excerpt_only; direct_HTML_open_failed_cache_miss; incomplete_fragment_not_adopted",
        "scope": "Negative/near-match evidence for withholding a complete Hanja value; no term is created from the fragment.",
    },
    "kmle-b04-hyoglossus": {
        "title": "KMLE hyoglossus term entry",
        "url": "https://m.kmle.co.kr/search.php?Search=hyoglossus+muscle",
        "locator": "Search-result excerpt: 대한해부학회 Hyoglossus m. → 목뿔혀근 [옛 용어] 설골설근; legacy row hyoglossus musculus → 설골혀근·설골설근(舌骨舌筋). Exact underlying dictionary edition/revision is not exposed; direct HTML open failed with Unicode decoding error.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "search_result_excerpt_only; direct_HTML_open_failed_Unicode_decoding_error",
        "scope": "Term spelling only; no muscle action, attachment, or clinical claim imported.",
    },
    "kmle-b04-styloglossus": {
        "title": "KMLE styloglossus term entry",
        "url": "https://m.kmle.co.kr/search.php?Page=1&Search=sty",
        "locator": "Search-result excerpt: 대한해부학회 Styloglossus m. → 붓혀근 [옛 용어] 경돌설근; legacy row stylglossus → 경돌설근(莖突舌筋). The spelling stylglossus is a source typo and is not copied as a term. Exact underlying dictionary edition/revision is not exposed; direct HTML open failed.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "search_result_excerpt_only; direct_HTML_open_failed; source_typo_not_adopted",
        "scope": "Term spelling only; source typo is noted but not added to search aliases.",
    },
    "kmle-b04-latissimus-dorsi": {
        "title": "KMLE latissimus dorsi term entry",
        "url": "https://m.kmle.co.kr/search.php?Search=latissimus+dorsi",
        "locator": "Opened HTML: current 대한의협 result lines 8–20 gives 넓은등근·광배근; old 대한의협 3 lines 53–71 gives 광배근(廣背筋); 대한해부학회 lines 139–148 gives 넓은등근 [옛 용어] 광배근; 대한신경외과학회 lines 161–173 gives 넓은등근·광배근 / 廣背筋. Exact underlying dictionary editions/revisions are not exposed.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "opened_HTML_page_text; dictionary_sections_visible_but_source_revisions_unexposed",
        "scope": "Term spelling only; no muscle action, attachment, or clinical claim imported.",
    },
    "kmle-b04-rhomboid-major": {
        "title": "KMLE rhomboid major term entry",
        "url": "https://m.kmle.co.kr/search.php?Search=rhomboid+muscle%2C+greater",
        "locator": "Search-result excerpt: 대한해부학회 Rhomboid major m. → 큰마름근 [옛 용어] 대능형근; old 대한의협 2 row greater rhomboid muscle / musculus rhomboideus major → 큰마름모근·대릉형근(大菱形筋). The source spelling is preserved as displayed; exact underlying edition/revision is not exposed and direct page open failed.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "search_result_excerpt_only; direct_HTML_open_failed; dictionary_revision_unexposed",
        "scope": "Term spelling only; no muscle action, attachment, or clinical claim imported.",
    },
}

TERMS = {
    "HA-M-000011": {"label":"상사근","korean":"위빗근","hanja":"上斜筋","source":"kmle-b04-superior-oblique","labelState":"attested_customary_hanja_name","koreanState":"attested_current_korean_name"},
    "HA-M-000012": {"label":"교근","korean":"깨물근","hanja":"咬筋","source":"kmle-b04-masseter","labelState":"attested_customary_hanja_name","koreanState":"attested_current_korean_name"},
    "HA-M-000013": {"label":"측두근","korean":"관자근","hanja":"側頭筋","source":"kmle-b04-temporalis","labelState":"attested_customary_hanja_name","koreanState":"attested_current_korean_name"},
    "HA-M-000014": {"label":"외측익돌근","korean":"가쪽날개근","hanja":"外側翼突筋","source":"kmle-b04-lateral-pterygoid","labelState":"attested_customary_hanja_name","koreanState":"attested_current_korean_name"},
    "HA-M-000015": {"label":"내측익돌근","korean":"안쪽날개근","hanja":"內側翼突筋","source":"kmle-b04-medial-pterygoid","labelState":"attested_customary_hanja_name","koreanState":"attested_current_korean_name"},
    "HA-M-000016": {"label":"이설근","korean":"턱끝혀근","hanja":None,"source":"kmle-b04-genioglossus","labelSource":["kmle-b04-genioglossus"],"koreanSource":["kmle-b04-genioglossus"],"hanjaSource":["kmle-b04-genioglossus-hanja-fragment"],"labelState":"attested_customary_korean_name","koreanState":"attested_current_korean_name","hanjaState":"missing_incomplete_fragment_no_full_hanja","missing":"KMLE search excerpts pair 이설근/턱끝혀근 but show only an incomplete 舌筋 fragment; a complete source Hanja form for the genioglossus was not observed. Do not expand the fragment into a guessed compound.","candidates":["舌筋 (incomplete fragment; not linked)"]},
    "HA-M-000017": {"label":"설골설근","korean":"목뿔혀근","hanja":"舌骨舌筋","source":"kmle-b04-hyoglossus","labelState":"attested_customary_hanja_name","koreanState":"attested_current_korean_name"},
    "HA-M-000018": {"label":"경돌설근","korean":"붓혀근","hanja":"莖突舌筋","source":"kmle-b04-styloglossus","labelState":"attested_customary_hanja_name","koreanState":"attested_current_korean_name"},
    "HA-M-000020": {"label":"광배근","korean":"넓은등근","hanja":"廣背筋","source":"kmle-b04-latissimus-dorsi","labelState":"attested_customary_hanja_name","koreanState":"attested_current_korean_name"},
    "HA-M-000021": {"label":"대능형근","korean":"큰마름근","hanja":"大菱形筋","source":"kmle-b04-rhomboid-major","labelState":"attested_customary_hanja_name","koreanState":"attested_current_korean_name"},
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def evidence(source_id: str, locator: str | None = None):
    source = SOURCES[source_id]
    return {"sourceId":source_id,"locator":locator or source["locator"],"verificationMode":source["verificationMode"],"sourceEdition":source["edition"],"checkedDate":CHECKED}


def field_record(identifier: str, field: str, value, state: str, source_ids: list[str], *, source_value=None, missing_reason=None, locators=None):
    return {"entryId":identifier,"field":field,"value":value,"state":state,"evidence":[evidence(sid,(locators or {}).get(sid)) for sid in source_ids],"sourceValue":source_value,"missingReason":missing_reason,"humanAnatomyReviewStatus":"not_performed","humanReviewed":False}


def main():
    names = read_json(NAMES_PATH)
    batches = read_json(BATCH_PATH)
    rows = [row for row in batches["canonicalCoverage"] if row["batchId"] == "T11-B04"]
    if [row["id"] for row in rows] != IDS:
        raise SystemExit("T11-B04 assignment changed; refusing to touch any other IDs")
    if any(row["status"] != "not_started" for row in rows):
        raise SystemExit("T11-B04 already has status; refusing a non-idempotent rebuild")
    if any(row["id"] in {entry["id"] for entry in batches["entries"]} for row in rows):
        raise SystemExit("A T11-B04 evidence entry already exists; refusing duplicate data")
    if any(entry["id"] in set(IDS) for entry in names["entries"]):
        raise SystemExit("A T11-B04 overlay entry already exists; refusing duplicate data")

    crosswalk = read_json(ROOT / "atlas-data/catalog/source-crosswalk.json")
    canonical_data = read_json(ROOT / "atlas-data/catalog/canonical-catalog.json")["entities"]["muscleConcepts"]
    canonical = {row["id"]: row for row in canonical_data}
    crosswalk_terms = {identifier:{term["sourceLanguage"]:term for term in crosswalk["termRecords"] if term["conceptId"]==identifier and term["sourceTextObserved"]} for identifier in IDS}
    new_entries, flat_field_evidence, overlay = [], [], []
    for row in rows:
        identifier = row["id"]
        concept = canonical[identifier]
        loc = row["sourceCrosswalkLocator"]
        terms = crosswalk_terms[identifier]
        if terms.get("en",{}).get("sourceTextObserved") != loc["englishTextObservation"]:
            raise SystemExit(f"English observation mismatch for {identifier}")
        if terms.get("la",{}).get("sourceTextObserved") != loc["latinTextObservation"]:
            raise SystemExit(f"Latin observation mismatch for {identifier}")
        value = TERMS[identifier]
        row_number, printed_page = ROWS[identifier]
        if (loc["tableRow"],loc["printedPage"]) != (row_number,printed_page):
            raise SystemExit(f"TA2 locator changed for {identifier}")
        display_english, latin = loc["englishTextObservation"], loc["latinTextObservation"]
        english_locator = f"TA2 Part 2 printed p. {printed_page}, table row {row_number}: exact English text observation '{display_english}' in official hosted-PDF search-index text; cell role remains unverified; direct PDF open returned HTTP 502."
        latin_locator = f"TA2 Part 2 printed p. {printed_page}, table row {row_number}: exact Latin text observation '{latin}' in official hosted-PDF search-index text; cell role remains unverified; direct PDF open returned HTTP 502."
        source_id = value["source"]
        hanja_state = value.get("hanjaState","attested_source_hanja" if value["hanja"] else "missing_not_observed")
        item_fields = [
            field_record(identifier,"label",value["label"],value["labelState"],value.get("labelSource",[source_id]),missing_reason=value.get("missing") if value["label"] is None else None),
            field_record(identifier,"korean",value["korean"],value["koreanState"],value.get("koreanSource",[source_id]),missing_reason=value.get("missing") if value["korean"] is None else None),
            field_record(identifier,"hanja",value["hanja"],hanja_state,value.get("hanjaSource",[source_id]),missing_reason=value.get("missing") if value["hanja"] is None else None),
            field_record(identifier,"english",display_english,"TA2_search_index_observation_cell_role_unverified",[FIPAT_ID],source_value=display_english,locators={FIPAT_ID:english_locator}),
            field_record(identifier,"aliases[0]",latin,"TA2_search_index_observation_cell_role_unverified",[FIPAT_ID],source_value=latin,locators={FIPAT_ID:latin_locator}),
        ]
        flat_field_evidence.extend(item_fields)
        name_record = {
            "id":identifier,"label":value["label"],"korean":value["korean"],"english":display_english,"hanja":value["hanja"],"aliases":[latin],
            "sourceIds":sorted({FIPAT_ID,*value.get("labelSource",[source_id]),*value.get("koreanSource",[source_id]),*value.get("hanjaSource",[source_id])}),"parentId":concept.get("parentId"),"entityType":concept["entityType"],"lookupOnly":False,
            "status":"web_attested_with_gaps","humanReviewed":False,
            "hanjaNote":"KMLE에서 출처 표기를 확인했다. 사람 해부학 검토는 수행하지 않았다." if value["hanja"] else value["missing"],
        }
        overlay.append(name_record)
        entry = {
            "id":identifier,"isCanonical":True,"entityType":concept["entityType"],"parentId":concept.get("parentId"),"lookupOnly":False,
            "canonicalStatus":"canonical_existing_id","canonicalSourceRow":{"sourceId":"FIPAT_TA2","tableRow":row_number,"printedPage":printed_page},
            "displayField":"label","displayValue":value["label"],"fieldEvidence":item_fields,"webVerificationStatus":"web_checked_with_gaps",
            "humanAnatomyReviewStatus":"not_performed","humanReviewer":None,"humanReviewed":False,"fieldEvidenceCount":len(item_fields),
        }
        if value.get("candidates"):
            entry["unadoptedCandidates"] = [{"value":candidate,"status":"near_match_not_linked","sourceIds":value.get("hanjaSource",[source_id]),"reason":value["missing"]} for candidate in value["candidates"]]
        new_entries.append(entry)
        row["status"] = "web_checked_with_gaps"
        row["statusReason"] = "TA2 indexed English/Latin observations and field-level KMLE name evidence are recorded; incomplete Hanja is withheld; source edition and index/original limitations remain explicit; human anatomy review was not performed."

    for source_id, source in SOURCES.items():
        names["sources"][source_id] = source
    batches["sources"].update(SOURCES)
    names["entries"].extend(overlay)
    batches["entries"].extend(new_entries)
    batches["fieldEvidence"].extend(flat_field_evidence)
    batches["checkedDate"] = CHECKED
    batches["revision"] = "T11-B04-web-checked-2026-09-25"
    batches["overallT11Status"] = "in_progress_partial"
    for batch in batches["batchOrder"]:
        if batch["batchId"] == "T11-B04":
            batch["status"] = "complete_with_gaps"
    batches["notes"].append("T11-B04 completed with gaps: 10 assigned existing IDs; 50 field evidence rows; 10 Korean display overlays; 9 full source-attested Hanja values; genioglossus incomplete Hanja fragment withheld; FIPAT TA2 search-index values lack local visual row/column audit; most KMLE underlying dictionary revisions are unexposed; human anatomy review not performed.")
    names["revision"] = "T11-B04-web-checked-2026-09-25"
    names["accessedAt"] = CHECKED
    write_json(NAMES_PATH,names)
    write_json(BATCH_PATH,batches)
    print(json.dumps({"batchId":"T11-B04","canonicalIds":IDS,"batchFieldEvidence":len(flat_field_evidence),"totalFieldEvidence":len(batches["fieldEvidence"]),"newLearnerNames":len(overlay),"totalLearnerNames":len(names["entries"]),"sourceHanjaValues":sum(1 for t in TERMS.values() if t["hanja"]),"batchStatus":"complete_with_gaps","humanReviewed":False},ensure_ascii=False,indent=2))

if __name__ == "__main__":
    main()
