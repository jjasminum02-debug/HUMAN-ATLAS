"""python3 -m unittest atlas-data/pipeline/test_za_classify.py"""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from za_classify import classify  # noqa: E402

JOINT_LL = [['Bonus collection', 'Arthrology', 'Joints of lower limb', 'Joints of free lower limb']]


class ClassifyTest(unittest.TestCase):
    def kind(self, name, top, paths=(), parent=None):
        return classify(name, top, list(paths), parent)

    def test_label_lines_and_aggregates_are_excluded(self):
        self.assertIn('exclude', self.kind('Ankle joint.j', '3: Joints'))
        self.assertIn('exclude', self.kind('Joints.g', '3: Joints'))

    def test_out_of_scope_collection(self):
        self.assertEqual(self.kind('Liver', '8: Visceral systems')['exclude'], 'collection_out_of_scope_8')

    def test_cardiovascular_kinds(self):
        cv = '5: Cardiovascular system'
        arteries, veins = [['Bonus collection', 'Cardiovascular system', 'Systemic arteries']], [['Bonus collection', 'Cardiovascular system', 'Systemic veins']]
        self.assertEqual(self.kind('Femoral artery.l', cv, arteries)['kind'], 'artery')
        self.assertEqual(self.kind('Great saphenous vein.r', cv, veins)['kind'], 'vein')
        self.assertEqual(self.kind('Sigmoid sinus.l', cv)['kind'], 'vein')
        self.assertEqual(self.kind('Left ventricle', cv)['kind'], 'heart')
        self.assertEqual(self.kind('Apex of heart', cv)['kind'], 'heart_landmark')
        self.assertEqual(self.kind('????????', cv)['exclude'], 'unnamed_object')

    def test_joint_kinds(self):
        self.assertEqual(self.kind('Anterior cruciate ligament.r', '3: Joints', JOINT_LL)['kind'], 'ligament')
        self.assertEqual(self.kind('Medial meniscus.l', '3: Joints', JOINT_LL)['kind'], 'meniscus')
        self.assertEqual(self.kind('Anterior meniscotibial ligament (Lateral meniscus).r', '3: Joints')['kind'], 'ligament')
        self.assertEqual(self.kind('Acetabular labrum.l', '3: Joints')['kind'], 'labrum')
        self.assertEqual(self.kind('Articular capsule of elbow joint.r', '3: Joints')['kind'], 'capsule')
        self.assertEqual(self.kind('Intervertebral disc L3-L4', '3: Joints')['kind'], 'disc')
        self.assertEqual(self.kind('Infrapatellar fat pad.r', '3: Joints')['kind'], 'fat_pad')

    def test_side(self):
        self.assertEqual(self.kind('Medial meniscus.l', '3: Joints')['side'], 'left')
        self.assertEqual(self.kind('Pubic symphysis', '3: Joints')['side'], 'unpaired')

    def test_muscular_kinds_prefer_collections(self):
        fascia = [['Bonus collection', 'Muscular system', 'Fascia']]
        self.assertEqual(self.kind('Brachial fascia.l', '4: Muscular system', fascia)['kind'], 'fascia')
        self.assertEqual(self.kind('Tensor fasciae latae.r', '4: Muscular system')['kind'], 'muscle')
        self.assertEqual(self.kind('Extensor retinaculum of wrist.r', '4: Muscular system')['kind'], 'retinaculum')
        self.assertEqual(self.kind('(Iliopectineal bursa).l', '4: Muscular system')['kind'], 'bursa')

    def test_connective_tissue_in_muscular_collection(self):
        self.assertEqual(self.kind('Calcaneal tendon.l', '4: Muscular system')['kind'], 'tendon')
        self.assertEqual(self.kind('Tendon of extensor digitorum longus.r', '4: Muscular system')['kind'], 'tendon')
        self.assertEqual(self.kind('Iliotibial tract.l', '4: Muscular system')['kind'], 'fascia')
        self.assertEqual(self.kind('Inguinal ligament.r', '4: Muscular system')['kind'], 'ligament')
        self.assertEqual(self.kind('Superior tarsus.l', '4: Muscular system')['kind'], 'connective')
        self.assertEqual(self.kind('Gastrocnemius muscle.l', '4: Muscular system')['kind'], 'muscle')

    def test_skeletal_cavities(self):
        self.assertEqual(self.kind('Sinus of frontal bone', '1: Skeletal system')['kind'], 'cavity')
        self.assertEqual(self.kind('Middle cells of ethmoid bone.l', '1: Skeletal system')['kind'], 'cavity')

    def test_attachments(self):
        o = self.kind('Abductor hallucis.ol', '2: Muscular insertions', parent='Calcaneus.l')
        self.assertEqual((o['kind'], o['side'], o['muscle'], o['bone']), ('origin', 'left', 'Abductor hallucis', 'Calcaneus.l'))
        e = self.kind('Longissimus thoracis muscle.e25r', '2: Muscular insertions')
        self.assertEqual((e['kind'], e['side'], e['patch']), ('insertion', 'right', 25))
        p = self.kind('(Abdominal part of pectoralis major muscle).or', '2: Muscular insertions')
        self.assertTrue(p['parenthesized'])
        self.assertEqual(p['name'], 'Abdominal part of pectoralis major muscle')

    def test_skeletal_kinds(self):
        self.assertEqual(self.kind('Upper first molar tooth.r', '1: Skeletal system')['kind'], 'tooth')
        self.assertEqual(self.kind('Femur.l', '1: Skeletal system')['kind'], 'bone')

    def test_nervous_kinds(self):
        self.assertEqual(self.kind('Optic nerve (II).r', '7: Nervous system & Sense organs')['kind'], 'nerve')
        self.assertEqual(self.kind('Retina.l', '7: Nervous system & Sense organs')['kind'], 'sense_organ')
        self.assertEqual(self.kind('Lateral corticospinal tract', '7: Nervous system & Sense organs')['kind'], 'cns')

    def test_ids_keep_prime_mark(self):
        self.assertNotEqual(self.kind("Central canal'", '7: Nervous system & Sense organs')['id'],
                            self.kind('Central canal', '7: Nervous system & Sense organs')['id'])

    def test_regions_from_main_divisions(self):
        paths = [['Bonus collection', 'Regions of human body', 'Main divisions', 'Left lower limb']]
        self.assertEqual(self.kind('Medial meniscus.l', '3: Joints', paths)['regions'], ['lower_limb'])


if __name__ == '__main__':
    unittest.main()
