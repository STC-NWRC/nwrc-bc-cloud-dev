#!/bin/bash

PROJECT_ID=fpca-336015
LOCATION=us-central1
ZONE=us-central1-a
EXTERNAL_BUCKET=gs://fpca-bay-of-quinte-test

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# set the active project
echo
echo setting active project to: ${PROJECT_ID}
gcloud config set project ${PROJECT_ID}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### list contents of a bucket folder
gsutil ls ${EXTERNAL_BUCKET}/*

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### copying contents of img
gsutil -m cp -r ${EXTERNAL_BUCKET}/img/* .

