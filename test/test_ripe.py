#!/usr/bin/env python3

import unittest
import logging
from unittest.mock import patch

from ripe import ripefetch

REQUEST_RESPONSE = {
    "status": "ok",
    "query_id": "",
    "data": {
        "query_time": "2019-09-09T00:00:00",
    }
}

COUNTRY_RESPONSE = {
    "status": "ok",
    "data": {
        "query_time": "2019-09-09T00:00:00",
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
        "query_time": "2019-12-09T16:00:00",
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
        self.time = "2019-09-09T00:00:00"
        logging.disable(logging.CRITICAL)

    @patch("requests.get")
    def test_fetch_data(self, mock):
        mock.return_value.json.return_value = REQUEST_RESPONSE
        response = ripefetch.fetch_data("https://some.url")
        self.assertEqual(response, {"query_time": self.time})

    @patch("requests.get")
    def test_fetch_country_data(self, mock):
        mock.return_value.json.return_value = COUNTRY_RESPONSE
        country_data = ripefetch.fetch_country_data("CA")
        self.assertEqual(country_data, [1, 2, 3])

    @patch("requests.get")
    def test_fetch_routing_data(self, mock):
        mock.return_value.json.return_value = ROUTING_RESPONSE
        routing_data = ripefetch.fetch_routing_data(1)
        self.assertEqual(routing_data, 30)

    @patch("requests.get")
    def test_fetch_asn_data(self, mock):
        with patch("ripe.ripefetch.fetch_country_data", return_value=[1]):
            mock.return_value.json.return_value = ROUTING_RESPONSE
            asn_data = ripefetch.fetch_asn_data("CA", [1, 2], self.time)
            output = {"CA": {1: {"current": 30, "past": 30}}}
            self.assertEqual(asn_data, output)

    def test_arg_parser(self):
        incorrect_args = ["-c CA", "-c CA -a", "-c CA -a 1 -t"]
        for each in incorrect_args:
            with self.assertRaises(SystemExit):
                ripefetch.arg_parser(each.split())
        correct_args = ["-c CA -a 1", "-c CA -a 1 -t {0}".format(self.time),
                        "-c CA -a 2 -v"]
        for each in correct_args:
            ripefetch.arg_parser(each.split())

    def test_main(self):
        command = "-c CA -a 1 -t {0}".format(self.time)
        with self.assertRaises(SystemExit) as exit_code:
            self.assertEqual(ripefetch.main(command.split()), exit_code)
        command_fake_time = "-c CA -a 1 -t 2019"
        with self.assertRaises(ValueError):
            ripefetch.main(command_fake_time.split())


if __name__ == "__main__":
    unittest.main()
