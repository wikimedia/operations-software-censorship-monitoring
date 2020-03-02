"""Query RIPEstat API to fetch BGP routing information for a given ASN.

This script queries RIPEstat's API (https://stat.ripe.net/docs/data_api/) to
fetch BGP routing information for a given ASN, specifically the current and
historic number of announced IPv4 prefixes. This information may be used to
determine if there was an instance of internet shutdown or outage in the
country, indicated by a significant change in the number of these prefixes.

Note that CAIDA's IODA project already takes into account BGP routing data for
detecting internet outages (and their data is more exhaustive) but their API
does not present this information.
"""

import logging

import requests

RIPE_COUNTRY_INFO = ("https://stat.ripe.net/data/"
                     "country-resource-list/data.json?resource={}")
RIPE_ROUTING_CURRENT = ("https://stat.ripe.net/data/"
                        "routing-status/data.json?resource={}")
RIPE_ROUTING_HIST = ("https://stat.ripe.net/data/"
                     "routing-status/data.json?resource={0}&timestamp={1}")


def fetch_data(request_url):
    """Query RIPEstat's API and return the JSON response.

    :param request_url: URL to make the request against
    :return response: JSON array of `data' from the API response
    """
    logging.debug("Requested URL is {0}".format(request_url))
    try:
        req = requests.get(request_url)
        req.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logging.error(e)
        return {}
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


def fetch_asn_data(asn, time=None):
    """Query RIPEstat's API and fetch BGP routing state for a given ASN.

    :param asn: ASN to query the API for (current time)
    :param time=None: time in ISO format to run the query at (past time)
    :return prefix: the number of IPv4 prefixes announced by the ASN
    """
    if time is not None:
        url = RIPE_ROUTING_HIST.format(asn, time)
    else:
        url = RIPE_ROUTING_CURRENT.format(asn)
    routing_data = fetch_data(url)
    query_time = routing_data["query_time"]
    logging.debug("Per RIPE, query was run for {0}".format(query_time))
    prefix = routing_data["announced_space"]["v4"]["prefixes"]
    return prefix


def fetch_routing_data(country, asns, since, until):
    """Fetch current and historic BGP routing data for ASNs in a country.

    :param country: two-letter country code
    :param asns: list of ASNs to query for (checked against :param country:)
    :param since: time in ISO format to run the query at (from)
    :param until: time in ISO format to run the query at (to)
    :return asn_data: mapping of ASNs to their routing history
    """
    country_asns = fetch_country_data(country)
    asn_data = {}
    for asn in asns:
        if asn in country_asns:
            current_routing = fetch_asn_data(asn)
            past_routing_since = fetch_asn_data(asn, since)
            past_routing_until = fetch_asn_data(asn, until)
            asn_data[asn] = {"current": current_routing,
                             "since": past_routing_since,
                             "until": past_routing_until}
            logging.debug("ASN {0} prefixes: {1} current,"
                          " {2} since,"
                          " {3} until".format(asn, current_routing,
                                              past_routing_since,
                                              past_routing_until))
        else:
            logging.warning("ASN {0} not in {1}".format(asn, country))
    return asn_data


def run(country, asns, *date_range, **config):
    """Entry point for the RIPE module.

    :param country: two-letter country code to run query against
    :param asns: list of ASNs to query for (checked against :param country:)
    :param date_range: tuple of date (since, until)
    :param config: (optional) other configuration parameters
                   not used for RIPE measurements
    :return asn_data: dict of ASNs mapped to their routing history
    """
    # If the ASNs were not specified, return early.
    if asns is None:
        logging.warning("No ASNs specified; skipping RIPE")
        return

    asn_data = fetch_routing_data(country, asns, *date_range)
    return asn_data
