"""Confirm current actual emitted motor direction and native fixed masks."""
import json,pathlib,sys,numpy as np
R=pathlib.Path(__file__).resolve().parents[4];O=pathlib.Path(__file__).parent
sys.path[:0]=[str(R/'work/tools'),str(R/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from verify_glb_interpolation import read_glb,channel_data,node_positions
from derive_source_surface_motion import sha
S={r['sourceKey']:r for r in json.load(open(R/'atlas-data/source-cache/datasets/za/compiled/manifest.json'))['instances']}
for label in sys.argv[1:]:
 kind,side=label.split('-');d=O/('enlargement-'+label+'-r2');p=json.load(open(d/'input.json'));geo=json.load(open(d/'geometry-record.json'));pose=json.load(open(d/'glb-pose-qc.json'));cq=json.load(open(d/'contact-qc.json'));assert pose['passed'] and cq['passed'];raw,doc,b=read_glb(d/'motion.glb');assert pose['motionSha256']==geo['motionSha256']==sha(raw);tr=channel_data(doc,b);nodes={n['extras']['sourceKey']:i for i,n in enumerate(doc['nodes'])};ar=json.load(open(R/('atlas-data/motion/authoring/t66-priority-s03-'+side[0]+'-'+kind+'-authoring.json')));out=[]
 for key in ar['motorRoleSourceKeys']:
  e=next(e for e in p['members'] if e['sourceKey']==key);w=node_positions(doc,b,tr,nodes[key],0);end=node_positions(doc,b,tr,nodes[key],p['family']['durationSeconds']);error=max(float(np.linalg.norm(node_positions(doc,b,tr,nodes[key],t)[e['fixedVertexIndices']]-w[e['fixedVertexIndices']],axis=1).max()) for t in np.linspace(0,p['family']['durationSeconds'],49));assert error<1e-6;spread=float(np.ptp(np.linalg.norm(end-w,axis=1)));assert spread>.001;outcome={}
  if kind=='pect':
   span=lambda a:float(np.linalg.norm(a[e['fixedVertexIndices']].mean(0)-a[e['movingVertexIndices']].mean(0)));outcome['reverseShorteningSpanMetres']=span(end)-span(w);assert outcome['reverseShorteningSpanMetres']>.0001
  else:
   sk=next(k for k in nodes if S[k]['name']=='Scapula.'+side[0]);s0=node_positions(doc,b,tr,nodes[sk],0).mean(0);s1=node_positions(doc,b,tr,nodes[sk],p['family']['durationSeconds']).mean(0);outcome['scapulaCentroidDeltaMetres']=(s1-s0).tolist();assert s1[1]>s0[1]+.001 if kind=='lev' else abs(s1[0])>abs(s0[0])+.001
  out.append({'sourceKey':key,'side':side,'kind':kind,'passed':True,'motionSha256':sha(raw),'endDegrees':p['family']['endDegrees'],'angleMultiplier':1.3,'actionDirection':'forward' if kind=='lev' else 'reverse','fixedMaskErrorMetres':error,'nonRigidDisplacementSpreadMetres':spread,'geometryQcPaths':{r['sourceKey']:r['geometryQcPath'] for r in pose['rows'] if r.get('geometryQcPath')},'contextSurfaceCount':len(nodes),'physiologicalContractionClaimed':False,'measuredAttachmentFootprints':False,**outcome})
 (d/'action-outcome.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(label,'action passed',len(out))
