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

    extract_entities(msg_content, eid)


# extract word tokens and filter by figures of speech
def extract_entities(msg_content, eid):
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

    response = client.analyze_entities(
        request={"document": document, "encoding_type": encoding_type}
    )
    entity_data_arr = []
    for entity in response.entities:
        if debugx:
            print(f"DEBUGX:{eid}: Representative entity:{entity.name}, Entity type:{language_v1.Entity.Type(entity.type_).name},Salience score:{entity.salience}")
        entity_data = {}
        entity_data['entity_name'] = entity.name
        entity_data['entity_type'] = language_v1.Entity.Type(entity.type_).name
        entity_data['entity_score'] = entity.salience
        entity_data_arr.append(entity_data)

    publish_text(json_data['bucket'], json_data['file_name'], entity_data_arr, eid)

# Publish the entity data to pub sub
def publish_text(bucket_name: str, file_name: str, entity_data_arr, eid):
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
    data['entity_data'] = entity_data_arr

    json_data = json.dumps(data)
    data = json_data.encode("utf-8")
    if debugx:
        print(f"DEBUGX:" + eid + ":" + "Data sent:" + json_data)

    future = publisher.publish(topic_path, data)
    if debugx:
        print(f"DEBUGX::{eid}: {future.result()}")