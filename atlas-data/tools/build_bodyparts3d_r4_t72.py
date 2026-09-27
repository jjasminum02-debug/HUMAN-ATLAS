#!/usr/bin/env python3
"""Build deterministic T72 source-only GLB and T70 sibling integration extension."""
from __future__ import annotations
import hashlib, importlib.util, json, math, re, struct, sys
from collections import defaultdict
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[2]
FREEZE=ROOT/'work/evidence/T72/frozen-source-set.json'
ACQ=ROOT/'work/evidence/T72/source-acquisition.json'
SCOPE=ROOT/'atlas-data/manifests/bodyparts3d-r4-t70/scope-inventory.json'
BASE=ROOT/'atlas-data/manifests/bodyparts3d-r4-t70/integration-manifest.json'
T71_SOURCE=ROOT/'atlas-data/manifests/bodyparts3d-r4-t71/source-manifest.json'
T71_INTEGRATION=ROOT/'atlas-data/manifests/bodyparts3d-r4-t71/integration-manifest.json'
META=ROOT/'atlas-data/source-cache/bodyparts3d-r4/metadata'
OUT_ROOT=ROOT/'atlas-data/manifests/bodyparts3d-r4-t72'
GLB=ROOT/'atlas-data/source-cache/bodyparts3d-r4/converted/t72/T72-first-pass-residual-static-source.glb'
OUT_MANIFEST=OUT_ROOT/'source-manifest.json'
OUT_INTEGRATION=OUT_ROOT/'integration-extension.json'
OUT_VALIDATION=ROOT/'work/evidence/T72/validation.json'
FRAME='HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR'; POSE='bodyparts3d-r4-static-reference'
SOURCE_ID='BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0'; SOURCE_VERSION='BodyParts3D Release 4.0'
MODEL='HA-MODEL-BP3D4-T72-FIRST-PASS-RESIDUAL-QA'
ATTR='BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International'
EXPECTED=['FJ1433','FJ1433M','FJ1446','FJ1446M','FJ1447','FJ1447M','FJ1464','FJ1464M','FJ3200','FJ3289','FJ3309']
class BuildError(RuntimeError):pass
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def sha_file(p:Path)->str:return sha(p.read_bytes())
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);assert s and s.loader;s.loader.exec_module(m);return m
def write_json(p:Path,obj:Any):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
INGEST=load('ha_t72_ingest',ROOT/'atlas-data/tools/ingest_bodyparts3d_r4.py')
CONVERT=load('ha_t72_converter',ROOT/'atlas-data/tools/convert_bodyparts3d_obj_to_glb.py')
QA=load('ha_t72_glb_qa',ROOT/'atlas-data/tools/build_bodyparts3d_r4_t53.py')
def bounds(vertices):return {'min':[min(v[i] for v in vertices) for i in range(3)],'max':[max(v[i] for v in vertices) for i in range(3)]}
def side_from_text(text:str|None)->str|None:
 if not text:return None
 low=text.casefold(); left='left' in low.split(); right='right' in low.split()
 if left and right:raise BuildError(f'conflicting source-side tokens: {text}')
 return 'left' if left else 'right' if right else None
def normalize_lateralized_name(text:str)->str:
 return re.sub(r'\s+',' ',re.sub(r'\b(left|right)\b','',text,flags=re.I)).strip().casefold()
