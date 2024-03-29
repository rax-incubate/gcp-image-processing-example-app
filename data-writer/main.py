import os
import base64
import json
import uuid
import time
import functions_framework
from google.api_core.client_options import ClientOptions
from google.cloud import bigquery
from random import randrange


@functions_framework.cloud_event
# receive new text events from pub sub
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

    sql = list()
    data_entry_type = ""
    if "syntax_data" in json_data:
        sql = list()
        data_entry_type = "syntax"
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
        data_entry_type = "sentiment"
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

    if "entity_data" in json_data:
        sql = list()
        data_entry_type = "entity"
        sql.append("INSERT INTO " + bq_dataset_id + "." + bq_table_id)
        sql.append("(bucket, filename, entities,last_update)")
        sql.append("VALUES (")
        sql.append("'" + json_data['bucket'] + "', ")
        sql.append("'" + json_data['file_name'] + "', ")
        sql.append("[")

        entities = json_data['entity_data']
        if debugx:
            print(f"DEBUGX:{eid}:entities:{entities}")
        first_ent = True
        for ent in entities:
            if debugx:
                print(f"DEBUGX:{eid}:ent:{ent}")

            if ent['entity_type'] != 'NUMBER' and ent['entity_score'] != '0.0':
                if not first_ent:
                    sql.append(",")
                sql.append("('" + ent['entity_name'].replace("'", "") + "', ")
                sql.append("'" + ent['entity_type'] + "', ")
                sql.append("CAST(" + str(ent['entity_score']) + " AS NUMERIC))")
                first_ent = False
        sql.append('], CURRENT_DATETIME()')
        sql.append(')')

    if "face_label_data" in json_data:
        sql = list()
        data_entry_type = "face_labels"
        sql.append("INSERT INTO " + bq_dataset_id + "." + bq_table_id)
        sql.append("(bucket, filename, face_labels,last_update)")
        sql.append("VALUES (")
        sql.append("'" + json_data['bucket'] + "', ")
        sql.append("'" + json_data['file_name'] + "', ")
        sql.append("[")

        face_labels = json_data['face_label_data']
        if debugx:
            print(f"DEBUGX:{eid}:face_labels:{face_labels}")
        first_face = True
        for face in face_labels:
            if debugx:
                print(f"DEBUGX:{eid}:face:{face}")

            if not first_face:
                sql.append(",")
            sql.append("('" + face['description'].replace("'", "") + "', ")
            sql.append("CAST(" + str(face['score']) + " AS NUMERIC), ")
            sql.append("CAST(" + str(face['topicality']) + " AS NUMERIC))")
            first_face = False
        sql.append('], CURRENT_DATETIME()')
        sql.append(')')
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
            print(f"DEBUGX:{eid}:bucket={json_data['bucket']},filename={json_data['file_name']},type={data_entry_type},Result=Max retries reached")
        else:
            print(f"DEBUGX:{eid}:bucket={json_data['bucket']},filename={json_data['file_name']},type={data_entry_type},Result=Data entry succeeded")

    else:
        print(f"DEBUGX:" + eid + ":" + "Empty Query")
