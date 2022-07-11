#!/usr/bin/env python

import os
import json

from speech_features import mfcc
from speech_features import logfbank
from speech_features import lbg
import scipy.io.wavfile as wav
import web_utils as utils
import app_config

import match


matched=0
total=0

all_tags_json = match.load_all_tags()
all_cb_json = match.load_all_codebooks(app_config.codebook_path)
for tag in all_tags_json:
	#print("Checking tag:"+tag)
	mediaFileIds = all_tags_json[tag]
	for mediaFileId in mediaFileIds:
		#print("Checking mediaFileId:"+mediaFileId)
		total+=1
		(found,min_distortion) = match.match(mediaFileId, all_cb_json, False)
		#print("found:", found['tag'],":", min_distortion)
		if (not found is None) and (tag == found['tag']):
			#print("matched!")
			matched+=1

print(matched," out of ", total, " matched.")
