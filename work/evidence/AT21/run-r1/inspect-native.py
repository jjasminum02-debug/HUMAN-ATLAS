"""Reuse AT20 native replay/intersection/figure audit in this versioned directory."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[4];side=sys.argv[1];assert side in ['right','left']
source=(R/'work/evidence/AT20/run-r1/inspect-boundary.py').read_text()
inputPath='atlas-data/acupoints/territories/AT20-r1/lung-forearm-right-boundary-r1.json' if side=='right' else 'work/evidence/AT21/run-r1/left-boundary-r1.json'
replacements={
 "atlas-data/acupoints/territories/AT20-r1/lung-forearm-right-boundary-r1.json":inputPath,
 "selected=np.all((angle[t]<=12)&(level[t]>=1)&(level[t]<=16),axis=1)":"selected=np.all("+('(angle[t]<=12)' if side=='right' else '((angle[t]>=28)|(angle[t]==0))')+"&(level[t]>=1)&(level[t]<=16),axis=1)",
 "c['side']=='right'":"c['side']=='"+side+"'",
 "c['code']+'-right'":"c['code']+'-"+side+"'",
 "row['side']!='right'":"row['side']!='"+side+"'",
 "['arm-right']":"['arm-"+side+"']",
 "'side':'right'":"'side':'"+side+"'",
 "'leftReflected':False":"'reflectionUsed':False",
 "surface-inspection-r1.json":"surface-inspection-"+side+"-r1.json",
 "boundary-native-three-views-r1":"boundary-native-"+side+"-three-views-r1",
 "LU right forearm:":"LU "+side+" forearm:",
 "Right lateral (-X)":"Right lateral (-X)" if side=='right' else "Left lateral (+X)",
 "source support65":"independent actual boundary support",
}
for a,b in replacements.items():
 assert a in source,a
 source=source.replace(a,b)
exec(compile(source,'AT20-reused-native-audit','exec'),globals())
