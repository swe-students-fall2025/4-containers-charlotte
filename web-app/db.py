"""Database operations for the web app"""

import os
import pathlib

from dotenv import load_dotenv
from pymongo import MongoClient

DIR = pathlib.Path(__file__).parent

load_dotenv(DIR / ".env", override=True)

client = MongoClient(os.getenv("DATABASE_URI"))
db = client.get_database(os.getenv("DATABASE_NAME"))
