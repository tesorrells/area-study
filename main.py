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
        # pull fire stations
        fire_file_name = save_directory + "/fire_" + str(center_point[0]) + "_" + str(center_point[1]) + ".json"
        if os.path.isfile(fire_file_name):
            with open(fire_file_name, 'r') as f:
                fire_json = json.load(f)
        else:
            fire_api_request = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" \
                          + str(center_point[0]) + "," + str(center_point[1]) + \
                          "&radius=" + str(radius) + "&type=fire_station&sensor=true&key=" + str(google_api_key)
            fire_response = requests.get(fire_api_request)
            if not os.path.isfile(fire_file_name):
                with open(fire_file_name, 'w') as f:
                    json.dump(fire_response.json(), f)
            fire_json = fire_response.json()

        fire_stations = fire_json["results"]
        kml_points = []
        for station in fire_stations:
            kml_points.append(kml.newpoint(name=station["name"],
                                           coords=[(station["geometry"]["location"]["lat"],
                                                    station["geometry"]["location"]["lng"])]))

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
        else:
            print("Config not found! Defaulting to cli arguments.")

    run(**vars(opt))


if __name__ == "__main__":
    main()
