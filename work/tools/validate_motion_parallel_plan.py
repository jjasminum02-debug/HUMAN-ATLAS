#!/usr/bin/env python3
"""Read-only validation of the full-muscle research allocation; no task promotion."""
import argparse, hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
DEFAULT = 'work/evidence/motion-all-muscles-plan-2026-10-02/run-manifest.json'
def read(path): return json.loads((ROOT / path).read_text())
def digest(path): return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
def unique_union(assignments, key, expected):
    flat = [v for a in assignments.values() for v in a[key]]
    assert len(flat) == len(set(flat)), 'overlapping assignment: ' + key
    assert set(flat) == expected, 'missing or extra assignment: ' + key

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--manifest', default=DEFAULT); parser.add_argument('--results', action='store_true'); args = parser.parse_args()
    m = read(args.manifest)
    assert m['schemaVersion'] == 'all-muscle-motion-research-manifest-v1'
    for path, sha in {**m['inputHashes'], **m['snapshots']}.items(): assert digest(path) == sha, 'input drift: ' + path
    parent = Path(args.manifest).parent
    targets = read(parent / 'muscle-targets.json'); sources = read(parent / 'source-concepts.json'); instances = read(parent / 'source-instances.json')
    t96 = read('atlas-data/catalog/target-scope-t96.json')
    expected = {r['id'] for r in t96['targets'] if r['semanticKind'] in {'named_muscle','muscle_part','muscle_group','muscle_complex','repeated_muscle_family'}}
    assert len(t96['targets']) == 542 and len(expected) == 429 and len(targets) == 429
    assert len(sources) == 232 and len(instances) == 462
    assert sum(len(t['regionIds']) for t in targets) == 447
    assert {r['id'] for r in targets} == expected
    assert {r['sourceKey'] for r in instances} == {key for r in sources for key in r['sourceKeys']}
    unique_union(m['assignments'], 'assignedTargetIds', expected)
    unique_union(m['assignments'], 'assignedSourceConceptKeys', {r['conceptKey'] for r in sources})
    unique_union(m['assignments'], 'assignedSourceKeys', {r['sourceKey'] for r in instances})
    assert set(region for a in m['assignments'].values() for region in a['primaryRegions']) == set(r['regionId'] for r in t96['regions'])
    for name, assignment in m['assignments'].items():
        assert assignment['counts'] == {'targets':len(assignment['assignedTargetIds']), 'sourceConcepts':len(assignment['assignedSourceConceptKeys']), 'sourceInstances':len(assignment['assignedSourceKeys'])}
        assert (ROOT / assignment['outputDirectory']).resolve().is_relative_to(ROOT)
        if args.results:
            result = read(Path(assignment['outputDirectory']) / 'proposals.json')
            assert result['runId'] == m['runId'] and result['assignment'] == name
            assert result['inputHashes'] == m['inputHashes']
            assert result['assignedTargetIds'] == assignment['assignedTargetIds']
            assert result['assignedSourceConceptKeys'] == assignment['assignedSourceConceptKeys']
            tr = result['targetRows']; sr = result['sourceRows']
            assert len(tr) == len(assignment['assignedTargetIds']) and {r['targetId'] for r in tr} == set(assignment['assignedTargetIds'])
            assert len(sr) == len(assignment['assignedSourceConceptKeys']) and {r['sourceConceptKey'] for r in sr} == set(assignment['assignedSourceConceptKeys'])
            assert result.get('productionAcceptance') is False
    print(json.dumps({'status':'passed','mode':'research_results' if args.results else 'ready_manifest','runId':m['runId'],'muscleTargetRecords':429,'muscleMembershipRows':447,'sourceConcepts':232,'sourceInstances':462,'assignments':{k:v['counts'] for k,v in m['assignments'].items()},'taskAcceptanceChanged':False},ensure_ascii=False))
if __name__ == '__main__': main()
