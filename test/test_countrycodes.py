import unittest

from ooni import countrycodes


class TestCountryCodes(unittest.TestCase):
    def setUp(self):
        self.cc = ["ZZ", "VN", "TR", "CN"]
        self.cc_name = ["Unknown", "Viet Nam", "Turkey", "China"]
        self.country_codes = countrycodes.get_codes()

        if self.country_codes:
            self.control_code = {k: v for (k, v) in zip(self.cc, self.cc_name)}
            self.sample_code = {k: self.country_codes[k] for (k, v) in
                                zip(self.cc, self.control_code.keys())}
        else:
            self.control_code = {}
            self.sample_code = {}

    def test_codes(self):
        self.assertEqual(self.control_code, self.sample_code)


if __name__ == "__main__":
    unittest.main()
