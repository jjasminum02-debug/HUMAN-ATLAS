#!/usr/bin/env python3
"""Deterministically build the T96 TA2 target and region-package freeze.

This is a local data/evidence builder. It never mutates source assets, app code,
canonical claims, rights state, or human-review state.
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "work/evidence/T96"
OUT_SCOPE = ROOT / "atlas-data/catalog/target-scope-t96.json"
OUT_INDEX = ROOT / "atlas-data/manifests/region-packages-t96.json"
OUT_PACKAGES = ROOT / "atlas-data/manifests/region-target-packages-t96"
REVISION = "T96-2026-09-28-semantic-freeze-v1"
MAX_UNIT = 10
CHECK_MODE = "--check" in sys.argv

INPUT_PATHS = [
    "design/2026-09-25-muscle-atlas/22-EFFICIENT-DELIVERY-AND-PERFORMANCE.md",
    "design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md",
    "work/tasks/T96.md",
    "work/tasks/T110.md", "work/tasks/T111.md", "work/tasks/T112.md",
    "work/tasks/T113.md", "work/tasks/T114.md", "work/tasks/T115.md",
    "work/tasks/T116.md", "work/tasks/T117.md", "work/tasks/T118.md",
    "work/tasks/T119.md", "work/tasks/T120.md", "work/tasks/T121.md",
    "work/evidence/T78/reference/source.json",
    "work/evidence/T78/reference/ta2-scope.json",
    "work/evidence/T78/classification-ledger.json",
    "work/evidence/T78/targets.json",
    "work/evidence/T78/source-elements.json",
    "work/evidence/T78/inventory-summary.json",
    "work/evidence/T78/target-task-map.json",
    "work/reports/T78.md",
    "work/reports/T95.md",
    "work/evidence/T95/overlay-validation.json",
    "atlas-data/catalog/canonical-catalog.json",
    "atlas-data/catalog/source-crosswalk.json",
    "atlas-data/catalog/whole-body-inventory-t15g.json",
    "atlas-data/terminology/learning-names.json",
    "atlas-data/terminology/ai-evidence-overlay.json",
    "atlas-data/motion/motion-learning.json",
    "atlas-data/navigation/atlas-navigation.json",
    "atlas-data/source-cache/bodyparts3d-r4/converted/t77/manifest.json",
]

REGIONS = [
    ("head", "머리", "Head", "T110"),
    ("neck", "목", "Neck", "T111"),
    ("back", "등", "Back", "T112"),
    ("shoulder-scapular", "어깨·어깨뼈", "Shoulder and scapular region", "T113"),
    ("thorax", "가슴우리", "Thorax", "T114"),
    ("abdomen-lumbar", "배·허리", "Abdomen and lumbar region", "T115"),
    ("pelvis-perineum", "골반·샅", "Pelvis and perineum", "T116"),
    ("gluteal-hip", "볼기·깊은엉덩이", "Gluteal and deep hip region", "T117"),
    ("thigh", "넙다리", "Thigh", "T118"),
    ("leg", "종아리", "Leg", "T119"),
    ("foot", "발", "Foot", "T120"),
    ("upper-limb", "팔·손", "Upper limb", "T121"),
]
REGION_META = {r[0]: r for r in REGIONS}
TASK_META = {r[3]: r for r in REGIONS}
REGION_INDEX = {r[0]: i for i, r in enumerate(REGIONS)}

# Explicit row decisions. TA2 identifiers and source hierarchy are preserved.
EXCLUDED_CANDIDATES = {
    **{i: "bone_morphology_taxonomy_not_a_located_bone_target" for i in range(367, 377)},
    1010: "cross_region_vertebral_column_aggregate",
    1141: "cross_region_upper_limb_bone_aggregate",
    1305: "cross_region_lower_limb_bone_aggregate",
    1359: "cross_region_free_lower_limb_bone_aggregate",
    2450: "cross_region_upper_limb_muscle_aggregate",
    2592: "cross_region_lower_limb_muscle_aggregate",
    2370: "inguinal_ring_crus_not_muscle_part",
    2371: "inguinal_ring_crus_not_muscle_part",
    2504: "aponeurotic_extensor_expansion_band_not_muscle_part",
    2647: "aponeurotic_extensor_expansion_band_not_muscle_part",
}
PROMOTED_FROM_SUPPORT = {
    2605: {"kind": "named_muscle", "reason": "named deep gluteal muscle, exact TA2 child of deep gluteal muscles"},
    2636: {"kind": "named_muscle", "reason": "named medial thigh muscle, exact TA2 child of medial thigh compartment"},
    880: {"kind": "bone_group", "reason": "named auditory-ossicle collection, exact skeletal-system row"},
    1105: {"kind": "bone_series", "reason": "named rib series, exact child of bones of thorax"},
    1118: {"kind": "bone", "reason": "named generic rib concept, exact child of ribs"},
    1282: {"kind": "bone_group", "reason": "named bony pelvis concept, exact skeletal-system row"},
}
MUSCLE_ROOTS = {
    2039: "head", 2145: "neck", 2224: "back", 2298: "thorax",
    2355: "abdomen-lumbar", 2396: "pelvis-perineum", 2451: "shoulder-scapular",
    2449: "upper-limb", 2591: "gluteal-hip", 2609: "thigh", 2626: "thigh",
    2637: "thigh", 2643: "leg", 2651: "leg", 2654: "leg", 2669: "foot",
}
BONE_ROOTS = {
    # The root is the closest exact TA2 branch that fits one product package.
    406: "head", 834: "head", 880: "head",
    1031: "neck", 1058: "back", 1067: "back", 1071: "pelvis-perineum", 1092: "pelvis-perineum",
    1096: "thorax", 1142: "shoulder-scapular", 1179: "upper-limb",
    1282: "pelvis-perineum", 1306: "pelvis-perineum", 1307: "pelvis-perineum",
    1359: None, 1360: "thigh", 1389: "thigh", 1397: "leg", 1427: "leg", 1446: "foot",
    # TA2's top-level facial-bone collection has its own direct parent branch.
    353: "head",
}
EXPLICIT_REGION_MEMBERSHIPS = {
    # Existing T78 curated cross-region contexts, reviewed against their exact TA2 terms.
    2230: {"add": ["neck"], "remove": ["shoulder-scapular"], "basis": "TA2 name transversus nuchae; posterior neck context; reject inherited heuristic shoulder tag"},
    2231: {"add": ["shoulder-scapular"], "basis": "T78 exact cross-region decision and T75 latissimus source target; no new mesh binding"},
    2234: {"add": ["neck", "shoulder-scapular"], "basis": "T78 exact cross-region decision; TA2 levator scapulae term"},
    2593: {"add": ["abdomen-lumbar"], "basis": "T78 explicit iliopsoas cross-region context"},
    2595: {"add": ["abdomen-lumbar"], "basis": "T78 explicit psoas-major cross-region context"},
    2605: {"add": ["pelvis-perineum"], "basis": "T78 planned deep-hip/pelvis context retained after promotion"},
    # Exact source hierarchy makes scapulohumeral targets shoulder-primary and limb-visible.
    2451: {"add": ["upper-limb"], "basis": "exact TA2 scapulohumeral branch nested under upper-limb system"},
    # T95 explicitly added the left scapula to upper-limb product context; right was already there.
    1143: {"add": ["upper-limb"], "basis": "T95 overlay-validation.json; left FJ3279 product context plus existing right FJ3384"},
    # Inconstant extra ribs are thoracic targets with a source-named adjacent region context.
    1116: {"add": ["neck"], "basis": "TA2 exact term cervical rib; source marks it as an inconstant rib variant"},
    1117: {"add": ["back"], "basis": "TA2 exact term lumbar rib; source marks it as an inconstant rib variant"},
}
COMPLEX_IDS = {2054, 2254, 2403, 2593, 2613, 2656}
REPEAT_FAMILY_IDS = {
    2237, 2238, 2239,
    2284, 2285, 2286, 2287, 2288, 2289,
    2290, 2291, 2292, 2293, 2294, 2295, 2296, 2297,
    2308, 2309, 2310, 2311, 2312, 2313, 2314,
    2532, 2533, 2534, 2685, 2686, 2687,
}
PART_RECLASS = {2632, 2680}
NAMED_RECLASS = {2055}


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_path(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def rendered_json(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n").encode("utf-8")


def write_json(path: Path, value):
    expected = rendered_json(value)
    if CHECK_MODE:
        if not path.exists() or path.read_bytes() != expected:
            raise ValueError(f"non-reproducible or missing generated output: {path.relative_to(ROOT)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(expected)


def term_en(row: dict) -> str | None:
    term = row.get("term", {})
    return term.get("en") or term.get("en_US") or term.get("en_GB")


def term_la(row: dict) -> str | None:
    return row.get("term", {}).get("la")


def ancestry(row_id: int, rows_by_id: dict[int, dict]) -> list[int]:
    result = []
    seen = set()
    current = rows_by_id.get(row_id)
    while current is not None:
        current_id = current["id"]
        if current_id in seen:
            raise ValueError(f"TA2 parent cycle at {current_id}")
        seen.add(current_id)
        result.append(current_id)
        parent_id = current.get("parent")
        current = rows_by_id.get(parent_id) if parent_id is not None else None
    return result


def semantic_kind(row_id: int, prior_kind: str, row: dict) -> str:
    if row_id in {880, 1282}:
        return "bone_group"
    if row_id == 1105:
        return "bone_series"
    if row_id == 1118:
        return "bone"
    if row_id in COMPLEX_IDS:
        return "muscle_complex"
    if row_id == 2055:
        return "named_muscle"
    if row_id in PART_RECLASS:
        return "muscle_part"
    if prior_kind == "serial_muscle_family":
        return "repeated_muscle_family" if row_id in REPEAT_FAMILY_IDS else "muscle_group"
    if prior_kind == "bone_or_bone_series":
        en = (term_en(row) or "").lower()
        la = (term_la(row) or "").lower()
        plural = en.startswith(("bones of ", "bones ", "accessory bones", "auditory ossicles", "facial bones", "cervical vertebrae", "thoracic vertebrae", "lumbar vertebrae", "true ribs", "false ribs", "floating ribs", "supernumerary ribs", "carpal bones", "metacarpal bones", "phalanges", "sesamoid bones", "tarsal bones", "metatarsal bones", "suprasternal bones"))
        latin_plural = la.startswith(("ossa ", "vertebrae ", "costae", "phalanges "))
        if plural or latin_plural:
            return "bone_series" if any(w in en for w in ("vertebra", "rib", "phalange", "metacarpal", "metatarsal")) or la.startswith(("vertebrae ", "costae", "phalanges ")) else "bone_group"
        return "bone"
    return prior_kind


def primary_owner(row_id: int, row: dict, rows_by_id: dict[int, dict], target_kind: str) -> str:
    path = ancestry(row_id, rows_by_id)
    if target_kind in {"named_muscle", "muscle_group", "muscle_part", "muscle_complex", "repeated_muscle_family"}:
        for ancestor_id in path:
            if ancestor_id in MUSCLE_ROOTS:
                return MUSCLE_ROOTS[ancestor_id]
        raise ValueError(f"no explicit muscular primary owner for TA2:{row_id} {term_en(row)}")
    if target_kind in {"bone", "bone_group", "bone_series"}:
        # Reject top-level/disjoint aggregates here; they should have an explicit exclusion.
        for ancestor_id in path:
            if ancestor_id in BONE_ROOTS:
                owner = BONE_ROOTS[ancestor_id]
                if owner is None:
                    break
                return owner
        raise ValueError(f"no explicit skeletal primary owner for TA2:{row_id} {term_en(row)}")
    raise ValueError(f"unsupported target kind {target_kind} for TA2:{row_id}")


def explicit_side(row: dict) -> str | None:
    values = [term_en(row) or "", term_la(row) or ""]
    joined = " ".join(values).lower()
    right = "right " in joined or " dexter" in joined or joined.startswith("dexter")
    left = "left " in joined or " sinister" in joined or joined.startswith("sinister")
    if right and left:
        return "conflicted_source_side"
    if right:
        return "right"
    if left:
        return "left"
    return None


def support_reason(row_id: int, row: dict, rows_by_id: dict[int, dict]) -> str:
    path = ancestry(row_id, rows_by_id)
    ancestors = set(path[1:])
    en = (term_en(row) or "").lower()
    la = (term_la(row) or "").lower()
    if row_id in EXCLUDED_CANDIDATES:
        return EXCLUDED_CANDIDATES[row_id]
    if row_id in {1975, 1976, 1977, 1978, 1979, 1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994}:
        return "general_muscle_classification_or_morphology_not_located_target"
    if row_id in {366, 377, 1010, 1011, 1141, 1305, 1359, 2450, 2592}:
        return "generic_or_cross_region_structural_context"
    if row_id in {6923, 6925}:
        return "ta2_primary_secondary_usage_alias_not_an_additional_target"
    if row.get("primary_usage") or row.get("secondary_usage"):
        return "ta2_explicit_primary_secondary_usage_alias_not_an_additional_target"
    if 1974 in ancestors:
        if any(k in en + " " + la for k in ["fascia", "aponeuros", "tendon", "tendo", "bursa", "ligament", "retinaculum", "sheath", "trochlea", "arch", "septum", "expansion", "crus of superficial inguinal ring"]):
            return "supporting_connective_tissue_or_auxiliary_muscle_associated_structure"
        if any(k in en + " " + la for k in ["head of muscle", "belly of muscle", "fascicle of muscle"]):
            return "generic_part_taxonomy_not_a_located_named_part"
        if 1975 in ancestors and row_id < 2039:
            return "general_muscle_classification_or_morphology_not_located_target"
        return "supporting_musculoskeletal_context_not_a_named_muscle_or_muscle_part"
    if 352 in ancestors or row_id == 352:
        if row_id in range(367, 377):
            return "bone_morphology_taxonomy_not_a_located_bone_target"
        if any(k in en + " " + la for k in ["bone", "ossa ", "ossicula", "vertebra", "cost", "costa", "os ", "femur", "scapula", "clavicle", "rib", "pelvis ossea"]):
            return "skeletal_taxonomy_or_bone_substructure_context; reviewed_against_candidate_reverse_scan"
        return "osteological_landmark_joint_or_supporting_skeletal_context_not_a_bone_target"
    return "outside_regional_muscle_and_bone_target_scope_in_frozen_TA2_snapshot"


def main() -> None:
    source_rows = read_json(ROOT / "work/evidence/T78/reference/ta2-scope.json")
    rows_by_id = {row["id"]: row for row in source_rows}
    prior_ledger_rows = read_json(ROOT / "work/evidence/T78/classification-ledger.json")
    prior_ledger = {row["ta2Id"]: row for row in prior_ledger_rows}
    prior_targets = read_json(ROOT / "work/evidence/T78/targets.json")
    prior_target_by_id = {int(row["id"].split(":", 1)[1]): row for row in prior_targets}
    source_rows_sha = sha_path(ROOT / "work/evidence/T78/reference/ta2-scope.json")
    source_metadata = read_json(ROOT / "work/evidence/T78/reference/source.json")
    crosswalk = read_json(ROOT / "atlas-data/catalog/source-crosswalk.json")
    crosswalk_by_row = {item["tableRow"]: item for item in crosswalk["catalogItems"]}
    canonical = read_json(ROOT / "atlas-data/catalog/canonical-catalog.json")
    canonical_entities = canonical.get("entities", {}).get("muscleConcepts", [])
    canonical_by_id = {item.get("id"): item for item in canonical_entities if item.get("id")}
    whole_inventory = read_json(ROOT / "atlas-data/catalog/whole-body-inventory-t15g.json")
    inventory_by_concept = {item["id"]: item for item in whole_inventory.get("currentMuscleConceptInventory", [])}
    source_elements = read_json(ROOT / "work/evidence/T78/source-elements.json")
    source_by_id = {item["id"]: item for item in source_elements}
    runtime = read_json(ROOT / "atlas-data/source-cache/bodyparts3d-r4/converted/t77/manifest.json")
    runtime_assets = {asset["id"]: asset for chunk in runtime["chunks"] for asset in chunk["assets"]}
    navigation = read_json(ROOT / "atlas-data/navigation/atlas-navigation.json")
    t95_overlay = read_json(ROOT / "work/evidence/T95/overlay-validation.json")

    input_hashes = {path: sha_path(ROOT / path) for path in INPUT_PATHS}
    input_hashes["work/evidence/T78/reference/ta2-scope.json"] = source_rows_sha

    prior_ids = set(prior_target_by_id)
    excluded_ids = set(EXCLUDED_CANDIDATES)
    promoted_ids = set(PROMOTED_FROM_SUPPORT)
    if len(prior_ids) != 556:
        raise ValueError(f"expected 556 T78 target rows, found {len(prior_ids)}")
    if len(excluded_ids) != 20 or len(promoted_ids) != 6:
        raise ValueError("T96 reconciliation decision set changed unexpectedly")
    if not excluded_ids <= prior_ids:
        raise ValueError(f"exclusion is not an original candidate: {sorted(excluded_ids-prior_ids)}")
    if not promoted_ids.isdisjoint(prior_ids):
        raise ValueError("promotion already appears in T78 target list")
    if not promoted_ids <= set(rows_by_id):
        raise ValueError("promoted TA2 row missing from frozen source snapshot")
    if any(prior_ledger.get(i, {}).get("kind") != "supporting_nomenclature_not_geometry_target" for i in promoted_ids):
        raise ValueError("promotion does not originate in the T78 support ledger")

    final_ids = sorted((prior_ids - excluded_ids) | promoted_ids)
    if len(final_ids) != 542:
        raise ValueError(f"expected 542 target concepts after 556 - 20 + 6, got {len(final_ids)}")

    target_records = []
    rows_by_target_id = {}
    for row_id in final_ids:
        row = rows_by_id[row_id]
        prior = prior_target_by_id.get(row_id)
        prior_kind = prior_ledger.get(row_id, {}).get("kind", "supporting_nomenclature_not_geometry_target")
        kind = PROMOTED_FROM_SUPPORT[row_id]["kind"] if row_id in PROMOTED_FROM_SUPPORT else semantic_kind(row_id, prior_kind, row)
        owner = primary_owner(row_id, row, rows_by_id, kind)
        region_ids = {owner}
        basis = "nearest exact TA2 regional branch"
        exception = EXPLICIT_REGION_MEMBERSHIPS.get(row_id)
        if exception:
            for region_id in exception.get("remove", []):
                region_ids.discard(region_id)
            region_ids.update(exception.get("add", []))
            basis += "; " + exception["basis"]
        # Scapulohumeral entries are owned by the shoulder package but remain limb members.
        if 2451 in ancestry(row_id, rows_by_id):
            region_ids.add("upper-limb")
            basis += "; exact scapulohumeral branch is nested in TA2 upper limb"
        # Rib variants remain thoracic target records; their source-named contexts are secondary.
        target_id = f"TA2:{row_id}"
        crosswalk_item = crosswalk_by_row.get(row_id)
        canonical_id = crosswalk_item["stableConceptId"] if crosswalk_item else None
        canonical_entity = canonical_by_id.get(canonical_id) if canonical_id else None
        inventory_row = inventory_by_concept.get(canonical_id) if canonical_id else None
        side = explicit_side(row)
        t78_state = prior.get("states", {}) if prior else None
        source_candidates = prior.get("sourceCandidates", []) if prior else []
        target = {
            "id": target_id,
            "ta2Id": row_id,
            "term": {"latin": term_la(row), "english": term_en(row), "sourceSynonyms": row.get("synonyms", {})},
            "sourceFlags": {
                "inconstant": row.get("inconstant"),
                "sex": row.get("sex"),
                "primaryUsage": row.get("primary_usage"),
                "secondaryUsage": row.get("secondary_usage"),
                "relatedTerms": row.get("related_terms", []),
                "noteReferences": row.get("note_references", []),
                "seeAlso": row.get("see_also", []),
                "disambiguationTerm": row.get("disambiguation_term"),
            },
            "semanticKind": kind,
            "priorT78Kind": prior_kind,
            "priorT78Candidate": prior is not None,
            "sourceParentId": row.get("parent"),
            "sourceParentTargetId": f"TA2:{row['parent']}" if row.get("parent") in final_ids else None,
            "sourceAncestryIds": ancestry(row_id, rows_by_id),
            "primaryOwner": owner,
            "regionIds": sorted(region_ids, key=lambda r: REGION_INDEX[r]),
            "regionDecisionBasis": basis,
            "scopeFlags": {
                "ta2Inconstant": row.get("inconstant") == "true",
                "sourceSex": row.get("sex"),
                "explicitSourceSide": side,
                "repeatedFamilyMemberCount": None if kind == "repeated_muscle_family" else "not_applicable_or_not_source_specified",
                "individualMuscleDenominatorContribution": "named_whole_muscle_record; not summed as a whole-body denominator" if kind == "named_muscle" and row.get("inconstant") != "true" and not row.get("sex") else "not_counted_without_variant_part_or_member_resolution",
            },
            "sourceCardinality": {
                "lateralityState": "explicit_source_side" if side else "not_specified_by_source",
                "explicitSourceSide": side,
                "bilateralInstanceCount": None,
                "midlineInstanceCount": None,
                "repeatedFamilyMemberCount": None if kind == "repeated_muscle_family" else "not_applicable_or_not_source_specified",
                "expansionPerformed": False,
            },
            "existingEvidence": {
                "sourceLexicalCandidates": source_candidates,
                "sourceCandidateMeaning": "lexical_candidate_only_not_identity_or_binding" if source_candidates else "none_recorded_in_T78",
                "priorT78States": t78_state,
                "canonicalStableConceptId": canonical_id,
                "canonicalCrosswalkState": crosswalk_item.get("reviewState") if crosswalk_item else "no_exact_tableRow_join",
                "canonicalEntityPresent": canonical_entity is not None,
                "t15gInventoryRowPresent": inventory_row is not None,
                "learningOverlayStatus": inventory_row.get("learningNameOverlay", {}).get("status") if inventory_row else "no_exact_crosswalk_join",
                "aiEvidenceJoin": "no_direct_TA2_tableRow_to_HA-M_join_used",
                "motionJoin": "no_direct_TA2_tableRow_to_HA-M_join_used",
                "runtimeAssetIdsFromLexicalCandidates": [sid for sid in source_candidates if sid in runtime_assets],
            },
            "contentState": {
                "semanticClassification": "frozen_from_TA2_2.07_tree_with_T96_reviewed_rules",
                "sourceIdentity": "not_approved_by_lexical_match",
                "geometry": (t78_state or {}).get("geometry", "unresolved_not_in_T78_target_list"),
                "side": "exact_source_side_only" if side else "not_inferred",
                "frame": (t78_state or {}).get("frame", "not_reconciled"),
                "canonicalBinding": (t78_state or {}).get("binding", "not_reconciled"),
                "threeNames": (t78_state or {}).get("threeNames", "not_reconciled"),
                "originInsertion": (t78_state or {}).get("originInsertion", "not_reconciled"),
                "function": (t78_state or {}).get("function", "not_reconciled"),
                "animation": (t78_state or {}).get("animation", "not_reconciled"),
                "humanReview": False,
                "rights": "not_promoted",
            },
        }
        if row_id in PROMOTED_FROM_SUPPORT:
            target["promotionReason"] = PROMOTED_FROM_SUPPORT[row_id]["reason"]
        target_records.append(target)
        rows_by_target_id[row_id] = target

    # Map support and removed candidates back to the full source ledger without dropping any row.
    final_by_id = {r["ta2Id"]: r for r in target_records}
    semantic_ledger = []
    for row in source_rows:
        row_id = row["id"]
        prior_kind = prior_ledger[row_id]["kind"]
        if row_id in final_by_id:
            item = final_by_id[row_id]
            disposition = "included_target"
            reason = "T96 semantic target retained; exact source target record and owner are frozen"
            semantic = item["semanticKind"]
            primary = item["primaryOwner"]
            product_regions = item["regionIds"]
        elif row_id in EXCLUDED_CANDIDATES:
            disposition = "excluded_candidate_with_explicit_reconciliation"
            reason = EXCLUDED_CANDIDATES[row_id]
            semantic = prior_kind
            primary = None
            product_regions = []
        else:
            disposition = "supporting_nomenclature_not_region_target"
            reason = support_reason(row_id, row, rows_by_id)
            semantic = "supporting_context"
            primary = None
            product_regions = []
        semantic_ledger.append({
            "ta2Id": row_id,
            "sourceLevel": row.get("level"),
            "sourceTerm": row.get("term", {}),
            "sourceSynonyms": row.get("synonyms", {}),
            "sourceRelatedTerms": row.get("related_terms", []),
            "sourceNoteReferences": row.get("note_references", []),
            "parentId": row.get("parent"),
            "english": term_en(row),
            "latin": term_la(row),
            "priorT78Kind": prior_kind,
            "disposition": disposition,
            "semanticKind": semantic,
            "decisionReason": reason,
            "targetId": f"TA2:{row_id}" if row_id in final_by_id else None,
            "primaryOwner": primary,
            "regionIds": product_regions,
            "ta2PrimaryUsage": row.get("primary_usage"),
            "ta2SecondaryUsage": row.get("secondary_usage"),
            "ta2Inconstant": row.get("inconstant") == "true",
            "ta2Sex": row.get("sex"),
            "sourceOtherAttributes": {k: v for k, v in row.items() if k not in {"id", "level", "term", "synonyms", "related_terms", "note_references", "parent", "inconstant", "sex", "primary_usage", "secondary_usage"}},
        })

    # Explicit usage links are a source-native alias graph, not extra concepts.
    usage_aliases = []
    for row in source_rows:
        if row.get("primary_usage") is not None:
            usage_aliases.append({"sourceId": row["id"], "relation": "primary_usage", "referencedId": row["primary_usage"]})
        if row.get("secondary_usage") is not None:
            usage_aliases.append({"sourceId": row["id"], "relation": "secondary_usage", "referencedId": row["secondary_usage"]})

    # Exact crosswalk joins are recorded as evidence availability only; no name fuzzy joins.
    target_counts = Counter(r["semanticKind"] for r in target_records)
    by_owner = defaultdict(list)
    for target in target_records:
        by_owner[target["primaryOwner"]].append(target)
    if set(by_owner) != {r[0] for r in REGIONS}:
        raise ValueError(f"not all 12 region owners have targets: {set(by_owner)}")

    package_documents = []
    package_index_rows = []
    for region_id, label_ko, label_en, task_id in REGIONS:
        region_targets = sorted(by_owner[region_id], key=lambda item: item["ta2Id"])
        ids = [item["id"] for item in region_targets]
        membership_count = sum(1 for target in target_records if region_id in target["regionIds"])
        work_units = []
        for offset in range(0, len(ids), MAX_UNIT):
            unit_number = len(work_units) + 1
            unit_ids = ids[offset:offset + MAX_UNIT]
            unit_targets = [next(t for t in region_targets if t["id"] == target_id) for target_id in unit_ids]
            work_units.append({
                "unitId": f"{task_id}-U{unit_number:03d}",
                "ordinal": unit_number,
                "targetIds": unit_ids,
                "targetCount": len(unit_ids),
                "targetsSha256": sha_bytes(canonical_json(unit_targets)),
                "status": "planned_not_started",
            })
        package = {
            "schemaVersion": "1.0.0",
            "revision": REVISION,
            "status": "frozen_input_not_started",
            "taskId": task_id,
            "regionId": region_id,
            "regionLabelKo": label_ko,
            "regionLabelEn": label_en,
            "ownerRule": "each target assigned exactly once by explicit TA2 ancestry mapping or listed explicit override",
            "inputHashes": input_hashes,
            "scopeManifest": "atlas-data/catalog/target-scope-t96.json",
            "targetIds": ids,
            "targetCount": len(ids),
            "workUnitLimit": MAX_UNIT,
            "workUnits": work_units,
            "nextUnit": work_units[0]["unitId"] if work_units else None,
            "progress": {"completedUnits": 0, "totalUnits": len(work_units), "completedTargets": 0, "totalTargets": len(ids)},
            "coverageBoundary": "this is a TA2 named target package, not complete visual/content coverage or an individual-muscle denominator",
        }
        path = f"atlas-data/manifests/region-target-packages-t96/{task_id}.json"
        package_documents.append((path, package))
        package_index_rows.append({"taskId": task_id, "regionId": region_id, "path": path, "sha256": sha_bytes(rendered_json(package)), "targetCount": len(ids), "primaryTargetCount": len(ids), "regionMembershipCount": membership_count, "workUnitCount": len(work_units), "nextUnit": package["nextUnit"]})

    target_scope = {
        "schemaVersion": "1.0.0",
        "revision": REVISION,
        "status": "frozen_ta2_scope_with_individual_muscle_denominator_unresolved",
        "source": {
            "name": "FIPAT Terminologia Anatomica, 2nd edition, online TA2 vocabulary 2.07",
            "retrieval": source_metadata,
            "snapshotPath": "work/evidence/T78/reference/ta2-scope.json",
            "snapshotSha256": source_rows_sha,
            "targetDefinition": "locatable named skeletal bone/bone-series or named skeletal muscle, muscle complex/group/repeated family/part in the frozen 12-region target scope; morphology taxonomy and cross-region roll-up rows are support context",
        },
        "inputHashes": input_hashes,
        "reconciliation": {
            "priorT78TargetCount": len(prior_ids),
            "removedWithExplicitReasons": sorted(f"TA2:{i}" for i in excluded_ids),
            "promotedFromSupportingLedger": sorted(f"TA2:{i}" for i in promoted_ids),
            "finalTargetCount": len(target_records),
            "arithmetic": "556 - 20 explicit exclusions + 6 exact source omissions = 542",
            "supportingLedgerRowsRetained": len(source_rows) - len(prior_ids) + len(excluded_ids) - len(promoted_ids),
            "noSourceRowDeleted": True,
        },
        "denominators": {
            "frozenTa2NamedTargetRecords": len(target_records),
            "primaryOwnerAssignments": len(target_records),
            "productRegionMembershipRows": sum(len(target["regionIds"]) for target in target_records),
            "targetKinds": dict(sorted(target_counts.items())),
            "wholeBodyIndividualMuscleDenominator": None,
            "reasonIndividualMuscleDenominatorNull": "TA2 target hierarchy mixes named whole muscles, groups, complexes, explicit parts, inconstant variants and repeated families; the repeated member/side counts are not specified uniformly and cannot be summed into unique individual muscles.",
            "boneTargetsAreNotMeshOrSideInstanceCounts": True,
            "ta2InconstantTargets": sum(bool(r["scopeFlags"]["ta2Inconstant"]) for r in target_records),
            "sexSpecificTargetRecords": sum(r["scopeFlags"]["sourceSex"] is not None for r in target_records),
            "explicitSideTargetRecords": sum(r["scopeFlags"]["explicitSourceSide"] is not None for r in target_records),
            "bilateralIndividualMuscleInstanceCount": None,
            "midlineIndividualMuscleInstanceCount": None,
            "repeatedFamilyTargetRecords": target_counts.get("repeated_muscle_family", 0),
            "repeatedFamilyMemberCounts": None,
        },
        "regions": [{
            "regionId": region_id, "labelKo": label_ko, "labelEn": label_en,
            "primaryTargetCount": len(by_owner.get(region_id, [])),
            "regionMembershipCount": sum(1 for target in target_records if region_id in target["regionIds"]),
            "taskId": task_id,
            "packagePath": f"atlas-data/manifests/region-target-packages-t96/{task_id}.json",
        } for region_id, label_ko, label_en, task_id in REGIONS],
        "aliasPolicy": {
            "sourceNativeUsageLinksPath": "work/evidence/T96/ta2-usage-aliases.json",
            "linkCount": len(usage_aliases),
            "rule": "primary_usage/secondary_usage are preserved as exact TA2 cross-reference aliases; they do not mint another anatomical target or stable ID",
        },
        "rulesPath": "work/evidence/T96/decision-rules.json",
        "ledgerPath": "work/evidence/T96/semantic-classification-ledger.json",
        "targets": target_records,
    }
    package_index = {
        "schemaVersion": "1.0.0",
        "revision": REVISION,
        "status": "all_targets_assigned_once_internal_units_bounded_not_started",
        "taskId": "T96",
        "scopePath": "atlas-data/catalog/target-scope-t96.json",
        "scopeSha256": sha_bytes(rendered_json(target_scope)),
        "inputHashes": input_hashes,
        "targetCount": len(target_records),
        "productRegionMembershipCount": sum(len(target["regionIds"]) for target in target_records),
        "wholeBodyIndividualMuscleDenominator": None,
        "workUnitLimit": MAX_UNIT,
        "packages": package_index_rows,
        "allTargetIdsExactlyOnce": True,
        "downstreamTasksStarted": False,
    }

    EVIDENCE.mkdir(parents=True, exist_ok=True)
    OUT_PACKAGES.mkdir(parents=True, exist_ok=True)
    write_json(OUT_SCOPE, target_scope)
    for path, package in package_documents:
        write_json(ROOT / path, package)
    # Package index hashes are recomputed against the byte-canonical payloads above.
    write_json(OUT_INDEX, package_index)
    write_json(EVIDENCE / "semantic-classification-ledger.json", semantic_ledger)
    write_json(EVIDENCE / "ta2-usage-aliases.json", {
        "sourceSnapshotSha256": source_rows_sha,
        "count": len(usage_aliases),
        "aliases": usage_aliases,
    })
    write_json(EVIDENCE / "input-hashes.json", {
        "task": "T96",
        "revision": REVISION,
        "hashes": input_hashes,
        "sourceRowCount": len(source_rows),
        "sourceSnapshotSha256": source_rows_sha,
    })
    write_json(EVIDENCE / "references.json", {
        "task": "T96",
        "frozenSource": {
            "title": "Terminologia Anatomica, 2nd edition, online vocabulary 2.07",
            "sourceUrl": source_metadata["source"],
            "viewerDataUrl": source_metadata["dataUrl"],
            "retrievedOn": source_metadata["retrieved"],
            "viewerVersion": source_metadata["version"]["viewer"],
            "vocabularyVersion": source_metadata["version"]["vocab"],
            "rawViewerJsSha256": source_metadata["rawSha256"],
            "snapshotPath": "work/evidence/T78/reference/ta2-scope.json",
            "snapshotSha256": source_rows_sha,
            "accessMethod": "Official viewer data bundle read as text and parsed from embedded vocabulary rows; JavaScript was not executed. The 2,422-row snapshot is the exact hierarchy/term input.",
            "limitation": "The published PDF was not downloaded or visually checked locally for every table row; selected candidate corrections have publisher-index evidence below.",
        },
        "publisherEvidence": [
            {
                "url": "https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf",
                "edition": "FIPAT TA2 2nd edition, Part 2; official-hosted PDF; online revision 2.07",
                "locator": "Printed page 37, table row 880",
                "observedRows": [{"ta2Id": 880, "latin": "Ossicula auditus", "english": "Auditory ossicles"}],
                "accessedOn": "2026-09-28",
                "accessMethod": "Official publisher-hosted PDF search index; exact table row returned. The PDF binary was not locally downloaded/visually audited.",
                "use": "Confirms the auditory-ossicle collection is a named skeletal target; its primary/secondary usage edge remains an alias, not a second target."
            },
            {
                "url": "https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf",
                "edition": "FIPAT TA2 2nd edition, Part 2; official-hosted PDF; online revision 2.07",
                "locator": "Printed page 44, table rows 1105 and 1118",
                "observedRows": [
                    {"ta2Id": 1105, "latin": "Costae", "english": "Ribs", "sourceSynonyms": ["Costae I-XII", "Ribs 1-12"]},
                    {"ta2Id": 1118, "latin": "Costa", "english": "Rib", "sourceSynonyms": ["Os costale", "Rib bone"]}
                ],
                "accessedOn": "2026-09-28",
                "accessMethod": "Official publisher-hosted PDF search index; exact table rows returned. The PDF binary was not locally downloaded/visually audited.",
                "use": "Confirms the rib series and generic rib concept are separate named hierarchy rows; they are not multiplied into individual rib instances."
            },
            {
                "url": "https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf",
                "edition": "FIPAT TA2 2nd edition, Part 2; official-hosted PDF; online revision 2.07",
                "locator": "Printed page 49, table row 1282",
                "observedRows": [{"ta2Id": 1282, "latin": "Pelvis ossea", "english": "Bony pelvis"}],
                "accessedOn": "2026-09-28",
                "accessMethod": "Official publisher-hosted PDF search index; exact table row returned. The PDF binary was not locally downloaded/visually audited.",
                "use": "Confirms a named bony-pelvis skeletal collection row; it remains a concept/group rather than an extra bone instance."
            },
            {
                "url": "https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf",
                "edition": "FIPAT TA2 2nd edition, Part 2; official-hosted PDF; online revision 2.07",
                "locator": "Printed page 94, table rows 2605 and 2636",
                "observedRows": [
                    {"ta2Id": 2605, "term": "Obturator internus / Obturator internus muscle", "latin": "Musculus obturatorius internus"},
                    {"ta2Id": 2636, "term": "Obturator externus / Obturator externus muscle", "latin": "Musculus obturatorius externus"}
                ],
                "accessedOn": "2026-09-28",
                "accessMethod": "Official PDF search index exposed exact table rows and printed-page locator; the PDF binary was not locally downloaded/visually audited.",
                "use": "Confirms two named muscles omitted from the T78 support-to-target heuristic; ownership follows exact TA2 parent hierarchy."
            },
            {
                "url": "https://fipat.library.dal.ca/wp-content/uploads/2021/08/FIPAT-TA2-Errata.pdf",
                "edition": "FIPAT TA2 official errata overview",
                "locator": "Version table, row 2.07; dated 16 August 2021 and Part II marked corrected",
                "accessedOn": "2026-09-28",
                "accessMethod": "Official-hosted PDF search-index text; not locally downloaded/visually checked.",
                "use": "Records the online vocabulary edition alignment; the snapshot names 2.07 explicitly."
            },
            {
                "url": "https://fipat.library.dal.ca/",
                "edition": "FIPAT terminology landing page",
                "locator": "TA2 publication and errata links",
                "accessedOn": "2026-09-28",
                "accessMethod": "Official FIPAT page opened in browser.",
                "use": "Publisher authority and source navigation."
            }
        ],
        "semanticLimit": "The freeze audits terminology and task ownership. It is not independent human anatomy review, tissue-source coverage proof, geometry identity approval, or redistribution-license approval."
    })
    state_matrix = []
    for target in target_records:
        state_matrix.append({
            "targetId": target["id"],
            "ta2TableRow": target["ta2Id"],
            "geometry": target["contentState"]["geometry"],
            "sourceIdentity": target["contentState"]["sourceIdentity"],
            "side": target["contentState"]["side"],
            "frame": target["contentState"]["frame"],
            "canonicalBinding": target["contentState"]["canonicalBinding"],
            "threeNames": target["contentState"]["threeNames"],
            "originInsertion": target["contentState"]["originInsertion"],
            "function": target["contentState"]["function"],
            "animation": target["contentState"]["animation"],
            "humanReview": target["contentState"]["humanReview"],
            "rights": target["contentState"]["rights"],
            "exactCanonicalConceptId": target["existingEvidence"]["canonicalStableConceptId"],
            "canonicalReviewState": target["existingEvidence"]["canonicalCrosswalkState"],
            "learningNameOverlayStatus": target["existingEvidence"]["learningOverlayStatus"],
            "runtimeAssetCandidates": target["existingEvidence"]["runtimeAssetIdsFromLexicalCandidates"],
            "aiEvidenceJoin": target["existingEvidence"]["aiEvidenceJoin"],
            "motionJoin": target["existingEvidence"]["motionJoin"]
        })
    write_json(EVIDENCE / "content-state-crosscheck.json", {
        "task": "T96",
        "revision": REVISION,
        "policy": "canonical records join only on exact TA2 tableRow; HA-M/AI/motion records are not joined by similar display text",
        "exactCanonicalJoinCount": sum(row["exactCanonicalConceptId"] is not None for row in state_matrix),
        "canonicalCrosswalkRows": len(crosswalk["catalogItems"]),
        "canonicalCrosswalkRowsJoinedToFrozenTarget": sum(item["tableRow"] in final_ids for item in crosswalk["catalogItems"]),
        "canonicalCrosswalkRowsKeptAsExplicitNonTargetContext": [
            {"stableConceptId": item["stableConceptId"], "ta2TableRow": item["tableRow"], "reason": EXCLUDED_CANDIDATES[item["tableRow"]]}
            for item in crosswalk["catalogItems"] if item["tableRow"] in EXCLUDED_CANDIDATES
        ],
        "canonicalCrosswalkRowsWithoutFrozenTargetOrExplicitExclusion": [
            item["tableRow"] for item in crosswalk["catalogItems"]
            if item["tableRow"] not in final_ids and item["tableRow"] not in EXCLUDED_CANDIDATES
        ],
        "exactCanonicalReviewStateCounts": dict(sorted(Counter(row["canonicalReviewState"] for row in state_matrix if row["exactCanonicalConceptId"] is not None).items())),
        "learningNameStatusCountsOnExactCanonicalJoins": dict(sorted(Counter(row["learningNameOverlayStatus"] for row in state_matrix if row["exactCanonicalConceptId"] is not None).items())),
        "lexicalRuntimeCandidateTargetCount": sum(bool(row["runtimeAssetCandidates"]) for row in state_matrix),
        "independentStateCounts": {
            field: dict(sorted(Counter(str(row[field]) for row in state_matrix).items()))
            for field in ["geometry", "side", "frame", "canonicalBinding", "threeNames", "originInsertion", "function", "animation", "humanReview", "rights"]
        },
        "canonicalClaimsCreated": 0,
        "bindingsCreated": 0,
        "humanReviewPromotions": 0,
        "rightsPromotions": 0,
        "aiAndMotionNoFuzzyJoin": True,
        "targets": state_matrix
    })
    write_json(EVIDENCE / "decision-rules.json", {
        "task": "T96",
        "revision": REVISION,
        "sourceEdition": source_metadata["version"],
        "sourceUrl": source_metadata["source"],
        "scopePrinciples": [
            "Keep every source row in the all-row ledger; target selection never deletes or rewrites TA2 source terms.",
            "Target means a region-locatable named bone/bone series or muscle/group/complex/part/repeated family in the twelve product categories.",
            "Morphologic bone classes 367-376 classify bone form and are not located structures; retain as source context, not regional targets.",
            "Cross-region roll-ups 1010, 1141, 1305, 1359, 2450 and 2592 summarize children spanning multiple packages; children remain and the roll-up is not counted again.",
            "Parts 2370-2371 are crura of superficial inguinal ring; 2504/2647 are aponeurotic expansion bands, not muscle tissue parts.",
            "Every TA2 inconstant flag and explicit sex/side term is preserved on its own row; it does not create inferred bilateral copies or repetition counts.",
            "A repeated-family concept is one target record; member counts remain null unless the source explicitly fixes them, and no aggregate becomes an individual-muscle denominator.",
            "A source group/complex and its named children may both remain targets for semantic navigation; count fields keep those kinds disjoint from single named muscles.",
            "Exactly one internal primary owner is assigned; only explicit T78/T95 cross-region rules add secondary product region memberships.",
            "TA2 primary_usage/secondary_usage links are aliases, never extra targets. No fuzzy crosswalk is used.",
            "Lexical source candidates, geometry, side, frame, canonical binding, three-name state, origin/insertion, function, animation, human review and rights remain independent.",
        ],
        "explicitCandidateExclusions": [{"id": f"TA2:{i}", "reason": EXCLUDED_CANDIDATES[i]} for i in sorted(EXCLUDED_CANDIDATES)],
        "promotionsFromSupport": [{"id": f"TA2:{i}", **PROMOTED_FROM_SUPPORT[i]} for i in sorted(PROMOTED_FROM_SUPPORT)],
        "semanticKindOverrides": {
            "repeatFamilies": sorted(f"TA2:{i}" for i in REPEAT_FAMILY_IDS),
            "otherOldSerialFamilyRowsBecomeMuscleGroups": True,
            "compoundComplexes": sorted(f"TA2:{i}" for i in COMPLEX_IDS),
            "TA2_2055_is_named_muscle": True,
            "TA2_2632_and_2680_are_hierarchical_muscle_parts": True,
        },
        "primaryOwnerRoots": {
            "muscle": {str(k): v for k, v in MUSCLE_ROOTS.items()},
            "bone": {str(k): v for k, v in BONE_ROOTS.items()},
            "regionOrder": [r[0] for r in REGIONS],
        },
        "secondaryRegionOverrides": {f"TA2:{i}": rule for i, rule in sorted(EXPLICIT_REGION_MEMBERSHIPS.items())},
        "identityAndApprovalBoundary": {
            "canonicalJoin": "exact FIPAT tableRow only",
            "bodyParts3dNameMatch": "lexical candidate only",
            "humanReview": False,
            "publicRedistributionRights": "not promoted",
            "claimGeometryBindingCreated": False,
        },
    })
    semantic_audit_rows = []
    for row_id in sorted(excluded_ids | promoted_ids):
        row = rows_by_id[row_id]
        path_ids = ancestry(row_id, rows_by_id)
        path_rows = [rows_by_id[parent_id] for parent_id in reversed(path_ids)]
        previous = prior_target_by_id.get(row_id)
        current = rows_by_target_id.get(row_id)
        semantic_audit_rows.append({
            "ta2Id": row_id,
            "sourceLocator": {
                "source": "official TA2Viewer 2.07 vocabulary snapshot",
                "snapshotPath": "work/evidence/T78/reference/ta2-scope.json",
                "snapshotRowId": row_id,
                "edition": source_metadata["version"],
                "snapshotSha256": source_rows_sha,
            },
            "sourceTerm": row.get("term", {}),
            "sourceSynonyms": row.get("synonyms", {}),
            "sourceParentId": row.get("parent"),
            "sourceParentChain": [{"ta2Id": item["id"], "term": item.get("term", {})} for item in path_rows],
            "previousT78Disposition": "candidate" if previous else "supporting_ledger",
            "previousT78Kind": prior_ledger[row_id].get("kind"),
            "t96Decision": "exclude_candidate" if row_id in excluded_ids else "promote_support_row",
            "decisionReason": EXCLUDED_CANDIDATES.get(row_id) or PROMOTED_FROM_SUPPORT[row_id]["reason"],
            "frozenTarget": ({"id": current["id"], "semanticKind": current["semanticKind"], "primaryOwner": current["primaryOwner"], "regionIds": current["regionIds"]} if current else None),
        })
    write_json(EVIDENCE / "semantic-exception-review.json", {
        "task": "T96", "revision": REVISION,
        "sourceSnapshotPath": "work/evidence/T78/reference/ta2-scope.json",
        "sourceSnapshotSha256": source_rows_sha,
        "reviewedExceptionCount": len(semantic_audit_rows),
        "candidateExclusions": len(excluded_ids),
        "supportPromotions": len(promoted_ids),
        "rows": semantic_audit_rows,
        "interpretation": "Per-row semantics are read from the exact official TA2Viewer 2.07 row and parent chain. Publisher PDF search-index corroboration for promoted rows is separately recorded in references.json; it is not a local visual audit of every PDF page.",
    })
    muscle_subtree_rows = [row for row in source_rows if 1974 in ancestry(row["id"], rows_by_id)]
    semantic_ledger_by_id = {item["ta2Id"]: item for item in semantic_ledger}
    support_muscle_lexical_rows = []
    for row in muscle_subtree_rows:
        row_id = row["id"]
        if row_id in final_by_id:
            continue
        searchable = json.dumps({"term": row.get("term", {}), "synonyms": row.get("synonyms", {})}, ensure_ascii=False).lower()
        if "muscle" not in searchable and "muscul" not in searchable:
            continue
        row_path = ancestry(row_id, rows_by_id)
        support_muscle_lexical_rows.append({
            "ta2Id": row_id,
            "term": row.get("term", {}),
            "synonyms": row.get("synonyms", {}),
            "parentId": row.get("parent"),
            "parentChainIds": list(reversed(row_path)),
            "priorT78Kind": prior_ledger[row_id].get("kind"),
            "disposition": semantic_ledger_by_id[row_id]["disposition"],
            "decisionReason": semantic_ledger_by_id[row_id]["decisionReason"],
        })
    write_json(EVIDENCE / "supporting-muscle-reverse-scan.json", {
        "task": "T96", "revision": REVISION,
        "sourceSnapshotPath": "work/evidence/T78/reference/ta2-scope.json",
        "sourceSnapshotSha256": source_rows_sha,
        "muscularSystemRootTa2Id": 1974,
        "muscularSystemSubtreeRowCount": len(muscle_subtree_rows),
        "nonTargetSubtreeRows": sum(1 for row in muscle_subtree_rows if row["id"] not in final_by_id),
        "nonTargetSubtreeRowsWhoseTermOrSynonymsContainMuscleStem": len(support_muscle_lexical_rows),
        "supportRowsRequiringSemanticReview": support_muscle_lexical_rows,
        "restoredNamedMusclesFromSupport": [
            {"ta2Id": i, "term": rows_by_id[i].get("term", {}), "reason": PROMOTED_FROM_SUPPORT[i]["reason"]}
            for i in [2605, 2636]
        ],
        "scopeFinding": "The lexical reverse scan is a review queue, not an automatic target classifier. Exact source terms/parent chains were checked; the two located named-muscle omissions are promoted above. Other matches are general morphology, regional system headings/rollups, aliases, connective/accessory structures or supporting context as shown row by row.",
        "humanAnatomyReview": False,
    })
    write_json(EVIDENCE / "freeze-summary.json", {
        "task": "T96", "revision": REVISION, "status": "passed_with_gaps",
        "sourceRows": len(source_rows), "priorCandidates": len(prior_ids), "explicitRemoved": len(excluded_ids),
        "promoted": len(promoted_ids), "frozenTargets": len(target_records),
        "targetKinds": dict(sorted(target_counts.items())),
        "wholeBodyIndividualMuscleDenominator": None,
        "aliasLinks": len(usage_aliases),
        "regions": {r[0]: len(by_owner[r[0]]) for r in REGIONS},
        "productRegionMemberships": sum(len(target["regionIds"]) for target in target_records),
        "primaryOwnerAssignments": len(target_records),
        "workUnitCount": sum(len(package["workUnits"]) for _, package in package_documents),
        "workUnits": {package["taskId"]: len(package["workUnits"]) for _, package in package_documents},
        "allUnitsPlannedNotStarted": True,
        "humanAnatomyReview": "not performed",
        "geometryCanonicalNameActionMotionStates": "not promoted by this freeze",
    })

if __name__ == "__main__":
    main()
