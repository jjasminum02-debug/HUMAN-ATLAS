#!/usr/bin/env python3
"""Author explicit family inputs against inspected original ZA surfaces. Never edits r2 or workers.

Principal attachment bone names select context only. Nearest-surface masks are reproducible
engineering selections, not measured footprints. Anatomy/source gaps stay in the full queue.
"""
import json, re, math
from pathlib import Path
import numpy as np
from author_source_surface_motion import ROOT, RIGHTS, read, dump, source_geometry
from derive_source_surface_motion import sha
from t66_contact_correctives import nearest_surface

OUT='work/evidence/T66/implementation-2026-10-02'
def base_name(row):return re.sub(r'\.[lr]$','',row['sourceName'])
def nearest(points,other):
    return np.concatenate([np.sqrt(((p[:,None]-other[None])**2).sum(2).min(1)) for p in np.array_split(points,max(1,math.ceil(len(points)/128)))])

def prepare():
    manifest=read('atlas-data/source-cache/datasets/za/compiled/manifest.json');instances=manifest['instances'];by={r['sourceKey']:r for r in instances}
    overlay=read('atlas-data/overlays/za-local-integration.json');runtime={r['sourceKey']:r for r in overlay['objects']}
    attachments=read('atlas-data/terminology/learner-attachment-context.json');cache={}
    def geom(key):
        if key not in cache:cache[key]=source_geometry(by[key],'overview')
        return cache[key]
    def bone(name,side):return next(r for r in instances if base_name(r)==name and r['sourceLabelSide']==side)
    # Recover explicit whole-bone words in the already reviewed attachment rows. These
    # context links remain T66 authoring inputs, not new canonical attachment footprints.
    boneWords={'Humerus':['위팔뼈','상완골'],'Ulna':['자뼈','팔꿈치뼈','척골'],'Radius':['노뼈','요골'],
      'Scapula':['어깨뼈','견갑골'],'Clavicle':['빗장뼈','쇄골'],'Femur':['넙다리뼈','넓적다리뼈','대퇴골'],
      'Tibia':['정강뼈','경골'],'Fibula':['종아리뼈','비골'],'Hip bone':['엉덩뼈','궁둥뼈','두덩뼈','장골','좌골','치골'],
      'Patella':['무릎뼈','슬개골'],'Calcaneus':['발꿈치뼈','종골'],'Talus':['목말뼈','거골']}
    recovered=[]
    pack=read('atlas-data/terminology/muscle-attachment-content-2026-10-02.json')
    for item in pack['records']:
        if item.get('evidenceState')=='conflicted_source_summary':continue
        for key in item['sourceKeys']:
            if key not in by:continue
            side=by[key]['sourceLabelSide'];entry=attachments.setdefault(key,{'origin':[],'insertion':[]})
            for role in ['origin','insertion']:
                text=item[role]
                for name,words in boneWords.items():
                    if not any(w in text for w in words):continue
                    matches=[r['sourceKey'] for r in instances if r['kind']=='skeletal_surface' and base_name(r)==name and r['sourceLabelSide']==side]
                    if len(matches)==1 and matches[0] not in entry[role]:
                        entry[role].append(matches[0]);recovered.append({'sourceKey':key,'role':role,'boneSourceKey':matches[0],'sourceFieldText':text,'fieldEvidence':item['fieldEvidence'][role]})
    dump(OUT+'/recovered-authoring-bone-context.json',{'meaning':'exact named whole-bone context from reviewed text; no footprint/axis claim','rows':recovered})
    research=[]
    for worker in 'abc':
        p=f'work/evidence/motion-all-muscles-plan-2026-10-02/research-{worker}/proposals.json';d=read(p)
        for row in d['sourceRows']:research.append({'worker':worker,'path':p,'pathSha256':sha((ROOT/p).read_bytes()),'row':row})
    # Every region/type remains a queue entry. A family only becomes registered after actual asset QA.
    types=['shoulder-girdle','shoulder','elbow','forearm','wrist','hand-digit','hip','knee','ankle','foot-digit','cervical','thoracolumbar','rib-respiration','jaw','hyoid-larynx','eye','facial','tongue','pharynx','pelvic-floor']
    queue={'schemaVersion':'t66-family-queue-v1','revision':'t66-normal-motion-v1','familyTypes':types,'scope':'all muscles and all actual skeletal source subjects; no initial shortlist','familyInputs':[]}
    world_bones={r['sourceKey']:geom(r['sourceKey'])[-1] for r in instances if r['kind']=='skeletal_surface'}
    boneGroups={}
    for side in ['left','right']:
        skeleton=[r for r in instances if r['kind']=='skeletal_surface' and r['sourceLabelSide']==side]
        hand=[r for r in skeleton if any(t in base_name(r) for t in ['of hand','metacarpal','Capitate','Hamate','Lunate','Pisiform','Scaphoid','Trapezi','Triquetrum'])]
        foot=[r for r in skeleton if any(t in base_name(r) for t in ['of foot','metatarsal','Calcaneus','Talus','Cuboid','Navicular','cuneiform'])]
        upper=[bone(n,side) for n in ['Humerus','Radius','Ulna']]+hand
        lower=[bone(n,side) for n in ['Femur','Tibia','Fibula','Patella']]+foot
        boneGroups[side]={'hand':hand,'foot':foot,'upper':upper,'lower':lower}
        # Family-specific educational ranges, not normative ROM. Direction is explicit in atlas frame.
        specs=[
          ('shoulder-flexion','어깨 앞쪽 굽힘','shoulder','Humerus',True,[-1,0,0],12,upper,['Scapula','Clavicle']),
          ('shoulder-external-rotation','어깨 가쪽돌림','shoulder','Humerus',True,[0,1,0],-8 if side=='right' else 8,upper,['Scapula','Clavicle']),
          ('elbow-flexion','팔꿈치 굽힘','elbow','Humerus',False,[-1,0,0],15,[bone('Radius',side),bone('Ulna',side)]+hand,['Humerus']),
          ('wrist-flexion','손목 굽힘','wrist','Radius',False,[-1,0,0],12,hand,['Radius','Ulna']),
          ('hip-flexion','엉덩관절 굽힘','hip','Femur',True,[-1,0,0],12,lower,['Hip bone']),
          ('hip-abduction','엉덩관절 벌림','hip','Femur',True,[0,0,1],10 if side=='left' else -10,lower,['Hip bone']),
          ('knee-flexion','무릎 굽힘','knee','Femur',False,[1,0,0],15,[bone('Tibia',side),bone('Fibula',side)]+foot,['Femur']),
        ]
        for slug,label,kind,landmarkName,proximal,axis,degrees,movingBones,fixedNames in specs:
            landmark=bone(landmarkName,side);lw=world_bones[landmark['sourceKey']]
            # Retained explicit vertex IDs identify the inspected proximal head / distal joint end.
            ids=np.flatnonzero(lw[:,1]>=np.quantile(lw[:,1],.92) if proximal else lw[:,1]<=np.quantile(lw[:,1],.08))
            pivot=lw[ids].mean(0);movingKeys={r['sourceKey'] for r in movingBones};fixedKeys={bone(n,side)['sourceKey'] for n in fixedNames}
            members=[]
            for r in movingBones:members.append({'sourceKey':r['sourceKey'],'lod':'overview','role':'moving_structure'})
            for key in sorted(fixedKeys-movingKeys):members.append({'sourceKey':key,'lod':'overview','role':'fixed_structure'})
            muscleBindings=[];rejected=[]
            for r in instances:
                key=r['sourceKey'];rr=runtime.get(key,{})
                if r['kind']!='muscle_surface_or_part' or r['sourceLabelSide']!=side or not rr.get('localDisplayEligible') or rr.get('hardHoldReasons'):continue
                context=attachments.get(key);keys=set(context.get('origin',[])+context.get('insertion',[])) if context else set()
                if not keys&movingKeys:continue
                static=keys-movingKeys;moving=keys&movingKeys
                if not static:
                    members.append({'sourceKey':key,'lod':'overview','role':'co_moving_context'});continue
                static={k for k in static if k in world_bones};moving={k for k in moving if k in world_bones}
                if not static or not moving:rejected.append({'sourceKey':key,'reason':'attachment context has no actual fixed/moving bone mesh'});continue
                # Actual whole-bone context surfaces, including broad vertebral/rib attachments.
                for k in sorted(static):
                    if k not in fixedKeys:members.append({'sourceKey':k,'lod':'overview','role':'fixed_structure'});fixedKeys.add(k)
                w=geom(key)[-1]
                # Use the actual indexed triangles, not distances to sparse LOD vertices.
                def surface_distance(keys):
                    return np.min(np.stack([np.linalg.norm(nearest_surface(w,geom(k)[-1],geom(k)[4])-w,axis=1) for k in keys]),axis=0)
                df=surface_distance(sorted(static));dm=surface_distance(sorted(moving))
                score=df/(df+dm+1e-12);fixed=np.flatnonzero(score<=np.quantile(score,.07));movingIds=np.flatnonzero(score>=np.quantile(score,.93))
                if not len(fixed) or not len(movingIds) or set(fixed)&set(movingIds):rejected.append({'sourceKey':key,'reason':'ambiguous authoring vertex regions'});continue
                low=score[fixed].max();high=score[movingIds].min();weights=np.clip((score-low)/(high-low),0,1);weights=weights*weights*(3-2*weights)
                weights[fixed]=0;weights[movingIds]=1
                members.append({'sourceKey':key,'lod':'overview','role':'deforming_passive_surface','fixedVertexIndices':fixed.tolist(),'movingVertexIndices':movingIds.tolist(),'weights':weights.tolist(),
                    'maskMeaning':'authored nearest-source-surface regions, not measured attachment footprints','fixedBoneKeys':sorted(static),'movingBoneKeys':sorted(moving)})
                muscleBindings.append(key)
            # Deduplicate exact shared bone context, never duplicate a source or fabricate a side.
            unique={r['sourceKey']:r for r in members};members=list(unique.values())
            family={'id':slug+'-'+side,'type':kind,'label':label,'frameId':manifest['frameContract']['targetFrameId'],
                'referencePoseId':manifest['frameContract']['staticReferencePose']['id'],'poseMeaning':'pinned source frame0 static reference, not measured neutral',
                'axis':axis,'pivotMetres':pivot.tolist(),'endDegrees':degrees,'validatedAuthoringLimitDegrees':abs(degrees),'samples':8,'durationSeconds':2,
                'rotationOrder':'single authored DOF; no unverified multi-axis combination','landmarks':[{'sourceKey':landmark['sourceKey'],'lod':'overview','vertexIndices':ids.tolist(),
                    'meaning':'authored centroid of inspected joint end; not measured instantaneous normal axis'}],
                'qualitativeEvidence':[{'url':'https://openstax.org/books/anatomy-and-physiology-2e/pages/9-5-types-of-body-movements','locator':'9.5 Flexion/Extension, Rotation and joint types; educational axis/range is authored separately'}],
                'surroundingTissuePolicy':'original actual attachment-linked muscles receive source-specific masks; intrinsic same-segment tissue co-moves',
                'unresolved':['Joint-end centroid is an authored approximation; articular pivot fitting/contact correction and actual scene QA required before registration.','Unlinked attachment contexts do not establish passive-tissue completeness.']}
            payload={'schemaVersion':'t66-family-surface-authoring-v1','revision':'t66-authoring-r2-exact-source-triangle-distance','id':'T66-'+family['id'],'clipId':'T66-CLIP-'+family['id'],'side':side,'rights':RIGHTS,
                'dataset':{'path':'atlas-data/source-cache/datasets/za/compiled/manifest.json','sha256':sha((ROOT/'atlas-data/source-cache/datasets/za/compiled/manifest.json').read_bytes())},'family':family,'members':members}
            path=OUT+'/family-inputs/'+family['id']+'.json';dump(path,payload)
            queue['familyInputs'].append({'id':family['id'],'path':path,'sha256':sha((ROOT/path).read_bytes()),'status':'authored_input_pending_geometry_qa','deformingSourceKeys':muscleBindings,'movingBoneKeys':sorted(movingKeys),'rejectedMasks':rejected})
    queue['remainingTypes']=[x for x in types if x not in {read(f['path'])['family']['type'] for f in queue['familyInputs']}]
    queue['fullSourceQueue']=[{'packageId':p['packageId'],'sourceConceptKey':p['sourceConceptKey'],'sourceKeys':p['assignedSourceKeys'],'status':'geometry_and_action_review_pending',
        'familyInputIds':[f['id'] for f in queue['familyInputs'] if set(p['assignedSourceKeys'])&set(f['deformingSourceKeys'])]} for p in read('work/evidence/T59/authoring-run-manifest-r2.json')['sourceConceptPackages']]
    dump(OUT+'/family-queue.json',queue)
    print(json.dumps({'familyInputs':len(queue['familyInputs']),'sourceConceptQueue':len(queue['fullSourceQueue']),'authoredMasks':sum(len(f['deformingSourceKeys']) for f in queue['familyInputs']),'registered':0}))

if __name__=='__main__':prepare()
