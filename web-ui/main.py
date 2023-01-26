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

    client = bigquery.Client()
    if search is None:
        query = "SELECT bucket, filename, syntax_text, sentiment_score FROM " + bq_dataset_id + "." + bq_table_id + " LIMIT 20"
    else:
        query = "SELECT bucket, filename, syntax_text, sentiment_score FROM " + bq_dataset_id + "." + bq_table_id + " WHERE REGEXP_CONTAINS(syntax_text,r'(?i){}') LIMIT 20".format(search)

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
        html.append("<b>No results found</b>")
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
            html.append("<img src=https://storage.googleapis.com/{}/{}>\n".format(row["bucket"], row["filename"]))
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
