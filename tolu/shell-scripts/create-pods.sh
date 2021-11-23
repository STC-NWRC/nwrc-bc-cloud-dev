#!/bin/bash
######Copy the new code to the running pod using kubectl 
buckets=$1
for bkt in $buckets
do
    kubectl cp ./${bkt} $(kubectl get pods | grep Running | grep pod_${bkt} | awk ‘{print $1}’):/root/.dbt
done