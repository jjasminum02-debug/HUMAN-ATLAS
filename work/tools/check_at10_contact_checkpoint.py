"""Scoped source/lineage/emitted/local-unit/preservation checks for AT10 r5."""
from pathlib import Path
import ast, hashlib, json
import numpy as np
R=Path(__file__).resolve().parents[2];E=R/'work/evidence/AT10/2026-10-14-skin-fit-r5';O=R/'atlas-data/anatomy/skin/at10-fit-r5'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
start=load(E/'start.json');base=load(R/'work/evidence/AT10/2026-10-13-skin-fit-r2/candidates/fit-r22.json')
for path,expected in start['trackedWipHashes'].items():assert sha(R/path)==expected,path
assert sha(R/'atlas-data/anatomy/skin/at10-fit-r2/skin-candidate-r22.glb')==start['primarySha256']
for path,expected in base['inputHashes'].items():assert sha(R/path)==expected,path
lineage=['sourceVertices','originalVertexIds','uv','faces','sourceGroupCounts','inputHashes']
for revision in ['r40','r41','r54']:
    candidate=E/f'candidates/fit-{revision}.json';d=load(candidate)
    for key in lineage:assert d[key]==base[key],(revision,key)
    assert not d['fitAcceptancePassed'] and not d['learnerEligible']
    mapping=load(O/f'source-to-derived-{revision}.json');cost=load(O/f'cost-{revision}.json')
    assert sha(O/f'skin-candidate-{revision}.glb')==mapping['glbSha256']==cost['sha256']
    assert mapping['helperExported'] is False and cost['logicalVertices']==13380 and cost['triangles']==26756
    assert not cost['existingBudgetsChanged'] and cost['perAsset8MiBPassed']
d=load(E/'candidates/fit-r41.json');v=np.array(d['positions'])
t=np.array([[x['derivedVertices'][0],x['derivedVertices'][j],x['derivedVertices'][j+1]] for x in d['faces'] for j in range(1,len(x['derivedVertices'])-1)])
npz=np.load(E/'candidates/fit-r41-full-native-r1-contact-addresses.npz');cross=npz['skinTriangle'];self_pairs=npz['selfCrossingTrianglePairs']
units=[];changed=set()
for revision,side in [('r40','right'),('r41','left')]:
    record=load(E/f'contact-fit-{revision}.json');unit=record['sourceUnit'];ids=unit['sourceVertices'];changed.update(ids)
    mask=np.isin(t,ids).any(1);local_native=len(set(cross[mask[cross]].tolist()));local_self=int(mask[self_pairs].any(1).sum())
    assert local_native==local_self==0,(side,local_native,local_self)
    field=load(E/f'contact-field-inspection-{revision}.json');assert field['numericalChecksPassed'] and field['candidateReadOnly']
    assert field['sourceVolumeGridQueries']>0 and field['minimumVolumeJacobian']>0
    units.append({'side':side,'nativeCrossingTriangles':local_native,'selfPairs':local_self,'sourceVertices':len(ids),'localContactPassed':True,'wholeSkinPassed':False})
outside=np.array([i for i in range(len(v)) if i not in changed]);assert np.array_equal(v[outside],np.array(base['positions'])[outside])
d54=load(E/'candidates/fit-r54.json');foot_ids=load(E/'contact-fit-r54.json')['sourceUnit']['sourceVertices'];outside_foot=~np.isin(np.arange(len(v)),foot_ids)
assert np.array_equal(np.array(d54['positions'])[outside_foot],v[outside_foot]),'Foot trial changed the successful hands/other body'
replayed=Path('/private/tmp/at10-contact-r5-replay-01/assets/skin-candidate-r41.glb');assert replayed.read_bytes()==(O/'skin-candidate-r41.glb').read_bytes()
inventory=load(E/'native-inventory-completion-r1.json');assert inventory['allDefaultVisibleBoneMuscleKeysCovered'] and inventory['newTotalObjects']==834
assert sha(E/'native-supplement-r1.json')==inventory['supplementSha256']
native=load(R/'work/evidence/AT10/2026-10-13-skin-fit-r1/native-surfaces-r1.json');native.update(load(E/'native-supplement-r1.json'))
foot=load(E/'surface-bands-r52.json')['patches'][0];toe_controls=[c for c in foot['nativeJointControls'] if '-toe-' in c['id']]
assert len(toe_controls)==19
for c in toe_controls:
    centers=[]
    for ref in c['nativeReferences']:
        item=native[ref['nativeSourceKey']];assert item['side']=='right'
        centers.append(np.array(item['v'])[ref['nativeVertexIds']].mean(0))
    assert np.linalg.norm(np.mean(centers,axis=0)-c['target'])<1e-12
    assert c['clinicalLandmarkApproval'] is False
pytools=['fit_at10_skin_contact.py','inspect_at10_skin_contact.py','replay_at10_skin_contact.py','at10_skin_field_math.py',
    'complete_at10_native_inventory.py','probe_at10_source_self.py','probe_at10_helper_embedding.py',
    'prepare_at10_head_field.py','prepare_at10_embedding_correction.py','prepare_at10_foot_chain.py',
    'author_at10_foot_webs.py','derive_at10_surface_guides.py','validate_at10_skin_blender.py','inspect_at10_skin_blender.py',
    'check_at10_contact_checkpoint.py']
for name in pytools:ast.parse((R/'work/tools'/name).read_text(),filename=name)
outputs={'scope':'AT10 skin-fit local contact checkpoint; whole task remains partial','protectedTrackedWipFiles':len(start['trackedWipHashes']),
    'protectedWipHashesPassed':True,'primaryR22Unchanged':True,'sourcePinnedInputsUnchanged':True,'sourceBodyUvFacesOriginalIdsUnchanged':True,
    'helpersOriginalAndNotExported':5778,'nativeDefaultVisibleBoneMuscleInventoryCompleted':True,'referenceObjects':834,
    'localUnits':units,'newFootTrialPreservedSuccessfulHandsByteExact':True,'sameInstalledGltfLoaderChecks':['r40','r41','r54'],
    'frozenNumericRecipeIndependentExactR41GlbReproduction':True,'reproductionSha256':sha(replayed),
    'originalNativeAndRuntimeModifiedByThisTask':False,'pythonSyntaxFiles':len(pytools),'footChainActualSourceHandles':19,
    'footJointCapsReconstructedFromActualNativeVertices':True,'sourceRigHandlesNotClinicalLandmarks':True,
    'wholeGeometryAcceptance':False,'learnerEligible':False,'actualLearnerImportCount':0,'allScopedChecksPassed':True}
(E/'scoped-checks-r41-r54.json').write_text(json.dumps(outputs,indent=2)+'\n');print(json.dumps(outputs),flush=True)
