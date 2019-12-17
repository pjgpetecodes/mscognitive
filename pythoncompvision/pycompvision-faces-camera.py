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
#          Get the Bounding Rectangle           #
#                                               #
#################################################

def getRectangle(faceDictionary):
    rect = faceDictionary.face_rectangle
    left = rect.left
    top = rect.top
    bottom = left + rect.height
    right = top + rect.width
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

font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 16)

computervision_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(KEY))

rootFilePath = os.path.dirname(os.path.realpath('__file__')) + '/'           # Get the Root File Path

camera = PiCamera()                                 # Create an instance of the PiCamera

# Take a photo
photoFilename = takePicture()

'''
Detect Faces - remote
This example detects faces in a remote image, gets their gender and age, 
and marks them with a bounding box.
'''
print("===== Detect Faces - remote =====")
# Select the visual feature(s) you want.
remote_image_features = ["faces"]
# Call the API with remote URL and features
detect_faces_results_remote = computervision_client.analyze_image_in_stream(open(photoFilename, 'rb'), remote_image_features)

# Print the results with gender, age, and bounding box
print("Faces in the remote image: ")
if (len(detect_faces_results_remote.faces) == 0):
    print("No faces detected.")
else:
    img = Image.open(photoFilename)
    # For each face returned use the face rectangle and draw a red box.
    print('Drawing rectangle around face... see popup for results.')
    draw = ImageDraw.Draw(img)
        
    for face in detect_faces_results_remote.faces:
        print("'{}' of age {} at location {}, {}, {},   {}".format(face.gender, face.age, \
        face.face_rectangle.left, face.face_rectangle.top, \
        face.face_rectangle.left + face.face_rectangle.width, \
        face.face_rectangle.top + face.face_rectangle.height))

        draw.rectangle(getRectangle(face), outline="red", width=2)
        draw.text((face.face_rectangle.left, face.face_rectangle.top + face.face_rectangle.height), face.gender + " aged " + str(face.age), font=font)
        #draw.text((face.face_rectangle.top, face.face_rectangle.left + face.face_rectangle.height), face.gender + " " + str(face.age), fill='green')                       

    # Display the image in the users default image browser.
    img.show()