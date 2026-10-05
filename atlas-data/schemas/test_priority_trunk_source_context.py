"""Bilateral context must be explicitly verified; subject-side checks remain separate."""
import unittest,copy
from validate_motion_learning import verified_family_bone_context
class SourceContextRegression(unittest.TestCase):
 def setUp(self):
  self.definition={'sourceFamilyId':'trunk','side':'left'}
  self.context={'sourceInstances':{'R-HIP':{'kind':'skeletal_surface','sourceLabelSide':'right'},'L1':{'kind':'skeletal_surface','sourceLabelSide':None}},'authoringRecords':{'author':{'sourceFamilyId':'trunk','movingBoneKeys':['L1'],'fixedBoneKeys':['R-HIP'],'_verifiedFamilyBoneContext':{'R-HIP':{'role':'fixed_structure','side':'right'},'L1':{'role':'moving_structure','side':None}}}}}
 def test_verified_opposite_and_axial_context(self):
  self.assertTrue(verified_family_bone_context('R-HIP','fixed_structure',self.definition,self.context));self.assertTrue(verified_family_bone_context('L1','moving_structure',self.definition,self.context))
 def test_context_does_not_infer_or_change_bone_side(self):
  self.context['authoringRecords']['author']['_verifiedFamilyBoneContext']['R-HIP']['side']='left';self.assertFalse(verified_family_bone_context('R-HIP','fixed_structure',self.definition,self.context))
 def test_missing_verification_or_wrong_role_fails_closed(self):
  self.assertFalse(verified_family_bone_context('R-HIP','moving_structure',self.definition,self.context));self.context['authoringRecords']['author'].pop('_verifiedFamilyBoneContext');self.assertFalse(verified_family_bone_context('L1','moving_structure',self.definition,self.context))
 def test_nonbone_source_and_unknown_family_are_rejected(self):
  self.context['sourceInstances']['L1']['kind']='muscular_surface';self.assertFalse(verified_family_bone_context('L1','moving_structure',self.definition,self.context));self.definition['sourceFamilyId']='other';self.assertFalse(verified_family_bone_context('R-HIP','fixed_structure',self.definition,self.context))
if __name__=='__main__':unittest.main()
