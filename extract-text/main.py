import functions_framework
import os
from google.cloud import storage
from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from google.cloud import pubsub_v1


@functions_framework.cloud_event
# receive new image events from GCS
def new_image_file(cloud_event):
    data = cloud_event.data

    event_id = cloud_event["id"]
    event_type = cloud_event["type"]

    bucket = data["bucket"]
    name = data["name"]
    metageneration = data["metageneration"]
    timeCreated = data["timeCreated"]
    updated = data["updated"]

    print(f"Debug: Event ID: {event_id}")
    print(f"Debug: Event type: {event_type}")
    print(f"Debug: Bucket: {bucket}")
    print(f"Debug: File: {name}")
    process_image(bucket, name)

# Get image content and extract text using document AI


def process_image(bucket_name: str, file_name: str):
    project_no = os.environ.get('PROJECT_NO')
    proc_location = os.environ.get('PROC_LOCATION')
    proc_id = os.environ.get('PROC_ID')

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    mime_type = "image/png"

    image_content = bucket.get_blob(file_name).download_as_bytes()

    opts = ClientOptions(api_endpoint=f"us-documentai.googleapis.com")

    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    proc_name = client.processor_path(project_no, proc_location, proc_id)

    print(f"Debug: Processor name: {proc_name}")

    raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)

    request = documentai.ProcessRequest(name=proc_name, raw_document=raw_document)

    result = client.process_document(request=request)

    extracted_text = result.document
    publish_text(bucket_name, file_name, extracted_text.text)


# Publish image metadata and extracted text to pub/sub


def publish_text(bucket_name: str, file_name: str, extracted_text):
    project_id = os.environ.get('PROJECT_ID')
    topic_id = os.environ.get('TOPIC_ID')

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    print(f"Debug: Topic path: {topic_path}")

    data_str = f"bucket:{bucket_name},name:{file_name},text:{extracted_text}"
    data = data_str.encode("utf-8")
    future = publisher.publish(topic_path, data)
    print(f"Debug: {future.result()}")