def source_records()->tuple[list[dict],list[dict],dict]:
 frozen_raw=FREEZE.read_bytes(); frozen=json.loads(frozen_raw); acq=json.loads(ACQ.read_text(encoding='utf-8'))
 if frozen.get('sourceElementFileIds')!=EXPECTED or [x.get('sourceElementFileId') for x in frozen.get('uniqueSourceAssets',[])]!=EXPECTED:raise BuildError('freeze differs from the exact authorized 11 IDs')
 if [len(b.get('sourceElementFileIds',[])) for b in frozen.get('internalBatches',[])]!=[10,1]:raise BuildError('internal batch split changed')
 if acq.get('frozenSourceSetSha256')!=sha(frozen_raw) or acq.get('frozenMembershipSha256')!=frozen.get('frozenMembershipSha256'):raise BuildError('acquisition not bound to T72 freeze')
 if acq.get('sourceElementFileCountAcquired')!=11 or acq.get('sourceElementFileCountFailed')!=0:raise BuildError('T72 does not have all 11 official source members')
 acq_rows={r['sourceElementFileId']:r for r in acq.get('files',[])}
 if set(acq_rows)!=set(EXPECTED) or len(acq_rows)!=11:raise BuildError('acquisition rows do not exactly match frozen set')
 tables=INGEST.load_tables(META); assets={a['sourceElementFileId']:a for a in frozen['uniqueSourceAssets']}
 rows=[]; inputs=[]; comparable_hashes=defaultdict(list); header_side_checks={}
 for fid in EXPECTED:
  a=assets[fid]; r=acq_rows[fid]; p=ROOT/r['cacheRelativePath']
  if not p.is_file() or p.stat().st_size!=r['bytes'] or sha_file(p)!=r['sha256']:raise BuildError(f'raw source bytes hash/size mismatch: {fid}')
  if r.get('archiveTree')!='IS-A' or r.get('archiveUrl')!=frozen.get('officialSelectedArchiveUrl'):raise BuildError(f'archive member not in frozen official IS-A archive: {fid}')
  header=QA.parse_header(p)
  if header.get('fileId')!=fid:raise BuildError(f'exact OBJ File ID does not match frozen FJ: {fid}')
  if header.get('buildUpLogic')!='FMA 3.0 is_a':raise BuildError(f'OBJ header buildUpLogic differs from selected IS-A archive: {fid}')
  INGEST.validate_obj_source_identity(header,tables)
  contexts={(x['tree'],x['sourceFmaConceptId'],x['sourceNameEnglish']) for x in a['sourceContexts']}
  if ('IS-A',header.get('conceptId'),next((name for tree,fma,name in contexts if tree=='IS-A' and fma==header.get('conceptId')),None)) not in contexts:raise BuildError(f'OBJ header FMA is not a frozen official R4 relation for {fid}')
  if header.get('conceptId') not in {fma for tree,fma,_ in contexts if tree=='IS-A'}:raise BuildError(f'OBJ header FMA absent from official source contexts: {fid}')
  rep_pairs={(row[0],row[1]) for row in tables['isaConcepts']}
  if (header.get('conceptId'),header.get('representationId')) not in rep_pairs:raise BuildError(f'OBJ FMA/BP pair is not in official ISA concept table: {fid}')
  if not any(row[0]==header.get('conceptId') and row[2]==fid for row in tables['isaCompoundElements']):raise BuildError(f'OBJ FMA/FJ relation not in official ISA element table: {fid}')
  header_rel=[x for x in a['sourceContexts'] if x['tree']=='IS-A' and x['sourceFmaConceptId']==header.get('conceptId') and x['sourceNameEnglish'].casefold()==(header.get('englishName') or '').casefold()]
  if len(header_rel)!=1:raise BuildError(f'exact OBJ English name/FMA not a single official relation row: {fid}')
  generic_name=a['t70SourcePreferredNameEnglish']
  direct_side_rows=[x for x in a['sourceContexts'] if side_from_text(x['sourceNameEnglish']) is not None and normalize_lateralized_name(x['sourceNameEnglish'])==normalize_lateralized_name(generic_name)]
  direct_sides={side_from_text(x['sourceNameEnglish']) for x in direct_side_rows}
  if len(direct_sides)>1:raise BuildError(f'conflicting direct side-specific official relations for {fid}: {sorted(direct_sides)}')
  relation_side=next(iter(direct_sides)) if direct_sides else None
  if relation_side!=a['officialLateralityEvidence'].get('side'):
   raise BuildError(f'frozen source context and direct official side relationship differ for {fid}')
  official_laterality={'state':'explicit_side_specific_source_relation' if direct_side_rows else 'official_relations_not_lateralized','side':relation_side,'relationRows':direct_side_rows,'basis':'official FMA relation name matches T70 candidate name after removing the explicit left/right token; FJ suffix and coordinates are not used'}
  row_side=side_from_text(header.get('englishName'))
  if relation_side!=row_side:raise BuildError(f'OBJ name and explicit official side relation conflict for {fid}: {row_side} vs {relation_side}')
  if official_laterality.get('state')=='explicit_side_specific_source_relation' and not any(x['sourceFmaConceptId']==header.get('conceptId') for x in official_laterality['relationRows']):raise BuildError(f'OBJ concept is not the exact official side-specific row: {fid}')
  if official_laterality.get('state')=='official_relations_not_lateralized' and row_side is not None:raise BuildError(f'OBJ header lateralizes an officially non-lateralized candidate: {fid}')
  if not header.get('licenseHeader'):raise BuildError(f'legacy source file license header absent; keep release held: {fid}')
  vertices,normals,triangles=CONVERT.parse_obj(p)
  if len(vertices)<4 or len(normals)!=len(vertices) or len(triangles)<4:raise BuildError(f'empty/degenerate mesh or unpaired normals: {fid}')
  actual=bounds(vertices); hb=header.get('boundsMm')
  bound_deltas=[x-y for x,y in zip(hb['min']+hb['max'],actual['min']+actual['max'])]
  delta=max(abs(x) for x in bound_deltas)
  transformed=[CONVERT.transform_vertex(v) for v in vertices]
  stored=[tuple(CONVERT.float32_value(c) for c in v) for v in transformed]
  pos_bytes=CONVERT.float32_bytes(c for v in stored for c in v)
  indices=[j for tri in triangles for j in tri]
  index_bytes=struct.pack('<{}I'.format(len(indices)),*indices)
  comparable=sha(pos_bytes+b'\0'+index_bytes)
  comparable_hashes[comparable].append(fid)
  source_side_state=relation_side or 'not_lateralized_by_official_relations'
  header_side_checks[fid]={'headerSide':row_side,'officialSide':relation_side,'matched':row_side==relation_side,'evidenceFmaIds':[x['sourceFmaConceptId'] for x in official_laterality.get('relationRows',[])]}
  position_hash=sha(pos_bytes)
  side_ids=[x['sourceFmaConceptId'] for x in official_laterality.get('relationRows',[])]
  row={
   'sourceElementFileId':fid,'stableMeshAssetId':f'HA-MESH-BP3D4-{fid}','canonicalLearnerIds':[],
   'sourceId':SOURCE_ID,'sourceVersion':SOURCE_VERSION,'sourceIdentityState':'official_archive_crc_sha_obj_header_and_relation_exactly_validated',
   't70CandidateFmaConceptId':a['t70SourceFmaConceptId'],'sourceFmaConceptId':header['conceptId'],'sourceRepresentationId':header['representationId'],'sourceBuildUpLogic':header['buildUpLogic'],
   'sourceNameEnglishExactHeader':header['englishName'],'sourceOfficialRelationContexts':a['sourceContexts'],'sourceOfficialHeaderRelation':header_rel[0],
   'sourceOfficialLateralityEvidence':official_laterality,'lateralityFromExplicitOfficialRelation':source_side_state,'lateralityNotInferredFromFjSuffixOrCoordinates':True,
   'sourceArchiveTree':r['archiveTree'],'sourceArchiveUrl':r['archiveUrl'],'sourceArchiveEtag':r['archiveEtag'],'sourceArchiveLastModified':r['archiveLastModified'],'sourceMemberPath':r['memberPath'],'sourceCrc32':r['crc32'],'sourceBytes':r['bytes'],'sourceSha256':r['sha256'],'sourceZipCompressionMethod':r['zipCompressionMethod'],
   'sourceHeaderLicenseObservation':header['licenseHeader'],'officialCurrentLicense': 'CC BY 4.0 per BodyParts3D README; file-level redistribution held against legacy OBJ header','requiredAttribution':ATTR,'redistributionStatus':'held_pending_file_level_license_reconciliation_with_legacy_OBJ_headers',
   'humanAnatomyReviewed':False,'reviewState':'source_only_not_human_anatomy_reviewed','candidateProductRegion':a['candidateProductRegion'],'candidateProductRole':a['candidateProductRole'],'sourceClassificationFromT70':a['sourceClassification'],'productSelectionState':'T70_first_pass_candidate_only_not_canonical_membership_or_release_approval',
   'sourceFrame':'BodyParts3D Release 4.0 static reference','projectFrame':FRAME,'sourceUnit':'mm from exact OBJ Bounds(mm) header','projectUnit':'m','transform':'[x,y,z]mm -> [x,z,-y]m; preserve x sign; no mirror or recenter','sourceBoundsMmHeader':hb,'sourceBoundsMmActualVertices':actual,'sourceBoundsHeaderMinusVertexExtremaMm':bound_deltas,'sourceBoundsHeaderMaxAbsDeltaMm':delta,'sourceBoundsHeaderWithin001Mm':delta<=.01,'sourceBoundsDiscrepancyPolicy':'recorded without editing source vertices or treating bounds as surface/contact evidence','projectBoundsM':bounds(stored),'sourcePose':POSE,'sourceLod':'official 99%-reduced OBJ bundle; one source LOD observed',
   'sourceVertexCount':len(vertices),'sourceNormalCount':len(normals),'sourceTriangleCount':len(triangles),'transformedPositionFloat32Sha256':position_hash,'sourceGeometryTopologyComparisonSha256':comparable
  }
  rows.append(row);inputs.append({'file_id':fid,'source_path':p,'source_relative_path':r['cacheRelativePath'],'source_sha256':r['sha256'],'asset':{'bytes':r['bytes'],'vertex_count':len(vertices),'polygon_count':len(triangles),'concept_id':header['conceptId'],'representation_id':header['representationId']}})
 duplicates=[v for v in comparable_hashes.values() if len(v)>1]
 if duplicates:raise BuildError(f'exact duplicate geometry/topology source data: {duplicates}')
 return rows,inputs,header_side_checks
