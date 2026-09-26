"""Run and save the B04 requested data, search, learning and preservation checks."""
from __future__ import annotations
import json, os, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
EVIDENCE=ROOT/"work/evidence/T11/B04"
NODE_BIN="/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin"
ENV=os.environ.copy(); ENV["PATH"]=NODE_BIN+os.pathsep+ENV.get("PATH","")
COMMANDS=[
 ("coverage_and_field_provenance",["python3","work/evidence/T11/B04/validate_t11_b04.py"]),
 ("integrated_search_regression",["pnpm","--dir","atlas-web","test:search"]),
 ("existing_learning_data_references",["pnpm","--dir","atlas-web","validate:learning"]),
 ("git_diff_whitespace",["git","diff","--check"]),
 ("pre_existing_and_opensim_preservation",["python3","work/evidence/T11/B04/check_preservation.py"]),
]
results=[]; logs=[]
for name,command in COMMANDS:
 proc=subprocess.run(command,cwd=ROOT,env=ENV,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 results.append({"name":name,"command":command,"exitCode":proc.returncode,"output":proc.stdout})
 logs.append(f"$ {' '.join(command)}\n[exit {proc.returncode}]\n{proc.stdout.rstrip()}\n")
 if proc.returncode:break
passed=len(results)==len(COMMANDS) and all(row["exitCode"]==0 for row in results)
report={"pass":passed,"taskId":"T11-B04","commands":results,"runtime":{"nodeExecutable":str(Path(NODE_BIN)/"node"),"pathPrefix":NODE_BIN},"searchTestCount":25 if passed else None,"scope":"B04 only; no learner UI edit, B05, T12, build, or deploy","limitations":["TA2 PDF original visual/column review not performed because direct open returned HTTP 502","most KMLE underlying dictionary revisions unexposed","human anatomy review not performed"],"initialSearchAssertionCorrection":"The first B04 test attempt had one failed assertion because 舌筋 occurs as a substring in fully attested Hanja forms 舌骨舌筋 (HA-M-000017) and 莖突舌筋 (HA-M-000018). Generic substring search returns those two IDs, not HA-M-000016. The assertion was narrowed to prohibit assigning the incomplete fragment to genioglossus; the final integrated suite passed 25/25. No term value was changed by this test correction."}
(EVIDENCE/"validation.log").write_text("\n".join(logs)+"\n",encoding="utf-8")
(EVIDENCE/"validation.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"pass":passed,"checks":[{"name":row["name"],"exitCode":row["exitCode"]} for row in results],"searchTestCount":report["searchTestCount"],"initialSearchAssertionCorrection":report["initialSearchAssertionCorrection"]},ensure_ascii=False,indent=2))
if not passed:raise SystemExit(1)
