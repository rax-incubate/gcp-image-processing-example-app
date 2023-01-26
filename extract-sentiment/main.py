import os
import base64
import json
import uuid
import functions_framework
from google.api_core.client_options import ClientOptions
from google.cloud import language_v1
from google.cloud import pubsub_v1


@functions_framework.cloud_event
# receive new text events from pub sub
def new_text(cloud_event):
    eid = uuid.uuid4().hex

    debugx = False
    if os.environ.get('DEBUGX') == "1":
        debugx = True

    msg_content = base64.b64decode(cloud_event.data["message"]["data"]).decode()

    if debugx:
        print(f"DEBUGX:" + eid + ":" + msg_content)

    extract_sentiment(msg_content, eid)


def extract_sentiment(msg_content, eid):
    debugx = False
    if os.environ.get('DEBUGX') == "1":
        debugx = True

    client = language_v1.LanguageServiceClient()
    type_ = language_v1.Document.Type.PLAIN_TEXT

    if debugx:
        print(f"DEBUGX:{eid}:pubsub data {msg_content}")

    json_data = json.loads(msg_content)

    language = "en"
    document = {"content": json_data['extracted_text'], "type_": type_, "language": language}

    encoding_type = language_v1.EncodingType.UTF8

    response = client.analyze_sentiment(
        request={"document": document, "encoding_type": encoding_type}
    )

    sentiment_score = response.document_sentiment.score
    sentiment_magnitude = response.document_sentiment.magnitude


    if debugx:
        print(f"DEBUGX:{eid}: Sentiment Score: {sentiment_score}")
        print(f"DEBUGX:{eid}: Sentiment Magnitude: {sentiment_magnitude}")

    publish_text(json_data['bucket'], json_data['file_name'], sentiment_score, sentiment_magnitude, eid)


# Clearly Positive*	"score": 0.8, "magnitude": 3.0
# Clearly Negative*	"score": -0.6, "magnitude": 4.0
# Neutral	"score": 0.1, "magnitude": 0.0
# Mixed	"score": 0.0, "magnitude": 4.0


# Publish the extracted words to pub sub
def publish_text(bucket_name: str, file_name: str, sentiment_score, sentiment_magnitude, eid):
    debugx = False
    if os.environ.get('DEBUGX') == "1":
        debugx = True

    project_id = os.environ.get('PROJECT_ID')
    topic_id = os.environ.get('TOPIC_ID')

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    if debugx:
        print(f"Debug:{eid}: Topic path: {topic_path}")
    data = {}
    data['bucket'] = bucket_name
    data['file_name'] = file_name
    data['sentiment_data'] = {} 
    data['sentiment_data']['score'] = sentiment_score
    data['sentiment_data']['magnitude'] = sentiment_magnitude

    json_data = json.dumps(data)
    data = json_data.encode("utf-8")
    if debugx:
        print(f"DEBUGX:" + eid + ":" + "Data sent:" + json_data)

    future = publisher.publish(topic_path, data)
    if debugx:
        print(f"DEBUGX::{eid}: {future.result()}")
