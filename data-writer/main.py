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

    if debugx:
        print(f"DEBUGX:" + eid + ":" + msg_content)

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
        print(f"DEBUGX:" + eid + ":" + "BQ Dataset ID:" + bq_dataset_id)
        print(f"DEBUGX:" + eid + ":" + "BQ Table ID:" + bq_table_id)
        print(f"DEBUGX:" + eid + ":" + "Msg content:" + msg_content)

    client = bigquery.Client()

    json_data = json.loads(msg_content)
    
    sql =  list()
    sql.append("INSERT INTO " + bq_dataset_id + "." + bq_table_id)
    sql.append("(bucket, filename, syntax_text, semantic_text, last_update)")
    sql.append("VALUES (")
    sql.append("'" + json_data['bucket'] + "', ")
    sql.append("'" + json_data['file_name'] + "', ")
    if "syntax_data" in json_data:
        sql.append("'" + json_data['syntax_data'] + "', ")
    else:
        sql.append("'" + "NULL" + "', ")
    if "semantic_data" in json_data:
        sql.append("'" + json_data['semantic_data'] + "', ")
    else:
        sql.append("'" + "NULL" + "', ")
    sql.append("CURRENT_DATETIME()")
    sql.append(")")
    query =  "".join(sql)

    if debugx:
         print(f"DEBUGX:" + eid + ":" + "Query:" + query)


    query_job = client.query(query) 
    # if debugx:
    #      print(f"DEBUGX:" + eid + ":" + "Query result:" + query_job)
