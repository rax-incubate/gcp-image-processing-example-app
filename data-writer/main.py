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
        print(f"DEBUGX:" + eid + ":" + "BQ Dataset ID:" + bq_dataset_id)
        print(f"DEBUGX:" + eid + ":" + "BQ Table ID:" + bq_table_id)
        print(f"DEBUGX:" + eid + ":" + "Msg content:" + msg_content)

    client = bigquery.Client()

    json_data = json.loads(msg_content)

    chk_query = "SELECT bucket,filename FROM " + bq_dataset_id + "." + bq_table_id + " WHERE bucket='" + json_data['bucket'] + "' AND filename='" + json_data['file_name'] + "'"

    chk_query_job = client.query(chk_query)  
    chk_rows = chk_query_job.result()

    if chk_rows.total_rows == 0:
        sql =  list()
        sql.append("INSERT INTO " + bq_dataset_id + "." + bq_table_id)
        sql.append("(bucket, filename, syntax_text, sentiment_score, last_update)")
        sql.append("VALUES (")
        sql.append("'" + json_data['bucket'] + "', ")
        sql.append("'" + json_data['file_name'] + "', ")
        if "syntax_data" in json_data:
            sql.append("\"" + str(json_data['syntax_data']) + "\", ")
        else:
            sql.append("'" + "NULL" + "', ")
        if "sentiment_data" in json_data:
            sql.append("SAFE.PARSE_JSON('" + str(json_data['sentiment_data']) + "'), ")
        else:
            sql.append(" SAFE.PARSE_JSON('') , ")
        sql.append("CURRENT_DATETIME()")
        sql.append(")")
    else:
        if "syntax_data" in json_data:
            sql =  list()
            sql.append("UPDATE " + bq_dataset_id + "." + bq_table_id)
            sql.append(" SET ")
            sql.append("syntax_data='" + str(json_data['syntax_data']) + "',")
            sql.append("last_update=CURRENT_DATETIME()")
            sql.append(" WHERE bucket='" + json_data['bucket'] + "'")
            sql.append(" AND filename='" + json_data['file_name'] + "'")
        if "sentiment_data" in json_data:
            sql =  list()
            sql.append("UPDATE " + bq_dataset_id + "." + bq_table_id)
            sql.append(" SET ")
            sql.append("sentiment_score=SAFE.PARSE_JSON('" + str(json_data['sentiment_data']) + "'),")
            sql.append("last_update=CURRENT_DATETIME()")
            sql.append(" WHERE bucket='" + json_data['bucket'] + "'")
            sql.append(" AND filename='" + json_data['file_name'] + "'")

    query =  "".join(sql)

    if debugx:
         print(f"DEBUGX:" + eid + ":" + "Query:" + query)

    query_job = client.query(query) 

    # if debugx:
    #      print(f"DEBUGX:" + eid + ":" + "Query result:" + query_job)
