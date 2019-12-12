import unittest
import argparse
import datetime
import logging

from psycopg2.extras import RealDictRow

from ooni import oonifetch, datehelper


class TestOONIFetch(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.parser = argparse.ArgumentParser()
        self.parser.since = datehelper.validate_date("2019-09-01")
        self.parser.until = datehelper.validate_date("2019-09-02")

        logging.disable(logging.CRITICAL)

        self.query = [RealDictRow([('measurement_start_time',
                                   datetime.datetime(2019, 9, 10, 0, 56, 35)),
                                   ('report_id', '20190910T001641Z_AS137_8x54aTKV44JF3TYMDnHCPeEYylq8DqU1o3qlpIeHAv8ncsmCkX'),
                                   ('probe_asn', 137),
                                   ('probe_cc', 'IT'),
                                   ('probe_ip', '160.80.101.36'),
                                   ('test_name', 'web_connectivity'),
                                   ('test_runtime', 0.850034),
                                   ('anomaly', None),
                                   ('confirmed', None),
                                   ('input', 'https://commons.wikimedia.org/'),
                                   ('blocking', 'false'),
                                   ('http_experiment_failure', None),
                                   ('dns_experiment_failure', None),
                                   ('control_failure', None)]),
                      RealDictRow([('measurement_start_time',
                                   datetime.datetime(2019, 9, 10, 8, 23, 17)),
                                   ('report_id', '20190913T040421Z_AS7470_dhYNAd9X8zjkHJu6GQVi1j7ufIK7hmdhSfqge676EMwUAJig47'),
                                   ('probe_asn', 7470),
                                   ('probe_cc', 'TH'),
                                   ('probe_ip', None),
                                   ('test_name', 'web_connectivity'),
                                   ('test_runtime', 0.00303888),
                                   ('anomaly', None),
                                   ('confirmed', None),
                                   ('input', 'https://de.wikipedia.org/'),
                                   ('blocking', None),
                                   ('http_experiment_failure', 'dns_lookup_error'),
                                   ('dns_experiment_failure', 'deferred_timeout_error'),
                                   ('control_failure', None)])]
        self.all_c = {
            'IT': [
                {'measurement_time': datetime.datetime(2019, 9, 10, 0, 56, 35),
                 'report_id': '20190910T001641Z_AS137_8x54aTKV44JF3TYMDnHCPeEYylq8DqU1o3qlpIeHAv8ncsmCkX',
                 'asn': 137,
                 'country':
                 'IT',
                 'url': 'https://commons.wikimedia.org/',
                 'blocking': 'false',
                 'http_failure': None,
                 'report_link': 'https://explorer.ooni.io/measurement/20190910T001641Z_AS137_8x54aTKV44JF3TYMDnHCPeEYylq8DqU1o3qlpIeHAv8ncsmCkX?input=https%3A//commons.wikimedia.org/',
                 'count': 0}
                  ],
            'TH': [
                {'measurement_time': datetime.datetime(2019, 9, 10, 8, 23, 17),
                 'report_id': '20190913T040421Z_AS7470_dhYNAd9X8zjkHJu6GQVi1j7ufIK7hmdhSfqge676EMwUAJig47',
                 'asn': 7470,
                 'country': 'TH',
                 'url': 'https://de.wikipedia.org/',
                 'blocking': None,
                 'http_failure': 'dns_lookup_error',
                 'report_link': 'https://explorer.ooni.io/measurement/20190913T040421Z_AS7470_dhYNAd9X8zjkHJu6GQVi1j7ufIK7hmdhSfqge676EMwUAJig47?input=https%3A//de.wikipedia.org/',
                 'count': 1}
                   ],
        }
        self.anom_c = {'IT': 0, 'TH': 1}
        self.one_anom_c = ['TH']

    def test_process_results(self):
        self.assertEqual(oonifetch.process_results(self.query),
                         (self.all_c, self.anom_c, self.one_anom_c))

    def test_validate_date(self):
        with self.assertRaises(ValueError):
            datehelper.validate_date("2019-20-09")
        self.assertEqual(datetime.datetime(2019, 9, 9),
                         datehelper.validate_date("2019-09-09"))


if __name__ == "__main__":
    unittest.main()
