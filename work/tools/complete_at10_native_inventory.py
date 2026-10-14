"""Supplement only missing native addresses; no source/old evidence writes.

Use the same source-bound AC1 reader with hash-checked detail GLBs and one world
matrix. Inventory membership is kind/default visibility, not English substrings.
"""
from pathlib import Path
import hashlib, importlib.util, json
import numpy as np
R=Path(__file__).resolve().parents[2];E=R/'work/evidence/AT10/2026-10-14-skin-fit-r5'
old=R/'work/evidence/AT10/2026-10-13-skin-fit-r1/native-surfaces-r1.json'
d=json.loads(old.read_text())
spec=importlib.util.spec_from_file_location('native',R/'work/evidence/AT8/2026-10-13-r1/native-reader.py')
n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n)
missing=[(k,row) for k,row in n.rows.items() if k not in d and row['kind'] in ['bone','muscle'] and row['defaultVisible']]
out={};records=[]
for key,row in missing:
    v,t=n.world(key)
    out[key]={'name':row['names']['en'],'side':row['side'],'v':v.tolist(),'t':t.tolist()}
    records.append({'sourceKey':key,'name':row['names']['en'],'side':row['side'],'kind':row['kind'],
        'reason':'default-visible native omitted by previous English substring selection',
        'vertices':len(v),'triangles':len(t),'worldBoundsM':[v.min(0).tolist(),v.max(0).tolist()],
        'topologyAndWorldPositionSha256':hashlib.sha256(v.astype('<f4').tobytes()+t.astype('<u4').tobytes()).hexdigest()})
supplement=E/'native-supplement-r1.json';assert not supplement.exists()
supplement.write_text(json.dumps(out,separators=(',',':')))
report={'oldReference':str(old.relative_to(R)),'oldReferenceSha256':hashlib.sha256(old.read_bytes()).hexdigest(),
    'oldObjects':len(d),'supplementObjects':len(out),'supplementTriangles':sum(len(x['t']) for x in out.values()),
    'newTotalObjects':len(d)+len(out),'allDefaultVisibleBoneMuscleKeysCovered':all(k in d or k in out for k,r in n.rows.items() if r['kind'] in ['bone','muscle'] and r['defaultVisible']),
    'supplementSha256':hashlib.sha256(supplement.read_bytes()).hexdigest(),'records':records,'readInputHashes':n.inputs,
    'oldHistoricalCrossingCountsRemainScopedTo648Surfaces':True,'sourceWrites':0,'downloadCount':0,
    'hiddenAccessoryCoverageIsNotClaimedExhaustive':True}
(E/'native-inventory-completion-r1.json').write_text(json.dumps(report,indent=2)+'\n')
print({k:v for k,v in report.items() if k not in ['records','readInputHashes']})
