#!/usr/bin/env python3

"""Query the IODA API and get internet outage events for a country.

This script queries IODA's API for a specific time period and processes the
result to extract internet outage data. It does this by detecting transitions
between "normal" to "warning" or "critical" levels and categorizes a country
to be affected by an outage event if it detects such a transition. This method
is not documented on the website or the API but was suggested by the IODA
developers and meets their definition of what constitutes an "outage" event.

For more information about CAIDA's IODA project and their methodology, please
visit the website: https://ioda.caida.org/ioda.
"""

import os
import json
import logging
import argparse
import itertools
import collections
import urllib.request

from . import datehelper

HOME_DIR = os.path.expanduser("~")

IODA_URL = "https://ioda.caida.org/ioda/data/alerts?" \
                "human=true&from={0}&until={1}&annotateMeta=true"


def pair(iterable):
    """Create pairs of items from an iterator.

    If the iterable is (1, 2, 3), this function returns [(1, 2), (2, 3)].

    :param iterable: an iterable object to create pairs from
    :return list: a list of pair of tuples from the iterable
    """
    if len(iterable) < 2:
        return None
    first, second = itertools.tee(iterable)
    next(second, None)
    return list(zip(first, second))


def parse_response(response, countries):
    """Parse IODA's API response to extract outage information.

    :param response: JSON response returned by IODA's API
    :param countries: list of countries to check for outage events
    :return outage_events: defaultdict of list of countries with an outage
    event mapped to the `fqid'
    """
    all_events = collections.defaultdict(list)
    for each in response["data"]["alerts"]:
        # IODA tracks both country- and AS-level outages but for our purpose,
        # we only care about country-wide outages and therefore filter the
        # `metaType` and only get the results for countries (`region').
        if each["metaType"] == "region":
            country_code = each["meta"]["attrs"]["country_code"]
            # Log the time, level, and fqid (unique measurement code) for the
            # list of countries we want to get outage data for.
            if country_code in countries:
                fqid = each["meta"]["attrs"]["fqid"]
                all_events[country_code].append({"time": each["time"],
                                                 "level": each["level"],
                                                 "fqid": fqid})

    outage_events = collections.defaultdict(list)
    for country, data in all_events.items():
        # Get the levels and sort them by when they happened.
        levels = [each["level"] for each in
                  sorted(data, key=lambda value: value["time"])]
        levels_pairs = pair(levels)
        # IODA categorizes an event as an "outage" if there is at least one
        # transition from (normal, warning) or (normal, critical) during the
        # specified time interval.
        #
        # Note that there can be multiple such transitions but even one
        # transition is indicative of an outage, so we check for one but log
        # all of them with their `fqid'.
        if levels_pairs is not None:
            if ("normal", "warning") in levels_pairs \
                    or ("normal", "critical") in levels_pairs:
                outage_events[country].extend([each["fqid"] for each in data])

    logging.debug(outage_events)
    return outage_events


def fetch_data(request_url):
    """Query IODA's API and return the JSON response.

    :param request_url: IODA_URL formatted with the date range
    :return response: JSON object from the API request
    """
    req = urllib.request.Request(request_url)
    logging.info("Requested URL is {0}".format(request_url))
    response = json.loads(urllib.request.urlopen(req).read())
    return response


def main():
    enable_logging()
    args = arg_parser()

    if args.verbose:
        logging.getLogger().setLevel("DEBUG")
    logging.info("Scanning countries {0}".format(" ".join(args.countries)))

    start_epoch, end_epoch = datehelper.time_epoch(args.since, args.until)
    response = fetch_data(IODA_URL.format(start_epoch, end_epoch))
    outage_events = parse_response(response, args.countries)
    print(outage_events)


def enable_logging():
    """Enable logging and set the log format, log file name and log level."""
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    log_dir = os.path.join(HOME_DIR, ".{}".format(script_name))
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir, 0o770)

    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s",
                        filename=os.path.join(log_dir, script_name+".log"),
                        filemode='a',
                        level=logging.INFO)
    logging.info("Starting script at {0}".format(datehelper.time_now()))


def arg_parser():
    """Initialize argument parser.

    :return parser: populated namespace of arguments
    """
    parser = argparse.ArgumentParser(description="Fetch IODA outage data")
    parser.add_argument("-c", "--countries",
                        nargs='+',
                        required=True,
                        help="two-letter country codes to fetch outage data")
    parser.add_argument("--since",
                        metavar=datehelper.DATE_FORMAT,
                        type=datehelper.validate_date,
                        required=True,
                        help="date and time (UTC) to show outage data since")
    parser.add_argument("--until",
                        metavar=datehelper.DATE_FORMAT,
                        type=datehelper.validate_date,
                        required=True,
                        help="date and time (UTC) to show outage data until")
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="enable verbose output (logging.DEBUG)")
    return parser.parse_args()


if __name__ == "__main__":
    main()
