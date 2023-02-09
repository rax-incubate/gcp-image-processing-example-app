import functions_framework
import os
import json
import uuid
import time
from google.cloud import storage
from google.api_core.client_options import ClientOptions
from google.cloud import bigquery
from random import randrange


@functions_framework.cloud_event
# receive delete image events from GCS
def new_text(cloud_event):
    debugx = False
    if os.environ.get('DEBUGX') == "1":
        debugx = True

    msg_content = base64.b64decode(cloud_event.data["message"]["data"]).decode()
    json_data = json.loads(msg_content)

    if "eid" in json_data:
        eid = json_data['eid']
    else:
        eid = uuid.uuid4().hex

    if debugx:
        print(f"DEBUGX:" + eid + ":" + msg_content)
    delete_data(bucket, filename, eid)


# Delete data in BQ
def delete_data(bucket, filename, eid):
    debugx = False
    if os.environ.get('DEBUGX') == "1":
        debugx = True

    project_id = os.environ.get('PROJECT_ID')
    bq_dataset_id = os.environ.get('BQ_DATASET_ID')
    bq_table_id = os.environ.get('BQ_TABLE_ID')

    if debugx:
        print(f"DEBUGX:{eid}:BQ Dataset:{bq_dataset_id},Table:{bq_table_id},Bucket:{bucket},File:{filename}")

    client = bigquery.Client()

    sql = list()
    data_entry_type = "delete"
    sql.append("DELETE FROM " + bq_dataset_id + "." + bq_table_id)
    sql.append(" WHERE bucket='" + bucket + "'")
    sql.append(" AND filename='" + filename + "'")
    query = "".join(sql)

    if debugx:
        print(f"DEBUGX:" + eid + ":" + "Query:" + query)

    if query:
        query_job = client.query(query)
        if query_job.errors:
            print(f"DEBUGX:" + eid + ":" + "Error in executing query:")

            retries = 10
            while retries > 0 and query_job.errors:
                rand_sleep = (10/retries) + randrange(5)
                print(f"DEBUGX:" + eid + ":" + "Sleeping " + str(rand_sleep) + " seconds and retrying query " + str(retries))
                time.sleep(rand_sleep)
                query_job = client.query(query)
                retries = retries - 1
        if query_job.errors:
            print(f"DEBUGX:{eid}:bucket={bucket},filename={filename},type={data_entry_type},Result=Max retries reached")
        else:
            print(f"DEBUGX:{eid}:bucket={bucket},filename={filename},type={data_entry_type},Result=Data entry succeeded")

    else:
        print(f"DEBUGX:" + eid + ":" + "Empty Query")
