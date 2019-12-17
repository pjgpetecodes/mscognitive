from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import TextOperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import TextRecognitionMode
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time
import glob
import json

with open('config.json') as config_file:
    data = json.load(config_file)

KEY = data['key']
ENDPOINT = data['endpoint']

computervision_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(KEY))

directory_name = "objectnet"

objectnet_photo = 'hammer.jpg'
#objectnet_photo = 'hammer-mod.jpg'
#objectnet_photo = 'hammer-cropped.jpg'
#objectnet_photo = 'hammer_on_bed.jpg'
#objectnet_photo = 'hammer_being_held.jpg'

#objectnet_photo = 'chair_on_floor.jpg'
#objectnet_photo = 'chair_from_above.jpg'
#objectnet_photo = 'ovenglove_on_counter.jpg'
#objectnet_photo = 'ovengloves_on_bed.jpg'

# Get test image
test_image_array = glob.glob1(directory_name, objectnet_photo)
image = open(directory_name + "/" + test_image_array[0], 'r+b')

'''
Describe an Image - remote
This example describes the contents of an image with the confidence score.
'''
print("===== Describe an image - remote =====")
# Call API
description_results = computervision_client.describe_image_in_stream( image )

# Get the captions (descriptions) from the response, with confidence level
print("Description of remote image: ")
if (len(description_results.captions) == 0):
    print("No description detected.")
else:
    for caption in description_results.captions:
        print("'{}' with confidence {:.2f}%".format(caption.text, caption.confidence * 100))