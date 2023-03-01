import json
import os
import typing
from collections import defaultdict

import requests
import simplekml


def load_polygons(data_directory: str, kml: simplekml.Kml):
    """
    Loads polygons from a file in a user specified data directory
    :param data_directory: directory user files are located
    :param kml: kml layer to add polygons to
    """
    for filename in os.listdir(data_directory):
        if os.path.isfile(os.path.join(data_directory, filename)):
            with open(os.path.join(data_directory, filename), 'r') as f:
                if filename.split(".")[1] == "json":
                    json_data = json.load(f)
                    for area in json_data:
                        bounds = []
                        for bound in json_data[area]:
                            bounds.append([bound[1], bound[0]])
                        poly = kml.newpolygon(name=area, outerboundaryis=bounds)
                        poly.style.polystyle.color = simplekml.Color.rgb(0, 0, 255, a=127)


def load_crime_data(crime_soda_addr: str,
                    location: typing.List[float],
                    center_point: typing.List[float],
                    save_directory: str,) -> tuple[dict[str, list], dict[str, list]]:
    """
    loads crime data from a SODA API
    :param crime_soda_addr: SODA API address
    :param location:
    :param center_point: center point for save file name
    :param save_directory: save directory to save API pull
    :return: returns dicts of violent and property crimes
    """
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

    return violent_crimes, property_crimes


def load_zipcode_boundaries(zipcode_soda_addr: str,
                            center_point: typing.List[float],
                            save_directory: str,
                            kml: simplekml.Kml,
                            crime_rate: typing.Optional[typing.Dict[str, int]] = None):
    """
    loads zipcode polygons from a SODA PI
    :param zipcode_soda_addr: SODA API adress
    :param center_point: center point for save file name
    :param save_directory: save directory to save API pull
    :param kml: kml layer to add polygons to
    :param crime_rate: crime rate list of area zip codes
    :return: returns the zipcode polygons
    """
    place_file_name = save_directory + "/zipcode_" + str(center_point[0]) + "_" + str(center_point[1]) + ".json"

    if os.path.isfile(place_file_name):
        with open(place_file_name, 'r') as f:
            zipcode_boundaries = json.load(f)
    else:
        zipcode_boundaries = requests.get(zipcode_soda_addr)
        zipcode_boundaries = zipcode_boundaries.json()
        if not os.path.isfile(place_file_name):
            with open(place_file_name, 'w') as f:
                json.dump(zipcode_boundaries, f)

    for zipcode in zipcode_boundaries:
        for poly in zipcode['the_geom']['coordinates']:
            bounds = []
            for area in poly:
                for point in area:
                    bounds.append(point)
        multipoly = kml.newpolygon(name=zipcode['zcta5ce10'], outerboundaryis=bounds)
        color_codes = defaultdict(lambda: simplekml.Color.rgb(82, 255, 255, a=100),
                                  {4000: simplekml.Color.rgb(255, 82, 82, a=100),
                                   3500: simplekml.Color.rgb(255, 125, 82, a=100),
                                   3000: simplekml.Color.rgb(255, 168, 82, a=100),
                                   2500: simplekml.Color.rgb(255, 212, 82, a=100),
                                   2000: simplekml.Color.rgb(255, 255, 82, a=100),
                                   1500: simplekml.Color.rgb(212, 255, 82, a=100),
                                   1000: simplekml.Color.rgb(168, 255, 82, a=100),
                                   500: simplekml.Color.rgb(125, 255, 82, a=100),
                                   400: simplekml.Color.rgb(82, 255, 82, a=100),
                                   300: simplekml.Color.rgb(82, 255, 125, a=100),
                                   200: simplekml.Color.rgb(82, 255, 168, a=100),
                                   100: simplekml.Color.rgb(82, 255, 212, a=100)})
        color_key_list = list(color_codes.keys())
        if zipcode['zcta5ce10'] not in crime_rate:
            multipoly.style.polystyle.color = simplekml.Color.rgb(82, 212, 255, a=100)
        else:
            color_key_idx = next(x[0] for x in enumerate(color_key_list) if x[1] < int(zipcode['zcta5ce10']))
            multipoly.style.polystyle.color = color_codes[color_key_list[color_key_idx]]

    return zipcode_boundaries
