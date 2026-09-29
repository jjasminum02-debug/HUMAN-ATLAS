"""ZA adapter -> common compiler; no learner binding or source visibility changes."""
import json
from pathlib import Path
from pack import compile_dataset, digest
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'atlas-data/source-cache/datasets/za'
EVIDENCE=ROOT/'work/evidence/T98/astra-resolution-2026-09-29'
if __name__=='__main__':
    catalog=json.loads((EVIDENCE/'source-catalog.json').read_text())
    progress=json.loads((BASE/'progress.json').read_text())
    assert progress['fingerprint']==digest(Path(__file__).with_name('compile_za.py').read_bytes()+(EVIDENCE/'source-catalog.json').read_bytes()), 'stale adapter checkpoint'
    assert not progress['failures'] and progress['completed']==len(catalog['objects'])
    instances=[];resources={}
    for row in catalog['objects']:
        unit=json.loads((BASE/'units'/f'{row["sourceKey"]}.json').read_text())
        assert unit['fingerprint']==progress['fingerprint']
        for r in unit['lods'].values():resources[r['resource']]={**r,'path':str(BASE/r['path'])}
        instances.append({**row,**unit,'lods':{level:{k:v for k,v in r.items() if k!='path'} for level,r in unit['lods'].items()}})
    result=compile_dataset({'namespace':'za-c7010a9','revision':digest((Path(__file__).read_bytes()+Path(__file__).with_name('pack.py').read_bytes()+json.dumps(instances,sort_keys=True,separators=(',',':')).encode())), 'adapterRevision':progress['fingerprint'],'localOnly':True,'publicRedistribution':'held',
        'unit':'m','geometrySpace':'source_local','instanceMatrix':'source_world_then_axis_conversion_once',
        'frameContract':json.loads((EVIDENCE/'frame-contract.json').read_text()),
        'rightsScope':json.loads((EVIDENCE/'rights-scope.json').read_text()),
        'sourceHash':catalog['sourceHash'],'catalogHash':digest((EVIDENCE/'source-catalog.json').read_bytes()),
        'canonicalTargetCount':542,'regionMembershipCount':563,'regionCount':12,
        'targetOverlay':catalog['targetOverlay'],'exclusions':catalog['exclusions'],
        'muscleUniqueDenominator':None,'instances':instances,'resources':resources},BASE/'compiled')
    (ROOT/'work/evidence/T99/compile-summary.json').write_text(json.dumps({'metrics':result['metrics'],'budgetPass':result['budgetPass'],'progress':progress},indent=2)+'\n')
    print(json.dumps(result['metrics']), 'budgetPass',result['budgetPass'])
    if not result['budgetPass']: raise SystemExit('budget gate failed; preserve all objects, adjust same compiler')
