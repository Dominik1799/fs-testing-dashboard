from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime
import pytz
import os

CONNECTION_STRING = "mongodb://{user}:{pasw}@{host}:27017/".format(user=os.environ["MONGO_USERNAME"], 
                                                                   pasw=os.environ["MONGO_PASSWORD"], 
                                                                   host=os.environ["MONGO_HOST"])

def parse_report_html(report_path):
    with open(report_path, "r", encoding="utf-8") as f:
        contents = f.read()
        soup = BeautifulSoup(contents, "html.parser")
        result = {}
        for res in soup.find("tr", class_="even").find_all("td"):
            if res.get("class")[0] == "marginicon": # skip icon
                continue
            result[res.get("class")[0]] = res.text
        
        return result

def parse_directory_contents(directory_path, only_today=True):
    # 1 document == 1 testing day
    # based in timestamp appended in the end of each test report
    documents = {}
    if only_today:
        tz = pytz.timezone('Europe/Bratislava')
        today = datetime.now(tz).strftime('%Y%m%d')[2:]
    with os.scandir(directory_path) as it:
        for entry in it:
            # if is not test report, skip
            if not os.path.exists(directory_path.rstrip("/") + "/" + entry.name + "/" + "report.html"):
                continue
            # extract only YYMMDD data from timestamp
            test_day = entry.name.split("_")[-1][:6]
            if only_today and test_day != today:
                continue
            if not test_day in documents:
                documents[test_day] = {}
                documents[test_day]["reports"] = []
            test_results = parse_report_html(os.path.join(entry.path, "report.html"))
            test_data = {
                "test_timestamp": int(entry.name.split("_")[-1]),
                "test_day": int(test_day),
                "test_name": entry.name[:-11],
                "full_test_name": entry.name,
                "full_path": os.path.abspath(entry.path),
                "full_path_html": os.path.abspath(os.path.join(entry.path, "report.html")),
                "test_results": test_results
            }
            documents[test_day]["reports"].append(test_data)
    
    return documents

def get_day_summary(reports):
    summary = {}
    avg = 0
    success = 0
    fail = 0
    total_time = 0
    t = 0
    for report in reports:
        avg += int(report["test_results"]["percent"])
        if report["test_results"]["percent"] == "100":
            success += 1
        else:
            fail += 1
        t = parse_time(report["test_results"]["realtime"])
        # wtf why can t be None??
        if t is not None:
            total_time += t
    avg = avg / len(reports)
    total_minutes = int(total_time) // 60
    total_seconds = total_time % 60
    if len(str(total_seconds)) == 1:
        total_seconds = str(0) + str(total_seconds)
    summary["overall_success_percent"] = round(avg, 2)
    summary["total_tests_executed"] = len(reports)
    summary["successful_tests"] = success
    summary["failed_tests"] = fail
    summary["total_time"] = "{min}:{sec} min".format(min=total_minutes, sec=total_seconds)

    return summary

def parse_time(duration):
    if "min" in duration:
        duration = duration.replace(" min", "").split(":")
        return int(duration[0]) * 60 + int(duration[1])
    if "s" in duration:
        duration = duration.replace(" s", "")
        return (int(duration))
    else:
        return 0
    
def update_db(directory_path, version ,only_today=True):
    client = MongoClient(CONNECTION_STRING)
    db = client["forumstar"]
    collection = db["testing_results_" + version]
    documents = parse_directory_contents(directory_path, only_today)
    
    for key in documents:
        mongo_doc = collection.find_one({"test_day": int(key)})
        # new day, no tests for this day
        if mongo_doc is None:
            collection.insert_one({"test_day": int(key), "version": version ,"reports": documents[key]["reports"], "summary": get_day_summary(documents[key]["reports"])})
        else:
            result = []
            mongo_reports = mongo_doc["reports"]
            new_reports = documents[key]["reports"]
            new_reports.extend(mongo_reports)
            i = 1
            for report in new_reports:
                if report not in result:
                    result.append(report)
            tem = collection.update_one({"test_day": int(key)}, { "$set": {"reports": result, "summary": get_day_summary(result)} })
            
            
