"""Numerical tests of shared offline bounded field composition, no anatomy approval."""
import unittest,numpy as np
from at10_skin_field_math import landmark_flow_operator,regional_shape_operator,solve_landmark_flow
class Fields(unittest.TestCase):
 def test_composed_analytic_derivative_and_positive_3d_orientation(self):
  g={'kind':'gaussian_translation','centreM':[.02,1.6,0],'sigmaM':.04,'translationM':[.002,.001,.003]};g['globalDisplacementLipschitzBound']=float(np.linalg.norm(g['translationM'])/(np.sqrt(np.e)*g['sigmaM']))
  f={'kind':'regional_affine','centreM':[0,1.64,-.012],'sigmaM':.09,'linearDisplacement':[.08,0,.22],'axialWindowY':[1.56,1.64]};f['globalDisplacementLipschitzBound']=float(.22*(1+2/np.e+1.5/.08*.09/np.sqrt(np.e)))
  base={'affine':np.eye(3).tolist(),'translation':[0,.003,0],'stages':[],'postFields':[g]};recipe={'affine':np.eye(3).tolist(),'translation':[0,0,0],'stages':[],'initialField':base,'postFields':[f]};op=landmark_flow_operator(recipe);p=np.random.default_rng(12).uniform([-.1,1.5,-.12],[.1,1.72,.12],(200,3));v,j=op(p);fd=np.stack([(op(p+np.eye(3)[i]*1e-6)[0]-op(p-np.eye(3)[i]*1e-6)[0])/(2e-6) for i in range(3)],2);self.assertLess(abs(fd-j).max(),1e-7);self.assertGreater(np.linalg.det(j).min(),0);self.assertTrue(np.isfinite(v).all())
 def test_unbounded_correction_and_reflected_source_map_rejected(self):
  with self.assertRaises(AssertionError):landmark_flow_operator({'affine':np.diag([-1,1,1]).tolist(),'translation':[0,0,0],'stages':[]})
  with self.assertRaises(AssertionError):regional_shape_operator({'kind':'gaussian_translation','centreM':[0,0,0],'sigmaM':.01,'translationM':[1,0,0],'globalDisplacementLipschitzBound':0})
 def test_landmark_solver_replays_constraints_without_granting_geometry_acceptance(self):
  controls=[{'source':p,'target':(np.asarray(p)+[.002,0,0]).tolist(),'sigmaM':.04} for p in [[0,0,0],[.04,0,0],[0,.04,0],[0,0,.04]]];recipe=solve_landmark_flow(controls,initial_affine=np.eye(3),initial_translation=np.zeros(3));p,j=landmark_flow_operator(recipe)([x['source'] for x in controls]);self.assertLess(np.linalg.norm(p-np.array([x['target'] for x in controls]),axis=1).max(),1e-8);self.assertTrue(recipe['sourceMeaningNotApprovedBySolver']);self.assertGreater(np.linalg.det(j).min(),0)
if __name__=='__main__':unittest.main()
