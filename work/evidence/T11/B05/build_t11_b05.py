"""Build only the assigned T11-B05 name evidence and learner search overlay."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CHECKED = "2026-09-25"
IDS = [f"HA-M-{number:06d}" for number in range(22, 32)]
FIPAT_ID = "fipat-ta2-b05-opened-original-pdf"
FIPAT_URL = "https://cdn.dal.ca/content/dam/dalhousie/pdf/library/FIPAT/TA2/FIPAT-TA2-Part-2.pdf"
FIPAT_EDITION = "Terminologia Anatomica, second edition (TA2), Part 2; online edition published 2019."
KMLE_EDITION = "KMLE web dictionary aggregation; exact underlying dictionary edition/revision is not exposed in the checked result."
NAMES_PATH = ROOT / "atlas-data/terminology/learning-names.json"
BATCH_PATH = ROOT / "atlas-data/terminology/term-review-batches.json"

ROWS = {
 "HA-M-000022": (2233, 81, "P60"), "HA-M-000023": (2234, 81, "P60"),
 "HA-M-000024": (2301, 83, "P62"), "HA-M-000025": (2305, 83, "P62"),
 "HA-M-000026": (2306, 83, "P62"), "HA-M-000027": (2307, 83, "P62"),
 "HA-M-000028": (2373, 86, "P65"), "HA-M-000029": (2375, 86, "P65"),
 "HA-M-000030": (2452, 89, "P68"), "HA-M-000031": (2457, 89, "P68"),
}

SOURCES = {
 FIPAT_ID: {
  "title": "FIPAT Terminologia Anatomica, second edition, Part 2 — direct text from official Dalhousie hosted PDF",
  "url": FIPAT_URL,
  "locator": "TA2 Part 2 PDF, 104 pages. Chapter 4 table header on PDF text page P52 names columns Latin term, Latin synonym, UK English, US English, English synonym, Other. Assigned rows: p. 81 rows 2233–2234; p. 83 rows 2301, 2305–2307; p. 86 rows 2373, 2375; p. 89 rows 2452, 2457. Exact text rows and table headings were read from the directly opened PDF text layer. The fipat.library.dal.ca URL returned HTTP 502; this alternate URL is the Dalhousie-hosted FIPAT TA2 PDF. No local copy or rendered page screenshot was created.",
  "edition": FIPAT_EDITION,
  "accessDate": CHECKED,
  "verificationMode": "official_Dalhousie_hosted_original_PDF_opened_text_layer; Chapter_4_table_headers_and_assigned_rows_read; no_local_copy_or_visual_screenshot",
  "scope": "TA2 term strings and stated table column roles only; no anatomical, functional, attachment, or clinical claim; human anatomy review not performed.",
 },
 "kmle-b05-rhomboid-minor": {
  "title": "KMLE rhomboid minor name search result",
  "url": "https://m.kmle.co.kr/search.php?Search=rhomboid+minor",
  "locator": "Search-result excerpt: rhomboid minor muscle → 작은마름근, 소능형근; 대한해부학회 Rhomboid minor m. → 작은마름근 [옛 용어] 소능형근. The excerpt does not expose the source dictionary edition/revision.",
  "edition": KMLE_EDITION, "accessDate": CHECKED,
  "verificationMode": "KMLE_search_index_excerpt_only; direct_page_open_failed_cache_miss; underlying_dictionary_edition_unexposed",
  "scope": "Korean term spelling only; not a human anatomy review.",
 },
 "kmle-b05-rhomboideus-hanja": {
  "title": "KMLE rhomboideus and rhomboid minor Hanja search result",
  "url": "https://m.kmle.co.kr/search.php?Search=rhomboideus",
  "locator": "Search-result excerpt, old 대한의협 3 entry: musculus rhomboideus minor → 작은마름모근, 소능형근(小菱形筋). Exact Hanja characters are shown; source dictionary edition/revision is not exposed.",
  "edition": KMLE_EDITION, "accessDate": CHECKED,
  "verificationMode": "KMLE_search_index_excerpt_only; direct_page_not_opened; underlying_dictionary_edition_unexposed",
  "scope": "Term spelling only; no inference from the rhomboid shape or other muscle name.",
 },
 "kmle-b05-levator-scapulae": {
  "title": "KMLE levator scapulae name search result",
  "url": "https://m.kmle.co.kr/search.php?FuzzyTrack=scapula&IsFuzzy=YES&Search=scapulae",
  "locator": "Search-result excerpt: levator scapulae m. → 어깨올림근; musculus levator scapulae → 견갑올림근, 견갑거근(肩甲擧筋); 대한해부학회 entry → 어깨올림근 [옛 용어] 견갑거근. Exact underlying dictionary edition/revision is not exposed.",
  "edition": KMLE_EDITION, "accessDate": CHECKED,
  "verificationMode": "KMLE_search_index_excerpt_only; direct_page_open_failed_cache_miss; underlying_dictionary_edition_unexposed",
  "scope": "Name spellings only; the source wording is not treated as anatomical equivalence review.",
 },
 "kmle-b05-pectoralis": {
  "title": "KMLE pectoralis major and minor name search result",
  "url": "https://www.kmle.co.kr/search.php?Search=pectoralis",
  "locator": "Search-result excerpt, 대한해부학회 entries: Pectoralis major m. → 큰가슴근 [옛 용어] 대흉근; Pectoralis minor m. → 작은가슴근 [옛 용어] 소흉근. Old 대한의협 3 entries show musculus pectoralis major → 대흉근(大胸筋), musculus pectoralis minor → 소흉근(小胸筋). Exact underlying dictionary edition/revision is not exposed.",
  "edition": KMLE_EDITION, "accessDate": CHECKED,
  "verificationMode": "KMLE_search_index_excerpt_only; direct_page_open_failed_Unicode_decoding_error; underlying_dictionary_edition_unexposed",
  "scope": "Name spellings only; no attachment/function text imported.",
 },
 "kmle-b05-subclavius": {
  "title": "KMLE subclavius name search result",
  "url": "https://www.kmle.co.kr/search.php?Search=subclavius+muscle",
  "locator": "Search-result excerpt: subclavius muscle → 빗장밑근; an old entry gives 쇄골아래근, 쇄골하근(鎖骨下筋). Exact underlying dictionary edition/revision is not exposed.",
  "edition": KMLE_EDITION, "accessDate": CHECKED,
  "verificationMode": "KMLE_search_index_excerpt_only; direct_page_open_failed_cache_miss; underlying_dictionary_edition_unexposed",
  "scope": "Name spellings only; no muscle description imported.",
 },
 "kmle-b05-serratus": {
  "title": "KMLE serratus anterior name search result",
  "url": "https://www.kmle.co.kr/search.php?Search=serratus",
  "locator": "Search-result excerpt: serratus anterior muscle → 앞톱니근, 전방거근; old 대한의협 3 entry: 앞톱니근, 전거근(前鋸筋); 대한해부학회 entry: 앞톱니근 [옛 용어] 전거근. The separate older form 前方鋸筋 is not adopted as the muscle name. Exact source edition/revision is not exposed.",
  "edition": KMLE_EDITION, "accessDate": CHECKED,
  "verificationMode": "KMLE_search_index_excerpt_only; direct_page_open_failed_Unicode_decoding_error; underlying_dictionary_edition_unexposed",
  "scope": "Name spellings only; the distinct/nearby form 前方鋸筋 is not conflated with the attested 前鋸筋.",
 },
 "kmle-b05-obliquus-internus": {
  "title": "KMLE internal abdominal oblique current Korean name search result",
  "url": "https://m.kmle.co.kr/search.php?Search=obliquus+internus+abdominis",
  "locator": "Search-result excerpt: 대한해부학회 Obliquus internus abdominis m. → 배속빗근 [옛 용어] 내복사근. Exact underlying dictionary edition/revision is not exposed.",
  "edition": KMLE_EDITION, "accessDate": CHECKED,
  "verificationMode": "KMLE_search_index_excerpt_only; direct_page_not_opened; underlying_dictionary_edition_unexposed",
  "scope": "Korean term spelling only.",
 },
 "kmle-b05-internal-oblique-hanja": {
  "title": "KMLE internal abdominal oblique Hanja search result",
  "url": "https://m.kmle.co.kr/search.php?Search=internal+oblique+muscle+of+abdomen",
  "locator": "Search-result excerpt, old 대한의협 3 entry: internal oblique muscle of abdomen → 내복사근(內腹斜筋). Exact source characters are shown; underlying edition/revision is not exposed.",
  "edition": KMLE_EDITION, "accessDate": CHECKED,
  "verificationMode": "KMLE_search_index_excerpt_only; direct_page_not_opened; underlying_dictionary_edition_unexposed",
  "scope": "Name spelling only.",
 },
 "kmle-b05-transversus-abdominis": {
  "title": "KMLE transversus abdominis name search result",
  "url": "https://m.kmle.co.kr/search.php?Search=transversus+abdominis",
  "locator": "Search-result excerpt: Transversus abdominis m. → 배가로근 [옛 용어] 복횡근; old entry musculus transversus abdominis → 가슴 가로 근, 배가로근, 복횡근(腹橫筋). Exact underlying dictionary edition/revision is not exposed.",
  "edition": KMLE_EDITION, "accessDate": CHECKED,
  "verificationMode": "KMLE_search_index_excerpt_only; direct_page_not_opened; underlying_dictionary_edition_unexposed",
  "scope": "Name spelling only; no muscle description imported.",
 },
 "kmle-deltoid": {
  "title": "KMLE deltoid name search result",
  "url": "https://m.kmle.co.kr/search.php?Search=deltoid",
  "locator": "Opened HTML page. 대한의협 lines 30–32 gives deltoid muscle → 어깨세모근, 삼각근; old 대한의협 3 lines 101–103 gives 삼각근(三角筋); CancerWEB lines 232–234 shows deltoid as the name/synonym for the muscle and Musculus deltoideus. The CancerWEB item is dated 05 Mar 2000; the underlying modern dictionary edition/revision is not exposed.",
  "edition": "KMLE web aggregation; CancerWEB entry displays 05 Mar 2000; exact underlying dictionary edition/revision is otherwise not exposed.", "accessDate": CHECKED,
  "verificationMode": "KMLE_HTML_page_opened; visible dictionary sections and CancerWEB date; other underlying source revisions unexposed",
  "scope": "Name spellings only; no anatomy description, function, attachment, or clinical claim imported.",
 },
 "kmle-b05-supraspinatus": {
  "title": "KMLE supraspinatus name search result",
  "url": "https://m.kmle.co.kr/search.php?Search=musculus+supraspinatus",
  "locator": "Search-result excerpt: supraspinatus muscle → 가시위근, 극상근; old 대한의협 3 entry → 가시윗근, 극상근(棘上筋); 대한해부학회 entry → 가시위근 [옛 용어] 극상근. Exact underlying dictionary edition/revision is not exposed.",
  "edition": KMLE_EDITION, "accessDate": CHECKED,
  "verificationMode": "KMLE_search_index_excerpt_only; direct_page_open_failed_Unicode_decoding_error; underlying_dictionary_edition_unexposed",
  "scope": "Name spelling only; no muscle description imported.",
 },
}

TERMS = {
 "HA-M-000022": {"label":"소능형근","korean":"작은마름근","hanja":"小菱形筋","labelSource":["kmle-b05-rhomboideus-hanja"],"koreanSource":["kmle-b05-rhomboid-minor"],"hanjaSource":["kmle-b05-rhomboideus-hanja"]},
 "HA-M-000023": {"label":"견갑거근","korean":"어깨올림근","hanja":"肩甲擧筋","labelSource":["kmle-b05-levator-scapulae"],"koreanSource":["kmle-b05-levator-scapulae"],"hanjaSource":["kmle-b05-levator-scapulae"]},
 "HA-M-000024": {"label":"대흉근","korean":"큰가슴근","hanja":"大胸筋","labelSource":["kmle-b05-pectoralis"],"koreanSource":["kmle-b05-pectoralis"],"hanjaSource":["kmle-b05-pectoralis"]},
 "HA-M-000025": {"label":"소흉근","korean":"작은가슴근","hanja":"小胸筋","labelSource":["kmle-b05-pectoralis"],"koreanSource":["kmle-b05-pectoralis"],"hanjaSource":["kmle-b05-pectoralis"]},
 "HA-M-000026": {"label":"쇄골하근","korean":"빗장밑근","hanja":"鎖骨下筋","labelSource":["kmle-b05-subclavius"],"koreanSource":["kmle-b05-subclavius"],"hanjaSource":["kmle-b05-subclavius"]},
 "HA-M-000027": {"label":"전거근","korean":"앞톱니근","hanja":"前鋸筋","labelSource":["kmle-b05-serratus"],"koreanSource":["kmle-b05-serratus"],"hanjaSource":["kmle-b05-serratus"]},
 "HA-M-000028": {"label":"내복사근","korean":"배속빗근","hanja":"內腹斜筋","labelSource":["kmle-b05-internal-oblique-hanja"],"koreanSource":["kmle-b05-obliquus-internus"],"hanjaSource":["kmle-b05-internal-oblique-hanja"]},
 "HA-M-000029": {"label":"복횡근","korean":"배가로근","hanja":"腹橫筋","labelSource":["kmle-b05-transversus-abdominis"],"koreanSource":["kmle-b05-transversus-abdominis"],"hanjaSource":["kmle-b05-transversus-abdominis"]},
 "HA-M-000030": {"label":"삼각근","korean":"어깨세모근","hanja":"三角筋","labelSource":["kmle-deltoid"],"koreanSource":["kmle-deltoid"],"hanjaSource":["kmle-deltoid"]},
 "HA-M-000031": {"label":"극상근","korean":"가시위근","hanja":"棘上筋","labelSource":["kmle-b05-supraspinatus"],"koreanSource":["kmle-b05-supraspinatus"],"hanjaSource":["kmle-b05-supraspinatus"]},
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
 names=read_json(NAMES_PATH); batches=read_json(BATCH_PATH)
 rows=[row for row in batches["canonicalCoverage"] if row["batchId"]=="T11-B05"]
 if [row["id"] for row in rows] != IDS: raise SystemExit("T11-B05 assignment changed; refusing to touch any other IDs")
 if any(row["status"]!="not_started" for row in rows): raise SystemExit("T11-B05 already has status; refusing a non-idempotent rebuild")
 if any(row["id"] in {entry["id"] for entry in batches["entries"]} for row in rows): raise SystemExit("A T11-B05 evidence entry already exists; refusing duplicates")
 existing_overlays={entry["id"]:entry for entry in names["entries"] if entry["id"] in set(IDS)}
 if set(existing_overlays)-{"HA-M-000030"}: raise SystemExit("Unexpected pre-existing T11-B05 overlays; refusing to overwrite")
 existing_deltoid=existing_overlays.get("HA-M-000030")
 if existing_deltoid and (existing_deltoid.get("label"),existing_deltoid.get("korean"),existing_deltoid.get("english"),existing_deltoid.get("hanja"),existing_deltoid.get("aliases")) != ("삼각근","어깨세모근","Deltoid","三角筋",[]):
  raise SystemExit("The pre-existing deltoid overlay differs from the captured baseline; refusing to overwrite")
 crosswalk=read_json(ROOT/"atlas-data/catalog/source-crosswalk.json")
 canonical={row["id"]:row for row in read_json(ROOT/"atlas-data/catalog/canonical-catalog.json")["entities"]["muscleConcepts"]}
 crosswalk_terms={identifier:{term["sourceLanguage"]:term for term in crosswalk["termRecords"] if term["conceptId"]==identifier and term["sourceTextObserved"]} for identifier in IDS}
 new_entries=[]; flat_field_evidence=[]; overlays=[]
 for row in rows:
  identifier=row["id"]; concept=canonical[identifier]; loc=row["sourceCrosswalkLocator"]
  if (loc["tableRow"],loc["printedPage"])!=ROWS[identifier][:2]: raise SystemExit(f"TA2 locator changed for {identifier}")
  observed=crosswalk_terms[identifier]
  if observed.get("en",{}).get("sourceTextObserved")!=loc["englishTextObservation"] or observed.get("la",{}).get("sourceTextObserved")!=loc["latinTextObservation"]: raise SystemExit(f"Source crosswalk observation mismatch for {identifier}")
  value=TERMS[identifier]; row_no,page,pdf_page=ROWS[identifier]
  # The PDF header shows English synonym as a separate column. The inherited crosswalk English text may be that synonym (M23) or the matching UK/US English cells.
  if identifier=="HA-M-000023": english_column="English synonym"
  else: english_column="UK English and US English"
  if identifier=="HA-M-000023": latin_column="Latin synonym"
  else: latin_column="Latin term"
  english=loc["englishTextObservation"]; latin=loc["latinTextObservation"]
  english_locator=f"TA2 Chapter 4, PDF text page {pdf_page}, printed p. {page}, table row {row_no}; exact English observation '{english}' in {english_column} column. Header names verified from Chapter 4 table heading; original PDF text opened, visual page rendering not inspected."
  latin_locator=f"TA2 Chapter 4, PDF text page {pdf_page}, printed p. {page}, table row {row_no}; exact Latin observation '{latin}' in {latin_column} column. Header names verified from Chapter 4 table heading; original PDF text opened, visual page rendering not inspected."
  name_sources={*value["labelSource"],*value["koreanSource"],*value["hanjaSource"]}
  fields=[
   field_record(identifier,"label",value["label"],"attested_customary_hanja_name",value["labelSource"]),
   field_record(identifier,"korean",value["korean"],"attested_current_korean_name",value["koreanSource"]),
   field_record(identifier,"hanja",value["hanja"],"attested_source_hanja",value["hanjaSource"]),
   field_record(identifier,"english",english,"TA2_opened_original_PDF_text_observation",[FIPAT_ID],source_value=english,locators={FIPAT_ID:english_locator}),
   field_record(identifier,"aliases[0]",latin,"TA2_opened_original_PDF_text_observation",[FIPAT_ID],source_value=latin,locators={FIPAT_ID:latin_locator}),
  ]
  if identifier=="HA-M-000030":
   fields.append(field_record(identifier,"aliases[1]","Deltoid","preserved_existing_KMLE_English_synonym",["kmle-deltoid"],source_value="Deltoid",locators={"kmle-deltoid":"Opened KMLE HTML: CancerWEB muscle entry headed deltoid at lines 232–234 includes the synonym 'deltoid'; that existing overlay value is retained as an English search alias while the exact TA2 English observation is stored in english."}))
  flat_field_evidence.extend(fields)
  existing_aliases=(["Deltoid"] if identifier=="HA-M-000030" else [])
  overlays.append({"id":identifier,"label":value["label"],"korean":value["korean"],"english":english,"hanja":value["hanja"],"aliases":[latin,*existing_aliases],"sourceIds":sorted({FIPAT_ID,*name_sources,*(["kmle-deltoid"] if identifier=="HA-M-000030" else [])}),"parentId":concept.get("parentId"),"entityType":concept["entityType"],"lookupOnly":False,"status":"web_attested_with_gaps","humanReviewed":False,"hanjaNote":"KMLE에 출처 표기를 확인했다. 하위 사전 판본은 대부분 노출되지 않았고 사람 해부학 검토는 수행하지 않았다."})
  new_entries.append({"id":identifier,"isCanonical":True,"entityType":concept["entityType"],"parentId":concept.get("parentId"),"lookupOnly":False,"canonicalStatus":"canonical_existing_id","canonicalSourceRow":{"sourceId":"FIPAT_TA2","tableRow":row_no,"printedPage":page},"displayField":"label","displayValue":value["label"],"fieldEvidence":fields,"webVerificationStatus":"web_checked_with_gaps","humanAnatomyReviewStatus":"not_performed","humanReviewer":None,"humanReviewed":False,"fieldEvidenceCount":len(fields)})
  row["status"]="web_checked_with_gaps"
  row["statusReason"]="Ten assigned existing IDs have field-level KMLE excerpts and directly opened official Dalhousie-hosted TA2 PDF text rows; KMLE source revisions are unexposed, PDF visual screenshots were not inspected, and human anatomy review was not performed."
  loc["existingEvidenceMode"]="T04 official search-index observation retained; T11-B05 additionally opened the official Dalhousie-hosted TA2 PDF text and verified assigned row strings and table heading; no visual page screenshot."
  loc["cellRoleStatus"]="column_role_confirmed_from_opened_PDF_text_header; visual_table_layout_not_inspected"
 for source_id,source in SOURCES.items():
  names["sources"][source_id]=source; batches["sources"][source_id]=source
 for overlay in overlays:
  if overlay["id"] in existing_overlays:
   names["entries"][names["entries"].index(existing_overlays[overlay["id"]])]=overlay
  else: names["entries"].append(overlay)
 batches["entries"].extend(new_entries); batches["fieldEvidence"].extend(flat_field_evidence)
 names["revision"]="T11-B05-web-checked-2026-09-25"; names["accessedAt"]=CHECKED
 batches["revision"]="T11-B05-web-checked-2026-09-25"; batches["checkedDate"]=CHECKED; batches["overallT11Status"]="in_progress_partial"
 for batch in batches["batchOrder"]:
  if batch["batchId"]=="T11-B05": batch["status"]="complete_with_gaps"
 batches["notes"].append("T11-B05 completed with gaps: 10 assigned existing IDs; 50 field evidence rows; 10 learner name overlays and 10 complete source-attested Hanja values. Official Dalhousie-hosted TA2 PDF opened directly and text table headers/assigned rows confirmed; FIPAT library URL returned 502, no page screenshot was inspected. KMLE evidence remains search-index excerpts with exact underlying dictionary revisions unexposed. Human anatomy review not performed.")
 write_json(NAMES_PATH,names); write_json(BATCH_PATH,batches)
 print(json.dumps({"batchId":"T11-B05","canonicalIds":IDS,"batchFieldEvidence":len(flat_field_evidence),"totalFieldEvidence":len(batches["fieldEvidence"]),"newLearnerNames":sum(1 for overlay in overlays if overlay["id"] not in existing_overlays),"preexistingOverlayEnriched":len(existing_overlays),"totalLearnerNames":len(names["entries"]),"sourceHanjaValues":len(overlays),"batchStatus":"complete_with_gaps","humanReviewed":False},ensure_ascii=False,indent=2))

if __name__=="__main__": main()
