import subprocess
import shutil
import sys
import uuid
import os
import time

debugx = False

GCS_BUCKET=os.environ.get('GCS_BUCKET')

if GCS_BUCKET == "" or GCS_BUCKET is None:
    print("Please set GCS_BUCKET env variable")
    sys.exit(1)

if os.environ.get('DEBUGX') == "1":
        debugx = True

if shutil.which("gsutil") is None or shutil.which("gcloud") is None or shutil.which("curl") is None:
    print("gsuti, gcloud and curl are required")
    sys.exit(1)

complete_success = True 

filename = "sample" + str(uuid.uuid4().hex) + ".png"
cmd = "gsutil -q cp -c test.png gs://" + GCS_BUCKET  + "/" + filename
if debugx:
    print(cmd)
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
p_status = p.wait()
msg = f"Test file upload {filename}"
if p_status == 0:
    print(f"{msg}: Success")
else:
    print(f"{msg}: Fail")
    complete_success = False 



print("Checking event in Text extract service", end='')
cmd = "gcloud beta functions logs read extract-text --gen2 --region=us-east1 --project $PROJECT_ID | grep '" + filename + "'"
retry_count = 0
p_status = 1
while retry_count < 3 and p_status == 1:
    print("..", end='')
    time.sleep(2)
    if debugx:
        print(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    if p_status == 0:
        print(":Success")
    retry_count = retry_count + 1
if p_status != 0:
    print(":Fail")
    complete_success = False 

print("Checking Text extraction", end='')
cmd = 'gcloud beta functions logs read extract-text --gen2 --region=us-east1 --project $PROJECT_ID | grep ' + "'" + 'Data sent:{"bucket": "' + GCS_BUCKET + '", "file_name": "' + filename + '", "extracted_text": "GOING TO THE\nBATHROOM.\nFLUSH' + "'"
retry_count = 0
p_status = 1
while retry_count < 3 and p_status == 1:
    print("..", end='')
    time.sleep(2)
    if debugx:
        print(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    if p_status == 0:
        print(":Success")
    retry_count = retry_count + 1
if p_status != 0:
    print(":Fail")
    complete_success = False 


print("Checking Face detection service", end='')
cmd = "gcloud beta functions logs read detect-faces --gen2 --region=us-east1 --project $PROJECT_ID | grep '" + filename + "' | grep 'Mammal'"
retry_count = 0
p_status = 1
while retry_count < 3 and p_status == 1:
    print("..", end='')
    time.sleep(2)
    if debugx:
        print(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    if p_status == 0:
        print(":Success")
    retry_count = retry_count + 1
if p_status != 0:
    print(":Fail")
    complete_success = False 



print("Checking Text Syntax extraction", end='')
cmd = 'gcloud beta functions logs read extract-syntax --gen2 --region=us-east1 --project $PROJECT_ID | grep ' + "'" + 'Data sent:{"bucket": "' + GCS_BUCKET + '", "file_name": "' + filename + '", "syntax_data":' + "'" + '| grep ' + "'GOING BATHROOM FLUSH'"
retry_count = 0
p_status = 1
while retry_count < 3 and p_status == 1:
    print("..", end='')
    time.sleep(2)
    if debugx:
        print(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    if p_status == 0:
        print(":Success")
    retry_count = retry_count + 1
if p_status != 0:
    print(":Fail")
    complete_success = False 


print("Checking Text Sentiment extraction", end='')
cmd = 'gcloud beta functions logs read extract-sentiment --gen2 --region=us-east1 --project $PROJECT_ID | grep ' + "'" + 'Data sent:{"bucket": "' + GCS_BUCKET + '", "file_name": "' + filename + '", "sentiment_score": 0.10000000149011612, "sentiment_magnitude": 2.4000000953674316' + "'"
retry_count = 0
p_status = 1
while retry_count < 3 and p_status == 1:
    print("..", end='')
    time.sleep(2)
    if debugx:
        print(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    if p_status == 0:
        print(":Success")
    retry_count = retry_count + 1
if p_status != 0:
    print(":Fail")
    complete_success = False 

print("Checking Text Entity extraction", end='')
cmd = 'gcloud beta functions logs read extract-entities --gen2 --region=us-east1 --project $PROJECT_ID | grep ' + "'" + 'Data sent:{"bucket": "' + GCS_BUCKET + '", "file_name": "' + filename + '", "entity_data": \[{"entity_name": "CALVIN", "entity_type": "PERSON", "entity_score": 0.5809273719787598}' + "'"
retry_count = 0
p_status = 1
while retry_count < 3 and p_status == 1:
    print("..", end='')
    time.sleep(2)
    if debugx:
        print(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    if p_status == 0:
        print(":Success")
    retry_count = retry_count + 1
if p_status != 0:
    print(":Fail")
    complete_success = False 

cmd = "gcloud functions describe web-ui --project $PROJECT_ID  --region=us-east1  --format='value(serviceConfig.uri)'"
if debugx:
    print(cmd)
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
url = output.decode().replace('\n','') + "?search=BATHROOM FLUSH"

print("Checking Data writer", end='')
cmd = 'gcloud beta functions logs read data-writer --gen2 --region=us-east1 --project $PROJECT_ID | grep ' + "'" + filename + "' | grep 'Data entry succeeded'" 
retry_count = 0
p_status = 1
while retry_count < 4 and p_status == 1:
    print("..", end='')
    time.sleep(2)
    if debugx:
        print(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    if p_status == 0:
        print(":Success")
    retry_count = retry_count + 1
if p_status != 0:
    print(":Fail")
    complete_success = False 

print("Checking Web search", end='')
cmd = "gcloud functions describe web-ui --project $PROJECT_ID  --region=us-east1  --format='value(serviceConfig.uri)'"
retry_count = 0
p_status = 1
while retry_count < 3 and p_status == 1:
    print("..", end='')
    time.sleep(2)
    if debugx:
        print(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    if p_status == 0:
        print(":Success")
    retry_count = retry_count + 1
if p_status != 0:
    print(":Fail")
    complete_success = False 


cmd = f"gsutil -q rm gs://{GCS_BUCKET}/{filename}"
if debugx:
    print(cmd)
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
p_status = p.wait()
msg = "Test file delete"
if p_status == 0:
    print(f"{msg}: Success")
else:
    print(f"{msg}: Fail")
    complete_success = False 

print("Checking Data Deleter", end='')
cmd = 'gcloud beta functions logs read data-deleter --gen2 --region=us-east1 --project $PROJECT_ID | grep ' + "'" + filename + "' | grep 'Data entry succeeded'" 
retry_count = 0
p_status = 1
while retry_count < 4 and p_status == 1:
    print("..", end='')
    time.sleep(2)
    if debugx:
        print(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    if p_status == 0:
        print(":Success")
    retry_count = retry_count + 1
if p_status != 0:
    print(":Fail")
    complete_success = False 


if complete_success:
    print ("All Tests Passed")
    sys.exit(0)
else:
    print ("Some Tests Failed. Please see above")
    sys.exit(1)

