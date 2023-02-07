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

        chk_jobs_qry = f"SELECT count(job_id) as job_cnt FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT WHERE state != 'DONE' AND project_id = '{project_id}' AND REGEXP_CONTAINS(query, 'DELETE FROM calvin.calvin_text')"
        chk_jobs_qry_job = client.query(chk_jobs_qry)
        chk_jobs_rows = chk_jobs_qry_job.result() 
        for chk_jobs_row in chk_jobs_rows:
            pending_cnt = chk_jobs_row['job_cnt']

        retries = 15
        while pending_cnt >= 19 and retries > 0
            print(f"DEBUGX:" + eid + ":" + " Queue has over " + str(pending_cnt) " querus, sleeping 2 seconds" )
            time.sleep(2)
            chk_jobs_qry_job = client.query(chk_jobs_qry)
            chk_jobs_rows = chk_jobs_qry_job.result() 
            for chk_jobs_row in chk_jobs_rows:
                pending_cnt = chk_jobs_row['job_cnt']
            retries = retries - 1

        if query_job.errors:
            print(f"DEBUGX:" + eid + ":" + "Error in executing query:")

            while retries > 0 and query_job.errors:
                rand_sleep = (10/retries) + randrange(5)
                query_job = client.query(query)
                retries = retries - 1
        if query_job.errors:
            print(f"DEBUGX:{eid}:bucket={bucket},filename={filename},type={data_entry_type},Result=Max retries reached")
        else:
            print(f"DEBUGX:{eid}:bucket={bucket},filename={filename},type={data_entry_type},Result=Data entry succeeded")

    else:
        print(f"DEBUGX:" + eid + ":" + "Empty Query")



    #     if query_job.errors:
    #         print(f"DEBUGX:" + eid + ":" + "Error in executing query:")

    #         retries = 10
    #         while retries > 0 and query_job.errors:
    #             rand_sleep = (10/retries) + randrange(5)
    #             print(f"DEBUGX:" + eid + ":" + "Sleeping " + str(rand_sleep) + " seconds and retrying query " + str(retries) )
    #             time.sleep(rand_sleep)
    #             query_job = client.query(query)
    #             retries = retries - 1
    #     if query_job.errors:
    #         print(f"DEBUGX:{eid}:bucket={bucket},filename={filename},type={data_entry_type},Result=Max retries reached")
    #     else:
    #         print(f"DEBUGX:{eid}:bucket={bucket},filename={filename},type={data_entry_type},Result=Data entry succeeded")

    # else:
    #     print(f"DEBUGX:" + eid + ":" + "Empty Query")
