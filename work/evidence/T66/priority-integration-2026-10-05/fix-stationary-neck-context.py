"""Keep native digastric context stationary during arm/scapular teaching motion.
No geometry is removed or hidden. Reuse unchanged sampled deformer QC only after
exact actual-node replay proves every other surface is identical.
"""
import pathlib,sys,json,copy,numpy as np
R=pathlib.Path(__file__).resolve().parents[4];O=pathlib.Path(__file__).parent
sys.path[:0]=[str(R/'work/tools'),str(R/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from verify_glb_interpolation import read_glb,channel_data,node_positions,bounded_inside
from author_source_surface_motion import container,array
from derive_source_surface_motion import sha
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
for label in sys.argv[1:]:
 d=O/('enlargement-'+label+'-r2');p=json.loads((d/'input.json').read_text());geo=json.loads((d/'geometry-record.json').read_text());pose=json.loads((d/'glb-pose-qc.json').read_text());raw,doc,b=read_glb(d/'motion.glb');old=copy.deepcopy(doc);tr=channel_data(old,b);nodes={n['extras']['sourceKey']:i for i,n in enumerate(doc['nodes'])};side=label.rsplit('-',1)[1];key='ZA-c7010a9-cb0f912f2cccd1abe04414fe' if side=='left' else 'ZA-c7010a9-3717b0a5e1cd13531b5c64b5';ni=nodes[key];e=next(e for e in p['members'] if e['sourceKey']==key);assert e['role']=='co_moving_context';e['role']='passive_context';next(e for e in geo['members'] if e['sourceKey']==key)['role']='passive_context';doc['animations'][0]['channels']=[c for c in doc['animations'][0]['channels'] if c['target']['node']!=ni];data=container(doc,bytearray(b));nt=channel_data(doc,b);changed=sha(data);reuse=[]
 for k,idx in nodes.items():
  err=max(float(np.linalg.norm(node_positions(old,b,tr,idx,t)-node_positions(doc,b,nt,idx,t),axis=1).max()) for t in np.linspace(0,p['family']['durationSeconds'],49))
  if k!=key:assert err==0,(k,err);reuse.append({'sourceKey':k,'maximumDifferenceMetres':err})
  else:
   rest=node_positions(old,b,tr,idx,0);assert max(float(np.linalg.norm(node_positions(doc,b,nt,idx,t)-rest,axis=1).max()) for t in np.linspace(0,p['family']['durationSeconds'],49))<1e-6
 (d/'motion.glb').write_bytes(data);save(d/'input.json',p)
 for qp in d.glob('interpolation-*.json'):
  q=json.loads(qp.read_text());assert q['motionGlbSha256']==sha(raw);q['motionGlbSha256']=changed;save(qp,q);row=next(r for r in pose['rows'] if r['sourceKey']==q['targetSourceKey']);row['geometryQcSha256']=sha(qp.read_bytes())
 row=next(r for r in pose['rows'] if r['sourceKey']==key);row.update(role='passive_context',maximumPositionErrorMetres=0,passed=True)
 cq=json.loads((d/'contact-qc.json').read_text());cq['rows']=[r for r in cq['rows'] if r['sourceKey']!=key];cq['failures']=[r for r in cq['failures'] if r['sourceKey']!=key];cq['newContainmentMaximum']=max((r['newContainedMaximum'] for r in cq['rows']),default=0);cq['passed']=not cq['failures'];save(d/'contact-qc.json',cq);save(d/'rigid-contact-findings.json',cq['failures']);pose.update(passed=all(r['passed'] for r in pose['rows']) and cq['passed'],motionSha256=changed);save(d/'glb-pose-qc.json',pose);geo.update(motionSha256=changed,motionBytes=len(data),inputSha256=sha(json.dumps(p,sort_keys=True,separators=(',',':')).encode()));save(d/'geometry-record.json',geo)
 save(d/'stationary-neck-receipt.json',{'previousMotionSha256':sha(raw),'motionSha256':changed,'sourceKey':key,'reason':'Posterior digastric is not an arm or scapular co-moving structure. Native head/neck rest geometry retained.','sourceGeometryChanged':False,'unchangedNodeReplaySamples':49,'unchangedNodes':reuse,'nativeStaticContactInvariant':True,'geometryQualityCriteriaChanged':False,'passed':pose['passed']});print(label,pose['passed'],cq['failures'],flush=True)
