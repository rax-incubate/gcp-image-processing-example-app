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

    extract_syntax(msg_content, eid)


# extract word tokens and filter by parts of speech
def extract_syntax(msg_content, eid):
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

    response = client.analyze_syntax(
        request={"document": document, "encoding_type": encoding_type}
    )

    # Extract the categories we want
    useful_parts_of_speech = ["NOUN", "ADJ", "VERB"]

    # An optional filter of words can also be implemented here
    extracted_words = ""
    for token in response.tokens:
        text = token.text
        part_of_speech = token.part_of_speech
        if language_v1.PartOfSpeech.Tag(part_of_speech.tag).name in useful_parts_of_speech:
            if extracted_words == "":
                extracted_words = extracted_words + text.content
            else:
                extracted_words = extracted_words + " " + text.content

    if debugx:
        print(f"DEBUGX:{eid}: Extracted words: {extracted_words}")

    publish_text(json_data['bucket'], json_data['file_name'], extracted_words, eid)


# Publish the extracted words to pub sub
def publish_text(bucket_name: str, file_name: str, syntax_data, eid):
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
    data['syntax_data'] = syntax_data
    data['eid'] = eid

    json_data = json.dumps(data)
    data = json_data.encode("utf-8")
    if debugx:
        print(f"DEBUGX:" + eid + ":" + "Data sent:" + json_data)

    future = publisher.publish(topic_path, data)
    if debugx:
        print(f"DEBUGX::{eid}: {future.result()}")
