from email.policy import default
from dotenv import load_dotenv
import os
if os.path.exists(".env"):
    load_dotenv()
from flask import Flask, jsonify, send_file
from utilities.parser import update_db
from utilities.reader import get_reports, get_logs
from dotenv import load_dotenv




app = Flask(__name__)


@app.route("/parse/<version>/<data>")
def parse(version ,data):
    directory = os.environ["REPORTS_DIRECTORY"].rstrip("/") + "/" + version
    if not os.path.exists(directory):
        return "Not fount", 404
    if data == "latest":
        update_db(directory, only_today=True)
    else:
        update_db(directory, only_today=False)
    return "success", 200

# day should be one of these values: latest | today | YYYY-MM-DD
@app.route("/reports/", defaults={"day": ""})
@app.route("/reports/<path:day>")
def reports(day):
    if day == "":
        return jsonify(get_reports(""))
    document = get_reports(day)
    if document is None:
        return "This day did not contain any testing records", 404
    document.pop("_id")
    return document, 200

@app.route("/logs/", defaults={"log": ""})
@app.route("/logs/<path:log>")
def logs(log):
    if log == "":
        return jsonify(get_logs()), 200
    else:
        return send_file(get_logs(log))

app.run(host="0.0.0.0")