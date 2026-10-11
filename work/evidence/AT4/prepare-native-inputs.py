"""Data configuration only; geometry compilation stays in the AT2/AT3 shared tool."""
from pathlib import Path
import ast,hashlib,json,struct
import numpy as np
R=Path(__file__).resolve().parents[3];A=R/'work/evidence/acupoint-AC1';E=Path(__file__).parent
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
rows={r['sourceKey']:r for r in read(A/'runtime-integration.json')['objects'] if r['sourceKey'].startswith('ZA-c7010a9-')}
cache=R/'atlas-data/source-cache/datasets/za';meshes={};inputs={}
tree=ast.parse((A/'build_carrier.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='world');exec(compile(ast.Module(body=[fn],type_ignores=[]),'AC1-world','exec'),globals())
def find(name,side):
 ks=[k for k,r in rows.items() if r['names']['en']==name and r['side']==side];assert len(ks)==1,(name,side);return ks[0]
def names(pattern,side):return [k for k,r in rows.items() if pattern(r['names']['en']) and r['side']==side and r['kind'] in ['muscle','bone'] and not r['hardHoldReasons']]
def make(ident,family,side,ks,axes,dimension,steps,angles,offset,limit,label,domain=None):
 v=np.concatenate([world(k)[0][np.unique(world(k)[1])] for k in axes]);lo,hi=v[:,dimension].min(),v[:,dimension].max();rg=domain or [float(lo+.0003),float(hi-.0003)]
 return {'id':ident,'family':family,'side':side,'sources':ks,'axis':axes,'range':rg,'dimension':dimension,'steps':steps,'angles':angles,'clearanceMetres':offset,'limit':limit,'cuts':[],'labels':[label],'component':ident,'landmarkBasis':'independent native component/bone section; no palpation/cun/acupoint approval'}
regions=[];probeinputs=[]
head=names(lambda n:True,None);head=[k for k,r in rows.items() if 'head' in r['regionIds'] and r['kind'] in ['muscle','bone'] and not r['hardHoldReasons']]
axes=[find('Frontal bone',None),find('Occipital bone',None),find('Mandible',None)]+[find('Parietal bone',s) for s in ['right','left']]
regions.append(make('head','head','midline',head,axes,1,32,32,.006,.17,'머리·얼굴'))
ordinals=['first','second','third','fourth','fifth'];labels=['엄지','둘째','셋째','넷째','다섯째']
for side,ko in [('right','오른'),('left','왼')]:
 palm=names(lambda n:'of hand' in n or 'metacarpal' in n or n in ['Trapezium bone','Trapezoid bone','Capitate bone','Hamate bone','Pisiform bone','Scaphoid bone','Lunate bone','Triquetrum bone','Abductor pollicis brevis','Opponens pollicis muscle'],side)
 axes=[find(n+' metacarpal bone',side) for n in ['First','Second','Third','Fourth','Fifth']]
 rg=[max(world(k)[0][:,1].min() for k in axes)+.0003,max(world(k)[0][:,1].max() for k in axes)-.0003]
 regions.append(make('hand-'+side,'hand',side,palm,axes,1,12,20,.003,.075,ko+'손·손바닥',rg))
 for i,ord in enumerate(ordinals):
  ks=names(lambda n,ord=ord:('phalanx of '+ord+' finger of hand') in n,side)
  regions.append(make('finger-'+side+'-'+str(i+1),'hand',side,ks,ks,1,10,12,.002,.02,ko+'손 '+labels[i]))
 foot=names(lambda n:True,side);foot=[k for k in foot if 'foot' in rows[k]['regionIds'] and 'phalanx' not in rows[k]['names']['en']]
 axes=[find(n+' metatarsal bone',side) for n in ['First','Second','Third','Fourth','Fifth']]+[find('Calcaneus',side)]
 regions.append(make('foot-'+side,'foot',side,foot,axes,2,20,20,.003,.075,ko+'발·발바닥'))
 for i,ord in enumerate(ordinals):
  ks=names(lambda n,ord=ord:('phalanx of '+ord+' finger of foot') in n,side)
  regions.append(make('toe-'+side+'-'+str(i+1),'foot',side,ks,ks,2,7,12,.0015,.02,ko+'발 '+labels[i]+'발가락'))
# Split actual nail/perionyx connected components; no space-bridging or mirror.
for path in [A/'source-probe.json',R/'work/evidence/acupoint-AC2/left-source-probe.json',E/'special-source-probe.json']:
 p=read(path)
 for obj in p['objects']:
  if not obj.get('triangles'):continue
  v=np.array(obj['positions']);t=np.array(obj['indices'],dtype='<u4');side='left' if obj['name'].endswith('.l') else 'right' if obj['name'].endswith('.r') else 'midline'
  graph=[set() for _ in v]
  for tri in t:
   for a,b in [(tri[0],tri[1]),(tri[1],tri[2]),(tri[2],tri[0])]:graph[a].add(int(b));graph[b].add(int(a))
  remain=set(int(i) for i in np.unique(t));components=[]
  while remain:
   todo=[min(remain)];comp=set()
   while todo:
    i=todo.pop()
    if i in comp:continue
    comp.add(i);todo.extend(graph[i]-comp)
   remain-=comp;components.append(comp)
  for ci,comp in enumerate(components):
   tids=[i for i,tri in enumerate(t) if int(tri[0]) in comp];cv=v[list(comp)];perineum='region.' in obj['name'].lower()
   ident=(('perineum-anal' if obj['name'].startswith('Anal') else 'perineum-urogenital')+'-'+side if perineum else 'tongue' if obj['name']=='Tongue' else ('toenail' if '(foot)' in obj['name'] else 'nail')+('-fold' if 'Perionyx' in obj['name'] else '-plate')+'-'+side)+'-'+str(ci)
   k='PROBE-'+ident;meshes[k]=(v,t[tids]);probeinputs.append({'key':k,'path':str(path.relative_to(R)),'sha256':sha(path.read_bytes()),'object':obj['name'],'side':side,'triangleIds':tids,'component':ci})
   dim=2 if obj['name']=='Tongue' or '(foot)' in obj['name'] else 1
   family='perineum' if perineum else 'oral' if obj['name']=='Tongue' else 'nail'
   regions.append(make(ident,family,side,[k],[k],dim,12 if family in ['oral','perineum'] else 6,20 if family in ['oral','perineum'] else 12,.002 if perineum else .001 if family=='oral' else .0007,.20 if perineum else .06 if family=='oral' else .03,'회음 구역 기준 표본' if perineum else '혀 기준 표본' if family=='oral' else ('왼쪽 ' if side=='left' else '오른쪽 ')+('발톱' if '(foot)' in obj['name'] else '손톱')+(' 주름' if 'Perionyx' in obj['name'] else ' 판')+' '+str(ci+1)))
x={'schemaVersion':1,'method':'AT2 native envelope, AT3 common compiler','probeInputs':probeinputs,'regions':regions,'unsupportedRegions':['true_skin','oral_gum_frenulum_mucosa','perineal_skin','finger_toe_pads','deforming_pose'],'noMirror':True,'pointsAuthored':0}
x['accessFile']='atlas-data/acupoints/carriers/education-r1/access.json'
P=R/'atlas-data/acupoints/carriers/education-special-inputs.json';P.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
print('regions',len(regions),'probe components',len(probeinputs))
