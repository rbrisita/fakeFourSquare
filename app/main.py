"""
Application responsible for packing and unpacking routes and views.
"""

import random
import logging

from flask import Flask, jsonify, render_template, redirect, url_for, request
from flask.ext.pymongo import PyMongo
from werkzeug.routing import NumberConverter

import api
import config
from tools.database_seeder import DatabaseSeeder

# CONSTANTS
TPL_INDEX = 'index.html'

class NegativeFloatConverter(NumberConverter):
    """ Override NumberConverter to fix the issue with negative floats. """
    regex = r'\-?\d+\.\d+'
    num_convert = float

    def __init__(self, map, min=None, max=None):
        NumberConverter.__init__(self, map, 0, min, max)

logging.basicConfig(
    level=logging.INFO,
    filename='../app.log',
    format='%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(funcName)s#%(lineno)d - %(message)s')
logging.info('App Start')

_app = Flask(__name__)

with _app.app_context():
    _app.url_map.converters['float'] = NegativeFloatConverter
    _app.config['MONGO_URI'] = config.DATABASE['uri']

    _mongo = PyMongo(_app)
    _db = DatabaseSeeder(_mongo.db)
    _api = api.Api(_mongo.db)

# ROUTES AND CONTROLLERS
@_app.route('/<path:path>/')  # Catch all
@_app.route('/')
def get_home(path=''):
    """ Get landing page of application """
    return render_template(TPL_INDEX, map_access_token=config.MAP['access_token'])

# get places
# post place
    # tags = request.form['tags']
    # if not tags:
    #     tags = []
    # else:
    #     tags = tags.split()

    # form = request.form.copy()
    # form['name'] = name
    # form['tags'] = arr_tag
    # form['location'] = _dictLocations[name]

@_app.route('/api/places/<place_id>/')
def get_place(place_id):
    """ Return place data by given place_id. """
    place = _api.request_place(place_id)
    if place:
        return jsonify(data = {'place': place})
    else:
        return jsonify(error = {'message': 'Place not found.'}), 404

@_app.route('/api/reviews/<review_id>/')
def get_review(review_id):
    """ Return review data by given review_id. """
    review = _api.request_review(review_id)
    if review:
        return jsonify(data = {'review': review})
    else:
        return jsonify(error = {'message': 'Review not found.'}), 404

@_app.route('/api/places/<place_id>/reviews/', methods=["POST"])
def post_place_review(place_id):
    """ Post a review about given place id.
    Unpack, validate, and pass to api.
    """
    blurb = request.form['blurb']
    rating = int(request.form['rating'])

    errors = {}
    if 3 > len(blurb) > 255:
        errors['blurb'] = 'Review is either too short or too long. Please revise.'

    if 1 > rating > 5:
        errors['rating'] = 'Rating is not in acceptable range. Please revise.'

    if errors:
        return jsonify(error=errors)

    review_id = _api.save_place_review(place_id, blurb, rating)
    if not review_id:
        errors['review'] = 'Review not saved.'
        return jsonify(error=errors)

    return jsonify(data = {'review_id': str(review_id)}), 201

@_app.route('/api/places/<place_id>/reviews/')
def get_place_reviews(place_id):
    """ Return json representation of reviews for given place id. """
    reviews = _api.request_place_reviews(place_id)
    return jsonify(data = {'reviews': reviews})

@_app.route('/api/search/<float:lng>/<float:lat>/')
@_app.route('/api/search/<float:lng>/<float:lat>/<int:meters>/')
def get_search(lng, lat, meters=100):
    """ Return json representation of search request """
    places = _api.search(lng, lat, meters)
    if not places:
        _db.seed(lng, lat, meters)
        _db.create_indexes()
        places = _api.search(lng, lat, meters)

    return jsonify(data = {'places': places})

# search by tags
# search by rating

# APPLICATION ENTRY
if __name__ == '__main__':
    _app.run(debug=config.DEBUG)
