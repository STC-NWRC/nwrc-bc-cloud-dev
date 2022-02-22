This DAG uses 2 major airflow operators (BashOperator and KurbernetesPodOperator) and the DummyOperator(just for testing purpose).

The purpose of these 2 major operators are explained below:

Using the BashOperator, we run commands for managing the dynamic persistent disk that will be mounted on the KubernetesPodOperator for data access (i.e read/write) by using two (i.e create-pods.sh and collating.sh) shell scripts and three (i.e create_sc.yaml,create_pvc.yaml,create_pod_data.yaml) yaml scripts. All these scripts can be found in the scripts folder.

The purpose of the three yaml files are further explained below:

create_sc.yaml: This is to create a storageclass for the dynamic persistent disk

create_pvc.yaml: This is to create the persistent volume claim.

create_pod_data.yaml: This is used to create the pod that will be used to migrate data from the bucket to the persistent disk that will be mounted on the KubernetesPodOperator. Through this method, data that are needed to be processed on each kubernete node can be read.

Using the KubernetesPodOperator, we can run the docker images on n-nodes by mounting the persistent volume object created using the BashOperator and the supporting files(i.e. the yaml and shell scripts). The persistent volume object serves as a storage for reading and writing into each of the pods deployed on the kubernete nodes.

Once the workflow is done, the "collating.sh" script does the summation of the all the results from each kubernete nodes and the final clean-up by deleting the pod used for data migration, the persistnet disk, and the storage class.