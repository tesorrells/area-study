import json
import os
import typing
from time import sleep

import overpy
import requests
import simplekml
import qwikidata
import qwikidata.sparql


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
            print("Loading Google " + place)
            json_data = json.load(f)
    else:
        print("Acquiring Google " + place)
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
            print("Acquiring " + category + " " + place)
            response = api.query(query)
            sleep(10)
        except overpy.exception.OverpassGatewayTimeout:
            print("Server load too high, rerunning " + category + " " + place)
            sleep(20)
            load_or_query_osm_place(location, center_point, category, place, save_directory, kml)
            return True
        except overpy.exception.OverpassTooManyRequests:
            print("Server load too high, rerunning " + category + " " + place)
            sleep(20)
            load_or_query_osm_place(location, center_point, category, place, save_directory, kml)
            return True
        # if not os.path.isfile(place_file_name):
        #     with open(place_file_name, 'w') as f:
        #         nodes = reponse.get_nodes()
        #         json.dump(json.dumps(nodes), f)

    for node in response.nodes:
        pnt = kml.newpoint(name=category + "_" + place + "_" + str(node.id),
                           coords=[(node.lon, node.lat)], )
        pnt.style.iconstyle.icon.href = None

    return True


def get_city_wikidata(city, country):
    """
    Used to query wikidata for city info
    :param city: city to query
    :param country: country the city resides in
    :return: dict with population of city
    """
    query = """
    SELECT ?city ?cityLabel ?country ?countryLabel ?population
    WHERE
    {
      ?city rdfs:label '%s'@en.
      ?city wdt:P1082 ?population.
      ?city wdt:P17 ?country.
      ?city rdfs:label ?cityLabel.
      ?country rdfs:label ?countryLabel.
      FILTER(LANG(?cityLabel) = "en").
      FILTER(LANG(?countryLabel) = "en").
      FILTER(CONTAINS(?countryLabel, "%s")).
    }
    ORDER BY DESC(?population) LIMIT 100
    """ % (city, country)

    res = qwikidata.sparql.return_sparql_query_results(query)
    out = res['results']['bindings'][0]
    return out
