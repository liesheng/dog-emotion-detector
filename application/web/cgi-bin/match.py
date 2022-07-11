#!/usr/bin/env python

from speech_features import mfcc
from speech_features import logfbank
from speech_features import lbg
import scipy.io.wavfile as wav
import numpy
import os
import sys
import io
import warnings
import json
import uuid
from threading import Thread

import app_config
import traceback

mfcc_path=app_config.mfcc_path
tags_path=app_config.tags_path
media_file_path=app_config.upload_path
codebook_path=app_config.codebook_path
thumbnail_image_path=app_config.thumbnail_image_path

MAX_DATA_SIZE=app_config.MAX_DATA_SIZE
SIZE_CODEBOOK=app_config.SIZE_CODEBOOK

def match(mediaFileId, all_cb_json, lookupTag=True):
	#print(" matching "+mediaFileId+"...")
	
	min_distortion=sys.float_info.max
	found=None
	
	if lookupTag:
		try:	
			tag = find_system_tag_for_mediaFile(mediaFileId)
			if not tag is None:
				for cb_json in all_cb_json:
					if tag==cb_json['tag']:
						found =  cb_json
						return (found, min_distortion)
		except:
			tag = None
			traceback.print_exc(file=sys.stderr)
		#warnings.warn("No system tag is found for "+mediaFileId)
	
	mfcc_feat = load_or_generate_mfcc_features(mediaFileId)
	if mfcc_feat is None:
		return (None, None)
	#(rate,sig) = wav.read(input_file)
	#mfcc_feat = mfcc(sig,rate)
	
	for cb_json in all_cb_json:
		cb=cb_json['codebook']
		tag=cb_json['tag']

		#print("checking against codebook tag:"+tag+"...")
		#print("codebook size ", len(cb))
		
		#avg_distortion = lbg.avg_distortion_c_list(cb,mfcc_feat)
		avg_distortion = get_avg_dist(cb,mfcc_feat)
		#print('avg distortion output:',avg_distortion)
		#print("")
		if(avg_distortion<min_distortion):
			min_distortion=avg_distortion
			found=cb_json

	return found,min_distortion

#load all codebooks
def load_all_codebooks(cb_dir):
	all_cb_json=[]
	for cb_json_file in os.listdir(cb_dir):
		if os.path.isdir(cb_dir+"/"+cb_json_file):
			# skip directories
			#print ("skip directory "+cb_json_file)
			continue
		cb_json_file_handler=io.open(cb_dir+"/"+cb_json_file,'r', encoding='utf8')
		cb_json = json.load(cb_json_file_handler)
		cb_json_file_handler.close()
		all_cb_json.append(cb_json)

	return all_cb_json


def get_avg_dist(cb, data):
	_data_size = len(data)
	if _data_size > MAX_DATA_SIZE:
		_data_size = MAX_DATA_SIZE
	total_dist=0
	#print("get_avg_dist,  _data_size:", _data_size)
	#print("get_avg_dist,  cb:", len(cb))
	for data_v in data[0:_data_size]:
	  for cb_v in cb:
	    total_dist+=lbg.euclid_squared(data_v, cb_v)
	
	return total_dist/_data_size
		
		
def load_or_generate_mfcc_features(mediaFileId):
	mfcc_json = {}

	mfcc_json_file=mfcc_path+"/"+mediaFileId+"-mfcc.json"
	if os.path.isfile(mfcc_json_file):
		mfcc_json_file_handle=open(mfcc_json_file,'r')
		mfcc_json = json.load(mfcc_json_file_handle)
		mfcc_json_file_handle.close()
		mfcc_feat=mfcc_json['mfcc_features']
	else:
		try:
			audioFile = media_file_path+"/"+mediaFileId+".wav"
			if not os.path.isfile(audioFile):
				audioFile = media_file_path+"/"+mediaFileId

			(rate,sig) = wav.read(audioFile)
			mfcc_feat = mfcc(sig,rate)
			mfcc_json['mfcc_features']=mfcc_feat.tolist()
		except Exception as e:
			sys.stderr.write("error to open media file:"+mediaFileId+", "+str(e)+"\n")
			return None;
		try:
			mfcc_json_file_handle=open(mfcc_json_file,'w')
			json.dump(mfcc_json, mfcc_json_file_handle)
			mfcc_json_file_handle.close()
		except Exception as e:
			sys.stderr.write("error to save mfcc for:"+mediaFileId+", "+str(e)+"\n")

	return mfcc_feat

