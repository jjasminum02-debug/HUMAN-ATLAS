import collections
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def read_json(path: str):
    return json.loads((ROOT / path).read_text())


def sha256(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


scope = read_json("work/evidence/T66/priority-integration-2026-10-05/product-scope.json")
bundle = read_json("atlas-data/motion/motion-learning.json")
overlay = read_json("atlas-data/overlays/za-local-integration.json")
attachment_context = read_json("atlas-data/terminology/learner-attachment-context.json")
objects = {row["sourceKey"]: row for row in overlay["objects"]}
assets = {row["id"]: row for row in bundle["motionAssets"]}

bindings = []
for scope_row in scope["sourceBindings"]:
    for option in scope_row["options"]:
        asset = assets[option["assetId"]]
        source_binding = asset["sourceBinding"]
        group = scope_row["group"]
        subject = scope_row["sourceKey"]
        side = scope_row["sourceSide"]
        members = source_binding["members"]
        member_by_key = {member["sourceKey"]: member for member in members}
        focus_keys = asset.get("poseControl", {}).get("framingSourceKeys") or []
        matched_focus = [key for key in focus_keys if key in member_by_key]
        base_frame = matched_focus or [member["sourceKey"] for member in members]
        moving_bones = [
            member["sourceKey"]
            for member in members
            if member.get("role") in ("moving_structure", "co_moving_context")
            and objects.get(member["sourceKey"], {}).get("kind") == "bone"
        ]

        attachment_fields = attachment_context.get(subject)
        raw_attachments = []
        if attachment_fields:
            raw_attachments = list(dict.fromkeys(
                attachment_fields.get("origin", []) + attachment_fields.get("insertion", [])
            ))
        attachment_rows = []
        eligible_attachments = []
        for key in raw_attachments:
            row = objects.get(key)
            if not row:
                status = "source-key-not-in-current-overlay"
            elif row.get("kind") != "bone":
                status = "not-bone"
            elif not row.get("localDisplayEligible"):
                status = "not-local-display-eligible"
            elif not row.get("defaultVisible"):
                status = "not-default-visible"
            elif row.get("hardHoldReasons"):
                status = "hard-held"
            elif row.get("sourceHiddenStatePreserved", {}).get("hideViewport"):
                status = "source-hidden"
            elif row.get("side") not in (side, None):
                status = "other-side"
            else:
                status = "eligible-exact-context-bone"
                eligible_attachments.append(key)
            role = "origin" if key in attachment_fields.get("origin", []) else "insertion"
            attachment_rows.append({
                "sourceKey": key,
                "role": role,
                "displayStatus": status,
                "sourceSide": row.get("side") if row else None,
                "memberAlreadyInPackage": key in member_by_key,
            })

        frame_keys = list(dict.fromkeys(base_frame + [subject] + moving_bones + eligible_attachments))
        role_counts = collections.Counter(member["role"] for member in members)
        bone_role_counts = collections.Counter(
            member["role"] for member in members
            if objects.get(member["sourceKey"], {}).get("kind") == "bone"
        )
        muscle_role_counts = collections.Counter(
            member["role"] for member in members
            if objects.get(member["sourceKey"], {}).get("kind") == "muscle"
        )
        bindings.append({
            "group": scope_row["group"],
            "subjectSourceKey": subject,
            "side": side,
            "action": option["label"],
            "actionId": option["actionId"],
            "learningIntent": option["learningIntent"],
            "assetId": asset["id"],
            "uri": asset["uri"],
            "sha256": asset["sha256"],
            "actualFileHashMatches": option.get("actualFileHashMatches"),
            "bindingSide": asset["staticBinding"]["side"],
            "frameId": asset["staticBinding"]["frameId"],
            "referencePoseId": asset["staticBinding"]["referencePoseId"],
            "memberCount": len(members),
            "roleCounts": dict(role_counts),
            "boneRoleCounts": dict(bone_role_counts),
            "muscleRoleCounts": dict(muscle_role_counts),
            "declaredFocusKeyCount": len(focus_keys),
            "matchedDeclaredFocusKeyCount": len(matched_focus),
            "movingBoneSourceKeys": moving_bones,
            "exactAttachmentBoneContext": attachment_rows,
            "frameSourceKeysBefore": len(matched_focus) if matched_focus else len(members),
            "frameSourceKeysAfter": len(frame_keys),
            "allSubjectMovingBonesInFrame": set(moving_bones).issubset(frame_keys),
            "subjectInFrame": subject in frame_keys,
            "allEligibleAttachmentContextInFrame": set(eligible_attachments).issubset(frame_keys),
            "oppositeSideContextMemberKeys": [
                member["sourceKey"] for member in members
                if member.get("side") not in (side, None)
            ],
            "oppositeSideContextDisposition": (
                "retained bilateral torso co-context; source-side labels remain unchanged"
                if group in ("복직근", "외복사근") and any(member.get("side") not in (side, None) for member in members)
                else "no opposite-side context members"
                if not any(member.get("side") not in (side, None) for member in members)
                else "requires source/action-specific review; no side inference"
            ),
            "isolatePolicy": "explicit user isolate remains authoritative; default motion view shows exact source context",
        })

input_paths = [
    "work/evidence/T66/priority-integration-2026-10-05/product-scope.json",
    "atlas-data/motion/motion-learning.json",
    "atlas-data/overlays/za-local-integration.json",
    "atlas-data/terminology/learner-attachment-context.json",
    "atlas-web/src/viewer/datasets/DatasetSceneAdapter.ts",
    "atlas-web/src/viewer/datasets/motionFrameContext.ts",
]
summary = {
    "T66SourceScope": {
        "groups": 7,
        "availableSurfaces": 20,
        "exactActionBindings": 22,
        "uniqueGlbUris": len({row["uri"] for row in bindings}),
        "wholeMuscleGoal": "partial",
        "sourceOnly": True,
        "humanReview": "not_performed",
        "publicRedistribution": "held",
    },
    "runtimeRowsAudited": len(bindings),
    "uniqueMotionSubjects": len({row["subjectSourceKey"] for row in bindings}),
    "uniqueGlbUris": len({row["uri"] for row in bindings}),
    "bindingHashMatches": all(row["actualFileHashMatches"] for row in bindings),
    "allSubjectsAndMovingBonesInFrame": all(
        row["allSubjectMovingBonesInFrame"] and row["subjectInFrame"] for row in bindings
    ),
    "eligibleAttachmentRows": sum(
        sum(item["displayStatus"] == "eligible-exact-context-bone" for item in row["exactAttachmentBoneContext"])
        for row in bindings
    ),
    "attachmentRowsNotEligibleOrMissing": sum(
        sum(item["displayStatus"] != "eligible-exact-context-bone" for item in row["exactAttachmentBoneContext"])
        for row in bindings
    ),
    "oppositeSideContextMemberRows": sum(len(row["oppositeSideContextMemberKeys"]) for row in bindings),
    "oppositeSideContextBindings": sum(bool(row["oppositeSideContextMemberKeys"]) for row in bindings),
    "oppositeSideContextDisposition": "the 4 affected bindings are paired trunk-flexion packages (rectus abdominis/external oblique); retain source-side identity and co-moving body context, do not infer opposite-side target selection",
    "framePolicy": "authored focus + exact subject + every moving/co-moving bone member + eligible exact origin/insertion whole-bone context; respects layer/hidden/isolate",
    "inputs": {path: sha256(path) for path in input_paths},
}
output = ROOT / "work/evidence/T85/quality-review-2026-10-06/motion-context-coverage.json"
output.write_text(json.dumps({"capturedAt": "2026-10-06", "summary": summary, "bindings": bindings}, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(summary, ensure_ascii=False, indent=2))
print(f"output={output.relative_to(ROOT)}")
