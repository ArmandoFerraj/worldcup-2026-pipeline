from dotenv import load_dotenv
import boto3
import psycopg2
import json
import os

"""
-This script connects to the data lake (S3) and our data warehouse (postgres DB).
- It finds all runs in the data lake that are NOT in the data warehouse
and then loads them into their respective relations.
"""

load_dotenv()
s3 = boto3.client("s3")
BUCKET = "wc2026-pipeline-data-lake-armandoferraj"
result = s3.list_objects_v2(Bucket= BUCKET, Delimiter="/")

snapshots = [ p["Prefix"].rstrip("/") for p in result.get("CommonPrefixes", []) ] # every "folder" in the bucket
conn = psycopg2.connect(
    host =os.getenv("DB_HOST"), 
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"), 
    user=os.getenv("DB_USER"), 
    password=os.getenv("DB_PASSWORD"),
)
cur = conn.cursor()

cur.execute("SELECT DISTINCT snap_shot_date FROM stg_matches;")
rows = cur.fetchall()
loaded = [ r[0] for r in rows]

new_snapshots = [ s for s in snapshots if s not in loaded ] #every folder in S3 bucket but NOT in DB

for snapshot in new_snapshots:
    objects = s3.list_objects_v2(Bucket= BUCKET, Prefix= f"{snapshot}/")
    keys = [obj["Key"] for obj in objects["Contents"]]      
    
    for key in keys:
        response = s3.get_object(Bucket=BUCKET, Key=key)
        content = response["Body"].read()
        data = json.loads(content)

        relation_name = key.split("/")[1]
        if relation_name.split("_")[0] == "wc":
            relation_name = "stg_" + relation_name.split("_")[1]
        else:
            relation_name = "stg_" + relation_name.split("_")[0]
        
        cur.execute(
            f"INSERT INTO {relation_name} (snap_shot_date, raw) VALUES (%s, %s)",
            (snapshot, json.dumps(data))
        )
    conn.commit()



