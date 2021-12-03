from datetime import timedelta,datetime
import airflow
from airflow.models import DAG   
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.kubernetes.volume import Volume
from airflow.kubernetes.volume_mount import VolumeMount
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
# from airflow.models import XCom
from aux_code import get_num_of_buckets

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

    # day,month,year=(datetime.now().day,datetime.now().month,datetime.now().year)
    # exec_date=datetime(year,month,day)

    # def num_of_jobs(ti):
    #     from google.cloud import storage
    #     from os import getcwd
    #     print(getcwd())
    #     storage_client = storage.Client()
    #     lists = [f.name for f in storage_client.list_buckets() if f.name.find('us-central1') == -1 ]
    #     # ti.xcom_push(key='buckets',value=lists)
    #     print((ti.task_id,ti.dag_id,exec_date))
    #     #print((ti.task_id,ti.dag_id,ti.execution_date))
    #     set_xcom('buckets',lists,ti.task_id,ti.dag_id,exec_date)

    # def set_xcom(key,value,task_id,dag_id,execution_date):
    #     XCom.set(key=key,
    #          value=value,
    #          task_id='{}_n_buckets'.format(task_id),
    #          dag_id=dag_id,
    #          execution_date=execution_date)

    # def get_xcom(key,task_id,dag_id,execution_date):
    #     return XCom.get_one(execution_date,
    #                     key=key,
    #                     task_id='{}_n_buckets'.format(task_id),
    #                     dag_id=dag_id,
    #                     include_prior_dates=False)

    

    # def n_buckets_creation(ti):
    #     buckets=ti.xcom_pull(key='buckets',task_ids='mother-job')
    # buckets=XCom.get_one(task_id="mother-job")
    # buckets_=" ".join(buckets)
    # BashOperator(
    #             task_id='copy-from-bucket-to-cluster',
    #             bash_command="scripts/create-buckets.sh",
    #             env={'BUCKETS_NAME': buckets_}
    # )
    def print_bucket_name(name):
        print ('{} is a bucket'.format(name))


    # python_test = [
    #     PythonOperator(
    #         task_id='task_{}'.format(b),
    #         python_callable=print_bucket_name,
    #         op_kwargs={'name':b}
    #     ) for b in get_num_of_buckets()
    # ] if get_num_of_buckets() != None else DummyOperator(task_id='nothing-to-process')
    buckets=get_num_of_buckets()
    num=str(len(buckets))
    # bash_list=[]
    # for bkt in buckets:
    #     bash_list.append(
    #         BashOperator(
    #             task_id='bash_{}'.format(bkt),
    #             bash_command='kubectl cp /home/airflow/gcs/data/${bkt} $(kubectl get pods | grep Running | grep pod_${bkt} | awk ‘{print $1}’):/temp/${bkt}'
    #         )
    #     )
    
    move_data=[
        BashOperator(
                task_id='bash_{}'.format(bkt),
                bash_command="kubectl exec -n default data-transfer-pod -- /bin/sh -c 'mkdir -p /temp/datastore/node_{0}; cd /temp/datastore/node_{0}; mkdir input; mkdir output; pwd; ls; exit' ; kubectl cp /home/airflow/gcs/data/{0}.txt default/data-transfer-pod:/temp/datastore/node_{0}/input".format(bkt)
            ) for bkt in buckets
    ]

    pod_list=[]
    for (i,bucket) in enumerate(buckets):
            command = ["python","/temp/scripts/aux_code.py","/temp/datastore/node_{0}/input/{0}.txt".format(bucket)]
            pod_list.append(KubernetesPodOperator(
                    namespace='default',
                    image='python:3.7',
                    # image_pull_policy='Never',
                    name='pod_{}'.format(bucket),
                    task_id='task_{}'.format(i),
                    volumes=[volume],
                    volume_mounts=[volume_mount],
                    cmds=command,
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
            )
            



    clear_pod= BashOperator(
        task_id='clear-pod',
        bash_command='kubectl delete -f /home/airflow/gcs/dags/scripts/create_pod_data.yaml'
    )

    start=DummyOperator(
        task_id='test-to-start'
    )
    end=DummyOperator(
        task_id='test-to-end'
    )

    transfer_bash_pod=BashOperator(
        task_id='transfer-to-pod',
        bash_command='bash /home/airflow/gcs/dags/scripts/create-pods.sh ',
    )

    # main_entry = PythonOperator(
    #     task_id='mother-job',
    #     python_callable=num_of_jobs,
    #     provide_context=True
    # )

    sum_results=BashOperator(
                task_id='daugther-node',
                bash_command="bash /home/airflow/gcs/dags/scripts/collating.sh {}".format(num)
                # env={'NUM': num}
    )

    # create_pods=PythonOperator(
    #     task_id='create-pods',
    #     python_callable=pods_creation,
    #     provide_context=True
    # )



    #this will be the daughter node responsible for computing
    #the results from the other 10 nodes
    #t11 = {}

    # [t1,t2,t3,t4,t5,t6,t7,t8,t9,t10] >> t11
    # [t1,t2]
    # start >> sum_results >> end
    for i in range(len(move_data)):
        start >> transfer_bash_pod >> move_data[i] >> clear_pod >> pod_list[i] >> sum_results >> end
    
    #testing>>display_bts      