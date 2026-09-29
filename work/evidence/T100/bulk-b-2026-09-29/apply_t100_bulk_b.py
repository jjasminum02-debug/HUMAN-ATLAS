#!/usr/bin/env python3
"""Rebuild the first evidence-backed portion of T100 unit B from its start HEAD."""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASELINE = json.loads((HERE / 'start-baseline.json').read_text())
OVERLAY_REL = 'atlas-data/overlays/za-local-integration.json'
SCOPE_REL = 'atlas-data/catalog/target-scope-t96.json'
CATALOG_REL = 'work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json'
META_REL = 'work/evidence/T100/resolution-2026-09-29/source-metadata.json'
SOURCE_REV = 'c7010a903b75a2fd24a13b1c2c4c3546a9223780'
SOURCE_SHA = '9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd'
FIPAT_ID = 'fipat-ta2-t96-frozen-target-terms'

PAGES = {
    'corrugator': {
        'id': 'kmle-t100-b-kas-corrugator-supercilii-opened',
        'url': 'https://m.kmle.co.kr/search.php?Search=corrugator+supercilii+m',
        'sourceLabel': 'KMLE aggregate HTML, 대한해부학회 의학용어 사전 section',
        'term': 'Corrugator supercilii m.',
        'koModern': '눈썹주름근',
        'koTraditional': '추미근',
        'locator': 'Opened KMLE aggregate HTML, 대한해부학회 의학용어 사전 맞춤 결과 at lines 92-95: Corrugator supercilii m. -> 눈썹주름근; [옛 용어] 추미근. The underlying dictionary edition is not exposed and its individual record page was not opened.'
    },
    'coccygeus': {
        'id': 'kmle-t100-b-kas-coccygeus-opened',
        'url': 'https://m.kmle.co.kr/search.php?Page=2&Search=muscle&SpecialSearch=DictAnatomy',
        'sourceLabel': 'KMLE aggregate HTML, 대한해부학회 의학용어 사전 section',
        'term': 'Coccygeus muscle',
        'koModern': '꼬리근',
        'koTraditional': '미골근',
        'locator': 'Opened KMLE aggregate HTML browser accessibility result, 대한해부학회 의학용어 사전 유사 검색 결과, page 2: Coccygeus muscle -> 꼬리근; [옛 용어] 미골근. The underlying dictionary edition is not exposed and its individual record page was not opened.'
    }
}
CONCEPTS = [
    {'targetId':'TA2:2071','key':'corrugator','sourceName':'Corrugator supercilii','region':'head','sourceKeys':['ZA-c7010a9-9f73db49eb355770a7814647','ZA-c7010a9-2b579c0a25cb9b5b100f96d5'],'sides':['left','right']},
    {'targetId':'TA2:2412','key':'coccygeus','sourceName':'Coccygeus muscle','region':'pelvis-perineum','sourceKeys':['ZA-c7010a9-8701ba72a3e3966c8deffc44','ZA-c7010a9-832ed8022cc12d8a69f7da32'],'sides':['left','right']},
]

def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()
def read_json(rel: str):
    return json.loads((ROOT / rel).read_text())
def need(ok: bool, message: str):
    if not ok: raise SystemExit(message)

def base_overlay_bytes() -> bytes:
    raw = subprocess.check_output(['git','show',f"{BASELINE['startHead']}:{OVERLAY_REL}"],cwd=ROOT)
    need(sha(raw) == BASELINE['frozenInputs'][OVERLAY_REL], 'T100-B start overlay hash changed')
    return raw

def target_row_fields(target):
    term = target['term']
    return term

