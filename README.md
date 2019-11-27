# Censorship Monitoring Scripts

## ioda-fetch

This script queries IODA's API for a given country within a specific time period and returns internet outage data as per IODA. It takes as input the country name (or a list of countries) and a range of date and time (in UTC) specified by `--since` and `--until`.

`ioda-fetch` also detects `outage` events (see below for a more formal definition) as the API does not provide that information directly.

### Outage Event

An internet outage -- as defined by IODA but not made available in the API -- is an event where there is a transition from `normal` to `warning` or `critical` levels in a measurement. Whenever we detect such a transition, we mark it as an `outage` event and note the `fqid` of the measurement.

### Example

```
iodafetch --countries IR --since 2019-11-16T00:00:00 --until 2019-11-16T21:00:00
```

Runs a query for `IR` on `2019-11-16` between `00:00:00` and `21:00:00` and checks for internet outages during that period.

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
