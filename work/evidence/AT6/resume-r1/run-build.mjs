import {readFileSync,writeFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {resolve,dirname} from 'node:path';
const evidence=dirname(fileURLToPath(import.meta.url)),web=resolve(evidence,'../../../../atlas-web');
const pkg=JSON.parse(readFileSync(resolve(web,'package.json'),'utf8')),steps=pkg.scripts.build.split(' && '),results=[];
for(const command of steps){const r=spawnSync(command,{cwd:web,shell:true,encoding:'utf8',env:{...process.env,PATH:resolve(web,'node_modules/.bin')+':/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:'+process.env.PATH},maxBuffer:8*1024*1024});results.push({command,exitCode:r.status,stdout:r.stdout,stderr:r.stderr});writeFileSync(resolve(evidence,'build-r6.json'),JSON.stringify(results,null,2)+'\n');if(r.status!==0){console.log(command,r.status);process.exit(r.status??1);}}
console.log('All',steps.length,'package build steps passed');
