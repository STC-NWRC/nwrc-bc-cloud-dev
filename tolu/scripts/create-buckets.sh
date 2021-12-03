#!/bin/bash
kubectl create -f /home/airflow/gcs/dags/scripts/create_pod_data.yaml

sleep 10

array=(for i in $(seq 0 ${NUM})
do
    kubectl exec -n default data-transfer-pod -- /bin/sh -c 'val=(cat /temp/datastore/node_${i}/output/result.txt); echo $a;'
done)

sum=$(IFS=+; echo "$((${array[*]}))")

echo $sum >> /home/airflow/gcs/dags/final_result

kubectl delete -f /home/airflow/gcs/dags/scripts/create_pod_data.yaml