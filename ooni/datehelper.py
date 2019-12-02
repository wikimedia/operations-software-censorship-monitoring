import logging
from datetime import datetime, timedelta

DATE_FORMAT = "%Y-%m-%d"


def date_yesterday():
    """Returns yesterday's date formatted to DATE_FORMAT."""
    return datetime.strftime(datetime.now() - timedelta(days=1), DATE_FORMAT)


def date_today():
    """Returns yesterday's date formatted to DATE_FORMAT."""
    return datetime.strftime(datetime.now(), DATE_FORMAT)


def time_now():
    """Returns the current time."""
    return datetime.now()


def format_date(date):
    """Format date as specified by DATE_FORMAT."""
    return datetime.strftime(date, DATE_FORMAT)


def validate_date(date):
    """Validate a date with DATE_FORMAT and convert it to a datetime object."""
    try:
        return datetime.strptime(date, DATE_FORMAT)
    except ValueError:
        logging.error("Invalid date: {0}. See --help".format(date))
        raise
