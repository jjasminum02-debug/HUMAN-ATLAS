#!/usr/bin/env python3
"""Recover explicit reviewed metacarpal context into versioned wrist inputs.

No canonical binding or anatomical footprint is inferred. The existing r2 inputs
and candidates remain immutable. New source-specific authored masks still need
independent geometry/contact and scene review before registration.
"""
import copy
import json
import re
import numpy as np
from author_source_surface_motion import ROOT, read, dump, source_geometry
from derive_source_surface_motion import sha
from t66_contact_correctives import nearest_surface

OUT = 'work/evidence/T66/implementation-2026-10-02'
REPAIR = OUT + '/wrist-context-r4'
PACK = 'atlas-data/terminology/muscle-attachment-content-2026-10-02.json'
ORDINALS = {'첫째': 'First', '둘째': 'Second', '셋째': 'Third', '넷째': 'Fourth', '다섯째': 'Fifth'}
WHOLE_BONES = {'Humerus': ('위팔뼈',), 'Radius': ('노뼈',), 'Ulna': ('자뼈',),
               'Pisiform bone': ('콩알뼈',), 'Hamate bone': ('갈고리뼈',)}

def explicit_bone_names(text):
    """Only literal principal bone words; no muscle-name-based inference."""
    names = {name for name, words in WHOLE_BONES.items() if any(w in text for w in words)}
    for match in re.finditer(r'((?:첫째|둘째|셋째|넷째|다섯째)(?:[·ㆍ, ]*(?:첫째|둘째|셋째|넷째|다섯째))*) 손허리뼈', text):
        for word in ORDINALS:
            if word in match.group(1):
                names.add(ORDINALS[word] + ' metacarpal bone')
    return names

def build():
    manifest = read('atlas-data/source-cache/datasets/za/compiled/manifest.json')
    rows = {r['sourceKey']: r for r in manifest['instances']}
    overlay = {r['sourceKey']: r for r in read('atlas-data/overlays/za-local-integration.json')['objects']}
    pack = read(PACK)
    cache = {}
    def geom(key):
        if key not in cache:
            cache[key] = source_geometry(rows[key], 'overview')
        return cache[key]
    summary = []
    for side in ('left', 'right'):
        path = OUT + '/family-inputs/wrist-flexion-' + side + '.json'
        payload = copy.deepcopy(read(path))
        payload['revision'] = 't66-wrist-context-r4-explicit-reviewed-bone-words'
        members = {m['sourceKey']: m for m in payload['members']}
        moving_keys = {k for k, m in members.items() if m['role'] == 'moving_structure'}
        radius = next(r for r in rows.values() if r['sourceName'] == 'Radius.' + side[0])
        radius_world = geom(radius['sourceKey'])[-1]
        proximal = radius_world[radius_world[:, 1] >= np.quantile(radius_world[:, 1], .92)].mean(0)
        pivot = np.array(payload['family']['pivotMetres'])
        distal_axis = pivot - proximal
        distal_axis /= np.linalg.norm(distal_axis)
        proofs = []
        for item in pack['records']:
            if item.get('evidenceState') == 'conflicted_source_summary':
                continue
            context = {}
            for role in ('origin', 'insertion'):
                text = item[role]
                # Verify the reviewed value, not just a copied evidence label.
                if sha(text.encode()) != item['fieldEvidence'][role]['learnerValueSha256']:
                    raise ValueError('reviewed field hash mismatch')
                names = explicit_bone_names(text)
                context[role] = {k for k, r in rows.items() if r['kind'] == 'skeletal_surface'
                    and r['sourceLabelSide'] == side and re.sub(r'\.[lr]$', '', r['sourceName']) in names}
            keys = context['origin'] | context['insertion']
            moving = keys & moving_keys
            static = keys - moving_keys
            if not moving or not static:
                continue
            for key in item['sourceKeys']:
                row = rows.get(key)
                eligibility = overlay.get(key, {})
                if not row or row['sourceLabelSide'] != side or not eligibility.get('localDisplayEligible') or eligibility.get('hardHoldReasons'):
                    continue
                if key in members:
                    continue
                world = geom(key)[-1]
                distal_projection = (world - pivot) @ distal_axis
                if distal_projection.max() < -.003:
                    # A named head/part can stop before the distal tendon. Do not
                    # rotate a proximal belly mask as if it were a carpal insertion.
                    members[key] = {'sourceKey': key, 'lod': 'overview', 'role': 'passive_context'}
                    proofs.append({'sourceKey': key, 'sourceName': row['sourceName'],
                        'status': 'proximal_source_part_no_distal_surface_track',
                        'closestDistalPlaneMetres': float(distal_projection.max()),
                        'fieldEvidence': item['fieldEvidence'], 'sourceOnly': True})
                    continue
                def distance(bones):
                    return np.min(np.stack([np.linalg.norm(nearest_surface(world, geom(k)[-1], geom(k)[4]) - world, axis=1)
                        for k in sorted(bones)]), axis=0)
                df, dm = distance(static), distance(moving)
                score = df / (df + dm + 1e-12)
                fixed = np.flatnonzero(score <= np.quantile(score, .07))
                mobile = np.flatnonzero(score >= np.quantile(score, .93))
                if set(fixed) & set(mobile) or not len(fixed) or not len(mobile):
                    raise ValueError('ambiguous wrist source mask')
                weights = np.clip((score - score[fixed].max()) / (score[mobile].min() - score[fixed].max()), 0, 1)
                weights = weights * weights * (3 - 2 * weights)
                weights[fixed], weights[mobile] = 0, 1
                members[key] = {'sourceKey': key, 'lod': 'overview', 'role': 'deforming_passive_surface',
                    'fixedVertexIndices': fixed.tolist(), 'movingVertexIndices': mobile.tolist(), 'weights': weights.tolist(),
                    'fixedBoneKeys': sorted(static), 'movingBoneKeys': sorted(moving),
                    'maskMeaning': 'authored nearest actual source triangle regions; not measured footprints'}
                for k in static:
                    members.setdefault(k, {'sourceKey': k, 'lod': 'overview', 'role': 'fixed_structure'})
                proofs.append({'sourceKey': key, 'sourceName': row['sourceName'], 'origin': item['origin'],
                    'insertion': item['insertion'], 'fieldEvidence': item['fieldEvidence'],
                    'fixedBoneKeys': sorted(static), 'movingBoneKeys': sorted(moving)})
        payload['members'] = list(members.values())
        payload['family']['unresolved'].append('Recovered whole-bone context is not an exact distal tendon footprint; actual geometry review remains required.')
        output = REPAIR + '/inputs/wrist-flexion-' + side + '.json'
        dump(output, payload)
        summary.append({'familyId': payload['family']['id'], 'path': output,
            'sha256': sha((ROOT / output).read_bytes()), 'baseInput': path,
            'baseInputSha256': sha((ROOT / path).read_bytes()), 'addedDeformingSources': proofs,
            'registered': False})
    dump(REPAIR + '/manifest.json', {'revision': 't66-wrist-context-r4', 'packPath': PACK,
        'packSha256': sha((ROOT / PACK).read_bytes()), 'families': summary,
        'originalInputsChanged': False, 'canonicalBindingsCreated': False})
    print(json.dumps([{'familyId': s['familyId'], 'addedDeformingSources': len([p for p in s['addedDeformingSources'] if 'status' not in p]),
        'proximalSourceParts': len([p for p in s['addedDeformingSources'] if 'status' in p])} for s in summary]))

if __name__ == '__main__':
    build()