def create_target_evidence(target, concept, overlay, catalog_by_key, raw_by_name):
    term = target['term']; page = PAGES[concept['key']]
    source_ids = {s['id'] for s in overlay['evidenceSources']}
    need(FIPAT_ID in source_ids, 'frozen FIPAT target source missing')
    fields = {
        'koModern': {'value':page['koModern'],'sourceIds':[page['id']],'locator':page['locator'],'status':'evidence_backed','missingReason':None},
        'koTraditional': {'value':page['koTraditional'],'sourceIds':[page['id']],'locator':page['locator'],'status':'evidence_backed','missingReason':None},
        'en': {'value':term['english'],'sourceIds':[FIPAT_ID],'locator':f"Pinned T96 target {concept['targetId']} exact English term: {term['english']}",'status':'evidence_backed','missingReason':None},
        'latin': {'value':term['latin'],'sourceIds':[FIPAT_ID],'locator':f"Pinned T96 target {concept['targetId']} exact Latin term: {term['latin']}",'status':'evidence_backed','missingReason':None},
        'sourceSynonyms': [],
        'hanja': {'value':None,'sourceIds':[],'locator':None,'status':'not_collected','missingReason':'Actual Hanja glyphs are not collected in this task.'}
    }
    for lang, vals in term.get('sourceSynonyms',{}).items():
        for val in vals:
            fields['sourceSynonyms'].append({'language':lang,'value':val,'sourceIds':[FIPAT_ID],'locator':f"Pinned T96 exact {lang} source synonym for {concept['targetId']}: {val}",'status':'evidence_backed'})
    objects=[]
    for key, side in zip(concept['sourceKeys'],concept['sides']):
        obj = catalog_by_key[key]
        objects.append({'sourceKey':key,'sourceObjectName':obj['name'],'sourceDataName':obj.get('dataName'),'sourceParent':obj.get('parent'),'sourceCollections':obj.get('collections',[]),'sourceSide':obj.get('sourceLabelSide'),'evaluatedGeometrySha256':obj['evaluatedGeometrySha256'],'sourceHash':SOURCE_SHA,'sourceRevision':SOURCE_REV,'sourceLocator':obj.get('sourceLocator')})
    primary = target['semanticKind']
    return {
        'targetId':concept['targetId'],
        'targetTermSourceIds':[FIPAT_ID],
        'english':term['english'],'latin':term['latin'],'sourceSynonyms':term.get('sourceSynonyms',{}),
        'relatedTerms':term.get('relatedTerms',[]),'semanticKind':target['semanticKind'],
        'primaryOwner':target['primaryOwner'],'regionIds':target['regionIds'],'sourceParentId':target.get('sourceParentId'),
        'sourceAncestryIds':target.get('sourceAncestryIds',[]),'sourceFlags':target.get('sourceFlags',{}),
        'classification':{'meaningType':primary,'groupPartVariant':'individual muscle; Korean name checked once for the exact shared English headword; the source presents two side-labelled objects','laterality':'left/right are retained as separate source objects; the term itself is shared'},
        'names':{'koModern':page['koModern'],'koTraditional':page['koTraditional'],'en':term['english']},
        'fieldEvidence':fields,'unappliedTermCandidates':[],
        'existingSurface':{'status':'two_exact_source_named_side_objects_present','exactSourceObjects':objects,'exactMemberCrosswalkAdded':False,'note':'The pre-existing T99 source target observation was preserved. This task adds Korean names only; it does not create a canonical HA learner binding.'},
        'observedSurfacesNotBound':objects,
        'learnerBindingCreated':False,'canonicalHaConceptId':None,'sourceOnly':True,
        'humanReview':'not_performed','publicRedistribution':'held','newGeometryCreated':False
    }

