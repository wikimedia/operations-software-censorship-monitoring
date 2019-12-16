# Censorship Monitoring Scripts

## Resources
1. [IODA](#ioda-fetch) [ioda-fetch]
2. [OONI](#ooni-fetch) [ooni-fetch]
3. [RIPE](#ripe-fetch) [ripe-fetch]

## ioda-fetch

This script queries IODA's API for a given country within a specific time period and returns internet outage data as per IODA. It takes as input the country name (or a list of countries) and a range of date and time (in UTC) specified by `--since` and `--until`.

`ioda-fetch` also detects `outage` events (see below for a more formal definition) as the API does not provide that information directly.

### Outage Event

An internet outage -- as defined by IODA but not made available in the API -- is an event where there is a transition from `normal` to `warning` or `critical` levels in a measurement. Whenever we detect such a transition, we mark it as an `outage` event and note the `fqid` of the measurement.

### Example

```
$ iodafetch --countries IR --since 2019-11-16T00:00:00 --until 2019-11-16T21:00:00
```

Runs a query for `IR` on `2019-11-16` between `00:00:00` and `21:00:00` to check for internet outages during that period and prints the result to `stdout`.

### Help

```
usage: iodafetch.py [-h] -c COUNTRIES [COUNTRIES ...] --since
                    %Y-%m-%dT%H:%M:%S --until %Y-%m-%dT%H:%M:%S [-v]

Fetch IODA outage data

optional arguments:
  -h, --help            show this help message and exit
  -c COUNTRIES [COUNTRIES ...], --countries COUNTRIES [COUNTRIES ...]
                        two-letter country codes to fetch outage data
  --since %Y-%m-%dT%H:%M:%S
                        date and time (UTC) to show outage data since
  --until %Y-%m-%dT%H:%M:%S
                        date and time (UTC) to show outage data until
  -v, --verbose         enable verbose output (logging.DEBUG)

```

## ooni-fetch

This script queries (a local copy of) OONI's `metadb` for specified domains within a given time period to check for anomalous measurements and generates an HTML report. It assumes you have a local copy of OONI's `metadb` that is running and actively synced so that it can make read-only queries to the database.

### Requirements

A copy of OONI's `metadb`; see https://github.com/ooni/sysadmin/blob/master/docs/metadb-sharing.md for setting a local replica. Note that this requires 700GB+ of disk space as it has all historic and current OONI measurements.

### Example

```
$ oonifetch --since 2019-11-16 --until 2019-11-17
```

Runs a query on all measurements for Wikimedia domains (see `ooni/oonifetch.py:DOMAINS`) from `2019-11-16` till `2019-11-17` and generates an HTML report that is printed to `stdout`.

### Help

```
usage: oonifetch.py [-h] [-v] [--since %Y-%m-%d] [--until %Y-%m-%d]

Fetch and parse Wikipedia domains from OONI's metadb

optional arguments:
  -h, --help        show this help message and exit
  -v, --verbose     enable verbose output (logging.DEBUG)
  --since %Y-%m-%d  date to show output since (from)
  --until %Y-%m-%d  date to show output until (to)
```

## ripe-fetch

This script queries RIPEstat's API (https://stat.ripe.net/docs/data_api/) to fetch BGP routing information for a given ASN, specifically the current and historic number of announced IPv4 prefixes. This information may be used to determine if there was an instance of internet shutdown or outage in the country, indicated by a significant change in the number of prefixes.

### Example

```
$ ripefetch -c IQ -a 50710 21277 -t 2019-10-04T09:00:00 -v
{'IQ': {50710: {'current': 489, 'past': 291}, 21277: {'current': 60, 'past': 56}}}
```

Fetches the announced IPv4 prefixes for ASNs `50710` and `21277` (in `IQ`) and prints the current and historic value (as on `2019-10-04`). If `-t` is not specified, it assumes a default date of yesterday.

### API Query Time

RIPEstat aligns the query time to either 00:00, 08:00 or 16:00 UTC by default. For example, if you run your query at 17:00 UTC, RIPEstat will return the information it had on 16:00 UTC. (This query time is also logged when the API request is made.)

### Help

```
usage: ripefetch.py [-h] -c COUNTRY -a ASNS [ASNS ...] [-t %Y-%m-%dT%H:%M:%S]
                    [-v]

Fetch routing history for a country and specified ASNs from RIPE

optional arguments:
  -h, --help            show this help message and exit
  -c COUNTRY, --country COUNTRY
                        two-letter country code to query for
  -a ASNS [ASNS ...], --asns ASNS [ASNS ...]
                        list of ASNs in country to run query against
  -t %Y-%m-%dT%H:%M:%S, --time %Y-%m-%dT%H:%M:%S
                        time to run the query for historic data
  -v, --verbose         enable verbose output (logging.DEBUG)
```
