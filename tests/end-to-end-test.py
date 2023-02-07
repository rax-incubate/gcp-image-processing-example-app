import subprocess
import shutil
import sys
import uuid
import os
import time

debugx = False
GS_BUCKET="gs://calvin-images/"

if os.environ.get('DEBUGX') == "1":
        debugx = True

if shutil.which("gsutil") is None or shutil.which("gcloud") is None or shutil.which("curl") is None:
    print("gsuti, gcloud and curl are required")
    sys.exit(1)

complete_success = True 

filename = "sample" + str(uuid.uuid4().hex) + ".png"
cmd = "gsutil -q cp -c test.png " + GS_BUCKET  + filename
if debugx:
    print(cmd)
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
p_status = p.wait()
msg = f"gsutil test file upload {filename}"
if p_status == 0:
    print(f"{msg}: Success")
else:
    print(f"{msg}: Fail")
    complete_success = False 



print("Checking event in Text extract service...")
cmd = "gcloud beta functions logs read extract-text --gen2 --region=us-east1 --project $PROJECT_ID | grep '" + filename + "'"
retry_count = 0
p_status = 1
while retry_count < 3 and p_status == 1:
    print("Waiting 2 seconds...")
    time.sleep(2)
    if debugx:
        print(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    msg = "Received event in Text extract service"
    if p_status == 0:
        print(f"{msg}: Success")
    retry_count = retry_count + 1
if p_status != 0:
    print(f"{msg}: Fail")
    complete_success = False 

print("Checking Text extraction...")
cmd = 'gcloud beta functions logs read extract-text --gen2 --region=us-east1 --project $PROJECT_ID | grep ' + "'" + 'Data sent:{"bucket": "calvin-images", "file_name": "' + filename + '", "extracted_text": "GOING TO THE\nBATHROOM.\nFLUSH' + "'"
retry_count = 0
p_status = 1
while retry_count < 3 and p_status == 1:
    print("Waiting 2 seconds...")
    time.sleep(2)
    if debugx:
        print(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    msg = "Text extraction"
    if p_status == 0:
        print(f"{msg}: Success")
    retry_count = retry_count + 1
if p_status != 0:
    print(f"{msg}: Fail")
    complete_success = False 


print("Checking Face detection service...")
cmd = "gcloud beta functions logs read detect-faces --gen2 --region=us-east1 --project $PROJECT_ID | grep '" + filename + "' | grep 'Mammal'"
retry_count = 0
p_status = 1
while retry_count < 3 and p_status == 1:
    print("Waiting 2 seconds...")
    time.sleep(2)
    if debugx:
        print(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    msg = "Face detection service"
    if p_status == 0:
        print(f"{msg}: Success")
    retry_count = retry_count + 1
if p_status != 0:
    print(f"{msg}: Fail")
    complete_success = False 



print("Checking Text Syntax extraction...")
cmd = 'gcloud beta functions logs read extract-syntax --gen2 --region=us-east1 --project $PROJECT_ID | grep ' + "'" + 'Data sent:{"bucket": "calvin-images", "file_name": "' + filename + '", "syntax_data":' + "'" + '| grep ' + "'GOING BATHROOM FLUSH'"
retry_count = 0
p_status = 1
while retry_count < 3 and p_status == 1:
    print("Waiting 2 seconds...")
    time.sleep(2)
    if debugx:
        print(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    msg = "Text syntax extraction"
    if p_status == 0:
        print(f"{msg}: Success")
    retry_count = retry_count + 1
if p_status != 0:
    print(f"{msg}: Fail")
    complete_success = False 


print("Checking Text Sentiment extraction...")
cmd = 'gcloud beta functions logs read extract-sentiment --gen2 --region=us-east1 --project $PROJECT_ID | grep ' + "'" + 'Data sent:{"bucket": "calvin-images", "file_name": "' + filename + '", "sentiment_score": 0.10000000149011612, "sentiment_magnitude": 2.4000000953674316' + "'"
retry_count = 0
p_status = 1
while retry_count < 3 and p_status == 1:
    print("Waiting 2 seconds...")
    time.sleep(2)
    if debugx:
        print(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    msg = "Text sentiment extraction"
    if p_status == 0:
        print(f"{msg}: Success")
    retry_count = retry_count + 1
if p_status != 0:
    print(f"{msg}: Fail")
    complete_success = False 

print("Checking Text Entity extraction...")
cmd = 'gcloud beta functions logs read extract-entities --gen2 --region=us-east1 --project $PROJECT_ID | grep ' + "'" + 'Data sent:{"bucket": "calvin-images", "file_name": "' + filename + '", "entity_data": \[{"entity_name": "CALVIN", "entity_type": "PERSON", "entity_score": 0.5809273719787598}' + "'"
retry_count = 0
p_status = 1
while retry_count < 3 and p_status == 1:
    print("Waiting 2 seconds...")
    time.sleep(2)
    if debugx:
        print(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    msg = "Text entity extraction"
    if p_status == 0:
        print(f"{msg}: Success")
    retry_count = retry_count + 1
if p_status != 0:
    print(f"{msg}: Fail")
    complete_success = False 

cmd = "gcloud functions describe web-ui --project $PROJECT_ID  --region=us-east1  --format='value(serviceConfig.uri)'"
if debugx:
    print(cmd)
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
url = output.decode().replace('\n','') + "?search=BATHROOM FLUSH"

print("Checking Data writer...")
cmd = 'gcloud beta functions logs read data-writer --gen2 --region=us-east1 --project $PROJECT_ID | grep ' + "'" + filename + "' | grep 'Data entry succeeded'" 
retry_count = 0
p_status = 1
while retry_count < 4 and p_status == 1:
    print("Waiting 2 seconds...")
    time.sleep(2)
    if debugx:
        print(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    msg = "Data Writer"
    if p_status == 0:
        print(f"{msg}: Success")
    retry_count = retry_count + 1
if p_status != 0:
    print(f"{msg}: Fail")
    complete_success = False 

print("Checking Web search...")
cmd = "gcloud functions describe web-ui --project $PROJECT_ID  --region=us-east1  --format='value(serviceConfig.uri)'"
retry_count = 0
p_status = 1
while retry_count < 3 and p_status == 1:
    print("Waiting 2 seconds...")
    time.sleep(2)
    if debugx:
        print(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    msg = "Web search"
    if p_status == 0:
        print(f"{msg}: Success")
    retry_count = retry_count + 1
if p_status != 0:
    print(f"{msg}: Fail")
    complete_success = False 


cmd = f"gsutil -q rm {GS_BUCKET}{filename}"
if debugx:
    print(cmd)
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
p_status = p.wait()
msg = "gsutil test file delete"
if p_status == 0:
    print(f"{msg}: Success")
else:
    print(f"{msg}: Fail")
    complete_success = False 

print("Checking Data Deleter...")
cmd = 'gcloud beta functions logs read data-deleter --gen2 --region=us-east1 --project $PROJECT_ID | grep ' + "'" + filename + "' | grep 'Data entry succeeded'" 
retry_count = 0
p_status = 1
while retry_count < 4 and p_status == 1:
    print("Waiting 2 seconds...")
    time.sleep(2)
    if debugx:
        print(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    msg = "Data Deleter"
    if p_status == 0:
        print(f"{msg}: Success")
    retry_count = retry_count + 1
if p_status != 0:
    print(f"{msg}: Fail")
    complete_success = False 


if complete_success:
    print ("All Tests Passed")
    sys.exit(0)
else:
    print ("Some Tests Failed. Please see above")
    sys.exit(1)

