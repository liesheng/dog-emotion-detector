#!/usr/bin/python

import uuid
import cgi
import json
import os
import io
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

#url = os.environ["REQUEST_URI"] 

#parts = url.split("?")
#url=parts[0]
#parts = url.split("/")

#mediaFileId=parts[len(parts)-1]
#parsed = urlparse.urlparse(url) 
#sys.stderr.write("requested url:"+url+"\n")
#sys.stderr.write("mediaFileId:"+mediaFileId+"\n")

SYSTEM_USER_ID=app_config.SYSTEM_USER_ID
data_path=app_config.data_path
upload_path=app_config.upload_path
thumbnail_image_path=app_config.thumbnail_image_path
metadata_path=app_config.metadata_path
tags_path=app_config.tags_path
codebook_path=app_config.codebook_path
system_data_path=app_config.system_data_path

form_data = cgi.FieldStorage()

mediaFileId = utils.get_post_param(form_data,'mediaFileId')
phoneId = utils.get_post_param(form_data,'phoneId')

targetLocale = utils.get_post_param(form_data,'targetLocale')
if targetLocale is None:
	targetLocale = 'en_US'	

media_file_error=False

file_meta_data={}
if not utils.isEmpty(mediaFileId):
	try:
		json_file=mediaFileId+".json"
		json_file_handle=io.open(metadata_path+"/"+json_file,'r', encoding='utf8')
		file_meta_data=json.load(json_file_handle)
	except:
		traceback.print_exc(file=sys.stderr)
		response['errorCode']="INVALID_INPUT"
		response['errorMessage']="Error to open the media file identified by:"+mediaFileId
		utils.send_error(400, response)
		sys.exit()

else:
	try:
		userId = utils.get_post_param(form_data,'userId')
		emotionHint=utils.get_post_param(form_data,'emotionHint')
		recordTime = utils.get_post_param(form_data,'recordTime')
		dogId = utils.get_post_param(form_data,'dogId')

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

		if len(errorMessage) > 0:
			#sys.stderr.write(errorMessage)
			response['errorCode']="INVALID_INPUT"
			response['errorMessage']=errorMessage
			utils.send_error(400, response)
			sys.exit()

		mediaFileId=str(uuid.uuid4())

		file_meta_data = utils.saveMediaFileAndExtractAudio(mediaFileId, form_data)
		mediaType=file_meta_data['mediaType']
		response['mediaFormat']=file_meta_data['mediaFormat']
		response['downloadUrl']=file_meta_data['downloadUrl']	
		if mediaType == "video":
			response['audioDownloadUrl']=file_meta_data['audioDownloadUrl']
			response['thumbnail']=file_meta_data['thumbnail']

	except Exception:
		traceback.print_exc(file=sys.stderr)
		response['errorCode']="INVALID_INPUT"
		if len(source_file_name) == 0:
			response['errorMessage']="Error to process media file:"+ source_file_name
		utils.send_error(400, response)
		sys.exit()

response['userId']=file_meta_data['userId']
response['mediaFileId']=file_meta_data['mediaFileId']
response['mediaType']=file_meta_data['mediaType']

#try to match

#load all codebooks
all_cb_json = match.load_all_codebooks(app_config.codebook_path)
try:
	(found,min_distortion) = match.match(mediaFileId, all_cb_json)
	if found is None:
		response['errorCode']="NOT_FOUND"
		response['errorMessage']="No Match Is Found"
		utils.send_error(404, response)
		sys.exit()

	tag=found['tag']

	if tag is None:
		tag = ''
	#translation=utils.get_json_property(found, 'translation')
	translation=utils.translate(system_data_path, tag, targetLocale)
	if translation is None:
		translation=tag

	#save tag

	#this is tag found by system algorithm, so use SYSTEM_USER_ID
	utils.saveTag(SYSTEM_USER_ID, tags_path, mediaFileId, tag)

	#send response
	print("Content-type: application/json; charset=utf-8\n\n")

	response['tag']=tag
	response['translation']=translation
	response['targetLocale']=targetLocale

	print(json.dumps(response))

except Exception:
	traceback.print_exc(file=sys.stderr)
	response['errorCode']="INVALID_INPUT"
	response['errorMessage']="File format is not support"
	utils.send_error(400, response)
	sys.exit()



