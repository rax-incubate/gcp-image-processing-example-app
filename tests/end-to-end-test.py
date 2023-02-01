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


print("Waiting 7 seconds...")
time.sleep(7)

cmd = "gcloud beta functions logs read extract-text --gen2 --region=us-east1 --project $PROJECT_ID | grep '" + filename + "'"
if debugx:
    print(cmd)
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
p_status = p.wait()
msg = "Received event in Text extract service"
if p_status == 0:
    print(f"{msg}: Success")
else:
    print(f"{msg}: Fail")

print("Waiting 7 seconds...")
time.sleep(7)

cmd = 'gcloud beta functions logs read extract-text --gen2 --region=us-east1 --project $PROJECT_ID | grep ' + "'" + 'Data sent:{"bucket": "calvin-images", "file_name": "' + filename + '", "extracted_text": "GOING TO THE\nBATHROOM.\nFLUSH' + "'"
if debugx:
    print(cmd)
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
p_status = p.wait()
msg = "Text extraction"
if p_status == 0:
    print(f"{msg}: Success")
else:
    print(f"{msg}: Fail")

cmd = 'gcloud beta functions logs read extract-syntax --gen2 --region=us-east1 --project $PROJECT_ID | grep ' + "'" + 'Data sent:{"bucket": "calvin-images", "file_name": "' + filename + '", "syntax_data":' + "'" + '| grep ' + "'GOING BATHROOM FLUSH'"
if debugx:
    print(cmd)
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
p_status = p.wait()
msg = "Text syntax extraction"
if p_status == 0:
    print(f"{msg}: Success")
else:
    print(f"{msg}: Fail")


cmd = 'gcloud beta functions logs read extract-sentiment --gen2 --region=us-east1 --project $PROJECT_ID | grep ' + "'" 'Data sent:{"bucket": "calvin-images", "file_name": "' + filename + '", "sentiment_score": 0.10000000149011612, "sentiment_magnitude": 2.4000000953674316' + "'"
if debugx:
    print(cmd)
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
p_status = p.wait()
msg = "Text sentiment extraction"
if p_status == 0:
    print(f"{msg}: Success")
else:
    print(f"{msg}: Fail")

cmd = "gcloud functions describe web-ui --project $PROJECT_ID  --region=us-east1  --format='value(serviceConfig.uri)'"
if debugx:
    print(cmd)
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
url = output.decode().replace('\n','') + "?search=BATHROOM FLUSH"

cmd = "curl -s " + url + " | grep 'alt=" + filename + "'"
if debugx:
    print(cmd)
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
p_status = p.wait()
msg = "Web search"
if p_status == 0:
    print(f"{msg}: Success")
else:
    print(f"{msg}: Fail")

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

print("Waiting 7 seconds...")
time.sleep(7)

cmd = 'gcloud beta functions logs read data-deleter --gen2 --region=us-east1 --project $PROJECT_ID | grep "' + "DELETE FROM calvin.calvin_text WHERE bucket='calvin-images' AND filename='" + filename + "'" + '"'
if debugx:
    print(cmd)
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
p_status = p.wait()
msg = "Data Deleter"
if p_status == 0:
    print(f"{msg}: Success")
else:
    print(f"{msg}: Fail")
