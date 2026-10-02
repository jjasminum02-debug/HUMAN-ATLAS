"""Source-relative discrete containment and mask tracking, every authored family/member.

Winding-number containment is not triangle intersection or continuous collision freedom.
No acceptance is inferred from absence of a sampled containment.
"""
import json
import numpy as np
from author_t66_family_motion import author
from author_source_surface_motion import ROOT,read,dump,rotation
from source_surface_constraints import inside

OUT='work/evidence/T66/implementation-2026-10-02'
def bounded_inside(points,vertices,triangles):
    result=np.zeros(len(points),dtype=bool)
    ids=np.flatnonzero(((points>=vertices.min(0)-1e-8)&(points<=vertices.max(0)+1e-8)).all(1))
    if len(ids): result[ids]=inside(points[ids],vertices,triangles)
    return result

def verify(payload,frames):
    members={r['sourceKey']:r for r in payload['members']}
    bones={k:f for k,f in frames.items() if members[k]['role'] in ['moving_structure','fixed_structure']}
    rows=[];failures=[]
    for key,(poses,triangles) in frames.items():
        role=members[key]['role']; rest=poses[0]
        if role not in ['moving_structure','deforming_passive_surface','deforming_muscle_surface']:continue
        for bk,(bp,bt) in bones.items():
            if key==bk or (role=='moving_structure' and members[bk]['role']=='moving_structure'):continue
            if any(rest.max(0)[i]<bp[0].min(0)[i]-.025 or rest.min(0)[i]>bp[0].max(0)[i]+.025 for i in range(3)):continue
            baseline=bounded_inside(rest,bp[0],bt);maximum=0;badIds=set()
            for step in [2,4,6,8]:
                fresh=bounded_inside(poses[step],bp[step],bt)&~baseline
                maximum=max(maximum,int(fresh.sum()));badIds.update(np.flatnonzero(fresh).tolist())
            row={'sourceKey':key,'boneSourceKey':bk,'role':role,'baselineContainedVertices':int(baseline.sum()),'newContainedMaximum':maximum,'newVertexIds':sorted(badIds)}
            rows.append(row)
            if maximum: failures.append(row)
    return {'familyId':payload['family']['id'],'testedPhases':[.25,.5,.75,1],
        'method':'All original overview vertices; bounding rejection then exact triangle solid-angle winding >0.75. Retain original overlap separately. Does not prove continuous collision freedom or footprint accuracy.',
        'rows':rows,'failures':failures,'newContainmentMaximum':max([r['newContainedMaximum'] for r in rows],default=0)}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--family');args=p.parse_args();results=[]
    for q in read(OUT+'/family-queue.json')['familyInputs']:
        if args.family and q['id']!=args.family:continue
        payload=read(q['path']);_,_,record,frames=author(payload);result=verify(payload,frames)
        dump(OUT+'/family-assets/'+q['id']+'/contact-qc.json',result);results.append({'familyId':q['id'],'newContainmentMaximum':result['newContainmentMaximum'],'conflictingPairs':len(result['failures'])})
        print(json.dumps(results[-1]),flush=True)
    dump(OUT+'/family-contact-summary.json',results)
