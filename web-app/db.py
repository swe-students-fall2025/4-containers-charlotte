"""Database operations for the web app"""

import os
import pathlib

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database

DIR = pathlib.Path(__file__).parent

load_dotenv(DIR / ".env", override=True)

client = MongoClient(os.getenv("MONGO_URI"))
db_name = os.getenv("MONGO_DB")
if db_name:
    db: Database = client.get_database(db_name)
else:
    print("WARNING: MONGO_DB not set — running UI without DB")
    db = None
