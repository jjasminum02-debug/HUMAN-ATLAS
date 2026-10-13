import unittest
from extract_acupoint_portfolio import consume, methods, HEADER
class ExtractionTests(unittest.TestCase):
    def test_only_method_cells(self):
        self.assertEqual(methods([['규격/자침깊이','private'],['탐혈 과정','landmarks'],['느낀점','private']]),['landmarks'])
    def test_column_and_page_continuation(self):
        rows, prev=consume([(10,'heading',('LI','15','견우'))],None,5)
        rows, prev=consume([(10,'table',((0,10,100,30),'어깨를 들어올린다.'))],prev,6)
        self.assertEqual((rows[0]['code'],rows[0]['headingPage'],rows[0]['page']),('LI15',5,6))
        self.assertEqual(rows[0]['postureCueCandidates'],['arm_raise'])
        self.assertIsNone(rows[0]['modelBinding'])
    def test_leading_punctuation_is_not_previous_point(self):
        self.assertEqual(HEADER.match('‘KI23 신봉(神封)').groups()[:2],('KI','23'))
    def test_unassigned_cell_is_error(self):
        with self.assertRaises(ValueError):consume([(5,'table',((0,5,100,30),'method'))],None,1)
if __name__=='__main__':unittest.main()
