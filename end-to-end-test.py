import subprocess
import shutil
import sys

if shutil.which("gsutil") is None or shutil.which("gcloud") is None or shutil.which("curl") is None:
    print("gsuti, gcloud and curl are required")
    sys.exit(1)


# p = subprocess.Popen("gsutil cp -c gs://calvin.tty0.me/calvin-999.png  gs://calvin-images/test-sample.png", stdout=subprocess.PIPE, shell=True)
# (output, err) = p.communicate()
# p_status = p.wait()
# msg="gsutil test file upload"
# if p_status == 0:
#     print(f"{msg}: Success")
# else:
#     print(f"{msg}: Fail")
# #print(f"Debugx : {output}")


p = subprocess.Popen("gcloud beta functions logs read extract-text --gen2 --region=us-east1 --project $PROJECT_ID | grep test-sample.png", stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
p_status = p.wait()
msg="Received event in Text extract service"
if p_status == 0:
    print(f"{msg}: Success")
else:
    print(f"{msg}: Fail")
#print(f"Debugx : {output}")


p = subprocess.Popen("gcloud beta functions logs read extract-text --gen2 --region=us-east1 --project $PROJECT_ID | grep 'Data sent:{\"bucket\": \"calvin-images\", \"file_name\": \"test-sample.png\", \"extracted_text\": \"CALVIN, WHAT'", stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
p_status = p.wait()
msg="Text extraction"
if p_status == 0:
    print(f"{msg}: Success")
else:
    print(f"{msg}: Fail")
#print(f"Debugx : {output}")


p = subprocess.Popen("gcloud beta functions logs read extract-syntax --gen2 --region=us-east1 --project $PROJECT_ID | grep 'Data sent:{\"bucket\": \"calvin-images\", \"file_name\": \"test-sample.png\", \"syntax_data\": \"CALVIN ARE DOING'", stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
p_status = p.wait()
msg="Text syntax extraction"
if p_status == 0:
    print(f"{msg}: Success")
else:
    print(f"{msg}: Fail")
#print(f"Debugx : {output}")


p = subprocess.Popen("gcloud beta functions logs read extract-sentiment --gen2 --region=us-east1 --project $PROJECT_ID | grep 'Data sent:{\"bucket\": \"calvin-images\", \"file_name\": \"test-sample.png\", \"sentiment_score\": 0.10000000149011612, \"sentiment_magnitude\": 2.4000000953674316'", stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
p_status = p.wait()
msg="Text sentiment extraction"
if p_status == 0:
    print(f"{msg}: Success")
else:
    print(f"{msg}: Fail")
#print(f"Debugx : {output}")


p = subprocess.Popen("curl -s https://web-ui-fpxn5dkopa-ue.a.run.app/?search=BATHROOM FLUSH | grep 'alt=test-sample.png'", stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
p_status = p.wait()
msg="Web search"
if p_status == 0:
    print(f"{msg}: Success")
else:
    print(f"{msg}: Fail")
#print(f"Debugx : {output}")
