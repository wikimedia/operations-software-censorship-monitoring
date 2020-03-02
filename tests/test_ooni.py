import datetime
import unittest
from unittest.mock import patch

from psycopg2 import OperationalError
from psycopg2.extras import RealDictRow

from cescout.projects import ooni


class TestOONI(unittest.TestCase):
    def setUp(self):
        self.since = datetime.datetime.fromisoformat("2020-02-01T10:00:00")
        self.until = datetime.datetime.fromisoformat("2020-02-02T10:00:00")
        self.query = [RealDictRow([('measurement_start_time', datetime.datetime(2020, 2, 11, 6, 53, 37)),
                                   ('report_id', '20200211T065336Z_AS4134_4M0eNXqQCp1mrHumzmR73pHhLRMyVh1dAc4VYcoICjBAkqjxlZ'),
                                   ('probe_asn', 4134),
                                   ('probe_cc', 'CN'),
                                   ('probe_ip', None),
                                   ('test_name', 'web_connectivity'),
                                   ('input', 'https://zh.wikipedia.org/'),
                                   ('blocking', 'tcp_ip'),
                                   ('http_experiment_failure', 'generic_timeout_error')]),
                      RealDictRow([('measurement_start_time', datetime.datetime(2020, 2, 13, 6, 16, 19)),
                                   ('report_id', '20200213T061554Z_AS45102_IVK2a2mfaXQTip5xHVezqfun2jnQo8auGA0D5JTEHK3ovOmrx1'),
                                   ('probe_asn', 45102),
                                   ('probe_cc', 'CN'),
                                   ('probe_ip', None),
                                   ('test_name', 'web_connectivity'),
                                   ('input', 'https://fr.wikipedia.org/'),
                                   ('blocking', 'false'),
                                   ('http_experiment_failure', None)]),
                      RealDictRow([('measurement_start_time', datetime.datetime(2020, 2, 11, 6, 53, 37)),
                                   ('report_id', '20200211T065336Z_AS4134_4M0eNXqQCp1mrHumzmR73pHhLRMyVh1dAc4VYcoICjBAkqjxlZ'),
                                   ('probe_asn', 0),
                                   ('probe_cc', 'VN'),
                                   ('probe_ip', None),
                                   ('test_name', 'web_connectivity'),
                                   ('input', 'https://zh.wikipedia.org/'),
                                   ('blocking', 'tcp_ip'),
                                   ('http_experiment_failure', 'generic_timeout_error')]),
                      RealDictRow([('measurement_start_time', datetime.datetime(2020, 2, 13, 6, 16, 19)),
                                   ('report_id', '20200213T061554Z_AS45102_IVK2a2mfaXQTip5xHVezqfun2jnQo8auGA0D5JTEHK3ovOmrx1'),
                                   ('probe_asn', 45102),
                                   ('probe_cc', 'CA'),
                                   ('probe_ip', None),
                                   ('test_name', 'web_connectivity'),
                                   ('input', 'https://fr.wikipedia.org/'),
                                   ('blocking', 'false'),
                                   ('http_experiment_failure', "unknown_failure")])]
        self.config = {"db_name": "metadb", "db_user": "postgres",
                       "domains": ["wikipedia.org"]}
        self.expected_results = {'len_all': 2, 'len_blocking': 1,
                                 'measurements': [
                                   {'url': 'https://explorer.ooni.io/measurement/20200211T065336Z_AS4134_4M0eNXqQCp1mrHumzmR73pHhLRMyVh1dAc4VYcoICjBAkqjxlZ?input=https%3A//zh.wikipedia.org/', 'blocking': 'tcp_ip'},
                                   {'url': 'https://explorer.ooni.io/measurement/20200213T061554Z_AS45102_IVK2a2mfaXQTip5xHVezqfun2jnQo8auGA0D5JTEHK3ovOmrx1?input=https%3A//fr.wikipedia.org/', 'blocking': 'false'}
                                  ]}
        self.unexpected_results = {'len_all': 2, 'len_blocking': 0,
                                   'measurements': [
                                     {'url': 'https://explorer.ooni.io/measurement/20200211T065336Z_AS4134_4M0eNXqQCp1mrHumzmR73pHhLRMyVh1dAc4VYcoICjBAkqjxlZ?input=https%3A//zh.wikipedia.org/', 'blocking': 'dns'},
                                     {'url': 'https://explorer.ooni.io/measurement/20200213T061554Z_AS45102_IVK2a2mfaXQTip5xHVezqfun2jnQo8auGA0D5JTEHK3ovOmrx1?input=https%3A//fr.wikipedia.org/', 'blocking': 'false'}
                                   ]}

    def test_run_query(self):
        with patch("cescout.projects.ooni.run_query", return_value=self.query):
            self.assertEqual(ooni.run_query("CN", self.since, self.until, self.config),
                             self.query)
        with patch("psycopg2.connect") as mock:
            mock.return_value.cursor.return_value.fetchall.return_value = [("some_value")]
            self.assertEqual(ooni.run_query("CN", self.since, self.until, **self.config),
                             None)
            ooni_config = {"ooni": self.config}
            self.assertEqual(ooni.run_query("CN", self.since, self.until, **ooni_config),
                             [("some_value")])
            mock.return_value.cursor.side_effect = OperationalError()
            self.assertEqual(ooni.run_query("CN", self.since, self.until, **ooni_config),
                             None)

    def test_process_results(self):
        self.assertEqual(ooni.process_results(self.query),
                         self.expected_results)
        self.assertNotEqual(ooni.process_results(self.query),
                            self.unexpected_results)

    def test_format_date(self):
        self.assertEqual(ooni.format_date(self.since),
                         "2020-02-01")
        self.assertNotEqual(ooni.format_date(self.since),
                            "2020-02-01T10:00:00")

    def test_run(self):
        with patch("cescout.projects.ooni.run_query") as mock:
            mock.side_effect = [self.query, None]
            self.assertEqual(ooni.run("CN", 1, self.since, self.until, self.config),
                             self.expected_results)
            self.assertEqual(ooni.run("CN", 1, self.since, self.until, self.config),
                             None)
            mock.assert_called_with("CN", "2020-02-01", "2020-02-02")
