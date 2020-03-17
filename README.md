# cescout: censorship monitoring toolkit

`cescout` is a censorship monitoring toolkit that queries multiple internet measurement projects to identify censorship events and internet outages. It serves as an interface to collect data from different projects to identify such events in a given country and uses that information to generate a report that helps distinguish between censorship of particular websites from broader internet outages or shutdowns. `cescout` does not perform any internet measurements by itself.

Currently it queries the following projects: OONI (ooni.org), for information about censorship of websites; IODA (ioda.caida.org), for internet outages (and shutdowns); and RIPE (stat.ripe.net), to fetch routing information that is used to correlate information from OONI and IODA.

## Requirements

Python 3.7 and some additional libraries; see `requirements.txt` in the root folder for a complete list.

For the OONI tests, a copy of OONI's `metadb` is required; please see the OONI documentation at https://github.com/ooni/sysadmin/blob/master/docs/metadb-sharing.md for instructions on how to set up a replica. Note that this requires 700GB+ of disk space as it has all current and historic OONI measurements.

## Install

To install the package, run:

```
# python3 setup.py install
```

You need root permissions for the installation but not for running `cescout`.

Note that you may need additional packages to install the `psycopg2` dependency; on Debian, `apt install python3-dev libpq-dev gcc`.

## Usage

```
usage: cescout [-h] -c COUNTRY -s %Y-%m-%dT%H:%M:%S [-u %Y-%m-%dT%H:%M:%S]
               [-a ASNS [ASNS ...]] [-v] [-r] [--skip-ooni] [--skip-ioda]
               [--skip-ripe]

cescout fetches censorship and internet outage measurements from OONI
(ooni.org), IODA (ioda.caida.org), RIPE (stat.ripe.net) for a given country
(and its ASNs) and generates a report.

optional arguments:
  -h, --help            show this help message and exit
  -c COUNTRY, --country COUNTRY
                        two-letter country code to run query against
  -s %Y-%m-%dT%H:%M:%S, --since %Y-%m-%dT%H:%M:%S
                        date and time in UTC to show data since (from)
  -u %Y-%m-%dT%H:%M:%S, --until %Y-%m-%dT%H:%M:%S
                        date and time in UTC to show data until (to)
  -a ASNS [ASNS ...], --asns ASNS [ASNS ...]
                        list of ASNs in country to query for
  -v, --verbose         enable verbose output (logging.DEBUG)
  -r, --raw             return the raw JSON results instead of a report
  --skip-ooni           skip measurements from ooni
  --skip-ioda           skip measurements from ioda
  --skip-ripe           skip measurements from ripe
```

## Example Run


```
$ cescout --country IR --since 2020-02-01T09:00:00 --until 2020-02-02T15:00:00 --asns 44244
Censorship Report for 'Iran, Islamic Republic of' [2020-02-01 09:00:00 to 2020-02-02 15:00:00]

[ooni] domains: wikipedia.org, wikimedia.org, wikidata.org, wikisource.org, wikibooks.org, wiktionary.org, wikiquote.org, wikiversity.org, wikivoyage.org, wikinews.org
[ooni] (0 / 0) anomalous measurements
[ioda] internet outage observed. more information at https://ioda.caida.org/ioda/dashboard#view=inspect&entity=country/IR&lastView=overview&from=1580547600&until=1580655600
[ripe] ASN 44244: 2020-02-25 13:56:05: 337 (current), 2020-02-01 09:00:00: 341 (since), 2020-02-02 15:00:00: 341 (until)
```

You can skip tests by passing the `--skip` argument.


```
$ cescout --country CN --since 2020-02-20 --skip-ioda --skip-ripe
Censorship Report for 'China' [2020-02-20 00:00:00 to 2020-02-25 14:48:48]

[ooni] domains: wikipedia.org, wikimedia.org, wikidata.org, wikisource.org, wikibooks.org, wiktionary.org, wikiquote.org, wikiversity.org, wikivoyage.org, wikinews.org
[ooni] (1 / 1) anomalous measurements
[ooni] https://explorer.ooni.io/measurement/20200222T155655Z_AS17621_XPfuzZadWqOI5uj4cEGHwMxNhsVJDFjNmTAtTGPaRdss6rptZc?input=https%3A//en.wiktionary.org/wiki/Wiktionary%3AMain_Page/ [!]
[ioda] skipped test
[ripe] skipped test
```

Note that if you don't pass `--until`, it assumes the current time.

By default, a report is generated (formatted according to `config/report.template`) once the measurement data is processed. To return the raw results in JSON instead, pass the `--raw` argument.

```
$ cescout --country CN --since 2020-02-20 --skip-ioda --skip-ripe --raw | python3 -m json.tool
{
    "country": "China",
    "asns": null,
    "current": "2020-02-25 15:08:39",
    "since": "2020-02-20 00:00:00",
    "until": "2020-02-25 15:08:39",
    "config": {
        "ooni": {
            "db_name": "metadb",
            "db_user": "postgres",
            "domains": [
                "wikipedia.org",
                "wikimedia.org",
                "wikidata.org",
                "wikisource.org",
                "wikibooks.org",
                "wiktionary.org",
                "wikiquote.org",
                "wikiversity.org",
                "wikivoyage.org",
                "wikinews.org"
            ]
        }
    },
    "projects": {
        "ooni": {
            "data": {
                "len_all": 1,
                "len_blocking": 1,
                "measurements": [
                    {
                        "url": "https://explorer.ooni.io/measurement/20200222T155655Z_AS17621_XPfuzZadWqOI5uj4cEGHwMxNhsVJDFjNmTAtTGPaRdss6rptZc?input=https%3A//en.wiktionary.org/wiki/Wiktionary%3AMain_Page/",
                        "blocking": "tcp_ip"
                    }
                ]
            },
            "ran_test": true
        },
        "ioda": {
            "ran_test": false
        },
        "ripe": {
            "ran_test": false
        }
    }
}
```

## Current Projects

All projects take as input a two-letter country code and a time period to run the query for, specified by `--since` and `--until` (the current time is assumed if `--until` is not passed). Additional arguments may be required depending on the project, such as `--asns` (list of ASNs) for running the RIPE test.

## Configuration File

During installation, the script copies the configuration files to `/etc/cescout`. To override the system-wide settings, copy the files from `/etc/cescout` (or `config/`) to `$HOME/.config/cescout` and edit as required.

## OONI

[From https://ooni.org/]

Queries (a local copy of) OONI's `metadb` for specified domains (see `config/cescout.cfg`) to check for anomalous measurements. A measurement is marked as anomalous if the `blocking` type is not `false` (examples: `dns` or `tcp_ip`).

Measurements are fetched for Wikimedia domains by default, as specified in `config/cescout.cfg`. To run the script for custom domains, add them to the `config/cescout.cfg` file.

This project assumes you have a local copy of OONI's `metadb` that is running and actively synced as that is used to make read-only queries to the database, and it is skipped if a local copy of `metadb` is not found or if it was unable to connect to it.

## IODA

[From https://ioda.caida.org/]

Queries IODA's API and returns internet outage data as per IODA.  An internet outage -- as defined by IODA but not made available in their API -- is an event where there is a transition from `normal` to `warning` or `critical` levels in the measurement time frame.

## RIPE

[From https://stat.ripe.net/]

Queries RIPEstat's API (https://stat.ripe.net/docs/data_api/) to fetch BGP routing information for a given ASN, specifically the current and historic number of announced IPv4 prefixes. This information may be used to determine if there was an instance of internet shutdown or outage in the country, indicated by a significant change in the number of prefixes.

This project is skipped if the `--asns` or `-a` argument is not passed.
