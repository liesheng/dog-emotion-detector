#!/usr/bin/env python

import os
import json

from speech_features import mfcc
from speech_features import logfbank
from speech_features import lbg
import scipy.io.wavfile as wav
import web_utils as utils

import match

base_path="/workspace/dogemotiondetector/demo/v0"
data_path=base_path+"/data"
samples_dir=data_path+"/samples"
cb_dir=data_path+"/codebooks/current"

#load all codebooks
all_cb_json = match.load_all_codebooks(cb_dir)
print("all_cb_json size:",len(all_cb_json))

files = os.listdir(samples_dir)
#files=['agitated-german-shephard.wav']
matched=0
total=0
for sample_fileName in files:
	print("Matching "+sample_fileName+"...")
	full_audio_path=samples_dir+"/"+sample_fileName
	if os.path.isdir(full_audio_path):
		# skip directories
		print ("skip directory "+full_audio_path)
		continue

	total+=1
	print(full_audio_path)

	#(rate,sig) = wav.read(full_audio_path)
	#mfcc_feat = mfcc(sig,rate)
	#fbank_feat = logfbank(sig,rate)

	try:
		(found,min_distortion) = match.match(full_audio_path, all_cb_json)
	except:
		continue

	srcTag = utils.derive_tag_from_filename(sample_fileName)
	print("Found cloest:",found['tag'], "(",min_distortion,")")
	if(found['tag'] == srcTag):
		matched+=1;
		print("matched!")
	else:
		print("not matched!")
	
	print("")
	print("")

print(matched," out of ", total, " matched.")
