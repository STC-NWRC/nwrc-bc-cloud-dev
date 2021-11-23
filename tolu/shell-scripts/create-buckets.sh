#!/bin/bash
######Connect to GKE Cluster 
gcloud container clusters get-credentials us-central1-toyworkflow-21399c22-gke --zone us-central1-c --project idyllic-anvil-331918 
######Copy the updated Composer bucket to Cluster
buckets=($BUCKETS_NAME)
for i in $(seq 0 ${#buckets[@]})
do
    mkdir ${buckets[$i]}
    gsutil rsync -r gs://${buckets[$i]} ./${buckets[$i]}
done