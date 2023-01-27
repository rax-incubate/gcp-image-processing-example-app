# Summary

This tutorial focuses on the use GCP's AI services to do following 

 - Extract Text from a large array of comic strips. We will focus on Calvin and Hobbes (https://en.wikipedia.org/wiki/Calvin_and_Hobbes) for this example but this could be any comic strip.

 - Analyse syntax of the extracted text. In case of syntax, we mean words and use the automated parts of speech extraction in GCP's natural language processing

 - Analyse sentiment of the extracted text using GCP's natural language processing 

 - Build a basic but working web-interface to test and demo the working of these examples

 - Other areas of interest which maybe developed in the future
  - Extract entities in text
  - Detect faces in the images

We are also imposing some self-imposed technological constraints to test the powers of the GCP serverless platforms. 

 - All code will be in implemented in Cloud Functions. We will use version 2 which uses Cloud Run under the hood.  Technically, that means, we can package this code into containers and run it on Cloud Run.

 - Keep the code simple and use Cloud Functions for single tasks. This also introduces a micro-services like design. 

 - Pub/Sub will provide the message bus for the distributed processing 

 - Cloud Functions will also service any web-frontend

 - File storage will be Google Cloud Storage (GCS)

 - Relational data storage will be done using Big Query. We can use Cloud SQL or Cloud Spanner but they were discarded in order to reduce cost. 


Here's the design we will implement

!(design.png)

At an high level, 
  * Image data arrives in a GCP bucket
  * Event processing is triggered to extract text from the image 
  * Extracted text is sent to NLP for syntax processing
  * Extracted text is sent to NLP for sentiment processing
  * All information are stored in a database
  * A web based frontend shows the results and allows demos

# Implementation

## Setup the environment

  * Clone the repo
    ```
    git clone 
    ```

  * Authenticate to Google and make sure you have access to a Project

  * Setup your env variables
    ```
    PROJECT_ID=$(gcloud config get-value project)
    PROJECT_NUMBER=$(gcloud projects list --filter="project_id:$PROJECT_ID" --format='value(project_number)')
    CLONE_FOLDER="<your folder>"
    ```

## Storage Setup

  * Create bucket for the images
    ```
    gsutil mb -l us-east1 gs://calvin-images`
    ```

## Create pub sub topics

  * Create pub/sub topic
    ```
    gcloud pubsub topics create calvin-text-extract \
     --message-retention-duration 3d \
     --project $PROJECT_ID 
    ```

    * Create pub/sub subscription for debug and demo purposes
    ```
     gcloud pubsub subscriptions create extracted-text \
     --topic calvin-text-extract \
     --retain-acked-messages \
     --project $PROJECT_ID 
    ```

  * Create pub/sub topic
    ```
    gcloud pubsub topics create calvin-data-writer \
     --message-retention-duration 3d \
     --project $PROJECT_ID 
    ```

  * Create pub/sub subscription for debug/demo purposes
    ```
    gcloud pubsub subscriptions create data-writer \
     --topic calvin-data-writer \
     --retain-acked-messages \
     --project $PROJECT_ID 
    ```

## Create BQ dataset and table

  * Create dataset
    ```
    bq  --project_id $PROJECT_ID  mk calvin
    ```

  * Create table
    ```
    bq --project_id $PROJECT_ID query --use_legacy_sql=false \
    'CREATE TABLE calvin.calvin_text ( 
      bucket STRING(256), 
      filename STRING(256), 
      syntax_text STRING(1024) ,
      sentiment_score NUMERIC ,
      sentiment_magnitude NUMERIC ,
      last_update DATETIME,
      );'
    ```

## Extract text from images

  * Grant IAM access to the KMS service account
    ```
    SERVICE_ACCOUNT=$(gsutil kms serviceaccount -p $PROJECT_NUMBER)

    gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member serviceAccount:$SERVICE_ACCOUNT \
    --role roles/pubsub.publisher
    ```

  * Update env.yaml with the right values

  * Deploy the extract-text function
    ```
    cd $CLONE_FOLDER/extract-text
    gcloud functions deploy extract-text \
     --gen2 \
     --runtime=python310 \
     --region=us-east1 \
     --source=. \
     --entry-point=new_image_file \
     --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
     --trigger-event-filters="bucket=calvin-images"  \
     --env-vars-file env.yaml \
     --project $PROJECT_ID
    ```

  * Test with a sample image 
    ```
    gsutil cp sample.png gs://calvin-images/sample.png
    ```

  * Review logs for function execution
    ```
    gcloud beta functions logs read extract-text \
     --gen2 \
     --limit=100 \
     --region=us-east1 \
     --project $PROJECT_ID
    ```

  * Check pub/sub for topic update
    ```
    gcloud pubsub subscriptions pull extracted-text --project $PROJECT_ID 
    ```

## Extract syntax

  * Update env.yaml with the right values

  * Deploy the extract-syntax function
    ```
    cd $CLONE_FOLDER/extract-syntax
    gcloud functions deploy extract-syntax \
     --gen2 \
     --runtime=python310 \
     --region=us-east1 \
     --source=. \
     --entry-point=new_text \
     --trigger-topic=calvin-text-extract  \
     --env-vars-file env.yaml \
     --retry \
     --project $PROJECT_ID
    ```

  * Review logs for function execution
    ```
    gcloud beta functions logs read extract-syntax \
     --gen2 \
     --limit=100 \
     --region=us-east1 \
     --project $PROJECT_ID
    ```

## Extract sentiment

  * Update env.yaml with the right values

  * Deploy the extract-sentiment function
    ```
    cd $CLONE_FOLDER/extract-sentiment
    gcloud functions deploy extract-sentiment \
     --gen2 \
     --runtime=python310 \
     --region=us-east1 \
     --source=. \
     --entry-point=new_text \
     --trigger-topic=calvin-text-extract \
     --env-vars-file env.yaml \
     --retry \
     --project $PROJECT_ID
    ```

  * Review logs for function execution
    ```
    gcloud beta functions logs read extract-sentiment \
     --gen2 \
     --limit=100 \
     --region=us-east1 \
     --project $PROJECT_ID
    ```
  
## Data writer 

  * Update env.yaml with the right values

  * Deploy the data-writer function
    ```
    cd $CLONE_FOLDER/data-writer
    gcloud functions deploy data-writer \
     --gen2 \
     --runtime=python310 \
     --region=us-east1 \
     --source=. \
     --entry-point=new_text \
     --trigger-topic=calvin-data-writer  \
     --env-vars-file env.yaml \
     --retry \
     --project $PROJECT_ID
    ```

  * Review logs for function execution
    ```
    gcloud beta functions logs read data-writer \
     --gen2 \
     --limit=100 \
     --region=us-east1 \
     --project $PROJECT_ID
    ```


## Process image delete eventa

  * Update env.yaml with the right values

  * Deploy the extract-text function
    ```
    cd $CLONE_FOLDER/data-deleter
    gcloud functions deploy data-deleter \
     --gen2 \
     --runtime=python310 \
     --region=us-east1 \
     --source=. \
     --entry-point=delete_image_data \
     --trigger-event-filters="type=google.cloud.storage.object.v1.deleted" \
     --trigger-event-filters="bucket=calvin-images"  \
     --env-vars-file env.yaml \
     --project $PROJECT_ID
    ```

  * Review logs for function execution
    ```
    gcloud beta functions logs read extract-text \
     --gen2 \
     --limit=100 \
     --region=us-east1 \
     --project $PROJECT_ID
    ```

  * Check pub/sub for topic update
    ```
    gcloud pubsub subscriptions pull extracted-text --project $PROJECT_ID 

    ```

## Web frontend

  * Deploy the web-ui function
    ```
    cd $CLONE_FOLDER/web-ui
    gcloud functions deploy web-ui \
     --gen2 \
     --allow-unauthenticated \
     --runtime=python310 \
     --region=us-east1 \
     --source=. \
     --entry-point=new_request \
     --trigger-http \
     --env-vars-file env.yaml \
     --project $PROJECT_ID
    ```

  
## Metrics and monitors

See cloud-monitoring-dashboard.json for metrics dashboard

Log query:-

```
(resource.type = "cloud_run_revision"
resource.labels.service_name = "extract-text"
resource.labels.location = "us-east1") OR 
(resource.type = "cloud_run_revision"
resource.labels.service_name = "extract-syntax"
resource.labels.location = "us-east1") OR 
(resource.type = "cloud_run_revision"
resource.labels.service_name = "extract-sentiment"
resource.labels.location = "us-east1")  OR 
(resource.type = "cloud_run_revision"
resource.labels.service_name = "data-writer"
resource.labels.location = "us-east1")  OR 
(resource.type = "cloud_run_revision"
resource.labels.service_name = "data-deleter"
resource.labels.location = "us-east1")  OR 
(resource.type = "cloud_run_revision"
resource.labels.service_name = "web-ui"
resource.labels.location = "us-east1")
 severity>=DEFAULT
```

## Test with lots of data
Not Implemented