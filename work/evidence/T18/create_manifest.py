#!/usr/bin/env python3
"""Create the manually researched, six-muscle T18 source manifest.

This prepares only the source/access/extraction records already checked by hand.
It does not fetch pages, select anatomical truth, change a canonical claim, or
approve a human review.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).with_name("source-manifest.json")
MODULE_PATH = ROOT / "atlas-data/sources/source_research.py"
spec = importlib.util.spec_from_file_location("t17_source_research", MODULE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("Could not load the T17 source research helper")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

access_date = "2026-09-27"
temple_id = "T18-HANDS-ON-ANATOMY-2024"
statpearls_id = "T18-STATPEARLS-FOOT-MUSCLES-2025"
temple_url = "https://temple.manifoldapp.org/read/a852952e-bd23-4a54-be97-be3a7ef5039f/section/fbaf4654-749e-4c63-baed-5d17cf03aafe"
statpearls_url = "https://www.ncbi.nlm.nih.gov/books/NBK539705/table/article-32230.table0/"

sources = [
    {
        "id": temple_id,
        "underlyingWorkId": "WORK-HANDS-ON-ANATOMY-2024",
        "workIdentityBasis": "A separate 2024 textbook publication by Jacqueline Phillips and Michael O'Hara; its title/copyright page and Chapter 7 were opened. This is not the StatPearls table rehosted under another URL. Publication-level distinction is established; shared textbook lineage was not exhaustively traced.",
        "title": "7. The Knee and Lower Leg | Hands-on Anatomy",
        "url": temple_url,
        "editionStatus": "verified",
        "edition": "Hands-on Anatomy, 2024 publication (no numbered edition stated), Chapter 7: The Knee and Lower Leg; title/copyright page states ©2024.",
    },
    {
        "id": statpearls_id,
        "underlyingWorkId": "WORK-STATPEARLS-CARD-BORDONI-2025",
        "workIdentityBasis": "A separately titled and authored StatPearls review/table cited to RK Card and B Bordoni, updated 2025-12-09; the exact article citation is printed below Table 1. It is not a rehost of Hands-on Anatomy. Bibliographic separation is established; upstream source lineage was not exhaustively traced.",
        "title": "Table 1. Overview of the Extrinsic Foot Muscles | StatPearls",
        "url": statpearls_url,
        "editionStatus": "verified",
        "edition": "Card RK, Bordoni B. Anatomy, Bony Pelvis and Lower Limb, Foot Muscles. Updated 2025-12-09. In: StatPearls [Internet], 2026 Jan-. Table 1.",
    },
]

ids = [f"HA-M-00000{i}" for i in range(1, 7)]
labels = {
    "HA-M-000001": "비복근",
    "HA-M-000002": "가자미근",
    "HA-M-000003": "전경골근",
    "HA-M-000004": "후경골근",
    "HA-M-000005": "장비골근",
    "HA-M-000006": "단비골근",
}

# These values are compact structured transcriptions/paraphrases of the named
# source rows, not literal quotations and not human-reviewed anatomy claims.
observed = {
    "HA-M-000001": {
        "origin": (
            {"headAssignments": {"HA-P-000001": "lateral femoral condyle", "HA-P-000002": "medial femoral condyle"}, "condyles": ["lateral femoral condyle", "medial femoral condyle"]},
            {"headAssignments": None, "condyles": ["medial femoral condyle", "lateral femoral condyle"]},
            "Chapter 7 > Musculature with Palpation Instructions > Gastrocnemius > Origin(s)",
            "Table 1, Gastrocnemius row, Origin column",
        ),
        "insertion": (
            {"site": "calcaneus"},
            {"site": "calcaneus", "pathway": "joins soleus to form Achilles tendon"},
            "Chapter 7 > Gastrocnemius > Insertion(s)",
            "Table 1, Gastrocnemius row, Insertion column",
        ),
    },
    "HA-M-000002": {
        "origin": (
            {"fibula": "posterior head and superior aspect", "tibia": ["soleal line", "middle third"]},
            {"fibula": "upper one quarter, posterior", "tibia": "middle posterior"},
            "Chapter 7 > Soleus > Origin(s)",
            "Table 1, Soleus row, Origin column",
        ),
        "insertion": (
            {"site": "calcaneus"},
            {"site": "calcaneus", "pathway": "joins gastrocnemius to form Achilles tendon"},
            "Chapter 7 > Soleus > Insertion(s)",
            "Table 1, Soleus row, Insertion column",
        ),
    },
    "HA-M-000003": {
        "origin": (
            {"tibia": ["lateral condyle", "superior half"], "interosseousMembrane": True},
            {"tibia": ["lateral condyle", "proximal half of shaft"], "fibula": "superomedial", "interosseousMembrane": True},
            "Chapter 7 > Tibialis Anterior > Origin(s)",
            "Table 1, Tibialis anterior row, Origin column",
        ),
        "insertion": (
            {"bones": ["medial cuneiform", "base of first metatarsal"]},
            {"bones": ["medial cuneiform", "base of first metatarsal"], "surfaces": ["medial", "plantar"]},
            "Chapter 7 > Tibialis Anterior > Insertion(s)",
            "Table 1, Tibialis anterior row, Insertion column",
        ),
    },
    "HA-M-000004": {
        "origin": (
            {"bones": ["interosseous membrane", "tibia"]},
            {"tibia": "superior two thirds, medial posterior", "fibula": "posterior", "interosseousMembrane": True},
            "Chapter 7 > Tibialis Posterior > Origin(s)",
            "Table 1, Tibialis posterior row, Origin column",
        ),
        "insertion": (
            {"sites": ["navicular tuberosity", "cuneiforms", "cuboid", "sustentaculum tali", "bases of metatarsals 2-4"]},
            {"superficial": ["navicular tuberosity", "cuneiforms", "cuboid"], "deep": ["plantar bases of metatarsals 2-4"]},
            "Chapter 7 > Tibialis Posterior > Insertion(s)",
            "Table 1, Tibialis posterior row, Insertion column",
        ),
    },
    "HA-M-000005": {
        "origin": (
            {"fibula": ["head", "superior two thirds"]},
            {"fibula": ["head", "superior one half"]},
            "Chapter 7 > Fibularis Longus > Origin(s)",
            "Table 1, Fibularis longus row, Origin column",
        ),
        "insertion": (
            {"bones": ["base of first metatarsal", "medial cuneiform"]},
            {"bones": ["lateral base of first metatarsal", "posterolateral medial cuneiform"]},
            "Chapter 7 > Fibularis Longus > Insertion(s)",
            "Table 1, Fibularis longus row, Insertion column",
        ),
    },
    "HA-M-000006": {
        "origin": (
            {"fibula": "inferior two thirds"},
            {"fibula": "inferior two thirds, lateral"},
            "Chapter 7 > Fibularis Brevis > Origin(s)",
            "Table 1, Fibularis brevis row, Origin column",
        ),
        "insertion": (
            {"site": "lateral base of fifth metatarsal"},
            {"site": "styloid process of fifth metatarsal"},
            "Chapter 7 > Fibularis Brevis > Insertion(s)",
            "Table 1, Fibularis brevis row, Insertion column",
        ),
    },
}

comparisons = {
    ("HA-M-000001", "origin"): ("wording_difference", "Both sources name the medial and lateral femoral condyles. Hands-on Anatomy maps each condyle to its head; the StatPearls table does not split the mapping, so head-specific support remains single-source."),
    ("HA-M-000001", "insertion"): ("wording_difference", "Both place the insertion at the calcaneus; the StatPearls table additionally describes the shared Achilles-tendon pathway."),
    ("HA-M-000002", "origin"): ("wording_difference", "Both include posterior fibula and posterior tibia. Their extent wording differs; the records preserve each source rather than deriving one boundary."),
    ("HA-M-000002", "insertion"): ("wording_difference", "Both place the insertion at the calcaneus; the StatPearls table describes a shared Achilles-tendon pathway."),
    ("HA-M-000003", "origin"): ("wording_difference", "Both include the lateral tibial condyle, proximal tibia, and interosseous membrane. StatPearls also names the superomedial fibula; omission in the other source is not a contradiction."),
    ("HA-M-000003", "insertion"): ("wording_difference", "Both name the medial cuneiform and base of metatarsal I; StatPearls specifies medial and plantar surfaces."),
    ("HA-M-000004", "origin"): ("wording_difference", "Both name the tibia and interosseous membrane; StatPearls adds the posterior fibula and extent detail."),
    ("HA-M-000004", "insertion"): ("wording_difference", "Both name navicular, cuneiforms, cuboid, and metatarsal bases II-IV. Hands-on Anatomy also lists sustentaculum tali; StatPearls does not name it. This omission alone does not establish a variant or contradiction."),
    ("HA-M-000005", "origin"): ("substantive_conflict", "Both name the fibular head, but the stated proximal extent differs: superior two-thirds versus superior one-half. No source or reviewer in this task resolves it."),
    ("HA-M-000005", "insertion"): ("wording_difference", "Both name metatarsal I base and medial cuneiform; StatPearls adds surface direction detail."),
    ("HA-M-000006", "origin"): ("wording_difference", "Both state inferior two-thirds of the fibula; StatPearls specifies the lateral surface."),
    ("HA-M-000006", "insertion"): ("wording_difference", "Both place insertion at the base region of metatarsal V; the terms lateral base and styloid process are retained as source wording."),
}

manifest = {
    "schemaVersion": "1.0.0",
    "manifestId": "T18-CALF-ORIGIN-INSERTION-2026-09-27",
    "fixtureOnly": False,
    "subjects": [
        {"id": concept_id, "kind": "individual_muscle", "recordType": "canonical", "fields": ["origin", "insertion"]}
        for concept_id in ids
    ],
    "sources": sources,
    "accesses": [],
    "extractions": [],
    "comparisons": [],
}

extraction_ids: dict[tuple[str, str, str], str] = {}
for subject_id, fields in observed.items():
    for field, (temple_value, statpearls_value, temple_locator, statpearls_locator) in fields.items():
        for source_id, prefix, value, locator, method in (
            (temple_id, "HOA", temple_value, temple_locator, "publisher_full_text"),
            (statpearls_id, "SP", statpearls_value, statpearls_locator, "repository_full_text"),
        ):
            access_id = f"A-{prefix}-{subject_id}-{field}"
            extraction_id = f"E-{prefix}-{subject_id}-{field}"
            manifest["accesses"].append({
                "id": access_id,
                "sourceId": source_id,
                "subjectId": subject_id,
                "field": field,
                "locator": locator,
                "accessedOn": access_date,
                "accessMethod": method,
                "textAccess": "full_text_opened",
                "accessOutcome": "opened",
                "note": f"Opened the named source page and inspected the field for {labels[subject_id]}.",
            })
            manifest["extractions"].append({
                "id": extraction_id,
                "subjectId": subject_id,
                "field": field,
                "accessId": access_id,
                "value": value,
                "valueHash": module.value_hash(value),
                "reference": {"sourceId": source_id, "accessId": access_id, "locator": locator},
                "note": "Compact structured source observation; source-specific level of detail is preserved; not a human-reviewed claim.",
            })
            extraction_ids[(subject_id, field, source_id)] = extraction_id
        classification, rationale = comparisons[(subject_id, field)]
        manifest["comparisons"].append({
            "id": f"C-{subject_id}-{field}",
            "subjectId": subject_id,
            "field": field,
            "leftExtractionId": extraction_ids[(subject_id, field, temple_id)],
            "rightExtractionId": extraction_ids[(subject_id, field, statpearls_id)],
            "classification": classification,
            "assessmentMode": "ai_candidate",
            "rationale": rationale,
        })

OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"manifest": str(OUT), "subjects": len(manifest["subjects"]), "accesses": len(manifest["accesses"]), "extractions": len(manifest["extractions"]), "comparisons": len(manifest["comparisons"])}, ensure_ascii=False, indent=2))
