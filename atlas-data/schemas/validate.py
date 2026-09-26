#!/usr/bin/env python3
"""Dependency-free Draft 2020-12 keyword subset + HUMAN ATLAS domain validator."""
from __future__ import annotations
import argparse
import copy
import datetime as dt
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "atlas-data/schemas/atlas.schema.json"
FIXTURE_INDEX = ROOT / "work/evidence/T03/fixtures/index.json"
T02_ATLAS_FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR"
SCHEMA_DRAFT = "https://json-schema.org/draft/2020-12/schema"

SUPPORTED = {
    "$schema", "$id", "title", "description", "$defs", "$ref", "type", "enum", "const",
    "required", "properties", "additionalProperties", "items", "minItems", "maxItems",
    "uniqueItems", "minLength", "maxLength", "pattern", "format", "minimum", "maximum",
    "allOf", "anyOf", "oneOf", "not", "if", "then", "else"
}
COLLECTIONS = {
    "regions": "Region", "muscleConcepts": "MuscleConcept", "instances": "AnatomicalInstance",
    "muscleParts": "MusclePart", "terms": "Term", "structures": "Structure",
    "attachments": "Attachment", "spatialAnnotations": "SpatialAnnotation", "meshAssets": "MeshAsset",
    "meshMappings": "MeshMapping", "jointActions": "JointAction", "innervations": "Innervation",
    "assessments": "Assessment", "sources": "Source", "evidence": "Evidence", "claims": "Claim",
    "reviews": "Review", "modelElements": "ModelElement"
}
REVIEWABLE_COLLECTIONS = ("terms", "spatialAnnotations", "meshMappings", "jointActions", "innervations", "assessments", "claims")


class Issue(dict):
    def __init__(self, code: str, path: str, message: str):
        super().__init__(code=code, path=path, message=message)


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def same_json(a: Any, b: Any) -> bool:
    # Python considers True == 1; JSON Schema does not.
    if type(a) is not type(b):
        if isinstance(a, (int, float)) and not isinstance(a, bool) and isinstance(b, (int, float)) and not isinstance(b, bool):
            return a == b
        return False
    if isinstance(a, list):
        return len(a) == len(b) and all(same_json(x, y) for x, y in zip(a, b))
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(same_json(a[k], b[k]) for k in a)
    return a == b


