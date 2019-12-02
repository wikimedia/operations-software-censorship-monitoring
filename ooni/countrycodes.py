import json
import logging

COUNTRY_CODES_FILE = "/usr/share/iso-codes/json/iso_3166-1.json"


def get_codes():
    """Get a mapping of two-letter country codes to their full names.

    :return countries: dict with two-letter codes as key and names as value
    """
    countries = {}
    try:
        with open(COUNTRY_CODES_FILE, "r") as f:
            json_data = json.loads(f.read())
    except IOError as e:
        logging.error(e)
        logging.error("File {0} not found".format(COUNTRY_CODES_FILE))
        return countries

    for each in json_data["3166-1"]:
        countries[each["alpha_2"]] = each["name"]

    # ZZ designates an unknown country.
    countries["ZZ"] = "Unknown"

    logging.debug("Fetched {0} country codes".format(len(countries)))

    return countries
