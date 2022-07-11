#!/usr/bin/env python

from speech_features import mfcc
from speech_features import logfbank
import scipy.io.wavfile as wav
import numpy
import match
import json
import sys
from threading import Thread
import subprocess
import app_config
import time

#p = subprocess.Popen([app_config.py_executable, 'generate_codebooks.py'], close_fds=True, stderr=subprocess.STDOUT,stdout=subprocess.PIPE)
paramList=["-i", "1.mp4", "-vframes", "1", "1.jpeg"]
p = subprocess.Popen(["/usr/bin/ffmpeg"]+paramList, close_fds=True, stderr=subprocess.PIPE,stdout=subprocess.PIPE)
#while True:
#	data = p.stderr.readline() #block / wait
#	print data
##time.sleep(.1)
