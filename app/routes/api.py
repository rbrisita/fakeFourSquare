""" Expose API """

from flask import jsonify, request

from main import app, dbs, cntl

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

@app.route('/api/places/<place_id>/')
def get_place(place_id):
    """ Return place data by given place_id. """
    place = cntl.request_place(place_id)
    if place:
        return jsonify(data = {'place': place})
    else:
        return jsonify(error = {'message': 'Place not found.'}), 404

@app.route('/api/reviews/<review_id>/')
def get_review(review_id):
    """ Return review data by given review_id. """
    review = cntl.request_review(review_id)
    if review:
        return jsonify(data = {'review': review})
    else:
        return jsonify(error = {'message': 'Review not found.'}), 404

@app.route('/api/places/<place_id>/reviews/', methods = ["POST"])
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

    review_id = cntl.save_place_review(place_id, blurb, rating)
    if not review_id:
        errors['review'] = 'Review not saved.'
        return jsonify(error=errors)

    return jsonify(data = {'review_id': str(review_id)}), 201

@app.route('/api/places/<place_id>/reviews/')
def get_place_reviews(place_id):
    """ Return json representation of reviews for given place id. """
    reviews = cntl.request_place_reviews(place_id)
    return jsonify(data = {'reviews': reviews})

@app.route('/api/search/<float:lng>/<float:lat>/')
@app.route('/api/search/<float:lng>/<float:lat>/<int:meters>/')
def get_search(lng, lat, meters=100):
    """ Return json representation of search request """
    places = cntl.search(lng, lat, meters)
    if not places:
        dbs.seed(lng, lat, meters)
        dbs.create_indexes()
        places = cntl.search(lng, lat, meters)

    return jsonify(data = {'places': places})

# search by tags
# search by rating
