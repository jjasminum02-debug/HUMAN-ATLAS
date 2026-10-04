#!/usr/bin/env python3
"""Build the T66 wave-1 source-local registration from frozen, QC-passed workers."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import struct
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[5]
WAVE = ROOT / "work/evidence/T66/parallel-completion-2026-10-03/wave-1"
WORKERS = WAVE / "workers"
OUT = ROOT / "work/evidence/T66/parallel-completion-2026-10-03/integration-wave1"
ASSET_OUT = ROOT / "atlas-data/assets/motion/t66-wave1"
OUT.mkdir(parents=True, exist_ok=True)
ASSET_OUT.mkdir(parents=True, exist_ok=True)

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def glb_doc(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if data[:4] != b"glTF" or struct.unpack_from("<I", data, 8)[0] != len(data):
        raise ValueError(f"invalid GLB header: {path}")
    offset = 12
    while offset < len(data):
        size, kind = struct.unpack_from("<I4s", data, offset)
        offset += 8
        chunk = data[offset:offset + size]
        offset += size
        if kind == b"JSON":
            return json.loads(chunk.rstrip(b" \t\r\n\0"))
    raise ValueError(f"GLB JSON chunk missing: {path}")

def copy_asset(source: Path, expected_hash: str, stem: str) -> tuple[str, int]:
    actual = sha(source)
    if actual != expected_hash:
        raise ValueError(f"worker GLB hash mismatch: {source}: {actual} != {expected_hash}")
    name = f"{stem}-{actual[:12]}.glb"
    dest = ASSET_OUT / name
    if dest.exists() and sha(dest) != actual:
        raise ValueError(f"refusing to overwrite a different integration asset: {dest}")
    if not dest.exists():
        shutil.copyfile(source, dest)
    return f"atlas-data/assets/motion/t66-wave1/{name}", source.stat().st_size

def side_laterality(value: str | None) -> str:
    return value if value in ("left", "right") else "midline"

def korean_digit(value: int) -> str:
    return {1: "엄지손가락", 2: "집게손가락", 3: "가운뎃손가락", 4: "약손가락", 5: "새끼손가락"}.get(value, "손가락")

def korean_joint(joint: str) -> str:
    return {
        "CMC": "손목손허리관절", "MCP": "손허리손가락관절",
        "PIP": "몸쪽손가락뼈사이관절", "DIP": "먼쪽손가락뼈사이관절", "IP": "손가락뼈사이관절",
    }.get(joint, "손가락관절")

def korean_action(action: str) -> str:
    normalized = action.strip().lower()
    for term, label in (("flexion", "굽힘"), ("extension", "폄"), ("abduction", "벌림"), ("adduction", "모음"), ("opposition", "맞섬")):
        if normalized == term or normalized.endswith(" " + term):
            return label
    return "움직임"

manifest_path = WAVE / "run-manifest.json"
manifest = read_json(manifest_path)
if manifest.get("runId") != "T66-W1-20261003-5dadff8d782b":
    raise ValueError("wave-1 runId mismatch")
source_manifest_path = ROOT / "atlas-data/source-cache/datasets/za/compiled/manifest.json"
overlay_path = ROOT / "atlas-data/overlays/za-local-integration.json"
source_manifest = read_json(source_manifest_path)
overlay = read_json(overlay_path)
source_validation_path = OUT / "candidate-source-validation.json"
source_validation = read_json(source_validation_path)
if source_validation.get("result") != "passed" or source_validation.get("runId") != manifest.get("runId"):
    raise ValueError("persisted C exact source/frame validation missing or stale")
runtime_node_id_by_source = {
    row["sourceKey"]: row["runtimeNodeId"]
    for candidate in source_validation["candidates"]
    for row in candidate["rows"]
}
geometry_by_source = {
    row["sourceKey"]: row["candidateGeometrySha256"]
    for candidate in source_validation["candidates"] for row in candidate["rows"]
}
source_hash = sha(source_manifest_path)
overlay_hash = sha(overlay_path)
instance_by_key = {row["sourceKey"]: row for row in source_manifest["instances"]}
chunk_by_id = {row["id"]: row for row in source_manifest["chunks"]}
frame_id = source_manifest["frameContract"]["targetFrameId"]
pose_id = source_manifest["frameContract"]["staticReferencePose"]["id"]
scene_ref = {
    "sceneId": "ZA-T59-R-ANKLE-SOURCE-SNAPSHOT",
    "sceneRevision": source_manifest["revision"],
    "modelId": source_manifest["namespace"],
    "sourceAssetSha256": "af7cdd79142f17016bafa744b219fd6587571b9a628899826885562195c57243",
    "frameId": frame_id,
    "units": "m",
    "poseId": pose_id,
}

actions: list[dict[str, Any]] = []
definitions: list[dict[str, Any]] = []
assets: list[dict[str, Any]] = []
provenance: list[dict[str, Any]] = []
package_refs: dict[str, dict[str, Any]] = {}
seen_action_ids: set[str] = set()
seen_definition_ids: set[str] = set()
seen_asset_ids: set[str] = set()

def validate_members(members: list[dict[str, Any]], glb_path: Path, source_kind: str) -> None:
    doc = glb_doc(glb_path)
    node_ids = {node.get("extras", {}).get("sourceKey"): node for node in doc.get("nodes", []) if node.get("extras", {}).get("sourceKey")}
    if len(node_ids) != len([node for node in doc.get("nodes", []) if node.get("extras", {}).get("sourceKey")]):
        raise ValueError(f"duplicate sourceKey in candidate GLB: {glb_path}")
    if len(members) != len(node_ids):
        raise ValueError(f"candidate node/member count mismatch for {source_kind}: {len(members)} != {len(node_ids)}")
    for member in members:
        source_key = member["sourceKey"]
        instance = instance_by_key.get(source_key)
        node = node_ids.get(source_key)
        if not instance or not node:
            raise ValueError(f"candidate/source manifest identity missing: {source_key}")
        namespace = instance.get("sourceNamespace", source_manifest["namespace"])
        if namespace != member["sourceNamespace"]:
            raise ValueError(f"namespace mismatch for {source_key}")
        side = instance.get("sourceLabelSide")
        if side != member.get("side"):
            raise ValueError(f"source side mismatch for {source_key}: {side} != {member.get('side')}")
        lod = instance["lods"][member["lod"]]
        if lod["resource"] != member["resourceKey"] or lod["chunk"] != member["sourceChunkSha256"]:
            raise ValueError(f"resource/chunk mismatch for {source_key}")
        if member["instanceMatrix"] != instance["matrix"]:
            raise ValueError(f"instance matrix mismatch for {source_key}")
        node_matrix = node.get("extras", {}).get("sourceInstanceMatrix", node.get("matrix"))
        if node_matrix is not None and len(node_matrix) == 16:
            if any(abs(float(a) - float(b)) > 1e-6 for a, b in zip(node_matrix, instance["matrix"])):
                raise ValueError(f"candidate frame matrix mismatch for {source_key}")
        if member.get("role") not in {"deforming_muscle_surface", "deforming_passive_surface", "moving_structure", "co_moving_context", "fixed_structure", "passive_context"}:
            raise ValueError(f"unsupported member role for {source_key}")
    if source_manifest["unit"] != "m" or frame_id != "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR":
        raise ValueError("source frame contract changed")

def add_selector(
    *, family_id: str, side: str, subject_key: str, subject_kind: str,
    action_label: str, explanation: str, glb_uri: str, glb_sha: str,
    duration: float, clip_id: str, members: list[dict[str, Any]],
    evidence_refs: list[str], pose_control: dict[str, Any] | None = None,
) -> None:
    action_id = f"T66-W1-ACTION-{len(actions)+1:04d}"
    definition_id = f"T66-W1-DEF-{len(definitions)+1:04d}"
    asset_id = f"T66-W1-ASSET-{len(assets)+1:04d}"
    if action_id in seen_action_ids or definition_id in seen_definition_ids or asset_id in seen_asset_ids:
        raise ValueError("generated integration ID collision")
    seen_action_ids.add(action_id); seen_definition_ids.add(definition_id); seen_asset_ids.add(asset_id)
    source_subject = next((row for row in members if row["sourceKey"] == subject_key), None)
    if not source_subject:
        raise ValueError(f"subject not present in package member list: {subject_key}")
    if subject_kind == "muscle" and (source_subject["role"] not in {"deforming_muscle_surface", "deforming_passive_surface"} or source_subject["side"] != side):
        raise ValueError(f"muscle subject role/side mismatch: {subject_key}")
    if subject_kind == "bone" and (source_subject["role"] not in {"moving_structure", "fixed_structure"} or side_laterality(source_subject.get("side")) != side):
        raise ValueError(f"bone subject role/side mismatch: {subject_key}")
    moving = [row["sourceKey"] for row in members if row["role"] in {"moving_structure", "co_moving_context"}]
    fixed = [row["sourceKey"] for row in members if row["role"] == "fixed_structure"]
    if subject_kind == "bone" and subject_key not in moving + fixed:
        raise ValueError(f"bone selector subject absent from moving/fixed set: {subject_key}")
    node_bindings = [{"structureId": row["sourceKey"], "nodeId": row["nodeId"]} for row in members if row["role"] in {"moving_structure", "co_moving_context"}]
    action = {
        "subjectKind": subject_kind,
        "id": action_id,
        "subjectIds": [],
        "sourceSubjectKeys": [subject_key],
        "learnerActionKey": action_id,
        "sideApplicability": side,
        "jointBindingState": "source_family_bound",
        "sourceFamilyId": family_id,
        "jointBindingNote": None,
        "targetJointIds": [],
        "actionLabel": action_label,
        "explanation": explanation,
        "postureConditions": [],
        "stabilizationConditions": [],
        "stabilizationNote": None,
        "contextRoles": [],
        "sourceRefs": [],
    }
    definition = {
        "sourceFamilyId": family_id,
        "id": definition_id,
        "actionId": action_id,
        "instanceId": subject_key,
        "side": side,
        "targetJointIds": [],
        "movingStructureIds": moving,
        "fixedStructureIds": fixed,
        "staticReference": scene_ref,
        "startPoseId": pose_id,
        "endPoseId": f"{family_id}:end",
        "poseSourceRefs": [],
    }
    binding = {
        "sourceFamilyId": family_id,
        "contractVersion": "t66-typed-source-motion-v2",
        "subjectKind": subject_kind,
        "datasetNamespace": source_manifest["namespace"],
        "datasetRevision": source_manifest["revision"],
        "integrationRevision": overlay["revision"],
        "sourceOverlaySha256": overlay_hash,
        "subjectSourceKey": subject_key,
        "frameId": frame_id,
        "units": "m",
        "referencePoseId": pose_id,
        "deformation": "morph_targets",
        "members": members,
    }
    asset = {
        "id": asset_id,
        "motionDefinitionId": definition_id,
        "uri": glb_uri,
        "revision": f"t66-wave1-{glb_sha[:12]}",
        "sha256": glb_sha,
        "sourceId": "ZA-c7010a9-PINNED-LOCAL",
        "licenseId": "LIC-ZA-PINNED-LOCAL-DECISION",
        "representationType": "source_bound_surface",
        "staticBinding": {
            "sceneId": scene_ref["sceneId"], "sceneRevision": source_manifest["revision"],
            "modelId": source_manifest["namespace"], "sourceAssetSha256": scene_ref["sourceAssetSha256"],
            "frameId": frame_id, "units": "m", "side": side, "referencePoseId": pose_id,
        },
        "rig": {"id": family_id, "nodeBindings": node_bindings},
        "illustration": None,
        "clip": {"id": clip_id, "durationSeconds": duration, "startPoseId": pose_id, "endPoseId": f"{family_id}:end"},
        "sourceBinding": binding,
        "technicalStatus": "binding_verified",
    }
    if pose_control:
        asset["poseControl"] = pose_control
    actions.append(action); definitions.append(definition); assets.append(asset)
    provenance.append({
        "actionId": action_id, "definitionId": definition_id, "assetId": asset_id,
        "familyId": family_id, "subjectSourceKey": subject_key, "subjectKind": subject_kind,
        "side": side, "evidenceRefs": evidence_refs, "sourceOnly": True,
        "publicRedistribution": "held", "humanReview": "not_performed",
        "canonicalTargetMembershipApproved": False,
        "scopeNote": "source-local educational motion; target identity/extent and human review remain unapproved",
    })

def make_a_members(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [{key: row[key] for key in (
        "sourceKey", "nodeId", "sourceNamespace", "role", "side", "resourceKey", "lod",
        "sourceChunkSha256", "geometrySha256", "instanceMatrix")}
        for row in record["members"]]

def integrate_a() -> dict[str, Any]:
    package = read_json(WORKERS / "A/candidate-package.json")
    catalog = read_json(WORKERS / "A/action-catalog.json")
    if package.get("runId") != manifest["runId"] or package.get("sourceOnly") is not True or package.get("publicRedistribution") != "held" or package.get("humanReview") != "not_performed" or package.get("canonicalBindingAdded") is not False:
        raise ValueError("A authority or run contract mismatch")
    record_by_work_key: dict[str, tuple[dict[str, Any], Path, Path]] = {}
    unique_glbs: dict[str, tuple[Path, dict[str, Any], list[dict[str, Any]], str, int, str]] = {}
    for artifact in package["artifacts"]:
        if artifact.get("role") != "derived_glb":
            continue
        glb = ROOT / artifact["path"]
        if sha(glb) != artifact["sha256"] or glb.stat().st_size != artifact["bytes"]:
            raise ValueError(f"A artifact receipt mismatch: {glb}")
        records = []
        for rec_path in glb.parent.glob("authoring-record-r*.json"):
            rec = read_json(rec_path)
            if all(rec.get(flag) is True for flag in ("candidateValidated", "actualGeometryQcPassed", "actualRigidGlbReplayPassed", "signedScaleReflectionPassed", "sourceContactQcPassed")):
                records.append((rec, rec_path))
        if not records:
            continue
        # The artifact in the package is the final named revision for this family directory.
        matching = [(rec, rec_path) for rec, rec_path in records
            if rec.get("motionSha256") == artifact["sha256"] and rec.get("motionBytes") == artifact["bytes"]]
        if not matching:
            continue
        record, record_path = max(matching, key=lambda pair: int(re.search(r"r(\d+)", pair[1].stem).group(1)))
        work_ids = record.get("sourceActionWorkKeyIds", [])
        for work_id in work_ids:
            record_by_work_key[work_id] = (record, record_path, glb)
        if work_ids:
            members = make_a_members(record)
            validate_members(members, glb, "A")
            uri, size = copy_asset(glb, artifact["sha256"], record["id"])
            unique_glbs[record["id"]] = (glb, record, members, uri, size, artifact["sha256"])
    accepted_rows = []
    assigned_scope_ids = {
        row.get("workKeyId") if isinstance(row, dict) else row
        for row in manifest["assignments"]["A"].get("assignedWorkKeys", [])
    }
    assigned_work_ids = {
        action_id
        for scope_row in catalog.get("assignedScopeWorkKeys", [])
        if scope_row.get("workKeyId") in assigned_scope_ids
        for action_id in scope_row.get("actionWorkKeyIds", [])
    }
    for row in catalog["actionRows"]:
        hit = record_by_work_key.get(row.get("workKeyId"))
        if not hit or row.get("workKeyId") not in assigned_work_ids or row.get("implementationState") != "qualitative_action_demonstration":
            continue
        record, record_path, glb = hit
        member = next((m for m in record["members"] if m["sourceKey"] == row["sourceKey"]), None)
        if not member or member.get("role") != "deforming_muscle_surface" or member.get("side") != row.get("side"):
            raise ValueError(f"A accepted action does not identify its exact deforming subject: {row.get('workKeyId')}")
        family = record["id"]
        _, _, members, uri, size, glb_hash = unique_glbs[family]
        doc = glb_doc(glb)
        clip_id = (doc.get("animations") or [{}])[0].get("name")
        if not clip_id:
            raise ValueError(f"A GLB animation missing: {glb}")
        digit = int(row.get("digit") or 0)
        joint = str(row.get("joint") or "")
        action_word = str(row.get("action") or "")
        label = f"{korean_digit(digit)} {korean_joint(joint)} {korean_action(action_word)}"
        explanation = "손가락 관절의 교육용 움직임과 함께 선택한 근육 표면의 변화를 관찰합니다. 정성적 시범이며 개인의 실제 수축량이나 정상 운동범위를 나타내지 않습니다."
        pose = record["family"]
        pose_control = None
        if isinstance(pose.get("endDegrees"), (int, float)) and pose.get("endDegrees") != 0:
            pose_control = {"label": "교육용 자세 각도", "startDegrees": 0, "endDegrees": float(pose["endDegrees"]), "combination": "single_dof_only"}
        duration = float(pose.get("durationSeconds") or (doc["animations"][0].get("extras", {}).get("durationSeconds") if doc["animations"] else 0) or 1.0)
        add_selector(family_id=family, side=row["side"], subject_key=row["sourceKey"], subject_kind="muscle",
            action_label=label, explanation=explanation, glb_uri=uri, glb_sha=glb_hash,
            duration=duration, clip_id=clip_id, members=members, evidence_refs=row.get("evidenceRefs", []), pose_control=pose_control)
        accepted_rows.append(row)
    action_row_by_family: dict[str, dict[str, Any]] = {}
    for row in accepted_rows:
        action_row_by_family.setdefault(row["assetFamilyId"], row)
    # Direct selection is available only for exact moving/fixed bone members in accepted packages.
    bone_rows = 0
    for family, (_, record, members, uri, size, glb_hash) in unique_glbs.items():
        doc = glb_doc(ROOT / next(a["path"] for a in package["artifacts"] if a.get("role") == "derived_glb" and a["sha256"] == glb_hash))
        clip_id = (doc.get("animations") or [{}])[0].get("name")
        duration = float(record["family"].get("durationSeconds") or 1.0)
        pose = record["family"]
        pose_control = {"label": "교육용 자세 각도", "startDegrees": 0, "endDegrees": float(pose["endDegrees"]), "combination": "single_dof_only"} if isinstance(pose.get("endDegrees"), (int, float)) and pose.get("endDegrees") != 0 else None
        for member in members:
            if member["role"] not in {"moving_structure", "fixed_structure"}:
                continue
            side = side_laterality(member.get("side"))
            if side not in {"left", "right"}:
                continue
            action_context = action_row_by_family.get(family, {})
            digit = int(action_context.get("digit") or 0)
            joint = korean_joint(str(action_context.get("joint") or "MCP"))
            action_word = korean_action(str(action_context.get("action") or "움직임"))
            label = f"{korean_digit(digit)} {joint} {action_word}에서 뼈 역할 관찰"
            explanation = "선택한 뼈가 교육용 자세에서 움직이거나 기준 구조로 유지되는 모습을 주변 구조와 함께 관찰합니다. 개인의 정상 관절축이나 운동범위를 뜻하지 않습니다."
            add_selector(family_id=family, side=side, subject_key=member["sourceKey"], subject_kind="bone",
                action_label=label, explanation=explanation, glb_uri=uri, glb_sha=glb_hash,
                duration=duration, clip_id=clip_id, members=members, evidence_refs=["exact-member-role:" + member["role"]], pose_control=pose_control)
            bone_rows += 1
    return {"acceptedActionRows": len(accepted_rows), "uniqueGlbPackages": len(unique_glbs), "muscleSelectors": len(accepted_rows), "boneSelectors": bone_rows,
        "uniqueGlbBytes": sum(row[4] for row in unique_glbs.values()), "familyIds": sorted(unique_glbs)}

def make_c_members(record: dict[str, Any], qc: dict[str, Any], glb_path: Path) -> list[dict[str, Any]]:
    role_by_key = {row["sourceKey"]: row for row in qc["memberRows"]}
    node_by_key = {node.get("extras", {}).get("sourceKey"): node for node in glb_doc(glb_path).get("nodes", []) if node.get("extras", {}).get("sourceKey")}
    source_rows = record.get("sourceRows", [])
    bone_rows = record.get("boneContextRows", [])
    members = []
    for source_row in source_rows:
        key = source_row["sourceKey"]
        qc_row = role_by_key.get(key)
        instance = instance_by_key.get(key)
        glb_node = node_by_key.get(key)
        if not qc_row or not instance or not glb_node:
            raise ValueError(f"C source row lacks QC/current instance: {key}")
        lod_name = qc_row["lod"]
        lod = instance["lods"][lod_name]
        members.append({
            "sourceKey": key, "nodeId": runtime_node_id_by_source.get(key), "sourceNamespace": instance.get("sourceNamespace", source_manifest["namespace"]),
            "role": qc_row["role"], "side": instance.get("sourceLabelSide"), "resourceKey": lod["resource"],
            "lod": lod_name, "sourceChunkSha256": lod["chunk"],
            "geometrySha256": geometry_by_source.get(key, ""),
            "instanceMatrix": instance["matrix"],
        })
        if not members[-1]["geometrySha256"]:
            raise ValueError(f"persisted C source hash validation is required before registration: {key}")
    for bone in bone_rows:
        key = bone["sourceKey"]
        qc_row = role_by_key.get(key)
        instance = instance_by_key.get(key)
        glb_node = node_by_key.get(key)
        if not qc_row or not instance or not glb_node:
            raise ValueError(f"C bone row lacks QC/current instance: {key}")
        lod_name = qc_row["lod"]
        lod = instance["lods"][lod_name]
        members.append({
            "sourceKey": key, "nodeId": runtime_node_id_by_source.get(key), "sourceNamespace": instance.get("sourceNamespace", source_manifest["namespace"]),
            "role": bone["role"], "side": instance.get("sourceLabelSide"), "resourceKey": lod["resource"],
            "lod": lod_name, "sourceChunkSha256": lod["chunk"],
            "geometrySha256": geometry_by_source.get(key, ""),
            "instanceMatrix": instance["matrix"],
        })
        if not members[-1]["geometrySha256"]:
            raise ValueError(f"persisted C source hash validation is required before registration: {key}")
    if len({row["sourceKey"] for row in members}) != len(members):
        raise ValueError(f"duplicate C source row in {record['candidateId']}")
    return members

def integrate_c() -> dict[str, Any]:
    handoff = read_json(WORKERS / "C/handoff.json")
    if handoff.get("runId") != manifest["runId"]:
        raise ValueError("C runId mismatch")
    integrated = []
    for entry in handoff["candidateAssets"]:
        if entry.get("passed") is not True:
            continue
        record_path = ROOT / entry["recordPath"]
        qc_path = ROOT / entry["poseQcPath"]
        record = read_json(record_path); qc = read_json(qc_path)
        if record.get("passed") is not True or record.get("productionAcceptance") is not False or qc.get("passed") is not True:
            raise ValueError(f"C pass state mismatch: {entry['candidateId']}")
        glb = ROOT / entry["motionGlbPath"]
        if sha(glb) != entry["motionGlbSha256"] or sha(qc_path) != entry["poseQcSha256"]:
            raise ValueError(f"C candidate receipt mismatch: {entry['candidateId']}")
        members = make_c_members(record, qc, glb)
        validate_members(members, glb, "C")
        uri, size = copy_asset(glb, entry["motionGlbSha256"], entry["candidateId"])
        doc = glb_doc(glb); clip_id = (doc.get("animations") or [{}])[0].get("name")
        if not clip_id:
            raise ValueError(f"C animation clip missing: {glb}")
        duration = float(qc["keyTimesSeconds"][-1])
        family = record["familyContract"]["namespace"]
        evidence_refs = record.get("actionEvidenceRefs", [])
        if len(record.get("sourceRows", [])) != 2:
            raise ValueError("C axial package must preserve its exact left and right source rows")
        for source_row in record["sourceRows"]:
            side = source_row["side"]
            key = source_row["sourceKey"]
            if source_row.get("targetExtentApproved") is not False or source_row.get("identityApproval") is not False:
                raise ValueError("C source relation approval was unexpectedly promoted")
            label = "허리 폄 자세 관찰" if "lumbar" in entry["candidateId"] else "목 굽힘 자세 관찰"
            if "lumbar" in entry["candidateId"]:
                explanation = "허리를 펴는 자세 일부에서 해당 다열근 표면 변화를 관찰합니다. 전체 척추 움직임이나 근육 활성도를 나타내지 않습니다."
            else:
                explanation = "목을 굽히는 자세 일부에서 긴목근 표면 변화를 관찰합니다. 위쪽 목뼈의 움직임은 포함하지 않으며 목 전체의 완전한 굽힘을 나타내지 않습니다."
            explanation += " 좌우의 해당 표면을 보여 주는 부분 시범이며 전체 근육 범위나 개인의 정상 운동범위를 확정하지 않습니다."
            add_selector(family_id=family, side=side, subject_key=key, subject_kind="muscle",
                action_label=label, explanation=explanation, glb_uri=uri, glb_sha=entry["motionGlbSha256"],
                duration=duration, clip_id=clip_id, members=members, evidence_refs=evidence_refs)
        bone_selectors = 0
        for bone in record.get("boneContextRows", []):
            key = bone["sourceKey"]
            if bone["role"] not in {"moving_structure", "fixed_structure"}:
                continue
            label = "척추 자세에서 역할 관찰"
            explanation = "선택한 뼈가 자세에서 움직이거나 기준 구조로 유지되는 모습을 주변과 함께 관찰합니다. 정상 관절축이나 전체 척추 움직임을 확정하지 않습니다."
            add_selector(family_id=family, side="midline", subject_key=key, subject_kind="bone",
                action_label=label, explanation=explanation, glb_uri=uri, glb_sha=entry["motionGlbSha256"],
                duration=duration, clip_id=clip_id, members=members, evidence_refs=evidence_refs)
            bone_selectors += 1
        integrated.append({"candidateId": entry["candidateId"], "sha256": entry["motionGlbSha256"], "bytes": size,
            "sourceMuscleRows": len(record["sourceRows"]), "boneContextRows": len(record["boneContextRows"]),
            "muscleSelectors": len(record["sourceRows"]), "boneSelectors": bone_selectors,
            "extentApproved": False, "identityApproved": False})
    return {"passedCandidateCount": len(integrated), "candidates": integrated,
        "uniqueGlbBytes": sum(row["bytes"] for row in integrated)}

if __name__ == "__main__":
    # C geometry hashes are supplied only after the separate GLTF source/member verifier writes them.
    a_metrics = integrate_a()
    c_metrics = integrate_c()
    if len(actions) != len(definitions) or len(definitions) != len(assets):
        raise ValueError("bundle cardinality mismatch")

    definition_by_action = {row["actionId"]: row for row in definitions}
    asset_by_definition = {row["motionDefinitionId"]: row for row in assets}
    templates: dict[tuple[str, str], dict[str, Any]] = {}
    selectors = []
    for action in actions:
        definition = definition_by_action.get(action["id"])
        asset = asset_by_definition.get(definition["id"]) if definition else None
        if not definition or not asset or not asset.get("sourceBinding"):
            raise ValueError(f"compact registration row is incomplete: {action['id']}")
        side = asset["staticBinding"]["side"]
        template_key = (asset["uri"], side)
        template_id = f"T66-W1-PKG-{len(templates) + 1:03d}"
        package = templates.get(template_key)
        if package is None:
            package = {
                "id": template_id,
                "familyId": action["sourceFamilyId"],
                "uri": asset["uri"], "revision": asset["revision"], "sha256": asset["sha256"],
                "sourceId": asset["sourceId"], "licenseId": asset["licenseId"],
                "representationType": asset["representationType"], "technicalStatus": asset["technicalStatus"],
                "staticBinding": asset["staticBinding"], "rig": asset["rig"], "illustration": asset["illustration"],
                "clip": asset["clip"], "poseControl": asset.get("poseControl"),
                "sourceBindingTemplate": {key: value for key, value in asset["sourceBinding"].items()
                    if key not in {"subjectKind", "subjectSourceKey"}},
                "definitionTemplate": {key: value for key, value in definition.items()
                    if key not in {"id", "actionId", "instanceId", "side"}},
            }
            templates[template_key] = package
        else:
            if package["familyId"] != action["sourceFamilyId"] or package["staticBinding"] != asset["staticBinding"]:
                raise ValueError(f"one motion URI has incompatible family/static binding: {asset['uri']}")
            if package["sourceBindingTemplate"]["members"] != asset["sourceBinding"]["members"]:
                raise ValueError(f"one motion URI has incompatible source members: {asset['uri']}")
        selectors.append({
            "actionId": action["id"], "definitionId": definition["id"], "packageId": package["id"],
            "subjectKind": action["subjectKind"], "sourceSubjectKey": action["sourceSubjectKeys"][0],
            "side": action["sideApplicability"], "learnerActionKey": action["learnerActionKey"],
            "label": action["actionLabel"], "explanation": action["explanation"],
            "evidenceRefs": next((row["evidenceRefs"] for row in provenance if row["actionId"] == action["id"]), []),
        })
    bundle = {"schemaVersion": "t66-wave1-source-motion-registration-v2",
        "revision": "t66-wave1-source-bound-local-2026-10-04",
        "authority": {"sourceOnly": True, "publicRedistribution": "held", "humanReview": "not_performed",
            "canonicalTargetMembershipApproved": False},
        "packages": list(templates.values()), "selectors": selectors}
    out_path = ROOT / "atlas-data/motion/t66-wave1-registration.json"
    out_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    evidence = {
        "schemaVersion": "t66-wave1-registration-build-v1", "runId": manifest["runId"],
        "inputHashes": {"wave1Manifest": sha(manifest_path), "sourceManifest": sha(source_manifest_path), "sourceOverlay": overlay_hash,
            "workerAActionCatalog": sha(WORKERS / "A/action-catalog.json"), "workerACandidatePackage": sha(WORKERS / "A/candidate-package.json"),
            "workerCHandoff": sha(WORKERS / "C/handoff.json")},
        "A": a_metrics, "B": {"registered": 0, "reason": "all fresh candidate geometry/contact checks failed"},
        "C": c_metrics, "bundle": {"path": str(out_path.relative_to(ROOT)), "sha256": sha(out_path),
            "selectorRows": len(selectors), "packageTemplates": len(templates),
            "muscleActionSelectors": sum(row["subjectKind"] == "muscle" for row in selectors),
            "boneSelectionSelectors": sum(row["subjectKind"] == "bone" for row in selectors),
            "uniqueGlbUris": len({asset["uri"] for asset in assets}), "uniqueGlbHashes": len({asset["sha256"] for asset in assets}),
            "sourceOnly": True, "publicRedistribution": "held", "humanReview": "not_performed", "canonicalTargetMembershipApproved": False},
        "provenance": provenance,
    }
    (OUT / "registration-build.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"A": a_metrics, "C": c_metrics, "bundle": evidence["bundle"]}, ensure_ascii=False, indent=2))
