#!/usr/bin/env python

from speech_features import mfcc
from speech_features import logfbank
from speech_features import lbg
import scipy.io.wavfile as wav
import numpy
import json
import uuid
import io

samples_dir="../data/samples"
samples_json="samples.json"
samples_json_file_handler = open(samples_dir+"/"+samples_json, "r")
samples = json.load(samples_json_file_handler)

SIZE_CODEBOOK = 128
cb_dir="../data/codebooks/backup."+str(SIZE_CODEBOOK)

print('generating codebook for size', SIZE_CODEBOOK, ' ...')
for sample in samples:
	sample_fileName=sample['fileName']
	sample_fileName=sample_fileName.strip()
	sample_tag=sample['tag']
	print('generating codebook for sample ', sample_fileName, ' ...')
	(rate,sig) = wav.read(samples_dir+"/"+sample_fileName)
	mfcc_feat = mfcc(sig,rate)
	fbank_feat = logfbank(sig,rate)

	#print(fbank_feat[:,:])
	population = fbank_feat
	cb, cb_abs_w, cb_rel_w = lbg.generate_codebook(population, SIZE_CODEBOOK);
	cb_uuid=str(uuid.uuid4())
	cb_metadata = {}
	cb_metadata['fileName']=sample_fileName
	cb_metadata['tag']=sample_tag
	cb_metadata['codebook']=cb
	cb_json_file=cb_uuid+".json"
	cb_json_file_handler=io.open(cb_dir+"/"+cb_json_file,'w', encoding='utf8')
	json.dump(cb_metadata, cb_json_file_handler)
	cb_json_file_handler.close()

	
	#print('CodeBook output:')
	#for i, c in enumerate(cb):
	#  print('> %s, abs_weight=%d, rel_weight=%f' % (c, cb_abs_w[i], cb_rel_w[i]))
	#print('CodeBook shape:')
	#print (numpy.array(cb).shape)
