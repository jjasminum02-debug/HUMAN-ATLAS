#!/usr/bin/env python3
"""Offline regressions for T72 exact-source acquisition, identity, frame and holds."""
from __future__ import annotations
import hashlib, importlib.util, json, unittest, zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
IDS=['FJ1433','FJ1433M','FJ1446','FJ1446M','FJ1447','FJ1447M','FJ1464','FJ1464M','FJ3200','FJ3289','FJ3309']
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);assert s and s.loader;s.loader.exec_module(m);return m
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ACQ=load('t72_acq',ROOT/'atlas-data/tools/acquire_bodyparts3d_r4_t72.py')
BUILD=load('t72_build',ROOT/'atlas-data/tools/build_bodyparts3d_r4_t72.py')
class T72Tests(unittest.TestCase):
 def test_freeze_exact_batches_and_target_scope(self):
  f=read(BUILD.FREEZE)
  self.assertEqual(f['sourceElementFileIds'],IDS)
  self.assertEqual([len(x['sourceElementFileIds']) for x in f['internalBatches']],[10,1])
  self.assertEqual(len(f['uniqueSourceAssets']),11)
  self.assertEqual(len(set(f['sourceElementFileIds'])),11)
  scope=read(BUILD.SCOPE)
  self.assertEqual(scope['productFirstPassMinimum']['remainingAfterT71Batch'],IDS)
  self.assertEqual(f['status'],'frozen_before_mesh_acquisition')
 def test_range_acquisition_archive_crc_raw_sha_and_no_full_archive(self):
  check=ACQ.check();a=read(BUILD.ACQ)
  self.assertEqual(check['sourceElementFileCount'],11)
  self.assertEqual([len(x['sourceElementFileIds']) for x in a['internalBatchResults']],[10,1])
  self.assertFalse(a['fullArchivesDownloaded'])
  self.assertTrue(a['selectedMemberRangeRequestsOnly'])
  self.assertTrue(a['officialArchive']['allRequestsUsedHTTP206'])
  self.assertEqual([r['sourceElementFileId'] for r in a['files']],IDS)
  for r in a['files']:
   self.assertEqual(r['status'],'acquired')
   self.assertEqual(r['archiveTree'],'IS-A')
   self.assertEqual(r['sha256'],sha(ROOT/r['cacheRelativePath']))
   self.assertEqual(int(r['crc32'],16),zlib.crc32((ROOT/r['cacheRelativePath']).read_bytes())&0xffffffff)
 def test_exact_obj_header_fma_bp_and_side_specific_official_relations(self):
  manifest=read(BUILD.OUT_MANIFEST); rows=manifest['sourceAssets']
  self.assertEqual([r['sourceElementFileId'] for r in rows],IDS)
  expected={'FJ1433':'right','FJ1433M':'left','FJ1446':'right','FJ1446M':'left','FJ1447':'right','FJ1447M':'left','FJ1464':'right','FJ1464M':'left','FJ3200':'not_lateralized_by_official_relations','FJ3289':'not_lateralized_by_official_relations','FJ3309':'not_lateralized_by_official_relations'}
  for r in rows:
   fid=r['sourceElementFileId']
   self.assertEqual(r['sourceFmaConceptId'],r['sourceOfficialHeaderRelation']['sourceFmaConceptId'])
   self.assertTrue(r['sourceRepresentationId'].startswith('BP'))
   self.assertEqual(r['lateralityFromExplicitOfficialRelation'],expected[fid])
   self.assertEqual(r['sourceOfficialLateralityEvidence']['side'],None if expected[fid].startswith('not_lateralized') else expected[fid])
   self.assertTrue(r['lateralityNotInferredFromFjSuffixOrCoordinates'])
   self.assertTrue(r['sourceHeaderLicenseObservation'])
   self.assertFalse(r['canonicalLearnerIds'])
 def test_mesh_glb_frame_and_no_duplicate_source_geometry(self):
  m=read(BUILD.OUT_MANIFEST);v=read(BUILD.OUT_VALIDATION)
  self.assertTrue(v['nonemptyMeshes']);self.assertEqual(v['exactDuplicateGeometryTopologyGroups'],[])
  self.assertTrue(v['glbPositionsMatchSourceTransform'])
  self.assertEqual(v['oneGlbNodePerFj'],True)
  self.assertEqual(v['derivedGlb']['meshNodeCount'],11)
  for r in m['sourceAssets']:
   self.assertEqual(r['sourceUnit'],'mm from exact OBJ Bounds(mm) header')
   self.assertEqual(r['projectFrame'],'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR')
   self.assertIn('[x,y,z]mm -> [x,z,-y]m',r['transform'])
   self.assertGreater(r['sourceTriangleCount'],0)
  # Four source headers have measurable (0.0954–0.2290 mm) bounds/extrema differences;
  # they remain observations and never replace the raw vertex coordinates.
  self.assertEqual(set(v['boundsDiscrepancyIdsOver001mm']),{'FJ1433','FJ1446','FJ1447','FJ1464'})
  self.assertEqual(max(x['maxAbsDeltaMm'] for x in v['sourceHeaderBoundsVsVerticesMm'].values()),max(r['sourceBoundsHeaderMaxAbsDeltaMm'] for r in m['sourceAssets']))
 def test_t70_sibling_extension_first_pass_and_bone_root_recalculation(self):
  e=read(BUILD.OUT_INTEGRATION);v=read(BUILD.OUT_VALIDATION);base=read(BUILD.BASE);t71=read(BUILD.T71_INTEGRATION)
  self.assertEqual(e['parentIntegrationManifest']['sha256'],sha(BUILD.BASE))
  self.assertTrue(e['parentIntegrationManifest']['historicalManifestUnchanged'])
  self.assertEqual(e['siblingPackageReferences'][0]['integrationManifestSha256'],sha(BUILD.T71_INTEGRATION))
  self.assertEqual(len(set(r['sourceElementFileId'] for r in e['assets'])),len(e['assets']))
  self.assertEqual(v['T70FirstPassSourceCount'],20)
  self.assertEqual(v['T71FirstPassSourceIdsPresent'],9)
  self.assertEqual(v['T72FirstPassSourceIdsPresent'],11)
  self.assertEqual(v['firstPassResidualCountAfterT71AndT72'],0)
  self.assertEqual(v['T70BoneRootMissingSourceCount'],35)
  self.assertEqual(len(v['T71BoneRootResidualIds']),6)
  self.assertEqual(set(v['T72BoneRootResidualIds']),{'FJ3200','FJ3289','FJ3309'})
  self.assertEqual(v['boneRootResidualCountAfterT71AndT72'],26)
  self.assertEqual(base['counts']['uniqueSourceNodes'],493)
  self.assertEqual(t71['counts']['uniqueSourceNodesIncludingT71'],502)
  self.assertEqual(e['counts']['uniqueSourceNodesIncludingT72'],504)
  self.assertEqual(e['counts']['newCanonicalBindings'],0)
  self.assertEqual(e['counts']['newHumanReviewed'],0)
  self.assertTrue(all(not row['learnerDefaultVisible'] and row['learnerPickState']=='source_only_unbound' for row in e['assets'] if row['sourceElementFileId'] in IDS))
 def test_preservation_of_t70_t71_and_frozen_prior_inputs(self):
  baseline=read(ROOT/'work/evidence/T72/start-baseline.json')
  for rel in ['atlas-data/manifests/bodyparts3d-r4-t70/scope-inventory.json','atlas-data/manifests/bodyparts3d-r4-t70/integration-manifest.json','atlas-data/manifests/bodyparts3d-r4-t71/source-manifest.json','atlas-data/manifests/bodyparts3d-r4-t71/integration-manifest.json','atlas-data/manifests/bodyparts3d-r4-source-manifest-t51.json','atlas-data/manifests/bodyparts3d-r4-t52/head-neck.json','atlas-data/manifests/bodyparts3d-r4-t53/source-manifest.json','atlas-data/manifests/bodyparts3d-r4-t54/source-manifest.json','atlas-data/manifests/bodyparts3d-r4-t55/source-manifest.json','work/evidence/T53/frozen-source-set.json','work/evidence/T53/source-acquisition.json','work/evidence/T55/frozen-source-set.json','work/evidence/T55/source-acquisition.json']:
   self.assertEqual(sha(ROOT/rel),baseline['requiredInputSha256'][rel],rel)
  after=read(ROOT/'work/evidence/T72/preservation-after.json')
  self.assertTrue(after['originalBodyParts3dMeshesPreserved'])
  self.assertTrue(after['originalDerivedGlbsPreserved'])
  self.assertTrue(after['openSimUnchangedAndClean'])
 def test_rights_human_and_release_holds_remain_independent(self):
  m=read(BUILD.OUT_MANIFEST);v=read(BUILD.OUT_VALIDATION)
  self.assertFalse(v['humanAnatomyReviewed']);self.assertFalse(v['publicRelease'])
  self.assertEqual(m['rights']['redistributionStatus'],'held_pending_file_level_license_reconciliation_with_legacy_OBJ_headers')
  self.assertEqual(v['canonicalLearnerBindings'],0)
  self.assertTrue(all(r['lateralityNotInferredFromFjSuffixOrCoordinates'] for r in m['sourceAssets']))
if __name__=='__main__':unittest.main(verbosity=2)
