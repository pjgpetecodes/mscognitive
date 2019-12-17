from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient

import os
import sys
import json

with open('config.json') as config_file:
    data = json.load(config_file)

# Get the Config Data
prediction_key = data['predictionKey']
project_id = data['projectID']
endPoint = data['endPoint']

# Now there is a trained endpoint that can be used to make a prediction
predictor = CustomVisionPredictionClient(prediction_key, endpoint=endPoint)

publish_iteration_name = "Iteration1"

rootFilePath = os.path.dirname(os.path.realpath('__file__')) + '/'           # Get the Root File Path

with open(rootFilePath + "testimage3.jpg", "rb") as image_contents:
    results = predictor.classify_image(
        project_id, publish_iteration_name, image_contents.read())

    # Display the results.
    for prediction in results.predictions:
        print("\t" + prediction.tag_name +
              ": {0:.2f}%".format(prediction.probability * 100))