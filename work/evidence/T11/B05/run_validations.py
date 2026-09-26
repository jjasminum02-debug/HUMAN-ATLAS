"""Run the requested B05 provenance, search, reference and preservation checks."""
from __future__ import annotations
import json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
EVIDENCE=ROOT/"work/evidence/T11/B05"
NODE_BIN="/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin"
ENV=os.environ.copy(); ENV["PATH"]=NODE_BIN+os.pathsep+ENV.get("PATH","")
COMMANDS=[
 ("coverage_and_field_provenance",["python3","work/evidence/T11/B05/validate_t11_b05.py"]),
 ("integrated_search_regression",["pnpm","--dir","atlas-web","test:search"]),
 ("existing_learning_data_references",["pnpm","--dir","atlas-web","validate:learning"]),
 ("git_diff_whitespace",["git","diff","--check"]),
 ("pre_existing_and_opensim_preservation",["python3","work/evidence/T11/B05/check_preservation.py"]),
]
results=[]; logs=[]
for name,command in COMMANDS:
 proc=subprocess.run(command,cwd=ROOT,env=ENV,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 results.append({"name":name,"command":command,"exitCode":proc.returncode,"output":proc.stdout})
 logs.append(f"$ {' '.join(command)}\n[exit {proc.returncode}]\n{proc.stdout.rstrip()}\n")
 if proc.returncode:break
passed=len(results)==len(COMMANDS) and all(row["exitCode"]==0 for row in results)
search_result=next((row for row in results if row["name"]=="integrated_search_regression"),None)
search_count=None
if search_result and search_result["exitCode"]==0:
 import re
 m=re.search(r"(?:#|ℹ) tests\s+(\d+)",search_result["output"])
 if m: search_count=int(m.group(1))
report={"pass":passed,"taskId":"T11-B05","commands":results,"runtime":{"nodeExecutable":str(Path(NODE_BIN)/"node"),"pathPrefix":NODE_BIN},"searchTestCount":search_count,"scope":"B05 only; no learner UI edit, B06, T12, build, or deploy","limitations":["FIPAT library URL returned HTTP 502; Dalhousie-hosted official TA2 PDF opened directly and relevant text rows/table headings were read, but visual page screenshots were not inspected","KMLE underlying dictionary editions/revisions remain unexposed for most terms; one KMLE HTML page was opened for deltoid and CancerWEB date was visible","human anatomy review was not performed"],"preservedPriorTerm":{"id":"HA-M-000030","existingEnglish":"Deltoid","preservedAsAlias":"Deltoid","newTa2English":"Deltoid muscle","newLatin":"Musculus deltoideus"}}
(EVIDENCE/"validation.log").write_text("\n".join(logs)+"\n",encoding="utf-8")
(EVIDENCE/"validation.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"pass":passed,"checks":[{"name":row["name"],"exitCode":row["exitCode"]} for row in results],"searchTestCount":search_count,"scope":report["scope"]},ensure_ascii=False,indent=2))
if not passed:raise SystemExit(1)
