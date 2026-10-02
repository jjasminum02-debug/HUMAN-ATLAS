"""Exact native-source cards, separately scoped literature and observed model course."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT='work/evidence/T66/implementation-2026-10-02'
def read(p):return json.loads((ROOT/p).read_text())
def save(p,v):
    f=ROOT/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
regions={'head':'머리','neck':'목','back':'등','shoulder-scapular':'어깨·어깨뼈','thorax':'가슴우리','abdomen-lumbar':'배·허리','pelvis-perineum':'골반·샅','gluteal-hip':'볼기·엉덩이','thigh':'넙다리','leg':'종아리','foot':'발','upper-limb':'팔·손'}
names={
 'Dorsal scapular nerve':('등쪽어깨신경','견갑배신경'),'Median nerve':('정중신경','정중신경'),
 'Axillary nerve':('겨드랑신경','액와신경'),'Radial nerve':('노신경','요골신경'),
 'Deep branch of radial nerve':('노신경 깊은가지','요골신경 심지'),'Superficial branch of radial nerve':('노신경 얕은가지','요골신경 천지'),
 'Lateral femoral cutaneous nerve':('가쪽넙다리피부신경','외측대퇴피신경'),
 'Posterior femoral cutaneous nerve':('뒤넙다리피부신경','후대퇴피신경'),'Femoral nerve':('넙다리신경','대퇴신경'),
 'Ulnar nerve':('자신경','척골신경'),'Musculocutaneous nerve':('근육피부신경','근피신경'),
 'Tibial nerve':('정강신경','경골신경'),'Saphenous nerve':('두렁신경','복재신경'),
 'Sural nerve':('장딴지신경','비복신경'),'Obturator nerve':('폐쇄신경','폐쇄신경'),
 'Suprascapular nerve':('어깨위신경','견갑상신경'),'Long thoracic nerve':('긴가슴신경','장흉신경'),
 'Medial plantar nerve':('안쪽발바닥신경','내측족저신경'),'Lateral plantar nerve':('가쪽발바닥신경','외측족저신경'),
}
# Concise educational paraphrases of actually opened primary papers/abstracts.
# No numerical location from a cadaver series is bound to this model's coordinates.
literature={
 'Dorsal scapular nerve':{
  'courseContext':'목의 상완신경얼기에서 시작해 중간목갈비근 주변을 지나 마름근·어깨올림근 쪽으로 내려갑니다. 중간목갈비근을 뚫거나 앞쪽을 지나는 경로가 해부 연구에서 보고되었습니다.',
  'compressionContext':'중간목갈비근 주변은 문헌에서 포착 맥락으로 다룹니다. 근육을 관통하는 경로와 앞쪽으로 지나는 변이가 있으므로 한 모형의 경로를 모든 사람에게 적용하지 않습니다.',
  'variationContext':'좌우가 서로 다른 경로를 보인 표본도 보고되었습니다. 문헌의 경로 변이는 이 정적 모형의 좌표로 확정하지 않습니다.',
  'source':'https://pmc.ncbi.nlm.nih.gov/articles/PMC6392864/','locator':'Abstract; Introduction; Results, middle-scalene piercing/anterior variants, 70 cadavers / 140 sides','access':'opened_primary_fulltext'},
 'Median nerve':{
  'courseContext':'아래팔의 몸쪽 구간에서 정중신경은 얕은손가락굽힘근의 섬유성 아치 아래로 지납니다. 앞뼈사이신경이 갈라지는 위치도 이 아치와의 관계에서 변이를 보입니다. 이 설명은 아래팔 몸쪽 구간에 한정합니다.',
  'compressionContext':'얕은손가락굽힘근의 아치는 정중신경의 포착 가능 구간으로 기술됩니다. 뚜렷한 가로 섬유띠와 주변 근막에 섞이는 형태가 구분되며 모형에서 압박이 발생했다고 판정하지 않습니다.',
  'variationContext':'아치 모양·덮는 근육·앞뼈사이신경 분지 위치에 변이가 보고되었습니다. 손목터널이나 모든 정중신경 구간의 확보를 뜻하지 않습니다.',
  'source':'https://pmc.ncbi.nlm.nih.gov/articles/PMC4235925/','locator':'Abstract; Anatomy; Discussion, FDS arch / median nerve / AIN takeoff, 38 cadavers','access':'opened_primary_fulltext'},
 'Lateral femoral cutaneous nerve':{
  'courseContext':'외측대퇴피신경은 골반에서 샅고랑인대·위앞엉덩뼈가시 주변을 지나 넙다리로 이어집니다. 인대 아래의 분지는 넙다리빗근과 넙다리근막긴장근 주변에서 여러 형태를 보입니다.',
  'compressionContext':'이 문헌은 샅고랑인대 주변의 주행·분지와 수술 중 손상 위험을 다룹니다. 만성 포착을 직접 확인한 근거는 아직 연결하지 않았습니다. 문헌의 위치를 모형 위의 포착점으로 표시하지 않으며, 가까이 보이는 것만으로 압박을 판정하지 않습니다.',
  'variationContext':'부채꼴·넙다리빗근을 따르는 형태·뒤쪽으로 가는 분지 형태가 보고되었습니다. 외측대퇴피신경의 뒤쪽 분지와 후대퇴피신경은 다른 개념입니다.',
  'source':'https://pmc.ncbi.nlm.nih.gov/articles/PMC11974468/','locator':'Measurement details; Results; Discussion, LFCN / inguinal ligament / ASIS / sartorius and TFL, 30 specimens','access':'opened_primary_fulltext'},
 'Axillary nerve':{
  'courseContext':'상완신경얼기 뒤다발에서 이어져 사각공간을 지나는 경로가 해부 연구에서 추적되었습니다. 이 구간에서 삼각근으로 가는 운동 섬유와 소원근·어깨 피부로 이어지는 섬유가 구별됩니다.',
  'compressionContext':'사각공간은 액와신경의 잠재적 포착 구간으로 해부 연구에서 다뤄집니다. 정적 모형의 신경과 주변 구조를 관찰하는 설명이며 실제 포착이나 질환을 재현하지 않습니다.',
  'variationContext':'문헌의 섬유다발 위치·거리와 현재 모형의 좌표는 별도입니다. 이를 개인의 안전 범위나 압박 좌표로 바꾸지 않습니다.',
  'source':'https://pubmed.ncbi.nlm.nih.gov/8866374/','locator':'Abstract, posterior cord to quadrangular space, 40 brachial plexuses; potential entrapment context: PMID15926719 abstract index','access':'opened_primary_abstract','additionalSource':'https://pubmed.ncbi.nlm.nih.gov/15926719/'},
 'Deep branch of radial nerve':{
  'courseContext':'요골신경의 깊은가지는 팔꿈치 주변에서 회외근의 몸쪽 아치 아래를 통과합니다. 이 설명은 깊은가지에 한정하며 피부 감각을 담당하는 얕은가지 전체와 합치지 않습니다.',
  'compressionContext':'회외근의 몸쪽 입구인 Frohse 아치와 짧은노쪽손목폄근 주변의 힘줄성 구조가 깊은가지 포착과 관련된 해부 맥락으로 연구되었습니다.',
  'variationContext':'아치가 섬유성인지, 주행을 가로지르는 조직과의 관계가 어떤지에 변이가 보고되었습니다. 문헌의 수치를 모형의 포착 좌표로 결속하지 않습니다.',
  'source':'https://pubmed.ncbi.nlm.nih.gov/2606390/','locator':'Indexed primary abstract; 120 cadaver elbow regions; ECRB initial deep surface and superior supinator hiatus; source fulltext unavailable','access':'primary_abstract_index_only'},
}

def build():
    graph=read('atlas-data/terminology/learner-nerve-graph-t25.json');old={c['names']['en']:c for c in graph['concepts']}
    registry=read('atlas-data/overlays/nerve-support-t66.json');groups={}
    for n in registry['instances']:
        if n['localSelection']=='verified_geometry':groups.setdefault(n['names']['en'],[]).append(n)
    oldTexts={r['nerveName']:r for r in read('atlas-data/terminology/nerve-learning-content-t65.json')['records']}
    learner={};ledger=[]
    for en,rows in sorted(groups.items()):
        c=old.get(en)
        if c is None:
            ko=names.get(en,(en,en));key='nerve-source-'+re.sub('[^a-z0-9]+','-',en.lower()).strip('-')
            c={'key':key,'names':{'koModern':ko[0],'koTraditional':ko[1],'en':en,'latin':None},'searchTerms':[ko[0],ko[1],en],
                'sourceNativeEnglishName':en,'summary':None}
            graph['concepts'].append(c)
        else:
            c['sourceNativeEnglishName']=en
            if en=='Dorsal scapular nerve' and c['summary']:
                c['summary']['course']=c['summary']['course'].replace('이 앱에는 이 신경의 3D 주행 모형이 없습니다.','한 정적 모형의 주행을 관찰할 수 있으며 개인별 경로에는 차이가 있습니다.')
        rids=sorted({r for n in rows for r in n['regionIds']})
        observed='정적 모형에서 '+', '.join(regions[r] for r in rids)+'의 주변 구조와 주행을 살펴볼 수 있습니다. 한 주행 표본이며 정상 경로의 모든 변이를 보여 주지는 않습니다.'
        text={'courseContext':observed,'compressionContext':'이 신경의 포착 가능 구간을 설명할 문헌 근거가 아직 연결되지 않았습니다. 모형의 가까움·교차만으로 포착을 판정하지 않습니다.',
            'variationContext':'현재는 정적 자세의 주행을 관찰합니다. 움직이는 자세에서의 신경 변형·미끄러짐은 제공하지 않습니다.',
            'functionContext':'확인된 신경 지배 관계가 있는 경우 아래 운동 연결에서 살펴볼 수 있습니다.'}
        evidence=[];support='observed_static_model_context'
        if en in oldTexts:
            text.update({k:oldTexts[en][k] for k in ['courseContext','compressionContext','functionContext']});evidence.append({'path':'atlas-data/terminology/nerve-learning-content-t65.json','sha256':sha('atlas-data/terminology/nerve-learning-content-t65.json'),'locator':'records[nerveName='+en+'].fieldEvidence'});support='reused_field_evidence'
        if en in literature:
            claim=literature[en];text.update({k:claim[k] for k in ['courseContext','compressionContext','variationContext']});evidence.append({k:claim[k] for k in ['source','locator','access']});
            if claim.get('additionalSource'):evidence.append({'source':claim['additionalSource'],'locator':'primary abstract index only; entrapment context','access':'primary_abstract_index_only'})
            support=claim['access']
        learner[en]=text
        ledger.append({'sourceNativeName':en,'sourceInstanceIds':[n['id'] for n in rows],'sourceKeys':[n['geometry']['assetPath'].split('/')[-1].replace('.glb','') for n in rows],
            'anatomicalConceptId':None,'displayNameMeaning':'context-composed learner names, not a quoted dictionary headword or canonical binding',
            'courseTextSupport':support,'entrapmentTextSupported':en in oldTexts or en in ['Dorsal scapular nerve','Median nerve'],
            'entrapmentEvidenceStatus':('reused_field_evidence' if en in oldTexts else 'opened_primary_fulltext' if en in ['Dorsal scapular nerve','Median nerve'] else 'primary_abstract_index_only' if en in ['Axillary nerve','Deep branch of radial nerve'] else 'surrounding_anatomy_only' if en=='Lateral femoral cutaneous nerve' else 'unavailable'),
            'observedModelCourse':observed,'regionIds':rids,'fieldEvidence':evidence,'staticGeometry':len(rows),'dynamicGeometry':0,'entrapmentCoordinates':0,
            'humanReview':'not_performed','publicRedistribution':'held'})
    save('atlas-data/terminology/learner-nerve-graph-t66.json',graph)
    save('atlas-data/terminology/nerve-learning-t66.json',learner)
    save(OUT+'/nerve-course-and-entrapment-ledger.json',{'schemaVersion':'t66-source-course-text-v1','originalT25Preserved':True,
        'rows':ledger,'literatureClaims':literature,'independentAnatomicalConceptCount':None,'nativeLabelGroups':len(groups),
        'scope':'Full currently evaluated native source set; roots/plexus/trunks/branches retained, not independent anatomy counts. Text/geometry/dynamic-pose/entrapment-coordinate support separate.'})
    print(json.dumps({'nativeSourceGroups':len(groups),'staticSurfaces':sum(len(r) for r in groups.values()),'literatureEntrapmentLabels':sum(x['entrapmentTextSupported'] for x in ledger)}))

if __name__=='__main__':build()
