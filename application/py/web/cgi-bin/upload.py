#!/usr/bin/python

import uuid
import cgi
import json
import os

form_data = cgi.FieldStorage()
file_data = form_data['fileToUpload'].value

upload_path="/Users/llong203/workspace/python/web/upload"
file_uuid=str(uuid.uuid4())
fp=open(upload_path+"/"+file_uuid,'wb')
fp.write(file_data)
fp.close()

meta_data={}
meta_data['rawFile']=upload_path+"/"+file_uuid
meta_data['tag']='I am happy'
json_file=file_uuid+".json"
json_file_handler=open(upload_path+"/"+json_file,'wb')
json.dump(meta_data, json_file_handler)

print("Content-type: text/html\n\n")
print("This is test1<br>\n\n");
print("uuid:"+str(file_uuid)+" is now uploaded.");

for uploaded_filename in os.listdir(upload_path):
	print (uploaded_filename+ "<br>")
