# fs-testing-dashboard

## Development
1. create .env file in root directory of this repository
  put these variables inside:
      - REPORTS_DIRECTORY=Directory where every testing reports are uploaded. In production, this should be a docker volume.
      - CLIENT_DOWNLOADER_LOGS_DIRECTORY=directory, where client downloader logs are uploaded. Should also be docker volume
      - MONGO_USERNAME=username for mongoDB
      - MONGO_PASSWORD=password for mongoDB
      - MONGO_HOST=hostname / IP for mongoDB. Without port, it expects mongo to be on port 27017.
2. create venv using "python -m venv venv"
3. activate the venv using "./venv/Scripts/activate"
4. run "pip install -r requirements.txt"
5. run the app using "python app.py"

The rest of the components required to debug this while developing should be ran as docker containers (NGINX, mongoDB and fs-testing-dashboard-client).
