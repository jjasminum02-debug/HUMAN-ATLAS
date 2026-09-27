#!/usr/bin/env python3
"""Acquire only the frozen T72 BodyParts3D R4 members using HTTP 206 ranges."""
from __future__ import annotations
import argparse, binascii, hashlib, importlib.util, json, sys, zlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[2]
FROZEN=ROOT/'work/evidence/T72/frozen-source-set.json'
OUT=ROOT/'work/evidence/T72/source-acquisition.json'
MESH=ROOT/'atlas-data/source-cache/bodyparts3d-r4/mesh/t72'
ARCHIVE='https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip'
EXPECTED=['FJ1433','FJ1433M','FJ1446','FJ1446M','FJ1447','FJ1447M','FJ1464','FJ1464M','FJ3200','FJ3289','FJ3309']
class AcquisitionError(RuntimeError):pass
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def sha_file(p:Path)->str:return sha(p.read_bytes())
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); assert s and s.loader; s.loader.exec_module(m); return m
def write_json(p:Path,obj:Any):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
RANGE=load('ha_t72_range_helper',ROOT/'atlas-data/tools/extract_bodyparts3d_r4_selected_zip_members.py')
T54=load('ha_t72_zip_m_parser',ROOT/'atlas-data/tools/acquire_bodyparts3d_r4_t54.py')
def validate_frozen()->tuple[dict,bytes]:
 if not FROZEN.is_file():raise AcquisitionError('T72 freeze missing; no acquisition allowed')
 raw=FROZEN.read_bytes(); frozen=json.loads(raw)
 if frozen.get('revision')!='BodyParts3D-R4-T72-FROZEN-EXACT-SOURCE-SET-v1' or frozen.get('status')!='frozen_before_mesh_acquisition':raise AcquisitionError('T72 freeze status/revision mismatch')
 if frozen.get('sourceElementFileIds')!=EXPECTED or [x.get('sourceElementFileId') for x in frozen.get('uniqueSourceAssets',[])]!=EXPECTED:raise AcquisitionError('frozen scope is not the exact authorized 11 IDs')
 if [len(b.get('sourceElementFileIds',[])) for b in frozen.get('internalBatches',[])]!=[10,1]:raise AcquisitionError('T72 internal 10+1 batch boundaries changed')
 canonical=''.join(f"{x['sourceElementFileId']}|{x['t70SourceFmaConceptId']}|{x['selectedArchiveTree']}|{x['candidateProductRegion']}\n" for x in frozen['uniqueSourceAssets'])
 if hashlib.sha256(canonical.encode()).hexdigest()!=frozen.get('frozenMembershipSha256'):raise AcquisitionError('frozen T72 membership hash is invalid')
 return frozen,raw