def resolve_pointer(root_schema: dict, ref: str):
    if ref == "#":
        return root_schema
    if not ref.startswith("#/"):
        raise ValueError(f"Only local JSON Pointer refs are supported, got {ref!r}")
    node: Any = root_schema
    for token in ref[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or token not in node:
            raise ValueError(f"Unresolved schema ref: {ref}")
        node = node[token]
    return node


def check_schema(schema: dict) -> list[Issue]:
    problems: list[Issue] = []
    if schema.get("$schema") != SCHEMA_DRAFT:
        problems.append(Issue("schema_draft_mismatch", "$.$schema", "Schema must declare Draft 2020-12."))

    def visit(sub: Any, path: str):
        if isinstance(sub, bool):
            return
        if not isinstance(sub, dict):
            problems.append(Issue("invalid_schema_node", path, "Schema node must be an object or boolean."))
            return
        for key, value in sub.items():
            if key not in SUPPORTED:
                problems.append(Issue("unsupported_schema_keyword", f"{path}.{key}", f"Validator does not implement keyword {key!r}."))
                continue
            if key == "$ref":
                try:
                    resolve_pointer(schema, value)
                except Exception as exc:
                    problems.append(Issue("unresolved_schema_ref", f"{path}.$ref", str(exc)))
            elif key == "$defs":
                if not isinstance(value, dict):
                    problems.append(Issue("invalid_schema_defs", f"{path}.$defs", "$defs must be an object."))
                else:
                    for name, child in value.items():
                        visit(child, f"{path}.$defs.{name}")
            elif key == "properties":
                if not isinstance(value, dict):
                    problems.append(Issue("invalid_schema_properties", f"{path}.properties", "properties must be an object."))
                else:
                    for name, child in value.items():
                        visit(child, f"{path}.properties.{name}")
            elif key in ("items", "additionalProperties", "not", "if", "then", "else"):
                if isinstance(value, (dict, bool)):
                    visit(value, f"{path}.{key}")
                else:
                    problems.append(Issue("invalid_schema_keyword_value", f"{path}.{key}", f"{key} must contain a schema."))
            elif key in ("allOf", "anyOf", "oneOf"):
                if not isinstance(value, list) or not value:
                    problems.append(Issue("invalid_schema_composition", f"{path}.{key}", f"{key} must be a nonempty schema array."))
                else:
                    for i, child in enumerate(value):
                        visit(child, f"{path}.{key}[{i}]")
            elif key == "pattern":
                try:
                    re.compile(value)
                except Exception as exc:
                    problems.append(Issue("invalid_schema_pattern", f"{path}.pattern", str(exc)))
            elif key == "format" and value not in ("date", "date-time"):
                problems.append(Issue("unsupported_schema_format", f"{path}.format", f"Validator does not implement format {value!r}."))
            elif key == "required" and (not isinstance(value, list) or any(not isinstance(name, str) for name in value) or len(value) != len(set(value))):
                problems.append(Issue("invalid_schema_required", f"{path}.required", "required must be an array of unique strings."))
            elif key == "enum" and (not isinstance(value, list) or not value):
                problems.append(Issue("invalid_schema_enum", f"{path}.enum", "enum must be a nonempty array."))
            elif key == "type":
                allowed = {"object", "array", "string", "integer", "number", "boolean", "null"}
                values = value if isinstance(value, list) else [value]
                if not values or any(t not in allowed for t in values):
                    problems.append(Issue("invalid_schema_type", f"{path}.type", f"Unsupported type declaration {value!r}."))
    visit(schema, "$")
    return problems


def type_matches(value: Any, expected: str) -> bool:
    if expected == "object": return isinstance(value, dict)
    if expected == "array": return isinstance(value, list)
    if expected == "string": return isinstance(value, str)
    if expected == "boolean": return isinstance(value, bool)
    if expected == "null": return value is None
    if expected == "integer": return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number": return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    return False


def check_format(value: str, format_name: str) -> bool:
    try:
        if format_name == "date":
            dt.date.fromisoformat(value)
            return True
        if format_name == "date-time":
            parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.tzinfo is not None and parsed.utcoffset() is not None
    except (TypeError, ValueError):
        return False
    return False


def schema_issues(schema: dict, instance: Any) -> list[Issue]:
    issues: list[Issue] = []

    def walk(rule: Any, value: Any, path: str):
        if rule is True: return
        if rule is False:
            issues.append(Issue("schema_false", path, "Value is rejected by a false schema.")); return
        if not isinstance(rule, dict):
            issues.append(Issue("invalid_schema_node", path, "Schema node is not an object or boolean.")); return
        if "$ref" in rule:
            try:
                walk(resolve_pointer(schema, rule["$ref"]), value, path)
            except Exception as exc:
                issues.append(Issue("unresolved_schema_ref", path, str(exc)))
        if "type" in rule:
            expected = rule["type"] if isinstance(rule["type"], list) else [rule["type"]]
            if not any(type_matches(value, t) for t in expected):
                issues.append(Issue("schema_type", path, f"Expected {expected}, got {type(value).__name__}.")); return
        if "const" in rule and not same_json(value, rule["const"]):
            issues.append(Issue("schema_const", path, f"Value must equal {rule['const']!r}."))
        if "enum" in rule and not any(same_json(value, option) for option in rule["enum"]):
            issues.append(Issue("schema_enum", path, "Value is outside the allowed enumeration."))
        if "allOf" in rule:
            for sub in rule["allOf"]: walk(sub, value, path)
        if "anyOf" in rule:
            outcomes = [walk_collect(sub, value, path) for sub in rule["anyOf"]]
            if not any(not outcome for outcome in outcomes):
                issues.append(Issue("schema_anyOf", path, "Value must match at least one alternative."))
        if "oneOf" in rule:
            outcomes = [walk_collect(sub, value, path) for sub in rule["oneOf"]]
            matched = sum(not outcome for outcome in outcomes)
            if matched != 1:
                issues.append(Issue("schema_oneOf", path, f"Value matched {matched} alternatives; exactly one is required."))
        if "not" in rule and not walk_collect(rule["not"], value, path):
            issues.append(Issue("schema_not", path, "Value matches a forbidden schema."))
        if "if" in rule:
            branch = "then" if not walk_collect(rule["if"], value, path) else "else"
            if branch in rule: walk(rule[branch], value, path)
        if isinstance(value, dict):
            for key in rule.get("required", []):
                if key not in value:
                    issues.append(Issue("schema_required", f"{path}.{key}", f"Required property {key!r} is missing."))
            properties = rule.get("properties", {})
            for key, sub in properties.items():
                if key in value: walk(sub, value[key], f"{path}.{key}")
            extra = set(value) - set(properties)
            additional = rule.get("additionalProperties", True)
            if additional is False:
                for key in sorted(extra): issues.append(Issue("schema_additional_property", f"{path}.{key}", "Unexpected property."))
            elif isinstance(additional, dict):
                for key in sorted(extra): walk(additional, value[key], f"{path}.{key}")
        if isinstance(value, list):
            if "minItems" in rule and len(value) < rule["minItems"]: issues.append(Issue("schema_minItems", path, "Array is shorter than minItems."))
            if "maxItems" in rule and len(value) > rule["maxItems"]: issues.append(Issue("schema_maxItems", path, "Array is longer than maxItems."))
            if rule.get("uniqueItems"):
                encoded = [canonical(item) for item in value]
                if len(encoded) != len(set(encoded)): issues.append(Issue("schema_uniqueItems", path, "Array items must be unique."))
            if "items" in rule:
                for i, item in enumerate(value): walk(rule["items"], item, f"{path}[{i}]")
        if isinstance(value, str):
            if "minLength" in rule and len(value) < rule["minLength"]: issues.append(Issue("schema_minLength", path, "String is shorter than minLength."))
            if "maxLength" in rule and len(value) > rule["maxLength"]: issues.append(Issue("schema_maxLength", path, "String is longer than maxLength."))
            if "pattern" in rule and re.search(rule["pattern"], value) is None: issues.append(Issue("schema_pattern", path, "String does not match the required pattern."))
            if "format" in rule and not check_format(value, rule["format"]): issues.append(Issue("schema_format", path, f"Invalid {rule['format']} value."))
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if "minimum" in rule and value < rule["minimum"]: issues.append(Issue("schema_minimum", path, "Number is below minimum."))
            if "maximum" in rule and value > rule["maximum"]: issues.append(Issue("schema_maximum", path, "Number is above maximum."))

    def walk_collect(rule: Any, value: Any, path: str) -> list[Issue]:
        before = len(issues)
        walk(rule, value, path)
        found = issues[before:]
        del issues[before:]
        return found

    walk(schema, instance, "$dataset")
    return issues


def revision_hash(entity: dict) -> str:
    payload = {key: value for key, value in entity.items() if key != "reviewState"}
    return hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()


def determinant3(matrix: list[list[float]]) -> float:
    a, b, c = matrix
    return (a[0] * (b[1] * c[2] - b[2] * c[1])
            - a[1] * (b[0] * c[2] - b[2] * c[0])
            + a[2] * (b[0] * c[1] - b[1] * c[0]))


def validate_dataset(data: Any, schema: dict) -> list[Issue]:
    issues = schema_issues(schema, data)
    if issues:
        return issues
    entities = data["entities"]
    records: dict[str, dict] = {}
    buckets: dict[str, dict[str, dict]] = {}
    for collection, _ in COLLECTIONS.items():
        buckets[collection] = {item["id"]: item for item in entities[collection]}
        for i, item in enumerate(entities[collection]):
            entity_id = item["id"]
            if entity_id in records:
                issues.append(Issue("duplicate_id", f"$.entities.{collection}[{i}].id", f"ID {entity_id!r} already exists in the dataset."))
            else:
                records[entity_id] = item
    for i, manifest in enumerate(data["publicationManifests"]):
        if manifest["id"] in records:
            issues.append(Issue("duplicate_id", f"$.publicationManifests[{i}].id", f"ID {manifest['id']!r} already exists in the dataset."))
        else:
            records[manifest["id"]] = manifest

    def ref(ok: bool, code: str, path: str, target: str):
        if not ok: issues.append(Issue(code, path, f"Referenced ID {target!r} does not resolve."))
    def exists(collection: str, ident: str | None) -> bool:
        return ident is not None and ident in buckets[collection]
    def cycle_check(collection: str, path_name: str):
        index = buckets[collection]
        for start in index:
            seen: set[str] = set(); current = start
            while current in index and index[current].get("parentId") is not None:
                if current in seen:
                    issues.append(Issue("parent_cycle", f"$.entities.{collection}[{start}].parentId", "Parent hierarchy contains a cycle.")); break
                seen.add(current); current = index[current]["parentId"]
                if current not in index: break
    source_by_id = buckets["sources"]
    license_index: dict[str, tuple[str, dict]] = {}
    for source in entities["sources"]:
        lic = source["license"]
        if lic["id"] in license_index:
            issues.append(Issue("duplicate_license_id", "$.entities.sources", f"License ID {lic['id']!r} is not unique."))
        else: license_index[lic["id"]] = (source["id"], lic)
        if lic["attributionRequired"] and not (lic["attributionText"] and lic["attributionText"].strip()):
            issues.append(Issue("license_attribution_missing", f"$.entities.sources[{source['id']}].license.attributionText", "A license requiring attribution must provide the exact attribution text."))
    concept_bearing = set(buckets["muscleConcepts"]) | set(buckets["structures"])
    muscle_or_part = set(buckets["muscleConcepts"]) | set(buckets["muscleParts"])
    claimable = set(records) - set(buckets["reviews"]) - {m["id"] for m in data["publicationManifests"]}

    # Hierarchies and basic entity relationships.
    cycle_check("regions", "regions"); cycle_check("muscleConcepts", "muscleConcepts"); cycle_check("structures", "structures")
    for region in entities["regions"]:
        if region.get("parentId") is not None: ref(exists("regions", region["parentId"]), "missing_reference", f"$.regions.{region['id']}.parentId", region["parentId"])
    for concept in entities["muscleConcepts"]:
        path = f"$.muscleConcepts.{concept['id']}"
        for rid in concept["regionIds"]: ref(exists("regions", rid), "missing_reference", f"{path}.regionIds", rid)
        parent = concept.get("parentId")
        if parent is not None: ref(exists("muscleConcepts", parent), "missing_reference", f"{path}.parentId", parent)
    for inst in entities["instances"]:
        path = f"$.instances.{inst['id']}"
        ref(exists("muscleConcepts", inst["conceptId"]), "missing_reference", f"{path}.conceptId", inst["conceptId"])
        variant = inst.get("variantId")
        if variant is not None:
            ref(exists("muscleConcepts", variant), "missing_reference", f"{path}.variantId", variant)
            if exists("muscleConcepts", variant) and buckets["muscleConcepts"][variant]["entityType"] != "variant":
                issues.append(Issue("instance_variant_type_mismatch", f"{path}.variantId", "variantId must reference a variant concept."))
    for part in entities["muscleParts"]:
        path = f"$.muscleParts.{part['id']}"; parent = part["parentMuscleId"]
        ref(exists("muscleConcepts", parent), "missing_reference", f"{path}.parentMuscleId", parent)
        if exists("muscleConcepts", parent) and buckets["muscleConcepts"][parent]["entityType"] not in ("individual_muscle", "muscle_group"):
            issues.append(Issue("muscle_part_parent_type", f"{path}.parentMuscleId", "A MusclePart parent must be an individual muscle or group."))
        for term_id in part["termIds"]: ref(exists("terms", term_id), "missing_reference", f"{path}.termIds", term_id)
    for term in entities["terms"]:
        path = f"$.terms.{term['id']}"; owner = term["conceptId"]
        ref(owner in concept_bearing, "missing_reference", f"{path}.conceptId", owner)
        for evidence_id in term["evidenceIds"]: ref(exists("evidence", evidence_id), "missing_reference", f"{path}.evidenceIds", evidence_id)
        if term["text"] is None and term["reviewState"] == "reviewed":
            issues.append(Issue("missing_term_marked_reviewed", f"{path}.reviewState", "A missing term cannot be reviewed."))
        if term["script"] == "Hani" and term["text"] is not None and term["reviewState"] != "reviewed":
            issues.append(Issue("unreviewed_hani_term_filled", f"{path}.text", "A filled Hani term requires evidence and current human review; do not auto-translate a missing term."))
        if term["reviewState"] == "reviewed" and (not term.get("edition") or not term["edition"].strip()):
            issues.append(Issue("reviewed_term_edition_missing", f"{path}.edition", "A reviewed term requires the exact source edition."))
    for structure in entities["structures"]:
        path = f"$.structures.{structure['id']}"; parent = structure.get("parentId")
        if parent is not None: ref(exists("structures", parent), "missing_reference", f"{path}.parentId", parent)
        for term_id in structure["termIds"]: ref(exists("terms", term_id), "missing_reference", f"{path}.termIds", term_id)
    for attachment in entities["attachments"]:
        path = f"$.attachments.{attachment['id']}"
        ref(attachment["muscleOrPartId"] in muscle_or_part, "missing_reference", f"{path}.muscleOrPartId", attachment["muscleOrPartId"])
        ref(exists("structures", attachment["targetStructureId"]), "missing_reference", f"{path}.targetStructureId", attachment["targetStructureId"])
        landmark = attachment.get("landmarkId")
        if landmark is not None:
            ref(exists("structures", landmark), "missing_reference", f"{path}.landmarkId", landmark)
            if exists("structures", landmark) and buckets["structures"][landmark]["kind"] != "landmark":
                issues.append(Issue("attachment_landmark_kind_mismatch", f"{path}.landmarkId", "landmarkId must reference a Structure of kind landmark."))
        ref(exists("claims", attachment["descriptionClaimId"]), "missing_reference", f"{path}.descriptionClaimId", attachment["descriptionClaimId"])
        if exists("claims", attachment["descriptionClaimId"]) and buckets["claims"][attachment["descriptionClaimId"]]["subjectId"] != attachment["id"]:
            issues.append(Issue("attachment_claim_subject_mismatch", f"{path}.descriptionClaimId", "Description claim subjectId must be this attachment ID."))

    # Sources, evidence, claims, and reciprocal provenance links.
    for source in entities["sources"]:
        # license index is built above; no license permission is inferred from a URI alone.
        pass
    for evidence in entities["evidence"]:
        path = f"$.evidence.{evidence['id']}"
        ref(exists("sources", evidence["sourceId"]), "missing_reference", f"{path}.sourceId", evidence["sourceId"])
        for cid in evidence["supportedClaimIds"]: ref(exists("claims", cid), "missing_reference", f"{path}.supportedClaimIds", cid)
    for claim in entities["claims"]:
        path = f"$.claims.{claim['id']}"
        ref(claim["subjectId"] in claimable, "missing_reference", f"{path}.subjectId", claim["subjectId"])
        for eid in claim["evidenceIds"]:
            ref(exists("evidence", eid), "missing_reference", f"{path}.evidenceIds", eid)
            if exists("evidence", eid) and claim["id"] not in buckets["evidence"][eid]["supportedClaimIds"]:
                issues.append(Issue("evidence_claim_link_not_reciprocal", f"{path}.evidenceIds", f"Evidence {eid!r} must list the claim in supportedClaimIds."))

    # Mesh, mapping sidedness, frame/units, revision freshness, and landmark scale sentinels.
    for asset in entities["meshAssets"]:
        path = f"$.meshAssets.{asset['id']}"
        ref(exists("sources", asset["sourceId"]), "missing_reference", f"{path}.sourceId", asset["sourceId"])
        ref(asset["licenseId"] in license_index, "missing_license", f"{path}.licenseId", asset["licenseId"])
        if asset["licenseId"] in license_index and license_index[asset["licenseId"]][0] != asset["sourceId"]:
            issues.append(Issue("mesh_license_source_mismatch", f"{path}.licenseId", "Mesh license terms must belong to the same source as the mesh asset."))
        axes = asset["axes"]
        if len({axes["positiveX"], axes["positiveY"], axes["positiveZ"]}) < 3 and "unknown" not in (axes["positiveX"], axes["positiveY"], axes["positiveZ"]):
            issues.append(Issue("coordinate_axes_not_independent", f"{path}.axes", "Positive X/Y/Z must identify three distinct anatomical directions."))
        if axes["frameId"] == T02_ATLAS_FRAME:
            expected = ("patient_left", "head", "anterior", "right")
            actual = (axes["positiveX"], axes["positiveY"], axes["positiveZ"], axes["handedness"])
            if actual != expected or asset["units"] != "m":
                issues.append(Issue("t02_coordinate_contract_mismatch", f"{path}.axes", "Atlas world v1 must be RH, +X patient-left, +Y head, +Z anterior, in meters."))
    for mapping in entities["meshMappings"]:
        path = f"$.meshMappings.{mapping['id']}"
        for iid in mapping["instanceIds"]: ref(exists("instances", iid), "missing_reference", f"{path}.instanceIds", iid)
        for pid in mapping["partIds"]:
            part_concept = buckets["muscleConcepts"].get(pid)
            valid_part_concept = part_concept is not None and part_concept["entityType"] == "muscle_part"
            ref(exists("muscleParts", pid) or valid_part_concept, "missing_reference", f"{path}.partIds", pid)
            if valid_part_concept and mapping["instanceIds"]:
                parent = part_concept.get("parentId")
                for iid in mapping["instanceIds"]:
                    if exists("instances", iid) and buckets["instances"][iid]["conceptId"] != parent:
                        issues.append(Issue("mesh_part_instance_parent_mismatch", f"{path}.partIds", f"Part concept {pid!r} does not belong to instance {iid!r}."))
        for mid in mapping["meshIds"]: ref(exists("meshAssets", mid), "missing_reference", f"{path}.meshIds", mid)
        for iid in mapping["instanceIds"]:
            if not exists("instances", iid): continue
            side = buckets["instances"][iid]["side"]
            for mid in mapping["meshIds"]:
                if not exists("meshAssets", mid): continue
                laterality = buckets["meshAssets"][mid]["laterality"]
                if laterality not in ("unknown", "bilateral") and laterality != side:
                    issues.append(Issue("mesh_laterality_mismatch", f"{path}.meshIds", f"Mesh {mid!r} is {laterality}, but instance {iid!r} is {side}."))
                if mapping["reviewState"] == "reviewed" and laterality == "unknown":
                    issues.append(Issue("reviewed_mapping_sidedness_unknown", f"{path}.reviewState", "A reviewed mapping requires known mesh laterality."))
    for ann in entities["spatialAnnotations"]:
        path = f"$.spatialAnnotations.{ann['id']}"
        ref(exists("attachments", ann["attachmentId"]), "missing_reference", f"{path}.attachmentId", ann["attachmentId"])
        ref(exists("instances", ann["instanceId"]), "missing_reference", f"{path}.instanceId", ann["instanceId"])
        ref(exists("meshAssets", ann["assetId"]), "missing_reference", f"{path}.assetId", ann["assetId"])
        for eid in ann["evidenceIds"]: ref(exists("evidence", eid), "missing_reference", f"{path}.evidenceIds", eid)
        if exists("attachments", ann["attachmentId"]) and exists("instances", ann["instanceId"]):
            attachment = buckets["attachments"][ann["attachmentId"]]
            owner = attachment["muscleOrPartId"]
            if exists("muscleParts", owner):
                expected_concept = buckets["muscleParts"][owner]["parentMuscleId"]
            elif owner in buckets["muscleConcepts"] and buckets["muscleConcepts"][owner]["entityType"] == "muscle_part":
                expected_concept = buckets["muscleConcepts"][owner].get("parentId")
            else:
                expected_concept = owner
            if buckets["instances"][ann["instanceId"]]["conceptId"] != expected_concept:
                issues.append(Issue("annotation_instance_concept_mismatch", f"{path}.instanceId", "Annotation instance must belong to the attachment's muscle concept."))
        if exists("meshAssets", ann["assetId"]):
            asset = buckets["meshAssets"][ann["assetId"]]
            mismatch = ann["assetRevision"] != asset["revision"] or ann["assetRevisionHash"] != asset["hash"]
            if mismatch and ann["reviewState"] != "stale":
                issues.append(Issue("stale_annotation_reviewed" if ann["reviewState"] == "reviewed" else "stale_annotation_not_marked", f"{path}.assetRevisionHash", "Annotation references an older mesh revision/hash; mark stale and remap before review/publication."))
            if not ann["transformChain"] and (ann["frameId"] != asset["axes"]["frameId"] or ann["units"] != asset["units"]):
                issues.append(Issue("annotation_frame_or_unit_mismatch", f"{path}.frameId", "Without a transform chain, annotation frame and units must match its referenced mesh asset."))
            if ann["poseId"] != asset["pose"]["id"]:
                issues.append(Issue("annotation_pose_mismatch", f"{path}.poseId", "Annotation pose must match the referenced mesh asset pose."))
            if ann["geometry"]["kind"] == "surface_patch":
                if not asset.get("topologyHash") or ann["geometry"]["topologyHash"] != asset.get("topologyHash"):
                    issues.append(Issue("annotation_topology_mismatch", f"{path}.geometry.topologyHash", "Surface patch topology hash must match the current mesh asset."))
            if exists("instances", ann["instanceId"]):
                side = buckets["instances"][ann["instanceId"]]["side"]
                laterality = asset["laterality"]
                if laterality not in ("unknown", "bilateral") and laterality != side:
                    issues.append(Issue("annotation_laterality_mismatch", f"{path}.assetId", "Annotation asset laterality does not match the selected instance."))
        chain = ann["transformChain"]
        if chain:
            expected_source = buckets["meshAssets"][ann["assetId"]]["axes"]["frameId"] if exists("meshAssets", ann["assetId"]) else None
            previous_target = None
            previous_units = None
            for idx, step in enumerate(chain):
                if idx == 0 and step["sourceFrameId"] != expected_source:
                    issues.append(Issue("transform_chain_start_mismatch", f"{path}.transformChain[{idx}]", "Transform chain must begin in the asset frame."))
                if idx == 0 and exists("meshAssets", ann["assetId"]) and step["sourceUnits"] != buckets["meshAssets"][ann["assetId"]]["units"]:
                    issues.append(Issue("transform_chain_source_unit_mismatch", f"{path}.transformChain[{idx}].sourceUnits", "Transform chain source units must match the asset units."))
                if previous_target is not None and step["sourceFrameId"] != previous_target:
                    issues.append(Issue("transform_chain_disconnected", f"{path}.transformChain[{idx}]", "Transform steps must join without gaps."))
                if previous_units is not None and step["sourceUnits"] != previous_units:
                    issues.append(Issue("transform_chain_unit_disconnected", f"{path}.transformChain[{idx}].sourceUnits", "Transform units must join without gaps."))
                if step.get("evidenceId") is not None:
                    ref(exists("evidence", step["evidenceId"]), "missing_reference", f"{path}.transformChain[{idx}].evidenceId", step["evidenceId"])
                computed_determinant = determinant3(step["rotationMatrix"])
                if not math.isclose(computed_determinant, step["rotationDeterminant"], rel_tol=0, abs_tol=1e-6):
                    issues.append(Issue("transform_determinant_mismatch", f"{path}.transformChain[{idx}].rotationDeterminant", "Declared determinant must match the recorded rotation matrix."))
                if step["targetFrameId"] == T02_ATLAS_FRAME:
                    expected_rotation = ((1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, -1.0, 0.0))
                    matrix_matches = all(math.isclose(float(step["rotationMatrix"][r][c]), expected_rotation[r][c], rel_tol=0, abs_tol=1e-9) for r in range(3) for c in range(3))
                    if not (step["sourceUnits"] == "mm" and step["targetUnits"] == "m" and math.isclose(step["scale"], 0.001, rel_tol=0, abs_tol=1e-12) and math.isclose(step["rotationDeterminant"], 1.0, rel_tol=0, abs_tol=1e-6) and matrix_matches):
                        issues.append(Issue("t02_transform_contract_mismatch", f"{path}.transformChain[{idx}]", "T02 BodyParts3D→Atlas requires [x,z,-y]/1000, source mm, target m, and determinant +1."))
                previous_target = step["targetFrameId"]
                previous_units = step["targetUnits"]
            if previous_target != ann["frameId"] or previous_units != ann["units"]:
                issues.append(Issue("transform_chain_end_mismatch", f"{path}.transformChain", "Transform chain must end at the annotation frame."))
        for idx, check in enumerate(ann["landmarkChecks"]):
            cpath = f"{path}.landmarkChecks[{idx}]"
            ref(exists("structures", check["landmarkId"]), "missing_reference", f"{cpath}.landmarkId", check["landmarkId"])
            ref(exists("evidence", check["evidenceId"]), "missing_reference", f"{cpath}.evidenceId", check["evidenceId"])
            if exists("structures", check["landmarkId"]) and buckets["structures"][check["landmarkId"]]["kind"] != "landmark":
                issues.append(Issue("landmark_check_kind_mismatch", f"{cpath}.landmarkId", "Landmark check must target a Structure of kind landmark."))
            error = math.sqrt(sum((a - b) ** 2 for a, b in zip(check["expectedAtlasPositionM"], check["observedAtlasPositionM"])))
            if error > check["toleranceM"]:
                issues.append(Issue("landmark_check_out_of_tolerance", cpath, f"Known-marker position error {error:.9g} m exceeds tolerance {check['toleranceM']:.9g} m."))
            if ann["geometry"]["kind"] == "point" and ann["geometry"]["position"] != check["observedAtlasPositionM"]:
                issues.append(Issue("landmark_check_observation_mismatch", f"{cpath}.observedAtlasPositionM", "For a point annotation, the recorded observation must equal the annotation coordinate."))

    # Functions, innervation, assessments, and model adapter records.
    for action in entities["jointActions"]:
        path = f"$.jointActions.{action['id']}"
        for mid in action["muscleOrPartIds"]: ref(mid in muscle_or_part, "missing_reference", f"{path}.muscleOrPartIds", mid)
        for jid in action["jointIds"]:
            ref(exists("structures", jid), "missing_reference", f"{path}.jointIds", jid)
            if exists("structures", jid) and buckets["structures"][jid]["kind"] != "joint": issues.append(Issue("action_target_not_joint", f"{path}.jointIds", f"Structure {jid!r} is not kind joint."))
        for eid in action["evidenceIds"]: ref(exists("evidence", eid), "missing_reference", f"{path}.evidenceIds", eid)
    for inn in entities["innervations"]:
        path = f"$.innervations.{inn['id']}"
        ref(inn["muscleOrPartId"] in muscle_or_part, "missing_reference", f"{path}.muscleOrPartId", inn["muscleOrPartId"])
        ref(exists("structures", inn["nerveStructureId"]), "missing_reference", f"{path}.nerveStructureId", inn["nerveStructureId"])
        if exists("structures", inn["nerveStructureId"]) and buckets["structures"][inn["nerveStructureId"]]["kind"] != "nerve": issues.append(Issue("innervation_target_not_nerve", f"{path}.nerveStructureId", "Nerve structure must have kind nerve."))
        for eid in inn["evidenceIds"]: ref(exists("evidence", eid), "missing_reference", f"{path}.evidenceIds", eid)
    for assessment in entities["assessments"]:
        path = f"$.assessments.{assessment['id']}"
        for fid in assessment["targetFunctionIds"]: ref(exists("jointActions", fid), "missing_reference", f"{path}.targetFunctionIds", fid)
        for mid in assessment["relatedMuscleIds"]: ref(mid in muscle_or_part, "missing_reference", f"{path}.relatedMuscleIds", mid)
        for eid in assessment["evidenceIds"]: ref(exists("evidence", eid), "missing_reference", f"{path}.evidenceIds", eid)
    for element in entities["modelElements"]:
        path = f"$.modelElements.{element['id']}"
        ref(exists("sources", element["sourceId"]), "missing_reference", f"{path}.sourceId", element["sourceId"])
        mapped = element["mappingStatus"] != "unmapped"
        target = element.get("muscleConceptId")
        if mapped and target is None: issues.append(Issue("model_mapping_target_missing", f"{path}.muscleConceptId", "verified/provisional model mappings require a muscle concept ID."))
        if not mapped and target is not None: issues.append(Issue("unmapped_model_element_has_target", f"{path}.muscleConceptId", "Unmapped model elements must not carry a muscle concept ID."))
        if target is not None: ref(exists("muscleConcepts", target), "missing_reference", f"{path}.muscleConceptId", target)

    # Reviews are revision-bound and never let AI or missing evidence produce reviewed status.
    reviewable: dict[str, dict] = {}
    for collection in REVIEWABLE_COLLECTIONS:
        for record in entities[collection]: reviewable[record["id"]] = record
    for review in entities["reviews"]:
        path = f"$.reviews.{review['id']}"; target_id = review["targetId"]
        ref(target_id in reviewable, "missing_review_target", f"{path}.targetId", target_id)
    for collection in REVIEWABLE_COLLECTIONS:
        for record in entities[collection]:
            if record["reviewState"] != "reviewed": continue
            path = f"$.{collection}.{record['id']}"
            evidence_ids = record.get("evidenceIds", [])
            if not evidence_ids:
                issues.append(Issue("reviewed_item_missing_evidence", f"{path}.evidenceIds", "Reviewed items require at least one evidence reference."))
            for eid in evidence_ids:
                if exists("evidence", eid):
                    ev = buckets["evidence"][eid]
                    if not ev["locator"].strip() or not exists("sources", ev["sourceId"]):
                        issues.append(Issue("reviewed_item_evidence_incomplete", f"{path}.evidenceIds", "Reviewed item evidence must resolve to a source and locator."))
            wanted_hash = revision_hash(record)
            current_human = any(r["targetId"] == record["id"] and r["targetRevisionHash"] == wanted_hash and r["reviewerKind"] == "human" and r["decision"] == "approved" and bool(r["reviewerId"].strip()) and bool(r["notes"].strip()) for r in entities["reviews"])
            if not current_human:
                issues.append(Issue("reviewed_item_without_current_human_approval", f"{path}.reviewState", "Reviewed state needs a current human approved Review record for this exact content hash."))

    # Learning manifests are explicit allow-lists; no automatic release is performed.
    pub_groups = {
        "includedClaimIds": "claims", "includedTermIds": "terms", "includedSpatialAnnotationIds": "spatialAnnotations",
        "includedMeshMappingIds": "meshMappings", "includedMeshAssetIds": "meshAssets", "includedJointActionIds": "jointActions",
        "includedInnervationIds": "innervations", "includedAssessmentIds": "assessments"
    }
    for manifest in data["publicationManifests"]:
        path = f"$.publicationManifests.{manifest['id']}"
        included: dict[str, list[dict]] = {}
        for prop, collection in pub_groups.items():
            included[prop] = []
            for ident in manifest[prop]:
                ref(exists(collection, ident), "missing_reference", f"{path}.{prop}", ident)
                if exists(collection, ident): included[prop].append(buckets[collection][ident])
        attrs: dict[str, str] = {}
        for attr in manifest["attributions"]:
            ref(exists("sources", attr["sourceId"]), "missing_reference", f"{path}.attributions", attr["sourceId"])
            if attr["sourceId"] in attrs: issues.append(Issue("duplicate_publication_attribution", f"{path}.attributions", f"Source {attr['sourceId']!r} appears more than once."))
            attrs[attr["sourceId"]] = attr["text"]
        if manifest["scope"] != "learning": continue
        used_source_ids: set[str] = set()
        for prop, records_included in included.items():
            for record in records_included:
                if prop != "includedMeshAssetIds" and record.get("reviewState") != "reviewed":
                    issues.append(Issue("publication_item_not_reviewed", f"{path}.{prop}", f"Learning item {record['id']!r} is not reviewed."))
                if prop == "includedTermIds" and record.get("text") is None:
                    issues.append(Issue("publication_term_missing", f"{path}.{prop}", f"Term {record['id']!r} has no text."))
                if prop == "includedSpatialAnnotationIds":
                    asset = buckets["meshAssets"].get(record["assetId"])
                    if asset and (record["assetRevision"] != asset["revision"] or record["assetRevisionHash"] != asset["hash"]):
                        issues.append(Issue("publication_stale_annotation", f"{path}.{prop}", f"Annotation {record['id']!r} references stale mesh content."))
                    if asset and asset["id"] not in manifest["includedMeshAssetIds"]:
                        issues.append(Issue("publication_annotation_asset_omitted", f"{path}.{prop}", f"Annotation {record['id']!r} requires its mesh asset in the manifest."))
                if prop == "includedMeshMappingIds":
                    for mid in record["meshIds"]:
                        if mid not in manifest["includedMeshAssetIds"]:
                            issues.append(Issue("publication_mapping_asset_omitted", f"{path}.{prop}", f"Mapping {record['id']!r} requires mesh asset {mid!r} in the manifest."))
                for eid in record.get("evidenceIds", []):
                    if exists("evidence", eid) and exists("sources", buckets["evidence"][eid]["sourceId"]):
                        used_source_ids.add(buckets["evidence"][eid]["sourceId"])
                if prop == "includedMeshAssetIds" and exists("meshAssets", record["id"]):
                    used_source_ids.add(record["sourceId"])
        for source_id in used_source_ids:
            if source_id not in source_by_id: continue
            source = source_by_id[source_id]; license_data = source["license"]
            if "learning" not in license_data["allowedUses"] and "public_learning" not in license_data["allowedUses"]:
                issues.append(Issue("publication_source_permission_missing", f"{path}.scope", f"Source {source_id!r} does not permit learning use."))
            if license_data["attributionRequired"]:
                required_text = license_data["attributionText"]
                if not required_text or attrs.get(source_id) != required_text:
                    issues.append(Issue("publication_attribution_missing_or_wrong", f"{path}.attributions", f"Source {source_id!r} requires its exact recorded attribution text."))

    return issues


def muscle_concept_count(data: dict) -> int:
    """Count individual concepts only; exclude side instances, parts, groups and model elements."""
    return sum(1 for row in data["entities"]["muscleConcepts"] if row["entityType"] == "individual_muscle")


def load_json(path: Path):
    with path.open(encoding="utf-8") as stream: return json.load(stream)


def validate_schema_file() -> tuple[dict | None, list[Issue]]:
    try:
        schema = load_json(SCHEMA_PATH)
    except Exception as exc:
        return None, [Issue("schema_load_error", str(SCHEMA_PATH), str(exc))]
    problems = check_schema(schema)
    return schema, problems


def run_fixtures(schema: dict) -> dict:
    index = load_json(FIXTURE_INDEX)
    results = []
    for entry in index["fixtures"]:
        fixture_path = ROOT / entry["path"]
        try:
            data = load_json(fixture_path)
            actual_issues = validate_dataset(data, schema)
            actual_valid = not actual_issues
            expected_valid = entry["expectedValid"]
            expected_codes = set(entry.get("expectedDiagnostics", []))
            actual_codes = {issue["code"] for issue in actual_issues}
            if expected_valid:
                passed = actual_valid
                detail = "Valid fixture passed." if passed else "Valid fixture produced unexpected diagnostics."
            else:
                passed = (not actual_valid) and expected_codes.issubset(actual_codes)
                detail = "Expected negative diagnostics observed." if passed else "Negative fixture did not fail for all expected diagnostics."
            results.append({"name": entry["name"], "expectedValid": expected_valid, "expectedDiagnostics": sorted(expected_codes), "actualValid": actual_valid, "actualDiagnostics": sorted(actual_codes), "passed": passed, "detail": detail})
        except Exception as exc:
            results.append({"name": entry["name"], "expectedValid": entry["expectedValid"], "passed": False, "detail": f"Fixture execution error: {type(exc).__name__}: {exc}"})
    return {"fixtures": results, "passed": bool(results) and all(x["passed"] for x in results), "fixtureCount": len(results), "conceptCountCheck": muscle_concept_count(load_json(ROOT / next(x["path"] for x in index["fixtures"] if x["expectedValid"]))) == index["expectedIndividualMuscleConceptCount"]}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate HUMAN ATLAS schema, dataset relationships, reviews, and learning manifest eligibility.")
    parser.add_argument("--dataset", type=Path, help="Validate one dataset JSON file.")
    parser.add_argument("--fixtures", action="store_true", help="Run the indexed positive/negative fixture suite.")
    parser.add_argument("--check-schemas", action="store_true", help="Check the Draft 2020-12 schema and supported-keyword constraints.")
    args = parser.parse_args()
    if not (args.dataset or args.fixtures or args.check_schemas): args.fixtures = True
    schema, schema_errors = validate_schema_file()
    if schema is None or schema_errors:
        print(json.dumps({"passed": False, "schemaErrors": schema_errors}, ensure_ascii=False, indent=2))
        return 2
    if args.check_schemas and not args.dataset and not args.fixtures:
        print(json.dumps({"passed": True, "schema": str(SCHEMA_PATH), "draft": SCHEMA_DRAFT, "keywordSubsetChecked": True}, ensure_ascii=False, indent=2))
        return 0
    results = {"schemaCheck": "passed"}
    if args.dataset:
        try:
            data = load_json(args.dataset)
            errors = validate_dataset(data, schema)
            results["dataset"] = str(args.dataset)
            results["valid"] = not errors
            results["issues"] = errors
        except Exception as exc:
            results["valid"] = False
            results["issues"] = [Issue("dataset_load_error", str(args.dataset), f"{type(exc).__name__}: {exc}")]
    if args.fixtures:
        fixture_results = run_fixtures(schema)
        results["fixtureSuite"] = fixture_results
    passed = results.get("valid", True) and results.get("fixtureSuite", {}).get("passed", True) and results.get("fixtureSuite", {}).get("conceptCountCheck", True)
    results["passed"] = passed
    results["exitCode"] = 0 if passed else 1
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0 if passed else 1

if __name__ == "__main__":
    raise SystemExit(main())
