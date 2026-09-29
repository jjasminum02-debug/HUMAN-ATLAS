#!/usr/bin/env python3
"""Deterministic T100 semantic continuation builder and evidence ledger."""
import argparse
import hashlib
import json
import re
import unicodedata
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OVERLAY = ROOT / "atlas-data/overlays/za-local-integration.json"
TARGETS = ROOT / "atlas-data/catalog/target-scope-t96.json"
COMPILED = ROOT / "atlas-data/source-cache/datasets/za/compiled/manifest.json"
COVERAGE = ROOT / "work/evidence/T100/bulk-continuation-2026-09-29/target-coverage-snapshot.json"
OUT = ROOT / "work/evidence/T100/semantic-relations-2026-09-30"
DATE = "2026-09-30"
START_HEAD = "63cee1868b62bcf3590339f9c2c2283500f4a8ae"
OVERLAY_START_SHA = "e99a3169ff424b494003f885aebce437f3fa7258522b69719dd8fe27ca2affab"

SOURCE_ROWS = [
    ("kli-t100-phalanx-root-opened", "https://kli.korean.go.kr/term/trgtWord/indexTrgtWord.do?trgtWordNo=2277690", "우리말샘 2023-06 표기", "손발가락뼈 표제어: 손·발의 마디뼈; 엄지(발가락)는 2개, 나머지는 각각 3개; 동의어 가락뼈/마디뼈."),
    ("kli-t100-phalanx-proximal-opened", "https://kli.korean.go.kr/term/trgtWord/indexTrgtWord.do?trgtWordNo=2080397", None, "기절골: 손발에서 몸쪽에 가까운 마디뼈; 영어 proximal phalanx; 다듬을 말 첫마디뼈."),
    ("kli-t100-phalanx-middle-opened", "https://kli.korean.go.kr/term/trgtWord/indexTrgtWord.do?trgtWordNo=200297", None, "중절골 항목 용례의 중간마디뼈[중절골]; 용례를 독립 표제어 확인으로 과장하지 않음."),
    ("kli-t100-phalanx-distal-opened", "https://kli.korean.go.kr/term/trgtWord/indexTrgtWord.do?trgtWordNo=2084588", None, "끝마디뼈: 손발가락에서 가장 먼 마디뼈; 영어 distal phalanx; 옛말 말절골."),
    ("kli-t100-metacarpal-root-opened", "https://kli.korean.go.kr/term/trgtWord/indexTrgtWord.do?trgtWordNo=200293", None, "중수골 항목의 다듬을 말 손허리뼈; 순번은 원본 First–Fifth와 T96 memberCode로 구성."),
    ("kli-t100-triquetrum-list-opened", "https://kli.korean.go.kr/term/trgtWord/indexTrgtWord.do?trgtWordNo=2277581", "우리말샘 2023-06 표기", "손목뼈 구성 목록의 세모뼈; Triquetrum bone 및 exact T96 member와 결합."),
    ("kli-t100-trapezium-opened", "https://kli.korean.go.kr/term/trgtWord/indexTrgtWord.do?trgtWordNo=565982", "21세기 세종계획 전문용어", "큰마름뼈 표제어의 영어 대응 trapezium bone; Triquetrum과 구분."),
]

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def norm(value):
    return "".join(c for c in unicodedata.normalize("NFKC", value).casefold().strip() if c.isalnum())

def base(name):
    return re.sub(r"\.[lr]$", "", name).strip()

def opaque_key(seed):
    return "LC-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:20]

def build_exact_target_index(targets):
    by_id = {target["id"]: target for target in targets}
    index = defaultdict(dict)
    for target in targets:
        term = target.get("term", {})
        values = [term.get("english", ""), term.get("latin", "")]
        values.extend(value for group in term.get("sourceSynonyms", {}).values() for value in group)
        for value in {value for value in values if value}:
            index[norm(value)].setdefault(target["id"], set()).add(value)
    return {
        key: [
            {**by_id[target_id], "_matchedExactValues": sorted(values)}
            for target_id, values in sorted(hits.items())
        ]
        for key, hits in index.items()
    }

