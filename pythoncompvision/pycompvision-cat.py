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

import json

#################################################
#                                               #
#              Collect the Config               #
#                                               #
#################################################

with open('config.json') as config_file:
    data = json.load(config_file)

KEY = data['key']
ENDPOINT = data['endpoint']

computervision_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(KEY))

# Get an image to get its category
remote_image_url = "https://images-na.ssl-images-amazon.com/images/I/61J3H--iSHL._SX466_.jpg"
# Alternate
#remote_image_url = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/ComputerVision/Images/landmark.jpg"
# Alternate
#remote_image_url = "https://www.dmu.ac.uk/webimages/DMU-students/Hot-topics/2017/December/Leicester-Tigers-veainu-tuilagi-main.jpg"

'''
Categorize an Image - remote
This example extracts (general) categories from a remote image with a confidence score.
'''
print("===== Categorize an image - remote =====")
# Select the visual feature(s) you want.
remote_image_features = ["categories"]
# Call API with URL and features
categorize_results_remote = computervision_client.analyze_image(remote_image_url , remote_image_features)

# Print results with confidence score
print("Categories from remote image: ")
if (len(categorize_results_remote.categories) == 0):
    print("No categories detected.")
else:
    for category in categorize_results_remote.categories:
        print("'{}' with confidence {:.2f}%".format(category.name, category.score * 100))