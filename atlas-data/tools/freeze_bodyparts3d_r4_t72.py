#!/usr/bin/env python3
"""Freeze T72's exact T70-derived 11 source members before mesh acquisition."""
from __future__ import annotations
import hashlib, importlib.util, json, re, sys
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'work/evidence/T72/frozen-source-set.json'
SCOPE=ROOT/'atlas-data/manifests/bodyparts3d-r4-t70/scope-inventory.json'
INTEGRATION=ROOT/'atlas-data/manifests/bodyparts3d-r4-t70/integration-manifest.json'
METADATA=ROOT/'atlas-data/source-cache/bodyparts3d-r4/metadata'
EXPECTED_BATCHES={
 'T72-B01':['FJ1433','FJ1433M','FJ1446','FJ1446M','FJ1447','FJ1447M','FJ1464','FJ1464M','FJ3200','FJ3289'],
 'T72-B02':['FJ3309'],
}
METADATA_FILES=['isa_element_parts.txt','partof_element_parts.txt','isa_inclusion_relation_list.txt','partof_inclusion_relation_list.txt','isa_parts_list_e.txt','partof_parts_list_e.txt']
class FreezeError(RuntimeError): pass
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def sha_file(p:Path)->str:return sha(p.read_bytes())
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); assert s and s.loader; s.loader.exec_module(m); return m
def write_json(path:Path,obj:Any):
 path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def generate()->dict[str,Any]:
 if not SCOPE.is_file() or not INTEGRATION.is_file(): raise FreezeError('T70 scope/integration parent is required')
 if OUT.exists():
  raise FreezeError('freeze already exists; never regenerate it after acquisition')
 ingest=load('ha_t72_freeze_ingest',ROOT/'atlas-data/tools/ingest_bodyparts3d_r4.py')
 scope=json.loads(SCOPE.read_text(encoding='utf-8')); integration=json.loads(INTEGRATION.read_text(encoding='utf-8'))
 expected=[fid for batch in EXPECTED_BATCHES.values() for fid in batch]
 if scope.get('productFirstPassMinimum',{}).get('remainingAfterT71Batch')!=expected:
  raise FreezeError('T70 remaining list no longer matches exact T72 task scope/order')
 concept_rows={}
 for concept in scope['productFirstPassMinimum']['conceptTargets']:
  for fid in concept['sourceElementFileIds']:
   if fid in expected:
    if fid in concept_rows: raise FreezeError(f'duplicate T70 concept target for {fid}')
    concept_rows[fid]=concept
 if set(concept_rows)!=set(expected): raise FreezeError('T70 concept targets do not cover exact expected 11')
 tables=ingest.load_tables(METADATA)
 table_for_tree={'IS-A':'isaCompoundElements','PART-OF':'partofCompoundElements'}
 assets=[]
 for fid in expected:
  c=concept_rows[fid]; expected_fma=c['sourceFmaConceptId']
  contexts=[]
  for tree,key in table_for_tree.items():
   for fma,name,source_id in tables[key]:
    if source_id==fid: contexts.append({'tree':tree,'sourceFmaConceptId':fma,'sourceNameEnglish':name})
  contexts=sorted({(x['tree'],x['sourceFmaConceptId'],x['sourceNameEnglish']):x for x in contexts}.values(),key=lambda x:(x['tree'],x['sourceFmaConceptId'],x['sourceNameEnglish']))
  if not any(x['tree']=='IS-A' and x['sourceFmaConceptId']==expected_fma and x['sourceNameEnglish'].casefold()==c['sourcePreferredNameEnglish'].casefold() for x in contexts):
   raise FreezeError(f'T70 expected concept/name absent from official R4 IS-A table: {fid}')
  isa_exact=[x for x in contexts if x['tree']=='IS-A' and x['sourceFmaConceptId']==expected_fma]
  if not isa_exact: raise FreezeError(f'ID missing from selected official IS-A relation: {fid}')
  side_rows=[x for x in contexts if re.search(r'\b(left|right)\b',x['sourceNameEnglish'],re.I)]
  sides={('left' if re.search(r'\bleft\b',x['sourceNameEnglish'],re.I) else 'right') for x in side_rows if re.search(r'\b(left|right)\b',x['sourceNameEnglish'],re.I)}
  if len(sides)>1: raise FreezeError(f'conflicting official side-specific relationship rows for {fid}: {sorted(sides)}')
  region=c['productDecision']['regionId']; role=c['productDecision']['role']
  assets.append({
   'sourceElementFileId':fid,'t70SourceFmaConceptId':expected_fma,'t70SourcePreferredNameEnglish':c['sourcePreferredNameEnglish'],
   'expectedArchiveTrees':sorted({x['tree'] for x in contexts}),'selectedArchiveTree':'IS-A',
   'candidateProductRegion':region,'candidateProductRole':role,'sourceClassification':c['sourceClassification'],
   'sourceContexts':contexts,
   'officialLateralityEvidence':{'state':('explicit_side_specific_source_relation' if sides else 'official_relations_not_lateralized'),'side':next(iter(sides)) if sides else None,'relationRows':side_rows,'basis':'explicit FMA side-specific row in official R4 element relation tables; FJ suffix is not used as evidence'},
   'membershipDecision':'T70 bounded first-pass candidate only; not canonical anatomy identity, learner binding, human review, or release approval'
  })
 ids=[a['sourceElementFileId'] for a in assets]
 if ids!=expected or len(set(ids))!=11: raise FreezeError('frozen allowlist order/uniqueness failure')
 canonical=''.join(f"{a['sourceElementFileId']}|{a['t70SourceFmaConceptId']}|{a['selectedArchiveTree']}|{a['candidateProductRegion']}\n" for a in assets)
 input_hashes={'t70ScopeInventorySha256':sha_file(SCOPE),'t70IntegrationManifestSha256':sha_file(INTEGRATION),'officialMetadataSha256':{f:sha_file(METADATA/f) for f in METADATA_FILES}}
 doc={'revision':'BodyParts3D-R4-T72-FROZEN-EXACT-SOURCE-SET-v1','task':'T72','status':'frozen_before_mesh_acquisition','frozenAtLocalDate':'2026-09-27 Asia/Seoul','inputHashes':input_hashes,'sourceId':'BODYPARTS3D_LSDB_ARCHIVE_RELEASE_4_0','sourceVersion':'BodyParts3D Release 4.0','officialSelectedArchiveUrl':'https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip','sourceElementFileIds':ids,'internalBatchSizeMaximum':10,'internalBatches':[{'batchId':batch,'sourceElementFileIds':fids} for batch,fids in EXPECTED_BATCHES.items()],'sourceElementFileCount':len(ids),'uniqueSourceAssets':assets,'frozenMembershipSha256':sha(canonical.encode()),'scopeLock':'exact T70 first-pass residual 11 IDs only; IS-A selected archive; no additional FJ, identity, side, canonical learner binding, human review, or public rights inferred'}
 write_json(OUT,doc); return doc
if __name__=='__main__':
 try: print(json.dumps(generate(),ensure_ascii=False,indent=2))
 except Exception as e: print(f'T72 freeze failed: {type(e).__name__}: {e}',file=sys.stderr); raise SystemExit(1)
