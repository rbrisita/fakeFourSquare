import datetime

class Api:
    """
    Api responsible for CRUD operations on database and supplying json response.
    """
    __db = None

    def __init__(self, db):
        self.__db = db

    def save_review(self, dictForm):
        review = {
            'date': datetime.datetime.utcnow(),
            'name': dictForm['name'],
            'location': dictForm['location'],
            'rate': dictForm['rate'],
            'review': dictForm['review'],
            'tags': dictForm['tags']
        }

        # review = {date, review}
        # db.reviews.update({_id:{name:'mytest', location:[1,2]}}, {rate:1}, {upsert:1})
        # db.reviews.find({_id:{name:'mytest', location:[1,2]}})
        # self.__db.reviews.update({_id:{name, location}}, {$set:{review:review}}, upsert=True)

        self.__db.reviews.insert(review)

    def request_reviews(self, name):
        cursor = self.__db.reviews.find({'name': name}).sort('date', direction=-1)
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

    def search(self, lat, lng, meters):
        cursor = self.__db.reviews.find({
            "location": {
                '$near': {
                    '$geometry': {
                        'type': "Point",
                        'coordinates': [lat, lng]
                    },
                    '$maxDistance': meters
                }
            }
        },
        {
            '_id': 1,
            'name': 1,
            'rate': 1,
            'location': 1
        })

        places = []
        for place in cursor:
            places.append(place)

        return places
