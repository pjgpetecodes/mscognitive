from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import TextOperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import TextRecognitionMode
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
from datetime import datetime
from picamera import PiCamera
from fractions import Fraction
from PIL import Image

import os
import sys
import time
import json

#################################################
#                                               #
#               Global Variables                #
#                                               #
#################################################

global rootFilePath
global camera

#################################################
#                                               #
#               Take a Picture                  #
#                                               #
#################################################

def takePicture():

    global camera                               # Get a reference to the Camera Class
    global rootFilePath                         # Get a reference to the root File Path

    camera.resolution = (720, 480)              # Set the Camera Resolution
    #camera.framerate = Fraction(1, 3)
    #camera.shutter_speed = 3000000
    #camera.exposure_mode = 'off'
    #camera.vflip = "true"
    
    camera.iso = 1600                            # Set Camera ISO to 800 to improve pictures
    camera.rotation = 90                        # Set Camera Rotation to 90 degrees
    
    camera.start_preview()                      # Start the Camera Preview (Needs to "warm up" the Camera)

    time.sleep(2)                               # Camera Warm Up
    
    photoFileName = datetime.now().strftime("%e-%m-%Y-%H-%M-%S") + ".jpg"     # Create a Unique Filename

    photoFileName = os.path.join(rootFilePath, photoFileName)                 # Prepend the correct path to the FileName

    camera.capture(photoFileName)               # Capture an Image

    camera.stop_preview()                       # Turn off the Camera Preview

    return photoFileName                        # Return the Photo FileName

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

rootFilePath = os.path.dirname(os.path.realpath('__file__')) + '/'           # Get the Root File Path

camera = PiCamera()                                 # Create an instance of the PiCamera

# Take a photo
photoFilename = takePicture()

# Get an image to get a description
#remote_image_url = "https://petecodes.co.uk/images/skateboard.png"
#Alternate
#remote_image_url = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/ComputerVision/Images/landmark.jpg"

'''
Describe an Image - local
This example describes the contents of an image with the confidence score.
'''
print("===== Describe an image - local =====")
# Call API
description_results = computervision_client.describe_image_in_stream(open(photoFilename, 'rb') )

# Get the captions (descriptions) from the response, with confidence level
print("Description of image: ")
if (len(description_results.captions) == 0):
    print("No description detected.")
else:
    for caption in description_results.captions:
        print("'{}' with confidence {:.2f}%".format(caption.text, caption.confidence * 100))