#!/usr/bin/env python3
"""Validate the source-backed T42 bone-name overlay and its navigation coverage."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OVERLAY_PATH = ROOT / "atlas-data/terminology/bone-name-overlay-t42.json"
NAVIGATION_PATH = ROOT / "atlas-data/navigation/atlas-navigation.json"
FIELDS = ("koModern", "koTraditional", "english")
HAN_SCRIPT = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


def walk_strings(value: Any, path: str = "$") -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if isinstance(value, str):
        rows.append((path, value))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            rows.extend(walk_strings(item, f"{path}[{index}]"))
    elif isinstance(value, dict):
        for key, item in value.items():
            rows.extend(walk_strings(item, f"{path}.{key}"))
    return rows


def selectable_bone_ids(navigation: dict[str, Any]) -> set[str]:
    selectable = {
        binding.get("selection", {}).get("conceptId")
        for scene in navigation.get("sceneManifests", [])
        if scene.get("availability") != "unavailable"
        for binding in scene.get("selectableBindings", [])
        if binding.get("selection", {}).get("kind") == "bone"
    }
    mapped = {
        instance.get("structureId")
        for instance in navigation.get("structureInstances", [])
        if any(mapping.get("structureInstanceId") == instance.get("id") and mapping.get("meshIds")
               for mapping in navigation.get("structureMeshMappings", []))
    }
    return {item for item in selectable if isinstance(item, str) and item in mapped}


def validate(overlay: dict[str, Any], navigation: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    sources = overlay.get("sources")
    entries = overlay.get("entries")
    if overlay.get("schemaVersion") != "T42-bone-name-overlay-v1":
        errors.append("unsupported schemaVersion")
    if not isinstance(sources, list) or not isinstance(entries, list):
        return errors + ["sources and entries must be arrays"]

    source_by_id: dict[str, dict[str, Any]] = {}
    for index, source in enumerate(sources):
        at = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{at} must be an object")
            continue
        source_id = source.get("id")
        if not isinstance(source_id, str) or source_id in source_by_id:
            errors.append(f"{at}.id must be a unique string")
            continue
        source_by_id[source_id] = source
        if not isinstance(source.get("url"), str) or not source["url"].startswith("https://"):
            errors.append(f"{at}.url must be HTTPS")
        if source.get("editionStatus") not in {"verified", "not_exposed"}:
            errors.append(f"{at}.editionStatus must distinguish verified from not exposed")
        if not isinstance(source.get("edition"), str) or not source["edition"].strip():
            errors.append(f"{at}.edition must be explicit, including 판본 미노출")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(source.get("accessedOn", ""))):
            errors.append(f"{at}.accessedOn must be YYYY-MM-DD")
        for required in ("title", "accessMethod", "textAccess"):
            if not isinstance(source.get(required), str) or not source[required].strip():
                errors.append(f"{at}.{required} is required")

    entry_ids: list[str] = []
    for index, entry in enumerate(entries):
        at = f"entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{at} must be an object")
            continue
        entry_id = entry.get("id")
        if not isinstance(entry_id, str):
            errors.append(f"{at}.id must be a string")
            continue
        entry_ids.append(entry_id)
        if entry.get("humanAnatomyReview") != "not_reviewed":
            errors.append(f"{at} cannot promote human anatomy review")
        if not all(isinstance(entry.get(field), str) and entry[field].strip() for field in ("displayTitle", *FIELDS)):
            errors.append(f"{at} needs all three display names")
        if entry.get("displayTitle") != entry.get("koTraditional"):
            errors.append(f"{at}.displayTitle must be the Hangul Sino-Korean name")
        evidence = entry.get("fieldEvidence")
        if not isinstance(evidence, dict):
            errors.append(f"{at}.fieldEvidence is required")
            evidence = {}
        for field in FIELDS:
            rows = evidence.get(field)
            if not isinstance(rows, list) or not rows:
                errors.append(f"{at}.fieldEvidence.{field} needs source locator(s)")
                continue
            for ev_index, ev in enumerate(rows):
                ev_at = f"{at}.fieldEvidence.{field}[{ev_index}]"
                if not isinstance(ev, dict) or ev.get("sourceId") not in source_by_id:
                    errors.append(f"{ev_at} references an unknown source")
                    continue
                if not isinstance(ev.get("locator"), str) or not ev["locator"].strip():
                    errors.append(f"{ev_at}.locator is required")
        aliases = entry.get("aliases")
        if not isinstance(aliases, list) or not aliases:
            errors.append(f"{at}.aliases must be a nonempty list")
        else:
            for alias_index, alias in enumerate(aliases):
                alias_at = f"{at}.aliases[{alias_index}]"
                if not isinstance(alias, dict) or not isinstance(alias.get("text"), str) or not alias["text"].strip():
                    errors.append(f"{alias_at}.text is required")
                    continue
                refs = alias.get("sourceIds")
                if not isinstance(refs, list) or not refs or any(ref not in source_by_id for ref in refs):
                    errors.append(f"{alias_at}.sourceIds must reference known sources")
                if not isinstance(alias.get("locator"), str) or not alias["locator"].strip():
                    errors.append(f"{alias_at}.locator is required")

    if len(entry_ids) != len(set(entry_ids)):
        errors.append("entry IDs must be unique")
    expected = selectable_bone_ids(navigation)
    actual = set(entry_ids)
    if actual != expected:
        errors.append(f"overlay/navigation mismatch: missing={sorted(expected - actual)}, extra={sorted(actual - expected)}")

    for path, value in walk_strings(overlay):
        if HAN_SCRIPT.search(value):
            errors.append(f"actual Hanja character is not allowed in this overlay: {path}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate and print a concise summary")
    args = parser.parse_args()
    del args
    overlay = json.loads(OVERLAY_PATH.read_text(encoding="utf-8"))
    navigation = json.loads(NAVIGATION_PATH.read_text(encoding="utf-8"))
    errors = validate(overlay, navigation)
    if errors:
        print(json.dumps({"status": "failed", "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({
        "status": "passed",
        "entryCount": len(overlay["entries"]),
        "selectableBoneCount": len(selectable_bone_ids(navigation)),
        "sourceCount": len(overlay["sources"]),
        "humanAnatomyReview": "not_reviewed",
        "actualHanjaCollected": False,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
