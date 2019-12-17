# Pi Emotion Sensor

## What it's about:

A collection of Raspberry Pi Python Examples for Azure Cognitive Services.

## Installation Instructions:

### Hardware:

You'll need a Raspberry Pi with a Camera installed.

### Azure Cognitive Services:

Create a Face and Computer Vision Azure Cognitive Services Resource at;

https://portal.azure.com

Grab;

- Key1 (KEY)
- Endpoint (ENDPOINT)

Fill the details into the associated config.json file in each directory

## Azure Custom Vision

Create a Custom Vision Service at;

https://www.customvision.ai/

### Azure Cognitive Services SDK:

Install the Azure Cognitive Services SDK using;

```shell
python3 -m pip install cognitive-face
python3 -m pip install --upgrade azure-cognitiveservices-vision-face
python3 -m pip install --upgrade azure-cognitiveservices-vision-computervision
python3 -m pip install azure-cognitiveservices-vision-customvision
```
