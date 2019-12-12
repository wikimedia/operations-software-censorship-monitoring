#!/usr/bin/env python3

"""Query RIPEstat API to fetch BGP routing information for a given ASN.

This script queries RIPEstat's API (https://stat.ripe.net/docs/data_api/) to
fetch BGP routing information for a given ASN, specifically the current and
historic number of announced IPv4 prefixes. This information may be used to
determine if there was an instance of internet shutdown or outage in the
country, indicated by a significant change in the number of prefixes.

Note that CAIDA's IODA project already takes into account BGP routing data for
detecting internet outages but their API does not present this information.
"""

import sys
import logging
import argparse

import requests

from . import datehelper

RIPE_COUNTRY_INFO = ("https://stat.ripe.net/data/"
                     "country-resource-list/data.json?resource={}")
RIPE_ROUTING_CURRENT = ("https://stat.ripe.net/data/"
                        "routing-status/data.json?resource={}")
RIPE_ROUTING_HIST = ("https://stat.ripe.net/data/"
                     "routing-status/data.json?resource={0}&timestamp={1}")


def fetch_data(request_url):
    """Query RIPEstat's API and return the JSON response.

    :param request_url: URL to make the request against
    :return response: JSON array of "data" from the API response
    """
    logging.info("Requested URL is {0}".format(request_url))
    req = requests.get(request_url)
    req.raise_for_status()
    response = req.json()["data"]
    return response


def fetch_country_data(country):
    """Query RIPEstat's API and fetch a list of ASNs in a country.

    :param country: two-letter country code to query the API for
    :return country_asns: list of ASNs in the country (int)
    """
    url = RIPE_COUNTRY_INFO.format(country)
    country_asns = [int(asn) for asn in fetch_data(url)["resources"]["asn"]]
    return country_asns


def fetch_routing_data(asn, time=None):
    """Query RIPEstat's API and fetch BGP routing state for a given ASN.

    :param asn: ASN to query the API for (current time)
    :param time=None: time in ISO8601 format to run the query at (past time)
    :return prefix: the number of IPv4 prefixes announced by the ASN
    """
    if time is not None:
        url = RIPE_ROUTING_HIST.format(asn, time)
    else:
        url = RIPE_ROUTING_CURRENT.format(asn)
    routing_data = fetch_data(url)
    query_time = routing_data["query_time"]
    logging.info("Per RIPE: query was run for {0}".format(query_time))
    prefix = routing_data["announced_space"]["v4"]["prefixes"]
    return prefix


def fetch_asn_data(country, asns, time):
    """Fetch current and historic BGP routing data for ASNs in a country.

    :param country: two-letter country code
    :param asns: list of ASNs to query for (checked against :param country:)
    :param time: time in ISO8601 format to run the query at (past time)
    :return asn_data: mapping of country to ASNs and their routing history
    """
    country_asns = fetch_country_data(country)
    asn_data = {}
    asn_data[country] = {}
    for asn in asns:
        if asn in country_asns:
            current_routing = fetch_routing_data(asn)
            past_routing = fetch_routing_data(asn, time)
            asn_data[country][asn] = {"current": current_routing,
                                      "past": past_routing}
            logging.debug("ASN {0} Prefixes: {1} current,"
                          " {2} past".format(asn, current_routing,
                                             past_routing))
        else:
            logging.error("ASN {0} not in {1}".format(asn, country))
    return asn_data


def main(argv=None):
    enable_logging()
    args = arg_parser(argv)

    if args.verbose:
        logging.getLogger().setLevel("DEBUG")

    datehelper.validate_date(args.time)

    logging.info("Starting script at {0}".format(datehelper.time_now()))
    logging.info("Scanning country {0} and {1} ASNs".format(args.country,
                                                            args.asns))
    asn_data = fetch_asn_data(args.country, args.asns, args.time)
    if asn_data:
        print(asn_data)

    sys.exit(0)


def enable_logging():
    """Enable logging and set the log format, log file name and log level."""
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s",
                        level=logging.INFO)


def arg_parser(args):
    """Initialize argument parser.

    :return parser: populated namespace of arguments
    """
    description = ("Fetch routing history for a country and"
                   " specified ASNs from RIPEStat's API")
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-c", "--country",
                        required=True,
                        help="two-letter country code to query for")
    parser.add_argument("-a", "--asns",
                        nargs="+",
                        type=int,
                        required=True,
                        help="list of ASNs in country to run query against")
    parser.add_argument("-t", "--time",
                        metavar=datehelper.DATE_FORMAT,
                        default=datehelper.date_yesterday(),
                        help="time to run the query for historic data")
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="enable verbose output (logging.DEBUG)")
    return parser.parse_args(args)


if __name__ == "__main__":
    main()
