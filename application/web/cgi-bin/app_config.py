#!/usr/bin/python

import sys
import math
import json
import os
import traceback

#environment specific
close_fds=False

base_path=os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
data_path=base_path+"/data"
system_data_path=data_path+"/system"
samples_path=data_path+"/samples"
upload_path=data_path+"/uploaded"
thumbnail_image_path=upload_path+"/thumbnail"
metadata_path=data_path+"/metadata"
mfcc_path=metadata_path+"/mfcc"
tags_path=metadata_path+"/tags"
codebook_path=data_path+"/codebooks/current"
tag_to_generate_codebook=True

version_path="v0.2"
#
SYSTEM_USER_ID="0"
MAX_DATA_SIZE=256
SIZE_CODEBOOK=128

#dynamic VQ
dvq_scheme_n=3
dvq_scheme_a=[1/3,1/3] #the last one is inferred

py_executable=sys.executable
ffmpeg="/usr/bin/ffmpeg"
thumbnail_image_type=".jpeg"

try:
	url = os.environ["REQUEST_URI"] 
	server_addr=os.environ["SERVER_ADDR"]
	server_port=os.environ["SERVER_PORT"]
	download_baseUrl="http://"+server_addr+":"+server_port+"/"+version_path+"/data/uploaded"
except:
	download_baseUrl=None
	traceback.print_exc(file=sys.stderr)
