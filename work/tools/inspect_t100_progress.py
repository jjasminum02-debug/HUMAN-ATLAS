#!/usr/bin/env python3
"""Bounded T100 inspection and action planning; never rewrites product data.

Keep the frozen nomenclature denominator, selectable routes, display names,
direct citations and visual acceptance separate. Default output is a summary,
not the multi-megabyte historical ledgers.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
RUN = Path('work/evidence/T100/parallel-resolution-2026-09-30')
OUT = Path('work/evidence/T100/closure-audit-2026-09-30')


def read(path):
    return json.loads((ROOT / path).read_text())


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def term_key(value):
    # Candidate lookup only: terminal class word and explicit side do not
    # establish a project crosswalk or completeness.
    value = re.sub(r'^(?:left|right)\s+', '', value.lower().strip())
    value = re.sub(r'\s+muscle$', '', value)
    return ''.join(c for c in value if c.isalnum())


def build(baseline_path):
    baseline = read(baseline_path)
    overlay_path = Path('atlas-data/overlays/za-local-integration.json')
    if sha(overlay_path) != baseline['overlay']['sha256']:
        raise SystemExit('QA overlay changed: inspect the new authoritative baseline; do not reuse stale evidence.')
    overlay = read(overlay_path)
    scope = read('atlas-data/catalog/target-scope-t96.json')
    targets = {r['id']: r for r in scope['targets']}
    assert len(targets) == 542 and sum(len(r['regionIds']) for r in targets.values()) == 563
    routes = baseline['routeCoverage']['memberships']
    assert len(routes) == 563
    missing = baseline['routeCoverage']['targetIdsWithoutPaths']
    audit = read('work/evidence/T100/target-scope-resolution-2026-09-30/representation-scope-audit.json')
    old_reasons = {r['targetId']: r['unresolvedReasonCategory'] for r in audit['remainingTargets']}
    bp_path = Path('atlas-data/manifests/bodyparts3d-r4-source-manifest-t51.json')
    bp = read(bp_path)
    registry_path = Path('atlas-data/source-cache/datasets/bp3d/registry.json')
    registry = read(registry_path)
    assets = {a['id']: (c, a) for c in registry['manifest']['chunks'] for a in c['assets']}
    files = {f['id']: f for f in registry['files']}
    index = defaultdict(list)
    for concept in bp['sourceConcepts']:
        index[term_key(concept['sourceNameEnglish'])].append(concept)
    rows = []
    for tid in missing:
        target = targets[tid]
        values = [target['term']['english'], *target['term']['sourceSynonyms'].get('en', [])]
        concepts = {c['sourceFmaConceptId']: c for v in values for c in index[term_key(v)]}
        candidates = []
        for concept in concepts.values():
            cached = []
            for fid in concept['elementFileIds']:
                if fid not in assets:
                    continue
                chunk, asset = assets[fid]
                file = files.get(chunk['id'])
                exists = bool(file and Path(file['path']).is_file())
                cached.append({'elementFileId': fid, 'nodeId': asset['nodeId'],
                               'side': asset['side'], 'regions': asset['regions'],
                               'holdReasons': asset['holdReasons'],
                               'localDisplayState': asset.get('localDisplay', {}).get('state'),
                               'chunkId': chunk['id'], 'chunkSha256': chunk['sha256'],
                               'chunkPath': file['path'] if file else None,
                               'chunkExists': exists,
                               'sourceSha256': asset['sourceSha256']})
            candidates.append({'sourceFmaConceptId': concept['sourceFmaConceptId'],
                               'sourceName': concept['sourceNameEnglish'],
                               'elementFileIds': concept['elementFileIds'], 'cachedAssets': cached})
        cached_present = any(a['chunkExists'] for c in candidates for a in c['cachedAssets'])
        reason = old_reasons.get(tid, 'held_source_pair_side_conflict')
        action = ('review_cached_cross_dataset_correspondence_and_frame' if cached_present else
                  'inspect_source_part_segmentation_or_acquire_exact_part' if reason == 'parent_or_whole_surface_not_an_exact_target_part' else
                  'establish_explicit_side_or_acquire_side_specific_surface' if reason == 'declared_target_side_not_separated_from_parent_surface' else
                  'establish_group_membership_and_extent' if reason == 'group_or_repeated_family_extent_not_established' else
                  'seek_variant_specific_source_evidence' if target['sourceFlags'].get('inconstant') else
                  'acquire_or_establish_exact_source_correspondence')
        rows.append({'targetId': tid, 'english': target['term']['english'],
                     'semanticKind': target['semanticKind'], 'primaryOwner': target['primaryOwner'],
                     'regionIds': target['regionIds'], 'inconstant': bool(target['sourceFlags'].get('inconstant')),
                     'reasonCategory': reason, 'nextAction': action, 'otherDatasetCandidates': candidates,
                     'candidateOnly': True, 'geometryAbsenceClaim': False,
                     'retryFrozenNameScanWithoutNewEvidence': False})

    # Reuse raster evidence only for the same region + actual selected source.
    # Every concept route must still resolve independently in the common router.
    physical = {}
    for membership in routes:
        for path in membership['paths']:
            key = membership['regionId'] + '|' + path['sourceKey']
            case = physical.setdefault(key, {'caseKey': key, 'regionId': membership['regionId'],
                                            'sourceKey': path['sourceKey'], 'sourceName': path['sourceName'],
                                            'side': path['side'], 'references': []})
            case['references'].append({'targetId': membership['targetId'],
                                       'conceptKey': path['conceptKey'],
                                       'relationKind': path['relationKind'], 'memberCode': path['memberCode']})
    names_complete = sum(r['localDisplayEligible'] and all(r['names'].get(f) for f in ['koModern', 'koTraditional', 'en']) for r in overlay['objects'])
    identity_exceptions = [{'sourceKey': r['sourceKey'], 'sourceName': r['sourceName'], 'declaredSide': r['side'],
                            'targetIds': sorted(set(t for l in r.get('learnerConceptLinks', [])
                                                   if l['identityStatus'] == 'side_conflicted' for t in l['targetIds'])),
                            'originalConflictStillUnresolved': True, 'inferMissingSide': False}
                           for r in overlay['objects'] if any(l['identityStatus'] == 'side_conflicted' for l in r.get('learnerConceptLinks', []))]
    summary = {'taskId': 'T100', 'nextUnit': 'resolve-target-representation-and-final-scene-qa',
               'acceptance': 'partial', 'denominators': {'targets': 542, 'memberships': 563, 'regions': 12},
               'overlaySha256': sha(overlay_path), 'qaBaselineSha256': sha(baseline_path),
               'targetsWithPaths': len(targets) - len(missing), 'targetsWithoutPaths': len(missing),
               'membershipsWithPaths': sum(bool(r['paths']) for r in routes),
               'membershipsWithoutPaths': sum(not r['paths'] for r in routes),
               'eligibleSurfacesWithThreeNames': names_complete,
               'eligibleSurfaces': sum(r['localDisplayEligible'] for r in overlay['objects']),
               'directKoreanCitationGapRows': baseline['terminology']['C_targetRowsWithAnyKoreanFieldGap'],
               'citationGapIsNotTheSameAsMissingLearnerName': True,
               'otherDatasetCandidateTargets': sum(bool(r['otherDatasetCandidates']) for r in rows),
               'cachedOtherDatasetCandidateTargets': sum(any(a['chunkExists'] for c in r['otherDatasetCandidates'] for a in c['cachedAssets']) for r in rows),
               'unroutedKinds': dict(Counter(r['semanticKind'] for r in rows)),
               'actionCounts': dict(Counter(r['nextAction'] for r in rows)),
               'inconstantUnroutedTargets': sum(r['inconstant'] for r in rows),
               'routePathOccurrences': sum(len(r['paths']) for r in routes),
               'distinctPhysicalVisualCases': len(physical),
               'visualAcceptance': 'pending; no passes inferred from this inventory',
               'fullTargetExtent': 'not established by member routes',
               'heldSourceIdentityExceptionRows': len(identity_exceptions),
               'performance': 'No repeated measurement requested by this audit; retain recorded input-bound evidence and separate unmeasured GPU/VRAM limits.',
               'inputHashes': {str(p): sha(p) for p in [overlay_path, baseline_path, bp_path, registry_path]}}
    return {'summary': summary, 'targets': rows, 'heldSourceIdentityExceptions': identity_exceptions}, {'summary': summary, 'cases': list(physical.values()),
            'claimBoundary': 'All original target/membership/path references retained. Raster reuse proves only the identical selected source in the same region, never target identity/full extent. Router checks and actual images are separate.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', help='Print only one unresolved target, e.g. TA2:2283')
    parser.add_argument('--write', action='store_true', help='Write derived action and visual worklists; never product data')
    parser.add_argument('--baseline', type=Path, default=OUT / 'qa-baseline.json', help='Authoritative current QA snapshot; old snapshots are immutable')
    args = parser.parse_args()
    queue, visual = build(args.baseline)
    if args.write:
        dest = ROOT / OUT
        dest.mkdir(parents=True, exist_ok=True)
        for name, value in [('action-queue.json', queue), ('visual-worklist.json', visual)]:
            (dest / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    value = next((r for r in queue['targets'] if r['targetId'] == args.target), None) if args.target else queue['summary']
    print(json.dumps(value, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
