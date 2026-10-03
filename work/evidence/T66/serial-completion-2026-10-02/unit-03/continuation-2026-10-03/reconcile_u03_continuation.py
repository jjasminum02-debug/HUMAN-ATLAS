#!/usr/bin/env python3
"""Reconcile the already-produced U03 packages and the U01 browser supplement."""
from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
BASE_HEAD = "2aa20fc03757f4a890dbe8220eb316aa282863bc"
UNIT = ROOT / "work/evidence/T66/serial-completion-2026-10-02/unit-03"
CONT = UNIT / "continuation-2026-10-03"


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def read_json(path: Path):
    return json.loads(path.read_text())


def git_file(rev: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{rev}:{path}"], cwd=ROOT)


def candidate_hash(row: dict) -> str | None:
    return row.get("motionSha256") or (row.get("metrics") or {}).get("motionSha256")


def main() -> None:
    # The user supplied these pre-U03 row-vs-unique counts. Verify the base
    # identity-set size from the pinned, actual motion bundle and compute only
    # the exact typed U03 delta from its registration receipt.
    base_raw = git_file(BASE_HEAD, "atlas-data/motion/motion-learning.json")
    base = json.loads(base_raw)
    base_instance_ids = {
        d["instanceId"] for d in base["motionDefinitions"]
        if isinstance(d.get("instanceId"), str) and d["instanceId"].startswith("ZA-")
    }
    base_uris = {a.get("uri") for a in base["motionAssets"] if a.get("uri")}
    base_source_uris = {u for u in base_uris if "/t24-" not in u and "/t24/" not in u}

    current_path = ROOT / "atlas-data/motion/motion-learning.json"
    current_raw = current_path.read_bytes()
    current = json.loads(current_raw)
    current_instance_ids = {
        d["instanceId"] for d in current["motionDefinitions"]
        if isinstance(d.get("instanceId"), str) and d["instanceId"].startswith("ZA-")
    }
    current_uris = {a.get("uri") for a in current["motionAssets"] if a.get("uri")}
    current_source_uris = {u for u in current_uris if "/t24-" not in u and "/t24/" not in u}
    current_uri_to_hashes: dict[str, set[str]] = defaultdict(set)
    for asset in current["motionAssets"]:
        uri = asset.get("uri")
        sha = asset.get("sha256")
        if uri and sha:
            current_uri_to_hashes[uri].add(sha)
    current_source_hashes = {
        sha for uri, hashes in current_uri_to_hashes.items()
        if uri in current_source_uris for sha in hashes
    }
    current_runtime_hashes = {sha for hashes in current_uri_to_hashes.values() for sha in hashes}
    current_t66_family_sides = {
        d.get("sourceFamilyId") for d in current["motionDefinitions"]
        if d.get("id", "").startswith("T66") and d.get("sourceFamilyId")
    }

    u02_path = ROOT / "work/evidence/T66/serial-completion-2026-10-02/unit-02/registration.json"
    u03_registration_path = UNIT / "registration.json"
    u02 = read_json(u02_path)
    u03 = read_json(u03_registration_path)
    u03_rows = u03["registeredRows"]
    subject_rows = Counter(row["subjectKind"] for row in u03_rows)
    u03_keys_by_kind = {
        kind: {row["sourceKey"] for row in u03_rows if row.get("subjectKind") == kind}
        for kind in ("muscle", "bone")
    }
    u03_new_keys = {kind: keys - base_instance_ids for kind, keys in u03_keys_by_kind.items()}

    # Candidate records are revision snapshots. Resolve latest per family-side
    # without deleting any earlier failed trial.
    revision_files = [
        "candidate-production.json",
        "revision-r2/candidate-production.json",
        "revision-r3/candidate-production.json",
        "revision-r4-authoring/candidate-production.json",
        "revision-r5-accepted-02/candidate-production.json",
        "revision-r5-accepted-04/candidate-production.json",
    ]
    latest: dict[str, dict] = {}
    historical_counts: dict[str, dict] = {}
    for relative in revision_files:
        path = UNIT / relative
        if not path.exists():
            continue
        payload = read_json(path)
        statuses = Counter(row.get("status", "missing_status") for row in payload.get("results", []))
        historical_counts[relative] = dict(sorted(statuses.items()))
        for row in payload.get("results", []):
            latest[row["id"]] = {"revisionFile": relative, **row}

    registered_families = set(u03["families"])
    candidate_families = set(latest)
    register_by_family: dict[str, list[dict]] = defaultdict(list)
    for row in u03_rows:
        register_by_family[row["familyId"]].append(row)
    hash_matches = {}
    for family in sorted(registered_families & candidate_families):
        candidate = latest[family]
        candidate_sha = candidate_hash(candidate)
        receipt_hashes = {row["motionSha256"] for row in register_by_family[family]}
        hash_matches[family] = candidate_sha is not None and receipt_hashes == {candidate_sha}

    registration_r2 = UNIT / "registration-r2.json"
    if registration_r2.exists():
        raise SystemExit("Unexpected registration-r2.json exists; reconcile its actual content before proceeding")

    runtime = {
        "schemaVersion": "t66-motion-count-reconciliation-v1",
        "task": "T66",
        "unit": "03-continuation-2026-10-03",
        "baselineHead": BASE_HEAD,
        "currentHead": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "baseline": {
            "motionLearningSha256": sha_bytes(base_raw),
            "motionActionCount": len(base["muscleActions"]),
            "motionDefinitionCount": len(base["motionDefinitions"]),
            "motionAssetCount": len(base["motionAssets"]),
            "uniqueZaInstanceIds": len(base_instance_ids),
            "uniqueAllRuntimeUris": len(base_uris),
            "uniqueSourceDerivedUrisExcludingT24": len(base_source_uris),
            "preU03MetricsAsSpecified": {
                "uniqueMuscleSourceSurfaces": 81,
                "muscleActionRows": 129,
                "uniqueBoneSourceInstances": 122,
                "boneFamilyRows": 327,
                "uniqueSourceDerivedMotionUris": 15
            },
            "sourceOfTypedBaselineCounts": "continuation instruction and pre-U03 T66 execution/report evidence; total distinct ZA instance identities independently reconcile to 203"
        },
        "unit03Registration": {
            "registrationFile": str(u03_registration_path.relative_to(ROOT)),
            "schemaVersion": u03["schemaVersion"],
            "sha256": sha_file(u03_registration_path),
            "registeredFamilySidePackages": len(registered_families),
            "registeredSelectorRows": len(u03_rows),
            "rowsBySubjectKind": dict(sorted(subject_rows.items())),
            "uniqueKeysBySubjectKind": {k: len(v) for k, v in u03_keys_by_kind.items()},
            "newKeysAgainstPinnedPreU03ZaIdentitySet": {k: len(v) for k, v in u03_new_keys.items()},
            "distinctMotionUris": len({r["motionUri"] for r in u03_rows}),
            "publicRights": sorted({r["publicRedistribution"] for r in u03_rows}),
            "humanReview": sorted({r["humanReview"] for r in u03_rows}),
            "localTechnicalOnlyValues": sorted({r["localTechnicalOnly"] for r in u03_rows}),
            "canonicalHaBindingsAdded": 0
        },
        "currentRuntime": {
            "motionLearningSha256": sha_bytes(current_raw),
            "motionActionCount": len(current["muscleActions"]),
            "motionDefinitionCount": len(current["motionDefinitions"]),
            "motionAssetCount": len(current["motionAssets"]),
            "uniqueZaInstanceIds": len(current_instance_ids),
            "uniqueRuntimeUrisIncludingNonZaT24": len(current_uris),
            "uniqueSourceDerivedUrisExcludingNonZaT24": len(current_source_uris),
            "uniqueRuntimeGlbSha256IncludingNonZaT24": len(current_runtime_hashes),
            "uniqueSourceDerivedGlbSha256ExcludingNonZaT24": len(current_source_hashes),
            "runtimeUriToHashRelationIsOneToOne": all(len(hashes) == 1 for hashes in current_uri_to_hashes.values()),
            "uniqueT66FamilySideKeys": len(current_t66_family_sides),
            "derivedFromBaselinePlusU03": {
                "uniqueMuscleSourceSurfaces": 81 + len(u03_new_keys["muscle"]),
                "muscleActionRows": 129 + subject_rows["muscle"],
                "uniqueBoneSourceInstances": 122 + len(u03_new_keys["bone"]),
                "boneFamilyRows": 327 + subject_rows["bone"],
                "uniqueSourceDerivedMotionUris": 15 + len({r["motionUri"] for r in u03_rows})
            },
            "calculationChecks": {
                "zaIdentityUnionMatchesCurrent": len(base_instance_ids | set().union(*u03_keys_by_kind.values())) == len(current_instance_ids),
                "u03MuscleAndBoneRowsSumToReceipt": subject_rows["muscle"] + subject_rows["bone"] == len(u03_rows),
                "runtimeSourceDerivedUriSetMatchesCalculatedCount": len(current_source_uris) == 15 + len({r["motionUri"] for r in u03_rows}),
                "sourceDerivedHashCountMatchesUniqueUris": len(current_source_hashes) == len(current_source_uris),
                "runtimeHashCountMatchesUniqueUris": len(current_runtime_hashes) == len(current_uris),
                "eachRuntimeUriHasOneHash": all(len(hashes) == 1 for hashes in current_uri_to_hashes.values()),
                "allTypedU03KeysAreZaIds": all(k.startswith("ZA-") for values in u03_keys_by_kind.values() for k in values)
            }
        }
    }
    runtime_path = CONT / "runtime-count-reconciliation.json"
    runtime_path.write_text(json.dumps(runtime, ensure_ascii=False, indent=2) + "\n")

    candidate_status = {k: v.get("status") for k, v in latest.items()}
    candidate = {
        "schemaVersion": "t66-u03-candidate-registration-reconciliation-v1",
        "unit": "03",
        "latestCandidateRecordByFamilySide": {
            family: {
                "latestRevisionFile": row["revisionFile"],
                "status": row.get("status"),
                "motionSha256": candidate_hash(row),
                "registrationHashMatches": hash_matches.get(family, False),
                "failureCount": len(row.get("failures", []))
            }
            for family, row in sorted(latest.items())
        },
        "latestCandidateCounts": dict(sorted(Counter(candidate_status.values()).items())),
        "historicalTrialCountsByRevision": historical_counts,
        "latestFamilySides": len(latest),
        "registeredFamilySides": len(registered_families),
        "candidatePassButUnregistered": sorted(f for f, row in latest.items() if row.get("status") == "candidate_pass" and f not in registered_families),
        "registeredButNotLatestCandidatePass": sorted(f for f in registered_families if latest.get(f, {}).get("status") != "candidate_pass"),
        "registrationFamilyHashMismatches": sorted(f for f, matches in hash_matches.items() if not matches),
        "registrationR2Artifact": {
            "expectedPath": str(registration_r2.relative_to(ROOT)),
            "exists": registration_r2.exists(),
            "actualLatestRegistration": str(u03_registration_path.relative_to(ROOT)),
            "actualLatestSchema": u03["schemaVersion"]
        },
        "registrationIsNotUiAcceptance": True
    }
    candidate_path = CONT / "candidate-registration-reconciliation.json"
    candidate_path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n")

    browser_path = CONT / "browser-u01/browser-validation.json"
    browser = read_json(browser_path)
    browser_files = []
    screenshot_root = CONT / "browser-u01/screenshots"
    for check in browser["checks"]:
        for name in check["screenshots"]:
            path = screenshot_root / name
            browser_files.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha_file(path)})
    browser_ok = all(
        row.get("cardMatchesSourceAndSide") is True
        and row.get("actionMatchesSelection") is True
        and row.get("playbackStarted") is True
        and row.get("midProgress", 0) > 0
        and row.get("canvasChangedAtMidpoint") is True
        and row.get("reClickReturnedProgressToZero") is True
        and row.get("returnedCardStillMatches") is True
        and row.get("internalMetadataVisible") is False
        and row.get("viewport", {}).get("width") == 1440
        and row.get("pageWidth") == 1440
        for row in browser["checks"]
    ) and not browser.get("consoleErrors") and not browser.get("pageErrors")
    browser_summary = {
        "schemaVersion": "t66-u01-browser-supplement-validation-v1",
        "input": str(browser_path.relative_to(ROOT)),
        "inputSha256": sha_file(browser_path),
        "fourCandidateChecksPassed": len(browser["checks"]) == 4 and browser_ok and browser.get("allFourCandidatesPassed") is True,
        "candidateCount": len(browser["checks"]),
        "checks": browser["checks"],
        "consoleErrors": browser.get("consoleErrors"),
        "pageErrors": browser.get("pageErrors"),
        "failure": browser.get("failure"),
        "screenshots": browser_files,
        "scopeLimit": "Exact bilateral short-head biceps source/action combinations only; not whole-family extent approval or human anatomy review."
    }
    (CONT / "u01-browser-supplement-validation.json").write_text(json.dumps(browser_summary, ensure_ascii=False, indent=2) + "\n")

    if not all(runtime["currentRuntime"]["calculationChecks"].values()):
        raise SystemExit("Runtime count reconciliation did not match current data")
    if candidate["latestCandidateCounts"] != {"candidate_pass": 18}:
        raise SystemExit(f"Unexpected latest U03 candidate status counts: {candidate['latestCandidateCounts']}")
    if candidate["candidatePassButUnregistered"] or candidate["registeredButNotLatestCandidatePass"] or candidate["registrationFamilyHashMismatches"]:
        raise SystemExit("Candidate and registration receipts disagree")
    if not browser_summary["fourCandidateChecksPassed"]:
        raise SystemExit("U01 browser supplement failed its recorded checks")
    print(json.dumps({
        "runtime": runtime["currentRuntime"],
        "candidate": {k: candidate[k] for k in ["latestCandidateCounts", "latestFamilySides", "registeredFamilySides", "candidatePassButUnregistered", "registeredButNotLatestCandidatePass", "registrationFamilyHashMismatches", "registrationR2Artifact"]},
        "browser": {k: browser_summary[k] for k in ["fourCandidateChecksPassed", "candidateCount", "consoleErrors", "pageErrors"]}
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
