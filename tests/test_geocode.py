import unittest
from app.utils import geocode


class ParseCsvTestCase(unittest.TestCase):

    # Check that geocoded coordinates match expected values
    def test_geocode(self):
        loc1 = geocode('15 & chestnut')
        self.assertAlmostEqual(float(loc1[0]), 39.951304, places=3)
        self.assertAlmostEqual(float(loc1[1]), -75.165601, places=3)

        loc2 = geocode('Poplar & n American')
        self.assertAlmostEqual(float(loc2[0]), 39.964792, places=3)
        self.assertAlmostEqual(float(loc2[1]), -75.141594, places=3)

        loc3 = geocode('Broad & arch')
        self.assertAlmostEqual(float(loc3[0]), 39.954659, places=3)
        self.assertAlmostEqual(float(loc3[1]), -75.163059, places=3)

    # Check that failed geocode returns None, None
    def test_geocode_fail(self):
        loc4 = geocode('I am happy!')
        self.assertTrue(loc4[0] is None)
        self.assertTrue(loc4[1] is None)
