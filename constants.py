import simplekml

GOOGLE_API_PLACES = {"emergency": ["fire_station", "hospital", "pharmacy", "veterinary_care"],
                     "law_enforcement": ["police"],
                     "military": [],
                     "water": [],
                     "power": [],
                     "food": ["supermarket", "convenience_store", "restaurant", "meal_takeaway", "meal_delivery"],
                     "transport": ["airport", "light_rail_station", "bus_station", "car_rental", "train_station",
                                   "transit_station", "subway_station", "gas_station"],
                     "services": ["bank", "dentist", "car_repair", "electrician", "laundry", "locksmith",
                                  "physiotherapist", "plumber", "post_office", "storage", ],
                     "government": ["city_hall", "courthouse", "embassy", "library", "local_government_office"],
                     "stores": ["book_store", "car_dealer", "department_store", "clothing_store", "electronics_store",
                                "furniture_store", "hardware_store", "home_goods_store", "jewelry_store",
                                "liquor_store", "shoe_store", "shopping_mall"],
                     "schools": ["university", "school", "secondary_school", "primary_school"],
                     "tourism": ["stadium", "tourist_attraction", "zoo", "night_club", "movie_theater",
                                 "amusement_park", "casino", "art_gallery"],
                     "shelter": ["campground", "lodging", "rv_park"],
                     "building": ["church", "mosque", "synagogue", "hindu_temple"],
                     "telecom": [],
                     "man_made": []}

OSM_API_PLACES = {"emergency": ["defibrillator", "landing_site", "fire_extinguisher", "fire_hydrant", "water_tank",
                                "drinking_water"],
                  "law_enforcement": [],
                  "military": ["airfield", "base", "bunker", "barracks", "checkpoint", "danger_area", "office", "range",
                               "training_area"],
                  "water": ["river", "oxbow", "canal", "lock", "fish_pass", "lake", "reservoir", "pond", "basin",
                            "lagoon", "stream_pool", "wastewater"],
                  "power": ["substation", "switch", "switchgear", "terminal", "tower", "transformer"],
                  "food": [],
                  "transport": [],
                  "services": [],
                  "government": [],
                  "stores": [],
                  "schools": [],
                  "tourism": [],
                  "shelter": [],
                  "building": ["shrine", "chapel", "monastery", "cathedral"],
                  "telecom": ["exchange", "connection_point", "distribution_point", "service_device", "data_center"],
                  "man_made": ["communications_tower", "monitoring_station", "observatory", "reservoir_covered",
                               "storage_tank", "street_cabinet", "surveillance", "water_tower", "water_well",
                               "water_tap", "water_works"]}

CATEGORIES = {0: "emergency",
              1: "law_enforcement",
              2: "military",
              3: "water",
              4: "power",
              5: "food",
              6: "transport",
              7: "services",
              8: "government",
              9: "stores",
              10: "schools",
              11: "tourism",
              12: "shelter",
              13: "building",
              14: "telecom",
              15: "man_made"}

OSM_PLACE_HIGH_FIDELITY = {"power": ["cable", "catenary_mast", "compensator", "connection", "converter", "generator",
                                     "heliosat", "insulator", "line", "busbar", "bay", "minor_line", "plant", "pole",
                                     "portal", ]}

VIOLENT_CRIME = ["MURDER", "ASSAULT", "RAPE", "ROBBERY", ]
PROPERTY_CRIME = ["THEFT", "BURGLARY", ]

CRIME_WEIGHTS = {"MURDER": 15, "ASSAULT": 2.5, "RAPE": 6.2, "ROBBERY": 4.7, "THEFT": 1, "BURGLARY": 2, }