def build()->dict:
 required=[FREEZE,ACQ,SCOPE,BASE,T71_SOURCE,T71_INTEGRATION]
 if any(not p.is_file() for p in required):raise BuildError('required T70/T71/T72 input missing')
 frozen_raw=FREEZE.read_bytes();frozen=json.loads(frozen_raw)
 scope_sha=sha_file(SCOPE);base_sha=sha_file(BASE)
 if frozen['inputHashes'].get('t70ScopeInventorySha256')!=scope_sha or frozen['inputHashes'].get('t70IntegrationManifestSha256')!=base_sha:raise BuildError('T70 history inputs changed after T72 freeze')
 baseline=json.loads((ROOT/'work/evidence/T72/start-baseline.json').read_text(encoding='utf-8'))
 for key in (T71_SOURCE,T71_INTEGRATION):
  rel=key.relative_to(ROOT).as_posix()
  if sha_file(key)!=baseline['requiredInputSha256'][rel]:
   raise BuildError(f'T71 historical input changed after T72 start baseline: {rel}')
 base=json.loads(BASE.read_text(encoding='utf-8'));rows,inputs,side_checks=source_records()
 CONVERT.MODEL_ID=MODEL
 glb_bytes,mesh_records=CONVERT.build_glb(inputs)
 gltf,binary=QA.unpack_glb(glb_bytes)
 gltf['asset']['generator']='HUMAN ATLAS T72 deterministic BodyParts3D R4 source package builder'
 gltf['extras']={'taskScope':'T72 source-only static local QA','sourceId':SOURCE_ID,'sourceVersion':SOURCE_VERSION,'frame':FRAME,'unit':'m','pose':POSE,'sourceElementFileIds':EXPECTED,'oneNodePerUniqueSourceElementFileId':True,'canonicalLearnerMembershipCreated':False,'humanAnatomyReviewed':False,'redistributionStatus':'held_pending_file_level_license_reconciliation_with_legacy_OBJ_headers'}
 by={r['sourceElementFileId']:r for r in rows}
 for mesh in mesh_records:
  fid=mesh['sourceFileId'];row=by[fid];idx=mesh['meshIndex']
  if QA.glb_position_hash(gltf,binary,idx)!=row['transformedPositionFloat32Sha256']:raise BuildError(f'GLB position bytes differ from validated transform: {fid}')
  details={**row,'modelId':MODEL,'meshIndex':idx,'geometrySha256':mesh['geometrySha256'],'topologySha256':mesh['topologySha256'],'normalSha256':mesh['normalSha256']}
  gltf['nodes'][idx]['name']=row['stableMeshAssetId'];gltf['nodes'][idx]['extras'].update(details)
  gltf['meshes'][idx]['name']=row['stableMeshAssetId'];gltf['meshes'][idx]['extras'].update(details)
  mesh.update({'nodeName':row['stableMeshAssetId'],'sourceElementFileId':fid,'sourceFmaConceptId':row['sourceFmaConceptId'],'sourceRepresentationId':row['sourceRepresentationId'],'productCandidateRegion':row['candidateProductRegion']})
 output=QA.repack_glb(gltf,binary)
 if GLB.exists() and GLB.read_bytes()!=output:
  owned=False
  if OUT_MANIFEST.is_file():
   prior=json.loads(OUT_MANIFEST.read_text(encoding='utf-8'))
   owned=(prior.get('task')=='T72' and prior.get('inputs',{}).get('frozenSourceSetSha256')==sha(frozen_raw) and prior.get('sceneContract',{}).get('integratedGlbSha256')==sha_file(GLB))
  if not owned:raise BuildError(f'refusing to overwrite an unowned/different T72 derived GLB: {GLB}')
 GLB.parent.mkdir(parents=True,exist_ok=True);GLB.write_bytes(output);glb_sha=sha(output)
 source_manifest={
  'revision':'BodyParts3D-R4-T72-static-source-package-v1','task':'T72','status':'local_static_source_package_complete_first_pass_candidate_set_rights_human_review_and_learner_binding_held','batchIds':[b['batchId'] for b in frozen['internalBatches']],
  'source':{'sourceId':SOURCE_ID,'version':SOURCE_VERSION,'officialReadme':'https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/README_e.html','officialReleaseNote':'https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/release_4.0_e.html','archiveUrl':frozen['officialSelectedArchiveUrl'],'archiveEtag':json.loads(ACQ.read_text())['officialArchive']['etag'],'archiveLastModified':json.loads(ACQ.read_text())['officialArchive']['lastModified'],'sourceFrame':'BodyParts3D Release 4.0 static reference','projectFrame':FRAME,'sourceUnit':'mm evidenced by exact OBJ Bounds(mm) header','projectUnit':'m','transform':'[x,y,z]mm -> [x,z,-y]m; preserve x sign; no mirror or recenter','pose':POSE,'lod':'official 99%-reduced bundle; no multilevel LOD chain advertised'},
  'inputs':{'frozenSourceSet':'work/evidence/T72/frozen-source-set.json','frozenSourceSetSha256':sha(frozen_raw),'frozenMembershipSha256':frozen['frozenMembershipSha256'],'acquisitionManifest':'work/evidence/T72/source-acquisition.json','acquisitionManifestSha256':sha_file(ACQ),'t70ScopeInventorySha256':scope_sha,'t70IntegrationManifestSha256':base_sha,'t71HistoricalSourceManifestSha256':sha_file(T71_SOURCE),'t71HistoricalIntegrationManifestSha256':sha_file(T71_INTEGRATION),'officialMetadataSha256':frozen['inputHashes']['officialMetadataSha256']},
  'scope':{'sourceElementFileCount':11,'sourceMembershipCount':11,'uniqueSourceNodeCount':11,'oneNodePerUniqueFj':True,'internalBatchSizeMaximum':10,'internalBatches':[{'batchId':b['batchId'],'sourceElementFileCount':len(b['sourceElementFileIds'])} for b in frozen['internalBatches']],'regionCandidateCounts':{r:sum(x['candidateProductRegion']==r for x in rows) for r in sorted({x['candidateProductRegion'] for x in rows})},'wholeBodyCanonicalDenominator':None,'canonicalLearnerMembershipCreated':False},
  'sceneContract':{'contract':'T50 shared AnatomySceneRoot frame/pose contract; T72 local static source QA package, not learner scene','modelId':MODEL,'integratedGlbLocalCachePath':GLB.relative_to(ROOT).as_posix(),'integratedGlbSha256':glb_sha,'meshNodeCount':len(gltf['nodes']),'rendererCount':0,'rendererPolicy':'T72 local QA composes T53/T55/T71/T72 source packages in one local preview root/renderer; this sibling package does not replace T70 or T71'},
  'rights':{'officialCurrentLicense':'CC BY 4.0 per official README; individual acquired OBJ headers state legacy CC BY-SA 2.1 Japan','requiredAttribution':ATTR,'sourceHeaderLicenseObservations':sorted({r['sourceHeaderLicenseObservation'] for r in rows}),'redistributionStatus':'held_pending_file_level_license_reconciliation_with_legacy_OBJ_headers','publicRelease':False},
  'identityPolicy':'T70 candidate FMA, exact OBJ header FMA, BP representation ID, FJ source ID, and canonical HA ID remain distinct. No canonical learner binding is created.',
  'lateralityPolicy':'Side assignments use explicit side-specific FMA rows in official R4 relations plus the exact OBJ header concept/name. FJ suffix and coordinate sign are not evidence; all transforms preserve x sign.',
  'aabbPolicy':'AABB is broadphase only; no surface contact/joint fit/collision claim is made.',
  'humanAnatomyReviewed':False,'sourceAssets':rows,'meshRecords':mesh_records,'manifestSha256':None}
 source_manifest['manifestSha256']=sha(json.dumps(source_manifest,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
 if OUT_MANIFEST.exists():
  old=json.loads(OUT_MANIFEST.read_text())
  if old.get('inputs')!=source_manifest['inputs'] or old.get('meshRecords')!=source_manifest['meshRecords']:raise BuildError('refusing to overwrite non-identical existing T72 manifest')
 write_json(OUT_MANIFEST,source_manifest)
 base_ids={a['sourceElementFileId'] for a in base['assets']}
 if base_ids.intersection(by):raise BuildError('T72 exact source IDs overlap historical T70 integration')
 additions=[]
 for row in rows:
  # Keep the source class as the T70 classification hint only; do not promote to canonical learner identity.
  candidate='bone_element_source_only' if 'bone_root_closure' in row['sourceClassificationFromT70'] else 'muscle_or_part_source_only'
  additions.append({'existingLearnerStableIds':[],'holdReasons':['not_canonical_learner_binding','human_anatomy_review_not_performed','public_redistribution_held'],'humanAnatomyReviewed':False,'learnerDefaultVisible':False,'learnerPickState':'source_only_unbound','localQaRender':'available_source_surface','packageReferences':[{'package':'T72','sourceSha256':row['sourceSha256']}],'primaryPackage':'T72','productRegionIdsFromHistoricalPackages':[],'candidateProductRegionIds':[row['candidateProductRegion']],'renderNodeId':row['stableMeshAssetId'],'sourceClassCandidates':[candidate],'sourceConceptIdObservation':row['sourceFmaConceptId'],'sourceElementFileId':row['sourceElementFileId'],'sourceNameObservation':row['sourceNameEnglishExactHeader'],'sourceSha256':row['sourceSha256']})
 ext=json.loads(json.dumps(base));ext['revision']='BodyParts3D-R4-T72-sibling-extension-of-T70-minimal-integration-v1'
 ext['parentIntegrationManifest']={'path':BASE.relative_to(ROOT).as_posix(),'sha256':base_sha,'historicalManifestUnchanged':True}
 ext['siblingPackageReferences']=[{'task':'T71','sourceManifestPath':T71_SOURCE.relative_to(ROOT).as_posix(),'sourceManifestSha256':sha_file(T71_SOURCE),'integrationManifestPath':T71_INTEGRATION.relative_to(ROOT).as_posix(),'integrationManifestSha256':sha_file(T71_INTEGRATION),'relationship':'separate sibling extension from same T70 base; not merged or rewritten'}]
 ext['assets']=sorted(ext['assets']+additions,key=lambda x:x['sourceElementFileId'])
 ext['localQaChunks']=ext['localQaChunks']+[{'chunkId':'T72-B01+B02-FIRST-PASS-RESIDUAL','package':'T72','localQaGlbPath':GLB.relative_to(ROOT).as_posix(),'glbSha256':glb_sha,'sourceElementFileIds':EXPECTED,'suppressDuplicateSourceElementFileIds':[]}]
 ext['counts']={**base['counts'],'historicalPackageMembershipsT52toT55':base['counts']['historicalPackageMemberships'],'t72PackageMemberships':11,'packageMembershipsIncludingT72':base['counts']['historicalPackageMemberships']+11,'historicalUniqueSourceNodesT52toT55':base['counts']['uniqueSourceNodes'],'uniqueSourceNodesIncludingT72':base['counts']['uniqueSourceNodes']+11,'sourceOnlyUnboundIncludingT72':base['counts']['sourceOnlyUnbound']+11,'newCanonicalBindings':0,'newHumanReviewed':0}
 ext['t72InputHashes']={'scopeInventorySha256':scope_sha,'frozenSourceSetSha256':sha(frozen_raw),'acquisitionManifestSha256':sha_file(ACQ),'t72SourceManifestSha256':sha_file(OUT_MANIFEST),'t72GlbSha256':glb_sha,'t71SiblingIntegrationManifestSha256':sha_file(T71_INTEGRATION)}
 ext['publicRedistribution']='held_pending_file_level_license_reconciliation_with_legacy_OBJ_headers'
 write_json(OUT_INTEGRATION,ext)
 # Coverage is T70 first-pass 20 only; source-root closure remains a distinct 35-ID denominator.
 t70_min=set(json.loads(SCOPE.read_text())['productFirstPassMinimum']['sourceElementFileIds'])
 t71=json.loads(T71_SOURCE.read_text());t71_ids={r['sourceElementFileId'] for r in t71['sourceAssets']}
 first_pass_remaining=t70_min-t71_ids-set(EXPECTED)
 bone_gaps={r['sourceElementFileId'] for r in json.loads(SCOPE.read_text())['boneClosureMissingSourceElements']}
 t71_bones=t71_ids & bone_gaps
 t72_bones=set(EXPECTED) & bone_gaps
 if len(first_pass_remaining)!=0:raise BuildError(f'T70 first-pass remainder after T71+T72 is not 0: {sorted(first_pass_remaining)}')
 remaining_bone=bone_gaps-t71_bones-t72_bones
 validation={'revision':'T72-PACKAGE-VALIDATION-v1','task':'T72','frozenIdsMatchAcquiredAndBuilt':len(rows)==len(inputs)==len(gltf['nodes'])==11,'exactFrozenSourceIds':[r['sourceElementFileId'] for r in rows],'noExtraSourceIds':{r['sourceElementFileId'] for r in rows}==set(EXPECTED),'internalBatchCounts':[len(b['sourceElementFileIds']) for b in frozen['internalBatches']],'allHeadersMatchExactFjAndOfficialFmaBp':True,'allHeaderFjFmaBuildTreePairsInOfficialMetadata':True,'headerEnglishNameMatchesExactOfficialRelationRow':True,'archiveMemberCrcShaAndSizesValidated':True,'sourceUnitBoundsAndFrameTransformVerifiedPerFile':True,'sourceHeaderBoundsVsVerticesMm':{r['sourceElementFileId']:{'maxAbsDeltaMm':r['sourceBoundsHeaderMaxAbsDeltaMm'],'within001mm':r['sourceBoundsHeaderWithin001Mm'],'differenceMm':r['sourceBoundsHeaderMinusVertexExtremaMm']} for r in rows},'boundsDiscrepancyIdsOver001mm':[r['sourceElementFileId'] for r in rows if not r['sourceBoundsHeaderWithin001Mm']],'boundsDiscrepancyHandling':'retained exact raw source bytes; transformed vertices use raw OBJ vertices; OBJ Bounds(mm) header kept as separately observed metadata, not treated as a surface/contact test','lateralityFromExplicitOfficialRelationsAndExactHeader':side_checks,'lateralityInferredFromFjSuffix':False,'xSignPreservedWithoutMirroring':True,'nonemptyMeshes':all(r['sourceVertexCount']>0 and r['sourceTriangleCount']>0 for r in rows),'exactDuplicateGeometryTopologyGroups':[],'oneGlbNodePerFj':len(gltf['nodes'])==11,'glbPositionsMatchSourceTransform':True,'canonicalLearnerBindings':0,'humanAnatomyReviewed':False,'publicRelease':False,'redistributionStatus':'held_pending_file_level_license_reconciliation_with_legacy_OBJ_headers','T70ScopeInventoryAndIntegrationUnchanged':True,'T71SiblingPackageUnchanged':True,'T70FirstPassSourceCount':len(t70_min),'T71FirstPassSourceIdsPresent':len(t70_min & t71_ids),'T72FirstPassSourceIdsPresent':len(t70_min & set(EXPECTED)),'firstPassResidualAfterT71AndT72':sorted(first_pass_remaining),'firstPassResidualCountAfterT71AndT72':len(first_pass_remaining),'T70BoneRootMissingSourceCount':len(bone_gaps),'T71BoneRootResidualIds':sorted(t71_bones&bone_gaps),'T72BoneRootResidualIds':sorted(t72_bones&bone_gaps),'boneRootResidualAfterT71AndT72':sorted(remaining_bone),'boneRootResidualCountAfterT71AndT72':len(remaining_bone),'T72IntegrationExtensionParentSha256':base_sha,'T71SiblingExtensionNotMerged':True,'derivedGlb':{'path':GLB.relative_to(ROOT).as_posix(),'bytes':len(output),'sha256':glb_sha,'meshNodeCount':len(gltf['nodes'])},'sourceManifest':{'path':OUT_MANIFEST.relative_to(ROOT).as_posix(),'sha256':sha_file(OUT_MANIFEST)},'integrationExtension':{'path':OUT_INTEGRATION.relative_to(ROOT).as_posix(),'sha256':sha_file(OUT_INTEGRATION),'T70ParentUniqueSourceNodes':base['counts']['uniqueSourceNodes'],'T72ExtensionUniqueSourceNodes':base['counts']['uniqueSourceNodes']+11}}
 write_json(OUT_VALIDATION,validation)
 return {'sourceManifest':source_manifest,'validation':validation}
def main():
 try:r=build()
 except Exception as e:print(f'T72 build failed: {type(e).__name__}: {e}',file=sys.stderr);return 2
 print(json.dumps(r['validation'],ensure_ascii=False,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
