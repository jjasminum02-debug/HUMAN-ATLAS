"""Reproduce T78 planning evidence only. Never mutates assets, app or registry."""
import json, hashlib, re, sys
from pathlib import Path
from collections import Counter, defaultdict
ROOT=Path(__file__).resolve().parents[3]; OUT=ROOT/'work/evidence/T78'
sys.path.insert(0,str(ROOT/'atlas-data/tools'))
import ingest_bodyparts3d_r4 as bp

def write(name,value):
 (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
terms=json.loads((OUT/'reference/ta2-scope.json').read_text()); by={x['id']:x for x in terms}
def ancestry(r):
 result=[]
 while r:
  result.append(r['id']);r=by.get(r.get('parent'))
 return result

def eng(r):return r['term'].get('en',r['term'].get('en_US',r['term'].get('en_GB','')))
# Explicit non-musculus named muscle lexemes; names remain verbatim TA2 facts.
lexemes=('levator ','depressor ','corrugator ','bucinator','buccinator','tensor ','masseter','platysma','constrictor ','erector ','rotatores ','levatores ','diaphragma','cremaster','sphincter ','compressor ','pronator ','flexor ','extensor ','supinator','abductor ','adductor ','iliopsoas','psoas ')
groups={2041,2054,2055,2116,2126,2176,2192,2247,2248,2254,2257,2262,2267,2272,2276,2280,2284,2290,2294,2308,2402,2403,2451,2463,2470,2476,2477,2490,2494,2495,2511,2519,2593,2597,2603,2609,2613,2626,2637,2643,2651,2654,2655,2664,2669}
regionroots={2039:'head',2145:'neck',2224:'back',2298:'thorax',2355:'abdomen-lumbar',2396:'pelvis-perineum',2449:'upper-limb',2451:'shoulder-scapular',2591:'gluteal-hip',2597:'gluteal-hip',2603:'gluteal-hip',2609:'thigh',2626:'thigh',2637:'thigh',2643:'leg',2651:'leg',2654:'leg',2669:'foot'}
def regions(r):
 a=ancestry(r)
 result=next(([regionroots[x]] for x in a if x in regionroots),[])
 extra={2230:['back','shoulder-scapular','neck'],2231:['back','shoulder-scapular'],2234:['neck','shoulder-scapular'],2593:['abdomen-lumbar','gluteal-hip'],2595:['abdomen-lumbar','gluteal-hip'],2605:['pelvis-perineum','gluteal-hip']}
 return sorted(set(result+extra.get(r['id'],[])))
rawmuscle=set()
for r in terms:
 la=r['term'].get('la','')
 if 1974 in ancestry(r) and r['id']>=2039 and (la.startswith(('musculus ','musculi ')+lexemes) or r['id'] in groups):rawmuscle.add(r['id'])
bonewords={'sternum','clavicula','scapula','humerus','radius','ulna','femur','patella','tibia','fibula','talus','calcaneus','vomer','malleus','incus','stapes','atlas','axis','mandibula','maxilla','sacrum','coccyx'}
classification={}
for r in terms:
 i=r['id'];la=r['term'].get('la','');a=ancestry(r)
 if i in rawmuscle:
  kind='muscle_group' if i in groups else ('serial_muscle_family' if la.startswith(('musculi ','rotatores ','levatores ')) else 'named_muscle')
 elif 1974 in a and i>=2039 and any(x in rawmuscle for x in a[1:]) and la.startswith(('pars ','partes ','caput ','venter ','fasciculus ','crus ','hemidiaphragma')):kind='muscle_part'
 elif 352 in a and (la in bonewords or la.startswith(('os ','ossa ','vertebra ','vertebrae ','costa ','costae ','phalanx ','phalanges '))):kind='bone_or_bone_series'
 else:kind='supporting_nomenclature_not_geometry_target'
 classification[i]=kind
# Source roots are edition-specific surface sets, never a whole-human denominator.
tables=bp.load_tables(ROOT/'atlas-data/source-cache/bodyparts3d-r4/metadata'); edges=defaultdict(set)
for p,_,c,_ in tables['isaInclusion']:edges[p].add(c)
def closure(root):
 seen=set();todo=[root]
 while todo:
  x=todo.pop()
  if x not in seen:seen.add(x);todo.extend(edges[x])
 return seen
muscleconcepts=set().union(*(closure(r) for r in ['FMA5022','FMA10474','FMA85453']));boneconcepts=closure('FMA5018')
def elements(concepts):return {r[2] for r in tables['isaCompoundElements'] if r[0] in concepts}
ms=elements(muscleconcepts);bs=elements(boneconcepts)
manifest=ROOT/'atlas-data/source-cache/bodyparts3d-r4/converted/t77/manifest.json'
m=json.loads(manifest.read_text());runtime={a['id']:a for c in m['chunks'] for a in c['assets']}
ms|={i for i,a in runtime.items() if a['layer']=='muscle'};bs|={i for i,a in runtime.items() if a['layer']=='bone'}
def norm(x):return re.sub(r'[^a-z0-9]','',re.sub(r'\b(muscle|muscles|left|right)\b','',x.lower()))
sourceNames=defaultdict(list);sourceConcepts=defaultdict(list)
for cid,name,sid in tables['isaCompoundElements']:
 if sid in ms|bs:

  if cid in muscleconcepts|boneconcepts:sourceConcepts[sid].append({'id':cid,'name':name})
  if cid in muscleconcepts|boneconcepts:sourceNames[norm(name)].append(sid)
# Matching is merely a lexical candidate set. No semantic/canonical approval.
ledger=[];targets=[]
for r in terms:
 kind=classification[r['id']]
 ledger.append({'ta2Id':r['id'],'kind':kind,'name':eng(r)})
 if kind=='supporting_nomenclature_not_geometry_target':continue
 names=[eng(r)]+r.get('synonyms',{}).get('en',[])
 candidates=sorted({sid for n in names for sid in sourceNames.get(norm(n),[])})
 row={'id':f"TA2:{r['id']}",'name':eng(r),'latin':r['term'].get('la'),'kind':kind,'parent':r.get('parent'),'inconstant':r.get('inconstant')=='true','regionCandidates':regions(r),'regionState':'planning_needs_context_audit','sideInstances':None,'countingRule':'named target record; not an individual side-specific muscle count','sourceCandidates':candidates,'correspondence':'lexical_candidate_only' if candidates else 'unresolved_no_exact_correspondence','states':{'geometry':'candidate_in_scene' if any(x in runtime for x in candidates) else 'candidate_not_acquired' if candidates else 'unresolved','side':'not_reconciled','frame':'not_reconciled','binding':'not_reconciled','threeNames':'not_reconciled','originInsertion':'not_reconciled','function':'not_reconciled','animation':'not_reconciled','humanReview':False,'rights':'no_new_permission'}}
 if r['id']==2231:row['states']['geometry']='missing';row['priorEvidence']='T94:no_exact_source_found';row['sourceCandidates']=[]
 targets.append(row)
sources=[]
for sid in sorted(ms|bs):
 a=runtime.get(sid)
 sources.append({'id':sid,'layer':'muscle' if sid in ms else 'bone','conceptCandidates':sourceConcepts[sid],'state':'in_scene' if a else 'not_acquired_or_integrated','runtime':None if not a else {k:a.get(k) for k in ['sourceSha256','regions','side','defaultVisible','pickState','stableIds','holdReasons','publicRedistribution','humanReviewed']}})
write('classification-ledger.json',ledger);write('targets.json',targets);write('source-elements.json',sources)
summary={'nomenclatureSnapshotTerms':len(terms),'targetRecords':len(targets),'targetKinds':dict(Counter(t['kind'] for t in targets)),'classificationStatus':'provisional_requires_semantic_reconciliation','wholeBodyIndividualMuscleDenominator':None,'namedTargetRecordDenominator':len(targets),'sourceElementDenominator':len(sources),'muscleSourceElements':len(ms),'boneSourceElements':len(bs),'runtimeSourceNodes':len(runtime),'missingMuscleSourceIds':sorted(ms-runtime.keys()),'missingBoneSourceIds':sorted(bs-runtime.keys()),'latissimus':'missing','visualCoverage':'partial','notClaims':['TA2 term is not a mesh','Lexical match is not a binding','Full source edition coverage is not full human anatomy coverage','Parts, groups, bilateral instances and serial families are not additive muscle counts'],'inputs':{'manifest':{'path':str(manifest.relative_to(ROOT)),'sha256':sha(manifest)},'metadata':{str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'atlas-data/source-cache/bodyparts3d-r4/metadata').glob('*')) if p.is_file()},'ta2SnapshotSha256':sha(OUT/'reference/ta2-scope.json')}}
write('inventory-summary.json',summary)
write('region-diagnostic.json',{'notBrowserVerification':True,'cause':'Single route.regionId and asymmetric runtime region membership; not missing scapula mesh','assets':{i:runtime[i] for i in ['FJ3279','FJ3384','FJ3237','FJ3362']},'appReferences':['atlas-web/src/ui/App.tsx:chooseRegion','atlas-web/src/domain/regionNavigation.ts','atlas-web/src/viewer/wholeBody/contract.ts'],'requiredChange':'Product context overlay and multi-region OR union; preserve historic source regions and layer-off/held behavior'})
print(json.dumps(summary,ensure_ascii=False,indent=2)[:5000])
