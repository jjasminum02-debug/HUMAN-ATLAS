#!/usr/bin/env python3
"""Koreanize Han-character glosses in the private T81 workbook without importing claims."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
HAN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
HANGUL = re.compile(r"[\uac00-\ud7af]")
NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
TERM_KOREAN = {
    "擧上": "들어올림",
    "後引": "뒤로 당김",
    "前引": "앞으로 당김",
    "閉鎖": "닫힘",
    "下降": "내림",
    "狹窄": "좁아짐",
    "擴張": "넓어짐",
    "壓迫": "눌림",
    "外轉": "바깥쪽 움직임",
    "內轉": "안쪽 움직임",
    "上轉": "위쪽 움직임",
    "內回旋": "안쪽 회선",
    "下轉": "아래쪽 움직임",
    "外回旋": "바깥쪽 회선",
    "後退": "뒤로 물러남",
    "回內": "회내",
    "回外": "회외",
    "對立": "맞섬",
    "背屈": "등쪽굽힘",
    "內翻": "안쪽번짐",
    "外翻": "가쪽번짐",
    "跖屈": "발바닥굽힘",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_sheet_rows(path: Path):
    with zipfile.ZipFile(path) as workbook:
        workbook_xml = ET.fromstring(workbook.read("xl/workbook.xml"))
        relationships = ET.fromstring(workbook.read("xl/_rels/workbook.xml.rels"))
        relation_map = {row.attrib["Id"]: row.attrib["Target"] for row in relationships}
        shared_strings = []
        if "xl/sharedStrings.xml" in workbook.namelist():
            strings_xml = ET.fromstring(workbook.read("xl/sharedStrings.xml"))
            shared_strings = ["".join(item.text or "" for item in node.findall(".//a:t", NS)) for node in strings_xml.findall("a:si", NS)]
        sheet = workbook_xml.find("a:sheets/a:sheet", NS)
        if sheet is None:
            raise ValueError("Workbook has no first sheet")
        target = relation_map[sheet.attrib[f"{{{NS['r']}}}id"]]
        sheet_path = target.lstrip("/") if target.startswith("/") else f"xl/{target}"
        sheet_path = str(Path(sheet_path))
        xml = ET.fromstring(workbook.read(sheet_path))
        rows = {}
        for row in xml.findall(".//a:sheetData/a:row", NS):
            cells = {}
            for cell in row.findall("a:c", NS):
                column = re.match(r"[A-Z]+", cell.attrib["r"]).group()
                value = cell.find("a:v", NS)
                text = value.text if value is not None and value.text else ""
                if cell.attrib.get("t") == "s" and text:
                    text = shared_strings[int(text)]
                if cell.attrib.get("t") == "inlineStr":
                    text = "".join(part.text or "" for part in cell.findall(".//a:t", NS))
                cells[column] = text
            rows[int(row.attrib["r"])] = cells
        return rows


def normalize_cell(text: str) -> tuple[str, list[str]]:
    terms = []

    def replace(match: re.Match[str]) -> str:
        gloss = match.group(1)
        if not HAN.search(gloss):
            return match.group(0)
        if gloss not in TERM_KOREAN:
            raise ValueError(f"Unmapped Hanja gloss in row: {gloss!r}")
        terms.append(gloss)
        return f"({TERM_KOREAN[gloss]})"

    normalized = re.sub(r"\(([^()]*)\)", replace, text)
    if HAN.search(normalized):
        raise ValueError("Hanja remains outside a translated parenthetical gloss")
    if text and not HANGUL.search(text):
        raise ValueError("Action cell does not contain Hangul to preserve")
    return normalized, terms


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="private-sources/t81/muscle-attachment-notes.xlsx")
    parser.add_argument("--output", default="private-sources/t83/action-normalization-candidates.json")
    parser.add_argument("--audit", default="work/evidence/T83/workbook-action-normalization-audit.json")
    args = parser.parse_args()

    source_path = ROOT / args.input
    disposition_path = ROOT / "work/evidence/T81/workbook-row-dispositions.json"
    if not source_path.is_file():
        raise SystemExit(f"Private workbook is unavailable: {args.input}")
    source_bytes = source_path.read_bytes()
    source_hash = sha(source_bytes)
    dispositions = json.loads(disposition_path.read_text(encoding="utf-8"))
    expected_source_hash = dispositions["source"]["sha256"]
    if source_hash != expected_source_hash:
        raise SystemExit("Private workbook hash differs from the frozen T81 source")
    disposition_by_row = {row["row"]: row for row in dispositions["rows"]}
    rows = load_sheet_rows(source_path)
    candidates = []
    audit_rows = []
    term_counts = {}
    for row_number, cells in sorted(rows.items()):
        action = cells.get("H", "")
        if not HAN.search(action):
            continue
        disposition = disposition_by_row.get(row_number)
        if not disposition:
            raise SystemExit(f"Workbook row {row_number} is absent from the frozen T81 disposition ledger")
        normalized, terms = normalize_cell(action)
        row_record = {
            "sheet": disposition["sheet"],
            "row": row_number,
            "sourceRowSha256": disposition["rowSha256"],
            "originalCellSha256": sha(action.encode("utf-8")),
            "normalizedCellSha256": sha(normalized.encode("utf-8")),
            "normalizedText": normalized,
            "normalizationTerms": terms,
            "candidateSupportedConceptKeys": disposition["candidateSupportedConceptKeys"],
            "sourceDisposition": disposition["disposition"],
            "learnerClaimEligible": False,
            "claimAdoption": "not_adopted_no_row_level_source_citation",
        }
        candidates.append(row_record)
        audit_rows.append({key: value for key, value in row_record.items() if key != "normalizedText"})
        for term in terms:
            term_counts[term] = term_counts.get(term, 0) + 1

    supported_hanja = [row for row in candidates if row["sourceDisposition"] == "exact_english_and_region_candidate_only_unverified"]
    if len(candidates) != 53 or len(supported_hanja) != 10:
        raise SystemExit(f"Frozen workbook count drift: Hanja cells={len(candidates)}, supported candidates={len(supported_hanja)}")
    if any(HAN.search(row["normalizedText"]) for row in candidates):
        raise SystemExit("Hanja remains in normalized candidate text")

    private_result = {
        "schemaVersion": "t83-private-workbook-action-candidates-v1",
        "source": {"path": args.input, "sha256": source_hash, "bytes": len(source_bytes), "sheet": dispositions["sheet"]},
        "candidateOnly": True,
        "rows": candidates,
    }
    audit = {
        "schemaVersion": "t83-workbook-action-normalization-audit-v1",
        "input": {
            "privateWorkbookSha256": source_hash,
            "t81RowDispositionPath": "work/evidence/T81/workbook-row-dispositions.json",
            "t81RowDispositionSha256": sha(disposition_path.read_bytes()),
            "rawWorkbookTrackedOrCopied": False,
        },
        "counts": {
            "workbookRows": dispositions["rowsProcessed"],
            "actionCellsWithHanja": len(candidates),
            "normalizedToHangul": sum(not HAN.search(row["normalizedText"]) for row in candidates),
            "exactSupportedConceptCandidatesStillUnverified": len(supported_hanja),
            "candidateRowsOutsideExactSupportedSet": len(candidates) - len(supported_hanja),
            "learnerClaimsAdopted": 0,
            "candidateCellsAddedToLearnerRuntime": 0,
        },
        "termReplacements": [{"sourceHanja": key, "koreanGloss": value, "occurrences": term_counts.get(key, 0)} for key, value in TERM_KOREAN.items() if term_counts.get(key, 0)],
        "policy": {
            "meaningAndPunctuationOutsideHanjaParentheticalsPreserved": True,
            "candidateTranslationsRemainPrivate": True,
            "noDirectRowSourceCitation": True,
            "noIndependentAnatomyVerification": True,
            "noLearnerClaimAdoption": True,
            "faceEyeTongueSphincterActionsMappedToJointRotation": False,
        },
        "rows": audit_rows,
        "privateDerivativePath": args.output,
    }
    output_path = ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(private_result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit_path = ROOT / args.audit
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", **audit["counts"], "privateDerivative": args.output, "audit": args.audit}, ensure_ascii=False))


if __name__ == "__main__":
    main()
