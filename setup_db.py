__author__ = 'rb'

import os
import datetime
from pymongo import MongoClient, GEOSPHERE, ASCENDING

# Connect
URI = os.environ.get('MONGOLAB_URI')
client = MongoClient(URI)

db = client.get_default_database()

#print 'Before seeding:'
#print client.database_names()


# Seed
# NOTE: location is stored as [long, lat]
docs = [{
    "name": "Test",
    "tags": [],
    "review": "test",
    "rate": "1",
    "location": [
        -73.986787,
        40.724106
    ],
    "date": datetime.datetime.utcnow()
}, {
    "name": "Momofuku Noodle Bar",
    "tags": ['noodles'],
    "review": "Good noodles",
    "rate": "5",
    "location": [
        -73.984423,
        40.729243
    ],
    "date": datetime.datetime.utcnow()
}]
db.reviews.insert(docs)


# Create Index according to current data access patterns
db.reviews.ensure_index([("name", ASCENDING)])
db.reviews.ensure_index([("location", GEOSPHERE)])

print 'After seeding:'
#print client.database_names()
print db.collection_names()
print db.reviews.index_information()



