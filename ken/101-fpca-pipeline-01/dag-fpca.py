
# from datetime import timedelta, datetime
import datetime

from airflow import models
from airflow.operators.bash_operator   import BashOperator
from airflow.operators.dummy_operator  import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.cncf.kubernetes.operators import kubernetes_pod
from airflow.models import Variable
from airflow.kubernetes.volume import Volume
from airflow.kubernetes.volume_mount import VolumeMount
from airflow.kubernetes.secret import Secret

import os

bucket_list     = ['fpca-bay-of-quinte-test','fpca-williston-a']
external_bucket = 'fpca-336015-xbucket'

JOB_NAME = 'fpca_gke'

start_date = datetime.datetime(2021, 1, 31)

default_args = {
    'start_date': start_date,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': datetime.timedelta(minutes=1)
}

secret_volume_service_account_key = Secret(
    # Name of Kubernetes Secret
    secret='fpca-secret',
    # type of secret
    deploy_type='volume',
    # Key in the form of service account file name
    key='fpca-service-account-key-2022-06-10-a.json',
    # Path where we mount the secret as volume
    deploy_target='/var/secrets/google'
    )

with models.DAG(JOB_NAME,
                default_args=default_args,
                schedule_interval=None,
                concurrency=3,
                catchup=False
                ) as dag:

    create_node_pool_command = """
    # Set some environment variables in case they were not set already

    # [ -z "${NODE_COUNT}" ] && NODE_COUNT=6
    # [ -z "${MACHINE_TYPE}" ] && MACHINE_TYPE=n1-standard-2
    # [ -z "${MACHINE_TYPE}" ] && MACHINE_TYPE=custom-4-5120
    # [ -z "${MACHINE_TYPE}" ] && MACHINE_TYPE=custom-16-65536
    # [ -z "${MACHINE_TYPE}" ] && MACHINE_TYPE=custom-80-262144
    # [ -z "${NODE_DISK_SIZE}" ] && NODE_DISK_SIZE=20
    # [ -z "${NODE_DISK_SIZE}" ] && NODE_DISK_SIZE=64
    # [ -z "${NODE_DISK_SIZE}" ] && NODE_DISK_SIZE=128
    # [ -z "${NODE_DISK_SIZE}" ] && NODE_DISK_SIZE=512

    [ -z "${NODE_COUNT}" ] && NODE_COUNT=3
    [ -z "${MACHINE_TYPE}" ] && MACHINE_TYPE=n1-standard-2
    [ -z "${SCOPES}" ] && SCOPES=default,cloud-platform
    [ -z "${NODE_DISK_SIZE}" ] && NODE_DISK_SIZE=20

    echo;echo whoami=`whoami`
    echo;echo pwd; pwd
    echo;echo cd /home/airflow/; cd /home/airflow/
    echo;echo pwd; pwd

    echo;echo COMPOSER_GKE_ZONE=${COMPOSER_GKE_ZONE}
    echo;echo COMPOSER_GKE_NAME=${COMPOSER_GKE_NAME}
    echo;echo CLUSTER_NAME=${CLUSTER_NAME}
    echo;echo NODE_POOL={NODE_POOL}
    echo;echo MACHINE_TYPE=${MACHINE_TYPE}
    echo;echo NODE_COUNT=${NODE_COUNT}
    echo;echo NODE_DISK_SIZE=${NODE_DISK_SIZE}
    echo;echo SCOPES=${SCOPES}

    ### It is important to set container/cluster; otherwise, Composer would
    ### throw an error at the node pool creation command below
    ### due to the fact that the node pool creation would require more vCPU
    ### than regional vCPU quota.
    echo;echo Executing: sudo gcloud config set container/cluster ${COMPOSER_GKE_NAME}
    sudo gcloud config set container/cluster ${COMPOSER_GKE_NAME}

    sleep 10

    ### set kubectl credentials (required by subsequent commands)
    ### Use the gcloud composer command to connect the kubectl command to the cluster.
    ### https://cloud.google.com/composer/docs/how-to/using/installing-python-dependencies#viewing_installed_python_packages
    echo;echo Executing: sudo gcloud container clusters get-credentials ${CLUSTER_NAME} --zone ${ZONE}
    sudo gcloud container clusters get-credentials ${CLUSTER_NAME} --zone ${ZONE}

    sleep 10

    echo;echo Executing: gcloud container node-pools create {NODE_POOL} ...
    gcloud container node-pools create {NODE_POOL} \
        --project=${GCP_PROJECT}       --cluster=${COMPOSER_GKE_NAME} --zone=${COMPOSER_GKE_ZONE} \
        --machine-type=${MACHINE_TYPE} --num-nodes=${NODE_COUNT}      --disk-size=${NODE_DISK_SIZE} \
        --enable-autoscaling --min-nodes 1 --max-nodes ${NODE_COUNT} \
        --scopes=${SCOPES} \
        --enable-autoupgrade

    ### Set the airflow variable name
    echo;echo Executing: airflow variables -s node_pool {NODE_POOL}
    airflow variables -s node_pool {NODE_POOL}

    sleep 10

    ### Examine clusters
    echo;echo Executing: gcloud container clusters list
    gcloud container clusters list

    sleep 10

    ### Examine Kubernetes namespaces
    echo;echo Executing: kubectl get namespaces
    kubectl get namespaces

    sleep 10
    """

    delete_node_pools_command = """
    echo; echo >> gcloud config set container/cluster ${COMPOSER_GKE_NAME}
    sudo gcloud config set container/cluster ${COMPOSER_GKE_NAME}

    echo;echo Executing: gcloud container node-pools delete {NODE_POOL} --zone ${COMPOSER_GKE_ZONE} --cluster ${COMPOSER_GKE_NAME} --quiet
    sudo gcloud container node-pools delete {NODE_POOL} --zone ${COMPOSER_GKE_ZONE} --cluster ${COMPOSER_GKE_NAME} --quiet
    """

    fpca_command = """
    echo;echo "sleep 10" ; sleep 10 ;
    echo;echo "ls -l ${SERVICE_ACCOUNT_KEY_JSON}" ; ls -l ${SERVICE_ACCOUNT_KEY_JSON} ;
    echo;echo "gcloud auth activate-service-account --key-file ${SERVICE_ACCOUNT_KEY_JSON}" ; gcloud auth activate-service-account --key-file ${SERVICE_ACCOUNT_KEY_JSON} ;
    echo;echo EXTERNAL_BUCKET=${EXTERNAL_BUCKET} ;
    echo;echo which docker ; which docker;
    echo;echo which R ; which R ;
    echo;echo R -e "library(help=arrow)" ; R -e "library(help=arrow)";
    echo;echo R -e "library(help=fpcFeatures)" ; R -e "library(help=fpcFeatures)";
    echo;echo ls -l /home/airflow/gcs/data/ ; ls -l /home/airflow/gcs/data/ ;
    echo;echo "gsutil ls gs://{BUCKET_NAME}" ; gsutil ls gs://{BUCKET_NAME} ;
    echo;echo "mkdir /datatransfer" ; mkdir /datatransfer;
    echo;echo "gsutil -m cp -r gs://{BUCKET_NAME}/TrainingData_Geojson /datatransfer" ; gsutil -m cp -r gs://{BUCKET_NAME}/TrainingData_Geojson /datatransfer ;
    echo;echo ls -l /datatransfer/TrainingData_Geojson ; ls -l /datatransfer/TrainingData_Geojson/ ;
    echo;echo mkdir github ; mkdir github ;
    echo;echo cd github ; cd github ;
    echo;echo git clone https://github.com/STC-NWRC/bay-of-quinte.git ; git clone https://github.com/STC-NWRC/bay-of-quinte.git ;
    echo;echo cd bay-of-quinte ; cd bay-of-quinte ;
    echo;echo chmod ugo+x run-main.sh ; chmod ugo+x run-main.sh ;
    echo;echo ./run-main.sh ; ./run-main.sh ;
    echo;echo pwd ; pwd ;
    echo;echo "ls -l .." ; ls -l .. ;
    echo;echo "ls -l ../.." ; ls -l ../.. ;
    echo;echo "cat ../../gittmp/bay-of-quinte/output/stdout.R.main" ; cat ../../gittmp/bay-of-quinte/output/stdout.R.main ;
    echo;echo "cd ../.." ; cd ../.. ;
    echo;echo pwd ; pwd ;
    echo;echo ls -l ; ls -l ;
    echo;echo "ls -l gittmp/" ; ls -l gittmp/ ;
    echo;echo "ls -l gittmp/bay-of-quinte/" ; ls -l gittmp/bay-of-quinte/ ;
    echo;echo "ls -l gittmp/bay-of-quinte/output/" ; ls -l gittmp/bay-of-quinte/output/ ;
    echo;echo "gsutil -m cp -r gittmp/bay-of-quinte/* gs://${EXTERNAL_BUCKET}/output/{BUCKET_NAME}" ; gsutil -m cp -r "gittmp/bay-of-quinte/*" gs://${EXTERNAL_BUCKET}/output/{BUCKET_NAME} ;
    echo;echo \'Done!\'
    """

    # Tasks definitions
    # start_task = DummyOperator(
    #     task_id="start"
    #     )

    # end_task = DummyOperator(
    #     task_id="end"
    #     )

    # create_node_pool_task = BashOperator(
    #     task_id      = "create_node_pool",
    #     bash_command = create_node_pool_command,
    #     xcom_push    = True,
    #     dag          = dag
    # )

    # delete_node_pool_task = BashOperator(
    #     task_id      = "delete_node_pool",
    #     bash_command = delete_node_pools_command,
    #     trigger_rule = 'all_done', # Always run even if failures so the node pool is deleted
    #     # xcom_push  = True,
    #     dag          = dag
    # )

    create_node_pool_tasks = []
    delete_node_pool_tasks = []
    fpca_tasks             = []

    for BUCKET_NAME in bucket_list:

        NODE_POOL = 'ndpl-' + BUCKET_NAME

        create_node_pool_tasks.append(BashOperator(
            task_id      = 'create_node_pool_{}'.format(BUCKET_NAME),
            bash_command = create_node_pool_command.replace("{NODE_POOL}",NODE_POOL),
            xcom_push    = True,
            dag          = dag
        ))

        delete_node_pool_tasks.append(BashOperator(
            task_id      = 'delete_node_pool_{}'.format(BUCKET_NAME),
            bash_command = delete_node_pools_command.replace("{NODE_POOL}",NODE_POOL),
            trigger_rule = 'all_done', # Always run even if failures so the node pool is deleted
            # xcom_push  = True,
            dag          = dag
        ))

        fpca_tasks.append(kubernetes_pod.KubernetesPodOperator(
            task_id   = 'fpca_{}'.format(BUCKET_NAME),
            name      = 'fpca_{}'.format(BUCKET_NAME),
            namespace = 'default',
            image     = 'paradisepilot/fpca-base:0.8',
            cmds      = ["sh", "-c", fpca_command.replace("{BUCKET_NAME}",BUCKET_NAME)],
            startup_timeout_seconds = 86400,
          # resources = {'request_cpu': "15000m", 'request_memory': "61440M"},
          # resources = {'request_cpu':  "3000m", 'request_memory':  "3072M"},
            secrets   = [secret_volume_service_account_key],
            env_vars = {
                'SERVICE_ACCOUNT_KEY_JSON': '/var/secrets/google/fpca-service-account-key-2022-06-10-a.json',
                'EXTERNAL_BUCKET': external_bucket
                },
            tolerations = [{
                'key': "work",
                'operator': 'Equal',
                'value': 'well',
                'effect': "NoSchedule"
                }],
            affinity = {
                'nodeAffinity': {
                    'requiredDuringSchedulingIgnoredDuringExecution': {
                        'nodeSelectorTerms': [{
                            'matchExpressions': [{
                                'key': 'cloud.google.com/gke-nodepool',
                                'operator': 'In',
                                'values': [
                                    Variable.get("node_pool", default_var = NODE_POOL)
                                ]
                            }]
                        }]
                    }
                }
            }
        ))

    # Tasks order
    for i in range(0,len(fpca_tasks)):
        create_node_pool_tasks[i] >> fpca_tasks[i] >> delete_node_pool_tasks[i]
