import os
from pymongo import MongoClient

def get_history_collection():
    uri = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
    db_name = os.getenv("MONGO_DB", "translator")
    client = MongoClient(uri)
    db = client[db_name]
    return db["history"]
