#!/usr/bin/env python3
"""Strict validator for the evidence-backed T100 B data-only name update."""
from __future__ import annotations
import hashlib,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[3]
BASE=json.loads((HERE/'start-baseline.json').read_text())
OVERLAY_REL='atlas-data/overlays/za-local-integration.json'
EXPECTED={
 'ZA-c7010a9-9f73db49eb355770a7814647':('Corrugator supercilii.l','left','눈썹주름근','추미근','kmle-t100-b-kas-corrugator-supercilii-opened','TA2:2071'),
 'ZA-c7010a9-2b579c0a25cb9b5b100f96d5':('Corrugator supercilii.r','right','눈썹주름근','추미근','kmle-t100-b-kas-corrugator-supercilii-opened','TA2:2071'),
 'ZA-c7010a9-8701ba72a3e3966c8deffc44':('Coccygeus muscle.l','left','꼬리근','미골근','kmle-t100-b-kas-coccygeus-opened','TA2:2412'),
 'ZA-c7010a9-832ed8022cc12d8a69f7da32':('Coccygeus muscle.r','right','꼬리근','미골근','kmle-t100-b-kas-coccygeus-opened','TA2:2412'),
}
def sha(b): return hashlib.sha256(b).hexdigest()
def need(ok,msg):
 if not ok: raise SystemExit('FAIL: '+msg)
def read(rel): return (ROOT/rel).read_bytes()
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
need(head==BASE['startHead'],'HEAD moved before B checkpoint validation')
for rel,digest in BASE['frozenInputs'].items():
 if rel==OVERLAY_REL: continue
 need(sha(read(rel))==digest,'frozen input changed: '+rel)
base_raw=subprocess.check_output(['git','show',f"{BASE['startHead']}:{OVERLAY_REL}"],cwd=ROOT)
need(sha(base_raw)==BASE['frozenInputs'][OVERLAY_REL],'baseline overlay does not match frozen input')
base=json.loads(base_raw); post=json.loads(read(OVERLAY_REL))
subprocess.check_call(['python3',str(HERE/'apply_t100_bulk_b.py'),'--check'],cwd=ROOT,stdout=subprocess.DEVNULL)
need(post['revision']=='T100-source-taxonomy-local-display-v1-B-bulk-verified-names','revision mismatch')
need(post['scope']==base['scope']=={'targets':542,'memberships':563,'regions':12},'scope denominator changed')
need(len(post['objects'])==len(base['objects'])==960,'source object count changed')
need(post['policy']==base['policy'],'rights/review policy changed')
base_objects={o['sourceKey']:o for o in base['objects']}; post_objects={o['sourceKey']:o for o in post['objects']}
need(set(base_objects)==set(post_objects),'source object inventory changed')
changed=set()
for key,b in base_objects.items():
 p=post_objects[key]
 if p!=b:
  changed.add(key)
  normalized=json.loads(json.dumps(p))
  normalized['names']=dict(b['names'])
  normalized['nameSourceIds']=list(b['nameSourceIds'])
  need(normalized==b,'unexpected object field changed: '+key)
need(changed==set(EXPECTED),'object delta is not the exact four-object name overlay')
for key,(name,side,modern,traditional,evidence_id,target_id) in EXPECTED.items():
 o=post_objects[key]
 need(o['sourceName']==name and o['side']==side,'source identity or side mismatch: '+name)
 need(o['names']=={'koTraditional':traditional,'koModern':modern,'en':base_objects[key]['names']['en']},'three-name tuple mismatch: '+name)
 need(o['nameSourceIds']==base_objects[key]['nameSourceIds']+[evidence_id],'name provenance mismatch: '+name)
 need(o['sourceOnly'] is True and o['haConceptId'] is None and o['humanReview']=='not_performed' and o['publicRedistribution']=='held','promotion/hold mismatch: '+name)
 need(o['localDisplayEligible'] is True and o['defaultVisible']==base_objects[key]['defaultVisible'],'display eligibility/default changed: '+name)
 term_ids=set(o['targetIds'])
 need(target_id in term_ids and o['targetId']==target_id,'pre-existing target relation mismatch: '+name)
