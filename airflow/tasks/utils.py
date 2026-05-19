# airflow/tasks/utils.py
import os, io
import pandas as pd
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

load_dotenv() # reads .env file automatically

AZURE_CONN_STR = os.getenv('AZURE_CONN_STR')
CONTAINER      = os.getenv('AZURE_CONTAINER', 'retail-pipeline')


def get_blob_client():
    return BlobServiceClient.from_connection_string(AZURE_CONN_STR)


def read_parquet(blob_name: str) -> pd.DataFrame:
    '''Read a Parquet file from Azure Blob into a DataFrame.'''
    client = get_blob_client()
    blob   = client.get_blob_client(container=CONTAINER, blob=blob_name)
    data   = blob.download_blob().readall()
    return pd.read_parquet(io.BytesIO(data))


def write_parquet(df: pd.DataFrame, blob_name: str) -> None:
    '''Write a DataFrame as Parquet to Azure Blob.'''
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False, engine='pyarrow')
    buffer.seek(0)
    client = get_blob_client()
    client.get_blob_client(container=CONTAINER, blob=blob_name) \
          .upload_blob(buffer, overwrite=True)
    print(f'[Azure] Written -> {blob_name} ({len(df):,} rows)')
