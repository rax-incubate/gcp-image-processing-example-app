import functions_framework
import os
import json
import uuid
from google.cloud import storage
from google.api_core.client_options import ClientOptions
from google.cloud import bigquery


@functions_framework.cloud_event
# receive delete image events from GCS
def delete_image_data(cloud_event):
    eid = uuid.uuid4().hex
    debugx = False
    if os.environ.get('DEBUGX') == "1":
        debugx = True

    data = cloud_event.data

    event_id = cloud_event["id"]
    event_type = cloud_event["type"]

    bucket = data["bucket"]
    filename = data["name"]

    if debugx:
        print(f"DEBUGX:{eid}:Event type:{event_type},Bucket:{bucket},File:{filename}")
    delete_data(bucket, filename, eid)


# Delete data in BQ
def delete_data(bucket, filename, eid):
    debugx = False
    if os.environ.get('DEBUGX') == "1":
        debugx = True

    bq_dataset_id = os.environ.get('BQ_DATASET_ID')
    bq_table_id = os.environ.get('BQ_TABLE_ID')

    if debugx:
        print(f"DEBUGX:{eid}:BQ Dataset:{bq_dataset_id},Table:{bq_table_id},Bucket:{bucket},File:{filename}")

    client = bigquery.Client()

    sql = list()
    sql.append("DELETE FROM " + bq_dataset_id + "." + bq_table_id)
    sql.append(" WHERE bucket='" + bucket + "'")
    sql.append(" AND filename='" + filename + "'")
    query = "".join(sql)

    if debugx:
        print(f"DEBUGX:" + eid + ":" + "Query:" + query)
    query_job = client.query(query)

    if query_job.errors:
        print("CRITICAL: Error in executing query")