def build():
    root_status = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    need(root_status == BASELINE['startHead'], 'HEAD moved after T100-B baseline; do not rebuild on a different baseline')
    for rel,digest in BASELINE['frozenInputs'].items():
        need(sha((ROOT/rel).read_bytes()) == digest or rel == OVERLAY_REL, f'frozen input changed: {rel}')
    scope = read_json(SCOPE_REL); catalog=read_json(CATALOG_REL); metadata=read_json(META_REL)
    need(len(scope['targets'])==542 and scope['denominators']['productRegionMembershipRows']==563, 'T96 denominator changed')
    need(catalog['sourceRevision']==SOURCE_REV and catalog['sourceHash']==SOURCE_SHA and len(catalog['objects'])==960,'pinned source catalog changed')
    overlay=json.loads(base_overlay_bytes())
    need(overlay['scope']=={'targets':542,'memberships':563,'regions':12} and len(overlay['objects'])==960,'overlay denominator/object inventory changed')
    need(overlay['revision'].endswith('B05-pelvis-lower-limb-bones'),'B05 input revision changed')
    existing_ids={s['id'] for s in overlay['evidenceSources']}
    need(not (existing_ids & {p['id'] for p in PAGES.values()}),'evidence source ID collision')
    fipat=next((s for s in overlay['evidenceSources'] if s['id']==FIPAT_ID),None)
    need(fipat is not None,'frozen FIPAT target source missing')
    target_map={t['id']:t for t in scope['targets']}
    existing_targets={t['targetId'] for t in overlay.get('targetTerminologyEvidence',[])}
    catalog_by_key={o['sourceKey']:o for o in catalog['objects']}
    raw_by_name={o['name']:o for o in metadata['objects']}
    terms=[]
    for concept in CONCEPTS:
        need(concept['targetId'] in target_map and concept['targetId'] not in existing_targets,'target missing or already has terminology evidence')
        term=target_map[concept['targetId']]
        need(term['term']['english'].lower()==concept['sourceName'].lower(),'T96/source exact English headword mismatch')
        need(term['semanticKind']=='named_muscle','unexpected target semantic kind')
        expected_names=[concept['sourceName']+'.l',concept['sourceName']+'.r']
        need(len(concept['sourceKeys'])==2 and concept['sides']==['left','right'],'paired concept definition malformed')
        for key, name, side in zip(concept['sourceKeys'],expected_names,concept['sides']):
            source=catalog_by_key.get(key); overlay_obj=next((o for o in overlay['objects'] if o['sourceKey']==key),None)
            raw=raw_by_name.get(name)
            need(source and overlay_obj and raw,'frozen source object absent')
            need(source['name']==name and overlay_obj['sourceName']==name and overlay_obj['kind']=='muscle','source identity/name mismatch')
            need(source['sourceLabelSide']==side and overlay_obj['side']==side,'source side label mismatch')
            need(concept['region'] in overlay_obj['regionIds'],'source region mismatch')
            need(len(source['evaluatedGeometrySha256'])==64 and all(c in '0123456789abcdef' for c in source['evaluatedGeometrySha256']),'evaluated geometry hash missing or malformed')
            need(source['parent']==raw['parent'],'source parent mismatch')
            need(source['collections']==raw['collections'],'source collection mismatch')
            need(overlay_obj['localDisplayEligible'] is True and overlay_obj['kind']=='muscle','not an eligible visible muscle surface')
            need(overlay_obj['sourceOnly'] is True and overlay_obj['haConceptId'] is None and overlay_obj['humanReview']=='not_performed' and overlay_obj['publicRedistribution']=='held','source/review/rights hold mismatch')
            need(overlay_obj['names']['koModern'] is None and overlay_obj['names']['koTraditional'] is None,'object already has Korean name')
            need(concept['targetId'] in overlay_obj['targetIds'] and overlay_obj['targetId']==concept['targetId'],'pre-existing target relation mismatch')
        terms.append(create_target_evidence(term,concept,overlay,catalog_by_key,raw_by_name))
    for key, page in PAGES.items():
        overlay['evidenceSources'].append({'id':page['id'],'url':page['url'],'sourceLabel':page['sourceLabel'],'exactEdition':None,'editionExposure':'The KMLE page labels the 대한해부학회 dictionary section but does not expose its edition or revision.','accessDate':'2026-09-29','accessMethod':'opened_html','retrievalLayer':'opened KMLE aggregate search result page','openedOriginalDictionaryRecord':False,'openedOriginalSourcePage':False,'locator':page['locator'],'term':page['term'],'koModern':page['koModern'],'koTraditional':page['koTraditional']})
    overlay['targetTerminologyEvidence'].extend(terms)
    by_key={o['sourceKey']:o for o in overlay['objects']}
    for concept in CONCEPTS:
        page=PAGES[concept['key']]
        for key in concept['sourceKeys']:
            obj=by_key[key]
            obj['names']['koModern']=page['koModern']; obj['names']['koTraditional']=page['koTraditional']
            obj['nameSourceIds']=list(dict.fromkeys([*obj.get('nameSourceIds',[]),page['id']]))
        # Explicit invariants: names change only; no canonical, visibility, rights or review promotion.
        for key in concept['sourceKeys']:
            obj=by_key[key]
            need(obj['sourceOnly'] is True and obj['haConceptId'] is None and obj['humanReview']=='not_performed' and obj['publicRedistribution']=='held','forbidden promotion')
            need(obj['localDisplayEligible'] is True and obj['defaultVisible'] is True,'visibility policy changed')
    overlay['revision']='T100-source-taxonomy-local-display-v1-B-bulk-verified-names'
    return overlay

if __name__=='__main__':
    output=build(); target=ROOT/OVERLAY_REL
    serialized=json.dumps(output,ensure_ascii=False,indent=2)+'\n'
    if '--check' in sys.argv:
        need(target.read_text()==serialized,'current overlay differs from deterministic T100-B output')
        print(json.dumps({'status':'pass','revision':output['revision'],'objects':len(output['objects']),'newTargets':2,'namedObjects':4,'sourceOnly':True,'humanReview':'not_performed','publicRedistribution':'held'},ensure_ascii=False,indent=2))
    else:
        target.write_text(serialized)
        print(json.dumps({'status':'written','revision':output['revision'],'objects':len(output['objects']),'newTargets':2,'namedObjects':4},ensure_ascii=False,indent=2))
