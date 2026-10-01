"""Apply bounded display rules; never changes identity, anatomy links, geometry or approvals."""
import argparse, hashlib, json, copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RULES=ROOT/'atlas-data/terminology/rules/t58-contextual-muscle-display.json'
OVERLAY=ROOT/'atlas-data/overlays/za-local-integration.json'

def apply(data,rules):
    source=rules['source']; rule_by_term={r['sourceTerm']:r for r in rules['rules']}
    learning=ROOT/'atlas-data/terminology/learning-names.json'
    assert hashlib.sha256(learning.read_bytes()).hexdigest()==rules['learningNamesSha256']
    parents={r['id']:r for r in json.loads(learning.read_text())['entries']}
    for rule in rules['rules']:
        if rule['parentEntryId']:assert rule['parentEntryId'] in parents
    source_ids={s['id'] for s in data['evidenceSources']}
    if source['id'] not in source_ids:data['evidenceSources'].append(source)
    changed=[]
    for row in data['objects']:
        rule=rule_by_term.get(row['names']['en'])
        if not rule or row['kind']!='muscle' or not row['localDisplayEligible']:continue
        before={k:copy.deepcopy(row.get(k)) for k in ['label','names','aliases','nameSourceIds','nameEvidence']}
        row.setdefault('nameEvidence',{})
        row['aliases']=list(dict.fromkeys(row['aliases']+[row['label'],row['names']['koModern'],row['names']['koTraditional'],rule['koModern'],rule['koTraditional']]+rule['aliases']))
        row['label']=rule['koTraditional']
        row['names']={**row['names'],'koModern':rule['koModern'],'koTraditional':rule['koTraditional']}
        row['nameSourceIds']=list(dict.fromkeys(row['nameSourceIds']+[source['id']]))
        for field in ['koModern','koTraditional']:
            row['nameEvidence'][field]={'value':rule[field],'sourceIds':[source['id']],'locator':f"T58 composed display, not dictionary headword: exact sourceTerm={rule['sourceTerm']}; parentEntryId={rule['parentEntryId']}; {rule['basis']}"}
        if before!={k:row[k] for k in before}:changed.append(row['sourceKey'])
    return changed

if __name__=='__main__':
    args=argparse.ArgumentParser();args.add_argument('--check',action='store_true');ns=args.parse_args()
    data=json.loads(OVERLAY.read_text());before=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
    changed=apply(data,json.loads(RULES.read_text()));out=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
    if ns.check:
        assert not changed,'T58 display rules are not applied'
    else:OVERLAY.write_text(out)
    print(json.dumps({'status':'passed' if ns.check else 'applied','changedSourceRows':len(changed)}))
