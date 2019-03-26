"""
Application responsible for packing and unpacking routes and views.
"""

import random

from flask import Flask, jsonify, render_template, redirect, url_for, request
from flask.ext.pymongo import PyMongo
from werkzeug.routing import NumberConverter

import api
import config
from generator import Generator

# CONSTANTS
DEBUG = True

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
_app.url_map.converters['float'] = NegativeFloatConverter
_app.config['MONGO_URI'] = config.DATABASE['uri']

_mongo = PyMongo(_app)

_dictLocations = {}  # Hold already entered business names and their generated locations

with _app.app_context():
    _api = api.Api(_mongo.db)

# ROUTES AND CONTROLLERS
@_app.route('/<path:path>/')  # Catch all
@_app.route('/')
def get_home(path=''):
    """ Get landing page of application """
    return render_template(TPL_INDEX)


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
    # Check ObjectId
    # Check name (force lower case) and location given

    # There should be multiple documents: places and reviews
    # name, location
    # rate, review, date
    # tags can be an array because tags are usually short words less than
    # 12 bytes (a size of an ObjectId) after long term usage where there
    # are multiple instances of the same tag (> 12 bytes) than a tags ObjectId
    # A manual reference can then be created.
    # a place has many reviews and many tags
    # tags can point to many places (index on tags)
    # a review is to one place

    arr_tag = request.form['tags']
    if not arr_tag:
        arr_tag = []
    else:
        arr_tag = request.form['tags'].split()

    if name not in _dictLocations:
        _dictLocations[name] = generate_location()

    form = request.form.copy()
    form['name'] = name
    form['tags'] = arr_tag
    form['location'] = _dictLocations[name]
    _api.save_review(form)

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


@_app.route('/api/search/<float:lat>/<float:lng>/')
@_app.route('/api/search/<float:lat>/<float:lng>/<int:meters>/')
def get_search_json(lat, lng, meters=100):
    """ Return json representation of search request """
    places = _api.search(lat, lng, meters)
    if not places:
        generator = Generator()
        places = []
        for _ in range(10):
            place = generator.generate_place(lat, lng, meters)
            places.append(place)

        # Generate 10 places

    return jsonify(places=places)


@_app.route('/search/<float:lat>/<float:lng>/')
@_app.route('/search/<float:lat>/<float:lng>/<int:meters>/')
def get_search(lat, lng, meters=100):
    """ With given lng, lat search in meters business near by. """
    places = _api.search(lat, lng, meters)
    return render_template(TPL_SEARCH, total=len(places), places=places)

def generate_location():
    """ Generate 2 random capped floating points and return array. """
    lat = round(random.uniform(40.722397, 40.733194), 6)
    lng = round(random.uniform(-73.985066, -73.999658), 6)
    return [lat, lng]

# APPLICATION ENTRY
if __name__ == '__main__':
    # main()
    _app.run(debug=DEBUG)
