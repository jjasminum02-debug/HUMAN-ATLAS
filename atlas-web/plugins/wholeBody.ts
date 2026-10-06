import { loadNerveAssets } from './nerveAssets.ts';
import { composeNerveScene } from '../src/viewer/datasets/nerveScene.ts';
import { readFile, realpath } from 'node:fs/promises';
import { resolve, sep } from 'node:path';
import { createHash } from 'node:crypto';
import type { Plugin } from 'vite';
import { applyLearnerNameAliasDelta, buildRuntimeIntegration } from '../src/viewer/datasets/integration.ts';
import { composeSupplementDataset, composeSupplementRuntime, type SourceSupplement } from '../src/viewer/datasets/sourceSupplement.ts';
import { resolveSupplementTargetRelations, targetRoutesBySource } from '../src/viewer/datasets/supplementRelations.ts';
import { validateDataset, type Dataset } from '../src/viewer/datasets/schema.ts';

type FileEntry = { id: string; path: string; sha256: string; bytes: number };
type Snapshot = { manifest: any; dependencies: {path: string; sha256: string}[]; files: FileEntry[] };
type ProjectionAssets = { dataset: Dataset; datasetBody: Buffer; runtimeBody: Buffer; key: string; nerveFiles: FileEntry[] };
const sha = (bytes: Buffer) => createHash('sha256').update(bytes).digest('hex');
const T100_INPUTS = [
  'work/evidence/T100/closure-audit-2026-09-30/action-queue.json',
  'atlas-data/catalog/target-scope-t96.json',
  'work/evidence/T78/source-elements.json',
  'work/evidence/T77/current-inventory.json',
  'atlas-data/manifests/bodyparts3d-r4-t77/display-policy.json',
  'atlas-data/source-cache/bodyparts3d-r4/converted/t77/manifest.json',
  'atlas-data/source-cache/datasets/bp3d/registry.json',
  'atlas-data/source-cache/bodyparts3d-r4/metadata/partof_element_parts.txt',
  'work/evidence/T50/scene-contract.md',
  'work/evidence/T69/diagnostic.json',
  'work/evidence/T100/source-completion-2026-10-01/integration/registration-evidence.json',
  'work/evidence/T100/source-completion-2026-10-01/integration/registration-regional-comparison.json',
];
/** Generic local delivery only. The merged view remains one dataset, renderer, and scene root. */
export function wholeBodyPlugin(root: string): Plugin {
  const cache = resolve(root, 'atlas-data/source-cache');
  const snapshots = new Map<string, Promise<Snapshot>>();
  let composed: Promise<ProjectionAssets> | undefined;
  return {
    name: 'local-compiled-datasets',
    configureServer(server) {
      // Frozen dependencies invalidate both namespaces and their single-scene composition.
      server.watcher.add([
        resolve(root, 'atlas-data/overlays/nerve-support-t66.json'), resolve(root, 'atlas-data/assets/derived-glb/za-nerve-t66'), ...['nerve-evaluated-surfaces.json','nerve-export-input.json','nerve-local-use-rights.json'].map(p => resolve(root, 'work/evidence/T66/implementation-2026-10-02', p)),
        resolve(root, 'atlas-data/terminology/learner-name-aliases-2026-10-06.json'),
        `${cache}/datasets`, `${root}atlas-data/overlays/nerve-support-t63.json`, `${root}atlas-data/assets/derived-glb/za-nerve-t63`, `${root}work/evidence/T63/local-use-rights.json`, `${root}work/evidence/T63/evaluated-surfaces.json`, `${root}atlas-data/manifests`, `${root}atlas-data/catalog/target-scope-t96.json`,
        `${root}work/evidence/T78/reference/ta2-scope.json`, `${root}work/evidence/T78/source-elements.json`,
        `${root}work/evidence/T50/scene-contract.md`, `${root}work/evidence/T69/diagnostic.json`,
        `${root}work/evidence/T100/source-completion-2026-10-01/integration/registration-evidence.json`,
        `${root}work/evidence/T100/source-completion-2026-10-01/integration/registration-regional-comparison.json`,
        `${cache}/bodyparts3d-r4/converted`,
      ]);
      const invalidate = (path: string) => { if(path.includes('atlas-data/') || path.includes('work/evidence/')) { snapshots.clear(); composed=undefined; } };
      server.watcher.on('change', invalidate).on('unlink', invalidate).on('add', invalidate);
      server.httpServer?.once('close', () => {
        server.watcher.off('change', invalidate).off('unlink', invalidate).off('add', invalidate); snapshots.clear(); composed=undefined;
      });
      async function snapshot(namespace: string): Promise<Snapshot> {
        let pending=snapshots.get(namespace);
        if(!pending) {
          pending=(async()=>{
            const index=JSON.parse(await readFile(`${cache}/datasets/index.json`,'utf8')) as {datasets:Record<string,string>};
            const relative=index.datasets[namespace]; if(!relative)throw Error('unknown dataset');
            const registry=await realpath(resolve(cache,'datasets',relative));
            if(!registry.startsWith(`${cache}/datasets/`))throw Error('registry containment');
            const result=JSON.parse(await readFile(registry,'utf8')) as Snapshot;
            for(const input of result.dependencies) if(sha(await readFile(input.path))!==input.sha256) throw Error('stale compiled snapshot');
            for(const file of result.files) {
              const path=await realpath(file.path);
              if(!path.startsWith(cache+sep)||!/^[a-zA-Z0-9-]+$/.test(file.id))throw Error('file containment');
            }
            return result;
          })();
          snapshots.set(namespace,pending);pending.catch(()=>{if(snapshots.get(namespace)===pending)snapshots.delete(namespace);});
        }
        return pending;
      }
      async function compose(): Promise<ProjectionAssets> {
        if(composed)return composed;
        const pending=(async()=>{
          const [overlayBytes,supplementBytes,targetScopeBytes,supportContextBytes,nameAliasBytes]=await Promise.all([
            readFile(resolve(root,'atlas-data/overlays/za-local-integration.json')),
            readFile(resolve(root,'atlas-data/manifests/bodyparts3d-r4-t100-source-supplement.json')),
            readFile(resolve(root,'atlas-data/catalog/target-scope-t96.json')),
            readFile(resolve(root,'work/evidence/T78/reference/ta2-scope.json')),
            readFile(resolve(root,'atlas-data/terminology/learner-name-aliases-2026-10-06.json')),
          ]);
          const overlaySha256=sha(overlayBytes),supplementSha256=sha(supplementBytes),nameAliasSha256=sha(nameAliasBytes);
          const overlay=JSON.parse(overlayBytes.toString());
          const supplement=JSON.parse(supplementBytes.toString()) as SourceSupplement;
          const nameAliasDelta=JSON.parse(nameAliasBytes.toString());
          const targetScope=JSON.parse(targetScopeBytes.toString());
          const targetScopeSha256=sha(targetScopeBytes),supportContextSha256=sha(supportContextBytes);
          if(supportContextSha256!==targetScope.source.snapshotSha256)throw Error('changed frozen support context');
          if(Object.keys(supplement.inputSha256).sort().join('\n')!==[...T100_INPUTS].sort().join('\n'))throw Error('supplement input allowlist');
          for(const [relative,expected] of Object.entries(supplement.inputSha256)) {
            const path=resolve(root,relative); if(!path.startsWith(`${resolve(root)}${sep}`))throw Error('supplement input containment');
            if(sha(await readFile(path))!==expected)throw Error(`stale supplement input: ${relative}`);
          }
          const rightsPath='atlas-data/manifests/bodyparts3d-r4-t77/display-policy.json';
          if(supplement.rightsDecision.evidencePath!==rightsPath)throw Error('supplement rights evidence path');
          const rightsBytes=await readFile(resolve(root,rightsPath));
          const rightsPolicy=JSON.parse(rightsBytes.toString());
          const supplementRightsSha256=sha(rightsBytes);
          if(supplementRightsSha256!==supplement.rightsDecision.evidenceSha256||rightsPolicy.revision!==supplement.rightsDecision.decisionRevision
            ||supplement.rightsDecision.publicRedistribution!=='held'||supplement.rightsDecision.humanReview!=='not_performed'||supplement.rightsDecision.sourceOnly!==true)
            throw Error('supplement rights provenance');
          const associatedTargets=new Set(supplement.objects.map(object=>object.targetAssociation.targetId));
          if(supplement.summary.targetCount!==associatedTargets.size||supplement.summary.uniqueObjects!==supplement.objects.length
            ||supplement.summary.newCanonicalHaBindings!==0||!associatedTargets.size
            ||[...associatedTargets].some(id=>!targetScope.targets.some((target:any)=>target.id===id)))
            throw Error('supplement data-driven target/object scope');

          const [baseSnapshot,bpSnapshot]=await Promise.all([snapshot('za-c7010a9'),snapshot('bp3d-r4')]);
          const baseDataset=validateDataset(baseSnapshot.manifest);
          if(baseDataset.revision!==overlay.datasetRevision)throw Error('stale base integration');
          const t77Manifest=bpSnapshot.manifest;
          const bpChunks=new Map<string,any>((t77Manifest.chunks??[]).map((chunk:any)=>[chunk.id,chunk] as [string,any]));
          const registryFiles=new Map(bpSnapshot.files.map(file=>[file.id,file]));
          const sourceCatalog=JSON.parse(await readFile(resolve(root,'work/evidence/T78/source-elements.json'),'utf8')) as any[];
          const sourceById=new Map(sourceCatalog.map(row=>[row.id,row]));
          const objectKeys=new Set<string>();
          for(const chunk of supplement.chunks) {
            const sourceChunk=bpChunks.get(chunk.id); const file=registryFiles.get(chunk.id);
            if(!sourceChunk||!file||sourceChunk.sha256!==chunk.sha256||sourceChunk.bytes!==chunk.bytes
              ||file.sha256!==chunk.sha256||file.bytes!==chunk.bytes||sourceChunk.url!==chunk.url)
              throw Error(`supplement chunk lineage mismatch: ${chunk.id}`);
            const chunkBytes=await readFile(file.path);
            if(chunkBytes.length!==chunk.bytes||sha(chunkBytes)!==chunk.sha256)throw Error(`supplement chunk integrity: ${chunk.id}`);
            if(!chunk.selectionScoped||chunk.sourceNamespace!=='bp3d-r4'||chunk.level!=='overview')throw Error('supplement chunk request class');
          }
          for(const object of supplement.objects) {
            const fj=object.sourceIdentity.sourceElementFileId,source=sourceById.get(fj) as any;
            const sourceChunk=bpChunks.get(object.chunkId); const asset=sourceChunk?.assets?.find((candidate:any)=>candidate.id===fj);
            const decision=rightsPolicy.items?.[fj];
            if(objectKeys.has(object.sourceKey)||!/^BP3D4-FJ\d+M?$/.test(object.sourceKey)||!supplement.chunks.find(chunk=>chunk.id===object.chunkId)?.resources.includes(object.resource)
              ||!asset||asset.nodeId!==object.resource||asset.sourceSha256!==object.sourceIdentity.sourceSha256||asset.side!==object.side
              ||!decision||decision.state!=='allowed'||decision.sourceSha256!==asset.sourceSha256||decision.runtimeSide!==object.side
              ||decision.publicRedistribution!=='held'||decision.humanReviewed!==false)
              throw Error(`supplement object identity/policy mismatch: ${fj}`);
            if(object.sourceIdentity.compiledChunkSha256!==sourceChunk.sha256||object.sourceIdentity.projectFrame!==supplement.projectFrame
              ||object.sourceIdentity.sourceUnit!=='mm (exact OBJ Bounds(mm) header; T77 transformed output is metres)'
              ||object.sourceIdentity.pose!=='bodyparts3d-r4-static-reference'||!/^([a-f0-9]{64})$/.test(String(object.sourceIdentity.compiledMeshAccessorSha256)))
              throw Error(`supplement frame/geometry evidence mismatch: ${fj}`);
            const member=source?.conceptCandidates?.some((candidate:any)=>candidate.id===object.sourceIdentity.sourceFmaId);
            if(!member)throw Error(`supplement source FMA identity missing: ${fj}`);
            const targetId=object.targetAssociation.targetId;
            if(targetId!=='TA2:1282'&&!source.conceptCandidates.some((candidate:any)=>candidate.id===object.targetAssociation.targetFma))
              throw Error(`supplement target parent FMA relation missing: ${fj}`);
            if(targetId==='TA2:1282') {
              const group=supplement.sourceGroupMembership?.FMA16580;
              if(!group||group.targetId!==targetId||!group.memberElementFileIds.includes(fj)||group.extentStatus!=='source-declared-three-member-set; not global anatomy completeness')
                throw Error(`supplement exact group membership missing: ${fj}`);
            } else if(object.side!=='left'&&object.side!=='right') throw Error(`supplement side is not explicit: ${fj}`);
            objectKeys.add(object.sourceKey);
          }
          const decisionPath=await realpath(resolve(root,overlay.policy.rightsEvidence));
          if(!decisionPath.startsWith(resolve(root,'work/evidence')+sep))throw Error('base rights evidence containment');
          const rightsEvidenceSha256=sha(await readFile(decisionPath));
          if(rightsEvidenceSha256!==overlay.policy.rightsEvidenceSha256)throw Error('changed base local-use decision');
          const frozenTargetLexicon={
            sha256:targetScopeSha256,
            supportContext:{sha256:supportContextSha256,terms:JSON.parse(supportContextBytes.toString())},
            targets:targetScope.targets.map((target:any)=>({
              id:target.id,term:target.term,semanticKind:target.semanticKind,primaryOwner:target.primaryOwner,regionIds:target.regionIds,
              sourceAncestryIds:target.sourceAncestryIds,
              sourceCardinality:target.sourceCardinality?{explicitSourceSide:target.sourceCardinality.explicitSourceSide??null}:undefined,
            })),
          };
          const baseProjection=buildRuntimeIntegration(overlay,baseDataset,overlaySha256,rightsEvidenceSha256,frozenTargetLexicon);
          const composedOverlaySha=sha(Buffer.from([overlaySha256,supplementSha256,nameAliasSha256].join('\n')));
          const namedBaseProjection=applyLearnerNameAliasDelta(baseProjection,baseDataset,nameAliasDelta,
            value=>sha(Buffer.from(value)),composedOverlaySha);
          const dataset=composeSupplementDataset(baseDataset,supplement);
          const partofPath='atlas-data/source-cache/bodyparts3d-r4/metadata/partof_element_parts.txt';
          const partofBytes=await readFile(resolve(root,partofPath));
          const groupRows=new Map<string,string[]>();
          for(const line of partofBytes.toString().split(/\r?\n/).filter(Boolean)) {
            const [groupId,,fj]=line.split('\t'); if(!groupId||!fj)continue;
            const rows=groupRows.get(groupId)??[];rows.push(fj);groupRows.set(groupId,rows);
          }
          const relationEvidence=resolveSupplementTargetRelations(supplement,{
            targets:targetScope.targets,sourceElements:sourceCatalog,evidenceHashes:{...supplement.inputSha256,
              [rightsPath]:supplementRightsSha256,[partofPath]:sha(partofBytes)},
          });
          for(const [groupId,group] of Object.entries(supplement.sourceGroupMembership??{})) {
            if(groupRows.get(groupId)?.sort().join('\n')!==[...group.memberElementFileIds].sort().join('\n'))
              throw Error(`supplement group relation changed against exact PART-OF table: ${groupId}`);
          }
          const composedRightsSha=sha(Buffer.from([rightsEvidenceSha256,supplementRightsSha256].join('\n')));
          const projection=composeSupplementRuntime(namedBaseProjection,dataset,supplement,targetRoutesBySource(relationEvidence),composedOverlaySha,composedRightsSha);
          const nerve = await loadNerveAssets(root);
          const combined = composeNerveScene(dataset, projection, nerve.manifest, nerve.registry, nerve.dataset, nerve.rights,
            sha(Buffer.from([composedOverlaySha, nerve.sha256].join('\n'))), sha(Buffer.from([composedRightsSha, nerve.rightsSha256].join('\n'))));
          return { dataset: combined.dataset, datasetBody: Buffer.from(JSON.stringify(combined.dataset)),
            runtimeBody: Buffer.from(JSON.stringify(combined.integration)), key: nerve.sha256, nerveFiles: nerve.files };
        })();
        composed=pending; pending.catch(()=>{if(composed===pending)composed=undefined;}); return pending;
      }
      server.middlewares.use(async (req,res,next) => {
        const path=req.url?.split('?')[0]??'';
        if(path==='/__atlas/integration.json'||path==='/__atlas/datasets/human-atlas-local/manifest.json') {
          try {
            const assets=await compose(); const body=path==='/__atlas/integration.json'?assets.runtimeBody:assets.datasetBody;
            res.setHeader('Cache-Control','no-store');res.setHeader('Content-Type','application/json');res.setHeader('Content-Length',String(body.byteLength));res.end(body);
          }catch(error){console.error('Local whole-body composition failed',error);res.statusCode=503;res.end(path==='/__atlas/integration.json'?'Local integration unavailable':'Local combined dataset unavailable');}
          return;
        }
        let namespace='',file='';
        if(path.startsWith('/__atlas/body/')){namespace='bp3d-r4';file=path.slice('/__atlas/body/'.length);}
        else if(path.startsWith('/__atlas/datasets/')) {
          const parts=path.slice('/__atlas/datasets/'.length).split('/');if(parts.length===2)[namespace,file]=parts;
        } else {next();return;}
        res.setHeader('Cache-Control','no-store');
        if(!/^[a-z0-9-]+$/.test(namespace)||!/^(manifest\.json|[a-zA-Z0-9-]+\.glb)$/.test(file)){res.statusCode=404;res.end();return;}
        try {
          const data=await snapshot(namespace);
          if(file==='manifest.json'){res.setHeader('Content-Type','application/json');res.end(JSON.stringify(data.manifest));return;}
          const nerveFiles = namespace === 'za-c7010a9' ? (await compose()).nerveFiles : [];
          const entry=[...data.files, ...nerveFiles].find(candidate=>`${candidate.id}.glb`===file);if(!entry){res.statusCode=404;res.end();return;}
          const bytes=await readFile(entry.path);if(bytes.length!==entry.bytes||sha(bytes)!==entry.sha256)throw Error('chunk integrity');
          if(req.destroyed)return;
          // URLs may survive recompilation: revalidate the actual verified content, never cache blindly.
          const etag=`"${entry.sha256}"`;
          res.setHeader('Cache-Control','private, no-cache');res.setHeader('ETag',etag);
          if(req.headers?.['if-none-match']===etag){res.statusCode=304;res.end();return;}
          res.setHeader('Content-Type','model/gltf-binary');res.setHeader('Content-Length',String(bytes.length));res.end(bytes);
        }catch{res.statusCode=503;res.end('Local compiled anatomy assets unavailable; prepare and validate the dataset.');}
      });
    },
  };
}
