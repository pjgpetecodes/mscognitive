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
        # We can pass in age, gender, headPose, smile, facialHair, glasses, emotion, hair, makeup, occlusion, accessories, blur, exposure, noise
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

            #print("----------------------------")

            #print("Face Rectangle = ")
            #print("Left = " + str(firstPerson.face_rectangle.left))
            #print("Top = " + str(firstPerson.face_rectangle.top))
            #print("Height = " + str(firstPerson.face_rectangle.height))
            #print("Width = " + str(firstPerson.face_rectangle.width))
            
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
            
            #if k == "Happy":
            #elif k == "Sad":
            #elif k == "Surprised":
            #elif k == "Neutral":
            #elif k == "Angry":
            #elif k == "Contemptful":
            #elif k == "Disgusted":
            #elif k == "Fearful":

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