#!/usr/bin/env python3
"""Register only independently verified production inputs; reuse bytes for typed bone subjects.

T59 anatomy/deformation QA is reused only for its identical ankle bytes. New family candidates
need their own completed geometry/context/UI review, not this registration helper as acceptance.
"""
import copy,json
from author_source_surface_motion import ROOT,read,dump
from derive_source_surface_motion import sha

def register_ankle_bones():
    bundle=read('atlas-data/motion/motion-learning.json');base=next(a for a in bundle['motionAssets'] if a['id']=='T59-ASSET-ZA-R-TIBANT-DF')
    base['poseControl']={'label':'발목 등쪽굽힘','startDegrees':0,'endDegrees':6.5,'combination':'single_dof_only'}
    definition=next(d for d in bundle['motionDefinitions'] if d['id']==base['motionDefinitionId']);action=next(a for a in bundle['muscleActions'] if a['id']==definition['actionId'])
    overlay={r['sourceKey']:r for r in read('atlas-data/overlays/za-local-integration.json')['objects']}
    bundle['muscleActions']=[a for a in bundle['muscleActions'] if not a['id'].startswith('T66-BONE-')]
    bundle['motionDefinitions']=[a for a in bundle['motionDefinitions'] if not a['id'].startswith('T66-BONE-')]
    bundle['motionAssets']=[a for a in bundle['motionAssets'] if not a['id'].startswith('T66-BONE-')]
    rows=[]
    for member in base['sourceBinding']['members']:
        row=overlay.get(member['sourceKey'])
        if not row or row['kind']!='bone' or member['role']!='moving_structure':continue
        key=member['sourceKey'];aid='T66-BONE-'+key;act=copy.deepcopy(action)
        act.update(subjectKind='bone',id=aid+'-ACTION',subjectIds=[],sourceSubjectKeys=[key],actionLabel='발목 등쪽굽힘에서 함께 이동',explanation='선택한 뼈는 발목 등쪽굽힘 시범에서 발과 함께 이동합니다. 이 뼈에 독립된 발목 회전축이 있다는 뜻은 아닙니다. 교육용 자세를 살펴보고 처음 자세로 돌아갈 수 있습니다.')
        # Retain the evidence for the family direction only. The exact bone's
        # co-movement is established by the hashed source member and TRS track;
        # tibialis muscle manual-test roles/postures are not bone anatomy.
        act.update(postureConditions=[],stabilizationConditions=[],contextRoles=[],
            stabilizationNote='시범에서 정강뼈·종아리뼈 문맥은 고정하고 발의 뼈는 함께 이동합니다. 선택한 뼈의 독립 운동이나 임상 검사 자세를 뜻하지 않습니다.',legacyJointActionId=None)
        act['sourceRefs']=[r for r in act['sourceRefs'] if r['appliesTo']=='action_explanation']
        act.pop('learnerActionKey',None)
        d=copy.deepcopy(definition);d.update(id=aid+'-MOTION',actionId=act['id'],instanceId=key)
        a=copy.deepcopy(base);a.update(id=aid+'-ASSET',motionDefinitionId=d['id'],revision='T66-typed-bone-ankle-r1')
        a['sourceBinding'].update(contractVersion='t66-typed-source-motion-v2',subjectKind='bone',subjectSourceKey=key)
        for m in a['sourceBinding']['members']:
            if m['role']=='deforming_muscle_surface':m['role']='deforming_passive_surface'
        bundle['muscleActions'].append(act);bundle['motionDefinitions'].append(d);bundle['motionAssets'].append(a)
        rows.append({'sourceKey':key,'kind':'bone','movementRole':'co_moving','family':'ZA-static-reference-sagittal-ankle-hinge','assetId':a['id'],'independentDOF':False,'geometryQaReused':'work/evidence/T59/resume-2026-10-02/geometry-qc.json','actualUI':'pending'})
    bundle['revision']='T66-typed-source-motion-v1';dump('atlas-data/motion/motion-learning.json',bundle)
    sources=read('atlas-data/motion/motion-asset-sources.json');sources['productionMotionAssetIds']=[a['id'] for a in bundle['motionAssets']];dump('atlas-data/motion/motion-asset-sources.json',sources)
    dump('work/evidence/T66/implementation-2026-10-02/typed-bone-registrations.json',{'rows':rows,'uniqueAssetBytesCreated':0,'referenceAssetSha256':base['sha256'],'noAnatomicalBindingsCreated':True})
    print(json.dumps({'registeredBoneSubjects':len(rows),'uniqueNewGLB':0}))

if __name__=='__main__':register_ankle_bones()
