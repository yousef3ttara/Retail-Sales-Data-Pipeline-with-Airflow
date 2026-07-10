# airflow/tasks/utils.py
import os, io, json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

load_dotenv() # reads .env file automatically

AZURE_CONN_STR = os.getenv('AZURE_CONN_STR')
CONTAINER      = os.getenv('AZURE_CONTAINER', 'retail-pipeline')


def get_blob_client():
    return BlobServiceClient.from_connection_string(AZURE_CONN_STR)


# Alias used by monitoring tasks (drift_check.py, write_run_log)
get_client = get_blob_client


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


def write_run_log(stats: dict) -> None:
    '''Write pipeline run stats as JSON to Azure Blob for audit trail.'''
    run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_data = {
        'run_id':    run_id,
        'timestamp': datetime.now().isoformat(),
        **stats,
    }
    buf = io.BytesIO(json.dumps(log_data, indent=2).encode())
    get_client().get_blob_client(
        container=CONTAINER,
        blob=f'logs/run_{run_id}.json',
    ).upload_blob(buf, overwrite=True)
    print(f'[LOG] Run log written to logs/run_{run_id}.json')