def exact_target_matches(label, target_index):
    return target_index.get(norm(label), [])

def target_source_ids(term):
    return list(dict.fromkeys([*term.get("targetTermSourceIds", []), "fipat-ta2-t96-full-target-catalog"]))

def exact_term_values(label, target):
    terms = [target.get("term", {}).get("english", ""), target.get("term", {}).get("latin", "")]
    for values in target.get("term", {}).get("sourceSynonyms", {}).values():
        terms.extend(values)
    return sorted({term for term in terms if term and norm(term) == norm(label)})

def member_relation(row):
    rels = [r for r in row.get("targetRelationEvidence", []) if r.get("relationKind") == "class_member"]
    codes = {r.get("memberCode") for r in rels if r.get("memberCode")}
    if len(codes) != 1 or not rels:
        return None
    raw_code = next(iter(codes))
    return {
        "memberCode": re.sub(r":(left|right)$", "", raw_code),
        "targetIds": sorted({r["targetId"] for r in rels}),
        "evidenceIds": sorted({sid for r in rels for sid in r.get("matchEvidenceSourceIds", [])}),
    }

def find_side_conflicts(rows, compiled):
    conflicts = []
    declared = {r.get("side") for r in rows}
    suffixes = set()
    for row in rows:
        source_match = re.search(r"\.([lr])$", row.get("sourceName", ""), re.I)
        compiled_name = compiled.get(row["sourceKey"], {}).get("dataName") or ""
        data_match = re.search(r"\.([lr])$", compiled_name, re.I)
        if source_match:
            suffix_side = "left" if source_match.group(1).lower() == "l" else "right"
            suffixes.add(suffix_side)
            if row.get("side") != suffix_side:
                conflicts.append({"sourceKey": row["sourceKey"], "kind": "source_suffix_overlay_side_conflict",
                                  "sourceSide": row.get("side"), "sourceSuffixSide": suffix_side})
        if source_match and data_match and source_match.group(1).lower() != data_match.group(1).lower():
            conflicts.append({"sourceKey": row["sourceKey"], "kind": "compiled_data_name_side_conflict",
                              "sourceName": row.get("sourceName"), "dataName": compiled_name})
    if len(rows) > 1 and (None in declared or (len(suffixes) == 2 and declared != {"left", "right"})):
        conflicts.append({"kind": "group_laterality_not_bilateral_or_unsided_member", "declaredSides": sorted(str(x) for x in declared)})
    return conflicts

def classify_part(label):
    low = label.casefold()
    if re.search(r"\bpart(?:s)? of\b", low): return "part"
    if re.search(r"\bhead of\b|\bhead\b", low): return "head"
    if "interossei" in low: return "muscle_group"
    if "sesamoid bones" in low: return "bone_group"
    if re.search(r"\b(vertebra|rib|phalanx|metacarpal|metatarsal)\b", low): return "named_member_or_series"
    return "unqualified_concept"

