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
TPL_REVIEW_FORM = 'review.html'
TPL_BUSINESS = 'business.html'
TPL_SEARCH = 'search.html'

class NegativeFloatConverter(NumberConverter):
    '''
    Override NumberConverter to fix the issue with negative floats
    '''
    regex = r'\-?\d+\.\d+'
    num_convert = float

    def __init__(self, map, min=None, max=None):
        NumberConverter.__init__(self, map, 0, min, max)

logging.basicConfig(
    level=logging.DEBUG,
    filename='../app.log',
    format='%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(funcName)s#%(lineno)d - %(message)s')
logging.debug('App Start')

# def main():
#     _app = Flask(__name__)
#     _app.url_map.converters['float'] = NegativeFloatConverter
#     _app.config['MONGO_URI'] = config.DATABASE['uri']
#     _mongo = PyMongo(_app)
#     _dictLocations = {}  # Hold already entered business names and their generated locations
#     _api = None
#     with _app.app_context():
#         _api = api.Api(_mongo.db)
#     _app.run(debug=DEBUG)

_app = Flask(__name__)
# _app.url_map.converters['float'] = NegativeFloatConverter
# _app.config['MONGO_URI'] = config.DATABASE['uri']

# _mongo = PyMongo(_app)
# _db = DatabaseSeeder(_mongo.db)

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
    return render_template(TPL_INDEX)

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

# get reviews
# post review

# search by name
# search by tags
# search by rating
# search by location

@_app.route('/review/<name>/')
def get_review_form(name=''):
    """ Get review form page so a user can post a review. """
    return render_template(TPL_REVIEW_FORM, name=name)


@_app.route('/review/<name>/post/', methods=["POST"])
def post_review(name):
    """
    Post a review about given business name.
    Unpack request form and pass to api.
    """
    _api.save_review(request.form.copy())

    return redirect(url_for('get_business', name=name))

@_app.route('/api/business/<name>/')
def get_business_json(name):
    """ Return json representation of business request. """
    return jsonify(_api.request_reviews(name))


@_app.route('/business/<name>/')
def get_business(name):
    """ Get business reviews by given name. """
    business = _api.request_reviews(name)
    if not business:
        return redirect(url_for('get_home'))

    return render_template(TPL_BUSINESS, business=business)


@_app.route('/api/search/<float:lng>/<float:lat>/')
@_app.route('/api/search/<float:lng>/<float:lat>/<int:meters>/')
def get_search_json(lng, lat, meters=100):
    """ Return json representation of search request """
    places = _api.search(lng, lat, meters)
    if not places:
        _db.seed(lng, lat, meters)
        _db.create_indexes()
        places = _api.search(lng, lat, meters)

    return jsonify(places=places)


@_app.route('/search/<float:lng>/<float:lat>/')
@_app.route('/search/<float:lng>/<float:lat>/<int:meters>/')
def get_search(lat, lng, meters=100):
    """ With given lng, lat search in meters business near by. """
    places = _api.search(lng, lat, meters)
    return render_template(TPL_SEARCH, total=len(places), places=places)

# APPLICATION ENTRY
if __name__ == '__main__':
    # main()
    _app.run(debug=config.DEBUG)
