"""Contextual naming must be reproducible without changing anatomical identity."""
import copy, json, subprocess, unittest
from apply_composed_names import ROOT, apply
class NamingTests(unittest.TestCase):
    def test_replay_preserves_identity_and_holds(self):
        original=json.loads(subprocess.check_output(['git','show','b105fad72f3bb66d638fcb680cce138ebf2b54ad:atlas-data/overlays/za-local-integration.json'],cwd=ROOT))
        current=json.loads((ROOT/'atlas-data/overlays/za-local-integration.json').read_text())
        rules=json.loads((ROOT/'atlas-data/terminology/rules/composed-parts.json').read_text())
        learning=json.loads((ROOT/'atlas-data/terminology/learning-names.json').read_text())
        replay=copy.deepcopy(original);apply(replay,rules,learning)
        self.assertEqual(replay,current)
        self.assertEqual(apply(replay,rules,learning),[])
        permitted={'names','label','nameEvidence','nameSourceIds'}
        for old,new in zip(original['objects'],replay['objects']):
            self.assertEqual({k:v for k,v in old.items() if k not in permitted},{k:v for k,v in new.items() if k not in permitted})
            self.assertEqual(old['names']['en'],new['names']['en'])
            if not old['localDisplayEligible']:self.assertEqual(old,new)
    def test_unknown_source_is_not_named_by_similarity(self):
        data=json.loads((ROOT/'atlas-data/overlays/za-local-integration.json').read_text())
        row=copy.deepcopy(next(r for r in data['objects'] if r['localDisplayEligible']))
        row['names']={'koModern':None,'koTraditional':None,'en':'Unknown muscle similar to masseter'}
        row['label']=row['names']['en'];data['objects']=[row]
        rules=json.loads((ROOT/'atlas-data/terminology/rules/composed-parts.json').read_text())
        learning=json.loads((ROOT/'atlas-data/terminology/learning-names.json').read_text())
        self.assertEqual(apply(data,rules,learning),[])
        self.assertIsNone(row['names']['koModern'])
if __name__=='__main__':unittest.main()
