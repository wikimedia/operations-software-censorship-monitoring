import logging
from datetime import datetime, timedelta

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def date_yesterday():
    """Returns yesterday's date formatted to year-month-day."""
    return datetime.strftime(datetime.now() - timedelta(days=1), DATE_FORMAT)


def date_today():
    """Returns today's date formatted to year-month-day."""
    return datetime.strftime(datetime.now(), DATE_FORMAT)


def time_now():
    """Returns the current time formatted to ISO format."""
    return datetime.now().isoformat()


def time_epoch(start_date, end_date):
    """Return the epoch in seconds for a date period tuple.

    :param start_date: start date to convert to epoch
    :param end_date: end date to convert to epoch
    :return tuple: tuple of epoch(start_date, end_date)
    """
    logging.debug("Date range is from {0} to {1}".format(start_date, end_date))
    # This assume that the system time is UTC. If not, `test_time_epoch' in
    # `test/test_datehelper.py' will also fail.
    start_epoch = int(start_date.timestamp())
    end_epoch = int(end_date.timestamp())
    return start_epoch, end_epoch


def validate_date(date):
    """Validate a date with DATE_FORMAT and convert it to a datetime object."""
    try:
        return datetime.strptime(date, DATE_FORMAT)
    except ValueError:
        logging.error("Invalid date: {0}. See --help".format(date))
        raise
