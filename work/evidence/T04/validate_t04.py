#!/usr/bin/env python3
"""Structural/provenance validation for T04's partial TA2 catalog."""
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
CAT=ROOT/'atlas-data/catalog'

def load(name):
    return json.loads((CAT/name).read_text())

def main():
    scope=json.loads((ROOT/'atlas-data/manifests/scope.json').read_text())
    assets=json.loads((ROOT/'atlas-data/manifests/assets.json').read_text())
    ds=load('canonical-catalog.json'); tree=load('region-tree.json')
    xw=load('source-crosswalk.json'); status=load('catalog-status.json')
    concepts=ds['entities']['muscleConcepts']; terms=ds['entities']['terms']
    rows=xw['catalogItems']; ev={e['id'] for e in ds['entities']['evidence']}
    term_map={t['id']:t for t in terms}
    concept_map={c['id']:c for c in concepts}
    checks=[]
    def check(name, ok, detail):
        checks.append({'name':name,'passed':bool(ok),'detail':detail})
    scope_ids={r['id'] for r in scope['regions']}
    tree_ids={r['id'] for r in tree['regions']}
    dataset_region_ids={r['id'] for r in ds['entities']['regions']}
    check('all_18_t01_regions_in_tree', tree_ids==scope_ids and len(tree_ids)==18,
          f"scope={len(scope_ids)} tree={len(tree_ids)} missing={sorted(scope_ids-tree_ids)}")
    check('scope_tree_has_single_project_root', tree['root_id']=='HA-R-ROOT' and all(r.get('parentId')=='HA-R-ROOT' for r in tree['regions']),
          'T01 scope regions are direct children of the project root; no unsourced subregions were added.')
    check('t03_region_ids_resolve', scope_ids <= dataset_region_ids and 'HA-R-ROOT' in dataset_region_ids,
          f"T03 region entity count={len(dataset_region_ids)}")
    ids=[c['id'] for c in concepts]
    check('stable_ids_unique_and_namespaced', len(ids)==len(set(ids)) and all(re.fullmatch(r'HA-(?:M|G|P)-\d{6}',i) for i in ids),
          f"concepts={len(ids)}; IDs are opaque, unique, append-only project IDs.")
    valid_types={'individual_muscle','muscle_group','muscle_part','variant'}
    check('concept_types_and_counts', all(c['entityType'] in valid_types for c in concepts) and
          status['partialEntryCounts']=={
            'individualMuscles':sum(c['entityType']=='individual_muscle' for c in concepts),
            'groups':sum(c['entityType']=='muscle_group' for c in concepts),
            'parts':sum(c['entityType']=='muscle_part' for c in concepts),
            'variants':sum(c['entityType']=='variant' for c in concepts)},
          f"counts={status['partialEntryCounts']}; only individual_muscle enters the partial count.")
    parents={c['id']:c.get('parentId') for c in concepts}
    check('all_parent_concepts_resolve', all(p is None or p in concept_map for p in parents.values()),
          f"concept references checked={len(parents)}")
    check('every_catalog_item_has_exact_row_and_page', len(rows)==len(concepts) and
          all(r['stableConceptId'] in concept_map and isinstance(r['tableRow'],int) and isinstance(r['printedPage'],int) and r['sourceId']=='FIPAT_TA2' for r in rows),
          f"row crosswalks={len(rows)}")
    ref_by_id={c['id']:c['standardRefs'][0]['identifier'] for c in concepts}
    check('row_reference_matches_concept_standard_ref', all(ref_by_id[r['stableConceptId']]==f"row {r['tableRow']}; printed page {r['printedPage']}" for r in rows),
          'T03 StandardRef locators match the source crosswalk row/page for each item.')
    check('all_row_evidence_resolves', all(f"EV-TA2-P2-R{r['tableRow']}" in ev for r in rows),
          f"evidence records={len(ev)}; each source item points to a recorded TA2 row locator.")
    check('terms_are_traceable_or_explicitly_missing', all(
        t['conceptId'] in concept_map and ((t['text'] is not None and t['reviewState']=='needs_review' and t['evidenceIds'] and all(e in ev for e in t['evidenceIds'])) or
        (t['text'] is None and t.get('missingReason') and not t['evidenceIds'] and t['reviewState']=='held')) for t in terms),
        f"term records={len(terms)}; source observations are needs_review, Korean/Hanja entries are null with reasons.")
    check('no_review_or_claims_or_attachments', not ds['entities']['reviews'] and not ds['entities']['claims'] and not ds['entities']['attachments'] and
          not ds['entities']['spatialAnnotations'] and not ds['entities']['jointActions'] and not ds['entities']['assessments'],
          'No anatomy claims, attachments, spatial annotations, functions, assessments, or reviewer approvals were created.')
    check('whole_body_denominator_stays_unfrozen', status['catalogComplete'] is False and status['denominatorFrozen'] is False and
          status['wholeBodyIndividualMuscleCount'] is None and status['wholeBodyGate']=='blocked',
          'Partial source extraction is not represented as the whole-body denominator.')
    check('all_t02_pilot_concepts_have_stable_ids', len(status['pilotConceptIds'])==6 and
          all(i in concept_map for i in status['pilotConceptIds'].values()),
          json.dumps(status['pilotConceptIds'],ensure_ascii=False,sort_keys=True))
    maps=xw['bodyParts3dMappings']
    expected_fma={p['concept_id'] for p in assets['pilotMuscles']}
    mapped_fma={m['externalConceptId'] for m in maps}
    check('all_7_t02_fma_mesh_mappings_carried_forward', len(maps)==7 and mapped_fma==expected_fma,
          f"T02 FMA IDs={len(expected_fma)} mapped={len(mapped_fma)}")
    gastro=[m for m in maps if m['externalConceptId'] in {'FMA45957','FMA45960'}]
    check('gastrocnemius_head_meshes_map_to_distinct_parts', len(gastro)==2 and
          {m['stableConceptId'] for m in gastro}=={'HA-P-000001','HA-P-000002'} and
          xw['wholeGastrocnemiusMapping']['status'].startswith('no_whole_muscle_asset'),
          'Two right-side T02 head meshes stay on child part IDs; no whole-muscle mesh is asserted.')
    check('no_bilateral_duplicate_instances_or_right_left_catalog_labels', not ds['entities']['instances'] and
          all('right ' not in (r['latinTextObservation']+' '+r['englishTextObservation']).lower() and
              'left ' not in (r['latinTextObservation']+' '+r['englishTextObservation']).lower() for r in rows),
          'Canonical concepts are side-independent; T02 side-specific assets remain in the external crosswalk.')
    check('no_variants_fabricated', status['partialEntryCounts']['variants']==0 and
          any('variants=0' in p for p in status['reasons']) is False,
          'No variant was asserted; the gap queue explicitly says zero enumerated is not absence.')
    passed=all(c['passed'] for c in checks)
    output={'passed':passed,'checks':checks,'conceptCounts':status['partialEntryCounts'],
            'regionCount':len(scope_ids),'termCount':len(terms),'rowEvidenceCount':len(ev),
            'wholeBodyGate':status['wholeBodyGate']}
    path=ROOT/'work/evidence/T04/catalog-validation.json'
    path.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(output,ensure_ascii=False,indent=2))
    return 0 if passed else 1

if __name__=='__main__':
    sys.exit(main())
