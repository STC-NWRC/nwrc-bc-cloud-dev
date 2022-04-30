#!/bin/bash

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
source ./global-parameters.txt

# set the active project
echo; echo setting active project to: ${PROJECT_ID}
gcloud config set project ${PROJECT_ID}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### upload a DAG to Composer environment
echo; echo Executing: gcloud composer environments storage dags import
gcloud composer environments storage dags import \
    --environment ${ENVIRONMENT_NAME} \
    --location ${LOCATION} \
    --source dag-fpca.py

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
echo; echo Executing: sleep 60
sleep 60

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### trigger the workflow
echo; echo Executing: gcloud composer environments run dags trigger
gcloud composer environments run ${ENVIRONMENT_NAME} \
    --location ${LOCATION} \
    trigger_dag -- fpca_gke --run_id=`date "+%F-%H-%M-%S"`
    # dags trigger -- fpca_gke --run_id=`date "+%F-%H-%M-%S"`
    # trigger_dag -- fpca_gke
