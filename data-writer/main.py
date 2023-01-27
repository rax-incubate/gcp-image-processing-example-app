import os
import base64
import json
import uuid
import functions_framework
from google.api_core.client_options import ClientOptions
from google.cloud import bigquery


@functions_framework.cloud_event
# receive new image events from GCS
def new_text(cloud_event):
    eid = uuid.uuid4().hex

    debugx = False
    if os.environ.get('DEBUGX') == "1":
        debugx = True

    msg_content = base64.b64decode(cloud_event.data["message"]["data"]).decode()

    write_data(msg_content, eid)


# Write data to BQ
def write_data(msg_content, eid):
    debugx = False
    if os.environ.get('DEBUGX') == "1":
        debugx = True

    project_no = os.environ.get('PROJECT_NO')
    bq_dataset_id = os.environ.get('BQ_DATASET_ID')
    bq_table_id = os.environ.get('BQ_TABLE_ID')

    if debugx:
        print(f"DEBUGX:{eid}:BQ Dataset:{bq_dataset_id},Table:{bq_table_id},Msg content:{msg_content}")

    client = bigquery.Client()

    json_data = json.loads(msg_content)

    if "syntax_data" in json_data:
        sql = list()
        sql.append("INSERT INTO " + bq_dataset_id + "." + bq_table_id)
        sql.append("(bucket, filename, syntax_text,last_update)")
        sql.append("VALUES (")
        sql.append("'" + json_data['bucket'] + "', ")
        sql.append("'" + json_data['file_name'] + "', ")
        sql.append("\"" + str(json_data['syntax_data']) + "\", ")
        sql.append("CURRENT_DATETIME()")
        sql.append(")")

    if "sentiment_score" in json_data and "sentiment_magnitude" in json_data:
        sql = list()
        sql.append("INSERT INTO " + bq_dataset_id + "." + bq_table_id)
        sql.append("(bucket, filename, sentiment_score, sentiment_magnitude, last_update)")
        sql.append("VALUES (")
        sql.append("'")
        sql.append(json_data['bucket'])
        sql.append("', ")
        sql.append("'")
        sql.append(json_data['file_name'])
        sql.append("', ")
        sql.append(str(json_data['sentiment_score']))
        sql.append(", ")
        sql.append(str(json_data['sentiment_magnitude']))
        sql.append(", ")
        sql.append("CURRENT_DATETIME()")
        sql.append(")")

    query = "".join(sql)

    if debugx:
        print(f"DEBUGX:" + eid + ":" + "Query:" + query)

    query_job = client.query(query)

    if query_job.errors:
        print("CRITICAL: Error in executing query")
