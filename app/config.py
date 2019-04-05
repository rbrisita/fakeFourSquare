"""
Configuration file for application.
"""

import os

import dotenv

dotenv.load_dotenv()

DATABASE = {
    'uri': os.getenv('MONGO_COLL_URI', 'mongodb://localhost/local')
}

LOCATION = {
    'lat': os.getenv('LOCATION_LAT', 40.729243),
    'lng': os.getenv('LOCATION_LNG', -73.984423)
}

DEBUG = os.getenv('DEBUG', False)

MAP = {
    'access_token': os.getenv('MAP_ACCESS_TOKEN', '{INSERT_YOUR_TOKEN}'),
    'max_area': os.getenv('MAP_MAX_AREA', 4000)
}
