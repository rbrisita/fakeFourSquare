from datetime import datetime
import logging

from pymongo import DESCENDING
from bson.objectid import ObjectId

class Api:
    """
    Responsible for CRUD operations on database.
    """

    def __init__(self, db):
        self._db = db

    def request_place(self, place_id):
        """ Return place info from given place_id """
        places = []
        if not self._db.places.count():
            return places

        cursor = self._db.places.aggregate(
            [{
                '$match': {
                    '_id': ObjectId(place_id)
                }
            },{
                '$lookup': {
                    'from': 'reviews',
                    'localField': '_id',
                    'foreignField': 'place_id',
                    'as': 'place_ratings'
                }
            },{
                '$project': {
                    '_id': 1,
                    'name': 1,
                    'location': 1,
                    'tags': 1,
                    'distance': 1,
                    'ratings_avg': {
                        '$avg': '$place_ratings.rating'
                    },
                    'ratings_total': {
                        '$size': '$place_ratings.rating'
                    }
                }
            }],
            cursor={}
        )

        for p in cursor:
            p['_id'] = str(p['_id'])
            location = p.pop('location', [0, 0])
            p['lng'] = location[0]
            p['lat'] = location[1]
            logging.debug("%s", p)
            places.append(p)

        return places

    def save_place_review(self, place_id, blurb, rating):
        """ Save review associated with given place_id. """
        date = datetime.utcnow()
        review = {
            'date': date,
            'blurb': blurb,
            'rating': rating,
            'place_id': ObjectId(place_id),
            'created_at': date
        }

        # Check ObjectId

        # Check ttl?

        return self._db.reviews.insert(review)

    def request_review(self, review_id):
        """ Return review by given review_id. """
        reviews = []
        if not self._db.reviews.count():
            return reviews

        cursor = self._db.reviews.find({
            '_id': ObjectId(review_id)
        },{
            'created_at': 0
        })

        for r in cursor:
            logging.debug("%s", r)
            r['_id'] = str(r['_id'])
            r['place_id'] = str(r['place_id'])
            reviews.append(r)

        return reviews

    def request_place_reviews(self, place_id):
        """ Return reviews associated with given place_id.
        {
            "_id" : ObjectId,
            "date" : ISODate,
            "blurb" : Text,
            "rating" : Int,
            "place_id" : ObjectId,
            "created_at": ISODate
        }
        """
        reviews = []
        if not self._db.reviews.count():
            return reviews

        cursor = self._db.reviews.find({
            'place_id': ObjectId(place_id)
        },{
            '_id': 0,
            'place_id': 0,
            'created_at': 0
        }).sort('date', direction=DESCENDING)

        # cursor = self._db.reviews.aggregate([{
        #     '$match': {
        #         'place_id': ObjectId(place_id)
        # }},{
        #     '$project': {
        #         'date': {
        #             '$dateToString': {
        #                 'date': '$date',
        #                 'format': '%Y-%m-%dT%H:%M:%S.%LZ'
        #             }
        #         },
        #         '_id': 0,
        #         'rating': 1,
        #         'blurb': 1
        #     }
        # }],
        #     cursor={}
        # )

        for r in cursor:
            logging.debug("%s", r)
            reviews.append(r)

        return reviews

    def search(self, lng, lat, meters):
        """ Return places up to given meters from given coordinates. """
        places = []
        if not self._db.places.count():
            return places

        # cursor = self._db.places.find({
        #     'location': {
        #         '$near': {
        #             '$geometry': {
        #                 'type': 'Point',
        #                 'coordinates': [lng, lat]
        #             },
        #             '$maxDistance': meters
        #         }
        #     }
        # })

        cursor = self._db.places.aggregate(
            [{
                '$geoNear': {
                    'spherical': True, # Needed for versions < 4.0
                    'near': {
                        'type':'Point',
                        'coordinates': [
                            lng,
                            lat
                        ]
                    },
                    'distanceField': 'distance',
                    'maxDistance': meters
                }
            },{
                '$lookup': {
                    'from': 'reviews',
                    'localField': '_id',
                    'foreignField': 'place_id',
                    'as': 'place_ratings'
                }
            },{
                '$project': {
                    '_id': 1,
                    'name': 1,
                    'location': 1,
                    'tags': 1,
                    'distance': 1,
                    'ratings_avg': {
                        '$avg': '$place_ratings.rating'
                    },
                    'ratings_total': {
                        '$size': '$place_ratings.rating'
                    }
                }
            }],
            cursor={}
        )

        for p in cursor:
            p['_id'] = str(p['_id'])
            location = p.pop('location', [0, 0])
            p['lng'] = location[0]
            p['lat'] = location[1]
            logging.debug("%s", p)
            places.append(p)

        return places
