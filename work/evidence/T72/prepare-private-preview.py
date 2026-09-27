#!/usr/bin/env python3
"""Prepare a file-allowlisted, temporary same-frame QA server directory."""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
EVIDENCE=ROOT/'work/evidence/T72'
HOST=EVIDENCE/'private-preview-host'
ASSET_ROOT=ROOT/'atlas-data/source-cache/bodyparts3d-r4/converted'
ASSETS={**{f'T52-B{i:02d}.glb':ASSET_ROOT/'t52'/f'T52-B{i:02d}.glb' for i in range(1,10)},
'T53-trunk-pelvis-static-source.glb':ASSET_ROOT/'t53/T53-trunk-pelvis-static-source.glb',
'T54-shoulder-upper-limb-static-source.glb':ASSET_ROOT/'t54/T54-shoulder-upper-limb-static-source.glb',
'T55-bilateral-lower-limb-static-source.glb':ASSET_ROOT/'t55/T55-bilateral-lower-limb-static-source.glb',
'T71-trunk-skeleton-static-source.glb':ASSET_ROOT/'t71/T71-trunk-skeleton-static-source.glb',
'T72-first-pass-residual-static-source.glb':ASSET_ROOT/'t72/T72-first-pass-residual-static-source.glb'}
VENDOR={'three/build/three.module.js':ROOT/'atlas-web/node_modules/three/build/three.module.js','three/build/three.core.js':ROOT/'atlas-web/node_modules/three/build/three.core.js','three/examples/jsm/loaders/GLTFLoader.js':ROOT/'atlas-web/node_modules/three/examples/jsm/loaders/GLTFLoader.js','three/examples/jsm/utils/BufferGeometryUtils.js':ROOT/'atlas-web/node_modules/three/examples/jsm/utils/BufferGeometryUtils.js','three/examples/jsm/utils/SkeletonUtils.js':ROOT/'atlas-web/node_modules/three/examples/jsm/utils/SkeletonUtils.js'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prepare():
 if HOST.exists():raise RuntimeError(f'refusing to overwrite existing preview host: {HOST}')
 for p in [*ASSETS.values(),*VENDOR.values()]:
  if not p.is_file():raise RuntimeError(f'allowlisted preview input missing: {p}')
 HOST.mkdir(parents=True)
 try:
  shutil.copyfile(EVIDENCE/'private-preview.html',HOST/'index.html')
  shutil.copyfile(EVIDENCE/'private-preview.mjs',HOST/'private-preview.mjs')
  (HOST/'assets').mkdir();(HOST/'vendor/three/build').mkdir(parents=True);(HOST/'vendor/three/examples/jsm/loaders').mkdir(parents=True);(HOST/'vendor/three/examples/jsm/utils').mkdir(parents=True)
  files=[]
  for name,source in ASSETS.items():
   dest=HOST/'assets'/name;os.link(source,dest);files.append({'path':dest.relative_to(HOST).as_posix(),'sourcePath':source.relative_to(ROOT).as_posix(),'sha256':sha(source),'bytes':source.stat().st_size,'materialization':'read-only hardlink; source bytes unchanged'})
  for rel,source in VENDOR.items():
   dest=HOST/'vendor'/rel;os.link(source,dest);files.append({'path':dest.relative_to(HOST).as_posix(),'sourcePath':source.relative_to(ROOT).as_posix(),'sha256':sha(source),'bytes':source.stat().st_size,'materialization':'read-only hardlink; source bytes unchanged'})
  for name in ['index.html','private-preview.mjs']:
   p=HOST/name;files.append({'path':name,'sourcePath':(EVIDENCE/('private-preview.html' if name=='index.html' else name)).relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size,'materialization':'task-owned preview source copy'})
  doc={'task':'T72','scope':'private preview allowlist only; no project-root directory is served','serverRoot':HOST.relative_to(ROOT).as_posix(),'files':files,'fileCount':len(files),'openSimExposed':False,'privateDataExposed':False}
  (EVIDENCE/'preview-inputs.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
  print(json.dumps(doc,ensure_ascii=False,indent=2))
 except Exception:
  shutil.rmtree(HOST,ignore_errors=True);raise
def clean():
 if not HOST.exists():print('preview host already absent');return
 expected=read_manifest()
 actual={p.relative_to(HOST).as_posix() for p in HOST.rglob('*') if p.is_file()}
 allowed={r['path'] for r in expected['files']}
 if actual!=allowed:raise RuntimeError('preview host contains an unexpected file; refusing cleanup')
 shutil.rmtree(HOST)
 print(json.dumps({'cleanedOnlyAllowlistedPreviewHost':True,'removedFileCount':len(actual),'sourceFilesUnlinkedOnly':True}))
def read_manifest():return json.loads((EVIDENCE/'preview-inputs.json').read_text(encoding='utf-8'))
if __name__=='__main__':
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--prepare',action='store_true');g.add_argument('--clean',action='store_true');a=p.parse_args()
 try:prepare() if a.prepare else clean()
 except Exception as e:print(f'preview harness failed: {type(e).__name__}: {e}',file=sys.stderr);raise SystemExit(2)
