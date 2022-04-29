GCP FPCA Workflow Prototype v00
===============================

This task is the first prototype of the GCP FPCA workflow.

# How to run the workflow:

1.  Create a Google Composer environment:
    ```
    sh ./gcloud-composer-environments-create.sh
    ```

2.  Upload the DAG of the pipeline, and trigger the corresponding Composer workflow:
    ```
    sh ./gcloud-composer-dag-upload-then-trigger.sh
    ```

3.  When the pipeline has finished execution, delete the Composer environment:
    ```
    sh ./gcloud-composer-environments-delete.sh
    ```

# Name of the DAG:

Look up the wokflow in the Airflow UI under the name: **fpca_gke**

# Output Google Storage bucket:

Output is written to the following Google Storage bucket: **gs://fpca-336015-xbucket/output**
