import unittest

from cescout import common


class TestCountryCodes(unittest.TestCase):
    def setUp(self):
        self.cc = ["VN", "TR", "ZZ"]
        self.cc_name = ["Viet Nam", "Turkey", "Unknown"]
        self.codes = {k: v for (k, v) in zip(self.cc, self.cc_name)}

    def test_country_name(self):
        for each in self.cc:
            self.assertEqual(common.country_name(each),
                             self.codes[each])
