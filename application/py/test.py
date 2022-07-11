#!/usr/bin/env python

from speech_features import mfcc
from speech_features import logfbank
import scipy.io.wavfile as wav
import numpy

(rate,sig) = wav.read("data/samples/english.wav")
mfcc_feat = mfcc(sig,rate)
fbank_feat = logfbank(sig,rate)

print(fbank_feat[1:3,:])
print(type(fbank_feat))
a=[0,1,2,3,4,5,6,7,8,9]
b=numpy.array(a)
print(type(b))
print(b[1:3])
