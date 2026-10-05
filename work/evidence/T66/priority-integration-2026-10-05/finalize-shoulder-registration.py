import pathlib,json,subprocess,copy,hashlib
R=pathlib.Path(__file__).resolve().parents[4];O=pathlib.Path(__file__).parent
load=lambda p:json.loads((R/p).read_text());sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest()
save=lambda p,v:(R/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
m=load('atlas-data/motion/motion-learning.json');sc=load('atlas-data/motion/motion-scenes.json');reg=load('atlas-data/motion/authoring/registry.json');ac=load('atlas-data/motion/t66-priority-action-acceptance.json');headsc={s['id']:s for s in json.loads(subprocess.check_output(['git','show','HEAD:atlas-data/motion/motion-scenes.json'],cwd=R))['sceneManifests']};receipt=[]
for re in reg['records']:
 if not re['id'].startswith('T66-PRIORITY-S05-') or 'KNEE' in re['id']:continue
 ar=load(re['path']);fid=ar['sourceFamilyId'];kind=fid.split('-')[1];side=ar['side'];d=O/('adopted-'+kind+'-'+side);inp=json.loads((d/'input.json').read_text());roles={e['sourceKey']:('deforming_muscle_surface' if e['sourceKey'] in ar['motorRoleSourceKeys'] else e['role']) for e in inp['members']}
 for e in inp['members']:e['role']=roles[e['sourceKey']]
 save(str((d/'input.json').relative_to(R)),inp);geo=load(ar['geometryRecordPath']);geo['inputSha256']=hashlib.sha256(json.dumps(inp,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for field in ['members','surfaceMetrics']:
  for e in geo[field]:e['role']=roles[e['sourceKey']]
 save(ar['geometryRecordPath'],geo);pose=load(ar['glbPoseQcPath'])
 for e in pose['rows']:e['role']=roles[e['sourceKey']]
 save(ar['glbPoseQcPath'],pose);ar['passiveDeformationKeys']=[k for k,v in roles.items() if v=='deforming_passive_surface'];assets=[a for a in m['motionAssets'] if a.get('sourceBinding',{}).get('sourceFamilyId')==fid];out=load(ar['actionOutcomePath']);oldar=load('atlas-data/motion/authoring/t66-priority-s03-'+side[0]+'-'+kind+'-authoring.json');newid='T66-PRIORITY-S05-'+side[0].upper()+'-'+kind.upper()+'-REFERENCE'
 for a in assets:
  oldid=a['staticBinding']['sceneId'];scene=next(s for s in sc['sceneManifests'] if s['id']==oldid)
  if not any(s['id']==newid for s in sc['sceneManifests']):
   n=copy.deepcopy(scene);n['id']=newid;sc['sceneManifests'].append(n)
   if oldid in headsc:sc['sceneManifests'][sc['sceneManifests'].index(scene)]=copy.deepcopy(headsc[oldid])
   else:
    ref=next(e for e in oldar['verificationDependencies'] if '/derived-glb/' in e['path'] and e['sha256']==oldar['restSha256']);scene.update(assetUri=ref['path'],sourceAssetSha256=ref['sha256'])
   receipt.append({'oldSceneId':oldid,'newSceneId':newid,'legacyRestPreserved':True})
  a['staticBinding']['sceneId']=newid;definition=next(v for v in m['motionDefinitions'] if v['id']==a['motionDefinitionId']);definition['staticReference']['sceneId']=newid
  for member in a['sourceBinding']['members']:
   member['role']=roles[member['sourceKey']]
  row=next(r for r in ac['rows'] if r['assetId']==a['id']);o=next(o for o in out if o['sourceKey']==row['sourceKey']);o['assetId']=a['id'];o['actionId']=row['actionId']
 save(ar['actionOutcomePath'],out)
 for dep in ar['verificationDependencies']:dep['sha256']=sha(dep['path'])
 save(re['path'],ar);re['sha256']=sha(re['path'])
 for row in ac['rows']:
  if row['authoringPath']==re['path']:row['authoringSha256']=re['sha256'];row['outcomeSha256']=sha(row['outcomePath'])
for p,v in [('atlas-data/motion/motion-learning.json',m),('atlas-data/motion/motion-scenes.json',sc),('atlas-data/motion/authoring/registry.json',reg),('atlas-data/motion/t66-priority-action-acceptance.json',ac),('work/evidence/T66/priority-integration-2026-10-05/shared-scene-isolation-receipt.json',receipt)]:save(p,v)
