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

match.generate_codebooks_from_metadata()
