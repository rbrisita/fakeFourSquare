""" Expose Web Views """

from flask import render_template

import config
from main import app

@app.route('/<path:path>/')  # Catch all
@app.route('/')
def get_home(path=''):
    """ Get landing page of application """
    return render_template(
        'index.html',
        map_access_token = config.MAP['access_token'],
        map_max_area = config.MAP['max_area'],
        location_lng = config.LOCATION['lng'],
        location_lat = config.LOCATION['lat']
    )
