#!/usr/bin/env python

from speech_features import mfcc
from speech_features import logfbank
from speech_features import lbg
import scipy.io.wavfile as wav
import numpy
import json
import uuid
import io
import os
import match
import web_utils as utils

import app_config

SYSTEM_USER_ID=app_config.SYSTEM_USER_ID
data_path=app_config.data_path
samples_path=app_config.samples_path
upload_path=app_config.upload_path
metadata_path=app_config.metadata_path
tags_path=app_config.tags_path
codebook_path=app_config.codebook_path


MAX_DATA_SIZE=32=app_config.MAX_DATA_SIZE
SIZE_CODEBOOK = app_config.SIZE_CODEBOOK

print('generating codebook for size', SIZE_CODEBOOK, ' ...')
for sample_fileName in os.listdir(samples_path):
	full_audio_path=samples_path+"/"+sample_fileName
	if os.path.isdir(full_audio_path):
		# skip directories
		#print ("skip directory "+cb_json_file)
		continue
	print(full_audio_path)
	try:
		(rate,sig) = wav.read(full_audio_path)
		mfcc_feat = mfcc(sig,rate)
		#fbank_feat = logfbank(sig,rate)
	except ValueError as e:
		print(e)
		continue
		

	#print(fbank_feat[:,:])
	_data_size=len(mfcc_feat)
	if _data_size > MAX_DATA_SIZE:
		_data_size = MAX_DATA_SIZE

	population = mfcc_feat[1:_data_size]
	cb, cb_abs_w, cb_rel_w = lbg.generate_codebook(population, SIZE_CODEBOOK);
	cb_uuid=str(uuid.uuid4())
	cb_metadata = {}
	cb_metadata['fileName']=sample_fileName
	cb_metadata['tag']=utils.derive_tag_from_filename(sample_fileName)
	cb_metadata['codebook']=cb
	cb_metadata['cb_abs_w']=cb_abs_w
	cb_metadata['cb_rel_w']=cb_rel_w
	cb_json_file=cb_uuid+".json"
	cb_json_file_handle=io.open(codebook_path+"/"+cb_json_file,'w', encoding='utf8')
	json.dump(cb_metadata, cb_json_file_handle)
	cb_json_file_handle.close()

	
	#print('CodeBook output:')
	#for i, c in enumerate(cb):
	#  print('> %s, abs_weight=%d, rel_weight=%f' % (c, cb_abs_w[i], cb_rel_w[i]))
	#print('CodeBook shape:')
	#print (numpy.array(cb).shape)
