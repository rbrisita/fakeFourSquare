"""
Seed database with test data and add indexes.
"""

import random

from pymongo import GEOSPHERE, ASCENDING

from tools.generator import Review
from tools.generator import Place

class DatabaseSeeder:
    def __init__(self, db):
        self._db = db
        random.seed(42)

    def clear(self):
        self._db.places.drop()
        self._db.reviews.drop()

    def reset(self, lng, lat, meters, total):
        self.clear()
        self.seed(lng, lat, meters, total)
        self.create_indexes()

    def seed(self, lng, lat, meters, total = 10):
        """ Seed database. """
        place = Place()
        places = []
        db = self._db

        for _ in range(total):
            places.append(place.generate(lng, lat, meters))

        ids = db.places.insert(places)
        review = Review()
        reviews = []
        while ids:
            place_id = ids.pop()
            for _ in range(random.randrange(1, 5)):
                r = review.generate()
                r['place_id'] = place_id
                reviews.append(r)

        db.reviews.insert(reviews)

    def create_indexes(self):
        db = self._db

        # Create Index according to current data access patterns
        db.places.ensure_index([("location", GEOSPHERE)])
        db.places.ensure_index([("tags", ASCENDING)])

        db.reviews.ensure_index([("rating", ASCENDING)])

        # Indexes for ttl deletions
        db.places.ensure_index([("created_at", ASCENDING)], expireAfterSeconds=600)
        db.reviews.ensure_index([("created_at", ASCENDING)], expireAfterSeconds=600)
