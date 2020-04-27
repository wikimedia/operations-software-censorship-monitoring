"""Query OONI's `metadb' and return measurement results.

This script queries (a local copy of) OONI's `metadb' for specified domains
(see `cescout.cfg`) to check for anomalous measurements. It assumes you have a
local copy of OONI's `metadb' that is running and actively synced as that is
used to make read-only queries to the database.
"""

import collections
import logging
import urllib.parse

import psycopg2
import psycopg2.extras

DB_QUERY = """
   SELECT measurement.measurement_start_time AS measurement_start_time,
          report.report_id,
          report.probe_asn,
          report.probe_cc,
          report.probe_ip,
          report.test_name,
          input.input,
          http_verdict.blocking,
          http_verdict.http_experiment_failure
     FROM measurement
     JOIN input ON input.input_no = measurement.input_no
     JOIN report ON report.report_no = measurement.report_no
     JOIN http_verdict ON http_verdict.msm_no = measurement.msm_no
    WHERE test_name = 'web_connectivity'
      AND input.input LIKE ANY(%s)
      AND probe_cc = %s
      AND test_start_time >= %s
      AND test_start_time <= %s;
"""

EXPLORER_LINK = "https://explorer.ooni.io/measurement/{0}?input={1}"


def run_query(country, *date_range, **query):
    """Run a Postgres query based on input parameters.

    Query parameters are specified by the `cescout.cfg' file and include the
    name of the database and the user, and the list of domains that will be
    used to query OONI's `metadb'.

    Note that if a local copy of `metadb' is not found or if the script was
    unable to connect to the database, we just return an empty result. There is
    no fallback mechanism, such as running a query against the API, at least
    not yet.

    :param country: two-letter country code to run query against
    :param date_range: tuple of date: since, until (ISO format)
    :param query: dict with db information: name, user, domains
    :return result: database query result
    """
    try:
        db_config = query["ooni"]["database"]
        domains = ["%{0}%".format(each) for each in query["ooni"]["domains"]]
    except KeyError:
        logging.error("Unable to read config settings for OONI's test."
                      " See `cescout.cfg` for an example.")
        return

    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    except psycopg2.OperationalError as e:
        logging.error("Unable to connect to the database: {0}.".format(e))
        return

    cur.execute(DB_QUERY, (domains, country, *date_range))
    logging.debug("Query: {0}".format(cur.query))

    result = cur.fetchall()
    cur.close()
    conn.close()

    return result


def process_results(result):
    """Process the results of a database query and return measurement data.

    :param result: database query returned by `run_query'
    :return all_measurements: dict of country mapped to its measurements
    """
    query = []
    for measurement in result:
        data = {
            "measurement_time": str(measurement["measurement_start_time"]),
            "report_id": measurement["report_id"],
            "asn": measurement["probe_asn"],
            "country": measurement["probe_cc"],
            "ip": measurement["probe_ip"],
            "url": measurement["input"],
            "blocking": measurement["blocking"],
            "http_failure": measurement["http_experiment_failure"]
        }
        # Encode the link to create an OONI Explorer URL for easy access. This
        # is also the URL we present in the final report.
        encode_link = EXPLORER_LINK.format(data["report_id"],
                                           urllib.parse.quote(data["url"]))
        data["report_link"] = encode_link

        # Ignore measurements that have 0 as the ASN as these are not useful
        # for us: these measurements are also missing the country so there
        # isn't much we can do.
        if data["asn"] == 0:
            logging.debug("Skipped test {0}: "
                          "invalid ASN".format(data["report_id"]))
            continue

        # Ignore false-positive measurements resulting from a bug in an
        # earlier version of OONI Probe.
        # See https://github.com/ooni/probe-legacy/issues/38
        if data["http_failure"] is not None:
            if "unknown_failure" in data["http_failure"]:
                logging.debug("Skipped test {0}: "
                              "HTTP error".format(data["report_id"]))
                continue

        query.append(data)

    len_all_measurements = len(query)
    # Length of all anomalous measurements. We consider a measurement as
    # anomalous when the blocking is *not* "false", indicated by a blocking
    # type like "dns" or "tcp_ip".
    len_anomalous_measurements = len([each["blocking"] for each in query
                                      if not each["blocking"] == "false"])

    all_measurements = collections.defaultdict(list)
    all_measurements["len_all"] = len_all_measurements
    all_measurements["len_blocking"] = len_anomalous_measurements
    for each in query:
        all_measurements["measurements"].append({"url": each['report_link'],
                                                "blocking": each['blocking']})

    return all_measurements


def run(country, asns, *date_range, **config):
    """Entry point for the OONI module.

    :param country: two-letter country code to run query against
    :param asns: list of ASNs to query for (checked against :param country:)
                 not used for OONI measurements
    :param date_range: tuple of date (since, until)
    :param config: config settings: db information, domains to scan
    :return measurements: defaultdict of measurements for :param country:
                          and domains specified by :param config:
    """
    # Run the database query.
    result = run_query(country, *date_range, **config)
    # It's possible that no results were returned from the query in case there
    # are no measurements from a country for the period specified.
    if result is None:
        logging.warning("No results from OONI's query")
        return

    # Process the results to get the measurement data we care about.
    measurements = process_results(result)
    return measurements
