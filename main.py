import argparse
import configparser
import os
import typing

import simplekml
import geopy.distance

from calculators import calculate_crime_rate
from constants import GOOGLE_API_PLACES, CATEGORIES, OSM_API_PLACES, CRIME_WEIGHTS
from data_loaders import load_polygons, load_crime_data, load_zipcode_boundaries
from data_queries import load_or_query_place, load_or_query_osm_place


def run(
        classification: str,
        data_directory: typing.Optional[str],
        save_directory: str,
        location: typing.List[float],
        google_api_key: str,
        categories: typing.List[bool],
        city: str,
        state: str,
        country_code: str,
        crime_soda_addr: typing.Optional[str] = None,
        zipcode_soda_addr: typing.Optional[str] = None,
        config_file: typing.Optional[str] = None,
) -> None:
    kml = simplekml.Kml()
    # ground = kml.newgroundoverlay(name='GroundOverlay')
    # ground.latlonbox.north = float(location[0])
    # ground.latlonbox.south = float(location[2])
    # ground.latlonbox.east = float(location[3])
    # ground.latlonbox.west = float(location[1])
    # ground.latlonbox.rotation = 0

    center_point = [(float(location[0]) + float(location[2])) / 2, (float(location[3]) + float(location[1])) / 2]
    radius = geopy.distance.geodesic(center_point, [float(location[0]), float(location[1])]).m

    file_name = save_directory + "/master_" + str(center_point[0]) + "_" + str(center_point[1]) + ".kml"

    if data_directory:
        load_polygons(data_directory, kml)

    for idx, val in enumerate(categories):
        if val:
            for place in GOOGLE_API_PLACES[CATEGORIES[idx]]:
                load_or_query_place(place, center_point, radius, save_directory, kml, google_api_key)
            for place in OSM_API_PLACES[CATEGORIES[idx]]:
                load_or_query_osm_place(location, center_point, CATEGORIES[idx], place, save_directory, kml)

    if crime_soda_addr:
        violent_crimes, property_crimes = load_crime_data(crime_soda_addr, location, center_point, save_directory)
        crime_rate = calculate_crime_rate(violent_crimes, property_crimes, city, country_code)

        if zipcode_soda_addr:
            zipcode_boundaries = load_zipcode_boundaries(zipcode_soda_addr,
                                                         center_point,
                                                         save_directory,
                                                         kml,
                                                         crime_rate)

    kml.save(file_name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--classification",
        default="UNCLASSIFIED",
        help="Classification level of output",
    )
    parser.add_argument(
        "--data-directory",
        required=False,
        type=str,
        help="directory of assets to detect on",
    )
    parser.add_argument(
        "--save-directory",
        default="save",
        help="directory to save results",
    )
    parser.add_argument(
        "--config-file",
        required=False,
        type=str,
        default="config.ini",
        help="config for CLI arguments",
    )
    parser.add_argument(
        "--google-api-key",
        required=False,
        type=str,
        default=None,
        help="google maps api key",
    )
    parser.add_argument(
        "--location",
        required=False,
        type=list,
        default=None,
        help="upper left, and lower right bounds of area study",
    )
    parser.add_argument(
        "--categories",
        type=list,
        help="List of categories",
    )
    parser.add_argument(
        "--crime_soda_addr",
        type=str,
        help="SODA API address for crime data",
    )
    parser.add_argument(
        "--zipcode_soda_addr",
        type=str,
        help="SODA API address for zipcode data",
    )
    parser.add_argument(
        "--city",
        type=int,
        help="City area resides in",
    )
    parser.add_argument(
        "--state",
        type=int,
        help="state area resides in",
    )
    parser.add_argument(
        "--country-code",
        type=int,
        help="country area resides in",
    )

    opt = parser.parse_args()
    if opt.config_file:
        if os.path.isfile(opt.config_file):
            config = configparser.ConfigParser()
            config.read(opt.config_file)
            opt.classification = config["area-study"].get("CLASSIFICATION")
            opt.data_directory = config["area-study"].get("DATA_DIRECTORY")
            opt.save_directory = config["area-study"].get("SAVE_DIRECTORY")
            opt.google_api_key = config["area-study"].get("GOOGLE_API_KEY")
            opt.location = config["area-study"].get("LOCATION").split(",")
            opt.categories = []
            opt.categories.append(config["area-study"].getboolean("EMERGENCY"))
            opt.categories.append(config["area-study"].getboolean("LAW_ENFORCEMENT"))
            opt.categories.append(config["area-study"].getboolean("MILITARY"))
            opt.categories.append(config["area-study"].getboolean("WATER"))
            opt.categories.append(config["area-study"].getboolean("POWER"))
            opt.categories.append(config["area-study"].getboolean("FOOD"))
            opt.categories.append(config["area-study"].getboolean("TRANSPORT"))
            opt.categories.append(config["area-study"].getboolean("SERVICES"))
            opt.categories.append(config["area-study"].getboolean("GOVERNMENT"))
            opt.categories.append(config["area-study"].getboolean("STORES"))
            opt.categories.append(config["area-study"].getboolean("SCHOOLS"))
            opt.categories.append(config["area-study"].getboolean("TOURISM"))
            opt.categories.append(config["area-study"].getboolean("SHELTER"))
            opt.categories.append(config["area-study"].getboolean("BUILDING"))
            opt.categories.append(config["area-study"].getboolean("TELECOM"))
            opt.categories.append(config["area-study"].getboolean("MAN_MADE"))
            opt.crime_soda_addr = config["area-study"].get("CRIME_SODA_ADDR")
            opt.zipcode_soda_addr = config["area-study"].get("ZIPCODE_SODA_ADDR")
            opt.city = config["area-study"].get("CITY")
            opt.state = config["area-study"].get("STATE")
            opt.country_code = config["area-study"].get("COUNTRY_CODE")
        else:
            print("Config not found! Defaulting to cli arguments.")

    run(**vars(opt))


if __name__ == "__main__":
    main()
