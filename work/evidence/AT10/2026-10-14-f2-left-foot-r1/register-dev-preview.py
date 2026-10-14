"""Register one explicit F2 candidate in the existing DEV-only loader."""
from pathlib import Path
import json,hashlib,struct,array,sys
R=Path.cwd();A=R/'atlas-data/anatomy/skin/at10-f2-left-foot-r1';rev=sys.argv[1];raw=(A/f'skin-candidate-{rev}.glb').read_bytes();jl=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+jl]);start=28+jl
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pos=g['bufferViews'][g['accessors'][0]['bufferView']];idx=g['bufferViews'][g['accessors'][3]['bufferView']];ind=array.array('H');ind.frombytes(raw[start+idx['byteOffset']:start+idx['byteOffset']+idx['byteLength']]);ints=array.array('I',ind)
top=hashlib.sha256(raw[start+pos['byteOffset']:start+pos['byteOffset']+pos['byteLength']]+ints.tobytes()).hexdigest();mapping=h(A/f'source-to-derived-{rev}.json');sha=h(A/f'skin-candidate-{rev}.glb')
p=R/'atlas-web/src/viewer/skin/skinReviewAsset.ts';s=p.read_text();assert f"requested==='{rev}'" not in s
s=s.replace("const revision=requested===",f"const revision=requested==='{rev}'||requested===",1).replace("const candidate=revision===",f"const candidate=revision==='{rev}'?{{\n    url:(await import('../../../../atlas-data/anatomy/skin/at10-f2-left-foot-r1/skin-candidate-{rev}.glb?url')).default,\n    sha256:'{sha}',\n    topologySha256:'{top}',mappingSha256:'{mapping}',\n  }}:revision===",1);p.write_text(s)
print({'revision':rev,'glbHash':sha,'emittedTopologyHash':top,'mappingHash':mapping,'DEVOnly':True})
