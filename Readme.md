https://cloud.google.com/functions/docs/tutorials/storage


* Setup your env variables
  PROJECT_ID=$(gcloud config get-value project)
  PROJECT_NUMBER=$(gcloud projects list --filter="project_id:$PROJECT_ID" --format='value(project_number)')

* Create bucket for the images
    gsutil mb -l us-east1 gs://calvin-images

* Grant IAM access
  SERVICE_ACCOUNT=$(gsutil kms serviceaccount -p $PROJECT_NUMBER)

  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member serviceAccount:$SERVICE_ACCOUNT \
    --role roles/pubsub.publisher

* Deploy the function
  cd <CLONE FOLDER>/process-new-images
  gcloud functions deploy process-new-images --gen2 --runtime=python310 --region=us-east1 --source=. --entry-point=new_image_file --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" --trigger-event-filters="bucket=calvin-images"  --env-vars-file env.yaml --project $PROJECT_ID

* Test with an image 
  gsutil cp sample.png gs://calvin-images/sample.png

* Review logs
  gcloud beta functions logs read process-new-images --gen2 --limit=100 --region=us-east1 --project $PROJECT_ID
