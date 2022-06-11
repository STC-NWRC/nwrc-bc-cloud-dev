#!/bin/bash

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
source ./global-parameters.txt

echo
echo PROJECT_ID=${PROJECT_ID}
echo ENVIRONMENT_NAME=${ENVIRONMENT_NAME}
echo LOCATION=${LOCATION}
echo ZONE=${ZONE}
echo EXTERNAL_BUCKET=${EXTERNAL_BUCKET}
echo BOQ_BUCKET=${BOQ_BUCKET}
echo WILLISTON_BUCKET=${WILLISTON_BUCKET}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# set the active project
echo; echo Executing: gcloud config set project ${PROJECT_ID}
gcloud config set project ${PROJECT_ID}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# Following instructions from:
# https://cloud.google.com/composer/docs/how-to/managing/creating#gcloud_1
# https://cloud.google.com/composer/docs/concepts/versioning/composer-versions#images
# https://cloud.google.com/compute/docs/general-purpose-machines
# https://cloud.google.com/composer/pricing#machine-type
# https://cloud.google.com/composer/pricing#db-machine-types
# https://cloud.google.com/composer/pricing#ws-machine-types

IMAGE_VERSION="composer-1.17.4-airflow-1.10.15"
NODE_COUNT=3
SCHEDULER_COUNT=1
# DISK_SIZE=64
# DISK_SIZE=500
# NODE_MACHINE_TYPE=n2-standard-16
# NODE_MACHINE_TYPE=n1-standard-2
DISK_SIZE=30
NODE_MACHINE_TYPE=n1-standard-2
SQL_MACHINE_TYPE=db-n1-standard-2
WS_MACHINE_TYPE=composer-n1-webserver-2

echo; echo Executing: gcloud composer environments create ${ENVIRONMENT_NAME} ...
gcloud composer environments create ${ENVIRONMENT_NAME} \
    --location ${LOCATION} \
    --zone     ${ZONE} \
    --image-version ${IMAGE_VERSION} \
    --node-count ${NODE_COUNT} \
    --disk-size ${DISK_SIZE} \
    --machine-type ${NODE_MACHINE_TYPE} \
    --cloud-sql-machine-type ${SQL_MACHINE_TYPE} \
    --web-server-machine-type ${WS_MACHINE_TYPE}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# set kubectl credentials (required by next command -- setting AirFlow variables)
# Use the gcloud composer command to connect the kubectl command to the cluster.
# https://cloud.google.com/composer/docs/how-to/using/installing-python-dependencies#viewing_installed_python_packages

CLUSTER_NAME=`gcloud container clusters list | tail -n +2 | awk '{print $1}'`
echo; echo CLUSTER_NAME=${CLUSTER_NAME}

echo; echo Executing: gcloud container clusters get-credentials ${CLUSTER_NAME} --zone ${ZONE}
gcloud container clusters get-credentials ${CLUSTER_NAME} --zone ${ZONE}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
AIRFLOW_CLUSTER_NAMESPACE=`kubectl get namespaces | egrep 'airflow' | awk '{print $1}'`
echo; echo AIRFLOW_CLUSTER_NAMESPACE=${AIRFLOW_CLUSTER_NAMESPACE}

AIRFLOW_POD_NAME=`kubectl get pods -n ${AIRFLOW_CLUSTER_NAMESPACE} | egrep 'worker' | head -n 1 | awk '{print $1}'`
echo; echo AIRFLOW_POD_NAME=${AIRFLOW_POD_NAME}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
##### install Python dependencies
# sleep 20
# echo; echo Executing: gcloud composer environments update -- adding python dependencies
# gcloud composer environments update ${ENVIRONMENT_NAME} --location ${LOCATION} \
#    --update-pypi-packages-from-file python-dependencies.txt

### set environment variables
sleep 20
echo; echo Executing: gcloud composer environments update -- setting environment variables
gcloud composer environments update ${ENVIRONMENT_NAME} --location ${LOCATION} \
   --update-env-variables=WILLISTON_BUCKET=${WILLISTON_BUCKET},BOQ_BUCKET=${BOQ_BUCKET},EXTERNAL_BUCKET=${EXTERNAL_BUCKET},ENVIRONMENT_NAME=${ENVIRONMENT_NAME},LOCATION=${LOCATION},ZONE=${ZONE},CLUSTER_NAME=${CLUSTER_NAME},AIRFLOW_CLUSTER_NAMESPACE=${AIRFLOW_CLUSTER_NAMESPACE}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
