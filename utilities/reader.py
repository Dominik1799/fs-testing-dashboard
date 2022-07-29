from cmath import log
from pymongo import MongoClient
from pymongo import DESCENDING, ASCENDING
from datetime import datetime
import pytz
import os



CONNECTION_STRING = "mongodb://{user}:{pasw}@{host}:27017/".format(user=os.environ["MONGO_USERNAME"], 
                                                                   pasw=os.environ["MONGO_PASSWORD"], 
                                                                   host=os.environ["MONGO_HOST"])


def get_reports(day):
    client = MongoClient(CONNECTION_STRING)
    db = client["forumstar"]
    collection = db["testing_results"]
    if day == "latest":
        report = collection.find().sort("test_day", DESCENDING).limit(1)
        return report[0]
    elif day == "today":
        tz = pytz.timezone('Europe/Bratislava')
        today = int(datetime.now(tz).strftime('%Y%m%d')[2:])
        report = collection.find_one({"test_day": today})
        return report
    else:
        day = day.replace("-", "")[2:] if "-" in day else day
        if not day.isdigit():
            return None
        day = int(day)
        report = collection.find_one({"test_day": day})
        return report
    

def get_logs(log=None):
    logs = []
    if log is not None:
        return os.environ["CLIENT_DOWNLOADER_LOGS_DIRECTORY"].rstrip("/") + "/" + log
    with os.scandir(os.environ["CLIENT_DOWNLOADER_LOGS_DIRECTORY"]) as it:
        for entry in it:
            logs.append(entry.name)
    return logs