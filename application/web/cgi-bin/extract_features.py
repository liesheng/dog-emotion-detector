#!/usr/bin/env python

from speech_features import mfcc
from speech_features import logfbank
import scipy.io.wavfile as wav
import numpy
import os
import app_config

(rate,sig) = wav.read("/workspace/long/audio/1.wav")
mfcc_feat = mfcc(sig,rate)
#fbank_feat = logfbank(sig,rate)

print(mfcc_feat[1:4,:])
#print(type(fbank_feat))
#a=[0,1,2,3,4,5,6,7,8,9]
#b=numpy.array(a)
#print(type(b))
#print(b[1:3])
