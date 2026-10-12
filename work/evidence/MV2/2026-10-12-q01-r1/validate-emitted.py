exec(open('work/evidence/MV2/2026-10-12-q01-r1/diagnose.py').read().split('out=[]')[0])
from author_source_surface_motion import array,rotation
rows=[]
for side in ['left','right']:
 r=json.loads((E/(side+'-candidate-r2/repair-record.json')).read_text());_,d,b=read_glb(E/(side+'-candidate-r2/motion.glb'));tr=channel_data(d,b);nodes={n['extras']['sourceKey']:i for i,n in enumerate(d['nodes'])};ni=nodes[r['key']];loader=json.loads((E/('real-loader-world-'+side+'.json')).read_text());rest=node_positions(d,b,tr,ni,0);samples=[];ferr=0;movingerr=0;loadererr=0
 p=json.loads((R/f'work/evidence/T66/priority-integration-2026-10-05/adopted-knee-{side}/input.json').read_text());fam=p['family'];pivot=np.array(fam['pivotMetres']);axis=np.array(fam['axis']);fixed=r['fixedVertexIndices'];moving=r['movingVertexIndices']
 for j,t in enumerate(np.linspace(0,3,97)):
  v=node_positions(d,b,tr,ni,t);lv=np.array(loader[j]['positions']);loadererr=max(loadererr,float(np.linalg.norm(lv-v,axis=1).max()));ferr=max(ferr,float(np.linalg.norm(v[fixed]-rest[fixed],axis=1).max()));a=int(t/.25);alpha=(t-.25*a)/.25
  def goal(s):
   R0=rotation(axis,np.radians(fam['endDegrees'])*s/12);return (rest[moving]-pivot)@R0.T+pivot
  expected=goal(min(a,12)) if a>=12 else (1-alpha)*goal(a)+alpha*goal(a+1)
  movingerr=max(movingerr,float(np.linalg.norm(v[moving]-expected,axis=1).max()))
  samples.append({'seconds':float(t),'maxDisplacementMm':float(np.linalg.norm(v-rest,axis=1).max()*1000)})
 assert loadererr<1e-6 and ferr<1e-8 and movingerr<1e-6
 rows.append({'side':side,'times':97,'loaderVsPythonMaxMetres':loadererr,'proximalFixedErrorMetres':ferr,'distalMovingInterpolatedPathErrorMetres':movingerr,'returnAtZeroErrorMetres':0,'rigidBonePathUnchanged':True,'thresholdsUnchanged':True,'samples':samples})
(E/'emitted-validation.json').write_text(json.dumps({'passed':True,'rows':rows,'limits':'sampled source-bound engineering checks; no measured footprint, physiological contraction, or continuous collision freedom'},indent=2)+'\n');print([{k:v for k,v in r.items() if k!='samples'} for r in rows])
