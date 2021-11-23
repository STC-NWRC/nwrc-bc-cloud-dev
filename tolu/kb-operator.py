from datetime import timedelta,datetime
import airflow
from airflow.models import DAG
# from airflow.contrib.operators import kubernetes_pod_operator   
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.kubernetes.volume import Volume
from airflow.kubernetes.volume_mount import VolumeMount
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator

#from kubernetes.client import V1Volume,V1VolumeMount,V1PersistentVolumeClaimVolumeSource

YESTERDAY = datetime.now() - timedelta(days=1)

default_args = {
    'start_date': YESTERDAY
}

# volume_mount = VolumeMount(name='new-disk-claim',mount_path='/temp',sub_path=None,read_only=False)

# pvc = V1PersistentVolumeClaimVolumeSource(claim_name="toy-data")

# volume = V1Volume(name="toy-data",persistent_volume_claim=pvc)
volume_mount = VolumeMount('new-disk-claim',mount_path='/temp',sub_path=None,read_only=False)
volume_config= {'persistentVolumeClaim':{'claimName': 'new-disk-claim'}}
volume = Volume(name='new-disk-claim', configs=volume_config)

with DAG(
    'kubernetes-test',
    default_args=default_args,
    schedule_interval=timedelta(days=1)) as dag:

    def num_of_jobs(ti):
        from google.cloud import storage
        from os import getcwd
        print(getcwd())
        storage_client = storage.Client()
        lists = [f.name for f in storage_client.list_buckets() if f.name.find('us-central1') == -1 ]
        ti.xcom_push(key='buckets',value=lists)

    def n_buckets_creation(ti):
        buckets=ti.xcom_pull(key='buckets',task_ids='mother-job')
        buckets_=" ".join(buckets)
        BashOperator(
                task_id='copy-from-bucket-to-cluster',
                bash_command="scripts/create-buckets.sh",
                env={'BUCKETS_NAME': buckets_}
    ) 

    def pods_creation(ti):
        buckets=ti.xcom_pull(key='buckets',task_ids='mother-job')
        for (i,bucket) in enumerate(buckets):
            create_repo_command = ["sh", "-c",'echo \'Init Container\'; pwd; mkdir /root/{}; cd /root/{}/; ls -lrt; echo \'Done!\''.format(bucket,bucket)]
            KubernetesPodOperator(
                    namespace='default',
                    image='ubuntu:latest',
                    name=bucket,
                    task_id='task_{}'.format(i),
                    volumes=[volume],
                    volume_mounts=[volume_mount],
                    cmds=create_repo_command,
                    tolerations=[{
                        'key': "work",
                        'operator': 'Equal',
                        'value': 'well',
                        'effect': "NoSchedule"
            }],
                    affinity={
                    'nodeAffinity': {
                        'requiredDuringSchedulingIgnoredDuringExecution': {
                            'nodeSelectorTerms': [{
                                'matchExpressions': [{
                                    'key': 'cloud.google.com/gke-nodepool',
                                'operator': 'In',
                                    # The label key's value that pods can be scheduled
                                    # on.
                                    'values': [
                                        'pool-1',
                                    ]
                                }]
                            }]
                        }
                    }
                }
                )
            



    # connect_clstr= BashOperator(
    #     task_id='connect-cluster',
    #     bash_command='gcloud container clusters get-credentials us-central1-toyworkflow-21399c22-gke --zone us-central1-c --project idyllic-anvil-331918'
    # )

    start=DummyOperator(
        task_id='test-to-start'
    )
    end=DummyOperator(
        task_id='test-to-end'
    )

    # display_bts=BashOperator(
    #     task_id='copy-from-buckets-to-cluster',
    #     bash_command='echo $(ls /home)',
        

    # )

    main_entry = PythonOperator(
        task_id='mother-job',
        python_callable=num_of_jobs,
        provide_context=True
    )

    buckets= PythonOperator(
        task_id='buckets-creation',
        python_callable=n_buckets_creation,
        provide_context=True
    )

    create_pods=PythonOperator(
        task_id='create-pods',
        python_callable=pods_creation,
        provide_context=True
    )



    #this will be the daughter node responsible for computing
    #the results from the other 10 nodes
    #t11 = {}

    # [t1,t2,t3,t4,t5,t6,t7,t8,t9,t10] >> t11
    # [t1,t2]
    main_entry >> buckets >> create_pods
    
    #testing>>display_bts      