__author__ = 'rb'

import os
import datetime
from pymongo import MongoClient, GEOSPHERE, ASCENDING

# Created to work around (test) permission issues

# Connect
URI = os.environ.get('MONGOLAB_URI')
client = MongoClient(URI)


# Create Index according to current data access patterns
client.rbrisita.reviews.ensure_index([("name", ASCENDING)])
client.rbrisita.reviews.ensure_index([("location", GEOSPHERE)])

print 'After seeding:'
print client.rbrisita.collection_names()
print client.rbrisita.reviews.index_information()


# Seed
# NOTE: location is stored as [long, lat]
docs = {
    "name": "Test",
    "tags": [],
    "review": "test",
    "rate": "1",
    "location": [
        -73.986787,
        40.724106
    ],
    "date": datetime.datetime.utcnow()
}
client.rbrisita.reviews.insert(docs)