# Existing developer records remain byte-for-byte equivalent after parse.
base_terms={x['targetId']:x for x in base['targetTerminologyEvidence']}; post_terms={x['targetId']:x for x in post['targetTerminologyEvidence']}
need(set(post_terms)-set(base_terms)=={'TA2:2071','TA2:2412'},'target term additions are not the two exact concepts')
need(all(post_terms[k]==v for k,v in base_terms.items()),'prior target terminology rows changed')
need(len(post['targetTerminologyEvidence'])==len(base_terms)+2,'target term evidence count mismatch')
base_sources={x['id']:x for x in base['evidenceSources']}; post_sources={x['id']:x for x in post['evidenceSources']}
need(set(post_sources)-set(base_sources)=={'kmle-t100-b-kas-corrugator-supercilii-opened','kmle-t100-b-kas-coccygeus-opened'},'source evidence additions mismatch')
need(all(post_sources[k]==v for k,v in base_sources.items()),'prior source evidence changed')
ledger=json.loads((HERE/'term-and-repetition-ledger.json').read_text())
query=json.loads((HERE/'source-query-observations.json').read_text())
need({x['id'] for x in query['observations']}==set(post_sources)-set(base_sources),'query record/source IDs mismatch')
need(len(ledger['repeatedStructureRelations'])==2 and len(ledger['targetNameEvidence'])==2,'ledger term/pair count mismatch')
pool=ledger['bulkCandidatePool']
need(pool['termsAppliedFromWorkbook']==0 and pool['workbookCandidatesVerifiedViaDirectKMLE']==1
     and pool['verifiedKoreanTermsAppliedTotal']==2,'workbook candidates were treated as name authority')
allowed_access={'opened_html','opened_pdf','search_index_excerpt','local_frozen_metadata'}
for observation in query['observations']:
 source=post_sources[observation['id']]
 need(observation['accessMethod'] in allowed_access,'unsupported access method: '+observation['id'])
 need(observation['accessMethod']==source['accessMethod'] and observation['url']==source['url']
      and observation['locator']==source['locator'] and observation['exactEdition']==source['exactEdition'],
      'query/source provenance mismatch: '+observation['id'])
 need(observation['openedOriginalSourcePage'] is False and observation['openedOriginalDictionaryRecord'] is False,
      'aggregate page misrepresented as original dictionary record: '+observation['id'])
 need(observation['observedFields']['koModern']==source['koModern']
      and observation['observedFields']['koTraditional']==source['koTraditional'],
      'opened-page term values disagree with overlay evidence: '+observation['id'])
for tid,modern,traditional,eid in [('TA2:2071','눈썹주름근','추미근','kmle-t100-b-kas-corrugator-supercilii-opened'),('TA2:2412','꼬리근','미골근','kmle-t100-b-kas-coccygeus-opened')]:
 t=post_terms[tid]
 need(t['names']['koModern']==modern and t['names']['koTraditional']==traditional,'target term name mismatch: '+tid)
 need(t['fieldEvidence']['koModern']['sourceIds']==[eid] and t['fieldEvidence']['koTraditional']['sourceIds']==[eid],'Korean term provenance mismatch: '+tid)
 need(t['fieldEvidence']['hanja']['value'] is None and t['fieldEvidence']['hanja']['status']=='not_collected','Hanja was collected or status changed')
 need(t['learnerBindingCreated'] is False and t['canonicalHaConceptId'] is None and t['newGeometryCreated'] is False,'canonical binding or geometry created: '+tid)
 need(t['sourceOnly'] is True and t['humanReview']=='not_performed' and t['publicRedistribution']=='held','target hold changed: '+tid)
 for value in (modern,traditional):
  need(not re.search(r'[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]',value),'actual Hanja glyph present in learner Korean name')