def load_all_tags():
	all_tags_json={}
	for tags_json_file in os.listdir(tags_path):
		if os.path.isdir(tags_path+"/"+tags_json_file):
			# skip directories
			#print ("skip directory "+tags_json_file)
			continue
		tags_json_file_handle=io.open(tags_path+"/"+tags_json_file,'r', encoding='utf8')
		tags_json = json.load(tags_json_file_handle)
		#print(tags_json)
		tags_json_file_handle.close()

		#figure out mediaFileId
		(mediaFileId, ext)= tags_json_file.split("-tags")
		#print("mediaFileId:"+mediaFileId)

		#figure out best tag for this file
		'''
		for userId in tags_json:
			#print(userId)
			tags = tags_json[userId]
		'''
		try:
			tags = tags_json[app_config.SYSTEM_USER_ID]
		except:
			tags = []
		
		tag = None
		if not tags is None and len(tags) >0:
			tag_info = tags[len(tags)-1]	
			tag = tag_info['tag']
		
		if tag is None:
			continue
		#else:
			#print("tag:"+tag, " source:"+mediaFileId)
		
		try:
			sources = all_tags_json[tag]
		except:
			sources = []
		#print("sources(1):", sources)
		sources.append(mediaFileId)
		#print("sources(2):", sources)
		all_tags_json[tag] = sources

	return all_tags_json

def generate_tag_codebooks(tag, mediaFileIds=None):
	if mediaFileIds is None or len(mediaFileIds) == 0:
		try:
			all_tags_json = load_all_tags()
			mediaFileIds = all_tags_json[tag]
		except:
			traceback.print_exc(file=sys.stderr)
			return

	#sys.stderr.write("Generating codebooks for tag:"+tag+" mediaFileIds:"+str(mediaFileIds)+"\n")
	#print >>sys.stderr, "Generating codebooks for tag:"+tag+" mediaFileIds:"+str(mediaFileIds)+"\n"
	#print ("Generating codebooks for tag:"+tag+" mediaFileIds:"+str(mediaFileIds))
	population = None
	for mediaFileId in mediaFileIds:
		#print ("mediaFileId:"+str(mediaFileId))
		mfcc_feat = load_or_generate_mfcc_features(mediaFileId)
		if mfcc_feat is None:
			continue
		_data_size=len(mfcc_feat)-1
		if _data_size > MAX_DATA_SIZE:
			_data_size = MAX_DATA_SIZE
		t_population = mfcc_feat[1:_data_size] #the first one is energy
		if population is None:
			population = t_population
		else:
			#merge
			population = numpy.concatenate((population, t_population))

	cb, cb_abs_w, cb_rel_w = lbg.generate_codebook(population, SIZE_CODEBOOK);

	#cb_json_name=str(uuid.uuid4())
	cb_json_name=tag
	cb_metadata = {}
	cb_metadata['tag']=tag
	cb_metadata['codebook']=cb
	cb_metadata['cb_abs_w']=cb_abs_w
	cb_metadata['cb_rel_w']=cb_rel_w
	cb_json_file=cb_json_name+".json"
	cb_json_file_handle=open(codebook_path+"/"+cb_json_file,'w')
	json.dump(cb_metadata, cb_json_file_handle)
	cb_json_file_handle.close()

def generate_codebooks_from_metadata():
	all_tags_json = load_all_tags()
	for tag in all_tags_json:
		generate_tag_codebooks(tag, all_tags_json[tag])
		
def find_system_tag_for_mediaFile(mediaFileId):
	try:
		tags_json_file=tags_path+"/"+mediaFileId+"-tags.json"
		if not os.path.isfile(tags_json_file):
			return None

		tags_json_file_handle=io.open(tags_json_file,'r', encoding='utf8')
		tags_json = json.load(tags_json_file_handle)
		tags_json_file_handle.close()
		
		if not tags_json is None:
			tags = tags_json[app_config.SYSTEM_USER_ID]
		if not tags is None:
			tag_info = tags[0]
			tag = tag_info['tag']
			
		#warnings.warn("Found system tag("+tag+") for "+mediaFileId)	
		return tag	
	except:
		traceback.print_exc(file=sys.stderr)
		return None
	
