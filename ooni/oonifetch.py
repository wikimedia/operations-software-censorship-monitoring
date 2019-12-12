#!/usr/bin/env python3

"""Query OONI's metadb and generate a report.

This script queries (a local copy of) OONI's metadb for specified domains
within a given time period to check for anomalous measurements and generates
an HTML report. It assumes you have a local copy of OONI's metadb that is
running and actively synced so that it can make read-only queries to the
database.

Queries are made using DB_QUERY over domains specified by DOMAINS.
"""

import os
import sys
import logging
import argparse
import collections
import urllib.parse

import jinja2
import psycopg2
import psycopg2.extras

from . import datehelper
from . import countrycodes

DB_NAME = "metadb"
DB_USER = "postgres"

DB_QUERY = """
   SELECT measurement.measurement_start_time AS measurement_start_time,
          report.report_id,
          report.probe_asn,
          report.probe_cc,
          report.probe_ip,
          report.test_name,
          input.input,
          http_verdict.blocking,
          http_verdict.http_experiment_failure,
     FROM measurement
     JOIN input ON input.input_no = measurement.input_no
     JOIN report ON report.report_no = measurement.report_no
     JOIN http_verdict ON http_verdict.msm_no = measurement.msm_no
    WHERE test_name = 'web_connectivity'
      AND input.input LIKE ANY(ARRAY[%s, %s, %s, %s, %s, %s, %s, %s, %s, %s])
      AND test_start_time >= %s and test_start_time < %s;
"""

DOMAINS = ("%wikipedia.org%",
           "%wikimedia.org%",
           "%wikidata.org%",
           "%wikisource.org%",
           "%wikibooks.org%",
           "%wiktionary.org%",
           "%wikiquote.org%",
           "%wikiversity.org%",
           "%wikivoyage.org%",
           "%wikinews.org%")

EXPLORER_LINK = "https://explorer.ooni.io/measurement/{0}?input={1}"

TEMPLATE_NAME = "template.html"


def run_query(date_range):
    """Run a Postgres query within a date range.

    Query parameters are specified by DB_QUERY and DOMAINS.

    :param date_range: tuple that specifies the date range (since, until)
    :return result: database query result
    """
    try:
        conn = psycopg2.connect("dbname={0} user={1}".format(DB_NAME, DB_USER))
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    except psycopg2.OperationalError as e:
        logging.error("Unable to connect to the {0} database.".format(DB_NAME))
        logging.error("Do you have a local copy of metadb running? See below.")
        logging.error(e)
        sys.exit(1)

    start_time = datehelper.time_now()
    query = DOMAINS + date_range
    cur.execute(DB_QUERY, query)
    logging.info("Query: {0}".format(query))
    end_time = datehelper.time_now() - start_time
    logging.debug("Executed in {0} seconds".format(end_time))

    result = cur.fetchall()
    cur.close()
    conn.close()

    return result


def process_results(result):
    """Process the results of a database query and return measurement data.

    :param result: database query returned by `run_query'
    :return all_c: default dict of countries mapped to their measurements
    :return anom_c: dict of countries with anomalous measurements mapped to
                    the number of measurements
    :return one_anom_c: list of countries with at least one anomalous
                        (blocking) measurement
    """
    all_c = collections.defaultdict(list)
    for (index, each) in enumerate(result):
        data = {
            "measurement_time": each["measurement_start_time"],
            "report_id": each["report_id"],
            "asn": each["probe_asn"],
            "country": each["probe_cc"],
            "url": each["input"],
            "blocking": each["blocking"],
            "http_failure": each["http_experiment_failure"]
        }
        # Encode the link to create an OONI Explorer URL.
        encode_link = EXPLORER_LINK.format(data["report_id"],
                                           urllib.parse.quote(data["url"]))
        data["report_link"] = encode_link

        # Ignore measurements that have 0 as the ASN as these are not useful
        # for us: these measurements are also missing the country so there
        # isn't much we can do.
        if data["asn"] == 0:
            continue
        # Ignore false-positive measurements resulting from a bug in an
        # earlier version of OONI Probe.
        # See https://github.com/ooni/probe-legacy/issues/38
        if data["http_failure"] is not None:
            if "unknown_failure" in data["http_failure"]:
                continue

        data["count"] = index
        all_c[data["country"]].append(data)

    anom_c = {}
    for country, data in all_c.items():
        len_measurements_blocked = len([each["blocking"] for each in data
                                        if not each["blocking"] == "false"])
        anom_c[country] = len_measurements_blocked
        logging.debug("{0} anomalies in {1}".format(len_measurements_blocked,
                                                    country))

    one_anom_c = [country for (country, data) in anom_c.items() if data > 0]

    return all_c, anom_c, one_anom_c


def initialize_template(report):
    """Generate a report from a Jinja template.

    :param report: dict for template specified in TEMPLATE_NAME
    :return template: HTML report formatted with template
    """
    template_path = os.path.join(os.path.dirname(__file__), "templates")
    logging.debug("Loading template {0} from {1}".format(TEMPLATE_NAME,
                                                         template_path))
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))
    template = env.get_template(TEMPLATE_NAME)

    return template.render(report=report)


def main():
    enable_logging()
    args = arg_parser()

    if args.verbose:
        logging.getLogger().setLevel("DEBUG")
    if args.since and args.until is None:
        logging.error("--since argument requires --until")
        sys.exit(1)

    logging.info("Starting script at {0}".format(datehelper.time_now()))
    date_yesterday, date_today = (datehelper.date_yesterday(),
                                  datehelper.date_today())
    if args.since and args.until:
        date_range = (datehelper.format_date(args.since),
                      datehelper.format_date(args.until))
    else:
        date_range = (date_yesterday, date_today)
    logging.info("Date range is {}".format(' to '.join(date_range)))

    # Run the actual database query.
    result = run_query(date_range)
    # Get the filtered results of countries to their measurements. For a
    # proper definition of the *_countries, see `process_results'.
    all_countries, anom_countries, one_anom_countries = process_results(result)
    len_one_anom_countries = len(one_anom_countries)

    # Mapping of two-letter country codes to names.
    country_codes = countrycodes.get_codes()

    report_dict = {
        "title": "OONI Report for {}".format(" to ".join(date_range)),
        "len_results": len(result),
        "len_one_anom": len_one_anom_countries,
        "anom_countries": anom_countries,
        "all_countries": all_countries,
        "domains": ", ".join(e.strip("%") for e in DOMAINS),
        "country_codes": country_codes
    }
    logging.info("{0} measurements from {1} countries. Anomalies in {2}: {3}".
                 format(len(result), len(all_countries),
                        len_one_anom_countries, one_anom_countries))

    print(initialize_template(report_dict))


def arg_parser():
    """Initialize argument parser.

    :return parser: populated namespace of arguments
    """
    parser = argparse.ArgumentParser(description="Fetch and parse Wikimedia "
                                                 "domains from OONI's metadb")
    parser.add_argument("--since",
                        metavar="%Y-%m-%d",
                        type=datehelper.validate_date,
                        help="date to show output since (from)")
    parser.add_argument("--until",
                        metavar="%Y-%m-%d",
                        type=datehelper.validate_date,
                        help="date to show output until (to)")
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="enable verbose output (logging.DEBUG)")
    return parser.parse_args()


def enable_logging():
    """Enable logging and set the log format, log file name and log level."""
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s",
                        stream=sys.stdout,
                        level=logging.INFO)


if __name__ == "__main__":
    main()
