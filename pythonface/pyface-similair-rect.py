#!/usr/bin/python3

#
#################################################
#                                               #
# Title:        PyFace                          #
# FileName:     pyface.py                       #
# Author:       Pete Gallagher                  #
# Date:         05/12/2019                      #
# Version:      1.0                             #
#                                               #
#################################################
#

#################################################
#                                               #
#                   Imports                     #
#                                               #
#################################################

from time import sleep
from datetime import datetime

from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from PIL import Image, ImageDraw

import time
import sys
import os
import json

#################################################
#                                               #
#               Global Variables                #
#                                               #
#################################################

global inProgress
global rootFilePath

global KEY
global ENDPOINT

#################################################
#                                               #
#              Azure Authentication             #
#                                               #
#################################################

with open('config.json') as config_file:
    data = json.load(config_file)

KEY = data['key']
ENDPOINT = data['endpoint']

# Create an authenticated FaceClient.
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

#################################################
#                                               #
#               Dump an Object                  #
#                                               #
#################################################

def dump(obj):
  for attr in dir(obj):
    print("obj.%s = %r" % (attr, getattr(obj, attr)))

#################################################
#                                               #
#          Get the Emotion from a Picture       #
#                                               #
#################################################

def getEmotion():
    
    #
    # Get references to our Global Variables
    #
    global inProgress           # the In Progress Flag
    global scrollText           # The Scroll Text Function
    global rootFilePath         # Get a reference to the root File Path

    #
    # Begin by taking a picture using the Raspberry Pi Camera
    #
    photoFilename = os.path.join(rootFilePath, "image1.jpg")                 # Prepend the correct path to the FileName
    
    #
    # Begin our API Call
    #
    try:

        #
        # Setup and perform the Request URL adding the Paramaters, the File (in the Body) and the headers 
        #
        attributes = list(['emotion', 'age'])

        detected_faces = face_client.face.detect_with_stream(open(photoFilename, 'rb'), return_face_attributes=attributes)
        
        print("Checking if we have a person")

        #
        # Check if the API Found any faces...
        #
        if detected_faces:

            #
            # We're only interested in one person at the moment, so get the first person found...
            #
            firstPerson = detected_faces[0]

            print("Faces Detected = ", detected_faces.count(detected_faces) + 1 )

            # Detect the faces in an image that contains multiple faces
            # Each detected face gets assigned a new ID            
            #photoFilename2 = os.path.join(rootFilePath, "image2.jpg")                 # Prepend the correct path to the FileName

            # Alternate
            photoFilename2 = os.path.join(rootFilePath, "image2.jpg")                 # Prepend the correct path to the FileName

            detected_faces2 = face_client.face.detect_with_stream(open(photoFilename2, 'rb'))

            # Search through faces detected in group image for the single face from first image.
            # First, create a list of the face IDs found in the second image.
            second_image_face_IDs = list(map(lambda x: x.face_id, detected_faces2))
            # Next, find similar face IDs like the one detected in the first image.
            similar_faces = face_client.face.find_similar(face_id=firstPerson.face_id, face_ids=second_image_face_IDs)
            if not similar_faces[0]:
                print('No similar faces found in', photoFilename2, '.')
            else:
                # Print the details of the similar faces detected
                print('Similar faces found in', photoFilename2 + ':')
                for face in similar_faces:
                    first_image_face_ID = face.face_id
                    # The similar face IDs of the single face image and the group image do not need to match, they are only used for identification purposes in each image.
                    # The similar faces are matched using the Cognitive Services algorithm in find_similar().
                    face_info = next(x for x in detected_faces2 if x.face_id == first_image_face_ID)
                    if face_info:
                        print('  Face ID: ', first_image_face_ID)
                        print('  Face rectangle:')
                        print('    Left: ', str(face_info.face_rectangle.left))
                        print('    Top: ', str(face_info.face_rectangle.top))
                        print('    Width: ', str(face_info.face_rectangle.width))
                        print('    Height: ', str(face_info.face_rectangle.height))

                        # Convert width height to a point in a rectangle
                        def getRectangle(faceDictionary):
                            rect = faceDictionary.face_rectangle
                            left = rect.left
                            top = rect.top
                            bottom = left + rect.height
                            right = top + rect.width
                            return ((left, top), (bottom, right))

                        img = Image.open(photoFilename2)

                        # For each face returned use the face rectangle and draw a red box.
                        print('Drawing rectangle around face... see popup for results.')
                        draw = ImageDraw.Draw(img)
                        draw.rectangle(getRectangle(face_info), outline="red", width=2)                            

                        # Display the image in the users default image browser.
                        img.show()

            inProgress = False          # Clear the In Progress flag
            
            return firstPerson          # Return our data

        else:

            print("Failed to get face")
            inProgress = False          # Clear the In Progress flag
            return                      # Return nothing

    except Exception as e:
        
        print(e)
        inProgress = False              # Clear the In Progress flag
        return                          # Return nothing

#################################################
#                                               #
#               Initial Setup                   #
#                                               #
#################################################

print("Begin Initial Setup")

inProgress = False                                  # Make sure we clear that we're currently processing an image

rootFilePath = os.path.dirname(os.path.realpath('__file__')) + '/'           # Get the Root File Path

print("Initial Setup Complete")

#################################################
#                                               #
#            Begin the Main Application         #
#                                               #
#################################################

getEmotion()                                        # Begin Processing an Emotion