def extract_ordinal(label):
    spinal = re.search(r"\bvertebra\s+([CTL])\s*(\d{1,2})\b", label, re.I)
    if spinal:
        return {"value": spinal.group(1).upper() + spinal.group(2), "basis": "source ordinal"}
    match = re.search(r"\b(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth)\b", label, re.I)
    return {"value": match.group(1).casefold(), "basis": "source ordinal"} if match else None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    current_overlay = read(OVERLAY)
    has_semantic_links = any(r.get("learnerConceptLinks") for r in current_overlay["objects"])
    if has_semantic_links:
        baseline_raw = subprocess.check_output(["git", "show", START_HEAD + ":atlas-data/overlays/za-local-integration.json"], cwd=ROOT)
        if hashlib.sha256(baseline_raw).hexdigest() != OVERLAY_START_SHA:
            raise SystemExit("frozen overlay baseline hash changed")
        overlay = json.loads(baseline_raw)
    else:
        overlay = current_overlay
    target_scope = read(TARGETS)
    targets = target_scope["targets"]
    target_index = build_exact_target_index(targets)
    target_terms = {x["targetId"]: x for x in overlay.get("targetTerminologyEvidence", [])}
    compiled_doc = read(COMPILED)
    compiled_rows = compiled_doc.get("objects", compiled_doc.get("instances", []))
    compiled = {x["sourceKey"]: x for x in compiled_rows if x.get("sourceKey")}
    evidence_by_id = {x["id"]: x for x in overlay.get("evidenceSources", [])}
    for sid, url, edition, locator in SOURCE_ROWS:
        source = {
            "id": sid, "url": url, "sourceLabel": "한국어기초사전 연계 국가 용어 페이지",
            "exactEdition": edition,
            "editionExposure": edition or "열린 페이지에 사전 판본이 별도 표시되지 않음",
            "accessDate": DATE, "accessMethod": "opened_html", "locator": locator,
            "retrievalLayer": "opened_original_terminology_page",
            "openedOriginalDictionaryRecord": True, "openedOriginalSourcePage": True,
        }
        if sid in evidence_by_id and evidence_by_id[sid] != source:
            raise SystemExit("evidence source ID collision: " + sid)
        if sid not in evidence_by_id:
            overlay.setdefault("evidenceSources", []).append(source)
    catalog_source = {
        "id": "fipat-ta2-t96-full-target-catalog",
        "url": "https://ta2viewer.openanatomy.org/",
        "sourceLabel": "FIPAT Terminologia Anatomica, 2nd edition, online TA2 vocabulary 2.07 frozen in T96",
        "exactEdition": "Terminologia Anatomica 2nd edition, vocabulary 2.07",
        "editionExposure": "exact online vocabulary version recorded in frozen T96 scope; this row documents local frozen target fields, not a fresh page retrieval",
        "accessDate": "2026-09-29",
        "accessMethod": "local_frozen_metadata",
        "locator": "atlas-data/catalog/target-scope-t96.json targets[] keyed by the exact TA2 ID; term.english/latin/sourceSynonyms and ancestry fields",
        "retrievalLayer": "frozen_local_target_catalog",
        "openedOriginalDictionaryRecord": False,
        "openedOriginalSourcePage": False,
    }
    if catalog_source["id"] in evidence_by_id and evidence_by_id[catalog_source["id"]] != catalog_source:
        raise SystemExit("evidence source ID collision: " + catalog_source["id"])
    if catalog_source["id"] not in evidence_by_id:
        overlay.setdefault("evidenceSources", []).append(catalog_source)
    unnamed = [r for r in overlay["objects"] if r.get("localDisplayEligible") and not r.get("names", {}).get("koModern")]
    if len(unnamed) != 226:
        raise SystemExit("unnamed eligible surface denominator changed: " + str(len(unnamed)))
    groups = defaultdict(list)
    for row in unnamed:
        groups[(row["kind"], base(row["sourceName"]))].append(row)
    if len(groups) != 113:
        raise SystemExit("side-deduplicated concept denominator changed: " + str(len(groups)))
    coverage = read(COVERAGE)
    candidate_free = [x for x in coverage["targets"] if x["candidateSourceSurfaceCount"] == 0]
    if len(candidate_free) != 163:
        raise SystemExit("candidate-free target denominator changed: " + str(len(candidate_free)))
    updates, group_records, link_counts = [], [], Counter()
    for (kind, label), rows in sorted(groups.items(), key=lambda item: (item[0][0], item[0][1].casefold())):
        rows.sort(key=lambda r: (r.get("side") or "", r["sourceKey"]))
        conflicts = find_side_conflicts(rows, compiled)
        hits = exact_target_matches(label, target_index)
        hit_ids = sorted({x["id"] for x in hits})
        members = [member_relation(row) for row in rows]
        member_json = {json.dumps(m, sort_keys=True) for m in members if m is not None}
        shared_member = json.loads(next(iter(member_json))) if len(member_json) == 1 and all(m is not None for m in members) else None
        if shared_member:
            link_type = "verified_class_member"
            concept_seed = "member|" + "|".join(shared_member["targetIds"]) + "|" + shared_member["memberCode"] + "|" + kind
        elif len(hit_ids) == 1:
            link_type = "normalized_exact_target_term"
            concept_seed = "target|" + hit_ids[0] + "|" + kind
        else:
            link_type = "paired_source_concept"
            concept_seed = "source|" + kind + "|" + norm(label)
        concept_key = opaque_key(concept_seed)
        conflict_group = bool(conflicts)
        conflict_evidence = ["za-t99-frozen-source-objects"] if conflict_group else []

        for row in rows:
            m = member_relation(row)
            exact = exact_target_matches(label, target_index)
            if m:
                row_link = {
                    "conceptKey": concept_key, "relationKind": "verified_class_member",
                    "targetIds": m["targetIds"], "memberCode": m["memberCode"],
                    "targetTermMatches": [],
                    "matchRule": "exact frozen T96 class_member memberCode + observed source side + row evidence",
                    "evidenceIds": m["evidenceIds"], "identityStatus": "evidence_backed",
                    "humanReview": "not_performed",
                }
                link_counts["verified_class_member"] += 1
            elif len({x["id"] for x in exact}) == 1:
                target = exact[0]
                row_link = {
                    "conceptKey": None if conflict_group else concept_key,
                    "relationKind": "normalized_exact_target_term", "targetIds": [target["id"]],
                    "memberCode": None,
                    "targetTermMatches": [{"targetId": target["id"], "matchedValues": exact_term_values(label, target)}],
                    "matchRule": "terminal-side-suffix removed; Unicode NFKC/casefold/alphanumeric-fold punctuation_fold_exact equality only",
                    "evidenceIds": list(dict.fromkeys([*target_source_ids(target_terms.get(target["id"], {})), *conflict_evidence])),
                    "identityStatus": "side_conflicted" if conflict_group else "evidence_backed",
                    "humanReview": "not_performed",
                }
                link_counts["normalized_exact_target_term"] += 1
            elif conflict_group:
                row_link = {
                    "conceptKey": None, "relationKind": "side_or_source_identity_conflict",
                    "targetIds": [], "memberCode": None, "targetTermMatches": [],
                    "matchRule": "explicit source side/identity conflict; no concept identity asserted",
                    "evidenceIds": conflict_evidence,
                    "identityStatus": "held", "humanReview": "not_performed",
                }
                link_counts["side_or_source_identity_conflict"] += 1
            else:
                row_link = {
                    "conceptKey": concept_key, "relationKind": "paired_source_concept",
                    "targetIds": [], "memberCode": None, "targetTermMatches": [],
                    "matchRule": "exact source base label with terminal .l/.r pair; no target identity asserted",
                    "evidenceIds": ["za-t99-frozen-source-objects"],
                    "identityStatus": "source_label_pair_only", "humanReview": "not_performed",
                }
                link_counts["paired_source_concept"] += 1
            row["learnerConceptLinks"] = [row_link]

            phalanx = re.match(r"^(Proximal|Middle|Distal) phalanx of (first|second|third|fourth|fifth) finger of (hand|foot)\.([lr])$", row["sourceName"], re.I)
            if phalanx and row.get("side") in ("left", "right") and row["sourceName"] != "Distal phalanx of fifth finger of hand.l":
                level_en, ordinal_en, limb, _suffix = phalanx.groups()
                level, ordinal_en, limb = level_en.casefold(), ordinal_en.casefold(), limb.casefold()
                member_code = f"{level}:{ordinal_en}:{row['side']}"
                exact_member = any(rel.get("relationKind") == "class_member" and rel.get("memberCode") == member_code
                                   for rel in row.get("targetRelationEvidence", []))
                if not exact_member:
                    raise SystemExit("phalanx composition lacks exact side/member crosswalk: " + row["sourceName"])
                level_ko, level_source = {
                    "proximal": ("첫", "kli-t100-phalanx-proximal-opened"),
                    "middle": ("중간", "kli-t100-phalanx-middle-opened"),
                    "distal": ("끝", "kli-t100-phalanx-distal-opened"),
                }[level]
                digit_ko = {"first": "엄지", "second": "둘째", "third": "셋째", "fourth": "넷째", "fifth": "다섯째"}[ordinal_en]
                digit_type = "손가락" if limb == "hand" else "발가락"
                value = digit_ko + digit_type + " " + level_ko + "마디뼈"
                relation_ids = sorted({
                    source_id for rel in row.get("targetRelationEvidence", [])
                    if rel.get("relationKind") == "class_member" and rel.get("memberCode") == member_code
                    for source_id in rel.get("matchEvidenceSourceIds", [])
                })
                ids = list(dict.fromkeys(["kli-t100-phalanx-root-opened", level_source, *relation_ids]))
                row["names"]["koModern"] = value
                row["label"] = value
                row.setdefault("nameEvidence", {})["koModern"] = {
                    "value": value,
                    "sourceIds": ids,
                    "locator": "구성명이며 독립 사전 표제어 주장이 아님: 손발가락뼈 범위, " + level
                               + " 마디뼈 용어, 원본 손가락/발가락 순번 및 exact T96 memberCode " + member_code
                               + "를 결합. 좌우는 이름에서 제외.",
                }
                updates.append({
                    "sourceKey": row["sourceKey"], "sourceName": row["sourceName"],
                    "value": value, "composition": "phalanx-root+level+digit", "sourceIds": ids,
                })

            metacarpal = re.match(r"^(First|Second|Third|Fourth|Fifth) metacarpal bone\.([lr])$", row["sourceName"], re.I)
            if metacarpal and row.get("side") in ("left", "right") and not row["names"].get("koModern"):
                ordinal_en = metacarpal.group(1).casefold()
                member_code = "metacarpal:" + ordinal_en + ":" + row["side"]
                relations = [rel for rel in row.get("targetRelationEvidence", [])
                             if rel.get("relationKind") == "class_member" and rel.get("memberCode") == member_code]
                if not relations:
                    raise SystemExit("metacarpal composition lacks exact class member: " + row["sourceName"])
                ordinal_ko = {"first": "첫째", "second": "둘째", "third": "셋째", "fourth": "넷째", "fifth": "다섯째"}[ordinal_en]
                value = ordinal_ko + " 손허리뼈"
                ids = list(dict.fromkeys(["kli-t100-metacarpal-root-opened", *sorted({
                    sid for rel in relations for sid in rel.get("matchEvidenceSourceIds", [])
                })]))
                row["names"]["koModern"] = value
                row["label"] = value
                row.setdefault("nameEvidence", {})["koModern"] = {
                    "value": value, "sourceIds": ids,
                    "locator": "구성명이며 독립 사전 표제어 주장이 아님: 중수골 항목의 다듬을 말 손허리뼈, 원본 순번 "
                               + ordinal_en + " 및 exact T96 memberCode " + member_code + "를 결합. 좌우는 이름에서 제외.",
                }
                updates.append({
                    "sourceKey": row["sourceKey"], "sourceName": row["sourceName"],
                    "value": value, "composition": "metacarpal-root+ordinal", "sourceIds": ids,
                })

            if row["sourceName"] in ("Triquetrum bone.l", "Triquetrum bone.r"):
                value = "세모뼈"
                row["names"]["koModern"] = value
                row["label"] = value
                row.setdefault("nameEvidence", {})["koModern"] = {
                    "value": value,
                    "sourceIds": ["kli-t100-triquetrum-list-opened", "fipat-ta2-t96-frozen-target-terms"],
                    "locator": "열린 손목뼈 목록의 세모뼈; 원본 Triquetrum bone 및 exact T96 carpal:triquetrum member. 손목뼈 전체가 아님.",
                }
                updates.append({
                    "sourceKey": row["sourceKey"], "sourceName": row["sourceName"], "value": value,
                    "composition": "exact-carpal-member",
                    "sourceIds": ["kli-t100-triquetrum-list-opened", "fipat-ta2-t96-frozen-target-terms"],
                })
            if row["sourceName"] in ("Trapezium bone.l", "Trapezium bone.r"):
                value = "큰마름뼈"
                row["names"]["koModern"] = value
                row["label"] = value
                row.setdefault("nameEvidence", {})["koModern"] = {
                    "value": value,
                    "sourceIds": ["kli-t100-trapezium-opened", "fipat-ta2-t96-frozen-target-terms"],
                    "locator": "큰마름뼈 표제어의 영어 대응 trapezium bone 및 exact T96 carpal:trapezium member. 기존 legacy field는 변경하지 않음.",
                }
                updates.append({
                    "sourceKey": row["sourceKey"], "sourceName": row["sourceName"], "value": value,
                    "composition": "exact-carpal-member",
                    "sourceIds": ["kli-t100-trapezium-opened", "fipat-ta2-t96-frozen-target-terms"],
                })

        aliases = sorted({alias for row in rows for alias in row.get("aliases", [])})
        target_synonyms = []
        for target in hits:
            for language, values in target.get("term", {}).get("sourceSynonyms", {}).items():
                target_synonyms.append({"language": language, "values": values, "targetId": target["id"]})
        if hit_ids:
            base_concept = {
                "classification": "exact_target_term_or_source_synonym",
                "targetConcepts": [{"targetId": t["id"], "english": t["term"]["english"], "latin": t["term"]["latin"]} for t in hits],
            }
        elif shared_member:
            base_concept = {
                "classification": "source_class_member_relation",
                "targetConcepts": [{"targetId": tid, "english": next((x["term"]["english"] for x in targets if x["id"] == tid), None)} for tid in shared_member["targetIds"]],
            }
        else:
            base_concept = {"classification": "source_label_observation_only", "sourceBaseLabel": label}
        part_match = re.match(r"^(.+?)\s+(?:part|head) of\s+(.+)$", label, re.I)
        part_qualifier = part_match.group(1).casefold() if part_match else None
        group_records.append({
            "conceptKey": None if conflict_group else concept_key,
            "kind": kind,
            "sourceBaseLabel": label,
            "baseConcept": base_concept,
            "surfaceSourceKeys": [r["sourceKey"] for r in rows],
            "surfaceSides": [{"sourceKey": r["sourceKey"], "side": r.get("side")} for r in rows],
            "laterality": "conflict_or_unresolved" if conflict_group else
                          "explicit_bilateral_pair" if {r.get("side") for r in rows} == {"left", "right"} else
                          "source_side_as_observed",
            "conflicts": conflicts,
            "regionIds": sorted({region for row in rows for region in row.get("regionIds", [])}),
            "baseConceptClass": kind,
            "partOrGroupClass": classify_part(label),
            "partQualifier": part_qualifier,
            "ordinal": extract_ordinal(label),
            "targetExactNameHits": [{"targetId": t["id"], "english": t["term"]["english"], "latin": t["term"]["latin"],
                                     "matchedValues": t["_matchedExactValues"]} for t in hits],
            "verifiedMemberRelations": [
                {"sourceKey": r["sourceKey"], "memberCode": m["memberCode"], "targetIds": m["targetIds"], "evidenceIds": m["evidenceIds"]}
                for r, m in zip(rows, members) if m
            ],
            "synonyms": {"sourceAliases": aliases, "targetSourceSynonyms": target_synonyms},
            "linkClassification": "side_or_source_identity_conflict" if conflict_group else link_type,
            "learnerBinding": "opaque key only; no HA canonical binding",
            "sourceOnly": True, "rights": "held", "humanReview": "not_performed",
        })
    target_by_num = {int(target["id"].split(":")[1]): target for target in targets}
    mapped_surfaces = defaultdict(list)
    exact_source_index = defaultdict(list)
    for row in overlay["objects"]:
        for target_id in set([row.get("targetId")] + list(row.get("targetIds", []))):
            if target_id:
                mapped_surfaces[target_id].append(row)
        source_record = compiled.get(row["sourceKey"], {})
        labels = {base(row.get("sourceName", "")), base(source_record.get("dataName") or "")}
        for text in labels:
            if text:
                exact_source_index[norm(text)].append({
                    "sourceKey": row["sourceKey"], "sourceName": row.get("sourceName"),
                    "dataName": source_record.get("dataName"), "side": row.get("side"),
                    "kind": row.get("kind"), "regionIds": row.get("regionIds", []),
                })

    gap_counts = Counter()
    gap_records = []
    for snapshot in candidate_free:
        target = target_by_num[int(snapshot["targetId"].split(":")[1])]
        lexical_terms = [target.get("term", {}).get("english", ""), target.get("term", {}).get("latin", "")]
        for values in target.get("term", {}).get("sourceSynonyms", {}).values():
            lexical_terms.extend(values)
        observations = {}
        for term in lexical_terms:
            if term:
                for row in exact_source_index.get(norm(term), []):
                    observations[row["sourceKey"]] = row
        descendants = []
        parent_num = int(target["id"].split(":")[1])
        for child in targets:
            if child["id"] != target["id"] and parent_num in child.get("sourceAncestryIds", []):
                for row in mapped_surfaces.get(child["id"], []):
                    descendants.append({
                        "descendantTargetId": child["id"], "sourceKey": row["sourceKey"],
                        "sourceName": row["sourceName"], "side": row.get("side"),
                    })
        descendants = list({(x["descendantTargetId"], x["sourceKey"]): x for x in descendants}.values())
        # A mapped ancestor surface can explain why an exact target candidate is
        # absent from this package, but it cannot stand in for target-specific
        # geometry. T96 records ancestry in nearest-to-farthest order; preserve
        # that order and keep each surface as an explicit, non-binding observation.
        ancestors = []
        ancestry_ids = [ancestor_id for ancestor_id in target.get("sourceAncestryIds", [])
                        if ancestor_id != parent_num]
        for depth, ancestor_num in enumerate(ancestry_ids, start=1):
            ancestor_id = f"TA2:{ancestor_num}"
            ancestor_target = target_by_num.get(ancestor_num)
            if ancestor_target is None:
                continue
            for row in mapped_surfaces.get(ancestor_id, []):
                ancestors.append({
                    "ancestorTargetId": ancestor_id,
                    "ancestorEnglish": ancestor_target.get("term", {}).get("english"),
                    "ancestryDepth": depth,
                    "sourceKey": row["sourceKey"],
                    "sourceName": row["sourceName"],
                    "side": row.get("side"),
                    "regionIds": row.get("regionIds", []),
                    "relationBasis": "T96 sourceAncestryIds + existing source overlay targetId/targetIds",
                    "targetSpecificGeometryProven": False,
                    "learnerBindingCreated": False,
                })
        ancestors = list({(x["ancestorTargetId"], x["sourceKey"]): x for x in ancestors}.values())
        if observations:
            category = "exact_source_label_observation_identity_crosswalk_needed"
        elif descendants:
            category = "descendant_surface_representation_present_target_specific_surface_unresolved"
        elif ancestors:
            category = "ancestor_surface_representation_present_target_specific_surface_unresolved"
        else:
            category = "no_exact_descendant_or_ancestor_surface_evidence_in_frozen_package"
        gap_counts[category] += 1
        if observations:
            conclusion = "exact source label exists, but this is not a validated target identity relation"
        elif descendants:
            conclusion = "descendant candidate surfaces exist; they do not prove target-specific whole geometry"
        elif ancestors:
            conclusion = "ancestor/group candidate surfaces exist; they do not prove target-specific geometry or membership"
        else:
            conclusion = "no exact label or mapped hierarchy surface in this frozen package; absence outside this package is unproven"
        gap_records.append({
            "targetId": target["id"], "english": target["term"]["english"], "latin": target["term"]["latin"],
            "semanticKind": target["semanticKind"], "primaryOwner": target["primaryOwner"],
            "regionIds": target["regionIds"], "sourceSynonyms": target["term"].get("sourceSynonyms", {}),
            "targetAncestryIds": [f"TA2:{value}" for value in ancestry_ids],
            "exactSourceLabelObservations": sorted(observations.values(), key=lambda x: x["sourceKey"]),
            "descendantSurfaceRepresentations": descendants,
            "ancestorSurfaceRepresentations": ancestors,
            "category": category, "geometryAssessment": conclusion,
            "candidateFreeMetricPreserved": True, "noFuzzySubstringOrParentOnlyJoin": True,
        })

    bilateral_groups = sum(1 for group in group_records if group["laterality"] == "explicit_bilateral_pair")
    conflict_groups = sum(1 for group in group_records if group["conflicts"])
    concept_doc = {
        "schemaVersion": 1, "taskId": "T100",
        "workUnit": "226 unnamed eligible surfaces, side-deduplicated concept classification",
        "denominator": {
            "surfaceRows": 226, "conceptGroups": 113,
            "bilateralGroups": bilateral_groups, "conflictGroups": conflict_groups,
        },
        "inputHashes": {
            "overlayBefore": "e99a3169ff424b494003f885aebce437f3fa7258522b69719dd8fe27ca2affab",
            "targetScope": "dba3f2a2dee6c732515e71082d62506b88375b0f88af392c950356703013ac24",
            "compiledManifest": "56ffd2d93d9a4c4b0b3954511c471358e3da54f47e6915c35d4b6111f1b7f42",
        },
        "linkCountsBySurface": dict(link_counts), "nameUpdates": updates, "groups": group_records,
    }
    gap_doc = {
        "schemaVersion": 1, "taskId": "T100",
        "workUnit": "163 candidate-free target expression-versus-gap triage",
        "denominator": {"candidateFreeTargets": 163},
        "categoryCounts": dict(gap_counts),
        "interpretation": "Frozen-package-only exact-name and mapped-descendant scan. No fuzzy or substring joins; exact label observations do not prove canonical identity, and no source-wide absence is claimed.",
        "targets": gap_records,
    }
    if args.apply and args.check:
        raise SystemExit("choose either --apply or --check")
    if args.check:
        if not has_semantic_links:
            raise SystemExit("semantic overlay has not been applied")
        if current_overlay != overlay:
            raise SystemExit("current overlay does not match deterministic semantic builder")
    if args.apply:
        write(OVERLAY, overlay)
    write(OUT / "unnamed-concept-classification.json", concept_doc)
    write(OUT / "target-gap-classification.json", gap_doc)
    print(json.dumps({
        "applied": args.apply, "unnamedSurfaceRows": len(unnamed), "conceptGroups": len(groups),
        "bilateralGroups": bilateral_groups, "conflictGroups": conflict_groups,
        "linksBySurface": dict(link_counts), "newModernNames": len(updates),
        "newNamesByValue": dict(Counter(row["value"] for row in updates)),
        "candidateFreeCategories": dict(gap_counts),
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
