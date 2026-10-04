#!/usr/bin/env python3
"""Freeze bounded T66 wave-2 D/E ownership over the immutable wave-1 snapshot."""
from __future__ import annotations
import copy, hashlib, json, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "work/evidence/T66/parallel-completion-2026-10-03"
W1 = BASE / "wave-1"
W2 = BASE / "wave-2"
INTEGRATION = BASE / "integration-wave1"
W1_MANIFEST = W1 / "run-manifest.json"
EXPECTED_W1_SHA = "7d12000c2a049d1c2bf09f8349159609a6dd7b5f93f1d0710742ede84aacad95"
D_NAMES = {
    "Bucinator", "Deep part of masseter", "Inferior head of lateral pterygoid muscle",
    "Medial pterygoid muscle", "Palatopharyngeus muscle", "Superficial part of masseter",
    "Superior head of lateral pterygoid muscle", "Temporalis muscle",
}
E_BONE_NAMES = {
    ("Ethmoid bone", None), ("Frontal bone", None),
    ("Inferior nasal concha bone", "left"), ("Inferior nasal concha bone", "right"),
    ("Lacrimal bone", "left"), ("Lacrimal bone", "right"),
    ("Maxilla", "left"), ("Maxilla", "right"),
    ("Nasal bone", "left"), ("Nasal bone", "right"),
    ("Palatine bone", "left"), ("Palatine bone", "right"),
    ("Sphenoid bone", None), ("Vomer", None),
    ("Zygomatic bone", "left"), ("Zygomatic bone", "right"),
}

