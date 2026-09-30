#!/usr/bin/env python3
"""Resolve only pending target representations from pinned object and typed child proofs.
Never alters existing exact-term links, frozen inputs, canonical bindings or rights.
"""
import argparse, hashlib, json, re, subprocess
from collections import Counter, defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'work/evidence/T100/target-scope-resolution-2026-09-30'
OVERLAY = ROOT/'atlas-data/overlays/za-local-integration.json'
SCOPE = ROOT/'atlas-data/catalog/target-scope-t96.json'
CATALOG = ROOT/'work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json'
COMPILED = ROOT/'atlas-data/source-cache/datasets/za/compiled/manifest.json'
PRIOR = ROOT/'work/evidence/T100/target-representation-continuation-2026-09-30'
SCOPE_ID='fipat-ta2-t96-full-target-catalog'
SOURCE_ID='za-t99-frozen-source-objects'
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def key(seed): return 'LC-'+hashlib.sha256(seed.encode()).hexdigest()[:20]
def norm(v): return ''.join(c for c in v.casefold() if c.isalnum())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
 baseline=read(OUT/'start-baseline.json')
 before_bytes=subprocess.check_output(['git','show',baseline['head']+':atlas-data/overlays/za-local-integration.json'],cwd=ROOT)
 assert hashlib.sha256(before_bytes).hexdigest()==baseline['inputSha256']['atlas-data/overlays/za-local-integration.json']
 before=json.loads(before_bytes);o=json.loads(json.dumps(before));scope=read(SCOPE);s={t['id']:t for t in scope['targets']}
 base_matrix={t['targetId']:t for t in read(ROOT/'work/evidence/T100/target-representation-2026-09-30/target-representation-matrix.json')['targets']}
 prior=read(PRIOR/'target-representation-continuation.json');pending={t['targetId']:t for t in prior['remainingTargets']}
 cat=read(CATALOG);src={r['sourceKey']:r for r in cat['objects']};c=read(COMPILED);mesh={r['sourceKey']:r for r in c['instances']}
 assert sha(SCOPE)==read(OUT/'start-baseline.json')['inputSha256']['atlas-data/catalog/target-scope-t96.json']
 assert len(s)==542 and sum(len(t['regionIds']) for t in s.values())==563 and o['scope']=={'targets':542,'memberships':563,'regions':12}
 index=defaultdict(set)
 for tid,t in s.items():
  for v in [t['term']['english'],t['term']['latin'],*sum(t['term']['sourceSynonyms'].values(),[])]:index[norm(v)].add(tid)
 support=ROOT/'work/evidence/T78/reference/ta2-scope.json'
 assert sha(support)==scope['source']['snapshotSha256']
 full=read(support);context={t['id']:t for t in full};context_index=defaultdict(set)
 for t in full:
  for v in [t['term'].get('en',''),t['term'].get('la',''),*sum(t.get('synonyms',{}).values(),[])]:context_index[norm(v)].add(t['id'])
 plan=[];excluded=[]
 def valid(row):
  source=src[row['sourceKey']];instance=mesh[row['sourceKey']]
  return (row['localDisplayEligible'] and row['inspectionEligible'] and not row['hardHoldReasons']
   and source['name']==instance['name']==row['sourceName']
   and source['evaluatedGeometrySha256']==instance['evaluatedGeometrySha256']
   and source['sourceLocator']['sourceFileSha256']==o['sourceHash']==cat['sourceHash']==c['sourceHash']
   and (not re.search(r'\.[lr]$',row['sourceName']) or row['side']==('left' if row['sourceName'][-1]=='l' else 'right')))
 def add(row,tid,kind,member,rule,ids):
  assert tid in pending and row['kind'] in s[tid]['semanticKind'] and set(row['regionIds'])&set(s[tid]['regionIds'])
  if s[tid]['sourceCardinality']['explicitSourceSide'] not in [None,row['side']]:return
  link={'conceptKey':key('|'.join([kind,tid,member or '',row['kind']])), 'relationKind':kind,'targetIds':[tid],'memberCode':member,'targetTermMatches':[], 'matchRule':rule,'evidenceIds':sorted({SCOPE_ID,SOURCE_ID,*ids}),'identityStatus':'evidence_backed','humanReview':'not_performed'}
  if not any(x==link for x in row.get('learnerConceptLinks',[])):
   row.setdefault('learnerConceptLinks',[]).append(link)
   plan.append({'sourceKey':row['sourceKey'],'sourceName':row['sourceName'],'side':row['side'],'targetId':tid,'link':link,'geometrySha256':src[row['sourceKey']]['evaluatedGeometrySha256']})
 # Retain all previous links; only new qualified, corrected, or bounded series proofs.
 for row in o['objects']:
  if not valid(row):continue
  for tid,t in pending.items():
   target=s[tid]
   if row['kind'] not in target['semanticKind'] or not set(target['regionIds'])&set(row['regionIds']):continue
   rels=[r for r in row.get('targetRelationEvidence',[]) if r['targetId']==tid and r.get('relationKind')=='qualified_target_synonym']
   if any(r.get('matchedTargetSynonym') in sum(target['term']['sourceSynonyms'].values(),[]) and r['sourceSide']==row['side'] and r['evaluatedGeometrySha256']==src[row['sourceKey']]['evaluatedGeometrySha256'] for r in rels):
    add(row,tid,'verified_source_crosswalk',None,'exact frozen target representation: qualified_synonym',sum([r['matchEvidenceSourceIds'] for r in rels],[]))
   elif row.get('surfaceAssignmentCorrection') and row['targetId']==tid and norm(row['names']['en'])==norm(target['term']['english']):
    assert row['surfaceAssignmentCorrection']['evaluatedGeometrySha256']==src[row['sourceKey']]['evaluatedGeometrySha256']
    add(row,tid,'verified_source_crosswalk',None,'exact frozen target representation: corrected_surface',[])
   elif not row.get('surfaceAssignmentCorrection') and row.get('targetId')==tid and index[norm(re.sub(r'\.[lr]$','',row['sourceName']))]=={tid} and any(l['relationKind']=='verified_class_member' and any(int(i[4:]) in target['sourceAncestryIds'][1:] for i in l['targetIds']) for l in row.get('learnerConceptLinks',[])):
    add(row,tid,'verified_source_crosswalk',None,'exact frozen target representation: direct_term_with_class_context',[])
   if target['semanticKind']=='bone_series':
    ranges=[re.fullmatch(r'ribs (\d+)-(\d+)',v) for v in sum(target['term']['sourceSynonyms'].values(),[])];ranges=[r for r in ranges if r]
    for l in list(row.get('learnerConceptLinks',[])):
     member=l.get('memberCode');match=re.fullmatch(r'rib:(\d+)',member or '')
     if l['relationKind']=='verified_class_member' and match and any(int(r[1])<=int(match[1])<=int(r[2]) for r in ranges):
      add(row,tid,'verified_source_crosswalk',member,'exact frozen target representation: series_member',l['evidenceIds'])
 # Frozen non-target parts can represent a member of a target without entering the 542 denominator.
 for row in o['objects']:
  if not valid(row) or row.get('surfaceAssignmentCorrection'):continue
  hits=context_index[norm(re.sub(r'\.[lr]$','',row['sourceName']))]
  if len(hits)!=1:continue
  child=next(iter(hits))
  if f'TA2:{child}' in s:continue
  ancestry=[];i=context[child].get('parent')
  while i in context and i not in ancestry:
   ancestry.append(i);i=context[i].get('parent')
  for tid in pending:
   if int(tid[4:]) in ancestry and tid in row['targetIds'] and row['kind'] in s[tid]['semanticKind'] and set(row['regionIds'])&set(s[tid]['regionIds']):
    add(row,tid,'verified_source_crosswalk',f'TA2:{child}','exact frozen target representation: context_part_member',[])
 # Extend parent routes from ALL already validated children, including early exact links
 # whose pinned source proof is supplied here rather than embedded in the lexical record.
 for row in o['objects']:
  if not valid(row):continue
  for proof in list(row.get('learnerConceptLinks',[])):
   if proof['relationKind'] not in ['normalized_exact_target_term','verified_class_member','verified_source_crosswalk'] or proof['identityStatus']!='evidence_backed':continue
   for child_id in proof['targetIds']:
    child=s[child_id]
    for i in child['sourceAncestryIds'][1:]:
     tid=f'TA2:{i}'
     if tid not in pending:continue
     if row['kind'] not in s[tid]['semanticKind'] or not set(s[tid]['regionIds'])&set(row['regionIds']):continue
     if child['sourceCardinality']['explicitSourceSide'] not in [None,row['side']]:continue
     # Same child may have multiple members on a side: do not issue an ambiguous handle.
     peers=[r for r in o['objects'] if valid(r) and r['side']==row['side'] and any(l['relationKind'] in ['normalized_exact_target_term','verified_class_member','verified_source_crosswalk'] and l['identityStatus']=='evidence_backed' and child_id in l['targetIds'] for l in r.get('learnerConceptLinks',[]))]
     if len(peers)!=1:
      excluded.append({'targetId':tid,'childTargetId':child_id,'sourceKey':row['sourceKey'],'reason':'multiple_child_surfaces_on_same_side; retain individual member proof only'});continue
     add(row,tid,'verified_taxonomy_member',child_id,'exact frozen T96 sourceAncestryIds parent membership from an identity-backed child member; one selectable source member only; not a completeness claim',proof['evidenceIds'])
 # Crosscheck existing relationship preservation and no non-link changes.
 current={r['sourceKey']:r for r in o['objects']};b={r['sourceKey']:r for r in before['objects']}
 for sk,r in b.items():
  assert {k:v for k,v in r.items() if k!='learnerConceptLinks'}=={k:v for k,v in current[sk].items() if k!='learnerConceptLinks'}
  assert all(l in current[sk].get('learnerConceptLinks',[]) for l in r.get('learnerConceptLinks',[]))
 def handles(tid,region=None):
  return [{'sourceKey':r['sourceKey'],'sourceName':r['sourceName'],'side':r['side'],'conceptKey':l['conceptKey'],'relationKind':l['relationKind'],'memberCode':l['memberCode']} for r in o['objects'] if valid(r) and (region is None or region in r['regionIds']) for l in r.get('learnerConceptLinks',[]) if tid in l['targetIds'] and l['identityStatus']=='evidence_backed' and l['conceptKey']]
 matrix=[];memberships=[];resolved=[]
 for tid,t in s.items():
  h=handles(tid);matrix.append({'targetId':tid,'english':t['term']['english'],'semanticKind':t['semanticKind'],'regionIds':t['regionIds'],'routes':h,'coverageCompleteness':'not_asserted; partial members remain distinct from full extent','actualVisualQA':'pending'})
  if tid in pending:
   old=pending[tid]; candidates=[]
   flags=t['sourceFlags'];explicit_side=t['sourceCardinality']['explicitSourceSide']
   limitation=('variant_specific_source_member_not_established' if flags.get('inconstant') else 'declared_target_side_not_separated_from_parent_surface' if explicit_side else 'parent_or_whole_surface_not_an_exact_target_part' if t['semanticKind']=='muscle_part' else 'group_or_repeated_family_extent_not_established' if t['semanticKind'] in ['bone_group','muscle_group','repeated_muscle_family'] else 'exact_target_identity_or_segment_not_established')
   for r in o['objects']:
    if tid==r.get('targetId') or tid in r.get('targetIds',[]) or r['sourceKey'] in {c['sourceKey'] for c in base_matrix[tid]['candidateSurfaces']}:
     source=src[r['sourceKey']]; candidates.append({'sourceKey':r['sourceKey'],'name':r['sourceName'],'side':r['side'],'eligible':r['localDisplayEligible'],'sourceParent':source['parent'],'sourceCollections':source['collections'],'sameSourceCompiledHash':source['evaluatedGeometrySha256']==mesh[r['sourceKey']]['evaluatedGeometrySha256'],'existingDirectTargetId':r.get('targetId'),'declaredTargetIds':r['targetIds'],'sourceLabelSide':source['sourceLabelSide'],'representationCorrection':r.get('surfaceAssignmentCorrection')})
   resolved.append({'targetId':tid,'english':t['term']['english'],'semanticKind':t['semanticKind'],'baselineDisposition':old['baselineDisposition'],'frozenAncestryIds':t['sourceAncestryIds'],'explicitTargetSide':t['sourceCardinality']['explicitSourceSide'],'status':'exact_member_routes_available_extent_not_asserted' if h else 'unresolved','routes':h,'candidateObjects':candidates,'targetScopeFlags':flags,'unresolvedReasonCategory':None if h else limitation,'requiredEvidence':[] if h else ['exact target or bounded part/member correspondence with pinned source object', 'declared laterality or explicit side split; do not infer from parent', 'real localized browser highlight and part/group extent QA'],'reason': 'typed per-member proof verified' if h else ('no pinned target crosswalk; no source-wide absence claim' if not candidates else 'candidate ancestor/parent or whole-surface does not establish exact target part/group/side extent'),'confirmedGeometryAbsence':False})
  for region in t['regionIds']:
   hh=handles(tid,region); unique={h['sourceKey']:h for h in hh}
   for h in unique.values():
    matches=[r for r in o['objects'] if r['localDisplayEligible'] and r['side']==h['side'] and any(l['conceptKey']==h['conceptKey'] for l in r.get('learnerConceptLinks',[]))]
    assert len(matches)==1 and matches[0]['sourceKey']==h['sourceKey']
   memberships.append({'targetId':tid,'regionId':region,'routes':list(unique.values()),'status':'exact_member_route' if hh else 'no_exact_member_route','visualStatus':'pending'})
 unresolved=[r for r in resolved if r['status']=='unresolved']
 summary={'taskId':'T100','nextUnit':'resolve-target-representation-and-final-scene-qa','acceptance':'partial','baselinePendingTargets':166,'resolvedTargets':166-len(unresolved),'remainingTargets':len(unresolved),'remainingByPriorClass':dict(Counter(r['baselineDisposition'] for r in unresolved)),'fixedDenominators':prior['fixedDenominators'],'selectableMemberships':sum(bool(r['routes']) for r in memberships),'unselectableMemberships':sum(not r['routes'] for r in memberships),'routeFailures':0,'termEvidenceGaps':75,'wholeBodyVisualQA':'incomplete','historical163':prior['historicalCandidateFree163'],'addedLinks':len(plan),'addedByKind':dict(Counter(r['link']['relationKind'] for r in plan)),'newHaBindings':0,'newGeometry':0}
 o['revision']+='-T100-target-scope-resolution-2026-09-30-v1'
 if args.check:
  assert o==read(OVERLAY),'current overlay differs from reproducible pinned representation plan';print(json.dumps(summary,ensure_ascii=False));return
 write(OVERLAY,o)
 write(OUT/'link-delta.json',{'entries':plan,'excluded':excluded,'inputHashes':{str(p.relative_to(ROOT)):sha(p) for p in [SCOPE,CATALOG,COMPILED,support]},'outputOverlaySha256':sha(OVERLAY)})
 write(OUT/'representation-scope-audit.json',{'summary':summary,'initial166':resolved,'remainingTargets':unresolved})
 write(OUT/'selection-visual-qa-ledger.json',{'denominators':{'targets':542,'memberships':563,'regions':12},'targets':matrix,'memberships':memberships,'claimBoundary':'Data routes are not browser visual passes. Local surface and parent/group total extent remain independent.'})
 write(OUT/'progress.json',summary);print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
