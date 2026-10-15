"""Read-only cross-check of version tags, actual hashes and independent raw counts."""
from pathlib import Path
import json,hashlib,numpy as np
R=Path.cwd();E=R/'work/evidence/AT10/2026-10-15-f3-head-r1';A=R/'atlas-data/anatomy/skin/at10-f3-head-r1';load=lambda p:json.loads(p.read_text())
for rev in ['f3c11','f3c12']:
 sha=hashlib.sha256((A/f'skin-candidate-{rev}.glb').read_bytes()).hexdigest();q=load(E/f'scoped-checks-{rev}.json');raw=load(E/f'candidates/fit-{rev}-intersections.json');field=load(E/f'field-preservation-{rev}.json');rep=load(E/f'reproduction-{rev}.json');loader=load(E/f'loader-validation-{rev}.json');face=load(E/f'native-face-relationship-{rev}.json')
 assert q['revision']==raw['revision']==field['revision']==face['revision']==rev
 assert q['emittedGlbSha256']==raw['emittedGlbSha256']==field['emittedGlbSha256']==rep['sha256']==loader['glbSha256']==face['emittedHash']==sha
 assert not q['acceptancePassed'] and not q['learnerEligible'] and not q['geometryAccepted'] and not q['appearanceAccepted']
 assert q['wholeRawNativeCrossingTriangles']==raw['crossingSkinTriangles'];assert q['wholeRawSelfCrossingPairs']==raw['nonAdjacentSelfCrossingPairs'];assert field['outsideF3PositionsExact']==8866
 if rev=='f3c11':
  assert q['localRawNativeCrossingTriangles']==1703 and q['localSelfCrossingPairs']==0
  m=load(E/'manifest.json');assert m['sha256']==sha and m['reviewCandidate']==rev and m['rawLocalNativeTriangles']==1703
  assert load(A/f'material-{rev}.json')['geometrySha256']==sha and load(E/f'uv-binding-{rev}.json')['geometrySha256']==sha
 decision=load(E/'candidate-decision.json');assert decision['reviewCandidate']=='f3c11' and decision['latestAttempt']=='f3c12' and not decision['latestAttemptAccepted']
print('PASS: C11 review and C12 rejection have distinct, actual GLB-bound QA and counts; no acceptance or learner promotion.')
