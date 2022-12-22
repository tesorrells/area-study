import argparse
import configparser
import os
import typing
import simplekml
import geopy.distance
import overpy
import requests
import json
import pandas as pd
from geopy.geocoders import Nominatim
from constants import GOOGLE_API_PLACES, CATEGORIES, OSM_API_PLACES, VIOLENT_CRIME, PROPERTY_CRIME


def run(
        classification: str,
        data_directory: typing.Optional[str],
        save_directory: str,
        location: typing.List[float],
        google_api_key: str,
        categories: typing.List[bool],
        crime_soda_addr: typing.Optional[str] = None,
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
        load_crime_data(crime_soda_addr, location, center_point, save_directory)

    kml.save(file_name)


def load_or_query_place(place: str,
                        center_point: typing.List[float],
                        radius: float,
                        save_directory: str,
                        kml: simplekml.Kml,
                        google_api_key: str) -> bool:
    """
    Queries Google Places API for place nodes, defined in constants,
    within a certain radius of the center point of the location bounding box
    :param place: place as defined in constants
    :param center_point: center point of location bounding box lat/lon
    :param radius: radius from center point to corner of bounding box in meters
    :param save_directory: directory to save response to
    :param kml: kml layer to add nodes to
    :param google_api_key: google api key to query google maps/places api
    :return: False if failure, True if success
    """
    place_file_name = save_directory + "/" + place + "_" + str(center_point[0]) + "_" + str(center_point[1]) + ".json"
    if os.path.isfile(place_file_name):
        with open(place_file_name, 'r') as f:
            json_data = json.load(f)
    else:
        api_request = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" \
                      + str(center_point[0]) + "," + str(center_point[1]) + \
                      "&radius=" + str(radius) + "&type=" + place + "&sensor=true&key=" + str(google_api_key)
        rest_response = requests.get(api_request)
        if rest_response.json()["status"] == "REQUEST_DENIED":
            print("No Google API Key found, make sure API key is specified in cli/config.ini")
            return False
        if not os.path.isfile(place_file_name):
            with open(place_file_name, 'w') as f:
                json.dump(rest_response.json(), f)
        json_data = rest_response.json()

    places = json_data["results"]
    for plc in places:
        pnt = kml.newpoint(name=plc["name"],
                           coords=[(plc["geometry"]["location"]["lng"],
                                    plc["geometry"]["location"]["lat"])])
        pnt.description = plc["vicinity"]
        pnt.style.iconstyle.icon.href = plc["icon"]

    return True


def load_or_query_osm_place(location: typing.List[float],
                            center_point: typing.List[float],
                            category: str,
                            place: str,
                            save_directory: str,
                            kml: simplekml.Kml) -> bool:
    """
    Queries Open Street Map API for category + place nodes within a certain location bounding box
    :param location: top right and bottom left corners of bounding box, lat/lon
    :param center_point: center point of location bounding box lat/lon
    :param category: category as defined in constants
    :param place: place as defined in constants
    :param save_directory: directory to save response to
    :param kml: kml layer to add nodes to
    :return: False if failure, True if success
    """
    place_file_name = save_directory + "/" + place + "_" + str(center_point[0]) + "_" + str(center_point[1]) + ".json"

    if os.path.isfile(place_file_name):
        with open(place_file_name, 'r') as f:
            json_data = json.load(f)
    else:
        api = overpy.Overpass()
        query = """
                [out:json];
                node["{0}"="{1}"]({2},{3},{4},{5}); 
                out center;
                """
        query = query.format(category, place, location[2], location[1], location[0], location[3])
        try:
            response = api.query(query)
        except overpy.exception.OverpassGatewayTimeout:
            print("Server load too high, rerun" + category + " " + place)
            return False
        # if not os.path.isfile(place_file_name):
        #     with open(place_file_name, 'w') as f:
        #         nodes = reponse.get_nodes()
        #         json.dump(json.dumps(nodes), f)

    for node in response.nodes:
        pnt = kml.newpoint(name=category + "_" + place + "_" + str(node.id),
                           coords=[(node.lon, node.lat)],)
        pnt.style.iconstyle.icon.href = None

    return True


def load_polygons(data_directory: str, kml: simplekml.Kml):
    for filename in os.listdir(data_directory):
        with open(os.path.join(data_directory, filename), 'r') as f:
            json_data = json.load(f)
            for area in json_data:
                bounds = []
                for bound in json_data[area]:
                    bounds.append(bound)
                kml.newpolygon(name=area, outerboundaryis=bounds)


def load_crime_data(crime_soda_addr: str,
                    location: typing.List[float],
                    center_point: typing.List[float],
                    save_directory: str,):
    place_file_name = save_directory + "/crime_" + str(center_point[0]) + "_" + str(center_point[1]) + ".json"

    if os.path.isfile(place_file_name):
        with open(place_file_name, 'r') as f:
            crime_data = json.load(f)
    else:
        crime_data = requests.get(crime_soda_addr + "?$limit=50000")
        crime_data = crime_data.json()
        if not os.path.isfile(place_file_name):
            with open(place_file_name, 'w') as f:
                json.dump(crime_data, f)

    violent_crimes = {"MURDER": [], "ASSAULT": [], "RAPE": [], "ROBBERY": []}
    property_crimes = {"THEFT": [], "BURGLARY": []}
    for crime in crime_data:
        for key in violent_crimes:
            if key in crime["crime_type"]:
                if "zip_code" in crime.keys():
                    violent_crimes[key].append(crime["zip_code"])
                elif "location" in crime.keys():
                    violent_crimes[key].append(crime["location"])
                else:
                    violent_crimes[key].append(crime["address"])
        for key in property_crimes:
            if key in crime["crime_type"]:
                if "zip_code" in crime.keys():
                    property_crimes[key].append(crime["zip_code"])
                elif "location" in crime.keys():
                    property_crimes[key].append(crime["location"])
                else:
                    property_crimes[key].append(crime["address"])


def load_zipcode_boundaries(zipcode_soda_addr: str,
                            center_point: typing.List[float],
                            save_directory: str,):
    place_file_name = save_directory + "/crime_" + str(center_point[0]) + "_" + str(center_point[1]) + ".json"

    if os.path.isfile(place_file_name):
        with open(place_file_name, 'r') as f:
            zipcode_boundaries = json.load(f)
    else:
        zipcode_boundaries = requests.get(zipcode_soda_addr)
        zipcode_boundaries = zipcode_boundaries.json()
        if not os.path.isfile(place_file_name):
            with open(place_file_name, 'w') as f:
                json.dump(zipcode_boundaries, f)

    return zipcode_boundaries


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
            opt.categories.append(config["area-study"].getboolean("EMERGENCY_SERVICES"))
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
            opt.crime_soda_addr = config["area-study"].get("CRIME_SODA_ADDR")
        else:
            print("Config not found! Defaulting to cli arguments.")

    run(**vars(opt))


if __name__ == "__main__":
    main()
