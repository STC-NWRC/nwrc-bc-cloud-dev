GCP FPCA Pipeline Prototype 00
==============================

This task is the first prototype of the GCP FPCA pipeline.

How to run the pipeline:

1.  Create a Google Composer environment:
    ```
    sh ./gcloud-composer-environments-create.sh
    ```

2.  Upload the DAG of the pipeline, and trigger the corresponding Composer workflow:
    ```
    sh ./gcloud-composer-dag-upload.sh
    ```

3.  When the pipeline has finished execution, delete the Composer environment:
    ```
    sh ./gcloud-composer-environments-delete.sh
    ```
