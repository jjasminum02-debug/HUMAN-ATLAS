/** Explicit, temporary no-login sharing of a verified snapshot, never the repository/dev server. */
import {readFile,writeFile,mkdir,realpath,stat} from 'node:fs/promises';
import {resolve,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawn} from 'node:child_process';
import {openLocalDelivery} from './localDeliveryServer.mjs';
const web=fileURLToPath(new URL('../',import.meta.url));
const args=process.argv.slice(2);let port=5192;
for(let i=0;i<args.length;i++){
  if(args[i]==='--port'){port=Number(args[++i]);if(!Number.isInteger(port)||port<1024||port>65535)throw Error('Invalid port.');}
  else throw Error('Unknown option: '+args[i]);
}
const pointer=JSON.parse(await readFile(resolve(web,'dist-local/CURRENT.json'),'utf8'));
if(!/^[a-zA-Z0-9-]+$/.test(pointer.snapshotDirectory))throw Error('Invalid snapshot pointer.');
const root=await realpath(resolve(web,'dist-local')),snapshot=await realpath(resolve(root,pointer.snapshotDirectory));
if(!snapshot.startsWith(root+sep))throw Error('Snapshot escaped its output directory.');
const binary=resolve(web,'.share-tools/cloudflared');await stat(binary);
const app=await openLocalDelivery(snapshot);
if(app.manifestSha256!==pointer.manifestSha256)throw Error('Snapshot hash differs.');
await new Promise((ok,fail)=>{app.server.once('error',fail);app.server.listen(port,'127.0.0.1',ok);});
const statusFile=resolve(web,'.share-tools/share-status.json');
const status={snapshot:app.manifest.snapshotId,manifestSha256:app.manifestSha256,url:null,state:'connecting',requiresLogin:false,temporary:true,publicRedistribution:'held',humanReview:'not_performed',startedAt:new Date().toISOString()};
await mkdir(resolve(web,'.share-tools'),{recursive:true});
await writeFile(statusFile,JSON.stringify(status,null,2)+'\n');
const tunnel=spawn(binary,['tunnel','--no-autoupdate','--protocol','http2','--url','http://127.0.0.1:'+port],{stdio:['ignore','pipe','pipe']});
let pending='', writes=Promise.resolve();
async function line(value){
  const url=value.match(/https:\/\/[a-z0-9-]+\.trycloudflare\.com/);
  if(url){status.url=url[0];console.log('공유 링크: '+status.url+' (로그인 없음 · 이 실행이 유지되는 동안 사용 가능)');}
  if(value.includes('Registered tunnel connection')){status.state='connected';console.log('공유 연결이 열렸습니다.');}
  if(value.includes('ERR'))console.error(value.trim());
  await writeFile(statusFile,JSON.stringify(status,null,2)+'\n');
}
function output(chunk){pending+=chunk.toString();const lines=pending.split('\n');pending=lines.pop()??'';for(const value of lines)writes=writes.then(()=>line(value));}
tunnel.stdout.on('data',output);tunnel.stderr.on('data',output);
let stopping=false;
function stop(){if(stopping)return;stopping=true;tunnel.kill('SIGTERM');app.server.close();}
tunnel.on('error',error=>{console.error(error.message);stop();process.exitCode=1;});
tunnel.on('exit',async code=>{await writes;status.state='stopped';await writeFile(statusFile,JSON.stringify(status,null,2)+'\n');app.server.close();if(!stopping&&code)process.exitCode=code;});
for(const signal of ['SIGINT','SIGTERM'])process.once(signal,stop);
console.log('검증된 모형 패키지만 임시 공유합니다. 종료는 Ctrl+C. 노트북 잠자기/종료 시 링크가 중단됩니다.');
