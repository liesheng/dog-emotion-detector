#!/usr/bin/python

import uuid
import cgi
import json
import os
import sys
import datetime
import calendar
import time

import traceback
#from urlparse import urlparse

import app_config
import match
import web_utils as utils

response = {}

url = os.environ["REQUEST_URI"] 
server_addr=os.environ["SERVER_ADDR"]
server_port=os.environ["SERVER_PORT"]
version_path="v0"
download_baseUrl="http://"+server_addr+":"+server_port+"/"+version_path+"/data/uploaded"

parts = url.split("?")
url=parts[0]
parts = url.split("/")

mediaFileId=parts[len(parts)-1]
#parsed = urlparse.urlparse(url) 
#sys.stderr.write("requested url:"+url+"\n")
#sys.stderr.write("mediaFileId:"+mediaFileId+"\n")

SYSTEM_USER_ID=app_config.SYSTEM_USER_ID
data_path=app_config.data_path
upload_path=app_config.upload_path
metadata_path=app_config.metadata_path
tags_path=app_config.tags_path
codebook_path=app_config.codebook_path


form_data = cgi.FieldStorage()


try:
	errorMessage = ''
	mediaFileId = utils.get_post_param(form_data,'mediaFileId')	
	if (mediaFileId is None) or (len(mediaFileId) ==0):
		errorMessage+="Media File ID is required"
	else:
		media_file=upload_path+"/"+mediaFileId+".wav"
		if not os.path.isfile(media_file):
			errorMessage+="The media file identified by "+mediaFileId+" doesn't exist"
	
	userId = utils.get_post_param(form_data,'userId')
	if (userId is None) or (len(userId) ==0):
		if len(errorMessage) >0:
			errorMessage+="; "
		errorMessage+="User ID is required"

	tag = utils.get_post_param(form_data,'tag')
	if (tag is None) or (len(tag) ==0):
		if len(errorMessage) >0:
			errorMessage+="; "
		errorMessage+="tag ID is required"

	if len(errorMessage) > 0:
		response['errorCode']="INVALID_INPUT"
		response['errorMessage']=errorMessage
		utils.send_error(400, response)
		sys.exit()

	phoneId = utils.get_post_param(form_data,'phoneId')

	response['mediaFileId']=mediaFileId

	#save tag
	tagResponse=utils.saveTag(userId, tags_path, mediaFileId, tag)
	
	#tagging is successful
	response['status']=tagResponse['status']
	tagId = utils.get_json_property(tagResponse, 'tagId')
	if len(tagId) >0:
		response['tagId']=tagId

	errorMessage = utils.get_json_property(tagResponse, 'errorMessage')
	if (not errorMessage is None) and len(errorMessage) >0:
		response['errorMessage']=errorMessage

except Exception:
	traceback.print_exc(file=sys.stderr)

	response['errorCode']="INVALID_INPUT"
	response['errorMessage']="Error to process media file:"+ mediaFileId
	utils.send_error(400, response)
	sys.exit()


#TODO:try to generate code book


#send response
print("Content-type: application/json; charset=utf-8\n\n")

print(json.dumps(response))
