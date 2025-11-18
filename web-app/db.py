"""Database operations for the web app"""

import os

from pymongo import MongoClient

client = MongoClient(os.getenv("MONGO_URI"))
db = client.get_database(os.getenv("MONGO_DB"))
