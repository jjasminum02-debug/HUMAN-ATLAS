"""Explicit source-taxonomy overlay. Never edits T96/T98/T99 source/freeze."""
import hashlib,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).parent
read=lambda p:json.loads((ROOT/p).read_text())
sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
source=read('work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json')
scope=read('atlas-data/catalog/target-scope-t96.json')
metadata=json.loads((OUT/'source-metadata.json').read_text())
manifest=read('atlas-data/source-cache/datasets/za/compiled/manifest.json')
objects={o['name']:o for o in metadata['objects']};collections={c['name']:c for c in metadata['collections']}
# Exact source vocabulary normalization, not fuzzy or substring similarity.
def base(s):return re.sub(r'\.(?:l|r|g)$','',s).strip()
def norm(s):return re.sub(r'\s+',' ',re.sub(r'\bmuscles?\b','',re.sub(r'[()\[\],]',' ',base(s).lower()))).strip()
targetindex={}
for t in scope['targets']:
 targetindex.setdefault(norm(t['term']['english']),[]).append(t)
for t in scope['targets']:
 aliases=t['term'].get('sourceSynonyms',{})
 # Only explicitly labelled English synonyms; never reuse Latin strings as English equivalence.
 for k,v in aliases.items():
  if 'en' in k.lower():
   for alias in v if isinstance(v,list) else [v]:
    if isinstance(alias,str):targetindex.setdefault(norm(alias),[]).append(t)

def ancestry(name):
 result=[];seen=set()
 while name and name not in seen:
  seen.add(name);result.append(name);name=objects.get(name,{}).get('parent')
 return result

# Region mapping uses source collection membership and explicit existing TA2 regional targets.
REGIONS={'Head':'head','Neck':'neck','Back':'back','Thorax':'thorax','Abdomen':'abdomen-lumbar',
'Pelvis':'pelvis-perineum','Perineum':'pelvis-perineum','Muscles of perineum':'pelvis-perineum',
'Perineal muscles':'pelvis-perineum','Muscles of gluteal region':'gluteal-hip','Gluteal region':'gluteal-hip',
'Muscles of thigh':'thigh','Muscles of leg':'leg','Muscles of foot':'foot','Bones of foot':'foot',
'Bones of upper limb':'upper-limb','Muscles of upper limb':'upper-limb','Bones of pectoral girdle':'shoulder-scapular',
'Bones of shoulder girdle':'shoulder-scapular','Left upper limb':'upper-limb','Right upper limb':'upper-limb'}
# These are explicit product context additions, not new anatomical membership claims.
CONTEXT={'Scapula':['shoulder-scapular','upper-limb'],'Clavicle':['shoulder-scapular','upper-limb'],
'Sacrum':['abdomen-lumbar','pelvis-perineum','back'],'Hip bone':['pelvis-perineum','gluteal-hip']}
entries=read('atlas-data/terminology/learning-names.json')['entries'];names={norm(x['english']):x for x in entries}
canonical=read('atlas-data/catalog/canonical-catalog.json')['entities']
ha_to_ta={}
for c in canonical['muscleConcepts']+canonical.get('muscleParts',[])+canonical['structures']:
 for ref in c.get('standardRefs',[]):
  match=re.search(r'row\s+(\d+)',ref.get('identifier',''))
  if match:ha_to_ta[c['id']]='TA2:'+match.group(1)
