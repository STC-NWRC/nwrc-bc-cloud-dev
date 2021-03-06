#!/bin/bash

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
source ./global-parameters.txt

### ########################################### ###
### The following gsutil commands work on a Composer worker node.
###
### Below, we assume the following environment variables have been set:
###
###     PROJECT_ID=fpca-336015
###     ENVIRONMENT_NAME=${PROJECT_ID}
###     LOCATION=us-central1
###     ZONE=us-central1-a
###     EXTERNAL_BUCKET=gs://${PROJECT_ID}-xbucket
###     BOQ_BUCKET=gs://fpca-bay-of-quinte-test
###     WILLISTON_BUCKET=gs://fpca-williston-a
###     SERVICE_ACCOUNT_ID=fpca-service-account
###     SERVICE_ACCOUNT_KEY_FILE=01-SECRETS/service-account-keys/fpca-service-account-key-2022-06-10-a.json
###

### ########################################### ###
###
### In order to allow a Kubernetes pod to read from and write to the project
### external bucket, proceed as follows:
### (a)  Create a service account.
### (b)  Create a service account key (JSON) for the service account in (a).
### (c)  Assign Object Admin role to the service account; add resulting IAM
###      policy to external bucket.
### (d)  Create a Kubernetes secret from service account key file
###      (as part of Composer Environment creation).
### (e)  Transfer -- via Kubernetes secret -- the service account key (JSON) to
###      each Kubernetes pod that needs to read from or write to project external
###      bucket.
### (f)  On each such Kubernetes pod, activate service account.
###

### ########################################### ###
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### (a)  Create service account.

# echo;echo gcloud iam service-accounts create ${SERVICE_ACCOUNT_ID} --display-name=${SERVICE_ACCOUNT_ID}
#           gcloud iam service-accounts create ${SERVICE_ACCOUNT_ID} --display-name=${SERVICE_ACCOUNT_ID}

sleep 10

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### (b)  Create service account key.
###
### Visit the following web page:
### https://cloud.google.com/iam/docs/creating-managing-service-account-keys
### https://console.cloud.google.com/projectselector2/iam-admin/serviceaccounts

# echo;echo gcloud iam service-accounts keys create ${SERVICE_ACCOUNT_KEY_FILE} --iam-account=${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com
#           gcloud iam service-accounts keys create ${SERVICE_ACCOUNT_KEY_FILE} --iam-account=${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com

sleep 10

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### list service accounts

echo;echo gcloud iam service-accounts list
          gcloud iam service-accounts list

sleep 10

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### (c)  Assign to the service account access roles to various Storage buckets.
###
### grant binding to ${EXTERNAL_BUCKET}:
### https://cloud.google.com/iam/docs/creating-managing-service-accounts#iam-service-accounts-create-gcloud
### https://cloud.google.com/iam/docs/understanding-roles

echo;echo gsutil iam ch serviceAccount:${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com:objectAdmin ${EXTERNAL_BUCKET}
#         gsutil iam ch serviceAccount:${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com:objectAdmin ${EXTERNAL_BUCKET}

for TEMP_BUCKET in ${BOQ_BUCKET} ${WILLISTON_BUCKET}
do
    echo;echo gsutil iam ch serviceAccount:${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com:objectViewer ${TEMP_BUCKET}
    #         gsutil iam ch serviceAccount:${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com:objectViewer ${TEMP_BUCKET}
done

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### get IAM permissions of Storage buckets

for TEMP_BUCKET in ${EXTERNAL_BUCKET} ${BOQ_BUCKET} ${WILLISTON_BUCKET}
do
    echo;echo gsutil iam get ${TEMP_BUCKET}
              gsutil iam get ${TEMP_BUCKET}
done

### ########################################### ###
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### (d)  Create a Kubernetes secret from the service account key file.
###      This step is needed as part of the Composer Environment creation step.
###      Once the following steps have been performed:
###
###      (*)  the service account has been created,
###      (*)  access roles to the various Storage buckets have been assigned to the service account,
###      (*)  a service account key have been created,
###
###      then we can "upload" to a active Composer Environment
###      the service account key as a Kubernetes secret.
###      This Kubernetes secret (service account key) can then be securely
###      communicated to Kubernetes pods, which can then use the service account
###      key to access the Storage buckets.
###

# echo;echo kubectl create secret generic fpca-secret --from-file=${SERVICE_ACCOUNT_KEY_FILE}
#           kubectl create secret generic fpca-secret --from-file=${SERVICE_ACCOUNT_KEY_FILE}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### (e)  Transfer service account key to Kubernetes pods.

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### (f)  On each such Kubernetes pod, activate service account.
###
### The following gcloud is to be run on each Kubernetes pod that needs to read
### from or write to the project external bucket.

# gcloud auth activate-service-account --key-file /var/secrets/google/gauss100-2021-11-13-a-f52029c2c997.json
