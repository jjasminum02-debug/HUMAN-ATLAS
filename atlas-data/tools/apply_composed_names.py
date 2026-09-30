"""Apply explicit part-name rules to existing source concepts; no fuzzy binding or new geometry."""
import argparse, copy, hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def norm(s):
    return re.sub(r'\s+',' ',re.sub(r'\bmuscle\b','',s.lower())).strip(' ()')
def apply(data, rules, learning):
    parents={norm(e['english']):e for e in learning['entries'] if e.get('korean')}
    before={r['sourceKey']:copy.deepcopy(r) for r in data['objects']}
    sid=rules['source']['id']
    if not any(s['id']==sid for s in data['evidenceSources']):data['evidenceSources'].append(rules['source'])
    for rule in rules['rules']:
        parent=parents[norm(rule['parent'])]
        for row in data['objects']:
            if norm(row['names']['en'])!=norm(rule['sourceTerm']):continue
            if not row['localDisplayEligible'] or row.get('hardHoldReasons'):continue
            links=row.get('learnerConceptLinks',[])
            # Require existing exact concept relation, not a broad parent target candidate.
            if not any(l['relationKind']=='normalized_exact_target_term' and l['identityStatus']=='evidence_backed' for l in links):continue
            for field,key in [('koModern','korean'),('koTraditional','label')]:
                if row['names'].get(field) and not rule.get('replaceEnglishPlaceholder',False):continue
                if row['names'].get(field) and re.search('[가-힣]',row['names'][field]):continue
                value=parent[key]+' · '+rule['modifier']
                row['names'][field]=value
                row.setdefault('nameEvidence',{})[field]={'value':value,'sourceIds':[sid], 'locator':f"AI descriptive composition, not a direct dictionary headword: learning-names {parent['id']} ({key}) + explicit source modifier {rule['modifierEnglish']} -> {rule['modifier']}; existing exact learner concept/side unchanged. Rule {rule['sourceTerm']}"}
            row['label']=row['names']['koTraditional'] or row['names']['koModern'] or row['names']['en']
            row['nameSourceIds']=list(dict.fromkeys(row['nameSourceIds']+[sid]))
    # Contextual terminology decisions are explicit data, not fuzzy identity matches.
    # They name the observed source concept and never mutate its target/side/geometry.
    for decision in rules.get('semanticNames', []):
        for row in data['objects']:
            if row['names']['en'] != decision['sourceTerm'] or not row['localDisplayEligible']:
                continue
            for field in ['koModern', 'koTraditional']:
                if row['names'].get(field) and re.search('[가-힣]', row['names'][field]):
                    continue
                value=decision[field]
                row['names'][field]=value
                row.setdefault('nameEvidence',{})[field]={'value':value,'sourceIds':[sid], 'locator':f"AI contextual anatomical rendering under user 2026-09-30 instruction; not a verbatim dictionary claim. Source concept: {decision['sourceTerm']}; retained explicit body-region/part scope. Decision in composed-parts.json semanticNames; uncertainty in identity/side remains independent."}
            row['label']=row['names']['koTraditional'] or row['names']['koModern'] or row['names']['en']
            row['nameSourceIds']=list(dict.fromkeys(row['nameSourceIds']+[sid]))
    ordinals=dict(zip(['First','Second','Third','Fourth','Fifth','Sixth','Seventh','Eighth','Ninth','Tenth','Eleventh','Twelfth'],range(1,13)))
    for row in data['objects']:
        if not row['localDisplayEligible'] or row['names']['koTraditional'] or not row['names']['koModern']:
            continue
        en=row['names']['en']; value=None
        if en.endswith(' rib') and en.split()[0] in ordinals:
            value=f"제{ordinals[en.split()[0]]}늑골"
        m=re.fullmatch(r'Vertebra L([1-5])',en)
        if m:value=f"제{m[1]}요추"
        m=re.fullmatch(r'(First|Second|Third|Fourth|Fifth) meta(carpal|tarsal) bone',en)
        if m:value=f"제{ordinals[m[1]]}{'중수골' if m[2]=='carpal' else '중족골'}"
        m=re.fullmatch(r'(Distal|Middle|Proximal) phalanx of (first|second|third|fourth|fifth) finger of (hand|foot)',en)
        if m:value=f"{'손' if m[3]=='hand' else '발'} 제{ordinals[m[2].capitalize()]}지 { {'Distal':'말절골','Middle':'중절골','Proximal':'기절골'}[m[1]]}"
        if en=='Triquetrum bone':value='삼각골'
        if en=='Extensor hallucis longus':value='발 장무지신근'
        if value:
            row['names']['koTraditional']=value;row['label']=value
            row.setdefault('nameEvidence',{})['koTraditional']={'value':value,'sourceIds':[sid], 'locator':'AI contextual ordinal/region composition from existing source segment and already resolved modern name; descriptive project label, not a verbatim dictionary headword. No geometry/identity change.'}
            row['nameSourceIds']=list(dict.fromkeys(row['nameSourceIds']+[sid]))
    for row in data['objects']:
        if row['localDisplayEligible'] and not re.search('[가-힣]', row['label']):
            row['label']=row['names']['koTraditional'] or row['names']['koModern'] or row['names']['en']
    changes=[{'sourceKey':r['sourceKey'],'before':before[r['sourceKey']]['names'],'after':r['names']} for r in data['objects'] if before[r['sourceKey']]!=r]
    return changes
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
    target=ROOT/'atlas-data/overlays/za-local-integration.json';d=json.loads(target.read_text());rules=json.loads((ROOT/'atlas-data/terminology/rules/composed-parts.json').read_text());lp=ROOT/'atlas-data/terminology/learning-names.json';assert hashlib.sha256(lp.read_bytes()).hexdigest()==rules['learningNamesSha256'];changes=apply(d,rules,json.loads(lp.read_text()))
    if a.check:assert not changes, 'composed names stale'
    else:target.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');(ROOT/'work/evidence/T100/completion-2026-09-30/name-delta.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'changes':len(changes),'modernNamed':sum(bool(r['names']['koModern']) for r in d['objects'] if r['localDisplayEligible'])}))
