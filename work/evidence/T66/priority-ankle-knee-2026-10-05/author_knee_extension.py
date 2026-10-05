"""Author both native knees with complete actual quadriceps/lower-leg context.

The bent endpoint is preparation; extension is the reversed trajectory to source rest.
Masks/pivot/range are educational engineering, never measured attachment footprints.
"""
import json,sys,pathlib,copy,math
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[4];OUT=pathlib.Path(__file__).parent
sys.path.insert(0,str(ROOT/'work/tools'))
from author_t66_family_motion import author
from author_source_surface_motion import source_geometry
from t66_contact_correctives import nearest_surface
from derive_source_surface_motion import sha
from PIL import Image,ImageDraw
load=lambda p:json.loads((ROOT/p).read_text())
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
man=load('atlas-data/source-cache/datasets/za/compiled/manifest.json');src={x['sourceKey']:x for x in man['instances']}
overlay={x['sourceKey']:x for x in load('atlas-data/overlays/za-local-integration.json')['objects']};cache={}
def geom(k):
 if k not in cache:cache[k]=source_geometry(src[k],'overview')
 return cache[k]
def bone(n,side):return next(x['sourceKey'] for x in src.values() if x['name']==n+'.'+side[0])
def mask(k,fixed,moving):
 w=geom(k)[-1]
 def distance(keys):return np.min(np.stack([np.linalg.norm(nearest_surface(w,geom(b)[-1],geom(b)[4])-w,axis=1) for b in keys]),axis=0)
 df,dm=distance(fixed),distance(moving);score=df/(df+dm+1e-12)
 fi=np.flatnonzero(score<=np.quantile(score,.07));mi=np.flatnonzero(score>=np.quantile(score,.93));weights=np.clip((score-score[fi].max())/(score[mi].min()-score[fi].max()),0,1);weights=weights*weights*(3-2*weights);weights[fi]=0;weights[mi]=1
 return {'sourceKey':k,'lod':'overview','role':'deforming_passive_surface','fixedVertexIndices':fi.tolist(),'movingVertexIndices':mi.tolist(),'weights':weights.tolist(),'maskMeaning':'authored actual native surface masks with qualitative whole-bone context; not measured footprints','fixedBoneKeys':fixed,'movingBoneKeys':moving}
for side in sys.argv[1:] or ['left','right']:
 p=load(f'work/evidence/T66/serial-completion-2026-10-02/unit-02/trials-r1/knee-flexion-{side}/input.json');p=copy.deepcopy(p)
 p.update(id='T66-PRIORITY-'+side[0].upper()+'-RECTUS-KNEE-AUTHORING',clipId='T66-PRIORITY-'+side[0].upper()+'-RECTUS-KNEE-CLIP',revision='t66-priority-knee-extension-native-r1')
 p['family'].update(id='priority-knee-extension-'+side,label='무릎 폄',endDegrees=15,validatedAuthoringLimitDegrees=15,samples=12,durationSeconds=3)
 p['family']['actionTrajectory']={'preparation':'source rest to authored knee flexion','action':'authored flexion to source rest','actionDirection':'reverse','rest':'original source frame0','physiologicalROM':False}
 p['family']['unresolved']=['Authored patella co-motion is not measured patellofemoral glide; actual native bones and original quadriceps surfaces retained.','No independent force, physiological activation, tendon footprint or normal ROM claim.']
 p['family']['qualitativeEvidence'].append({'url':'https://medicine.uams.edu/neuroscience/education/medical-school-courses/human-structure-module/anatomy-tables/muscle-tables/muscles-of-the-lower-limb/','locator':'quadriceps and gastrocnemius/plantaris rows: qualitative action and attachment context only'})
 members={e['sourceKey']:e for e in p['members']};fem=bone('Femur',side);pat=bone('Patella',side);cal=bone('Calcaneus',side)
 for r in src.values():
  k=r['sourceKey'];o=overlay.get(k,{})
  if r['sourceLabelSide']!=side or r['kind']!='muscle_surface_or_part' or not o.get('localDisplayEligible') or o.get('hardHoldReasons'):continue
  if r['name'].startswith(('Vastus lateralis','Vastus medialis')):members[k]=mask(k,[fem],[pat])
  elif 'head of gastrocnemius' in r['name'] or r['name'].startswith('Plantaris muscle'):members[k]=mask(k,[fem],[cal])
  elif k not in members and set(o['regionIds'])&{'leg','foot'}:members[k]={'sourceKey':k,'lod':'overview','role':'co_moving_context'}
  if r['name'].startswith('Rectus femoris') and k in members:members[k]['role']='deforming_muscle_surface'
 p['members']=list(members.values());dest=OUT/('knee-extension-'+side);save(dest/'input.json',p)
 # Inspect actual full source surfaces and masks before authoring. No new geometry is drawn here.
 im=Image.new('RGB',(1200,1100),'white');d=ImageDraw.Draw(im);selected=[e for e in p['members'] if 'Vastus' in src[e['sourceKey']]['name'] or 'Rectus femoris' in src[e['sourceKey']]['name'] or 'gastrocnemius' in src[e['sourceKey']]['name'] or e['sourceKey'] in [fem,pat,cal]]
 worlds=[geom(e['sourceKey'])[-1] for e in selected];allw=np.concatenate(worlds);lo=allw[:,[2,1]].min(0);scale=1000/np.ptp(allw[:,1]);d.text((10,10),side+' native knee source context / authored masks',fill='black')
 for e,w in zip(selected,worlds):
  xy=(w[:,[2,1]]-lo)*scale;xy[:,0]+=300;xy[:,1]=1070-xy[:,1]
  for tri in geom(e['sourceKey'])[4]:d.line([tuple(xy[v]) for v in [*tri,tri[0]]],fill=(190,100,90) if 'deforming' in e['role'] else (125,125,125),width=1)
  for v in e.get('fixedVertexIndices',[]):d.ellipse((*tuple(xy[v]-2),*tuple(xy[v]+2)),fill='blue')
  for v in e.get('movingVertexIndices',[]):d.ellipse((*tuple(xy[v]-2),*tuple(xy[v]+2)),fill='green')
 im.save(dest/'native-context-inspection.png')
 print(side,'authoring',len(p['members']),'actual surfaces',flush=True)
 rest,motion,record,frames=author(p)
 (dest/'reference.glb').write_bytes(rest);(dest/'motion.glb').write_bytes(motion);save(dest/'geometry-record.json',record)
 print(side,'emitted',len(motion),sha(motion),flush=True)
