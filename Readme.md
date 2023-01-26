# Common

* Setup your env variables
    ```
    PROJECT_ID=$(gcloud config get-value project)
    PROJECT_NUMBER=$(gcloud projects list --filter="project_id:$PROJECT_ID" --format='value(project_number)')
    CLONE_FOLDER="/Users/sriram.rajan/data/rack/git/RSS-Engineering/calvin"
    ```
# GCS Setup

  `* Create bucket for the images
    ```
    gsutil mb -l us-east1 gs://calvin-images`
    ```
`
# Create pub sub topics

* Create pub/sub topic
    ```
    gcloud pubsub topics create calvin-text-extract \
     --message-retention-duration 3d \
     --project $PROJECT_ID 
    ```

* Create pub/sub subscription for debug purposes
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

* Create pub/sub subscription for debug purposes
    ```
    gcloud pubsub subscriptions create data-writer \
     --topic calvin-data-writer \
     --retain-acked-messages \
     --project $PROJECT_ID 
    ```

# Create BQ dataset and table

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
      semantic_text STRING(1024) ,
      last_update DATETIME,
      );'
    ```

# Extract text from images

* Grant IAM access
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

# Extract syntax

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

# Data writer 

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

# Setup Load balancer

 * Get an IP
    ```
    gcloud compute addresses create calvin-ip \
      --network-tier=PREMIUM \
      --ip-version=IPV4 \
      --global \
      --project $PROJECT_ID 
    ```

 * Record the IP
    ```
    gcloud compute addresses describe calvin-ip \
     --format="get(address)" \
     --global \
     --project $PROJECT_ID 
    ```

 * Create a SSL cert
    ```
    gcloud compute ssl-certificates create calvinhobbs-org \
     --description=Calvin \
     --domains=calvinhobbs.org \
     --global \
     --project $PROJECT_ID 
    ```

 * Create a NEG

    ```
   gcloud compute network-endpoint-groups create calvin \
    --region=us-east1 \
    --network-endpoint-type=serverless  \
    --cloud-function-url-mask="calvinhobbs.org/<function>" \
    --project $PROJECT_ID 
    ```
    * Delete command
      ```
      gcloud compute network-endpoint-groups delete calvin \
       --region=us-east1 \
       --project $PROJECT_ID
      ``` 

 * Create a backend

  ```
   gcloud compute backend-services create calvin \
    --load-balancing-scheme=EXTERNAL \
    --global \
    --project $PROJECT_ID 
  ```

    * Delete command
      ```
      gcloud compute backend-services delete calvin \
       --global \
       --project $PROJECT_ID 
      ```

 * Add the serverless NEG as a backend to the backend service:

  ```
   gcloud compute backend-services add-backend calvin \
    --global \
    --network-endpoint-group=calvin \
    --network-endpoint-group-region=us-east1 \
    --project $PROJECT_ID 
  ```

 * Create a URL map to route incoming requests to the backend service:
  ```
   gcloud compute url-maps create calvin \
    --default-service calvin \
    --project $PROJECT_ID 
  ```
    * Delete command
      ```
      gcloud compute url-maps delete calvin \
       --project $PROJECT_ID 
      ```

 * Create an HTTPS target proxy. The proxy is the portion of the load balancer that holds the SSL certificate for HTTPS Load Balancing, so you also load your certificate in this step.

  ```
   gcloud compute target-https-proxies create calvin \
    --ssl-certificates=calvinhobbs-org \
    --url-map=calvin \
    --project $PROJECT_ID 
  ```

    * Delete command
      ```
      gcloud compute target-https-proxies delete calvin \
        --project $PROJECT_ID 
      ```

 * Create a forwarding rule to route incoming requests to the proxy.

  ```
   gcloud compute forwarding-rules create calvin \
       --load-balancing-scheme=EXTERNAL \
       --network-tier=PREMIUM \
       --address=calvin-ip \
       --target-https-proxy=calvin \
       --global \
       --ports=443 \
       --project $PROJECT_ID 
  ```

    * Delete command
      ```
      gcloud compute forwarding-rules delete calvin \
       --global \
       --project $PROJECT_ID 
      ```


# Web frontend

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

# Extract sentiment

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

# Process image delete eventa

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

# Detect faces

Not Implemented


# Metrics and monitors

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
resource.labels.service_name = "web-ui"
resource.labels.location = "us-east1")
 severity>=ERROR
```


# Test with lots of data

Not Implemented