import { readFile, realpath } from 'node:fs/promises';
import { resolve, sep } from 'node:path';
import { createHash } from 'node:crypto';
import type { Plugin } from 'vite';
import { buildRuntimeIntegration } from '../src/viewer/datasets/integration.ts';
import { validateDataset } from '../src/viewer/datasets/schema.ts';

type FileEntry = { id: string; path: string; sha256: string; bytes: number };
type Snapshot = { manifest: unknown; dependencies: {path: string; sha256: string}[]; files: FileEntry[] };
const sha = (bytes: Buffer) => createHash('sha256').update(bytes).digest('hex');
/** Generic local delivery only. Offline adapters own historical composition. Never emits public assets. */
export function wholeBodyPlugin(root: string): Plugin {
  const cache = resolve(root, 'atlas-data/source-cache');
  const snapshots = new Map<string, Promise<Snapshot>>();
  const runtimeProjections = new Map<string, { key: string; body: Buffer }>();
  return {
    name: 'local-compiled-datasets',
    configureServer(server) {
      // A new immutable snapshot or changed frozen dependency must be revalidated, never mixed.
      server.watcher.add([`${cache}/datasets`, `${root}atlas-data/manifests`, `${root}atlas-data/catalog/target-scope-t96.json`, `${root}work/evidence/T78/reference/ta2-scope.json`, `${cache}/bodyparts3d-r4/converted`]);
      const invalidate = (path: string) => { if(path.includes('atlas-data/')) { snapshots.clear(); runtimeProjections.clear(); } };
      server.watcher.on('change', invalidate).on('unlink', invalidate).on('add', invalidate);
      server.httpServer?.once('close', () => {
        server.watcher.off('change', invalidate).off('unlink', invalidate).off('add', invalidate); snapshots.clear(); runtimeProjections.clear();
      });
      async function snapshot(namespace: string): Promise<Snapshot> {
        let pending = snapshots.get(namespace);
        if (!pending) {
          pending = (async () => {
            const index=JSON.parse(await readFile(`${cache}/datasets/index.json`,'utf8')) as {datasets:Record<string,string>};
            const relative=index.datasets[namespace];
            if(!relative)throw Error('unknown dataset');
            const registry=await realpath(resolve(cache,'datasets',relative));
            if(!registry.startsWith(`${cache}/datasets/`))throw Error('registry containment');
            const result=JSON.parse(await readFile(registry,'utf8')) as Snapshot;
            for(const input of result.dependencies) if(sha(await readFile(input.path))!==input.sha256) throw Error('stale compiled snapshot; run prepare:datasets');
            for(const file of result.files) {
              const path=await realpath(file.path);
              if(!path.startsWith(cache+sep) || !/^[a-zA-Z0-9-]+$/.test(file.id)) throw Error('file containment');
            }
            return result;
          })();
          snapshots.set(namespace,pending);
          pending.catch(()=> {if(snapshots.get(namespace)===pending) snapshots.delete(namespace);});
        }
        return pending;
      }
      server.middlewares.use(async (req,res,next) => {
        const path=req.url?.split('?')[0] ?? '';
        if(path==='/__atlas/integration.json') {
          try {
            const bytes=await readFile(resolve(root,'atlas-data/overlays/za-local-integration.json'));
            const overlaySha256=sha(bytes);
            const overlay=JSON.parse(bytes.toString());
            const targetScopeBytes=await readFile(resolve(root,'atlas-data/catalog/target-scope-t96.json'));
            const targetScope=JSON.parse(targetScopeBytes.toString());
            const targetScopeSha256=sha(targetScopeBytes);
            const supportContextBytes=await readFile(resolve(root,'work/evidence/T78/reference/ta2-scope.json'));
            const supportContextSha256=sha(supportContextBytes);
            if(supportContextSha256!==targetScope.source.snapshotSha256)throw Error('changed frozen support context');
            const frozenTargetLexicon={
              sha256:targetScopeSha256,
              supportContext:{sha256:supportContextSha256,terms:JSON.parse(supportContextBytes.toString())},
              targets:targetScope.targets.map((target:{id:string;term:{english:string;latin:string;sourceSynonyms:Record<string,string[]>};semanticKind:string;primaryOwner:string;regionIds:string[];sourceAncestryIds?:number[];sourceCardinality?:{explicitSourceSide?:string|null}})=>({
                id:target.id,term:target.term,semanticKind:target.semanticKind,primaryOwner:target.primaryOwner,regionIds:target.regionIds,
                sourceAncestryIds:target.sourceAncestryIds,
                sourceCardinality:target.sourceCardinality ? {explicitSourceSide:target.sourceCardinality.explicitSourceSide ?? null} : undefined,
              })),
            };
            const decisionPath=await realpath(resolve(root,overlay.policy.rightsEvidence));
            if(!decisionPath.startsWith(resolve(root,'work/evidence')+sep))throw Error('decision containment');
            const rightsEvidenceSha256=sha(await readFile(decisionPath));
            if(rightsEvidenceSha256!==overlay.policy.rightsEvidenceSha256)throw Error('changed local-use decision');
            const compiled=await snapshot('za-c7010a9');
            const dataset=validateDataset(compiled.manifest);
            if(dataset.revision!==overlay.datasetRevision)throw Error('stale integration');
            const cacheKey=sha(Buffer.from([overlaySha256,dataset.revision,rightsEvidenceSha256,targetScopeSha256,supportContextSha256].join('\n')));
            let cached=runtimeProjections.get('za-c7010a9');
            if(!cached||cached.key!==cacheKey) {
              const projection=buildRuntimeIntegration(overlay,dataset,overlaySha256,rightsEvidenceSha256,frozenTargetLexicon);
              cached={key:cacheKey,body:Buffer.from(JSON.stringify(projection))};
              runtimeProjections.set('za-c7010a9',cached);
            }
            res.setHeader('Cache-Control','no-store');res.setHeader('Content-Type','application/json');res.setHeader('Content-Length',String(cached.body.byteLength));res.end(cached.body);
          }catch{res.statusCode=503;res.end('Local integration unavailable');}
          return;
        }
        let namespace='', file='';
        if(path.startsWith('/__atlas/body/')) {namespace='bp3d-r4';file=path.slice('/__atlas/body/'.length);}
        else if(path.startsWith('/__atlas/datasets/')) {
          const parts=path.slice('/__atlas/datasets/'.length).split('/');
          if(parts.length===2) [namespace,file]=parts;
        } else { next(); return; }
        res.setHeader('Cache-Control','no-store');
        if(!/^[a-z0-9-]+$/.test(namespace) || !/^(manifest\.json|[a-zA-Z0-9-]+\.glb)$/.test(file)) {res.statusCode=404;res.end();return;}
        try {
          const data=await snapshot(namespace);
          if(file==='manifest.json') {res.setHeader('Content-Type','application/json');res.end(JSON.stringify(data.manifest));return;}
          const entry=data.files.find(c=>`${c.id}.glb`===file);
          if(!entry) {res.statusCode=404;res.end();return;}
          const bytes=await readFile(entry.path);
          if(bytes.length!==entry.bytes || sha(bytes)!==entry.sha256) throw Error('chunk integrity');
          if(req.destroyed) return;
          res.setHeader('Content-Type','model/gltf-binary');res.end(bytes);
        } catch {res.statusCode=503;res.end('Local compiled anatomy assets unavailable; prepare and validate the dataset.');}
      });
    },
  };
}
