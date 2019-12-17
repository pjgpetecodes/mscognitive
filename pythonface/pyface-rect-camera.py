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

from PIL import Image, ImageDraw, ImageFont
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

global inProgress
global rootFilePath

global KEY
global ENDPOINT

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
    global rootFilePath         # Get a reference to the root File Path

    # Take a photo
    photoFilename = takePicture()

    #
    # Begin our API Call
    #
    try:

        #
        # Setup and perform the Request URL adding the Paramaters, the File (in the Body) and the headers 
        #
        # We can pass in 'age', 'gender', 'headPose', 'smile', 'facialHair', 'glasses', 'emotion', 'hair', 'makeup', 'occlusion', 'accessories', 'blur', 'exposure', 'noise'
        #
        attributes = list(['emotion', 'age'])
        #attributes = list(['age', 'gender', 'headPose', 'smile', 'facialHair', 'glasses', 'emotion', 'hair', 'makeup', 'occlusion', 'accessories', 'blur', 'exposure', 'noise'])
        
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

            #dump(firstPerson.face_attributes)
                
            print("Faces Detected = ", detected_faces.count(detected_faces) + 1 )

            print("----------------------------")

            print("Face Rectangle = ")
            print("Left = " + str(firstPerson.face_rectangle.left))
            print("Top = " + str(firstPerson.face_rectangle.top))
            print("Height = " + str(firstPerson.face_rectangle.height))
            print("Width = " + str(firstPerson.face_rectangle.width))
            
            print("----------------------------")
            
            print("Emotions = ")
            print("Happiness = " + str(firstPerson.face_attributes.emotion.happiness))
            print("Sadness = " + str(firstPerson.face_attributes.emotion.sadness))
            print("Surprised = " + str(firstPerson.face_attributes.emotion.surprise))
            print("Neutral = " + str(firstPerson.face_attributes.emotion.neutral))
            print("Angry = " + str(firstPerson.face_attributes.emotion.anger))
            print("Contemptful = " + str(firstPerson.face_attributes.emotion.contempt))
            print("Disgusted = " + str(firstPerson.face_attributes.emotion.disgust))
            print("Fearful = " + str(firstPerson.face_attributes.emotion.fear))
            
            print("----------------------------")
            
            #
            # Get the Emotion Scores
            #
            firstPersonScores = firstPerson.face_attributes.emotion
            
            #
            # Create a custom JSON object to hold the data in a more friendly way
            #
            emotions = {'Happy': firstPersonScores.happiness * 100,
                        'Sad' : firstPersonScores.sadness * 100,
                        'Surprised' : firstPersonScores.surprise * 100,
                        'Neutral' : firstPersonScores.neutral * 100,
                        'Angry' : firstPersonScores.anger * 100,
                        'Contemptful' : firstPersonScores.contempt * 100,
                        'Disgusted' : firstPersonScores.disgust * 100,
                        'Fearful' : firstPersonScores.fear * 100} 

            #
            # Sort the emotions found by the value in a decending order, so the highest result is the first item in the list
            #
            sortedEmotions = sorted(emotions.items(), key=lambda x: x[1], reverse = True)

            #
            # Get the Key and Value of the first item in the list (the Emotion with the highest score)
            #
            k, v = next(iter(sortedEmotions))

            print("The top emotion is = " + k)
            
            print("----------------------------")
            
            if k == "Happy":
                color = "pink"
            elif k == "Sad":
                color = "blue"
            elif k == "Surprised":
                color = "organge"
            elif k == "Neutral":
                color = "white"
            elif k == "Angry":
                color = "red"
            elif k == "Contemptful":
                color = "brown"
            elif k == "Disgusted":
                color = "green"
            elif k == "Fearful":
                color = "yellow"

            # Convert width height to a point in a rectangle
            def getRectangle(faceDictionary):
                rect = faceDictionary.face_rectangle
                left = rect.left
                top = rect.top
                bottom = rect.left + rect.height
                right = rect.top + rect.width
                return ((left, top), (bottom, right))

            img = Image.open(photoFilename)

            # For each face returned use the face rectangle and draw a red box.
            print('Drawing rectangle around face... see popup for results.')
            draw = ImageDraw.Draw(img)
            for face in detected_faces:
                draw.rectangle(getRectangle(face), outline=color, width=2)

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

camera = PiCamera()                                 # Create an instance of the PiCamera

print("Initial Setup Complete")

#################################################
#                                               #
#            Begin the Main Application         #
#                                               #
#################################################

getEmotion()                                        # Begin Processing an Emotion