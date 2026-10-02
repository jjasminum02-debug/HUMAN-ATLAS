#!/usr/bin/env python3
"""Apply one unchanged contact-preserving authoring method to the full family queue.

The prior inputs/assets are historical evidence. Only this explicit r6 is written;
failed geometry is never registered, and existing angle/quality limits stay fixed.
"""
import copy
import json
from author_source_surface_motion import ROOT, read, dump
from author_t66_family_motion import author
from derive_source_surface_motion import sha
from verify_t66_family_contacts import verify

BASE = 'work/evidence/T66/implementation-2026-10-02'
OUT = BASE + '/contact-production-r6'

def produce():
    results = []
    for row in read(BASE + '/family-queue.json')['familyInputs']:
        original = row['path']
        if row['id'].startswith('wrist-'):
            original = BASE + '/wrist-context-r4/inputs/' + row['id'] + '.json'
        payload = copy.deepcopy(read(original))
        payload.update(revision='t66-family-contact-r6', correctContactWeights=True)
        path = OUT + '/' + row['id']
        dump(path + '/input.json', payload)
        result = {'id': row['id'], 'inputPath': path + '/input.json',
            'inputSha256': sha((ROOT / path / 'input.json').read_bytes()),
            'priorInputPath': original, 'priorInputSha256': sha((ROOT / original).read_bytes()),
            'registered': False}
        try:
            rest, motion, record, frames = author(payload)
            qc = verify(payload, frames)
            (ROOT / path / 'reference.glb').write_bytes(rest)
            (ROOT / path / 'motion.glb').write_bytes(motion)
            dump(path + '/authoring-record.json', record)
            dump(path + '/contact-qc.json', qc)
            result.update(status='candidate_geometry_contact_pass' if not qc['failures'] else 'source_contact_rejected',
                newContainmentMaximum=qc['newContainmentMaximum'], conflictingPairs=len(qc['failures']),
                deformingMembers=len([m for m in record['members'] if m['role'].startswith('deforming')]),
                flips=sum(m['flips'] for m in record['surfaceMetrics']), bytes=len(motion),
                recordPath=path + '/authoring-record.json', qcPath=path + '/contact-qc.json')
        except ValueError as exc:
            result.update(status='geometry_rejected', error=str(exc))
        results.append(result)
        dump(OUT + '/production.json', results)
        print(json.dumps({k: v for k, v in result.items() if k not in ['inputPath', 'priorInputPath', 'priorInputSha256', 'inputSha256', 'recordPath', 'qcPath']}), flush=True)
    return results

if __name__ == '__main__':
    produce()
