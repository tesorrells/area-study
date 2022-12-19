import argparse
import configparser
import os
import typing
import simplekml
import geopy.distance
import requests
import json


def run(
    classification: str,
    data_directory: typing.Optional[str],
    save_directory: str,
    location: typing.List[float],
    google_api_key: str,
    config_file: typing.Optional[str] = None,
    emergency_services: typing.Optional[bool] = None,
    law_enforcement: typing.Optional[bool] = None,
    military: typing.Optional[bool] = None,
    water: typing.Optional[bool] = None,
    power: typing.Optional[bool] = None,
    food: typing.Optional[bool] = None,
    transport: typing.Optional[bool] = None,
    services: typing.Optional[bool] = None,
    government: typing.Optional[bool] = None,
) -> None:
    kml = simplekml.Kml()
    ground = kml.newgroundoverlay(name='GroundOverlay')
    ground.latlonbox.north = float(location[0])
    ground.latlonbox.south = float(location[2])
    ground.latlonbox.east = float(location[3])
    ground.latlonbox.west = float(location[1])
    ground.latlonbox.rotation = 0

    center_point = [(float(location[0]) + float(location[2])) / 2, (float(location[3]) + float(location[1])) / 2]
    radius = geopy.distance.geodesic(center_point, [float(location[0]), float(location[1])]).m

    file_name = save_directory + "/master_" + str(center_point[0]) + "_" + str(center_point[1]) + ".kml"

    if emergency_services:
        load_or_query_place("fire_station", center_point, radius, save_directory, kml, google_api_key)
        load_or_query_place("hospital", center_point, radius, save_directory, kml, google_api_key)
        load_or_query_place("veterinary_care", center_point, radius, save_directory, kml, google_api_key)
    if law_enforcement:
        load_or_query_place("police", center_point, radius, save_directory, kml, google_api_key)
    if military:
        x = 1
    if water:
        x = 1
    if power:
        x = 1
    if food:
        load_or_query_place("supermarket", center_point, radius, save_directory, kml, google_api_key)
    if transport:
        load_or_query_place("airport", center_point, radius, save_directory, kml, google_api_key)
        load_or_query_place("light_rail_station", center_point, radius, save_directory, kml, google_api_key)
        load_or_query_place("bus_station", center_point, radius, save_directory, kml, google_api_key)
        load_or_query_place("car_rental", center_point, radius, save_directory, kml, google_api_key)
        load_or_query_place("train_station", center_point, radius, save_directory, kml, google_api_key)
        load_or_query_place("transit_station", center_point, radius, save_directory, kml, google_api_key)
        load_or_query_place("subway_station", center_point, radius, save_directory, kml, google_api_key)
        load_or_query_place("gas_station", center_point, radius, save_directory, kml, google_api_key)
    if services:
        x = 1
    if government:
        x = 1

        kml.save(file_name)


def load_or_query_place(place: str,
                        center_point: typing.List[float],
                        radius: float,
                        save_directory: str,
                        kml: simplekml.Kml,
                        google_api_key: str):
    place_file_name = save_directory + "/" + place + "_" + str(center_point[0]) + "_" + str(center_point[1]) + ".json"
    if os.path.isfile(place_file_name):
        with open(place_file_name, 'r') as f:
            json_data = json.load(f)
    else:
        fire_api_request = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" \
                           + str(center_point[0]) + "," + str(center_point[1]) + \
                           "&radius=" + str(radius) + "&type=" + place + "&sensor=true&key=" + str(google_api_key)
        rest_response = requests.get(fire_api_request)
        if not os.path.isfile(place_file_name):
            with open(place_file_name, 'w') as f:
                json.dump(rest_response.json(), f)
        json_data = rest_response.json()

    places = json_data["results"]
    for plc in places:
        kml.newpoint(name=plc["name"],
                     coords=[(plc["geometry"]["location"]["lat"],
                              plc["geometry"]["location"]["lng"])])


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
        "--emergency-services",
        type=bool,
        default=True,
        help="Label emergency services",
    )
    parser.add_argument(
        "--law-enforcement",
        type=bool,
        default=True,
        help="Label law enforcement",
    )
    parser.add_argument(
        "--military",
        type=bool,
        default=True,
        help="Label military infrastructure",
    )
    parser.add_argument(
        "--water",
        type=bool,
        default=True,
        help="Label water infrastructure",
    )
    parser.add_argument(
        "--power",
        type=bool,
        default=True,
        help="Label power infrastructure",
    )
    parser.add_argument(
        "--food",
        type=bool,
        default=True,
        help="Label food locations",
    )
    parser.add_argument(
        "--transport",
        type=bool,
        default=True,
        help="Label transport locations",
    )
    parser.add_argument(
        "--services",
        type=bool,
        default=True,
        help="Label transport locations",
    )
    parser.add_argument(
        "--government",
        type=bool,
        default=True,
        help="Label transport locations",
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
            opt.emergency_services = config["area-study"].get("EMERGENCY_SERVICES")
            opt.law_enforcement = config["area-study"].get("LAW_ENFORCEMENT")
            opt.military = config["area-study"].get("MILITARY")
            opt.water = config["area-study"].get("WATER")
            opt.power = config["area-study"].get("POWER")
            opt.food = config["area-study"].get("FOOD")
            opt.transport = config["area-study"].get("TRANSPORT")
            opt.services = config["area-study"].get("SERVICES")
            opt.government = config["area-study"].get("government")
        else:
            print("Config not found! Defaulting to cli arguments.")

    run(**vars(opt))


if __name__ == "__main__":
    main()
