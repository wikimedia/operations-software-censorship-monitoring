"""Query the IODA API and get internet outage/shutdown events for a country.

This script queries IODA's API for a specific time period and processes the
result to extract internet outage data. It does this by detecting transitions
between "normal" to "warning" or "critical" levels and marks a country to be
affected by an outage event if it detects such a transition. This method is not
documented on the website or the API but was suggested by the IODA developers
and meets their definition of what constitutes an "outage" event.

For more information about CAIDA's IODA project and their methodology, please
visit the website: https://ioda.caida.org/ioda.
"""

import collections
import itertools
import logging
from datetime import timezone

import requests

IODA_API_URL = ("https://ioda.caida.org/ioda/data/alerts?"
                "human=true&from={0}&until={1}&annotateMeta=true")
IODA_VIEW_URL = ("https://ioda.caida.org/ioda/dashboard#"
                 "view=inspect&entity=country/{0}&"
                 "lastView=overview&from={1}&until={2}")


def pair(iterable):
    """Create pairs of items from an iterator.

    If the iterable is (1, 2, 3), this function returns [(1, 2), (2, 3)]. We
    use this to to pair the levels returned by the API so that we can detect
    transitions between them.

    :param iterable: an iterable object to create pairs from
    :return list: a list of pair of tuples from the iterable
    """
    if len(iterable) < 2:
        return None
    first, second = itertools.tee(iterable)
    next(second, None)
    return list(zip(first, second))


def parse_response(response, country):
    """Parse IODA's API response to extract outage information.

    :param response: JSON response returned by IODA's API
    :param country: two-letter country code to check for outage events
    :return outage: dict with a single key `is_outage' that specifies if an
                    outage event was detected for :param country:
    """
    all_events = collections.defaultdict(list)
    for each in response["data"]["alerts"]:
        # IODA tracks both country- and AS-level outages but for our purpose,
        # we only care about country-wide outages and therefore filter the
        # `metaType` and get the results for countries (`region').
        if each["metaType"] == "region":
            country_code = each["meta"]["attrs"]["country_code"]
            if country_code == country:
                fqid = each["meta"]["attrs"]["fqid"]
                logging.debug("Logging fqid {0}".format(fqid))
                all_events[country_code].append({"time": each["time"],
                                                 "level": each["level"],
                                                 "fqid": fqid})
    logging.debug("Fetched measurements from IODA")

    outage = {}
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
        # transition is indicative of an outage.
        if levels_pairs is not None:
            if ("normal", "warning") in levels_pairs \
                    or ("normal", "critical") in levels_pairs:
                outage["is_outage"] = True
            else:
                outage["is_outage"] = False

    logging.debug(outage)
    return outage


def fetch_data(request_url):
    """Query IODA's API and return the JSON response.

    :param request_url: IODA_API_URL formatted with the date range
    :return response: JSON object from the API request
    """
    logging.debug("Requested URL is {0}".format(request_url))
    try:
        req = requests.get(request_url)
        req.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logging.error(e)
        return {}
    response = req.json()
    return response


def time_epoch(start_date, end_date):
    """Return the epoch in seconds (UTC) for a date range tuple.

    :param start_date: start date to convert to epoch
    :param end_date: end date to convert to epoch
    :return tuple: tuple of epoch(start_date, end_date)
    """
    start_epoch = int(start_date.replace(tzinfo=timezone.utc).timestamp())
    end_epoch = int(end_date.replace(tzinfo=timezone.utc).timestamp())
    logging.debug("Time interval is {0} to {1}".format(start_epoch, end_epoch))
    return start_epoch, end_epoch


def run(country, asns, *date_range, **config):
    """Entry point for the IODA module.

    :param country: two-letter country code to run query against
    :param asns: list of ASNs to query for (checked against :param country:)
                 not used for IODA measurements
    :param date_range: tuple of date (since, until)
    :param config: (optional) other configuration parameters
                   not used for IODA measurements
    :return outage_data: dict with two keys: outage state and a link to IODA's
                         web interface for the measurement period
    """
    since, until = time_epoch(*date_range)
    response = fetch_data(IODA_API_URL.format(since, until))

    outage_data = parse_response(response, country)
    outage_data["url"] = IODA_VIEW_URL.format(country, since, until)
    return outage_data