def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def sha_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def read(path: Path): return json.loads(path.read_text(encoding="utf-8"))
def write(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink(): raise FileExistsError(f"refusing to overwrite: {path}")
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def ref(path: Path, *, snapshot_path: Path | None=None, role: str):
    if path.is_symlink() or not path.is_file(): raise FileNotFoundError(path)
    return {"path":path.relative_to(ROOT).as_posix(),"snapshotPath":(snapshot_path or path).relative_to(ROOT).as_posix(),"bytes":path.stat().st_size,"sha256":sha_file(path),"role":role}

def main():
    if W2.exists(): raise FileExistsError(f"wave-2 already exists; refusing to replace run: {W2}")
    raw_w1=W1_MANIFEST.read_bytes()
    if sha_bytes(raw_w1)!=EXPECTED_W1_SHA: raise ValueError("wave-1 raw manifest hash differs from the reviewed fixed run")
    w1=read(W1_MANIFEST)
    sys_path=str(ROOT/"work/tools")
    import sys
    sys.path.insert(0,sys_path)
    from t66_parallel_protocol import validate_manifest
    validate_manifest(w1,repo_root=ROOT,verify_snapshot=True,verify_original_inputs=False,verify_source_bytes=False)

    src_by={r["sourceKey"]:r for r in w1["sourceDisposition"]}
    unassigned=[r for r in w1["sourceActionScopeQueue"] if r["disposition"]!="assigned"]
    d_rows=[]; e_rows=[]; rest=[]
    for row in unassigned:
        key=row["key"]; src=src_by[key["sourceKey"]]
        regions=set(src.get("regionIds") or [])
        base_name=src["sourceName"].rsplit(".",1)[0]
        if "head" in regions and base_name in D_NAMES:
            d_rows.append(copy.deepcopy(row))
        elif "head" in regions or "pelvis-perineum" in regions:
            e_rows.append(copy.deepcopy(row))
        else: rest.append(copy.deepcopy(row))
    if len(d_rows)!=16 or len(e_rows)!=66 or len(rest)!=60:
        raise ValueError(f"unexpected D/E residual partition: D={len(d_rows)}, E={len(e_rows)}, other={len(rest)}")
    if {src_by[r["key"]["sourceKey"]]["sourceName"].rsplit(".",1)[0] for r in d_rows} != D_NAMES:
        raise ValueError("D source names do not match the frozen jaw/temporal/mastication/pharyngeal set")
    d_sources={r["key"]["sourceKey"] for r in d_rows}; e_sources={r["key"]["sourceKey"] for r in e_rows}
    if len(d_sources)!=16 or len(e_sources)!=66 or d_sources&e_sources: raise ValueError("D/E source assignment collision")
    if any((r["key"].get("action") is not None or r["key"].get("part") is not None) for r in d_rows+e_rows):
        raise ValueError("scope disposition rows unexpectedly imply an action/part")

    bone_rows=copy.deepcopy(w1["boneContextDisposition"])
    d_bones=[r for r in bone_rows if r.get("sourceName")=="Mandible" and r.get("side") is None and "head" in (r.get("regionIds") or [])]
    e_bones=[r for r in bone_rows if (r.get("sourceName"),r.get("side")) in E_BONE_NAMES and "head" in (r.get("regionIds") or [])]
    if len(d_bones)!=1 or len(e_bones)!=16 or len({r["sourceKey"] for r in e_bones})!=16:
        raise ValueError(f"exact D/E bone context mismatch: D={len(d_bones)}, E={len(e_bones)}")
    d_bone_keys={r["sourceKey"] for r in d_bones}; e_bone_keys={r["sourceKey"] for r in e_bones}
    if d_bone_keys&e_bone_keys: raise ValueError("D/E bone context overlap")

    m=copy.deepcopy(w1)
    m["waveNumber"]=2
    m["runId"]="T66-W2-20261004-"+sha_bytes((w1["runId"]+"|"+"|".join(sorted([r["workKeyId"] for r in d_rows+e_rows]))).encode())[:12]
    m["createdAtUtc"]=datetime.now(timezone.utc).isoformat()
    m["baselineHead"]=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    m["manifestPath"]=(W2/"run-manifest.json").relative_to(ROOT).as_posix()
    m["supplementalSnapshotRoot"]=(W2/"input-snapshot").relative_to(ROOT).as_posix()
    m["parentWave"]={"runId":w1["runId"],"manifestPath":W1_MANIFEST.relative_to(ROOT).as_posix(),"manifestSha256":EXPECTED_W1_SHA,"rawBytes":len(raw_w1),"sourceSnapshotRoot":w1["snapshotRoot"],"sourceInputsReusedByReference":True}
    baseline_path=INTEGRATION/"start-baseline.json"
    baseline_doc=read(baseline_path)
    status_lines=subprocess.check_output(["git","status","--porcelain","-uall"],cwd=ROOT,text=True).splitlines()
    prior_status=set(baseline_doc.get("gitStatusPorcelain",[]))
    m["wave2Baseline"]={
        "capturedAtUtc":datetime.now(timezone.utc).isoformat(),
        "baselineHead":m["baselineHead"],
        "priorWriterStartBaselinePath":baseline_path.relative_to(ROOT).as_posix(),
        "priorWriterStartBaselineSha256":sha_file(baseline_path),
        "priorDirtyEntryCount":baseline_doc.get("gitDirtyEntryCount"),
        "currentDirtyEntryCount":len(status_lines),
        "newStatusEntriesSinceWriterStart":sorted(set(status_lines)-prior_status),
        "note":"Existing dirty WIP is protected by the earlier captured baseline; this delta records newly observed status entries without rehashing all source assets.",
    }
    m["assignmentPolicyRevision"]="t66-wave2-exact-context-disposition-2026-10-04"
    m["assignmentsPolicy"]={"wave1":"A/B/C/F fixed and read-only carry-forward","wave2":["D","E"],"autoLaunch":False,"onlyDAndEMayWrite":True,"sourceContextRefsDoNotApproveTargetOrMembershipExtent":True}
    m["candidateOutputRules"]={
        "geometryWorkers":"D/E candidate derivation, local authoring inputs/records/QC and exact assigned source work only under worker-owned outputRoot",
        "textWorkerF":"prior wave-1 evidence is historical read-only context; no new F output in wave-2",
        "candidateReview":"sourceOnly=true, publicRedistribution=held, humanReview=not_performed, canonicalBindingAdded=false",
        "noAppRegistration":"wave-2 workers submit candidates only; integration remains a later writer step",
    }

    w2_workers={}
    for who in ("A","B","C","F"):
        prior=copy.deepcopy(w1["assignments"][who])
        prior["outputRoot"]=(W2/"workers"/who).relative_to(ROOT).as_posix()
        prior["outputAccess"]="read_only_carry_forward"
        prior["writePolicy"]="historical wave-1 result only; no new candidate output in wave-2"
        w2_workers[who]=prior
    def assignment(worker, rows, sources, bones, target_context_refs):
        return {
            "description":"wave-2 bounded source-action disposition; exact source-local coverage only, no inferred target/group extent",
            "assignedWorkKeys":[r["workKeyId"] for r in rows],
            "assignedWorkKeyRows":rows,
            "assignedSourceKeys":sorted(sources),
            "assignedTargetIds":[],"assignedMembershipKeys":[],
            "assignedBoneSourceKeys":sorted(bones),"assignedNerveRowIds":[],
            "targetContextRefs":target_context_refs,
            "outputRoot":(W2/"workers"/worker).relative_to(ROOT).as_posix(),
            "outputAccess":"write",
            "writePolicy":"only this worker outputRoot; no shared runtime/data/EXECUTION/report or other worker output writes",
            "reviewStateOnSubmission":"candidate_unreviewed_not_registered",
        }
    def context_refs(rows):
        return [{"workKeyId":r["workKeyId"],"sourceKey":r["key"]["sourceKey"],"targetIds":src_by[r["key"]["sourceKey"]].get("existingTargetIds",[]),"use":"context_only_not_an_accepted_target_or_membership_binding"} for r in rows]
    w2_workers["D"]=assignment("D",d_rows,d_sources,d_bone_keys,context_refs(d_rows))
    w2_workers["E"]=assignment("E",e_rows,e_sources,e_bone_keys,context_refs(e_rows))
    # Worker validator expects assignedWorkKeys as rows; retain the canonical rows field used in wave-1.
    for who in ("D","E"):
        record=w2_workers[who]
        record["assignedWorkKeys"]=record.pop("assignedWorkKeyRows")
    # Keep source ownership fields synchronized with exact D/E keys.
    for row in m["sourceActionScopeQueue"]:
        wid=row["workKeyId"]
        if wid in {r["workKeyId"] for r in d_rows}:
            row.update({"disposition":"assigned","assignedTo":"D","deferredTo":None,"reason":None})
        elif wid in {r["workKeyId"] for r in e_rows}:
            row.update({"disposition":"assigned","assignedTo":"E","deferredTo":None,"reason":None})
    for row in m["sourceDisposition"]:
        key=row["sourceKey"]
        if key in d_sources: row.update({"disposition":"assigned","assignedTo":"D","deferredTo":None,"assignmentBasis":"wave-2 exact source scope from worker D; no new target/part/group identity approval","reason":None})
        elif key in e_sources: row.update({"disposition":"assigned","assignedTo":"E","deferredTo":None,"assignmentBasis":"wave-2 exact source scope from worker E; no new target/part/group identity approval","reason":None})
    for row in m["boneContextDisposition"]:
        key=row["sourceKey"]
        if key in d_bone_keys: row.update({"disposition":"assigned","assignedTo":"D","deferredTo":None,"reason":"context-only jaw selection; no independent DOF inferred","independentDOFInferred":False})
        elif key in e_bone_keys: row.update({"disposition":"assigned","assignedTo":"E","deferredTo":None,"reason":"context-only face/orbit selection; no independent DOF inferred","independentDOFInferred":False})
    m["assignments"]=w2_workers

    # Preserve all 47 immutable wave-1 inputs and add a D/E-aware candidate schema.
    snapshot=W2/"input-snapshot"
    schema_out=snapshot/"files/work/schemas/t66-parallel-candidate-package.schema.json"
    schema=read(ROOT/"work/schemas/t66-parallel-candidate-package.schema.json")
    schema["properties"]["assignment"]["enum"]=["A","B","C","D","E","F"]
    schema["properties"]["candidateNamespace"]["pattern"]="^worker-(A|B|C|D|E|F):[a-z0-9][a-z0-9._-]*$"
    schema_out.parent.mkdir(parents=True,exist_ok=True)
    schema_out.write_text(json.dumps(schema,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    schema_ref=ref(schema_out,role="wave-2 D/E-aware candidate package schema")
    # The schema path is the copy frozen for wave-2, not a mutation of the live shared schema.
    schema_ref["path"]=schema_out.relative_to(ROOT).as_posix()
    schema_ref["snapshotPath"]=schema_out.relative_to(ROOT).as_posix()
    m["inputs"]=copy.deepcopy(w1["inputs"])+[schema_ref]
    m["workerOutputSchema"]=schema_ref["path"]
    m["workerOutputSchemaSha256"]=schema_ref["sha256"]

    # New current control snapshots; inherited source/data snapshots remain content-addressed in wave-1.
    controls=[]
    for rel in ("work/EXECUTION.json","work/NEXT.md"):
        original=ROOT/rel
        snap=snapshot/"files"/rel
        snap.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(original,snap)
        controls.append({"path":rel,"snapshotPath":snap.relative_to(ROOT).as_posix(),"sha256":sha_file(snap),"bytes":snap.stat().st_size,"role":"wave-2 writer-start routing context; administrative only"})
    m["controlContextSnapshots"]=controls
    assignment_snaps=[]
    for worker,record in w2_workers.items():
        item={"schemaVersion":"t66-worker-assignment-snapshot-v1","runId":m["runId"],"assignment":worker}
        for field in ("assignedWorkKeys","assignedSourceKeys","assignedTargetIds","assignedMembershipKeys","assignedBoneSourceKeys","assignedNerveRowIds"):
            item[field]=record.get(field,[])
        item["outputRoot"]=record["outputRoot"]
        item["outputAccess"]=record["outputAccess"]
        path=snapshot/f"assignments/{worker}.json"
        write(path,item)
        assignment_snaps.append({"assignment":worker,"path":path.relative_to(ROOT).as_posix(),"sha256":sha_file(path),"bytes":path.stat().st_size})
    m["assignmentSnapshots"]=assignment_snaps
    m["snapshotIndexPath"]=(snapshot/"snapshot-index.json").relative_to(ROOT).as_posix()
    m["workerToolSnapshots"]=[]
    tool_specs=[
        ("work/tools/run_t66_parallel_candidate.py",ROOT/"work/tools/run_t66_parallel_candidate.py","writer-owned runner frozen for wave-2"),
        ("work/tools/t66_parallel_protocol.py",ROOT/"work/tools/t66_parallel_protocol.py","writer-owned protocol frozen for wave-2"),
        ("work/tools/author_t66_family_motion.py",W1/"input-snapshot/files/work/tools/author_t66_family_motion.py","inherited immutable wave-1 authoring module"),
        ("work/tools/author_source_surface_motion.py",W1/"input-snapshot/files/work/tools/author_source_surface_motion.py","inherited immutable wave-1 source geometry module"),
        ("work/tools/verify_t66_glb_pose.py",W1/"input-snapshot/files/work/tools/verify_t66_glb_pose.py","inherited immutable wave-1 emitted-GLB pose verifier"),
        ("work/tools/validate_authored_surface_geometry.py",W1/"input-snapshot/files/work/tools/validate_authored_surface_geometry.py","inherited immutable wave-1 geometry QC"),
        ("work/tools/verify_t66_family_contacts.py",W1/"input-snapshot/files/work/tools/verify_t66_family_contacts.py","inherited immutable wave-1 contact QC"),
    ]
    tools_dir=snapshot/"tools"
    for rel,source,note in tool_specs:
        if source.is_symlink() or not source.is_file(): raise FileNotFoundError(source)
        dest=tools_dir/Path(rel).name
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,dest)
        m["workerToolSnapshots"].append({"modulePath":rel,"sourcePath":source.relative_to(ROOT).as_posix(),"snapshotPath":dest.relative_to(ROOT).as_posix(),"bytes":dest.stat().st_size,"sha256":sha_file(dest),"provenance":note})
    m["snapshotRoot"]=w1["snapshotRoot"]
    m["writerDryRun"]={"outputRoot":(W2/"writer-dry-run").relative_to(ROOT).as_posix(),"assignment":"writer-dry-run","sourceCandidateOnly":True}
    m["promptFiles"]=[]
    for worker,rel in (("D","work/plans/t66-parallel-completion-2026-10-03/07-worker-D-jaw-hyoid-pharynx.txt"),("E","work/plans/t66-parallel-completion-2026-10-03/08-worker-E-eye-face-tongue-pelvic.txt")):
        p=ROOT/rel
        m["promptFiles"].append({"assignment":worker,"path":rel,"sha256":sha_file(p),"bytes":p.stat().st_size,"launch":"manual_only_not_started_by_wave1_integration"})

    # Keep source-only and independent review/rights states explicit in the wave extension.
    m["wave2Authority"]={"sourceOnly":True,"publicRedistribution":"held","humanReview":"not_performed","canonicalBindingAdded":False,"targetBindingsAdded":False,"targetContextRefsAreNonAuthoritative":True}
    m["wave2Counts"]={"dWorkKeys":len(d_rows),"eWorkKeys":len(e_rows),"dSourceKeys":len(d_sources),"eSourceKeys":len(e_sources),"dBoneContextRows":len(d_bones),"eBoneContextRows":len(e_bones),"otherDeferredWorkKeys":len(rest),"wave1SourceResourceRefCount":len(w1["sourceResourceRefs"]),"wave1UniqueSourceHashCount":len(w1["sourceResourceHashesUnique"])}
    # Keep all output roots explicit; only D/E have write permission.
    m["assignments"]["A"]["outputAccess"]="read_only_carry_forward"
    m["assignments"]["B"]["outputAccess"]="read_only_carry_forward"
    m["assignments"]["C"]["outputAccess"]="read_only_carry_forward"
    m["assignments"]["F"]["outputAccess"]="read_only_carry_forward"
    for worker in ("A","B","C","D","E","F"):
        m["assignments"][worker]["outputRoot"]=(W2/"workers"/worker).relative_to(ROOT).as_posix()
    m["writerDryRun"]["outputRoot"]=(W2/"writer-dry-run").relative_to(ROOT).as_posix()
    m["sampleInputs"]=copy.deepcopy(w1["sampleInputs"])
    m["commonNoWritePaths"]=list(dict.fromkeys(m.get("commonNoWritePaths",[])+["atlas-data/overlays/za-local-integration.json","atlas-data/motion/motion-learning.json","work/EXECUTION.json","work/reports/T66.md","OpenSim_Models/","atlas-data/source-cache/"]))
    m["preservation"]=dict(m.get("preservation",{}),wave1ManifestAndInputsImmutable=True,onlyDAndEOutputWritable=True,denominatorsFixed=True,sourceOnlyRightsAndReviewUnchanged=True)
    # Write manifest only after all its declared snapshots exist.
    manifest_out=W2/"run-manifest.json"
    manifest_out.parent.mkdir(parents=True,exist_ok=True)
    write(manifest_out,m)
    snapshot_index={
        "schemaVersion":"t66-wave2-supplemental-snapshot-index-v1","runId":m["runId"],
        "wave1Base":{"runId":w1["runId"],"manifestPath":W1_MANIFEST.relative_to(ROOT).as_posix(),"rawSha256":EXPECTED_W1_SHA,"inputSnapshotRoot":w1["snapshotRoot"],"reusedInputCount":len(w1["inputs"]),"sourceResourceRefs":len(w1["sourceResourceRefs"]),"uniqueSourceResourceHashes":len(w1["sourceResourceHashesUnique"])},
        "wave2SnapshotRoot":snapshot.relative_to(ROOT).as_posix(),"workerOutputSchema":{"path":schema_ref["path"],"sha256":schema_ref["sha256"],"bytes":schema_ref["bytes"]},
        "workerToolSnapshots":m["workerToolSnapshots"],"controlSnapshots":controls,"assignmentSnapshots":assignment_snaps,
        "snapshotPolicy":"wave-2 stores only supplemental control/assignment/schema/runner inputs; immutable source/data bytes and 47 pinned input snapshots are reused from wave-1 without rewriting them",
    }
    write(snapshot/"snapshot-index.json",snapshot_index)
    print(json.dumps({"status":"wave2_manifest_frozen","runId":m["runId"],"manifest":manifest_out.relative_to(ROOT).as_posix(),"manifestSha256":sha_file(manifest_out),"d":len(d_rows),"e":len(e_rows),"deferredOther":len(rest),"sourceResourceRefs":len(w1["sourceResourceRefs"]),"uniqueSourceHashes":len(w1["sourceResourceHashesUnique"]),"snapshotIndex":(snapshot/"snapshot-index.json").relative_to(ROOT).as_posix()},ensure_ascii=False,indent=2))

if __name__=="__main__": main()
