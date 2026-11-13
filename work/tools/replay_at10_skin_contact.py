"""Reproduce preserved local units from their frozen addressed numeric recipe.

No optimizer or final target coordinates are read. This rebuilds from the r22
source/canonical topology, original numeric initial fields and accepted increments.
"""
from pathlib import Path
import argparse, json, hashlib
import numpy as np
R=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--out',required=True);p.add_argument('--revisions',nargs='+',required=True);a=p.parse_args()
E=R/a.evidence;O=Path(a.out);(O/'candidates').mkdir(parents=True,exist_ok=True)
load=lambda p:json.loads(p.read_text())
base=R/'work/evidence/AT10/2026-10-13-skin-fit-r2/candidates/fit-r22.json'
d=load(base);v=np.array(d['positions']);fields=load(E/'initial-hand-fields-r31.json')
checks=[]
for revision in a.revisions:
    record=load(E/f'contact-fit-{revision}.json');unit=record['sourceUnit'];ids=np.array(unit['sourceVertices']);roots=np.array(unit['sharedBoundaryVertices'])
    initial=next(x for x in fields['patches'] if x['patch']==unit.get('unit','hand')+'-'+unit['side'])
    old=v.copy();v[ids]=np.array(initial['initialUnitPositionsM']);v[roots]=old[roots]
    for stage in record['steps']:
        delta=v[:,None]-np.array(stage['fieldCentersM'])[None]
        phi=np.exp(-np.einsum('qnk,qnk->qn',delta,delta)/(2*np.array(stage['sigmaM'])**2))
        change=phi@np.array(stage['rawFieldCoefficients'])
        v[ids]+=change[ids];v[roots]=old[roots]
    checks.append({'revision':revision,'unit':initial['patch'],'fieldStages':len(record['steps']),'outsideUnitByteExact':np.array_equal(v[~np.isin(np.arange(len(v)),ids)],old[~np.isin(np.arange(len(v)),ids)])})
    d['positions']=v.tolist();d['candidateRevision']=revision;d['fitAcceptancePassed']=False;d['learnerEligible']=False
    path=O/f'candidates/fit-{revision}.json';assert not path.exists();path.write_text(json.dumps(d,separators=(',',':')))
(O/'replay.json').write_text(json.dumps({'sourceRecipe':str(E/'initial-hand-fields-r31.json'),'baselineCandidateSha256':hashlib.sha256(base.read_bytes()).hexdigest(),'units':checks,'targetPositionCoordinatesRead':False,'approval':False},indent=2)+'\n')
print(checks)
