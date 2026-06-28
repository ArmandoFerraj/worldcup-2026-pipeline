from dotenv import load_dotenv
import os
import requests
import json
import datetime as dt
from pathlib import Path
import boto3
import time

"""
- This script connects to the footballdata.com data source.
- We connect to the 5 endoints and extract json blobs from each one.
- We place all the blobs inside of a folder and upload it to our data lake (S3 BUCKET)
each time this script is ran.
- The API call is wrapped in a retry loop to absorb transient network/SSL failures.
"""

current_date_time = dt.datetime.now(dt.timezone.utc)  # current universal time
run_date = current_date_time.strftime("%Y-%m-%d_%H-%M")
script_dir = Path(__file__).parent  # dir the script lives in (extract/)
root_dir = script_dir.parent  # project root dir

run_dir = root_dir / "data" / "raw" / run_date  # path to this run's data
run_dir.mkdir(parents=True, exist_ok=True)  # create dir for this run
bucket_name = "wc2026-pipeline-data-lake-armandoferraj"

load_dotenv()
s3 = boto3.client("s3")
api_key = os.getenv("FOOTBALL_DATA_API_KEY")

url_base = "https://api.football-data.org/v4/competitions/WC/"
endpoints = {
    "wc_metadata": "",
    "matches": "matches",
    "standings": "standings",
    "teams": "teams",
    "scorers": "scorers?limit=100",
}
header = {"X-Auth-Token": api_key}

for attempt in range(5):
    try:
        for name, endpoint in endpoints.items():
            response = requests.get(url=url_base + endpoint, headers=header)
            response.raise_for_status()
            data = response.json()
            filename = run_dir / f"{name}_{run_date}.json"
            s3_key = f"{run_date}/{name}_{run_date}.json"
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)

            s3.upload_file(str(filename), bucket_name, s3_key)
        break
    except requests.exceptions.RequestException as e:
        print(f"Attempt {attempt + 1} failed: {e}")
        time.sleep(30)
else:
    raise Exception("All attempts failed -- API unreachable")