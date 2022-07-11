#!/usr/bin/env python

import json
from speech_features import mfcc
from speech_features import logfbank
from speech_features import lbg
import scipy.io.wavfile as wav

import match

#load all codebooks
cb_dir="../data/codebooks/backup.128"
all_cb_json = match.load_all_codebooks(cb_dir)
print("all_cb_json size:",len(all_cb_json))

samples_dir="../data/samples"
samples_json="samples.json"

samples_json_file_handler = open(samples_dir+"/"+samples_json, "r")
samples = json.load(samples_json_file_handler)

matched=0;
for input in samples:
	input_fileName=input['fileName']
	input_fileName=input_fileName.strip()
	print("Matching "+input_fileName+" tag:"+input['tag'], "...")

	(rate,sig) = wav.read(samples_dir+"/"+input_fileName)
	mfcc_feat = mfcc(sig,rate)
	fbank_feat = logfbank(sig,rate)

	(found,min_distortion) = match.match(samples_dir+"/"+input_fileName, all_cb_json)

	print("Found cloest:",found['tag'], "(",min_distortion,")")
	if(found['tag'] == input['tag']):
		matched+=1;
		print("matched!")
	else:
		print("not matched!")
	
	print("")
	print("")

print(matched," out of ", len(samples), " matched.")