namebytarget={ha_to_ta[n['id']]:n for n in entries if n['id'] in ha_to_ta}
# Newly checked dictionary names are independently cited; absence is null, not a generated translation.
newnames={'scapula':('견갑골','어깨뼈','https://www.kmle.co.kr/search.php?Search=scapula'),
'humerus':('상완골','위팔뼈','https://www.kmle.co.kr/search.php?Search=humerus'),
'sacrum':('천골','엉치뼈','https://m.kmle.co.kr/search.php?Search=sacrum')}
bonenames={norm(x['english']):x for x in read('atlas-data/terminology/bone-name-overlay-t42.json')['entries']}
records=[];joins={t['id']:[] for t in scope['targets']};audit=[]
for i in source['objects']:
 o=objects[i['name']];assert o['parent']==i['parent'] and sorted(o['collections'])==i['collections']
 chain=ancestry(i['name']);kind='bone' if i['kind']=='skeletal_surface' else 'muscle' if i['kind']=='muscle_surface_or_part' else 'accessory'
 if any(word in i['name'].lower() for word in ['retinaculum','ligament','aponeurosis','tendinous','tarsus','tendon','iliotibial tract','linea alba','trochlea','cartilage','tooth','canine','incisor','premolar','molar','sinus of','cells of ethmoid']):kind='accessory'
 labels=set(i['collections'])|{base(x) for x in chain} # do not inherit regions through nerve cross-references
 matches=[]
 for label in chain if kind!='accessory' else []:
  candidates={t['id']:t for t in targetindex.get(norm(label),[]) if (t['semanticKind'].startswith('bone') if kind=='bone' else 'muscle' in t['semanticKind'])}
  if len(candidates)==1:
   t=next(iter(candidates.values()));matches.append((t,label))
 # A named match is accepted as source-taxonomy correspondence only with the independently frozen
 # system membership + exact object/data/parent/collection + evaluated geometry identity evidence.
 # This is an AI-reviewed project crosswalk, never an upstream-declared TA2 ID or human approval.
 regionids=set(r for label,r in REGIONS.items() if label in labels)
 if matches:regionids.update(matches[0][0]['regionIds'])
 for label,rs in CONTEXT.items():
  if label in labels:regionids.update(rs)
 if any('Lumbar vertebra' in x for x in labels):regionids.update(['abdomen-lumbar','back'])
 if any('Thoracic vertebra' in x for x in labels):regionids.update(['thorax','back'])
 if any('Cervical vertebra' in x for x in labels):regionids.update(['neck','back'])
 # Original viewport hides remain held. Render flags are source export settings, retained separately.
 exception=any(word in ' '.join(chain+i['collections']).lower() for word in ['inner ear','kidney','cranial nerve','white matter','brainder','foramina'])
 eligible=kind in ['bone','muscle'] and not i['sourceHiddenStatePreserved']['hideViewport'] and not exception
 target=matches[0][0] if matches else None
 name=(namebytarget.get(target['id']) if target else None) or names.get(norm(i['name']))
 label=base(i['name']);modern=traditional=None;aliases=[];nameids=[];ha=None
 if name:
  # Group name may label a parent, never silently rename a separate part.
  same=norm(i['name'])==norm(name['english'])
  traditional=name['label'] if same else None;modern=name.get('korean') if same else None
  aliases=name.get('aliases',[]);nameids=name.get('sourceIds',[]);ha=name['id'] if same and target and ha_to_ta.get(name['id'])==target['id'] and matches[0][1]==i['name'] and regionids and i['sourceLabelSide'] in ['left','right'] else None
 if kind=='bone' and norm(i['name']) in bonenames:
  bn=bonenames[norm(i['name'])];traditional=bn['koTraditional'];modern=bn['koModern'];aliases=[a['text'] for a in bn['aliases']]
  nameids=sorted(set(e['sourceId'] for es in bn['fieldEvidence'].values() for e in es))
  boneids=[re.search(r'item (\d+)',e['locator']).group(1) for e in bn['fieldEvidence']['english'] if re.search(r'item (\d+)',e['locator'])]
  if target and str(target['ta2Id']) in boneids:ha=bn['id']
 if norm(i['name']) in newnames:
  traditional,modern,url=newnames[norm(i['name'])];nameids=[url]
 if i['sourceLabelSide'] in ['left','right']:
  cx=sum(b[0] for b in i['sourceLocalBounds'])/2
  if (i['sourceLabelSide']=='left' and cx<0) or (i['sourceLabelSide']=='right' and cx>0):ha=None
 if traditional:label=traditional
 row={'sourceKey':i['sourceKey'],'sourceName':i['name'],'kind':kind,'regionIds':sorted(regionids),
      'side':i['sourceLabelSide'],'label':label,'names':{'koTraditional':traditional,'koModern':modern,'en':base(i['name'])},
      'aliases':aliases,'nameSourceIds':nameids,'haConceptId':ha,'targetId':target['id'] if target else None,
      'targetIds':[t['id'] for t,_ in matches], 'mappingStatus':'source_taxonomy_correspondence' if target else 'source_observation_only',
      'localDisplayEligible':eligible,'inspectionEligible':eligible,'defaultVisible':eligible,
      'sourceOnly':ha is None,'originalSourceOnly':i['sourceOnly'],'semanticReview':'ai_crosschecked_exact_term_system_region_side_and_source_identity' if ha else 'candidate_only','humanReview':i['humanReview'],'publicRedistribution':'held',
      'originalDisplayState':i['appDisplayRights'],'sourceHiddenStatePreserved':i['sourceHiddenStatePreserved'],
      'localUseRights':'supported_local_prototype' if eligible else 'not_eligible',
      'displayDecisionBasis':'ZA-musculoskeletal-local-prototype-2026-09-29' if eligible else 'accessory-or-original-hidden-or-exception',
      'hardHoldReasons':[] if eligible else ['accessory-or-original-hidden-or-exception'],
      'bounds':[[i['sourceLocalBounds'][0][0],i['sourceLocalBounds'][0][2],-i['sourceLocalBounds'][1][1]], [i['sourceLocalBounds'][1][0],i['sourceLocalBounds'][1][2],-i['sourceLocalBounds'][0][1]]]}
 records.append(row)
 for t,label in matches:joins[t['id']].append(i['sourceKey'])
 audit.append({'haConceptId':ha,'semanticReview':row['semanticReview'],'localDisplayEligible':eligible,'displayDecisionBasis':row['displayDecisionBasis'],'checks':{'exactObjectParentCollections':True,'evaluatedGeometryHashPreserved':True,'targetTermOnDirectObject':bool(matches and matches[0][1]==i['name']),'haStandardRefMatchesTarget':bool(ha),'sourceSide':i['sourceLabelSide'],'regionRule':'frozen TA2 membership plus explicit source/product context; not inferred through nerve collections'},'sourceKey':i['sourceKey'],'object':i['name'],'geometrySha256':i['evaluatedGeometrySha256'],'ancestry':chain,'sourceCollections':i['collections'],
               'matchedTargets':[{'targetId':t['id'],'sourceHierarchyNode':label,'english':t['term']['english'],'semanticKind':t['semanticKind']} for t,label in matches],
               'upstreamTA2Claim':False,'humanReviewed':False,'method':'exact-source-object+system+hierarchy+frozen-TA2-term; AI project correspondence, not provider crosswalk'})
