"""
Application responsible for packing and unpacking routes and views.
"""

__author__ = 'rb'

# CONSTANTS
DEBUG = True

TPL_INDEX = 'index.html'
TPL_REVIEW_FORM = 'review.html'
TPL_BUSINESS = 'business.html'
TPL_SEARCH = 'search.html'


# LIBRARIES
import os
import random
from werkzeug.routing import NumberConverter, ValidationError
from flask import Flask, render_template, redirect, url_for, request
from flask.ext.pymongo import PyMongo
import api


# Override to fix the issue with negative floats
class NegativeFloatConverter(NumberConverter):
    regex = r'\-?\d+\.\d+'
    num_convert = float

    def __init__(self, map, min=None, max=None):
        NumberConverter.__init__(self, map, 0, min, max)


# MAIN VARIABLES
_app = Flask(__name__)
_app.url_map.converters['float'] = NegativeFloatConverter

URI = os.environ.get('MONGOLAB_URI')
if URI:
    _app.config['MONGO_URI'] = URI

_mongo = PyMongo(_app)

_dictLocations = {}  # Hold already entered business names and their generated locations

_api = None

with _app.app_context():
    _api = api.API(_mongo.db)


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
    return _api.request_reviews_json(name)


@_app.route('/business/<name>/')
def get_business(name):
    """ Get business reviews by given name. """
    business = _api.request_reviews(name)
    if not business:
        return redirect(url_for('get_home'))

    return render_template(TPL_BUSINESS, business=business)


@_app.route('/api/search/<float:lng>/<float:lat>/')
@_app.route('/api/search/<float:lng>/<float:lat>/<int:meters>/')
def get_search_json(lng, lat, meters=10):
    """ Return json representation of search request """
    return _api.search_json(lng, lat, meters)


@_app.route('/search/<float:lng>/<float:lat>/')
@_app.route('/search/<float:lng>/<float:lat>/<int:meters>/')
def get_search(lng, lat, meters=10):
    """ With given lng, lat search in meters business near by. """
    places = _api.search(lng, lat, meters)
    return render_template(TPL_SEARCH, total=len(places), places=places)


def generate_location():
    """ Generate 2 random capped floating points and return array. """
    lng = round(random.uniform(-73.985066, -73.999658), 6)
    lat = round(random.uniform(40.722397, 40.733194), 6)
    return [lng, lat]


# APPLICATION ENTRY
if __name__ == '__main__':
    _app.run(debug=DEBUG)
