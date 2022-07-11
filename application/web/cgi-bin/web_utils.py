#!/usr/bin/env python

import json
import sys
import io
import os
import time
import uuid
from threading import Thread
import subprocess
import app_config
import match

import traceback

upload_path = app_config.upload_path
tags_path=app_config.tags_path
metadata_path=app_config.metadata_path
thumbnail_image_path=app_config.thumbnail_image_path
download_baseUrl=app_config.download_baseUrl

def isEmpty(s):
	if (s is None) or len(s) ==0:
		return True
	else:
		return False

def get_post_param(form_data,post_param):
	if form_data is None: 
		return None
	else:
		try:
			if form_data[post_param] is None:
				return None
			else:
				return form_data[post_param].value
		except KeyError:		
			return None
	
def get_json_property(json_data,prop_name):
	if json_data is None: 
		return None
	else:
		try:
			if json_data[prop_name] is None:
				return None
			else:
				return json_data[prop_name]
		except KeyError:		
			return None

def derive_tag_from_filename(filename):
	if "bark" in filename:
		return "I am a barking dog"
	
	if "whin" in filename:
		return "I am a whining dog"

	if "grow" in filename:
		return "I am a growling dog"

	if "sick" in filename or "cough" in filename:
		return "I am a sick dog"

	if "biting" in filename or "bite" in filename:
		return "I am a siciting dog"

	parts = filename.split(".")

	return parts[0]


def send_error(http_status_code, jsonMsg):
	print ('Content-Type: application/json')
	print ('Status: '+str(http_status_code))
	print ("\n\n")
	print (json.dumps(jsonMsg))
	#os._exit(1)
	
def translate(translation_metadata_path, tag_name, locale_name):
	translation_json_handle=io.open(translation_metadata_path+"/translations.json",'r', encoding='utf8')
	translation_json = json.load(translation_json_handle)
	translation_json_handle.close()
	try:
		return translation_json[tag_name][locale_name]
	except:
		return tag_name

def saveMediaFileAndExtractAudio(mediaFileId, form_data, doExtractAudio=True, audioFormat=".wav", doExtractThumbnail=True, imageFormat=".jpeg"):
	mediaFile = form_data['mediaFile']
	file_data = mediaFile.value	
	source_file_name=mediaFile.filename
	source_file_name_lower=source_file_name.lower()
	mediaFormat = os.path.splitext(source_file_name_lower)[1]
	if '.wav' == mediaFormat:
		mediaType="audio"
	elif ".mp4" == mediaFormat:
		mediaType="video"
		#TODO: extract audio file
	elif ".gif" == mediaFormat or ".jpg" == mediaFormat or ".jpeg" == mediaFormat:
		mediaType="image"
	else:
		mediaType="Unknown"
	
	mediaFilePath=upload_path+"/"+mediaFileId+mediaFormat
	audioFilePath=upload_path+"/"+mediaFileId+audioFormat
	thumbnailPath=thumbnail_image_path+"/"+mediaFileId+imageFormat

	#save raw data
	fp=open(mediaFilePath,'wb')
	fp.write(file_data)
	fp.close()

	#for video file, extract its audio
	if doExtractAudio:
		if not mediaType is None:
			if mediaType.lower() == "video":
				extractAudio(mediaFilePath, audioFilePath)
	
	if doExtractThumbnail:
		extractThumbnail (mediaFilePath, thumbnailPath)

	#prepare file metadata	
	file_meta_data={}
	file_meta_data['mediaFileId']=mediaFileId
	file_meta_data['srcFilename']=source_file_name
	file_meta_data['mediaType']=mediaType
	file_meta_data['mediaFormat']=mediaFormat

	file_meta_data['userId']= get_post_param(form_data,'userId')
	file_meta_data['emotionHint']=get_post_param(form_data,'emotionHint')
	file_meta_data['recordTime'] =get_post_param(form_data,'recordTime')
	file_meta_data['dogId'] = get_post_param(form_data,'dogId')
	file_meta_data['phoneId']=get_post_param(form_data,'phoneId')

	file_meta_data['rawFileLocation']=mediaFilePath
	file_meta_data['downloadUrl']=download_baseUrl+"/"+mediaFileId+mediaFormat
	if mediaType == "video":
		file_meta_data['audioLocation']=audioFilePath
		file_meta_data['audioDownloadUrl']=download_baseUrl+"/"+mediaFileId+".wav"
		file_meta_data['thumbnailPath']=thumbnailPath
		file_meta_data['thumbnail']=download_baseUrl+"/thumbnail/"+mediaFileId+".jpeg"
	
	#save file metadata	
	json_file=mediaFileId+".json"
	json_file_handle=open(metadata_path+"/"+json_file,'w')
	json.dump(file_meta_data, json_file_handle)
	json_file_handle.close()

	return file_meta_data

