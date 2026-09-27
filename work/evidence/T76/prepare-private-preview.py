#!/usr/bin/env python3
"""Create and clean a strict local-only allowlist for T76 visual QA."""
from __future__ import annotations
import os, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HOST=Path(__file__).resolve().parent/'private-preview-host'
ALLOWLIST={
 'index.html':ROOT/'work/evidence/T76/private-preview.html',
 'private-preview.mjs':ROOT/'work/evidence/T76/private-preview.mjs',
 'assets/T53-trunk-pelvis-static-source.glb':ROOT/'atlas-data/source-cache/bodyparts3d-r4/converted/t53/T53-trunk-pelvis-static-source.glb',
 'assets/T76-pelvic-floor-static-source.glb':ROOT/'atlas-data/source-cache/bodyparts3d-r4/converted/t76/T76-pelvic-floor-static-source.glb',
 'vendor/three/build/three.module.js':ROOT/'atlas-web/node_modules/three/build/three.module.js',
 'vendor/three/build/three.core.js':ROOT/'atlas-web/node_modules/three/build/three.core.js',
 'vendor/three/examples/jsm/loaders/GLTFLoader.js':ROOT/'atlas-web/node_modules/three/examples/jsm/loaders/GLTFLoader.js',
 'vendor/three/examples/jsm/utils/BufferGeometryUtils.js':ROOT/'atlas-web/node_modules/three/examples/jsm/utils/BufferGeometryUtils.js',
 'vendor/three/examples/jsm/utils/SkeletonUtils.js':ROOT/'atlas-web/node_modules/three/examples/jsm/utils/SkeletonUtils.js',
}
def prepare():
 if HOST.exists(): raise RuntimeError(f'refusing existing host: {HOST}')
 for rel,src in ALLOWLIST.items():
  if not src.is_file(): raise RuntimeError(f'missing input: {src}')
  dest=HOST/rel; dest.parent.mkdir(parents=True,exist_ok=True); os.link(src,dest)
 actual={p.relative_to(HOST).as_posix() for p in HOST.rglob('*') if p.is_file()}
 if actual!=set(ALLOWLIST): raise RuntimeError(f'host differs from exact allowlist: {sorted(actual^set(ALLOWLIST))}')
 return {'result':'pass','relativeHostPath':HOST.relative_to(ROOT).as_posix(),'files':[{'path':x,'bytes':(HOST/x).stat().st_size} for x in sorted(ALLOWLIST)],'repoRootExposed':False,'sourceCacheExposed':False,'onlyExactAllowlist':True}
def cleanup():
 if not HOST.exists(): return {'result':'already_clean','relativeHostPath':HOST.relative_to(ROOT).as_posix()}
 actual={p.relative_to(HOST).as_posix() for p in HOST.rglob('*') if p.is_file()}
 if actual!=set(ALLOWLIST): raise RuntimeError('refusing cleanup; allowlist changed')
 for rel in sorted(ALLOWLIST,reverse=True): (HOST/rel).unlink()
 for p in sorted((x for x in HOST.rglob('*') if x.is_dir()),reverse=True): p.rmdir()
 HOST.rmdir()
 return {'result':'pass','removedOnlyAllowlistLinks':True,'sourceInodesUntouched':True,'hostRemoved':not HOST.exists()}
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--prepare',action='store_true');g.add_argument('--cleanup',action='store_true');a=ap.parse_args();print(json.dumps(prepare() if a.prepare else cleanup(),indent=2))
