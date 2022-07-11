#!/usr/bin/env python

from speech_features import mfcc
from speech_features import logfbank
from speech_features import lbg
import scipy.io.wavfile as wav
import numpy
import os
import sys
import io
import json

def match(input_file, all_cb_json):
	(rate,sig) = wav.read(input_file)
	mfcc_feat = mfcc(sig,rate)
	fbank_feat = logfbank(sig,rate)

	min_distortion=sys.float_info.max
	found=None
	for cb_json in all_cb_json:
		cb=cb_json['codebook']
		tag=cb_json['tag']
		avg_distortion = lbg.avg_distortion_c_list(cb,fbank_feat)
		print("checking "+tag)
		print('avg distortion output:',avg_distortion)
		print("")
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