def acquire()->dict:
 frozen,frozen_raw=validate_frozen()
 meta=RANGE.head_archive(ARCHIVE)
 tail_size=min(meta['contentLength'],65557)
 tail,_=RANGE.fetch_range(ARCHIVE,meta['contentLength']-tail_size,meta['contentLength']-1,meta['etag'])
 count,cd_size,cd_offset=RANGE.parse_eocd(tail,meta['contentLength'])
 cd,_=RANGE.fetch_range(ARCHIVE,cd_offset,cd_offset+cd_size-1,meta['etag'])
 members=T54.parse_central_directory(cd,count)
 missing=sorted(set(EXPECTED)-set(members))
 if missing:raise AcquisitionError(f'official IS-A archive lacks selected frozen members: {missing}')
 file_rows=[]; transfer_ranges=[]
 for asset in frozen['uniqueSourceAssets']:
  fid=asset['sourceElementFileId']; m=members[fid]
  if m['compressionMethod'] not in (0,8):raise AcquisitionError(f'unsupported member compression for {fid}: {m["compressionMethod"]}')
  offset=m['localHeaderOffset']
  header,_=RANGE.fetch_range(ARCHIVE,offset,offset+29,meta['etag'])
  if header[:4]!=b'PK\x03\x04':raise AcquisitionError(f'local member header absent for {fid}')
  import struct
  sig,ver,flags,method,mtime,mdate,local_crc,local_comp,local_uncomp,nlen,xlen=struct.unpack('<4s5H3I2H',header)
  if method!=m['compressionMethod'] or flags&1 or m['flags']&1:raise AcquisitionError(f'unsupported or encrypted archive member {fid}')
  name_range=(offset+30,offset+30+nlen+xlen-1)
  variable,_=RANGE.fetch_range(ARCHIVE,*name_range,meta['etag'])
  member_name=variable[:nlen].decode('utf-8' if flags&0x800 else 'cp437')
  if member_name!=m['memberPath']:raise AcquisitionError(f'local and central member paths differ for {fid}')
  if not(flags&8) and (local_crc,local_comp,local_uncomp)!=(m['crc32'],m['compressedBytes'],m['uncompressedBytes']):raise AcquisitionError(f'local/central ZIP values mismatch for {fid}')
  payload_range=(offset+30+nlen+xlen,offset+30+nlen+xlen+m['compressedBytes']-1)
  if payload_range[1]<payload_range[0]:raise AcquisitionError(f'empty selected member bytes for {fid}')
  compressed,_=RANGE.fetch_range(ARCHIVE,*payload_range,meta['etag'])
  payload=compressed if method==0 else zlib.decompress(compressed,-15)
  if len(payload)!=m['uncompressedBytes'] or (binascii.crc32(payload)&0xffffffff)!=m['crc32']:raise AcquisitionError(f'official ZIP size/CRC validation failed for {fid}')
  if not payload:raise AcquisitionError(f'empty source OBJ member for {fid}')
  destination=MESH/f'{fid}.obj'
  if destination.exists():
   prior=destination.read_bytes()
   if prior!=payload:raise AcquisitionError(f'refusing to overwrite a different existing source object {fid}')
   method_used='existing_T72_cache_reverified_against_official_range'
  else:
   destination.parent.mkdir(parents=True,exist_ok=True)
   temp=destination.with_suffix('.obj.partial');temp.write_bytes(payload);temp.replace(destination)
   method_used='official_HTTP_206_selected_member_range'
  row={'sourceElementFileId':fid,'status':'acquired','sourceAcquisitionMethod':method_used,'archiveTree':'IS-A','archiveUrl':ARCHIVE,'archiveEtag':meta['etag'],'archiveLastModified':meta.get('lastModified'),'memberPath':m['memberPath'],'zipCompressionMethod':method,'zipCentralDirectoryLocalHeaderOffset':offset,'crc32':f"{m['crc32']:08x}",'bytes':len(payload),'compressedBytes':m['compressedBytes'],'sha256':sha(payload),'cacheRelativePath':destination.relative_to(ROOT).as_posix(),'sourceHeaderLicenseObservation':None}
  file_rows.append(row)
  transfer_ranges.extend([{'sourceElementFileId':fid,'kind':'localHeader','start':offset,'end':offset+29},{'sourceElementFileId':fid,'kind':'memberPathAndExtra','start':name_range[0],'end':name_range[1]},{'sourceElementFileId':fid,'kind':'compressedMemberPayload','start':payload_range[0],'end':payload_range[1]}])
 result={'revision':'BodyParts3D-R4-T72-SELECTED-RANGE-ACQUISITION-v1','task':'T72','acquiredAt':datetime.now(timezone.utc).isoformat(),'frozenSourceSetSha256':sha(frozen_raw),'frozenMembershipSha256':frozen['frozenMembershipSha256'],'officialArchive':{**meta,'url':ARCHIVE,'centralDirectoryEntries':count,'centralDirectoryBytes':cd_size,'centralDirectoryStartByte':cd_offset,'archiveTailBytes':tail_size,'selectedMemberCount':len(file_rows),'selectedPayloadBytes':sum(r['bytes'] for r in file_rows),'completeArchiveDownloaded':False,'allRequestsUsedHTTP206':True},'internalBatchResults':[{'batchId':b['batchId'],'sourceElementFileIds':b['sourceElementFileIds'],'selectedMemberCount':len(b['sourceElementFileIds'])} for b in frozen['internalBatches']],'sourceElementFileCountFrozen':11,'sourceElementFileCountAcquired':len(file_rows),'sourceElementFileCountFailed':0,'fullArchivesDownloaded':False,'selectedMemberRangeRequestsOnly':True,'rangeRequests':[{'kind':'boundedArchiveTail','start':meta['contentLength']-tail_size,'end':meta['contentLength']-1},{'kind':'zipCentralDirectory','start':cd_offset,'end':cd_offset+cd_size-1},*transfer_ranges],'files':file_rows}
 if OUT.exists():
  old=json.loads(OUT.read_text(encoding='utf-8'))
  if old.get('frozenSourceSetSha256')!=result['frozenSourceSetSha256']:raise AcquisitionError('existing T72 acquisition belongs to a different freeze')
  old_by={r['sourceElementFileId']:r for r in old.get('files',[])}
  for row in file_rows:
   if row['sourceElementFileId'] in old_by and old_by[row['sourceElementFileId']].get('sha256')!=row['sha256']:raise AcquisitionError(f'refusing to replace old T72 member hash {row["sourceElementFileId"]}')
 write_json(OUT,result);return result
def check()->dict:
 frozen,frozen_raw=validate_frozen()
 if not OUT.is_file():raise AcquisitionError('T72 acquisition manifest missing')
 acq=json.loads(OUT.read_text(encoding='utf-8'))
 if acq.get('frozenSourceSetSha256')!=sha(frozen_raw) or acq.get('frozenMembershipSha256')!=frozen.get('frozenMembershipSha256'):raise AcquisitionError('acquisition is not bound to current freeze')
 if acq.get('fullArchivesDownloaded') is not False or acq.get('selectedMemberRangeRequestsOnly') is not True or acq.get('officialArchive',{}).get('allRequestsUsedHTTP206') is not True:raise AcquisitionError('range-only archive acquisition contract failed')
 if [x.get('sourceElementFileId') for x in acq.get('files',[])]!=EXPECTED:raise AcquisitionError('acquisition IDs/order differ from exact scope')
 for row in acq['files']:
  p=ROOT/row['cacheRelativePath']; data=p.read_bytes()
  if len(data)!=row['bytes'] or sha(data)!=row['sha256'] or (binascii.crc32(data)&0xffffffff)!=int(row['crc32'],16):raise AcquisitionError(f'cached source hash/CRC/size differs: {row["sourceElementFileId"]}')
 return {'result':'pass','sourceElementFileCount':11,'selectedPayloadBytes':acq['officialArchive']['selectedPayloadBytes'],'fullArchivesDownloaded':False,'batches':[len(x['sourceElementFileIds']) for x in acq['internalBatchResults']]}
def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--acquire',action='store_true');g.add_argument('--check',action='store_true');a=p.parse_args()
 try:r=acquire() if a.acquire else check()
 except Exception as e:print(f'T72 acquisition failed: {type(e).__name__}: {e}',file=sys.stderr);return 2
 print(json.dumps(r,ensure_ascii=False,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
