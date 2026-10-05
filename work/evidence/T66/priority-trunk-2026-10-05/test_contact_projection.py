import unittest
import pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[4]/'work/tools'))
import numpy as np
from trunk_contact_patch import _weighted_halfspace_projection
class ContactProjectionRegression(unittest.TestCase):
 def test_later_plane_must_not_silently_break_earlier_plane(self):
  x,n,w,e=_weighted_halfspace_projection([[1,0],[-1,1]],[1,1],[],[],[1,1])
  self.assertGreater(n,1);np.testing.assert_allclose(x,[1,2],atol=1e-8);self.assertLess(w,1e-9)
 def test_equality_and_collision_plane_remain_satisfied_together(self):
  x,n,w,e=_weighted_halfspace_projection([[1,0]],[1],[[1,-1]],[0],[1,2])
  np.testing.assert_allclose(x,[1,1],atol=1e-8);self.assertLess(e,1e-9)
if __name__=='__main__':unittest.main()