for row in records:
 if row['kind']=='bone' and row['haConceptId']:
  attachments=[a for a in canonical['attachments'] if a.get('targetStructureId')==row['haConceptId']]
  row['relatedMuscles']=[{'sourceKey':m['sourceKey'],'label':m['label'],'roles':sorted(set(a['role'] for a in attachments if a['muscleOrPartId']==m['haConceptId']))} for m in records if m['kind']=='muscle' and m['haConceptId'] and m['side']==row['side'] and any(a['muscleOrPartId']==m['haConceptId'] for a in attachments)]
coverage=[]
for t in scope['targets']:
 keys=sorted(set(joins[t['id']]));coverage.append({'targetId':t['id'],'english':t['term']['english'],'semanticKind':t['semanticKind'],'regionIds':t['regionIds'],
 'sourceKeys':keys,'status':'source_taxonomy_correspondence' if keys else 'variant_not_in_snapshot' if t['scopeFlags']['ta2Inconstant'] else 'unresolved_or_missing',
 'optionalVariant':t['scopeFlags']['ta2Inconstant'],'humanReview':False})
result={'schemaVersion':1,'revision':'T100-source-taxonomy-local-display-v1','datasetRevision':manifest['revision'],
 'sourceCatalogSha256':sha('work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json'),
 'targetScopeSha256':sha('atlas-data/catalog/target-scope-t96.json'),'sourceHash':source['sourceHash'],
 'scope':{'targets':542,'memberships':563,'regions':12},'policy':{'publicRedistribution':'held','humanReview':'not_performed','localOnly':True,
 'localUseRights':'supported_local_prototype','rightsDecisionId':'ZA-musculoskeletal-local-prototype-2026-09-29',
 'rightsEvidence':'work/evidence/T100/resolution-2026-09-29/local-display-review.json','rightsEvidenceSha256':sha('work/evidence/T100/resolution-2026-09-29/local-display-review.json'),'doesNotModifyFrozenSources':True},'objects':records}
(ROOT/'atlas-data/overlays/za-local-integration.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(OUT/'crosswalk-audit.json').write_text(json.dumps({'rows':audit,'coverage':coverage},ensure_ascii=False,indent=2)+'\n')
print('targets',Counter(c['status'] for c in coverage),'eligible',sum(r['localDisplayEligible'] for r in records),'names',sum(bool(r['names']['koTraditional']) for r in records),'regions',Counter(r for i in records if i['inspectionEligible'] for r in i['regionIds']))
print('no region',[(r['sourceName'],r['kind'])for r in records if r['inspectionEligible'] and not r['regionIds']])
