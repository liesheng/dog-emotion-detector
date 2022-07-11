#!/usr/bin/env python

from speech_features import mfcc
from speech_features import logfbank
import scipy.io.wavfile as wav
import numpy
import match
import json
import sys
from threading import Thread

def testNums():
	print("in testNums now")
	i=0
	while i <1000:
		i+=1
		print (i)
	print("end of testNum")

tag="angry"
#t = Thread(target=match.generate_tag_codebooks, args=(tag,), daemon=None)
t = Thread(target=testNums, args=())
t.daemon=True
t.start()

#all_tags_json = match.load_all_tags()
#print(all_tags_json)

#match.generate_codebooks_from_metadata()

#wav_file="/workspace/dogemotiondetector/demo/v0/data/samples/dog_bark3.wav"
#wav_file="/workspace/dogemotiondetector/demo/v0/data/samples/dog_whine.wav"
#(rate,sig) = wav.read("/workspace/dogemotiondetector/demo/v0/data/samples/dog_whine.wav")
#(rate,sig) = wav.read(wav_file)
#mfcc_feat = mfcc(sig,rate)
#fbank_feat = logfbank(sig,rate)

#print(fbank_feat[1:3,:])
#print(type(fbank_feat))
#a=[0,1,2,3,4,5,6,7,8,9]
#b=numpy.array(a)
#print(type(b))
#print(b[1:3])

sys.exit()
