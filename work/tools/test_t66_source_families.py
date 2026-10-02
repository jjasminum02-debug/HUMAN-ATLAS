"""Real production family contracts: source-only support without canonical promotion.

Mutation cases ensure that removing the old canonical-ID prerequisite does not
permit orphan families, wrong pose/side, different buffers or unrelated evidence.
"""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('motion_validator', ROOT / 'atlas-data/schemas/validate_motion_learning.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

class SourceFamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(v.SCHEMA_PATH.read_text())
        cls.context = v.load_production_context()
        bundle = json.loads(v.DATA_PATH.read_text())
        cls.assets = [a for a in bundle['motionAssets'] if a.get('sourceBinding', {}).get('sourceFamilyId')]
        cls.bundles = []
        for asset in cls.assets:
            definition = next(d for d in bundle['motionDefinitions'] if d['id'] == asset['motionDefinitionId'])
            action = next(a for a in bundle['muscleActions'] if a['id'] == definition['actionId'])
            cls.bundles.append({'schemaVersion': bundle['schemaVersion'], 'revision': bundle['revision'],
                'muscleActions': [action], 'motionDefinitions': [definition], 'motionAssets': [asset]})
        cls.sample = next(b for b in cls.bundles if b['motionDefinitions'][0]['instanceId'] == 'ZA-c7010a9-e65b8c86027df88000cfa861')

    def issues(self, bundle):
        return v.validate_bundle(bundle, self.schema, self.context)

    def test_every_registered_subject_without_canonical_promotion(self):
        self.assertEqual(len(self.assets), 246)
        self.assertEqual(len({a['sourceBinding']['sourceFamilyId'] for a in self.assets}), 6)
        for bundle in self.bundles:
            with self.subTest(subject=bundle['motionDefinitions'][0]['instanceId']):
                self.assertEqual(self.issues(bundle), [])
                self.assertEqual(bundle['muscleActions'][0]['subjectIds'], [])
                self.assertEqual(bundle['motionDefinitions'][0]['targetJointIds'], [])

    def test_unrelated_family_cannot_bind(self):
        b = copy.deepcopy(self.sample)
        b['motionDefinitions'][0]['sourceFamilyId'] = 'hip-abduction-right'
        self.assertIn('motion_source_family_mismatch', {i['code'] for i in self.issues(b)})

    def test_same_bytes_cannot_promote_normal_range(self):
        b = copy.deepcopy(self.sample)
        b['motionAssets'][0]['poseControl']['endDegrees'] = 90
        self.assertIn('source_family_asset_mismatch', {i['code'] for i in self.issues(b)})

    def test_wrong_side_rejected(self):
        b = copy.deepcopy(self.sample)
        b['motionDefinitions'][0]['side'] = 'left'
        self.assertIn('motion_source_family_mismatch', {i['code'] for i in self.issues(b)})

    def test_canonical_state_requires_canonical_joint(self):
        b = copy.deepcopy(self.sample)
        b['muscleActions'][0]['jointBindingState'] = 'canonical_bound'
        b['muscleActions'][0]['jointBindingNote'] = None
        self.assertIn('motion_canonical_joint_required', {i['code'] for i in self.issues(b)})

    def test_different_pose_evidence_rejected(self):
        b = copy.deepcopy(self.sample)
        b['motionDefinitions'][0]['poseSourceRefs'][0]['valueHash'] = 'a' * 64
        self.assertIn('invalid_authoring_pose_reference', {i['code'] for i in self.issues(b)})

    def test_different_action_field_rejected(self):
        b = copy.deepcopy(self.sample)
        b['muscleActions'][0]['sourceRefs'][0]['valueHash'] = 'a' * 64
        self.assertIn('invalid_source_family_reference', {i['code'] for i in self.issues(b)})

if __name__ == '__main__':
    unittest.main()
