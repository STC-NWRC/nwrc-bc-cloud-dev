#!/bin/bash
n=$1

kubectl create -f /home/airflow/gcs/dags/scripts/create_pod_data.yaml

sleep 10

array=$(kubectl exec -n default data-transfer-pod -- /bin/sh -c 'for i in $(seq 1 '"${n}"')
                                                                    do
                                                                    echo $(cat /temp/datastore/node_${i}/output/result.txt)
                                                                    done';)


sum=0
for i in $array
do
    sum=$(echo "$sum $i" | awk '{print $1 + $2}')
    
done


echo $sum > ./final_result.txt

gsutil cp ./final_result.txt gs://us-central1-toyworkflow-21399c22-bucket

rm -f ./final_result.txt

kubectl delete -f /home/airflow/gcs/dags/scripts/create_pod_data.yaml

kubectl delete -f /home/airflow/gcs/dags/scripts/create_pvc.yaml

kubectl delete -f /home/airflow/gcs/dags/scripts/create_sc.yaml