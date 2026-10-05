import pathlib,sys,json,numpy as np,hashlib,shutil,subprocess
R=pathlib.Path(__file__).resolve().parents[4];O=pathlib.Path(__file__).parent
sys.path[:0]=[str(R/'work/tools'),str(R/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from verify_glb_interpolation import read_glb,channel_data,node_positions
from author_source_surface_motion import source_geometry
load=lambda p:json.loads((R/p).read_text());sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest()
b=load('atlas-data/motion/motion-learning.json');r=load('atlas-data/motion/authoring/registry.json');manifest=load('atlas-data/source-cache/datasets/za/compiled/manifest.json');names={x['sourceKey']:x['name'] for x in manifest['instances']};results=[];inputs=[]
if not (O/'start.json').exists():
 for p in ['atlas-data/motion/motion-learning.json','atlas-data/motion/authoring/registry.json','atlas-data/motion/motion-scenes.json','atlas-data/motion/motion-asset-sources.json','atlas-data/motion/t66-priority-action-acceptance.json','atlas-web/src/data/learnerMotionRuntime.generated.ts','work/EXECUTION.json','work/reports/T66.md']:
  d=O/'baseline'/p;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/p,d);inputs.append({'path':p,'sha256':sha(p)})
 (O/'start.json').write_text(json.dumps({'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'inputs':inputs,'scope':'T66 step03 pectoralis major three parts, levator scapulae and rhomboid major/minor, both native sides'},ensure_ascii=False,indent=2)+'\n')
for side in ['left','right']:
 for stem in ['shoulder-girdle-elevation','shoulder-girdle-protraction','shoulder-external-rotation','shoulder-abduction']:
  family=stem+'-'+side;arpath=next(x['path'] for x in reversed(r['records']) if load(x['path']).get('sourceFamilyId')==family);ar=load(arpath);ip=next(d['path'] for d in ar['verificationDependencies'] if d['path'].endswith('/input.json'));p=load(ip);asset=next(x for x in b['motionAssets'] if x.get('sourceBinding',{}).get('sourceFamilyId')==family);raw,doc,binary=read_glb(R/asset['uri']);tracks=channel_data(doc,binary);nodes={n['extras']['sourceKey']:i for i,n in enumerate(doc['nodes'])};entries={m['sourceKey']:m for m in p['members']}
  print('\n',family,asset['uri'],flush=True)
  for m in asset['sourceBinding']['members']:
   key=m['sourceKey']
   if not any(y in names[key].lower() for y in ['pectoralis major','levator','rhomboid']):continue
   e=entries[key];st=node_positions(doc,binary,tracks,nodes[key],0);en=node_positions(doc,binary,tracks,nodes[key],asset['clip']['durationSeconds']);f=e.get('fixedVertexIndices',[]);v=e.get('movingVertexIndices',[]); span=lambda x:np.linalg.norm(x[v].mean(0)-x[f].mean(0)) if f and v else None
   s0=span(st);s1=span(en);row={'familyId':family,'sourceKey':key,'name':names[key],'role':m['role'],'startSpanMetres':s0,'endSpanMetres':s1,'shorteningForwardMetres':None if s0 is None else s0-s1,'fixedMaskMaximumErrorMetres':None if not f else float(np.linalg.norm(en[f]-st[f],axis=1).max()),'surfaceMaximumDisplacementMetres':float(np.linalg.norm(en-st,axis=1).max()),'assetId':asset['id'],'motionUri':asset['uri'],'motionSha256':asset['sha256'],'authoringPath':arpath,'inputPath':ip};results.append(row);print(names[key],m['role'],'shortening',row['shorteningForwardMetres'],'fixederr',row['fixedMaskMaximumErrorMetres'],'max',row['surfaceMaximumDisplacementMetres'],flush=True)
(O/'reuse-scope-probe.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
