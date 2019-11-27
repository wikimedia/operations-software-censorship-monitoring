#!/usr/bin/env python3

import logging
import unittest
import datetime

from ioda import datehelper


class TestDateHelper(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def test_time_epoch(self):
        start_time = 1568020149
        end_time = 1570612149
        start_date = datehelper.validate_date("2019-09-09T09:09:09")
        end_date = datehelper.validate_date("2019-10-09T09:09:09")
        self.assertEqual(datehelper.time_epoch(start_date, end_date),
                         (start_time, end_time))

    def test_validate_date(self):
        with self.assertRaises(ValueError):
            datehelper.validate_date("2019-20-09 09:09:09")
        self.assertEqual(datetime.datetime(2019, 9, 9, 9, 9, 9),
                         datehelper.validate_date("2019-09-09T09:09:09"))


if __name__ == "__main__":
    unittest.main()
