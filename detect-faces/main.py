import functions_framework
import os
import json
import uuid
from google.api_core.client_options import ClientOptions
from google.cloud import vision
from google.cloud import pubsub_v1


@functions_framework.cloud_event
# receive new image events from GCS
def new_image_file(cloud_event):
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

    process_image(bucket, filename, eid)


# Get image content and extract text using document AI
def process_image(bucket_name: str, filename: str, eid: str):
    debugx = False
    if os.environ.get('DEBUGX') == "1":
        debugx = True

    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = "gs://" + bucket_name + "/" + filename

    response = client.label_detection(image=image)
    labels = response.label_annotations
    face_label_data_arr = []
    for label in labels:
        label_data = {}
        label_data['description'] = label.description
        label_data['score'] = label.score
        label_data['topicality'] = label.topicality
        face_label_data_arr.append(label_data)
        if debugx:
            print(f"DEBUGX:{eid}: label data: {label_data}")


    publish_text(bucket_name, filename, face_label_data_arr,  eid)

# Publish the face labels to pub sub
def publish_text(bucket_name: str, file_name: str,face_label_data,  eid):
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
    data['face_label_data'] = face_label_data
    data['eid'] = eid

    json_data = json.dumps(data)
    data = json_data.encode("utf-8")
    if debugx:
        print(f"DEBUGX:" + eid + ":" + "Data sent:" + json_data)

    future = publisher.publish(topic_path, data)
    if debugx:
        print(f"DEBUGX::{eid}: {future.result()}")