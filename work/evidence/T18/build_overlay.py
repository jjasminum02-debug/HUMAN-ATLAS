#!/usr/bin/env python3
"""Append the T18 source-bound fields to the learner evidence overlay.

All output summaries are tied to the T17 source-research manifest. The script
preserves existing overlay rows, denominator state, catalog claims, reviews and
canonical IDs; it never creates a human review or spatial geometry.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent
MANIFEST_PATH = EVIDENCE / "source-manifest.json"
ACCESS_PATH = EVIDENCE / "run-2026-09-27/access-ledger.json"
OVERLAY_PATH = ROOT / "atlas-data/terminology/ai-evidence-overlay.json"
REGISTRY_PATH = ROOT / "atlas-data/sources/registry.json"


def module_from(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = module_from(ROOT / "atlas-data/schemas/validate_ai_evidence.py", "t18_ai_evidence_validator")
manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
access_payload = json.loads(ACCESS_PATH.read_text(encoding="utf-8"))
source_by_id = {row["id"]: row for row in manifest["sources"]}
access_by_id = {row["id"]: row for row in access_payload["accesses"]}

TEMPLE = "T18-HANDS-ON-ANATOMY-2024"
STATPEARLS = "T18-STATPEARLS-FOOT-MUSCLES-2025"
PARENT = {
    "HA-M-000001": {
        "origin": ("cross_checked", [("비복근은 대퇴골 안쪽관절융기와 가쪽관절융기에서 시작합니다.", [TEMPLE, STATPEARLS])]),
        "insertion": ("cross_checked", [("비복근은 발꿈치뼈(종골)에 정지합니다.", [TEMPLE, STATPEARLS])]),
    },
    "HA-M-000002": {
        "origin": ("cross_checked", [("가자미근은 종아리뼈 뒤쪽과 정강뼈 뒤쪽에서 시작합니다.", [TEMPLE, STATPEARLS])]),
        "insertion": ("cross_checked", [("가자미근은 종골에 정지합니다.", [TEMPLE, STATPEARLS])]),
    },
    "HA-M-000003": {
        "origin": ("cross_checked", [("앞정강근은 정강뼈 가쪽관절융기·몸쪽 정강뼈와 뼈사이막에서 시작합니다.", [TEMPLE, STATPEARLS])]),
        "insertion": ("cross_checked", [("앞정강근은 안쪽쐐기뼈와 첫째 중족골 바닥에 정지합니다.", [TEMPLE, STATPEARLS])]),
    },
    "HA-M-000004": {
        "origin": ("cross_checked", [("뒤정강근은 정강뼈와 뼈사이막에서 시작합니다.", [TEMPLE, STATPEARLS])]),
        "insertion": ("cross_checked", [("뒤정강근은 발배뼈·쐐기뼈·입방뼈와 둘째~넷째 중족골에 정지합니다.", [TEMPLE, STATPEARLS])]),
    },
    "HA-M-000005": {
        "origin": ("conflicted", [
            ("Hands-on Anatomy(2024): 종아리뼈 머리와 위쪽 3분의 2에서 시작합니다.", [TEMPLE]),
            ("StatPearls(2025 갱신): 종아리뼈 머리와 위쪽 절반에서 시작합니다.", [STATPEARLS]),
        ]),
        "insertion": ("cross_checked", [("긴종아리근은 첫째 중족골 바닥과 안쪽쐐기뼈에 정지합니다.", [TEMPLE, STATPEARLS])]),
    },
    "HA-M-000006": {
        "origin": ("cross_checked", [("짧은종아리근은 종아리뼈 아래쪽 3분의 2에서 시작합니다.", [TEMPLE, STATPEARLS])]),
        "insertion": ("cross_checked", [("짧은종아리근은 다섯째 중족골 바닥 부위에 정지합니다.", [TEMPLE, STATPEARLS])]),
    },
}

PARTS = {
    "HA-P-000001": {
        "origin": ("single_source", [("비복근 외측두는 대퇴골 외측관절융기에서 시작합니다.", [TEMPLE])]),
        "insertion": ("cross_checked", [("자료에는 비복근의 공통 정지가 종골로 기록되어 있고, 외측두만의 별도 원위 부착면은 나뉘어 제시되지 않습니다.", [TEMPLE, STATPEARLS])]),
    },
    "HA-P-000002": {
        "origin": ("single_source", [("비복근 내측두는 대퇴골 내측관절융기에서 시작합니다.", [TEMPLE])]),
        "insertion": ("cross_checked", [("자료에는 비복근의 공통 정지가 종골로 기록되어 있고, 내측두만의 별도 원위 부착면은 나뉘어 제시되지 않습니다.", [TEMPLE, STATPEARLS])]),
    },
}


def registry_rows() -> list[dict[str, Any]]:
    common = {
        "category": "modern_anatomy_reference",
        "access_state": "opened_full_text_online_2026_09_27; field locators captured in work/evidence/T18/source-manifest.json",
        "artifact_state": "no_local_copy; source observations and paraphrases only; no source images copied",
        "intended_use_candidate": "Internal educational origin/insertion comparison only; not a canonical human review or exact attachment-surface source.",
    }
    return [
        {
            **common,
            "id": TEMPLE,
            "title": source_by_id[TEMPLE]["title"],
            "organization": "Temple University Press / North Broad Press",
            "edition": source_by_id[TEMPLE]["edition"],
            "edition_status": "2024 copyright/publication verified; numbered edition not stated",
            "primary_locator": source_by_id[TEMPLE]["url"],
            "license": {
                "name": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
                "status": "copyright page states all material is CC BY 4.0 unless otherwise noted",
                "url": "https://creativecommons.org/licenses/by/4.0/",
                "note": "Chapter text is paraphrased. The chapter's OpenStax figures are separately credited and were not copied or incorporated.",
            },
            "limitations": ["Concise educational table; not a complete footprint map or individual-variation review.", "The source includes palpation guidance, but T18 uses only origin/insertion rows."],
        },
        {
            **common,
            "id": STATPEARLS,
            "title": source_by_id[STATPEARLS]["title"],
            "organization": "StatPearls Publishing / NCBI Bookshelf",
            "edition": source_by_id[STATPEARLS]["edition"],
            "edition_status": "article citation and update date shown below Table 1",
            "primary_locator": source_by_id[STATPEARLS]["url"],
            "license": {
                "name": "Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0)",
                "status": "page copyright notice identifies CC BY-NC-ND 4.0",
                "url": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
                "note": "Used only for this private local comparison with attribution. No public sharing or redistribution of adapted text is authorized by T18; review rights before any external use.",
            },
            "limitations": ["A compact table; omission of a structure is not evidence that an attachment is absent.", "The shared citation identifies the containing article but does not prove an independent primary anatomical dataset."],
        },
    ]


def add_sources_to_project_registry() -> None:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    current = {row["id"]: row for row in registry["sources"]}
    for row in registry_rows():
        prior = current.get(row["id"])
        if prior is None:
            registry["sources"].append(row)
        elif prior != row:
            raise ValueError(f"Existing source registry row differs; refusing to overwrite: {row['id']}")
    REGISTRY_PATH.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def access_id(parent_id: str, field: str, source_id: str) -> str:
    prefix = "HOA" if source_id == TEMPLE else "SP"
    return f"A-{prefix}-{parent_id}-{field}"


def make_item(subject_id: str, field: str, state: str, claim_specs: list[tuple[str, list[str]]], parent_id: str) -> dict[str, Any]:
    evidence_rows: list[dict[str, Any]] = []
    evidence_ids_by_source: dict[str, str] = {}
    used_source_ids = list(dict.fromkeys(source_id for _, supported in claim_specs for source_id in supported))
    for source_id in used_source_ids:
        aid = access_id(parent_id, field, source_id)
        access = access_by_id[aid]
        evidence_id = f"T18-E-{subject_id}-{field}-{'HOA' if source_id == TEMPLE else 'SP'}"
        evidence_ids_by_source[source_id] = evidence_id
        evidence = {
            "id": evidence_id,
            "sourceId": source_id,
            "locator": access["locator"],
            "accessedOn": access["accessedOn"],
            "accessMethod": access["accessMethod"],
            "textAccess": access["textAccess"],
            "supportsClaimIds": [],
        }
        evidence_rows.append(evidence)

    claims = []
    for index, (text, supporting_sources) in enumerate(claim_specs):
        claim_id = f"T18-C-{subject_id}-{field}-{'AB'[index] if len(claim_specs) == 2 else 'A'}"
        evidence_ids = [evidence_ids_by_source[source_id] for source_id in supporting_sources]
        claims.append({
            "id": claim_id,
            "value": text,
            "valueHash": validator.value_hash(text),
            "evidenceIds": evidence_ids,
            "attribution": "ai_source_summary" if len(supporting_sources) > 1 else "source_paraphrase",
        })
        for evidence in evidence_rows:
            if evidence["id"] in evidence_ids:
                evidence["supportsClaimIds"].append(claim_id)

    source_rows = []
    for source_id in used_source_ids:
        source = source_by_id[source_id]
        first_access = access_by_id[access_id(parent_id, field, source_id)]
        row = {
            "id": source_id,
            "underlyingWorkId": source["underlyingWorkId"],
            "title": source["title"],
            "url": source["url"],
            "editionStatus": source["editionStatus"],
            "edition": source["edition"],
            "accessedOn": first_access["accessedOn"],
            "accessMethod": first_access["accessMethod"],
            "textAccess": first_access["textAccess"],
        }
        row["sourceHash"] = validator.source_hash(row)
        source_rows.append(row)
    for row in evidence_rows:
        row["evidenceHash"] = validator.evidence_hash(row)
    return {
        "id": f"T18-FIELD-{subject_id}-{field}",
        "subjectId": subject_id,
        "field": field,
        "evidenceState": state,
        "claims": claims,
        "sources": source_rows,
        "evidence": evidence_rows,
        "geometryState": "absent",
        "motionState": "absent",
    }


def build_items() -> list[dict[str, Any]]:
    items = []
    for subject_id, fields in PARENT.items():
        for field, (state, claim_specs) in fields.items():
            items.append(make_item(subject_id, field, state, claim_specs, subject_id))
    for subject_id, fields in PARTS.items():
        parent_id = "HA-M-000001"
        for field, (state, claim_specs) in fields.items():
            items.append(make_item(subject_id, field, state, claim_specs, parent_id))
    return items


def main() -> None:
    if len(manifest["subjects"]) != 6 or len(manifest["extractions"]) != 24:
        raise ValueError("T18 manifest count mismatch; do not update the overlay")
    if access_payload["humanAnatomyReview"].get("performed") is not False:
        raise ValueError("Research tool indicates human review; refuse to build overlay")
    add_sources_to_project_registry()
    overlay = json.loads(OVERLAY_PATH.read_text(encoding="utf-8"))
    # Rebuild only rows owned by this task; retain every unrelated/current row.
    overlay["items"] = [row for row in overlay["items"] if not row.get("id", "").startswith("T18-FIELD-")]
    additions = build_items()
    existing_pairs = {(row["subjectId"], row["field"]) for row in overlay["items"]}
    if any((row["subjectId"], row["field"]) in existing_pairs for row in additions):
        raise ValueError("A T18 subject/field already exists; refusing duplicate or overwrite")
    overlay["revision"] = "T18-2026-09-27-calf-origin-insertion"
    overlay["items"].extend(additions)
    OVERLAY_PATH.write_text(json.dumps(overlay, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "overlay-build-summary.json").write_text(
        json.dumps({"addedRows": len(additions), "addedSubjectFields": [{"subjectId": row["subjectId"], "field": row["field"], "evidenceState": row["evidenceState"]} for row in additions], "denominatorFrozen": overlay["denominatorFrozen"], "wholeBodyIndividualMuscleCount": overlay["wholeBodyIndividualMuscleCount"], "coveragePercent": overlay["coveragePercent"], "humanAnatomyReviewPerformed": False, "canonicalClaimsWritten": False}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"addedRows": len(additions), "registrySources": len(registry_rows()), "overlayRevision": overlay["revision"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
