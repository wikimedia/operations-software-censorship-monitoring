import unittest
from unittest.mock import patch

from requests.exceptions import HTTPError

from cescout import common
from cescout.projects import ioda


SAMPLE_REQUEST = {
    "type": "watchtower.alerts",
    "queryParameters": {
        "level": [],
        "from": "1580551200",
        "until": "1580637600",
    },
    "data": {
        "alerts": [
            {
                "fqid": "bgp.v4.visibility_threshold.min_50%",
                "time": 1570070400,
                "level": "normal",
                "method": "last_value",
                "metaType": "region",
                "metaCode": "1870",
                "meta": {
                    "name": "Babil",
                    "attrs": {
                        "fqid": "geo.netacuity.AS.IQ.1870",
                        "country_name": "Iraq",
                        "country_code": "IQ"
                    }
                }
            },
            {
                "fqid": "bgp.v4.visibility_threshold.min_50%",
                "time": 1570070400,
                "level": "critical",
                "method": "last_value",
                "condition": "\u003C historical * 0.5",
                "value": 7,
                "historyValue": 59,
                "metaType": "region",
                "metaCode": "1859",
                "meta": {
                    "name": "Karbala\u0027",
                    "attrs": {
                        "fqid": "geo.netacuity.AS.IQ.1859",
                        "country_name": "Iraq",
                        "country_code": "IQ"
                    }
                }
            },
            {
                "fqid": "bgp.v4.visibility_threshold.min_50%",
                "time": 1570070400,
                "level": "critical",
                "method": "last_value",
                "condition": "\u003C historical * 0.5",
                "value": 0,
                "historyValue": 1,
                "metaType": "region",
                "metaCode": "2389",
                "meta": {
                    "name": "Rugaju",
                    "attrs": {
                        "fqid": "geo.netacuity.EU.LV.2389",
                        "country_name": "Latvia",
                        "country_code": "LV"
                    }
                }
            },
            {
                "fqid": "bgp.v4.visibility_threshold.min_50%",
                "time": 1570070400,
                "level": "normal",
                "method": "last_value",
                "condition": "\u003C historical * 0.5",
                "value": 0,
                "historyValue": 1,
                "metaType": "region",
                "metaCode": "2389",
                "meta": {
                    "name": "Rugaju",
                    "attrs": {
                        "fqid": "geo.netacuity.EU.LV.2389",
                        "country_name": "Latvia",
                        "country_code": "LV"
                    }
                }
            }
        ]
    }
}


class TestIODA(unittest.TestCase):
    def setUp(self):
        self.since = common.validate_date("2020-02-01T10:00:00")
        self.until = common.validate_date("2020-02-02T10:00:00")
        self.start_time = 1580551200
        self.end_time = 1580637600

    def test_pair(self):
        self.assertEqual(ioda.pair(('level', 'warning', 'critical')),
                         [('level', 'warning'), ('warning', 'critical')])
        self.assertEqual(ioda.pair(('level', 'critical')),
                         [('level', 'critical')])
        self.assertEqual(ioda.pair(('warning', )),
                         None)

    def test_parse_response(self):
        self.assertEqual(ioda.parse_response(SAMPLE_REQUEST, "IQ"),
                         {"is_outage": True})
        self.assertEqual(ioda.parse_response(SAMPLE_REQUEST, "LV"),
                         {"is_outage": False})
        self.assertEqual(ioda.parse_response(SAMPLE_REQUEST, "US"),
                         {})

    def test_fetch_data(self):
        with patch("requests.get") as mock:
            mock.return_value.json.return_value = SAMPLE_REQUEST
            response = ioda.fetch_data("https://some.url")
            self.assertEqual(response, SAMPLE_REQUEST)
        with patch("requests.get") as mock:
            mock.return_value.raise_for_status.side_effect = HTTPError()
            self.assertEqual(ioda.fetch_data("https://some.url"),
                             {})

    def test_time_epoch(self):
        self.assertEqual(ioda.time_epoch(self.since, self.until),
                         (self.start_time, self.end_time))

    @patch("requests.get")
    def test_run(self, mock):
        mock.return_value.json.return_value = SAMPLE_REQUEST
        url = ioda.IODA_VIEW_URL.format("IQ", *ioda.time_epoch(self.since,
                                                               self.until))
        return_obj = {"is_outage": True, "url": url}
        self.assertEqual(ioda.run("IQ", None, self.since, self.until),
                         return_obj)
        mock.assert_called_with(ioda.IODA_API_URL.format(self.start_time, self.end_time))
