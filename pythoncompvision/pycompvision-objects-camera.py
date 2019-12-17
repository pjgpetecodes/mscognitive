from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import TextOperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import TextRecognitionMode
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from picamera import PiCamera
from fractions import Fraction

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

    camera.resolution = (1920, 1080)            # Set the Camera Resolution
    #camera.framerate = Fraction(1, 3)
    #camera.shutter_speed = 3000000
    #camera.exposure_mode = 'off'
    #camera.vflip = "true"
    
    camera.iso = 800                            # Set Camera ISO to 800 to improve pictures
    camera.rotation = 90                        # Set Camera Rotation to 90 degrees
    
    camera.start_preview()                      # Start the Camera Preview (Needs to "warm up" the Camera)

    time.sleep(2)                               # Camera Warm Up
    
    photoFileName = datetime.now().strftime("%e-%m-%Y-%H-%M-%S") + ".jpg"     # Create a Unique Filename

    photoFileName = os.path.join(rootFilePath, photoFileName)                 # Prepend the correct path to the FileName

    camera.capture(photoFileName)               # Capture an Image

    camera.stop_preview()                       # Turn off the Camera Preview

    return photoFileName                        # Return the Photo FileName

# Convert width height to a point in a rectangle
def getRectangle(objectDictionary):
    rect = objectDictionary.rectangle
    left = rect.x
    top = rect.y
    bottom = rect.x + rect.w
    right = rect.y + rect.h
    return ((left, top), (bottom, right))

#################################################
#                                               #
#              Collect the Config               #
#                                               #
#################################################

with open('config.json') as config_file:
    data = json.load(config_file)

KEY = data['key']
ENDPOINT = data['endpoint']

font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 36)

computervision_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(KEY))

rootFilePath = os.path.dirname(os.path.realpath('__file__')) + '/'           # Get the Root File Path

camera = PiCamera()                                 # Create an instance of the PiCamera

# Take a photo
photoFilename = takePicture()

'''
Detect Objects - remote
This example detects different kinds of objects with bounding boxes in a remote image.
'''
print("===== Detect Objects - remote =====")
# Call API with URL
detect_objects_results_remote = computervision_client.detect_objects_in_stream(open(photoFilename, 'rb'))

# Print detected objects results with bounding boxes
print("Detecting objects in remote image:")
if len(detect_objects_results_remote.objects) == 0:
    print("No objects detected.")
else:

    img = Image.open(photoFilename)
    # For each face returned use the object rectangle and draw a red box.
    print('Drawing rectangle around objects... see popup for results.')
    draw = ImageDraw.Draw(img)

    for object in detect_objects_results_remote.objects:
        print("object of type ", object.object_property, " with a confidence of ", object.confidence, "at location {}, {}, {}, {}".format( \
        object.rectangle.x, object.rectangle.x + object.rectangle.w, \
        object.rectangle.y, object.rectangle.y + object.rectangle.h))

        draw.rectangle(getRectangle(object), outline="red", width=2)

        if object.rectangle.y + object.rectangle.h < 1000:
            draw.text((object.rectangle.x, object.rectangle.y + object.rectangle.h), object.object_property + " " + str(object.confidence), font=font)
        else:
            draw.text((object.rectangle.x, object.rectangle.y - 40), object.object_property + " " + str(object.confidence), font=font)


    # Display the image in the users default image browser.
    img.show()