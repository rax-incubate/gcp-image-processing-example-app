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

    client = bigquery.Client()
    query = "SELECT DISTINCT filename, bucket FROM " + bq_dataset_id + "." + bq_table_id + " LIMIT 20"

    if search is not None:
        query = "SELECT DISTINCT filename, bucket FROM " + bq_dataset_id + "." + bq_table_id + " WHERE REGEXP_CONTAINS(syntax_text,r'(?i){}') LIMIT 20".format(search)

    if sentiment == "positive":
        query = "SELECT DISTINCT filename, bucket FROM " + bq_dataset_id + "." + bq_table_id + " WHERE sentiment_score >= 0.2 AND sentiment_magnitude >= 3.0 LIMIT 20"

    if sentiment == "negative":
        query = "SELECT DISTINCT filename, bucket FROM " + bq_dataset_id + "." + bq_table_id + " WHERE sentiment_score <= -0.2 AND sentiment_magnitude >= 3.0 LIMIT 20"

    if sentiment == "neutral":
        query = "SELECT DISTINCT filename, bucket FROM " + bq_dataset_id + "." + bq_table_id + " WHERE sentiment_score >= 0.0 AND sentiment_score <= 0.2 AND sentiment_magnitude <= 0.0 LIMIT 20"

    if debugx:
        print(f"DEBUGX:" + eid + ":Query:" + query)
    query_job = client.query(query)  # Make an API request.
    rows = query_job.result()  # Waits for query to finish

    html =  list()

    html.append("""
<!DOCTYPE html>
<html>
<body>
<table border="1">
<tbody>

""")
    if rows.total_rows == 0:
        html.append("<b>No results found !</b>")
    else:
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
            html.append("File:{}".format(row["filename"]))
            html.append("</td>\n")
            col_cnt = col_cnt + 1
        html.append("</tr>\n")
    html.append("""
</tbody>
</table>
</body>
</html>
""")
    return ("".join(html))
