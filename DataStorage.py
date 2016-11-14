__author__ = 'rb'

from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')

db = 'test'

collections = client[db].collection_names()

if not collections:
    client[db].create_collection()




# database_names()
# database.create_collection
