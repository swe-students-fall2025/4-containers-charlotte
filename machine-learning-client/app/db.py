"""
Database operations for the ML client
"""

import os
import pathlib

from dotenv import load_dotenv
from gridfs import GridFSBucket
from pymongo import MongoClient
from pymongo.database import Database

DIR = pathlib.Path(__file__).parent

load_dotenv(DIR / ".env", override=True)

client = MongoClient(os.getenv("MONGO_URI"))
db_name = os.getenv("MONGO_DB")
if not db_name:
    print("WARNING: MONGO_DB not set — running UI without DB")
    db = None
    gridfs = None
else:
    db: Database = client.get_database(db_name)
    gridfs = GridFSBucket(db, bucket_name="audio")
