"""Read cached metadata and exact runtime IDs; never resolve canonical anatomy by substring."""
import csv, hashlib, json
from pathlib import Path
from collections import defaultdict
R=Path(__file__).resolve().parents[3]
E=R/'work/evidence/T77'
path=R/'atlas-data/source-cache/bodyparts3d-r4/converted/t77/manifest.json'
m=json.loads(path.read_text());assets={a['id']:a for c in m['chunks'] for a in c['assets']}
meta=R/'atlas-data/source-cache/bodyparts3d-r4/metadata/isa_element_parts.txt'
rows=list(csv.DictReader(meta.open(),delimiter='\t'))
names=defaultdict(list)
for row in rows:
 names[row['element file id']].append({'sourceConceptId':row['concept id'],'sourceName':row['name']})
queries=json.loads((R/'work/evidence/2026-09-28-full-muscle-order/source-observations.json').read_text())['queries']
result=[]
for query in queries:
 q=query['query'];ids=sorted({r['element file id'] for r in rows if q.lower() in r['name'].lower()})
 result.append({'query':q,'method':'substring discovery only; matches may include non-muscle structures; no match is not proof of absence','metadataCandidateIds':ids,'present':[i for i in ids if i in assets],'missingFromRuntime':[i for i in ids if i not in assets],'defaultVisible':[i for i in ids if i in assets and assets[i]['defaultVisible']],'heldHidden':[i for i in ids if i in assets and not assets[i]['defaultVisible']],'learnerLinked':[i for i in ids if i in assets and assets[i]['stableIds']]})
items=[]
for id,a in sorted(assets.items()):
 items.append({'sourceElementId':id,'sourceNamesNotCanonical':names[id],'package':a['sourcePackage'],'geometry':'present','localVisibility':'default_visible' if a['defaultVisible'] else 'held_hidden','binding':a['pickState'],'stableIds':a['stableIds'],'regions':a['regions'],'layer':a['layer'],'sourceSha256':a['sourceSha256'],'holdReasons':a['holdReasons'],'publicRedistribution':a['publicRedistribution'],'humanReviewed':a['humanReviewed'],'viewOcclusion':'camera_dependent_not_measured_per_surface','userLayerOff':'user_state_not_geometry_absence'})
armids=['FJ1512','FJ1512M','FJ1478','FJ1478M','FJ1479','FJ1479M','FJ1480','FJ1480M','FJ1477','FJ1477M']
assert all(i not in assets for i in armids)
out={'runtimeManifestSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'metadataSha256':hashlib.sha256(meta.read_bytes()).hexdigest(),'wholeBodyDenominator':None,'notCompleteAnatomyInventory':True,'items':items,'namedQueries':result,'bicepsTricepsMissingExactIds':armids,'latissimus':{'state':'missing','decision':'T94:no_exact_source_found','geometry':None,'binding':None,'futureImplementationRequested':True},'handoff':'T78: resolve source concepts, side/part and independent anatomy inventory; freeze all bounded acquisition/binding batches before T80. Latissimus remains mandatory, not removed from denominator.'}
(E/'current-inventory.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'runtimeIds':len(items),'namedQueries':len(result),'armMissing':len(armids),'wholeBodyDenominator':None}))
