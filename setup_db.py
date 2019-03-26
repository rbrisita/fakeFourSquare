#!/usr/bin/env python

"""
Seed database with test data and add indexes.
"""

import datetime

from pymongo import MongoClient, GEOSPHERE, ASCENDING

import config

def main():
    '''
    Main entry point.
    '''
    # Connect and get database from URI
    client = MongoClient(config.DATABASE['uri'])
    db = client.get_default_database() # pylint: disable=invalid-name

    print('Before seeding:')
    print(client.database_names())
    print(db.name)

    # Seed
    # NOTE: location is stored as [lat, long]
    docs = [{
        "name": "Test",
        "tags": [],
        "review": "test",
        "rate": "1",
        "location": [
            40.724106,
            -73.986787
        ],
        "date": datetime.datetime.utcnow()
    }, {
        "name": "Momofuku Noodle Bar",
        "tags": ['noodles'],
        "review": "Good noodles",
        "rate": "5",
        "location": [
            40.729243,
            -73.984423
        ],
        "date": datetime.datetime.utcnow()
    }]
    db.reviews.insert(docs)

    # Create Index according to current data access patterns
    db.reviews.ensure_index([("name", ASCENDING)])
    db.reviews.ensure_index([("location", GEOSPHERE)])

    print('After seeding:')
    print(client.database_names())
    print(db.collection_names())
    print('Total records:', db.reviews.count())
    print(db.reviews.index_information())

if __name__ == '__main__':
    main()
