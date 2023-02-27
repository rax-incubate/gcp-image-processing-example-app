import functions_framework
from google.cloud import bigquery
import json
import uuid
import os
import base64


@functions_framework.http
def new_request(request):

    eid = uuid.uuid4().hex
    debugx = False
    if os.environ.get('DEBUGX') == "1":
        debugx = True

    request_json = request.get_json(silent=True)
    request_args = request.args

    bq_dataset_id = os.environ.get('BQ_DATASET_ID')
    bq_table_id = os.environ.get('BQ_TABLE_ID')

    if request_json and 'bucket' in request_json:
        bucket = request_json['bucket']
    elif request_args and 'bucket' in request_args:
        bucket = request_args['bucket']
    else:
        bucket = None

    if request_json and 'search' in request_json:
        search = request_json['search']
    elif request_args and 'search' in request_args:
        search = request_args['search']
    else:
        search = None

    if debugx:
        print(f"DEBUGX:" + eid + ":Search:" + str(search or ''))

    if request_json and 'sentiment' in request_json:
        sentiment = request_json['sentiment']
    elif request_args and 'sentiment' in request_args:
        sentiment = request_args['sentiment']
    else:
        sentiment = None

    if debugx:
        print(f"DEBUGX:" + eid + ":sentiment:" + str(sentiment or ''))

    if request_json and 'entity_name' in request_json:
        entity_name = request_json['entity_name']
    elif request_args and 'entity_name' in request_args:
        entity_name = request_args['entity_name']
    else:
        entity_name = None

    if debugx:
        print(f"DEBUGX:" + eid + ":entity_name:" + str(entity_name or ''))

    if request_json and 'entity_type' in request_json:
        entity_type = request_json['entity_type']
    elif request_args and 'entity_type' in request_args:
        entity_type = request_args['entity_type']
    else:
        entity_type = None

    if debugx:
        print(f"DEBUGX:" + eid + ":entity_type:" + str(entity_type or ''))

    if request_json and 'face_desc' in request_json:
        face_desc = request_json['face_desc']
    elif request_args and 'face_desc' in request_args:
        face_desc = request_args['face_desc']
    else:
        face_desc = None

    if debugx:
        print(f"DEBUGX:" + eid + ":entity_type:" + str(entity_type or ''))

    client = bigquery.Client()
    html = list()

    many_buckets_found = False
    if bucket is None:
        uniq_buckets = f"SELECT DISTINCT bucket FROM {bq_dataset_id}.{bq_table_id}" 
        if debugx:
            print(f"DEBUGX:" + eid + ":Unique buckets query:" + uniq_buckets)
        uniq_buckets_query_job = client.query(uniq_buckets)
        uniq_buckets_query_rows = uniq_buckets_query_job.result()
        if debugx:
            print(f"DEBUGX:" + eid + ": Found " + str(uniq_buckets_query_rows.total_rows) + " buckets ")
        if uniq_buckets_query_rows.total_rows > 1:
            many_buckets_found = True
            html.append(f"<b>Select image bucket:</b>")
            html.append("<br>")
            for uniq_buckets_query_row in uniq_buckets_query_rows:
                html.append("<a href={}?bucket={}>{}</a>".format(request.base_url, uniq_buckets_query_row["bucket"], uniq_buckets_query_row["bucket"]))
                html.append("<br>")
        else:
            for uniq_buckets_query_row in uniq_buckets_query_rows:
                bucket = uniq_buckets_query_row["bucket"]

    if bucket is None and not many_buckets_found:
        html.append("<b>No results found.</b>")
    else:
        if not many_buckets_found:
            query = f"SELECT DISTINCT filename, bucket FROM {bq_dataset_id}.{bq_table_id} WHERE bucket='{bucket}' LIMIT 100"

            if search is not None:
                query = f"SELECT DISTINCT filename, bucket FROM {bq_dataset_id}.{bq_table_id} WHERE bucket='{bucket}' AND REGEXP_CONTAINS(syntax_text,r'(?i){search}') LIMIT 100"

            if face_desc is not None:
                query = f"SELECT DISTINCT filename, bucket FROM {bq_dataset_id}.{bq_table_id}, UNNEST(face_labels) f WHERE bucket='{bucket}' AND REGEXP_CONTAINS(f.description ,r'(?i){face_desc}') LIMIT 100"

            if entity_name is not None:
                query = f"SELECT DISTINCT filename, bucket FROM {bq_dataset_id}.{bq_table_id}, UNNEST(entities) e WHERE bucket='{bucket}' AND REGEXP_CONTAINS(e.name ,r'(?i){entity_name}') LIMIT 100"

            if entity_type is not None:
                query = f"SELECT DISTINCT filename, bucket FROM {bq_dataset_id}.{bq_table_id}, UNNEST(entities) e WHERE bucket='{bucket}' AND  REGEXP_CONTAINS(e.type ,r'(?i){entity_type}') LIMIT 100"

            if sentiment == "positive":
                query = f"SELECT DISTINCT filename, bucket FROM {bq_dataset_id}.{bq_table_id} WHERE bucket='{bucket}' AND  sentiment_score >= 0.1 AND sentiment_magnitude >= 2.0 LIMIT 100"

            if sentiment == "negative":
                query = f"SELECT DISTINCT filename, bucket FROM {bq_dataset_id}.{bq_table_id} WHERE bucket='{bucket}' AND sentiment_score <= -0.1 AND sentiment_magnitude >= 3.0 LIMIT 100"

            if sentiment == "neutral":
                query = f"SELECT DISTINCT filename, bucket FROM {bq_dataset_id}.{bq_table_id} WHERE bucket='{bucket}' AND sentiment_score >= -0.1 AND sentiment_score <= 0.1  LIMIT 100"

            if debugx:
                print(f"DEBUGX:" + eid + ":Query:" + query)


            html.append("""
        <!DOCTYPE html>
        <html>
        <body>
        """)

            html.append("Sentiment:")
            html.append("<a href={}?sentiment=positive>positive</a> | ".format(request.base_url))
            html.append("<a href={}?sentiment=negative>negative</a> | ".format(request.base_url))
            html.append("<a href={}?sentiment=neutral>neutral</a> | ".format(request.base_url))
            html.append("<br>")

            ent_type_filter_query = f"SELECT e.type,count(e.type) as e_cnt FROM {bq_dataset_id}.{bq_table_id} , UNNEST(entities) e WHERE bucket='{bucket}' AND e.type != 'OTHER' GROUP by e.type ORDER by e_cnt DESC LIMIT 10"
            if debugx:
                print(f"DEBUGX:" + eid + ":Entity type filter query:" + ent_type_filter_query)
            ent_type_filter_query_job = client.query(ent_type_filter_query)
            ent_type_filter_query_rows = ent_type_filter_query_job.result()
            html.append("Entity type (top 10):")
            for ent_type_filter_query_row in ent_type_filter_query_rows:
                html.append("<a href={}?bucket={}&entity_type={}>{}</a> | ".format(request.base_url, bucket, ent_type_filter_query_row["type"], ent_type_filter_query_row["type"]))
            html.append("<br>")

            ent_name_filter_query = f"SELECT e.name,count(e.name) as e_cnt FROM {bq_dataset_id}.{bq_table_id} , UNNEST(entities) e WHERE bucket='{bucket}' GROUP by e.name ORDER by e_cnt DESC LIMIT 10"
            if debugx:
                print(f"DEBUGX:" + eid + ":Entity name filter query:" + ent_name_filter_query)
            ent_name_filter_query_job = client.query(ent_name_filter_query)
            ent_name_filter_query_rows = ent_name_filter_query_job.result()
            html.append("Entity name (top 10):")
            for ent_name_filter_query_row in ent_name_filter_query_rows:
                html.append("<a href={}?bucket={}&entity_name={}>{}</a> | ".format(request.base_url, bucket, ent_name_filter_query_row["name"], ent_name_filter_query_row["name"]))
            html.append("<br>")

            face_label_filter_query = f"SELECT f.description,count(f.description) as f_cnt FROM {bq_dataset_id}.{bq_table_id} , UNNEST(face_labels) f WHERE bucket='{bucket}' GROUP by f.description ORDER by f_cnt DESC LIMIT 10"
            if debugx:
                print(f"DEBUGX:" + eid + ":Face label filter query:" + face_label_filter_query)
            face_label_filter_query_job = client.query(face_label_filter_query)
            face_label_filter_query_rows = face_label_filter_query_job.result()
            html.append("Face labels (Top 10):")
            for face_label_filter_query_row in face_label_filter_query_rows:
                html.append("<a href={}?bucket={}&face_desc={}>{}</a> | ".format(request.base_url, bucket, face_label_filter_query_row["description"], face_label_filter_query_row["description"]))
            html.append("<br>")

            html.append("""
        <table border="1">
        <tbody>
        """)
            query_job = client.query(query)
            rows = query_job.result()
            if rows.total_rows == 0:
                html.append("<b>No results found.</b>")
            else:
                html.append(f"<b>Showing {rows.total_rows} results.</b>")
                col_cnt = 0
                first_row = True
                for row in rows:
                    if col_cnt % 3 == 0:
                        if first_row:
                            html.append("<tr>\n")
                            first_row = False
                        else:
                            html.append("</tr>\n")
                            html.append("<tr>\n")
                        col_cnt = 0
                    html.append("<td>\n")
                    html.append("<img src=https://storage.googleapis.com/{}/{} alt={}>\n".format(row["bucket"], row["filename"], row["filename"]))
                    html.append("</td>\n")
                    html.append("<td bgcolor=grey>&nbsp;&nbsp;&nbsp;</td>\n")
                    col_cnt = col_cnt + 1
                html.append("</tr>\n")

    html.append("""
</tbody>
</table>
</body>
</html>
""")
    return ("".join(html))
