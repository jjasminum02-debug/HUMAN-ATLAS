"""Current T100 decisions validate independently of historical not-approved-by-task flags."""
import hashlib,json,subprocess
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).parent
read=lambda p:json.loads((ROOT/p).read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=read('atlas-data/overlays/za-local-integration.json');source=read('work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json');frozen=read('atlas-data/source-cache/datasets/za/compiled/manifest.json');scope=read('atlas-data/catalog/target-scope-t96.json')
assert len(a['objects'])==len(source['objects'])==len(frozen['instances'])==960
assert a['datasetRevision']==frozen['revision']
assert a['policy']['rightsEvidenceSha256']==sha(ROOT/a['policy']['rightsEvidence'])
assert len(scope['targets'])==542 and sum(len(t['regionIds'])for t in scope['targets'])==563
assert all(not x['defaultLearnerVisible'] and x['canonicalConceptId'] is None and x['appDisplayRights']=='held_not_approved_by_this_task' for x in frozen['instances'])
sourceBy={x['sourceKey']:x for x in source['objects']};byTarget={t['id']:t for t in scope['targets']}
eligible=[r for r in a['objects']if r['localDisplayEligible']]
for row in a['objects']:
 original=sourceBy[row['sourceKey']]
 assert row['sourceName']==original['name'] and row['sourceHiddenStatePreserved']==original['sourceHiddenStatePreserved']
 assert row['humanReview']=='not_performed' and row['publicRedistribution']=='held'
 if row['localDisplayEligible']:assert row['localUseRights']=='supported_local_prototype' and not row['hardHoldReasons'] and not row['sourceHiddenStatePreserved']['hideViewport']
 if row['haConceptId']:assert row['semanticReview'].startswith('ai_crosschecked_') and row['targetId'] in byTarget
before={p:sha(ROOT/p)for p in ['atlas-data/overlays/za-local-integration.json',str((OUT/'crosswalk-audit.json').relative_to(ROOT))]}
subprocess.run(['python3',str(OUT/'build_integration.py')],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
assert before=={p:sha(ROOT/p)for p in before}
family=defaultdict(list)
for row in eligible:
 if row['side'] in ['left','right']:family[row['sourceName'][:-2]].append(row['side'])
audit=read(str((OUT/'crosswalk-audit.json').relative_to(ROOT)))
covered={r['targetId']for r in audit['coverage']if r['sourceKeys']};remaining=[]
for row in audit['coverage']:
 if row['sourceKeys']:continue
 descendants=[tid for tid in covered if row['targetId'] in ['TA2:'+str(x)for x in byTarget[tid]['sourceAncestryIds']]]
 remaining.append({**row,'coveredDescendantTargets':descendants,'resolutionClass':'optional_variant' if row['optionalVariant'] else 'part_or_group_resolution' if descendants else 'unresolved_identity_or_missing_surface','warning':'No name match is not proof of anatomical absence; review synonyms/parts before acquiring geometry.'})
(OUT/'remaining-targets.json').write_text(json.dumps({'targets':542,'sourceTaxonomyCandidateTargets':len(covered),'unresolved':remaining},ensure_ascii=False,indent=2)+'\n')
result={'sourceObjects':960,'originalSourceKinds':dict(Counter(r['kind']for r in source['objects'])),'displayedObjects':len(eligible),'displayKinds':dict(Counter(r['kind']for r in eligible)),'retainedNotDisplayed':960-len(eligible),'sourceTaxonomyCandidateTargets':len(covered),'unresolvedTargets':len(remaining),'threeNameSurfaceInstances':sum(bool(r['names']['koModern']and r['names']['koTraditional'])for r in eligible),'boundSurfaceInstances':sum(bool(r['haConceptId'])for r in eligible),'boundHAConcepts':len(set(r['haConceptId']for r in eligible if r['haConceptId'])),'unpairedNamedSourceInstances':{k:v for k,v in family.items()if len(v)!=2},'reproduction':'byte_identical','historicalCompilerPolicy':'unchanged','humanReview':'not_performed','publicRedistribution':'held','localDisplayDecision':'supported_local_prototype','G1Complete':False}
(OUT/'current-metrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
