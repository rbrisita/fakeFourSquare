import datetime
import logging

class Api:
    """
    Responsible for CRUD operations on database and supplying json response.
    """

    def __init__(self, db):
        self._db = db

    def save_review(self, dictForm):
        review = {
            'date': datetime.datetime.utcnow(),
            'name': dictForm['name'],
            'location': dictForm['location'],
            'rate': dictForm['rate'],
            'review': dictForm['review'],
            'tags': dictForm['tags']
        }

        # Check ObjectId
        # Check name (force lower case) and location given

        # There should be multiple documents: places and reviews
        # name, location
        # rate, review, date
        # tags can be an array because tags are usually short words less that 12 bytes (a size of an ObjectId)
        # after long term usuage where there are multiple instances of the same tag
        # (> 12 bytes) than a tags ObjectId manual reference can be created.
        # a place has many reviews and many tags
        # tags can point to many places (index on tags)
        # a review is to one place

        # review = {date, review}
        # db.reviews.update({_id:{name:'mytest', location:[1,2]}}, {rate:1}, {upsert:1})
        # db.reviews.find({_id:{name:'mytest', location:[1,2]}})
        # self._db.reviews.update({_id:{name, location}}, {$set:{review:review}}, upsert=True)

        self._db.reviews.insert(review)

    def request_reviews(self, name):
        cursor = self._db.reviews.find({'name': name}).sort('date', direction=-1)
        if not cursor.count():
            return {}

        location = []
        rating = 0
        reviews = []
        tags = []
        for review in cursor:
            rating += int(review['rate'])
            reviews.append({'date': review['date'].strftime("%A, %B %d %Y at %I:%M%p"), 'review': review['review']})
            tags += review['tags']

            if not location:
                location = review['location']

        tags = list(set(tags))  # no duplicates
        tags.sort()
        rating = round(float(rating) / float(cursor.count()), 2)

        return {
            'name': name,
            'location': location,
            'rating': rating,
            'reviews': reviews,
            'tags': tags
        }

    def search(self, lng, lat, meters):
        cursor = self._db.places.find({
            'location': {
                '$near': {
                    '$geometry': {
                        'type': 'Point',
                        'coordinates': [lng, lat]
                    },
                    '$maxDistance': meters
                }
            }
        })

        logging.debug("%s", cursor)

        places = []
        for p in cursor:
            p['_id'] = str(p['_id'])
            location = p.pop('location', [0, 0])
            p['lng'] = location[0]
            p['lat'] = location[1]
            logging.debug("%s", p)
            places.append(p)

        return places