# Actual source identity, side and compiled surface resources.
catalog=json.loads(read('work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json'))
meta=json.loads(read('work/evidence/T100/resolution-2026-09-29/source-metadata.json'))
compiled=json.loads(read('atlas-data/source-cache/datasets/za/compiled/manifest.json'))
cat={x['sourceKey']:x for x in catalog['objects']}; raw={x['name']:x for x in meta['objects']}; inst={x['sourceKey']:x for x in compiled['instances']}
for key,(name,side,*_) in EXPECTED.items():
 c=cat[key]; r=raw[name]; i=inst[key]
 need(c['name']==name and c['sourceLabelSide']==side,'frozen source catalog name/side mismatch: '+name)
 need(c['parent']==r['parent'] and c['collections']==r['collections'],'raw source hierarchy mismatch: '+name)
 need(i['name']==name and i['sourceLabelSide']==side and i['sourceKey']==key,'compiled instance identity/side mismatch: '+name)
 need(i['sourceOnly'] is True and i['canonicalConceptId'] is None and i['learnerBinding']=='source_only_unbound','compiled source-only binding changed: '+name)
 need(i['publicRedistribution']=='held' and i['humanReview']=='not_performed' and i['appDisplayRights']=='held_not_approved_by_this_task','compiled rights/review hold changed: '+name)
 need(i['lods']['detail']['sha256'] in i['lods']['detail']['resource'] and i['lods']['detail']['triangles']>0,'compiled surface resource missing: '+name)
# Workbook and OpenSim preservation.
book=Path.home()/'Downloads'/'근육-기시정지-신경-작용-정리.xlsx'
need(book.exists() and sha(book.read_bytes())==BASE['privateWorkbookNameReference']['expectedSha256'],'private source workbook changed')
open_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT/'OpenSim_Models',text=True).strip()
open_status=subprocess.check_output(['git','status','--short'],cwd=ROOT/'OpenSim_Models',text=True).splitlines()
need(open_head==BASE['readOnlyOpenSimModels']['head'] and not open_status,'OpenSim_Models changed')
eligible=[o for o in post['objects'] if o['localDisplayEligible']]
named=[o for o in eligible if o['names'].get('koModern')]
need(len(eligible)==672 and len(named)==160,'local display/name coverage count mismatch')
result={'schemaVersion':1,'taskId':'T100','workUnit':'B','status':'pass_partial_unit','checkedAtLocal':'2026-09-29','startingHead':BASE['startHead'],'currentPreCommitHead':head,'checks':{'deterministicRebuild':True,'scope542_563_12Preserved':True,'sourceObjectInventory960Preserved':True,'exactTwoTargetsFourSideObjects':True,'KoreanNameProvenanceAndNoHanja':True,'openedAggregatePageNotMisreportedAsOriginalDictionary':True,'allEarlierB01B05TargetAndSourceEvidenceUnchanged':True,'noHaCanonicalBindingOrReviewRightsPromotion':True,'noGeometryOrDefaultVisibilityChange':True,'compiledInstanceSideHashAndSurfaceResourcePresent':True,'privateWorkbookHashPreserved':True,'OpenSimModelsReadOnlyAndClean':True},'counts':{'newNamedConcepts':2,'newNamedSurfaceObjects':4,'targetTermRowsBefore':len(base_terms),'targetTermRowsAfter':len(post_terms),'eligibleSurfaceObjects':len(eligible),'eligibleObjectsWithKoModern':len(named),'eligibleObjectsStillUnnamed':len(eligible)-len(named),'historicalTargetRemainder':142,'wholeBodyTargetDenominator':542,'regionMembershipDenominator':563,'regions':12},'sourceObjects':[{ 'sourceKey':key,'sourceName':EXPECTED[key][0],'side':EXPECTED[key][1],'evaluatedGeometrySha256':cat[key]['evaluatedGeometrySha256'],'compiledLodSha256':inst[key]['lods']['detail']['sha256'],'triangles':inst[key]['lods']['detail']['triangles']} for key in EXPECTED], 'holds':{'sourceOnly':True,'humanReview':'not_performed','publicRedistribution':'held','canonicalHaBindingsAdded':0,'geometryChanged':False,'wholeBodyCompletion':False},'nextUnit':'bulk-verified-korean-naming-and-repeated-structures'}
(HERE/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
