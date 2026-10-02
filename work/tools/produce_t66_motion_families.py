#!/usr/bin/env python3
"""Produce all authored family inputs, retaining explicit failures and candidates without promotion."""
import json
from author_source_surface_motion import ROOT,read,dump
from author_t66_family_motion import author
OUT='work/evidence/T66/implementation-2026-10-02'
def produce():
    q=read(OUT+'/family-queue.json');results=[]
    for f in q['familyInputs']:
        try:
            payload=read(f['path']);rest,motion,record,frames=author(payload)
            directory=ROOT/OUT/'family-assets'/f['id'];directory.mkdir(parents=True,exist_ok=True)
            (directory/'reference.glb').write_bytes(rest);(directory/'motion.glb').write_bytes(motion)
            dump(str((directory/'authoring-record.json').relative_to(ROOT)),record)
            result={'id':f['id'],'status':'candidate_pending_context_and_visual_qa','bytes':len(motion),'members':len(record['members']),
                'recordPath':str((directory/'authoring-record.json').relative_to(ROOT)),'flips':sum(r['flips'] for r in record['surfaceMetrics'])}
        except Exception as error:
            result={'id':f['id'],'status':'geometry_rejected','reason':str(error)}
        results.append(result);dump(OUT+'/family-production.json',results);print(json.dumps(result,ensure_ascii=False),flush=True)
    return results
if __name__=='__main__':produce()
