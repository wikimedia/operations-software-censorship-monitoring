#!/usr/bin/env python3

import json
import unittest

from ioda import iodafetch


REQUEST = """
{
    "type": "watchtower.alerts",
    "error": null,
    "queryParameters": {
        "human": true,
        "level": [],
        "from": "1570024940",
        "until": "1570072282",
        "expression": [],
        "queryExpression": [],
        "fqid": [],
        "name": [],
        "meta": null,
        "limit": null,
        "annotateMeta": true
    },
    "data": {
        "alerts": [
            {
                "fqid": "bgp.v4.visibility_threshold.min_50%_ff_peer_asns.visible_slash24_cnt",
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
                "fqid": "bgp.v4.visibility_threshold.min_50%_ff_peer_asns.visible_slash24_cnt",
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
                "fqid": "bgp.v4.visibility_threshold.min_50%_ff_peer_asns.visible_slash24_cnt",
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
            }
        ]
    }
}"""


class TestCAIDA(unittest.TestCase):
    def test_pair(self):
        self.assertEqual(iodafetch.pair(('level', 'warning', 'critical')),
                         [('level', 'warning'), ('warning', 'critical')])
        self.assertEqual(iodafetch.pair(('level', 'critical')),
                         [('level', 'critical')])
        self.assertEqual(iodafetch.pair(('warning', )),
                         None)

    def test_parse_response(self):
        self.assertEqual(iodafetch.parse_response(json.loads(REQUEST), ["IQ", "CA"]),
                         {'IQ': ['geo.netacuity.AS.IQ.1870', 'geo.netacuity.AS.IQ.1859']})
        self.assertEqual(iodafetch.parse_response(json.loads(REQUEST), ["US"]),
                         {})


if __name__ == "__main__":
    unittest.main()
