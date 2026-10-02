#!/usr/bin/env python3
"""Reproduce every selected passing r13 family, retaining historical candidates.

Run with the bundled Python/NumPy runtime. Existing evidence may be checked but
never replaced by changed bytes; use a new explicit revision/output directory.
The emitted GLB, ideal geometry and actual source-frame replay all must pass.
"""
import argparse,json
from author_source_surface_motion import ROOT,read
from derive_source_surface_motion import sha
from author_t66_family_motion import author
from verify_t66_family_contacts import verify
from verify_t66_glb_pose import verify_glb

BASE='work/evidence/T66/implementation-2026-10-02'
def pin(path,value):
    target=ROOT/path
    raw=value if isinstance(value,bytes) else (json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
    if target.exists():
        if target.read_bytes()!=raw:raise ValueError('Existing evidence differs; use a new explicit revision: '+path)
    else:
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)

def produce(out,revision):
    production={r['id']:r for r in read(BASE+'/contact-production-r6/production.json')}
    production.update({r['id']:r for r in read(BASE+'/rotation-direction-r7/production.json')})
    results=[]
    for previous in production.values():
        if previous['status']!='candidate_geometry_contact_pass':continue
        payload=read(previous['inputPath']);payload['revision']=revision;case=out+'/'+previous['id']
        pin(case+'/input.json',payload)
        rest,motion,record,frames=author(payload);qc=verify(payload,frames)
        pin(case+'/reference.glb',rest);pin(case+'/motion.glb',motion)
        emitted=verify_glb(ROOT/case/'motion.glb',payload,frames)
        if qc['failures'] or not emitted['passed']:raise ValueError('GLB/source contact rejected: '+previous['id'])
        pin(case+'/authoring-record.json',record);pin(case+'/contact-qc.json',qc);pin(case+'/glb-pose-qc.json',emitted)
        row={'id':previous['id'],'status':'candidate_geometry_contact_pass','inputPath':case+'/input.json','recordPath':case+'/authoring-record.json','qcPath':case+'/contact-qc.json','glbQcPath':case+'/glb-pose-qc.json','priorInputPath':previous['inputPath'],'inputSha256':sha((ROOT/case/'input.json').read_bytes()),'newContainmentMaximum':qc['newContainmentMaximum'],'maximumWorldErrorMetres':emitted['maximumWorldErrorMetres'],'registered':False}
        results.append(row);print(json.dumps(row),flush=True)
    pin(out+'/production.json',results)
    return results

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output-directory',default=BASE+'/signed-trs-r13');parser.add_argument('--revision',default='t66-source-family-signed-trs-r13');args=parser.parse_args()
    produce(args.output_directory,args.revision)
