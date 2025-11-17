from db import get_history_collection
from datetime import datetime
import time

collection = get_history_collection()

while True:
    print("ML client running...")
    collection.insert_one({"timestamp": datetime.utcnow(), "msg": "test insert"})
    time.sleep(10)
