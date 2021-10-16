from google.cloud import storage
from google.oauth2 import credentials, service_account


# Explictly set the credentials to the desired project
# create a credentials obj
CREDENTIALS_PATH = r"C:\Users\rhamilton\.gcloud\supple-folder-320414-10bdf03ef07a.json"

credential = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)

storage_client = storage.Client(project='')
bucket = storage_client.bucket('new_bucket')
bucket.storage_class = 'STANDARD'
new_bucket = storage_client.create_bucket(bucket)