#!/bin/bash
######Copy the new code to the running pod using kubectl 


kubectl create -f /home/airflow/gcs/dags/scripts/create_sc.yaml

sleep 5

kubectl create -f /home/airflow/gcs/dags/scripts/create_pvc.yaml

sleep 5

kubectl create -f /home/airflow/gcs/dags/scripts/create_pod_data.yaml

sleep 30

kubectl exec -n default data-transfer-pod -- /bin/sh -c 'mkdir /temp/scripts/; cd /temp/scripts; pwd; exit'

kubectl cp /home/airflow/gcs/dags/aux_code.py default/data-transfer-pod:/temp/scripts

