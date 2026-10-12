"""Run the package's checks against an isolated build output, preserving existing dist/WIP."""
from pathlib import Path
import json,subprocess,shlex,sys
R=Path(__file__).resolve().parents[4];E=Path(__file__).parent;W=R/'atlas-web'
node='/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
revision=sys.argv[1] if len(sys.argv)>1 else 'r1';assert revision in ['r1','r2','r3','r4','r5','r6','r7']
output=E/'build-output'/revision;commands=json.loads((W/'package.json').read_text())['scripts']['build'].split(' && ');results=[]
for i,command in enumerate(commands):
 args=shlex.split(command);note=None
 if args[0]=='node':args[0]=node
 if args[0]=='tsc':args=[node,str(W/'node_modules/typescript/bin/tsc'),*args[1:]]
 if args[0]=='vite':args=[node,str(W/'node_modules/vite/bin/vite.js'),*args[1:],'--outDir',str(output)];note='isolated output; original dist untouched'
 if command.startswith('node scripts/auditLearnerCardDistribution.mjs') or command.startswith('node scripts/checkLazyFeatures.mjs'):
  path=W/args[1];source=path.read_text().replace('import.meta.url',json.dumps(path.as_uri()))
  if path.name=='auditLearnerCardDistribution.mjs':
   assert 'const bundleRoot = resolve(webRoot, "dist");' in source
   source=source.replace('const bundleRoot = resolve(webRoot, "dist");','const bundleRoot = '+json.dumps(str(output))+';')
  else:
   assert "const dist = new URL('../dist/', " in source
   begin=source.index('const dist = ');end=source.index(';',begin)+1
   source=source[:begin]+'const dist = new URL('+json.dumps(output.as_uri()+'/')+');'+source[end:]
  args=[node,'--input-type=module','--eval',source];note='same saved checker read-only in memory, only build output root substituted'
 p=subprocess.run(args,cwd=W,capture_output=True,text=True);results.append({'command':command,'outputRootOverride':note,'exitCode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 (E/f'build-step-{i+1:02d}-{revision}.log').write_text(p.stdout+p.stderr)
 (E/f'build-final-{revision}.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
 print(i+1,p.returncode,command,flush=True)
 if p.returncode:raise SystemExit(p.returncode)
print('PASS: all',len(commands),'package build checks; existing dist preserved')