def extractAudio (videoFilePath, audioFilePath, waitProcess=True):
	paramList =["-i", videoFilePath,  audioFilePath]
	p = subprocess.Popen([app_config.ffmpeg]+paramList, close_fds=app_config.close_fds, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if waitProcess:
		p.wait()

def extractThumbnail (videoFilePath, thumbnailPath, waitProcess=True):
	paramList =["-i", videoFilePath,  "-vframes", "1", thumbnailPath]
	sys.stderr.write(str(paramList))
	p = subprocess.Popen([app_config.ffmpeg]+paramList, close_fds=app_config.close_fds, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	#p = subprocess.Popen([app_config.ffmpeg]+paramList, close_fds=True)
	if waitProcess:
		p.wait()

	
def saveTag(userId, tags_path, mediaFileId, tag):
	response = {}
	try:
		tags_json_file=tags_path+"/"+mediaFileId+"-tags.json"
		
		if os.path.isfile(tags_json_file):
			try:
				tags_json_file_handle=open(tags_json_file,'r')
				tags_data=json.load(tags_json_file_handle)
				#sys.stderr.write("found file:"+str(tags_data))
				tags_json_file_handle.close();
			except:
				tags_data={}
		else:
			tags_data={}
				
		#TODO: save tag history?
		try:
			tags = tags_data[userId]
		except:
			tags = []
		
		tag_info={}
		
		tagId = str(uuid.uuid4())
		tag_info['tagId']=tagId
		tag_info['tag'] = tag
		tag_info['tagTime']= str(time.time())
		#tag_info['userId']=get_json_property(file_meta_data, 'userId')

		tags.append(tag_info)
		tags_data[userId]=tags
		
		#add it for system user
		tags_data[app_config.SYSTEM_USER_ID]=[tag_info]

		tags_json_file_handle=open(tags_json_file,'w+')	
		json.dump(tags_data, tags_json_file_handle)
		tags_json_file_handle.close()
		
		response['status']='success'
		response['tagId']=tagId

		#generate mfcc and codebook
		if app_config.tag_to_generate_codebook:
			#match.load_or_generate_mfcc_features(mediaFileId)
			#'''
			try:
				##t = Thread(target=match.generate_tag_codebooks, args=(tag,), daemon=True)
				#t = Thread(target=match.generate_tag_codebooks, args=(tag,))
				#t.daemon = True 
				#t.start()
				##thread.start_new_thread(match.generate_tag_codebooks(tag))
				#p = subprocess.Popen([app_config.py_executable, 'generate_codebooks.py'], close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

				p = subprocess.Popen([app_config.py_executable, 'generate_codebooks.py'], close_fds=app_config.close_fds, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


			except:
				sys.stderr.write("Error: unable to start thread to generate codebook for tag:"+tag)
				traceback.print_exc(file=sys.stderr)
			#'''
			

		return response
	except:
		traceback.print_exc(file=sys.stderr)
		#sys.stderr.write("error to save tag (mediaFile:"+mediaFileId+", tag_info:"+ str(tag_info))
			
		response['status']='failed'
		return response

def getMediaInfo(mediaFileId):
	response = {}
	try:
		try:
			media_json_file=metadata_path+"/"+mediaFileId+".json"
			media_json_file_handle=open(media_json_file,'r')
			response = json.load(media_json_file_handle)
			media_json_file_handle.close()
		except:
			response['errorCode']="FILE_NOT_FOUND"
			response['errorMessage']="The media file identified by "+mediaFileId+" is not found."
			traceback.print_exc(file=sys.stderr)
			return response
		try:
			tags_json_file=tags_path+"/"+mediaFileId+"-tags.json"
			tags_json_file_handle=open(tags_json_file,'r')
			tags_json = json.load(tags_json_file_handle)
		
			response['tags']=tags_json
		except:
			response['tags']=[]
	except:		
		traceback.print_exc(file=sys.stderr)

	return response
		
