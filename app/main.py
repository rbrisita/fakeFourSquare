"""
fake Four Square
Exposes an api to search for generated places and allows users to leave reviews.
Created data has a life expectancy of 10 minutues.
"""

import logging
import os

from flask import Flask
from flask_pymongo import PyMongo

import config
from controller import Controller
from converters import NegativeFloatConverter
from tools import DatabaseSeeder

file_path = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(
    level = logging.INFO,
    filename = file_path + '/../logs/app.log',
    format = '%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(funcName)s#%(lineno)d - %(message)s'
)

app = Flask(__name__)
app.config['DEBUG'] = config.DEBUG
app.config['MONGO_URI'] = config.DATABASE['uri']
app.url_map.converters['float'] = NegativeFloatConverter

with app.app_context():
    _mongo = PyMongo(app)
    dbs = DatabaseSeeder(_mongo.db)
    cntl = Controller(_mongo.db)

from routes import api, web

app.logger.info('App Start')

# APPLICATION ENTRY
if __name__ == '__main__':
    app.run()
