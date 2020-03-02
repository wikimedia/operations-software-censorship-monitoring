import unittest
from unittest.mock import patch

from requests.exceptions import HTTPError

from cescout.projects import ripe

REQUEST_RESPONSE = {
    "status": "ok",
    "query_id": "",
    "data": {
        "query_time": "2020-02-01T10:00:00",
    }
}

COUNTRY_RESPONSE = {
    "status": "ok",
    "data": {
        "query_time": "2020-02-02T10:00:00",
        "resources": {
            "ipv6": [
                "",
            ],
            "asn": [
                "1",
                "2",
                "3",
            ],
            "ipv4": [
                "",
            ]
        }
    }
}

ROUTING_RESPONSE = {
    "status": "ok",
    "data": {
        "query_time": "2020-02-03T10:00:00",
        "visibility": {
            "v4": {
                "total_ris_peers": 261,
                "ris_peers_seeing": 261
            },
            "v6": {
                "total_ris_peers": 254,
                "ris_peers_seeing": 0
            }
        },
        "announced_space": {
            "v4": {
                "prefixes": 30,
                "ips": 7680
            },
            "v6": {
                "prefixes": 0,
                "48s": 0
            }
        },
        "observed_neighbours": 3,
    }
}


class TestRIPE(unittest.TestCase):
    def setUp(self):
        self.since = "2020-02-01T10:00:00"
        self.until = "2020-02-02T10:00:00"
        self.asn_data_output = {1: {"current": 30, "since": 30, "until": 30}}

    def test_fetch_data(self):
        with patch("requests.get") as mock:
            mock.return_value.json.return_value = REQUEST_RESPONSE
            response = ripe.fetch_data("https://some.url")
            self.assertEqual(response, {"query_time": self.since})
            mock.assert_called_with("https://some.url")
        with patch("requests.get") as mock_error:
            mock_error.return_value.raise_for_status.side_effect = HTTPError()
            self.assertEqual(ripe.fetch_data("https://error.url"),
                             {})
            mock_error.assert_called_with("https://error.url")

    @patch("requests.get")
    def test_fetch_country_data(self, mock):
        mock.return_value.json.return_value = COUNTRY_RESPONSE
        country_data = ripe.fetch_country_data("CA")
        self.assertEqual(country_data, [1, 2, 3])
        self.assertNotEqual(country_data, 1)
        mock.assert_called_with(ripe.RIPE_COUNTRY_INFO.format("CA"))

    @patch("requests.get")
    def test_fetch_asn_data(self, mock):
        mock.return_value.json.return_value = ROUTING_RESPONSE
        routing_data = ripe.fetch_asn_data(1)
        self.assertEqual(routing_data, 30)
        self.assertNotEqual(routing_data, 0)
        mock.assert_called_with(ripe.RIPE_ROUTING_CURRENT.format(1))
        routing_data_hist = ripe.fetch_asn_data(1, self.since)
        self.assertEqual(routing_data_hist, 30)
        mock.assert_called_with(ripe.RIPE_ROUTING_HIST.format(1, self.since))

    @patch("requests.get")
    def test_fetch_routing_data(self, mock):
        with patch("cescout.projects.ripe.fetch_country_data", return_value=[1]):
            mock.return_value.json.return_value = ROUTING_RESPONSE
            self.assertEqual(ripe.fetch_routing_data("CA", [1, 2], self.since, self.until),
                             self.asn_data_output)
            self.assertNotEqual(ripe.fetch_routing_data("CA", [2], self.since, self.until),
                                self.asn_data_output)

    @patch("requests.get")
    def test_run(self, mock):
        with patch("cescout.projects.ripe.fetch_country_data", return_value=[1]):
            mock.return_value.json.return_value = ROUTING_RESPONSE
            self.assertEqual(ripe.run("CA", [1, 2], self.since, self.until),
                             self.asn_data_output)
            self.assertEqual(ripe.run("CA", [2], self.since, self.until),
                             {})
            self.assertEqual(ripe.run("CA", None, self.since, self.until),
                             None)
