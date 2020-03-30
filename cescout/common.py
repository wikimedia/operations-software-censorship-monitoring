import logging
from datetime import datetime, timezone

import iso3166

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def date_today():
    """Returns a datetime object formatted to ISO format.

    This calls `time_now()' so microseconds is set to 0.

    :return: datetime object
    """
    return datetime.fromisoformat(time_now())


def time_now():
    """Returns the current time in UTC in ISO format with microsecond=0.

    :return: string
    """
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def validate_date(date):
    """Validate a date string and convert it to a datetime object.

    If the conversion to ISO format is successful, return a datetime object
    otherwise raise ValueError that indicates an invalid date was passed.

    :param date: string to convert to a datetime object
    :return: datetime object
    """
    try:
        return datetime.fromisoformat(date)
    except ValueError:
        logging.error("Invalid date: {0}. See --help".format(date))
        raise


def country_name(country):
    """Return the full name of a country from its two-letter code.

    :param country: two-letter country code
    :return country_name: name of a country
    """
    try:
        country_name = iso3166.countries.get(country).name
    except KeyError:
        logging.error("Code for country {0} not found".format(country))
        country_name = "Unknown"

    return country_name
