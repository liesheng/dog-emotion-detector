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

import match
import app_config
import web_utils as utils


response = {}

url = os.environ["REQUEST_URI"] 
server_addr=os.environ["SERVER_ADDR"]
server_port=os.environ["SERVER_PORT"]
download_baseUrl="http://"+server_addr+":"+server_port+"/"+app_config.version_path+"/data/uploaded"

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

mediaFileId = utils.get_post_param(form_data,'mediaFileId')
phoneId = utils.get_post_param(form_data,'phoneId')

targetLocale = utils.get_post_param(form_data,'targetLocale')
if targetLocale is None:
	targetLocale = 'en_US'	

media_file_error=False

file_meta_data={}

try:
		userId = utils.get_post_param(form_data,'userId')
		emotionHint=utils.get_post_param(form_data,'emotionHint')
		recordTime = utils.get_post_param(form_data,'recordTime')
		if(recordTime is None) or len(recordTime) == 0:
			recordTime = str(time.time())

		dogId = utils.get_post_param(form_data,'dogId')
		tag = utils.get_post_param(form_data,'tag')

		errorMessage = ""
		source_file_name = ""

		try:
			mediaFile = form_data['mediaFile']
			file_data = mediaFile.value	
			source_file_name=mediaFile.filename
		except:
			errorMessage="Media File is required"

		if (source_file_name is None) or (len(source_file_name) ==0):
			errorMessage="Media File is required"

		if (dogId is None) or (len(dogId) ==0):
			if len(errorMessage) >0:
				errorMessage+=", "
			errorMessage+="Dog ID is required"

		if (userId is None) or (len(userId) ==0):
			if len(errorMessage) >0:
				errorMessage+=", "
			errorMessage+="User ID is required"

		if (tag is None) or (len(tag) ==0):
			if len(errorMessage) >0:
				errorMessage+=", "
			errorMessage+="Tag is required"

		if len(errorMessage) > 0:
			#sys.stderr.write(errorMessage)
			response['errorCode']="INVALID_INPUT"
			response['errorMessage']=errorMessage
			utils.send_error(400, response)
			sys.exit()

		mediaFileId=str(uuid.uuid4())

		file_meta_data = utils.saveMediaFileAndExtractAudio(mediaFileId, form_data)
		response['userId']=file_meta_data['userId']
		response['mediaFileId']=file_meta_data['mediaFileId']
		mediaType=file_meta_data['mediaType']
		response['mediaFormat']=file_meta_data['mediaFormat']
		response['mediaType']=file_meta_data['mediaType']
		response['downloadUrl']=file_meta_data['downloadUrl']	
		if mediaType == "video":
			response['audioDownloadUrl']=file_meta_data['audioDownloadUrl']
			response['thumbnail']=file_meta_data['thumbnail']

		#save tag
		tagResponse =utils.saveTag(userId, tags_path, mediaFileId, tag)

		#tagging is successful
		response['status']=tagResponse['status']
		tagId = utils.get_json_property(tagResponse, 'tagId')
		if (not tagId is None) and len(tagId) >0:
			response['tagId']=tagId

		errorMessage = utils.get_json_property(tagResponse, 'errorMessage')
		if (not errorMessage is None) and len(errorMessage) >0:
			response['errorMessage']=errorMessage

		#send response
		print("Content-type: application/json; charset=utf-8\n\n")

		print(json.dumps(response))

except Exception:
		traceback.print_exc(file=sys.stderr)
		response['errorCode']="INVALID_INPUT"
		if len(source_file_name) == 0:
			response['errorMessage']="Error to process media file:"+ source_file_name
		utils.send_error(400, response)
		sys.exit()



