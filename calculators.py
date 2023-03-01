import typing

import pandas as pd

from constants import CRIME_WEIGHTS
from data_queries import get_city_wikidata


def calculate_crime_rate(violent_crimes: typing.Dict[str, str],
                         property_crimes: typing.Dict[str, str],
                         city: str,
                         country_code: str):
    """
    Calculates the overall crime rate in a zipcode and applies a color code to the zipcode polygon
    :param violent_crimes: dict of violent crimes and the zipcodes they occur in
    :param property_crimes: dict of property crimes and the zipcodes they occur in
    :param city: city used to get population information to calculate crime rate
    :param country_code: country code used to get population information to calculate crime rate
    :return: returns a list of the crime rates for each zipcode
    """
    city_wikidata = get_city_wikidata(city, country_code)
    population = int(city_wikidata["population"]["value"])
    crime_counts = {"MURDER": [], "ASSAULT": [], "RAPE": [], "ROBBERY": [], "THEFT": [], "BURGLARY": []}
    for key, values in violent_crimes.items():
        crime_counts[key] = pd.Series(values).value_counts()
    for key, values in property_crimes.items():
        crime_counts[key] = pd.Series(values).value_counts()
    for key in crime_counts:
        crime_counts[key] = list(zip(crime_counts[key], crime_counts[key].index))

    crime_rate = {}
    for key, value in crime_counts.items():
        try:
            for zipcode in value:
                if zipcode[1] in crime_rate:
                    crime_rate[zipcode[1]] += zipcode[0] * CRIME_WEIGHTS[key]
                else:
                    crime_rate[zipcode[1]] = zipcode[0] * CRIME_WEIGHTS[key]
        except:
            continue

    return crime_rate
