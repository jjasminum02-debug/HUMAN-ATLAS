import pathlib,json,sys,hashlib,numpy as np
R=pathlib.Path(__file__).resolve().parents[4];O=pathlib.Path(__file__).parent;sys.path[:0]=[str(R/'work/tools'),str(R/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from verify_glb_interpolation import read_glb,channel_data,node_positions
load=lambda p:json.loads((R/p).read_text());sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest();save=lambda p,v:(R/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
reg=load('atlas-data/motion/authoring/registry.json');ac=load('atlas-data/motion/t66-priority-action-acceptance.json');b=load('atlas-data/motion/motion-learning.json')
for re in reg['records']:
 if not re['id'].startswith('T66-PRIORITY-S05-') or 'KNEE' in re['id']:continue
 ar=load(re['path']);kind=ar['sourceFamilyId'].split('-')[1];side=ar['side'];d=O/('adopted-'+kind+'-'+side);p=json.loads((d/'input.json').read_text());out=load(ar['actionOutcomePath']);asset=next(a for a in b['motionAssets'] if a.get('sourceBinding',{}).get('sourceFamilyId')==ar['sourceFamilyId']);raw,doc,buf=read_glb(R/asset['uri']);tr=channel_data(doc,buf);nodes={n['extras']['sourceKey']:i for i,n in enumerate(doc['nodes'])}
 for row in out:
  e=next(e for e in p['members'] if e['sourceKey']==row['sourceKey']);fi=e['fixedVertexIndices'];mi=e['movingVertexIndices'];poses=[node_positions(doc,buf,tr,nodes[row['sourceKey']],float(t)) for t in np.linspace(0,p['family']['durationSeconds'],49)];span=lambda w:float(np.linalg.norm(w[fi].mean(0)-w[mi].mean(0)));short=(span(poses[0])-span(poses[-1])) if kind=='lev' else span(poses[-1])-span(poses[0]);assert short>.0005,(kind,side,short);row.update(kind=kind.upper(),shorteningMetres=short,inspectedPoseSamples=49)
 save(ar['actionOutcomePath'],out)
 for dep in ar['verificationDependencies']:dep['sha256']=sha(dep['path'])
 save(re['path'],ar);re['sha256']=sha(re['path'])
 for row in ac['rows']:
  if row['authoringPath']==re['path']:row['authoringSha256']=re['sha256'];row['outcomeSha256']=sha(row['outcomePath'])
save('atlas-data/motion/authoring/registry.json',reg);save('atlas-data/motion/t66-priority-action-acceptance.json',ac)
